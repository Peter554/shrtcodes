import pytest

from shrtcodes.shrtcodes import (
    InvalidShortcodeName,
    OverpairedShortcode,
    Shrtcodes,
    UnpairedShortcode,
    UnrecognizedShortcode,
)


@pytest.mark.parametrize(
    "shortcode, handler_name, params",
    [
        ("{% hello %}", "hello", []),
        ('{% hello "foo" %}', "hello", ["foo"]),
        ("{% hello 'foo bar baz' %}", "hello", ["foo bar baz"]),
        (
            '{% hello "foo bar baz", 4.32, "4.32", True %}',
            "hello",
            ["foo bar baz", 4.32, "4.32", True],
        ),
    ],
)
def test_find_shortcode_start(shortcode, handler_name, params):
    lines = ["foo bar baz", "", shortcode, "", "foo bar baz"]

    assert Shrtcodes._find_shortcode_start(lines)[0] == 2
    assert Shrtcodes._find_shortcode_start(lines)[1] == handler_name
    assert Shrtcodes._find_shortcode_start(lines)[2] == params


def test_find_shortcode_end():
    lines = [
        "foo bar baz",
        "",
        "{% hello %}",
        "foo bar baz",
        "{% end_hello %}",
        "",
        "foo bar baz",
    ]

    assert Shrtcodes._find_shortcode_end(lines, "hello") == 4


def test_process_1():
    in_text = "\n".join(
        [
            "foo bar baz",
            "",
            "{% hello %}",
            "",
            "{% link 'Google', 'google.com' %}",
            "",
            "{% double %}",
            "Please please...",
            "...double me!",
            "{% end_double %}",
            "",
            "{% ntimes 3 %}",
            "Please please...",
            "...triple me!",
            "{% end_ntimes %}",
            "",
            "foo bar baz",
        ]
    )

    shrtcodes = Shrtcodes()

    @shrtcodes.register("hello")
    def hello_handler():
        return "Hello!"

    @shrtcodes.register("link")
    def link_handler(text, url):
        return f'<a href="https://{url}">{text}</a>'

    @shrtcodes.register_paired("double")
    def double_handler(block):
        return f"{block}\n{block}"

    @shrtcodes.register_paired("ntimes")
    def ntimes_handler(n, block):
        return "\n".join([block] * n)

    out_text = shrtcodes.process(in_text)

    assert out_text == "\n".join(
        [
            "foo bar baz",
            "",
            "Hello!",
            "",
            '<a href="https://google.com">Google</a>',
            "",
            "Please please...",
            "...double me!",
            "Please please...",
            "...double me!",
            "",
            "Please please...",
            "...triple me!",
            "Please please...",
            "...triple me!",
            "Please please...",
            "...triple me!",
            "",
            "foo bar baz",
        ]
    )


def test_process_2():
    in_text = "\n".join(
        [
            "Foo bar baz.",
            "",
            "{% img 'https://images.com/cutedog.jpg', 'A cute dog!' %}",
            "",
            "{% details 'Some extra info' %}",
            "This is some extra info.",
            "{% end_details %}",
            "",
            "Foo bar baz.",
        ]
    )

    shrtcodes = Shrtcodes()

    @shrtcodes.register("img")
    def img_handler(src, alt):
        return f'<img src="{src}" alt="{alt}"/>'

    @shrtcodes.register_paired("details")
    def details_handler(summary, block):
        return f"<details><summary>{summary}</summary>{block}</details>"

    out_text = shrtcodes.process(in_text)

    assert out_text == "\n".join(
        [
            "Foo bar baz.",
            "",
            '<img src="https://images.com/cutedog.jpg" alt="A cute dog!"/>',
            "",
            "<details><summary>Some extra info</summary>This is some extra info.</details>",
            "",
            "Foo bar baz.",
        ]
    )


def test_context():
    in_text = "\n".join(
        [
            "foo bar baz",
            "",
            "{% user_name %}",
            "",
            "{% ntimes 'Bye :)' %}",
            "hello!!",
            "{% end_ntimes %}",
            "",
            "foo bar baz",
        ]
    )

    shrtcodes = Shrtcodes()

    @shrtcodes.register("user_name")
    def user_name_handler(context):
        user_name = context["user"]["name"]
        return f"<p>Hello, {user_name}!</p>"

    @shrtcodes.register_paired("ntimes")
    def ntimes_handler(extra, block, context):
        n = context["ntimes"]
        return "\n".join([block] * n + [extra])

    out_text = shrtcodes.process(in_text, {"user": {"name": "Paul"}, "ntimes": 2})

    assert out_text == "\n".join(
        [
            "foo bar baz",
            "",
            "<p>Hello, Paul!</p>",
            "",
            "hello!!",
            "hello!!",
            "Bye :)",
            "",
            "foo bar baz",
        ]
    )


def test_nested():
    in_text = "\n".join(
        [
            "{% double %}",
            "{% link 'Google', 'google.com' %}",
            "{% double %}",
            "Hello!",
            "{% end_double %}",
            "Bye!",
            "{% end_double %}",
        ]
    )

    shrtcodes = Shrtcodes(allow_nested=True)

    @shrtcodes.register("link")
    def link_handler(text, url):
        return f'<a href="https://{url}">{text}</a>'

    @shrtcodes.register_paired("double")
    def double_handler(block):
        return "\n".join([block, block])

    out_text = shrtcodes.process(in_text)

    assert out_text == "\n".join(
        [
            '<a href="https://google.com">Google</a>',
            "Hello!",
            "Hello!",
            "Bye!",
            '<a href="https://google.com">Google</a>',
            "Hello!",
            "Hello!",
            "Bye!",
        ]
    )


def test_process_raises_on_unrecognized_shortcode():
    with pytest.raises(UnrecognizedShortcode):
        Shrtcodes().process("\n".join(["foo bar baz", "{% hello %}", "foo bar baz",]))


def test_process_raises_on_unpaired_shortcode():
    shortcodes = Shrtcodes()

    @shortcodes.register_paired("hello")
    def hello():
        return "Hello!"

    with pytest.raises(UnpairedShortcode):
        shortcodes.process("\n".join(["foo bar baz", "{% hello %}", "foo bar baz",]))


def test_process_raises_on_overpaired_shortcode():
    shortcodes = Shrtcodes()

    @shortcodes.register("hello")
    def hello():
        return "Hello!"

    with pytest.raises(OverpairedShortcode):
        shortcodes.process(
            "\n".join(["foo bar baz", "{% hello %}", "{% end_hello %}", "foo bar baz",])
        )


def test_register_raises_on_invalid_shortcode_name():
    shortcodes = Shrtcodes()

    with pytest.raises(InvalidShortcodeName):

        @shortcodes.register("end_foo")
        def foo():
            return "foo"

    with pytest.raises(InvalidShortcodeName):

        @shortcodes.register_paired("end_bar")
        def bar():
            return "bar"
