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
    rn = rec.case.real_name
    if rn == rec.case.pseudonym:
        continue
    regex = re.compile('|'.join([r'\b'+n+r'\b' for n in rn.split(' ')]))
    matches = []
    for line in rec.content:
        m = regex.search(line['text'])
        if m:
            matches.append(m)
    if matches:
        mstring = ', '.join([m.group() for m in matches])
        print(f"Chat {rec} matches: elements of {rn} found: {mstring}")
