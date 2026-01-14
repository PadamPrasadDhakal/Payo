from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import User


class Command(BaseCommand):
    help = 'Set all applicant users tokens to 7 immediately'

    def handle(self, *args, **options):
        current_time = timezone.now()
        
        # Get all applicant users
        applicants = User.objects.filter(user_type=User.UserType.APPLICANT)
        total_applicants = applicants.count()
        
        # Update all applicant users
        updated_count = applicants.update(
            tokens_left=7,
            tokens_restored_flag=True,
            last_token_reset=current_time
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully set tokens to 7 for {updated_count} out of {total_applicants} applicant users'
            )
        )
        
        # Show statistics
        self.stdout.write(self.style.WARNING('\nToken Statistics:'))
        users_with_7 = User.objects.filter(user_type=User.UserType.APPLICANT, tokens_left=7).count()
        self.stdout.write(f'  - Applicants with 7 tokens: {users_with_7}')
        self.stdout.write(f'  - Total applicants: {total_applicants}')
