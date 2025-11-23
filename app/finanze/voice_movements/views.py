# voice_movements/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.core.files.uploadedfile import UploadedFile
from openai import OpenAI
import json
from datetime import datetime, timedelta
from typing import Dict, Any
import os
from io import BytesIO
from . import logger

# Import your existing models
from movimenti.models import Movement, Category, Subcategory

from django.conf import settings

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny


class VoiceMovementView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        POST /api/voice-movement/
        Accepts audio file, transcribes, and creates Movement
        """
        try:
            # Get audio file from request
            audio_file = request.FILES.get('audio')
            if not audio_file:
                return Response({
                    'success': False,
                    'error': 'No audio file provided'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate file type
            if not self._is_valid_audio(audio_file):
                return Response({
                    'success': False,
                    'error': 'Invalid audio format. Supported: mp3, wav, m4a, webm'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Step 1: Transcribe audio
            transcript = self._transcribe_audio(audio_file)
            
            # Step 2: Parse transcript to extract movement data
            movement_data = self._parse_transcript(transcript)
            
            # Step 3: Create Movement in database
            movement = self._create_movement(request.user, movement_data)
            
            return Response({
                'success': True,
                'movement': {
                    'id': movement.id,
                    'date': movement.date.isoformat(),
                    'amount': float(movement.amount),
                    'category': movement.category.category,
                    'description': movement.description,
                    'transcript': transcript
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _is_valid_audio(self, file: UploadedFile) -> bool:
        """Validate audio file format"""
        valid_extensions = ['.mp3', '.wav', '.m4a', '.webm', '.ogg', '.mp4']
        valid_mimetypes = ['audio/mpeg', 'audio/wav', 'audio/mp4', 'audio/webm', 
                          'audio/ogg', 'video/mp4']
        
        file_ext = file.name.lower().split('.')[-1]
        logger.info(f"File extension: {file_ext}")
        logger.info(f"File mimetype: {file.content_type}")
        return (f'.{file_ext}' in valid_extensions or 
                file.content_type in valid_mimetypes)
    
    def _transcribe_audio(self, audio_file: UploadedFile) -> str:
        """
        Transcribe audio using OpenAI Whisper
        Configure openai.api_key in settings.py
        """
        try:
            client = OpenAI(
                # This is the default and can be omitted
                api_key=os.environ.get("OPENAI_API_KEY"),
            )
            # Read file content
            audio_file.seek(0)
            audio_data = audio_file.read()
            buffer = BytesIO(audio_data)
            buffer.name = audio_file.name
            # Call Whisper API
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=buffer,
                response_format="text"
            )
            
            return response.strip()
            
        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")
    
    def _parse_transcript(self, transcript: str) -> Dict[str, Any]:
        """
        Use LLM to extract structured movement data from transcript
        """
        try:
            # Get available categories from database
            categories = list(Category.objects.values_list('category', flat=True))
            subcategories = list(Subcategory.objects.values_list('subcategory', flat=True))

            client = OpenAI(
                # This is the default and can be omitted
                api_key=os.environ.get("OPENAI_API_KEY"),
            )
            
            system_prompt = f"""You are a financial assistant extracting transaction data.
Extract and return ONLY valid JSON with these exact keys:
- date: ISO format datetime (YYYY-MM-DDTHH:MM). "yesterday" = {(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M')}, 
    "today" = {datetime.now().strftime('%Y-%m-%dT%H:%M')}, "tomorrow" = {(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M')}.
    Try and guess time if not explicitly given: if the description is about "lunch" or "dinner", then set time to 12pm/8pm; if it's about "morning" set 10am, "afternoon" 4pm, "evening" 8pm.
    If no time indication is given at all, use the current time.
- amount: Numeric value only (no currency symbols)
- category: Must match one of: {', '.join(categories)}
- subcategory: Optional field whose value must match one of: {', '.join(subcategories)}. Don't overstate it: if no strong match is found, set it to "other" if available or don't set it at all.
- description: Brief transaction description

Current date: {datetime.now().strftime('%Y-%m-%d')}"""


            response = client.responses.create(
                model="gpt-5-mini",
                instructions=system_prompt,
                input=transcript
            )
            
            content = response.output_text

            logger.info(f'Transcript content: {content}')  # Log the transcript content)
            
            # Clean markdown formatting if present
            if content.startswith("```"):
                content = '\n'.join(content.split('\n')[1:-1])
                if content.startswith("json"):
                    content = content[4:].strip()
            
            data = json.loads(content)
            
            # Validate required fields
            required = ['date', 'amount', 'category']
            if not all(k in data for k in required):
                raise ValueError(f"Missing required fields. Got: {list(data.keys())}")
            
            return data
            
        except Exception as e:
            raise Exception(f"Failed to parse transcript: {str(e)}")
    
    def _create_movement(self, user, data: Dict[str, Any]) -> Movement:
        """
        Create Movement instance using existing Django models
        """
        try:
            # Parse date
            movement_date = datetime.fromisoformat(data['date']).date()
            
            # Get or match category (case-insensitive)
            category = Category.objects.filter(
                category__iexact=data['category']
            ).first()
            
            if not category:
                # Fallback to 'Other' or first available category
                category = Category.objects.filter(
                    category__iexact='other'
                ).first() or Category.objects.first()
            
            # optional field
            opt_fields = {}
            subcategory = Subcategory.objects.filter(
                subcategory__iexact=data.get('subcategory')).first()
            if subcategory:
                opt_fields['subcategory'] = subcategory
            # Create movement
            movement = Movement.objects.create(
                user=user,
                date=movement_date,
                abs_amount=abs(float(data['amount'])),  # Ensure positive
                category=category,
                description=data.get('description', ''),
                # Add any other fields your Movement model has
                **opt_fields
            )
            
            return movement
            
        except Exception as e:
            raise Exception(f"Failed to create movement: {str(e)}")

class TextMovementView(APIView):
    permission_classes = [AllowAny]
    """
    Alternative endpoint for testing with text directly
    """
    def post(self, request):
        return self._text_movement_view(request)

    def _text_movement_view(self, request):
        """
        Alternative endpoint for testing with text directly
        POST /api/text-movement/
        Body: {"text": "I bought groceries yesterday for $50"}
        """
        try:
            data = json.loads(request.body)
            transcript = data.get('text', '')
            
            if not transcript:
                return JsonResponse({
                    'success': False,
                    'error': 'No text provided'
                }, status=400)
            
            view = VoiceMovementView()
            movement_data = view._parse_transcript(transcript)
            # This is mock, no need to create movement
            # movement = view._create_movement(request.user, movement_data)
            
            return JsonResponse({
                'success': True,
                'movement': movement_data,
            }, status=201)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)