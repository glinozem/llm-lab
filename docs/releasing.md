# Releasing

Minimal release process for `llm-lab`.

## Versioning

We use Semantic Versioning: `MAJOR.MINOR.PATCH`.

- `MAJOR`: breaking changes
- `MINOR`: new features (backwards compatible)
- `PATCH`: bug fixes (backwards compatible)

## Before you tag

1. Make sure `master` is green:
   ```bash
   make check
   ```
2. Update `CHANGELOG.md`:
   - move items from `[Unreleased]` to a new version section
   - add release date (YYYY-MM-DD)
   - keep `[Unreleased]` section for next cycle

## Tag and push

Example for `v0.1.1`:

```bash
git checkout master
git pull
git tag -a v0.1.1 -m "v0.1.1"
git push origin v0.1.1
```

## Create GitHub Release

On GitHub:
- Releases → Draft a new release
- Select tag `vX.Y.Z`
- Title: `vX.Y.Z`
- Notes: copy the corresponding section from `CHANGELOG.md`

## Hotfix policy (optional)

For urgent fixes:
- create a branch `hotfix/vX.Y.Z+1`
- PR into `master`
- tag + release
