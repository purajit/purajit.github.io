#!/usr/bin/env python3
"""A tiny static-site generator for purajit.com.

The site is a tree of pages described by ``sitemap.json``:

* a node with ``children`` is a listing page,
* a node with ``data_type`` is a content page (``text`` / ``markdown`` / ``json``),
* ``template`` is optional. Listing pages default to ``contents.html`` and
  content pages to ``page.html``, so most new pages need nothing more than a
  ``title``, a ``route`` and (optionally) a data file.

Content lives in ``data/`` (mirroring routes), templates in ``templates/``,
and the generated site is written to ``docs/``.

    python build.py            # production (CDN asset URLs)
    python build.py --local    # local asset URLs (for `make run-server`)
"""
# /// script
# requires-python = ">=3.9"
# dependencies = ["jinja2", "marko"]
# ///
from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
from pathlib import Path

import marko
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).resolve().parent

DEFAULTS = {
    "site_name": "site",
    "base_url": "",
    "static_url": "",
    "local_static_url": "",
    "default_image": "/static/tiledspace.jpg",
    "site_dir": "docs",
    "data_dir": "data",
    "templates_dir": "templates",
    "sitemap_file": "sitemap.json",
    "functions_file": None,
    "permanent_paths": [],
}


def load_config(path: Path) -> dict:
    config = dict(DEFAULTS)
    config.update(json.loads(path.read_text()))
    return config


def load_functions(env: Environment, path: str | None) -> None:
    """Expose every public callable from the functions file to templates."""
    if not path or not (ROOT / path).exists():
        return
    spec = importlib.util.spec_from_file_location("site_functions", ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for name in dir(module):
        if name.startswith("_"):
            continue
        value = getattr(module, name)
        if callable(value):
            env.globals[name] = value


def read_data(data_dir: Path, level_path: str, data_type: str | None):
    if not data_type:
        return None
    file = data_dir / level_path
    if not file.exists():
        return None
    text = file.read_text()
    if data_type == "json":
        return json.loads(text)
    if data_type == "markdown":
        return marko.convert(text)
    return text


def is_external(route: str) -> bool:
    return route.startswith(("http://", "https://"))


def clean_site(site_dir: Path, permanent: list[str]) -> None:
    site_dir.mkdir(parents=True, exist_ok=True)
    for child in site_dir.iterdir():
        if child.name in permanent:
            continue
        if child.is_dir() and not child.is_symlink():
            shutil.rmtree(child)
        else:
            child.unlink()


def render_node(env, cfg, node, data_dir, site_dir, parent_path, parent_page, section):
    """Render ``node`` (and its subtree); return nothing."""
    route = node["route"]
    level_path = f"{parent_path}/{route}".strip("/") if route else parent_path
    link = "/" + level_path if level_path else "/"
    canonical = link if link.endswith("/") else link + "/"
    is_root = not level_path

    title = node["title"]
    tab_title = node.get("tab_title", title)
    this_section = title if section is None else section
    # The visible header names the *section* (e.g. "purajit | writing"), not
    # the individual page, which is shown in the page body instead.
    header_title = title if is_root else f"{cfg['site_name']} | {this_section}"
    meta_title = node.get("meta_title", f"{cfg['site_name']} | {tab_title}")

    children = node.get("children")
    data = None
    params = {
        "title": title,
        "tab_title": tab_title,
        "header_title": header_title,
        "parent_page": parent_page,
        "site_name": cfg["site_name"],
        "base_url": cfg["base_url"],
        "static_url": cfg["_static_url"],
        "page_class": node.get("page_class", ""),
        "meta_title": meta_title,
        "meta_description": node.get("meta_description", meta_title),
        "meta_image": node.get("meta_image", cfg["base_url"] + cfg["default_image"]),
        "meta_type": node.get("meta_type", "website"),
        "meta_url": node.get("meta_url", cfg["base_url"] + canonical),
        "data": data,
    }

    if children is not None:
        template = node.get("template", "contents.html")
        contents = []
        for child in children:
            child_route = child["route"]
            child_link = child_route if is_external(child_route) else (
                "/" + f"{level_path}/{child_route}".strip("/")
            )
            contents.append({"title": child["title"], "link": child_link})
        params["contents"] = contents

        child_section = None if is_root else this_section
        for child in children:
            if is_external(child["route"]):
                continue
            render_node(
                env, cfg, child, data_dir, site_dir, level_path, link, child_section
            )
    else:
        template = node.get("template", "page.html")
        params["data"] = read_data(data_dir, level_path, node.get("data_type"))

    output = site_dir / level_path / "index.html"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(env.get_template(template).render(**params))


def build(config_path: Path, local: bool) -> None:
    cfg = load_config(config_path)
    cfg["_static_url"] = cfg["local_static_url"] if local else cfg["static_url"]

    data_dir = ROOT / cfg["data_dir"]
    site_dir = ROOT / cfg["site_dir"]
    templates_dir = ROOT / cfg["templates_dir"]

    env = Environment(loader=FileSystemLoader(templates_dir))
    load_functions(env, cfg["functions_file"])

    clean_site(site_dir, cfg["permanent_paths"])

    sitemap = json.loads((ROOT / cfg["sitemap_file"]).read_text())
    render_node(env, cfg, sitemap, data_dir, site_dir, "", "/", None)

    print(f"built {cfg['site_name']} -> {cfg['site_dir']} ({'local' if local else 'cdn'} assets)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", nargs="?", default="site.json")
    parser.add_argument("--local", action="store_true", help="use local asset URLs")
    args = parser.parse_args()
    build(ROOT / args.config, args.local)


if __name__ == "__main__":
    main()
