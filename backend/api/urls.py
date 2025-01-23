from django.urls import include, path
from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet

app_name = 'api'

router = DefaultRouter()
router.register('ingredients', IngredientViewSet)

urlpatterns = [
    path('auth/', views.obtain_auth_token),
    path('', include(router.urls)),
]
