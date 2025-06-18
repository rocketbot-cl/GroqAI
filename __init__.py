# coding: utf-8
"""
Módulo Rocketbot para conectarse con groq AI usando su SDK oficial.

Para obtener el módulo/función que se está llamando:
    GetParams("module")

Para obtener variables desde Rocketbot:
    var = GetParams("nombre_variable")

Para modificar variables en Rocketbot:
    SetVar("nombre_variable", valor)

Para instalar el SDK:
    pip install groqai -t libs
"""

import os
import sys

base_path = tmp_global_obj["basepath"]  # type: ignore
cur_path = base_path + 'modules' + os.sep + 'GroqAI' + os.sep + 'scripts' + os.sep
libs_path = base_path + 'modules' + os.sep + 'GroqAI' + os.sep + 'libs' + os.sep
GetParams = GetParams  # type: ignore
SetVar = SetVar  # type: ignore
PrintException = PrintException  # type: ignore

if cur_path not in sys.path:
    sys.path.append(cur_path)

# Agregar la carpeta 'libs' al path si no está ya
if libs_path not in sys.path:
    sys.path.append(libs_path)

module = GetParams("module")

from conect_groq import connect_to_groq  # type: ignore
from get_models import get_models  # type: ignore
from generate_text import generate_text  # type: ignore
from ocr_document import process_file  # type: ignore

try:
    if module == "connect":
        api_key = GetParams("api_key")
        result_var = GetParams("result_var")
        connect_to_groq(api_key, result_var, SetVar, PrintException)

    elif module == "get_models":
        result_var = GetParams("result_var")
        get_models(result_var, SetVar, PrintException)

    elif module == "generate_text":
        prompt = GetParams("prompt")
        model = GetParams("model")
        result_var = GetParams("result_var")
        
        # Parámetros opcionales con valores por defecto
        temperature = GetParams("temperature")  # Ahora acepta valores entre 0 y 2
        max_completion_tokens = GetParams("max_tokens")  # Renombrado para coincidir con la API
        stop_sequence = GetParams("stop_sequence")
        
        generate_text(
            prompt=prompt,
            model=model,
            result_var=result_var,
            temperature=temperature,
            max_tokens=max_completion_tokens,  # Pasamos el parámetro con el nombre antiguo por compatibilidad
            stop_sequence=stop_sequence,
            SetVar=SetVar,
            PrintException=PrintException
        )

    elif module == "ocr_document":
        model = GetParams("model")
        file_path = GetParams("file_path")
        result_var = GetParams("result_var")
        process_file(model, file_path, result_var, SetVar, PrintException)
    
    else:
        raise Exception(f"El módulo '{module}' no está implementado.")
except Exception as e:
    PrintException()
    raise e
