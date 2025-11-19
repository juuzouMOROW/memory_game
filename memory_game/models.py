from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class PlayerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_games = models.IntegerField(default=0)
    games_won = models.IntegerField(default=0)
    games_lost = models.IntegerField(default=0)
    average_time = models.FloatField(default=0.0)
    favorite_difficulty = models.CharField(max_length=10, default='basic')
    total_score = models.IntegerField(default=0)  # NUEVO: Puntuación total acumulada
    best_score = models.IntegerField(default=0)   # NUEVO: Mejor puntuación individual
    
    def win_rate(self):
        if self.total_games == 0:
            return 0
        return (self.games_won / self.total_games) * 100
    
    def average_score(self):
        """NUEVO: Puntuación promedio por partida"""
        if self.total_games == 0:
            return 0
        return self.total_score / self.total_games
    
    def __str__(self):
        return f"Perfil de {self.user.username}"

class GameSession(models.Model):
    DIFFICULTY_CHOICES = [
        ('basic', 'Básico (6 intentos, 90s)'),
        ('medium', 'Medio (4 intentos, 60s)'),
        ('advanced', 'Avanzado (2 intentos, 45s)'),
    ]
    
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    moves = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    won = models.BooleanField(default=False)
    time_taken = models.IntegerField(default=0)  # en segundos
    
    # NUEVOS CAMPOS PARA SCORING
    score = models.IntegerField(default=0)           # Puntuación de esta partida
    max_combo = models.IntegerField(default=0)       # Máximo combo consecutivo
    perfect_game = models.BooleanField(default=False) # Juego perfecto (mínimos movimientos)
    rank_position = models.IntegerField(default=0)   # Posición en el ranking global
    
    def calculate_score(self):
        """Calcula la puntuación basada en dificultad, tiempo y movimientos"""
        base_scores = {'basic': 500, 'medium': 800, 'advanced': 1200}
        base_score = base_scores.get(self.difficulty, 500)
        
        # Bonificación por victoria
        if self.won:
            # Bonificación por tiempo (más rápido = más puntos)
            time_bonus = max(0, (90 - self.time_taken) * 5)  # +5 puntos por segundo restante
            
            # Bonificación por eficiencia (menos movimientos = más puntos)
            min_moves = 8  # Mínimo teórico de movimientos
            moves_bonus = max(0, (20 - self.moves) * 10)    # +10 puntos por movimiento restante
            
            # Bonificación por juego perfecto
            perfect_bonus = 300 if self.moves == min_moves else 0
            
            total_score = base_score + time_bonus + moves_bonus + perfect_bonus
            self.perfect_game = (self.moves == min_moves)
        else:
            total_score = max(0, base_score // 4)  # Puntos base reducidos por derrota
            
        return total_score
    
    def get_difficulty_multiplier(self):
        """Multiplicador según dificultad"""
        multipliers = {'basic': 1.0, 'medium': 1.5, 'advanced': 2.0}
        return multipliers.get(self.difficulty, 1.0)
    
    def duration(self):
        if self.end_time:
            return (self.end_time - self.start_time).seconds
        return 0
    
    def __str__(self):
        status = "Ganada" if self.won else "Perdida"
        return f"Partida de {self.player.username} - {self.difficulty} - {status} - {self.score} pts"

class Card(models.Model):
    session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='cards')
    symbol = models.CharField(max_length=1)
    position = models.IntegerField()  # 0-15 para tablero 4x4
    flipped = models.BooleanField(default=False)
    matched = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Carta {self.symbol} en posición {self.position}"

# NUEVO MODELO PARA RANKING GLOBAL
class GlobalRanking(models.Model):
    player = models.OneToOneField(User, on_delete=models.CASCADE)
    total_score = models.IntegerField(default=0)
    games_played = models.IntegerField(default=0)
    win_rate = models.FloatField(default=0.0)
    average_score = models.FloatField(default=0.0)
    best_score = models.IntegerField(default=0)
    rank_position = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-total_score']  # Ordenar por puntuación total descendente
    
    def __str__(self):
        return f"#{self.rank_position} - {self.player.username} - {self.total_score} pts"