# macOS `uchg` Immutable Flag on config.yaml

## Symptom

`hermes config set` fails with `PermissionError: [Errno 1] Operation not permitted`.
Even `sed -i ''` fails with `rename(): Operation not permitted`.

## Root cause

Hermes `config.yaml` has the macOS user-immutable flag (`uchg`) set:

```
$ ls -laO ~/.hermes/config.yaml
-rw-------  1 user  staff  uchg 15157 ... config.yaml
```

The `uchg` flag prevents any modification (including rename/replace) of the file. `hermes config set` uses atomic file replacement (`os.replace`), which is blocked by this flag.

## Fix

```bash
chflags nouchg ~/.hermes/config.yaml
```

After removing the flag, editing works normally. Optionally re-set it:

```bash
chflags uchg ~/.hermes/config.yaml
```

## Detection

```bash
ls -laO ~/.hermes/config.yaml
# Look for "uchg" in the flags column
```

## Notes

- macOS-specific. Linux and Windows don't have this flag.
- The flag appears to be set by Hermes during initialization — possibly as a safety measure.
- `hermes config set` replaces the file atomically via temp-file → rename, which `uchg` blocks even though the file contents are writable by normal means.
