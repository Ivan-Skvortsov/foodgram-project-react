from django.urls import path, include

from rest_framework.routers import DefaultRouter

from api.views import IngredientViewSet, TagViewSet, RecipeViewSet, UserViewSet


router = DefaultRouter()

router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet, basename='recipe')
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken'))
]
