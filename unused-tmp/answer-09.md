Проверил zip. Твоя картина в целом верная, но я бы уточнил несколько важных мест.

## Исправленная картина текущего состояния

### 1. `evo-root.sh`

Да, это единая точка входа в CLI `project-evo-method`.

Сейчас поддерживает:

```bash
bash ./evo-root.sh help
bash ./evo-root.sh check-document-metadata-header
bash ./evo-root.sh spec-to-code
bash ./evo-root.sh test
bash ./evo-root.sh test check-document-metadata-header
bash ./evo-root.sh test spec-to-code
```

Важное замечание: в zip у shell/python-файлов нет executable-бита. Поэтому прямой вызов:

```bash
./evo-root.sh test
```

может дать:

```text
Permission denied
```

А так работает:

```bash
bash ./evo-root.sh test
```

Лучше на сервере после распаковки сделать:

```bash
chmod +x evo-root.sh
chmod +x project--site-0/evo.sh
chmod +x method/tools/*.sh
chmod +x method/tools/*.py
chmod +x meta/tools/*.py
```

### 2. Области `/meta`, `/method`, `/project--<name>`

Да, текущая модель такая:

```text
/meta
  layer-0: проверяет саму реализацию method

/method
  layer-1: реализация project-evo-method

/project--site-0
  прикладной project workspace, который ведется методом
```

Но сейчас это еще не полноценная онтология слоев, а минимальный исполняемый вертикальный срез.

### 3. `project--site-0/evo.sh`

Да, это project-local wrapper.

Он делает две вещи:

```bash
PROJECT_DIR="$(.../project--site-0)"
ROOT_DIR="$(.../repo-root)"
export PROJECT_EVO_LLM_COMMAND="${PROJECT_EVO_LLM_COMMAND:-$ROOT_DIR/method/tools/codex-text-llm.sh}"
exec "$ROOT_DIR/evo-root.sh" "$@" --project-dir "$PROJECT_DIR"
```

То есть из папки проекта можно вызывать:

```bash
bash ./evo.sh spec-to-code
```

И команда пойдет в root CLI уже с правильным `--project-dir`.

### 4. `check-document-metadata-header`

Да, команда проверяет Markdown-документы в `/method`.

Сейчас правило минимальное:

обязательные поля:

```yaml
id:
type:
status:
scope:
```

разрешены только эти поля;

проверяется:

```text
- наличие YAML front matter
- обязательные поля
- отсутствие лишних полей
- known type/status/scope
- уникальность id
```

Важная поправка: правило описано в `/meta/rules/document-metadata-header.md`, но сам этот файл находится в `/meta`, поэтому **не обязан** проходить проверку `/method`. Проверка применяется к `/method/**/*.md`.

### 5. `spec-to-code`

Твое описание почти точное.

Сейчас `spec-to-code`:

```text
1. принимает --project-dir
2. читает только project/spec/index.md
3. строит prompt
4. вызывает LLM-команду из --llm-command или PROJECT_EVO_LLM_COMMAND
5. передает prompt в stdin
6. получает stdout
7. парсит project-evo-file blocks
8. поддерживает только action: create
9. очищает generated/
10. записывает файлы в generated/
```

Формат сейчас не совсем “сокращение от SEARCH/REPLACE”. Скорее это собственный минимальный file-operation block format:

````text
```project-evo-file
action: create
path: index.html
---
file content
```
````

Ограничения:

```text
- только create
- фактически режим rewrite всего generated/
- нет update/patch/delete
- нет SEARCH/REPLACE
- нет diff/apply patch
- нет ownership-проверок
- нет impl-area
- нет repair-loop
- нет validation после генерации, кроме path safety
```

Проверка безопасности уже есть:

```text
- запрещены absolute paths
- запрещен ..
- проверяется, что output остается внутри generated/
```

### 6. Тесты

Есть тесты для:

```text
check-document-metadata-header:
- required headers
- no extra headers
- unique ids

spec-to-code:
- fails if no project
- fails if no LLM command
- applies create file block
- rejects path traversal
```

То есть сейчас это не просто набор скриптов, а уже маленький executable-method skeleton с регрессионными тестами.

---

# Уточненный текущий функционал

Я бы сформулировал так:

1. **`evo-root.sh`** — root CLI для запуска команд метода.
2. **`/meta`** — слой проверки самой реализации `/method`.
3. **`/method`** — исполняемая реализация `project-evo-method`: tools, tests, method-documents.
4. **`/project--site-0`** — первый project workspace, ведомый методом.
5. **`project--site-0/evo.sh`** — project-local wrapper, который вызывает root CLI с правильным `--project-dir`.
6. **`check-document-metadata-header`** — meta-команда, проверяющая metadata headers документов `/method`.
7. **`spec-to-code`** — первая method-команда генерации кода из одного spec-файла.
8. **`PROJECT_EVO_LLM_COMMAND`** — контракт подключения LLM: stdin prompt → stdout file-operation blocks.
9. **`codex-text-llm.sh`** — текущий adapter к Codex CLI в режиме text-only.
10. **`fake-llm.py`** — тестовый deterministic LLM adapter.
11. **`generated/`** — rewrite-target, полностью очищается и пересоздается из LLM-ответа.
12. **`test`** — минимальный regression suite для проверки method tools.

---

# Исправленный план развития

Я бы разложил твой план не просто списком тем, а по слоям зрелости.

## Этап 1. Стабилизировать v0 как foundation

Сначала надо закрепить текущий минимальный вертикальный срез.

Сделать:

1. Добавить executable-bit или инструкцию `chmod +x`.
2. Зафиксировать версию как условный `foundation-00-minimal`.
3. Добавить `README`-раздел “known limitations”.
4. Добавить smoke-команду:

```bash
bash ./evo-root.sh smoke
```

которая делает:

```text
- check-document-metadata-header
- test
- spec-to-code через fake-llm
- проверку, что generated/index.html существует
```

5. Развести clearly:

```text
real LLM run
test fake LLM run
```

Сейчас `spec-to-code` зависит от `PROJECT_EVO_LLM_COMMAND`, а для smoke-теста лучше иметь deterministic mode.

---

## Этап 2. Нормализовать command contract

Сейчас `spec-to-code` — код есть, но формального command schema еще нет.

Добавить в `/method` документы:

```text
method/commands/spec-to-code.command.md
method/contracts/llm-text-command.contract.md
method/contracts/project-evo-file-block.contract.md
```

И зафиксировать:

```text
- input
- output
- env
- allowed side effects
- failure modes
- validation steps
```

Это важно до усложнения, иначе новые возможности начнут расползаться.

---

## Этап 3. Сделать нормальный spec-index

Сейчас `spec-to-code` читает только:

```text
project--site-0/spec/index.md
```

Следующий шаг — превратить `spec/index.md` не в единственный spec, а в entrypoint/index.

Например:

```text
spec/index.md
spec/project.yaml
spec/impl-areas.yaml
spec/site-front/index.md
spec/site-front/ui.md
spec/site-front/runtime.md
spec/orchestrator/index.md
```

`spec/index.md` должен стать manifest/index-файлом, а не единственным источником.

Минимально:

```yaml
spec_version: 1
project: site-0
impl_areas:
  - id: site-front
    spec_files:
      - site-front/index.md
      - site-front/ui.md
```

---

## Этап 4. Ввести impl-area как основной unit генерации

Это, на мой взгляд, главный следующий архитектурный шаг.

Нужно перейти от:

```text
spec-to-code генерит весь generated/
```

к:

```text
spec-to-code генерит конкретные impl-area
```

Например:

```text
impl-area: site-front
owns:
  - generated/site-front/**
checks:
  - npm test
  - npm run build
runtime:
  type: docker-compose-service
```

Даже для текущего `site-0` можно ввести один impl-area:

```text
site-front
```

Тогда текущая генерация станет частным случаем.

---

## Этап 5. Artifact ownership и boundaries

До repair-loop обязательно нужен ownership.

Иначе LLM/runner не сможет безопасно менять файлы.

Добавить manifest:

```text
project--site-0/.evo/artifact-ownership.yaml
```

или пока:

```text
project--site-0/spec/artifact-ownership.yaml
```

Пример:

```yaml
owners:
  site-front:
    can_write:
      - generated/site-front/**
    can_read:
      - spec/site-front/**
      - spec/shared/**
    cannot_write:
      - spec/**
      - .evo/**
      - method/**
```

Для текущего v0 можно оставить:

```yaml
site-front:
  can_write:
    - generated/**
```

---

## Этап 6. Контекстный snapshot / repomix

Твой пункт про `repomix` правильный, но я бы не ставил его раньше impl-area.

Правильная роль `repomix`:

```text
создать bounded context bundle для конкретного impl-area
```

Не “дать LLM весь repo”, а собрать строго выбранный контекст:

```text
- relevant spec files
- relevant generated files текущего impl-area
- relevant shared contracts
- package/build files, если нужны
- checks output, если repair
```

Артефакты:

```text
generated/.project-evo/context/site-front.prompt.md
generated/.project-evo/context/site-front.snapshot.md
generated/.project-evo/context/site-front.files.txt
```

---

## Этап 7. Validation pipeline

Валидация должна быть многоуровневой:

```text
1. input validation
2. spec validation
3. impl-area graph validation
4. artifact ownership validation
5. generated output format validation
6. generated boundaries validation
7. build/test/runtime validation
8. spec-to-code trace validation
```

Для `site-front` минимум:

```text
- files generated only inside allowed paths
- expected files exist
- HTML/Vite/Vue build passes
- docker-compose build passes
- docker-compose up health check passes
```

Сейчас validation есть только на уровне output path safety.

---

## Этап 8. Repair-loop

Repair-loop надо вводить только после checks.

Минимальная схема:

```text
generate
validate
if failed:
  build repair prompt:
    - original bounded context
    - generated files summary
    - validation errors
    - allowed write paths
  call LLM
  apply operations
  validate again
```

Параметры:

```text
max_attempts: 2 или 3
repair_scope: same impl-area only
repair_input: validation errors + owned files
repair_output: same file-operation blocks
```

Важно: repair-loop не должен превращаться в “LLM делает что хочет”. Он должен быть таким же bounded, как генерация.

---

## Этап 9. Разные LLM adapters

Сейчас есть один контракт:

```text
PROJECT_EVO_LLM_COMMAND
```

Это хорошая минимальная абстракция.

Дальше можно сделать adapters:

```text
method/tools/llm/codex-text-llm.sh
method/tools/llm/lmstudio-text-llm.py
method/tools/llm/openai-text-llm.py
method/tools/llm/claude-text-llm.sh
method/tools/llm/fake-llm.py
```

Но важно сохранить общий контракт:

```text
stdin: prompt
stdout: project-evo-file blocks
stderr: diagnostics
exit code: success/failure
```

И добавить capabilities:

```yaml
id: codex-text
supports:
  filesystem_access: false
  structured_output: weak
  long_context: medium
  patch_mode: false
```

---

## Этап 10. Контейнеры для impl-area

Этот пункт лучше оформить как `impl-area runtime/check adapter`.

Например:

```yaml
impl_areas:
  site-front:
    type: vue-vite-front
    runtime:
      adapter: docker-compose
      service: site-front
    checks:
      - npm install
      - npm run build
      - npm test
      - docker compose build site-front
```

То есть контейнеры — не отдельная сущность верхнего уровня, а способ проверки/запуска конкретного impl-area.

---

## Этап 11. `.evo` и `evo init`

Да, это важный будущий шаг.

Но я бы разделил:

```text
project-evo-method repo
```

и

```text
project workspace initialized by evo
```

После `evo init` в проекте должно быть что-то вроде:

```text
.evo/
  project.yaml
  method.lock.yaml
  state.yaml
  runs/
  cache/
  context/
  manifests/

spec/
generated/
evo.sh
```

`evo init` должен быть похож не только на `git init`, а скорее на:

```text
git init + npm init + framework scaffold + method binding
```

---

## Этап 12. Foundation

Текущий `site-0` лучше считать не foundation, а **example instance** или **minimal fixture**.

Разделить:

```text
/foundations
  /foundation--static-site-min
  /foundation--vue-vite-tailwind
  /foundation--fullstack-db

/project--site-0
  instance created from foundation--static-site-min
```

То есть:

```text
foundation = шаблон/исходная заготовка
site-0 = конкретный экземпляр
```

Сейчас `site-0` — хороший кандидат на первый example project, но не стоит смешивать его с reusable foundation.

---

## Этап 13. Git workflow и feature integration

Этот слой лучше вводить после `.evo/state.yaml`.

Состояния:

```text
main-ready
feature-idea
feature-brief
feature-spec
feature-generating
feature-validating
feature-review
feature-integrating
```

Git branches:

```text
main
feature/<feature-id>
spec/<feature-id>       # возможно, не отдельная ветка, а стадия feature branch
repair/<run-id>         # опционально
```

Но я бы не усложнял git раньше, чем появятся:

```text
- spec validation
- generated validation
- run manifests
- trace между spec и generated
```

---

## Этап 14. Получение spec через API evo

Да, но это уже переход от CLI к service/API.

Нужен pipeline приема spec:

```text
1. receive spec package
2. place into incoming area
3. validate structure
4. normalize
5. assign ids
6. compare with current project spec
7. create proposal
8. human approve
9. merge into spec/
10. run spec-to-code
```

Папки:

```text
.evo/inbox/spec-proposals/
.evo/runs/
.evo/reports/
spec/
```

Команды:

```bash
evo spec receive <path>
evo spec validate <proposal-id>
evo spec accept <proposal-id>
evo spec reject <proposal-id>
```

---

## Этап 15. Views

`view` я бы не делал просто как “отчеты”. Лучше зафиксировать как read-model поверх method state.

Примеры views:

```text
project graph view
impl-area graph view
spec coverage view
artifact ownership view
run history view
validation report view
feature state view
LLM context bundle view
```

Файлы:

```text
.evo/views/project-graph.view.md
.evo/views/impl-areas.view.md
.evo/views/latest-run.view.md
.evo/views/validation-report.view.md
```

Позже это станет основой UI.

---

## Этап 16. UI / evo-IDE

Варианты UI я бы разделил на 4 уровня.

### Вариант A. CLI + generated markdown views

Самый дешевый и правильный ближайший шаг.

```text
evo view project
evo view impl-areas
evo view latest-run
```

Генерит Markdown/HTML views.

### Вариант B. Local static dashboard

Команда:

```bash
evo ui build
```

Создает:

```text
.evo/ui/index.html
```

Показывает:

```text
- project state
- impl-areas
- latest runs
- validation errors
- generated artifacts
```

### Вариант C. Local web server

Команда:

```bash
evo ui serve
```

Открывает локальный интерфейс.

### Вариант D. IDE-like рабочая среда

Это уже целевой `evo-IDE`:

```text
- слева project/spec/impl-area graph
- центр: spec/editor/view
- справа: run/validation/LLM context/repair
- снизу: logs/checks
```

Я бы шел так:

```text
CLI → markdown views → static dashboard → local web UI → evo-IDE
```

---

# Что я бы поправил в твоем плане

Твой список хороший, но порядок я бы изменил.

Не так:

```text
валидация → repair-loop → impl-area → repomix → ...
```

А так:

```text
1. стабилизировать v0
2. command contracts
3. spec-index
4. impl-area model
5. artifact ownership
6. bounded context snapshot / repomix
7. validation pipeline
8. repair-loop
9. run manifests
10. LLM adapters
11. containers/check adapters
12. views
13. .evo + evo init
14. foundations
15. git workflow
16. spec intake API
17. evo-IDE
```

Главная поправка: **repair-loop нельзя делать до impl-area, ownership и validation**. Иначе repair-loop будет не инженерным механизмом, а просто повторным вызовом LLM.

---

# Ближайший практический следующий шаг

Я бы следующим шагом сделал не repair-loop, а **v1 `spec-to-code` с impl-area = `site-front`**.

Минимальная цель:

```text
site-0 остается простым,
но pipeline уже становится правильным.
```

Добавить:

```text
project--site-0/spec/project.yaml
project--site-0/spec/impl-areas.yaml
project--site-0/spec/site-front/index.md
project--site-0/spec/artifact-ownership.yaml
```

И изменить `spec-to-code.py`, чтобы он делал:

```text
1. load project.yaml
2. load impl-areas.yaml
3. select impl-area site-front
4. validate ownership
5. build bounded prompt
6. call LLM
7. parse file blocks
8. validate output paths against ownership
9. write generated/
10. write run manifest
```

Это будет правильный мост от текущего v0 к настоящему `project-evo-method`.
