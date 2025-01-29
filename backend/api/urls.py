from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    FoodgramUserViewSet, RecipeViewSet, IngredientViewSet)

app_name = 'api'

router = DefaultRouter()
router.register('ingredients', IngredientViewSet)
router.register('users', FoodgramUserViewSet)
router.register('recipes', RecipeViewSet)

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
