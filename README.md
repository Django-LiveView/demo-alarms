# Alert System with Django LiveView

A real-time alert system demonstration built with Django LiveView, showcasing HTML over WebSockets capabilities.

## Features

- **Real-time Updates**: All changes are reflected instantly across all connected clients
- **Alert Management**: Create, view, and delete alerts
- **Random Alert Generator**: Quickly create test alerts with random types
- **Alert Types**: Info, Warning, and Critical
- **Modal Details View**: View full alert information in a modal
- **Form Validation**: Client-side validation with error messages
- **Broadcast Notifications**: All users receive notifications when new alerts are created
- **Single Page Navigation**: Page changes without full reloads using HTML over WebSockets

## Technology Stack

- **Django 5.1.4**: Web framework
- **Django LiveView 2.1.4**: Real-time WebSocket communication
- **Bulma CSS**: Styling framework
- **PostgreSQL**: Database
- **Redis**: Channel layer for WebSocket connections
- **Docker**: Containerization

## Quick Start

### Prerequisites

- Docker and Docker Compose installed

### Running the Application

1. Clone the repository and navigate to the project directory

2. Build and start the containers:
```bash
docker-compose up --build
```

3. The application will be available at `http://localhost:8000`

4. Create a superuser (optional, in a new terminal):
```bash
docker-compose exec web python manage.py createsuperuser
```

Access the admin panel at `http://localhost:8000/admin`

## Project Structure

```
demo-alarms/
├── alerts/                     # Main application
│   ├── liveview_handlers.py   # LiveView WebSocket handlers
│   ├── models.py               # Alert model
│   ├── forms.py                # Alert form with validation
│   └── views.py                # Django views
├── config/                     # Django project configuration
│   ├── settings.py
│   ├── urls.py
│   └── asgi.py                 # ASGI configuration for WebSockets
├── templates/
│   ├── base.html
│   └── alerts/
│       ├── index.html          # Main alerts page
│       ├── new_alert.html      # New alert form page
│       └── components/         # Reusable components
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## How It Works

### Django LiveView

This project uses Django LiveView to send HTML over WebSockets instead of JSON. The key benefits:

1. **No JavaScript needed**: All logic is in Python
2. **Real-time updates**: Changes are pushed to clients instantly
3. **Broadcast support**: Notify all connected users
4. **Simple syntax**: Use template tags to bind events

### Example Handler

```python
@liveview_handler("create_random_alert")
def create_random_alert(consumer, content):
    # Create alert
    alert = Alert.objects.create(...)

    # Send HTML update
    send(consumer, {
        "target": "#alerts-table",
        "html": render_to_string(...)
    })

    # Broadcast to all users
    send(consumer, {...}, broadcast=True)
```

### Template Integration

```html
<button {% liveview create_random_alert %}>
    Add Random Alert
</button>
```

## Features Demonstration

### 1. View Alerts
- Displays all alerts in a table
- Shows ID, type, description, and creation time
- Auto-loads on page visit

### 2. Create Random Alert
- Generates an alert with random type (Info/Warning/Critical)
- Shows success notification for 3 seconds
- Updates the table in real-time

### 3. Delete Alert
- Removes alert from database
- Updates all clients
- Shows deletion notification

### 4. View Details
- Opens modal with full alert information
- Click outside or close button to dismiss

### 5. New Alert Form
- Navigate to form page (URL changes to /new)
- Select alert type and enter description
- Form validation with error messages
- On success, returns to home page
- Broadcasts notification to all users

### 6. Form Validation
- Description is required
- Maximum 500 characters
- Real-time error display

## Broadcasting

When a new alert is created via the form, all connected users receive a notification:

```python
send(consumer, {...}, broadcast=True)
```

This demonstrates how LiveView can push updates to all active sessions simultaneously.

## Development

### Without Docker

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables (create .env file)

4. Run migrations:
```bash
python manage.py migrate
```

5. Run the development server:
```bash
daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

## Notes

- This is a demonstration project
- No external JavaScript or CSS compilation needed
- Uses Bulma CSS from CDN
- All interactions are handled via WebSockets
- Page navigation changes URL without page reload

## License

MIT License - Feel free to use this as a reference for your own Django LiveView projects!
