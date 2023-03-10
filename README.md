# purajit.github.io

Personal website! It's simple, it's static, it's served out of GitHub Pages. People overcomplicate web development, but for 99% of cases,
I don't believe you need anything more than some simple HTML + CSS (+ JS, barely). Especially for a personal website! Keep the web simple, folks.
There's really nothing impressive about complexity.

The site's served at [https://purajit.com](https://purajit.com).

# Development

I use the static site generator [purajit/YASS](https://github.com/purajit/YASS), with the default structure.

Assets are stored separately in the [purajit/assets.purajit.github.io](https://github.com/purajit/assets.purajit.github.io) repo to keep deploys artifacts and times small.

## Local testing
```sh
# To run the website locally on `localhost:80`
make run-server

# To stop the server
make stop-server

# To regenerate the website if changes were made to non-static files
# Changes will be instantly reflected
make generate-pages-cdn
```

You will need [colima](https://github.com/abiosoft/colima).

If you want to change assets and test it, you will have to clone the assets repo [purajit/assets.purajit.github.io](https://github.com/purajit/assets.purajit.github.io) into the same parent directory as this one. To use locally-available assets, run

```sh
make generate-pages-local
```

You could also use this simply to avoid network requests.
