from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import *
from users.models import CustomUser, Subscription

User = get_user_model()


class UserRegSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        model = User


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )
        model = CustomUser

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is not None and hasattr(request, 'user'):
            user = self.context['request'].user
            if user.is_anonymous:
                return False
            if Subscription.objects.filter(
                    user=user, subscribe=obj).exists():
                return True
            return False


class PasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class ReadRecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit', read_only=True)
    amount = serializers.IntegerField()

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = RecipeIngredient


class CreateRecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField()

    class Meta:
        fields = ('id', 'amount')
        model = RecipeIngredient


class CreateRecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    tags = serializers.SlugRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        slug_field='id',
    )
    ingredients = CreateRecipeIngredientSerializer(
        many=True,
        write_only=True,
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'image',
            'name',
            'text',
            'cooking_time',
        )
        read_only_fields = ('author',)

    def create(self, validated_data):
        user = self.context['request'].user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data, author=user)
        for ingredient in ingredients:
            RecipeIngredient.objects.get_or_create(
                recipe_id=recipe.id,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount'],
            )
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredient.clear()

        create_ingredients = [
            RecipeIngredient(
                recipe=instance,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(create_ingredients)
        instance.save()
        return instance


class ReadRecipeSerializer(serializers.ModelSerializer):

    ingredients = ReadRecipeIngredientSerializer(
        source='recipe_ingredient',
        many=True,
        read_only=True,
    )
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    is_favorite = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    def get_is_favorite(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = self.context['request'].user
            if user.is_anonymous:
                return False
            if Favorite.objects.filter(user=user, recipe=obj.id).exists():
                return True

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = self.context['request'].user
            if user.is_anonymous:
                return False
            if Basket.objects.filter(user=user, recipe=obj.id).exists():
                return True
            return False

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
            'is_favorite',
            'is_in_shopping_cart',
        )
        read_only_fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
            'is_favorite',
            'is_in_shopping_cart',
        )


class CutRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe


class SubscriptionSerializer(serializers.ModelSerializer):
    subscribe = CustomUserSerializer()
    recipes = CutRecipeSerializer(
        many=True,
        read_only=True,
        source='subscribe.recipe_author')
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        fields = ('subscribe', 'recipes', 'recipes_count')
        model = Subscription
        validators = (
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'subscribe'),
                message=('Эта подписка уже оформлена ранее!')
            ),
        )

    def validate(self, data):
        if self.context['request'].user == data['subscribe']:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя!')
        return data

    def get_recipes_count(self, obj):
        return obj.subscribe.recipe_author.count()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {
            'email': representation['subscribe']['email'],
            'id': representation['subscribe']['id'],
            'username': representation['subscribe']['username'],
            'first_name': representation['subscribe']['first_name'],
            'last_name': representation['subscribe']['last_name'],
            'is_subscribed': representation['subscribe']['is_subscribed'],
            'recipes': representation['recipes'],
            'recipes_count': representation['recipes_count'],
        }
