from rest_framework import serializers
from .models import Post, Profil
from django.contrib.auth.models import User

class PostSerializer(serializers.ModelSerializer):
    muallif_ismi = serializers.CharField(source='muallif.username', read_only=True)

    class Meta:
        model = Post
        fields = [
            'id',
            'sarlavha',
            'matn',
            'muallif',
            'muallif_ismi',
            'rasm',
            'yaratilgan_sana',
            'yangilangan_sana',
            'nashr_etilgan',
            'korildi'
        ]
        read_only_fields = ['id', 'yaratilgan_sana', 'yangilangan_sana', 'korildi']