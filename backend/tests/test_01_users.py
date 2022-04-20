import pytest

from django.contrib.auth import get_user_model

from api.serializers import UserSerializer


User = get_user_model()

API_USERS_ENDPOINT = '/api/users/'
CURRENT_USER_ENDPOINT = '/api/users/me/'
CHANGE_PASSWORD_ENDPOINT = '/api/users/set_password/'
GET_TOKEN_ENDPOINT = '/api/auth/token/login/'
DELETE_TOKEN_ENDPOINT = '/api/auth/token/logout/'

USER_FIELDS = [
    'email',
    'id',
    'username',
    'first_name',
    'last_name',
    'is_subscribed'
]


@pytest.mark.django_db(transaction=True)
def test_get_all_users(guest_client, test_user_1):
    serializer = UserSerializer(instance=test_user_1)
    response = guest_client.get(API_USERS_ENDPOINT)

    assert response.status_code != 404
    assert response.status_code == 200

    data = response.json()
    assert 'count' in data
    assert data['count'] == 1
    assert 'next' in data
    assert 'previous' in data
    assert 'results' in data
    assert type(data['results']) == list
    assert set(data['results'][0]) == set(USER_FIELDS)
    assert data['results'][0] == serializer.data


@pytest.mark.django_db(transaction=True)
def test_get_all_users_with_pagination_query_params(
    guest_client, test_user_1, test_user_2
):
    endpoint = API_USERS_ENDPOINT + '?limit=1'
    response = guest_client.get(endpoint)
    assert response.status_code != 404
    assert response.status_code == 200

    data = response.json()
    assert data['count'] == 2
    assert len(data['results']) == 1
    assert test_user_1.username in data['results'][0].values()

    endpoint = API_USERS_ENDPOINT + '?limit=1&page=2'
    response = guest_client.get(endpoint)
    data = response.json()
    assert response.status_code != 404
    assert response.status_code == 200
    assert data['count'] == 2
    assert len(data['results']) == 1
    assert test_user_2.username in data['results'][0].values()


@pytest.mark.django_db(transaction=True)
def test_user_signup_with_empty_data(guest_client):
    response = guest_client.post(API_USERS_ENDPOINT)
    assert response.status_code != 404
    assert response.status_code == 400
    response_fields = response.json().keys()
    required_fields_for_signup = ['email', 'username', 'first_name',
                                  'last_name', 'password']
    for field in required_fields_for_signup:
        assert field in response_fields


@pytest.mark.django_db(transaction=True)
def test_user_signup_with_invalid_data(guest_client):
    invalid_user_data = {
        'email': 'invalid_mail',
        'username': 'invalid_username!',
        'first_name': 'Вася',
        'last_name': 'Пупкин',
        'password': 'SomePassword123'
    }
    response = guest_client.post(API_USERS_ENDPOINT, data=invalid_user_data)

    assert response.status_code != 404
    assert response.status_code == 400

    invalid_fields = ['email', 'username']
    for field in invalid_fields:
        assert field in response.json().keys()

    invalid_user_data['email'] = 'valid@mail.com'
    response = guest_client.post(API_USERS_ENDPOINT, data=invalid_user_data)
    assert response.status_code == 400

    invalid_user_data['username'] = 'valid_username'
    del invalid_user_data['password']

    response = guest_client.post(API_USERS_ENDPOINT, data=invalid_user_data)
    assert response.status_code == 400


@pytest.mark.django_db(transaction=True)
def test_user_signup_with_valid_data(guest_client):
    valid_user_data = {
        'email': 'someuser@example.com',
        'username': 'notherusern@me',
        'first_name': 'Вася',
        'last_name': 'Пупкин',
        'password': 'SomePassword123'
    }
    response = guest_client.post(API_USERS_ENDPOINT, data=valid_user_data)
    assert response.status_code != 404
    assert response.status_code == 201
    created_user = User.objects.filter(username=valid_user_data['username'])
    assert created_user.exists()


@pytest.mark.django_db(transaction=True)
def test_get_single_user_by_id(authorized_client_1, test_user_1):
    endpoint_404 = API_USERS_ENDPOINT + '555/'
    response = authorized_client_1.get(endpoint_404)
    assert response.status_code == 404

    endpoint = API_USERS_ENDPOINT + f'{test_user_1.pk}/'
    response = authorized_client_1.get(endpoint)
    serializer = UserSerializer(instance=test_user_1)

    assert response.status_code != 404
    assert response.status_code == 200
    assert serializer.data == response.json()

    # delete credentials
    authorized_client_1.credentials()
    response = authorized_client_1.get(endpoint)
    assert response.status_code != 404
    assert response.status_code == 401


@pytest.mark.django_db(transaction=True)
def test_delete_or_modify_user_not_allowed(authorized_client_1, test_user_1):
    payload = {
        'email': 'user@example.com',
        'username': '@username',
        'first_name': 'Вася',
        'last_name': 'Пупкин',
        'password': 'SomePassword123'
    }
    endpoints = [API_USERS_ENDPOINT,
                 CURRENT_USER_ENDPOINT,
                 API_USERS_ENDPOINT + f'{test_user_1.pk}/']
    for endpoint in endpoints:
        response = authorized_client_1.put(endpoint, payload)
        assert response.status_code != 404
        assert response.status_code == 403

        response = authorized_client_1.patch(endpoint, payload)
        assert response.status_code != 404
        assert response.status_code == 403

        response = authorized_client_1.delete(endpoint, payload)
        assert response.status_code != 404
        assert response.status_code == 403


@pytest.mark.django_db(transaction=True)
def test_get_current_user(authorized_client_1, test_user_1):
    # Test_user_1 is user instance of authorized_client_1
    serializer = UserSerializer(instance=test_user_1)
    response = authorized_client_1.get(CURRENT_USER_ENDPOINT)
    response_data = response.json()

    assert response.status_code != 404
    assert response.status_code == 200
    assert response_data == serializer.data

    # delete credentials
    authorized_client_1.credentials()
    response = authorized_client_1.get(CURRENT_USER_ENDPOINT)
    assert response.status_code != 404
    assert response.status_code == 401


@pytest.mark.django_db(transaction=True)
def test_user_change_passwd_with_valid_data(authorized_client_1, test_user_1):
    valid_payload = {
        'new_password': 'NewPassword123',
        'current_password': 'SomePassword123'
    }
    test_user_1.set_password(valid_payload['current_password'])
    test_user_1.save()

    response = authorized_client_1.post(
        CHANGE_PASSWORD_ENDPOINT, valid_payload
    )

    assert response.status_code != 404
    assert response.status_code == 204
    assert response.data is None


@pytest.mark.django_db(transaction=True)
def test_user_change_password_invalid_data(authorized_client_1, test_user_1):
    payload_invalid_old_password = {
        'new_password': 'NewPassword123',
        'current_password': 'WrongPassword'
    }
    response = authorized_client_1.post(
        CHANGE_PASSWORD_ENDPOINT, payload_invalid_old_password
    )
    assert response.status_code != 404
    assert response.status_code == 400
    assert not test_user_1.check_password(
        payload_invalid_old_password['new_password']
    )

    payload_invalid_new_password = {
        'new_password': '123',
        'current_password': 'SomePassword123'
    }
    invalid_new_passwords = ['', ('tuple',), 123, 'pw']
    for passwd in invalid_new_passwords:
        payload_invalid_new_password['new_password'] = passwd
        response = authorized_client_1.post(
            CHANGE_PASSWORD_ENDPOINT, payload_invalid_new_password
        )
        assert response.status_code == 400


@pytest.mark.django_db(transaction=True)
def test_user_change_password_empty_data(authorized_client_1):
    response = authorized_client_1.post(CHANGE_PASSWORD_ENDPOINT)

    assert response.status_code != 404
    assert response.status_code == 400

    required_fields = ['new_password', 'current_password']
    for field in required_fields:
        assert field in response.json()


@pytest.mark.django_db(transaction=True)
def test_unauth_user_change_password(guest_client):
    response = guest_client.post(CHANGE_PASSWORD_ENDPOINT)
    assert response.status_code != 404
    assert response.status_code == 401


@pytest.mark.django_db(transaction=True)
def test_users_get_token(guest_client, test_user_1):
    valid_password = 'SomePass123'
    test_user_1.set_password(valid_password)
    test_user_1.save()

    valid_payload = {
        'password': valid_password,
        'email': test_user_1.email,
    }
    response = guest_client.post(GET_TOKEN_ENDPOINT, valid_payload)

    assert response.status_code != 404
    assert response.status_code == 200
    assert 'auth_token' in response.json()


@pytest.mark.django_db(transaction=True)
def test_users_delete_token_authorized_client(authorized_client_1):
    response = authorized_client_1.post(DELETE_TOKEN_ENDPOINT)
    assert response.status_code != 404
    assert response.status_code == 204


@pytest.mark.django_db(transaction=True)
def test_users_delete_token_unauthorized_client(guest_client):
    response = guest_client.post(DELETE_TOKEN_ENDPOINT)
    assert response.status_code != 404
    assert response.status_code == 401
