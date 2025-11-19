from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import PlayerProfile, GameSession, Card, GlobalRanking
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
import json
from django.utils import timezone
from django.db import models
from django.db.models import Count, Avg, Max, Sum

def login_view(request):
    # Si ya está logueado, redirigir
    if request.user.is_authenticated:
        return redirect('select_difficulty')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('select_difficulty')  # Redirigir después del login
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'memory_game/login.html')

def register_view(request):
    if request.method == 'POST':
        # Crear usuario manualmente
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        if password1 != password2:
            messages.error(request, 'Las contraseñas no coinciden')
        else:
            from django.contrib.auth.models import User
            if User.objects.filter(username=username).exists():
                messages.error(request, 'El usuario ya existe')
            else:
                user = User.objects.create_user(username=username, password=password1)
                PlayerProfile.objects.create(user=user)
                # Crear entrada en el ranking global
                GlobalRanking.objects.create(player=user)
                messages.success(request, 'Cuenta creada exitosamente')
                return redirect('login')
    
    return render(request, 'memory_game/register.html')

@login_required
def select_difficulty(request):
    # Obtener o crear el perfil del usuario
    profile, created = PlayerProfile.objects.get_or_create(user=request.user)
    return render(request, 'memory_game/select_difficulty.html', {'profile': profile})

@login_required
def game_view(request, difficulty):
    return render(request, 'memory_game/game.html', {'difficulty': difficulty})

@login_required
def profile_view(request):
    profile = PlayerProfile.objects.get(user=request.user)
    recent_games = GameSession.objects.filter(player=request.user).order_by('-start_time')[:5]
    
    # Obtener ranking global del jugador
    try:
        global_rank = GlobalRanking.objects.get(player=request.user)
    except GlobalRanking.DoesNotExist:
        global_rank = None
    
    return render(request, 'memory_game/profile.html', {
        'profile': profile,
        'recent_games': recent_games,
        'global_rank': global_rank
    })

@login_required
def save_game_result(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            difficulty = data.get('difficulty')
            won = data.get('won')
            time_taken = data.get('time_taken')
            moves = data.get('moves')
            
            print(f"Guardando partida: {difficulty}, won: {won}, time: {time_taken}, moves: {moves}")
            
            # Crear nueva sesión de juego
            game_session = GameSession.objects.create(
                player=request.user,
                difficulty=difficulty,
                completed=True,
                won=won,
                time_taken=time_taken,
                moves=moves,
                end_time=timezone.now()
            )
            
            # CALCULAR Y GUARDAR SCORE
            game_session.score = game_session.calculate_score()
            game_session.save()
            
            print(f"GameSession creada: {game_session.id} - Score: {game_session.score}")
            
            # Actualizar perfil del jugador
            profile = PlayerProfile.objects.get(user=request.user)
            profile.total_games += 1
            
            if won:
                profile.games_won += 1
                # Actualizar mejores puntuaciones
                if game_session.score > profile.best_score:
                    profile.best_score = game_session.score
                profile.total_score += game_session.score
            else:
                profile.games_lost += 1
            
            # Calcular tiempo promedio
            total_time = (profile.average_time * (profile.total_games - 1)) + time_taken
            profile.average_time = total_time / profile.total_games
            
            # Actualizar dificultad favorita
            difficulty_stats = GameSession.objects.filter(player=request.user).values('difficulty').annotate(count=Count('id')).order_by('-count')
            if difficulty_stats:
                profile.favorite_difficulty = difficulty_stats[0]['difficulty']
            
            profile.save()
            
            # ACTUALIZAR RANKING GLOBAL
            update_global_ranking(request.user)
            
            return JsonResponse({
                'success': True, 
                'message': 'Partida guardada correctamente',
                'score': game_session.score,
                'new_stats': {
                    'total_games': profile.total_games,
                    'games_won': profile.games_won,
                    'games_lost': profile.games_lost,
                    'average_time': profile.average_time,
                    'win_rate': profile.win_rate(),
                    'total_score': profile.total_score,
                    'best_score': profile.best_score,
                    'average_score': profile.average_score()
                }
            })
            
        except Exception as e:
            print(f"ERROR guardando partida: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

def update_global_ranking(user):
    """Actualiza el ranking global para un usuario"""
    try:
        # Obtener estadísticas actualizadas
        user_games = GameSession.objects.filter(player=user)
        total_score = user_games.aggregate(total=Sum('score'))['total'] or 0
        games_played = user_games.count()
        games_won = user_games.filter(won=True).count()
        win_rate = (games_won / games_played * 100) if games_played > 0 else 0
        best_score = user_games.aggregate(best=Max('score'))['best'] or 0
        average_score = user_games.aggregate(avg=Avg('score'))['avg'] or 0
        
        # Actualizar o crear ranking
        ranking, created = GlobalRanking.objects.get_or_create(player=user)
        ranking.total_score = total_score
        ranking.games_played = games_played
        ranking.win_rate = win_rate
        ranking.average_score = average_score
        ranking.best_score = best_score
        ranking.save()
        
        # Recalcular posiciones de todos los jugadores
        recalculate_global_rankings()
        
    except Exception as e:
        print(f"Error actualizando ranking: {e}")

def recalculate_global_rankings():
    """Recalcula todas las posiciones del ranking global"""
    rankings = GlobalRanking.objects.all().order_by('-total_score')
    
    for position, ranking in enumerate(rankings, start=1):
        ranking.rank_position = position
        ranking.save()

# NUEVAS VISTAS PARA SCOREBOARD

@login_required
def leaderboard(request):
    """Ranking global de jugadores"""
    # Top 10 por puntuación total
    top_players = GlobalRanking.objects.all().order_by('-total_score')[:10]
    
    # Mejores puntuaciones individuales
    top_scores = GameSession.objects.filter(won=True).order_by('-score')[:10]
    
    # Mejores por dificultad
    best_basic = GameSession.objects.filter(won=True, difficulty='basic').order_by('-score').first()
    best_medium = GameSession.objects.filter(won=True, difficulty='medium').order_by('-score').first()
    best_advanced = GameSession.objects.filter(won=True, difficulty='advanced').order_by('-score').first()
    
    return render(request, 'memory_game/leaderboard.html', {
        'top_players': top_players,
        'top_scores': top_scores,
        'best_basic': best_basic,
        'best_medium': best_medium,
        'best_advanced': best_advanced,
    })

@login_required
def game_history(request):
    """Historial completo de partidas del usuario"""
    games = GameSession.objects.filter(player=request.user).order_by('-start_time')
    
    # Calcular estadísticas para el template
    games_won_count = games.filter(won=True).count()
    games_lost_count = games.count() - games_won_count
    
    # Mejor puntuación
    best_score_game = games.filter(won=True).order_by('-score').first()
    best_score = best_score_game.score if best_score_game else 0
    
    # Tiempo promedio de partidas ganadas
    won_games = games.filter(won=True)
    if won_games.exists():
        avg_time = won_games.aggregate(avg_time=Avg('time_taken'))['avg_time']
    else:
        avg_time = 0
    
    # Estadísticas por dificultad - CALCULADO EN LA VISTA
    basic_count = games.filter(difficulty='basic').count()
    medium_count = games.filter(difficulty='medium').count()
    advanced_count = games.filter(difficulty='advanced').count()
    
    # Calcular porcentajes
    total_games = games.count()
    basic_percent = (basic_count / total_games * 100) if total_games > 0 else 0
    medium_percent = (medium_count / total_games * 100) if total_games > 0 else 0
    advanced_percent = (advanced_count / total_games * 100) if total_games > 0 else 0
    
    # Calcular win rate
    win_rate = (games_won_count / total_games * 100) if total_games > 0 else 0
    
    # Filtrar si se solicita
    filter_type = request.GET.get('filter', 'all')
    if filter_type == 'won':
        games = games.filter(won=True)
    elif filter_type == 'lost':
        games = games.filter(won=False)
    
    return render(request, 'memory_game/game_history.html', {
        'games': games,
        'games_won_count': games_won_count,
        'games_lost_count': games_lost_count,
        'best_score': best_score,
        'avg_time': avg_time,
        # NUEVAS VARIABLES CALCULADAS
        'basic_count': basic_count,
        'medium_count': medium_count,
        'advanced_count': advanced_count,
        'basic_percent': basic_percent,
        'medium_percent': medium_percent,
        'advanced_percent': advanced_percent,
        'win_rate': win_rate,
    })

@login_required
def player_stats(request):
    """Estadísticas detalladas del jugador"""
    profile = PlayerProfile.objects.get(user=request.user)
    games = GameSession.objects.filter(player=request.user)
    
    # Estadísticas por dificultad
    basic_stats = games.filter(difficulty='basic').aggregate(
        total=Count('id'),
        won=Count('id', filter=models.Q(won=True)),
        avg_score=Avg('score'),
        best_score=Max('score')
    )
    
    medium_stats = games.filter(difficulty='medium').aggregate(
        total=Count('id'),
        won=Count('id', filter=models.Q(won=True)),
        avg_score=Avg('score'),
        best_score=Max('score')
    )
    
    advanced_stats = games.filter(difficulty='advanced').aggregate(
        total=Count('id'),
        won=Count('id', filter=models.Q(won=True)),
        avg_score=Avg('score'),
        best_score=Max('score')
    )
    
    # CALCULAR WIN RATES EN LA VISTA
    basic_win_rate = (basic_stats['won'] / basic_stats['total'] * 100) if basic_stats['total'] and basic_stats['total'] > 0 else 0
    medium_win_rate = (medium_stats['won'] / medium_stats['total'] * 100) if medium_stats['total'] and medium_stats['total'] > 0 else 0
    advanced_win_rate = (advanced_stats['won'] / advanced_stats['total'] * 100) if advanced_stats['total'] and advanced_stats['total'] > 0 else 0
    
    # Partidas recientes
    recent_games = games.order_by('-start_time')[:10]
    
    return render(request, 'memory_game/player_stats.html', {
        'profile': profile,
        'basic_stats': basic_stats,
        'medium_stats': medium_stats,
        'advanced_stats': advanced_stats,
        'recent_games': recent_games,
        # NUEVAS VARIABLES CALCULADAS
        'basic_win_rate': basic_win_rate,
        'medium_win_rate': medium_win_rate,
        'advanced_win_rate': advanced_win_rate,
    })