from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import User
from PIL import Image
import os


class Kategoriya(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom
    
class Post(models.Model):
    sarlavha = models.CharField(max_length=200, db_index=True)
    matn = models.TextField()
    muallif = models.ForeignKey(User, on_delete=models.CASCADE)
    rasm = models.ImageField(upload_to='postlar/', blank=True, null=True)  
    yaratilgan_sana = models.DateTimeField(auto_now_add=True)
    yangilangan_sana = models.DateTimeField(auto_now=True)
    nashr_etilgan = models.BooleanField(default=True)
    korildi = models.IntegerField(default=0)

    class Meta:
        ordering = ['-yaratilgan_sana']
        indexes = [
            models.Index(fields=['-yaratilgan_sana', 'nashr_etilgan']),
        ]

    def __str__(self):
        return self.sarlavha
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.rasm:
            img = Image.open(self.rasm.path)

            if img.height > 800 or img.width > 800:
                output_size = (800, 800)
                img.thumbnail(output_size)
                img.save(self.rasm.path)



class Izoh(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='izohlar')
    muallif = models.ForeignKey(User, on_delete=models.CASCADE)
    matn = models.TextField()
    yaratilgan = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.muallif.username} - {self.matn[:20]}"
    
class Profil(models.Model):
    foydalanuvchi = models.OneToOneField(User, on_delete=models.CASCADE)
    rasm = models.ImageField(
        upload_to='profillar/', 
        default='profillar/default.jpg'
    )
    bio = models.TextField(max_length=500, blank=True)
    tugilgan_sana = models.DateField(null=True, blank=True)
    manzil = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.foydalanuvchi.username} profili"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        
        if self.rasm and os.path.exists(self.rasm.path):
            img = Image.open(self.rasm.path)

            
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            max_size = (800, 800)
            img.thumbnail(max_size)
            img.save(self.rasm.path)

    
class PostRasm(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    rasm = models.ImageField(upload_to='post_rasmlari/')