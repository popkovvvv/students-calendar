from typing import List, Dict, Optional, Union
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google.auth.external_account_authorized_user import Credentials as ExternalCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
import os
from config.settings import SCOPES, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI
import logging

logger = logging.getLogger(__name__)

class GoogleCalendarAPI:
    def __init__(self):
        self.credentials: Optional[Union[Credentials, ExternalCredentials]] = None
        self.service = None
        self._cache = {}
        
    def get_credentials(self) -> Optional[Union[Credentials, ExternalCredentials]]:
        """Получение или обновление учетных данных."""
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.credentials = pickle.load(token)
                
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_config(
                    {
                        "installed": {
                            "client_id": GOOGLE_CLIENT_ID,
                            "client_secret": GOOGLE_CLIENT_SECRET,
                            "redirect_uris": [GOOGLE_REDIRECT_URI],
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token"
                        }
                    },
                    SCOPES
                )
                self.credentials = flow.run_local_server(port=8080)
                
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.credentials, token)
                
        return self.credentials
        
    def get_service(self):
        """Получение сервиса Google Calendar."""
        if not self.service:
            credentials = self.get_credentials()
            if credentials:
                self.service = build('calendar', 'v3', credentials=credentials)
        return self.service
        
    async def get_events(self, days: int = 7) -> List[Dict]:
        """Получение событий календаря на указанное количество дней."""
        cache_key = f"events_{days}"
        if cache_key in self._cache:
            logger.info(f"Returning events from cache for key: {cache_key}")
            return self._cache[cache_key]

        logger.info(f"Fetching events from Google Calendar API for key: {cache_key}")
        try:
            service = self.get_service()
            if not service:
                return []
                
            now = datetime.utcnow()
            time_min = now.isoformat() + 'Z'
            time_max = (now + timedelta(days=days)).isoformat() + 'Z'
            
            events_result = service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            self._cache[cache_key] = events
            return events
            
        except Exception as e:
            logger.error(f"Error getting events: {e}")
            return []
            
    async def create_event(self, summary: str, start_time: datetime, end_time: datetime, description: str = "") -> Optional[Dict]:
        """Создание нового события в календаре."""
        try:
            service = self.get_service()
            if not service:
                logger.error("Google Calendar service not available.")
                return None
                
            event = {
                'summary': summary,
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'Europe/Moscow',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'Europe/Moscow',
                },
            }
            
            logger.info(f"Creating event with body: {event}")
            event = service.events().insert(calendarId='primary', body=event).execute()
            logger.info(f"Event created successfully: {event}")
            # Очищаем кэш после успешного создания события
            self._cache = {}
            return event
            
        except Exception as e:
            logger.error(f"Error creating event: {e}")
            return None
            
    async def delete_event(self, event_id: str) -> bool:
        """Удаление события из календаря."""
        try:
            service = self.get_service()
            if not service:
                logger.error("Google Calendar service not available for deletion.")
                return False
                
            logger.info(f"Attempting to delete event with ID: {event_id}")
            service.events().delete(calendarId='primary', eventId=event_id).execute()
            logger.info(f"Event with ID {event_id} deleted successfully.")
            # Очищаем кэш после успешного удаления события
            self._cache = {}
            return True
            
        except Exception as e:
            logger.error(f"Error deleting event with ID {event_id}: {e}")
            return False 