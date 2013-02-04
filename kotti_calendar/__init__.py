from pyramid.i18n import TranslationStringFactory
from kotti.util import extract_from_settings

_ = TranslationStringFactory('kotti_calendar')


def kotti_configure(settings):

    settings['pyramid.includes'] += ' kotti_calendar kotti_calendar.views'
    settings['kotti.available_types'] += ' kotti_calendar.resources.Calendar kotti_calendar.resources.Event'

CALENDAR_WIDGET_DEFAULTS = {
    'show_upcoming_events': 'true',
    'show_past_events': 'true',
    'calendar_position': 'above',
    }

EVENTS_WIDGET_DEFAULTS = {
    'events_count': '5',
    }


def calendar_settings(name='', settings=None):

    prefix = 'kotti_calendar.calendar_widget.'
    if name:
        prefix += name + '.'  # pragma: no cover

    working_settings = CALENDAR_WIDGET_DEFAULTS.copy()

    working_settings.update(extract_from_settings(prefix, settings=settings))

    return working_settings


def upcoming_events_settings(name=''):
    prefix = 'kotti_calendar.upcoming_events_widget.'
    if name:
        prefix += name + '.'  # pragma: no cover
    settings = EVENTS_WIDGET_DEFAULTS.copy()
    settings.update(extract_from_settings(prefix))
    try:
        settings['events_count'] = int(settings['events_count'])
    except ValueError:
        settings['events_count'] = 5
    return settings


def includeme(config):

    config.add_translation_dirs('kotti_calendar:locale')


def _patch_colander():
    # https://github.com/dnouri/colander/commit/6a09583a8b9bcae29d6f51ce05434becff379134
    from colander import null
    from colander import DateTime

    save_datetime_serialize = DateTime.serialize

    def datetime_serialize(self, node, appstruct):
        if not appstruct:
            return null
        return save_datetime_serialize(self, node, appstruct)

    DateTime.serialize = datetime_serialize

_patch_colander()
