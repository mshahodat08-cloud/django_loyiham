from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from rest_framework import filters, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .forms import (
    FoydalanuvchiYangilashForma,
    IzohForm,
    PostForma,
    ProfilYangilashForma,
    RoyxatdanOtishForma,
)
from .models import  Post, Profil
from .permissions import FaqatMuallifOzgartiradi
from .serializers import PostSerializer

try:
    from django_filters.rest_framework import DjangoFilterBackend
except Exception:  # django-filter o'rnatilmagan holatda loyiha yiqilib qolmasin
    DjangoFilterBackend = None


def bosh_sahifa(request):
    postlar_list = Post.objects.select_related('muallif').filter(
        nashr_etilgan=True
    ).order_by('-yaratilgan_sana')
    paginator = Paginator(postlar_list, 5)
    sahifa_raqami = request.GET.get('sahifa')
    postlar = paginator.get_page(sahifa_raqami)
    return render(request, 'blog/bosh.html', {'postlar': postlar})


def biz_haqimizda(request):
    return render(request, 'blog/biz_haqimizda.html')


def aloqa(request):
    return render(request, 'blog/aloqa.html')


def portfolio(request):
    return render(request, 'blog/portfolio.html')


def ommabop_postlar(request):
    postlar = Post.objects.filter(nashr_etilgan=True).order_by('-korildi')[:5]
    return render(request, 'blog/ommabop.html', {'postlar': postlar})


def post_batafsil(request, post_id):
    post = get_object_or_404(Post, id=post_id, nashr_etilgan=True)
    post.korildi += 1
    post.save(update_fields=['korildi'])

    user_liked = False
    if request.user.is_authenticated:
        user_liked = Like.objects.filter(post=post, user=request.user).exists()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "❌ Izoh qoldirish uchun tizimga kiring.")
            return redirect('kirish')

        forma = IzohForma(request.POST)
        if forma.is_valid():
            izoh = forma.save(commit=False)
            izoh.post = post
            izoh.muallif = request.user
            izoh.save()
            messages.success(request, "✅ Izoh qoldirildi!")
            return redirect('post_batafsil', post_id=post.id)
    else:
        forma = IzohForma()

    izohlar = post.izohlar.select_related('muallif').all().order_by('-yaratilgan_sana')
    return render(request, 'blog/post_batafsil.html', {
        'post': post,
        'izohlar': izohlar,
        'user_liked': user_liked,
        'forma': forma,
    })


@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, nashr_etilgan=True)
    like_obj, created = Like.objects.get_or_create(post=post, user=request.user)
    if created:
        messages.success(request, "👍 Post yoqdi!")
    else:
        like_obj.delete()
        messages.info(request, "Like olib tashlandi")
    return redirect('post_batafsil', post_id=post.id)


def profil(request, username):
    foydalanuvchi = get_object_or_404(User, username=username)
    Profil.objects.get_or_create(foydalanuvchi=foydalanuvchi)
    postlar = Post.objects.filter(muallif=foydalanuvchi, nashr_etilgan=True).order_by('-yaratilgan_sana')
    return render(request, 'blog/profil.html', {
        'profil_egasi': foydalanuvchi,
        'postlar': postlar,
        'postlar_soni': postlar.count(),
    })


def qidiruv(request):
    soz = request.GET.get('q', '').strip()
    postlar = Post.objects.none()
    if soz:
        postlar = Post.objects.filter(
            Q(sarlavha__icontains=soz) | Q(matn__icontains=soz),
            nashr_etilgan=True,
                   ).select_related('muallif')
    return render(request, 'blog/qidiruv.html', {'postlar': postlar, 'soz': soz})


@login_required
def post_yaratish(request):
    if request.method == 'POST':
        forma = PostForma(request.POST, request.FILES)
        if forma.is_valid():
            post = forma.save(commit=False)
            post.muallif = request.user
            post.save()
            messages.success(request, '✅ Post yaratildi!')
            return redirect('bosh_sahifa')
    else:
        forma = PostForma()
    return render(request, 'blog/post_yaratish.html', {'forma': forma})


@login_required
def post_tahrirlash(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.muallif != request.user:
        messages.error(request, "❌ Siz faqat o'z postingizni tahrirlashingiz mumkin!")
        return redirect('post_batafsil', post_id=post.id)

    if request.method == 'POST':
        forma = PostForma(request.POST, request.FILES, instance=post)
        if forma.is_valid():
            forma.save()
            messages.success(request, '✅ Post yangilandi!')
            return redirect('post_batafsil', post_id=post.id)
    else:
        forma = PostForma(instance=post)
    return render(request, 'blog/post_tahrirlash.html', {'forma': forma, 'post': post})


@login_required
def post_ochirish(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.muallif != request.user:
        messages.error(request, "❌ Siz faqat o'z postingizni o'chirishingiz mumkin!")
        return redirect('post_batafsil', post_id=post.id)

    if request.method == 'POST':
        post.delete()
        messages.success(request, "✅ Post o'chirildi!")
        return redirect('bosh_sahifa')
    return render(request, 'blog/post_ochirish.html', {'post': post})


def royxatdan_otish(request):
    if request.method == 'POST':
        forma = RoyxatdanOtishForma(request.POST)
        if forma.is_valid():
            user = forma.save()
            login(request, user)
            messages.success(request, f'✅ Xush kelibsiz, {user.username}!')
            return redirect('bosh_sahifa')
    else:
        forma = RoyxatdanOtishForma()

    return render(request, 'blog/royxatdan_otish.html', {'forma': forma})


def kirish(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'✅ Xush kelibsiz, {user.username}!')
            return redirect('bosh_sahifa')
        messages.error(request, "❌ Noto'g'ri foydalanuvchi nomi yoki parol!")
    return render(request, 'blog/kirish.html')


def chiqish(request):
    logout(request)
    messages.info(request, '👋 Xayr! Tez orada qaytib kelasiz!')
    return redirect('bosh_sahifa')


@login_required
def profil_tahrirlash(request):
    profil_obj, _ = Profil.objects.get_or_create(foydalanuvchi=request.user)

    if request.method == 'POST':
        f_forma = FoydalanuvchiYangilashForma(request.POST, instance=request.user)
        p_forma = ProfilYangilashForma(request.POST, request.FILES, instance=profil_obj)
        if f_forma.is_valid() and p_forma.is_valid():
            f_forma.save()
            p_forma.save()
            messages.success(request, '✅ Profilingiz yangilandi!')
            return redirect('profil', username=request.user.username)
    else:
        f_forma = FoydalanuvchiYangilashForma(instance=request.user)
        p_forma = ProfilYangilashForma(instance=profil_obj)

    return render(request, 'blog/profil_tahrirlash.html', {'f_forma': f_forma, 'p_forma': p_forma})


@login_required
def post_izoh(request, post_id):
    # Eski URL bilan moslik uchun: izoh qo'shish post batafsil sahifasida bajariladi.
    return redirect('post_batafsil', post_id=post_id)


@api_view(['GET', 'POST'])
def post_list_api(request):
    if request.method == 'GET':
        postlar = Post.objects.filter(nashr_etilgan=True).order_by('-yaratilgan_sana')
        serializer = PostSerializer(postlar, many=True, context={'request': request})
        return Response(serializer.data)

    if not request.user.is_authenticated:
        return Response({'xato': 'Post yaratish uchun tizimga kiring'}, status=status.HTTP_401_UNAUTHORIZED)

    serializer = PostSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save(muallif=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def post_detail_api(request, post_id):
    post = get_object_or_404(Post, id=post_id, nashr_etilgan=True)
    post.korildi += 1
    post.save(update_fields=['korildi'])
    serializer = PostSerializer(post, context={'request': request})
    return Response(serializer.data)


@api_view(['PUT', 'PATCH'])
def post_update_api(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if not request.user.is_authenticated:
        return Response({'xato': 'Tizimga kirish kerak'}, status=status.HTTP_401_UNAUTHORIZED)
    if post.muallif != request.user:
        return Response({'xato': "Ruxsat yo'q"}, status=status.HTTP_403_FORBIDDEN)

    serializer = PostSerializer(post, data=request.data, partial=True, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def post_delete_api(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if not request.user.is_authenticated:
        return Response({'xato': 'Tizimga kirish kerak'}, status=status.HTTP_401_UNAUTHORIZED)
    if post.muallif != request.user:
        return Response({'xato': "Ruxsat yo'q"}, status=status.HTTP_403_FORBIDDEN)

    post.delete()
    return Response({'xabar': "Post o'chirildi"}, status=status.HTTP_204_NO_CONTENT)


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, FaqatMuallifOzgartiradi]
    search_fields = ['sarlavha', 'matn', 'muallif__username']
    ordering_fields = ['yaratilgan_sana', 'korildi', 'sarlavha']
    ordering = ['-yaratilgan_sana']

    if DjangoFilterBackend:
        filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
        filterset_fields = ['muallif', 'nashr_etilgan']
    else:
        filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    def get_queryset(self):
        qs = Post.objects.select_related('muallif').filter(nashr_etilgan=True)
        if self.request.user.is_authenticated and self.action in ['mening_postlarim']:
            return Post.objects.select_related('muallif').filter(muallif=self.request.user)
        return qs.order_by('-yaratilgan_sana')

    def perform_create(self, serializer):
        serializer.save(muallif=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.korildi += 1
        instance.save(update_fields=['korildi'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def ommabop(self, request):
        postlar = Post.objects.filter(nashr_etilgan=True).order_by('-korildi')[:5]
        serializer = self.get_serializer(postlar, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def mening_postlarim(self, request):
        postlar = Post.objects.filter(muallif=request.user).order_by('-yaratilgan_sana')
        serializer = self.get_serializer(postlar, many=True)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_api(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)

    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user_id': user.id, 'username': user.username})
    return Response({'xato': "Noto'g'ri login yoki parol"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_api(request):
    Token.objects.filter(user=request.user).delete()
    return Response({'xabar': 'Muvaffaqiyatli chiqildi'})


@api_view(['POST'])
@permission_classes([AllowAny])
def register_api(request):
    username = request.data.get('username')
    email = request.data.get('email', '')
    password = request.data.get('password')

    if not username or not password:
        return Response({'xato': 'username va password majburiy'}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(username=username).exists():
        return Response({'xato': 'Bu username band'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, email=email, password=password)
    token = Token.objects.create(user=user)
    return Response({'token': token.key, 'user_id': user.id, 'username': user.username}, status=status.HTTP_201_CREATED)
