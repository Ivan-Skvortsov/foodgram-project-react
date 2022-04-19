import pytest

from recipes.models import Tag, Ingredient, Recipe, ShoppingList


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
        image='',
        name='Тестовый рецепт 1',
        text='Описание тестового рецепта №1',
        cooking_time=12
    )
    recipe1.save()
    recipe1.tags.add(*test_tags)
    recipe1.ingredients.add(*test_ingredients, through_defaults={'amount': 3})

    recipe2 = Recipe.objects.create(
        author=test_user_2,
        image='',
        name='Тестовый рецепт 2',
        text='Описание тестового рецепта №2',
        cooking_time=1
    )
    recipe2.save()
    less_tags = test_tags[::-1]
    less_ingredients = test_ingredients[::-1]
    recipe2.tags.add(*less_tags)
    recipe2.ingredients.add(
        *less_ingredients, through_defaults={'amount': 2}
    )

    return Recipe.objects.all()


@pytest.fixture
def valid_recipe_data(test_ingredients, test_tags):
    return {
        'ingredients': [
            {'id': test_ingredients[0].pk, 'amount': 10},
            {'id': test_ingredients[1].pk, 'amount': 5}
        ],
        'tags': [test_tags[0].pk, test_tags[1].pk],
        'image': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==',  # noqa
        'name': 'Рецепт, созданный/измененный запросом API',
        'text': 'Описание рецепта',
        'cooking_time': 1
    }


@pytest.fixture
def shopping_list_recipes(test_recipes, test_user_1):
    ShoppingList.objects.create(
        user=test_user_1,
        recipe=test_recipes[0]
    )
    ShoppingList.objects.create(
        user=test_user_1,
        recipe=test_recipes[1]
    )
    return Recipe.objects.all()
