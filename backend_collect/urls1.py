"""
URL routing for EC Carbon Survey API.
Includes: Auth, Plots, Trees, Soil, Water, Socio-Economic, Stats.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from collect.views import (
    PlotViewSet, TreeViewSet, SoilSampleViewSet,
    WaterAssessmentViewSet, SocioEconomicViewSet,
    StatsViewSet, login_view, register_view, me_view,
)

router = DefaultRouter()
router.register(r'plots', PlotViewSet, basename='plot')
router.register(r'trees', TreeViewSet, basename='tree')
router.register(r'soil', SoilSampleViewSet, basename='soil')
router.register(r'water', WaterAssessmentViewSet, basename='water')
router.register(r'socioeconomic', SocioEconomicViewSet, basename='socioeconomic')
router.register(r'stats', StatsViewSet, basename='stats')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    # Auth endpoints
    path('api/auth/login/', login_view, name='login'),
    path('api/auth/register/', register_view, name='register'),
    path('api/auth/me/', me_view, name='me'),
    # Survey submission
    path('api/plots/submit_survey/', PlotViewSet.as_view({'post': 'submit_survey'}), name='submit_survey'),
    # DRF browsable API
    path('api-auth/', include('rest_framework.urls')),
]
