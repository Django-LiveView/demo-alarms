# Django LiveView Auto-Discovery Bug Report

## Resumen del Problema

El autodescubrimiento de handlers de Django LiveView **NO FUNCIONA** cuando se usa Daphne (ASGI server) en modo DEBUG=True, que es el escenario típico de desarrollo.

## Análisis del Código Fuente

### Ubicación del Problema
**Archivo:** `liveview/apps.py`
**Método:** `LiveViewConfig._should_import_components()`
**Líneas:** 22-41

### Código Problemático

```python
def _should_import_components(self):
    """
    Determine if we should import components based on the current process.
    """
    # Don't import during migrations, collectstatic, etc.
    if any(
        cmd in sys.argv
        for cmd in ["migrate", "makemigrations", "collectstatic", "compilemessages"]
    ):
        return False

    # Only import in the actual server process, not the reloader process
    if os.environ.get("RUN_MAIN") == "true":  # ← PROBLEMA AQUÍ
        return True

    # For production (no autoreload)
    if not settings.DEBUG:  # ← Y AQUÍ
        return True

    return False  # ← RETORNA False EN DESARROLLO CON DAPHNE
```

## ¿Por Qué Falla?

### Escenario 1: Desarrollo con `python manage.py runserver`
✅ **FUNCIONA**
- Django runserver establece `RUN_MAIN=true` cuando inicia el proceso principal
- La condición de la línea 34 se cumple
- Los handlers se importan correctamente

### Escenario 2: Desarrollo con Daphne (`daphne config.asgi:application`)
❌ **NO FUNCIONA**
- Daphne NO establece la variable `RUN_MAIN`
- `DEBUG=True` (modo desarrollo)
- La condición de la línea 34 falla: `RUN_MAIN` no existe
- La condición de la línea 38 falla: `DEBUG=True`
- Retorna `False` → **No se importan los handlers**

### Escenario 3: Producción con Daphne (`DEBUG=False`)
✅ **FUNCIONA**
- Aunque `RUN_MAIN` no está establecido
- La condición de la línea 38 se cumple: `not settings.DEBUG` = `True`
- Los handlers se importan correctamente

## Impacto

Este bug afecta a **todos los desarrolladores** que:
1. Usan Daphne para desarrollo (recomendado para apps con WebSockets)
2. Tienen `DEBUG=True` (estándar en desarrollo)
3. Esperan que el autodescubrimiento funcione según la documentación

## Casos de Uso Afectados

### ❌ No Funciona
```bash
# Desarrollo con Daphne (caso común)
DEBUG=True daphne config.asgi:application
```

### ✅ Funciona
```bash
# Desarrollo con runserver
DEBUG=True python manage.py runserver

# Producción con Daphne
DEBUG=False daphne config.asgi:application
```

## Workarounds Actuales

### Opción 1: Importación Manual en `asgi.py` (Lo que hicimos)
```python
# config/asgi.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# ← WORKAROUND: Importar manualmente los handlers
import alerts.liveview_components.alerts

from liveview.consumers import LiveViewConsumer
```

**Problema:** Requiere importación manual de cada módulo de handlers, anula el propósito del autodescubrimiento.

### Opción 2: Importación en `AppConfig.ready()`
```python
# alerts/apps.py
class AlertsConfig(AppConfig):
    def ready(self):
        import alerts.liveview_components.alerts
```

**Problema:** Mismo que la Opción 1, cada app debe hacerlo manualmente.

### Opción 3: Establecer `RUN_MAIN` manualmente
```bash
RUN_MAIN=true DEBUG=True daphne config.asgi:application
```

**Problema:** No es intuitivo, no está documentado, y la variable `RUN_MAIN` es interna de Django.

## Propuestas de Solución

### Solución 1: Detectar Daphne/ASGI (RECOMENDADA)

```python
def _should_import_components(self):
    """
    Determine if we should import components based on the current process.
    """
    # Don't import during migrations, collectstatic, etc.
    if any(
        cmd in sys.argv
        for cmd in ["migrate", "makemigrations", "collectstatic", "compilemessages"]
    ):
        return False

    # Check if we're running under ASGI/Daphne
    # These processes don't set RUN_MAIN but should still import
    if 'daphne' in sys.argv[0] or 'asgi' in ' '.join(sys.argv):
        return True

    # Only import in the actual server process, not the reloader process
    if os.environ.get("RUN_MAIN") == "true":
        return True

    # For production (no autoreload)
    if not settings.DEBUG:
        return True

    return False
```

### Solución 2: Siempre Importar en DEBUG (Más Simple)

```python
def _should_import_components(self):
    """
    Determine if we should import components based on the current process.
    """
    # Don't import during migrations, collectstatic, etc.
    if any(
        cmd in sys.argv
        for cmd in ["migrate", "makemigrations", "collectstatic", "compilemessages"]
    ):
        return False

    # In development, always import (remove RUN_MAIN check)
    if settings.DEBUG:
        return True

    # In production, always import
    return True
```

**Ventaja:** Mucho más simple, funciona en todos los casos
**Desventaja:** Se importa dos veces con runserver (reloader + main), pero no es problemático

### Solución 3: Nueva Variable de Entorno

```python
def _should_import_components(self):
    # Check for explicit opt-in
    if os.environ.get("LIVEVIEW_AUTO_IMPORT") == "true":
        return True

    # ... resto del código actual
```

**Ventaja:** Control explícito del usuario
**Desventaja:** Requiere configuración adicional, contra el objetivo de "funciona automáticamente"

## Recomendación

**Implementar Solución 2** por las siguientes razones:

1. ✅ **Simplicidad:** Elimina complejidad innecesaria
2. ✅ **Funciona en todos los casos:** runserver, Daphne, Gunicorn, etc.
3. ✅ **Sin configuración:** El autodescubrimiento realmente funciona automáticamente
4. ✅ **Sin efectos secundarios:** Importar dos veces no causa problemas (los decorators se registran una sola vez)
5. ✅ **Coherente con la documentación:** "Los handlers se cargan automáticamente"

## Cambios Necesarios

### En el Código
**Archivo:** `liveview/apps.py`
**Cambio:** Simplificar `_should_import_components()` según Solución 2

### En la Documentación
Añadir nota sobre el comportamiento en desarrollo:

> **Nota para desarrollo:** Los handlers se cargan automáticamente al iniciar el servidor,
> independientemente de si usas `runserver` o un servidor ASGI como Daphne.
> No necesitas configuración adicional.

## Testing

Para verificar la solución:

```bash
# 1. Desarrollo con runserver
DEBUG=True python manage.py runserver
# → Debe cargar handlers ✓

# 2. Desarrollo con Daphne
DEBUG=True daphne config.asgi:application
# → Debe cargar handlers ✓

# 3. Producción con Daphne
DEBUG=False daphne config.asgi:application
# → Debe cargar handlers ✓

# 4. Durante migraciones
python manage.py migrate
# → NO debe cargar handlers ✓
```

## Conclusión

Este es un **BUG en Django LiveView**, no en nuestro código. El problema está en la lógica de
`_should_import_components()` que asume que solo se usa con `runserver`, pero el caso de uso
real incluye servidores ASGI como Daphne.

La solución es simple y no rompe compatibilidad: eliminar la dependencia de `RUN_MAIN` y
simplemente importar siempre (excepto durante comandos de management).
