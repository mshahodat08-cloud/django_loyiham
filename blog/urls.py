from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'postlar', views.PostViewSet, basename='post')

urlpatterns = [
    path('', views.bosh_sahifa, name='bosh_sahifa'),
    path('post/<int:post_id>/', views.post_batafsil, name='post_batafsil'),
    path('post/<int:post_id>/like/', views.like_post, name='like_post'),
    path('post/<int:post_id>/izoh/', views.post_izoh, name='post_izoh'),
    path('post/<int:post_id>/tahrirlash/', views.post_tahrirlash, name='post_tahrirlash'),
    path('post/<int:post_id>/ochirish/', views.post_ochirish, name='post_ochirish'),

    path('ommabop/', views.ommabop_postlar, name='ommabop'),
    path('qidiruv/', views.qidiruv, name='qidiruv'),
    path('biz-haqimizda/', views.biz_haqimizda, name='biz_haqimizda'),
    path('aloqa/', views.aloqa, name='aloqa'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('yangi/', views.post_yaratish, name='post_yaratish'),

    path('royxatdan-otish/', views.royxatdan_otish, name='royxatdan_otish'),
    path('profil/tahrirlash/', views.profil_tahrirlash, name='profil_tahrirlash'),
    path('profil/<str:username>/', views.profil, name='profil'),
    path('kirish/', views.kirish, name='kirish'),
    path('chiqish/', views.chiqish, name='chiqish'),

    # Function-based API endpoints
    
    path('api/kirish/', views.login_api, name='login_api'),
    path('api/chiqish/', views.logout_api, name='logout_api'),
    path('api/royxatdan-otish/', views.register_api, name='register_api'),
    # path('api/postlar-fbv/', views.post_list_api, name='post_list_api'),
    # path('api/postlar-fbv/<int:post_id>/', views.post_detail_api, name='post_detail_api'),
    # path('api/postlar-fbv/<int:post_id>/yangilash/', views.post_update_api, name='post_update_api'),
    # path('api/postlar-fbv/<int:post_id>/ochirish/', views.post_delete_api, name='post_delete_api'),

    # ViewSet API endpoints
    path('api/', include(router.urls)),
]
