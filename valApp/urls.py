from django.urls import path
from . import views

urlpatterns = [
    path('',  views.index , name='index'),
    path('professions',  views.professions , name='professions'),
    path('heroes',  views.heroes , name='heroes'),
    path('professions/<int:profession_id>/', views.profession_detail, name='profession_detail'),

]