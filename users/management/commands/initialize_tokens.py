from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import User


class Command(BaseCommand):
    help = 'Initialize tokens for existing users who have 0 tokens'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force reset all users to 7 tokens',
        )

    def handle(self, *args, **options):
        force = options['force']
        
        if force:
            # Reset all users to 7 tokens
            users_updated = User.objects.all().update(
                tokens_left=7,
                last_token_reset=timezone.now(),
                tokens_restored_flag=False
            )
            self.stdout.write(
                self.style.SUCCESS(f'Successfully reset tokens for {users_updated} users')
            )
        else:
            # Only update users with 0 tokens
            users_to_update = User.objects.filter(tokens_left=0)
            count = users_to_update.count()
            
            if count > 0:
                users_to_update.update(
                    tokens_left=7,
                    last_token_reset=timezone.now(),
                    tokens_restored_flag=False
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully initialized tokens for {count} users with 0 tokens')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('No users found with 0 tokens')
                )
        
        # Show current token status
        token_stats = User.objects.values_list('tokens_left', flat=True)
        self.stdout.write(f'Current token distribution:')
        for tokens in set(token_stats):
            count = list(token_stats).count(tokens)
            self.stdout.write(f'  {count} users with {tokens} tokens')