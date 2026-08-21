"""
Django admin configuration for collect models.
"""
from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from .models import Plot, TreeMeasurement, Transect, SpeciesObservation, GrassBiomassSample, SoilSample


class TreeInline(admin.TabularInline):
    model = TreeMeasurement
    extra = 0
    fields = ['tree_id', 'species', 'tree_status', 'dbh', 'height']


class SoilSampleInline(admin.TabularInline):
    model = SoilSample
    extra = 0
    fields = ['point_id', 'depth_class', 'depth_cm', 'soil_texture', 'soil_ph']


class TransectInline(admin.TabularInline):
    model = Transect
    extra = 0
    fields = ['transect_id', 'transect_num']


@admin.register(Plot)
class PlotAdmin(GISModelAdmin):
    list_display = ['plot_id', 'site_name', 'forest_type', 'date', 'enumerator', 'total_trees', 'canopy_cover']
    list_filter = ['forest_type', 'province', 'habitat_condition', 'carbon_standard', 'date']
    search_fields = ['plot_id', 'site_name', 'enumerator']
    inlines = [TreeInline, TransectInline, SoilSampleInline]
    gis_widget_kwargs = {
        'attrs': {
            'default_zoom': 8,
            'default_lon': 26.8,
            'default_lat': -32.5,
        }
    }


@admin.register(TreeMeasurement)
class TreeAdmin(admin.ModelAdmin):
    list_display = ['tree_id', 'plot', 'species', 'dbh', 'height', 'estimated_carbon']
    list_filter = ['species', 'tree_status']
    search_fields = ['tree_id', 'plot__plot_id']


@admin.register(SoilSample)
class SoilSampleAdmin(GISModelAdmin):
    list_display = ['plot', 'point_id', 'depth_class', 'soil_texture', 'soil_ph']
    list_filter = ['depth_class', 'soil_texture']


@admin.register(Transect)
class TransectAdmin(GISModelAdmin):
    list_display = ['plot', 'transect_id', 'transect_num']
    inlines = []  # Could add species obs inline


@admin.register(SpeciesObservation)
class SpeciesObsAdmin(admin.ModelAdmin):
    list_display = ['species', 'transect', 'bio_type', 'abundance', 'threat_status']
    list_filter = ['bio_type', 'threat_status']


@admin.register(GrassBiomassSample)
class GrassSampleAdmin(admin.ModelAdmin):
    list_display = ['transect', 'sample_num', 'grass_species', 'grass_weight']
