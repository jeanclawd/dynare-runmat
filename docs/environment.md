# Environment notes

## RunMat install

RunMat 0.6.2, prebuilt Linux x86_64 binary from
`runmat-org/runmat` releases. Building from source is possible but
`cargo install runmat` compiles the full workspace including Cranelift, which is
impractical on a small box.

```bash
gh release download v0.6.2 --repo runmat-org/runmat \
  --pattern "*linux-x86_64.tar.gz"
tar xzf runmat-v0.6.2-linux-x86_64.tar.gz
```

## The HDF5 problem

The prebuilt binary is linked against HDF5 1.10:

```
$ ldd runmat | grep "not found"
    libhdf5_serial.so.103 => not found
```

Ubuntu 24.04+ ships HDF5 1.14 (`libhdf5_serial.so.310`). The sonames are not
compatible, so symlinking `.so.310` to `.so.103` is not safe — the ABI differs.

The fix used here keeps the old runtime in a private directory so the system
HDF5 is untouched:

```bash
curl -O https://archive.ubuntu.com/ubuntu/pool/universe/h/hdf5/\
libhdf5-103-1_1.10.7+repack-4ubuntu2_amd64.deb
dpkg-deb -x libhdf5-103-1_*.deb ex
mkdir -p ~/.local/lib/runmat-compat
cp -P ex/usr/lib/x86_64-linux-gnu/libhdf5_serial.so.103* ~/.local/lib/runmat-compat/
```

Then a wrapper on `PATH` sets `LD_LIBRARY_PATH` for RunMat only:

```sh
#!/bin/sh
LD_LIBRARY_PATH="$HOME/.local/lib/runmat-compat${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export LD_LIBRARY_PATH
exec "$HOME/.local/bin/runmat.real" "$@"
```

## Headless noise

On a machine with no display, RunMat's plotting backend probes for a GPU and
writes warnings to stderr:

```
WARN wgpu_hal::gles::egl] No windowing system present. Using surfaceless platform
libEGL warning: egl: failed to create dri2 screen
```

These are harmless but pollute captured output, so both harnesses filter them.
`--plot-headless` / `--plot-mode headless` reduce but do not eliminate them.

## Dynare source

The canonical remote is GitLab:

```bash
git clone --depth 1 https://git.dynare.org/Dynare/dynare.git
```

`github.com/DynareTeam/dynare` no longer exists — it returns "Repository not
found". Anything pointing there is stale.

Version measured: **8-unstable**, commit `0fad4db`, 1056 `.m` files under
`matlab/`.
