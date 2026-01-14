from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import User


class Command(BaseCommand):
    help = 'Reset daily application tokens for all applicant users to 7'

    def handle(self, *args, **options):
        current_time = timezone.now()
        
        # Update only applicant users
        updated_count = User.objects.filter(
            user_type=User.UserType.APPLICANT
        ).update(
            tokens_left=7,
            tokens_restored_flag=True,
            last_token_reset=current_time
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully reset tokens for {updated_count} applicant users to 7 at {current_time}'
            )
        )
