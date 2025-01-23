from django.contrib import admin

from .models import Ingredient, Recipe


# Register your models here.
@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_editable = ('name', 'measurement_unit')


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'author',
        'name',
        'image',
        'description',
        'ingredients',
        'created_at',
    )
