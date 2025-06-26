import datetime
import os.path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Escopo de acesso de leitura da agenda
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

class GoogleCalendar: 
    def __init__(self):
        self.creds = None
        # Token armazenado localmente após login
        token_path = os.path.join(os.path.dirname(__file__), 'calendar_token.json')
        if os.path.exists(token_path):
            self.creds = Credentials.from_authorized_user_file(token_path, SCOPES)

        # Login e autorização via navegador (na 1ª execução)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                credentials_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'credentials.json')
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SCOPES)
                self.creds = flow.run_local_server(port=0)

            # Salva token para reuso
            with open(token_path, 'w') as token:
                token.write(self.creds.to_json())

        # Conexão com a API
        self.service = build('calendar', 'v3', credentials=self.creds)

    def consult(self):
        agora = datetime.datetime.utcnow().isoformat() + 'Z'
        eventos_resultado = self.service.events().list(calendarId='primary', timeMin=agora,
                                                      maxResults=10, singleEvents=True,
                                                      orderBy='startTime').execute()
        eventos = eventos_resultado.get('items', [])
        response = []
        
        for evento in eventos:
            inicio = evento['start'].get('dateTime', evento['start'].get('date'))
            print(f"Evento: {evento['summary']} - Início: {inicio}")
            response.append({
                'summary': evento['summary'],
                'start': inicio
            })

        return response    

if __name__ == '__main__':
    calendar = GoogleCalendar()
    events = calendar.consult()
    print("Próximos eventos:", events)
