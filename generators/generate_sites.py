import json
import logging
import os
import shutil
import sys

from jinja2 import FileSystemLoader, Environment

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

LOG = logging.getLogger()
SITE_DIR = "./docs"
DATA_DIR = "./data"
TEMPLATES_DIR = "./templates"
PERMANENT_PATHS = ['CNAME', 'static']
TEMPLATE_ENV = Environment(loader=FileSystemLoader(searchpath=TEMPLATES_DIR))


def read_json_file(filename):
    with open(os.path.join(DATA_DIR, filename)) as f:
        return json.loads(f.read())


def render_and_write(template_file, params, output_file):
    output = TEMPLATE_ENV.get_template(template_file).render(**params)

    with open(os.path.join(SITE_DIR, output_file), "w") as f:
        f.write(output)


def generate_page_params(level_path, level_data):
    params = {}
    if level_data.get("data_type"):
        with open(os.path.join(DATA_DIR, level_path)) as f:
            params["data"] = f.read()
            if level_data.get("data_type") == "json":
                params["data"] = json.loads(params["data"])

    return params


def generate_level(level_map, previous_level_path):
    level_name = level_map["route"]
    level_path = os.path.join(previous_level_path, level_name)
    output_file = os.path.join(level_path, 'index.html')
    link = os.path.join("/", level_path)
    template = level_map.get("template", "template_contents.html")
    LOG.info(f"{previous_level_path} | {level_path} | {output_file} | {link} | {template}")

    os.makedirs(os.path.join(SITE_DIR, level_path), exist_ok=True)

    if "children" in level_map:
        # generate children and get table of contents
        additional_params = {
            "contents": [
                generate_level(child, level_path) for child in level_map["children"]
            ],
            "content_type": "contents-page"
        }
    else:
        # single page
        additional_params = generate_page_params(level_path, level_map)

    params = {
        "title": level_map["title"],
        "tab_title": level_map.get("tab_title"),
        "previous_page": os.path.join('/', previous_level_path),
        **additional_params
    }

    render_and_write(template, params, output_file)

    return {
        "title": level_map["title"],
        "link": link,
    }


def clear_directory():
    paths = os.listdir(SITE_DIR)
    for path in paths:
        if path in PERMANENT_PATHS:
            continue
        path = os.path.join(SITE_DIR, path)
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)

def main():
    sitemap = read_json_file("sitemap.json")
    clear_directory()
    generate_level(sitemap, previous_level_path="")


if __name__ == "__main__":
    main()
