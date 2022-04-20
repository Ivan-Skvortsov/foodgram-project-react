import pytest


SHOPPING_LIST_ENDPOINT = '/api/recipes/download_shopping_cart/'
MODIFY_SHOPPING_LIST_ENDPOINT = '/api/recipes/{id}/shopping_cart/'
SHOPPING_LIST_REICPE_FIELDS = {
    'id',
    'name',
    'image',
    'cooking_time'
}


@pytest.mark.django_db(transaction=True)
def test_get_shopping_list(authorized_client_1, shopping_list_recipes):
    response = authorized_client_1.get(SHOPPING_LIST_ENDPOINT)

    assert response.status_code != 404
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/pdf'


@pytest.mark.django_db(transaction=True)
def test_shopping_list_not_allowed_to_guests(guest_client,
                                             shopping_list_recipes):
    endpoints = [
        SHOPPING_LIST_ENDPOINT,
        MODIFY_SHOPPING_LIST_ENDPOINT.format(id=shopping_list_recipes[0].id)
    ]
    for endpoint in endpoints:
        response = guest_client.get(endpoint)
        assert response.status_code != 404
        assert response.status_code == 401

        response = guest_client.post(endpoint)
        assert response.status_code != 404
        assert response.status_code == 401

        response = guest_client.delete(endpoint)
        assert response.status_code != 404
        assert response.status_code == 401


@pytest.mark.django_db(transaction=True)
def test_add_recipe_to_shopping_list(authorized_client_1,
                                     test_recipes,
                                     test_user_1):
    endpoint = MODIFY_SHOPPING_LIST_ENDPOINT.format(id=test_recipes[0].id)
    shopping_list_count = test_user_1.shoppinglist_recipes.all().count()

    response = authorized_client_1.post(endpoint)
    assert response.status_code != 404
    assert response.status_code == 201
    assert set(response.json()) == set(SHOPPING_LIST_REICPE_FIELDS)

    new_shopping_list_count = test_user_1.shoppinglist_recipes.all().count()
    assert new_shopping_list_count == shopping_list_count + 1


@pytest.mark.django_db(transaction=True)
def test_can_not_add_existing_recipe_to_shopping_list(authorized_client_1,
                                                      shopping_list_recipes,
                                                      test_user_1):
    endpoint = MODIFY_SHOPPING_LIST_ENDPOINT.format(
        id=shopping_list_recipes[0].id
    )
    shopping_list_count = test_user_1.shoppinglist_recipes.all().count()
    response = authorized_client_1.post(endpoint)

    assert response.status_code != 404
    assert response.status_code == 400

    new_shopping_list_count = test_user_1.shoppinglist_recipes.all().count()
    assert new_shopping_list_count == shopping_list_count


@pytest.mark.django_db(transaction=True)
def test_delete_recipe_from_shopping_list(authorized_client_1,
                                          shopping_list_recipes,
                                          test_user_1):
    endpoint = MODIFY_SHOPPING_LIST_ENDPOINT.format(
        id=shopping_list_recipes[0].id
    )
    shopping_list_count = test_user_1.shoppinglist_recipes.all().count()

    response = authorized_client_1.delete(endpoint)
    assert response.status_code != 404
    assert response.status_code == 204

    new_shopping_list_count = test_user_1.shoppinglist_recipes.all().count()
    assert new_shopping_list_count == shopping_list_count - 1


@pytest.mark.django_db(transaction=True)
def test_can_not_del_unexisting_recipe_from_shopping_list(authorized_client_1,
                                                          test_recipes,
                                                          test_user_1):
    endpoint = MODIFY_SHOPPING_LIST_ENDPOINT.format(
        id=test_recipes[0].id
    )
    shopping_list_count = test_user_1.shoppinglist_recipes.all().count()
    response = authorized_client_1.delete(endpoint)

    assert response.status_code != 404
    assert response.status_code == 400

    new_shopping_list_count = test_user_1.shoppinglist_recipes.all().count()
    assert new_shopping_list_count == shopping_list_count
