from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    # Rutas de autenticación
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    
    # Rutas principales del juego
    path('select-difficulty/', views.select_difficulty, name='select_difficulty'),
    path('game/<str:difficulty>/', views.game_view, name='game'),
    path('profile/', views.profile_view, name='profile'),
    path('save-game-result/', views.save_game_result, name='save_game_result'),
    
    # NUEVAS RUTAS PARA SISTEMA DE SCORES
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('game-history/', views.game_history, name='game_history'),
    path('player-stats/', views.player_stats, name='player_stats'),
    
    # Ruta por defecto
    path('', views.select_difficulty, name='home'),
]