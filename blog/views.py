from django.shortcuts import render, get_object_or_404
from .models import Post, Izoh  # ← Model ni import qilamiz

from django.shortcuts import render, redirect
from .models import Post
from .forms import PostForma
from django.contrib import messages
from django.contrib.auth import login
from .forms import RoyxatdanOtishForma
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Post, Kategoriya
from .forms import IzohForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.db.models import Q
from django.contrib.auth.models import User
from .models import Post, Profil
from .forms import FoydalanuvchiYangilashForma, ProfilYangilashForma
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db import connection
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import PostSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

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

def post_batafsil(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    izohlar = post.izohlar.all().order_by('-yaratilgan')

    if request.method == 'POST':
        form = IzohForm(request.POST)
        if form.is_valid():
            yangi_izoh = form.save(commit=False)
            yangi_izoh.post = post
            yangi_izoh.muallif = request.user
            yangi_izoh.save()
            return redirect('post_batafsil', pk=post.pk)
    else:
        form = IzohForm()

    return render(request, 'blog/post_batafsil.html', {
        'post': post,
        'izohlar': izohlar,
        'form': form
    })
def ommabop_postlar(request):
    postlar = Post.objects.filter(
        nashr_etilgan=True
    ).order_by('-korildi')[:5]  

    context = {'postlar': postlar}
    return render(request, 'blog/ommabop.html', context)

def qidiruv(request):
    query = request.GET.get('q')
    natijalar = []

    if query:
        natijalar = Post.objects.filter(
            Q(sarlavha__icontains=query) |
            Q(matn__icontains=query)
        )

    return render(request, 'blog/qidiruv.html', {
        'natijalar': natijalar,
        'query': query
    })

def draft_postlar(request):
    postlar = Post.objects.filter(nashr_etilgan=False)

    return render(request, 'blog/draftlar.html', {
        'postlar': postlar
    })

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
        messages.error(request, '❌ Siz faqat o\'z postingizni tahrirlashingiz mumkin!')
        return redirect('post_batafsil', post_id=post.id)

    if request.method == 'POST':
        forma = PostForma(request.POST, instance=post)
        if forma.is_valid():
            forma.save()
            messages.success(request, '✅ Post yangilandi!')
            return redirect('post_batafsil', post_id=post.id)
    else:
        forma = PostForma(instance=post)

    context = {'forma': forma, 'post': post}
    return render(request, 'blog/post_tahrirlash.html', context)

@login_required
def post_ochirish(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        post.delete()
        messages.success(request, '✅ Post o\'chirildi!')
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
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'✅ Xush kelibsiz, {user.username}!')
            return redirect('bosh_sahifa')
        else:
            messages.error(request, '❌ Noto\'g\'ri foydalanuvchi nomi yoki parol!')

    return render(request, 'blog/kirish.html')

def chiqish(request):
    logout(request)
    messages.info(request, '👋 Xayr! Tez orada qaytib kelasiz!')
    return redirect('bosh_sahifa')


def portfolio(request):
    return render(request, 'blog/portfolio.html')

def profil_sahifasi(request, username):
    user = get_object_or_404(User, username=username)
    postlar = Post.objects.filter(muallif=user).order_by('-yaratilgan_sana')
    jami_postlar = postlar.count()
    birinchi_post = postlar.first()
    return render(request, 'blog/profil.html', {
        'user': user,
        'postlar': postlar,
        'jami_postlar': jami_postlar,
        'birinchi_post': birinchi_post
    })

@login_required
def parol_ozgartirish(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()  
            update_session_auth_hash(request, user)  
            messages.success(request, "Parolingiz muvaffaqiyatli o'zgartirildi!")
            return redirect('profil_sahifasi', username=request.user.username)
        else:
            messages.error(request, "Iltimos, xatoliklarni tuzating.")
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'blog/parol_ozgartirish.html', {'form': form})

def kategoriya_postlari(request, id):
    kategoriya = get_object_or_404(Kategoriya, id=id)
    postlar = Post.objects.filter(kategoriya=kategoriya)

    return render(request, 'blog/kategoriya.html', {
        'kategoriya': kategoriya,
        'postlar': postlar
    })

@login_required
def profil(request, username):
    foydalanuvchi = get_object_or_404(User, username=username)
    postlar = Post.objects.filter(muallif=foydalanuvchi, nashr_etilgan=True).order_by('-yaratilgan_sana')
    profil_obj = get_object_or_404(Profil, foydalanuvchi=foydalanuvchi) 

    context = {
        'profil_egasi': foydalanuvchi,
        'profil': profil_obj,
        'postlar': postlar,
        'postlar_soni': postlar.count()
    }
    return render(request, 'blog/profil.html', context)



@login_required
def profil_tahrirlash(request):
    if request.method == 'POST':
        f_forma = FoydalanuvchiYangilashForma(request.POST, instance=request.user)
        p_forma = ProfilYangilashForma(request.POST, request.FILES, instance=request.user.profil)

        if f_forma.is_valid() and p_forma.is_valid():
            f_forma.save()
            p_forma.save()
            messages.success(request, '✅ Profilingiz yangilandi!')
            return redirect('profil', username=request.user.username)
    else:
        f_forma = FoydalanuvchiYangilashForma(instance=request.user)
        p_forma = ProfilYangilashForma(instance=request.user.profil)

    context = {
        'f_forma': f_forma,
        'p_forma': p_forma
    }
    return render(request, 'blog/profil_tahrirlash.html', context)



def health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({'status': 'ok'})
    except:
        return JsonResponse({'status': 'error'}, status=500)
    





@api_view(['GET'])
def post_list_api(request):
    postlar = Post.objects.filter(nashr_etilgan=True).order_by('-yaratilgan_sana')
    serializer = PostSerializer(postlar, many=True)
    return Response(serializer.data)


@api_view(['GET', 'POST'])
def post_list_api(request):
    if request.method == 'GET':
        postlar = Post.objects.filter(nashr_etilgan=True).order_by('-yaratilgan_sana')
        serializer = PostSerializer(postlar, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(muallif=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
def post_detail_api(request, post_id):
    try:
        post = Post.objects.get(id=post_id, nashr_etilgan=True)
    except Post.DoesNotExist:
        return Response(
            {'xato': 'Post topilmadi'},
            status=status.HTTP_404_NOT_FOUND
        )
    post.korildi += 1
    post.save()

    serializer = PostSerializer(post)
    return Response(serializer.data)


@api_view(['PUT', 'PATCH'])
def post_update_api(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response(
            {'xato': 'Post topilmadi'},
            status=status.HTTP_404_NOT_FOUND
        )
    if post.muallif != request.user:
        return Response(
            {'xato': 'Ruxsat yo\'q'},
            status=status.HTTP_403_FORBIDDEN
        )

    serializer = PostSerializer(post, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def post_delete_api(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response(
            {'xato': 'Post topilmadi'},
            status=status.HTTP_404_NOT_FOUND
        )
    if post.muallif != request.user:
        return Response(
            {'xato': 'Ruxsat yo\'q'},
            status=status.HTTP_403_FORBIDDEN
        )

    post.delete()
    return Response(
        {'xabar': 'Post o\'chirildi'},
        status=status.HTTP_204_NO_CONTENT
    )



class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.filter(nashr_etilgan=True).order_by('-yaratilgan_sana')
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(muallif=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.korildi += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def ommabop(self, request):
        postlar = Post.objects.filter(nashr_etilgan=True).order_by('-korildi')[:5]
        serializer = self.get_serializer(postlar, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def mening_postlarim(self, request):
        if not request.user.is_authenticated:
            return Response(
                {'xato': 'Tizimga kirish kerak'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        postlar = Post.objects.filter(muallif=request.user).order_by('-yaratilgan_sana')
        serializer = self.get_serializer(postlar, many=True)
        return Response(serializer.data)
    


@api_view(['POST'])
def login_api(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)

    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username
        })
    else:
        return Response(
            {'xato': 'Noto\'g\'ri login yoki parol'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
@api_view(['POST'])
def logout_api(request):
    if request.user.is_authenticated:
        request.user.auth_token.delete()
        return Response({'xabar': 'Muvaffaqiyatli chiqildi'})
    return Response(
        {'xato': 'Tizimga kirilmagan'},
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
def register_api(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    if User.objects.filter(username=username).exists():
        return Response(
            {'xato': 'Bu username band'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )

    token = Token.objects.create(user=user)

    return Response({
        'token': token.key,
        'user_id': user.id,
        'username': user.username
    }, status=status.HTTP_201_CREATED)