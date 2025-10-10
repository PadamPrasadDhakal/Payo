from django.core.management.base import BaseCommand
from users.models import User


class Command(BaseCommand):
    help = 'Display current user token status'

    def handle(self, *args, **options):
        users = User.objects.all()
        
        if not users.exists():
            self.stdout.write(self.style.WARNING('No users found in the database'))
            return
        
        self.stdout.write(f'Found {users.count()} users:')
        self.stdout.write('-' * 50)
        
        for user in users:
            self.stdout.write(
                f'Username: {user.username} | '
                f'Tokens: {user.tokens_left} | '
                f'Type: {user.get_user_type_display()} | '
                f'Last Reset: {user.last_token_reset}'
            )
        
        # Summary
        token_counts = {}
        for user in users:
            tokens = user.tokens_left
            token_counts[tokens] = token_counts.get(tokens, 0) + 1
        
        self.stdout.write('\nToken Distribution:')
        for tokens, count in sorted(token_counts.items()):
            self.stdout.write(f'  {count} users with {tokens} tokens')