#!/usr/bin/env python3
# Указываем, что файл можно запускать напрямую как исполняемый Python-скрипт.

from __future__ import annotations
# Включаем современное поведение аннотаций типов.
# Это полезно для совместимости и аккуратности type hints.

import subprocess
# Нужен, чтобы запустить spec-to-code.py как отдельный процесс.

import tempfile
# Нужен, чтобы создать временную директорию для изолированного test project.

from pathlib import Path
# Удобная работа с путями к файлам и папкам.


ROOT = Path(__file__).resolve().parents[3]
# Находим корень repo.
# Ожидаем, что тест лежит здесь:
# method/tests/spec-to-code/test-3-applies-create-file-block.py
#
# parents[0] = method/tests/spec-to-code
# parents[1] = method/tests
# parents[2] = method
# parents[3] = repo root

TOOL = ROOT / "method" / "tools" / "spec-to-code.py"
# Путь к тестируемому инструменту.


FAKE_LLM = r'''#!/usr/bin/env python3
from __future__ import annotations

import sys

_ = sys.stdin.read()

print("""```project-evo-file
action: create
path: index.html
---
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <title>Test</title>
</head>
<body>
  <h1>Generated from fake LLM</h1>
</body>
</html>
```""")
'''
# Это текст fake LLM-скрипта.
#
# fake LLM:
# - читает prompt из stdin, чтобы соответствовать контракту PROJECT_EVO_LLM_COMMAND;
# - не анализирует prompt, потому что это тест не LLM-логики, а runner-логики;
# - возвращает один project-evo-file block;
# - этот block должен быть распарсен spec-to-code.py;
# - результат должен быть записан в generated/index.html.


def main() -> int:
    # Главная функция теста.
    # Возвращает process exit code.

    with tempfile.TemporaryDirectory() as tmp:
        # Создаем временную директорию.
        # После выхода из блока она будет автоматически удалена.

        tmp_dir = Path(tmp)
        # Преобразуем строковый путь временной директории в Path.

        project = tmp_dir / "project--site-0"
        # Создаем путь к временному project workspace.

        spec_dir = project / "spec"
        # Путь к папке spec внутри временного проекта.

        generated_dir = project / "generated"
        # Путь к generated output внутри временного проекта.

        spec_dir.mkdir(parents=True)
        # Создаем папку spec.
        # parents=True создает промежуточные директории project--site-0/spec.

        generated_dir.mkdir(parents=True)
        # Создаем папку generated.
        # В реальном project она уже может существовать, но в тесте создаем явно.

        (spec_dir / "index.md").write_text(
            """# Test Spec

Generate a minimal runnable static page.
""",
            encoding="utf-8",
        )
        # Создаем минимальный spec-файл.
        # Важно: spec-to-code.py должен читать именно project/spec/index.md.
        # Конкретное содержание здесь почти не важно, потому что fake LLM его не анализирует.

        fake_llm_path = tmp_dir / "fake-llm.py"
        # Путь, куда запишем fake LLM-скрипт.

        fake_llm_path.write_text(FAKE_LLM, encoding="utf-8")
        # Записываем fake LLM-код во временный файл.

        fake_llm_path.chmod(0o755)
        # Делаем fake LLM исполняемым.
        # Даже если запускаем через python3, это полезно для консистентности.

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
        # Передаем:
        # - --project-dir: временный project workspace;
        # - --llm-command: команду запуска fake LLM.
        #
        # text=True означает, что stdout/stderr будут строками, а не bytes.
        # stdout=subprocess.PIPE сохраняет stdout для проверки.
        # stderr=subprocess.PIPE сохраняет stderr для диагностики.

        assert result.returncode == 0, result.stderr
        # Проверяем, что spec-to-code.py завершился успешно.
        # Если нет — показываем stderr как сообщение ошибки.

        assert "spec-to-code OK" in result.stdout
        # Проверяем, что инструмент сообщил об успешном выполнении.

        output_path = generated_dir / "index.html"
        # Ожидаемый файл, который должен быть создан из file operation block.

        assert output_path.exists()
        # Проверяем, что файл действительно создан.

        output_text = output_path.read_text(encoding="utf-8")
        # Читаем содержимое созданного файла.

        assert "Generated from fake LLM" in output_text
        # Проверяем, что содержимое файла пришло именно из fake LLM response.

        assert "<!doctype html>" in output_text
        # Дополнительная проверка, что HTML-содержимое записалось полностью,
        # а не только фрагмент.

    print("OK test-3-applies-create-file-block")
    # Печатаем понятный маркер успеха для человека/CI.

    return 0
    # Возвращаем успешный exit code.


if __name__ == "__main__":
    # Выполняем main() только при прямом запуске файла.

    raise SystemExit(main())
    # Превращаем return value main() в exit code процесса.