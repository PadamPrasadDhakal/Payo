from django.core.management.base import BaseCommand
from django.utils import timezone
import pytz
from users.models import User


class Command(BaseCommand):
    help = 'Reset daily application tokens for all users'

    def handle(self, *args, **options):
        nepal_tz = pytz.timezone('Asia/Kathmandu')
        current_time = timezone.now().astimezone(nepal_tz)
        
        # Update all users
        updated_count = User.objects.update(
            tokens_left=7,
            tokens_restored_flag=True,
            last_token_reset=current_time
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully reset tokens for {updated_count} users at {current_time}')
        )