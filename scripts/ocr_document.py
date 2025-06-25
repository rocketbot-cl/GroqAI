from groq_client import get_client  # Importar la función para obtener el cliente
import base64
import traceback
import mimetypes  # Importar mimetypes para detectar el tipo de archivo
import re  # Importar re para trabajar con expresiones regulares
import requests  # type: ignore
from urllib.parse import urlparse  # Para analizar URLs
import os  # Para validar la existencia de archivos locales
from groq.resources.models import Models  # type: ignore
import imghdr
import os.path

# Add after other constants at the top
SUPPORTED_IMAGE_FORMATS = ['jpeg', 'jpg', 'png', 'gif', 'webp', 'bmp']

def is_valid_url(url):
    """
    Validate if a URL is accessible and is a valid image or PDF.

    :param url: URL to validate
    :return: tuple (is_valid, is_pdf, error_message)
    """
    try:
        response = requests.head(url)
        
        # Check content type
        content_type = response.headers.get('content-type', '').lower()
        if 'application/pdf' in content_type:
            return True, True, None
        elif any(f'image/{fmt}' in content_type for fmt in SUPPORTED_IMAGE_FORMATS):
            return True, False, None
        else:
            return False, False, f"Unsupported file type: {content_type}. Supported formats are: {', '.join(SUPPORTED_IMAGE_FORMATS)}"

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
                                formatted_cells.append(
                                    f"{headers[i]}: {row[i]}")
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

def is_url(string):
    """Check if string is a URL."""
    try:
        result = urlparse(string)
        return all([result.scheme, result.netloc])
    except:
        return False

def encode_image(image_path):
    """
    Encode the image file to base64.
    """
    try:
        with open(image_path, "rb") as image_file:
            # Detect image type
            image_type = imghdr.what(image_file)
            if not image_type:
                raise ValueError("File not recognized as a valid image")
            
            # Read and encode
            image_file.seek(0)
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            return f"data:image/{image_type};base64,{base64_image}"
    except Exception as e:
        raise Exception(f"Error encoding image: {str(e)}")

def validate_image_file(file_path):
    """
    Validates if a file is a supported image file.
    
    Args:
        file_path (str): Path to the file to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        # Check file extension
        ext = os.path.splitext(file_path)[1].lower().replace('.', '')
        if ext not in SUPPORTED_IMAGE_FORMATS:
            return False, f"ERROR: Unsupported file format '.{ext}'. Supported formats are: {', '.join(SUPPORTED_IMAGE_FORMATS)}"
        
        # Verify it's actually an image using imghdr
        with open(file_path, 'rb') as f:
            actual_type = imghdr.what(f)
            if not actual_type:
                return False, "ERROR: The file is not recognized as a valid image file. Please provide a valid image file."
            if actual_type not in SUPPORTED_IMAGE_FORMATS:
                return False, f"ERROR: Unsupported image format '{actual_type}'. Supported formats are: {', '.join(SUPPORTED_IMAGE_FORMATS)}"
            
        return True, None
        
    except Exception as e:
        return False, f"ERROR validating image file: {str(e)}"

def process_file(model, file_path, result_var, message=None, temperature=0.7, SetVar=None, PrintException=None):

    """Process an image file using Groq AI's vision model.
    
    Args:
        model (str): Model ID to use
        file_path (str): Path to file or image URL
        result_var (str): Variable name to store the result
        temperature (float): Temperature for generation (default 0.7)
        message (str): Message/prompt for the model
    """
    try:
        print("\n=== Processing image with Groq AI ===")
        
        # Establecer resultado por defecto
        if SetVar:
            SetVar(result_var, None)
        
        # Obtener el cliente
        client = get_client()
        if not client:
            error_msg = "ERROR: You must connect to Groq AI before using this command. Please run the connection module first."
            print(error_msg)
            raise Exception(error_msg)

        # Validar parámetros básicos
        if not model:
            error_msg = "ERROR: Model must be specified"
            print(error_msg)
            raise Exception(error_msg)

        if not file_path:
            error_msg = "ERROR: File path or URL must be provided"
            print(error_msg)
            raise Exception(error_msg)

        # Preparar la imagen según sea URL o archivo local
        if is_url(file_path):
            # Validate URL points to an image
            is_valid, is_pdf, url_error = is_valid_url(file_path)
            if not is_valid:
                error_msg = f"ERROR: Invalid image URL - {url_error}"
                print(error_msg)
                raise Exception(error_msg)
            if is_pdf:
                error_msg = f"ERROR: PDF files are not supported. Supported formats are: {', '.join(SUPPORTED_IMAGE_FORMATS)}"
                print(error_msg)
                raise Exception(error_msg)
                
            image_data = {"url": file_path}
            print("\nProcessing image from URL...")
        else:
            # Validate local file is an image
            file_ext = file_path.lower().split('.')[-1]
            if file_ext not in SUPPORTED_IMAGE_FORMATS:
                error_msg = f"ERROR: Unsupported file format '.{file_ext}'. Supported formats are: {', '.join(SUPPORTED_IMAGE_FORMATS)}"
                print(error_msg)
                raise Exception(error_msg)
            
            # Validate image file
            is_valid, validation_error = validate_image_file(file_path)
            if not is_valid:
                print(validation_error)
                raise Exception(validation_error)
                
            print("\nProcessing local image...")
            try:
                image_data = {"url": encode_image(file_path)}
            except Exception as e:
                error_msg = f"ERROR processing file: {str(e)}"
                print(error_msg)
                raise Exception(error_msg)

        print("\nSending request to Groq AI...")
        try:
            # First try with complex content structure
            content = [
                {
                    "type": "text",
                    "text": message if message else "Please describe what you see in this image."
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_data["url"]
                    }
                }
            ]
            
            messages = [
                {
                    "role": "user",
                    "content": content
                }
            ]

            try:
                # Try first with complex structure
                completion = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature
                )
            except Exception as complex_error:
                if "message[0].content must be a string" in str(complex_error):
                    # If failed with complex structure, try with simple string content
                    simple_content = f"{message if message else 'Please describe what you see in this image.'}\n{image_data['url']}"
                    messages = [
                        {
                            "role": "user",
                            "content": simple_content
                        }
                    ]
                    completion = client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=temperature
                    )
                else:
                    # If it's a different error, raise it
                    raise complex_error
        
            # Extraer el texto generado
            extracted_text = completion.choices[0].message.content
            
            print("\n✓ Text extracted successfully!")
            
            # Guardar el resultado
            if SetVar: SetVar(result_var, extracted_text)
            
            return extracted_text

        except Exception as api_error:
            error_str = str(api_error)
            if "model_decommissioned" in error_str:
                error_msg = f"ERROR: The model '{model}' has been discontinued and is no longer supported.\n\nTo see available models you can:\n1. Run the 'Get available models' command from the module\n2. Check the official documentation at https://console.groq.com/docs/models"
                print(error_msg)
                raise Exception(error_msg)
            elif "model_terms_required" in error_str:
                error_msg = f"ERROR: El modelo '{model}' requiere aceptación de términos y condiciones.\nPor favor, solicite al administrador de la organización que acepte los términos en:\nhttps://console.groq.com/playground?model={model}"
                print(error_msg)
                raise Exception(error_msg)
            elif "request_too_large" in error_str or "Request Entity Too Large" in error_str:
                error_msg = f"ERROR: La imagen es demasiado grande para ser procesada con el modelo '{model}'.\nPuede intentar:\n1. Usar un modelo más robusto para OCR\n2. Reducir el tamaño o peso de la imagen\n3. Dividir la imagen en secciones más pequeñas"
                print(error_msg)
                raise Exception(error_msg)
            elif "does not support chat completions" in error_str.lower():
                error_msg = f"ERROR: The model '{model}' is not compatible with OCR/image processing. This model is designed for another purpose (e.g., audio transcription). Please use a vision-capable model that supports chat completions."
                print(error_msg)
                raise Exception(error_msg)
            elif "does not support" in error_str.lower() and ("vision" in error_str.lower() or "image" in error_str.lower() or "multimodal" in error_str.lower()):
                error_msg = f"ERROR: The model '{model}' is not compatible with image processing. This model is designed for another purpose (e.g., text generation or audio transcription). Please use a vision-capable model like GPT-4 Vision or Claude 3."
                print(error_msg)
                raise Exception(error_msg)
            elif "context deadline exceeded" in error_str.lower():
                error_msg = "ERROR: Could not process the image. Please verify you are providing a valid image file in one of these formats: " + ", ".join(SUPPORTED_IMAGE_FORMATS)
                print(error_msg)
                raise Exception(error_msg)
            else:
                error_msg = f"ERROR in Groq API: {str(api_error)}"
                print(error_msg)
                raise Exception(error_msg)

    except Exception as e:
        error_msg = f"Error processing image: {str(e)}"
        print(error_msg)
        print("\nError details:")
        print(traceback.format_exc())
        if PrintException:
            PrintException()
        raise Exception(error_msg)
