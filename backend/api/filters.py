import django_filters

from recipes.models import Recipe


class RecipeFilter(django_filters.FilterSet):
    """Custom filter for RecipeViewSet."""

    tags = django_filters.CharFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = ['tags', 'author']
