from groq_client import get_client
import traceback
import os

# Lista de formatos de archivo soportados
SUPPORTED_FORMATS = ['mp3', 'm4a', 'ogg', 'wav']

def process_file(
    model,
    file_path,
    result_var,
    language=None,
    prompt=None,
    temperature=0,
    timestamp_granularities=None,
    SetVar=None,
    PrintException=None
):
    """
    Procesa un archivo de audio usando el servicio de transcripción de Groq AI.
    
    Args:
        model (str): ID del modelo a usar (ej: "whisper-large-v3")
        file_path (str): Ruta al archivo local o URL del audio
        result_var (str): Nombre de la variable para almacenar el resultado
        language (str, optional): Código ISO-639-1 del idioma (ej: "en", "es")
        prompt (str, optional): Texto para guiar el estilo o especificar palabras
        temperature (float, optional): Temperatura entre 0 y 1 (default 0)
        timestamp_granularities (list, optional): ["word"] y/o ["segment"]
        SetVar: Función para establecer variables en Rocketbot
        PrintException: Función para imprimir excepciones en Rocketbot
    """
    try:
        print("\n=== Processing audio with Groq AI ===")
        
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

        # Preparar los parámetros de la solicitud
        request_params = {
            "model": model,
            "response_format": "text",  # Always text
            "temperature": temperature
        }

        # Agregar parámetros opcionales si se proporcionan
        if language:
            request_params["language"] = language
        if prompt:
            request_params["prompt"] = prompt
        if timestamp_granularities:
            request_params["timestamp_granularities"] = timestamp_granularities

        # Determinar si es URL o archivo local
        if file_path.startswith(("http://", "https://")):
            request_params["url"] = file_path
            print("\nProcessing audio from URL...")
        else:
            # Verificar que el archivo existe
            if not os.path.exists(file_path):
                error_msg = f"ERROR: The file {file_path} does not exist"
                print(error_msg)
                raise Exception(error_msg)
            
            # Verificar la extensión del archivo
            file_ext = os.path.splitext(file_path)[1].lower().replace('.', '')
            if file_ext not in SUPPORTED_FORMATS:
                error_msg = f"ERROR: Unsupported file format. Allowed formats are: {', '.join(SUPPORTED_FORMATS)}"
                print(error_msg)
                raise Exception(error_msg)
                
            print("\nProcessing local audio file...")
            with open(file_path, "rb") as audio_file:
                request_params["file"] = audio_file
                try:
                    response = client.audio.transcriptions.create(**request_params)
                except Exception as e:
                    error_str = str(e)
                    if "could not process file" in error_str.lower():
                        error_msg = "ERROR: Could not process file. Please verify it is a valid audio file in one of these formats: " + ", ".join(SUPPORTED_FORMATS)
                    elif "file too large" in error_str.lower():
                        error_msg = "ERROR: File is too large. The limit is 25MB (free tier) or 100MB (dev tier)"
                    elif "does not support" in error_str.lower() and "transcribe" in error_str.lower():
                        error_msg = f"ERROR: The model '{model}' is not compatible with audio transcription."
                    else:
                        error_msg = f"ERROR processing file: {str(e)}"
                    print(error_msg)
                    raise Exception(error_msg)

        # Si es URL, hacer la solicitud fuera del bloque with
        if "url" in request_params:
            try:
                response = client.audio.transcriptions.create(**request_params)
            except Exception as e:
                error_str = str(e)
                if "could not process file" in error_str.lower():
                    error_msg = "ERROR: Could not process file from URL. Please verify the URL points to a valid audio file in one of these formats: " + ", ".join(SUPPORTED_FORMATS)
                elif "file too large" in error_str.lower():
                    error_msg = "ERROR: File is too large. The limit is 25MB (free tier) or 100MB (dev tier)"
                elif "does not support" in error_str.lower() and "transcribe" in error_str.lower():
                    error_msg = f"ERROR: The model '{model}' is not compatible with audio transcription."
                else:
                    error_msg = f"ERROR processing URL: {str(e)}"
                print(error_msg)
                raise Exception(error_msg)

        print("\n✓ Audio processed successfully!")
        
        # La respuesta ya es el texto directamente
        if SetVar:
            SetVar(result_var, response)
        
        return response

    except Exception as e:
        error_msg = f"Error processing audio: {str(e)}"
        print(error_msg)
        print("\nError details:")
        print(traceback.format_exc())
        if PrintException:
            PrintException()
        raise Exception(error_msg)
