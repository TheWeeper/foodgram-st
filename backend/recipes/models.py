from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class FoodgramUser(AbstractUser):
    username = models.CharField('Никнейм', max_length=150, unique=True)
    first_name = models.CharField('Имя', max_length=150, blank=True)
    last_name = models.CharField('Фамилия', max_length=150, blank=True)
    email = models.EmailField('Электронная почта', blank=True, unique=True)
    avatar = models.ImageField('Аватарка', blank=True)


# class Ingredient(models.Model):
#     name = models.CharField('Название')
#     unit = models.CharField('Единица измерения')


# class Recipe(models.Model):
#     name = models.CharField('Название')
