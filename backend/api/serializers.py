import base64

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import serializers

from recipes.models import Tag, Ingredient, Recipe, RecipeIngredients


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj in request.user.subscribed_to.all()

    class Meta:
        model = User
        fields = ('email', 'username', 'last_name', 'first_name',
                  'id', 'is_subscribed')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientsSerializer(serializers.ModelSerializer):

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):

    is_favorited = serializers.BooleanField(default=False)
    is_in_shopping_cart = serializers.BooleanField(default=False)
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientsSerializer(
        source='recipe_ingredients', many=True
    )
    author = UserSerializer()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')


class Base64ToImageField(serializers.ImageField):

    def to_internal_value(self, data):
        if not isinstance(data, str):
            raise serializers.ValidationError(
                f'Incorrect type. Expected string, got {type(data).__name__}'
            )
        if ';base64,' and 'data:image/' not in data:
            raise serializers.ValidationError(
                'Incorrect format. Expected base64 encoded image'
            )
        try:
            data_format,  encoded_img = data.split(';base64,')
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
                'Incorrect format. Expected base64 encoded image'
            )


class RecipeWriteSerializer(serializers.ModelSerializer):

    image = Base64ToImageField()
    ingredients = RecipeIngredientWriteSerializer(many=True)

    def validate_ingredients(self, ingredients):
        if len(ingredients) < 1:
            raise serializers.ValidationError('This list can not be empty')
        return ingredients

    def create(self, validated_data):
        tag_list = validated_data.pop('tags')
        ingredient_list = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredient_list:
            RecipeIngredients.objects.create(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
        recipe.tags.set(tag_list)
        return recipe

    def update(self, instance, validated_data):
        tag_list = validated_data.pop('tags')
        ingredient_list = validated_data.pop('ingredients')
        instance.ingredients.clear()
        instance.tags.clear()
        for ingredient in ingredient_list:
            RecipeIngredients.objects.create(
                recipe=instance,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
        instance.tags.set(tag_list)
        for key, val in validated_data.items():
            setattr(instance, key, val)
        instance.save()
        return instance

    def to_representation(self, instance):
        serializer = RecipeSerializer(instance)
        return serializer.data

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'name', 'text',
                  'cooking_time')
        required_fields = ('ingredients', 'tags', 'image', 'name', 'text',
                           'cooking_time')


class ShortRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'image', 'name', 'cooking_time')


class UserWithRecipesSerializer(UserSerializer):

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.BooleanField(default=True)

    def get_recipes(self, obj):
        recipes_limit = self.context.get('recipes_limit')
        if recipes_limit:
            try:
                recipes_limit = int(recipes_limit)
            except ValueError:
                recipes_limit = None
        recipes = obj.recipes.all()[:recipes_limit]
        return ShortRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.all().count()

    class Meta:
        model = User
        fields = ('email', 'username', 'last_name', 'first_name',
                  'id', 'is_subscribed', 'recipes', 'recipes_count')
