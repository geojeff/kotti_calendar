import colander
import datetime

from paste.deploy.converters import asbool

from pyramid.compat import json
from pyramid.i18n import get_locale_name
from pyramid.url import resource_url
from pyramid.view import view_config
from pyramid.view import view_defaults

from sqlalchemy import desc
from sqlalchemy.sql.expression import or_

from js.fullcalendar import locales as fullcalendar_locales

from deform.widget import SelectWidget

from kotti import DBSession
from kotti.security import has_permission
from kotti.views.edit import ContentSchema
from kotti.views.edit import DocumentSchema
from kotti.views.form import AddFormView
from kotti.views.form import EditFormView
from kotti.views.util import template_api
from kotti.views.util import nodes_tree
from kotti.views.view import view_node
from kotti.resources import Content

from kotti_calendar import _
from kotti_calendar import upcoming_events_settings
from kotti_calendar.resources import Calendar
from kotti_calendar.resources import Event
from kotti_calendar.fanstatic import kotti_calendar_resources


class Feeds(colander.SequenceSchema):

    feed = colander.SchemaNode(
        colander.String(),
        title=_(u"Feed"),
        missing=None,
        )


class CalendarSchema(ContentSchema):

    feeds = Feeds(
        missing=[],
        title=_(u"Calendar feeds"),
        description=_(u"Paste Google calendar XML feeds here"),)

    weekends = colander.SchemaNode(
        colander.Boolean(),
        default=True,
        missing=True,
        title=_(u"Include Weekends"),)

    choices = (('calendar_only', 'Calendar (Show events contained in calendar only)'),
               ('recursive', 'Recursive (Show events in and below calendar location)'),
               ('site_wide', 'Site Wide (Show all events in the site)'),)
    scope = colander.SchemaNode(
        colander.String(),
        default=_(u'calendar_only'),
        missing=_(u'calendar_only'),
        title=_(u'Scope'),
        widget=SelectWidget(values=choices),)

    choices = (('no', 'Do not show'),
               ('above', 'Above calendar'),
               ('below', 'Below Calendar'),)
    show_events_list = colander.SchemaNode(
        colander.String(),
        default=_(u'below'),
        missing=_(u'below'),
        title=_(u'Show Events List?'),
        widget=SelectWidget(values=choices),)

    choices = (('past_first', 'Show past events first'),
               ('upcoming_first', 'Show upcoming events first'),
               ('past_only', 'Show past events only'),
               ('upcoming_only', 'Show upcoming events only'),)
    events_list_order = colander.SchemaNode(
        colander.String(),
        default=_(u'upcoming_first'),
        missing=_(u'upcoming_first'),
        title=_(u'Events List Order'),
        widget=SelectWidget(values=choices),)


class EventSchema(DocumentSchema):

    start = colander.SchemaNode(
        colander.DateTime(default_tzinfo=None),
        title=_(u"Start"))

    end = colander.SchemaNode(
        colander.DateTime(default_tzinfo=None),
        title=_(u"End"),
        missing=None)

    all_day = colander.SchemaNode(
        colander.Boolean(),
        title=_(u"All day"),
        default=False,
        missing=False)


@view_config(name=Calendar.type_info.add_view,
             permission='add',
             renderer='kotti:templates/edit/node.pt')
class CalendarAddForm(AddFormView):
    schema_factory = CalendarSchema
    add = Calendar
    item_type = _(u"Calendar")


@view_config(name='edit',
             context=Calendar,
             permission='edit',
             renderer='kotti:templates/edit/node.pt')
class CalendarEditForm(EditFormView):
    schema_factory = CalendarSchema


@view_config(name=Event.type_info.add_view,
             permission='add',
             renderer='kotti:templates/edit/node.pt')
class EventAddForm(AddFormView):
    schema_factory = EventSchema
    add = Event
    item_type = _(u"Event")


@view_config(name='edit',
             context=Event,
             permission='edit',
             renderer='kotti:templates/edit/node.pt')
class EventEditForm(EditFormView):
    schema_factory = EventSchema


class BaseView(object):
    """ BaseView provides a common constructor method. """

    def __init__(self, context, request):
        """ Constructor.  Sets context and request as instance attributes.

        :param context: context.
        :type context: kotti.resources.Content or subclass thereof.

        :param request: request.
        :type request: pyramid.request.Request
        """

        self.context = context
        self.request = request


@view_defaults(context=Calendar, permission='view')
class CalendarView(BaseView):
    """ View for Calendar. """

    @view_config(name='view',
                 permission='view',
                 renderer='templates/calendar-view.pt')
    def view_calendar(self):

        kotti_calendar_resources.need()

        locale_name = get_locale_name(self.request)
        if locale_name in fullcalendar_locales:
            fullcalendar_locales[locale_name].need()
        else:  # pragma: no cover (safety belt only, should never happen)
            fullcalendar_locales["en"].need()

        session = DBSession()

        now = datetime.datetime.now()

        upcoming = []
        past = []

        # Make false, if no.
        if self.context.show_events_list == 'no':
            self.context.show_events_list = ''

        if self.context.scope in ['calendar_only', 'site_wide']:

            if self.context.scope == 'calendar_only':
                query = session.query(Event).filter(Event.parent_id == self.context.id)
            else:  # show_events_scope == 'site_wide'
                query = session.query(Event)

            if self.context.show_events_list:
                future_filter = or_(Event.start > now, Event.end > now)
                upcoming = query.filter(future_filter).order_by(Event.start).all()

                past = query.filter(Event.start < now).order_by(desc(Event.start)).all()

        else:  # scope == 'recursive':

            events = self.events_below_context(self.context.parent)

            if self.context.show_events_list:
                upcoming = [e for e in events if e.start > now]
                upcoming.sort(key=lambda e: e.start)

                past = [e for e in events if e.start < now]
                past.sort(key=lambda e: e.start, reverse=True)

        if self.context.show_events_list:
            upcoming = [event for event in upcoming if\
                        has_permission('view', event, self.request)]

            past = [event for event in past if\
                        has_permission('view', event, self.request)]

        datetime_format = '%Y-%m-%d %H:%M:%S'

        fullcalendar_events = []

        for event in (upcoming + past):
            json_event = {
                'title': event.title,
                'url': resource_url(event, self.request),
                'start': event.start.strftime(datetime_format),
                'allDay': event.all_day,
                }
            if event.end:
                json_event['end'] = event.end.strftime(datetime_format)
            fullcalendar_events.append(json_event)

        fullcalendar_options = {
            'header': {
                'left': 'prev,next today',
                'center': 'title',
                'right': 'month,agendaWeek,agendaDay'
            },
            'eventSources': self.context.feeds,
            'weekends': self.context.weekends,
            'events': fullcalendar_events,
            }

        return {
            'api': template_api(self.context, self.request),
            'upcoming': {'label': 'upcoming', 'events': upcoming},
            'past': {'label': 'past', 'events': past},
            'fullcalendar_options': json.dumps(fullcalendar_options),
            }

    def events_below_context(self, context, permission='view'):
        """
        Recursively find all Events from the context.

        :result: List with all Event items in and below a context.
        :rtype: list
        """
        tree = nodes_tree(self.request,
                          context=context,
                          permission=permission)

        return [n for n in tree.tolist()[1:] if n.type_info.name == u'Event']


@view_defaults(context=Event, permission='view')
class EventView(BaseView):
    """ View for Event. """

    @view_config(name='event-view',
                 permission='view',
                 renderer='kotti_calendar:templates/event-view.pt')
    def view(self):

        return {}


@view_defaults(context=Content, permission='view')
class EventListViews(BaseView):
    """ List views for Events.
    """

    @view_config(name='upcoming-events',
                 renderer='kotti_calendar:templates/upcoming-events.pt')
    def upcoming_events(self):
        now = datetime.datetime.now()
        settings = upcoming_events_settings()
        future = or_(Event.start > now, Event.end > now)
        events = DBSession.query(Event).filter(future).order_by(Event.start).all()
        events = [event for event in events if\
                    has_permission('view', event, self.request)]
        if len(events) > settings['num_events']:
            events = events[:settings['num_events']]
        return {'events': events}


def includeme(config):

    config.add_static_view('static-kotti_calendar', 'kotti_calendar:static')
