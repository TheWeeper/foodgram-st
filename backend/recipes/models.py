from django.core.validators import MinValueValidator
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

MIN_COOKING_TIME = 1


# Create your models here.
class FoodgramUser(AbstractUser):
    username = models.CharField('Никнейм', max_length=254, unique=True)
    first_name = models.CharField('Имя', max_length=150, blank=True)
    last_name = models.CharField('Фамилия', max_length=150, blank=True)
    email = models.EmailField('Электронная почта', blank=True, unique=True)
    avatar = models.ImageField(
        'Аватарка', blank=True, upload_to='avatar_images')


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
    image = models.ImageField('Изображение', blank=True)
    description = models.TextField('Описание рецепта')
    ingredients = models.ManyToManyField(Ingredient, verbose_name='Ингредиеты')
    cooking_time = models.PositiveIntegerField(
        'Время приготовления',
        validators=(MinValueValidator(MIN_COOKING_TIME),)
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
        related_name='subscribers',
        verbose_name='Автор'
    )

    class Meta:
        unique_together = ('user', 'subscribing')
