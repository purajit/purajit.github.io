import json
import os

from jinja2 import FileSystemLoader, Environment

SITE_DIR = "./docs"
DATA_DIR = "./data"
TEMPLATES_DIR = "./templates"
TEMPLATE_ENV = Environment(loader=FileSystemLoader(searchpath=TEMPLATES_DIR))


def read_json_file(filename):
    with open(os.path.join(DATA_DIR, filename)) as f:
        return json.loads(f.read())


def render_and_write(template_file, params, output_file):
    output = TEMPLATE_ENV.get_template(template_file).render(**params)

    with open(os.path.join(output_file), "w") as f:
        f.write(output)


def generate_children(children_data, level_name, next_level_path):
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


def generate_level(level_map, level_path):
    level_name = level_map["route"]
    next_level_path = level_path + (level_name, )
    output_path = os.path.join(SITE_DIR, *level_path)
    next_level_output_path = os.path.join(SITE_DIR, *next_level_path)
    output_file = os.path.join(next_level_output_path, 'index.html')
    link = os.path.join(*next_level_path)

    params = {
        "title": level_map["title"],
        "tab_title": level_map.get("tab_title"),
        "previous_page": os.path.join('/', *level_path) if len(level_path) > 0 else None,
    }

    if "children" in level_map:
        os.makedirs(os.path.join(SITE_DIR, level_name), exist_ok=True)
        children_data = level_map["children"]
        if isinstance(children_data, list):
            # children explicitly defined
            params["contents"] = [generate_level(child, next_level_path)
                                  for child in level_map["children"]]
        elif isinstance(level_map["children"], str):
            # children to be generated from json definition
            params["contents"] = generate_children(
                read_json_file(children_data), level_name, next_level_path)
        else:
            raise Exception("invalid children type")
    else:
        # single page
        output_filename = f"{ level_map['route'] }.html"
        output_file = os.path.join(output_path, output_filename)
        link += '.html'
        level_data = level_map.get("data", {})
        if isinstance(level_data, dict):
            for data_var, data_file in level_data.items():
                params[data_var] = read_json_file(data_file)
        elif isinstance(level_data, str):
            params["data"] = level_data
        else:
            raise Exception("invalid data type")

    link = '/' + link
    print(level_path, '|', next_level_path, '|', output_path, '|', next_level_output_path, '|', output_file, '|', link)

    render_and_write(level_map["template"], params, output_file)

    return {
        "title": level_map["title"],
        "link": link,
    }


def main():
    sitemap = read_json_file("sitemap.json")
    generate_level(sitemap, level_path=tuple())


if __name__ == "__main__":
    main()
