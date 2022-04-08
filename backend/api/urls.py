from django.urls import path, include

from rest_framework.routers import DefaultRouter

from api.views import IngredientViewSet, TagViewSet


router = DefaultRouter()

router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken'))
]
