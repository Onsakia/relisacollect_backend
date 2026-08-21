"""
Django REST Framework serializers with GeoJSON support.
Includes all 5 modules: Biomass, Biodiversity, Soil, Water/Hydrology, Socio-Economic.
"""
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import (
    Plot, TreeMeasurement, Transect, SpeciesObservation, GrassBiomassSample,
    SoilSample, WaterAssessment, SocioEconomic,
)


class TreeSerializer(serializers.ModelSerializer):
    species_display = serializers.CharField(source='get_species_display', read_only=True)
    tree_status_display = serializers.CharField(source='get_tree_status_display', read_only=True)
    estimated_carbon = serializers.FloatField(read_only=True)

    class Meta:
        model = TreeMeasurement
        fields = [
            'id', 'tree_id', 'tree_num', 'gps_waypoint_number',
            'species', 'species_display',
            'tree_status', 'tree_status_display',
            'dbh', 'height',
            'crown_width_n', 'crown_width_e', 'estimated_carbon',
        ]


class TreeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreeMeasurement
        fields = [
            'tree_id', 'tree_num', 'gps_waypoint_number',
            'species', 'tree_status', 'dbh', 'height',
            'crown_width_n', 'crown_width_e',
        ]


class SpeciesObservationSerializer(serializers.ModelSerializer):
    species_display = serializers.CharField(source='get_species_display', read_only=True)
    bio_type_display = serializers.CharField(source='get_bio_type_display', read_only=True)
    threat_status_display = serializers.CharField(source='get_threat_status_display', read_only=True)

    class Meta:
        model = SpeciesObservation
        fields = [
            'id', 'observation_num', 'gps_waypoint_number',
            'bio_type', 'bio_type_display', 'species', 'species_display',
            'abundance', 'threat_status', 'threat_status_display', 'dbh_bio',
            'aspect', 'landform', 'degradation_level', 'erosion', 'water_distance',
            'micro_habitat_notes',
        ]


class SpeciesObservationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpeciesObservation
        fields = [
            'observation_num', 'gps_waypoint_number', 'bio_type', 'species',
            'abundance', 'threat_status', 'dbh_bio', 'aspect', 'landform',
            'degradation_level', 'erosion', 'water_distance', 'micro_habitat_notes',
        ]


class GrassSampleSerializer(serializers.ModelSerializer):
    grass_species_display = serializers.CharField(source='get_grass_species_display', read_only=True)
    last_burned_display = serializers.CharField(source='get_last_burned_display', read_only=True)

    class Meta:
        model = GrassBiomassSample
        fields = [
            'id', 'sample_num', 'gps_waypoint_number',
            'grass_species', 'grass_species_display',
            'grass_weight', 'last_burned', 'last_burned_display', 'grass_notes',
        ]


class GrassSampleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrassBiomassSample
        fields = [
            'sample_num', 'gps_waypoint_number', 'grass_species',
            'grass_weight', 'last_burned', 'grass_notes',
        ]


class TransectSerializer(serializers.ModelSerializer):
    transect_id_display = serializers.CharField(source='get_transect_id_display', read_only=True)
    species_obs = SpeciesObservationSerializer(many=True, read_only=True)
    grass_samples = GrassSampleSerializer(many=True, read_only=True)

    class Meta:
        model = Transect
        fields = [
            'id', 'transect_id', 'transect_id_display', 'transect_num',
            'start_point', 'end_point', 'species_obs', 'grass_samples',
        ]


class TransectCreateSerializer(serializers.ModelSerializer):
    species_obs = SpeciesObservationCreateSerializer(many=True, required=False)
    grass_samples = GrassSampleCreateSerializer(many=True, required=False)

    class Meta:
        model = Transect
        fields = ['transect_id', 'transect_num', 'start_point', 'end_point', 'species_obs', 'grass_samples']

    def create(self, validated_data):
        species_data = validated_data.pop('species_obs', [])
        grass_data = validated_data.pop('grass_samples', [])
        transect = Transect.objects.create(**validated_data)
        for s in species_data:
            SpeciesObservation.objects.create(transect=transect, **s)
        for g in grass_data:
            GrassBiomassSample.objects.create(transect=transect, **g)
        return transect


class SoilSampleSerializer(serializers.ModelSerializer):
    depth_class_display = serializers.CharField(source='get_depth_class_display', read_only=True)
    soil_texture_display = serializers.CharField(source='get_soil_texture_display', read_only=True)

    class Meta:
        model = SoilSample
        fields = [
            'id', 'point_id', 'point_num', 'gps_waypoint_number', 'soil_gps',
            'depth_class', 'depth_class_display', 'depth_cm',
            'soil_texture', 'soil_texture_display',
            'bulk_density', 'soil_ph', 'lab_id',
        ]


class SoilSampleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoilSample
        fields = [
            'point_id', 'point_num', 'gps_waypoint_number', 'soil_gps',
            'depth_class', 'depth_cm', 'soil_texture', 'bulk_density', 'soil_ph', 'lab_id',
        ]


# ═══════════════════════════════════════════════════════════════
#  WATER / HYDROLOGY
# ═══════════════════════════════════════════════════════════════

class WaterAssessmentSerializer(serializers.ModelSerializer):
    water_source_type_display = serializers.CharField(source='get_water_source_type_display', read_only=True)
    flow_regime_display = serializers.CharField(source='get_flow_regime_display', read_only=True)
    seasonal_availability_display = serializers.CharField(source='get_seasonal_availability_display', read_only=True)
    water_quality_category_display = serializers.CharField(source='get_water_quality_category_display', read_only=True)
    riparian_veg_condition_display = serializers.CharField(source='get_riparian_veg_condition_display', read_only=True)
    stream_bank_erosion_display = serializers.CharField(source='get_stream_bank_erosion_display', read_only=True)
    wetland_type_display = serializers.CharField(source='get_wetland_type_display', read_only=True)
    wetland_condition_display = serializers.CharField(source='get_wetland_condition_display', read_only=True)
    downstream_impacts_display = serializers.CharField(source='get_downstream_impacts_display', read_only=True)
    water_extraction_uses_list = serializers.SerializerMethodField()

    class Meta:
        model = WaterAssessment
        fields = [
            'id', 'water_source_type', 'water_source_type_display',
            'water_source_name', 'water_source_gps',
            'flow_regime', 'flow_regime_display',
            'seasonal_availability', 'seasonal_availability_display',
            'water_ph', 'water_temperature', 'water_turbidity_ntu',
            'electrical_conductivity', 'water_quality_category',
            'water_quality_category_display',
            'riparian_veg_condition', 'riparian_veg_condition_display',
            'stream_bank_erosion', 'stream_bank_erosion_display',
            'wetland_type', 'wetland_type_display',
            'wetland_condition', 'wetland_condition_display',
            'wetland_width_m',
            'water_extraction_uses', 'water_extraction_uses_list',
            'downstream_impacts', 'downstream_impacts_display',
            'water_notes',
        ]

    def get_water_extraction_uses_list(self, obj):
        if obj.water_extraction_uses:
            return [u.strip() for u in obj.water_extraction_uses.split(',')]
        return []


class WaterAssessmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaterAssessment
        fields = [
            'water_source_type', 'water_source_name', 'water_source_gps',
            'flow_regime', 'seasonal_availability', 'water_ph', 'water_temperature',
            'water_turbidity_ntu', 'electrical_conductivity', 'water_quality_category',
            'riparian_veg_condition', 'stream_bank_erosion', 'wetland_type',
            'wetland_condition', 'wetland_width_m', 'water_extraction_uses',
            'downstream_impacts', 'water_notes',
        ]


# ═══════════════════════════════════════════════════════════════
#  SOCIO-ECONOMIC
# ═══════════════════════════════════════════════════════════════

class SocioEconomicSerializer(serializers.ModelSerializer):
    community_type_display = serializers.CharField(source='get_community_type_display', read_only=True)
    tenure_security_display = serializers.CharField(source='get_tenure_security_display', read_only=True)
    land_use_current_display = serializers.CharField(source='get_land_use_current_display', read_only=True)
    primary_income_source_display = serializers.CharField(source='get_primary_income_source_display', read_only=True)
    household_income_level_display = serializers.CharField(source='get_household_income_level_display', read_only=True)
    awareness_display = serializers.CharField(source='get_community_restoration_awareness_display', read_only=True)
    support_display = serializers.CharField(source='get_restoration_support_display', read_only=True)
    willingness_display = serializers.CharField(source='get_willingness_to_participate_display', read_only=True)
    job_potential_display = serializers.CharField(source='get_job_creation_potential_display', read_only=True)
    gender_display = serializers.CharField(source='get_gender_balance_participation_display', read_only=True)
    fire_risk_display = serializers.CharField(source='get_fire_risk_level_display', read_only=True)

    land_use_history_list = serializers.SerializerMethodField()
    livelihood_activities_list = serializers.SerializerMethodField()
    expected_benefits_list = serializers.SerializerMethodField()
    indigenous_practices_list = serializers.SerializerMethodField()
    capacity_needs_list = serializers.SerializerMethodField()
    restoration_challenges_list = serializers.SerializerMethodField()
    invasive_species_list = serializers.SerializerMethodField()

    class Meta:
        model = SocioEconomic
        fields = [
            'id', 'community_type', 'community_type_display',
            'households_nearby', 'population_estimate',
            'tenure_security', 'tenure_security_display',
            'land_use_current', 'land_use_current_display',
            'land_use_history', 'land_use_history_list',
            'livelihood_activities', 'livelihood_activities_list',
            'primary_income_source', 'primary_income_source_display',
            'household_income_level', 'household_income_level_display',
            'community_restoration_awareness', 'awareness_display',
            'restoration_support', 'support_display',
            'expected_restoration_benefits', 'expected_benefits_list',
            'willingness_to_participate', 'willingness_display',
            'traditional_leadership_involved',
            'indigenous_practices_present',
            'indigenous_practices_types', 'indigenous_practices_list',
            'traditional_knowledge_notes',
            'capacity_building_needs', 'capacity_needs_list',
            'job_creation_potential', 'job_potential_display',
            'gender_balance_participation', 'gender_display',
            'restoration_challenges', 'restoration_challenges_list',
            'fire_risk_level', 'fire_risk_display',
            'invasive_species_threats', 'invasive_species_list',
            'socioeconomic_notes',
        ]

    def _split_field(self, obj, field_name):
        val = getattr(obj, field_name, '')
        if val:
            return [v.strip() for v in val.split(',')]
        return []

    def get_land_use_history_list(self, obj): return self._split_field(obj, 'land_use_history')
    def get_livelihood_activities_list(self, obj): return self._split_field(obj, 'livelihood_activities')
    def get_expected_benefits_list(self, obj): return self._split_field(obj, 'expected_restoration_benefits')
    def get_indigenous_practices_list(self, obj): return self._split_field(obj, 'indigenous_practices_types')
    def get_capacity_needs_list(self, obj): return self._split_field(obj, 'capacity_building_needs')
    def get_restoration_challenges_list(self, obj): return self._split_field(obj, 'restoration_challenges')
    def get_invasive_species_list(self, obj): return self._split_field(obj, 'invasive_species_threats')


class SocioEconomicCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocioEconomic
        fields = [
            'community_type', 'households_nearby', 'population_estimate',
            'tenure_security', 'land_use_current', 'land_use_history',
            'livelihood_activities', 'primary_income_source', 'household_income_level',
            'community_restoration_awareness', 'restoration_support',
            'expected_restoration_benefits', 'willingness_to_participate',
            'traditional_leadership_involved', 'indigenous_practices_present',
            'indigenous_practices_types', 'traditional_knowledge_notes',
            'capacity_building_needs', 'job_creation_potential',
            'gender_balance_participation', 'restoration_challenges',
            'fire_risk_level', 'invasive_species_threats', 'socioeconomic_notes',
        ]


# ═══════════════════════════════════════════════════════════════
#  PLOT SERIALIZERS
# ═══════════════════════════════════════════════════════════════

class PlotListSerializer(serializers.ModelSerializer):
    forest_type_display = serializers.CharField(source='get_forest_type_display', read_only=True)
    province_display = serializers.CharField(source='get_province_display', read_only=True)
    total_trees = serializers.IntegerField(read_only=True)
    total_waypoints = serializers.IntegerField(read_only=True)
    samples_collected = serializers.IntegerField(read_only=True)
    soil_coverage = serializers.FloatField(read_only=True)
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()

    class Meta:
        model = Plot
        fields = [
            'id', 'plot_id', 'site_name', 'province', 'province_display',
            'date', 'enumerator', 'latitude', 'longitude',
            'altitude', 'gps_accuracy', 'gps_point_number', 'plot_radius',
            'dist_water_point', 'dist_settlement',
            'forest_type', 'forest_type_display',
            'trees_count_est', 'habitat_condition', 'canopy_cover',
            'carbon_standard', 'land_tenure', 'community_consult',
            'total_trees', 'total_waypoints', 'samples_collected', 'soil_coverage',
            'module_biomass', 'module_biodiversity', 'module_soil',
            'module_water', 'module_socioeconomic',
            'created_at', 'updated_at',
        ]

    def get_latitude(self, obj):
        return obj.location.y if obj.location else None

    def get_longitude(self, obj):
        return obj.location.x if obj.location else None


class PlotDetailSerializer(serializers.ModelSerializer):
    forest_type_display = serializers.CharField(source='get_forest_type_display', read_only=True)
    province_display = serializers.CharField(source='get_province_display', read_only=True)
    habitat_condition_display = serializers.CharField(source='get_habitat_condition_display', read_only=True)
    carbon_standard_display = serializers.CharField(source='get_carbon_standard_display', read_only=True)
    land_tenure_display = serializers.CharField(source='get_land_tenure_display', read_only=True)
    dist_water_display = serializers.CharField(source='get_dist_water_point_display', read_only=True)
    dist_settlement_display = serializers.CharField(source='get_dist_settlement_display', read_only=True)

    trees = TreeSerializer(many=True, read_only=True)
    transects = TransectSerializer(many=True, read_only=True)
    soil_samples = SoilSampleSerializer(many=True, read_only=True)
    water_assessment = WaterAssessmentSerializer(read_only=True)
    socioeconomic = SocioEconomicSerializer(read_only=True)

    total_trees = serializers.IntegerField(read_only=True)
    total_waypoints = serializers.IntegerField(read_only=True)
    samples_collected = serializers.IntegerField(read_only=True)
    soil_coverage = serializers.FloatField(read_only=True)
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()

    class Meta:
        model = Plot
        fields = [
            'id', 'plot_id', 'site_name', 'province', 'province_display',
            'date', 'enumerator', 'latitude', 'longitude',
            'altitude', 'gps_accuracy', 'gps_point_number', 'plot_radius',
            'dist_water_point', 'dist_water_display',
            'dist_settlement', 'dist_settlement_display',
            'water_point_notes', 'settlement_notes',
            'forest_type', 'forest_type_display',
            'trees_count_est', 'habitat_condition', 'habitat_condition_display',
            'canopy_cover',
            'carbon_standard', 'carbon_standard_display',
            'land_tenure', 'land_tenure_display',
            'community_consult', 'community_name',
            'ccb_compliance', 'ccb_level', 'gs_sdgs',
            'pv_community', 'pv_scheme',
            'total_trees', 'total_waypoints', 'trees',
            'transects',
            'samples_collected', 'soil_samples', 'soil_coverage',
            'water_assessment', 'socioeconomic',
            'module_biomass', 'module_biodiversity', 'module_soil',
            'module_water', 'module_socioeconomic',
            'created_at', 'updated_at',
        ]

    def get_latitude(self, obj):
        return obj.location.y if obj.location else None

    def get_longitude(self, obj):
        return obj.location.x if obj.location else None


class PlotGeoJSONSerializer(GeoFeatureModelSerializer):
    forest_type_display = serializers.CharField(source='get_forest_type_display', read_only=True)

    class Meta:
        model = Plot
        geo_field = 'location'
        fields = [
            'plot_id', 'site_name', 'forest_type',
            'forest_type_display', 'canopy_cover', 'gps_point_number',
        ]


class PlotCreateSerializer(serializers.ModelSerializer):
    trees = TreeCreateSerializer(many=True, required=False)
    transects = TransectCreateSerializer(many=True, required=False)
    soil_samples = SoilSampleCreateSerializer(many=True, required=False)
    water_assessment = WaterAssessmentCreateSerializer(required=False)
    socioeconomic = SocioEconomicCreateSerializer(required=False)

    class Meta:
        model = Plot
        fields = [
            'plot_id', 'site_name', 'province', 'date', 'enumerator',
            'location', 'altitude', 'gps_accuracy', 'gps_point_number', 'plot_radius',
            'dist_water_point', 'dist_settlement',
            'water_point_notes', 'settlement_notes',
            'forest_type', 'trees_count_est', 'habitat_condition', 'canopy_cover',
            'carbon_standard', 'land_tenure', 'community_consult',
            'community_name', 'ccb_compliance', 'ccb_level',
            'gs_sdgs', 'pv_community', 'pv_scheme',
            'module_biomass', 'module_biodiversity', 'module_soil',
            'module_water', 'module_socioeconomic',
            'trees', 'transects', 'soil_samples',
            'water_assessment', 'socioeconomic',
        ]

    def create(self, validated_data):
        trees_data = validated_data.pop('trees', [])
        transects_data = validated_data.pop('transects', [])
        soil_data = validated_data.pop('soil_samples', [])
        water_data = validated_data.pop('water_assessment', None)
        socio_data = validated_data.pop('socioeconomic', None)

        plot = Plot.objects.create(**validated_data)

        for t in trees_data:
            TreeMeasurement.objects.create(plot=plot, **t)

        for tr_data in transects_data:
            species_obs_data = tr_data.pop('species_obs', [])
            grass_samples_data = tr_data.pop('grass_samples', [])
            transect = Transect.objects.create(plot=plot, **tr_data)
            for s in species_obs_data:
                SpeciesObservation.objects.create(transect=transect, **s)
            for g in grass_samples_data:
                GrassBiomassSample.objects.create(transect=transect, **g)

        for s in soil_data:
            SoilSample.objects.create(plot=plot, **s)

        if water_data:
            WaterAssessment.objects.create(plot=plot, **water_data)

        if socio_data:
            SocioEconomic.objects.create(plot=plot, **socio_data)

        return plot


# ═══════════════════════════════════════════════════════════════
#  SURVEY RECORD (from mobile submissions)
# ═══════════════════════════════════════════════════════════════

class SurveyRecordSerializer(serializers.Serializer):
    """Serializer for mobile survey record submission."""
    instance_id = serializers.CharField(max_length=100)
    form_id = serializers.CharField(max_length=50)
    status = serializers.ChoiceField(choices=['draft', 'submitted', 'synced', 'error'])
    data = serializers.DictField()
    device_id = serializers.CharField(max_length=100, allow_blank=True)
    enumerator = serializers.CharField(max_length=100, allow_blank=True)
    created_at = serializers.IntegerField()
    submitted_at = serializers.IntegerField(required=False, allow_null=True)


class SurveyRecordResponseSerializer(serializers.Serializer):
    instance_id = serializers.CharField()
    status = serializers.CharField()
    message = serializers.CharField()
    plot_id = serializers.CharField(required=False, allow_null=True)
