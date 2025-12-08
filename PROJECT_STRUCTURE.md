# Project Structure

```
demo-alarms/
│
├── alerts/                          # Main Django app
│   ├── migrations/                  # Database migrations
│   │   ├── __init__.py
│   │   └── 0001_initial.py          # Alert model migration
│   ├── __init__.py
│   ├── admin.py                     # Django admin configuration
│   ├── apps.py                      # App configuration
│   ├── forms.py                     # AlertForm with validation
│   ├── liveview_handlers.py         # All LiveView WebSocket handlers
│   ├── models.py                    # Alert model definition
│   ├── urls.py                      # App URL routing
│   └── views.py                     # Django views (index)
│
├── config/                          # Django project configuration
│   ├── __init__.py
│   ├── asgi.py                      # ASGI config for WebSocket
│   ├── settings.py                  # Main Django settings
│   ├── urls.py                      # Root URL configuration
│   └── wsgi.py                      # WSGI config (not used)
│
├── templates/                       # HTML templates
│   ├── base.html                    # Base template with LiveView JS
│   └── alerts/
│       ├── index.html               # Main alerts page
│       ├── new_alert.html           # Alert creation form
│       └── components/
│           ├── alerts_table.html    # Table component
│           ├── alert_modal.html     # Modal component
│           └── notification.html    # Notification component
│
├── docker-compose.yml               # Docker Compose configuration
├── Dockerfile                       # Web container definition
├── requirements.txt                 # Python dependencies
├── manage.py                        # Django management script
├── start.sh                         # Quick start script
├── .dockerignore                    # Docker ignore patterns
├── .gitignore                       # Git ignore patterns
├── .env.example                     # Environment variables example
├── README.md                        # Project documentation
├── FEATURES.md                      # Features overview
└── PROJECT_STRUCTURE.md             # This file

# Docker Volumes Created:
demo-alarms_postgres_data/           # PostgreSQL data persistence
```

## File Descriptions

### alerts/liveview_handlers.py
Contains all WebSocket handler functions:
- `load_alerts_table()` - Loads alerts into table
- `create_random_alert()` - Creates random alert
- `delete_alert()` - Deletes an alert
- `show_alert_details()` - Shows modal
- `close_modal()` - Closes modal
- `show_new_alert_form()` - Navigate to form
- `submit_new_alert()` - Form submission
- `go_home()` - Return to home

Each handler uses `@liveview_handler("name")` decorator and receives:
- `consumer`: WebSocket consumer instance
- `content`: Dict with data from client

### alerts/models.py
Defines the Alert model:
- `type`: CharField with choices (INFO, WARNING, CRITICAL)
- `description`: TextField (can be blank)
- `created_at`: Auto-generated timestamp

### alerts/forms.py
AlertForm with validation:
- Validates description is not empty
- Limits description to 500 characters
- Uses Django's built-in form validation

### config/asgi.py
ASGI configuration for WebSocket support:
- Imports LiveViewConsumer after django.setup()
- Routes `/ws/liveview/<room_name>/` to LiveView
- Uses AuthMiddlewareStack for authentication

### config/settings.py
Django settings including:
- INSTALLED_APPS: daphne, channels, liveview, alerts
- CHANNEL_LAYERS: Redis configuration
- DATABASES: PostgreSQL configuration
- Static files configuration

### templates/
All templates use Bulma CSS from CDN. LiveView 2.x data attributes:
- `data-lv-load="handler"` - Auto-load on mount
- `data-lv-action="handler"` - Click handler
- `data-lv-submit="handler"` - Form submit handler
- `data-*` - Pass data to handlers (becomes camelCase in Python)

### docker-compose.yml
Defines three services:
- **db**: PostgreSQL 16 database
- **redis**: Redis 7 for channel layer
- **web**: Django app with Daphne ASGI server

### Dockerfile
Multi-stage build:
1. Base: Python 3.12 slim
2. Install: PostgreSQL client + Python deps
3. Copy: Application code
4. Command: Daphne ASGI server

## Key Design Decisions

### Why Django LiveView?
- No JavaScript framework needed
- HTML generated in Python
- Real-time updates via WebSocket
- Familiar Django patterns

### Why Bulma CSS?
- No build step required
- CDN delivery
- Clean, modern design
- Component-based

### Why Docker?
- Consistent environment
- Easy deployment
- Service orchestration
- Development/production parity

### Why PostgreSQL?
- Production-ready
- Excellent Django support
- Reliable transactions
- Scalable

### Why Redis?
- Required for Django Channels
- Fast in-memory operations
- Pub/sub for broadcasting
- Channel layer storage

## Development Workflow

1. **Start**: `docker compose up`
2. **Migrations**: `docker compose exec web python manage.py makemigrations`
3. **Apply**: `docker compose exec web python manage.py migrate`
4. **Shell**: `docker compose exec web python manage.py shell`
5. **Logs**: `docker compose logs -f web`
6. **Stop**: `docker compose down`

## Production Considerations

For production deployment:
1. Change SECRET_KEY
2. Set DEBUG=False
3. Configure ALLOWED_HOSTS
4. Use proper database credentials
5. Add SSL/TLS
6. Configure static file serving
7. Set up monitoring
8. Use docker-compose.prod.yml
