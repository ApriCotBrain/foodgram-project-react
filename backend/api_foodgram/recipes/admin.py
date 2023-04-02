from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from recipes.models import (
    Ingredient, Favorite, Recipe, RecipeIngredient, Tag, RecipeTag,
    Subscription)


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


@admin.register(Tag)
class AdminTag(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', )


@admin.register(Recipe)
class AdminRecipe(admin.ModelAdmin):
    list_display = (
        'author', 'name', 'image', 'cooking_time', 'text', )
    # search_fields = ('name',)
    # list_filter = ('author', 'tags', 'cooking_time', )


@admin.register(RecipeIngredient)
class AdminRecipeIngredient(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount',)


@admin.register(RecipeTag)
class AdminRecipeTag(admin.ModelAdmin):
    list_display = ('recipe', 'tag')


@admin.register(Favorite)
class AdminFavorite(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'user')


@admin.register(Subscription)
class AdminSubscriptions(admin.ModelAdmin):
    list_display = ('id', 'subscribe', 'user')
