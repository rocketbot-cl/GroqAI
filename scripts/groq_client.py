# Variable global para almacenar la conexión
mod_model_groq = None

def set_client(client):
    """
    Establece el cliente global de groq.
    """
    global mod_model_groq
    mod_model_groq = client

def get_client():
    """
    Obtiene el cliente global de groq.
    """
    global mod_model_groq
    return mod_model_groq