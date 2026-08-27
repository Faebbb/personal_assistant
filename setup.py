"""Сумісний setup-скрипт для пакета «Персональний помічник»."""

from setuptools import find_packages, setup


setup(
    name="personal-assistant-cli",
    version="1.1.0",
    description=(
        "CLI personal assistant for contacts, birthdays, notes and tags"
    ),
    author="Faebbb & xDSmile",
    packages=find_packages(),
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "personal-assistant=personal_assistant.main:main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
)
