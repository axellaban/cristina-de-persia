#!/bin/sh
# Compila Cristina of Persia para el navegador (WebAssembly) con Emscripten.
# Resultado en web/: index.html + prince.js + prince.wasm + prince.data
# Uso: sh webbuild/build.sh   (hace falta emcc: brew install emscripten)
set -e
cd "$(dirname "$0")/.."

# sólo los archivos que el juego necesita
STAGE=webbuild/.stage
rm -rf "$STAGE"
mkdir -p "$STAGE/mods/CristinaOfPersia"
cp -R data "$STAGE/data"
cp -R mods/CristinaOfPersia/data "$STAGE/mods/CristinaOfPersia/data"
if [ -d mods/CristinaOfPersia/music ]; then
	mkdir -p "$STAGE/mods/CristinaOfPersia/music"
	cp mods/CristinaOfPersia/music/*.ogg "$STAGE/mods/CristinaOfPersia/music/" 2>/dev/null || true
fi
cp webbuild/SDLPoP.ini "$STAGE/SDLPoP.ini"

mkdir -p web
emcc -O2 \
	src/main.c src/data.c src/seg000.c src/seg001.c src/seg002.c src/seg003.c \
	src/seg004.c src/seg005.c src/seg006.c src/seg007.c src/seg008.c src/seg009.c \
	src/seqtbl.c src/replay.c src/options.c src/lighting.c src/screenshot.c \
	src/menu.c src/midi.c src/opl3.c src/stb_vorbis.c \
	-sUSE_SDL=2 -sUSE_SDL_IMAGE=2 -sSDL2_IMAGE_FORMATS='["png"]' \
	-sASYNCIFY -sASYNCIFY_STACK_SIZE=65536 \
	-sALLOW_MEMORY_GROWTH=1 -sINITIAL_MEMORY=67108864 \
	-sENVIRONMENT=web -sEXIT_RUNTIME=0 \
	-sEXPORTED_RUNTIME_METHODS='["callMain"]' \
	--preload-file "$STAGE@/" \
	-o web/prince.js

cp webbuild/index.html web/index.html
cp webbuild/manifest.json web/manifest.json
cp mods/CristinaOfPersia/promo.png web/promo.png
cp data/icon.png web/icon.png
cp webbuild/icon-192.png webbuild/icon-512.png webbuild/apple-touch-icon.png web/
rm -rf "$STAGE"
ls -la web
