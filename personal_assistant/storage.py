"""Постійне JSON-сховище для контактів і нотаток."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .models import Note, Record

if TYPE_CHECKING:
    from .addressbook import AddressBook
    from .notes import NotesBook


DATA_DIR = Path.home() / ".personal_assistant"
CONTACTS_FILE = DATA_DIR / "contacts.json"
NOTES_FILE = DATA_DIR / "notes.json"


def ensure_data_dir() -> None:
    """Створює папку даних застосунку, якщо вона ще не існує."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _write_json(path: Path, data: Any) -> None:
    """Атомарно записує JSON, щоб зменшити ризик пошкодження даних."""
    ensure_data_dir()
    temporary = path.with_suffix(path.suffix + ".tmp")
    try:
        with temporary.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        temporary.replace(path)
    except OSError as error:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass
        raise OSError(f"Не вдалося зберегти дані у {path}: {error}") from error


def _read_json(path: Path) -> list:
    """Зчитує список у форматі JSON з диска."""
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as error:
        raise ValueError(f"Файл {path.name} пошкоджено: {error}") from error
    except OSError as error:
        raise OSError(f"Не вдалося прочитати {path}: {error}") from error

    if not isinstance(data, list):
        raise ValueError(f"Некоректний формат даних у файлі {path.name}.")
    return data


def save_address_book(book: "AddressBook") -> None:
    _write_json(CONTACTS_FILE, [record.to_dict() for record in book])


def load_address_book(book: "AddressBook") -> list[str]:
    warnings = []
    try:
        data = _read_json(CONTACTS_FILE)
    except (ValueError, OSError) as error:
        return [str(error)]

    for index, item in enumerate(data, start=1):
        try:
            if not isinstance(item, dict):
                raise ValueError("запис має бути об'єктом")
            record = Record.from_dict(item)
            book.data[record.name.value.casefold()] = record
        except (KeyError, TypeError, ValueError) as error:
            warnings.append(f"Контакт #{index} пропущено: {error}")
    return warnings


def save_notes_book(notes: "NotesBook") -> None:
    _write_json(NOTES_FILE, [note.to_dict() for note in notes])


def load_notes_book(notes: "NotesBook") -> list[str]:
    warnings = []
    try:
        data = _read_json(NOTES_FILE)
    except (ValueError, OSError) as error:
        return [str(error)]

    for index, item in enumerate(data, start=1):
        try:
            if not isinstance(item, dict):
                raise ValueError("запис має бути об'єктом")
            note = Note.from_dict(item)
            notes.data[note.title.casefold()] = note
        except (KeyError, TypeError, ValueError) as error:
            warnings.append(f"Нотатку #{index} пропущено: {error}")
    return warnings


def save_all(book: "AddressBook", notes: "NotesBook") -> None:
    save_address_book(book)
    save_notes_book(notes)


def load_all(book: "AddressBook", notes: "NotesBook") -> list[str]:
    warnings = []
    warnings.extend(load_address_book(book))
    warnings.extend(load_notes_book(notes))
    return warnings
