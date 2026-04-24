

from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'postlar', views.PostViewSet, basename='post')

urlpatterns = [
    path('', views.bosh_sahifa, name='bosh_sahifa'),
    path('biz-haqimizda/', views.biz_haqimizda, name='biz_haqimizda'),
    path('aloqa/', views.aloqa, name='aloqa'),
    path('post/<int:post_id>/', views.post_batafsil, name='post_batafsil'),
    path('ommabop/', views.ommabop_postlar, name='ommabop'),
    path('qidiruv/', views.qidiruv, name='qidiruv'),
    path('draftlar/', views.draft_postlar, name='draft_postlar'),
    path('yangi/', views.post_yaratish, name='post_yaratish'),
    path('post/<int:post_id>/tahrirlash/', views.post_tahrirlash, name='post_tahrirlash'),
    path('post/<int:post_id>/ochirish/', views.post_ochirish, name='post_ochirish'),
    path('royxatdan-otish/', views.royxatdan_otish, name='royxatdan_otish'),
    path('kirish/', views.kirish, name='kirish'),
    path('chiqish/', views.chiqish, name='chiqish'),
    path('portfolio/',views.portfolio, name='portfolio'),
    path('profil/<str:username>/', views.profil_sahifasi, name='profil_sahifasi'),
    path('parol-ozgartirish/', views.parol_ozgartirish, name='parol_ozgartirish'),
    path('kategoriya/<int:id>/', views.kategoriya_postlari, name='kategoriya_postlari'),
    path('profil/<str:username>/', views.profil, name='profil'),
    path('profil/tahrirlash/', views.profil_tahrirlash, name='profil_tahrirlash'),
    path('api/', include(router.urls)),
    
    # API endpoints
    path('api/postlar/', views.post_list_api, name='post_list_api'),
    path('api/postlar/<int:post_id>/', views.post_detail_api, name='post_detail_api'),
    path('api/postlar/<int:post_id>/yangilash/', views.post_update_api, name='post_update_api'),
    path('api/postlar/<int:post_id>/ochirish/', views.post_delete_api, name='post_delete_api'),

    path('api/kirish/', views.login_api, name='login_api'),
    path('api/chiqish/', views.logout_api, name='logout_api'),
    path('api/royxatdan-otish/', views.register_api, name='register_api')

   
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)