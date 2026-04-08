from django.contrib import admin
from .models import Post, Izoh, Profil, Kategoriya

# ====== Izoh Inline ======
class IzohInline(admin.TabularInline):
    model = Izoh
    extra = 1

# ====== PostAdmin ======
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('sarlavha', 'muallif', 'yaratilgan_sana', 'nashr_etilgan')
    list_filter = ('nashr_etilgan', 'yaratilgan_sana')
    search_fields = ('sarlavha', 'matn')
    date_hierarchy = 'yaratilgan_sana'
    inlines = [IzohInline]   # Izoh inline qo‘shildi

# ====== ProfilAdmin ======
@admin.register(Profil)
class ProfilAdmin(admin.ModelAdmin):
    list_display = ('foydalanuvchi', 'tugilgan_sana')
    search_fields = ('foydalanuvchi__username',)

admin.site.register(Kategoriya)


admin.site.register(Izoh)


