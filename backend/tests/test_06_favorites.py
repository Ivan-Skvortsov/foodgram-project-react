import pytest


MODIFY_FAVORITES_ENDPOINT = '/api/recipes/{id}/favorite/'
FAVORITE_REICPE_FIELDS = {
    'id',
    'name',
    'image',
    'cooking_time'
}


@pytest.mark.django_db(transaction=True)
def test_favorite_endpoint_not_accessed_by_guests(guest_client,
                                                  test_recipes):
    response = guest_client.post(MODIFY_FAVORITES_ENDPOINT)
    assert response.status_code != 404
    assert response.status_code == 401

    response = guest_client.delete(MODIFY_FAVORITES_ENDPOINT)
    assert response.status_code != 404
    assert response.status_code == 401


@pytest.mark.django_db(transaction=True)
def test_add_recipe_to_favorites(authorized_client_1,
                                 test_recipes,
                                 test_user_1):
    endpoint = MODIFY_FAVORITES_ENDPOINT.format(id=test_recipes[0].id)
    favorites_count = test_user_1.favorite_recipes.all().count()

    response = authorized_client_1.post(endpoint)
    assert response.status_code != 404
    assert response.status_code == 201
    assert set(response.json()) == set(FAVORITE_REICPE_FIELDS)

    new_favorites_count = test_user_1.favorite_recipes.all().count()
    assert new_favorites_count == favorites_count + 1


@pytest.mark.django_db(transaction=True)
def test_can_not_add_existing_recipe_to_favorites(authorized_client_1,
                                                  test_recipes,
                                                  test_user_1):
    endpoint = MODIFY_FAVORITES_ENDPOINT.format(
        id=test_recipes[0].id
    )
    response = authorized_client_1.post(endpoint)
    favorites_count = test_user_1.favorite_recipes.all().count()
    assert response.status_code != 404
    assert response.status_code == 201

    response = authorized_client_1.post(endpoint)
    assert response.status_code != 404
    assert response.status_code == 400

    new_favorites_count = test_user_1.favorite_recipes.all().count()
    assert new_favorites_count == favorites_count


@pytest.mark.django_db(transaction=True)
def test_delete_recipe_from_favorites(authorized_client_1,
                                      test_recipes,
                                      test_user_1):
    endpoint = MODIFY_FAVORITES_ENDPOINT.format(
        id=test_recipes[0].id
    )
    response = authorized_client_1.post(endpoint)
    favorites_count = test_user_1.favorite_recipes.all().count()

    response = authorized_client_1.delete(endpoint)
    assert response.status_code != 404
    assert response.status_code == 204

    new_favorites_count = test_user_1.favorite_recipes.all().count()
    assert new_favorites_count == favorites_count - 1


@pytest.mark.django_db(transaction=True)
def test_can_not_del_unexisting_recipe_from_favorites(authorized_client_1,
                                                      test_recipes,
                                                      test_user_1):
    endpoint = MODIFY_FAVORITES_ENDPOINT.format(
        id=test_recipes[0].id
    )
    favorites_count = test_user_1.favorite_recipes.all().count()
    response = authorized_client_1.delete(endpoint)

    assert response.status_code != 404
    assert response.status_code == 400

    new_favorites_count = test_user_1.favorite_recipes.all().count()
    assert new_favorites_count == favorites_count
