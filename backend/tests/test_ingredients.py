import pytest

from recipes.models import Ingredient
from api.serializers import IngredientSerializer


@pytest.mark.django_db(transaction=True)
def test_get_all_ingredients(guest_client):
    """Test ingredient list resource."""
    endpoint = '/api/ingredients/'

    Ingredient.objects.create(name='Salt', measurement_unit='g')
    Ingredient.objects.create(name='Sugar', measurement_unit='kg')

    ingredients = Ingredient.objects.all()
    serializer = IngredientSerializer(ingredients, many=True)

    response = guest_client.get(endpoint)

    assert response.status_code != 404
    assert response.status_code == 200
    assert len(response.data) == ingredients.count()
    assert set(response.data[0]) == set(['id', 'name', 'measurement_unit'])
    assert response.data == serializer.data


@pytest.mark.django_db(transaction=True)
def test_get_single_ingredient(guest_client):
    """Test single ingredient resource."""
    ingredient = Ingredient.objects.create(name='Salt', measurement_unit='g')
    endpoint = f'/api/ingredients/{ingredient.pk}/'

    serializer = IngredientSerializer(ingredient)
    response = guest_client.get(endpoint)

    assert response.status_code != 404
    assert response.status_code == 200
    assert set(response.data) == set(['id', 'name', 'measurement_unit'])
    assert response.data == serializer.data


@pytest.mark.django_db(transaction=True)
def test_ingredients_allow_only_get_method(guest_client):
    """Test that ingredient resource allow only GET http method."""
    endpoints = ('/api/ingredients/', f'/api/ingredients/{1}/')
    data = {
        'name': 'Salt',
        'measurement_unit': 'g'
    }
    for endpoint in endpoints:
        response = guest_client.post(endpoint, data)
        assert response.status_code == 405

        response = guest_client.put(endpoint, data)
        assert response.status_code == 405

        response = guest_client.patch(endpoint, data)
        assert response.status_code == 405

        response = guest_client.delete(endpoint, data)
        assert response.status_code == 405


@pytest.mark.django_db(transaction=True)
def test__ingredients_search_by_name(guest_client):
    """Test search ingredients by name."""
    Ingredient.objects.create(name='Salt', measurement_unit='g')
    Ingredient.objects.create(name='Sugar', measurement_unit='kg')
    Ingredient.objects.create(name='Лимон', measurement_unit='шт')

    response = guest_client.get('/api/ingredients/?search=Лим')
    assert response.status_code != 404
    assert response.status_code == 200
    assert len(response.data) == 1

    response = guest_client.get('/api/ingredients/?search=s')
    assert len(response.data) == 2

    response = guest_client.get('/api/ingredients/?search=ugar')
    assert len(response.data) == 0
