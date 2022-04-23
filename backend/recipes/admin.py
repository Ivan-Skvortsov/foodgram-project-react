from django.contrib import admin, messages
from django.conf.urls import url
from django.http import HttpResponseRedirect

from recipes.models import Tag, Ingredient, Recipe


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    change_list_template = 'admin/ingredient_change_list.html'
    list_display = ('name', 'measurement_unit')
    search_fields = ('name', )

    def get_urls(self):
        urls = super(IngredientAdmin, self).get_urls()
        custom_urls = [url('import_json/', self.import_ingredients_from_json)]
        return custom_urls + urls

    def import_ingredients_from_json(self, request):
        import json
        json_file = request.FILES['json_file']
        try:
            json_data = json.loads(json_file.read())
            ingredients = []
            for entry in json_data:
                ingredients.append(Ingredient(**entry))
            Ingredient.objects.bulk_create(ingredients)
            self.message_user(request, 'Ингредиенты импортированы')
        except Exception as e:
            self.message_user(request, f'Ошибка: {e}', level=messages.ERROR)
        return HttpResponseRedirect('../')


class IngredientsInLine(admin.TabularInline):
    model = Recipe.ingredients.through


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author_username')
    search_fields = ('author__username', 'name')
    list_filter = ('tags', )
    fields = ('author', 'name', 'tags', 'text', 'image', 'cooking_time',
              'favorite_count')
    readonly_fields = ('favorite_count', )
    inlines = (IngredientsInLine, )

    @admin.display(description='Автор')
    def author_username(self, obj):
        return obj.author.username

    @admin.display(description='В избранном у')
    def favorite_count(self, obj):
        count = obj.favorite_recipes.all().count()
        return f'{count} чел.'
