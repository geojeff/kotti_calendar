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
followed by a list of upcoming and past events. You have a choice of displaying
the upcoming and past events list or not, and whether it is shown above or
below the calendar.

And, if the events list is shown, you can control which goes first, upcoming or
past events.

Scope of Events Shown
---------------------

The default calendar will only show events that have been added to the calendar
itself. There are two other scopes available:

- site wide: Show all events found by an exhaustive search of the site database.
- recursive: Show events found in the calendar itself, in the current context
  (where the calendar "lives"), and in any content nodes contained within.

The ``site wide`` choice is useful for a site that has a single calendar, and
the events need to be stored in different places around the site. For example,
if an add-on content type is a container for events, as with an "ArtClass" type
that contains events for class periods, the __init__.py setup for the add-on
can set the type_info.addable_to of Event, such as:::

    Event.type_info.addable_to.append("ArtClass")

The ``recursive`` choice is useful for a site that has a need to show more than
one calendar. Imagine a site for a sporting league, in which there are two
divisions, "East" and "West." There are separate content hierarchies for these
divisions, with events held in some fashion within them. A calendar could be
added to each division, and the scope set to ``recursive`` to show all events
for the given division.

Upcoming events widget
----------------------

kotti_calendar provides a upcoming events widget, which is disabled by default.
To enable the widget in a slot add the following configuration line::

  kotti_calendar.upcoming_events_widget.slot = left

where the value for ``slot`` is one of:::

  none, left, right, abovecontent, belowcontent, beforebodyend

Set this to ``none`` if you don't want the widget to show in a slot (the
default).

You can adjust how many events will be shown in the upcoming events widget, if
shown, with ``kotti_calendar.upcoming_events_widget.events_count``.  It
defaults to ``5``::

    kotti_calendar.upcoming_events_widget.events_count = 10

.. _FullCalendar jQuery plugin: http://arshaw.com/fullcalendar/
.. _Find out more about Kotti: http://pypi.python.org/pypi/Kotti
