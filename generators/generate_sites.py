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


def generate_page_params(level_data):
    params = {}
    if isinstance(level_data, dict):
        for data_var, data_file in level_data.items():
            params[data_var] = read_json_file(data_file)
    elif isinstance(level_data, str):
        params["data"] = level_data
    else:
        LOG.error("Level data must be dict or str")
        raise Exception("invalid data type")
    return params


def generate_children_from_definition(children_data, level_name, next_level_path):
    contents = []
    for child_data in children_data["contents"]:
        with open(os.path.join(DATA_DIR, level_name, child_data["route"])) as f:
            data = f.read()
        next_level = {
            "template": children_data["template"],
            "title": child_data["title"],
            "route": child_data["route"],
            "data": data,
        }
        contents.append(generate_level(next_level, next_level_path))
    return contents


def generate_children(children_data, level_path, level_name):
    params = {}
    if isinstance(children_data, list):
        # children explicitly defined
        params["contents"] = [
            generate_level(child, level_path) for child in children_data]
    elif isinstance(children_data, str):
        # children to be generated from json definition
        params["contents"] = generate_children_from_definition(
            read_json_file(children_data), level_name, level_path)
    else:
        LOG.error("Children data must be list or str")
        raise Exception("invalid children type")
    return params


def generate_level(level_map, previous_level_path):
    level_name = level_map["route"]
    level_path = os.path.join(previous_level_path, level_name)
    output_file = os.path.join(level_path, 'index.html')
    link = os.path.join("/", level_path)
    LOG.info(f"{previous_level_path} | {level_path} | {output_file} | {link}")

    os.makedirs(os.path.join(SITE_DIR, level_path), exist_ok=True)

    if "children" in level_map:
        # generate children and get table of contents
        additional_params = generate_children(
            level_map["children"], level_path, level_name)
        additional_params["content_type"] = "contents-page"
    else:
        # single page
        additional_params = generate_page_params(level_map.get("data", {}))

    params = {
        "title": level_map["title"],
        "tab_title": level_map.get("tab_title"),
        "previous_page": os.path.join('/', previous_level_path),
        **additional_params
    }

    render_and_write(level_map["template"], params, output_file)

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
