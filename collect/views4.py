"""
Django REST Framework viewsets and API endpoints.
All 5 modules: Biomass, Biodiversity, Soil, Water/Hydrology, Socio-Economic.
Includes auth, survey submission, stats, GPS waypoint tracking, and uploaded layers.
"""
from django.db.models import Avg, Count, Q, Sum
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point, GEOSGeometry, GeometryCollection
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from django.core.cache import cache
import json as json_mod

from .models import (
    Plot, TreeMeasurement, Transect, SpeciesObservation, GrassBiomassSample,
    SoilSample, WaterAssessment, SocioEconomic, UploadedLayer,
)
from .serializers import (
    PlotListSerializer,
    PlotDetailSerializer,
    PlotCreateSerializer,
    PlotGeoJSONSerializer,
    TreeSerializer,
    TreeCreateSerializer,
    SoilSampleSerializer,
    TransectSerializer,
    WaterAssessmentSerializer,
    WaterAssessmentCreateSerializer,
    SocioEconomicSerializer,
    SocioEconomicCreateSerializer,
    SurveyRecordSerializer,
    SurveyRecordResponseSerializer,
    UploadedLayerSerializer,
)
from .filters import PlotFilter


# ═══════════════════════════════════════════════════════════════
#  AUTHENTICATION
# ═══════════════════════════════════════════════════════════════

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Obtain auth token for mobile app."""
    username = request.data.get('username')
    password = request.data.get('password')
    if not username or not password:
        return Response({'error': 'Username and password required'}, status=400)
    user = authenticate(username=username, password=password)
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': {'id': user.id, 'username': user.username, 'email': user.email},
        })
    return Response({'error': 'Invalid credentials'}, status=401)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """Register a new survey user."""
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email', '')
    if not username or not password:
        return Response({'error': 'Username and password required'}, status=400)
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=400)
    user = User.objects.create_user(username=username, password=password, email=email)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({
        'token': token.key,
        'user': {'id': user.id, 'username': user.username, 'email': user.email},
    }, status=201)


@api_view(['GET'])
def me_view(request):
    """Get current authenticated user."""
    user = request.user
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'is_staff': user.is_staff,
    })


# ═══════════════════════════════════════════════════════════════
#  PLOT VIEWSET
# ═══════════════════════════════════════════════════════════════

class PlotViewSet(viewsets.ModelViewSet):
    queryset = Plot.objects.all().select_related().prefetch_related(
        'trees', 'soil_samples', 'transects__species_obs', 'transects__grass_samples',
        'water_assessment', 'socioeconomic',
    )
    filterset_class = PlotFilter
    ordering_fields = ['date', 'plot_id', 'canopy_cover', 'created_at']
    ordering = ['-date']

    def get_serializer_class(self):
        if self.action == 'create':
            return PlotCreateSerializer
        if self.action == 'geojson':
            return PlotGeoJSONSerializer
        if self.action in ['retrieve', 'update', 'partial_update']:
            return PlotDetailSerializer
        return PlotListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lat = self.request.query_params.get('lat')
        lon = self.request.query_params.get('lon')
        radius = self.request.query_params.get('radius', 10000)
        province = self.request.query_params.get('province')
        if lat and lon:
            point = Point(float(lon), float(lat), srid=4326)
            queryset = queryset.annotate(
                distance=Distance('location', point)
            ).filter(distance__lte=radius).order_by('distance')
        if province:
            queryset = queryset.filter(province=province)
        return queryset

    @action(detail=False, methods=['get'])
    def geojson(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def trees(self, request, pk=None):
        plot = self.get_object()
        trees = plot.trees.all()
        serializer = TreeSerializer(trees, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def soil_samples(self, request, pk=None):
        plot = self.get_object()
        samples = plot.soil_samples.all()
        serializer = SoilSampleSerializer(samples, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def water(self, request, pk=None):
        plot = self.get_object()
        wa = plot.water_assessment
        if wa:
            serializer = WaterAssessmentSerializer(wa)
            return Response(serializer.data)
        return Response({'detail': 'No water assessment for this plot'}, status=404)

    @action(detail=True, methods=['get'])
    def socioeconomic(self, request, pk=None):
        plot = self.get_object()
        se = plot.socioeconomic
        if se:
            serializer = SocioEconomicSerializer(se)
            return Response(serializer.data)
        return Response({'detail': 'No socio-economic data for this plot'}, status=404)

    @action(detail=False, methods=['post'])
    def submit_survey(self, request):
        """Accept survey submission from mobile app and create Plot."""
        serializer = SurveyRecordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        data = serializer.validated_data
        form_data = data.get('data', {})

        try:
            from django.contrib.gis.geos import Point as GisPoint
            import datetime

            # Extract GPS
            gps = form_data.get('plot_gps', {})
            if gps and gps.get('lat') and gps.get('lng'):
                location = GisPoint(float(gps['lng']), float(gps['lat']), srid=4326)
            else:
                location = None

            # Parse date
            date_str = form_data.get('today', timezone.now().strftime('%Y-%m-%d'))
            try:
                survey_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                survey_date = timezone.now().date()

            # Create Plot
            plot = Plot.objects.create(
                plot_id=form_data.get('plot_id', f"SURVEY-{data['instance_id'][:8]}"),
                site_name=form_data.get('site_name', 'Untitled Survey'),
                province=form_data.get('province', 'eastern_cape'),
                date=survey_date,
                enumerator=data.get('enumerator', form_data.get('enumerator', 'Unknown')),
                location=location,
                altitude=form_data.get('altitude_manual') or None,
                gps_accuracy=form_data.get('plot_gps_accuracy') or None,
                gps_point_number=int(form_data.get('gps_point_number', 1)) or 1,
                plot_radius=25,
                dist_water_point=form_data.get('dist_water_point', ''),
                dist_settlement=form_data.get('dist_settlement', ''),
                water_point_notes=form_data.get('water_point_notes', ''),
                settlement_notes=form_data.get('settlement_notes', ''),
                forest_type=form_data.get('forest_type', 'afrotemperate'),
                trees_count_est=form_data.get('trees_count_est') or None,
                canopy_cover=form_data.get('canopy_cover_est') or None,
                module_biomass=form_data.get('module_biomass', 'yes'),
                module_biodiversity=form_data.get('module_biodiversity', 'yes'),
                module_soil=form_data.get('module_soil', 'yes'),
                module_water=form_data.get('module_water', 'no'),
                module_socioeconomic=form_data.get('module_socioeconomic', 'no'),
            )

            # Create Trees (from repeat)
            tree_measurements = form_data.get('tree_measurement', [])
            for idx, t in enumerate(tree_measurements):
                TreeMeasurement.objects.create(
                    plot=plot,
                    tree_id=t.get('tree_id', f"{plot.plot_id}-T{idx+1:02d}"),
                    tree_num=idx + 1,
                    gps_waypoint_number=int(t.get('gps_waypoint_number', idx + 1)),
                    species=t.get('tree_species', 'other'),
                    tree_status=t.get('tree_status', 'live'),
                    dbh=float(t.get('dbh', 0) or 0),
                    height=float(t.get('height', 0) or 0),
                )

            # Create Soil Samples
            soil_data = form_data.get('soil_collection', [])
            for idx, s in enumerate(soil_data):
                SoilSample.objects.create(
                    plot=plot,
                    point_id=s.get('soil_point_id', f"p{idx+1}"),
                    point_num=idx + 1,
                    gps_waypoint_number=int(s.get('gps_waypoint_number', idx + 1)),
                    depth_class=s.get('soil_depth_class', 'topsoil'),
                    depth_cm=float(s.get('soil_depth_cm', 0) or 0),
                    soil_texture=s.get('soil_texture', 'loam'),
                    bulk_density=float(s.get('bulk_density', 0) or 0) or None,
                    soil_ph=float(s.get('ph', 0) or 0) or None,
                )

            # Create Water Assessment
            if form_data.get('module_water') == 'yes':
                water_gps = form_data.get('water_source_gps', {})
                w_gps = None
                if water_gps and water_gps.get('lat') and water_gps.get('lng'):
                    w_gps = GisPoint(float(water_gps['lng']), float(water_gps['lat']), srid=4326)

                extraction_uses = form_data.get('water_extraction_uses', [])
                if isinstance(extraction_uses, list):
                    extraction_uses = ','.join(extraction_uses)

                WaterAssessment.objects.create(
                    plot=plot,
                    water_source_type=form_data.get('water_source_type', ''),
                    water_source_name=form_data.get('water_source_name', ''),
                    water_source_gps=w_gps,
                    flow_regime=form_data.get('flow_regime', ''),
                    seasonal_availability=form_data.get('seasonal_water_availability', ''),
                    water_ph=float(form_data.get('water_ph', 0) or 0) or None,
                    water_temperature=float(form_data.get('water_temperature', 0) or 0) or None,
                    water_turbidity_ntu=float(form_data.get('turbidity_ntu', 0) or 0) or None,
                    electrical_conductivity=float(form_data.get('electrical_conductivity', 0) or 0) or None,
                    water_quality_category=form_data.get('water_quality_category', ''),
                    riparian_veg_condition=form_data.get('riparian_veg_condition', ''),
                    stream_bank_erosion=form_data.get('stream_bank_erosion', ''),
                    wetland_type=form_data.get('wetland_type', ''),
                    wetland_condition=form_data.get('wetland_condition', ''),
                    wetland_width_m=int(form_data.get('wetland_width_m', 0) or 0) or None,
                    water_extraction_uses=extraction_uses,
                    downstream_impacts=form_data.get('downstream_hydrological_impacts', ''),
                    water_notes=form_data.get('water_notes', ''),
                )

            # Create Socio-Economic
            if form_data.get('module_socioeconomic') == 'yes':
                def join_list(val):
                    if isinstance(val, list):
                        return ','.join(val)
                    return val or ''

                SocioEconomic.objects.create(
                    plot=plot,
                    community_type=form_data.get('community_type', ''),
                    households_nearby=int(form_data.get('households_nearby', 0) or 0) or None,
                    population_estimate=int(form_data.get('population_estimate', 0) or 0) or None,
                    tenure_security=form_data.get('tenure_security', ''),
                    land_use_current=form_data.get('current_land_use', ''),
                    land_use_history=join_list(form_data.get('historical_land_uses', [])),
                    livelihood_activities=join_list(form_data.get('livelihood_activities', [])),
                    primary_income_source=form_data.get('primary_income_source', ''),
                    household_income_level=form_data.get('household_income_level', ''),
                    community_restoration_awareness=form_data.get('community_awareness_restoration', ''),
                    restoration_support=form_data.get('community_support_restoration', ''),
                    expected_restoration_benefits=join_list(form_data.get('expected_benefits', [])),
                    willingness_to_participate=form_data.get('willingness_participate', ''),
                    traditional_leadership_involved=form_data.get('traditional_leadership', ''),
                    indigenous_practices_present=form_data.get('indigenous_practices', ''),
                    indigenous_practices_types=join_list(form_data.get('indigenous_practices_types', [])),
                    traditional_knowledge_notes=form_data.get('traditional_knowledge_notes', ''),
                    capacity_building_needs=join_list(form_data.get('capacity_building_needs', [])),
                    job_creation_potential=form_data.get('job_creation_potential', ''),
                    gender_balance_participation=form_data.get('gender_balance', ''),
                    restoration_challenges=join_list(form_data.get('restoration_challenges', [])),
                    fire_risk_level=form_data.get('fire_risk_level', ''),
                    invasive_species_threats=join_list(form_data.get('invasive_species_threats', [])),
                    socioeconomic_notes=form_data.get('socioeconomic_notes', ''),
                )

            return Response({
                'instance_id': data['instance_id'],
                'status': 'synced',
                'message': 'Survey saved successfully',
                'plot_id': plot.plot_id,
            })

        except Exception as e:
            import traceback
            return Response({
                'instance_id': data.get('instance_id', ''),
                'status': 'error',
                'message': str(e),
                'detail': traceback.format_exc(),
            }, status=500)


# ═══════════════════════════════════════════════════════════════
#  TREE VIEWSET
# ═══════════════════════════════════════════════════════════════

class TreeViewSet(viewsets.ModelViewSet):
    queryset = TreeMeasurement.objects.all().select_related('plot')
    serializer_class = TreeSerializer
    filterset_fields = ['plot', 'species', 'tree_status']
    ordering_fields = ['tree_num', 'dbh', 'height']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TreeCreateSerializer
        return TreeSerializer


# ═══════════════════════════════════════════════════════════════
#  SOIL VIEWSET
# ═══════════════════════════════════════════════════════════════

class SoilSampleViewSet(viewsets.ModelViewSet):
    queryset = SoilSample.objects.all().select_related('plot')
    serializer_class = SoilSampleSerializer
    filterset_fields = ['plot', 'depth_class', 'soil_texture']
    ordering_fields = ['point_num', 'soil_ph', 'depth_cm']


# ═══════════════════════════════════════════════════════════════
#  WATER VIEWSET
# ═══════════════════════════════════════════════════════════════

class WaterAssessmentViewSet(viewsets.ModelViewSet):
    queryset = WaterAssessment.objects.all().select_related('plot')
    serializer_class = WaterAssessmentSerializer
    filterset_fields = ['plot', 'water_source_type', 'flow_regime']
    ordering_fields = ['water_source_name']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return WaterAssessmentCreateSerializer
        return WaterAssessmentSerializer


# ═══════════════════════════════════════════════════════════════
#  SOCIO-ECONOMIC VIEWSET
# ═══════════════════════════════════════════════════════════════

class SocioEconomicViewSet(viewsets.ModelViewSet):
    queryset = SocioEconomic.objects.all().select_related('plot')
    serializer_class = SocioEconomicSerializer
    filterset_fields = ['plot', 'community_type', 'tenure_security']
    ordering_fields = ['community_type']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SocioEconomicCreateSerializer
        return SocioEconomicSerializer


# ═══════════════════════════════════════════════════════════════
#  UPLOADED LAYERS VIEWSET
# ═══════════════════════════════════════════════════════════════

class UploadedLayerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing uploaded spatial layers.
    Supports: GeoJSON, GPX, KML, CSV, Shapefile formats.
    Stores geometries in PostGIS for map visualization.
    """
    queryset = UploadedLayer.objects.all()
    serializer_class = UploadedLayerSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_fields = ['layer_type', 'visible', 'uploaded_by']
    ordering_fields = ['uploaded_at', 'name', 'feature_count']
    ordering = ['-uploaded_at']

    def get_queryset(self):
        """Return layers for current user only."""
        user = self.request.user
        if user.is_authenticated:
            return UploadedLayer.objects.filter(uploaded_by=user)
        return UploadedLayer.objects.none()

    def perform_create(self, serializer):
        """Set uploaded_by to current user."""
        serializer.save(uploaded_by=self.request.user)

    @action(detail=False, methods=['post'], url_path='upload')
    def upload_geojson(self, request):
        """
        Accept GeoJSON FeatureCollection from frontend, validate,
        convert to PostGIS GeometryCollection, and persist.
        """
        name = request.data.get('name', 'Untitled Layer')
        geojson_data = request.data.get('geojson')
        color = request.data.get('color', '#c4a84a')
        layer_type = request.data.get('layer_type', 'geojson')

        if not geojson_data or not isinstance(geojson_data, dict):
            return Response(
                {'error': 'geojson field required as GeoJSON FeatureCollection'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if geojson_data.get('type') != 'FeatureCollection':
            return Response(
                {'error': 'GeoJSON must be a FeatureCollection'},
                status=status.HTTP_400_BAD_REQUEST
            )

        features = geojson_data.get('features', [])
        if not features:
            return Response(
                {'error': 'FeatureCollection contains no features'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Convert GeoJSON features to GEOS geometries for PostGIS storage
        # GEOSGeometry accepts GeoJSON string with srid=4326
        geometries = []
        for feature in features:
            geom = feature.get('geometry')
            if geom and geom.get('type'):
                try:
                    g = GEOSGeometry(json_mod.dumps(geom), srid=4326)
                    geometries.append(g)
                except Exception as e:
                    # Skip invalid geometries but continue processing
                    print(f"Warning: Failed to parse geometry: {e}")
                    continue

        if not geometries:
            return Response(
                {'error': 'No valid geometries found in uploaded data'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create GeometryCollection for mixed geometry types
        try:
            collection = GeometryCollection(*geometries, srid=4326)
        except Exception as e:
            return Response(
                {'error': f'Failed to create geometry collection: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create layer instance
        layer = UploadedLayer.objects.create(
            name=name,
            layer_type=layer_type,
            geojson_data=geojson_data,
            geometry=collection,
            color=color,
            visible=True,
            feature_count=len(features),
            uploaded_by=request.user,
        )

        serializer = self.get_serializer(layer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def bulk_upload(self, request):
        """Upload multiple layers at once."""
        layers_data = request.data.get('layers', [])
        created = []
        errors = []

        for layer_data in layers_data:
            serializer = self.get_serializer(data=layer_data)
            if serializer.is_valid():
                serializer.save(uploaded_by=request.user)
                created.append(serializer.data)
            else:
                errors.append({
                    'data': layer_data.get('name'),
                    'errors': serializer.errors
                })

        return Response({
            'created': len(created),
            'errors': len(errors),
            'layers': created,
            'error_details': errors,
        }, status=status.HTTP_201_CREATED if created else status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def toggle_visibility(self, request, pk=None):
        """Toggle layer visibility on/off."""
        layer = self.get_object()
        layer.visible = not layer.visible
        layer.save()
        return Response(self.get_serializer(layer).data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get upload statistics for current user."""
        queryset = self.get_queryset()
        return Response({
            'total_layers': queryset.count(),
            'total_features': sum(l.feature_count for l in queryset),
            'by_type': {
                'geojson': queryset.filter(layer_type='geojson').count(),
                'gpx': queryset.filter(layer_type='gpx').count(),
                'kml': queryset.filter(layer_type='kml').count(),
                'csv': queryset.filter(layer_type='csv').count(),
                'shapefile': queryset.filter(layer_type='shapefile').count(),
            },
        })


# ═══════════════════════════════════════════════════════════════
#  STATS
# ═══════════════════════════════════════════════════════════════

class StatsViewSet(viewsets.ViewSet):
    """Aggregate statistics with all 5 modules."""
    permission_classes = [AllowAny]

    def _get_or_compute(self, key, compute_fn, timeout=300):
        cached = cache.get(key)
        if cached is not None:
            return cached
        result = compute_fn()
        cache.set(key, result, timeout)
        return result

    def list(self, request):
        stats = self._get_or_compute('stats_summary', self._compute_summary)
        return Response(stats)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        stats = self._get_or_compute('stats_summary', self._compute_summary)
        return Response(stats)

    @action(detail=False, methods=['get'])
    def forest_types(self, request):
        data = self._get_or_compute('stats_forest_types', self._compute_forest_types)
        return Response(data)

    @action(detail=False, methods=['get'])
    def provinces(self, request):
        data = self._get_or_compute('stats_provinces', self._compute_provinces)
        return Response(data)

    @action(detail=False, methods=['get'])
    def species(self, request):
        data = self._get_or_compute('stats_species', self._compute_species)
        return Response(data)

    @action(detail=False, methods=['get'])
    def dbh_distribution(self, request):
        data = self._get_or_compute('stats_dbh', self._compute_dbh)
        return Response(data)

    @action(detail=False, methods=['get'])
    def soil(self, request):
        data = self._get_or_compute('stats_soil', self._compute_soil)
        return Response(data)

    @action(detail=False, methods=['get'])
    def timeline(self, request):
        data = self._get_or_compute('stats_timeline', self._compute_timeline)
        return Response(data)

    @action(detail=False, methods=['get'])
    def waypoints(self, request):
        data = self._get_or_compute('stats_waypoints', self._compute_waypoints)
        return Response(data)

    @action(detail=False, methods=['get'])
    def water(self, request):
        data = self._get_or_compute('stats_water', self._compute_water)
        return Response(data)

    @action(detail=False, methods=['get'])
    def socioeconomic(self, request):
        data = self._get_or_compute('stats_socioeconomic', self._compute_socioeconomic)
        return Response(data)

    def _compute_summary(self):
        from collections import Counter
        plots = Plot.objects.all()
        trees = TreeMeasurement.objects.all()
        soil = SoilSample.objects.all()
        transects = Transect.objects.all()
        water = WaterAssessment.objects.all()
        socio = SocioEconomic.objects.all()

        ft_counts = Counter(p.forest_type for p in plots)
        province_counts = Counter(p.province for p in plots)
        sp_counts = Counter(t.species for t in trees)

        dbh_buckets = [0, 0, 0, 0, 0, 0]
        for t in trees:
            dbh = float(t.dbh)
            if dbh < 15: dbh_buckets[0] += 1
            elif dbh < 25: dbh_buckets[1] += 1
            elif dbh < 35: dbh_buckets[2] += 1
            elif dbh < 45: dbh_buckets[3] += 1
            elif dbh < 55: dbh_buckets[4] += 1
            else: dbh_buckets[5] += 1

        total_grass_samples = sum(t.grass_samples.count() for t in transects)
        total_species_obs = sum(t.species_obs.count() for t in transects)

        # Water source breakdown
        water_source_counts = Counter(w.water_source_type for w in water if w.water_source_type)

        # Livelihood breakdown
        livelihood_counts = Counter()
        for s in socio:
            if s.livelihood_activities:
                for act in s.livelihood_activities.split(','):
                    livelihood_counts[act.strip()] += 1

        # Restoration support
        support_counts = Counter(s.restoration_support for s in socio if s.restoration_support)

        return {
            'total_plots': plots.count(),
            'total_trees_measured': trees.count(),
            'total_waypoints': sum(p.total_waypoints for p in plots),
            'total_grass_samples': total_grass_samples,
            'total_species_obs': total_species_obs,
            'avg_dbh': round(trees.aggregate(avg=Avg('dbh'))['avg'] or 0, 2),
            'avg_canopy_cover': round(plots.aggregate(avg=Avg('canopy_cover'))['avg'] or 0, 1),
            'total_species_observed': len(sp_counts),
            'total_soil_samples': soil.count(),
            'total_transects': transects.count(),
            'total_water_assessments': water.count(),
            'total_socioeconomic': socio.count(),
            'avg_ph': round(soil.aggregate(avg=Avg('soil_ph'))['avg'] or 0, 2),
            'forest_type_breakdown': dict(ft_counts),
            'province_breakdown': dict(province_counts),
            'species_counts': dict(sp_counts),
            'dbh_distribution': dbh_buckets,
            'dbh_labels': ['5-15', '15-25', '25-35', '35-45', '45-55', '55+'],
            'water_source_breakdown': dict(water_source_counts),
            'livelihood_breakdown': dict(livelihood_counts),
            'restoration_support_breakdown': dict(support_counts),
        }

    def _compute_forest_types(self):
        from collections import Counter
        plots = Plot.objects.all()
        return dict(Counter(p.forest_type for p in plots))

    def _compute_provinces(self):
        from collections import Counter
        plots = Plot.objects.all()
        return dict(Counter(p.province for p in plots))

    def _compute_species(self):
        from collections import Counter
        trees = TreeMeasurement.objects.all()
        return dict(Counter(t.species for t in trees))

    def _compute_dbh(self):
        trees = TreeMeasurement.objects.all()
        buckets = [0, 0, 0, 0, 0, 0]
        for t in trees:
            dbh = float(t.dbh)
            if dbh < 15: buckets[0] += 1
            elif dbh < 25: buckets[1] += 1
            elif dbh < 35: buckets[2] += 1
            elif dbh < 45: buckets[3] += 1
            elif dbh < 55: buckets[4] += 1
            else: buckets[5] += 1
        return {'labels': ['5-15', '15-25', '25-35', '35-45', '45-55', '55+'], 'values': buckets}

    def _compute_soil(self):
        soil = SoilSample.objects.all()
        from collections import Counter
        texture_counts = Counter(s.soil_texture for s in soil)
        depth_counts = Counter(s.depth_class for s in soil)
        return {
            'total_samples': soil.count(),
            'avg_ph': round(soil.aggregate(avg=Avg('soil_ph'))['avg'] or 0, 2),
            'avg_bulk_density': round(soil.aggregate(avg=Avg('bulk_density'))['avg'] or 0, 3),
            'texture_breakdown': dict(texture_counts),
            'depth_breakdown': dict(depth_counts),
        }

    def _compute_timeline(self):
        from collections import defaultdict
        plots = Plot.objects.order_by('date').prefetch_related(
            'trees', 'soil_samples', 'transects__species_obs',
            'transects__grass_samples', 'water_assessment', 'socioeconomic'
        )
        date_map = defaultdict(lambda: {
            'plots': 0, 'samples': 0, 'trees': 0,
            'water': 0, 'socio': 0, 'species_obs': 0, 'grass': 0
        })
        for p in plots:
            date_key = p.date.isoformat()
            date_map[date_key]['plots'] += 1
            date_map[date_key]['samples'] += p.soil_samples.count()
            date_map[date_key]['trees'] += p.trees.count()
            date_map[date_key]['water'] += 1 if hasattr(p, 'water_assessment') and p.water_assessment else 0
            date_map[date_key]['socio'] += 1 if hasattr(p, 'socioeconomic') and p.socioeconomic else 0
            date_map[date_key]['species_obs'] += sum(
                t.species_obs.count() for t in p.transects.all()
            )
            date_map[date_key]['grass'] += sum(
                t.grass_samples.count() for t in p.transects.all()
            )

        sorted_dates = sorted(date_map.keys())
        cum_plots, cum_samples, cum_trees, cum_water, cum_socio, cum_species, cum_grass = 0, 0, 0, 0, 0, 0, 0
        result = {
            'dates': [],
            'cumulative_plots': [],
            'cumulative_samples': [],
            'cumulative_trees': [],
            'cumulative_water': [],
            'cumulative_socio': [],
            'cumulative_species_obs': [],
            'cumulative_grass': [],
        }
        for d in sorted_dates:
            v = date_map[d]
            cum_plots += v['plots']
            cum_samples += v['samples']
            cum_trees += v['trees']
            cum_water += v['water']
            cum_socio += v['socio']
            cum_species += v['species_obs']
            cum_grass += v['grass']
            result['dates'].append(d)
            result['cumulative_plots'].append(cum_plots)
            result['cumulative_samples'].append(cum_samples)
            result['cumulative_trees'].append(cum_trees)
            result['cumulative_water'].append(cum_water)
            result['cumulative_socio'].append(cum_socio)
            result['cumulative_species_obs'].append(cum_species)
            result['cumulative_grass'].append(cum_grass)
        return result

    def _compute_waypoints(self):
        plots = Plot.objects.all()
        trees = TreeMeasurement.objects.count()
        soil = SoilSample.objects.count()
        transects = Transect.objects.all()
        grass = sum(t.grass_samples.count() for t in transects)
        species_obs = sum(t.species_obs.count() for t in transects)
        total = sum(p.total_waypoints for p in plots)
        return {
            'total': total,
            'plot_centers': plots.count(),
            'tree_measurements': trees,
            'species_observations': species_obs,
            'grass_samples': grass,
            'soil_samples': soil,
        }

    def _compute_water(self):
        from collections import Counter
        water = WaterAssessment.objects.all()
        source_counts = Counter(w.water_source_type for w in water if w.water_source_type)
        regime_counts = Counter(w.flow_regime for w in water if w.flow_regime)
        quality_counts = Counter(w.water_quality_category for w in water if w.water_quality_category)
        return {
            'total': water.count(),
            'source_breakdown': dict(source_counts),
            'flow_regime_breakdown': dict(regime_counts),
            'quality_breakdown': dict(quality_counts),
        }

    def _compute_socioeconomic(self):
        from collections import Counter
        socio = SocioEconomic.objects.all()
        community_counts = Counter(s.community_type for s in socio if s.community_type)
        tenure_counts = Counter(s.tenure_security for s in socio if s.tenure_security)
        support_counts = Counter(s.restoration_support for s in socio if s.restoration_support)
        return {
            'total': socio.count(),
            'community_type_breakdown': dict(community_counts),
            'tenure_security_breakdown': dict(tenure_counts),
            'restoration_support_breakdown': dict(support_counts),
        }