import json
import os

from jinja2 import FileSystemLoader, Environment

TEMPLATES_DIR = "./templates"
TEMPLATE_ENV = Environment(loader=FileSystemLoader(searchpath=TEMPLATES_DIR))

SITE_DIR = "./docs/new"
DATA_DIR = "./data"

# HEADER AND FOOTER
HEADER_TEMPLATE = TEMPLATE_ENV.get_template("header.html")
FOOTER_TEMPLATE = TEMPLATE_ENV.get_template("footer.html")

def read_json_file(filename):
    with open(os.path.join(DATA_DIR, filename)) as f:
        return json.loads(f.read())


def render_and_write(template_file, params, output_file):
    header = HEADER_TEMPLATE.render(
        title=params["title"],
        previous_page=params["previous_page"],
    )
    footer = FOOTER_TEMPLATE.render()
    output = TEMPLATE_ENV.get_template(template_file).render(**params)

    print(SITE_DIR, output_file, os.path.join(SITE_DIR, output_file))
    with open(os.path.join(SITE_DIR, output_file), "w") as f:
        f.write(header)
        f.write(output)
        f.write(footer)


def generate_level(level_map, level_path):
    level_name = level_map.get("route", level_map.get("id", level_map["title"]))
    next_level_path = level_path + (level_name, )
    output_path = os.path.join('', *level_path)
    print(output_path, level_path)
    output_filename = f"{ level_map.get('id', level_map['title']) }.html"
    output_file = os.path.join(output_path, output_filename)

    params = {
        "title": level_map["title"],
        "tab_title": level_map.get("title"),
        "previous_page": level_path[-1] if len(level_path) > 0 else None,
    }

    if "children" in level_map:
        os.makedirs(os.path.join(SITE_DIR, level_name), exist_ok=True)
        if isinstance(level_map["children"], list):
            params["contents"] = [generate_level(child, next_level_path)
                                  for child in level_map["children"]]
        elif isinstance(level_map["children"], str):
            params["contents"] = []
            children_data = read_json_file(level_map["children"])
            for child_data in children_data["contents"]:
                with open(os.path.join(DATA_DIR, level_name, child_data["id"])) as f:
                    data = f.read()
                next_level = {
                    "template": children_data["template"],
                    "title": child_data["title"],
                    "id": child_data["id"],
                    "data": data,
                }
                params["contents"].append(generate_level(next_level, next_level_path))
        else:
            raise Exception("invalid children type")
    else:
        level_data = level_map.get("data", {})
        if isinstance(level_data, dict):
            for data_var, data_file in level_data.items():
                params[data_var] = read_json_file(data_file)
        elif isinstance(level_data, str):
            params["data"] = level_data
        else:
            raise Exception("invalid data type")

    render_and_write(level_map["template"], params, output_file)

    return {
        "title": level_map["title"],
        "link": output_file,
    }


def main():
    sitemap = read_json_file("sitemap.json")
    generate_level(sitemap, level_path=tuple())


if __name__ == "__main__":
    main()
