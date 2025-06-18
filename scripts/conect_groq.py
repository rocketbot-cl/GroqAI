from groq import Groq  # type: ignore
from groq_client import set_client  # Import function to set client
import traceback  # Para capturar el trace completo del error

# Global variable to store connection
global mod_model_groq

try:
    if not mod_model_groq:  # type: ignore
        mod_model_groq = None
except NameError:
    mod_model_groq = None


def connect_to_groq(api_key, result_var, SetVar, PrintException):
    """
    Conectar a Groq AI usando el SDK oficial y almacenar la conexión globalmente.

    :param api_key: API key para autenticar con Groq AI.
    :param result_var: Nombre de la variable para almacenar el resultado.
    :param SetVar: Función para establecer variables en Rocketbot.
    :param PrintException: Función para imprimir excepciones en Rocketbot.
    """
    global mod_model_groq

    try:
        # Establecer el resultado como False por defecto
        SetVar(result_var, False)
        
        print("Iniciando conexión con Groq AI...")
        print(f"Validando API key: {'*' * (len(api_key)-4) + api_key[-4:] if isinstance(api_key, str) else 'No proporcionada'}")
        
        # Validar que se proporcione la api_key
        if not isinstance(api_key, str):
            error_msg = "ERROR: La API key debe ser una cadena de texto."
            print(error_msg)
            raise Exception(error_msg)
        
        api_key = api_key.strip()
        if not api_key:
            error_msg = "ERROR: La API key es requerida. Por favor, proporcione una API key válida."
            print(error_msg)
            raise Exception(error_msg)
            
        if not api_key.startswith("gsk_"):
            error_msg = "ERROR: La API key debe comenzar con 'gsk_'. Por favor, verifique que está usando una API key válida de Groq."
            print(error_msg)
            raise Exception(error_msg)

        print("Intentando inicializar el cliente de Groq...")
        # Inicializar el cliente de Groq y almacenarlo globalmente
        client = Groq(api_key=api_key)

        try:
            # print("\nListando modelos disponibles...")
            # Obtener la lista de modelos
            models_response = client.models.list()
            
            # Extraer y mostrar los modelos disponibles
            # print("\nModelos disponibles:")
            available_models = []
            for model in models_response.data:
            #     print(f"- {model.id}")
                available_models.append(model.id)
            
            if not available_models:
                print("¡Advertencia! No se encontraron modelos disponibles.")
            
            # Almacenar el cliente globalmente
            set_client(client)
            SetVar(result_var, True)
            print("\n✓ Conexión establecida exitosamente!")

        except Exception as sdk_error:
            error_msg = ""
            if "401" in str(sdk_error):
                error_msg = "ERROR: API key inválida o expirada. Por favor, verifique sus credenciales e intente nuevamente."
            else:
                error_msg = f"ERROR al conectar con Groq AI: {str(sdk_error)}"
            print(error_msg)
            print("Detalles del error:")
            print(traceback.format_exc())
            raise Exception(error_msg)

    except Exception as e:
        # En caso de fallo, asegurarse de que la variable de resultado sea False
        SetVar(result_var, False)
        print("\nError completo:")
        print(traceback.format_exc())
        if PrintException:
            PrintException()
        raise e