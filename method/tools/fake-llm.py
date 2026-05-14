#!/usr/bin/env python3
import sys

prompt = sys.stdin.read()

print("""```project-evo-file
action: create
path: index.html
---
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <title>site-0</title>
</head>
<body>
  <h1>Счетчик</h1>
  <div>1</div>
</body>
</html>
```""")