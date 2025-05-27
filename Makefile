.PHONY: clean

symlink-assets:
	rm -f ./docs/static/assets
	ln -s ../../assets ./docs/static/assets

run-server: symlink-assets
	colima status > /dev/null 2>&1 || DYLD_LIBRARY_PATH=/System/Library/Frameworks/ImageIO.framework/Versions/A/Resources/ colima start
	docker stop purajit.com || true
	docker run  -it --rm -d -p 80:80 --name purajit.com -v ./docs:/usr/share/nginx/html -v $(realpath ../assets.purajit.github.io/docs/):/usr/share/nginx/assets nginx:1.22-alpine

stop-server:
	docker stop purajit.com

enter-server:
	docker exec -w /usr/share/nginx/html -it purajit.com sh

generate-pages-local:
	uv run https://raw.githubusercontent.com/purajit/YASS/refs/heads/main/generate_site.py yass_config_local.json

# only used in local testing, but with "CDN" paths instead of local ones
generate-pages-cdn:
	uv run https://raw.githubusercontent.com/purajit/YASS/refs/heads/main/generate_site.py yass_config_prod.json
