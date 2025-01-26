from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe

from .models import (
    Recipe, RecipeIngredient, Ingredient, Subscription,
    FavoriteRecipe, ShoppingCart)

User = get_user_model()


# Register your models here.
@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_editable = ('name', 'measurement_unit')


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'get_image', 'cooking_time')
    search_fields = ('name', 'author__username', 'author__email')
    list_filter = ('name', 'author', 'ingredients')
    inlines = (RecipeIngredientInline,)

    def get_image(self, obj):
        if obj.image:
            return mark_safe(
                f'<img src="{obj.image.url}" width="50" height="50" />')
        return "Нет изображения"


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'email',
        'username',
        'first_name',
        'last_name',
        'is_staff',
        'is_active'
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscribing')


@admin.register(FavoriteRecipe, ShoppingCart)
class FavoriteRecipeShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
