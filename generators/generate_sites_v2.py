import json
import os

from jinja2 import FileSystemLoader, Environment

TEMPLATES_DIR = "./templates"
TEMPLATE_ENV = Environment(loader=FileSystemLoader(searchpath=TEMPLATES_DIR))

SITE_DIR = "docs/new"
DATA_DIR = "data"

# HEADER AND FOOTER
HEADER_TEMPLATE = TEMPLATE_ENV.get_template("header.html")
FOOTER_TEMPLATE = TEMPLATE_ENV.get_template("footer.html")

def render_and_write(template_file, params, output_file):
    header = HEADER_TEMPLATE.render(
        title=params["title"],
        previous_page=params["previous_page"],
    )
    footer = FOOTER_TEMPLATE.render()
    output = TEMPLATE_ENV.get_template(template_file).render(**params)

    with open(f"{SITE_DIR}/{output_file}", "w") as f:
        f.write(header)
        f.write(output)
        f.write(footer)


def main():
    with open(f"{DATA_DIR}/sitemap.json") as f:
        sitemap = json.loads(f.read())

    children = []
    for child in sitemap["children"]:
        # render each
        # accumulate list

    render_and_write("template_index.html", {
        "title": sitemap["title"],
        "tab_title": sitemap["tab_title"],
        "contents": text,
    }, "index.html")

    # WRITING
    with open(f"{DATA_DIR}/writing.json") as f:
        writings = json.loads(f.read())
    os.makedirs(f"{SITE_DIR}/writing", exist_ok=True)
    for writing in writings:
        with open(f"{DATA_DIR}/writing/{writing['id']}.html") as f:
            text = f.read()
        render_and_write("template_writing.html", {
            "title": writing["title"],
            "previous_page": "../writing.html",
            "writing": text,
        }, f"writing/{ writing['id'] }.html")

    # THOUGHTS
    with open(f"{DATA_DIR}/thoughts.json") as f:
        thought_groups = json.loads(f.read())

    render_and_write("template_thoughts.html", {
        "title": "thoughts",
        "previous_page": "/",
        "thought_groups": thought_groups,
    }, "thoughts.html")

    # LOREM
    render_and_write("template_lorem.html", {
        "title": "lorem",
        "previous_page": "/",
    }, "lorem.html")

    # ABOUT PAGE
    with open(f"{DATA_DIR}/favorites.json") as f:
        favs = json.loads(f.read())

    with open(f"{DATA_DIR}/work.json") as f:
        jobs = json.loads(f.read())

    render_and_write("template_about.html", {
        "title": "about",
        "previous_page": "/",
        "jobs": jobs,
        "favs": favs
    }, "about.html")

if __name__ == "__main__":
    main()
