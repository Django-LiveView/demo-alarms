# Implementation Notes - Django LiveView 2.x

## Correcciones Realizadas

Después de revisar la documentación oficial de Django LiveView, se realizaron las siguientes correcciones para asegurar la correcta implementación de la versión 2.x:

### 1. Template Base (base.html)

#### Antes (incorrecto):
```html
<html>
<head>
    <script src="{% static 'liveview/liveview.js' %}" defer data-ws-url="ws://..."></script>
</head>
<body>
```

#### Después (correcto):
```html
<html data-room="{% if request.user.is_authenticated %}{{ request.user.id }}{% else %}anonymous{% endif %}">
<head>
    <script src="{% static 'liveview/liveview.min.js' %}" defer></script>
</head>
<body data-controller="page">
```

**Cambios clave:**
- Añadido `data-room` al elemento `<html>` para identificar la sala de WebSocket
- Añadido `data-controller="page"` al elemento `<body>` para activar el controlador Stimulus
- Cambiado `liveview.js` por `liveview.min.js` (versión minificada)
- Eliminado `data-ws-url` (no es necesario, se auto-configura)

### 2. Atributos de Data en Templates

#### Antes (incorrecto):
```html
<button data-lv-action="create_random_alert">Add Random Alert</button>
<div data-lv-load="load_alerts_table">...</div>
<form data-lv-submit="submit_new_alert">...</form>
```

#### Después (correcto):
```html
<button data-liveview-function="create_random_alert" data-action="click->page#run">
    Add Random Alert
</button>
<div data-liveview-function="load_alerts_table" data-action="connect->page#run">
    ...
</div>
<form data-liveview-function="submit_new_alert" data-action="submit->page#run">
    ...
</form>
```

**Cambios clave:**
- Usar `data-liveview-function` en lugar de `data-lv-action`, `data-lv-load`, etc.
- Añadir `data-action` con el formato Stimulus: `evento->controlador#método`
- Eventos disponibles:
  - `click->page#run` para botones y clicks
  - `connect->page#run` para carga automática al montar el elemento
  - `submit->page#run` para formularios

### 3. Paso de Datos a Handlers

#### Antes (incorrecto):
```html
<button data-lv-action="delete_alert" data-alert-id="{{ alert.id }}">
```

```python
def delete_alert(consumer, content):
    alert_id = content.get('alertId')  # ❌ No funciona
```

#### Después (correcto):
```html
<button
    data-liveview-function="delete_alert"
    data-action="click->page#run"
    data-data-alert-id="{{ alert.id }}">
```

```python
def delete_alert(consumer, content):
    alert_id = content.get('data', {}).get('alertId')  # ✅ Correcto
```

**Cambios clave:**
- Los atributos de datos deben tener el prefijo `data-data-*`
- En el handler, acceder a través de `content.get('data', {})`
- Los nombres de atributos con guiones se convierten a camelCase en Python:
  - `data-data-alert-id` → `alertId`
  - `data-data-user-name` → `userName`

### 4. Estructura del objeto `content`

Según la documentación, el objeto `content` que reciben los handlers tiene esta estructura:

```python
{
    "function": "nombre_del_handler",  # El handler que se está llamando
    "data": {},                         # Datos de atributos data-data-*
    "form": {},                         # Datos del formulario si es submit
    "lang": "es",                       # Idioma del usuario
    "room": "anonymous"                 # ID de la sala WebSocket
}
```

### 5. Configuración ASGI correcta

El archivo `asgi.py` se configuró correctamente:

```python
import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()  # Importante: llamar antes de importar consumers

from liveview.consumers import LiveViewConsumer

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path('ws/liveview/<str:room_name>/', LiveViewConsumer.as_asgi()),
        ])
    ),
})
```

**Puntos clave:**
- Llamar a `django.setup()` antes de importar `LiveViewConsumer`
- Usar `LiveViewConsumer` directamente (no hay `websocket_urlpatterns`)
- El patrón de URL debe ser `ws/liveview/<str:room_name>/`

## Patrones Correctos de Uso

### Carga Automática de Contenido
```html
<div id="my-content"
     data-liveview-function="load_content"
     data-action="connect->page#run">
    <!-- Contenido inicial -->
</div>
```

### Botón con Acción
```html
<button
    data-liveview-function="do_something"
    data-action="click->page#run">
    Do Something
</button>
```

### Botón con Datos
```html
<button
    data-liveview-function="delete_item"
    data-action="click->page#run"
    data-data-item-id="{{ item.id }}"
    data-data-item-type="product">
    Delete
</button>
```

Handler correspondiente:
```python
@liveview_handler("delete_item")
def delete_item(consumer, content):
    item_id = content.get('data', {}).get('itemId')      # "123"
    item_type = content.get('data', {}).get('itemType')  # "product"
    # ... lógica
```

### Formulario
```html
<form
    data-liveview-function="submit_form"
    data-action="submit->page#run">
    <input type="text" name="username">
    <input type="email" name="email">
    <button type="submit">Submit</button>
</form>
```

Handler correspondiente:
```python
@liveview_handler("submit_form")
def submit_form(consumer, content):
    username = content.get('form', {}).get('username')
    email = content.get('form', {}).get('email')
    # ... lógica
```

## Eventos Stimulus Disponibles

- `click` - Click del ratón
- `submit` - Envío de formulario
- `change` - Cambio de valor en input
- `input` - Escritura en input
- `connect` - Elemento conectado al DOM (útil para carga inicial)
- `disconnect` - Elemento desconectado del DOM
- Y más eventos estándar del DOM...

## Buenas Prácticas

1. **Siempre usar `data-room`** en `<html>` para identificar usuarios
2. **Siempre usar `data-controller="page"`** en `<body>`
3. **Usar nombres descriptivos** para las funciones de LiveView
4. **Prefijo `data-data-`** para todos los datos personalizados
5. **Acceder a datos vía** `content.get('data', {})` y `content.get('form', {})`
6. **Manejar errores** cuando los datos no existen

## Recursos

- Documentación oficial: https://django-liveview.andros.dev/
- GitHub: https://github.com/Django-LiveView/liveview
- Quick Start: https://django-liveview.andros.dev/quick-start/
- Reference (andros.dev source): ~/workspace/opensource/andros.dev
