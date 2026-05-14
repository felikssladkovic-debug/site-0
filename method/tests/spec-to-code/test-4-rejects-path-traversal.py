#!/usr/bin/env python3
# Указываем, что тест можно запускать напрямую как executable Python script.

from __future__ import annotations
# Включаем отложенную обработку type annotations.
# Это полезно для совместимости и аккуратности типизации.

import subprocess
# Нужен для запуска spec-to-code.py как отдельного процесса.

import tempfile
# Нужен для создания временной директории изолированного test project.

from pathlib import Path
# Удобная объектная работа с путями к файлам и папкам.


ROOT = Path(__file__).resolve().parents[3]
# Находим корень repo.
# Ожидаем, что файл лежит здесь:
# method/tests/spec-to-code/test-4-rejects-path-traversal.py
#
# parents[0] = method/tests/spec-to-code
# parents[1] = method/tests
# parents[2] = method
# parents[3] = repo root

TOOL = ROOT / "method" / "tools" / "spec-to-code.py"
# Путь к тестируемому инструменту spec-to-code.py.


FAKE_LLM = r'''#!/usr/bin/env python3
from __future__ import annotations

import sys

_ = sys.stdin.read()

print("""```project-evo-file
action: create
path: ../escaped.txt
---
This file must not be written.
```""")
'''
# Текст fake LLM-скрипта.
#
# fake LLM:
# - читает prompt из stdin, чтобы соответствовать контракту LLM-команды;
# - возвращает project-evo-file block;
# - намеренно указывает path: ../escaped.txt;
# - такой path пытается выйти из generated/ наружу;
# - spec-to-code.py обязан отклонить этот output.


def main() -> int:
    # Главная функция теста.

    with tempfile.TemporaryDirectory() as tmp:
        # Создаем временную директорию.
        # Она автоматически удалится после выхода из блока.

        tmp_dir = Path(tmp)
        # Преобразуем путь временной директории в Path.

        project = tmp_dir / "project--site-0"
        # Создаем путь к временному project workspace.

        spec_dir = project / "spec"
        # Путь к spec-директории проекта.

        generated_dir = project / "generated"
        # Путь к generated-директории проекта.

        spec_dir.mkdir(parents=True)
        # Создаем project--site-0/spec.

        generated_dir.mkdir(parents=True)
        # Создаем project--site-0/generated.

        (spec_dir / "index.md").write_text(
            """# Test Spec

Generate any file.
""",
            encoding="utf-8",
        )
        # Создаем минимальный spec-файл.
        # Его содержание не важно: fake LLM всегда вернет опасный path.

        fake_llm_path = tmp_dir / "fake-llm-path-traversal.py"
        # Путь к временному fake LLM-скрипту.

        fake_llm_path.write_text(FAKE_LLM, encoding="utf-8")
        # Записываем fake LLM-код в файл.

        fake_llm_path.chmod(0o755)
        # Делаем fake LLM исполняемым.
        # Даже если запускаем через python3, это не мешает и делает файл полноценным script.

        result = subprocess.run(
            [
                "python3",
                str(TOOL),
                "--project-dir",
                str(project),
                "--llm-command",
                f"python3 {fake_llm_path}",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        # Запускаем настоящий spec-to-code.py.
        #
        # Он должен:
        # - прочитать spec/index.md;
        # - вызвать fake LLM;
        # - получить block с path: ../escaped.txt;
        # - отклонить этот path;
        # - завершиться с ошибкой.

        assert result.returncode != 0
        # Проверяем, что spec-to-code.py завершился неуспешно.

        assert "must not contain '..'" in result.stderr
        # Проверяем, что ошибка именно про path traversal через '..'.
        # Это важно: тест должен ловить конкретное нарушение безопасности.

        escaped_path = project / "escaped.txt"
        # Это путь, куда файл попал бы, если бы runner ошибочно разрешил ../escaped.txt.
        #
        # generated/../escaped.txt нормализуется примерно в:
        # project--site-0/escaped.txt

        assert not escaped_path.exists()
        # Проверяем, что файл за пределами generated/ не был создан.

        assert not any(generated_dir.iterdir())
        # Проверяем, что generated/ остался пустым.
        # Это ожидаемо, потому что операция должна быть отклонена до применения.

    print("OK test-4-rejects-path-traversal")
    # Печатаем понятный маркер успеха.

    return 0
    # Возвращаем успешный exit code.


if __name__ == "__main__":
    # Выполняем main() только при прямом запуске файла.

    raise SystemExit(main())
    # Превращаем return value main() в exit code процесса.