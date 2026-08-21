"""
URL routing for the survey app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PlotViewSet, StatsViewSet

router = DefaultRouter()
router.register(r'plots', PlotViewSet, basename='plot')
router.register(r'stats', StatsViewSet, basename='stats')

urlpatterns = [
    path('', include(router.urls)),
]
