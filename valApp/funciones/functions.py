import os
import sys
import django
from solan.service import phantom_wallet
from django.http import JsonResponse
from django.db.models import Prefetch
import json
from valApp.models import *
from django.db import connection
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



def actualizarPrecios():
    reset_table_objects_prices(ObjectsPrices)
    for object in Objects.objects.all():
        prices = phantom_wallet.getMarketPrices(object.objectCategory.name, object.objectType.name, object.name)

        if len(prices) > 0:
            for price_data in prices:
                amount = price_data['amount']
                price = price_data['price']

                if amount and price:
                # Create or update the ObjectsPrices entry
                    obj_price = ObjectsPrices.objects.create(
                        object=object,
                        price=price,
                        amount=amount
                    )

def reset_table_objects_prices(model):
    # Delete all data from the table
    model.objects.all().delete()

    # Reset the auto-increment field
    with connection.cursor() as cursor:
        # Replace 'your_table_name' with the actual table name
        # The SQL command varies depending on the database
        if connection.vendor == 'sqlite':
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='valApp_objectsprices';")
        elif connection.vendor == 'postgresql':
            cursor.execute("ALTER SEQUENCE valApp_objectsprices RESTART WITH 1;")
        elif connection.vendor == 'mysql':
            cursor.execute("ALTER TABLE valApp_objectsprices AUTO_INCREMENT = 1;")

def importGuilds():
    guilds = phantom_wallet.getGuilds()
    for guild in guilds:
        race = Races.objects.get(name=guild.get("Race"))
        gg = Guilds.objects.create(
            uuid=guild.get("UUID"),
            name=guild.get("Name"),     
            avatar=guild.get("Avatar"),
            tag=guild.get("TAG"),
            race=race,
            description=guild.get("Description"),
            language=guild.get("Languages")[0],
            members=guild.get("Members"),
            announce=guild.get("Announcement"),
            leader=guild.get("LeaderUUID"),
            ranking=guild.get("Ranking"),
            usdc=guild.get("USDC"))
    
def importMembersGuilds():
    guilds = Guilds.objects.all()
    for guilda in guilds:

        
        members = phantom_wallet.getMembersGuilds(guilda.uuid)
        for member in members:
            print(guilda)
            race = Races.objects.get(name=member.get("race"))
            gg = GuildMembers.objects.create(
                name='',
                kkey=member.get("id"),
                address=member.get("address"),
                points=member.get("points"),
                artisan=member.get("artisan"),
                alchemist=member.get("alchemist"),
                architect=member.get("architect"),
                blacksmith=member.get("blacksmith"),
                engineer=member.get("engineer"),
                explorer=member.get("explorer"),
                jeweler=member.get("jeweler"),
                miner=member.get("miner"),
                uuidGuild = member.get("guild"),
                idGuild = guilda)
                
        

# Example usage



         



