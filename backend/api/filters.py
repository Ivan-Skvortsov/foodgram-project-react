import django_filters

from recipes.models import Recipe


class RecipeFilter(django_filters.FilterSet):
    """Custom filter for RecipeViewSet."""

    tags = django_filters.CharFilter(field_name='tags__slug')
    is_favorited = django_filters.NumberFilter(field_name='is_favorited')
    is_in_shopping_cart = django_filters.NumberFilter(
        field_name='is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_favorited', 'is_in_shopping_cart']
