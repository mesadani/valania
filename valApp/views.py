from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse,JsonResponse
# Create your views here.
from .models import Professions, Heroes, Races, Crafting, craftingRequirements

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
