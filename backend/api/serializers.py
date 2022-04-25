import base64

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import serializers

from recipes.models import Tag, Ingredient, Recipe, RecipeIngredients


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Main user serializer, used for `users` endpoints."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'username', 'last_name', 'first_name',
                  'id', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj in request.user.subscribed_to.all()


class TagSerializer(serializers.ModelSerializer):
    """Tag serializer for `tags` endpoints."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Ingredient serializer for `ingredients` endpoints."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    """
    RecipeIngredient serializer, used as nested serializer for `ingredients`
    field of Recipe. Provides `amount` of ingredient for specific Recipe.
    Represents `safe` methods.
    """

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    """
    Same as RecipeIngredient serializer, but used for creating and updating
    Recipe objects.
    """

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for Recipe model. Represents `safe` methods."""
    is_favorited = serializers.BooleanField(default=False)
    is_in_shopping_cart = serializers.BooleanField(default=False)
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientsSerializer(
        source='recipe_ingredients', many=True
    )
    author = UserSerializer()
    image = serializers.ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')


class Base64ToImageField(serializers.ImageField):
    """Custom image field, that converts Base64 encoded string to image."""

    def to_internal_value(self, data):
        if not isinstance(data, str):
            raise serializers.ValidationError(
                'Неверный тип данных. '
                f'Требуемый тип - string, полученный - {type(data).__name__}'
            )
        if ';base64,' and 'data:image/' not in data:
            raise serializers.ValidationError(
                'Некорректный формат. '
                'Требуется изображение, закодированное в строку base64'
            )
        try:
            data_format, encoded_img = data.split(';base64,')
            _, content_type = data_format.split(':')
            img_extension = content_type.split('/')[-1]
            decoded_img = base64.b64decode(encoded_img)
            return SimpleUploadedFile(
                name=f'img.{img_extension}',
                content=decoded_img,
                content_type=content_type
            )
        except Exception:
            raise serializers.ValidationError(
                'Некорректный формат строки base64. '
                'Требуется изображение, закодированное в строку base64'
            )


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Serializer for Recipe model. Used for creating and updating Recipe
    objects."""

    image = Base64ToImageField()
    ingredients = RecipeIngredientWriteSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'name', 'text',
                  'cooking_time')

    def update_or_create_recipe(self, validated_data, instance=None):
        tag_list = validated_data.pop('tags', None)
        ingredient_list = validated_data.pop('ingredients', None)
        if not (tag_list or ingredient_list):
            raise serializers.ValidationError(
                'Укажите как минимум один тег и ингредиент'
            )
        if not instance:
            instance = Recipe()
        for key, val in validated_data.items():
            setattr(instance, key, val)
        instance.save()
        instance.ingredients.clear()
        instance.tags.clear()
        for ingredient in ingredient_list:
            RecipeIngredients.objects.create(
                recipe=instance,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
        instance.tags.set(tag_list)
        return instance

    def create(self, validated_data):
        return self.update_or_create_recipe(validated_data)

    def update(self, instance, validated_data):
        return self.update_or_create_recipe(validated_data, instance=instance)

    def to_representation(self, instance):
        serializer = RecipeSerializer(instance)
        return serializer.data


class ShortRecipeSerializer(serializers.ModelSerializer):
    """
    Serializer for Recipe model with reduced number of fields.
    Used to represent User->Recipe relations (favorites, shopping list, etc.).
    """

    class Meta:
        model = Recipe
        fields = ('id', 'image', 'name', 'cooking_time')


class UserWithRecipesSerializer(UserSerializer):
    """Serializer for User model. Used to represent User subscriptions."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(source='recipes.count')
    is_subscribed = serializers.BooleanField(default=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'last_name', 'first_name',
                  'id', 'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        recipes_limit = self.context.get('recipes_limit')
        if recipes_limit:
            try:
                recipes_limit = int(recipes_limit)
            except ValueError:
                recipes_limit = None
        recipes = obj.recipes.all()[:recipes_limit]
        return ShortRecipeSerializer(recipes, many=True).data
