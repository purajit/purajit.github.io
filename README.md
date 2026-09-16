# purajit.github.io

Personal website! It's simple, it's static, it's served out of GitHub Pages. People overcomplicate web development, but for 99% of cases,
I don't believe you need anything more than some simple HTML + CSS (+ JS, barely). Especially for a personal website! Keep the web simple, folks.
There's really nothing impressive about complexity.

The site's served at [https://purajit.com](https://purajit.com).

Assets are stored separately in the [purajit/assets.purajit.github.io](https://github.com/purajit/assets.purajit.github.io) repo to keep deploys artifacts and times small.

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

If you want to change assets and test them, clone the assets repo
[purajit/assets.purajit.github.io](https://github.com/purajit/assets.purajit.github.io)
into the same parent directory as this one, then use
`make generate-pages-local` so the site points at the local copies.
