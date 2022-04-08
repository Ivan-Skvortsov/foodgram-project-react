import pytest

from recipes.models import Tag
from api.serializers import TagSerializer


@pytest.mark.django_db(transaction=True)
def test_get_all_tags(guest_client):
    """Test tag list resource."""
    endpoint = '/api/tags/'

    Tag.objects.create(name='Тег 1', color='#a9d27d', slug='tag_color')
    Tag.objects.create(name='Тег 2 (без цвета)', slug='tag_no_color')

    tags = Tag.objects.all()
    serializer = TagSerializer(tags, many=True)

    response = guest_client.get(endpoint)
    data = response.json()

    assert response.status_code != 404
    assert response.status_code == 200
    assert len(data) == tags.count()
    assert set(data[0]) == set(['id', 'name', 'color', 'slug'])
    assert data == serializer.data


@pytest.mark.django_db(transaction=True)
def test_get_single_tag(guest_client):
    """Test single tag resource."""
    tag = Tag.objects.create(name='Тег 1', color='#a9d27d', slug='tag_color')
    endpoint = f'/api/tags/{tag.pk}/'

    serializer = TagSerializer(tag)
    response = guest_client.get(endpoint)
    data = response.json()

    assert response.status_code != 404
    assert response.status_code == 200
    assert set(data) == set(['id', 'name', 'color', 'slug'])
    assert data == serializer.data


@pytest.mark.django_db(transaction=True)
def test_tags_endpoint_allow_only_get_method(guest_client):
    """Test that tags resource allow only GET http method."""
    endpoints = ('/api/tags/', f'/api/tags/{1}/')
    payload = {
        'name': 'name',
        'color': '#a9d27d',
        'slug': 'slug'
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
