from rest_framework import serializers
from .models import AudioRecord

class AudioRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioRecord
        fields = ['id', 'source', 'edit_source', 'sentiment_analysis', 'rating', 'audio_file']
