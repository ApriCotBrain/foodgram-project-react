from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views

from api.views import (
    IngredientViewSet,
    TagViewSet,
    RecipeViewSet,
    UserViewSet,
    # GetTokenAPIView
)

router = DefaultRouter()

router.register('tags', TagViewSet, basename='tag')
router.register('ingredients', IngredientViewSet, basename='ingredient')
router.register('recipes', RecipeViewSet, basename='recipe')
router.register('users', UserViewSet, basename='users')



urlpatterns = [
    path('', include(router.urls)),
    #path('api-token-auth/', views.obtain_auth_token),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    #path('auth/', include('djoser.urls.authtoken')),
]
