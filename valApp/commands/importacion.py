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
from valApp.models import *
from solan.service import phantom_wallet
from valApp.funciones import functions

def importarDatos():
    objects = Objects.objects.all()
    for obj in objects:
        if obj.mint != "0" and obj.nftImage == "0":
            infoNft = phantom_wallet.get_nft_metadata(obj.mint)
            print(infoNft)
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
    signatures = phantom_wallet.get_nft_transactions(mint_address,50)

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

def importacionValania():
    nfts = phantom_wallet.get_nfts('FiG8tbM9RMnJWS7ezFqVzJsGzCRHV3V9e4kaSwZ6vzmR')
    
       
      
    data =  phantom_wallet.extract_nft_info_extends({"nfts": nfts})



import requests
from datetime import datetime

def verificar_listado_nft(mint):
    url = "https://mainnet.helius-rpc.com/?api-key=a3d88e42-62d1-4f91-b43d-a316f334fc45"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getNftEditions",
        "params": [
            {
                "query": {
                    "mint": mint
                },
                "options": {
                    "limit": 50,
                    "sortOrder": "desc"
                }
            }
        ]
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        print("❌ Error al consultar la API de Helius:")
        print(response.text)
        return

    data = response.json()
    eventos = data.get("result", {}).get("result", [])

    ultimo_listado = None

    for evento in eventos:
        tipo = evento.get("type")
        if tipo == "NFT_LISTING":
            ultimo_listado = evento
            break
        elif tipo in ["NFT_CANCEL_LISTING", "NFT_SALE"]:
            break

    if ultimo_listado:
        precio_sol = evento.get("amount", 0) / 1e9
        marketplace = evento.get("source", "Desconocido")
        fecha = datetime.utcfromtimestamp(evento.get("timestamp", 0)).strftime('%Y-%m-%d %H:%M:%S')
        print(f"✅ El NFT está listado en {marketplace} por {precio_sol} SOL (desde {fecha} UTC)")
    else:
        print("❌ El NFT no está listado actualmente.")



def traspaso_animation():
    heroes = Heroes.objects.all()
    for hero in heroes:
        object_with_animation = Objects.objects.filter(name__icontains=hero.name).first()
        if object_with_animation:
            animation = object_with_animation.animation
            hero.animation = animation
            hero.mint = object_with_animation.mint
            hero.nftImage = object_with_animation.nftImage
            hero.uri = object_with_animation.uri
            hero.save()
        else:
            print(f"No se encontró un objeto para el héroe: {hero.name}")


def probar():
     for object in Objects.objects.all():
         print(object.objectType.name)
         if(object.objectType.name=="Swords"):
            print(object)
            prices = phantom_wallet.getMarketPrices(object.objectCategory.name, object.objectType.name, object.name)      
            print(prices)

functions.actualizarPrecios()
#phantom_wallet.get_closable_accounts('GqGGU5onmSoQQVL1YKXFk5ALQuwWqK8A8y5TedFmcqy6');
#functions.importMembersGuilds()        
#verificar_listado_nft("6o4AZhaqmLuBrf8Sy8tGgTxZ5uPkcsbPiNTvCLbSA8NC")
#importarDatos()
#traspaso_animation()
#getNFTPrices("B1TKjiMGUhGk32v2yYQ5Q7Rhb2a9U8oGABAtNz4CtfSq")
#getMaxSupply('B1TKjiMGUhGk32v2yYQ5Q7Rhb2a9U8oGABAtNz4CtfSq')