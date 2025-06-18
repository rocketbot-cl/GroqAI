from groq_client import get_client  # Import function to get client
import traceback  # For capturing error traces


def get_models(result_var, SetVar, PrintException):
    """
    Obtiene la lista de modelos disponibles usando el cliente global de Groq.

    :param result_var: Nombre de la variable para almacenar la lista de modelos.
    :param SetVar: Función para establecer variables en Rocketbot.
    :param PrintException: Función para imprimir excepciones en Rocketbot.
    """
    try:
        print("\n=== Obteniendo lista de modelos de Groq AI ===")
        
        # Establecer resultado por defecto
        SetVar(result_var, [])
        
        # Obtener el cliente
        client = get_client()
        if not client:
            error_msg = "ERROR: Debe conectarse a Groq AI antes de usar este comando. Por favor, ejecute primero el módulo de conexión."
            print(error_msg)
            raise Exception(error_msg)

        print("Obteniendo modelos disponibles...")
        # Obtener la lista de modelos
        response = client.models.list()

        # Extraer los IDs de los modelos
        model_ids = [model.id for model in response.data]
        
        if not model_ids:
            print("¡Advertencia! No se encontraron modelos disponibles.")
        else:
            print("\nModelos disponibles:")
            for model_id in model_ids:
                print(f"- {model_id}")

        # Guardar la lista en la variable de resultado
        SetVar(result_var, model_ids)
        print("\n✓ Lista de modelos obtenida exitosamente!")

    except Exception as e:
        error_msg = f"Error al obtener la lista de modelos: {str(e)}"
        print(error_msg)
        print("\nDetalles del error:")
        print(traceback.format_exc())
        if PrintException:
            PrintException()
        raise Exception(error_msg)