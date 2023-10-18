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
