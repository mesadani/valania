from django.urls import path
from . import views

urlpatterns = [
    path('',  views.index , name='index'),
    path('objects',  views.objects , name='objects'),
    path('heroes',  views.heroes , name='heroes'),
]