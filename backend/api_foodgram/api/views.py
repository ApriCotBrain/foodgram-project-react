from django.http import Http404
from rest_framework import filters
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from djoser.views import UserViewSet

from api.serializers import *
from recipes.models import Ingredient, Recipe, Tag, Favorite, Subscription
from users.models import User


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
    #filter_backends = (filters.OrderingFilter,)
    #ordering_fields = ('pub_date',)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        data = ReadRecipeSerializer(
            instance=serializer.instance).data
        return Response(data, status=status.HTTP_201_CREATED)
    # def perform_create(self, serializer):
    #     serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return CreateRecipeSerializer
        return ReadRecipeSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='favorite',
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            recipe = self.get_object()
            created = Favorite.objects.get_or_create(
                user=request.user,
                recipe_id=recipe.id,
            )
            if created:
                return Response({
                    'message': 'Рецепт добавлен в избранное'},
                    status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            recipe = self.get_object()
            deleted = Favorite.objects.get(
                user=request.user,
                recipe_id=recipe.id).delete()
            if deleted:
                return Response({
                    'message': 'Рецепт удален из избранного'},
                    status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

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

    # @action(methods=['GET', ],
    #         url_path='subscriptions', detail=False,
    #         permission_classes=(IsAuthenticated,))
    # def read_subscribe(self, request):
    #     if request.method == 'GET':
    #         serializer = self.get_serializer(data=request.data)
    #         data = SubscriptionSerializer(
    #             instance=serializer.instance).data
    #         return Response(data)

    # @action(methods=['POST', 'DELETE'],
    #         url_path='subscribe', detail=True,
    #         permission_classes=(IsAuthenticated,))
    # def subscribe(self, request, pk):
    #     if request.method == 'POST':
    #         subscribe = self.get_object()
    #         created = Subscription.objects.get_or_create(
    #             user=request.user,
    #             subscribe_id=subscribe.id,
    #         )
    #         if created:
    #             return Response({
    #                 'message': 'Подписка на автора оформлена'},
    #                 status=status.HTTP_201_CREATED)
    #     elif request.method == 'DELETE':
    #         subscribe = self.get_object()
    #         deleted = Subscription.objects.get(
    #             user=request.user,
    #             subscribe_id=subscribe.id).delete()
    #         if deleted:
    #             return Response({
    #                 'message': 'Вы отписались от этого автора'},
    #                 status=status.HTTP_200_OK)
