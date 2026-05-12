Да. Я посмотрел приложенный zip. В нем сейчас уже есть хорошая минимальная схема:

```text
method/
  ontology/
  rules/
  command-schemas/

project/
  method-instance/
    rules-profile.md
    commands/spec-to-code.site-0.md

  spec/
    00-meta/
    10-product/
    20-architecture/
    30-site-front/
    40-orchestrator/
    60-quality/
```

Ключевой файл запуска сейчас:

```text
project/method-instance/commands/spec-to-code.site-0.md
```

Он является **command-instance**: конкретной командой `spec-to-code` для конкретного проекта `site-0`.

---

# 1. Как spec-to-code работает сейчас

Сейчас команда устроена как **LLM-driven command**.

То есть алгоритм фактически такой:

```text
человек / CLI
  -> берет prompt-файл spec-to-code.site-0.md
  -> подает его в Codex / LLM-code
  -> LLM-code сам читает перечисленные файлы
  -> сам строит понимание проекта
  -> сам генерирует generated/
  -> сам пытается соблюсти acceptance criteria
```

## 1.1. Как ее выполнить вручную

Практический запуск сейчас мог бы выглядеть так:

```bash
cd site-0-project-evo-spec-method-instance
codex < project/method-instance/commands/spec-to-code.site-0.md
```

Или, если Codex CLI принимает текстовую задачу иначе:

```bash
codex "Read and execute project/method-instance/commands/spec-to-code.site-0.md"
```

Логика важнее конкретной команды: **рабочая директория должна быть корнем пакета**, потому что в prompt-файле пути указаны относительно корня:

```text
method/...
project/method-instance/...
project/spec/...
generated/
```

## 1.2. Что LLM-code должен сделать по текущей команде

Текущий `spec-to-code.site-0.md` прямо говорит агенту:

1. Прочитать method-level файлы:

```text
method/ontology/project-evo-method-schema.md
method/rules/impl-area-rule.md
method/rules/spec-to-code-rule.md
method/rules/acceptance-check-rule.md
method/command-schemas/spec-to-code-command-schema.md
```

2. Прочитать project-level method-instance файлы:

```text
project/method-instance/rules-profile.md
project/spec/00-meta/site-0-ontology-instance.md
```

3. Прочитать project spec файлы:

```text
project/spec/00-meta/spec-index.md
project/spec/10-product/site-0-brief.md
project/spec/20-architecture/implementation-areas.md
project/spec/30-site-front/site-front-contract.md
project/spec/40-orchestrator/orchestrator-contract.md
project/spec/60-quality/acceptance-checks.md
```

4. Извлечь из них:

```yaml
project: site-0
allowed_impl_areas:
  - site-front
  - orchestrator

output_root: generated/

site-front_stack:
  - TypeScript
  - Vue 3
  - Tailwind
  - Vite

runtime:
  - Docker Compose

required_ui:
  - "Счетчик"
  - "1"
```

5. Сгенерировать только разрешенные артефакты:

```text
generated/
  site-front/
    package.json
    index.html
    vite.config.ts
    tsconfig.json
    tailwind.config.*
    postcss.config.*
    src/**
    Dockerfile
  docker-compose.yaml
```

6. Не генерировать запрещенные части:

```text
backend
database
admin UI
auth
API server
routing
i18n
real mutable counter
persistence
extra implementation areas
```

7. Сделать проект запускаемым:

```bash
docker-compose up --build
```

8. Проверить, что страница показывает:

```text
Счетчик
1
```

## 1.3. Какой внутренний алгоритм сейчас, если описать честно

Сейчас реальный алгоритм не зафиксирован детерминированно. Он примерно такой:

```text
1. LLM-code получает command-instance.
2. LLM-code читает перечисленные файлы.
3. LLM-code сам интерпретирует ontology/rules/spec.
4. LLM-code сам определяет, какие файлы надо создать.
5. LLM-code создает generated/site-front.
6. LLM-code создает generated/docker-compose.yaml.
7. LLM-code, возможно, запускает docker-compose up --build.
8. LLM-code, возможно, чинит ошибки.
9. LLM-code завершает работу и сообщает summary.
```

То есть сейчас `spec-to-code` — это не строгий исполняемый pipeline, а **хорошо структурированный большой prompt с правилами**.

Это нормально для первого вертикального среза. Но как только появятся несколько impl-area, backend, db, ETL, read-model, миграции, тесты, acceptance gates — такой подход начнет плыть.

---

# 2. Главная проблема текущего варианта

Текущий подход слишком много доверяет LLM-code.

Сейчас LLM-code сам решает:

```text
- правильно ли он понял список impl-area;
- в каком порядке их генерировать;
- какие spec-файлы относятся к какой impl-area;
- какие файлы создавать;
- какие проверки запускать;
- как интерпретировать acceptance checks;
- что считать успешным результатом;
- можно ли отклониться от структуры;
- как чинить ошибки.
```

Для `site-0` это допустимо, потому что проект маленький:

```text
site-front + docker-compose
```

Но для реального ItemAdvisor это будет рискованно:

```text
site-front
site-backend
admin-front
admin-backend
db-canonical
db-read
ETL
orchestrator
```

Там уже нельзя просто сказать LLM: “прочитай всё и сделай”. Нужно разделить:

```text
детерминированная подготовка / анализ / валидация
  +
ограниченная LLM-генерация
  +
детерминированные проверки
  +
итеративный repair-loop
```

---

# 3. Вариант Б — более правильный

Твой вариант Б я считаю правильным направлением:

> 1. Разобрать четко алгоритм spec-to-code.
> 2. Разделить: что делает bash/python/js, что делает LLM строго по контракту, что делает LLM свободнее.
> 3. Подготовить zip и проверить подход.

Я бы только уточнил формулировку:

**spec-to-code должен быть не одним prompt-файлом, а pipeline-командой**, где prompt является только одним из этапов.

То есть:

```text
spec-to-code = deterministic pipeline + bounded LLM-code tasks + deterministic validation
```

---

# 4. Разбор твоего алгоритма 1.1–1.6

Ты предложил:

```text
1.1. вычитать правила в /method
1.2. вычитать ontology-instance проекта — из него взять список impl-area
1.3. по списку impl-area и их связям построить очередность сборки/компиляции
1.4. для каждой impl-area:
   1.4.1. собрать нужные spec — подготовить контекст
   1.4.2. выполнить сборку и компиляцию кода
   1.4.3. выполнить проверки
1.5. проверить итоговый вариант
1.6. что-то еще?
```

Я бы сказал: это хорошая основа, но в текущем виде в ней смешаны **три разных процесса**:

```text
A. планирование генерации
B. генерация кода
C. сборка/валидация результата
```

Их лучше явно разделить.

---

# 5. Что хорошо в твоем алгоритме

## 5.1. Правильно начинать с /method

Да, команда должна сначала читать reusable method layer:

```text
method/ontology
method/rules
method/command-schemas
```

Но в варианте Б это должен делать не только LLM. Лучше, чтобы deterministic runner тоже умел прочитать эти файлы и проверить базовые условия.

Например:

```text
- есть command schema spec-to-code;
- есть rules-profile;
- все enabled_rules существуют;
- command-instance действительно instantiates нужную command-schema;
- output_root объявлен;
- forbidden_impl_areas не пересекаются с allowed_impl_areas.
```

## 5.2. Правильно брать impl-area из ontology-instance

Да. В текущем zip это файл:

```text
project/spec/00-meta/site-0-ontology-instance.md
```

Там есть:

```yaml
- id: site-front
  type: ImplementationArea
  kind: application

- id: orchestrator
  type: ImplementationArea
  kind: infrastructure
```

И связи:

```yaml
- subject: site-0
  predicate: has_impl_area
  object: site-front

- subject: site-0
  predicate: has_impl_area
  object: orchestrator

- subject: orchestrator
  predicate: depends_on
  object: site-front
```

Это уже почти граф исполнения.

## 5.3. Правильно строить очередность по зависимостям

Да. Для `site-0` порядок очевидный:

```text
site-front -> orchestrator -> final acceptance
```

Почему?

Потому что `orchestrator` зависит от `site-front`:

```text
orchestrator depends_on site-front
```

Значит сначала надо создать application artifact:

```text
generated/site-front/**
```

А потом infrastructure artifact:

```text
generated/docker-compose.yaml
```

## 5.4. Правильно собирать контекст по impl-area

Это очень важная идея.

Не надо каждый раз отдавать LLM-code весь проект. Для каждой impl-area лучше готовить bounded context:

Для `site-front`:

```text
method/rules/impl-area-rule.md
method/rules/spec-to-code-rule.md
project/method-instance/rules-profile.md
project/spec/10-product/site-0-brief.md
project/spec/20-architecture/implementation-areas.md
project/spec/30-site-front/site-front-contract.md
project/spec/60-quality/acceptance-checks.md
```

Для `orchestrator`:

```text
method/rules/impl-area-rule.md
method/rules/spec-to-code-rule.md
project/method-instance/rules-profile.md
project/spec/20-architecture/implementation-areas.md
project/spec/40-orchestrator/orchestrator-contract.md
project/spec/60-quality/acceptance-checks.md
generated/site-front/** summary/manifest
```

То есть `orchestrator` не обязательно должен читать весь frontend code целиком. Ему достаточно знать:

```text
- где build context;
- какой service name;
- какой порт;
- какой Dockerfile;
- какая команда запуска.
```

---

# 6. Проблемы в твоем алгоритме

## Проблема 1. “Вычитать правила” — слишком размыто

Нужно разделить:

```text
read
parse
validate
apply
```

Иначе LLM-code “прочитал” правила, но ты не знаешь, применил ли он их.

Лучше:

```text
1. load method files
2. extract rule ids
3. load rules-profile
4. verify enabled_rules exist
5. convert rules into execution constraints
6. pass only relevant constraints into each LLM task
```

## Проблема 2. ontology-instance сейчас в Markdown, а не в машинном формате

Сейчас YAML лежит внутри Markdown fenced blocks.

Это удобно человеку, но неудобно deterministic runner.

Например, чтобы вытащить:

```yaml
instances:
relations:
transitions:
```

нужно парсить Markdown, искать YAML-блоки, склеивать или интерпретировать.

Для варианта Б лучше добавить machine-readable слой:

```text
project/method-instance/graph.yaml
```

или:

```text
project/spec/00-meta/site-0-ontology-instance.yaml
```

А Markdown оставить как human-readable view.

## Проблема 3. “Построить очередность сборки и компиляции” не всегда то же самое, что “построить очередность генерации”

Есть минимум три порядка:

```text
generation_order
build_order
runtime_start_order
```

Например:

```text
db-canonical
  может генерироваться рано,
  build может быть не нужен,
  runtime нужен до backend.

site-backend
  генерируется после API/domain spec,
  build зависит от backend code,
  runtime зависит от db.

site-front
  может генерироваться параллельно с backend,
  но integration check требует backend.
```

Поэтому в ontology/impl-area graph нужно различать relation types:

```yaml
depends_on
builds
runs
calls
reads_from
writes_to
migrates
served_by
requires_runtime
requires_contract
```

Для `site-0` достаточно `orchestrator runs/builds site-front`, но для общего метода этого мало.

## Проблема 4. “Для каждой impl-area выполнить сборку и компиляцию” не универсально

Не каждая impl-area компилируется.

Например:

```text
db-canonical      -> schema/migration validation
db-read           -> index/read-model validation
orchestrator      -> docker-compose config validation
ETL               -> script/test/data-flow validation
quality           -> test plan/report generation
```

Значит лучше не говорить “compile each impl-area”, а говорить:

```text
run area-specific validation profile
```

Для `site-front` это:

```bash
npm install
npm run build
```

Для `orchestrator`:

```bash
docker-compose config
docker-compose up --build
```

Для DB:

```bash
migration dry-run
schema validation
seed validation
```

## Проблема 5. Не хватает manifest/checkpoint слоя

После генерации каждой impl-area нужно фиксировать результат:

```text
.generated-manifest/site-front.generated.json
.generated-manifest/orchestrator.generated.json
```

Например:

```json
{
  "impl_area": "site-front",
  "owned_artifacts": [
    "generated/site-front/package.json",
    "generated/site-front/src/App.vue",
    "generated/site-front/Dockerfile"
  ],
  "spec_sources": [
    "project/spec/30-site-front/site-front-contract.md"
  ],
  "checks": [
    {
      "id": "site-front-build",
      "status": "passed"
    }
  ]
}
```

Без manifest трудно понять:

```text
- что было сгенерировано;
- какая impl-area владеет файлом;
- по каким spec это было сделано;
- какие проверки прошли;
- где искать расхождение.
```

## Проблема 6. Не хватает repair loop

Реальный `spec-to-code` почти всегда должен быть циклом:

```text
generate
  -> validate
  -> collect errors
  -> repair
  -> validate again
  -> stop after N attempts
```

Без этого LLM-code сгенерирует код, упадет build, и человек будет вручную возвращать ошибку.

Вариант Б должен сразу включать:

```yaml
repair_policy:
  max_attempts: 3
  repair_scope: current_impl_area
  input_to_repair:
    - failed command
    - stdout/stderr
    - relevant generated files
    - relevant spec context
```

## Проблема 7. Не хватает preflight-check

До генерации нужно проверить, что spec-пакет сам непротиворечив.

Например для текущего zip:

```text
- allowed_impl_areas совпадают в rules-profile и implementation-areas.md?
- forbidden_impl_areas не пересекаются с allowed?
- output_root есть?
- все пути из spec-index существуют?
- все command-instance inputs существуют?
- ownership не конфликтует?
- acceptance checks существуют?
- required generated structure не противоречит ownership?
```

Это лучше делать deterministic кодом до вызова LLM.

---

# 7. Как я бы описал правильный алгоритм spec-to-code

Я бы сделал так.

```text
0. Preflight
1. Load method profile
2. Load project graph
3. Build execution plan
4. For each impl-area: prepare bounded context
5. For each impl-area: generate artifacts
6. For each impl-area: validate artifacts
7. Repair loop if needed
8. Integration generation/validation
9. Final acceptance
10. Write report/manifest
```

Подробно.

---

## 0. Preflight

Цель: убедиться, что команда вообще может быть выполнена.

Проверить:

```text
- command-instance файл существует;
- command-instance имеет type: command-instance;
- instantiates указывает на существующую command-schema;
- rules-profile существует;
- все enabled_rules существуют;
- spec-index существует;
- все spec_files из spec-index существуют;
- ontology-instance существует;
- output_root объявлен;
- generated/ либо пустой, либо разрешен режим overwrite/update;
- нет конфликтующего ownership.
```

Для текущего `site-0` preflight должен подтвердить:

```text
output_root = generated/
impl areas = site-front, orchestrator
artifact ownership:
  site-front -> generated/site-front/**
  orchestrator -> generated/docker-compose.yaml
```

---

## 1. Load method profile

Загрузить:

```text
method/ontology/project-evo-method-schema.md
method/rules/*.md
method/command-schemas/spec-to-code-command-schema.md
project/method-instance/rules-profile.md
```

Результатом должен быть нормализованный объект:

```yaml
method_context:
  command_schema: spec-to-code
  enabled_rules:
    - impl-area-rule
    - spec-to-code-rule
    - acceptance-check-rule
  output_root: generated/
  forbidden:
    - backend API
    - database
    - admin UI
    - authentication
    - authorization
    - routing
    - i18n
    - real mutable counter
    - persistence
```

---

## 2. Load project graph

Загрузить ontology-instance и implementation area specs.

Результат:

```yaml
project_graph:
  project: site-0
  impl_areas:
    site-front:
      kind: application
      owns:
        - generated/site-front/**
    orchestrator:
      kind: infrastructure
      owns:
        - generated/docker-compose.yaml
  relations:
    - from: orchestrator
      to: site-front
      relation: builds
    - from: orchestrator
      to: site-front
      relation: runs
```

---

## 3. Build execution plan

Из графа построить порядок.

Для `site-0`:

```yaml
execution_plan:
  generation_order:
    - site-front
    - orchestrator

  validation_order:
    - site-front
    - orchestrator
    - final-acceptance
```

Почему именно так:

```text
site-front owns the application code.
orchestrator owns docker-compose.
orchestrator builds/runs site-front.
Therefore site-front must exist before orchestrator can be validated.
```

---

## 4. Prepare bounded context для каждой impl-area

Для каждой области нужно собрать context bundle.

### site-front context

```yaml
impl_area: site-front
must_read:
  - method/rules/impl-area-rule.md
  - method/rules/spec-to-code-rule.md
  - method/rules/acceptance-check-rule.md
  - project/method-instance/rules-profile.md
  - project/spec/10-product/brief-000-structure.md
  - project/spec/20-architecture/implementation-areas.md
  - project/spec/30-site-front/site-front-contract.md
  - project/spec/60-quality/acceptance-checks.md

must_generate:
  - generated/site-front/**

must_not_generate:
  - generated/docker-compose.yaml
  - backend
  - database
  - admin UI
```

### orchestrator context

```yaml
impl_area: orchestrator
must_read:
  - method/rules/impl-area-rule.md
  - method/rules/spec-to-code-rule.md
  - project/method-instance/rules-profile.md
  - project/spec/20-architecture/implementation-areas.md
  - project/spec/40-orchestrator/orchestrator-contract.md
  - project/spec/60-quality/acceptance-checks.md
  - generated manifest for site-front

must_generate:
  - generated/docker-compose.yaml

must_not_generate:
  - backend
  - database
  - admin UI
```

---

## 5. Generate artifacts

Тут LLM-code делает то, что действительно хорошо умеет:

```text
- создать Vue/Vite/Tailwind файлы;
- написать package.json;
- написать App.vue;
- написать Dockerfile;
- написать docker-compose.yaml;
- привести проект к минимально рабочему виду.
```

Но важно: LLM-code получает не весь космос, а конкретную задачу:

```text
Generate only artifacts for impl_area=site-front.
Write only under generated/site-front/**.
Do not touch method/** or project/spec/**.
Do not create orchestrator artifacts.
```

Потом отдельно:

```text
Generate only artifacts for impl_area=orchestrator.
Write only generated/docker-compose.yaml.
Use existing generated/site-front as build context.
```

---

## 6. Validate area artifacts

Для `site-front`:

```bash
cd generated/site-front
npm install
npm run build
```

Можно также:

```bash
npm run typecheck
```

если package.json это предусматривает.

Для `orchestrator`:

```bash
cd generated
docker-compose config
docker-compose up --build
```

Или, если используется современный Docker Compose:

```bash
docker compose config
docker compose up --build
```

Важно: в spec сейчас написано `docker-compose`, но на современных системах чаще `docker compose`. Лучше в будущей версии явно решить:

```yaml
docker_compose_command:
  preferred: docker compose
  legacy_accepted: docker-compose
```

---

## 7. Repair loop

Если validation падает:

```text
1. сохранить stderr/stdout;
2. определить failing impl-area;
3. собрать repair context;
4. вызвать LLM-code с ограниченной задачей;
5. повторить проверку;
6. остановиться после max_attempts.
```

Например:

```yaml
repair:
  max_attempts: 3
  scope: impl-area
  on_failure:
    - include failed command
    - include stderr
    - include relevant files
    - include relevant spec
    - forbid unrelated changes
```

---

## 8. Integration validation

После area-level проверок нужно проверить весь проект:

```bash
cd generated
docker-compose up --build
```

Потом UI check:

```text
open frontend page
assert visible text contains "Счетчик"
assert visible text contains "1"
```

Для автоматизации можно использовать Playwright:

```bash
npx playwright test
```

Но для `site-0` это может быть избыточно. Минимально можно иметь простой curl/html check, если Vite отдает static page.

---

## 9. Final acceptance

Проверить acceptance checks из:

```text
project/spec/60-quality/acceptance-checks.md
```

Текущие:

```yaml
- app-builds
- app-runs
- page-renders-counter
```

И сформировать отчет:

```yaml
acceptance_report:
  app-builds: passed
  app-runs: passed
  page-renders-counter: passed
  status: accepted
```

---

## 10. Write manifest/report

Вариант Б обязательно должен создавать отчет.

Например:

```text
generated/.project-evo/spec-to-code-report.md
generated/.project-evo/spec-to-code-manifest.json
```

Содержимое:

```yaml
command: spec-to-code
project: site-0
input_specs:
  - project/spec/10-product/brief-000-structure.md
  - project/spec/20-architecture/implementation-areas.md
  - project/spec/30-site-front/site-front-contract.md
  - project/spec/40-orchestrator/orchestrator-contract.md
  - project/spec/60-quality/acceptance-checks.md

generated_artifacts:
  site-front:
    - generated/site-front/package.json
    - generated/site-front/src/App.vue
    - generated/site-front/Dockerfile
  orchestrator:
    - generated/docker-compose.yaml

checks:
  app-builds: passed
  app-runs: passed
  page-renders-counter: passed
```

Это критично для дальнейшей эволюции метода.

---

# 8. Что делать deterministic кодом, а что LLM

Вот главное разделение.

## 8.1. Детерминированный код

Лучше делать bash/python/js без LLM:

```text
- проверить структуру папок;
- проверить наличие файлов;
- распарсить YAML front matter;
- распарсить machine-readable YAML блоки;
- проверить enabled_rules;
- проверить allowed/forbidden impl areas;
- проверить ownership;
- построить dependency graph;
- сделать topological sort;
- подготовить context bundles;
- вызвать LLM-code;
- запустить npm/docker checks;
- собрать stdout/stderr;
- сформировать report;
- остановить pipeline при stop conditions.
```

Почему: это всё не требует “творчества”. Это контроль, дисциплина и воспроизводимость.

## 8.2. LLM-code со строгими границами

LLM-code должен делать:

```text
- генерировать файлы конкретной impl-area;
- чинить ошибки конкретной impl-area;
- объяснять mapping spec -> generated files;
- предлагать минимальные изменения при repair.
```

Но ему надо запрещать:

```text
- менять method/**;
- менять project/spec/**;
- создавать undeclared impl-area;
- добавлять undeclared services;
- расширять scope;
- переписывать чужую impl-area без явного разрешения.
```

## 8.3. LLM-code со свободой

Свободнее можно оставить только детали реализации внутри границ:

```text
- структура Vue components внутри generated/site-front/src;
- CSS/Tailwind оформление;
- конкретная версия npm packages, если не зафиксирована;
- Dockerfile implementation details;
- minor naming внутри области.
```

Но даже это лучше постепенно сужать.

Например, для production-подхода версии пакетов лучше фиксировать шаблоном.

---

# 9. Альтернативные варианты архитектуры spec-to-code

## Вариант A — текущий: один большой prompt

```text
codex < project/method-instance/commands/spec-to-code.site-0.md
```

Плюсы:

```text
- быстро;
- просто;
- удобно для первого эксперимента;
- хорошо подходит для site-0.
```

Минусы:

```text
- слабая воспроизводимость;
- много скрытой логики внутри LLM;
- трудно отлаживать;
- трудно масштабировать на много impl-area;
- acceptance checks могут быть “прочитаны”, но не выполнены;
- непонятно, что именно стало причиной ошибки.
```

Подходит для:

```text
site-0
маленькие proof-of-concept
ручной прогон метода
```

---

## Вариант B — deterministic runner + bounded LLM

Это то, что ты предлагаешь. Я считаю его лучшим следующим шагом.

```text
project-evo spec-to-code site-0
  -> preflight
  -> graph
  -> plan
  -> context bundles
  -> LLM per impl-area
  -> validation
  -> repair
  -> final report
```

Плюсы:

```text
- воспроизводимо;
- понятно, где ошибка;
- можно масштабировать;
- можно добавлять validators;
- можно управлять LLM context;
- можно собирать trace/report;
- метод становится настоящим workflow engine.
```

Минусы:

```text
- больше инфраструктурного кода;
- нужно формализовать YAML/JSON contracts;
- нужно поддерживать runner;
- придется решить, где human-readable markdown, а где machine-readable source.
```

Подходит для:

```text
project-evo-method как реальный инструмент
ItemAdvisor
много impl-area
итеративная разработка
```


# 10. Что я бы добавил в пункт 1.6 “что-то еще?”

Да, обязательно.

Я бы добавил минимум эти пункты:

```text
1.6. Preflight validation до генерации.
1.7. Построить execution plan и сохранить его.
1.8. Подготовить context bundle для каждой impl-area.
1.9. После генерации каждой impl-area писать manifest.
1.10. Запускать area-specific checks.
1.11. Делать repair loop при ошибках.
1.12. Делать final integration checks.
1.13. Писать итоговый spec-to-code report.
1.14. Проверять, что LLM не изменил запрещенные файлы.
1.15. Проверять, что не появились undeclared artifacts/services.
```

Итоговый алгоритм:

```text
1. Load command instance.
2. Load method schema/rules/command schema.
3. Load project rules-profile.
4. Load spec-index and verify all spec files exist.
5. Load ontology-instance / project graph.
6. Validate graph against method schema.
7. Validate allowed/forbidden impl-area constraints.
8. Validate artifact ownership.
9. Build generation/build/runtime/validation plan.
10. For each impl-area in generation order:
    10.1. Build bounded context.
    10.2. Generate artifacts with LLM-code.
    10.3. Check file ownership boundaries.
    10.4. Run area-specific validation.
    10.5. Repair if needed.
    10.6. Write area manifest.
11. Run integration validation.
12. Run acceptance checks.
13. Verify no forbidden artifacts/services were created.
14. Write final report.
15. Mark state transition:
    spec-defined -> code-generated -> runnable -> accepted
```

---

# 11. Как это применить конкретно к site-0

Для текущего zip execution plan должен получиться таким:

```yaml
project: site-0
command: spec-to-code
output_root: generated/

impl_areas:
  - id: site-front
    kind: application
    owns:
      - generated/site-front/**
    generate:
      - Vue 3 + Vite + TypeScript app
      - Tailwind config
      - Dockerfile
    checks:
      - npm install
      - npm run build

  - id: orchestrator
    kind: infrastructure
    depends_on:
      - site-front
    owns:
      - generated/docker-compose.yaml
    generate:
      - docker-compose.yaml
    checks:
      - docker-compose config
      - docker-compose up --build

final_acceptance:
  - page displays "Счетчик"
  - page displays "1"
```

---

# 12. Какой zip я бы готовил для варианта Б

Я бы не ломал текущую структуру, а добавил слой runner/tools.

Например:

```text
method/
  ontology/
  rules/
  command-schemas/
  templates/
  tools/
    spec-to-code/
      README.md
      spec-to-code.pipeline.md
      context-bundle.schema.yaml
      execution-plan.schema.yaml
      manifest.schema.yaml

project/
  method-instance/
    rules-profile.md
    commands/
      spec-to-code.site-0.md
    generated-command-input/
      spec-to-code.site-0.input.yaml

  spec/
    00-meta/
      spec-index.md
      site-0-ontology-instance.md
      site-0-ontology-instance.yaml   # machine-readable
    ...

tools/
  project-evo-spec-to-code.py
  validators/
    validate_spec_index.py
    validate_impl_areas.py
    validate_artifact_ownership.py
    validate_generated_boundaries.py
```

Для первого рабочего прототипа можно проще:

```text
tools/spec_to_code.py
tools/lib/
  markdown_yaml.py
  graph.py
  llm_runner.py
  validators.py
```

Но концептуально лучше держать tool description в `/method/tools`, а исполняемый прототип можно положить в `/tools`.

---

# 13. Мой вывод

Текущий zip уже хорош как **вариант A: prompt-command для первого spec-to-code прогона**.

Но если цель — сделать `project-evo-method` устойчивым методом, то следующий шаг должен быть именно **вариант Б**:

```text
не “LLM, прочитай всё и сделай”,
а “runner построил план, нарезал контекст, вызвал LLM только там, где нужна генерация, проверил результат, запустил repair-loop, выдал report”.
```

Твой список 1.1–1.5 правильный по направлению, но я бы переписал его так:

```text
1. Preflight: проверить command/spec/method package.
2. Load method rules and command schema.
3. Load project method instance.
4. Load ontology-instance / project graph.
5. Extract impl-area list, ownership, dependencies, checks.
6. Build execution plan.
7. For each impl-area:
   7.1. build bounded context;
   7.2. invoke LLM-code only for this impl-area;
   7.3. verify generated files stay inside ownership boundary;
   7.4. run impl-area validation;
   7.5. repair if failed;
   7.6. write impl-area manifest.
8. Run integration validation.
9. Run acceptance checks.
10. Verify no forbidden scope was generated.
11. Write final report.
12. Transition project state to accepted only if all checks passed.
```

Главная архитектурная мысль: **LLM-code не должен быть владельцем алгоритма spec-to-code. Он должен быть исполнителем отдельных generation/repair tasks внутри алгоритма, которым владеет deterministic runner.**
