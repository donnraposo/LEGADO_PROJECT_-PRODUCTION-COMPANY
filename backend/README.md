# Backend

Backend central em Python, Django e Django REST Framework, organizado como monólito modular com Clean Architecture.

O servidor ASGI aprovado é Daphne. A estrutura interna segue [Estrutura do repositório e módulos](../docs/03-arquitetura/estrutura-repositorio.md).

## Comandos planejados

```text
python -m pip install -e ".[dev]"
python manage.py check
daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

O ambiente alvo é Python 3.14. Configurações reais deverão ser fornecidas por variáveis de ambiente ou arquivos de segredo não versionados.
