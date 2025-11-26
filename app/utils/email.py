import logging

# Configurar logger
logger = logging.getLogger(__name__)

def enviar_correo(destinatario: str, asunto: str, mensaje: str):
    """
    Simula el envío de un correo electrónico.
    En producción, esto se conectaría a un servidor SMTP.
    """
    logger.info(f"--- SIMULACIÓN DE ENVÍO DE CORREO ---")
    logger.info(f"Para: {destinatario}")
    logger.info(f"Asunto: {asunto}")
    logger.info(f"Mensaje: {mensaje}")
    logger.info(f"-------------------------------------")
    
    print(f"📧 [EMAIL SENT] To: {destinatario} | Subject: {asunto}")
    return True
