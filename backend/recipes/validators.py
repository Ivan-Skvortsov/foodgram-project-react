from django.core.exceptions import ValidationError


def cooking_time_validator(value):
    if value < 1:
        raise ValidationError(
            'Время приготовления не может быть меньше 1 минуты!'
        )
