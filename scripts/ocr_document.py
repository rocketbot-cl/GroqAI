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
                raise ValueError("Archivo no reconocido como imagen válida")
            
            # Read and encode
            image_file.seek(0)
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            return f"data:image/{image_type};base64,{base64_image}"
    except Exception as e:
        raise Exception(f"Error al codificar la imagen: {str(e)}")

def process_file(model, file_path, result_var, message="Por favor, describe lo que ves en esta imagen.", temperature=0.7, SetVar=None, PrintException=None):
    """
    Procesa un archivo de imagen usando el modelo de visión de Groq AI.
    
    Args:
        model (str): ID del modelo a usar
        file_path (str): Ruta al archivo o URL de la imagen
        result_var (str): Nombre de la variable para almacenar el resultado
        message (str): Mensaje/prompt para el modelo
        temperature (float): Temperatura para la generación (default 0.7)
        SetVar: Función para establecer variables en Rocketbot
        PrintException: Función para imprimir excepciones en Rocketbot
    """
    try:
        print("\n=== Procesando imagen con Groq AI ===")
        
        # Establecer resultado por defecto
        if SetVar:
            SetVar(result_var, None)
        
        # Obtener el cliente
        client = get_client()
        if not client:
            error_msg = "ERROR: Debe conectarse a Groq AI antes de usar este comando."
            print(error_msg)
            raise Exception(error_msg)

        # Validar parámetros básicos
        if not model:
            error_msg = "ERROR: Debe especificar un modelo"
            print(error_msg)
            raise Exception(error_msg)

        if not file_path:
            error_msg = "ERROR: Debe proporcionar una ruta de archivo o URL"
            print(error_msg)
            raise Exception(error_msg)

        # Preparar la imagen según sea URL o archivo local
        if is_url(file_path):
            image_data = {"url": file_path}
            print("\nProcesando imagen desde URL...")
        else:
            # Verificar que el archivo existe
            if not os.path.exists(file_path):
                error_msg = f"ERROR: El archivo {file_path} no existe"
                print(error_msg)
                raise Exception(error_msg)
                
            print("\nProcesando imagen local...")
            try:
                image_data = {"url": encode_image(file_path)}
            except Exception as e:
                error_msg = f"ERROR al procesar el archivo: {str(e)}"
                print(error_msg)
                raise Exception(error_msg)

        print("\nEnviando solicitud a Groq AI...")
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": message
                            },
                            {
                                "type": "image_url",
                                "image_url": image_data
                            }
                        ]
                    }
                ],
                temperature=temperature,
                max_completion_tokens=1024,
                stream=False
            )
            
            # Extraer el texto generado
            extracted_text = response.choices[0].message.content
            
            print("\n✓ Texto extraído exitosamente!")
            
            # Guardar el resultado
            if SetVar:
                SetVar(result_var, extracted_text)
            
            return extracted_text

        except Exception as api_error:
            error_msg = f"ERROR en la API de Groq: {str(api_error)}"
            print(error_msg)
            raise Exception(error_msg)

    except Exception as e:
        error_msg = f"Error al procesar la imagen: {str(e)}"
        print(error_msg)
        print("\nDetalles del error:")
        print(traceback.format_exc())
        if PrintException:
            PrintException()
        raise Exception(error_msg)
