#!/usr/bin/env python

import os
import re
import sys
import django
from uuid import uuid4

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.projects import models  # noqa: E402

ure = re.compile(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}')

for rec in models.Record.objects.filter(record_type='ai_chat'):
    dirty = False
    for row in rec.content:
        if not ure.match(row['id']):
            row['id'] = str(uuid4())
            dirty = True
    if dirty:
        print(f"Updating record {rec}")
        rec.save()
