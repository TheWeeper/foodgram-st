from django.urls import include, path
from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter

from .views import FoodgramUserViewSet, IngredientViewSet

app_name = 'api'

router = DefaultRouter()
router.register('ingredients', IngredientViewSet)
router.register('users', FoodgramUserViewSet)

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
