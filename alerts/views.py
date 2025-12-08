from django.shortcuts import render
from .models import Alert


def index(request):
    alerts = Alert.objects.all()
    return render(request, 'alerts/index.html', {'alerts': alerts})
