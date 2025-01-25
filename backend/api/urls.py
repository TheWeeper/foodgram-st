from django.urls import include, path
from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter

from .views import (
    FoodgramUserViewSet, RecipeViewSet, IngredientViewSet, get_recipe)

app_name = 'api'

router = DefaultRouter()
router.register('ingredients', IngredientViewSet)
router.register('users', FoodgramUserViewSet)
router.register('recipes', RecipeViewSet)

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
    path('s/<int:recipe_id>/', get_recipe, name='get_recipe')
]
