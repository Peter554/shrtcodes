import ast
import re
from inspect import signature
from typing import Any, Callable, Dict, List, Tuple


class ShrtcodesError(Exception):
    pass


class UnrecognizedShortcode(ShrtcodesError):
    pass


class UnpairedShortcode(ShrtcodesError):
    pass


class OverpairedShortcode(ShrtcodesError):
    pass


class InvalidShortcodeName(ShrtcodesError):
    pass


class Shrtcodes:
    def __init__(self, allow_nested: bool = False):
        self._handlers: Dict[str, Callable[..., str]] = {}
        self._paired_handlers: Dict[str, Callable[..., str]] = {}
        self._allow_nested = allow_nested

    def register(self, name: str):
        if name.startswith("end_"):
            raise InvalidShortcodeName()

        def decorator(handler: Callable[..., str]):
            self._handlers = {**self._handlers, name: handler}
            return handler

        return decorator

    def register_paired(self, name: str):
        if name.startswith("end_"):
            raise InvalidShortcodeName()

        def decorator(handler: Callable[..., str]):
            self._paired_handlers = {**self._paired_handlers, name: handler}
            return handler

        return decorator

    @staticmethod
    def _find_shortcode_start(
        lines: List[str], start_at_idx: int = 0
    ) -> Tuple[int, str, List]:
        regex = re.compile(r"{%\s*(\w+)(\s.+\s)?\s*%}")
        for idx, line in enumerate(lines[start_at_idx:]):
            match = regex.match(line)
            if match:
                params = (
                    ast.literal_eval(f"[{match.group(2)}]") if match.group(2) else []
                )
                return idx + start_at_idx, match.group(1), params
        return -1, "", []

    @staticmethod
    def _find_shortcode_end(
        lines: List[str], handler_name: str, start_at_idx: int = 0
    ) -> int:
        regex = re.compile(fr"{{%\s*end_{handler_name}\s*%}}")
        for idx, line in enumerate(lines[start_at_idx:]):
            match = regex.match(line)
            if match:
                return idx + start_at_idx
        return -1

    @staticmethod
    def _contains_shortcode(lines: List[str]) -> bool:
        regex = re.compile(r"{%.+%}")
        for line in lines:
            if regex.match(line):
                return True
        return False

    def process(self, text: str, context: Dict[str, Any] = {}) -> str:
        lines = text.splitlines()

        done = False
        while True:
            start_idx = -1
            while True:
                start_idx, handler_name, params = self._find_shortcode_start(
                    lines, start_idx + 1
                )
                if start_idx < 0:
                    done = True
                    break

                if handler_name in self._handlers:
                    if (
                        self._find_shortcode_end(lines, handler_name, start_idx + 1)
                        >= 0
                    ):
                        raise OverpairedShortcode(
                            f"Shortcode {handler_name} is overpaired."
                        )
                    handler = self._handlers[handler_name]
                    lines = (
                        lines[:start_idx]
                        + [
                            handler(*params, context)
                            if "context" in signature(handler).parameters
                            else handler(*params)
                        ]
                        + lines[start_idx + 1 :]
                    )
                    break

                if handler_name not in self._paired_handlers:
                    raise UnrecognizedShortcode(
                        f"Shortcode {handler_name} is unrecognized."
                    )
                handler = self._paired_handlers[handler_name]

                end_idx = self._find_shortcode_end(lines, handler_name, start_idx + 1)
                if end_idx < 0:
                    raise UnpairedShortcode(f"Shortcode {handler_name} is unpaired.")
                block_lines = lines[start_idx + 1 : end_idx]

                if self._allow_nested and self._contains_shortcode(block_lines):
                    continue

                block = "\n".join(block_lines)
                lines = (
                    lines[:start_idx]
                    + [
                        handler(*params, block, context)
                        if "context" in signature(handler).parameters
                        else handler(*params, block)
                    ]
                    + lines[end_idx + 1 :]
                )
                break

            if done:
                break

        return "\n".join(lines)
