import subprocess

from shrtcodes import Shrtcodes

shortcodes = Shrtcodes()


@shortcodes.register_inline("embed_file")
def handle_embed_file(file_path: str, syntax: str = "", comment_char: str = "#") -> str:
    with open(file_path) as f:
        return f"""```{syntax}
{comment_char} {file_path}
{f.read()}
```
"""


@shortcodes.register_inline("execute_python")
def handle_execute_python(*python_args: str) -> str:
    cmd = subprocess.run(["python", *python_args], capture_output=True)
    return f"""```
python {' '.join(python_args)}
```

```
{cmd.stdout.decode()}
```
"""


shortcodes.create_cli()
