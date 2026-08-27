"""Основні регресійні тести для «Персонального помічника»."""

import unittest
from datetime import date
from unittest.mock import patch

from personal_assistant.addressbook import AddressBook
from personal_assistant.models import Birthday, Email, Note, Phone, Record
from personal_assistant.notes import NotesBook


class FieldValidationTests(unittest.TestCase):
    def test_phone_normalization(self):
        self.assertEqual(Phone("099 123-45-67").value, "+380991234567")
        self.assertEqual(Phone("+380991234567").value, "+380991234567")

    def test_invalid_phone(self):
        with self.assertRaises(ValueError):
            Phone("123")

    def test_email_validation(self):
        self.assertEqual(Email("user@example.com").value, "user@example.com")
        with self.assertRaises(ValueError):
            Email("wrong-email")

    def test_future_birthday_rejected(self):
        future_year = date.today().year + 1
        with self.assertRaises(ValueError):
            Birthday(f"01.01.{future_year}")

    def test_leap_day_does_not_crash(self):
        birthday = Birthday("29.02.2000")
        with patch("personal_assistant.models.date") as mocked_date:
            mocked_date.today.return_value = date(2025, 2, 27)
            mocked_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)
            days = birthday.days_until(today=date(2025, 2, 27))
        self.assertEqual(days, 1)


class AddressBookTests(unittest.TestCase):
    def test_add_find_search_delete(self):
        book = AddressBook()
        record = Record("Alex")
        record.add_phone("0991234567")
        record.add_email("alex@example.com")
        record.set_address("Kyiv")
        book.add_record(record)

        self.assertIs(book.find("alex"), record)
        self.assertIn(record, book.search("99123"))
        self.assertIn(record, book.search("example.com"))
        self.assertIn(record, book.search("kyiv"))

        book.delete("Alex")
        self.assertIsNone(book.find("Alex"))

    def test_duplicate_contact_rejected(self):
        book = AddressBook()
        book.add_record(Record("Alex"))
        with self.assertRaises(ValueError):
            book.add_record(Record("alex"))

    def test_today_birthday_is_sorted_first(self):
        today = date.today()
        year = max(1900, today.year - 20)
        record = Record("Today")
        record.add_birthday(f"{today.day:02}.{today.month:02}.{year}")
        book = AddressBook()
        book.add_record(record)
        self.assertEqual(book.upcoming_birthdays(0)[0].name.value, "Today")


class NotesBookTests(unittest.TestCase):
    def test_search_and_tag_sorting(self):
        notes = NotesBook()
        notes.add_note(Note("B", "text", ["work"]))
        notes.add_note(Note("A", "python text", ["python"]))
        notes.add_note(Note("C", "other", []))

        self.assertEqual(notes.search("python")[0].title, "A")
        self.assertEqual(notes.search_by_tag("#work")[0].title, "B")
        self.assertEqual(
            [note.title for note in notes.sort_by_tags()],
            ["A", "B", "C"],
        )

    def test_duplicate_note_rejected(self):
        notes = NotesBook()
        notes.add_note(Note("Idea"))
        with self.assertRaises(ValueError):
            notes.add_note(Note("idea"))


if __name__ == "__main__":
    unittest.main()
