from django.contrib import admin

from .models import (
    Ingredient,
    Tag,
    Recipe,
    IngredientInRecipe,
    Favorited,
    ShoppingCart,)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    search_fields = ('name',)
    list_filter = ('name',)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'name', 'in_favorite')
    readonly_fields = ('in_favorite',)
    search_fields = ('name',)
    list_filter = ('author', 'name', 'tags')
    empty_value_display = '-пусто-'

    def in_favorite(self, obj):
        return obj.favorites.count()

    in_favorite.short_description = 'Добавленные рецепты в избранное'


class IngredientInRecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'ingredient', 'amount')
    search_fields = ('recipe',)
    list_filter = ('recipe', 'ingredient')
    empty_value_display = '-пусто-'


class FavoritedAdmin(admin.ModelAdmin):
    list_display = ('author', 'recipe')
    search_fields = ('author',)
    list_filter = ('author',)


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('author', 'recipe')
    search_fields = ('author',)
    list_filter = ('author',)


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientInRecipe, IngredientInRecipeAdmin)
admin.site.register(Favorited, FavoritedAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
