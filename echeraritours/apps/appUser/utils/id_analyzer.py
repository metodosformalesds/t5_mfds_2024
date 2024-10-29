import requests
import idanalyzer
from django.conf import settings


def verify_document(document_url, biometric_photo):
    try:
        coreapi = idanalyzer.CoreAPI(f"{settings.ID_ANALYZER_API_KEY}", "US")
        coreapi.throw_api_exception(True)
        coreapi.enable_authentication(True, 'quick')

        response = coreapi.scan(
            document_primary=document_url, biometric_photo=biometric_photo)

        if not response:
            print("No se recibió respuesta de la API.")

        if response.get("status") != "success":
            print("Error en la verificación:", response)

        return response

    except idanalyzer.APIError as e:
        details = e.args[0]
        print("API error code: {}, message: {}".format(
            details["code"], details["message"]))
        return None
    except Exception as e:
        print(e)
        return None
