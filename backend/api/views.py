from django.db.models import Sum
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, reverse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import filters, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response


from .permissions import IsAuthorOrReadOnly
from .serializers import (
    FoodgramUserSerializer, RecipeSerializer, RecipeResponseSerializer,
    IngredientSerializer, UserAvatarSerializer, SubscriptionSerializer,
    UserRecipesSerializer)
from recipes.models import (
    FavoriteRecipe, Recipe, RecipeIngredient,
    ShoppingCart, Ingredient, Subscription)

User = get_user_model()


# Create your views here.
class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = None
    filter_backend = (filters.SearchFilter,)
    search_fields = ('^name',)

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.query_params.get('name', None)
        if name:
            queryset = queryset.filter(name__istartswith=name)
        return queryset


class FoodgramUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = FoodgramUserSerializer

    @action(detail=False, methods=('put', 'delete'), url_path='me/avatar',
            permission_classes=(permissions.IsAuthenticated,))
    def avatar(self, request):
        user = request.user
        if request.method == 'PUT':
            serializer = UserAvatarSerializer(
                user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            user.avatar.delete(save=True)
            return Response(status=status.HTTP_204_NO_CONTENT)   

    @action(detail=False, methods=('get',), url_path='subscriptions',
            permission_classes=(permissions.IsAuthenticated,))
    def subscriptions(self, request):
        subscriptions = Subscription.objects.filter(user=request.user)
        serializer = SubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=('post', 'delete'), url_path='subscribe')
    def subscribe(self, request, pk=None):
        user = request.user
        author = get_object_or_404(User, pk=pk)
        subscription = Subscription.objects.filter(user=user, author=author)
        if request.method == 'POST':
            if user == author or subscription.exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            Subscription.objects.create(user=user, author=author)
            serializer = UserRecipesSerializer(author)
            return Response(serializer, status=status.HTTP_201_CREATED)
        elif request.method == "DELETE":
            if subscription.exists():
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
    # filter_backends = (DjangoFilterBackend,)
    # filterset_fields = ('is_favorited', 'is_in_shopping_cart', 'author')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def retrieve(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = self.get_serializer(recipe)
        return Response(serializer.data)

    @action(detail=True, methods=('get',), url_path='get-link')
    def get_link(self, request, pk=None):
        short_url = request.build_absolute_uri(reverse(
            'api:get_recipe', kwargs={'recipe_id': pk}
        ))
        return Response({'short_link': short_url})

    @action(detail=True, methods=('post', 'delete'), url_path='favorite',
            permission_classes=(permissions.IsAuthenticated,))
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        favorite = FavoriteRecipe.objects.filter(user=user, recipe=recipe)
        if request.method == 'POST':
            if favorite.exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            serializer = RecipeResponseSerializer(recipe)
            FavoriteRecipe.objects.create(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if favorite.exists():
                favorite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=('post', 'delete'), url_path='shopping_cart',
            permission_classes=(permissions.IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        shopping_cart = ShoppingCart.objects.filter(user=user, recipe=recipe)
        if request.method == 'POST':
            if shopping_cart.exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            serializer = RecipeResponseSerializer(recipe)
            ShoppingCart.objects.create(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if shopping_cart.exists():
                shopping_cart.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_404_NOT_FOUND)
        
    @action(detail=False, methods=('get',), url_path='download_shopping_cart',
            permission_classes=(permissions.IsAuthenticated,))
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe__shopping_cart__user=user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(amount_total=Sum('amount'))
            .order_by('ingredient__name')
        )
        shopping_list = ''
        for ingredient in ingredients:
            shopping_list += (
                f'- {ingredient["ingredient__name"]}'
                f'({ingredient["amount_total"]}'
                f'{ingredient["ingredient__measurement_unit"]})\n'
            )
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; file_name="shopping_list.txt"'
        )
        return response


def get_recipe(request, recipe_id):
    return redirect(f'/recipes/{recipe_id}')
