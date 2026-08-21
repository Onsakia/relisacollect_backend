"""
GeoDjango models for SA Carbon & Biodiversity Survey.
All spatial fields use SRID 4326 (WGS 84).
Includes: Biomass, Biodiversity, Soil, Water/Hydrology, Socio-Economic modules.
"""
from django.contrib.gis.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# ── All choice definitions (complete) ──────────────────────────

PROVINCE_CHOICES = [
    ('eastern_cape','Eastern Cape'), ('free_state','Free State'), ('gauteng','Gauteng'),
    ('kwazulu_natal','KwaZulu-Natal'), ('limpopo','Limpopo'), ('mpumalanga','Mpumalanga'),
    ('northern_cape','Northern Cape'), ('north_west','North West'), ('western_cape','Western Cape'),
    ('other','Other (Specify)'),
]

FOREST_TYPE_CHOICES = [
    ('afrotemperate','Afrotemperate Forest'), ('thicket','Albany Thicket'),
    ('savanna','Savanna Woodland'), ('grassland','Grassland'),
    ('plantation','Commercial Plantation'), ('other','Other (Specify)'),
]

TREE_STATUS_CHOICES = [
    ('live','Live/Healthy'), ('live_damaged','Live/Damaged'),
    ('dead_standing','Dead Standing'), ('dead_down','Dead Down'),
    ('stump','Stump'), ('other','Other (Specify)'),
]

WATER_DIST_CHOICES = [
    ('less_200m','0-200m (Very close)'), ('200_600m','200-600m (Moderate distance)'),
    ('beyond_600m','Beyond 600m (Distant)'),
]

SETTLEMENT_DIST_CHOICES = [
    ('less_500m','0-500m (Very close)'), ('500_1500m','500m-1.5km (Moderate distance)'),
    ('beyond_1500m','More than 1.5km (Remote)'),
]

HABITAT_CONDITION_CHOICES = [
    ('pristine','Pristine/Natural'), ('good','Good Condition'),
    ('moderate','Moderate Degradation'), ('degraded','Degraded'),
    ('other','Other (Specify)'),
]

STANDARD_CHOICES = [
    ('ccb','CCB (Climate, Community & Biodiversity)'),
    ('vcs','VCS (Verified Carbon Standard)'), ('ccb_vcs','CCB + VCS'),
    ('gold','Gold Standard'), ('planvivo','Plan Vivo'),
    ('multiple','Multiple Standards'), ('other','Other (Specify)'),
]

TENURE_CHOICES = [
    ('communal','Communal Land'), ('private','Private Land'),
    ('state','State Land'), ('community','Community Trust'),
    ('pa','Protected Area'), ('other','Other (Specify)'),
]

YES_NO_CHOICES = [('yes','Yes'), ('no','No')]
YES_NO_OTHER_CHOICES = [('yes','Yes'), ('no','No'), ('other','Other (Specify)')]

SPECIES_CHOICES = [
    ('acacia_karroo','Acacia karroo (Soetdoring)'), ('acacia_mearnsii','Acacia mearnsii (Black Wattle)'),
    ('afrocarpus_falcatus','Afrocarpus falcatus (Outeniqua Yellowwood)'), ('brabejum','Brabejum stellatifolium (Wild Almond)'),
    ('celtis_africana','Celtis africana (White Stinkwood)'), ('euphorbia','Euphorbia spp.'),
    ('ficus','Ficus spp. (Wild Fig)'), ('ilex_mitis','Ilex mitis (African Holly)'),
    ('olea_capensis','Olea capensis (Ironwood)'), ('podocarpus','Podocarpus latifolius (Real Yellowwood)'),
    ('prunus_africana','Prunus africana (Red Stinkwood)'), ('virgilia','Virgilia oroboides (Blossom Tree)'),
    ('invasive_wattle','Invasive Acacia spp.'), ('eucalyptus','Eucalyptus spp.'), ('pine','Pinus spp.'),
    ('other','Other (Specify)'),
]

GRASS_SPECIES_CHOICES = [
    ('loteropsis_semialata','Loteropsis semialata'), ('andropogon_eucomis','Andropogon eucomis'),
    ('bewsia_biflora','Bewsia biflora'), ('brachiaria_serrata','Brachiaria serrata'),
    ('cymbopogon_nardus','Cymbopogon nardus'), ('themeda_triandra','Themeda triandra'),
    ('heteropogon_contortus','Heteropogon contortus'), ('hyparrhenia_hirta','Hyparrhenia hirta'),
    ('megathyrsus_maximus','Megathyrsus maximus'), ('ehrharta_calycina','Ehrharta calycina'),
    ('mixed','Mixed grass species'), ('other','Other (Specify)'),
]

TRANSECT_CHOICES = [
    ('t1','Transect 1 (NE-SW)'), ('t2','Transect 2 (NW-SE)'), ('other','Other (Specify)'),
]

BIO_TYPE_CHOICES = [
    ('tree','Tree/Shrub'), ('herb','Herb/Forb'), ('grass','Grass'), ('fern','Fern'),
    ('animal_sign','Animal Sign'), ('invasive','Invasive Species'), ('other','Other (Specify)'),
]

THREAT_CHOICES = [
    ('lc','Least Concern (LC)'), ('nt','Near Threatened (NT)'), ('vu','Vulnerable (VU)'),
    ('en','Endangered (EN)'), ('cr','Critically Endangered (CR)'), ('invasive','Invasive/Alien'),
    ('other','Other (Specify)'),
]

ASPECT_CHOICES = [
    ('north','North (0)'), ('northeast','North-East (45)'), ('east','East (90)'),
    ('southeast','South-East (135)'), ('south','South (180)'), ('southwest','South-West (225)'),
    ('west','West (270)'), ('northwest','North-West (315)'), ('flat','Flat/No Aspect'),
    ('other','Other (Specify)'),
]

LANDFORM_CHOICES = [
    ('ridge','Ridge/Crest'), ('upper_slope','Upper Slope'), ('mid_slope','Middle Slope'),
    ('lower_slope','Lower Slope'), ('valley','Valley/Footslope'), ('plain','Plain/Flat'),
    ('depression','Depression/Wetland'), ('other','Other (Specify)'),
]

DEGRADATION_CHOICES = [
    ('none','None/Pristine'), ('low','Low - Minor disturbances'), ('moderate','Moderate - Some loss of function'),
    ('high','High - Significant degradation'), ('severe','Severe - Major rehabilitation needed'),
    ('other','Other (Specify)'),
]

EROSION_CHOICES = [
    ('none','No visible erosion'), ('sheet','Sheet erosion (surface wash)'),
    ('rill','Rill erosion (small channels)'), ('gully','Gully erosion (large channels)'),
    ('slump','Slumping/mass movement'), ('wind','Wind erosion'), ('other','Other (Specify)'),
]

WATER_DIST_CHOICES_MICRO = [
    ('less_100m','Less than 100m'), ('100_200m','100-200m'), ('200_500m','200-500m'),
    ('greater_500m','Greater than 500m'), ('no_water','No permanent water nearby'), ('other','Other (Specify)'),
]

DEPTH_CHOICES = [
    ('topsoil','Topsoil (0-10cm)'), ('subsoil','Subsoil (10-30cm)'), ('deep','Deep (30-50cm)'),
    ('custom','Custom Depth'), ('other','Other (Specify)'),
]

TEXTURE_CHOICES = [
    ('sand','Sand'), ('loam','Loam'), ('clay','Clay'), ('sandy_loam','Sandy Loam'),
    ('clay_loam','Clay Loam'), ('silt','Silt'), ('other','Other (Specify)'),
]

SOIL_POINT_CHOICES = [
    ('p1','Point 1 (Center)'), ('p2','Point 2 (North)'), ('p3','Point 3 (East)'),
    ('p4','Point 4 (South)'), ('p5','Point 5 (West)'), ('other','Other (Specify)'),
]

BURN_HISTORY_CHOICES = [
    ('recent','Recent (within 1 year)'), ('1_2_years','1-2 years ago'), ('2_5_years','2-5 years ago'),
    ('more_5_years','More than 5 years ago'), ('never','Never/No evidence of burning'), ('unknown','Unknown'),
]

# ── Water/Hydrology Choices ────────────────────────────────────

WATER_SOURCE_CHOICES = [
    ('perennial_river','Perennial River'), ('seasonal_river','Seasonal River/Stream'),
    ('spring','Spring (Natural)'), ('wetland','Wetland/Marsh'), ('dam_reservoir','Dam/Reservoir'),
    ('farm_dam','Farm Dam'), ('groundwater_borehole','Groundwater/Borehole'),
    ('rainwater_harvest','Rainwater Harvesting'), ('ephemeral_pan','Ephemeral Pan/Vlei'),
    ('no_water','No Permanent Water Source'), ('other','Other (Specify)'),
]

FLOW_REGIME_CHOICES = [
    ('perennial','Perennial (flows year-round)'), ('intermittent','Intermittent (seasonal flow)'),
    ('ephemeral','Ephemeral (flows only after rain)'), ('dry','Dry/No Flow Observed'),
    ('regulated','Regulated/Controlled (dam upstream)'), ('unknown','Unknown'),
]

SEASONAL_AVAILABILITY_CHOICES = [
    ('permanent','Permanent (available year-round)'), ('seasonal_reliable','Seasonal but Reliable'),
    ('seasonal_unreliable','Seasonal and Unreliable'), ('drought_prone','Drought-Prone (often dries up)'),
    ('unknown','Unknown'),
]

WATER_QUALITY_CHOICES = [
    ('excellent','Excellent (pristine, potable)'), ('good','Good (minor impairments)'),
    ('fair','Fair (some pollution/impairment)'), ('poor','Poor (significantly impaired)'),
    ('very_poor','Very Poor (heavily polluted)'), ('not_tested','Not Field-Tested'),
]

RIPARIAN_CONDITION_CHOICES = [
    ('pristine','Pristine (intact natural vegetation)'), ('good','Good (minor disturbances)'),
    ('moderate','Moderate (some degradation)'), ('degraded','Degraded (significant loss)'),
    ('severely_degraded','Severely Degraded (bare/cultivated banks)'),
]

STREAM_BANK_EROSION_CHOICES = [
    ('none','None (stable banks)'), ('slight','Slight (<10% bank affected)'),
    ('moderate','Moderate (10-30% bank affected)'), ('severe','Severe (30-60% bank affected)'),
    ('very_severe','Very Severe (>60% bank affected)'),
]

WETLAND_TYPE_CHOICES = [
    ('floodplain','Floodplain'), ('depression','Depression (endoreic basin)'),
    ('channelled_valley','Channelled Valley Bottom'), ('hillslope_seep','Hillslope Seep'),
    ('pan','Pan (endorheic depression)'), ('estuarine','Estuarine'),
    ('none','No Wetland Present'), ('other','Other (Specify)'),
]

WETLAND_CONDITION_CHOICES = [
    ('unmodified','Unmodified (natural/near-natural)'), ('largely_natural','Largely Natural'),
    ('moderately_modified','Moderately Modified'), ('largely_modified','Largely Modified'),
    ('seriously_modified','Seriously Modified'), ('none','No Wetland Present'),
]

WATER_EXTRACTION_CHOICES = [
    ('domestic','Domestic/Household'), ('livestock','Livestock Watering'),
    ('irrigation','Irrigation (Agriculture)'), ('mining','Mining/Industrial'),
    ('recreation','Recreation/Tourism'), ('ecosystem','Ecosystem Maintenance'),
    ('none_observed','No Extraction Observed'),
]

DOWNSTREAM_IMPACT_CHOICES = [
    ('none','None Observed'), ('reduced_flow','Reduced Downstream Flow'),
    ('sedimentation','Increased Sedimentation'), ('pollution','Pollution Transfer'),
    ('erosion','Downstream Erosion'), ('wetland_loss','Wetland Loss Downstream'),
    ('unknown','Unknown'),
]

# ── Socio-Economic Choices ─────────────────────────────────────

COMMUNITY_TYPE_CHOICES = [
    ('rural_village','Rural Village (traditional)'), ('rural_scattered','Rural (scattered homesteads)'),
    ('peri_urban','Peri-Urban'), ('township','Township'),
    ('farm_laborer','Farm Labourer Settlement'), ('communal_area','Communal/Traditional Authority Area'),
    ('informal_settlement','Informal Settlement'), ('other','Other (Specify)'),
]

TENURE_SECURITY_CHOICES = [
    ('very_secure','Very Secure (freehold/deed)'), ('secure','Secure (CPAs, Trusts, Communal Permission)'),
    ('moderate','Moderate (Permission to Occupy)'), ('insecure','Insecure (no formal documentation)'),
    ('disputed','Disputed (under land claim/court case)'),
]

LAND_USE_CURRENT_CHOICES = [
    ('grazing','Grazing (livestock)'), ('cropland','Cropland (cultivation)'),
    ('fallow','Fallow/Abandoned'), ('forest_reserve','Forest Reserve/Protected'),
    ('plantation','Commercial Plantation'), ('mining','Mining/Extractive'),
    ('conservation','Conservation Area'), ('unoccupied','Unoccupied/Unused'),
    ('mixed_use','Mixed Use'), ('other','Other (Specify)'),
]

LAND_USE_HISTORY_CHOICES = [
    ('grazing','Historical Grazing'), ('cropland','Historical Cropland'),
    ('plantation','Historical Plantation'), ('mining','Historical Mining'),
    ('indigenous_forest','Indigenous Forest (historically)'), ('settlement','Settlement'),
    ('fire','Repeated Fire History'),
]

LIVELIHOOD_CHOICES = [
    ('livestock','Livestock Farming'), ('crop_farming','Crop Farming (subsistence/commercial)'),
    ('wage_labour','Wage Labour (farm/mine/other)'), ('informal_trade','Informal Trade/Small Business'),
    ('remittances','Remittances'), ('government_grant','Government Social Grants'),
    ('tourism','Tourism/Conservation Employment'), ('hunting_gathering','Hunting/Gathering (wild resources)'),
    ('artisanal_mining','Artisanal/Small-scale Mining'), ('other','Other'),
]

INCOME_SOURCE_CHOICES = [
    ('agriculture','Agriculture (crops/livestock)'), ('wage_labour','Wage Labour'),
    ('social_grants','Social Grants (SASSA)'), ('remittances','Remittances'),
    ('informal_business','Informal Business'), ('mining','Mining (formal/informal)'),
    ('tourism','Tourism/Conservation'), ('other','Other'),
]

INCOME_LEVEL_CHOICES = [
    ('below_poverty','Below Food Poverty Line (<R760/month)'), ('low','Low Income (R760 - R2,500/month)'),
    ('lower_middle','Lower-Middle (R2,500 - R5,500/month)'), ('middle','Middle Income (R5,500 - R15,000/month)'),
    ('above_middle','Above Middle (>R15,000/month)'), ('unknown','Unknown/Declined to Answer'),
]

AWARENESS_CHOICES = [
    ('very_aware','Very Aware (active engagement)'), ('aware','Aware (have heard of it)'),
    ('somewhat','Somewhat Aware (limited knowledge)'), ('not_aware','Not Aware'),
]

SUPPORT_CHOICES = [
    ('very_supportive','Very Supportive'), ('supportive','Supportive'),
    ('neutral','Neutral'), ('opposed','Opposed'), ('very_opposed','Very Opposed'),
]

RESTORATION_BENEFIT_CHOICES = [
    ('jobs','Job Creation'), ('water_security','Improved Water Security'),
    ('grazing','Better Grazing/Forage'), ('firewood','Firewood/Fuelwood Supply'),
    ('medicinal_plants','Medicinal Plants Access'), ('carbon_payments','Carbon Credit Payments'),
    ('tourism','Tourism Opportunities'), ('soil_protection','Soil Erosion Protection'),
    ('biodiversity','Biodiversity/Natural Heritage'), ('climate_adaptation','Climate Change Adaptation'),
]

YES_NO_UNSURE_CHOICES = [('yes','Yes'), ('no','No'), ('unsure','Unsure/Maybe')]

INDIGENOUS_PRACTICE_CHOICES = [
    ('controlled_burning','Controlled Burning (traditional)'), ('rotational_grazing','Rotational Grazing Systems'),
    ('seed_harvesting','Indigenous Seed Harvesting'), ('water_harvesting','Traditional Water Harvesting'),
    ('sacred_groves','Sacred Grove Protection'), ('taboo_systems','Taboo/Access Restriction Systems'),
    ('herbal_medicine','Traditional Herbal Medicine Collection'), ('other','Other (Specify)'),
]

CAPACITY_NEED_CHOICES = [
    ('nursery_management','Tree Nursery Management'), ('planting_techniques','Planting & Establishment Techniques'),
    ('fire_management','Fire Management'), ('monitoring','Ecological Monitoring'),
    ('business_skills','Small Business/Enterprise Skills'), ('carbon_markets','Carbon Market/Trading Knowledge'),
    ('gis_gps','GIS/GPS Technology Use'), ('record_keeping','Financial/Project Record Keeping'),
    ('leadership','Community Leadership/Organizing'), ('other','Other'),
]

JOB_POTENTIAL_CHOICES = [
    ('1_10','1-10 jobs'), ('11_50','11-50 jobs'), ('51_100','51-100 jobs'),
    ('100_plus','100+ jobs'), ('unknown','Unknown'),
]

GENDER_BALANCE_CHOICES = [
    ('mostly_men','Mostly Male Participants'), ('mostly_women','Mostly Female Participants'),
    ('balanced','Gender Balanced'), ('women_led','Women-Led'), ('unknown','Unknown'),
]

FIRE_RISK_CHOICES = [
    ('low','Low (rare fires)'), ('moderate','Moderate (occasional fires)'),
    ('high','High (frequent fires)'), ('very_high','Very High (annual/severe fires)'),
]

RESTORATION_CHALLENGE_CHOICES = [
    ('tenure_insecurity','Land Tenure Insecurity'), ('funding','Insufficient Funding'),
    ('capacity','Lack of Technical Capacity'), ('water_scarcity','Water Scarcity/Drought'),
    ('grazing_pressure','Livestock Grazing Pressure'), ('invasive_species','Invasive Species'),
    ('fire','Uncontrolled Fire'), ('mining','Mining/Extractive Activities'),
    ('community_conflict','Community Conflict'), ('climate_change','Climate Change Impacts'),
    ('seed_availability','Indigenous Seed Availability'), ('other','Other'),
]

INVASIVE_THREAT_CHOICES = [
    ('acacia_mearnsii','Black Wattle (Acacia mearnsii)'), ('acacia_dealbata','Silver Wattle (Acacia dealbata)'),
    ('acacia_saligna','Port Jackson (Acacia saligna)'), ('eucalyptus','Eucalyptus/Gum Trees'),
    ('pine','Pine Species (Pinus)'), ('lantana','Lantana (Lantana camara)'),
    ('prickly_pear','Prickly Pear (Opuntia)'), ('parthenium','Parthenium (Parthenium hysterophorus)'),
    ('chromolaena','Chromolaena (Chromolaena odorata)'), ('sesbania','Red Sesbania (Sesbania punicea)'),
    ('triffid_weed','Triffid Weed (Chromolaena)'), ('other','Other (Specify)'),
]

SDG_CHOICES = [
    ('sdg13','SDG 13: Climate Action'), ('sdg15','SDG 15: Life on Land'),
    ('sdg1','SDG 1: No Poverty'), ('sdg8','SDG 8: Decent Work'),
    ('sdg12','SDG 12: Responsible Consumption'), ('other','Other (Specify)'),
]

PHOTO_TYPE_CHOICES = [
    ('whole_plant','Whole Plant/Organism'), ('leaf_detail','Leaf/Stem Detail'),
    ('flower_fruit','Flower/Fruit/Seed'), ('bark_trunk','Bark/Trunk Texture'),
    ('habitat','Habitat Context'), ('close_up','Diagnostic Close-up'),
    ('scale','Scale/Reference Object'), ('other','Other (Specify)'),
]


# ═══════════════════════════════════════════════════════════════
#  MODELS
# ═══════════════════════════════════════════════════════════════

class Plot(models.Model):
    """Primary survey unit -- a 50x50m vegetation plot."""
    plot_id = models.CharField(max_length=20, unique=True, db_index=True)
    site_name = models.CharField(max_length=100)
    province = models.CharField(max_length=20, choices=PROVINCE_CHOICES, default='eastern_cape')
    date = models.DateField()
    enumerator = models.CharField(max_length=100)

    # Spatial
    location = models.PointField(srid=4326, geography=True)
    altitude = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    gps_accuracy = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    gps_point_number = models.PositiveIntegerField(default=1, help_text='Sequential GPS waypoint for plot center')
    plot_radius = models.IntegerField(default=25)

    # Distances
    dist_water_point = models.CharField(max_length=20, choices=WATER_DIST_CHOICES, blank=True)
    dist_settlement = models.CharField(max_length=20, choices=SETTLEMENT_DIST_CHOICES, blank=True)
    water_point_notes = models.TextField(blank=True)
    settlement_notes = models.TextField(blank=True)

    # Vegetation
    forest_type = models.CharField(max_length=20, choices=FOREST_TYPE_CHOICES)
    trees_count_est = models.IntegerField(blank=True, null=True)
    habitat_condition = models.CharField(max_length=20, choices=HABITAT_CONDITION_CHOICES, blank=True)
    canopy_cover = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(100)])

    # Carbon standards
    carbon_standard = models.CharField(max_length=20, choices=STANDARD_CHOICES, blank=True)
    land_tenure = models.CharField(max_length=20, choices=TENURE_CHOICES, blank=True)
    community_consult = models.CharField(max_length=10, choices=YES_NO_CHOICES, blank=True)
    community_name = models.CharField(max_length=100, blank=True)
    ccb_compliance = models.CharField(max_length=10, choices=YES_NO_OTHER_CHOICES, blank=True)
    ccb_level = models.CharField(max_length=20, blank=True)
    gs_sdgs = models.CharField(max_length=10, choices=YES_NO_OTHER_CHOICES, blank=True)
    pv_community = models.CharField(max_length=100, blank=True)
    pv_scheme = models.CharField(max_length=100, blank=True)

    # Module flags
    module_biomass = models.CharField(max_length=10, choices=YES_NO_CHOICES, blank=True, default='yes')
    module_biodiversity = models.CharField(max_length=10, choices=YES_NO_CHOICES, blank=True, default='yes')
    module_soil = models.CharField(max_length=10, choices=YES_NO_CHOICES, blank=True, default='yes')
    module_water = models.CharField(max_length=10, choices=YES_NO_CHOICES, blank=True, default='no')
    module_socioeconomic = models.CharField(max_length=10, choices=YES_NO_CHOICES, blank=True, default='no')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', 'plot_id']
        indexes = [
            models.Index(fields=['forest_type']),
            models.Index(fields=['date']),
            models.Index(fields=['province']),
            models.Index(fields=['module_water']),
            models.Index(fields=['module_socioeconomic']),
        ]

    def __str__(self):
        return f"{self.plot_id} -- {self.site_name}"

    @property
    def total_trees(self):
        return self.trees.count()

    @property
    def samples_collected(self):
        return self.soil_samples.count()

    @property
    def total_waypoints(self):
        return (1 + self.trees.count() +
                sum(t.species_obs.count() for t in self.transects.all()) +
                sum(t.grass_samples.count() for t in self.transects.all()) +
                self.soil_samples.count())

    @property
    def soil_coverage(self):
        if self.soil_samples.count() == 0:
            return 0
        return (self.soil_samples.count() / 5) * 100


class TreeMeasurement(models.Model):
    """Individual tree measurements within a plot."""
    plot = models.ForeignKey(Plot, on_delete=models.CASCADE, related_name='trees')
    tree_id = models.CharField(max_length=20)
    tree_num = models.IntegerField()
    gps_waypoint_number = models.PositiveIntegerField(help_text='GPS waypoint for this tree sample point')
    species = models.CharField(max_length=30, choices=SPECIES_CHOICES)
    tree_status = models.CharField(max_length=20, choices=TREE_STATUS_CHOICES)
    dbh = models.DecimalField(max_digits=6, decimal_places=2)
    height = models.DecimalField(max_digits=6, decimal_places=2)
    crown_width_n = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    crown_width_e = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    herbal_veg_present = models.CharField(max_length=10, choices=YES_NO_OTHER_CHOICES, blank=True)
    herbal_veg_weight = models.DecimalField(max_digits=6, decimal_places=3, blank=True, null=True)
    deadwood = models.CharField(max_length=10, choices=YES_NO_OTHER_CHOICES, blank=True)
    deadwood_weight = models.DecimalField(max_digits=6, decimal_places=3, blank=True, null=True)

    class Meta:
        ordering = ['tree_num']

    @property
    def estimated_carbon(self):
        rho = 0.6
        dbh = float(self.dbh)
        height = float(self.height)
        agb = 0.0673 * (rho * (dbh ** 2) * height) ** 0.976
        return round(agb * 1.85, 2)


class Transect(models.Model):
    plot = models.ForeignKey(Plot, on_delete=models.CASCADE, related_name='transects')
    transect_id = models.CharField(max_length=10, choices=TRANSECT_CHOICES)
    transect_num = models.IntegerField()
    start_point = models.PointField(srid=4326, geography=True, blank=True, null=True)
    end_point = models.PointField(srid=4326, geography=True, blank=True, null=True)

    class Meta:
        ordering = ['transect_num']


class SpeciesObservation(models.Model):
    transect = models.ForeignKey(Transect, on_delete=models.CASCADE, related_name='species_obs')
    observation_num = models.PositiveIntegerField(default=1)
    gps_waypoint_number = models.PositiveIntegerField(help_text='GPS waypoint for this observation point')
    bio_type = models.CharField(max_length=20, choices=BIO_TYPE_CHOICES)
    species = models.CharField(max_length=30, choices=SPECIES_CHOICES)
    abundance = models.IntegerField()
    threat_status = models.CharField(max_length=20, choices=THREAT_CHOICES, blank=True)
    dbh_bio = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    aspect = models.CharField(max_length=20, choices=ASPECT_CHOICES, blank=True)
    landform = models.CharField(max_length=20, choices=LANDFORM_CHOICES, blank=True)
    degradation_level = models.CharField(max_length=20, choices=DEGRADATION_CHOICES, blank=True)
    erosion = models.CharField(max_length=20, choices=EROSION_CHOICES, blank=True)
    water_distance = models.CharField(max_length=20, choices=WATER_DIST_CHOICES_MICRO, blank=True)
    micro_habitat_notes = models.TextField(blank=True)


class GrassBiomassSample(models.Model):
    transect = models.ForeignKey(Transect, on_delete=models.CASCADE, related_name='grass_samples')
    sample_num = models.IntegerField()
    gps_waypoint_number = models.PositiveIntegerField(help_text='GPS waypoint for this grass sample point')
    grass_gps = models.PointField(srid=4326, geography=True, blank=True, null=True)
    grass_species = models.CharField(max_length=30, choices=GRASS_SPECIES_CHOICES)
    grass_weight = models.DecimalField(max_digits=6, decimal_places=3)
    last_burned = models.CharField(max_length=20, choices=BURN_HISTORY_CHOICES, blank=True)
    grass_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['sample_num']


class SoilSample(models.Model):
    plot = models.ForeignKey(Plot, on_delete=models.CASCADE, related_name='soil_samples')
    point_id = models.CharField(max_length=10, choices=SOIL_POINT_CHOICES)
    point_num = models.IntegerField()
    gps_waypoint_number = models.PositiveIntegerField(help_text='GPS waypoint for this soil sample point')
    soil_gps = models.PointField(srid=4326, geography=True, blank=True, null=True)
    depth_class = models.CharField(max_length=20, choices=DEPTH_CHOICES)
    depth_cm = models.DecimalField(max_digits=6, decimal_places=2)
    soil_texture = models.CharField(max_length=20, choices=TEXTURE_CHOICES)
    bulk_density = models.DecimalField(max_digits=6, decimal_places=3, blank=True, null=True)
    soil_ph = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    lab_id = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ['point_num']


# ═══════════════════════════════════════════════════════════════
#  WATER / HYDROLOGY MODULE
# ═══════════════════════════════════════════════════════════════

class WaterAssessment(models.Model):
    """Water and hydrology data collected per plot."""
    plot = models.OneToOneField(Plot, on_delete=models.CASCADE, related_name='water_assessment')
    water_source_type = models.CharField(max_length=30, choices=WATER_SOURCE_CHOICES, blank=True)
    water_source_name = models.CharField(max_length=100, blank=True)
    water_source_gps = models.PointField(srid=4326, geography=True, blank=True, null=True)
    flow_regime = models.CharField(max_length=20, choices=FLOW_REGIME_CHOICES, blank=True)
    seasonal_availability = models.CharField(max_length=20, choices=SEASONAL_AVAILABILITY_CHOICES, blank=True)
    water_ph = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    water_temperature = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    water_turbidity_ntu = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    electrical_conductivity = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    water_quality_category = models.CharField(max_length=20, choices=WATER_QUALITY_CHOICES, blank=True)
    riparian_veg_condition = models.CharField(max_length=20, choices=RIPARIAN_CONDITION_CHOICES, blank=True)
    stream_bank_erosion = models.CharField(max_length=20, choices=STREAM_BANK_EROSION_CHOICES, blank=True)
    wetland_type = models.CharField(max_length=20, choices=WETLAND_TYPE_CHOICES, blank=True)
    wetland_condition = models.CharField(max_length=20, choices=WETLAND_CONDITION_CHOICES, blank=True)
    wetland_width_m = models.PositiveIntegerField(blank=True, null=True)
    water_extraction_uses = models.CharField(max_length=200, blank=True)  # stored as comma-separated
    downstream_impacts = models.CharField(max_length=20, choices=DOWNSTREAM_IMPACT_CHOICES, blank=True)
    water_notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.plot.plot_id} -- Water"


# ═══════════════════════════════════════════════════════════════
#  SOCIO-ECONOMIC MODULE
# ═══════════════════════════════════════════════════════════════

class SocioEconomic(models.Model):
    """Socio-economic and community data collected per plot."""
    plot = models.OneToOneField(Plot, on_delete=models.CASCADE, related_name='socioeconomic')
    community_type = models.CharField(max_length=20, choices=COMMUNITY_TYPE_CHOICES, blank=True)
    households_nearby = models.PositiveIntegerField(blank=True, null=True)
    population_estimate = models.PositiveIntegerField(blank=True, null=True)
    tenure_security = models.CharField(max_length=20, choices=TENURE_SECURITY_CHOICES, blank=True)
    land_use_current = models.CharField(max_length=20, choices=LAND_USE_CURRENT_CHOICES, blank=True)
    land_use_history = models.CharField(max_length=200, blank=True)
    livelihood_activities = models.CharField(max_length=300, blank=True)
    primary_income_source = models.CharField(max_length=20, choices=INCOME_SOURCE_CHOICES, blank=True)
    household_income_level = models.CharField(max_length=20, choices=INCOME_LEVEL_CHOICES, blank=True)
    community_restoration_awareness = models.CharField(max_length=20, choices=AWARENESS_CHOICES, blank=True)
    restoration_support = models.CharField(max_length=20, choices=SUPPORT_CHOICES, blank=True)
    expected_restoration_benefits = models.CharField(max_length=300, blank=True)
    willingness_to_participate = models.CharField(max_length=10, choices=YES_NO_UNSURE_CHOICES, blank=True)
    traditional_leadership_involved = models.CharField(max_length=10, choices=YES_NO_CHOICES, blank=True)
    indigenous_practices_present = models.CharField(max_length=10, choices=YES_NO_CHOICES, blank=True)
    indigenous_practices_types = models.CharField(max_length=300, blank=True)
    traditional_knowledge_notes = models.TextField(blank=True)
    capacity_building_needs = models.CharField(max_length=300, blank=True)
    job_creation_potential = models.CharField(max_length=20, choices=JOB_POTENTIAL_CHOICES, blank=True)
    gender_balance_participation = models.CharField(max_length=20, choices=GENDER_BALANCE_CHOICES, blank=True)
    restoration_challenges = models.CharField(max_length=300, blank=True)
    fire_risk_level = models.CharField(max_length=20, choices=FIRE_RISK_CHOICES, blank=True)
    invasive_species_threats = models.CharField(max_length=300, blank=True)
    socioeconomic_notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.plot.plot_id} -- Socio-Economic"
