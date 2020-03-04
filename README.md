[![Build Status](https://dev.azure.com/asottile/asottile/_apis/build/status/asottile.onigurumacffi?branchName=master)](https://dev.azure.com/asottile/asottile/_build/latest?definitionId=61&branchName=master)
[![Azure DevOps coverage](https://img.shields.io/azure-devops/coverage/asottile/asottile/61/master.svg)](https://dev.azure.com/asottile/asottile/_build/latest?definitionId=61&branchName=master)

onigurumacffi
=============

python cffi bindings for the oniguruma regex engine

### installation

```bash
pip install onigurumacffi
```

- manylinux wheels should be available on pypi in most cases
- to build from source, `libonig-dev` must be installed prior to installation

### api

the api is currently *very limited* (basically just enough to support what I
needed).

#### `compile(pattern: str) -> _Pattern`

make a compiled pattern

#### `compile_regset(*patterns: str) -> _RegSet`

make a compiled RegSet

#### `_Pattern.match(s: str, start: int = 0) -> Optional[_Match]`

match a string using the pattern.  optionally set `start` to adjust the offset
which is searched from

#### `_Pattern.search(s: str, start: int = 0) -> Optional[_Match]`

search a string using the pattern.  optionally set `start` to adjust the offset
which is searched from

#### `_Pattern.number_of_captures() -> int`

return the number of captures in the regex

#### `_RegSet.search(s: str, start: int = 0) -> Tuple[int, Optional[_Match]]`

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
