# purajit.github.io

Personal website! It's simple, it's static, it's served out of GitHub Pages. People overcomplicate web development, but for 99% of cases,
I don't believe you need anything more than some simple HTML + CSS (+ JS, barely). Especially for a personal website! Keep the web simple, folks.
There's really nothing impressive about complexity.

The site's served at [https://purajit.com](https://purajit.com).

# How it's built

A single small generator, [`build.py`](build.py), turns a tree of pages into
`docs/`. There are no hidden conventions to memorise:

```
site.json      site-wide config (name, URLs, asset CDN)
sitemap.json   the tree of pages
data/          page content, mirroring the routes (text / markdown / json)
templates/     Jinja templates (base.html + a few special pages)
docs/          generated output (gitignored except CNAME/static)
```

## Adding a page

Add a node to `sitemap.json` and (for a content page) a matching file under
`data/`. That's it — the generator figures out the rest.

```json
{
  "title": "my new page",
  "route": "my-new-page",
  "data_type": "markdown"
}
```

* a node **with `children`** becomes a listing page (template defaults to
  `contents.html`),
* a node **with `data_type`** becomes a content page (template defaults to
  `page.html`, `data_type` is `text`, `markdown` or `json`),
* `template` is **optional** — only set it for a page that needs custom markup
  (see `templates/recipe.html`, `templates/zeitgeist.html`, …),
* `page_class` adds extra classes to the content wrapper (e.g.
  `"preserve-whitespace"` for poetry),
* `meta_*`, canonical URLs and the `purajit | <section>` header are all
  **computed** for you and can be overridden per-node if needed.

Every template extends [`templates/base.html`](templates/base.html), so the
page chrome (head, meta, header, footer) lives in exactly one place.

## Local testing

```sh
# run the site locally on localhost:80
make run-server

# stop it
make stop-server

# regenerate after changing content/templates/config
make generate-pages-cdn    # production (CDN asset URLs)
make generate-pages-local  # local asset URLs
```

The generator is a [uv](https://docs.astral.sh/uv/) script, so
`uv run build.py` works on its own with no setup. `make run-server` uses
[colima](https://github.com/abiosoft/colima).

If you want to change assets and test them, clone the assets repo
[purajit/assets.purajit.github.io](https://github.com/purajit/assets.purajit.github.io)
into the same parent directory as this one, then use
`make generate-pages-local` so the site points at the local copies.
