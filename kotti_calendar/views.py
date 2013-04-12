import colander
import datetime

from paste.deploy.converters import asbool

from pyramid.compat import json
from pyramid.i18n import get_locale_name
from pyramid.url import resource_url
from sqlalchemy import desc
from sqlalchemy.sql.expression import or_

from js.fullcalendar import locales as fullcalendar_locales

from kotti import DBSession
from kotti.security import has_permission
from kotti.views.edit import ContentSchema
from kotti.views.edit import DocumentSchema
from kotti.views.form import AddFormView
from kotti.views.form import EditFormView
from kotti.views.util import template_api
from kotti.views.util import nodes_tree
from kotti.views.view import view_node
from pyramid.compat import json
from pyramid.i18n import get_locale_name
from pyramid.url import resource_url
from sqlalchemy import desc
from sqlalchemy.sql.expression import or_

from kotti_calendar import _
from kotti_calendar import calendar_settings
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
        description=_(u"Paste Google calendar XML feeds here"),
        )
    weekends = colander.SchemaNode(
        colander.Boolean(),
        title=_(u"Weekends"))


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


class CalendarAddForm(AddFormView):
    schema_factory = CalendarSchema
    add = Calendar
    item_type = _(u"Calendar")


class CalendarEditForm(EditFormView):
    schema_factory = CalendarSchema


class EventAddForm(AddFormView):
    schema_factory = EventSchema
    add = Event
    item_type = _(u"Event")


class EventEditForm(EditFormView):
    schema_factory = EventSchema


def events_below_context(self, context, request, permission='view'):
    """
    Get recursive all children of the given context, that are Events.

    :result: List with all event children of a given context.
    :rtype: list
    """
    tree = nodes_tree(request,
                      context=context,
                      permission=permission)

    return [n for n in tree.tolist()[1:] if n.type_info.name == u'Event']


def view_calendar(context, request):

    kotti_calendar_resources.need()

    settings = calendar_settings()

    calendar_position = settings['calendar_position']
    show_upcoming_events = asbool(settings['show_upcoming_events'])
    show_past_events = asbool(settings['show_past_events'])
    show_events_scope = settings['show_events_scope']

    locale_name = get_locale_name(request)
    if locale_name in fullcalendar_locales:
        fullcalendar_locales[locale_name].need()
    else:  # pragma: no cover (safety belt only, should never happen)
        fullcalendar_locales["en"].need()

    session = DBSession()

    now = datetime.datetime.now()

    if show_events_scope in ['context_only', 'site_wide']:

        if show_events_scope == 'context_only':
            query = session.query(Event).filter(Event.parent_id == context.id)
        else:  # show_events_scope == 'site_wide'
            query = session.query(Event)

        future = or_(Event.start > now, Event.end > now)
        upcoming = query.filter(future).order_by(Event.start).all()
        past = query.filter(Event.start < now).order_by(desc(Event.start)).all()

    else:  #show_events_scope == 'recursive':

        events = events_below_context(context, request)
        if context.type_info.name == u'Event':
            events.append(context)

        upcoming = [e for e in events if e.start > now and e.end > now]
        past = [e for e in events if e.start < now]

        upcoming.sort(key=lambda e: e.start)
        past.sort(key=lambda e: e.start, reverse=True)

    upcoming = [event for event in upcoming if\
                has_permission('view', event, request)]
    past = [event for event in past if\
                has_permission('view', event, request)]

    datetime_format = '%Y-%m-%d %H:%M:%S'

    fullcalendar_events = []
    for event in (upcoming + past):
        json_event = {
            'title': event.title,
            'url': resource_url(event, request),
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
        'eventSources': context.feeds,
        'weekends': context.weekends,
        'events': fullcalendar_events,
        }

    return {
        'api': template_api(context, request),
        'upcoming_events': upcoming,
        'past_events': past,
        'calendar_position': calendar_position,
        'show_upcoming_events': show_upcoming_events,
        'show_past_events': show_past_events,
        'fullcalendar_options': json.dumps(fullcalendar_options),
        }


def includeme_edit(config):
    config.add_view(
        CalendarAddForm,
        name=Calendar.type_info.add_view,
        permission='add',
        renderer='kotti:templates/edit/node.pt',
        )

    config.add_view(
        CalendarEditForm,
        context=Calendar,
        name='edit',
        permission='edit',
        renderer='kotti:templates/edit/node.pt',
        )

    config.add_view(
        EventAddForm,
        name=Event.type_info.add_view,
        permission='add',
        renderer='kotti:templates/edit/node.pt',
        )

    config.add_view(
        EventEditForm,
        context=Event,
        name='edit',
        permission='edit',
        renderer='kotti:templates/edit/node.pt',
        )


def includeme_view(config):
    config.add_view(
        view_calendar,
        context=Calendar,
        name='view',
        permission='view',
        renderer='templates/calendar-view.pt',
        )

    config.add_view(
        view_node,
        context=Event,
        name='view',
        permission='view',
        renderer='templates/event-view.pt',
        )

    config.add_static_view('static-kotti_calendar', 'kotti_calendar:static')


def includeme(config):
    includeme_edit(config)
    includeme_view(config)
