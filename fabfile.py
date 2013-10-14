import os
import re
import shutil
import jinja2
import fabric

TEMPLATES_DIR = "templates"
OUTPUT_DIR = "gen"
PROTECTED_DIRS = ['assets', 'statics', 'templates']

ABS_ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

ABS_OUTPUT_PATH = os.path.join(ABS_ROOT_PATH, OUTPUT_DIR)


def clean():
    if os.path.exists(ABS_OUTPUT_PATH):
        __print_remove(OUTPUT_DIR)
        shutil.rmtree(ABS_OUTPUT_PATH)


def build():
    # clean first...
    clean()

    # copy statics, and assets
    for dir in ['assets', "statics"]:
        __print_move(dir, os.path.join(OUTPUT_DIR, dir))
        shutil.copytree(dir, os.path.join(OUTPUT_DIR,dir))

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath=TEMPLATES_DIR))

    # go through each files in TEMPLATES_DIR
    for root, dirs, files in os.walk(TEMPLATES_DIR):
        for dir in dirs:
            __print_create(os.path.join(OUTPUT_DIR, dir))
            os.makedirs(os.path.join(ABS_OUTPUT_PATH, dir))
        for file in files:
             name, ext = os.path.splitext(file)
             if not name.startswith("_") and ext == ".html":
                 __print_build(root, file)
                 template = env.get_template(file)
                 file_output_dir = re.sub(r"^({})".format(TEMPLATES_DIR), OUTPUT_DIR, root)
                 with open(os.path.join(file_output_dir, file), "wb") as fh:
                    fh.write(template.render())


# --- stupid output functions ---


def __print_create(path):
    print(fabric.colors.yellow("creating ")+fabric.colors.blue(os.path.join(path)))


def __print_move(src, dst):
    print(fabric.colors.yellow("moving ")+fabric.colors.blue(src)+" to "+fabric.colors.blue(dst))


def __print_remove(path):
    print(fabric.colors.yellow("removing ")+fabric.colors.blue(path))


def __print_build(root, file):
    print(fabric.colors.yellow("building ")+fabric.colors.blue(os.path.join(root, file)))