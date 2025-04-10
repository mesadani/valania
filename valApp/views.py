from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse,JsonResponse
# Create your views here.
from .models import Professions, Heroes, Races, Crafting, craftingRequirements, CombatUnits,Rarities, Objects
from solan.service.phantom_wallet import get_nft_transactions, get_nfts, extract_nft_info, getMarketPrices
import json
from django.views.decorators.csrf import csrf_exempt
from .funciones import functions
from collections import defaultdict
from deep_translator import GoogleTranslator
def index(request):
    title = 'Welcome to the Jungle !'
    professions = Professions.objects.all();

    return render(request,"index.html",{
        'title': title,
        'professions': professions  # Pasar los proyectos al contexto

    })

def professions(request):
    professions = Professions.objects.all();

    return render(request, 'objects.html', {'professions': professions})


def heroes(request):
    heroes = Heroes.objects.all();
    races = Races.objects.all();
    rarities = Rarities.objects.all();

    return render(request, 'heroes.html', {'heroes': heroes, 'races': races, 'rarities': rarities})

def combatUnits(request):
    combatUnits = CombatUnits.objects.all();
    races = Races.objects.all();
    rarities = Rarities.objects.all();
    troopPoints = combatUnits.values_list('troopPoints', flat=True).distinct().order_by('troopPoints')


    return render(request, 'combatUnits.html', {'combatUnits': combatUnits, 'races': races, 'rarities': rarities, 'troopPoints': troopPoints})


def profession_detail_back(request, profession_id):
    profession = get_object_or_404(Professions, id=profession_id)
    craftings = Crafting.objects.filter(proffesion=profession).order_by('level')
    
    crafting_details = []
    for crafting in craftings:
       # requirements = craftingRequirements.objects.filter(craft=crafting)
       # requirements_list = [{'name': req.object.name, 'quantity': req.quantity} for req in requirements]
        
        crafting_details.append({
            'crafting_name': crafting.object.name,
            'level': crafting.level,
            'quantity': crafting.quantity,
            'probability': crafting.probability,
            'time': crafting.time,
            'image': crafting.object.image.url if crafting.object.image else ''
          #  'requirements': requirements_list
        })
    
    response_data = {
        'profession_name': profession.name,
        'profession_description': profession.description,
        'crafting_details': crafting_details
    }
    
    return JsonResponse(response_data)

def nft_detail(request, nft_type, nft_id):
    if nft_type == 'object':
        nft_type = Objects
    elif nft_type == 'Races':
        nft_type = Races
    else:
        raise ValueError("Invalid NFT type")
  

    crafting_details = []
    craftingInverse_details = []


    nft = nft_type.objects.get(id=nft_id)

    transactions = get_nft_transactions(nft.mint,5)

    crafting = Crafting.objects.get(object=nft.id)

    requirements = craftingRequirements.objects.filter(craft=crafting)
   

    requirements_list = [{'id': req.object.id,'name': req.object.name, 'quantity': req.quantity, 'image': req.object.image.url if req.object.image.url else ''} for req in requirements]

    crafting_details.append({
        'crafting_name': crafting.object.name,
        'level': crafting.level,
        'quantity': crafting.quantity,
        'probability': crafting.probability,
        'time': crafting.time,
        'image': crafting.object.image.url if crafting.object.image else '',
        'requirements': requirements_list
    })


    requirementsInverse = craftingRequirements.objects.filter(object=nft_id)

    for req in requirementsInverse:
         craftingInverse_details.append({
            'id': req.craft.object.id,
            'crafting_name': req.craft.object.name,
            'level': req.craft.level,
            'quantity': req.craft.quantity,
            'probability': req.craft.probability,
            'time': req.craft.time,
            'image': req.craft.object.image.url if req.craft.object.image else '',
            'profesion': req.craft.proffesion.name,
        })

    return render(request, 'nft_detail.html', {'nft': nft, 'transactions': transactions,'crafting_details': crafting_details,'craftingInverse_details': craftingInverse_details})

@csrf_exempt
def buscador_objeto(request):
    if request.method != 'POST':
        return JsonResponse({"success": False, "error": "Only POST requests are allowed"})

    try:
        data = json.loads(request.body)
        query = data.get('q', '')
        wallet = data.get('wallet', '')
        if not query:
            return JsonResponse({"success": False, "error": "No query provided"})

        translated_query = GoogleTranslator(source='auto', target='en').translate(query)

        print(translated_query)

        data = []
        if wallet:
            nfts = get_nfts(wallet)       
            data = extract_nft_info({"nfts": nfts})

        
        nft = Objects.objects.filter(name__icontains=translated_query).select_related(
            'objectType', 'objectCategory'
        ).first()
        
        if not nft:
            return JsonResponse({"success": False, "error": "NFT not found"})

        transactions = get_nft_transactions(nft.mint, 5) if nft.mint != '0' else []
        holders = functions.getMaxSupply(nft.mint) if nft.mint != '0' else []



        # precios

        prices = getMarketPrices(nft.objectCategory.name,nft.objectType.name,nft.name)

        response_data = {
            "success": True,
            "nft": functions.get_nft_data(nft),
            "transactions": transactions,
            "crafting_details_by_level": functions.get_crafting_details(nft,data),
            "craftingInverse_details": functions.get_inverse_crafting_details(nft,data),
            "holders": holders,
            "prices" : prices

        }

        return JsonResponse(response_data)

    except Objects.DoesNotExist:
        return JsonResponse({"success": False, "error": "Object not found"})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})
def search(request):
    return render(request, 'search.html')


def profession_detail(request, profession_id):
    profession = get_object_or_404(Professions, id=profession_id)

    craftings = (
        Crafting.objects
        .filter(proffesion=profession)
        .select_related('object')  # Para evitar consultas adicionales
        .order_by('level')
    )

    crafting_details_by_level = defaultdict(list)

    for crafting in craftings:
        crafting_details_by_level[crafting.level].append({
            'crafting_name': crafting.object.name,
            'quantity': crafting.quantity,
            'probability': crafting.probability,
            'time': crafting.time,
            'image': crafting.object.image.url if crafting.object.image else ''
        })

    response_data = {
        'profession_name': profession.name,
        'profession_description': profession.description,
        'crafting_details_by_level': crafting_details_by_level
    }

    return JsonResponse(response_data)

def inventory(request):
    return render(request, 'inventory.html')

def tracker(request):
    return render(request, 'tracker.html')

