import pytest


from recipes.models import Tag, Ingredient, Recipe


@pytest.fixture
def guest_client():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def test_user_1(django_user_model):
    user_data = {
        'email': 'user@example.com',
        'username': '@username',
        'first_name': 'Вася',
        'last_name': 'Пупкин',
        'password': 'SomePassword123'
    }
    return django_user_model.objects.create(**user_data)


@pytest.fixture
def test_user_2(django_user_model):
    user_data = {
        'email': 'user2@example.com',
        'username': '@username2',
        'first_name': 'Петя',
        'last_name': 'Курочкин',
        'password': 'SomePassword123'
    }
    return django_user_model.objects.create(**user_data)


@pytest.fixture
def authorized_client_1(test_user_1):
    from rest_framework.authtoken.models import Token
    from rest_framework.test import APIClient
    token = Token.objects.get_or_create(user=test_user_1)[0]
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    return client


@pytest.fixture
def test_tags():
    Tag.objects.create(name='Тег 1', color='#a9d27d', slug='tag_color')
    Tag.objects.create(name='Тег 2 (без цвета)', slug='tag_no_color')
    Tag.objects.create(name='Тег 3', color='#ffffff', slug='another_tag')
    return Tag.objects.all()


@pytest.fixture
def test_ingredients():
    Ingredient.objects.create(name='Salt', measurement_unit='g')
    Ingredient.objects.create(name='Sugar', measurement_unit='kg')
    Ingredient.objects.create(name='Milk', measurement_unit='l')
    return Ingredient.objects.all()


@pytest.fixture
def test_recipes(test_tags, test_ingredients, test_user_1, test_user_2):
    recipe1 = Recipe.objects.create(
        author=test_user_1,
        name='Тестовый рецепт 1',
        # image='images/image.png',  # FIXME!
        text='Описание тестового рецепта №1',
        cooking_time=12
    )
    recipe1.save()
    recipe1.tags.add(*test_tags)
    recipe1.ingredients.add(*test_ingredients, through_defaults={'amount': 3})

    recipe2 = Recipe.objects.create(
        author=test_user_2,
        name='Тестовый рецепт 2',
        # image='images/image.png',  # FIXME!
        text='Описание тестового рецепта №2',
        cooking_time=1
    )
    recipe2.save()
    less_tags = test_tags[::-1]
    recipe2.tags.add(*less_tags)
    less_ingredients = test_ingredients[::-1]
    recipe2.ingredients.add(
        *less_ingredients, through_defaults={'amount': 2}
    )

    return Recipe.objects.all()
