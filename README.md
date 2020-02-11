[![Build Status](https://dev.azure.com/asottile/asottile/_apis/build/status/asottile.onigurumacffi?branchName=master)](https://dev.azure.com/asottile/asottile/_build/latest?definitionId=61&branchName=master)
[![Azure DevOps coverage](https://img.shields.io/azure-devops/coverage/asottile/asottile/61/master.svg)](https://dev.azure.com/asottile/asottile/_build/latest?definitionId=61&branchName=master)

onigurumacffi
=============

python cffi bindings for the oniguruma regex engine

### installation

currently this requires `libonig-dev` to be installed prior to installation

```bash
pip install onigurumacffi
```

### api

the api is currently *very limited* (basically just enough to support what I
needed).

#### `compile(pattern: str) -> _Pattern`

make a compiled pattern

#### `_Pattern.match(s: str, start: int = 0) -> Optional[_Match]`

match a string using the pattern.  optionally set `start` to adjust the offset
which is searched from

#### `_Pattern.search(s: str, start: int = 0) -> Optional[_Match]`

search a string using the pattern.  optionally set `start` to adjust the offset
which is searched from

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

#### `_Match.expand(s: str) -> str`

expand numeric groups in `s` via the groups in the match
