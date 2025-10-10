from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from users.models import User
from organization.models import Application


class Command(BaseCommand):
    help = 'Update profile scores for all users based on their application history'

    def handle(self, *args, **options):
        self.stdout.write('Starting profile score update...')
        
        # Get all applicant users
        applicants = User.objects.filter(user_type=User.UserType.APPLICANT)
        
        for user in applicants:
            # Count achievements from application history
            applications = Application.objects.filter(applicant=user)
            
            shortlisted_count = applications.filter(status='SL').count()
            selected_count = applications.filter(status='SE').count()
            hired_count = applications.filter(status='HD').count()
            
            # Also count those who were shortlisted/selected but later hired
            # (they should get credit for all achievements)
            all_shortlisted = applications.filter(
                status__in=['SL', 'SE', 'HD']  # Anyone who reached shortlist or beyond
            ).count()
            
            all_selected = applications.filter(
                status__in=['SE', 'HD']  # Anyone who reached selection or beyond
            ).count()
            
            # Update user counts (use the higher counts for maximum benefit)
            user.shortlisted_count = max(shortlisted_count, all_shortlisted)
            user.selected_count = max(selected_count, all_selected)
            user.hired_count = hired_count
            
            # Calculate and update profile score
            user.update_profile_score()
            
            self.stdout.write(
                f'Updated {user.username}: '
                f'shortlisted={user.shortlisted_count}, '
                f'selected={user.selected_count}, '
                f'hired={user.hired_count}, '
                f'score={user.profile_score}'
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated profile scores for {applicants.count()} users'
            )
        )