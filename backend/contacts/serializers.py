from rest_framework import serializers
from .models import Contact

class ContactSerializer(serializers.ModelSerializer):
    # Map 'full_name' from import script to 'name' model field if needed, 
    # but strictly script sends 'full_name'.
    # I should add full_name as a read_only field or alias it to name?
    # Better to alias name to full_name for compatibility.
    
    full_name = serializers.CharField(source='name', required=False)

    class Meta:
        model = Contact
        fields = '__all__'
        extra_kwargs = {'name': {'required': False}} # Allow name to be inferred from full_name
    
    def validate(self, attrs):
        # Handle the script sending 'full_name' but model expecting 'name'
        # The source='name' on Read field handles GET, but for POST we need to ensure 'name' is populated.
        # Actually, DRF with source='name' on a writable field handles both directions usually.
        # Let's verify: script sends {"full_name": "...", "email": "..."}
        # If I define full_name = CharField(source='name'), input "full_name" will map to "name".
        return attrs
