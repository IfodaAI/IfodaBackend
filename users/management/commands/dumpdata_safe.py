import json
from django.core.management.commands.dumpdata import Command as DumpDataCommand
from phonenumber_field.phonenumber import PhoneNumber


class Command(DumpDataCommand):
    def handle(self, *app_labels, **options):
        from django.core.serializers.json import DjangoJSONEncoder

        class SafeJSONEncoder(DjangoJSONEncoder):
            def default(self, obj):
                if isinstance(obj, PhoneNumber):
                    return str(obj)
                return super().default(obj)

        options['indent'] = 4
        options['cls'] = SafeJSONEncoder
        super().handle(*app_labels, **options)
