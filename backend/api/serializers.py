from drf_extra_fields.fields import Base64ImageField
from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipes.models import Recipe, RecipeIngredient, Ingredient

User = get_user_model()


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class FoodgramUserSerializer(UserSerializer):
    avatar = Base64ImageField(allow_null=True, required=False)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )

    def get_is_subscribed(self, author):
        user = self.context.get('request').user
        return user.is_authenticated and author.authors.filter(
            user=user).exists()


class UserAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)

    def validate(self, data):
        if data.get('avatar') is None:
            raise ValidationError('Необходимо передать изображение')
        return super().validate(data)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True)
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )

    def validate_id(self, id):
        if not Ingredient.objects.filter(pk=id).exists():
            raise ValidationError(f'Ингредиент с {id} не найден.')
        return id


class RecipeSerializer(serializers.ModelSerializer):
    author = FoodgramUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients', many=True, required=True)
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate(self, data):
        if 'recipe_ingredients' not in data:
            raise ValidationError('Поле ingredients обязательно для заполнения')
        return super().validate(data)

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise ValidationError('Необходимо указать хотя бы один ингредиент')
        ingredient_ids = [
            ingredient.get('ingredient')
            .get('id') for ingredient in ingredients]
        dublicate_ids = [
            ingredient_id for ingredient_id in set(ingredient_ids)
            if ingredient_ids.count(ingredient_id) > 1
        ]
        if dublicate_ids:
            raise ValidationError(
                'Некоторые ингредиенты повторяются: '
                f'{dublicate_ids}'
            )
        existing_ingredients = Ingredient.objects.filter(
            id__in=ingredient_ids).values_list('id', flat=True)
        missing_ingredients = set(ingredient_ids) - set(existing_ingredients)
        if missing_ingredients:
            raise ValidationError(
                'Некоторые ингредиенты не найдены: '
                f'{missing_ingredients}'
            )
        return ingredients

    def validate_image(self, image):
        if image is None:
            raise ValidationError('Необходимо добавить изображение')
        return image

    def create(self, validated_data):
        ingredients = validated_data.pop('recipe_ingredients')
        recipe = super().create(validated_data)
        self.save_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('recipe_ingredients')
        instance.ingredients.clear()
        self.save_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def save_ingredients(self, recipe, ingredients_data):
        ingredient_ids = (
            ingredient['ingredient']['id'] for ingredient in ingredients_data
        )
        ingredient_dict = {
            ingredient.id: ingredient
            for ingredient in Ingredient.objects.filter(id__in=ingredient_ids)
        }
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient_dict[ingredient['ingredient']['id']],
                amount=ingredient['amount'],
            )
            for ingredient in ingredients_data
        )

    def get_is_favorited(self, recipe):
        user = self.context.get('request').user
        return user.is_authenticated and recipe.favoriterecipes.filter(
            user=user).exists()

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get('request').user
        return user.is_authenticated and recipe.shoppingcarts.filter(
            user=user).exists()


class RecipeResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
        read_only_fields = fields


class UserRecipesSerializer(FoodgramUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='recipes.count',
        read_only=True,
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar',
        )

    def get_recipes(self, user):
        return RecipeResponseSerializer(
            user.recipes.all()[:int(self.context['request'].query_params.get('recipes_limit', 10**10))],
            many=True,
            context=self.context
        ).data
