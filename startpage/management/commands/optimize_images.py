from django.core.management.base import BaseCommand

from startpage.image_utils import optimize_image_field
from startpage.models import Article, Event


class Command(BaseCommand):
    help = 'Resize and convert existing article/event images to WebP.'

    def handle(self, *args, **options):
        count = 0
        for model, fields in ((Article, ('featured_image', 'top_image')), (Event, ('featured_image',))):
            for obj in model.objects.all():
                for name in fields:
                    ff = getattr(obj, name)
                    if ff and not ff.name.endswith('.webp'):
                        ff.open()
                        ff._committed = False
                        optimize_image_field(ff)
                        count += 1
                obj.save()
        self.stdout.write(self.style.SUCCESS(f'Optimized {count} images'))
