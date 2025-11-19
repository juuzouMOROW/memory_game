FROM python:3.11
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar proyecto
COPY . .

# Comando por defecto: Gunicorn (docker-compose.dev puede sobrescribir)
CMD ["gunicorn", "memory_project.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
