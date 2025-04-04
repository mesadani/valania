import os
import sys
import django

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valProject.settings')  # Reemplaza con tu proyecto
django.setup()
import requests
from io import BytesIO
from django.core.files.base import ContentFile
import cloudinary.uploader
# Importar modelos de Django
from valApp.models import Objects
from solan.service import phantom_wallet

def importarDatos():
    objects = Objects.objects.all()
    for obj in objects:
        if obj.mint != "0" and obj.nftImage == "0":
            infoNft = phantom_wallet.get_nft_metadata(obj.mint)
            uri = infoNft.get("uri", "No URI found")
            metadata = phantom_wallet.obtener_json_desde_uri(uri)

            response = requests.get(metadata["image"])

            # Verificamos que la solicitud fue exitosa
            if response.status_code == 200:
                # Convertimos el contenido de la imagen a un archivo que Django puede manejar
                image_content = ContentFile(response.content)
                
                # Subimos la imagen a Cloudinary
                upload_result = cloudinary.uploader.upload(image_content, folder='objects')

                # Guardamos la URL de la imagen subida en el campo de la instancia de tu modelo
                obj.image = upload_result['secure_url']
                obj.description = metadata['description']
                obj.nftImage = metadata['image']
                obj.uri = uri
                obj.save()

                print(f'Imagen subida para {obj.name}: {upload_result["secure_url"]}')

                upload_result['secure_url']  # Devuelve la URL de la imagen subida
            else:
                return None  # Si no se pudo descargar la imagen
            

        if obj.mint != "0":
            supply = getMaxSupplyOne(obj.mint)
            obj.supply = supply
            obj.save()

def getMaxSupplyOne(mint):
    token_accounts = phantom_wallet.getTokenLargestAccounts(mint)

    if not token_accounts:
        print("No se encontraron cuentas para este mint.")
        return None

    # Tomamos solo el primero
    top_account = token_accounts[0]
    account_address = top_account["address"]
    amount = top_account["uiAmount"]
    total = 1000000 - amount
    return total  # Cantidad de tokens (en formato legible)

   
def getMaxSupply(mint):
    token_accounts = phantom_wallet.getTokenLargestAccounts(mint)
    all_owners = []
    
    if not token_accounts:
        print("No se encontraron cuentas para este mint.")
        return []
    all_owners = []
    for account in token_accounts:
        # Extraer la dirección de la cuenta
        account_address = account["address"]
        amount = account["uiAmount"]  # Cantidad de tokens (en formato legible)

        # Obtener el owner de esta cuenta de token
        owner = phantom_wallet.get_owner_from_token_account(account_address)
        if owner:
            all_owners.append(owner)
            print(f"Wallet: {owner} tiene {amount} tokens en la cuenta {account_address}")
        else:
            print(f"🔴 No se pudo obtener el owner para la cuenta {account_address}")


def getNFTPrices(mint_address):
    # Obtener las transacciones relacionadas con el mint
    signatures = phantom_wallet.get_nft_transactions(mint_address,10)

    prices = []
    for signature_info in signatures:
        signature = signature_info["signature"]
        transaction_details = phantom_wallet.getTransactionDetails(signature)

        if transaction_details:
            # Aquí deberías examinar los detalles de la transacción para extraer el precio.
            print(f"Detalles de la transacción: {transaction_details}")
            # Ejemplo: Si la transacción incluye un precio
            price = extract_price_from_transaction(transaction_details)
            if price:
                prices.append(price)

    return prices

def extract_price_from_transaction(transaction_details):
    try:
        # Busca en la transacción los detalles de la compra y precio
        # Este es un ejemplo general. Deberías ajustarlo dependiendo del formato de la transacción
        logs = transaction_details.get("meta", {}).get("logMessages", [])
        for log in logs:
            if "sale" in log:  # Busca un log que indique una venta
                # Extraer el precio de la venta (esto es solo un ejemplo)
                price = extract_price_from_log(log)
                if price:
                    return price
    except Exception as e:
        print(f"Error al extraer precio de la transacción: {e}")
        return None

def extract_price_from_log(log):
    if "precio" in log:  # Reemplaza con lo que busques en los logs
        # Parsear el precio (esto dependerá de cómo se registre el precio)
        price = log.split("precio:")[1].strip()  # Solo un ejemplo, ajusta el formato
        return price
    return None

# Ejemplo de uso
mint_address = 'B1TKjiMGUhGk32v2yYQ5Q7Rhb2a9U8oGABAtNz4CtfSq'
prices = getNFTPrices(mint_address)

if prices:
    print(f"Precios del NFT en el marketplace: {prices}")
else:
    print("No se encontraron precios para este mint.")

#importarDatos()          
#getMaxSupply('B1TKjiMGUhGk32v2yYQ5Q7Rhb2a9U8oGABAtNz4CtfSq')