from django.db.models import Exists, OuterRef
from rest_framework import mixins, viewsets, filters, permissions

from django_filters import rest_framework as dj_filters

from recipes.models import Ingredient, ShoppingList, Tag, Recipe, Favorite
from api.serializers import (IngredientSerializer, TagSerializer,
                             RecipeSerializer, RecipeWriteSerializer)
from api.filters import RecipeFilter
from api.permissions import IsAuthorOfContentOrReadOnly


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
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOfContentOrReadOnly
    )
    filter_backends = (dj_filters.DjangoFilterBackend, )
    filterset_class = RecipeFilter

    def get_queryset(self):
        user = self.request.user
        return (
            Recipe.objects.all().annotate(
                is_favorited=Exists(Favorite.objects.filter(recipe=OuterRef('pk'), user=user.pk)),  # noqa
                is_in_shopping_cart=Exists(ShoppingList.objects.filter(recipe=OuterRef('pk'), user=user.pk))  # noqa
            )
        )

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
