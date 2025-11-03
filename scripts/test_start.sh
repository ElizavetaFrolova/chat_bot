#!/bin/bash

echo "СКРИПТ НАСТРОЙКИ ПРОЕКТА"
echo "========================"

echo "[1/7] Проверка виртуального окружения..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "СОЗДАНО: Виртуальное окружение"
else
    echo "УЖЕ СУЩЕСТВУЕТ: Виртуальное окружение"
fi

echo "[2/7] Активация виртуального окружения..."
source .venv/bin/activate

echo "[3/7] Установка зависимостей..."
pip install --upgrade pip
pip install python-dotenv black ruff pytest

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "УСТАНОВЛЕНО: requirements.txt"
else
    echo "ПРОПУЩЕНО: requirements.txt не найден"
fi

echo "[4/7] Обновление зависимостей..."
pip freeze > requirements.txt

echo "[5/7] Форматирование кода..."
black .

echo "[6/7] Проверка качества кода..."
ruff check . --fix

echo "[7/7] Запуск тестов..."
PYTHONPATH=. pytest tests/ -v

echo "========================"
echo "НАСТРОЙКА ЗАВЕРШЕНА"
echo "Для активации окружения выполните: source .venv/bin/activate"