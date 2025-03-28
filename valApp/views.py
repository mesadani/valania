from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
# Create your views here.
from .models import Professions, Heroes, Races

def index(request):
    title = 'Welcome to the Jungle !'
    professions = Professions.objects.all();

    return render(request,"index.html",{
        'title': title,
        'professions': professions  # Pasar los proyectos al contexto

    })

def objects(request):
    professions = Professions.objects.all();

    return render(request, 'objects.html', {'professions': professions})


def heroes(request):
    heroes = Heroes.objects.all();
    races = Races.objects.all();

    return render(request, 'heroes.html', {'heroes': heroes, 'races': races})