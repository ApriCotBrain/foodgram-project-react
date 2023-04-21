from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)


class IngredientResource(resources.ModelResource):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


@admin.register(Ingredient)
class AdminIngredient(ImportExportModelAdmin):
    resource_classes = [IngredientResource]
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name', )


@admin.register(Tag)
class AdminTag(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', )


@admin.register(Recipe)
class AdminRecipe(admin.ModelAdmin):
    list_display = (
        'author', 'name', 'image', 'cooking_time', 'text', 'count_favorites',
    )
    list_filter = ('name', 'author', 'tags',)

    def count_favorites(self, obj):
        return obj.favorites.count()


@admin.register(RecipeIngredient)
class AdminRecipeIngredient(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount',)


@admin.register(Favorite)
class AdminFavorite(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'user')


@admin.register(ShoppingCart)
class AdminShoppingCart(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'user')
