# LearnPath AI Backend

LearnPath AI is an AI-powered personalized learning platform backend built with Django, Django Channels, MongoDB (PyMongo), Redis, and JWT authentication.

## Architecture

- **Primary Communication**: WebSockets (Django Channels ASGI)
- **Database**: MongoDB via PyMongo with Repository Pattern
- **Message Broker & Channel Layer**: Redis
- **Authentication**: JWT (JSON Web Tokens) with PBKDF2 Password Hashing
- **External AI Integration**: Modular HTTP Client Gateway in `ai_integrations/`

## WebSocket Protocol Specification

### Connection Endpoints

- `/ws/auth/`: Public authentication endpoint (login, register, token refresh)
- `/ws/user/`: Authenticated learner operations
- `/ws/admin/`: Authenticated administrator operations
- `/ws/chat/`: Authenticated AI assistant chat endpoint
- `/ws/notifications/`: Authenticated notification stream endpoint

### Message Contract

#### Client Request Frame
```json
{
  "action": "module.action_name",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "payload": {}
}
```

#### Server Success Response
```json
{
  "type": "response",
  "action": "module.action_name",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "success": true,
  "data": {}
}
```

#### Server Error Response
```json
{
  "type": "error",
  "action": "module.action_name",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Descriptive error message",
    "details": {}
  }
}
```

#### Server Broadcast Event
```json
{
  "type": "event",
  "event": "event.name",
  "data": {}
}
```

## Running the Backend

### Environment Configuration
Provide runtime secrets through your deployment platform or Docker secret manager.
Do not commit `.env` files or copy configuration templates into production images.

### Direct Execution
```bash
pip install -r requirements.txt
python manage.py runserver
```
or with Daphne ASGI:
```bash
daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

### Docker Execution
The canonical production deployment is defined by the root `docker-compose.yml`.
The backend is hosted separately from the static frontend.
