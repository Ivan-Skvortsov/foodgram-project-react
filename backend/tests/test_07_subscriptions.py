import pytest


SUBSCRIPTIONS_ENDPOINT = '/api/users/subscriptions/'
SUBSCRIPTION_MODIFY_ENDPOINT = '/api/users/{id}/subscribe/'
USERS_FIELDS = [
    'email',
    'id',
    'username',
    'first_name',
    'last_name',
    'is_subscribed',
    'recipes',
    'recipes_count'
]
RECIPE_FIELDS = ['id', 'name', 'image', 'cooking_time']


@pytest.mark.django_db(transaction=True)
def test_get_all_subscriptions(authorized_client_1,
                               test_recipes,
                               test_user_1,
                               test_user_2):
    test_user_1.subscribed_to.add(test_user_2)
    response = authorized_client_1.get(SUBSCRIPTIONS_ENDPOINT)

    assert response.status_code != 404
    assert response.status_code == 200

    data = response.json()
    assert 'count' in data
    assert data['count'] == 1
    assert 'next' in data
    assert 'previous' in data
    assert 'results' in data
    assert type(data['results']) == list
    assert set(data['results'][0]) == set(USERS_FIELDS)
    assert set(data['results'][0]['recipes'][0]) == set(RECIPE_FIELDS)
    assert data['results'][0]['id'] == test_user_2.id
    assert data['results'][0]['recipes_count'] == test_user_2.recipes.all().count()  # noqa E501


@pytest.mark.django_db(transaction=True)
def test_get_subscriptions_with_query_params(authorized_client_1,
                                             test_recipes,
                                             test_user_1,
                                             test_user_2):
    test_user_1.subscribed_to.add(test_user_2)
    endpoint = SUBSCRIPTIONS_ENDPOINT + '?limit=1'
    response = authorized_client_1.get(endpoint)
    assert response.status_code != 404
    assert response.status_code == 200

    endpoint = SUBSCRIPTIONS_ENDPOINT + '?limit=1&page=1'
    response = authorized_client_1.get(endpoint)
    assert response.status_code != 404
    assert response.status_code == 200

    # test_user_2 became an author of all recipes
    for recipe in test_recipes:
        recipe.author = test_user_2
        recipe.save()

    endpoint = SUBSCRIPTIONS_ENDPOINT + '?recipes_limit=1'
    response = authorized_client_1.get(endpoint)
    data = response.json()
    assert response.status_code != 404
    assert response.status_code == 200
    assert len(data['results'][0]['recipes']) == 1


@pytest.mark.django_db(transaction=True)
def test_subscribe_to_user(authorized_client_1,
                           test_user_1,
                           test_user_2):
    endpoint = SUBSCRIPTION_MODIFY_ENDPOINT.format(id=test_user_2.id)
    subscriptions_count = test_user_1.subscribed_to.all().count()

    response = authorized_client_1.post(endpoint)
    assert response.status_code != 404
    assert response.status_code == 201
    assert set(response.json()) == set(USERS_FIELDS)

    new_subscriptions_count = test_user_1.subscribed_to.all().count()
    assert new_subscriptions_count == subscriptions_count + 1

    # user cannot subscibe to himself
    endpoint = SUBSCRIPTION_MODIFY_ENDPOINT.format(id=test_user_1.id)
    response = authorized_client_1.post(endpoint)
    assert response.status_code != 404
    assert response.status_code == 400
    assert new_subscriptions_count == test_user_1.subscribed_to.all().count()


@pytest.mark.django_db(transaction=True)
def test_unsubscribe_user(authorized_client_1,
                          test_user_1,
                          test_user_2):
    endpoint = SUBSCRIPTION_MODIFY_ENDPOINT.format(id=test_user_2.id)

    # unexisting subscription
    response = authorized_client_1.delete(endpoint)
    assert response.status_code != 404
    assert response.status_code == 400

    # subscribe to test_user_2
    response = authorized_client_1.post(endpoint)
    subscriptions_count = test_user_1.subscribed_to.all().count()

    response = authorized_client_1.delete(endpoint)
    assert response.status_code != 404
    assert response.status_code == 204
    assert test_user_1.subscribed_to.all().count() == subscriptions_count - 1


@pytest.mark.django_db(transaction=True)
def test_sub_endpoints_can_not_be_accessed_by_guest(guest_client,
                                                    test_user_2):
    response = guest_client.get(SUBSCRIPTIONS_ENDPOINT)
    assert response.status_code != 404
    assert response.status_code == 401

    response = guest_client.post(
        SUBSCRIPTION_MODIFY_ENDPOINT.format(id=test_user_2.id)
    )
    assert response.status_code != 404
    assert response.status_code == 401

    response = guest_client.delete(
        SUBSCRIPTION_MODIFY_ENDPOINT.format(id=test_user_2.id)
    )
    assert response.status_code != 404
    assert response.status_code == 401
