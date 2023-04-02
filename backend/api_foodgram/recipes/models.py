from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField(
        max_length=16,
        verbose_name='Тэг',
    )
    color = models.CharField(
        max_length=7,
        default='#49B64E',
        verbose_name='Цвет тэга')
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

    # def colored_name(self):
    #     return format_html(
    #         '<span style="color: #{};">{}</span>',
    #         self.color,
    #         self.name
    #     )


class Ingredient(models.Model):
    name = models.CharField(
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
        User,
        on_delete=models.CASCADE,
        related_name='recipe_author',
        verbose_name='Автор рецепта',
        blank=True, null=True,
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
        upload_to='recipes/image/',
        verbose_name='Картинка',
    )
    text = models.TextField(
        max_length=1056,
        verbose_name='Описание рецепта'
    )
    ingredient = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиент рецепта',
    )
    tag = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        verbose_name='Тэг рецепта',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления в минутах'
    )
    is_favorited = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        #constraints = [
            #models.UniqueConstraint(fields=['name', 'image'],
                                    #name='unique_name_image')
        #]

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredient',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredient',
    )
    amount = models.FloatField(
        verbose_name='Количество',
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'

        # constraints = [
        #     models.UniqueConstraint(fields=['recipe', 'ingredient'],
        #                             name='unique_name_image')
        # ]

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Тэг рецепта'
        verbose_name_plural = 'Тэги рецептов'

    def __str__(self):
        return f'{self.recipe} {self.tag}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='fan',
        verbose_name='Фэн',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe',
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
        return str(self.user_id)


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик')
    subscribe = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribe',
        verbose_name='Автор рецептов')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(fields=['user', 'subscribe'],
                                    name='unique_subscribe')
        ]

    def __str__(self):
        return str(self.user_id)
