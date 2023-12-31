from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser import views as djoser_views
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response

from api.paginations import ApiPagination
from api.permissions import AdminOrReadOnlyPermission
from recipes.models import Ingredient, IngredientInRecipe, Recipe, Tag
from users.models import User

from .filters import IngredientFilter, RecipeFilter
from .serializers import (
    FavoritedSerializer,
    FollowSerializer,
    FollowUserSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    ShoppingCartSerializer,
    TagSerializer,
)


class CustomUserViewSet(djoser_views.UserViewSet):
    """Работа с пользователями."""

    http_method_names = ['get', 'post', 'delete']

    @action(
        detail=True, methods=['post'], permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id):
        """Создаёт связь между пользователями."""
        user_to_subscribe = get_object_or_404(User, pk=id)
        user = request.user
        serializer = FollowSerializer(
            data={
                'user': user.username,
                'following': user_to_subscribe.username,
            },
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'detail': 'Подписка успешно создана.'},
            status=status.HTTP_201_CREATED,)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id):
        """Удалет связь между пользователями."""
        user_to_unsubscribe = get_object_or_404(User, pk=id)
        user = request.user
        serializer = FollowSerializer(
            data={
                'user': user.username,
                'following': user_to_unsubscribe.username,
            },
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        follow = user_to_unsubscribe.following.filter(user=user)
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,),
        serializer_class=FollowUserSerializer,)
    def subscriptions(self, request):
        """Отображает все подписки пользователя."""
        followed_users = User.objects.filter(following__user=self.request.user)
        page = self.paginate_queryset(followed_users)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(followed_users, many=True)
        return Response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):
    """Работа с рецептами: [GET, POST, DELETE, PATCH]."""

    queryset = Recipe.objects.all()
    pagination_class = ApiPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Выбор сериализатора при безопасных и не безопасных методах."""
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(
        detail=True,
        methods=['post'],
        permission_classes=(IsAuthenticated,),)
    def favorite(self, request, pk):
        """
        Получить/добавить рецепт
        из/в избранного/е у текущего пользоватля.
        """
        serializer = FavoritedSerializer(
            data={
                'author': request.user.pk,
                'recipe': pk,
            },
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'detail': 'Рецепт успешно добавлен в избранное.'},
            status=status.HTTP_201_CREATED,)

    @favorite.mapping.delete
    def unfavorite(self, request, pk):
        """
        Удалить рецепт из избранного у текущего пользоватля.
        """
        serializer = FavoritedSerializer(
            data={
                'author': request.user.pk,
                'recipe': pk,
            },
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        recipe = get_object_or_404(Recipe, pk=pk)
        favorites = recipe.favorites.filter(author=request.user)
        favorites.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated],)
    def shopping_cart(self, request, pk):
        """
        Получить/добавить рецепт из/в избранного/е из списка покупок у
        текущего пользователя.
        """
        serializer = ShoppingCartSerializer(
            data={
                'author': request.user.pk,
                'recipe': pk,
            },
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'detail': 'Рецепт успешно добавлен в список покупок.'},
            status=status.HTTP_201_CREATED,)

    @shopping_cart.mapping.delete
    def unshopping_cart(self, request, pk):
        """
        Удалить рецепт из списка покупок у текущего пользоватля.
        """
        serializer = ShoppingCartSerializer(
            data={
                'author': request.user.pk,
                'recipe': pk,
            },
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        recipe = get_object_or_404(Recipe, pk=pk)
        shopping_cart = recipe.shopping_cart.filter(author=request.user)
        shopping_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',
        permission_classes=(IsAuthenticated,),)
    def download_shopping_cart(self, request):
        """
        Скачать список покупок для выбранных рецептов,
        данные которых суммируются.
        """
        user = request.user
        ingredients = (
            IngredientInRecipe.objects.filter(
                recipe__shopping_cart__author=request.user
            )
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(amount=Sum('amount')))
        shopping_list = [
            f'{ingredient["ingredient__name"]}:'
            f'{ingredient["ingredient__measurement_unit"]}'
            f' {ingredient["amount"]}'
            for ingredient in ingredients
        ]
        if not shopping_list:
            shopping_list = ['Корзина пуста.']
        filename = f'{user.username}_shopping_cart.txt'
        response = HttpResponse(
            '\n'.join(shopping_list), content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response


class TagViewSet(viewsets.ModelViewSet):
    """Работа с тегами."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnlyPermission,)
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    """Работа с ингредиентами."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnlyPermission,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
