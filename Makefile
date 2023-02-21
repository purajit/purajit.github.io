.PHONY: clean

ROOT_DIR=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

run-server:
	colima status > /dev/null 2>&1 || DYLD_LIBRARY_PATH=/System/Library/Frameworks/ImageIO.framework/Versions/A/Resources/ colima start
	@echo $(ROOT_DIR)
	docker stop purajit.com || true
	docker run  -it --rm -d -p 80:80 --name purajit.com -v $(ROOT_DIR)/docs:/usr/share/nginx/html nginx:1.22-alpine

enter-server:
	docker exec -w /usr/share/nginx/html -it purajit.com sh

generate-pages:
	./generators/generate

clean:
	git clean -fd
