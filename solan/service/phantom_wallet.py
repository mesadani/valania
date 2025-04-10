# myapp/services/phantom_wallet.py
import base58
import base64
import requests
from solana.rpc.api import Client  # Este es el cliente para interactuar con Solana
from solders.pubkey import Pubkey
from valApp.models import Objects, ObjectCategorys, ObjectTypes
from django.core.files.base import ContentFile
from django.db import transaction
import cloudinary.uploader
SOLANA_API_URL = "https://rpc.helius.xyz/?api-key=a3d88e42-62d1-4f91-b43d-a316f334fc45"
client = Client(SOLANA_API_URL)

def get_balance(wallet_address):
    """
    Función para obtener el saldo de una wallet en la blockchain de Solana.
    """
    headers = {
        "Content-Type": "application/json",
    }

    # JSON para la solicitud RPC
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getBalance",
        "params": [wallet_address],
    }

    response = requests.post(SOLANA_API_URL, json=payload, headers=headers)

    if response.status_code == 200:
        result = response.json()
        return result.get('result', {}).get('value', 0)
    else:
        raise Exception("Error al consultar el saldo de la wallet")


METADATA_PROGRAM_ID = Pubkey.from_string("metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s")




def get_nft_metadata(mint_address):
    mint_pubkey = Pubkey.from_string(mint_address)

    metadata_seeds = [
        b"metadata",
        bytes(METADATA_PROGRAM_ID),
        bytes(mint_pubkey)
    ]

    metadata_account, _ = Pubkey.find_program_address(metadata_seeds, METADATA_PROGRAM_ID)

    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getAccountInfo",
        "params": [str(metadata_account), {"encoding": "base64"}],
    }

    response = requests.post(SOLANA_API_URL, json=payload, headers=headers)

    if response.status_code == 200:
        result = response.json().get("result", {}).get("value", {})
        if not result:
            return {"error": "No se encontró metadata para esta mint"}

        # Extraer datos Base64
        data_base64 = result.get("data", [None])[0]
        if not data_base64:
            return {"error": "No se pudo obtener la metadata"}

        # Decodificar la data Base64
        metadata_bytes = base64.b64decode(data_base64)

        # Extraer la URI (está en una posición específica)
        uri_start = metadata_bytes.find(b'http')
        uri_end = metadata_bytes.find(b'\x00', uri_start)  # Buscar el fin de la URL

        if uri_start == -1 or uri_end == -1:
            return {"error": "No se pudo extraer la URI"}

        uri = metadata_bytes[uri_start:uri_end].decode("utf-8")
        return {"uri": uri}

    else:
        return {"error": "Error al consultar la metadata"}

def get_nfts(wallet_address):
    headers = {
        "Content-Type": "application/json",
    }

    # JSON para la solicitud RPC
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTokenAccountsByOwner",
        "params": [wallet_address,
            {
                "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
            },
            {
                "encoding": "jsonParsed"
            }
        ],
    }

    response = requests.post(SOLANA_API_URL, json=payload, headers=headers)

    if response.status_code == 200:
        result = response.json()
        return result.get('result', {}).get('value', 0)
    else:
        raise Exception("Error al consultar el saldo de la wallet")

def get_owner_from_token_account(account_address):
    headers = {
        "Content-Type": "application/json",
    }

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getAccountInfo",
        "params": [
            account_address,
            {"encoding": "jsonParsed"}
        ]
    }

    response = requests.post(SOLANA_API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        result = response.json()["result"]["value"]
        if result:
            owner = result["data"]["parsed"]["info"]["owner"]
            return owner
        else:
            return None
    else:
        print("Error al obtener el owner", response.status_code)
        return None
def get_nft_supply(mint):
    """
    Función para obtener el saldo de una wallet en la blockchain de Solana.
    """
    headers = {
        "Content-Type": "application/json",
    }

    # JSON para la solicitud RPC
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTokenSupply",
        "params": [mint],
    }

    response = requests.post(SOLANA_API_URL, json=payload, headers=headers)

    if response.status_code == 200:
        result = response.json()
        print(result)

        return result.get('result', {}).get('value', 0)
    else:
        raise Exception("Error al consultar el saldo de la wallet")
    
def getTokenAccountsByMint(mint):

    headers = {
        "Content-Type": "application/json",
    }

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTokenAccountsByMint",
        "params": [mint, {"encoding": "jsonParsed"}],
    }

    response = requests.post(SOLANA_API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        # Obtener todas las cuentas de token asociadas al mint
        token_accounts = response.json().get("result", {}).get("value", [])
        return token_accounts
    else:
        raise Exception("Error al consultar las cuentas del mint")
def getTokenLargestAccounts(mint):
    """
    
    """
    headers = {
        "Content-Type": "application/json",
    }

    # JSON para la solicitud RPC
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTokenLargestAccounts",
        "params": [mint],
    }

    response = requests.post(SOLANA_API_URL, headers=headers, json=payload)

    
    if response.status_code == 200:
        largest_accounts = response.json()["result"]["value"]
        result = largest_accounts
        return result
    else:
        raise Exception("Error al consultar el saldo de la wallet")    
    
def getTransactionDetails(signature):
    """
    Obtiene los detalles de una transacción para ver el precio de un NFT.
    """
    headers = {
        "Content-Type": "application/json",
    }

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [signature, {"encoding": "jsonParsed"}],
    }

    response = requests.post(SOLANA_API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json().get("result", {})
    else:
        print(f"Error al obtener detalles de la transacción: {response.status_code}")
        return None

def get_nft_transactions(mint,limit):
    """
    Función para obtener el saldo de una wallet en la blockchain de Solana.
    """
    headers = {
        "Content-Type": "application/json",
    }

    # JSON para la solicitud RPC
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [mint,{"limit": limit}],
    }

    response = requests.post(SOLANA_API_URL, json=payload, headers=headers)
    
    if response.status_code == 200:

        result = response.json()
        return result.get('result', {})
    else:
        raise Exception("Error al consultar trasnsacciones")

def extract_nft_info(nft_data):
    nft_list = []

    for nft in nft_data.get("nfts", []):  # Recorre la lista de NFTs
        try:
            info = nft["account"]["data"]["parsed"]["info"]
            mint = info["mint"]
            amount = info["tokenAmount"]["amount"]
            decimals = info["tokenAmount"]["decimals"]

            uri_data = get_nft_metadata(mint)  # Obtener URI de la metadata
            uri = uri_data.get("uri", "No URI found")
            category_value = '';
            type_value = '';
            if "valannia" in uri.lower():
                metadata = obtener_json_desde_uri(uri)  # Obtener datos del JSON
                if amount != '0':
                    nombreBd = Objects.objects.filter(name=metadata['name']).first()
                    if nombreBd:
                        if nombreBd.mint == '0':
                            nombreBd.mint = mint
                            nombreBd.uri = uri
                            nombreBd.save() 
                            print(f"objti creadoPPP: {metadata['name']}")
                        else:
                            print(f"objti existente: {metadata['name']}")
                    else:
                
                        if 'attributes' in metadata:
                            for atributo in metadata['attributes']:
                                if atributo['trait_type'] == 'category':
                                    category_value = atributo['value']
                                elif atributo['trait_type'] == 'type':
                                    type_value = atributo['value']

                            
                            if category_value != '' and type_value != '':
                                response = requests.get(metadata["image"])
                                final = '';
                            # Verificamos que la solicitud fue exitosa
                                if response.status_code == 200:
                                    # Convertimos el contenido de la imagen a un archivo que Django puede manejar
                                    image_content = ContentFile(response.content)                                
                                    # Subimos la imagen a Cloudinary
                                    upload_result = cloudinary.uploader.upload(image_content, folder='objects')

                                    final = upload_result['secure_url']

                                object_category, _ = ObjectCategorys.objects.get_or_create(name=category_value)
                                object_type, _ = ObjectTypes.objects.get_or_create(name=type_value)
                                Objects.objects.create(
                                    name=metadata['name'], 
                                    description=metadata['description'], 
                                    objectType=object_type, 
                                    objectCategory=object_category,
                                    image= final,
                                    mint=mint,
                                    uri=uri,
                                    nftImage=metadata['image'],
                                    supply=int(amount))
                                print(f"objti creado: {metadata['name']}")   
                            else:
                                print(f"no: {metadata['name']}")    

                             
                                
                                # Realiza la acción que corresponde cuando tiene 'attributes'
                        else:
                            print("Este JSON NO tiene 'attributes'.")
                        

                    nft_list.append({
                        "mint": mint,
                        "amount": amount,
                        "decimals": decimals,
                        "name": metadata['name'],
                        "image": metadata['image'],
                        "metadata" : metadata
                    })
        except KeyError:
            continue  # Si falta alguna clave, simplemente lo ignora

    return nft_list
def obtener_json_desde_uri(uri):
    """
    Descarga el JSON desde la URI y devuelve su contenido.
    """
    try:
        response = requests.get(uri, timeout=5)  # Tiempo máximo de espera: 5 segundos
        response.raise_for_status()  # Lanza una excepción si la respuesta tiene error (4xx o 5xx)
        return response.json()  # Convertimos la respuesta en un diccionario
    except requests.exceptions.RequestException as e:
        return {"error": f"No se pudo obtener el JSON: {str(e)}"}



def get_or_create_object_category_and_type(metadata):
    """Obtiene o crea una categoría y tipo de objeto"""
    category_value = ''
    type_value = ''
    if 'attributes' in metadata:
        for atributo in metadata['attributes']:
            if atributo['trait_type'] == 'category':
                category_value = atributo['value']
            elif atributo['trait_type'] == 'type':
                type_value = atributo['value']
    return category_value, type_value


def upload_image_from_url(image_url):
    """Descarga y sube la imagen a Cloudinary, devuelve la URL segura"""
    response = requests.get(image_url)
    if response.status_code == 200:
        image_content = ContentFile(response.content)
        upload_result = cloudinary.uploader.upload(image_content, folder='objects')
        return upload_result['secure_url']
    return None

def getInfoNft(metadata, mint, uri, amount):
    return {
                "mint": mint,
                "amount": amount,
                "decimals": metadata.get("tokenAmount", {}).get("decimals", 0),
                "name": metadata['name'],
                "image": metadata['image'],
                #"metadata": metadata
            }
def create_or_update_object(metadata, mint, uri, amount):
    """Crea o actualiza un objeto en la base de datos"""
    category_value, type_value = get_or_create_object_category_and_type(metadata)

    if category_value and type_value:
        final_image_url = upload_image_from_url(metadata["image"])

        # Usar `get_or_create` de manera eficiente con las relaciones
        object_category, _ = ObjectCategorys.objects.get_or_create(name=category_value)
        object_type, _ = ObjectTypes.objects.get_or_create(name=type_value)

        # Usamos `select_related` para evitar consultas adicionales
        existing_object = Objects.objects.select_related('objectType', 'objectCategory').filter(name=metadata['name']).first()

        if amount != '0':
            if existing_object:
                if existing_object.mint == '0':
                    # Actualizamos el objeto existente
                    existing_object.mint = mint
                    existing_object.uri = uri
                    existing_object.save()
                    print(f"objti actualizado: {metadata['name']}")
                else:
                    print(f"objti ya existe: {metadata['name']}")
            else:
                # Si no existe el objeto, lo creamos
                new_object = Objects.objects.create(
                    name=metadata['name'],
                    description=metadata['description'],
                    objectType=object_type,
                    objectCategory=object_category,
                    image=final_image_url,
                    mint=mint,
                    uri=uri,
                    nftImage=metadata['image'],
                    supply=int(amount)
                )
                print(f"objti creado: {metadata['name']}")

            return {
                "mint": mint,
                "amount": amount,
                "decimals": metadata.get("tokenAmount", {}).get("decimals", 0),
                "name": metadata['name'],
                "image": metadata['image'],
                "metadata": metadata
            }
    else:
        print(f"no: {metadata['name']}")
    return None


@transaction.atomic  # Usamos transacciones para garantizar la integridad de las operaciones
def extract_nft_info_extends(nft_data):
    nft_list = []

    for nft in nft_data.get("nfts", []):  # Recorre la lista de NFTs
        try:
            info = nft["account"]["data"]["parsed"]["info"]
            mint = info["mint"]
            amount = info["tokenAmount"]["amount"]
            decimals = info["tokenAmount"]["decimals"]

            uri_data = get_nft_metadata(mint)  # Obtener URI de la metadata
            uri = uri_data.get("uri", "No URI found")

            if "valannia" in uri.lower():
                metadata = obtener_json_desde_uri(uri)  # Obtener datos del JSON
                #nft_info = create_or_update_object(metadata, mint, uri, amount)
                #if nft_info:
                    #nft_list.append(nft_info)
                nftInfo = getInfoNft(metadata, mint, uri, amount)
                nft_list.append(nftInfo)
        except KeyError as e:
            print(f"Error de clave: {e}")  # Para depuración más detallada
            continue  # Si falta alguna clave, simplemente lo ignora

    return nft_list
