import ast
from pathlib import Path


def test_domain_and_application_do_not_import_outer_layers() -> None:
    source_root = Path(__file__).parents[2] / "src" / "legado_agent"
    forbidden = (
        "legado_agent.adapters",
        "legado_agent.infrastructure",
        "PySide6",
        "httpx",
        "sqlite3",
    )
    violations: list[str] = []
    for layer in ("domain", "application"):
        for path in (source_root / layer).rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                module = ""
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.startswith(forbidden):
                            violations.append(f"{path.name}: {alias.name}")
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    if module.startswith(forbidden):
                        violations.append(f"{path.name}: {module}")
    assert not violations, violations
