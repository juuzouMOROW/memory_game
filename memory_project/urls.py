from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('memory/', include('memory_game.urls')),
    path('', RedirectView.as_view(url='/memory/')),  # / → /memory/
]