import pytest

from http import HTTPStatus

from recipes.models import Tag
from api.serializers import TagSerializer


@pytest.mark.django_db(transaction=True)
def test_get_all_tags(guest_client):
    """Test tag list resource."""
    endpoint = '/api/v1/tags/'

    Tag.objects.create(name='Тег 1', color='#a9d27d', slug='tag_color')
    Tag.objects.create(name='Тег 2 (без цвета)', slug='tag_no_color')

    tags = Tag.objects.all()
    serializer = TagSerializer(tags, many=True)

    response = guest_client.get(endpoint)

    assert response.status_code != HTTPStatus.NOT_FOUND
    assert response.status_code == HTTPStatus.OK
    assert type(response.data) == list
    assert len(response.data) == tags.count()
    assert response.data == serializer.data


@pytest.mark.django_db(transaction=True)
def test_get_single_tag(guest_client):
    """Test single tag resource."""
    tag = Tag.objects.create(name='Тег 1', color='#a9d27d', slug='tag_color')
    endpoint = f'/api/v1/tags/{tag.pk}/'

    serializer = TagSerializer(tag)
    response = guest_client.get(endpoint)

    assert response.status_code != HTTPStatus.NOT_FOUND
    assert response.status_code == HTTPStatus.OK
    assert type(response.data) == dict
    assert set(response.data) == set(['name', 'color', 'slug'])
    assert response.data == serializer.data


def test_allowed_only_get_method(guest_client):
    """Test HTTP methods: only GET allowed."""
    endpoints = ('/api/v1/tags/', f'/api/v1/tags/{1}/')
    data = {
        'name': 'name',
        'color': '#a9d27d',
        'slug': 'slug'
    }
    for endpoint in endpoints:
        response = guest_client.post(endpoint, data)
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

        response = guest_client.put(endpoint, data)
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

        response = guest_client.patch(endpoint, data)
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

        response = guest_client.delete(endpoint, data)
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

        response = guest_client.head(endpoint, data)
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

        response = guest_client.options(endpoint, data)
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
