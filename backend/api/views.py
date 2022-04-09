from rest_framework import mixins, viewsets, filters

from django_filters import rest_framework as dj_filters


from recipes.models import Ingredient, Tag, Recipe
from api.serializers import (IngredientSerializer, TagSerializer,
                             RecipeSerializer)
from api.filters import RecipeFilter


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (dj_filters.DjangoFilterBackend, )
    filterset_class = RecipeFilter
