# myapp/services/phantom_wallet.py
import requests
from solana.rpc.api import Client  # Este es el cliente para interactuar con Solana

SOLANA_API_URL = "https://api.mainnet-beta.solana.com"
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

