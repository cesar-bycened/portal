from rest_framework import serializers
from .models import *

class ProgramaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramaEducativo
        fields = '__all__'





