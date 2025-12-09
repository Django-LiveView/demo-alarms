import random
import threading
from time import sleep
from uuid import uuid4

from django.template.loader import render_to_string
from liveview.connections import send
from liveview.decorators import liveview_handler

from alerts.forms import AlertForm
from alerts.models import Alert


@liveview_handler("load_alerts_table")
def load_alerts_table(consumer, content):
    """Load all alerts into the table"""
    alerts = Alert.objects.all()
    send(
        consumer,
        {
            "target": "#alerts-table-content",
            "html": render_to_string(
                "alerts/components/alerts_table.html",
                {"alerts": alerts},
            ),
        },
    )


@liveview_handler("create_random_alert")
def create_random_alert(consumer, content):
    """Create a random alert"""
    alert_types = ['INFO', 'WARNING', 'CRITICAL']
    random_type = random.choice(alert_types)

    alert = Alert.objects.create(
        type=random_type,
        description=''
    )

    # Reload the table for all users
    alerts = Alert.objects.all()
    send(
        consumer,
        {
            "target": "#alerts-table-content",
            "html": render_to_string(
                "alerts/components/alerts_table.html",
                {"alerts": alerts},
            ),
        },
        broadcast=True,
    )

    # Show notification to all users
    def send_notification():
        notification_id = str(uuid4().hex)
        notification_target = f"notification-{notification_id}"
        send(
            consumer,
            {
                "target": "#notifications",
                "html": render_to_string(
                    "alerts/components/notification.html",
                    {
                        "id": notification_target,
                        "message": f"Random {alert.type} alert created!",
                    },
                ),
                "append": True,
            },
            broadcast=True,
        )
        sleep(3)
        send(
            consumer,
            {
                "target": f"#{notification_target}",
                "remove": True,
            },
            broadcast=True,
        )

    threading.Thread(target=send_notification).start()


@liveview_handler("delete_alert")
def delete_alert(consumer, content):
    """Delete an alert"""
    alert_id = content.get('data', {}).get('data_alert_id')

    try:
        alert = Alert.objects.get(id=alert_id)
        alert.delete()

        # Reload the table for all users
        alerts = Alert.objects.all()
        send(
            consumer,
            {
                "target": "#alerts-table-content",
                "html": render_to_string(
                    "alerts/components/alerts_table.html",
                    {"alerts": alerts},
                ),
            },
            broadcast=True,
        )

        # Show notification to all users
        def send_notification():
            notification_id = str(uuid4().hex)
            notification_target = f"notification-{notification_id}"
            send(
                consumer,
                {
                    "target": "#notifications",
                    "html": render_to_string(
                        "alerts/components/notification.html",
                        {
                            "id": notification_target,
                            "message": "Alert deleted successfully!",
                        },
                    ),
                    "append": True,
                },
                broadcast=True,
            )
            sleep(3)
            send(
                consumer,
                {
                    "target": f"#{notification_target}",
                    "remove": True,
                },
                broadcast=True,
            )

        threading.Thread(target=send_notification).start()
    except Alert.DoesNotExist:
        pass


@liveview_handler("show_alert_details")
def show_alert_details(consumer, content):
    """Show alert details in a modal"""
    alert_id = content.get('data', {}).get('data_alert_id')

    try:
        alert = Alert.objects.get(id=alert_id)
        send(
            consumer,
            {
                "target": "#modal-container",
                "html": render_to_string(
                    "alerts/components/alert_modal.html",
                    {"alert": alert},
                ),
                "url": f"/alert/{alert_id}",
                "title": f"Alert #{alert_id} - Alert System",
            },
        )
    except Alert.DoesNotExist:
        pass


@liveview_handler("close_modal")
def close_modal(consumer, content):
    """Close the modal"""
    send(
        consumer,
        {
            "target": "#modal-container",
            "html": "",
            "url": "/",
            "title": "Home - Alert System",
        },
    )


@liveview_handler("show_new_alert_form")
def show_new_alert_form(consumer, content):
    """Navigate to the new alert form page"""
    send(
        consumer,
        {
            "target": "body",
            "html": render_to_string(
                "alerts/new_alert.html",
                {"form": AlertForm()},
            ),
            "url": "/new",
            "title": "New Alert - Alert System",
        },
    )


@liveview_handler("submit_new_alert")
def submit_new_alert(consumer, content):
    """Submit the new alert form"""
    form = AlertForm(content.get('form'))

    if form.is_valid():
        alert = form.save()

        # Navigate back to home page
        alerts = Alert.objects.all()
        send(
            consumer,
            {
                "target": "body",
                "html": render_to_string(
                    "alerts/index.html",
                    {"alerts": alerts},
                ),
                "url": "/",
                "title": "Home - Alert System",
            },
        )

        # Broadcast notification to all users
        def send_broadcast_notification():
            notification_id = str(uuid4().hex)
            notification_target = f"notification-{notification_id}"
            send(
                consumer,
                {
                    "target": "#notifications",
                    "html": render_to_string(
                        "alerts/components/notification.html",
                        {
                            "id": notification_target,
                            "message": f"New {alert.type} alert created!",
                        },
                    ),
                    "append": True,
                },
                broadcast=True,
            )
            sleep(3)
            send(
                consumer,
                {
                    "target": f"#{notification_target}",
                    "remove": True,
                },
                broadcast=True,
            )

        threading.Thread(target=send_broadcast_notification).start()
    else:
        # Show form with errors
        send(
            consumer,
            {
                "target": "body",
                "html": render_to_string(
                    "alerts/new_alert.html",
                    {"form": form},
                ),
            },
        )


@liveview_handler("go_home")
def go_home(consumer, content):
    """Navigate back to home page"""
    alerts = Alert.objects.all()
    send(
        consumer,
        {
            "target": "body",
            "html": render_to_string(
                "alerts/index.html",
                {"alerts": alerts},
            ),
            "url": "/",
            "title": "Home - Alert System",
        },
    )
