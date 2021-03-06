import pytest

from recipes.models import Ingredient
from api.serializers import IngredientSerializer


@pytest.mark.django_db(transaction=True)
def test_get_all_ingredients(guest_client, test_ingredients):
    endpoint = '/api/ingredients/'
    serializer = IngredientSerializer(test_ingredients, many=True)
    response = guest_client.get(endpoint)
    data = response.json()

    assert response.status_code != 404
    assert response.status_code == 200
    assert len(data) == test_ingredients.count()
    assert set(data[0]) == set(['id', 'name', 'measurement_unit'])
    assert data == serializer.data


@pytest.mark.django_db(transaction=True)
def test_get_single_ingredient(guest_client, test_ingredients):
    ingredient = test_ingredients[0]
    endpoint = f'/api/ingredients/{ingredient.pk}/'

    serializer = IngredientSerializer(ingredient)
    response = guest_client.get(endpoint)
    data = response.json()

    assert response.status_code != 404
    assert response.status_code == 200
    assert set(data) == set(['id', 'name', 'measurement_unit'])
    assert data == serializer.data


@pytest.mark.django_db(transaction=True)
def test_ingredients_endpoint_allow_only_get_method(guest_client):
    endpoints = ('/api/ingredients/', f'/api/ingredients/{1}/')
    payload = {
        'name': 'Salt',
        'measurement_unit': 'g'
    }
    for endpoint in endpoints:
        response = guest_client.post(endpoint, payload)
        assert response.status_code == 405

        response = guest_client.put(endpoint, payload)
        assert response.status_code == 405

        response = guest_client.patch(endpoint, payload)
        assert response.status_code == 405

        response = guest_client.delete(endpoint, payload)
        assert response.status_code == 405


@pytest.mark.django_db(transaction=True)
def test_filter_ingredients_by_name(guest_client):
    Ingredient.objects.create(name='Salt', measurement_unit='g')
    Ingredient.objects.create(name='Sugar', measurement_unit='kg')
    Ingredient.objects.create(name='??????????', measurement_unit='????')

    response = guest_client.get('/api/ingredients/?name=??????')
    assert response.status_code != 404
    assert response.status_code == 200
    assert len(response.data) == 1
    assert '??????????' in str(response.data)

    response = guest_client.get('/api/ingredients/?name=s')
    assert len(response.data) == 2

    response = guest_client.get('/api/ingredients/?name=ugar')
    assert len(response.data) == 1
