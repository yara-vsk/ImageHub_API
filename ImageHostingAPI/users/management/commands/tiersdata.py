from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from users.models import Tier, Thumbnail



class Command(BaseCommand):
    help = 'tiersdata'

    def add_arguments(self, parser):
        parser.add_argument('Create all tiers', type=str)

    def handle(self, *args, **options):
        if options['Create all tiers']=='all':
            thumbnail_200 = Thumbnail.objects.create(size=200)
            thumbnail_400 = Thumbnail.objects.create(size=400)
            tier_bas = Tier.objects.create(name='Basic', link_originally_image=False, expiring_links=False)
            tier_prem = Tier.objects.create(name='Premium', link_originally_image=True, expiring_links=False)
            tier_ent=Tier.objects.create(name='Enterprise', link_originally_image=True, expiring_links=True)
            tier_bas.thumbnail_sizes.add(thumbnail_200)
            tier_prem.thumbnail_sizes.add(thumbnail_200,thumbnail_400)
            tier_ent.thumbnail_sizes.add(thumbnail_200,thumbnail_400)
            tier_bas.save()
            tier_prem.save()
            tier_ent.save()
            get_user_model().objects.create_superuser(username='test',tier=tier_ent,password='test', email='test@test.test')
            return
        else:
            raise CommandError('Enter as argument "all".')

