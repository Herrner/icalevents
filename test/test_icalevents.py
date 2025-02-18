import unittest
from icalevents import icalevents
from datetime import date, timedelta, datetime
from time import sleep
from dateutil.relativedelta import relativedelta
from dateutil.tz import UTC, gettz
from re import search


class ICalEventsTests(unittest.TestCase):
    def test_events_url(self):
        url = "https://raw.githubusercontent.com/jazzband/icalevents/master/test/test_data/basic.ics"
        start = date(2017, 5, 18)
        end = date(2017, 5, 19)

        evs = icalevents.events(url=url, file=None, start=start, end=end)

        self.assertEqual(len(evs), 2, "two events are found")

    def test_events_start(self):
        ical = "test/test_data/basic.ics"
        start = date(2017, 5, 16)

        evs = icalevents.events(url=None, file=ical, start=start)

        self.assertEqual(len(evs), 3, "three events are found")

    def test_events(self):
        ical = "test/test_data/basic.ics"
        start = date(2017, 5, 18)
        end = date(2017, 5, 19)

        evs = icalevents.events(url=None, file=ical, start=start, end=end)

        self.assertEqual(len(evs), 2, "two events are found")

    def test_events_duration(self):
        ical = "test/test_data/duration.ics"
        start = date(2018, 1, 1)
        end = date(2018, 2, 1)

        evs = icalevents.events(file=ical, start=start, end=end)

        e1 = evs[0]
        self.assertEqual(e1.start.day, 10, "explicit event start")
        self.assertEqual(e1.end.day, 13, "implicit event end")

        e2 = evs[1]
        self.assertEqual(e2.start.hour, 10, "explicit event start")
        self.assertEqual(e2.end.hour, 13, "implicit event end")

        e3 = evs[2]
        self.assertEqual(e3.start.hour, 12, "explicit event start")
        self.assertEqual(e3.end.hour, 12, "implicit event end")

    def test_events_recurring(self):
        ical = "test/test_data/recurring.ics"
        start = date(2018, 10, 15)
        end = date(2018, 11, 15)

        evs = icalevents.events(file=ical, start=start, end=end)

        e1 = evs[1]
        self.assertEqual(e1.start.hour, 10, "check time with DST")
        self.assertEqual(
            e1.start.tzinfo.utcoffset(e1.start),
            timedelta(seconds=7200),
            "check UTC offset with DST",
        )

        e2 = evs[2]
        self.assertEqual(e2.start.hour, 10, "check time without DST")
        self.assertEqual(
            e2.start.tzinfo.utcoffset(e2.start),
            timedelta(seconds=3600),
            "check UTC offset without DST",
        )

        self.assertEqual(e2.start.day, 5, "Check observance of exdate.")

    def test_events_exdates(self):
        ical = "test/test_data/recurring.ics"
        start = date(2018, 6, 1)
        end = date(2018, 6, 30)

        evs = icalevents.events(file=ical, start=start, end=end)

        self.assertEqual(evs[0].start.day, 1, "check first recurrence.")
        self.assertEqual(evs[1].start.day, 15, "check first exdate.")
        self.assertEqual(evs[2].start.day, 29, "check second exdate.")

    def test_events_all_day_recurring(self):
        ical = "test/test_data/recurring.ics"
        start = date(2018, 10, 30)
        end = date(2018, 10, 31)

        evs = icalevents.events(file=ical, start=start, end=end)

        event_set = icalevents.events(url=None, file=ical, start=start, end=end)
        ev = event_set[0]

        self.assertEqual(len(event_set), 1)
        self.assertEqual(ev.summary, "Recurring All-day Event")
        self.assertEqual(ev.description, "All-day event recurring on tuesday each week")
        self.assertTrue(
            ev.all_day, "Recurring All-day Event's first instance is an all-day event"
        )

        start_2nd_instance = date(2018, 11, 6)
        end_2nd_instance = date(2018, 11, 7)

        event_set2 = icalevents.events(
            url=None, file=ical, start=start_2nd_instance, end=end_2nd_instance
        )
        ev_2 = event_set2[0]

        self.assertEqual(len(event_set2), 1)
        self.assertEqual(ev_2.summary, "Recurring All-day Event")
        self.assertEqual(
            ev_2.description, "All-day event recurring on tuesday each week"
        )
        self.assertTrue(
            ev_2.all_day,
            "Recurring All-day Event's second instance is an all-day event",
        )

    def test_events_rrule_until_all_day_ms(self):
        ical = "test/test_data/rrule_until_all_day_ms.ics"
        start = date(2021, 1, 1)
        end = date(2022, 1, 1)

        evs = icalevents.events(file=ical, start=start, end=end)
        ev_0 = evs[0]

        self.assertEqual(
            len(evs), 6, "Seven events and one is excluded"
        )  # rrule_until_all_day_ms has one exdate (EXDATE;TZID=W. Europe Standard Time:20210430T000000)
        self.assertEqual(
            ev_0.start, datetime(2021, 3, 19, 00, 0, 0, tzinfo=gettz("Europe/Berlin"))
        )
        self.assertEqual(ev_0.recurring, True, "Recurring all day event")
        self.assertEqual(ev_0.summary, "Away")

    def test_events_rrule_until_all_day_google(self):
        ical = "test/test_data/rrule_until_all_day_google.ics"
        start = date(2021, 1, 1)
        end = date(2022, 1, 1)

        evs = icalevents.events(file=ical, start=start, end=end)
        ev_2 = evs[2]

        self.assertEqual(len(evs), 3)
        self.assertEqual(
            ev_2.start, datetime(2021, 3, 24, 00, 0, 0, tzinfo=gettz("Europe/Zurich"))
        )
        self.assertEqual(ev_2.all_day, True, "All day event")
        self.assertEqual(ev_2.summary, "Busy")

    def test_events_rrule_until_only_date(self):
        ical = "test/test_data/rrule_until_only_date.ics"
        start = date(2021, 9, 29)
        end = date(2021, 10, 19)
        evs = icalevents.events(file=ical, start=start, end=end)
        self.assertEqual(len(evs), 8)
        self.assertEqual(
            evs[0].start,
            datetime(2021, 9, 29, 13, 0, 0, 0, tzinfo=gettz("America/Boise")),
        )
        self.assertEqual(
            evs[-1].start,
            datetime(2021, 10, 18, 13, 0, 0, 0, tzinfo=gettz("America/Boise")),
        )

    def test_events_rrule_until(self):
        ical = "test/test_data/rrule_until.ics"
        start = date(2019, 4, 2)
        end = date(2019, 4, 3)

        evs = icalevents.events(file=ical, start=start, end=end)

        self.assertEqual(len(evs), 2)
        self.assertEqual(evs[0].recurring, True)
        self.assertEqual(evs[0].summary, "Recurring All-day Event")
        self.assertEqual(evs[1].recurring, True)
        self.assertEqual(evs[1].summary, "Daily lunch event")

    def test_event_attributes(self):
        ical = "test/test_data/basic.ics"
        start = date(2017, 7, 12)
        end = date(2017, 7, 13)

        ev = icalevents.events(url=None, file=ical, start=start, end=end)[0]

        self.assertEqual(ev.summary, "graue Restmülltonne")
        self.assertEqual(ev.description, "graue Restmülltonne nicht vergessen!")
        self.assertTrue(ev.all_day)

    def test_event_recurring_attribute(self):
        ical = "test/test_data/basic.ics"
        start = date(2017, 7, 12)
        end = date(2017, 7, 13)

        ev = icalevents.events(url=None, file=ical, start=start, end=end)[0]
        self.assertEqual(
            ev.recurring, False, "check recurring=False for non recurring event"
        )

        ical = "test/test_data/recurring.ics"
        start = date(2018, 10, 15)
        end = date(2018, 11, 15)

        evs = icalevents.events(file=ical, start=start, end=end)

        e1 = evs[1]
        e2 = evs[2]
        self.assertEqual(
            e1.recurring, True, "check recurring=True for recurring event (1)"
        )
        self.assertEqual(
            e2.recurring, True, "check recurring=True for recurring event (2)"
        )

    def test_events_async_url(self):
        url = "https://raw.githubusercontent.com/jazzband/icalevents/master/test/test_data/basic.ics"
        start = date(2017, 5, 18)
        end = date(2017, 5, 19)
        key = "basic"

        icalevents.events_async(key, url=url, file=None, start=start, end=end)

        sleep(4)

        self.assertTrue(icalevents.all_done(key), "request is finished")
        self.assertEqual(len(icalevents.latest_events(key)), 2, "two events are found")

    def test_events_async(self):
        ical = "test/test_data/basic.ics"
        start = date(2017, 5, 18)
        end = date(2017, 5, 19)
        key = "basic"

        icalevents.events_async(key, url=None, file=ical, start=start, end=end)

        sleep(4)

        self.assertTrue(icalevents.all_done(key), "request is finished")
        self.assertEqual(len(icalevents.latest_events(key)), 2, "two events are found")

    def test_request_data(self):
        ical = "test/test_data/basic.ics"
        start = date(2017, 5, 18)
        end = date(2017, 5, 19)
        key = "basic"

        icalevents.request_data(
            key,
            url=None,
            file=ical,
            string_content=None,
            start=start,
            end=end,
            fix_apple=False,
        )

        self.assertTrue(icalevents.all_done(key), "request is finished")
        self.assertEqual(len(icalevents.latest_events(key)), 2, "two events are found")

    def test_string_data(self):
        ical = "test/test_data/basic.ics"

        with open(ical, mode="rb") as f:
            string_content = f.read()

        start = date(2017, 5, 18)
        end = date(2017, 5, 19)
        key = "basic"

        icalevents.request_data(
            key,
            url=None,
            file=None,
            string_content=string_content,
            start=start,
            end=end,
            fix_apple=False,
        )

        self.assertTrue(icalevents.all_done(key), "request is finished")
        self.assertEqual(len(icalevents.latest_events(key)), 2, "two events are found")

    def test_event_str(self):
        ical = "test/test_data/duration.ics"
        start = date(2018, 1, 1)
        end = date(2018, 2, 1)
        n = datetime.now(UTC)
        m = relativedelta(hour=0, minute=0, second=0, microsecond=0)

        evs = icalevents.events(file=ical, start=start, end=end)

        e1 = evs[0]
        self.assertIsNotNone(
            search(r"ended", str(e1.copy_to(n - relativedelta(days=5) + m))),
            "stringify past event",
        )
        self.assertIsNotNone(
            search(r"today", str(e1.copy_to(n - relativedelta(days=1) + m))),
            "stringify ongoing event",
        )
        self.assertIsNotNone(
            search(r"days left", str(e1.copy_to(n + relativedelta(days=3) + m))),
            "stringify future event",
        )

        e2 = evs[1]
        self.assertIsNotNone(
            search(r"ended", str(e2.copy_to(n - relativedelta(hours=5)))),
            "stringify past event",
        )
        self.assertIsNotNone(
            search(r"now", str(e2.copy_to(n - relativedelta(hours=1)))),
            "stringify ongoing event",
        )
        self.assertIsNotNone(
            search(r"hours left", str(e2.copy_to(n + relativedelta(hours=3)))),
            "stringify future event",
        )
        self.assertIsNotNone(
            search(r"days left", str(e2.copy_to(n + relativedelta(days=3)))),
            "stringify future event",
        )

    def test_events_no_description(self):
        ical = "test/test_data/no_description.ics"
        start = date(2018, 10, 15)
        end = date(2018, 11, 15)

        e1 = icalevents.events(file=ical, start=start, end=end)[0]

        self.assertEqual(e1.description, None)
        self.assertEqual(e1.summary, None)
        self.assertEqual(e1.location, None)

    def test_event_created_last_modified(self):
        ical = "test/test_data/created_last_modified.ics"
        start = date(2017, 7, 12)
        end = date(2017, 7, 15)

        events = icalevents.events(url=None, file=ical, start=start, end=end)

        self.assertEqual(events[0].created, datetime(2017, 1, 3, 7, 4, 1, tzinfo=UTC))
        self.assertEqual(
            events[0].last_modified, datetime(2017, 7, 11, 14, 0, 50, tzinfo=UTC)
        )

        self.assertEqual(events[1].created, datetime(2017, 1, 4, 8, 4, 1, tzinfo=UTC))
        self.assertEqual(
            events[1].last_modified, datetime(2017, 1, 4, 8, 4, 1, tzinfo=UTC)
        )

        self.assertEqual(events[2].created, None)
        self.assertEqual(events[2].last_modified, None)

    def test_event_categories(self):
        ical = "test/test_data/categories_test.ics"
        start = date(2020, 11, 10)
        end = date(2020, 11, 19)
        events = icalevents.events(url=None, file=ical, start=start, end=end)
        self.assertEqual(
            events[0].categories, ["In19-S04-IT2403"], "event 1 is not equal"
        )
        self.assertEqual(
            events[1].categories,
            ["In19-S04-IT2406", "In19-S04-IT2405"],
            "event 2 is not equal",
        )

    def test_google_timezone(self):
        ical = "test/test_data/google_tz.ics"
        start = date(2021, 1, 1)
        end = date(2021, 12, 31)

        evs = icalevents.events(file=ical, start=start, end=end)

        e1 = evs[0]
        self.assertEqual(e1.start.hour, 0, "check start of the day")
        self.assertEqual(
            e1.start.tzinfo, gettz("Europe/Zurich"), "check tz as specified in calendar"
        )

    def test_ms_timezone(self):
        ical = "test/test_data/ms_tz.ics"
        start = date(2021, 1, 1)
        end = date(2021, 12, 31)

        evs = icalevents.events(file=ical, start=start, end=end)

        e1 = evs[0]
        self.assertEqual(e1.start.hour, 0, "check start of the day")
        self.assertEqual(
            e1.start.tzinfo, gettz("Europe/Berlin"), "check tz as specified in calendar"
        )

    def test_recurence_id_ms(self):
        ical = "test/test_data/recurrenceid_ms.ics"
        start = date(2021, 1, 1)
        end = date(2021, 12, 31)

        evs = icalevents.events(file=ical, start=start, end=end)

        self.assertEqual(len(evs), 42, "42 events in total - one was moved")

    def test_recurence_id_google(self):
        ical = "test/test_data/recurrenceid_google.ics"
        start = date(2021, 1, 1)
        end = date(2021, 12, 31)

        evs = icalevents.events(file=ical, start=start, end=end)

        self.assertEqual(len(evs), 4, "4 events in total")

    def test_cest(self):
        ical = "test/test_data/cest.ics"
        start = date(2010, 1, 1)
        end = date(2023, 12, 31)

        evs = icalevents.events(file=ical, start=start, end=end)

        self.assertEqual(
            len(evs), 239, "239 events in total"
        )  # 102 events / 91 + 11 recurring

    def test_cest_2021_03(self):
        ical = "test/test_data/cest.ics"
        start = date(2021, 3, 1)
        end = date(2021, 3, 31)

        evs = icalevents.events(file=ical, start=start, end=end)
        self.assertEqual(len(evs), 30, "30 in march")

    def test_cest_2021_04(self):
        ical = "test/test_data/cest.ics"
        start = date(2021, 4, 1)
        end = date(2021, 5, 1)

        evs = icalevents.events(file=ical, start=start, end=end)
        self.assertEqual(len(evs), 27, "27 in april")

    def test_cest_2021_05(self):
        ical = "test/test_data/cest.ics"
        start = date(2021, 5, 1)
        end = date(2021, 6, 1)

        evs = icalevents.events(file=ical, start=start, end=end)
        self.assertEqual(len(evs), 20, "20 in mai")

    def test_cest_1(self):
        ical = "test/test_data/cest_every_day_for_one_year.ics"
        start = date(2020, 1, 1)
        end = date(2024, 12, 31)

        evs = icalevents.events(file=ical, start=start, end=end)

        self.assertEqual(
            len(evs),
            366,
            "366 events in total - one year + 1 (2021-11-11 to 2022-11-11)",
        )

    def test_cest_2(self):
        ical = "test/test_data/cest_every_second_day_for_one_year.ics"
        start = date(2020, 1, 1)
        end = date(2024, 12, 31)

        evs = icalevents.events(file=ical, start=start, end=end)
        self.assertEqual(
            len(evs), 183, "183 events in total - one year (2021-11-11 to 2022-11-11)"
        )

    def test_cest_3(self):
        ical = "test/test_data/cest_with_deleted.ics"
        start = date(2020, 1, 1)
        end = date(2024, 12, 31)

        evs = icalevents.events(file=ical, start=start, end=end)
        self.assertEqual(
            len(evs), 3, "3 events in total - 5 events in rrule but 2 deleted"
        )

    def test_transparent(self):
        ical = "test/test_data/transparent.ics"
        start = date(2021, 1, 1)
        end = date(2021, 12, 31)

        [e1, e2] = icalevents.events(file=ical, start=start, end=end)

        self.assertEqual(e1.transparent, True, "respect transparency")
        self.assertEqual(e2.transparent, False, "respect opaqueness")

    def test_status_and_url(self):
        ical = "test/test_data/status_and_url.ics"
        start = date(2018, 10, 30)
        end = date(2018, 10, 31)

        [ev1, ev2, ev3, ev4, ev5] = icalevents.events(file=ical, start=start, end=end)
        self.assertEqual(ev1.status, "TENTATIVE")
        self.assertEqual(ev1.url, None)
        self.assertEqual(ev2.status, "CONFIRMED")
        self.assertEqual(ev2.url, "https://example.com/")
        self.assertEqual(ev3.status, "CANCELLED")
        self.assertEqual(ev4.status, "CANCELLED")
        self.assertEqual(ev5.status, None)

    def test_recurrence_tz(self):
        ical = "test/test_data/recurrence_tz.ics"
        start = datetime(2021, 10, 24, 00, 0, 0, tzinfo=gettz("Australia/Sydney"))
        end = datetime(2021, 10, 26, 00, 0, 0, tzinfo=gettz("Australia/Sydney"))

        [e1] = icalevents.events(file=ical, start=start, end=end)
        expect = datetime(2021, 10, 24, 9, 0, 0, tzinfo=gettz("Australia/Sydney"))
        self.assertEqual(
            e1.start, expect, "Recurring event matches event in ical (Issue #89)"
        )

    def test_attenddees_have_params(self):
        ical = "test/test_data/response.ics"
        start = date(2021, 1, 1)
        end = date(2021, 12, 31)

        [e1] = icalevents.events(file=ical, start=start, end=end)

        self.assertEqual(e1.attendee.params["PARTSTAT"], "DECLINED", "add paarams")
        self.assertEqual(
            e1.attendee, "mailto:calendar@gmail.com", "still is like a string"
        )

    def test_attenddees_can_be_multiple(self):
        ical = "test/test_data/multi_attendee_response.ics"
        start = date(2021, 1, 1)
        end = date(2021, 12, 31)

        [e1] = icalevents.events(file=ical, start=start, end=end)

        self.assertEqual(e1.attendee[0].params["PARTSTAT"], "DECLINED", "add paarams")
        self.assertEqual(
            e1.attendee[0], "mailto:calendar@gmail.com", "we have a list of attendees"
        )
        self.assertEqual(
            e1.attendee[1],
            "mailto:calendar@microsoft.com",
            "we have more than one attendee",
        )

    def test_floating(self):
        ical = "test/test_data/floating.ics"
        start = date(2021, 1, 1)
        end = date(2021, 12, 31)

        [e1, e2] = icalevents.events(file=ical, start=start, end=end)

        self.assertEqual(e1.transparent, True, "respect transparency")
        self.assertEqual(e1.start.hour, 0, "check start of the day")
        self.assertEqual(e1.end.hour, 0, "check end of the day")
        self.assertEqual(e1.floating, True, "respect floating time")
        self.assertEqual(e1.start.tzinfo, UTC, "check tz as default utc")

        self.assertEqual(e2.transparent, False, "respect transparency")
        self.assertEqual(e2.start.hour, 6, "check start of the day")
        self.assertEqual(e2.end.hour, 14, "check end of the day")
        self.assertEqual(e2.floating, False, "respect floating time")
        self.assertEqual(e2.start.tzinfo, UTC, "check tz as default utc")

    def test_non_floating(self):
        ical = "test/test_data/non_floating.ics"
        start = date(2021, 1, 1)
        end = date(2021, 12, 31)

        [e1, e2] = icalevents.events(file=ical, start=start, end=end)

        self.assertEqual(e1.transparent, True, "respect transparency")
        self.assertEqual(e1.start.hour, 0, "check start of the day")
        self.assertEqual(e1.end.hour, 0, "check end of the day")
        self.assertEqual(e1.floating, False, "respect floating time")
        self.assertEqual(
            e1.start.tzinfo, gettz("Europe/Zurich"), "check tz as specified in calendar"
        )

        self.assertEqual(e2.transparent, False, "respect transparency")
        self.assertEqual(e2.start.hour, 8, "check start of the day")
        self.assertEqual(e2.end.hour, 16, "check end of the day")
        self.assertEqual(e2.floating, False, "respect floating time")
        self.assertEqual(
            e1.start.tzinfo, gettz("Europe/Zurich"), "check tz as specified in calendar"
        )

    def test_recurring_override(self):
        ical = "test/test_data/recurring_override.ics"
        start = date(2021, 11, 23)
        end = date(2021, 11, 24)

        [e0, e1, e2] = icalevents.events(file=ical, start=start, end=end)

        # Here all dates are in utc because the .ics has two timezones and this causes a transformation
        self.assertEqual(e0.start, datetime(2021, 11, 23, 9, 0, tzinfo=UTC))
        self.assertEqual(e1.start, datetime(2021, 11, 23, 10, 45, tzinfo=UTC))
        self.assertEqual(
            e2.start,
            datetime(2021, 11, 23, 13, 0, tzinfo=UTC),
            "moved 1 hour from 12:00 to 13:00",
        )
