from datetime import datetime
from datetime import timedelta

from pyramid.threadlocal import get_current_registry
from kotti.testing import FunctionalTestBase
from kotti.testing import DummyRequest


class TestUpcomingEventsWidget(FunctionalTestBase):
    def setUp(self):
        conf = {
            'kotti.configurators':
            'kotti_calendar.kotti_configure',
            'pyramid.includes':
            'kotti_calendar.widgets.includeme_upcoming_events',
            }
        super(TestUpcomingEventsWidget, self).setUp(**conf)

    def test_view(self):
        from kotti_calendar.widgets import upcoming_events
        from kotti.resources import get_root
        from kotti.workflow import get_workflow
        from kotti_calendar.resources import Calendar
        from kotti_calendar.resources import Event

        now = datetime.now()
        root = get_root()

        result = upcoming_events(root, DummyRequest())
        assert len(result['events']) == 0

        root['calendar'] = Calendar()
        root['calendar']['event1'] = Event(title=u'Event 1',
                                           start=now - timedelta(1),
                                           end=now + timedelta(2))
        root['calendar']['event2'] = Event(title=u'Event 2',
                                           start=now + timedelta(1),
                                           end=now + timedelta(2))
        wf = get_workflow(root)
        wf.transition_to_state(root['calendar']['event1'], None, u'public')
        wf.transition_to_state(root['calendar']['event2'], None, u'public')
        result = upcoming_events(root, DummyRequest())

        events = result['events']
        assert len(events) == 2
        assert events[0].title == u'Event 1'
        assert events[0].start == now - timedelta(1)
        assert events[1].title == u'Event 2'
        assert events[1].start == now + timedelta(1)

    def test_render(self):
        browser = self.login_testbrowser()
        ctrl = browser.getControl

        browser.getLink(u'Calendar').click()
        ctrl('Title').value = u'Calendar'
        ctrl(name=u'save').click()

        browser.getLink(u'Event').click()
        ctrl('Title').value = u'This is my Event'
        ctrl('Start').value = u'2112-08-22 20:00:00'
        ctrl('End').value = u'2112-08-22 22:00:00'
        ctrl(name=u'save').click()

        browser.open(self.BASE_URL)
        assert 'This is my Event' in browser.contents
        assert 'Aug 22, 2112 8:00:00 PM' in browser.contents

    def test_settings(self):
        browser = self.login_testbrowser()
        ctrl = browser.getControl
        browser.getLink(u'Calendar').click()
        ctrl('Title').value = u'Calendar'
        ctrl(name=u'save').click()

        for c in range(6):
            browser.getLink(u'Calendar').click()
            browser.getLink(u'Event').click()
            ctrl('Title').value = u'Future Event %d' % c
            ctrl('Start').value = u'2112-08-23 20:00:00'
            ctrl(name=u'save').click()

        browser.open(self.BASE_URL)
        assert u"Future Event 5" not in browser.contents

        settings = get_current_registry().settings
        settings['kotti_calendar.upcoming_events_widget.num_events'] = u'nan'
        browser.open(self.BASE_URL)
        assert u"Future Event 5" not in browser.contents

        settings = get_current_registry().settings
        settings['kotti_calendar.upcoming_events_widget.num_events'] = u'7'
        browser.open(self.BASE_URL)
        assert u"Future Event 5" in browser.contents

        # Note, for the main page, even if both show_upcoming_events and
        # show_past_events are false, titles of events will be in javascript
        # as configured for these tests.

        settings = get_current_registry().settings
        settings['kotti_calendar.upcoming_events_widget.num_events'] = u'7'
        settings['kotti_calendar.calendar_widget.show_upcoming_events'] = u'true'
        browser.open(self.BASE_URL)
        browser.getLink(u'Calendar').click()
        # Expect a given future event title to be in javascript, in right slot
        # widget, and in main page list.
        assert browser.contents.count(u"Future Event 5") == 3

        for i in range(6):
            browser.getLink(u'Calendar').click()
            browser.getLink(u'Event').click()
            ctrl('Title').value = u'Past Event %d' % i
            ctrl('Start').value = u'2012-08-23 20:00:00'
            ctrl(name=u'save').click()

        settings = get_current_registry().settings
        settings['kotti_calendar.calendar_widget.show_past_events'] = u'true'
        browser.open(self.BASE_URL)
        browser.getLink(u'Calendar').click()
        # For each past event, expect an occurrence in javascript and list on
        # the main page. Plus one because 'Past Event' is in 'Past Events'!
        assert browser.contents.count(u"Past Event") == 13

        settings = get_current_registry().settings
        settings['kotti_calendar.calendar_widget.show_past_events'] = u'false'
        browser.open(self.BASE_URL)
        browser.getLink(u'Calendar').click()
        # Expect only the occurrence in javascript.
        assert browser.contents.count(u"Past Event 5") == 1

        settings = get_current_registry().settings
        settings['kotti_calendar.calendar_widget.calendar_position'] = u'above'
        settings['kotti_calendar.calendar_widget.show_upcoming_events'] = u'true'
        settings['kotti_calendar.calendar_widget.show_past_events'] = u'true'
        browser.open(self.BASE_URL)
        browser.getLink(u'Calendar').click()
        html = browser.contents
        pos = browser.contents.index
        assert html.index('fullcalendar') < pos(u'Upcoming Events') < pos(u'Past Events')

        settings = get_current_registry().settings
        settings['kotti_calendar.calendar_widget.calendar_position'] = u'between'
        settings['kotti_calendar.calendar_widget.show_upcoming_events'] = u'true'
        settings['kotti_calendar.calendar_widget.show_past_events'] = u'true'
        browser.open(self.BASE_URL)
        browser.getLink(u'Calendar').click()
        pos = browser.contents.index
        assert pos(u'Upcoming Events') < pos('fullcalendar') < pos(u'Past Events')

        settings = get_current_registry().settings
        settings['kotti_calendar.calendar_widget.calendar_position'] = u'below'
        settings['kotti_calendar.calendar_widget.show_upcoming_events'] = u'true'
        settings['kotti_calendar.calendar_widget.show_past_events'] = u'true'
        browser.open(self.BASE_URL)
        browser.getLink(u'Calendar').click()
        pos = browser.contents.index
        assert pos(u'Upcoming Events') < pos(u'Past Events') < pos('fullcalendar')
