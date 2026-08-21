"""
Management command to import mock plot data into the database.
Usage: python manage.py import_mock
"""
import json
import os
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from survey.models import (
    Plot, TreeMeasurement, Transect, SpeciesObservation,
    GrassBiomassSample, SoilSample
)


class Command(BaseCommand):
    help = 'Import mock plot data from JSON'

    def handle(self, *args, **options):
        # Path to mock data
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        json_path = os.path.join(base_dir, '..', '..', 'app', 'src', 'data', 'plots.json')

        if not os.path.exists(json_path):
            self.stderr.write(f"Mock data not found at {json_path}")
            return

        with open(json_path, 'r') as f:
            plots_data = json.load(f)

        created_count = 0

        for plot_data in plots_data:
            plot, created = Plot.objects.get_or_create(
                plot_id=plot_data['id'],
                defaults={
                    'site_name': plot_data['site_name'],
                    'province': plot_data['province'],
                    'date': plot_data['date'],
                    'enumerator': plot_data['enumerator'],
                    'location': Point(plot_data['longitude'], plot_data['latitude'], srid=4326),
                    'altitude': plot_data.get('altitude'),
                    'gps_accuracy': plot_data.get('gps_accuracy'),
                    'plot_radius': plot_data.get('plot_radius', 25),
                    'dist_water_point': plot_data.get('dist_water_point', ''),
                    'dist_settlement': plot_data.get('dist_settlement', ''),
                    'forest_type': plot_data.get('forest_type', 'grassland'),
                    'trees_count_est': plot_data.get('trees_count_est'),
                    'habitat_condition': plot_data.get('habitat_condition', ''),
                    'canopy_cover': plot_data.get('canopy_cover'),
                    'carbon_standard': plot_data.get('carbon_standard', ''),
                    'land_tenure': plot_data.get('land_tenure', ''),
                    'community_consult': plot_data.get('community_consult', ''),
                }
            )

            if created:
                created_count += 1
                self.stdout.write(f"Created plot: {plot.plot_id}")

                # Create trees
                for tree_data in plot_data.get('trees', []):
                    TreeMeasurement.objects.create(
                        plot=plot,
                        tree_id=tree_data['tree_id'],
                        tree_num=tree_data['tree_num'],
                        species=tree_data['species'],
                        tree_status=tree_data.get('status', 'live'),
                        dbh=tree_data['dbh'],
                        height=tree_data['height'],
                        crown_width_n=tree_data.get('crown_width_n'),
                        crown_width_e=tree_data.get('crown_width_e'),
                    )

                # Create transects with species and grass samples
                for transect_data in plot_data.get('transects', []):
                    transect = Transect.objects.create(
                        plot=plot,
                        transect_id=transect_data['transect_id'],
                        transect_num=transect_data['transect_num'],
                    )

                    for obs_data in transect_data.get('species_observations', []):
                        SpeciesObservation.objects.create(
                            transect=transect,
                            bio_type=obs_data['bio_type'],
                            species=obs_data['species'],
                            abundance=obs_data['abundance'],
                            threat_status=obs_data.get('threat_status', ''),
                        )

                    for grass_data in transect_data.get('grass_samples', []):
                        GrassBiomassSample.objects.create(
                            transect=transect,
                            sample_num=grass_data['sample_num'],
                            grass_species=grass_data['species'],
                            grass_weight=grass_data['weight'],
                            last_burned=grass_data.get('last_burned', ''),
                        )

                # Create soil samples
                for soil_data in plot_data.get('soil_samples', []):
                    SoilSample.objects.create(
                        plot=plot,
                        point_id=soil_data['point_id'],
                        point_num=soil_data['point_num'],
                        depth_class=soil_data['depth_class'],
                        depth_cm=soil_data['depth_cm'],
                        soil_texture=soil_data['texture'],
                        bulk_density=soil_data.get('bulk_density'),
                        soil_ph=soil_data.get('ph'),
                    )

        self.stdout.write(
            self.style.SUCCESS(f"Successfully imported {created_count} plots")
        )
