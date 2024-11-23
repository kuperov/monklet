#!./.venv/bin/python

import os
import re
import sys
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.projects import models  # noqa: E402

for rec in models.Record.objects.filter(record_type='ai_chat'):
    rn, ps = rec.case.real_name, rec.case.pseudonym
    if rn == ps:
        continue
    regex = re.compile('|'.join([r'\b'+n+r'\b' for n in rn.split(' ')]))
    matches = 0
    for line in rec.content:
        m = regex.search(line['text'])
        if m:
            matches += 1
            line['text'] = regex.sub(ps, line['text'])
    if matches:
        print(f"{rec}: {matches} occurrence(s) of {rn} replaced")
        rec.save()
