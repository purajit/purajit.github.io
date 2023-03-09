# purajit.github.io

Personal website! It's simple, it's static, it's served out of GitHub Pages. People overcomplicate web development, but for 99% of cases,
I don't believe you need anything more than some simple HTML + CSS (+ JS, barely). Especially for a personal website! Keep the web simple, folks.
There's really nothing impressive about complexity.

The site's served at [https://purajit.com](https://purajit.com).

# Development

I use a custom site generator whose logic is pretty simple - each page is either a table of contents of its children, or an end page. It's trees all the way down.
* The structure is defined in `data/sitemap.json`. 
* All templates are in `templates/`. 
* Statics are in `docs/static`
* The website is served out of `docs/`.
* Assets are stored separately in the `purajit/assets.purajit.github.io` repo to keep deploys artifacts and times small.

This exact same model also serves [https://mythmancer.com](https://mythmancer.com).

## Generating the website
You will have to clone the assets repo `purajit/assets.purajit.github.io` into the same parent directory as this one.

When you make statics changes (including css/js), just refreshing the page will show you the updates. If you made changes to the
page contents, regenerate the site with
```sh
make generate-pages-local
```

## Running the website locally
Run
```sh
make run-server
```
to run the website on `localhost:80`. You will need colima. Alternatively, you can just `file://`, but the linking and static sourcing
will not work.

To stop the server
```sh
docker stop purajit.com
```
