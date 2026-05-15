
план мини 15.05.2026

# Этап 1. Стабилизировать v-0.

1. evo + команда chmod - ставит chmod для всех .sh, .py
   - chmod +x evo-root.sh
   - chmod +x project--site-0/evo.sh
   - chmod +x method/tools/*.sh
   - chmod +x method/tools/*.py
   - chmod +x meta/tools/*.py

2. evo-root + команда smoke
   - check-document-metadata-header
   - test
   - spec-to-code через fake-llm
   - проверку, что generated/index.html существует

3. Как лучше Развести clearly "real LLM" / fake-llm
   "real LLM run" и "test fake LLM run" ?



---
Доработаем project-evo-method.
Текущая версия - приложенный файл zip.

В соседнем чате ты рекомендуешь такие первые шаги:

