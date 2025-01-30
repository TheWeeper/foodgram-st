from datetime import datetime

INGREDIENT_ITEM = '{i}. {name} {amount} {measurement_unit}'
RECIPE_ITEM = '{i}. {name}'
LIST_HEADER = 'Список покупок {first_name} {last_name} на {date}'


def render_shopping_list(ingredients, recipes, user):
    return '\n'.join([
        LIST_HEADER.format(
            first_name=user.first_name,
            last_name=user.last_name,
            date=datetime.now()
        ),
        'Продукты',
        *(
            INGREDIENT_ITEM.format(
                i=i,
                name=ingredient['ingredient__name'].capitalize(),
                amount=ingredient['amount_total'],
                measurement_unit=ingredient['ingredient__measurement_unit']
            ) for i, ingredient in enumerate(ingredients, start=1)
        ),
        'Рецепты',
        *(
            RECIPE_ITEM.format(i=i, name=recipe)
            for i, recipe in enumerate(recipes, start=1)
        ),
    ])
