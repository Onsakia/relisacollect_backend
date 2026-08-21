#!/usr/bin/env python
r"""
EC Carbon Survey - Standalone Database Seeder
================================================
Tailored for your project: backend_collect / collect app

Usage (in PowerShell, with venv activated):
    cd C:\Users\fredo\Documents\ReLISA\Collect\backend_collect
    .\venv\Scripts\Activate.ps1
    python seed_standalone.py
    python seed_standalone.py --plots 100
    python seed_standalone.py --flush
"""
import argparse
import os
import sys
import random
from datetime import datetime, timedelta
from decimal import Decimal

# ── Setup Django ──────────────────────────────────────────────────────────────
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

# YOUR project settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_collect.settings')

import django
django.setup()

from django.contrib.gis.geos import Point

# Import from YOUR app: collect (not survey)
from collect.models import (
    Plot, TreeMeasurement, Transect, SpeciesObservation,
    GrassBiomassSample, SoilSample, WaterAssessment, SocioEconomic,
)

print(f"Django ready. Settings: backend_collect.settings | App: collect")

# ═══════════════════════════════════════════════════════════════
#  SEED DATA POOLS
# ═══════════════════════════════════════════════════════════════

random.seed(42)

PROVINCE_CENTERS = {
    'eastern_cape': (-32.3, 26.4), 'free_state': (-28.5, 27.0),
    'gauteng': (-26.0, 28.0), 'kwazulu_natal': (-29.0, 31.0),
    'limpopo': (-23.5, 30.0), 'mpumalanga': (-25.5, 31.0),
    'northern_cape': (-29.0, 22.0), 'north_west': (-26.5, 26.0),
    'western_cape': (-33.8, 20.0),
}

SITE_NAMES = {
    'eastern_cape': ['Amatola Forest','Addo Park Buffer','Great Fish River',
                     'Stutterheim Indigenous','Baviaanskloof','Grahamstown Plantation'],
    'free_state': ['Golden Gate','Clarens Afrotemperate','Bethlehem Grassland',
                   'Frankfort Savanna','Vrede Thicket','Senekal Woodland'],
    'gauteng': ['Walter Sisulu Botanic','Groenkloof Reserve','Rietvlei Grassland',
                'Suikerbosrand Savanna','Dinokeng Buffer','Cullinan Woodland'],
    'kwazulu_natal': ['Dlinza Forest','Oribi Gorge','Hluhluwe Savanna',
                      'iSimangaliso','Midlands Grassland','Karkloof Indigenous'],
    'limpopo': ['Magoebaskloof','Woodbush','Wolkberg Grassland',
                'Kruger Buffer','Soutpansberg','Polokwane Savanna'],
    'mpumalanga': ["God's Window",'Sabie River','Barberton Grassland',
                   'Kruger Southern','Dullstroom',"Pilgrim's Rest"],
    'northern_cape': ['Nieuwveld','Richtersveld','Augrabies Savanna',
                      'Kalahari Woodland','Namaqualand','Kimberley Grassland'],
    'north_west': ['Magaliesberg','Pilanesberg Buffer','Marikana Grassland',
                   'Rustenburg Savanna','Klerksdorp','Lichtenburg Plantation'],
    'western_cape': ['Knysna Forest','Jonkershoek','Cederberg Wilderness',
                     'Kogelberg','Garden Route','Table Mountain Buffer'],
}

FOREST_TYPES = ['afrotemperate', 'thicket', 'savanna', 'grassland', 'plantation']
FOREST_WEIGHTS = [0.15, 0.25, 0.25, 0.15, 0.20]
ENUMERATORS = ['Thabo Mokoena','Sarah van der Merwe','Lungile Dlamini','Pieter Botha',
               'Nomsa Nkosi','John Peterson','Fatima Abrahams','David Nkosi',
               'Amanda Jacobs','Sipho Zulu','Mary Smith','Jan de Villiers',
               'Grace Molefe','Robert Williams','Beauty Mabunda']
TREE_SPECIES = ['acacia_karroo','acacia_mearnsii','afrocarpus_falcatus','brabejum',
                'celtis_africana','ficus','ilex_mitis','olea_capensis','podocarpus',
                'prunus_africana','virgilia','eucalyptus','sideroxylon_inerme',
                'buddleja_saligna','rapanea_melanophloeos']
GRASS_SPECIES = ['themeda_triandra','andropogon_eucomis','cymbopogon_nardus',
                 'heteropogon_contortus','bewsia_biflora','brachiaria_serrata',
                 'hyparrhenia_hirta','danthonia_rehmii']

# Water module pools
WATER_SOURCES = ['perennial_river','seasonal_river','spring','wetland',
                 'dam_reservoir','farm_dam','groundwater_borehole','ephemeral_pan']
FLOW_REGIMES = ['perennial','intermittent','ephemeral','regulated']
SEASONAL_AVAIL = ['permanent','seasonal_reliable','seasonal_unreliable','drought_prone']
WATER_QUALITY = ['excellent','good','fair','poor','not_tested']
RIPARIAN_COND = ['pristine','good','moderate','degraded','severely_degraded']
STREAM_EROSION = ['none','slight','moderate','severe','very_severe']
WETLAND_TYPES = ['floodplain','depression','channelled_valley','hillslope_seep','pan','none']
WETLAND_COND = ['unmodified','largely_natural','moderately_modified','seriously_modified','none']
EXTRACTION_USES = ['domestic','livestock','irrigation','ecosystem','none_observed']
DOWNSTREAM_IMPACTS = ['none','reduced_flow','sedimentation','pollution','erosion','unknown']

# Socio-economic pools
COMMUNITY_TYPES = ['rural_village','rural_scattered','peri_urban','communal_area','farm_laborer']
TENURE_SECURITY = ['very_secure','secure','moderate','insecure','disputed']
LAND_USE_CURRENT = ['grazing','cropland','fallow','forest_reserve','plantation','conservation','mixed_use']
LIVELIHOOD_POOL = ['livestock','crop_farming','wage_labour','informal_trade','government_grant','tourism','hunting_gathering']
INCOME_SOURCES = ['agriculture','wage_labour','social_grants','remittances','informal_business']
INCOME_LEVELS = ['below_poverty','low','lower_middle','middle','above_middle','unknown']
AWARENESS = ['very_aware','aware','somewhat','not_aware']
SUPPORT = ['very_supportive','supportive','neutral','opposed','very_opposed']
WILLINGNESS = ['yes','no','unsure']
JOB_POTENTIAL = ['1_10','11_50','51_100','100_plus','unknown']
GENDER_BALANCE = ['mostly_men','mostly_women','balanced','women_led','unknown']
FIRE_RISK = ['low','moderate','high','very_high']
RESTORATION_BENEFITS = ['jobs','water_security','grazing','firewood','carbon_payments','biodiversity','climate_adaptation','soil_protection']
CAPACITY_NEEDS = ['nursery_management','planting_techniques','fire_management','monitoring','business_skills','carbon_markets','gis_gps','record_keeping']
CHALLENGES = ['funding','capacity','water_scarcity','grazing_pressure','invasive_species','fire','tenure_insecurity','climate_change']
INVASIVE_THREATS = ['acacia_mearnsii','acacia_dealbata','eucalyptus','pine','lantana','prickly_pear']
INDIGENOUS_PRACTICES = ['controlled_burning','rotational_grazing','seed_harvesting','sacred_groves','herbal_medicine']

# ═══════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════

def random_date(start_year=2023, end_year=2025):
    start, end = datetime(start_year, 1, 1), datetime(end_year, 12, 31)
    return start + timedelta(days=random.randint(0, (end - start).days))

def random_point(lat, lng, spread=1.5):
    return (round(lat + random.uniform(-spread, spread), 6),
            round(lng + random.uniform(-spread, spread), 6))

# ═══════════════════════════════════════════════════════════════
#  CREATE FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def create_plot(province, plot_num):
    center = PROVINCE_CENTERS[province]
    forest_type = random.choices(FOREST_TYPES, weights=FOREST_WEIGHTS)[0]
    site_name = random.choice(SITE_NAMES[province])
    date = random_date()
    lat, lng = random_point(center[0], center[1])
    has_water = random.random() < 0.55
    has_socio = random.random() < 0.60

    plot = Plot.objects.create(
        plot_id=f"P-{province[:2].upper()}-{plot_num:03d}",
        site_name=f"{site_name} - Plot {plot_num}",
        province=province,
        date=date.date(),
        enumerator=random.choice(ENUMERATORS),
        location=Point(lng, lat, srid=4326),
        altitude=Decimal(str(round(random.uniform(200, 1800), 2))),
        gps_accuracy=Decimal(str(round(random.uniform(1.5, 8.5), 2))),
        gps_point_number=plot_num,
        plot_radius=25,
        dist_water_point=random.choice(['less_200m', '200_600m', 'beyond_600m']),
        dist_settlement=random.choice(['less_500m', '500_1500m', 'beyond_1500m']),
        forest_type=forest_type,
        trees_count_est=random.randint(15, 120),
        habitat_condition=random.choice(['pristine', 'good', 'moderate', 'degraded']),
        canopy_cover=random.randint(10, 95),
        carbon_standard=random.choice(['ccb', 'vcs', 'ccb_vcs', 'gold', 'planvivo', 'other']),
        land_tenure=random.choice(['communal', 'private', 'state', 'community', 'pa']),
        community_consult=random.choice(['yes', 'no']),
        module_biomass='yes', module_biodiversity='yes', module_soil='yes',
        module_water='yes' if has_water else 'no',
        module_socioeconomic='yes' if has_socio else 'no',
    )
    return plot, has_water, has_socio

def create_trees(plot, count):
    for i in range(count):
        TreeMeasurement.objects.create(
            plot=plot, tree_id=f"{plot.plot_id}-T{i+1:02d}", tree_num=i + 1,
            gps_waypoint_number=plot.gps_point_number + i + 1,
            species=random.choice(TREE_SPECIES),
            tree_status=random.choice(['live', 'live_damaged', 'dead_standing', 'live']),
            dbh=Decimal(str(round(random.uniform(5.5, 95.5), 2))),
            height=Decimal(str(round(random.uniform(2.0, 35.0), 2))),
            crown_width_n=Decimal(str(round(random.uniform(1.5, 15.0), 2))),
            crown_width_e=Decimal(str(round(random.uniform(1.5, 15.0), 2))),
        )

def create_transects(plot):
    num_transects = random.randint(1, 3)
    for t in range(num_transects):
        transect = Transect.objects.create(
            plot=plot, transect_id=random.choice(['t1', 't2', 'other']), transect_num=t + 1,
        )
        num_obs = random.randint(3, 12)
        base_wp = plot.gps_point_number + plot.trees.count() + t * 20
        for o in range(num_obs):
            SpeciesObservation.objects.create(
                transect=transect, observation_num=o + 1,
                gps_waypoint_number=base_wp + o + 1,
                bio_type=random.choice(['tree', 'herb', 'grass', 'fern', 'animal_sign', 'invasive']),
                species=random.choice(TREE_SPECIES), abundance=random.randint(1, 50),
                threat_status=random.choice(['lc', 'nt', 'vu', 'en', 'invasive', 'other']),
            )
        for g in range(random.randint(2, 8)):
            GrassBiomassSample.objects.create(
                transect=transect, sample_num=g + 1,
                gps_waypoint_number=base_wp + num_obs + g + 1,
                grass_species=random.choice(GRASS_SPECIES),
                grass_weight=Decimal(str(round(random.uniform(50.0, 850.0), 3))),
                last_burned=random.choice(['recent', '1_2_years', '2_5_years', 'more_5_years', 'never']),
            )

def create_soil_samples(plot):
    soil_points = ['p1', 'p2', 'p3', 'p4', 'p5']
    base_wp = plot.gps_point_number + plot.trees.count() + 100
    for i, point_id in enumerate(soil_points):
        SoilSample.objects.create(
            plot=plot, point_id=point_id, point_num=i + 1,
            gps_waypoint_number=base_wp + i,
            depth_class=random.choice(['topsoil', 'subsoil', 'deep', 'custom']),
            depth_cm=Decimal(str(round(random.uniform(5.0, 50.0), 2))),
            soil_texture=random.choice(['sand', 'loam', 'clay', 'sandy_loam', 'clay_loam', 'silt']),
            bulk_density=Decimal(str(round(random.uniform(0.8, 1.6), 3))),
            soil_ph=Decimal(str(round(random.uniform(4.5, 8.5), 2))),
        )

def create_water_assessment(plot):
    WaterAssessment.objects.create(
        plot=plot, water_source_type=random.choice(WATER_SOURCES),
        water_source_name=f"{plot.site_name.split(' - ')[0]} Water Source",
        water_source_gps=Point(plot.location.x + random.uniform(-0.05, 0.05),
                               plot.location.y + random.uniform(-0.05, 0.05), srid=4326),
        flow_regime=random.choice(FLOW_REGIMES),
        seasonal_availability=random.choice(SEASONAL_AVAIL),
        water_ph=Decimal(str(round(random.uniform(5.5, 9.0), 2))),
        water_temperature=Decimal(str(round(random.uniform(12.0, 28.0), 2))),
        water_turbidity_ntu=Decimal(str(round(random.uniform(0.5, 45.0), 2))),
        electrical_conductivity=Decimal(str(round(random.uniform(50.0, 800.0), 2))),
        water_quality_category=random.choice(WATER_QUALITY),
        riparian_veg_condition=random.choice(RIPARIAN_COND),
        stream_bank_erosion=random.choice(STREAM_EROSION),
        wetland_type=random.choice(WETLAND_TYPES),
        wetland_condition=random.choice(WETLAND_COND),
        wetland_width_m=random.randint(5, 200) if random.random() > 0.3 else None,
        water_extraction_uses=','.join(random.sample(EXTRACTION_USES, k=random.randint(1, 3))),
        downstream_impacts=random.choice(DOWNSTREAM_IMPACTS),
        water_notes=f"Water assessment on {plot.date}.",
    )

def create_socioeconomic(plot):
    def join_list(pool, k):
        return ','.join(random.sample(pool, k=min(k, len(pool))))
    SocioEconomic.objects.create(
        plot=plot, community_type=random.choice(COMMUNITY_TYPES),
        households_nearby=random.randint(5, 500),
        population_estimate=random.randint(20, 2500),
        tenure_security=random.choice(TENURE_SECURITY),
        land_use_current=random.choice(LAND_USE_CURRENT),
        land_use_history=join_list(['grazing','cropland','plantation','indigenous_forest','fire'], random.randint(1, 3)),
        livelihood_activities=join_list(LIVELIHOOD_POOL, random.randint(2, 5)),
        primary_income_source=random.choice(INCOME_SOURCES),
        household_income_level=random.choice(INCOME_LEVELS),
        community_restoration_awareness=random.choice(AWARENESS),
        restoration_support=random.choice(SUPPORT),
        expected_restoration_benefits=join_list(RESTORATION_BENEFITS, random.randint(2, 5)),
        willingness_to_participate=random.choice(WILLINGNESS),
        traditional_leadership_involved=random.choice(['yes', 'no']),
        indigenous_practices_present=random.choice(['yes', 'no']),
        indigenous_practices_types=join_list(INDIGENOUS_PRACTICES, random.randint(1, 3)) if random.random() > 0.4 else '',
        traditional_knowledge_notes=f"Community has {random.choice(['strong','moderate','limited'])} traditional ecological knowledge.",
        capacity_building_needs=join_list(CAPACITY_NEEDS, random.randint(2, 5)),
        job_creation_potential=random.choice(JOB_POTENTIAL),
        gender_balance_participation=random.choice(GENDER_BALANCE),
        restoration_challenges=join_list(CHALLENGES, random.randint(2, 5)),
        fire_risk_level=random.choice(FIRE_RISK),
        invasive_species_threats=join_list(INVASIVE_THREATS, random.randint(1, 4)),
        socioeconomic_notes=f"Assessment for {plot.site_name}.",
    )

# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description='Seed EC Carbon Survey database')
    parser.add_argument('--plots', type=int, default=50, help='Number of plots')
    parser.add_argument('--flush', action='store_true', help='Delete existing data first')
    args = parser.parse_args()

    print("=" * 60)
    print("EC Carbon Survey - Database Seeder")
    print("=" * 60)

    if args.flush:
        print("\n[1/6] Deleting existing data...")
        SocioEconomic.objects.all().delete()
        WaterAssessment.objects.all().delete()
        GrassBiomassSample.objects.all().delete()
        SpeciesObservation.objects.all().delete()
        Transect.objects.all().delete()
        SoilSample.objects.all().delete()
        TreeMeasurement.objects.all().delete()
        Plot.objects.all().delete()
        print("      All existing data deleted.")

    print(f"\n[2/6] Creating {args.plots} plots...")

    created = water_count = socio_count = 0
    for i in range(args.plots):
        province = list(PROVINCE_CENTERS.keys())[i % 9]
        plot_num = i + 1
        plot, has_water, has_socio = create_plot(province, plot_num)
        create_trees(plot, random.randint(5, 25))
        create_transects(plot)
        create_soil_samples(plot)
        if has_water:
            create_water_assessment(plot); water_count += 1
        if has_socio:
            create_socioeconomic(plot); socio_count += 1
        created += 1
        if created % 10 == 0:
            print(f"      {created}/{args.plots} plots created...")

    print("\n" + "=" * 60)
    print("SEED COMPLETE")
    print("=" * 60)
    print(f"  Plots:              {Plot.objects.count()}")
    print(f"  Trees:              {TreeMeasurement.objects.count()}")
    print(f"  Transects:          {Transect.objects.count()}")
    print(f"  Species obs:        {SpeciesObservation.objects.count()}")
    print(f"  Grass samples:      {GrassBiomassSample.objects.count()}")
    print(f"  Soil samples:       {SoilSample.objects.count()}")
    print(f"  Water assessments:  {WaterAssessment.objects.count()}")
    print(f"  Socio-economic:     {SocioEconomic.objects.count()}")
    print("=" * 60)

if __name__ == '__main__':
    main()
