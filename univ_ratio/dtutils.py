import datetime


def get_discord_timestamp(dt: datetime.datetime, style: str = None):
    """
    Convert datetime object into discord's timestamp expression.
    :param dt: datetime object to convert.
    :param style: timestamp style. default is None.
    :return: string value of timestamp expression.
    """
    if dt is None:
        return 'UNDEFINED'
    if dt.tzinfo is None:
        dt = dt.astimezone(tz=datetime.timezone.utc)
    elif dt.isoformat().split('+')[1] == '00:00':   # UTC
        dt = dt.replace(tzinfo=datetime.timezone.utc)

    return f'(KST) <t:{int(dt.timestamp())}' + (f':{style}>' if style else '>')
