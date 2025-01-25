from drf_extra_fields.fields import Base64ImageField
from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipes.models import Recipe, RecipeIngredient, Ingredient, Subscription

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

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj.subscriber.filter(user=user).exists()
        return False


class UserAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)

    def validate(self, data):
        if data.get('avatar') is None:
            raise ValidationError('Необходимо передать изображение')
        return super().validate(data)


# class SubscriptionSerializer(serializers.ModelSerializer):
#     subscribing = serializers.SlugRelatedField(
#         slug_field='username', queryset=User.objects.all()
#     )

#     class Meta:
#         model = Subscription
#         fields = ('id', 'user', 'subscribing')

#     def validate_subscribing(self, value):
#         user = self.context['request'].user
#         if user == value:
#             raise serializers.ValidationError()
#         return value


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
        print(data)
        if 'recipe_ingredients' not in data:
            raise ValidationError('Необходимо указать хотя бы один ингредиент')
        return super().validate(data)

    def validate_ingredients(self, value):
        if len(value) == 0:
            raise ValidationError('Необходимо указать хотя бы один ингредиент')
        ingredient_ids = [
            ingredient.get('ingredient').get('id') for ingredient in value]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise ValidationError('Ингредиенты не должны повторяться')
        existing_ingredients = Ingredient.objects.filter(
            id__in=ingredient_ids).values_list('id', flat=True)
        missing_ingredients = set(ingredient_ids) - set(existing_ingredients)
        if missing_ingredients:
            raise ValidationError('Некоторые ингредиенты не найдены')
        return value

    def validate_image(self, value):
        if value is None:
            raise ValidationError()
        return value

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
        ingredients = (
            RecipeIngredient(
                recipe=recipe,
                ingredient=Ingredient.objects.get(
                    pk=item.get('ingredient').get('id')),
                amount=item.get('amount'),
            ) for item in ingredients_data
        )
        RecipeIngredient.objects.bulk_create(ingredients)

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj.favorites.filter(user=user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj.shopping_cart.filter(user=user).exists()
        return False


class RecipeResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class UserRecipesSerializer(FoodgramUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

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

    def get_recipes(self, obj):
        recipes_limit = self.context.get('recipes_limit')
        queryset = obj.recipes.all()
        if recipes_limit:
            queryset = queryset[:int(recipes_limit)]
        return RecipeResponseSerializer(
            queryset, many=True, context=self.context).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
