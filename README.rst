==============
kotti_calendar
==============

This is an extension to the Kotti CMS that allows you to add calendars
with events to your Kotti site.

It uses the `FullCalendar jQuery plugin`_ to display calendars.

Events can be either pulled from Google calendar XML feeds or added in
Kotti itself.

`Find out more about Kotti`_

Setup
=====

To activate the kotti_calendar add-on in your Kotti site, you need to
add an entry to the ``kotti.configurators`` setting in your Paste
Deploy config.  If you don't have a ``kotti.configurators`` option,
add one.  The line in your ``[app:main]`` section could then look
like this::

  kotti.configurators = kotti_calendar.kotti_configure

With this, you'll be able to add calendar and event items in your site.

Calendar Page Layout
--------------------

The default layout in the calendar template is to have the calendar at the top,
followed by a list of upcoming events, followed by a list of past events. You
can control the positioning of the calendar relative to the two lists with the
following setting (default is ``above``):::

    kotti_calendar.calendar_widget.calendar_position = above

A value of ``between`` will place the upcoming events list first, then the
calendar, then the past events list. A value of ``below`` will have the two
lists first, followed by the calendar.

The two lists, for upcoming and past events, are only shown if there are such
events presently in the system. You can control whether these lists show,
whether or not events are present in the system, with these too boolean
settings (default is true for both):::

    kotti_calendar.calendar_widget.show_upcoming_events = true
    kotti_calendar.calendar_widget.show_past_events = true

.. Note:: These two boolean settings apply only to the two lists that show on
          the calendar page; they do not apply to the upcoming events widget,
          described next.

Upcoming events widget
----------------------

kotti_calendar provides a upcoming events widget, which is disabled by default.
To enable the widget add the following to the ``pyramid.includes`` setting::

  pyramid.includes = kotti_calendar.widgets.includeme_upcoming_events

With this, the upcoming events will be shown in the right column of the site.

You can adjust how many events will be shown in the widget with set
``kotti_calendar.upcoming_events_widget.events_count`` to a different
value. It defaults to ``5``::

    kotti_calendar.upcoming_events_widget.events_count = 10

An appropriate combination of settings, should the upcoming_events_widget be
enabled, would be:::

    kotti_calendar.calendar_widget.show_upcoming_events = false
    kotti_calendar.calendar_widget.show_past_events = true
    kotti_calendar.calendar_widget.calendar_position = above

This would show upcoming events with the upcoming events widget in the right
column, and the calendar at the top of the main page, with the past events
list shown below it.

.. _FullCalendar jQuery plugin: http://arshaw.com/fullcalendar/
.. _Find out more about Kotti: http://pypi.python.org/pypi/Kotti
