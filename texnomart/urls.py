from django.urls import path
from texnomart import views
from django.views.decorators.cache import cache_page
from texnomart.custom_cache import conditional_cache_page
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from texnomart.simplejwt_tokens import CustomObtainPairView



urlpatterns=[
   path('', views.AllProducts.as_view(), name='all-products'),
   path('categories/', views.AllCategories.as_view(), name='all-categories'),
   path('category/<slug:slug>/', cache_page(60*2)(views.CategoryDetail.as_view()), name='category_detail'),
   path('add_category/', cache_page(60*3)(views.CategoryAdd.as_view()), name='category_add'),
   path('category/<slug:slug>/edit/', cache_page(60*2)(views.CategoryEdit.as_view()), name='category_edit'),
   path('category/<slug:slug>/delete/', views.CategoryDelete.as_view(), name='category_delete'),
   path('product/detail/<int:id>/', cache_page(60*2)(views.ProductDetail.as_view()), name='product_detail'),
   path('product/<int:id>/edit/', cache_page(60*2)(views.ProductEdit.as_view()), name='product_edit'),
   path('product/<int:id>/delete/', conditional_cache_page(60*2)(views.ProductDelete.as_view()), name='product_delete'),
   path('attribute_key/', conditional_cache_page(60*2)(views.KeyAPIView.as_view()), name='attrKeys'),
   path('attribute_value/', conditional_cache_page(60*2)(views.ValueAPIView.as_view()), name='attrValue'),
   path('register/', views.RegisterAPI.as_view(), name='register'),
   path('login/', views.UserLoginView.as_view(), name='login'),
   path('logout/', views.UserLogoutAPIView.as_view(), name='logout'),
   path('token-auth/', ObtainAuthToken.as_view()),
   path('api/token/', CustomObtainPairView.as_view(), name='token_obtain_pair'),
   path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]