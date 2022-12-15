from shrtcodes import Shrtcodes

in_text = """
Hello!

{% img http://cutedogs.com/dog123.jpg "A very cute dog" %}

Foo bar baz...

{% repeat 3 %}
Woop
{% / %}

Bye!
""".strip()

shortcodes = Shrtcodes()


@shortcodes.register_inline("img")
def handle_img(src, alt):
    return f'<img src="{src}" alt="{alt}"/>'


@shortcodes.register_block("repeat")
def handle_repeat(block, n):
    return block * int(n)


out_text = shortcodes.process_text(in_text)
print(out_text)
