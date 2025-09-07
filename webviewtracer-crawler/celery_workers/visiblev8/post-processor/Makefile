PHONY: rust-build go-build fetch-easy-privacy preprocess_android_buckets frida-build#build_entity_hashmap

docker:
	./build/docker.sh

preprocess_android_buckets:
	./build/preprocess_android_buckets.py ./android_apis_buckets.json ./artifacts/android_api_buckets.json

rust-build:
	mkdir -p ./artifacts
	rustup default stable
	cd ./adblock/adblock-oracle-rs && cargo build --release
	cp ./adblock/adblock-oracle-rs/target/release/adblock-oracle-rs ./artifacts/adblock
	cp exfil_apis ./artifacts/exfil_apis
#	cp ./android_apis_buckets.json ./artifacts/android_api_buckets.json

go-build:
	mkdir -p ./artifacts
	go build -o ./artifacts/vv8-post-processor -buildvcs=false .

frida-build:
	mkdir -p ./artifacts
	go build -o ./artifacts/frida-post-processor -buildvcs=false ./webview/frida

publish:
	./build/publish.sh

fetch-easy-privacy:
	./build/fetch_easy_privacy.sh

build_entity_hashmap:
	./build/entity_hashmap.sh

clean:
	rm -rf ./artifacts
	rm -rf ./adblock/adblock-oracle-rs/target
	rm -rf ./vv8-postprocessor