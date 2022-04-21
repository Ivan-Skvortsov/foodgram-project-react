from django.db.models import Exists, OuterRef
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework import (mixins, viewsets, filters, permissions, response,
                            status, exceptions)
from rest_framework.decorators import action

from django_filters import rest_framework as dj_filters
from djoser.views import UserViewSet as DjoserUserViewSet

from recipes.models import Ingredient, ShoppingList, Tag, Recipe, Favorite
from api.serializers import (IngredientSerializer, TagSerializer,
                             RecipeSerializer, RecipeWriteSerializer,
                             ShortRecipeSerializer, UserWithRecipesSerializer)
from api.filters import RecipeFilter
from api.permissions import IsAuthorOfContentOrReadOnly
from api.services import ShoppingListGenerator


User = get_user_model()


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


class UserRecipeMixin:

    def modify_user_to_recipe_relation(self, request, pk=None,
                                       model_class=None):
        """
        Adds/removes user-recipe entry of given model_class.
        model_class should be a child of UserRecipe model.
        """
        if request.method not in ['POST', 'DELETE']:
            raise exceptions.APIException('Method not allowed')
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        related_model_entry = model_class.objects.filter(
            user=user,
            recipe=recipe
        )
        if request.method == 'POST':
            if related_model_entry:
                raise exceptions.ValidationError(
                    'Error. You are already added this recipe'
                )
            model_class.objects.create(user=user, recipe=recipe)
            serializer = ShortRecipeSerializer(instance=recipe)
            return response.Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            if not related_model_entry:
                raise exceptions.ValidationError(
                    'Error. You have not added this recipe'
                )
            related_model_entry.delete()
            return response.Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(UserRecipeMixin, viewsets.ModelViewSet):
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

    @action(methods=['GET'], detail=False,
            permission_classes=[permissions.IsAuthenticated],
            url_path='download_shopping_cart')
    def download_shopping_list(self, request):
        shopping_list = ShoppingListGenerator(self.request.user)
        return shopping_list.generate_pdf()

    @action(methods=['POST', 'DELETE'], detail=True,
            permission_classes=[permissions.IsAuthenticated],
            url_path='shopping_cart')
    def modify_shopping_list(self, request, pk=None):
        return self.modify_user_to_recipe_relation(request, pk, ShoppingList)

    @action(methods=['POST', 'DELETE'], detail=True,
            permission_classes=[permissions.IsAuthenticated],
            url_path='favorite')
    def modify_favorites(self, request, pk=None):
        return self.modify_user_to_recipe_relation(request, pk, Favorite)


class UserViewSet(DjoserUserViewSet):

    @action(methods=['GET'], detail=False,
            permission_classes=[permissions.IsAuthenticated],
            url_path='subscriptions')
    def get_subscriptions(self, request):
        users = self.request.user.subscribed_to.all()
        paginated_qs = self.paginate_queryset(users)
        serializer = UserWithRecipesSerializer(paginated_qs, many=True)
        recipes_limit = self.request.query_params.get('recipes_limit')
        serializer.context['recipes_limit'] = recipes_limit
        return self.get_paginated_response(serializer.data)

    @action(methods=['POST', 'DELETE'], detail=True,
            permission_classes=[permissions.IsAuthenticated],
            url_path='subscribe')
    def modify_subscriptions(self, request, id=None):
        user = self.request.user
        subscription = get_object_or_404(User, id=id)
        if user.id == subscription.id:
            raise exceptions.ValidationError(
                    'Error. You can not follow/unfollow yourself'
                )
        if request.method == 'POST':
            if subscription in user.subscribed_to.all():
                raise exceptions.ValidationError(
                    'Error. You are already following this user'
                )
            user.subscribed_to.add(subscription)
            serializer = UserWithRecipesSerializer(instance=subscription)
            return response.Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            if subscription not in user.subscribed_to.all():
                raise exceptions.ValidationError(
                    'Error. You are not following this user'
                )
            user.subscribed_to.remove(subscription)
            return response.Response(status=status.HTTP_204_NO_CONTENT)
