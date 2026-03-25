"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.http import HttpResponse
from core.views import upload_file
from core.views import homepage, profile, create_cio
from django.conf import settings
from django.conf.urls.static import static
from core.views import homepage, profile, create_cio, create_review

urlpatterns = [
    path("", homepage, name="homepage"),
    path('admin/', admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path('profile/', profile, name="profile"),
    path("create-cio/", create_cio, name="create_cio"),
    path("cio/<int:cio_id>/upload/", upload_file, name="upload_file"),
    path("create-review/",create_review,name="create_review"),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
