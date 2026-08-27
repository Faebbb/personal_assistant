"""Колекція нотаток із пошуком і сортуванням за тегами."""

from __future__ import annotations

from typing import Dict, Iterator, List, Optional

from .models import Note, Tag


class NotesBook:
    """Колекція об’єктів ``Note`` із доступом за назвою нотатки."""

    def __init__(self) -> None:
        self.data: Dict[str, Note] = {}

    @staticmethod
    def _key(title: str) -> str:
        return title.strip().casefold()

    def add_note(self, note: Note) -> None:
        key = self._key(note.title)
        if key in self.data:
            raise ValueError(f"Нотатка з назвою '{note.title}' вже існує.")
        self.data[key] = note

    def find(self, title: str) -> Optional[Note]:
        return self.data.get(self._key(title))

    def rename(self, old_title: str, new_title: str) -> Note:
        old_key = self._key(old_title)
        note = self.data.get(old_key)
        if note is None:
            raise ValueError(f"Нотатку '{old_title}' не знайдено.")

        new_key = self._key(new_title)
        if new_key != old_key and new_key in self.data:
            raise ValueError(f"Нотатка '{new_title}' вже існує.")

        note.set_title(new_title)
        if new_key != old_key:
            del self.data[old_key]
            self.data[new_key] = note
        return note

    def delete(self, title: str) -> None:
        key = self._key(title)
        if key not in self.data:
            raise ValueError(f"Нотатку '{title}' не знайдено.")
        del self.data[key]

    def search(self, query: str) -> List[Note]:
        value = query.strip().casefold()
        if not value:
            return []

        results = []
        for note in self.data.values():
            if value in note.title.casefold() or value in note.text.casefold():
                results.append(note)
                continue
            if any(value in tag.value.casefold() for tag in note.tags):
                results.append(note)

        return sorted(results, key=lambda item: item.title.casefold())

    def search_by_tag(self, tag: str) -> List[Note]:
        value = Tag(tag).value
        result = [
            note
            for note in self.data.values()
            if any(item.value == value for item in note.tags)
        ]
        return sorted(result, key=lambda item: item.title.casefold())

    def all_notes(self) -> List[Note]:
        return sorted(
            self.data.values(),
            key=lambda item: item.created,
            reverse=True,
        )

    def sort_by_tags(self) -> List[Note]:
        """Сортує нотатки за тегами в алфавітному порядку, потім за назвою."""
        return sorted(self.data.values(), key=lambda item: item.tag_sort_key())

    def __len__(self) -> int:
        return len(self.data)

    def __iter__(self) -> Iterator[Note]:
        return iter(self.data.values())
