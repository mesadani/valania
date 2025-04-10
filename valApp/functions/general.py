from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Prefetch
import json
from valApp.models import *
def get_nft_data(nft):
    return {
        'id': nft.id,
        'name': nft.name,
        'description': nft.description,
        'image': nft.image.url if nft.image else '',
    }


def get_crafting_details(nft):
    try:
        crafting = Crafting.objects.select_related('object__objectType', 'object__objectCategory', 'proffesion').get(object=nft.id)

        requirements = craftingRequirements.objects.select_related('object').filter(craft=crafting)

        requirements_list = [{
            'id': req.object.id,
            'name': req.object.name,
            'quantity': req.quantity,
            'image': req.object.image.url if req.object.image else ''
        } for req in requirements]

        type_slug = crafting.object.objectType.name.replace(" ", "-").lower()
        kind_slug = crafting.object.name.replace(" ", "-").lower()

        market_url = f'https://market.valannia.com/market/{crafting.object.objectCategory.name}?type={type_slug}&kind={kind_slug}'
        profession_url = f'https://market.valannia.com/realms/professions/{crafting.proffesion.name.lower().replace(" ", "-")}'

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
            'requirements': requirements_list
        }]
    except Crafting.DoesNotExist:
        return []

def get_inverse_crafting_details(nft):
    inverse_reqs = craftingRequirements.objects.filter(object=nft.id).select_related(
        'craft__object', 'craft__proffesion'
    )

    return [{
        'id': req.craft.object.id,
        'crafting_name': req.craft.object.name,
        'level': req.craft.level,
        'quantity': req.craft.quantity,
        'probability': req.craft.probability,
        'time': req.craft.time,
        'image': req.craft.object.image.url if req.craft.object.image else '',
        'profesion': req.craft.proffesion.name,
    } for req in inverse_reqs]
