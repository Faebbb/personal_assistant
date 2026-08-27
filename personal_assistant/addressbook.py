"""Контейнер адресної книги для зберігання контактів."""

from __future__ import annotations

from typing import Dict, Iterator, List, Optional

from .models import Record


class AddressBook:
    """Колекція об’єктів ``Record`` із доступом за ім’ям контакту."""

    def __init__(self) -> None:
        self.data: Dict[str, Record] = {}

    @staticmethod
    def _key(name: str) -> str:
        return name.strip().casefold()

    def add_record(self, record: Record) -> None:
        key = self._key(record.name.value)
        if key in self.data:
            raise ValueError(f"Контакт '{record.name.value}' вже існує.")
        self.data[key] = record

    def find(self, name: str) -> Optional[Record]:
        return self.data.get(self._key(name))

    def rename(self, old_name: str, new_name: str) -> Record:
        old_key = self._key(old_name)
        record = self.data.get(old_key)
        if record is None:
            raise ValueError(f"Контакт '{old_name}' не знайдено.")

        new_key = self._key(new_name)
        if new_key != old_key and new_key in self.data:
            raise ValueError(f"Контакт '{new_name}' вже існує.")

        record.name.value = new_name
        if new_key != old_key:
            del self.data[old_key]
            self.data[new_key] = record
        return record

    def delete(self, name: str) -> None:
        key = self._key(name)
        if key not in self.data:
            raise ValueError(f"Контакт '{name}' не знайдено.")
        del self.data[key]

    def search(self, query: str) -> List[Record]:
        value = query.strip().casefold()
        if not value:
            return []

        results: List[Record] = []
        for record in self.data.values():
            searchable = [record.name.value.casefold()]
            searchable.extend(phone.value.casefold() for phone in record.phones)
            if record.email:
                searchable.append(record.email.value.casefold())
            if record.address:
                searchable.append(record.address.value.casefold())

            if any(value in item for item in searchable):
                results.append(record)

        return sorted(results, key=lambda item: item.name.value.casefold())

    def upcoming_birthdays(self, days: int = 7) -> List[Record]:
        if days < 0:
            raise ValueError("Кількість днів не може бути від'ємною.")
        if days > 366:
            raise ValueError("Вкажіть період від 0 до 366 днів.")

        result = []
        for record in self.data.values():
            days_left = record.days_to_birthday()
            if days_left is not None and 0 <= days_left <= days:
                result.append(record)

        return sorted(
            result,
            key=lambda item: (
                item.days_to_birthday()
                if item.days_to_birthday() is not None
                else 367,
                item.name.value.casefold(),
            ),
        )

    def all_records(self) -> List[Record]:
        return sorted(
            self.data.values(),
            key=lambda item: item.name.value.casefold(),
        )

    def __len__(self) -> int:
        return len(self.data)

    def __iter__(self) -> Iterator[Record]:
        return iter(self.data.values())
