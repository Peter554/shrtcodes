# shrtcodes

[![Build Status](https://travis-ci.org/Peter554/shrtcodes.svg?branch=master)](https://travis-ci.org/Peter554/shrtcodes)

`pip install shrtcodes`

Simple shortcodes for Python.

## Example

Text containing shortcodes.

- `img` - a shortcode.
- `details` - a paired shortcode.

```text
Foo bar baz.

{% img "https://images.com/cutedog.jpg", "A cute dog!" %}

{% details "Some extra info" %}
This is some extra info.
{% end_details %}

Foo bar baz.
```

Build your shortcodes:

```python
# shortcodes.py

from shrtcodes.shrtcodes import Shrtcodes

shortcodes = Shrtcodes()

# `img_handler` is a shortcode handler. 
#   * Arguments correspond to the shortcode parameters.  
@shortcodes.register('img')
def img_handler(src, alt):
    return f'<img src="{src}" alt="{alt}"/>'

# `details_handler` is a paired shortcode handler.
#   * Starting arguments correspond to the shortcode parameters.  
#   * Last argument is the contained block.
@shortcodes.register_paired('details')
def details_handler(summary, block):
    return f'<details><summary>{summary}</summary>{block}</details>'
```

Use your shortcodes:

```python
from shortcodes import shortcodes
text = shortcodes.process('...')
```

Output:

```text
Foo bar baz.

<img src="https://images.com/cutedog.jpg" alt="A cute dog!"/>

<details><summary>Some extra info</summary>This is some extra info.</details>

Foo bar baz.
```

## Further examples

See the tests.
