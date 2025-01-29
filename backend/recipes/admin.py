from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe

from .admin_filters import CookingTimeFilter
from .models import (
    Recipe, RecipeIngredient, Ingredient, Subscription,
    FavoriteRecipe, ShoppingCart)

User = get_user_model()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit', 'get_in_recipes')
    list_editable = ('name', 'measurement_unit')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)

    def get_in_recipes(self, ingredient):
        return ingredient.recipe_ingredients.count()


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'cooking_time',
        'author',
        'get_in_favorites',
        'get_ingredients',
        'get_image',
    )
    search_fields = ('name', 'author__username', 'author__email')
    list_filter = ('author', CookingTimeFilter)
    inlines = (RecipeIngredientInline,)

    def get_in_favorites(self, recipe):
        return recipe.favoriterecipes.count()

    @mark_safe
    def get_ingredients(self, recipe):
        ingredients = recipe.recipe_ingredients.all()
        return '<br>'.join(
            f'- {ingredient.ingredient.name} {ingredient.amount} '
            f'{ingredient.ingredient.measurement_unit}'
            for ingredient in ingredients
        )

    @mark_safe
    def get_image(self, recipe):
        if recipe.image:
            return f'<img src="{recipe.image.url}" style="height: 100px;" />'
        return "Нет изображения"


@admin.register(User)
class FoodgramUserAdmin(UserAdmin):
    list_display = (
        'id',
        'username',
        'full_name',
        'email',
        'get_avatar',
        'get_recipes',
        'get_subscriptions',
        'get_subscribers',
    )

    def full_name(self, user):
        return f'{user.first_name} {user.last_name}'

    @mark_safe
    def get_avatar(self, user):
        if user.avatar:
            return (f'<img src="{user.avatar_url}" '
                    'style="width:50 px;border-radius:50%;" />')
        return 'Нет аватара'

    def get_recipes(self, user):
        return user.recipes.count()

    def get_subscriptions(self, user):
        return user.subscribers.count()

    def get_subscribers(self, user):
        return user.authors.count()


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')


@admin.register(FavoriteRecipe, ShoppingCart)
class FavoriteRecipeShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
