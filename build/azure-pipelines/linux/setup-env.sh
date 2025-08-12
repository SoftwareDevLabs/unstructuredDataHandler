#!/usr/bin/env bash

set -e

SYSROOT_ARCH=$SDLC_CORE_ARCH
if [ "$SYSROOT_ARCH" == "x64" ]; then
  SYSROOT_ARCH="amd64"
fi

export SDLC_CORE_CLIENT_SYSROOT_DIR=$PWD/.build/sysroots/glibc-2.28-gcc-10.5.0
export SDLC_CORE_REMOTE_SYSROOT_DIR=$PWD/.build/sysroots/glibc-2.28-gcc-8.5.0
if [ -d "$SDLC_CORE_CLIENT_SYSROOT_DIR" ]; then
  echo "Using cached client sysroot"
else
  echo "Downloading client sysroot"
  SYSROOT_ARCH="$SYSROOT_ARCH" SDLC_CORE_SYSROOT_DIR="$SDLC_CORE_CLIENT_SYSROOT_DIR" node -e '(async () => { const { getSDLCcoreSysroot } = require("./build/linux/debian/install-sysroot.js"); await getSDLCcoreSysroot(process.env["SYSROOT_ARCH"]); })()'
fi

if [ -d "$SDLC_CORE_REMOTE_SYSROOT_DIR" ]; then
  echo "Using cached remote sysroot"
else
  echo "Downloading remote sysroot"
  SYSROOT_ARCH="$SYSROOT_ARCH" SDLC_CORE_SYSROOT_DIR="$SDLC_CORE_REMOTE_SYSROOT_DIR" SDLC_CORE_SYSROOT_PREFIX="-glibc-2.28-gcc-8.5.0" node -e '(async () => { const { getSDLCcoreSysroot } = require("./build/linux/debian/install-sysroot.js"); await getSDLCcoreSysroot(process.env["SYSROOT_ARCH"]); })()'
fi

if [ "$npm_config_arch" == "x64" ]; then
  # Download clang based on chromium revision used by vscode
  curl -s https://raw.githubusercontent.com/chromium/chromium/138.0.7204.100/tools/clang/scripts/update.py | python - --output-dir=$PWD/.build/CR_Clang --host-os=linux

  # Download libcxx headers and objects from upstream electron releases
  DEBUG=libcxx-fetcher \
  SDLC_CORE_LIBCXX_OBJECTS_DIR=$PWD/.build/libcxx-objects \
  SDLC_CORE_LIBCXX_HEADERS_DIR=$PWD/.build/libcxx_headers  \
  SDLC_CORE_LIBCXXABI_HEADERS_DIR=$PWD/.build/libcxxabi_headers \
  SDLC_CORE_ARCH="$npm_config_arch" \
  node build/linux/libcxx-fetcher.js

  # Set compiler toolchain
  export CC="$PWD/.build/CR_Clang/bin/clang --gcc-toolchain=$SDLC_CORE_CLIENT_SYSROOT_DIR/x86_64-linux-gnu"
  export CXX="$PWD/.build/CR_Clang/bin/clang++ --gcc-toolchain=$SDLC_CORE_CLIENT_SYSROOT_DIR/x86_64-linux-gnu"
  export CXXFLAGS="-nostdinc++ -D__NO_INLINE__ -DSPDLOG_USE_STD_FORMAT -I$PWD/.build/libcxx_headers -isystem$PWD/.build/libcxx_headers/include -isystem$PWD/.build/libcxxabi_headers/include -fPIC -flto=thin -fsplit-lto-unit -D_LIBCPP_ABI_NAMESPACE=Cr -D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_EXTENSIVE --sysroot=$SDLC_CORE_CLIENT_SYSROOT_DIR/x86_64-linux-gnu/x86_64-linux-gnu/sysroot"
  export LDFLAGS="-stdlib=libc++ --sysroot=$SDLC_CORE_CLIENT_SYSROOT_DIR/x86_64-linux-gnu/x86_64-linux-gnu/sysroot -fuse-ld=lld -flto=thin -L$PWD/.build/libcxx-objects -lc++abi -L$SDLC_CORE_CLIENT_SYSROOT_DIR/x86_64-linux-gnu/x86_64-linux-gnu/sysroot/usr/lib/x86_64-linux-gnu -L$SDLC_CORE_CLIENT_SYSROOT_DIR/x86_64-linux-gnu/x86_64-linux-gnu/sysroot/lib/x86_64-linux-gnu -Wl,--lto-O0"

  # Set compiler toolchain for remote server
  export SDLC_CORE_REMOTE_CC=$SDLC_CORE_REMOTE_SYSROOT_DIR/x86_64-linux-gnu/bin/x86_64-linux-gnu-gcc
  export SDLC_CORE_REMOTE_CXX=$SDLC_CORE_REMOTE_SYSROOT_DIR/x86_64-linux-gnu/bin/x86_64-linux-gnu-g++
  export SDLC_CORE_REMOTE_CXXFLAGS="--sysroot=$SDLC_CORE_REMOTE_SYSROOT_DIR/x86_64-linux-gnu/x86_64-linux-gnu/sysroot"
  export SDLC_CORE_REMOTE_LDFLAGS="--sysroot=$SDLC_CORE_REMOTE_SYSROOT_DIR/x86_64-linux-gnu/x86_64-linux-gnu/sysroot -L$SDLC_CORE_REMOTE_SYSROOT_DIR/x86_64-linux-gnu/x86_64-linux-gnu/sysroot/usr/lib/x86_64-linux-gnu -L$SDLC_CORE_REMOTE_SYSROOT_DIR/x86_64-linux-gnu/x86_64-linux-gnu/sysroot/lib/x86_64-linux-gnu"
elif [ "$npm_config_arch" == "arm64" ]; then
  # Set compiler toolchain for client native modules
  export CC=$VSCODE_CLIENT_SYSROOT_DIR/aarch64-linux-gnu/bin/aarch64-linux-gnu-gcc
  export CXX=$VSCODE_CLIENT_SYSROOT_DIR/aarch64-linux-gnu/bin/aarch64-linux-gnu-g++
  export CXXFLAGS="--sysroot=$VSCODE_CLIENT_SYSROOT_DIR/aarch64-linux-gnu/aarch64-linux-gnu/sysroot"
  export LDFLAGS="--sysroot=$VSCODE_CLIENT_SYSROOT_DIR/aarch64-linux-gnu/aarch64-linux-gnu/sysroot -L$VSCODE_CLIENT_SYSROOT_DIR/aarch64-linux-gnu/aarch64-linux-gnu/sysroot/usr/lib/aarch64-linux-gnu -L$VSCODE_CLIENT_SYSROOT_DIR/aarch64-linux-gnu/aarch64-linux-gnu/sysroot/lib/aarch64-linux-gnu"

  # Set compiler toolchain for remote server
  export VSCODE_REMOTE_CC=$VSCODE_REMOTE_SYSROOT_DIR/aarch64-linux-gnu/bin/aarch64-linux-gnu-gcc
  export VSCODE_REMOTE_CXX=$VSCODE_REMOTE_SYSROOT_DIR/aarch64-linux-gnu/bin/aarch64-linux-gnu-g++
  export VSCODE_REMOTE_CXXFLAGS="--sysroot=$VSCODE_REMOTE_SYSROOT_DIR/aarch64-linux-gnu/aarch64-linux-gnu/sysroot"
  export VSCODE_REMOTE_LDFLAGS="--sysroot=$VSCODE_REMOTE_SYSROOT_DIR/aarch64-linux-gnu/aarch64-linux-gnu/sysroot -L$VSCODE_REMOTE_SYSROOT_DIR/aarch64-linux-gnu/aarch64-linux-gnu/sysroot/usr/lib/aarch64-linux-gnu -L$VSCODE_REMOTE_SYSROOT_DIR/aarch64-linux-gnu/aarch64-linux-gnu/sysroot/lib/aarch64-linux-gnu"
elif [ "$npm_config_arch" == "arm" ]; then
  # Set compiler toolchain for client native modules
  export CC=$VSCODE_CLIENT_SYSROOT_DIR/arm-rpi-linux-gnueabihf/bin/arm-rpi-linux-gnueabihf-gcc
  export CXX=$VSCODE_CLIENT_SYSROOT_DIR/arm-rpi-linux-gnueabihf/bin/arm-rpi-linux-gnueabihf-g++
  export CXXFLAGS="--sysroot=$VSCODE_CLIENT_SYSROOT_DIR/arm-rpi-linux-gnueabihf/arm-rpi-linux-gnueabihf/sysroot"
  export LDFLAGS="--sysroot=$VSCODE_CLIENT_SYSROOT_DIR/arm-rpi-linux-gnueabihf/arm-rpi-linux-gnueabihf/sysroot -L$VSCODE_CLIENT_SYSROOT_DIR/arm-rpi-linux-gnueabihf/arm-rpi-linux-gnueabihf/sysroot/usr/lib/arm-linux-gnueabihf -L$VSCODE_CLIENT_SYSROOT_DIR/arm-rpi-linux-gnueabihf/arm-rpi-linux-gnueabihf/sysroot/lib/arm-linux-gnueabihf"

  # Set compiler toolchain for remote server
  export VSCODE_REMOTE_CC=$VSCODE_REMOTE_SYSROOT_DIR/arm-rpi-linux-gnueabihf/bin/arm-rpi-linux-gnueabihf-gcc
  export VSCODE_REMOTE_CXX=$VSCODE_REMOTE_SYSROOT_DIR/arm-rpi-linux-gnueabihf/bin/arm-rpi-linux-gnueabihf-g++
  export VSCODE_REMOTE_CXXFLAGS="--sysroot=$VSCODE_REMOTE_SYSROOT_DIR/arm-rpi-linux-gnueabihf/arm-rpi-linux-gnueabihf/sysroot"
  export VSCODE_REMOTE_LDFLAGS="--sysroot=$VSCODE_REMOTE_SYSROOT_DIR/arm-rpi-linux-gnueabihf/arm-rpi-linux-gnueabihf/sysroot -L$VSCODE_REMOTE_SYSROOT_DIR/arm-rpi-linux-gnueabihf/arm-rpi-linux-gnueabihf/sysroot/usr/lib/arm-linux-gnueabihf -L$VSCODE_REMOTE_SYSROOT_DIR/arm-rpi-linux-gnueabihf/arm-rpi-linux-gnueabihf/sysroot/lib/arm-linux-gnueabihf"
fi
