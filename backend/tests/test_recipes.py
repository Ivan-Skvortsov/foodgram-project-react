import pytest

from recipes.models import Favorite, ShoppingList
from api.serializers import RecipeSerializer

RECIPES_ENDPOINT = '/api/recipes/'

RECIPE_FIELDS = [
    'id',
    'tags',
    'author',
    'ingredients',
    'is_favorited',
    'is_in_shopping_cart',
    'name',
    'image',
    'text',
    'cooking_time'
]
TAG_FIELDS = ['id', 'name', 'color', 'slug']
INGREDIENT_FIELDS = ['id', 'name', 'measurement_unit', 'amount']
AUTHOR_FIELDS = ['email', 'id', 'username', 'first_name', 'last_name',
                 'is_subscribed']


@pytest.mark.django_db(transaction=True)
def test_get_all_recipes(guest_client, test_recipes):
    response = guest_client.get(RECIPES_ENDPOINT)
    assert response.status_code != 404
    assert response.status_code == 200

    data = response.json()
    assert 'count' in data
    assert data['count'] == 2
    assert 'next' in data
    assert 'previous' in data
    assert 'results' in data
    assert type(data['results']) == list
    assert set(data['results'][0]) == set(RECIPE_FIELDS)

    assert type(data['results'][0]['tags']) == list
    assert set(data['results'][0]['tags'][0]) == set(TAG_FIELDS)

    assert type(data['results'][0]['ingredients']) == list
    assert set(data['results'][0]['ingredients'][0]) == set(INGREDIENT_FIELDS)

    assert type(data['results'][0]['author']) == dict
    assert set(data['results'][0]['author']) == set(AUTHOR_FIELDS)

    serializer = RecipeSerializer(test_recipes, many=True)
    assert data['results'] == serializer.data


@pytest.mark.django_db(transaction=True)
def test_recipes_pagination(guest_client, test_recipes):
    endpoint = RECIPES_ENDPOINT + '?limit=1'
    response = guest_client.get(endpoint)
    assert response.status_code != 404
    assert response.status_code == 200

    data = response.json()
    assert data['count'] == 2
    assert len(data['results']) == 1
    assert test_recipes[0].name in data['results'][0].values()

    endpoint = RECIPES_ENDPOINT + '?limit=1&page=2'
    response = guest_client.get(endpoint)
    data = response.json()
    assert response.status_code != 404
    assert response.status_code == 200
    assert data['count'] == 2
    assert len(data['results']) == 1
    assert test_recipes[1].name in data['results'][0].values()


def test_get_recipes_with_filter_favorites(authorized_client_1,
                                           test_user_1,
                                           test_recipes):
    endpoint = RECIPES_ENDPOINT + '?is_favorited=1'
    Favorite.objects.create(user=test_user_1, recipe=test_recipes[0])
    response = authorized_client_1.get(endpoint)

    assert response.status_code != 404
    assert response.status_code == 200

    data = response.json()
    assert data['count'] == 2
    assert len(data['results']) == 1
    assert data['results'][0]['id'] == test_recipes[0].id


def test_get_recipes_with_filter_shopping_list(authorized_client_1,
                                               test_user_1,
                                               test_recipes):
    endpoint = RECIPES_ENDPOINT + '?is_in_shopping_cart=1'
    ShoppingList.objects.create(user=test_user_1, recipe=test_recipes[0])
    response = authorized_client_1.get(endpoint)

    assert response.status_code != 404
    assert response.status_code == 200

    data = response.json()
    assert data['count'] == 2
    assert len(data['results']) == 1
    assert data['results'][0]['id'] == test_recipes[0].id


def test_get_recipes_with_filter_by_author(authorized_client_1,
                                           test_user_1,
                                           test_user_2,
                                           test_recipes):
    endpoint = RECIPES_ENDPOINT + f'?author={test_user_1.pk}'
    response = authorized_client_1.get(endpoint)

    assert response.status_code != 404
    assert response.status_code == 200

    data = response.json()
    assert data['count'] == 1
    assert len(data['results']) == 1
    assert data['results'][0]['id'] == test_recipes[0].id

    test_recipes.update(author=test_user_2)

    response = authorized_client_1.get(endpoint)
    data = response.json()
    assert data['count'] == 0
    assert len(data['results']) == 0

    test_recipes.update(author=test_user_1)

    response = authorized_client_1.get(endpoint)
    data = response.json()
    assert data['count'] == 2
    assert len(data['results']) == 2


def test_get_recipes_with_filter_by_tags(authorized_client_1,
                                         test_tags,
                                         test_recipes):
    endpoint = (RECIPES_ENDPOINT +
                f'?tags={test_tags[0].slug}&tags={test_tags[1].slug}')

    test_recipes[1].tags.clear()
    response = authorized_client_1.get(endpoint)

    assert response.status_code != 404
    assert response.status_code == 200

    data = response.json()
    assert data['count'] == 1
    assert len(data['results']) == 1
    assert data['results'][0]['id'] == test_recipes[0].id

    test_recipes[1].tags.add(test_tags[0])
    response = authorized_client_1.get(endpoint)
    data = response.json()
    assert response.json()['count'] == 1

    test_recipes[1].tags.add(test_tags[1])
    response = authorized_client_1.get(endpoint)
    data = response.json()
    assert response.json()['count'] == 2
