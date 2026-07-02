"""
Management command to seed 53 subscriptions spread unevenly across the last 5 days,
covering all 5 apps (Campus Eats, Reconna, LifeRack, ChristNotes, BuyerKraze).

Usage:
    python manage.py seed_subscriptions
    python manage.py seed_subscriptions --force  (to delete existing data first)
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from subscriptions.models import App, AccessKey, Subscription
import secrets
from decimal import Decimal


# ─── App Definitions ─────────────────────────────────────────────

APPS = [
    {
        'name': 'Campus Eats',
        'code': 'campuseats',
        'description': 'Campus food delivery and ordering platform',
        'tiers': [
            {'name': 'Basic', 'prefix': 'ce_basic_', 'price': Decimal('0.00'), 'duration': 30,
             'desc': 'Free tier with standard delivery', 'reqs': 50, 'sessions': 1},
            {'name': 'Premium', 'prefix': 'ce_prem_', 'price': Decimal('9.99'), 'duration': 30,
             'desc': 'Priority delivery and exclusive deals', 'reqs': 200, 'sessions': 3},
            {'name': 'Enterprise', 'prefix': 'ce_ent_', 'price': Decimal('29.99'), 'duration': 30,
             'desc': 'Unlimited orders and partner perks', 'reqs': 1000, 'sessions': 10},
        ],
    },
    {
        'name': 'Reconna',
        'code': 'reconna',
        'description': 'AI-powered reconnaissance and data analysis tool',
        'tiers': [
            {'name': 'Basic', 'prefix': 're_basic_', 'price': Decimal('0.00'), 'duration': 30,
             'desc': 'Limited daily scans', 'reqs': 30, 'sessions': 1},
            {'name': 'Pro', 'prefix': 're_pro_', 'price': Decimal('14.99'), 'duration': 30,
             'desc': 'Advanced analytics and reports', 'reqs': 300, 'sessions': 5},
            {'name': 'Enterprise', 'prefix': 're_ent_', 'price': Decimal('49.99'), 'duration': 30,
             'desc': 'Full API access and dedicated support', 'reqs': 5000, 'sessions': 20},
        ],
    },
    {
        'name': 'LifeRack',
        'code': 'liferack',
        'description': 'Productivity and life management application',
        'tiers': [
            {'name': 'Free', 'prefix': 'lr_free_', 'price': Decimal('0.00'), 'duration': 30,
             'desc': 'Basic task management', 'reqs': 100, 'sessions': 1},
            {'name': 'Premium', 'prefix': 'lr_prem_', 'price': Decimal('7.99'), 'duration': 30,
             'desc': 'Advanced features and integrations', 'reqs': 500, 'sessions': 5},
        ],
    },
    {
        'name': 'ChristNotes',
        'code': 'christnotes',
        'description': 'Bible study and devotional note-taking platform',
        'tiers': [
            {'name': 'Free', 'prefix': 'cn_free_', 'price': Decimal('0.00'), 'duration': 30,
             'desc': 'Basic note-taking and reading plans', 'reqs': 100, 'sessions': 2},
            {'name': 'Premium', 'prefix': 'cn_prem_', 'price': Decimal('4.99'), 'duration': 30,
             'desc': 'Unlimited notes, audio Bibles, and commentary', 'reqs': 500, 'sessions': 10},
        ],
    },
    {
        'name': 'BuyerKraze',
        'code': 'buyerkraze',
        'description': 'E-commerce and shopping deal aggregator',
        'tiers': [
            {'name': 'Basic', 'prefix': 'bk_basic_', 'price': Decimal('0.00'), 'duration': 30,
             'desc': 'Standard deal alerts', 'reqs': 100, 'sessions': 1},
            {'name': 'Premium', 'prefix': 'bk_prem_', 'price': Decimal('19.99'), 'duration': 30,
             'desc': 'Early access and price drop alerts', 'reqs': 500, 'sessions': 5},
            {'name': 'Enterprise', 'prefix': 'bk_ent_', 'price': Decimal('99.99'), 'duration': 30,
             'desc': 'Bulk purchase API and wholesale access', 'reqs': 5000, 'sessions': 25},
        ],
    },
]

# ─── Subscription Distribution ──────────────────────────────────
# 53 subs spread unevenly across 5 days (day 0 = today)
# Format: (days_ago, count)

DISTRIBUTION = [
    (0, 15),
    (1, 12),
    (2, 10),
    (3, 8),
    (4, 5),
    (5, 3),
]

# Names and emails for realistic seed data
SUBSCRIBERS = [
    ("Alice Johnson", "alice.johnson@email.com"),
    ("Bob Smith", "bob.smith@email.com"),
    ("Charlie Brown", "charlie.brown@email.com"),
    ("Diana Prince", "diana.prince@email.com"),
    ("Edward Norton", "edward.norton@email.com"),
    ("Fiona Apple", "fiona.apple@email.com"),
    ("George Lucas", "george.lucas@email.com"),
    ("Hannah Montana", "hannah.montana@email.com"),
    ("Ivan Petrov", "ivan.petrov@email.com"),
    ("Julia Roberts", "julia.roberts@email.com"),
    ("Kevin Hart", "kevin.hart@email.com"),
    ("Laura Croft", "laura.croft@email.com"),
    ("Mike Ross", "mike.ross@email.com"),
    ("Nancy Drew", "nancy.drew@email.com"),
    ("Oscar Wilde", "oscar.wilde@email.com"),
    ("Patricia Kane", "patricia.kane@email.com"),
    ("Quinn Fabray", "quinn.fabray@email.com"),
    ("Rachel Green", "rachel.green@email.com"),
    ("Steve Rogers", "steve.rogers@email.com"),
    ("Tina Fey", "tina.fey@email.com"),
    ("Uma Thurman", "uma.thurman@email.com"),
    ("Victor Creed", "victor.creed@email.com"),
    ("Wendy Darling", "wendy.darling@email.com"),
    ("Xander Cage", "xander.cage@email.com"),
    ("Yara Shahidi", "yara.shahidi@email.com"),
    ("Zack Morris", "zack.morris@email.com"),
    ("Amy Pond", "amy.pond@email.com"),
    ("Bruce Wayne", "bruce.wayne@email.com"),
    ("Clara Oswald", "clara.oswald@email.com"),
    ("Don Draper", "don.draper@email.com"),
    ("Eve Polastri", "eve.polastri@email.com"),
    ("Frank Castle", "frank.castle@email.com"),
    ("Gina Linetti", "gina.linetti@email.com"),
    ("Homer Simpson", "homer.simpson@email.com"),
    ("Iris West", "iris.west@email.com"),
    ("Jake Peralta", "jake.peralta@email.com"),
    ("Katniss Everdeen", "katniss.everdeen@email.com"),
    ("Loki Laufeyson", "loki.laufeyson@email.com"),
    ("Molly Weasley", "molly.weasley@email.com"),
    ("Neo Anderson", "neo.anderson@email.com"),
    ("Olive Penderghast", "olive.penderghast@email.com"),
    ("Peter Parker", "peter.parker@email.com"),
    ("Queen Latifah", "queen.latifah@email.com"),
    ("Randy Marsh", "randy.marsh@email.com"),
    ("Samantha Jones", "samantha.jones@email.com"),
    ("Tony Stark", "tony.stark@email.com"),
    ("Ursula Buffay", "ursula.buffay@email.com"),
    ("Vito Corleone", "vito.corleone@email.com"),
    ("Walter White", "walter.white@email.com"),
    ("Xena Warrior", "xena.warrior@email.com"),
    ("Yondu Udonta", "yondu.udonta@email.com"),
    ("Zoe Washburne", "zoe.washburne@email.com"),
    ("Arthur Curry", "arthur.curry@email.com"),
]


class Command(BaseCommand):
    help = 'Seed 53 subscriptions across 5 apps spread over the last 5 days'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Delete existing apps, tiers, and subscriptions before seeding',
        )

    def handle(self, *args, **options):
        force = options.get('force')

        if force:
            self.stdout.write(self.style.WARNING('Deleting existing data...'))
            Subscription.objects.all().delete()
            AccessKey.objects.all().delete()
            App.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing data deleted.'))

        # Check if already seeded
        if App.objects.exists():
            self.stdout.write(self.style.WARNING(
                'Apps already exist. Use --force to re-seed from scratch.'
            ))
            return

        now = timezone.now()
        tier_map = {}  # (app_code, tier_name) -> AccessKey instance

        with transaction.atomic():
            # ── Create apps and tiers ──
            for app_data in APPS:
                app = App.objects.create(
                    name=app_data['name'],
                    code=app_data['code'],
                    description=app_data['description'],
                    is_active=True,
                )
                self.stdout.write(f"  Created app: {app.name}")

                for tier_data in app_data['tiers']:
                    tier = AccessKey.objects.create(
                        app=app,
                        name=tier_data['name'],
                        key_prefix=tier_data['prefix'],
                        description=tier_data['desc'],
                        price=tier_data['price'],
                        duration_days=tier_data['duration'],
                        max_requests_per_day=tier_data['reqs'],
                        max_concurrent_sessions=tier_data['sessions'],
                        is_active=True,
                    )
                    tier_map[(app_data['code'], tier_data['name'])] = tier
                    self.stdout.write(f"    Tier: {tier.name} (${tier.price})")

            # ── Collect all available tier combinations ──
            all_tiers = list(tier_map.values())

            # ── Create 53 subscriptions ──
            sub_index = 0
            created_count = 0

            for days_ago, count in DISTRIBUTION:
                created_date = now - timedelta(days=days_ago)
                # Spread subscriptions within that day (different hours/minutes)
                for i in range(count):
                    if sub_index >= len(SUBSCRIBERS):
                        break

                    name, email = SUBSCRIBERS[sub_index]
                    # Pick a random tier (weighted toward paid tiers for variety)
                    tier = all_tiers[sub_index % len(all_tiers)]

                    # Random offset within the day (0-23 hours, 0-59 mins)
                    hour_offset = i % 24
                    minute_offset = (i * 17) % 60
                    sub_created = created_date.replace(
                        hour=hour_offset,
                        minute=minute_offset,
                        second=(i * 3) % 60,
                        microsecond=0,
                    )

                    # Start date = created date (some subs started in the past)
                    start_date = sub_created

                    # Status: mostly active, some expired/cancelled for realism
                    if days_ago >= 4 and i % 7 == 0:
                        status = 'expired'
                    elif days_ago >= 3 and i % 5 == 0:
                        status = 'cancelled'
                    elif i % 13 == 0:
                        status = 'pending'
                    else:
                        status = 'active'

                    # End date depends on status and tier duration
                    if status == 'expired':
                        end_date = start_date + timedelta(days=tier.duration_days)
                        # Make sure end_date is in the past for old subs
                        if end_date > now:
                            end_date = start_date + timedelta(days=min(tier.duration_days, days_ago))
                    elif status == 'cancelled':
                        # Cancelled after a portion of the duration
                        portion = max(1, tier.duration_days // 3)
                        end_date = start_date + timedelta(days=portion)
                    else:
                        end_date = start_date + timedelta(days=tier.duration_days)

                    sub = Subscription.objects.create(
                        app=tier.app,
                        access_key=tier,
                        user_name=name,
                        user_email=email,
                        start_date=start_date,
                        end_date=end_date,
                        status=status,
                        notes=f"Seeded subscription for {tier.app.name} - {tier.name}",
                    )
                    # Override created_at since auto_now_add can't be set directly
                    Subscription.objects.filter(pk=sub.pk).update(created_at=sub_created)

                    created_count += 1
                    if created_count % 10 == 0:
                        self.stdout.write(f"  Created {created_count} subscriptions...")

                    sub_index += 1

            self.stdout.write(self.style.SUCCESS(
                f"\n✓ Seeded {created_count} subscriptions across {len(APPS)} apps "
                f"and {len(all_tiers)} tiers, spanning the last {DISTRIBUTION[-1][0]} days."
            ))
            self.stdout.write(f"  Apps: {', '.join(a['name'] for a in APPS)}")
