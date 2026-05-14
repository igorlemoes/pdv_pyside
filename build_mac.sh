#!/bin/bash
set -e

echo "==> Limpando build anterior..."
rm -rf dist build

echo "==> Gerando bundle com PyInstaller..."
.venv/bin/pyinstaller pdv.spec --noconfirm

APP="dist/PDV.app"

echo "==> Re-assinando dylibs (remove hardened runtime incompatível)..."
find "$APP" \( -name "*.dylib" -o -name "*.so" \) | while read f; do
    codesign --force --sign - --timestamp=none "$f"
done

echo "==> Re-assinando executável principal..."
codesign --force --sign - --timestamp=none \
    --entitlements entitlements.plist \
    "$APP/Contents/MacOS/PDV"

echo "==> Re-assinando bundle completo..."
codesign --force --sign - --timestamp=none \
    --entitlements entitlements.plist \
    "$APP"

echo "==> Removendo quarentena..."
xattr -cr "$APP"

echo ""
echo "Pronto! Abrindo o app para testar..."
open "$APP"
