from datetime import datetime


def render_shopping_list(ingredients, recipes):
    ingredients_list = (
        f'{i + 1}.  {ingredient["ingredient__name"].capitalize()} '
        f'{ingredient["amount_total"]}'
        f'{ingredient["ingredient__measurement_unit"]}'
        for i, ingredient in enumerate(ingredients)
    )
    recipes_list = [f'{i + 1} {recipe}' for i, recipe in enumerate(recipes)]
    return '\n'.join([
        f'Список покупок на {datetime.now()}',
        'Продукты',
        *ingredients_list,
        'Рецепты',
        *recipes_list,
    ])
