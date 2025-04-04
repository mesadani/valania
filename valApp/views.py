from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse,JsonResponse
# Create your views here.
from .models import Professions, Heroes, Races, Crafting, craftingRequirements, Objects
from solan.service.phantom_wallet import get_nft_transactions
import json
from django.views.decorators.csrf import csrf_exempt
from .funciones import functions
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

    return render(request, 'heroes.html', {'heroes': heroes, 'races': races})



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
    if request.method == 'POST':
        # Extrae el query de la solicitud POST
        data = json.loads(request.body)
        query = data.get('q', '')

        if not query:
            return JsonResponse({"success": False, "error": "No query provided"})
        
        crafting_details = []
        craftingInverse_details = []


        try:
            nfts = Objects.objects.filter(name__icontains=query)
            nft = nfts.first() if nfts.exists() else None
            transactions = []
            
           
            holders = []
          
            if nft:

                if nft.mint != '0':
                    transactions = get_nft_transactions(nft.mint, 5)
                    holders = functions.getMaxSupply(nft.mint)




                crafting = Crafting.objects.get(object=nft.id)
                requirements = craftingRequirements.objects.filter(craft=crafting)

                requirements_list = [{'id': req.object.id, 'name': req.object.name, 'quantity': req.quantity, 'image': req.object.image.url if req.object.image.url else ''} for req in requirements]

                type_convertido = crafting.object.objectType.name.replace(" ", "-").lower()
                kind_convertido = crafting.object.name.replace(" ", "-").lower()
                marketURl = 'https://market.valannia.com/market/'+crafting.object.objectCategory.name+'?type='+type_convertido+'&kind='+kind_convertido
                
                crafting_details.append({
                    'crafting_name': crafting.object.name,
                    'level': crafting.level,
                    'quantity': crafting.quantity,
                    'probability': crafting.probability,
                    'time': crafting.time,
                    'profesion': crafting.proffesion.name,
                    'urlMarket': marketURl,
                    'supply': crafting.object.supply,
                    'image': crafting.object.image.url if crafting.object.image else '',
                    'requirements': requirements_list
                })

                requirementsInverse = craftingRequirements.objects.filter(object=nft.id)

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



                nft_data = {
                    'id': nft.id,
                    'name': nft.name,
                    'description': nft.description,
                    'image': nft.image.url if nft.image else '',
                    # Agregar otros campos necesarios de tu modelo Objects
                }
                
                
                response_data = {
                    "success": True,
                    'nft': nft_data,
                    'transactions': transactions,
                    'crafting_details_by_level': crafting_details,
                    'craftingInverse_details': craftingInverse_details,
                    'holders': holders,
                }

                
            
                
                return JsonResponse(response_data)
            else:
                return JsonResponse({"success": False, "error": "NFT not found"})
        except Objects.DoesNotExist:
            print('sws')
            return JsonResponse({"success": False, "error": "Object not found"})
        except Exception as e:
            print('ss')
            return JsonResponse({"success": False, "error": str(e)})
    else:
        return JsonResponse({"success": False, "error": "Only POST requests are allowed"})


def search(request):
    return render(request, 'search.html')


def profession_detail(request, profession_id):
    profession = get_object_or_404(Professions, id=profession_id)
    craftings = Crafting.objects.filter(proffesion=profession).order_by('level')
    
    crafting_details_by_level = {}
    for crafting in craftings:
        level = crafting.level
        if level not in crafting_details_by_level:
            crafting_details_by_level[level] = []
        
        crafting_details_by_level[level].append({
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