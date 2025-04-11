from django.urls import path
from . import views

urlpatterns = [
    path('',  views.index , name='index'),
    path('professions',  views.professions , name='professions'),
    path('heroes',  views.heroes , name='heroes'),
    path('combatUnits',  views.combatUnits , name='combatUnits'),
    path('professions/<int:profession_id>/', views.profession_detail, name='profession_detail'),
    #path('nft_detail/<str:nft_type>/<int:nft_id>/', views.nft_detail, name='nft_detail'),
    path('buscador_objeto/', views.buscador_objeto, name='buscador_objeto'),
    path('search', views.search, name='search'),
    path('inventory', views.inventory, name='inventory'),
    path('tracker', views.tracker, name='tracker'),
    path('guilds', views.guilds, name='guilds'),
    path('players', views.players, name='players'),
    path('stadistics', views.stadistics, name='stadistics'),
    path('market', views.market, name='market'),

]