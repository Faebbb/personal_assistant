"""Інтерфейс командного рядка для «Персонального помічника»."""

from __future__ import annotations

from typing import Callable

from .addressbook import AddressBook
from .models import Note, Phone, Record
from .notes import NotesBook
from .storage import DATA_DIR, load_all, save_all

CLEAR_VALUE = "-"


def input_non_empty(prompt: str) -> str:
    """Запитує значення, доки користувач не введе непорожній рядок."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Поле не може бути порожнім. Спробуйте ще раз.")


def input_optional(prompt: str) -> str:
    """Зчитує необов’язкове значення."""
    return input(prompt).strip()


def print_help() -> None:
    print(
        """
╔══════════════════════════════════════════════════════════════════╗
║                 ПЕРСОНАЛЬНИЙ ПОМІЧНИК — КОМАНДИ                 ║
╠══════════════════════════════════════════════════════════════════╣
║  КОНТАКТИ                                                        ║
║  add-contact          — додати контакт                           ║
║  edit-contact         — редагувати контакт                       ║
║  delete-contact       — видалити контакт                         ║
║  search-contact       — пошук контактів                          ║
║  all-contacts         — показати всі контакти                    ║
║  birthdays [N]        — дні народження протягом N днів (7)       ║
║                                                                  ║
║  НОТАТКИ                                                         ║
║  add-note             — додати нотатку з тегами                  ║
║  edit-note            — редагувати нотатку                       ║
║  delete-note          — видалити нотатку                         ║
║  search-note          — пошук за назвою, текстом або тегом       ║
║  search-tag [tag]     — пошук нотаток за точним тегом            ║
║  all-notes            — показати нотатки (нові спочатку)         ║
║  sort-notes-tag       — сортувати нотатки за тегами              ║
║                                                                  ║
║  help / ?             — показати цю довідку                      ║
║  exit / quit / close  — зберегти дані та вийти                   ║
╚══════════════════════════════════════════════════════════════════╝
Під час редагування введіть '-' для очищення email, адреси,
дня народження, тексту нотатки або списку тегів.
"""
    )


def _print_items(items) -> None:
    for item in items:
        print("-" * 48)
        print(item)


def cmd_add_contact(book: AddressBook) -> None:
    print("\n--- Додавання контакту ---")
    name = input_non_empty("Ім'я: ")
    if book.find(name):
        print(f"❌ Контакт '{name}' вже існує.")
        return

    record = Record(name)

    while True:
        phone = input_optional("Телефон (Enter — пропустити/завершити): ")
        if not phone:
            break
        try:
            record.add_phone(phone)
            print(f"   ✓ Додано: {record.phones[-1].value}")
        except ValueError as error:
            print(f"❌ {error}")

    while True:
        email = input_optional("Email (Enter — пропустити): ")
        if not email:
            break
        try:
            record.add_email(email)
            break
        except ValueError as error:
            print(f"❌ {error}")

    while True:
        address = input_optional("Адреса (Enter — пропустити): ")
        if not address:
            break
        try:
            record.set_address(address)
            break
        except ValueError as error:
            print(f"❌ {error}")

    while True:
        birthday = input_optional(
            "День народження (ДД.ММ.РРРР, Enter — пропустити): "
        )
        if not birthday:
            break
        try:
            record.add_birthday(birthday)
            break
        except ValueError as error:
            print(f"❌ {error}")

    book.add_record(record)
    print(f"✅ Контакт '{record.name.value}' додано.")


def _replace_phones_safely(record: Record) -> None:
    """Перевіряє всі нові телефони перед заміною старого списку."""
    new_phones = []
    print("Введіть новий список телефонів. Enter — завершити.")
    while True:
        raw_phone = input_optional("Телефон: ")
        if not raw_phone:
            break
        try:
            phone = Phone(raw_phone)
            if any(item.value == phone.value for item in new_phones):
                raise ValueError(f"Телефон {phone.value} вже введено.")
            new_phones.append(phone)
        except ValueError as error:
            print(f"❌ {error}")

    record.phones = new_phones


def cmd_edit_contact(book: AddressBook) -> None:
    print("\n--- Редагування контакту ---")
    name = input_non_empty("Ім'я контакту: ")
    record = book.find(name)
    if record is None:
        print(f"❌ Контакт '{name}' не знайдено.")
        return

    print(f"Поточні дані:\n{record}\n")
    print("Enter — залишити без змін, '-' — очистити необов'язкове поле.")

    new_name = input_optional(f"Нове ім'я [{record.name.value}]: ")
    if new_name:
        record = book.rename(name, new_name)

    if input_optional("Замінити список телефонів? (y/N): ").casefold() == "y":
        _replace_phones_safely(record)

    current_email = record.email.value if record.email else "—"
    email = input_optional(f"Email [{current_email}]: ")
    if email == CLEAR_VALUE:
        record.remove_email()
    elif email:
        record.add_email(email)

    current_address = record.address.value if record.address else "—"
    address = input_optional(f"Адреса [{current_address}]: ")
    if address == CLEAR_VALUE:
        record.remove_address()
    elif address:
        record.set_address(address)

    current_birthday = str(record.birthday) if record.birthday else "—"
    birthday = input_optional(f"День народження [{current_birthday}]: ")
    if birthday == CLEAR_VALUE:
        record.remove_birthday()
    elif birthday:
        record.add_birthday(birthday)

    print(f"✅ Контакт '{record.name.value}' оновлено.")


def cmd_delete_contact(book: AddressBook) -> None:
    name = input_non_empty("Ім'я контакту для видалення: ")
    book.delete(name)
    print(f"✅ Контакт '{name}' видалено.")


def cmd_search_contact(book: AddressBook) -> None:
    query = input_non_empty("Пошук (ім'я / телефон / email / адреса): ")
    results = book.search(query)
    if not results:
        print("Нічого не знайдено.")
        return
    print(f"\nЗнайдено: {len(results)}")
    _print_items(results)


def cmd_all_contacts(book: AddressBook) -> None:
    records = book.all_records()
    if not records:
        print("Книга контактів порожня.")
        return
    print(f"\nУсього контактів: {len(records)}")
    _print_items(records)


def cmd_birthdays(book: AddressBook, days: int = 7) -> None:
    upcoming = book.upcoming_birthdays(days)
    if not upcoming:
        print(f"Немає днів народження протягом наступних {days} днів.")
        return

    print(f"\n🎂 Дні народження протягом {days} днів:")
    for record in upcoming:
        days_left = record.days_to_birthday()
        print(
            f"  • {record.name.value}: {record.birthday} "
            f"(через {days_left} дн.)"
        )


def cmd_add_note(notes: NotesBook) -> None:
    print("\n--- Додавання нотатки ---")
    title = input_non_empty("Назва: ")
    if notes.find(title):
        print(f"❌ Нотатка '{title}' вже існує.")
        return

    text = input_optional("Текст: ")
    tags_raw = input_optional("Теги через кому (напр. робота, python): ")
    tags = [item.strip() for item in tags_raw.split(",") if item.strip()]
    notes.add_note(Note(title=title, text=text, tags=tags))
    print(f"✅ Нотатку '{title}' додано.")


def cmd_edit_note(notes: NotesBook) -> None:
    print("\n--- Редагування нотатки ---")
    title = input_non_empty("Назва нотатки: ")
    note = notes.find(title)
    if note is None:
        print(f"❌ Нотатку '{title}' не знайдено.")
        return

    print(f"Поточна нотатка:\n{note}\n")
    print("Enter — залишити без змін, '-' — очистити текст або теги.")

    new_title = input_optional(f"Нова назва [{note.title}]: ")
    if new_title:
        note = notes.rename(title, new_title)

    new_text = input_optional("Новий текст: ")
    if new_text == CLEAR_VALUE:
        note.set_text("")
    elif new_text:
        note.set_text(new_text)

    current_tags = ", ".join(tag.value for tag in note.tags) or "—"
    tags_raw = input_optional(f"Теги через кому [{current_tags}]: ")
    if tags_raw == CLEAR_VALUE:
        note.replace_tags([])
    elif tags_raw:
        tags = [item.strip() for item in tags_raw.split(",") if item.strip()]
        note.replace_tags(tags)

    print(f"✅ Нотатку '{note.title}' оновлено.")


def cmd_delete_note(notes: NotesBook) -> None:
    title = input_non_empty("Назва нотатки для видалення: ")
    notes.delete(title)
    print(f"✅ Нотатку '{title}' видалено.")


def cmd_search_note(notes: NotesBook) -> None:
    query = input_non_empty("Пошук (назва / текст / тег): ")
    results = notes.search(query)
    if not results:
        print("Нічого не знайдено.")
        return
    print(f"\nЗнайдено: {len(results)}")
    _print_items(results)


def cmd_search_tag(notes: NotesBook, tag: str) -> None:
    results = notes.search_by_tag(tag)
    if not results:
        print(f"Нотаток з тегом '{tag}' не знайдено.")
        return
    print(f"\nНотатки з тегом #{tag.lstrip('#')}:")
    _print_items(results)


def cmd_all_notes(notes: NotesBook) -> None:
    items = notes.all_notes()
    if not items:
        print("Нотаток немає.")
        return
    print(f"\nУсього нотаток: {len(items)}")
    _print_items(items)


def cmd_sort_notes_tag(notes: NotesBook) -> None:
    items = notes.sort_by_tags()
    if not items:
        print("Нотаток немає.")
        return
    print("\nНотатки, відсортовані за тегами:")
    _print_items(items)


def _parse_days(argument: str) -> int:
    if not argument:
        return 7
    try:
        days = int(argument)
    except ValueError as error:
        raise ValueError("Кількість днів має бути цілим числом.") from error
    if not 0 <= days <= 366:
        raise ValueError("Вкажіть кількість днів від 0 до 366.")
    return days


def _safe_save(book: AddressBook, notes: NotesBook) -> None:
    try:
        save_all(book, notes)
    except OSError as error:
        print(f"⚠️  {error}")


def main() -> None:
    """Точка входу в застосунок."""
    book = AddressBook()
    notes = NotesBook()

    warnings = load_all(book, notes)
    for warning in warnings:
        print(f"⚠️  {warning}")

    print("╔══════════════════════════════════════╗")
    print("║   Персональний помічник запущено!    ║")
    print("║   Введіть 'help' для списку команд   ║")
    print("╚══════════════════════════════════════╝")
    print(f"Дані зберігаються в: {DATA_DIR}")

    commands: dict[str, Callable[[], None]] = {
        "add-contact": lambda: cmd_add_contact(book),
        "edit-contact": lambda: cmd_edit_contact(book),
        "delete-contact": lambda: cmd_delete_contact(book),
        "search-contact": lambda: cmd_search_contact(book),
        "all-contacts": lambda: cmd_all_contacts(book),
        "add-note": lambda: cmd_add_note(notes),
        "edit-note": lambda: cmd_edit_note(notes),
        "delete-note": lambda: cmd_delete_note(notes),
        "search-note": lambda: cmd_search_note(notes),
        "all-notes": lambda: cmd_all_notes(notes),
        "sort-notes-tag": lambda: cmd_sort_notes_tag(notes),
    }

    while True:
        try:
            raw = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nДані збережено. До побачення!")
            _safe_save(book, notes)
            break

        if not raw:
            continue

        parts = raw.split(maxsplit=1)
        command = parts[0].casefold()
        argument = parts[1].strip() if len(parts) > 1 else ""

        if command in {"exit", "quit", "close", "q"}:
            _safe_save(book, notes)
            print("Дані збережено. До побачення!")
            break

        try:
            if command in {"help", "?", "h"}:
                print_help()
            elif command == "birthdays":
                cmd_birthdays(book, _parse_days(argument))
            elif command == "search-tag":
                tag = argument or input_non_empty("Тег: ")
                cmd_search_tag(notes, tag)
            elif command in commands:
                commands[command]()
            else:
                print(f"Невідома команда: '{command}'. Введіть 'help'.")
        except ValueError as error:
            print(f"❌ {error}")
        except (EOFError, KeyboardInterrupt):
            print("\nОперацію скасовано.")
        
        # останній захист від аварійного завершення інтерактивного CLI
        except Exception as error:
            print(f"❌ Неочікувана помилка: {error}")

        _safe_save(book, notes)


if __name__ == "__main__":
    main()
