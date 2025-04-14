from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse,JsonResponse
# Create your views here.
from .models import Professions, Heroes, Races, Crafting, craftingRequirements, CombatUnits,Rarities, Objects,Guilds,GuildMembers, ObjectCategorys, ObjectTypes,ObjectsPrices,UserNotification
from solan.service.phantom_wallet import get_nft_transactions, get_nfts, extract_nft_info, getMarketPrices
import json
from django.views.decorators.csrf import csrf_exempt
from .funciones import functions
from collections import defaultdict
from deep_translator import GoogleTranslator
from django.core.paginator import Paginator
from django.db.models import Min
from django.db.models import Max
from django.db.models import Prefetch
from django.core.cache import cache
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
from django.contrib.auth import login, logout
import os
from django.contrib.auth.models import User
import base58
from django.contrib.auth.decorators import login_required as login_requireds


from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Notification


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

def tracker(request):
    return render(request, 'tracker.html')

def guilds(request):
    guildmembers_prefetch = Prefetch(
        'guildmembers_set',
        queryset=GuildMembers.objects.only('name', 'address', 'points', 'profession__name', 'professionMastery', 'ranking', 'usdc', 'weeklyCrafts').select_related('profession')
    )
    guilds = Guilds.objects.all().prefetch_related(guildmembers_prefetch)
    races = Races.objects.all()
    return render(request, 'guilds.html', {'guilds': guilds, 'races': races})



def stadistics(request):
    top_5_most_supply = Heroes.objects.all().order_by('-supply')[:10]
    top_5_least_supply = Heroes.objects.all().order_by('supply')[:10]

    top_5_most_supply_objects = Objects.objects.filter(supply__lt=100000).order_by('-supply')[:5]
    top_5_least_supply_objects = Objects.objects.filter(supply__gt=0).order_by('supply')[:5]


    top_10_most_expensive_objects = ObjectsPrices.objects.all().order_by('-price')[:10]
    top_10_least_expensive_objects = ObjectsPrices.objects.all().order_by('price')[:10]
   # top_10_most_expensive_objects = ObjectsPrices.objects.values('object_id').annotate(max_price=Max('price')).order_by('-max_price')[:10]

   # top_10_least_expensive_objects = ObjectsPrices.objects.values('object_id').annotate(min_price=Max('price')).order_by('min_price')[:10]

    
    top_10_most_expensive_by_category = functions.top_10_most_expensive_by_category()
    top_10_least_expensive_by_category = functions.top_10_least_expensive_by_category()

    
    
    return render(request, 'stadistics.html', {
        'top_5_most_supply': top_5_most_supply,
        'top_5_least_supply': top_5_least_supply,
        'top_5_most_supply_objects': top_5_most_supply_objects,
        'top_5_least_supply_objects': top_5_least_supply_objects,
        'top_10_most_expensive_objects': top_10_most_expensive_objects,
        'top_10_least_expensive_objects': top_10_least_expensive_objects,
        'top_10_most_expensive_by_category': top_10_most_expensive_by_category, 
        'top_10_least_expensive_by_category': top_10_least_expensive_by_category 
   
    })

def players(request):
    members_list = GuildMembers.objects.all().order_by('-professionMastery').values('name','address', 'professionMastery', 'race__name','profession__name','weeklyCrafts')

    paginator = Paginator(members_list, 300)  # Muestra 10 miembros por página

    page_number = request.GET.get('page')
    members = paginator.get_page(page_number)

    races = Races.objects.all()
    professions = Professions.objects.all()

    
    return render(request, 'players.html', {
        'guildmembers': members,
        'races': races,
        'professions': professions
    })


from django.core.paginator import Paginator

def market(request):
    last_update = ObjectsPrices.objects.aggregate(last_update=Max('created_at'))['last_update']

    print(f"Last update: {last_update}")
    # Filtrar objetos que tienen precios asociados y ordenar por el created_at más reciente de ObjectsPrices
    objects_with_prices = (
        Objects.objects
        .filter(objectsprices__isnull=False)
        .annotate(min_created_at=Min('objectsprices__created_at'))
        .order_by('min_created_at')
        .select_related('objectCategory', 'objectType')
        .prefetch_related('objectsprices_set', 'objectsbuyprices_set')
    )

    # Configurar la paginación
    paginator = Paginator(objects_with_prices, 500)  # Mostrar 10 objetos por página
    page_number = request.GET.get('page')
    page_objects = paginator.get_page(page_number)

    categories = ObjectCategorys.objects.all()
    types = ObjectTypes.objects.all()

    return render(request, 'market.html', {
        'objects': page_objects,
        'categories': categories,
        'types': types,
        'last_update': last_update
    })

@csrf_exempt
def get_nonce(request):
    data = json.loads(request.body)
    public_key = data["public_key"]
    nonce = os.urandom(16).hex()

    cache.set(f"nonce_{public_key}", nonce, timeout=300)  # 5 minutos
    return JsonResponse({"nonce": nonce})


@csrf_exempt
def verify_login(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        data = json.loads(request.body)
        public_key = data["public_key"]
        signature = bytes(data["signature"])  # ✅ CONVERTIR array a bytes
    except (KeyError, ValueError, TypeError) as e:
        return JsonResponse({"error": f"Entrada inválida: {e}"}, status=400)

    # Recuperar el nonce previamente guardado (en cache o DB)
    nonce = cache.get(f"nonce_{public_key}")
    if not nonce:
        return JsonResponse({"error": "Nonce no encontrado o expirado"}, status=400)

    try:
        # Convertir la clave pública de Base58 a binario
        public_key_bytes = base58.b58decode(public_key)  # Usamos base58 para convertir
        verify_key = VerifyKey(public_key_bytes)  # Crear la verificación con la clave pública

        # Verificar la firma
        message = nonce.encode("utf-8")
        verify_key.verify(message, signature)

    except ValueError:
        return JsonResponse({"error": "Clave pública inválida"}, status=400)
    except BadSignatureError:
        return JsonResponse({"error": "Firma inválida"}, status=400)

    # Autenticación exitosa, crear/obtener usuario y login
    user, _ = User.objects.get_or_create(username=public_key[:30])  # Usamos parte de la pubkey
    login(request, user)

    # Eliminar nonce para evitar reuse
    cache.delete(f"nonce_{public_key}")

    return JsonResponse({"success": True})

def logout_view(request):
    logout(request)
    return redirect('/')
def login_phantom(request):

    objects  = Objects.objects.all()
    notifications = []

    if request.user.is_authenticated:
        notifications = UserNotification.objects.filter(user=request.user).order_by('-created_at')[:6]



        

    return render(request, 'login_phantom.html', {
        'objects': objects,
        'notifications':notifications,
    
    })

def crear_notificacion(user, message):
    Notification.objects.create(user=user, message=message)

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'user_{user.id}',
        {
            'type': 'send_notification',
            'message': message,
        }
    )
###### AUTH VIEWS ######


@login_requireds
def inventory(request):
    return render(request, 'inventory.html')


@login_requireds
def mark_notifications_as_read(request):
    if request.method == "POST":
        request.user.notifications.filter(is_read=False).update(is_read=True)
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'Método no permitido'}, status=405)


@login_requireds
def save_order(request):
    data = json.loads(request.body)
    object_id = data["object_id"]
    price = data["price"]
    user = request.user
    object = Objects.objects.get(pk=object_id)
    UserNotification.objects.create(user=user, object=object, price = price)

    return JsonResponse({'status': 'ok'})



@login_requireds
def delete_order(request):
    data = json.loads(request.body)
    idNotification = data["idNotification"]

    # Obtener la instancia de UserNotification que deseas eliminar
    notification = UserNotification.objects.get(id=idNotification)
    # Eliminar la instancia
    notification.delete()

    return JsonResponse({'status': 'ok'})