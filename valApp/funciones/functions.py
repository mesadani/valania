import os
import sys
import django
from solan.service import phantom_wallet
from django.http import JsonResponse
from django.db.models import Prefetch,OuterRef, Subquery
import json
from valApp.models import *
from django.db import connection
from django.db.models import Max,Min, F
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db import transaction

def get_guild_and_members_by_username(username):
    try:
        # Obtener el miembro del guild usando el username como address
        guild_member = GuildMembers.objects.get(address=username)
        
        # Obtener la guild del miembro
        guild = guild_member.guild
        
        # Obtener todos los miembros de la misma guild
        guild_members = GuildMembers.objects.filter(guild=guild)
        
        # Preparar la información para devolver
        guild_info = {
            'guild_name': guild.name,
            'guild_description': guild.description,
            'tag': guild.tag,
            'image': guild.avatar,
            'guild_members': [
                {
                    'name': member.name,
                    'address': member.address,
                    'role': member.roleuuid,
                    'points': member.points,
                    # Agrega más campos según sea necesario
                }
                for member in guild_members
            ]
        }
        
        return guild_info
    
    except GuildMembers.DoesNotExist:
        return {}
    
def top_10_least_expensive_by_category():
    categories = ObjectCategorys.objects.all()
    top_10_least_expensive_by_category = {}

    for category in categories:
        top_10_least_expensive_by_category[category.name] = (
            Objects.objects.filter(objectCategory=category)
            .filter(objectsprices_set__price__gt=0)
            .annotate(min_price=Min('objectsprices_set__price'))
            .annotate(amount=F('objectsprices_set__amount'))
            .order_by('min_price')[:10]
        )
    return top_10_least_expensive_by_category
def top_10_most_expensive_by_category():
    categories = ObjectCategorys.objects.all()
    top_10_most_expensive_by_category = {}

    for category in categories:
        top_10_most_expensive_by_category[category.name] = (
            Objects.objects.filter(objectCategory=category)
            .annotate(max_price=Max('objectsprices_set__price'))
            .annotate(amount=F('objectsprices_set__amount'))
            .order_by('-max_price')[:10]
        )
    return top_10_most_expensive_by_category
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

def get_crafting_details_profession(nft,data,amountT):
    try:
       
        crafting = Crafting.objects.select_related('object__objectType', 'object__objectCategory', 'proffesion').get(object=nft.id)
      
        requirements = craftingRequirements.objects.select_related('object').filter(craft=crafting)
       

       ##### requirements_list = [{
        #    'id': req.object.id,
        #    'name': req.object.name,
        #    'quantity': req.quantity,
       #     'image': req.object.image.url if req.object.image else '',
        #    'have': data_dict.get(req.object.name, 0),
        #    'price': req.object.objectsprices_set.first().price if req.object.objectsprices_set.exists() else 0

      #  } for req in requirements]
        
        totalPrice = 0

        requirements_list = []
        for req in requirements:
            # Obtener el precio más bajo del objeto
            lowest_price = ObjectsPrices.objects.filter(object=req.object).order_by('price').first()
           
            if lowest_price is not None:
                type_slug = lowest_price.object.objectType.name.replace(" ", "-").lower()
                kind_slug = lowest_price.object.name.replace(" ", "-").lower()
                market_url = f'https://market.valannia.com/market/{lowest_price.object.objectCategory.name}?type={type_slug}&kind={kind_slug}'
            else:

                lowest_price = Objects.objects.get(id=req.object.id)       
                type_slug = lowest_price.objectType.name.replace(" ", "-").lower()
                kind_slug = lowest_price.name.replace(" ", "-").lower()
                market_url = f'https://market.valannia.com/market/{lowest_price.objectCategory.name}?type={type_slug}&kind={kind_slug}'

            
            requirements_list.append({
                'id': req.object.id,
                'name': req.object.name,
                'quantity': int(req.quantity),
                'image': req.object.image.url if req.object.image else '',
                'marketUrl': market_url
            })

        
        return requirements_list
    except Crafting.DoesNotExist:
        return []
def get_crafting_details(nft,data,amountT):

    try:
       
        crafting = Crafting.objects.select_related('object__objectType', 'object__objectCategory', 'proffesion').get(object=nft.id)
      
        requirements = craftingRequirements.objects.select_related('object').filter(craft=crafting)
        have = 0
        data_dict = {item['name']: item['amount'] for item in data}

       ##### requirements_list = [{
        #    'id': req.object.id,
        #    'name': req.object.name,
        #    'quantity': req.quantity,
       #     'image': req.object.image.url if req.object.image else '',
        #    'have': data_dict.get(req.object.name, 0),
        #    'price': req.object.objectsprices_set.first().price if req.object.objectsprices_set.exists() else 0

      #  } for req in requirements]
        
        totalPrice = 0
        totalNecesitas = 0;
        requirements_list = []
        for req in requirements:
            # Obtener el precio más bajo del objeto
            lowest_price = ObjectsPrices.objects.filter(object=req.object).order_by('price').first()
   
            price_value = lowest_price.price if lowest_price is not None else 0
     
            have = int(data_dict.get(req.object.name, 0))
            necesitas = int(req.quantity) * int(amountT)
            
            necesitasPrecio = (int(req.quantity) * int(amountT)) * price_value
            if have > 0:
                necesitas =(int(req.quantity) * int(amountT)) - have
                necesitasPrecio = necesitas * price_value
                if necesitasPrecio < 0:
                    necesitasPrecio = 0
                totalNecesitas+= necesitasPrecio
            else:
                totalNecesitas+=necesitasPrecio
           
            totalPrice+=price_value * int((req.quantity * amountT))
           
            if lowest_price is not None:
                type_slug = lowest_price.object.objectType.name.replace(" ", "-").lower()
                kind_slug = lowest_price.object.name.replace(" ", "-").lower()
                market_url = f'https://market.valannia.com/market/{lowest_price.object.objectCategory.name}?type={type_slug}&kind={kind_slug}'
            else:

                lowest_price = Objects.objects.get(id=req.object.id)
        
                type_slug = lowest_price.objectType.name.replace(" ", "-").lower()
                kind_slug = lowest_price.name.replace(" ", "-").lower()
                market_url = f'https://market.valannia.com/market/{lowest_price.objectCategory.name}?type={type_slug}&kind={kind_slug}'
            
       
            
            
   
            
            requirements_list.append({
                'id': req.object.id,
                'name': req.object.name,
                'quantity': int(req.quantity) * int(amountT),
                'image': req.object.image.url if req.object.image else '',
                'have': have,
                'price': price_value,
                'necesitas':necesitas,
                'necesitasPrecio':necesitasPrecio,
                'marketUrl': market_url
            })


        
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
            
        precio =0;            
        priceActual = ObjectsPrices.objects.filter(object=crafting.object.id).only('price').first()
        if priceActual:
            precio = priceActual.price   
        
        return [{
            'crafting_name': crafting.object.name,
            'level': crafting.level,
            'quantity': crafting.quantity ,
            'probability': crafting.probability,
            'time': crafting.time,
            'profesion': crafting.proffesion.name,
            'urlMarket': market_url,
            'urlPorfession': profession_url,
            'supply': crafting.object.supply,
            'image': crafting.object.image.url if crafting.object.image else '',
            'requirements': requirements_list,
            'have': have,
            'precio' :precio,
            'totalPrice':totalPrice,
            'totalNecesitas':totalNecesitas
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
    reset_table_objects_prices(ObjectsPrices,'valApp_objectsprices')
    reset_table_objects_prices(ObjectsBuyPrices,'valApp_objectsbuyprices')

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

        pricesBuy = phantom_wallet.getMarketActions(object.objectCategory.name, object.objectType.name, object.name)

        if len(pricesBuy) > 0:
            for price_buy_data in pricesBuy:
                amount = price_buy_data['amount']
                price = price_buy_data['price']

                if amount and price:
                # Create or update the ObjectsPrices entry
                    obj_price = ObjectsBuyPrices.objects.create(
                        object=object,
                        price=price,
                        amount=amount
                    )
                    

from django.db import connection

def reset_table_objects_prices(model, table_name):
    # Delete all data from the table
    model.objects.all().delete()

    # Reset the auto-increment field
    with connection.cursor() as cursor:
        # Use parameterized queries to prevent SQL injection
        if connection.vendor == 'sqlite':
            cursor.execute("DELETE FROM sqlite_sequence WHERE name=%s;", [table_name])
        elif connection.vendor == 'postgresql':
            cursor.execute(f"ALTER SEQUENCE {table_name}_id_seq RESTART WITH 1;")
        elif connection.vendor == 'mysql':
            cursor.execute(f"ALTER TABLE {table_name} AUTO_INCREMENT = 1;")


def importGuilds():
    guilds = phantom_wallet.getGuilds()
    for guild in guilds:
        race = Races.objects.get(name=guild.get("Race"))
        gg, created = Guilds.objects.update_or_create(
                uuid=guild.get("UUID"),
                defaults={
                    'uuid':guild.get("UUID"),
                    'name':guild.get("Name"),     
                    'avatar':guild.get("Avatar"),
                    'tag':guild.get("TAG"),
                    'race':race,
                    'description':guild.get("Description"),
                    'language':guild.get("Languages")[0],
                    'members':guild.get("Members"),
                    'announce':guild.get("Announcement"),
                    'leader':guild.get("LeaderUUID"),
                    'ranking':guild.get("Ranking"),
                    'usdc':guild.get("USDC")
                }
            )

def membersGuilds(members,guilda):
    for member in members:
            
            race = Races.objects.get(name=member.get("race"))
            gg, created = GuildMembers.objects.update_or_create(
                address=member.get("address"),
                defaults={
                    'name': '',
                    'idRank': member.get("id"),
                    'points': member.get("points"),
                    'artisan': member.get("artisan"),
                    'alchemist': member.get("alchemist"),
                    'architect': member.get("architect"),
                    'blacksmith': member.get("blacksmith"),
                    'engineer': member.get("engineer"),
                    'explorer': member.get("explorer"),
                    'jeweler': member.get("jeweler"),
                    'miner': member.get("miner"),
                    'uuidGuild': member.get("guild"),
                    'guild': guilda,
                    'race' :race    # asegurate que el campo se llame 'guild' y no 'idGuild'
                }
            ) 
def importMembersGuilds():
    guilds = Guilds.objects.all()
    for guilda in guilds:

        
        members = phantom_wallet.getMembersGuildsRank(guilda.uuid)
      
        #memberGuild(members,guilda);
            
        membersGuild = phantom_wallet.getMembersGuilds(guilda.uuid)
        
        for memberGuild in membersGuild:
      
            
            profession = memberGuild.get('Profession', '').strip()  # strip para limpiar espacios
            prof = None
            if profession:
                if profession == 'Engineer':
                    prof = 'Engineering'
                elif profession == 'Explorer':
                    prof = 'Exploration'
                elif profession == 'Alchemist':
                    prof = 'Alchemy'
                elif profession == 'Architect':
                    prof = 'Architecture'
                elif profession == 'Jeweler':
                    prof = 'Jewelry'
                elif profession == 'Blacksmith':
                    pro = 'Blacksmith'
                elif profession == 'Miner':
                    prof = 'Mining'
                elif profession == 'Artisan':
                    prof = 'Artisan'
 

            if prof is not None:
                print(f"Profesión encontrada: {prof}")
                prof = Professions.objects.get(name=prof)  

            hkind = memberGuild.get('HeroKind', '').strip()  # strip para limpiar espacios

            if hkind:
                heroKind = memberGuild['HeroKind']
                heroLvl = memberGuild['HeroLevel']
            else:
                heroKind = ''
                heroLvl = 0


            gg, created = GuildMembers.objects.update_or_create(
                address=memberGuild['Address'],
                defaults={
                    'name': memberGuild['Name'],
                    'avatar': memberGuild['Avatar'],
                    'usdc': memberGuild['USDC'],
                    'ranking': memberGuild['Ranking'],
                    'herokind': heroKind,
                    'heroLvl': heroLvl,
                    'profession': prof,
                    'guild': guilda,
                    'professionMastery': memberGuild.get('ProfessionMastery', 0),  # Usa get para evitar KeyError
                    'weeklyCrafts': memberGuild.get('WeeklyCrafts', 0),  # Usa get para evitar KeyError              
                }
            )

import logging
def detectPricesNoti():
    channel_layer = get_channel_layer()
    object_prices = ObjectsPrices.objects.all()
    logging.info(f"Found {len(object_prices)} object prices.")

    notified_objects = set()

    for obj_price in object_prices:
        if obj_price.object.id in notified_objects:
            continue

        user_notifications = UserNotification.objects.filter(
            object=obj_price.object,
            price__lte=obj_price.price
        )

        logging.info(f"Object: {obj_price.object.name}, Price: {obj_price.price}, Notifications: {user_notifications.count()}")

        for user_notification in user_notifications:
            message = f"El objeto {obj_price.object.name} está disponible por {obj_price.price}."
            Notification.objects.create(user=user_notification.user, message=message)
            logging.info(f"Notificación enviada a {user_notification.user.username}: {message}")

            # Enviar notificación a través del canal
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'user_{user_notification.user.id}',
                {
                    'type': 'send_notification',
                    'message': message
                }
            )

        notified_objects.add(obj_price.object.id)

            
                
        

# Example usage



         



