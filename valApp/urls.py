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
    
    path('tracker', views.tracker, name='tracker'),
    path('guilds', views.guilds, name='guilds'),
    path('players', views.players, name='players'),
    path('stadistics', views.stadistics, name='stadistics'),
    path('market', views.market, name='market'),
    path('get-nonce/', views.get_nonce, name='get_nonce'),
    path('verify-login/', views.verify_login, name='verify_login'),
    
    path('login_phantom', views.login_phantom, name='login_phantom'),

    #### AUTH #####
    path('logout/', views.logout_view, name='logout'),
    path('inventory', views.inventory, name='inventory'),
    path('notifications/mark-read/', views.mark_notifications_as_read, name='mark_notifications_as_read'),
    path('save-order/', views.save_order, name='save_order'),
    path('delete_order/', views.delete_order, name='delete_order'),

]