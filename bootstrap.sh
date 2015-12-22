#!/bin/sh
set -e

echo "Updating Git submodules..."
git submodule init
git submodule update

echo "Compiling protocol buffers..."
protoc -I=hs-proto --python_out=. hs-proto/*/*.proto

echo "Done."
