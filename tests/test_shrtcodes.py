import pytest

from shrtcodes import (
    Shrtcodes,
    UnrecognizedShortcode,
)


def test_kwargs() -> None:
    text = """
{% echo Dog Cat %}
{% echo first=Dog last=Cat %}
{% echo first=Dog last="Kitty Cat" %}
{% echo last=Dog first=Cat %}
{% echo Dog %}
{% echo first=Dog %}
{% echo last=Dog %}
"""

    shortcodes = Shrtcodes()

    @shortcodes.register_inline("echo")
    def handle_echo(first: str = "!!!", last: str = "...") -> str:
        return first + " " + last

    assert (
        shortcodes.process_text(text)
        == """
Dog Cat
Dog Cat
Dog Kitty Cat
Cat Dog
Dog ...
Dog ...
!!! Dog
"""
    )


def test_quoting() -> None:
    text = """
{% echo "Dog Cat" %}
{% echo 'Dog Cat' %}
{% echo 'Dog " Cat' %}
"""

    shortcodes = Shrtcodes()

    @shortcodes.register_inline("echo")
    def handle_echo(s: str) -> str:
        return s

    assert (
        shortcodes.process_text(text)
        == """
Dog Cat
Dog Cat
Dog " Cat
"""
    )


def test_escaping() -> None:
    text = """
{% echo Dog %}
\\{% echo Dog %}
{% echo Dog %}
"""

    shortcodes = Shrtcodes()

    @shortcodes.register_inline("echo")
    def handle_echo(s: str) -> str:
        return s

    assert (
        shortcodes.process_text(text)
        == """
Dog
{% echo Dog %}
Dog
"""
    )


def test_block() -> None:
    text = """
foo

{% ntimes 3 %}
bar
{% / %}

baz
"""

    shortcodes = Shrtcodes()

    @shortcodes.register_block("ntimes")
    def handle_ntimes(block: str, n: str) -> str:
        return block * int(n)

    assert (
        shortcodes.process_text(text)
        == """
foo

bar
bar
bar

baz
"""
    )


def test_nesting() -> None:
    text = """
{% double %}
{% link google.com Google %}
{% double %}
Hello!
{% / %}
Bye!
{% / %}
"""

    shortcodes = Shrtcodes()

    @shortcodes.register_inline("link")
    def link_handler(url: str, text: str) -> str:
        return f'<a href="https://{url}">{text}</a>'

    @shortcodes.register_block("double")
    def double_handler(block: str) -> str:
        return block * 2

    assert (
        shortcodes.process_text(text)
        == """
<a href="https://google.com">Google</a>
Hello!
Hello!
Bye!
<a href="https://google.com">Google</a>
Hello!
Hello!
Bye!
"""
    )


def test_process_raises_on_unrecognized_shortcode() -> None:
    with pytest.raises(UnrecognizedShortcode):
        Shrtcodes().process_text(
            """
foo bar baz
{% hello %}
foo bar baz
"""
        )
