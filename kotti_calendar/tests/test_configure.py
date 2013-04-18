from pyramid.interfaces import ITranslationDirectories

from kotti_calendar import includeme
from kotti_calendar import kotti_configure


def test_kotti_configure():

    settings = {
        'kotti.available_types': '',
        'pyramid.includes': '',
    }

    kotti_configure(settings)

    assert settings['pyramid.includes'] == ' kotti_calendar kotti_calendar.views'
    assert settings['kotti.available_types'] == ' kotti_calendar.resources.Calendar kotti_calendar.resources.Event'

    assert settings['kotti_calendar.upcoming_events_widget.slot'] == 'none'
    assert settings['kotti_calendar.upcoming_events_widget.num_events'] == 5

    settings['kotti_calendar.upcoming_events_widget.num_events'] = "3"
    kotti_configure(settings)
    assert settings['kotti_calendar.upcoming_events_widget.num_events'] == 3

    settings['kotti_calendar.upcoming_events_widget.slot'] = "right"
    kotti_configure(settings)

    from kotti.events import objectevent_listeners
    from kotti.views.slots import RenderRightSlot

    oel = objectevent_listeners
    assert len(oel[(RenderRightSlot, None)]) == 1


def test_includeme(config):

    includeme(config)

    utils = config.registry.__dict__['_utility_registrations']
    k = (ITranslationDirectories, u'')

    # test if the translation dir is registered
    assert k in utils
    assert utils[k][0][0].find('kotti_calendar/locale') > 0
