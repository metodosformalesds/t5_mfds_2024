import os
import paypalrestsdk
from dotenv import load_dotenv

# Cargar las variables de entorno desde .env
load_dotenv()
# Configurar PayPal SDK
paypalrestsdk.configure({
    "mode": "sandbox", # sandbox o live
    "client_id": os.getenv("PAYPAL_CLIENT_ID"),
    "client_secret": os.getenv("PAYPAL_CLIENT_SECRET")
})