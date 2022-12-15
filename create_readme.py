import subprocess

from shrtcodes import Shrtcodes

shortcodes = Shrtcodes()


@shortcodes.register_inline("cat")
def handle_cat(file_path):
    with open(file_path) as f:
        return f.read()


@shortcodes.register_inline("execute_python")
def handle_execute_python(file_path):
    cmd = subprocess.run(["python", file_path], capture_output=True)
    return cmd.stdout.decode()


with open("README.template.md") as f:
    in_text = f.read()

out_text = shortcodes.process_text(in_text)
with open("README.md", "w") as f:
    f.write(out_text)
