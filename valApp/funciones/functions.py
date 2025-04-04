import os
import sys
import django
from solan.service import phantom_wallet

def getMaxSupply(mint):
    token_accounts = phantom_wallet.getTokenLargestAccounts(mint)
    all_owners = []
    
    if not token_accounts:
        return []
    all_owners = []
    for account in token_accounts:
        # Extraer la dirección de la cuenta
        account_address = account["address"]
        amount = account["uiAmount"]  # Cantidad de tokens (en formato legible)

        # Obtener el owner de esta cuenta de token
        owner = phantom_wallet.get_owner_from_token_account(account_address)
        if owner:
            all_owners.append({
                'owner': owner,
                'amount': amount,
                'account_address': account_address,
                
            })

    return all_owners