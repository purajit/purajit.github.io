.PHONY: clean

ROOT_DIR=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

get-yass:
	curl https://raw.githubusercontent.com/purajit/YASS/main/generate_site.py > generate_site.py

symlink-assets:
	rm -f $(ROOT_DIR)/docs/static/assets
	ln -s ../../assets $(ROOT_DIR)/docs/static/assets

run-server: symlink-assets
	colima status > /dev/null 2>&1 || DYLD_LIBRARY_PATH=/System/Library/Frameworks/ImageIO.framework/Versions/A/Resources/ colima start
	@echo $(ROOT_DIR)
	docker stop purajit.com || true
	docker run  -it --rm -d -p 80:80 --name purajit.com -v $(ROOT_DIR)/docs:/usr/share/nginx/html -v $(realpath ../assets.purajit.github.io/docs/):/usr/share/nginx/assets nginx:1.22-alpine

enter-server:
	docker exec -w /usr/share/nginx/html -it purajit.com sh

generate-pages-local: get-yass
	./generate_site.py yass_config_local.json

clean:
	git clean -fd
