import django_filters

from recipes.models import Recipe


class RecipeFilter(django_filters.FilterSet):
    is_favorited = django_filters.NumberFilter(method='filter_is_favorited')
    is_in_shopping_cart = django_filters.NumberFilter(
        method='filter_is_inshopping_cart')

    class Meta:
        model = Recipe
        fields = ('author',)

    def filter_is_favorited(self, recipes, name, value):
        user = self.request.user
        if user.is_authenticated and value:
            return recipes.filter(favoriterecipes__user=user)
        return recipes

    def filter_is_inshopping_cart(self, recipes, name, value):
        user = self.request.user
        if user.is_authenticated and value:
            return recipes.filter(shoppingcarts__user=user)
        return recipes
