"""
URL configuration for hospedai project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from core import views
from django.conf.urls.static import static
from django.conf import settings
from django.http import HttpResponse  # <- add
from core import views as core_views

def ping(request):                     # <- add (view mínima)
    return HttpResponse("HospedAI OK 🚀")

urlpatterns = [

    # HOME
    path('', core_views.home, name='home'),

    path('admin/', admin.site.urls),
    path('', ping, name='home'),       # <- raiz responde algo simples
    path('users/', include('users.urls')),
    path('reservas/', include('reservas.urls')),
    path('quartos/', include('quartos.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
