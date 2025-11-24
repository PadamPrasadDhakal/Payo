from django.contrib import admin
from .models import Payment
from django.utils import timezone

# Job and Application models are registered in jobs/admin.py with custom admin classes
# This avoids duplicate registration errors


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'organization', 'plan', 'amount', 'payment_method', 'status_badge', 'premium_status_badge', 'created_at', 'premium_approved_at')
    list_filter = ('status', 'premium_status', 'plan', 'payment_method', 'created_at')
    search_fields = ('organization__username', 'organization__email', 'transaction_id')
    readonly_fields = ('transaction_id', 'created_at', 'updated_at', 'paid_at', 'premium_approved_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('organization', 'plan', 'amount', 'payment_method', 'transaction_id')
        }),
        ('Payment Status', {
            'fields': ('status', 'created_at', 'updated_at', 'paid_at'),
            'classes': ('collapse',),
        }),
        ('Premium Status', {
            'fields': ('premium_status', 'premium_approved_at'),
            'classes': ('collapse',),
        }),
        ('Subscription Dates', {
            'fields': ('subscription_start', 'subscription_end'),
            'classes': ('collapse',),
        }),
    )
    
    actions = ['verify_payment', 'approve_premium', 'reject_premium', 'mark_completed', 'mark_failed']
    
    def status_badge(self, obj):
        """Display payment status with color coding"""
        colors = {
            'completed': '#10b981',
            'pending': '#f59e0b',
            'failed': '#ef4444',
            'cancelled': '#6b7280',
        }
        color = colors.get(obj.status, '#6b7280')
        return f'<span style="background-color: {color}; color: white; padding: 3px 10px; border-radius: 4px; font-weight: bold;">{obj.get_status_display()}</span>'
    status_badge.short_description = 'Payment Status'
    status_badge.allow_tags = True
    
    def premium_status_badge(self, obj):
        """Display premium status with color coding"""
        colors = {
            'approved': '#10b981',
            'pending': '#f59e0b',
            'rejected': '#ef4444',
        }
        color = colors.get(obj.premium_status, '#6b7280')
        return f'<span style="background-color: {color}; color: white; padding: 3px 10px; border-radius: 4px; font-weight: bold; font-size: 11px;">⭐ {obj.get_premium_status_display()}</span>'
    premium_status_badge.short_description = 'Premium Status'
    premium_status_badge.allow_tags = True
    
    def verify_payment(self, request, queryset):
        """Verify/Mark payment as verified (status = completed)"""
        updated = queryset.exclude(status='completed').update(status='completed', paid_at=timezone.now())
        self.message_user(request, f'✓ {updated} payment(s) marked as completed/verified.')
    verify_payment.short_description = '✓ Verify Payment (Mark as Completed)'
    
    def approve_premium(self, request, queryset):
        """Approve pending premium requests"""
        updated = 0
        for payment in queryset.filter(premium_status='pending'):
            payment.premium_status = 'approved'
            payment.premium_approved_at = timezone.now()
            payment.save()
            updated += 1
        
        self.message_user(request, f'✓ {updated} payment(s) marked as premium approved.')
    approve_premium.short_description = '⭐ Approve Premium'
    
    def reject_premium(self, request, queryset):
        """Reject pending premium requests"""
        updated = 0
        for payment in queryset.filter(premium_status='pending'):
            payment.premium_status = 'rejected'
            payment.save()
            updated += 1
        
        self.message_user(request, f'✗ {updated} payment(s) marked as premium rejected.')
    reject_premium.short_description = '✗ Reject Premium'
    
    def mark_completed(self, request, queryset):
        """Mark payment status as completed"""
        updated = queryset.update(status='completed', paid_at=timezone.now())
        self.message_user(request, f'{updated} payment(s) marked as completed.')
    mark_completed.short_description = 'Mark as Completed'
    
    def mark_failed(self, request, queryset):
        """Mark payment as failed"""
        updated = queryset.update(status='failed')
        self.message_user(request, f'{updated} payment(s) marked as failed.')
    mark_failed.short_description = 'Mark as Failed'
    
    def get_queryset(self, request):
        """Filter to show pending premium requests at the top"""
        qs = super().get_queryset(request)
        # Orders by premium_status (pending first) and then by created_at
        return qs.order_by('-premium_status', '-created_at')