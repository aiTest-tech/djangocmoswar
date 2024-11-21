import base64
import json
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import AudioRecord
from .serializers import AudioRecordSerializer

# External API settings
url = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"
headers = {
    "Content-Type": "application/json",
    "Authorization": "PcYD3f6WgosaSlLXLa7K7f5OteKLYQ6Cjyn0dyHEt2Fm7Ho7Sq-oo44N73XZvdDs"
}

# Define the body parameter for /process_audio endpoint
process_audio_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'file': openapi.Schema(type=openapi.TYPE_FILE),
    }
)

class ProcessAudioView(APIView):
    @swagger_auto_schema(request_body=process_audio_body, responses={200: AudioRecordSerializer})
    def post(self, request):
        if 'file' not in request.FILES:
            return Response({"error": "No file part in the request"}, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['file']

        if file.filename == '':
            return Response({"error": "No selected file"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Encode the file to base64
            audio_base64 = base64.b64encode(file.read()).decode('utf-8')

            # Prepare the payload for the external API
            payload = {
                "pipelineTasks": [
                    {
                        "taskType": "asr",
                        "config": {
                            "preProcessors": ["vad"],
                            "language": {
                                "sourceLanguage": "gu"
                            },
                            "audioFormat": "wav",
                            "samplingRate": 16000
                        }
                    }
                ],
                "inputData": {
                    "audio": [
                        {
                            "audioContent": audio_base64
                        }
                    ]
                }
            }

            # Send the request to the external API
            response = requests.post(url, headers=headers, data=json.dumps(payload))

            if response.status_code == 200:
                source = response.json()['pipelineResponse'][0]['output'][0]['source']

                # Create an AudioRecord and save to DB
                audio_record = AudioRecord.objects.create(
                    audio_base64=audio_base64,
                    source=source
                )

                # Return the response with the transcription and the ID of the record
                return Response({"text": source, 'id': audio_record.id}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Failed to process audio"}, status=response.status_code)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


submit_audio_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'text': openapi.Schema(type=openapi.TYPE_STRING),
    }
)

class SubmitAudioView(APIView):
    @swagger_auto_schema(request_body=submit_audio_body, responses={200: openapi.Response('Record updated successfully')})
    def post(self, request):
        data = request.data
        if not data.get('id') or not data.get('text'):
            return Response({'status': 'fail', 'message': 'Missing id or text'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            audio_record = AudioRecord.objects.get(id=data['id'])
            audio_record.edit_source = data['text']
            audio_record.save()

            return Response({'status': 'success', 'message': 'Record updated successfully'}, status=status.HTTP_200_OK)
        
        except AudioRecord.DoesNotExist:
            return Response({'status': 'fail', 'message': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)


rating_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'rating': openapi.Schema(type=openapi.TYPE_INTEGER),
    }
)

class AccRatingView(APIView):
    @swagger_auto_schema(request_body=rating_body, responses={200: openapi.Response('Rating updated successfully')})
    def post(self, request):
        data = request.data
        if not data.get('id') or not data.get('rating'):
            return Response({'status': 'fail', 'message': 'Missing id or rating'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            audio_record = AudioRecord.objects.get(id=data['id'])
            audio_record.rating = data['rating']
            audio_record.save()

            return Response({'status': 'success', 'message': 'Rating updated successfully'}, status=status.HTTP_200_OK)

        except AudioRecord.DoesNotExist:
            return Response({'status': 'fail', 'message': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)

class GetGrievanceRecordsView(APIView):
    @swagger_auto_schema(responses={200: AudioRecordSerializer(many=True)})
    def get(self, request):
        try:
            audio_records = AudioRecord.objects.all()
            serializer = AudioRecordSerializer(audio_records, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
