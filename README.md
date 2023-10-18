# shrtcodes

![example workflow name](https://github.com/Peter554/shrtcodes/workflows/CI/badge.svg)

`pip install shrtcodes`

Shortcodes for Python.

## Example:

A toy example.

Define our shortcodes:

```py
# example.py
from shrtcodes import Shrtcodes


shortcodes = Shrtcodes()


# {% img src alt %} will create an image.
@shortcodes.register_inline("img")
def handle_img(src: str, alt: str) -> str:
    return f'<img src="{src}" alt="{alt}"/>'


# {% repeat n %}...{% / %} will repeat a block n times.
@shortcodes.register_block("repeat")
def handle_repeat(block: str, n: str) -> str:
    return block * int(n)


# we can call process_text to get the final text.
in_text = "..."
out_text = shortcodes.process_text(in_text)

# or, we can create a CLI.
shortcodes.create_cli()

```

```
python example.py --help
```

```
usage: example.py [-h] [--check_file CHECK_FILE] in_file

positional arguments:
  in_file               File to be processed

options:
  -h, --help            show this help message and exit
  --check_file CHECK_FILE
                        Checks the output against this file and errors if
                        there is a diff

```

Write some text:

```
# example.txt
Hello!

{% img http://cutedogs.com/dog123.jpg "A very cute dog" %}

Foo bar baz...

{% repeat 3 %}
Woop
{% / %}

Bye!
```

Process the text:

```
python example.py example.txt
```

```
Hello!

<img src="http://cutedogs.com/dog123.jpg" alt="A very cute dog"/>

Foo bar baz...

Woop
Woop
Woop

Bye!
```

A more useful example would be the generation of this README itself.
See [`make_readme.py`](/make_readme.py) and [`.README.template.md`](/.README.template.md).
