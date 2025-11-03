#!/bin/bash

echo "Создание виртуального окружения..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "Виртуальное окружение создано"
else
    echo "Виртуальное окружение уже существует"
fi

echo "Активация виртуального окружения в текущей оболочке..."
source .venv/bin/activate

echo "Обновление pip и установка основных зависимостей..."
pip install --upgrade pip
pip install python-dotenv black ruff pytest

echo "Установка зависимостей из requirements.txt..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "Зависимости установлены"
else
    echo "Файл requirements.txt не найден"
fi

echo "Обновление requirements.txt..."
pip freeze > requirements.txt

echo "Запуск форматирования кода black..."
black .

echo "Запуск проверки кода ruff..."
ruff check . --fix

echo "Запуск тестов..."
python -m pytest tests/