[![build status](https://github.com/asottile/onigurumacffi/actions/workflows/main.yml/badge.svg)](https://github.com/asottile/onigurumacffi/actions/workflows/main.yml)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/asottile/onigurumacffi/main.svg)](https://results.pre-commit.ci/latest/github/asottile/onigurumacffi/main)

onigurumacffi
=============

python cffi bindings for the oniguruma regex engine

### installation

```bash
pip install onigurumacffi
```

- wheels should be available on pypi in most cases
- to build from source, `libonig-dev` must be installed prior to installation

### api

the api is currently *very limited* (basically just enough to support what I
needed).

#### `compile(pattern: str) -> _Pattern`

make a compiled pattern

#### `compile_regset(*patterns: str) -> _RegSet`

make a compiled RegSet

#### `OnigSearchOption`

an enum listing the search-time options for oniguruma

the current set of options are:

```python
class OnigSearchOption(enum.IntEnum):
    NONE = ...
    NOTBOL = ...
    NOTEOL = ...
    POSIX_REGION = ...
    CHECK_VALIDITY_OF_STRING = ...
    NOT_BEGIN_STRING = ...
    NOT_BEGIN_POSITION = ...
```

#### `_Pattern.match(s: str, start: int = 0, flags: OnigSearchOption = OnigSearchOption.NONE) -> Optional[_Match]`

match a string using the pattern.  optionally set `start` to adjust the offset
which is searched from

#### `_Pattern.search(s: str, start: int = 0, flags: OnigSearchOption = OnigSearchOption.NONE) -> Optional[_Match]`

search a string using the pattern.  optionally set `start` to adjust the offset
which is searched from

#### `_Pattern.number_of_captures() -> int`

return the number of captures in the regex

#### `_RegSet.search(s: str, start: int = 0, flags: OnigSearchOption = OnigSearchOption.NONE) -> Tuple[int, Optional[_Match]]`

search a string using the RegSet.  optionally set `start` to adjust the offset
which is searched from

the leftmost regex index and match is returned or `(-1, None)` if there is no
match

#### `_Match.group(n: int = 0) -> str`

return the string of the matched group, defaults to 0 (the whole match)

#### `_Match[n: int] -> str`

a shorthand alias for `_Match.group(...)`

#### `_Match.start(n: int = 0) -> int`

return the character position of the start of the matched group, defaults to 0
(the whole match)

#### `_Match.end(n: int = 0) -> int`

return the character position of the end of the matched group, defaults to 0
(the whole match)

#### `_Match.span(n: int = 0) -> int`

return `(start, end)` character position of the matched group, defaults to 0
(the whole match)

#### `_Match.expand(s: str) -> str`

expand numeric groups in `s` via the groups in the match
