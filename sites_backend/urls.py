"""
URL configuration for sites_backend project.

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
from django.urls import include, path
from sites_function.views import *
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', homepage, name='homepage'),
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('auth/google_login/', google_login,name='auth_google'),
    path('admin/', admin.site.urls),
    path('user/<int:user_id>/sites/', user_all_sites, name='user_sites'),
    path('sites/<uuid:uuid>/',sitesview,name='sites'),
    path('site_search/', search_site, name='site_search'),
    path('user_sites/', get_user_sites, name='get_user_sites'),
    path('site_byid/', get_site_by_id, name='site_byid'),
    path('add_sites/', create_site, name='create_site'),
    path('delete_site/<str:id>/', delete_site, name='delete_site'),
    # path('addsites/', add_or_edit_site, name='addsite'),
    path('editsites/<uuid:id>/', edit_site, name='editsites'),
    # path('api/auth/',include('sites_function.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

