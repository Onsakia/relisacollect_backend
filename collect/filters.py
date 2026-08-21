"""
Django-filter classes for spatial and attribute filtering.
"""
import django_filters
from django.contrib.gis.geos import Polygon
from .models import Plot


class PlotFilter(django_filters.FilterSet):
    """Filter plots by attributes and spatial bounding box."""

    bbox = django_filters.CharFilter(method='filter_bbox')
    forest_type = django_filters.ChoiceFilter(choices=Plot._meta.get_field('forest_type').choices)
    canopy_cover__gte = django_filters.NumberFilter(field_name='canopy_cover', lookup_expr='gte')
    canopy_cover__lte = django_filters.NumberFilter(field_name='canopy_cover', lookup_expr='lte')
    date__gte = django_filters.DateFilter(field_name='date', lookup_expr='gte')
    date__lte = django_filters.DateFilter(field_name='date', lookup_expr='lte')

    class Meta:
        model = Plot
        fields = [
            'forest_type', 'province', 'habitat_condition',
            'carbon_standard', 'land_tenure',
        ]

    def filter_bbox(self, queryset, name, value):
        """Filter by bounding box: min_lon,min_lat,max_lon,max_lat"""
        try:
            min_lon, min_lat, max_lon, max_lat = map(float, value.split(','))
            bbox = Polygon.from_bbox((min_lon, min_lat, max_lon, max_lat))
            return queryset.filter(location__within=bbox)
        except (ValueError, TypeError):
            return queryset
