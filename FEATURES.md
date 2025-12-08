# Alert System - Features Overview

This demo application showcases Django LiveView capabilities with a real-time alert management system.

## Core Features Implemented

### 1. Real-time Alert Table
- **Location**: Main page (`/`)
- **Description**: Displays all alerts in a responsive table
- **Columns**: ID, Type, Description, Created At, Actions
- **Auto-load**: Table loads automatically on page visit
- **Technology**: Uses `data-lv-load="load_alerts_table"` to fetch data via WebSocket

### 2. Random Alert Generator
- **Button**: "Add Random Alert"
- **Functionality**: Creates a new alert with random type (Info/Warning/Critical)
- **Description**: Empty by default
- **Notification**: Shows success message for 3 seconds
- **Real-time**: Table updates instantly for all connected users

### 3. Delete Alert
- **Location**: Delete button in each table row
- **Functionality**: Removes alert from database
- **Real-time Update**: Table refreshes automatically
- **Notification**: Confirmation message appears for 3 seconds

### 4. Alert Details Modal
- **Trigger**: "Details" button in table
- **Display**: Modal overlay with full alert information
  - Alert ID
  - Type (with color-coded badge)
  - Full description
  - Creation timestamp
- **Close Options**: Background click, close button, or "Close" button

### 5. New Alert Form
- **Navigation**: "New Alert Form" button
- **Page Change**: URL changes to `/new` without page reload
- **Title Update**: Page title changes to "New Alert"
- **Form Fields**:
  - Type selector (Info/Warning/Critical)
  - Description textarea

### 6. Form Validation
- **Description Required**: Cannot be empty
- **Max Length**: 500 characters
- **Error Display**: Red error messages below fields
- **Server-side**: All validation happens in Python
- **UX**: Form re-displays with errors if validation fails

### 7. Broadcast Notifications
- **Trigger**: When a new alert is created via form
- **Recipients**: All connected users receive notification
- **Message**: "New [TYPE] alert created!"
- **Duration**: Auto-dismisses after 3 seconds
- **Technology**: Uses `broadcast=True` in LiveView send()

### 8. Single Page Navigation
- **Form to Home**: Returns to main page after alert creation
- **URL Management**: Uses `window.history.pushState` via WebSocket
- **No Reload**: Entire body HTML is replaced without page refresh
- **Title Sync**: Page title updates match navigation

## Technical Highlights

### HTML over WebSockets
Instead of JSON API calls, the entire HTML is generated server-side and sent through WebSocket:

```python
send(consumer, {
    "target": "#alerts-table",
    "html": render_to_string("alerts/components/alerts_table.html", {...})
})
```

### Data Attributes (LiveView 2.x syntax)
- `data-lv-load="handler_name"`: Auto-loads content on mount
- `data-lv-action="handler_name"`: Triggers action on click
- `data-lv-submit="handler_name"`: Handles form submission
- `data-alert-id="{{ alert.id }}"`: Passes data to handlers (camelCase in Python)

### Broadcast Communication
```python
send(consumer, {...}, broadcast=True)
```
Sends updates to all WebSocket connections in the same room.

### Threading for Notifications
```python
threading.Thread(target=send_notification).start()
```
Allows delayed notification dismissal without blocking.

## User Interface

### Bulma CSS
- Clean, modern interface
- Responsive design
- No custom CSS needed
- Color-coded alert types:
  - Info: Blue
  - Warning: Yellow
  - Critical: Red

### Notifications
- Fixed position: top-right corner
- Green success messages
- Auto-dismiss after 3 seconds
- Stacks multiple notifications

## Database Schema

### Alert Model
```python
class Alert(models.Model):
    type = CharField(choices=['INFO', 'WARNING', 'CRITICAL'])
    description = TextField(blank=True)
    created_at = DateTimeField(auto_now_add=True)
```

## API / Handlers

All handlers are registered with `@liveview_handler(name)`:

1. `load_alerts_table` - Initial table load
2. `create_random_alert` - Random alert creation
3. `delete_alert` - Alert deletion
4. `show_alert_details` - Modal display
5. `close_modal` - Modal dismissal
6. `show_new_alert_form` - Navigate to form
7. `submit_new_alert` - Form submission & validation
8. `go_home` - Return to home page

## Performance Considerations

- **Database Queries**: Optimized with `Alert.objects.all()`
- **No Polling**: Pure WebSocket push
- **Efficient Updates**: Only affected HTML fragments are replaced
- **Concurrent Users**: Redis handles multiple connections

## Security

- **CSRF Protection**: Django middleware enabled
- **SQL Injection**: Protected by Django ORM
- **XSS**: Template escaping enabled
- **WebSocket Auth**: AuthMiddlewareStack

## Browser Requirements

- WebSocket support (all modern browsers)
- JavaScript enabled
- No special polyfills needed

## Scalability

- **Redis**: Channel layer for distributed WebSocket
- **PostgreSQL**: Reliable persistent storage
- **Docker**: Easy horizontal scaling
- **Daphne**: ASGI server for WebSocket handling

## No JavaScript Required

All interactivity is handled by the LiveView JavaScript client (included in the package). No custom JavaScript code was written for this demo.
