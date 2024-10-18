from django.shortcuts import render
from rest_framework.generics import ListAPIView, RetrieveAPIView, ListCreateAPIView, RetrieveUpdateAPIView, RetrieveDestroyAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework import status
from texnomart.models import Category, Group, Product, CharacteristicsKey, CharacteristicsValue
from texnomart.serializers import CategorySerializer, GroupSerializer, ProductSerializer, CategorySlugSerializer, AllProductSerializer, KeySerializer, ValueSerializer
from django.contrib.auth import authenticate
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from django.db.models.signals import post_save
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.dispatch import receiver
from texnomart.serializers import RegisterSerializer, UserSerializer
from django.utils.decorators import method_decorator
# from rest_framework.permissions import IsAuthenticated
# from rest_framework_simplejwt.authentication import JWTAuthentication

# FOR SWAGGER

from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


# caching
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers
from django.core.cache import cache
# Create your views here.

class AllProducts(ListAPIView):
    queryset=Product.objects.all()
    serializer_class=AllProductSerializer

    def get_queryset(self):
        cache_key='all_products'
        cached_data=cache.get(cache_key)
        if not cached_data:
            queryset=Product.objects.all()
            cache.set(cache_key, queryset, timeout=60*3)
            return queryset
        return cached_data
    
class AllCategories(ListAPIView):
    queryset=Category.objects.all()
    serializer_class=CategorySerializer

class CategoryDetail(RetrieveAPIView):
    queryset=Category.queryset = Category.objects.prefetch_related('groups__products__images').all()
    serializer_class=CategorySlugSerializer
    lookup_field = 'slug'

    def get_serializer(self, *args, **kwargs):
        # Pass the request context to the serializer
        kwargs['context'] = {'request': self.request}
        return super().get_serializer(*args, **kwargs)

class CategoryAdd(ListCreateAPIView):
    queryset=Category.objects.all()
    serializer_class=CategorySerializer

class CategoryEdit(RetrieveUpdateAPIView):
    queryset=Category.objects.all()
    serializer_class=CategorySerializer
    lookup_field = 'slug'

class CategoryDelete(RetrieveDestroyAPIView):
    queryset=Category.objects.all()
    serializer_class=CategorySerializer
    lookup_field = 'slug'

    def get_queryset(self):
        cache_key='add_category'
        cached_data=cache.get(cache_key)
        if not cached_data:
            queryset=Category.objects.get(id=id).all()
            cache.set(cache_key, queryset, timeout=60*3)
            return cache
        return cached_data

# Product part***

class ProductDetail(RetrieveAPIView):
    queryset=Product.objects.all()
    serializer_class= ProductSerializer
    lookup_field = 'id'

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = {'request': self.request}
        return super().get_serializer(*args, **kwargs)

class ProductEdit(RetrieveUpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = AllProductSerializer
    lookup_field = 'id'


    def get_serializer(self, *args, **kwargs):
        # Pass the request context to the serializer
        kwargs['context'] = {'request': self.request}
        return super().get_serializer(*args, **kwargs)
            
def conditional_cache_page(timeout):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                return cache_page(timeout)(view_func)(request, *args, **kwargs)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
# FAILED!

class ProductDelete(RetrieveDestroyAPIView):
    queryset=Product.objects.all()
    serializer_class=AllProductSerializer
    lookup_field = 'id' 

class KeyAPIView(ListAPIView):
    queryset=CharacteristicsKey.objects.all()
    serializer_class=KeySerializer

class ValueAPIView(ListAPIView):
    queryset=CharacteristicsValue.objects.all()
    serializer_class=ValueSerializer


# Token Authentication
class RegisterAPI(APIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
               "user": UserSerializer(user).data,
               "token": token.key, 'created':created }, status=201)
    
   
@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

class UserLoginView(APIView):
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        user = authenticate(username=request.data['username'], password=request.data['password'])
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'created':created})
        else:
            return Response({'error': 'Invalid credentials'}, status=401)
        

class UserLogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)

    def post(self, request, *args):
        token = Token.objects.get(user=request.user)
        token.delete()
        return Response({"success": True, "detail": "Logged out!"}, status=status.HTTP_200_OK)