# purajit.github.io

Personal website! It's simple, it's static, it's served out of GitHub Pages. People overcomplicate web development, but for 99% of cases,
I don't believe you need anything more than some simple HTML + CSS + JS. Especially for a personal website! Keep the web simple, folks.
There's really nothing impressive about complexity.

# Development

I use a custom site generator whose logic is pretty simple - each page is either a table of contents of its children, or an end page. 
The structure is defined in `data/sitemap.json`. All templates are in `templates/`. Statics are in `docs/static`, and the website is
served out of `docs/`.

Locally, run
```sh
make run-server
```
to run the website on `localhost:80`. You will need Docker. Alternatively, you can just `file://`, but the linking and static sourcing
will not work.

When you make statics changes (including css/js), just refreshing the page will show you the updates. If you made changes to the 
page contents, regenerate the site with
```sh
make generate-pages
```

Check-in all files, including the generated ones. I used to have a GHA that ran the generation, but that's a bit wonkier with branch
protection.
