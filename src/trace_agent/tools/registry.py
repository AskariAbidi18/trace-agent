
from collections.abc import Callable
from typing import Any


class ToolRegistry:
    """Stores and manages tools available to the agent."""

    def __init__(self) -> None:
        self._tools: dict[str, Callable[..., Any]] = {}
        self._descriptions: dict[str, str] = {}

    def register(
        self,
        name: str,
        function: Callable[..., Any],
        description: str = "",
    ) -> None:
        """Register a callable tool under a unique name."""

        if not name or not name.strip():
            raise ValueError("Tool name cannot be empty.")

        if not callable(function):
            raise TypeError("Registered tool must be callable.")

        if name in self._tools:
            raise ValueError(f"Tool '{name}' is already registered.")

        self._tools[name] = function
        self._descriptions[name] = description

    def get(self, name: str) -> Callable[..., Any]:
        """Retrieve a registered tool."""

        if name not in self._tools:
            raise KeyError(f"Tool '{name}' is not registered.")

        return self._tools[name]

    def list_tools(self) -> list[str]:
        """Return the names of all registered tools."""

        return list(self._tools.keys())

    def has_tool(self, name: str) -> bool:
        """Check whether a tool is registered."""

        return name in self._tools

    def unregister(self, name: str) -> None:
        """Remove a registered tool."""

        if name not in self._tools:
            raise KeyError(f"Tool '{name}' is not registered.")

        del self._tools[name]
        del self._descriptions[name]

    def describe(self) -> dict[str, str]:
        """Return registered tool names and their descriptions."""

        return self._descriptions.copy()
