import shlex
import re
from typing import Callable


class ShrtcodesError(Exception):
    ...


class UnrecognizedShortcode(ShrtcodesError):
    ...


class Shrtcodes:
    def __init__(self):
        self._inline_handlers: dict[str, Callable[..., str]] = {}
        self._block_handlers: dict[str, Callable[..., str]] = {}

    def register_inline(self, name: str):
        def decorator(handler: Callable[..., str]):
            self._inline_handlers = {**self._inline_handlers, name: handler}
            return handler

        return decorator

    def register_block(self, name: str):
        def decorator(handler: Callable[..., str]):
            self._block_handlers = {**self._block_handlers, name: handler}
            return handler

        return decorator

    def process_text(self, text: str) -> str:
        text_stack = [""]
        shortcode_stack: list[tuple[str, list, dict]] = []
        for line in text.splitlines(keepends=True):
            if self._is_escaped_shortcode(line):
                text_stack[-1] += line[1:]
            elif not self._is_shortcode(line):
                text_stack[-1] += line
            elif line.strip() == "{% / %}":
                name, args, kwargs = shortcode_stack.pop()
                t = self._block_handlers[name](text_stack.pop(), *args, **kwargs)
                text_stack[-1] += t
            else:
                name, args, kwargs = self._parse_shortcode(line)
                if name in self._block_handlers:
                    shortcode_stack.append((name, args, kwargs))
                    text_stack.append("")
                elif name in self._inline_handlers:
                    text_stack[-1] += (
                        self._inline_handlers[name](*args, **kwargs) + "\n"
                    )
                else:
                    raise UnrecognizedShortcode(name)
        return "".join(text_stack)

    @classmethod
    def _is_escaped_shortcode(cls, line: str) -> bool:
        return line.startswith("\{% ") and line.strip().endswith(" %}")

    @classmethod
    def _is_shortcode(cls, line: str) -> bool:
        return line.startswith("{% ") and line.strip().endswith(" %}")

    @classmethod
    def _parse_shortcode(cls, line: str) -> tuple[str, list, dict]:
        line = line.strip()[3:-3]
        name = line.split()[0]
        args, kwargs = cls._parse_shortcode_arguments(line[len(name) :])
        return name, args, kwargs

    @classmethod
    def _parse_shortcode_arguments(cls, raw_args: str) -> tuple[list, dict]:
        raw_args = raw_args.strip()
        all_args = shlex.split(raw_args)
        args = []
        kwargs = {}
        for arg in all_args:
            if match := re.match(r"^(\w+)=(.*)$", arg):
                kwargs[match.group(1)] = match.group(2)
            else:
                args.append(arg)
        return args, kwargs
