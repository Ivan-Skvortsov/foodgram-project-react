import pytest

from recipes.models import Favorite, Recipe, ShoppingList
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
    assert data['count'] == 1
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
    assert data['count'] == 1
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
    endpoint = (
        RECIPES_ENDPOINT + f'?tags={test_tags[0].slug}&tags={test_tags[1].slug}'  # noqa E501
    )

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
    assert response.json()['count'] == 2

    test_recipes[1].tags.add(test_tags[1])
    response = authorized_client_1.get(endpoint)
    data = response.json()
    assert response.json()['count'] == 2


@pytest.mark.django_db(transaction=True)
def test_create_recipe_empty_data(authorized_client_1, valid_recipe_data):
    response = authorized_client_1.post(RECIPES_ENDPOINT)

    assert response.status_code != 404
    assert response.status_code == 400

    for field in valid_recipe_data.keys():
        assert field in response.json()

    assert not Recipe.objects.all().exists()


@pytest.mark.django_db(transaction=True)
def test_create_recipe_invalid_data(authorized_client_1, valid_recipe_data):
    invalid_data = valid_recipe_data
    invalid_data['ingredients'] = [1, 2]
    invalid_data['cooking_time'] = 'two minutes'
    invalid_data['tags'] = ['tag_one', 'tag_two']
    response = authorized_client_1.post(RECIPES_ENDPOINT, invalid_data)

    assert response.status_code != 404
    assert response.status_code == 400
    for field in ['ingredients', 'cooking_time', 'tags']:
        assert field in response.json()

    assert not Recipe.objects.all().exists()


@pytest.mark.django_db(transaction=True)
def test_create_recipe_valid_data(authorized_client_1, valid_recipe_data):
    response = authorized_client_1.post(
        RECIPES_ENDPOINT, valid_recipe_data, format='json'
    )

    assert response.status_code != 404
    assert response.status_code == 201

    recipe = Recipe.objects.all()
    assert recipe.exists()
    assert recipe.count() == 1

    data = response.json()
    assert set(data) == set(RECIPE_FIELDS)


@pytest.mark.django_db(transaction=True)
def test_create_recipe_unexisted_tags(authorized_client_1, valid_recipe_data):
    valid_recipe_data['tags'].append(123)
    response = authorized_client_1.post(
        RECIPES_ENDPOINT, valid_recipe_data, format='json')
    assert response.status_code != 404
    assert response.status_code == 400
    assert not Recipe.objects.all().exists()


@pytest.mark.django_db(transaction=True)
def test_create_recipe_unexisted_ingredients(authorized_client_1,
                                             valid_recipe_data):
    valid_recipe_data['ingredients'].append({'id': 123, 'amount': 5})
    response = authorized_client_1.post(
        RECIPES_ENDPOINT, valid_recipe_data, format='json')
    assert response.status_code != 404
    assert response.status_code == 400
    assert not Recipe.objects.all().exists()


@pytest.mark.django_db(transaction=True)
def test_create_recipe_unavailable_to_guest(guest_client, valid_recipe_data):
    response = guest_client.post(
        RECIPES_ENDPOINT, valid_recipe_data, format='json'
    )

    assert response.status_code != 404
    assert response.status_code == 401
    assert not Recipe.objects.all().exists()


@pytest.mark.django_db(transaction=True)
def test_get_single_recipe_by_id(guest_client, test_recipes):
    endpoint = RECIPES_ENDPOINT + f'{test_recipes[0].pk}/'
    response = guest_client.get(endpoint)
    assert response.status_code != 404
    assert response.status_code == 200

    data = response.json()
    assert set(data) == set(RECIPE_FIELDS)

    assert type(data['tags']) == list
    assert set(data['tags'][0]) == set(TAG_FIELDS)

    assert type(data['ingredients']) == list
    assert set(data['ingredients'][0]) == set(INGREDIENT_FIELDS)

    assert type(data['author']) == dict
    assert set(data['author']) == set(AUTHOR_FIELDS)

    serializer = RecipeSerializer(test_recipes[0])
    assert data == serializer.data


@pytest.mark.django_db(transaction=True)
def test_update_recipe_valid_data(authorized_client_1,
                                  test_recipes,
                                  valid_recipe_data):
    # authorized_client_1 is author of test_recipes[0]
    endpoint = RECIPES_ENDPOINT + f'{test_recipes[0].pk}/'
    response = authorized_client_1.patch(
        endpoint, valid_recipe_data, format='json'
    )

    assert response.status_code != 404
    assert response.status_code == 200

    data = response.json()
    assert set(data) == set(RECIPE_FIELDS)
    assert data['text'] == valid_recipe_data['text']
    assert data['name'] == valid_recipe_data['name']
    assert data['cooking_time'] == valid_recipe_data['cooking_time']


@pytest.mark.django_db(transaction=True)
def test_update_recipe_invalid_data(authorized_client_1,
                                    test_recipes,
                                    valid_recipe_data):
    invalid_data = valid_recipe_data
    invalid_data['cooking_time'] = 'two minutes'
    invalid_data['tags'] = ['tag_one', 'tag_two']
    endpoint = RECIPES_ENDPOINT + f'{test_recipes[0].pk}/'
    response = authorized_client_1.patch(endpoint, invalid_data)

    assert response.status_code != 404
    assert response.status_code == 400
    for field in ['cooking_time', 'tags']:
        assert field in response.json()


@pytest.mark.django_db(transaction=True)
def test_update_recipe_empty_data(authorized_client_1,
                                  test_recipes,
                                  valid_recipe_data):
    endpoint = RECIPES_ENDPOINT + f'{test_recipes[0].pk}/'
    response = authorized_client_1.patch(endpoint)

    assert response.status_code != 404
    assert response.status_code == 400

    for field in valid_recipe_data.keys():
        assert field in response.json()


@pytest.mark.django_db(transaction=True)
def test_update_recipe_not_allowed_to_guest(guest_client,
                                            test_recipes,
                                            valid_recipe_data):
    endpoint = RECIPES_ENDPOINT + f'{test_recipes[0].pk}/'
    response = guest_client.patch(endpoint, valid_recipe_data)
    assert response.status_code != 404
    assert response.status_code == 401


@pytest.mark.django_db(transaction=True)
def test_update_recipe_allowed_only_to_author(authorized_client_1,
                                              test_recipes,
                                              valid_recipe_data):
    # authorized_client_1 is author of test_recipes[0].
    endpoint = RECIPES_ENDPOINT + f'{test_recipes[1].pk}/'
    response = authorized_client_1.patch(endpoint, valid_recipe_data)
    assert response.status_code != 404
    assert response.status_code == 403


@pytest.mark.django_db(transaction=True)
def test_update_unexisted_recipe_returns_404(authorized_client_1,
                                             test_recipes,
                                             valid_recipe_data):
    endpoint = RECIPES_ENDPOINT + '555/'
    response = authorized_client_1.patch(endpoint, valid_recipe_data)
    assert response.status_code == 404


@pytest.mark.django_db(transaction=True)
def test_delete_unexisted_recipe_returns_404(authorized_client_1,
                                             test_recipes,
                                             valid_recipe_data):
    endpoint = RECIPES_ENDPOINT + '555/'
    response = authorized_client_1.patch(endpoint, valid_recipe_data)
    assert response.status_code == 404


@pytest.mark.django_db(transaction=True)
def test_delete_recipe_allowed_only_to_author(authorized_client_1,
                                              guest_client,
                                              test_recipes,
                                              valid_recipe_data):
    # authorized_client_1 is author of test_recipes[0]
    endpoint = RECIPES_ENDPOINT + f'{test_recipes[1].pk}/'
    response = guest_client.delete(endpoint)
    assert response.status_code != 404
    assert response.status_code == 401
    assert Recipe.objects.all().count() == len(test_recipes)

    response = authorized_client_1.delete(endpoint)
    assert response.status_code != 404
    assert response.status_code == 403
    assert Recipe.objects.all().count() == len(test_recipes)

    endpoint = RECIPES_ENDPOINT + f'{test_recipes[0].pk}/'
    response = authorized_client_1.delete(endpoint)
    assert response.status_code != 404
    assert response.status_code == 204
    assert Recipe.objects.all().count() == len(test_recipes) - 1
