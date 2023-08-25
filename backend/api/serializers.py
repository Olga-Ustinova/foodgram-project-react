import base64

from django.core.files.base import ContentFile
from django.db import transaction
from djoser import serializers as djoser_serializers
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator, ValidationError

from recipes.models import (Favorited, Ingredient, IngredientInRecipe,
                            Recipe, ShoppingCart, Tag,)
from users.models import Follow, User


class Base64ImageField(serializers.ImageField):
    """
    Сериализатор для обработки изображений, представленных в кодировке
    base64, которые могут быть отправлены клиентом при создании или обновлении
    объекта.
    """

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class CustomUserSerializer(djoser_serializers.UserSerializer):
    """Сериализатор для пользователя с дополнительным полем is_subscribed."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed',)

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and Follow.objects.filter(user=user, following=obj).exists())


class CreateUserSerializer(djoser_serializers.UserCreateSerializer):
    """Сериализатор создания пользователей."""

    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ('id',)

    def validate_username(self, value):
        """Запрет на использование имени 'me'."""
        if value.lower() == 'me':
            raise serializers.ValidationError('Имя "me" не валидно')
        return value


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Follow."""
    user = SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='username',
        default=serializers.CurrentUserDefault(),)
    following = SlugRelatedField(
        queryset=User.objects.all(), slug_field='username')

    class Meta:
        fields = '__all__'
        model = Follow

        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following'),
                message=('Вы уже подписаны на данного пользователя.'),
            )
        ]

    def validate(self, data):
        if data['user'] == data['following']:
            raise serializers.ValidationError(
                'Невозможно подписаться на самого себя')
        return data


class FollowUserSerializer(CustomUserSerializer):
    """Сериализатор для модели Follow."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='recipes.count')

    class Meta:
        fields = CustomUserSerializer.Meta.fields + (
            'recipes',
            'recipes_count',)
        model = CustomUserSerializer.Meta.model

    def get_recipes(self, user):
        recipes = user.recipes.all()
        limit = self.context['request'].query_params.get('recipes_limit', 0)
        try:
            limit_int = int(limit)
        except ValueError:
            raise ValidationError('limit должен быть числом')
        else:
            if limit_int > 0:
                recipes = recipes[:limit_int]
        serializer = RecipeMiniSerializer(recipes, many=True)
        return serializer.data


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода тэгов."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientInRecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для связаной модели Recipe и Ingredient."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = IngredientInRecipe


class IngredientInRecipeWriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для поля ingredients модели Recipe -
    создание ингредиентов.
    """

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        fields = ('id', 'amount')
        model = IngredientInRecipe


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe - чтение данных."""

    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    image = serializers.URLField(source='image.url')
    ingredients = IngredientInRecipeReadSerializer(
        many=True, read_only=True, source='ingredients_amounts')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'author', 'name', 'image', 'text',
                  'ingredients', 'tags', 'cooking_time',
                  'is_favorited', 'is_in_shopping_cart',)
        model = Recipe

    def get_is_favorited(self, obj):
        """Отмечен ли рецепт как избранный текущим пользователем."""
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Favorited.objects.filter(recipe=obj, author=user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        """Находится ли рецепт в корзине текущего пользователя."""
        user = self.context.get('request').user
        if not user.is_anonymous:
            return ShoppingCart.objects.filter(recipe=obj,
                                               author=user).exists()
        return False


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe - запись/обновление/удаление данных."""

    ingredients = IngredientInRecipeWriteSerializer(
        source='ingredients_amounts', many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    image = Base64ImageField()
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        fields = ('ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time', 'author',)
        model = Recipe

    def validate_ingredients(self, ingredients):
        """
        Проверка данных по ингредиентам при создании/редактировании рецепта.
        """
        if not ingredients:
            raise serializers.ValidationError('Выберете ингредиент.')
        for item in ingredients:
            if int(item['amount']) < 1:
                raise serializers.ValidationError(
                    'Минимальное количество ингредиентов - 1.')
        return ingredients

    def validate_tags(self, tags):
        """
        Проверка данных по тегам при создании/редактировании рецепта.
        """
        if not tags:
            raise serializers.ValidationError(
                'У рецепта должен быть выбран минимум один тег.')
        if len(tags) != len(set(tag.id for tag in tags)):
            raise serializers.ValidationError('Теги повторяются')
        return tags

    @staticmethod
    def add_ingredients(ingredients_data, recipe):
        """Добавляет ингридиенты."""
        IngredientInRecipe.objects.bulk_create(
            IngredientInRecipe(
                recipe=recipe,
                ingredient=ingredient.get('id'),
                amount=ingredient.get('amount'),)
            for ingredient in ingredients_data
        )

    @transaction.atomic
    def create(self, validated_data):
        """Создаёт рецепт."""
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients_amounts')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        self.add_ingredients(ingredients_data, recipe)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        """Обновляет рецепт."""
        ingredients_data = validated_data.pop('ingredients_amounts')
        tags_data = validated_data.pop('tags')
        super().update(instance, validated_data)
        instance.tags.set(tags_data)
        instance.ingredients.clear()
        self.add_ingredients(ingredients_data, instance)
        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


class RecipeMiniSerializer(serializers.ModelSerializer):
    """Сериализатор предназначен для вывода рецептов в FollowSerializer."""

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода ингридиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'
