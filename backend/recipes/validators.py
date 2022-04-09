from django.core.exceptions import ValidationError


def cooking_time_validator(value):
    if value < 1:
        raise ValidationError('Cooking time can not be less than 1 minute!')
