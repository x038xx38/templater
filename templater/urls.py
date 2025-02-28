"""templater URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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

# использование статических файлов
from django.conf import settings
from django.conf.urls.static import static

# перенаплавние запросов с корневого URL
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('site/', include('landing.urls')),
    path('accounts/', include('accounts.urls')),
    path('app/', include('app.urls')),
    path('', RedirectView.as_view(url='/site/', permanent=True)),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
