import os

from io import BytesIO
from typing import List

from django.http import HttpResponse
from django.template.loader import get_template
from django.db.models import QuerySet
from django.contrib.auth import get_user_model
from django.conf import settings

from xhtml2pdf import pisa


UserModel = get_user_model()


class ShoppingListGenerator:

    def __init__(self, user: UserModel) -> None:
        self.user = user

    def get_list_of_all_ingredient_querysets(self) -> List[QuerySet]:
        """
        Returns list of querysets of all recipes ingredients
        from user's shopping list.
        """
        ingredients = []
        shopping_list = self.user.shoppinglist_recipes.all()
        for entry in shopping_list:
            ingredients.append(entry.recipe.recipe_ingredients.all())
        return ingredients

    def get_all_ingredients_with_amounts(
        self, ingredients_list: List[QuerySet]
    ) -> dict:
        """
        Gets list of ingredient querysets, returns dict of ingredients with
        amounts and measurement units, e.g.:
            {'salt': {'amount': 100,
                      'measurement_unit': 'kg'}}
        """
        output = {}
        for queryset in ingredients_list:
            for entry in queryset:
                ingredient = entry.ingredient.name
                if ingredient in output:
                    output[ingredient]['amount'] += entry.amount
                else:
                    output[ingredient] = {
                        'amount': entry.amount,
                        'measurement_unit': entry.ingredient.measurement_unit
                    }
        return output

    def link_callback(self, uri, rel):
        """Convert HTML URI to absolute system path so xhtml2pdf can access those
            resources."""
        return os.path.join(
            settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, '')
        )

    def render_pdf_from_html_template(
        self, template_name: str = None, context: dict = None
    ) -> HttpResponse:
        """Render html template, converts it to PDF and returns as
        HttpResponse."""
        if not template_name:
            template = get_template('shopping_list_template.html')
        else:
            template = get_template(template_name)
        html = template.render({'ingredients': context})
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')),
                                result,
                                link_callback=self.link_callback)
        if pdf.err:
            return HttpResponse('Ops, something went worng')
        return HttpResponse(result.getvalue(), content_type='application/pdf')

    def generate_pdf(self) -> HttpResponse:
        """Entry point to generate shopping list pdf."""
        ingredient_list = self.get_list_of_all_ingredient_querysets()
        context = self.get_all_ingredients_with_amounts(ingredient_list)
        return self.render_pdf_from_html_template(context=context)
