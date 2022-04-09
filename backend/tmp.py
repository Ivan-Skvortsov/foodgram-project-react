from django.contrib.auth import get_user_model

from recipes.models import Ingredient, Tag, Recipe

User = get_user_model()

user_data = {
    'email': 'user@example.com',
    'username': '@username',
    'first_name': 'Вася',
    'last_name': 'Пупкин',
    'password': 'SomePassword123'
}
test_user_1 = User.objects.create(**user_data)


def test_tagsz():
    Tag.objects.create(name='Тег 1', color='#a9d27d', slug='tag_color')
    Tag.objects.create(name='Тег 2 (без цвета)', slug='tag_no_color')
    Tag.objects.create(name='Тег 3', color='#ffffff', slug='another_tag')
    return Tag.objects.all()


def test_ingredientz():
    Ingredient.objects.create(name='Salt', measurement_unit='g')
    Ingredient.objects.create(name='Sugar', measurement_unit='kg')
    Ingredient.objects.create(name='Milk', measurement_unit='l')
    return Ingredient.objects.all()


def test_recipes():
    test_tags = test_tagsz()
    test_ingredients = test_ingredientz()
    recipe1 = Recipe.objects.create(
        author=test_user_1,
        name='Тестовый рецепт 1',
        image='images/image.png',  # FIXME!
        text='Описание тестового рецепта №1',
        cooking_time=12
    )
    recipe1.save()
    recipe1.tags.add(*test_tags)
    recipe1.ingredients.add(*test_ingredients, through_defaults={'amount': 3})

    recipe2 = Recipe.objects.create(
        author=test_user_1,
        name='Тестовый рецепт 2',
        image='images/image.png',  # FIXME!
        text='Описание тестового рецепта №2',
        cooking_time=1
    )
    recipe2.save()
    recipe2.tags.add(test_tags[0])
    recipe2.ingredients.add(
        test_ingredients[0], through_defaults={'amount': 2}
    )

    return Recipe.objects.all()
