import pytest

from shrtcodes import (
    Shrtcodes,
    UnrecognizedShortcode,
)


def test_process_1():
    in_text = """
foo bar baz

{% hello %}
\{% hello %}

{% link google.com Google %}
{% link text="Click me to visit Google" url=google.com %}

{% double %}
Please please...
...double me!
{% / %}

{% ntimes 3 %}
Please please...
...triple me!
{% / %}

foo bar baz
"""

    shrtcodes = Shrtcodes()

    @shrtcodes.register_inline("hello")
    def hello_handler():
        return "Hello!"

    @shrtcodes.register_inline("link")
    def link_handler(url, text):
        return f'<a href="https://{url}">{text}</a>'

    @shrtcodes.register_block("double")
    def double_handler(block):
        return block * 2

    @shrtcodes.register_block("ntimes")
    def ntimes_handler(block, n):
        return block * int(n)

    out_text = shrtcodes.process_text(in_text)

    assert (
        out_text
        == """
foo bar baz

Hello!
{% hello %}

<a href="https://google.com">Google</a>
<a href="https://google.com">Click me to visit Google</a>

Please please...
...double me!
Please please...
...double me!

Please please...
...triple me!
Please please...
...triple me!
Please please...
...triple me!

foo bar baz
"""
    )


def test_process_2():
    in_text = """
Foo bar baz.

{% img https://images.com/cutedog.jpg "A cute dog!" %}

{% details "Some extra info" %}
This is some extra info.
{% / %}

Foo bar baz.
"""

    shrtcodes = Shrtcodes()

    @shrtcodes.register_inline("img")
    def img_handler(src, alt):
        return f'<img src="{src}" alt="{alt}"/>'

    @shrtcodes.register_block("details")
    def details_handler(block, summary):
        return f"""<details>
<summary>
{summary}
</summary>
{block}</details>
"""

    out_text = shrtcodes.process_text(in_text)

    assert (
        out_text
        == """
Foo bar baz.

<img src="https://images.com/cutedog.jpg" alt="A cute dog!"/>

<details>
<summary>
Some extra info
</summary>
This is some extra info.
</details>

Foo bar baz.
"""
    )


def test_nested():
    in_text = """
{% double %}
{% link google.com Google %}
{% double %}
Hello!
{% / %}
Bye!
{% / %}
"""

    shrtcodes = Shrtcodes()

    @shrtcodes.register_inline("link")
    def link_handler(url, text):
        return f'<a href="https://{url}">{text}</a>'

    @shrtcodes.register_block("double")
    def double_handler(block):
        return block * 2

    out_text = shrtcodes.process_text(in_text)

    assert (
        out_text
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


def test_process_raises_on_unrecognized_shortcode():
    with pytest.raises(UnrecognizedShortcode):
        Shrtcodes().process_text(
            """
foo bar baz
{% hello %}
foo bar baz
"""
        )
