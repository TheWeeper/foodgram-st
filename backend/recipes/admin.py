from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Ingredient

User = get_user_model()


# Register your models here.
@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_editable = ('name', 'measurement_unit')


# @admin.register(Recipe)
# class RecipeAdmin(admin.ModelAdmin):
#     list_display = (
#         'id',
#         'author',
#         'name',
#         'image',
#         'description',
#         'ingredients',
#         'created_at',
#     )


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
