import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.load_csv('ingredients.csv', Ingredient)

    def load_csv(self, csv_file, model):
        csv_file_path = Path(settings.BASE_DIR) / 'data' / csv_file
        with open(csv_file_path, 'r', encoding='utf-8') as data_csv_file:
            reader = csv.DictReader(data_csv_file)
            for row in reader:
                model.objects.create(**row)
            self.stdout.write(
                self.style.SUCCESS(
                    'Данные успешно загружены из файла '
                    f'{csv_file} в модель {model.__name__}'
                )
            )
