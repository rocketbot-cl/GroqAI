from groq_client import get_client  # Import function to get client
import traceback  # For capturing error traces
from groq._exceptions import BadRequestError  #type: ignore


def generate_text(prompt, model, result_var, temperature, max_tokens, stop_sequence, SetVar, PrintException):
    """
    Genera texto usando el cliente de Groq AI y asigna el resultado a la variable especificada.

    :param prompt: El prompt de entrada para la generación de texto.
    :param model: El modelo a usar para la generación de texto.
    :param result_var: Nombre de la variable para almacenar el texto generado.
    :param temperature: Temperatura para la generación (entre 0 y 2).
    :param max_tokens: Número máximo de tokens a generar.
    :param stop_sequence: Secuencia opcional para detener la generación.
    :param SetVar: Función para establecer variables en Rocketbot.
    :param PrintException: Función para imprimir excepciones en Rocketbot.
    """
    try:
        print("\n=== Generando texto con Groq AI ===")
        
        # Establecer resultado por defecto
        SetVar(result_var, None)
        
        # Obtener el cliente
        client = get_client()
        if not client:
            error_msg = "ERROR: Debe conectarse a Groq AI antes de usar este comando. Por favor, ejecute primero el módulo de conexión."
            print(error_msg)
            raise Exception(error_msg)

        # Validar parámetros requeridos
        if not prompt:
            error_msg = "ERROR: El prompt es requerido."
            print(error_msg)
            raise Exception(error_msg)
            
        if not model:
            error_msg = "ERROR: El modelo es requerido."
            print(error_msg)
            raise Exception(error_msg)

        # Convertir parámetros a sus tipos correctos
        try:
            temp = float(temperature) if temperature else 0.7
            max_tok = int(max_tokens) if max_tokens else 100
            stop = [stop_sequence] if stop_sequence else None
        except ValueError as e:
            error_msg = f"ERROR: Error al convertir parámetros: {str(e)}"
            print(error_msg)
            raise Exception(error_msg)

        print("\nParámetros de generación:")
        print(f"- Modelo: {model}")
        print(f"- Temperatura: {temp}")
        print(f"- Máximo de tokens: {max_tok}")
        print(f"- Secuencia de parada: {stop}")
        
        print("\nGenerando respuesta...")
        # Crear la solicitud de chat completion
        try:
            response = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=model,
                temperature=temp,
                max_completion_tokens=max_tok,
                stop=stop
            )
        except BadRequestError as e:
            if "model_decommissioned" in str(e):
                error_msg = f"ERROR: El modelo '{model}' ha sido descontinuado y ya no está soportado.\n\nPara ver los modelos disponibles puede:\n1. Ejecutar el comando 'Obtener modelos disponibles' del módulo\n2. Consultar la documentación oficial en https://console.groq.com/docs/models"
                print(error_msg)
                raise Exception(error_msg)
            raise e

        # Extraer el texto generado
        generated_text = response.choices[0].message.content
        
        print("\n✓ Texto generado exitosamente!")
        
        # Guardar el resultado
        SetVar(result_var, generated_text)

    except Exception as e:
        error_msg = f"Error al generar texto: {str(e)}"
        print(error_msg)
        print("\nDetalles del error:")
        print(traceback.format_exc())
        if PrintException:
            PrintException()
        raise Exception(error_msg)
