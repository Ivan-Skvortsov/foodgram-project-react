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

    assert response.status_code != 404
    assert response.status_code == 200
    assert len(response.data) == tags.count()
    assert set(response.data[0]) == set(['id', 'name', 'color', 'slug'])
    assert response.data == serializer.data


@pytest.mark.django_db(transaction=True)
def test_get_single_tag(guest_client):
    """Test single tag resource."""
    tag = Tag.objects.create(name='Тег 1', color='#a9d27d', slug='tag_color')
    endpoint = f'/api/tags/{tag.pk}/'

    serializer = TagSerializer(tag)
    response = guest_client.get(endpoint)

    assert response.status_code != 404
    assert response.status_code == 200
    assert set(response.data) == set(['id', 'name', 'color', 'slug'])
    assert response.data == serializer.data


@pytest.mark.django_db(transaction=True)
def test_allowed_only_get_method(guest_client):
    """Test allowed HTTP methods: only GET allowed."""
    endpoints = ('/api/tags/', f'/api/tags/{1}/')
    data = {
        'name': 'name',
        'color': '#a9d27d',
        'slug': 'slug'
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
