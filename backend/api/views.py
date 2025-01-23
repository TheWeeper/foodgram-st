from rest_framework import viewsets, permissions

from recipes.models import Ingredient
from .serializers import IngredientSerializer


# Create your views here.
class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

