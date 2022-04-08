import re

from django.contrib.auth import get_user_model
from rest_framework import serializers

from recipes.models import Tag, Ingredient


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request:
            return False
        user = request.user
        if user.is_authenticated:
            return obj in user.subscribed_to.all()
        return False

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
