import ast
import operator
import time
from dataclasses import dataclass
from typing import Any, Callable

from .models import ToolResult


@dataclass
class ToolSpec:
    name: str
    description: str
    required_arguments: list[str]
    function: Callable[..., Any]

    def public_schema(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "required_arguments": self.required_arguments,
        }


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, ToolSpec] = {}

    def register(self, spec: ToolSpec) -> None:
        self._tools[spec.name] = spec

    def schemas(self) -> list[dict[str, Any]]:
        return [tool.public_schema() for tool in self._tools.values()]

    def get(self, name: str) -> ToolSpec:
        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")
        return self._tools[name]

    def execute(self, name: str, arguments: dict[str, Any]) -> ToolResult:
        started = time.perf_counter()
        try:
            spec = self.get(name)
            missing = [key for key in spec.required_arguments if key not in arguments]
            if missing:
                raise ValueError(f"Missing required argument(s): {', '.join(missing)}")
            output = spec.function(**arguments)
            return ToolResult(
                tool_name=name, success=True, output=output,
                duration_ms=(time.perf_counter() - started) * 1000,
            )
        except Exception as exc:
            return ToolResult(
                tool_name=name, success=False, error=f"{type(exc).__name__}: {exc}",
                duration_ms=(time.perf_counter() - started) * 1000,
            )


_ALLOWED_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}
_ALLOWED_UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def safe_calculate(expression: str) -> float | int:
    """Evaluate a restricted arithmetic expression; never uses eval()."""
    tree = ast.parse(expression, mode="eval")

    def visit(node):
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINOPS:
            return _ALLOWED_BINOPS[type(node.op)](visit(node.left), visit(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARY:
            return _ALLOWED_UNARY[type(node.op)](visit(node.operand))
        raise ValueError(f"Unsupported expression element: {type(node).__name__}")

    return visit(tree)


def build_default_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(ToolSpec(
        name="calculator",
        description="Evaluate a basic arithmetic expression.",
        required_arguments=["expression"],
        function=safe_calculate,
    ))
    return registry
