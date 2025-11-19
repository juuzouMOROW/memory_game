# 🧠 Memory Game – Django (Proyecto Final)

## 📘 Descripción del Proyecto

Aplicación web desarrollada en **Django** que implementa un juego de memoria con tres niveles de dificultad, sistema de puntuación, historial de partidas, perfil de jugador y ranking global. Este proyecto corresponde al **Proyecto Final** de la asignatura **Arquitectura de Computadoras**.

## 👥 Información del Grupo

**Integrantes:**

- Ingris Gissell Samayoa - 202310010702
- Hadith Gissel Reyes Sierra - 202310110397
- Yudith Skarlet Rodríguez Mejía - 201330060004
- Roberto Carlos Morales Ordóñez - 202310110239
- Héctor David Bonilla Osorto - 202320110097
- Rony Josué Caballero Pineda - 201810080073
- Manuel Enrique Castro - 202130010208

**Clase:** Arquitectura de Computadoras – Proyecto Final  
**Universidad:** UTH - Universidad Tecnológica de Honduras

---

## ⚙️ Características

- Tres niveles de dificultad: **Básico (6 intentos, 90s)**, **Intermedio (4 intentos, 60s)** y **Avanzado (2 intentos, 45s)**.
- Mecánicas del juego: vista previa inicial de cartas, intentos limitados, temporizador y contador de pares encontrados.
- **Autenticación** (registro, inicio/cierre de sesión) y **perfil de jugador**.
- **Sistema de puntuación** por partida con bonificaciones por tiempo, movimientos y juego perfecto.
- **Historial de partidas**, estadísticas por dificultad y métricas personales (win rate, mejor score, promedio, etc.).
- **Ranking global**: top por puntaje acumulado y mejores partidas individuales.
- **Sonidos** de juego y **música de fondo** por dificultad con control de volumen.
- Interfaz moderna con **Bootstrap** y **FontAwesome**.

---

## 🧠 Tecnologías Utilizadas

- **Backend:** Django 5.2.8
- **Frontend:** HTML5, CSS3, Bootstrap 5, FontAwesome 6
- **Lenguaje:** Python 3.11 (Docker) / 3.10+ recomendado
- **Base de datos:** PostgreSQL (por defecto) y opción **SQLite** para desarrollo local
- **Contenedores:** Docker, docker-compose
- **Servidor WSGI (deploy):** Gunicorn (via Procfile)

---

## 📁 Estructura del Proyecto

```
memory-game/
└── memory-game/
		├── manage.py
		├── requirements.txt
		├── docker-compose.yml
		├── Dockerfile
		├── Procfile
		├── db.sqlite3
		├── media/
		├── memory_project/
		│   ├── settings.py
		│   ├── urls.py
		│   ├── wsgi.py
		│   └── asgi.py
		└── memory_game/
				├── models.py
				├── views.py
				├── urls.py
				├── admin.py
				├── migrations/
				├── static/
				│   └── memory_game/
				│       ├── css/style.css
				│       ├── js/
				│       └── sounds/
				└── templates/
						└── memory_game/
								├── base_app.html
								├── login.html / register.html
								├── select_difficulty.html
								├── game.html
								├── leaderboard.html
								├── game_history.html
								├── player_stats.html
								├── profile.html
								└── partials/navbar.html
```

Rutas principales (prefijo ` /memory/ `):
- `/login/`, `/register/`, `/logout/`
- `/select-difficulty/`
- `/game/<difficulty>/` (basic | medium | advanced)
- `/profile/`
- `/leaderboard/`
- `/game-history/`
- `/player-stats/`

La raíz `/` redirige a `/memory/`.

---

## 🛠️ Instalación y Configuración

### 🔹 Opción A: Entorno local (SQLite recomendado)

1. Ubícate en la carpeta del proyecto:

	 ```powershell
	 Set-Location "..\memory-game"
	 ```

2. Crear y activar entorno virtual:

	 ```powershell
	 python -m venv venv; .\\venv\\Scripts\\Activate.ps1
	 ```

3. Instalar dependencias:

	 ```powershell
	 pip install -r requirements.txt
	 ```

4. Usar SQLite (evita levantar PostgreSQL en local):

	 ```powershell
	 $env:USE_SQLITE = "1"
	 ```

5. Aplicar migraciones y crear superusuario (opcional):

	 ```powershell
	 python manage.py migrate
	 python manage.py createsuperuser
	 ```

6. Ejecutar el servidor de desarrollo:

	 ```powershell
	 python manage.py runserver
	 ```

7. Abrir en el navegador:

	 - `http://127.0.0.1:8000/memory/`
	 - Admin: `http://127.0.0.1:8000/admin/`

### 🔹 Opción B: Docker + PostgreSQL (por defecto)

1. Construir y levantar servicios:

	 ```powershell
	 docker-compose up --build
	 ```

2. Ejecutar migraciones y crear superusuario dentro del contenedor:

	 ```powershell
	 docker-compose exec web python manage.py migrate
	 docker-compose exec web python manage.py createsuperuser
	 ```

3. Abrir en el navegador:

	 - `http://localhost:8000/memory/`

Variables de entorno relevantes (Docker usa PostgreSQL por defecto):
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`
- Para forzar SQLite en local: `USE_SQLITE=1`

---

## 📊 Uso de la Aplicación

1. Regístrate e inicia sesión (`/memory/register/` y `/memory/login/`).
2. Selecciona un nivel en `/memory/select-difficulty/`.
3. Memoriza las cartas durante la vista previa y comienza a jugar.
4. Completa el tablero antes de que se acabe el tiempo o los intentos.
5. Revisa tu **perfil**, **historial**, **estadísticas** y el **ranking global**.

---

## 🧩 Detalles Técnicos Relevantes

- 
	Dificultades y parámetros:
	- Básico: 6 intentos, 90s
	- Medio: 4 intentos, 60s
	- Avanzado: 2 intentos, 45s
- 
	Scoring por partida (modelo `GameSession`):
	- Base por dificultad, bonus por tiempo restante, eficiencia en movimientos y juego perfecto.
	- Persistencia de `score`, `max_combo`, `perfect_game` y `rank_position`.
- 
	Perfil de jugador (`PlayerProfile`):
	- `total_games`, `games_won/lost`, `average_time`, `favorite_difficulty`, `total_score`, `best_score`.
- 
	Ranking global (`GlobalRanking`):
	- Top por `total_score`, mejor score, win rate, promedio; posiciones recalculadas automáticamente.
- 
	Rutas clave (ver `memory_game/urls.py`) y vistas en `memory_game/views.py`.

---

## 🔧 Comandos Útiles

- Migraciones:

	```powershell
	python manage.py makemigrations; python manage.py migrate
	```

- Crear superusuario:

	```powershell
	python manage.py createsuperuser
	```

- Chequeo del proyecto:

	```powershell
	python manage.py check
	```

- Docker (reiniciar servicio web):

	```powershell
	docker-compose restart web
	```

---

## 🚨 Solución de Problemas Comunes

- Error de base de datos (PostgreSQL no disponible):
	- Usa SQLite en local: ` $env:USE_SQLITE = "1" ` y vuelve a migrar.
- Puerto 8000 ocupado:
	- Ejecuta: `python manage.py runserver 8001`
- Migraciones pendientes o inconsistentes:
	- `python manage.py makemigrations; python manage.py migrate`
- Archivos estáticos no cargan en dev:
	- Asegúrate de `{% load static %}` y rutas correctas (ver `static/memory_game/...`).

---

## 📝 Notas Importantes

- En producción, configura `DEBUG=False`, `ALLOWED_HOSTS` y variables de BD.
- El repo incluye `Procfile` para despliegues en PaaS (p. ej., Gunicorn).  
- Para desarrollo rápido en Windows: recomienda `SQLite` con `USE_SQLITE`.
- La raíz del sitio redirige a `/memory/` (ver `memory_project/urls.py`).

---

¡Listo! Disfruta jugando y compitiendo en el ranking 🏆

---

## 🧭 Operaciones en VPS (Docker – producción)

- Arrancar en producción (requiere `.env` y `docker-compose.prod.yml`):

	```powershell
	docker compose -f docker-compose.prod.yml up -d --build
	```

- Ver logs de la app:

	```powershell
	docker compose -f docker-compose.prod.yml logs -f web
	```

- Reiniciar solo la app (cero cambios en DB):

	```powershell
	docker compose -f docker-compose.prod.yml restart web
	```

- Parar la app temporalmente ("dejar caer" el juego):

	```powershell
	docker compose -f docker-compose.prod.yml stop web
	```

- Apagar todo (app + DB) y liberar puertos:

	```powershell
	docker compose -f docker-compose.prod.yml down
	```

- Ejecutar comandos dentro del contenedor (migraciones, createsuperuser):

	```powershell
	docker compose -f docker-compose.prod.yml exec web python manage.py migrate
	docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
	```
