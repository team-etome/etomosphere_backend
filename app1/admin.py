from django.contrib import admin
from django.apps import apps

APP_LABELS = [
    'employees'
]

for app_label in APP_LABELS:
    try:
        app_config = apps.get_app_config(app_label)
    except LookupError:
        # app not installed; skip
        continue

    for model in app_config.get_models():
        try:
            admin.site.register(model)
        except admin.sites.AlreadyRegistered:
            pass
