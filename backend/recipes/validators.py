from django.core.exceptions import ValidationError


def cooking_time_validator(value):
    if value < 1:
        raise ValidationError(
            'Значение не может быть меньше 1!'
        )
