from django.db.models import Exists, OuterRef
from django.shortcuts import get_object_or_404

from rest_framework import (mixins, viewsets, filters, permissions, response,
                            status, exceptions)
from rest_framework.decorators import action

from django_filters import rest_framework as dj_filters

from recipes.models import Ingredient, ShoppingList, Tag, Recipe, Favorite
from api.serializers import (IngredientSerializer, TagSerializer,
                             RecipeSerializer, RecipeWriteSerializer,
                             ShortRecipeSerializer)
from api.filters import RecipeFilter
from api.permissions import IsAuthorOfContentOrReadOnly
from api.services import ShoppingListGenerator


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

    @action(methods=['GET'],
            detail=False,
            permission_classes=[permissions.IsAuthenticated],
            url_path='download_shopping_cart',
            url_name='download_shopping_cart')
    def download_shopping_list(self, request):
        shopping_list = ShoppingListGenerator(self.request.user)
        return shopping_list.generate_pdf()

    @action(methods=['POST', 'DELETE'],
            detail=True,
            permission_classes=[permissions.IsAuthenticated],
            url_path='shopping_cart',
            url_name='shopping_cart')
    def modify_shopping_list(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        shopping_list_entry = ShoppingList.objects.filter(
            user=user,
            recipe=recipe
        )
        if request.method == 'POST':
            if shopping_list_entry:
                raise exceptions.ValidationError(
                    'Error. This recipe is already in shopping list'
                )
            ShoppingList.objects.create(user=user, recipe=recipe)
            serializer = ShortRecipeSerializer(instance=recipe)
            return response.Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            if not shopping_list_entry:
                raise exceptions.ValidationError(
                    'Error. This recipe is not in your shopping list'
                )
            shopping_list_entry.delete()
            return response.Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['POST', 'DELETE'],
            detail=True,
            permission_classes=[permissions.IsAuthenticated],
            url_path='favorite',
            url_name='favorite')
    def modify_favorites(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        favorites_entry = Favorite.objects.filter(
            user=user,
            recipe=recipe
        )
        if request.method == 'POST':
            if favorites_entry:
                raise exceptions.ValidationError(
                    'Error. This recipe is already in your favorites'
                )
            Favorite.objects.create(user=user, recipe=recipe)
            serializer = ShortRecipeSerializer(instance=recipe)
            return response.Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            if not favorites_entry:
                raise exceptions.ValidationError(
                    'Error. This recipe is not in your favorites'
                )
            favorites_entry.delete()
            return response.Response(status=status.HTTP_204_NO_CONTENT)
