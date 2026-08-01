import ast
from pathlib import Path

FORBIDDEN_ROOTS = {"celery", "django", "rest_framework"}


def test_domain_and_application_do_not_import_frameworks() -> None:
    source_root = Path(__file__).resolve().parents[2] / "src" / "modules"
    violations: list[str] = []
    for module_root in source_root.iterdir():
        for layer in ("domain", "application"):
            layer_root = module_root / layer
            if not layer_root.exists():
                continue
            for file in layer_root.rglob("*.py"):
                tree = ast.parse(file.read_text(encoding="utf-8"))
                for node in ast.walk(tree):
                    names: list[str] = []
                    if isinstance(node, ast.Import):
                        names = [alias.name for alias in node.names]
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        names = [node.module]
                    for name in names:
                        if name.split(".", maxsplit=1)[0] in FORBIDDEN_ROOTS:
                            violations.append(f"{file.relative_to(source_root)}: {name}")
    assert violations == []


def test_invitation_http_adapters_do_not_import_persistence() -> None:
    source_root = Path(__file__).resolve().parents[2] / "src"
    api_root = source_root / "modules" / "companies" / "adapters" / "api"
    files = (
        api_root / "invitation_accept_view.py",
        api_root / "invitation_collection_view.py",
        api_root / "invitation_detail_view.py",
    )
    forbidden = ("django.db", ".infrastructure.persistence.models")
    violations: list[str] = []
    for file in files:
        tree = ast.parse(file.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            module = node.module if isinstance(node, ast.ImportFrom) else ""
            names = [alias.name for alias in node.names] if isinstance(node, ast.Import) else []
            imported = [module, *names]
            if any(marker in name for name in imported for marker in forbidden):
                violations.append(str(file.relative_to(source_root)))
    assert violations == []
