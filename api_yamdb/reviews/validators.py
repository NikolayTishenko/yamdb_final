from django.core.exceptions import ValidationError
from django.utils import timezone
from re import findall


ANTI_PATTERN = r'[^\w.@+-]'


def validate_year(value):
    current_year = timezone.now().year
    if value > current_year:
        raise ValidationError(
            ('Год выпуска произведения - {} не может быть больше '
             'текущего года - {}!'.format(value, current_year))
        )
    return value


def validate_username(data):
    if data == 'me':
        raise ValidationError('Имя "me" не использовать!')

    result = set(findall(ANTI_PATTERN, data))
    if result:
        raise ValidationError(
            f'В имени недопустимые символы: {"".join(result)}'
        )
    return data
