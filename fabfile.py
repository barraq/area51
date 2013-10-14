import os
import re
import time
import shutil
import jinja2

from fabric.api import run, execute, task, abort, local
from fabric.colors import yellow, blue, red

OUTPUT_DIR = "gen"
TEMPLATES_DIR = "templates"
RESOURCES_DIR = "resources"
STATICS_DIRS = "statics"
PROTECTED_DIRS = [STATICS_DIRS, TEMPLATES_DIR]

ABS_ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

ABS_OUTPUT_PATH = os.path.join(ABS_ROOT_PATH, OUTPUT_DIR)


@task
def clean():
    """Clean up generated files."""
    if os.path.exists(ABS_OUTPUT_PATH):
        __print_remove(OUTPUT_DIR)
        shutil.rmtree(ABS_OUTPUT_PATH)


@task
def generate():
    """Generate website locally."""

    # clean first...
    execute(clean)

    # copy statics
    if os.path.exists(STATICS_DIRS):
        __print_copy(STATICS_DIRS, os.path.join(OUTPUT_DIR, STATICS_DIRS))
        shutil.copytree(STATICS_DIRS, os.path.join(OUTPUT_DIR, STATICS_DIRS))

    # merge resources
    for root, dirs, files in os.walk(RESOURCES_DIR):
        for file in files:
            __print_copy(os.path.join(root, file), os.path.join(OUTPUT_DIR, file))
            shutil.copyfile(os.path.join(root, file), os.path.join(OUTPUT_DIR, file))

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath=TEMPLATES_DIR))

    # go through each files in TEMPLATES_DIR
    for root, dirs, files in os.walk(TEMPLATES_DIR):
        for dir in dirs:
            if dir in PROTECTED_DIRS:
                abort(red("you cannot use restricted names (i.e. {}) for naming your directories.".format(
                    ','.join(PROTECTED_DIRS))))
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


@task
def publish(from_branch="master", to_branch="gh-pages"):
    local("git branch -D {0}".format(to_branch))
    local("git checkout --orphan {0}".format(to_branch))
    local("git rm --cached $(git ls-files)")
    local("bower install")
    execute(generate)
    local("git clean -xdf -e {0}".format(OUTPUT_DIR))
    local("mv gen/* .")
    local("rm -r {0}".format(OUTPUT_DIR))
    local("git add .")
    local("git commit -m \"updating at {0}\"".format(time.strftime("%d %b %Y %H:%M%S", time.localtime())))
    local("git push origin {0} --force".format(to_branch))
    local("git checkout {0}".format(from_branch))


# --- stupid output functions ---


def __print_create(path):
    print(yellow("creating ") + blue(os.path.join(path)))


def __print_copy(src, dst):
    print(yellow("copying ") + blue(src) + " to " + blue(dst))


def __print_remove(path):
    print(yellow("removing ") + blue(path))


def __print_build(root, file):
    print(yellow("building ") + blue(os.path.join(root, file)))