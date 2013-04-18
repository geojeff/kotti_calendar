from kotti.views.slots import assign_slot
from kotti.util import extract_from_settings

from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('kotti_calendar')


def kotti_configure(settings):

    working_settings = upcoming_events_settings(settings=settings)

    settings['kotti_calendar.upcoming_events_widget.slot'] = \
            working_settings['slot']
    settings['kotti_calendar.upcoming_events_widget.num_events'] = \
            working_settings['num_events']

    if working_settings['slot'] != 'none':
        assign_slot('upcoming-events', working_settings['slot'])

    settings['pyramid.includes'] += ' kotti_calendar kotti_calendar.views'
    settings['kotti.available_types'] += \
            ' kotti_calendar.resources.Calendar kotti_calendar.resources.Event'


EVENTS_WIDGET_DEFAULTS = {
    'slot': 'none',
    'num_events': '5',
    }


def upcoming_events_settings(name='', settings=None):

    prefix = 'kotti_calendar.upcoming_events_widget.'
    if name:
        prefix += name + '.'  # pragma: no cover

    working_settings = EVENTS_WIDGET_DEFAULTS.copy()

    working_settings.update(extract_from_settings(prefix, settings=settings))

    try:
        working_settings['num_events'] = int(working_settings['num_events'])
    except ValueError:
        working_settings['num_events'] = 5

    try:
        working_settings['slot'] in [u'none',
                                     u'left',
                                     u'right',
                                     u'abovecontent',
                                     u'belowcontent',
                                     u'beforebodyend']
    except ValueError:
        working_settings['slot'] = 'none'

    return working_settings


def includeme(config):

    config.add_translation_dirs('kotti_calendar:locale')
    config.scan(__name__)


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
