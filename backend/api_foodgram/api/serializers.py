from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import *
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    #is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            #'is_subscribed'
        )
        model = User

    # def get_is_subscribed(self, obj):
    #     user = self.context.get('request').user
    #     if user.is_anonymous:
    #         return False
    #     return Subscription.subscribe.filter(user=user, subscribe=obj).exists()


class PasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class GetTokenSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('password', 'email')


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
    #author = UserSerializer(read_only=True)
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
        #user = self.context['request'].user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            RecipeIngredient.objects.get_or_create(
                recipe_id=recipe.id,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount'],
            )
        recipe.tag.set(tags)
        return recipe

    # def update(self, instance, validated_data):
    #     tags = validated_data.pop('tags')
    #     ingredients = validated_data.pop('ingredients')
    #     instance = super().update(instance, validated_data)
    #     instance.tags.clear()
    #     instance.tags.set(tags)
    #     instance.ingredients.clear()
    #     instance.ingredients.set(ingredients)
    #     instance.save()
    #     return instance


class ReadRecipeSerializer(serializers.ModelSerializer):

    ingredients = ReadRecipeIngredientSerializer(
        source='recipe_ingredient',
        many=True,
        read_only=True,
    )
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    #is_favorited = serializers.SerializerMethodField(read_only=True)

    # def get_is_favorited(self, obj):
    #     user = self.context.get('request').user
    #     if user.is_anonymous:
    #         return False
    #     return user.fan.filter(recipe=obj).exists()

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
            #'is_favorited',
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
        )


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault())
    recipe = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Recipe.objects.all()
    )

    class Meta:
        fields = ('user', 'recipe')
        read_only_fields = ('user', )

        model = Favorite


class SubscriptionSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault())
    subscribe = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )

    class Meta:
        fields = ('user', 'subscribe')
        read_only_fields = ('user', )

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

