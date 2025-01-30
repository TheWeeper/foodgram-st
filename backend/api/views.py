from django.db.models import Sum
from django.contrib.auth import get_user_model
from django.http import FileResponse
from django.shortcuts import get_object_or_404, reverse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import filters, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .filters import RecipeFilter
from .renderers import render_shopping_list
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    FoodgramUserSerializer, RecipeSerializer, RecipeResponseSerializer,
    IngredientSerializer, UserAvatarSerializer,
    UserRecipesSerializer)
from recipes.models import (
    FavoriteRecipe, Recipe, RecipeIngredient,
    ShoppingCart, Ingredient, Subscription)

User = get_user_model()


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

    @action(detail=False, methods=('get',), url_path='me',
            permission_classes=(permissions.IsAuthenticated,))
    def me(self, request):
        return super().me(request)

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
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=('get',), url_path='subscriptions',
            permission_classes=(permissions.IsAuthenticated,))
    def subscriptions(self, request):
        subscriptions = User.objects.filter(authors__user=request.user)
        paginated_subscriptions = self.paginate_queryset(subscriptions)
        serializer = UserRecipesSerializer(
            paginated_subscriptions, many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=('post', 'delete'), url_path='subscribe')
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        subscription = Subscription.objects.filter(user=user, author=author)
        if request.method == 'POST':
            if user == author:
                raise ValidationError('Вы не можете подписаться сами на себя')
            if subscription.exists():
                raise ValidationError('Вы уже подписаны на этого пользователя')
            Subscription.objects.create(user=user, author=author)
            serializer = UserRecipesSerializer(
                author, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == "DELETE":
            get_object_or_404(Subscription, user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=('get',), url_path='get-link')
    def get_link(self, request, pk=None):
        get_object_or_404(Recipe, pk=pk)
        return Response({
            'short-link': request.build_absolute_uri(
                reverse('recipes:get_recipe', args=(self.get_object().pk,))
            )
        })

    @staticmethod
    def handle_recipe(model_class, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        if request.method == 'POST':
            relation, created = model_class.objects.get_or_create(
                user=user, recipe=recipe)
            if not created:
                raise ValidationError('Вы уже добавили этот рецепт')
            return Response(
                RecipeResponseSerializer(recipe).data,
                status=status.HTTP_201_CREATED
            )
        elif request.method == 'DELETE':
            get_object_or_404(model_class, user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=('post', 'delete'), url_path='favorite',
            permission_classes=(permissions.IsAuthenticated,))
    def favorite(self, request, pk=None):
        return self.handle_recipe(FavoriteRecipe, request, pk)

    @action(detail=True, methods=('post', 'delete'), url_path='shopping_cart',
            permission_classes=(permissions.IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        return self.handle_recipe(ShoppingCart, request, pk)

    @action(detail=False, methods=('get',), url_path='download_shopping_cart',
            permission_classes=(permissions.IsAuthenticated,))
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe__in=user.shoppingcarts.values('recipe'))
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(amount_total=Sum('amount'))
            .order_by('ingredient__name')
        )
        print(ingredients)
        recipes = (
            Recipe.objects
            .filter(shoppingcarts__user=user)
        )
        return FileResponse(
            render_shopping_list(ingredients, recipes, user),
            as_attachment=True,
            filename='Shopping_list.txt',
            content_type='text/plain',
        )
