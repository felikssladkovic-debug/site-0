#!/usr/bin/env python3
# Указываем, что файл можно запускать напрямую как executable Python script.

from __future__ import annotations
# Включаем современное поведение аннотаций типов.
# Для этого теста не критично, но хорошо держать единый стиль Python-файлов.

import os
# Нужен, чтобы управлять environment variables при запуске spec-to-code.py.

import subprocess
# Нужен, чтобы запускать spec-to-code.py как отдельный процесс.

import tempfile
# Нужен, чтобы создать временную директорию для изолированного test project.

from pathlib import Path
# Удобная объектная работа с путями к файлам и папкам.


ROOT = Path(__file__).resolve().parents[3]
# Находим корень repo.
# Ожидаем, что тест лежит здесь:
# method/tests/spec-to-code/test-2-fails-if-no-llm-command.py
#
# parents[0] = method/tests/spec-to-code
# parents[1] = method/tests
# parents[2] = method
# parents[3] = repo root

TOOL = ROOT / "method" / "tools" / "spec-to-code.py"
# Путь к тестируемому инструменту.


def main() -> int:
    # Главная функция теста.
    # Возвращает process exit code.

    with tempfile.TemporaryDirectory() as tmp:
        # Создаем временную директорию.
        # Она будет автоматически удалена после выхода из блока.

        project = Path(tmp) / "project--site-0"
        # Создаем путь к временному project workspace.

        spec_dir = project / "spec"
        # Путь к папке spec внутри временного проекта.

        generated_dir = project / "generated"
        # Путь к generated-директории внутри временного проекта.

        spec_dir.mkdir(parents=True)
        # Создаем project--site-0/spec.
        # parents=True также создаст project--site-0.

        generated_dir.mkdir(parents=True)
        # Создаем project--site-0/generated.
        # Наличие этой папки показывает, что ошибка будет именно из-за отсутствия LLM command,
        # а не из-за отсутствия project structure.

        (spec_dir / "index.md").write_text(
            """# Test Spec

Generate any minimal runnable output.
""",
            encoding="utf-8",
        )
        # Создаем минимальный spec-файл.
        # Это нужно, чтобы spec-to-code.py успешно прошел этап чтения spec
        # и дошел до этапа вызова LLM.

        env = os.environ.copy()
        # Копируем текущие environment variables.
        # Так мы сохраняем нормальное окружение, но можем точечно удалить нужную переменную.

        env.pop("PROJECT_EVO_LLM_COMMAND", None)
        # Удаляем PROJECT_EVO_LLM_COMMAND из окружения тестового процесса.
        # None означает: если переменной нет, не выбрасывать KeyError.
        #
        # Это ключевое условие теста:
        # - --llm-command мы не передаем;
        # - PROJECT_EVO_LLM_COMMAND тоже отсутствует.

        result = subprocess.run(
            ["python3", str(TOOL), "--project-dir", str(project)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )
        # Запускаем настоящий spec-to-code.py как отдельный процесс.
        #
        # Важно:
        # - передаем только --project-dir;
        # - не передаем --llm-command;
        # - env передаем очищенный от PROJECT_EVO_LLM_COMMAND.
        #
        # text=True делает stdout/stderr строками.
        # stdout=subprocess.PIPE сохраняет stdout для проверки/диагностики.
        # stderr=subprocess.PIPE сохраняет stderr для проверки ошибки.

        assert result.returncode != 0
        # Проверяем, что инструмент завершился ошибкой.
        # Это ожидаемое поведение: без LLM command генерация невозможна.

        assert "PROJECT_EVO_LLM_COMMAND is not set" in result.stderr
        # Проверяем, что ошибка именно про отсутствие LLM-команды.
        # Это важно: тест должен ловить конкретную причину отказа,
        # а не любую случайную ошибку.

        assert not any(generated_dir.iterdir())
        # Проверяем, что generated/ остался пустым.
        # Если LLM command отсутствует, spec-to-code.py не должен ничего генерировать.

    print("OK test-2-fails-if-no-llm-command")
    # Печатаем понятный маркер успешного прохождения теста.

    return 0
    # Возвращаем успешный exit code.


if __name__ == "__main__":
    # Выполняем main() только при прямом запуске файла.

    raise SystemExit(main())
    # Превращаем return value main() в exit code процесса.