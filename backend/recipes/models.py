from django.core.validators import RegexValidator, MinValueValidator
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class FoodgramUser(AbstractUser):
    username = models.CharField(
        'Никнейм',
        max_length=254,
        unique=True,
        validators=(RegexValidator('^[\w.@+-]+\z'),)
    )
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)
    email = models.EmailField('Электронная почта', unique=True)
    avatar = models.ImageField(
        'Аватарка', blank=True, upload_to='avatar_images')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)


class Ingredient(models.Model):
    name = models.CharField('Название', max_length=150, unique=True)
    measurement_unit = models.CharField('Единица измерения', max_length=150)

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    name = models.CharField('Название', max_length=150)
    image = models.ImageField(
        'Изображение',
        blank=True,
        upload_to='recipe_images'
    )
    text = models.TextField('Описание рецепта')
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиеты',
        through='RecipeIngredient',
        related_name='recipes',
    )
    cooking_time = models.PositiveIntegerField(
        'Время приготовления',
        validators=(MinValueValidator(1),)
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-created_at',)

    def __str__(self):
        return self.name


class Subscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='subscribing',
        verbose_name='Подписчик'
    )
    subscribing = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Автор'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=("user", "subscribing"), name="unique_subscription"),
        )

    def __str__(self):
        return f"{self.user} подписан на {self.subscribing}"


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    amount = models.PositiveIntegerField(validators=(MinValueValidator(1),))


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping_cart'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='shopping_cart',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=("user", "recipe"), name="unique_shopping_cart"),
        )


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorites',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='favorites',
    )

    # class Meta:
    #     constraints = (
    #         models.UniqueConstraint(
    #             fields=("user", "recipe"), name="unique_favorite_recipe"),
    #     )
