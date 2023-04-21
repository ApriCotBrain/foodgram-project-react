import io

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.filters import RecipeFilter, IngredientFilter
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (CreateRecipeSerializer, CustomUserSerializer,
                             IngredientSerializer, ReadRecipeSerializer,
                             ShortRecipeSerializer,
                             SubscriptionSerializer,
                             TagSerializer)
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Subscription

User = get_user_model()


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = CreateRecipeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH'):
            return CreateRecipeSerializer
        return ReadRecipeSerializer

    def add_to(self, model, user, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        obj, created = model.objects.get_or_create(user=user, recipe=recipe)
        if created:
            serializer = ShortRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_304_NOT_MODIFIED)

    def delete_from(self, model, user, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        obj = get_object_or_404(model, user=user, recipe=recipe)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        url_path='favorite',
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.add_to(Favorite, request.user, pk)
        elif request.method == 'DELETE':
            return self.delete_from(Favorite, request.user, pk)

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        url_path='shopping_cart',
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.add_to(ShoppingCart, request.user, pk)
        elif request.method == 'DELETE':
            return self.delete_from(ShoppingCart, request.user, pk)

    @action(
        detail=False,
        methods=('GET',),
        url_path='download_shopping_cart',
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        shopping_cart = (
            RecipeIngredient.objects.filter(
                recipe__shopping_cart_recipe__user=request.user
            )
            .values('ingredient__name',
                    'ingredient__measurement_unit', )
            .annotate(amount=Sum('amount'))
            .order_by('ingredient__name')
        )

        buffer = io.StringIO()

        for item in shopping_cart:
            buffer.write(f"{item['ingredient__name']}\t")
            buffer.write(f"{item['amount']}\t")
            buffer.write(f"{item['ingredient__measurement_unit']} \n")

        response = FileResponse(buffer.getvalue(), content_type='text/plain')
        response[
            'Content-Disposition'] = 'attachment; filename="shopping_cart.txt"'
        return response


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticatedOrReadOnly,)

    @action(methods=('GET', ),
            url_path='subscriptions', detail=False,
            permission_classes=(IsAuthenticated,))
    def read_subscribe(self, request):
        user = request.user
        subscriptions = Subscription.objects.filter(user=user)
        page = self.paginate_queryset(subscriptions)
        serializer = SubscriptionSerializer(page, many=True,
                                            context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(methods=('POST', 'DELETE'),
            url_path='subscribe', detail=True,
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id=None):
        user = request.user
        subscribe = get_object_or_404(User, id=id)
        if request.method == 'POST':
            subscription = Subscription.objects.create(
                user=user, subscribe=subscribe)
            serializer = SubscriptionSerializer(
                subscription,
                context={'request': request},
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            subscribe = self.get_object()
            deleted = Subscription.objects.get(
                user=user, subscribe=subscribe).delete()
            if deleted:
                return Response({
                    'message': 'Вы отписались от этого автора'},
                    status=status.HTTP_204_NO_CONTENT)
