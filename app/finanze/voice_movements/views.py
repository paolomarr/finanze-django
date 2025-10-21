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
import logging

# Import your existing models
from movimenti.models import Movement, Category

from django.conf import settings

class VoiceMovementView(View):
    """
    Django view to handle voice recording uploads and convert to Movement
    """
    
    @method_decorator(login_required)
    @method_decorator(csrf_exempt)  # If using token auth, otherwise remove
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        """
        POST /api/voice-movement/
        Accepts audio file, transcribes, and creates Movement
        """
        try:
            # Get audio file from request
            audio_file = request.FILES.get('audio')
            if not audio_file:
                return JsonResponse({
                    'success': False,
                    'error': 'No audio file provided'
                }, status=400)
            
            # Validate file type
            if not self._is_valid_audio(audio_file):
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid audio format. Supported: mp3, wav, m4a, webm'
                }, status=400)
            
            # Step 1: Transcribe audio
            transcript = self._transcribe_audio(audio_file)
            
            # Step 2: Parse transcript to extract movement data
            movement_data = self._parse_transcript(transcript)
            
            # Step 3: Create Movement in database
            movement = self._create_movement(request.user, movement_data)
            
            return JsonResponse({
                'success': True,
                'movement': {
                    'id': movement.id,
                    'date': movement.date.isoformat(),
                    'amount': float(movement.amount),
                    'category': movement.category.name,
                    'description': movement.description,
                    'transcript': transcript
                }
            }, status=201)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    def _is_valid_audio(self, file: UploadedFile) -> bool:
        """Validate audio file format"""
        valid_extensions = ['.mp3', '.wav', '.m4a', '.webm', '.ogg', '.mp4']
        valid_mimetypes = ['audio/mpeg', 'audio/wav', 'audio/mp4', 'audio/webm', 
                          'audio/ogg', 'video/mp4']
        
        file_ext = file.name.lower().split('.')[-1]
        return (f'.{file_ext}' in valid_extensions or 
                file.content_type in valid_mimetypes)
    
    def _transcribe_audio(self, audio_file: UploadedFile) -> str:
        """
        Transcribe audio using OpenAI Whisper
        Configure openai.api_key in settings.py
        """
        try:
            # Read file content
            audio_file.seek(0)
            
            # Call Whisper API
            response = openai.Audio.transcribe(
                model="whisper-1",
                file=audio_file,
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

            client = OpenAI(
                # This is the default and can be omitted
                api_key=os.environ.get("OPENAI_API_KEY"),
            )
            
            system_prompt = f"""You are a financial assistant extracting transaction data.
Extract and return ONLY valid JSON with these exact keys:
- date: ISO format (YYYY-MM-DD). "yesterday" = {(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')}, "today" = {datetime.now().strftime('%Y-%m-%d')}
- amount: Numeric value only (no currency symbols)
- category: Must match one of: {', '.join(categories)}
- description: Brief transaction description

Current date: {datetime.now().strftime('%Y-%m-%d')}"""


            response = client.responses.create(
                model="gpt-5-mini",
                instructions=system_prompt,
                input=transcript
            )
            
            content = response.output_text

            logging.info(f'Transcript content: {content}')  # Log the transcript content)
            
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
            
            # Create movement
            movement = Movement.objects.create(
                user=user,
                date=movement_date,
                abs_amount=abs(float(data['amount'])),  # Ensure positive
                category=category,
                description=data.get('description', ''),
                # Add any other fields your Movement model has
            )
            
            return movement
            
        except Exception as e:
            raise Exception(f"Failed to create movement: {str(e)}")


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def text_movement_view(request):
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
        movement = view._create_movement(request.user, movement_data)
        
        return JsonResponse({
            'success': True,
            'movement': {
                'id': movement.id,
                'date': movement.date.isoformat(),
                'amount': float(movement.amount),
                'category': movement.category.category,
                'description': movement.description
            }
        }, status=201)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)