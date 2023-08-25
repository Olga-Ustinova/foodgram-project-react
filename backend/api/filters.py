from django_filters import (
    CharFilter,
    FilterSet,
    ModelChoiceFilter,
    ModelMultipleChoiceFilter,
    NumberFilter,)

from recipes.models import Ingredient, Recipe, Tag
from users.models import User


class IngredientFilter(FilterSet):
    name = CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    author = ModelChoiceFilter(queryset=User.objects.all())
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),)
    is_in_shopping_cart = NumberFilter(
        method='filter_by_shopping_cart',)
    is_favorited = NumberFilter(
        method='filter_by_favorited',)

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_in_shopping_cart', 'is_favorited',)

    def filter_by_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(shopping_cart__author=self.request.user)
        return queryset

    def filter_by_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(favorites__author=self.request.user)
        return queryset
