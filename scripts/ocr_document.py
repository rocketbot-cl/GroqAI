from groq_client import get_client  # Importar la función para obtener el cliente
import base64
import traceback
import mimetypes  # Importar mimetypes para detectar el tipo de archivo
import re  # Importar re para trabajar con expresiones regulares
import requests  # type: ignore
from urllib.parse import urlparse  # Para analizar URLs
import os  # Para validar la existencia de archivos locales
from groq.resources.models import Models  # type: ignore


def is_valid_url(url):
    """
    Validate if a URL is accessible and is a valid image or PDF.
    
    :param url: URL to validate
    :return: tuple (is_valid, is_pdf, error_message)
    """
    try:
        # Parse the URL
        parsed = urlparse(url)
        if not all([parsed.scheme, parsed.netloc]):
            return False, False, "Invalid URL"

        # Try to get headers without downloading the full content
        response = requests.head(url, allow_redirects=True)
        if response.status_code != 200:
            return False, False, f"URL is not accessible (Status: {response.status_code})"

        # Check content type
        content_type = response.headers.get('content-type', '').lower()
        if 'application/pdf' in content_type:
            return True, True, None
        elif any(img_type in content_type for img_type in ['image/jpeg', 'image/png', 'image/gif', 'image/webp']):
            return True, False, None
        else:
            return False, False, f"Unsupported file type: {content_type}"

    except requests.exceptions.RequestException as e:
        return False, False, f"Error accessing URL: {str(e)}"


def convert_markdown_table_to_text(text):
    """
    Convierte una tabla en formato Markdown a texto plano.
    
    :param text: Texto que puede contener tablas en formato Markdown
    :return: Texto con las tablas convertidas a formato texto plano
    """
    lines = text.split('\n')
    result = []
    in_table = False
    table_data = []
    
    for line in lines:
        # Detectar si es una línea de tabla
        if '|' in line:
            # Si es una línea de separación (| --- | --- |), la ignoramos
            if re.match(r'\s*\|[\s\-]+\|\s*$', line) or re.match(r'\s*\|(?:[:\-]+\|)+\s*$', line):
                continue
                
            # Procesar la línea de la tabla
            cells = [cell.strip() for cell in line.split('|')]
            # Eliminar células vacías al inicio y final (debido a los | externos)
            cells = [cell for cell in cells if cell]
            # Unir múltiples espacios y reemplazar saltos de línea
            cells = [' '.join(cell.split()) for cell in cells]
            # Ignorar filas que solo contienen guiones o están vacías
            if not all(cell == '---' or cell == '' for cell in cells):
                table_data.append(cells)
            in_table = True
        else:
            if in_table:
                # Procesar la tabla acumulada
                if table_data:
                    # Si hay encabezados, usarlos para formatear la salida
                    headers = table_data[0]
                    for row in table_data[1:]:
                        # Asegurarse de que tengamos el mismo número de columnas
                        row = row + [''] * (len(headers) - len(row))
                        # Crear una línea de texto con el formato "Header: Value", ignorando valores vacíos
                        formatted_cells = []
                        for i in range(len(headers)):
                            if row[i].strip():  # Solo incluir si el valor no está vacío
                                formatted_cells.append(f"{headers[i]}: {row[i]}")
                        if formatted_cells:  # Solo agregar la línea si hay algún valor
                            formatted_row = '; '.join(formatted_cells)
                            result.append(formatted_row)
                    result.append('')  # Línea en blanco después de cada tabla
                table_data = []
                in_table = False
            result.append(line)
    
    # Procesar última tabla si existe
    if in_table and table_data:
        headers = table_data[0]
        for row in table_data[1:]:
            row = row + [''] * (len(headers) - len(row))
            formatted_cells = []
            for i in range(len(headers)):
                if row[i].strip():  # Solo incluir si el valor no está vacío
                    formatted_cells.append(f"{headers[i]}: {row[i]}")
            if formatted_cells:  # Solo agregar la línea si hay algún valor
                formatted_row = '; '.join(formatted_cells)
                result.append(formatted_row)
    
    return '\n'.join(result)


def process_file(model, file_path, result_var, SetVar, PrintException):
    """
    Process a file (PDF or image) with groq AI OCR.

    :param model: The OCR model to use.
    :param file_path: The absolute path to the file or the URL of the file to process.
    :param result_var: Name of the variable to store the OCR result.
    :param SetVar: Function to set variables in Rocketbot.
    :param PrintException: Function to print exceptions in Rocketbot.
    """
    try:
        # Get the existing client
        client = get_client()
        if not client:
            raise Exception("You must connect to groq AI before using this command. Please run the connection module first.")

        # Validate model parameter
        if not model:
            raise Exception("You must specify a valid model for OCR.")

        # Validate file_path parameter
        if not file_path:
            raise Exception("You must specify a valid file path or URL.")

        # Detect if it's a URL or local file
        is_url = file_path.startswith(("http://", "https://"))
        
        if is_url:
            # Validate URL and get file type
            is_valid, is_pdf, error_msg = is_valid_url(file_path)
            if not is_valid:
                raise Exception(f"Invalid or inaccessible URL: {error_msg}")
                
            document = {
                "type": "document_url" if is_pdf else "image_url",
                f"{'document' if is_pdf else 'image'}_url": file_path
            }
        else:
            # Validate local file exists
            if not os.path.exists(file_path):
                raise Exception(f"Local file does not exist: {file_path}")
                
            # For local files, use mimetypes and encode content
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                raise Exception("Could not determine file type")
                
            is_pdf = mime_type == "application/pdf"
            is_image = mime_type.startswith("image/") if mime_type else False
            
            if not (is_pdf or is_image):
                raise Exception("File must be a valid PDF or image (JPEG, PNG, GIF, WEBP). Detected type: " + (mime_type if mime_type else "unknown"))
            
            with open(file_path, "rb") as file:
                encoded_content = base64.b64encode(file.read()).decode("utf-8")
                
            if is_pdf:
                document = {
                    "type": "document_url",
                    "document_url": f"data:application/pdf;base64,{encoded_content}"
                }
            else:
                document = {
                    "type": "image_url",
                    "image_url": f"data:{mime_type};base64,{encoded_content}"
                }

        try:
            # Perform OCR using the `process` method
            response = client.ocr.process(
                model=model,
                document=document,
                include_image_base64=not is_pdf  # Only include base64 for images
            )
        except SDKError as e:
            if "Invalid model" in str(e):
                raise Exception(f"The model '{model}' is not valid for OCR. Please verify the model name.")
            raise e

        # Extract the text from the response
        extracted_text = ""
        if response.pages:
            for page in response.pages:
                if page.markdown:
                    extracted_text += page.markdown + "\n"
        else:
            extracted_text = "No text could be extracted from the document."

        # Clean the Markdown content for better readability
        clean_text = re.sub(r"!\[.*?\]\(.*?\)", "", extracted_text)  # Remove images
        clean_text = re.sub(r"#\s*", "", clean_text)  # Remove Markdown headers
        clean_text = clean_text.strip()  # Remove leading/trailing whitespace
        
        # Convert tables to text format
        clean_text = convert_markdown_table_to_text(clean_text)

        # Print debug information
        print("DEBUG: OCR Cleaned Text =", clean_text)

        # Set the result in Rocketbot
        SetVar(result_var, clean_text)

    except Exception as e:
        SetVar(result_var, None)
        print("Error processing file with groq AI OCR:")
        print(traceback.format_exc())
        PrintException()
        raise e