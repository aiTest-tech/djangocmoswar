from django.db import models

class AudioRecord(models.Model):
    source = models.TextField()  # For storing the transcribed text
    edit_source = models.TextField(null=True, blank=True)  # For storing edited text
    sentiment_analysis = models.FloatField(null=True, blank=True)  # For storing sentiment score
    rating = models.IntegerField(null=True, blank=True)  # For storing rating
    audio_file = models.FileField(upload_to='audio_files/', null=True, blank=True)  # Audio file

    def __str__(self):
        return f"AudioRecord {self.id}"
