#!/usr/bin/env python3
"""Mirror the zeitgeist album/movie artwork into the assets repo.

The zeitgeist data in ``data/zeitgeist/<year>`` points at remote artwork
(last.fm for albums, letterboxd for movies). This downloads all of it into
``../assets.purajit.github.io/docs/images`` so the site can serve it from the
asset CDN instead of hot-linking, then (optionally) commits and pushes.

    python fetch_assets.py            # download whatever is missing
    python fetch_assets.py --force    # re-download everything
    python fetch_assets.py --push     # download, then commit + push the assets repo
    python fetch_assets.py --dry-run  # just list what would be downloaded

Filenames (must match ``templates/zeitgeist.html``):

    album -> music-<lastfm_id>.png
    movie -> movie-<slugified title>.jpg

last.fm occasionally drops an album's artwork (the stored id 404s). When that
happens we fall back to Deezer, matched by artist + album name.
"""
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow"]
# ///
from __future__ import annotations

import argparse
import io
import json
import re
import subprocess
import sys
import unicodedata
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent
ASSETS_REPO = ROOT.parent / "assets.purajit.github.io"
IMAGES = ASSETS_REPO / "docs" / "images"
ALBUM_URL = "https://lastfm.freetls.fastly.net/i/u/300x300/{}.png"
DEEZER_SEARCH = "https://api.deezer.com/search/album?q={}&limit=8"
USER_AGENT = "Mozilla/5.0 (purajit.com artwork mirror)"

sys.path.insert(0, str(ROOT))
from site_functions import slugify  # noqa: E402


@dataclass(frozen=True)
class Asset:
    name: str
    url: str
    fmt: str  # "PNG" or "JPEG" - the format the file must be in
    artist: str = ""
    album: str = ""


def collect() -> list[Asset]:
    """Return every artwork file the site needs, de-duplicated by filename."""
    assets: dict[str, Asset] = {}
    for year_file in sorted(ROOT.glob("data/zeitgeist/*")):
        if not year_file.name.isdigit():
            continue
        data = json.loads(year_file.read_text())
        for album in data.get("albums", []):
            lastfm_id = album.get("lastfm_id")
            if lastfm_id:
                name = f"music-{lastfm_id}.png"
                assets[name] = Asset(
                    name, ALBUM_URL.format(lastfm_id), "PNG",
                    album.get("artist", ""), album.get("album", ""),
                )
        for movie in data.get("movies", []):
            if movie.get("link"):
                name = f"movie-{slugify(movie['movie'])}.jpg"
                assets[name] = Asset(name, movie["link"], "JPEG")
    return list(assets.values())


def fetch_bytes(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read()
    if not body:
        raise ValueError("empty response")
    return body


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", text.lower())


def deezer_search(query: str) -> list[dict]:
    request = urllib.request.Request(
        DEEZER_SEARCH.format(urllib.parse.quote(query)),
        headers={"User-Agent": USER_AGENT},
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response).get("data", [])


def deezer_cover(artist: str, album: str) -> str | None:
    """Best-effort cover lookup by artist + album name.

    Deezer's free-text search is inconsistent, so try a few query shapes and
    keep the highest-scoring result. A cover is only returned when both the
    artist and the album name match exactly, so we never grab the wrong art.
    """
    best: tuple[int, str] | None = None
    for query in (f"{artist} {album}", f'artist:"{artist}"', f'album:"{album}"'):
        for result in deezer_search(query):
            score = 0
            if normalize(result["artist"]["name"]) == normalize(artist):
                score += 2
            if normalize(result["title"]) == normalize(album):
                score += 3
            cover = result.get("cover_xl") or result.get("cover_big")
            if cover and (best is None or score > best[0]):
                best = (score, cover)
    return best[1] if best and best[0] >= 5 else None


def save_image(body: bytes, dest: Path, fmt: str) -> None:
    """Write ``body`` to ``dest``, converting only if the format differs."""
    image = Image.open(io.BytesIO(body))
    if (image.format or "").upper() == fmt:
        dest.write_bytes(body)
        return
    if fmt == "PNG":
        image.convert("RGBA").save(dest, "PNG")
    else:
        image.convert("RGB").save(dest, "JPEG", quality=90)


def fetch(asset: Asset) -> tuple[int, str]:
    """Download one asset (with fallback); returns (bytes, source_url)."""
    try:
        body, source = fetch_bytes(asset.url), asset.url
    except Exception:
        if not asset.artist:
            raise
        fallback = deezer_cover(asset.artist, asset.album)
        if not fallback:
            raise
        body, source = fetch_bytes(fallback), fallback
    save_image(body, IMAGES / asset.name, asset.fmt)
    return len(body), source


def push() -> None:
    def git(*args: str) -> subprocess.CompletedProcess:
        return subprocess.run(["git", "-C", str(ASSETS_REPO), *args], check=True)

    git("add", "docs/images")
    if subprocess.run(
        ["git", "-C", str(ASSETS_REPO), "diff", "--cached", "--quiet"]
    ).returncode == 0:
        print("assets repo: nothing to push")
        return
    git("commit", "-m", "add zeitgeist artwork")
    git("push")
    print("assets repo: pushed")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--force", action="store_true", help="re-download existing files")
    parser.add_argument("--push", action="store_true", help="commit + push the assets repo")
    parser.add_argument("--dry-run", action="store_true", help="list what would be downloaded")
    parser.add_argument("--jobs", type=int, default=8, help="parallel downloads (default 8)")
    args = parser.parse_args()

    if not IMAGES.is_dir():
        sys.exit(f"assets repo not found at {ASSETS_REPO} (expected {IMAGES})")

    assets = collect()
    todo = [
        asset
        for asset in assets
        if args.force or not (IMAGES / asset.name).exists()
    ]
    print(f"{len(assets)} images total, {len(todo)} to download")

    if args.dry_run:
        for asset in sorted(todo, key=lambda a: a.name):
            print(f"  {asset.name}  <-  {asset.url}")
        return

    failures: list[tuple[str, str]] = []
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = {pool.submit(fetch, asset): asset for asset in todo}
        for done, future in enumerate(as_completed(futures), start=1):
            asset = futures[future]
            try:
                size, source = future.result()
                note = "" if source == asset.url else "  (via Deezer fallback)"
                print(f"  [{done}/{len(todo)}] {asset.name} ({size // 1024} KiB){note}")
            except Exception as error:  # noqa: BLE001 - report and continue
                failures.append((asset.name, str(error)))
                print(f"  [{done}/{len(todo)}] FAILED {asset.name}: {error}", file=sys.stderr)

    if failures:
        print(f"\n{len(failures)} download(s) failed:", file=sys.stderr)
        for name, error in failures:
            print(f"  {name}: {error}", file=sys.stderr)
        sys.exit(1)

    if args.push:
        push()


if __name__ == "__main__":
    main()
