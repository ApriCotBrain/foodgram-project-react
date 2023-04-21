from django.core.validators import RegexValidator, MinValueValidator
from django.db import models

from users.models import CustomUser

MIN_COOKING_TIME = 1


class Tag(models.Model):
    name = models.CharField(
        unique=True,
        max_length=16,
        verbose_name='Тэг',
    )
    color = models.CharField(
        unique=True,
        max_length=7,
        validators=[RegexValidator('^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')],
        verbose_name='Цвет тэга'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Slug'
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        unique=True,
        max_length=64,
        verbose_name='Ингредиент',
    )
    measurement_unit = models.CharField(
        max_length=8,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='recipe_author',
        verbose_name='Автор рецепта',
    )
    name = models.CharField(
        max_length=256,
        verbose_name='Название рецепта',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Картинка',
    )
    text = models.TextField(
        verbose_name='Описание рецепта'
    )
    ingredient = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиент рецепта',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тэг рецепта',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления в минутах',
        validators=[MinValueValidator(MIN_COOKING_TIME)]
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
    )
    amount = models.FloatField(
        verbose_name='Количество',
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'

    def __str__(self):
        return f'{self.recipe_id} {self.ingredient_id}'


class Favorite(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        ordering = ['user']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe'
            )
        ]

    def __str__(self):
        return f'{self.user_id} {self.recipe_id}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='shopping_cart_user',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart_recipe',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    def __str__(self):
        return f'{self.user_id} {self.recipe_id}'
