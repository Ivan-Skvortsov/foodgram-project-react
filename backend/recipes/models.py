from django.db import models
from django.contrib.auth import get_user_model

from recipes.validators import cooking_time_validator


User = get_user_model()


def get_deleted_user():
    """Returns `deleted` user."""
    return User.objects.get_or_create(
        username='deleted',
        first_name='Пользователь',
        last_name='Удален'
    )[0]


def get_image_upload_path(instance, filename):
    """
    Generate path to upload recipe images.
    Images will be uploaded to <MEDIA_ROOT>/user_<id>/recipe_<id>/<filename>.
    """
    return f'user_{instance.author.id}/recipe_{instance.id}/{filename}'


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название тега'
    )
    color = models.CharField(
        max_length=7,
        null=True,
        blank=True,
        verbose_name='Цвет'
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='Слаг тега'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.SET(get_deleted_user),
        related_name='recipes',
        verbose_name='Автор'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredients',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта'
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to=get_image_upload_path
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления (мин)',
        validators=[cooking_time_validator]
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredients(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name='Ингредиент'
    )
    amount = models.IntegerField(verbose_name='Количество')

    def __str__(self):
        return self.ingredient.name

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class UserRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='%(class)s_%(app_label)s'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='%(class)s_%(app_label)s'
    )

    def __str__(self):
        return f'Пользователь: {self.user}, рецепт: {self.recipe}'

    class Meta:
        abstract = True
        ordering = ['user']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_%(class)s_entry')
        ]


class Favorite(UserRecipe):

    class Meta(UserRecipe.Meta):
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'


class ShoppingList(UserRecipe):

    class Meta(UserRecipe.Meta):
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
