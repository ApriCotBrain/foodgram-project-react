from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, \
    IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from api.serializers import *
from recipes.models import Ingredient, Recipe, Tag, Favorite
from users.models import CustomUser, Subscription


class TagViewSet(mixins.RetrieveModelMixin,
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin,
                 viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(mixins.RetrieveModelMixin,
                        mixins.ListModelMixin,
                        mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = CreateRecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('tags',)
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        data = ReadRecipeSerializer(
            instance=serializer.instance).data
        return Response(data, status=status.HTTP_201_CREATED)

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return CreateRecipeSerializer
        return ReadRecipeSerializer

    def add_to(self, model, user, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = CutRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from(self, model, user, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        model.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
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
        methods=['POST', 'DELETE'],
        url_path='shopping_cart',
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.add_to(Basket, request.user, pk)
        elif request.method == 'DELETE':
            return self.delete_from(Basket, request.user, pk)

    @action(
        detail=False,
        methods=['GET'],
        url_path='download_shopping_cart',
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        if request.method == 'GET':
            basket = (
                RecipeIngredient.objects.filter(
                    recipe__basket_recipe__user=request.user
                )
                .values('ingredient__name',
                        'ingredient__measurement_unit',)
                .annotate(amount=Sum('amount'))
                .order_by('ingredient__name')
            )

            response = HttpResponse(content_type='text/plain')
            response[
                'Content-Disposition'
            ] = 'attachment; filename=shopping_cart.txt"'

            data = ['Ingredient\tAmount\tMeasurement Unit']
            for item in basket:
                data.append(
                    f"{item['ingredient__name']}"
                    f"\t{item['amount']}"
                    f"\t{item['ingredient__measurement_unit']}"
                )

            response.write('\n'.join(data))
            return response


class CustomUserViewSet(UserViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = PageNumberPagination

    @action(
        methods=['GET', ], url_path='me', detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)

    @action(methods=['POST'], url_path='set_password', detail=False,
            permission_classes=(IsAuthenticated,))
    def set_password(self, request):
        serializer = PasswordSerializer(data=request.data)
        user = request.user
        if serializer.is_valid():
            if not user.check_password(serializer.data.get(
                    'current_password')):
                return Response({'current_password': ['Wrong password.']},
                                status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.data.get('new_password'))
            user.save()
            return Response({'status': 'Пароль успешно изменен.'},
                            status=status.HTTP_200_OK)

        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['GET', ],
            url_path='subscriptions', detail=False,
            permission_classes=(IsAuthenticated,))
    def read_subscribe(self, request):
        if request.method == 'GET':
            user = request.user
            subscriptions = Subscription.objects.filter(user=user)
            paginator = PageNumberPagination()
            paginator.page_size = 10
            subscriptions = paginator.paginate_queryset(subscriptions, request)

            serializer = SubscriptionSerializer(subscriptions, many=True,
                                                context={'request': request})
            return paginator.get_paginated_response(serializer.data)

    @action(methods=['POST', 'DELETE'],
            url_path='subscribe', detail=True,
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id=None):
        user = request.user
        subscribe = get_object_or_404(CustomUser, id=id)
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
