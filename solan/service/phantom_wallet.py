# myapp/services/phantom_wallet.py
import base58
import base64
import requests
from solana.rpc.api import Client  # Este es el cliente para interactuar con Solana
from solders.pubkey import Pubkey
from valApp.models import Objects

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

            if "valannia" in uri.lower():
                metadata = obtener_json_desde_uri(uri)  # Obtener datos del JSON
                if amount != '0':
                    nombreBd = Objects.objects.filter(name=metadata['name']).first()
                    if nombreBd:
                        nombreBd.mint = mint
                        nombreBd.uri = uri
                        nombreBd.save()              

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
