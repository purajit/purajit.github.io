import json
from jinja2 import FileSystemLoader, Environment

with open("data/favorites.json") as f:
    favs = json.loads(f.read())
templateLoader = FileSystemLoader(searchpath="./templates")
templateEnv = Environment(loader=templateLoader)
template = templateEnv.get_template("about_template.html")
output = template.render(
    title="about",
    favs=favs,
    previous_page="/",
)

with open('new/about.html', 'w') as f:
    f.write(output)
