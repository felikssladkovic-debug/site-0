# Контекст для проверки zip: site-0 project-evo-method

Мы прорабатываем минимальный кейс `site-0` для `project-evo-method`.

Цель кейса: заменить один большой prompt для Codex на минимальный набор файлов spec/method, из которых Codex сможет сгенерировать самый простой Vue-сайт.

## Функциональная цель site-0

Сгенерированное приложение должно быть минимальным:

- frontend only
- TypeScript
- Vue 3
- Tailwind
- Vite
- запуск и сборка через docker-compose
- на странице отображается текст `Счетчик` и число `1`
- никаких backend, db, admin, auth, API, i18n, роутинга, настоящей логики счетчика пока нет

## Важное решение по impl-area

Сначала была ошибка: `docker-compose` рассматривался просто как runtime mechanism.

Потом мы уточнили: в рамках project-evo-method `orchestrator` тоже должен быть `impl-area`, но служебный/infrastructure.

Итогово для `site-0` есть ровно два impl-area:

```yaml
implementation_areas:
  - id: site-front
    kind: application
    responsibility: frontend app
    owns:
      - generated/site-front/**

  - id: orchestrator
    kind: infrastructure
    responsibility: docker-compose build/run orchestration
    owns:
      - generated/docker-compose.yaml
```

Связи:

```yaml
relations:
  - subject: orchestrator
    predicate: builds
    object: site-front

  - subject: orchestrator
    predicate: runs
    object: site-front
```

## Важное решение по ontology/rules/commands

Мы решили разделить общую часть метода и конкретное применение к site-0.

Неправильно смешивать в `method/` конкретику `site-0`.

Правильная модель:

```text
method/
  ontology/          # общая схема метода, без site-0
  rules/             # reusable method rules, без site-0
  command-schemas/   # reusable command contracts, без site-0

project/
  method-instance/   # применение метода к конкретному project instance site-0
  spec/              # конкретная постановка site-0
```

## Желаемая структура zip

```text
site-0-project-evo-spec-method-instance/
  README.md

  method/
    ontology/
      project-evo-method-schema.md

    rules/
      impl-area-rule.md
      spec-to-code-rule.md
      acceptance-check-rule.md

    command-schemas/
      spec-to-code-command-schema.md

  project/
    method-instance/
      rules-profile.md
      commands/
        spec-to-code.site-0.md

    spec/
      00-meta/
        spec-index.md
        site-0-ontology-instance.md

      10-product/
        site-0-brief.md

      20-architecture/
        implementation-areas.md

      30-site-front/
        site-front-contract.md

      40-orchestrator/
        orchestrator-contract.md

      60-quality/
        acceptance-checks.md
```

## Семантика файлов

### `method/ontology/project-evo-method-schema.md`

Общая онтология метода.

Должна описывать типы сущностей и допустимые связи, например:

- Project
- Method
- Rule
- CommandSchema
- CommandInstance
- Spec
- SpecFile
- ImplementationArea
- Artifact
- GeneratedCode
- AcceptanceCheck
- Behavior
- State
- Transition

Не должна упоминать `site-0`, `site-front`, `orchestrator`, Vue, Tailwind, docker-compose, `Счетчик`.

### `method/rules/*.md`

Общие reusable rules метода.

Например:

- `impl-area-rule.md`
  - каждый impl-area должен иметь id, kind, responsibility, owned artifacts, contract spec
  - generated artifact должен принадлежать impl-area
  - infrastructure impl-area допустимы

- `spec-to-code-rule.md`
  - code generation must follow spec
  - do not generate artifacts outside allowed implementation areas
  - do not invent extra features/areas

- `acceptance-check-rule.md`
  - generated code must be validated through explicit acceptance checks
  - acceptance checks should map back to spec/behavior/runtime requirements

Эти файлы не должны содержать конкретику `site-0`.

### `method/command-schemas/spec-to-code-command-schema.md`

Общий шаблон команды `spec-to-code`.

Должен описывать:

- inputs:
  - method ontology schema
  - enabled method rules
  - command schema
  - project method instance
  - project spec
- output:
  - generated code
- generic execution contract:
  - read specs
  - respect impl-area boundaries
  - generate only allowed artifacts
  - satisfy acceptance checks

Не должен быть конкретным промптом для `site-0`.

### `project/method-instance/rules-profile.md`

Конкретная конфигурация правил для `site-0`.

Здесь уже можно указывать:

```yaml
project: site-0

enabled_rules:
  - impl-area-rule
  - spec-to-code-rule
  - acceptance-check-rule

allowed_impl_areas:
  - site-front
  - orchestrator

forbidden_impl_areas:
  - site-backend
  - admin-front
  - admin-backend
  - db-canonical
  - db-read
  - etl
```

### `project/method-instance/commands/spec-to-code.site-0.md`

Главная команда для Codex.

Это конкретный executable prompt/command instance для `site-0`.

Должна говорить Codex:

- прочитать:
  - `method/ontology/project-evo-method-schema.md`
  - `method/rules/*.md`
  - `method/command-schemas/spec-to-code-command-schema.md`
  - `project/method-instance/rules-profile.md`
  - `project/spec/**`
- сгенерировать код в:
  - `generated/`
- создать только:
  - `generated/site-front/**`
  - `generated/docker-compose.yaml`
- реализовать только:
  - Vue 3 + TypeScript + Tailwind + Vite frontend
  - docker-compose запуск
  - страницу с `Счетчик` и `1`
- не создавать:
  - backend
  - database
  - admin UI
  - auth
  - API
  - i18n
  - extra features

### `project/spec/00-meta/site-0-ontology-instance.md`

Это не общая онтология, а instance-граф site-0 по общей онтологии метода.

Должен описывать конкретные экземпляры:

- `site-0` is Project
- `project-evo-method-minimal` is Method
- `site-front` is ImplementationArea
- `orchestrator` is ImplementationArea
- `spec-to-code.site-0` is CommandInstance
- `generated/site-front/**` is Artifact/GeneratedCode
- `generated/docker-compose.yaml` is Artifact/GeneratedCode
- `render-counter-static-value` is Behavior
- acceptance checks

И конкретные связи между ними.

### `project/spec/20-architecture/implementation-areas.md`

Должен явно фиксировать ровно два impl-area:

- `site-front`
- `orchestrator`

И явно запрещать остальные.

### `project/spec/30-site-front/site-front-contract.md`

Контракт frontend impl-area:

- Vue 3
- TypeScript
- Tailwind
- Vite
- renders `Счетчик`
- renders `1`
- owns `generated/site-front/**`

### `project/spec/40-orchestrator/orchestrator-contract.md`

Контракт infrastructure impl-area:

- owns `generated/docker-compose.yaml`
- builds/runs `site-front`
- uses docker-compose
- expected command: `docker-compose up --build`

### `project/spec/60-quality/acceptance-checks.md`

Минимальные проверки:

- generated project builds
- docker-compose starts frontend
- page displays `Счетчик`
- page displays `1`
- no backend/db/admin/auth/API extra areas generated

## Что нужно проверить в новом чате

Проверить zip на согласованность:

1. Нет ли site-0 конкретики в `method/ontology`, `method/rules`, `method/command-schemas`.
2. Все ли site-0 конкретные данные находятся в `project/method-instance` или `project/spec`.
3. Везде ли согласовано, что impl-area ровно две: `site-front` и `orchestrator`.
4. Нет ли старой модели, где `docker-compose` описан как отдельный `RuntimeArea` вместо artifact/ответственности `orchestrator`.
5. Главная команда для Codex должна быть:
   `project/method-instance/commands/spec-to-code.site-0.md`
6. Команда должна генерировать только:
   - `generated/site-front/**`
   - `generated/docker-compose.yaml`
7. Команда не должна создавать backend/db/admin/auth/API/i18n/роутинг/лишние фичи.
8. Acceptance checks должны соответствовать только минимальному site-0.
