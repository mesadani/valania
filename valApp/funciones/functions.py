import os
import sys
import django
from solan.service import phantom_wallet
from django.http import JsonResponse
from django.db.models import Prefetch
import json
from valApp.models import *
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

def get_nft_data(nft):
    return {
        'id': nft.id,
        'name': nft.name,
        'description': nft.description,
        'image': nft.image.url if nft.image else '',
    }


def get_crafting_details(nft,data):
    try:
        crafting = Crafting.objects.select_related('object__objectType', 'object__objectCategory', 'proffesion').get(object=nft.id)

        requirements = craftingRequirements.objects.select_related('object').filter(craft=crafting)
        have = 0
        data_dict = {item['name']: item['amount'] for item in data}

        requirements_list = [{
            'id': req.object.id,
            'name': req.object.name,
            'quantity': req.quantity,
            'image': req.object.image.url if req.object.image else '',
            'have': data_dict.get(req.object.name, 0)
        } for req in requirements]

        type_slug = crafting.object.objectType.name.replace(" ", "-").lower()
        kind_slug = crafting.object.name.replace(" ", "-").lower()

        market_url = f'https://market.valannia.com/market/{crafting.object.objectCategory.name}?type={type_slug}&kind={kind_slug}'
        profession_url = f'https://market.valannia.com/realms/professions/{crafting.proffesion.name.lower().replace(" ", "-")}'

        have = 0

# Iterar sobre la lista de datos para encontrar el objeto
        for item in data:
            if crafting.object.name == item['name']:
                have = item['amount']
                break 
            
        return [{
            'crafting_name': crafting.object.name,
            'level': crafting.level,
            'quantity': crafting.quantity,
            'probability': crafting.probability,
            'time': crafting.time,
            'profesion': crafting.proffesion.name,
            'urlMarket': market_url,
            'urlPorfession': profession_url,
            'supply': crafting.object.supply,
            'image': crafting.object.image.url if crafting.object.image else '',
            'requirements': requirements_list,
            'have': have,
        }]
    except Crafting.DoesNotExist:
        return []

def get_inverse_crafting_details(nft,data):
    inverse_reqs = craftingRequirements.objects.filter(object=nft.id).select_related(
        'craft__object', 'craft__proffesion'
    )
    data_dict = {item['name']: item['amount'] for item in data}
    return [{
        'id': req.craft.object.id,
        'crafting_name': req.craft.object.name,
        'level': req.craft.level,
        'quantity': req.craft.quantity,
        'probability': req.craft.probability,
        'time': req.craft.time,
        'image': req.craft.object.image.url if req.craft.object.image else '',
        'profesion': req.craft.proffesion.name,
        'have': data_dict.get(req.craft.object.name, 0)
    } for req in inverse_reqs]
