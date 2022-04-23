import django_filters

from recipes.models import Recipe
from django.db.models import Value, IntegerField, Q


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


class IngredientFilter(django_filters.FilterSet):
    """Custom filter for IngredientViewSet."""

    name = django_filters.CharFilter(method='filter_by_name')

    def filter_by_name(self, queryset, name, value):
        name_starts = Q(name__istartswith=value)
        name_contains = Q(name__icontains=value)
        qs1 = queryset.filter(name_starts).annotate(
            order=Value(0, IntegerField())
        )
        qs2 = queryset.filter(name_contains).exclude(name_starts).annotate(
            order=Value(1, IntegerField())
        )
        return qs1.union(qs2).order_by('order')
