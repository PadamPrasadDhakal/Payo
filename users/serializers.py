from rest_framework import serializers
from .models import IndividualKYC, OrganizationKYC, KycAudit
from django.contrib.auth import get_user_model

User = get_user_model()


class IndividualKYCSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndividualKYC
        fields = [
            'id', 'user', 'full_name', 'date_of_birth', 'gender', 'marital_status', 'nationality',
            'occupation', 'income_source', 'education_level', 'contact_mobile', 'contact_landline',
            'permanent_address_province', 'permanent_address_district', 'permanent_address_municipality',
            'permanent_address_ward', 'temporary_address', 'citizenship_number', 'citizenship_issue_date',
            'citizenship_issue_district', 'passport_number', 'driving_license_number', 'father_name',
            'mother_name', 'grandfather_name', 'spouse_name', 'purpose_of_account',
            'expected_monthly_transaction_range', 'expected_annual_income_range', 'is_pep', 'fatca_declaration',
            'status', 'current_step', 'submitted_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'status', 'submitted_at', 'updated_at']


class OrganizationKYCSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationKYC
        fields = [
            'id', 'user', 'org_name', 'registration_number', 'registration_date', 'registered_office_address',
            'current_operating_address', 'org_type', 'nature_of_business', 'contact_number', 'contact_email',
            'website', 'authorized_signatories', 'major_shareholders', 'purpose_of_account',
            'expected_monthly_transactions', 'source_of_funds', 'fatca_declaration', 'is_pep',
            'status', 'current_step', 'submitted_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'status', 'submitted_at', 'updated_at']


class KycAuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = KycAudit
        fields = ['id', 'kyc_type', 'kyc_id', 'actor', 'action', 'message', 'created_at']
        read_only_fields = fields
