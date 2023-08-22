from django_filters import CharFilter, FilterSet

from recipes.models import Ingredient


class IngredientFilter(FilterSet):
    name = CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)
