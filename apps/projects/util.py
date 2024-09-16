from datetime import datetime

_ECMASCRIPT_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'  # plus Z

def datetime_str(dt: datetime) -> str:
    # standard format for ecmascript: YYYY-MM-DDTHH:mm:ss.sssZ
    # https://tc39.es/ecma262/multipage/numbers-and-dates.html#sec-date-time-string-format
    if not isinstance(dt, datetime):
        return dt
    return dt.strftime(_ECMASCRIPT_FORMAT) + 'Z'

def parse_datetime(s: str) -> datetime:
    if s and isinstance(s, str):
        try:
            if s.endswith('Z'):
                # https://tc39.es/ecma262/multipage/numbers-and-dates.html#sec-date-time-string-format
                return datetime.strptime(s[:-1], _ECMASCRIPT_FORMAT)
            else:
                return datetime.strptime(s, '%Y-%m-%d %H:%M:%S.%f%z')
        except Exception:
            pass
    return s
