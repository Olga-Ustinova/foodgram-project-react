from django.core import validators
from django.core.validators import MinValueValidator
from django.db import models

from users.models import User

MAX_RECIPE_LENGTH = 200
MAX_TAG_LENGTH = 200
MAX_INGREDIENT_LENGTH = 200


class Ingredient(models.Model):
    name = models.CharField(
        max_length=MAX_INGREDIENT_LENGTH,
        verbose_name='Ингредиент')
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единицы измерения')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=MAX_TAG_LENGTH,
        verbose_name='Тег')
    color = models.CharField(
        max_length=7,
        verbose_name='Цвет в HEX')
    slug = models.SlugField(
        max_length=200,
        unique=True,
        validators=[validators.RegexValidator(
            r'^[-a-zA-Z0-9_]+$',
            'Введите правильный слаг.',
            'invalid'),
        ],
        verbose_name='Слаг')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта')
    name = models.CharField(
        max_length=MAX_RECIPE_LENGTH,
        verbose_name='Название рецепта')
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Картинка рецепта')
    text = models.TextField(
        verbose_name='Описание блюда')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        verbose_name='Список ингредиентов')
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тэг')
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
        ],
        verbose_name='Время приготовления')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_amounts',
        verbose_name='Рецепты')
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиенты')
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
        ],
        verbose_name='Количество')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = [
            models.UniqueConstraint(fields=['recipe', 'ingredient'],
                                    name='unique_fields_recipe_ingredient'),
        ]

    def __str__(self):
        return (
            f'{self.recipe.name}: {self.ingredient.name} - '
            f'{self.amount} {self.ingredient.measurement_unit}')


class Favorited(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Автор рецепта')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепты')

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        ordering = ('recipe',)
        constraints = [models.UniqueConstraint(
            fields=['author', 'recipe'],
            name='unique_favorite')]

    def __str__(self):
        return f'{self.author} подписан(а) на {self.recipe}'


class ShoppingCart(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Автор рецепта')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепты')

    class Meta:
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'
        ordering = ('recipe',)
        constraints = [models.UniqueConstraint(
            fields=['author', 'recipe'],
            name='unique_cart')]

    def __str__(self):
        return f'У {self.author} {self.recipe} в списке покупок'
