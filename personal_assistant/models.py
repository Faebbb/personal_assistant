"""Моделі даних для застосунку «Персональний помічник».

Модуль демонструє спадкування та композицію:
Field -> Name, Phone, Email, Birthday, Address, Tag.
Record містить валідовані поля контакту.
Note містить текст нотатки та колекцію об’єктів Tag.
"""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import List, Optional


class Field:
    """Базовий клас для полів даних із валідацією."""

    def __init__(self, value) -> None:
        self._value = None
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value) -> None:
        self._value = new_value

    def __str__(self) -> str:
        return str(self._value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._value!r})"


class Name(Field):
    """Ім’я контакту. Значення не може бути порожнім."""

    @Field.value.setter
    def value(self, new_value: str) -> None:
        value = str(new_value).strip() if new_value is not None else ""
        if not value:
            raise ValueError("Ім'я не може бути порожнім.")
        if len(value) > 100:
            raise ValueError("Ім'я занадто довге (максимум 100 символів).")
        self._value = value


class Phone(Field):
    """Український номер телефону у форматі +380XXXXXXXXX."""

    PHONE_PATTERN = re.compile(r"^\+380\d{9}$")

    @staticmethod
    def _normalize(phone: str) -> str:
        raw = str(phone).strip()
        digits = re.sub(r"\D", "", raw)

        if digits.startswith("380") and len(digits) == 12:
            return f"+{digits}"
        if digits.startswith("0") and len(digits) == 10:
            return f"+38{digits}"
        if len(digits) == 9:
            return f"+380{digits}"
        return raw

    @Field.value.setter
    def value(self, new_value: str) -> None:
        raw = str(new_value).strip() if new_value is not None else ""
        if not raw:
            raise ValueError("Номер телефону не може бути порожнім.")

        normalized = self._normalize(raw)
        if not self.PHONE_PATTERN.fullmatch(normalized):
            raise ValueError(
                "Некоректний номер телефону. "
                "Приклад: +380991234567 або 0991234567."
            )
        self._value = normalized


class Email(Field):
    """Email-адреса з базовою перевіркою формату."""

    EMAIL_PATTERN = re.compile(
        r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
        r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
        r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$"
    )

    @Field.value.setter
    def value(self, new_value: str) -> None:
        email = str(new_value).strip() if new_value is not None else ""
        if not email:
            raise ValueError("Email не може бути порожнім.")
        if len(email) > 254 or not self.EMAIL_PATTERN.fullmatch(email):
            raise ValueError(
                "Некоректний email. Приклад: user@example.com."
            )
        self._value = email


class Birthday(Field):
    """День народження, що зберігається як ``datetime.date``."""

    FORMATS = ("%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y")

    @Field.value.setter
    def value(self, new_value) -> None:
        if isinstance(new_value, date):
            birthday = new_value
        else:
            raw = str(new_value).strip() if new_value is not None else ""
            if not raw:
                raise ValueError("Дата народження не може бути порожньою.")

            birthday = None
            for date_format in self.FORMATS:
                try:
                    birthday = datetime.strptime(raw, date_format).date()
                    break
                except ValueError:
                    continue
            if birthday is None:
                raise ValueError(
                    "Некоректна дата. Використовуйте формат ДД.ММ.РРРР."
                )

        if birthday > date.today():
            raise ValueError("Дата народження не може бути у майбутньому.")
        self._value = birthday

    def days_until(self, today: Optional[date] = None) -> int:
        """Повертає кількість днів до найближчого дня народження."""
        today = today or date.today()
        month = self._value.month
        day = self._value.day

        for year in (today.year, today.year + 1):
            try:
                next_birthday = date(year, month, day)
            except ValueError:
                # Для 29 лютого в невисокосному році використовуємо 28 лютого.
                next_birthday = date(year, 2, 28)

            if next_birthday >= today:
                return (next_birthday - today).days

        return 0

    def __str__(self) -> str:
        return self._value.strftime("%d.%m.%Y")


class Address(Field):
    """Поштова адреса. Необов’язкова в Record, але перевіряється, якщо задана."""

    @Field.value.setter
    def value(self, new_value: str) -> None:
        address = str(new_value).strip() if new_value is not None else ""
        if not address:
            raise ValueError("Адреса не може бути порожньою.")
        if len(address) > 300:
            raise ValueError("Адреса занадто довга (максимум 300 символів).")
        self._value = address


class Tag(Field):
    """Нормалізований тег нотатки."""

    @Field.value.setter
    def value(self, new_value: str) -> None:
        tag = str(new_value).strip().lower().lstrip("#") if new_value else ""
        if not tag:
            raise ValueError("Тег не може бути порожнім.")
        if len(tag) > 50:
            raise ValueError("Тег занадто довгий (максимум 50 символів).")
        if any(char.isspace() for char in tag):
            raise ValueError("Тег не повинен містити пробіли.")
        self._value = tag


class Record:
    """Запис контакту, складений з об’єктів валідованих полів."""

    def __init__(self, name: str) -> None:
        self.name = Name(name)
        self.phones: List[Phone] = []
        self.email: Optional[Email] = None
        self.birthday: Optional[Birthday] = None
        self.address: Optional[Address] = None

    def add_phone(self, phone: str) -> None:
        phone_obj = Phone(phone)
        if any(item.value == phone_obj.value for item in self.phones):
            raise ValueError(f"Телефон {phone_obj.value} вже є у контакті.")
        self.phones.append(phone_obj)

    def remove_phone(self, phone: str) -> None:
        normalized = Phone(phone).value
        for item in self.phones:
            if item.value == normalized:
                self.phones.remove(item)
                return
        raise ValueError(f"Телефон {phone} не знайдено.")

    def edit_phone(self, old_phone: str, new_phone: str) -> None:
        normalized_old = Phone(old_phone).value
        new_phone_obj = Phone(new_phone)

        if any(
            item.value == new_phone_obj.value and item.value != normalized_old
            for item in self.phones
        ):
            raise ValueError(f"Телефон {new_phone_obj.value} вже є у контакті.")

        for index, item in enumerate(self.phones):
            if item.value == normalized_old:
                self.phones[index] = new_phone_obj
                return
        raise ValueError(f"Телефон {old_phone} не знайдено.")

    def find_phone(self, phone: str) -> Optional[Phone]:
        normalized = Phone(phone).value
        return next(
            (item for item in self.phones if item.value == normalized),
            None,
        )

    def add_email(self, email: str) -> None:
        self.email = Email(email)

    def remove_email(self) -> None:
        self.email = None

    def add_birthday(self, birthday: str) -> None:
        self.birthday = Birthday(birthday)

    def remove_birthday(self) -> None:
        self.birthday = None

    def set_address(self, address: str) -> None:
        self.address = Address(address)

    def remove_address(self) -> None:
        self.address = None

    def days_to_birthday(self) -> Optional[int]:
        if self.birthday is None:
            return None
        return self.birthday.days_until()

    def to_dict(self) -> dict:
        return {
            "name": self.name.value,
            "phones": [phone.value for phone in self.phones],
            "email": self.email.value if self.email else None,
            "address": self.address.value if self.address else None,
            "birthday": (
                self.birthday.value.isoformat() if self.birthday else None
            ),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Record":
        record = cls(data["name"])
        for phone in data.get("phones", []):
            record.add_phone(phone)
        if data.get("email"):
            record.add_email(data["email"])
        if data.get("address"):
            record.set_address(data["address"])
        if data.get("birthday"):
            record.add_birthday(data["birthday"])
        return record

    def __str__(self) -> str:
        phones = ", ".join(item.value for item in self.phones) or "—"
        email = self.email.value if self.email else "—"
        address = self.address.value if self.address else "—"
        birthday = str(self.birthday) if self.birthday else "—"
        days = self.days_to_birthday()
        days_text = f" (через {days} дн.)" if days is not None else ""

        return (
            f"👤 {self.name.value}\n"
            f"   📞 {phones}\n"
            f"   ✉️  {email}\n"
            f"   🏠 {address}\n"
            f"   🎂 {birthday}{days_text}"
        )


class Note:
    """Текстова нотатка з валідованими тегами."""

    def __init__(
        self,
        title: str,
        text: str = "",
        tags: Optional[List[str]] = None,
    ) -> None:
        self.title = self._validate_title(title)
        self.text = self._validate_text(text)
        self.tags: List[Tag] = []
        self.created = datetime.now().isoformat(timespec="seconds")

        if tags:
            for tag in tags:
                self.add_tag(tag)

    @staticmethod
    def _validate_title(title: str) -> str:
        value = str(title).strip() if title is not None else ""
        if not value:
            raise ValueError("Назва нотатки не може бути порожньою.")
        if len(value) > 150:
            raise ValueError(
                "Назва нотатки занадто довга (максимум 150 символів)."
            )
        return value

    @staticmethod
    def _validate_text(text: str) -> str:
        value = str(text).strip() if text is not None else ""
        if len(value) > 10000:
            raise ValueError(
                "Текст нотатки занадто довгий (максимум 10000 символів)."
            )
        return value

    def set_title(self, title: str) -> None:
        self.title = self._validate_title(title)

    def set_text(self, text: str) -> None:
        self.text = self._validate_text(text)

    def add_tag(self, tag: str) -> None:
        tag_obj = Tag(tag)
        if any(item.value == tag_obj.value for item in self.tags):
            return
        self.tags.append(tag_obj)

    def remove_tag(self, tag: str) -> None:
        value = Tag(tag).value
        for item in self.tags:
            if item.value == value:
                self.tags.remove(item)
                return
        raise ValueError(f"Тег '{tag}' не знайдено.")

    def replace_tags(self, tags: List[str]) -> None:
        validated: List[Tag] = []
        for tag in tags:
            tag_obj = Tag(tag)
            if not any(item.value == tag_obj.value for item in validated):
                validated.append(tag_obj)
        self.tags = validated

    def tag_sort_key(self) -> tuple:
        """Повертає ключ для стабільного алфавітного сортування за тегами."""
        values = tuple(sorted(tag.value for tag in self.tags))
        return (values if values else ("~",), self.title.lower())

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "text": self.text,
            "tags": [tag.value for tag in self.tags],
            "created": self.created,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Note":
        note = cls(
            title=data["title"],
            text=data.get("text", ""),
            tags=data.get("tags", []),
        )
        if data.get("created"):
            note.created = str(data["created"])
        return note

    def __str__(self) -> str:
        tags = ", ".join(f"#{tag.value}" for tag in self.tags) or "без тегів"
        preview = self.text[:80] + ("..." if len(self.text) > 80 else "")
        return (
            f"📝 {self.title}\n"
            f"   {preview or '—'}\n"
            f"   Теги: {tags}\n"
            f"   Створено: {self.created}"
        )
