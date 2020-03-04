import re
from typing import Any
from typing import Optional
from typing import Tuple

import _onigurumacffi

_ffi = _onigurumacffi.ffi
_lib = _onigurumacffi.lib

_BACKREF_RE = re.compile(r'((?<!\\)(?:\\\\)*)\\([0-9]+)')


class OnigError(RuntimeError):
    pass


def _err(code: int, *args: Any) -> str:
    buf = _ffi.new('OnigUChar[ONIG_MAX_ERROR_MESSAGE_LEN]')
    length = _lib.onig_error_code_to_str(buf, code, *args)
    return bytes(buf[0:length]).decode()


def _check(code: int, *args: Any) -> None:
    if code < 0:
        raise OnigError(_err(code, *args))


_check(_lib.onigcffi_initialize())
__onig_version__ = _ffi.string(_lib.onig_version()).decode()


class _Match:
    __slots__ = ('_s_b', '_begs', '_ends')

    def __init__(
        self,
        s_b: bytes,
        begs: Tuple[int, ...],
        ends: Tuple[int, ...],
    ) -> None:
        self._s_b = s_b
        self._begs = begs
        self._ends = ends

    def __repr__(self) -> str:
        return f'<onigurumacffi._Match span={self.span()} match={self[0]!r}>'

    def group(self, n: int = 0) -> str:
        return self._s_b[self._begs[n]:self._ends[n]].decode()

    __getitem__ = group

    def start(self, n: int = 0) -> int:
        return len(self._s_b[:self._begs[n]].decode())

    def end(self, n: int = 0) -> int:
        return len(self._s_b[:self._ends[n]].decode())

    def span(self, n: int = 0) -> Tuple[int, int]:
        return self.start(n), self.end(n)

    def expand(self, s: str) -> str:
        return _BACKREF_RE.sub(lambda m: f'{m[1]}{self[int(m[2])]}', s)

    @property
    def string(self) -> str:
        return self._s_b.decode()


def _start_params(s: str, start: int) -> Tuple[bytes, int]:
    return s.encode(), len(s[:start].encode())


def _region() -> Any:
    return _ffi.gc(_lib.onig_region_new(), _lib.onigcffi_region_free)


def _match_ret(ret: int, s_b: bytes, region: Any) -> Optional[_Match]:
    if ret == _lib.ONIG_MISMATCH:
        return None
    else:
        _check(ret)

    begs = tuple(region[0].beg[0:region[0].num_regs])
    ends = tuple(region[0].end[0:region[0].num_regs])

    return _Match(s_b, begs, ends)


class _Pattern:
    def __init__(self, pattern: str, regex_t: Any) -> None:
        self._pattern = pattern
        self._regex_t = _ffi.gc(regex_t, _lib.onig_free)

    def __repr__(self) -> str:
        return f'{__name__}.compile({self._pattern!r})'

    def number_of_captures(self) -> int:
        return _lib.onig_number_of_captures(self._regex_t)

    def match(self, s: str, start: int = 0) -> Optional[_Match]:
        s_b, start_b = _start_params(s, start)
        region = _region()

        ret = _lib.onigcffi_match(
            self._regex_t, s_b, len(s_b), start_b, region,
        )

        return _match_ret(ret, s_b, region)

    def search(self, s: str, start: int = 0) -> Optional[_Match]:
        s_b, start_b = _start_params(s, start)
        region = _region()

        ret = _lib.onigcffi_search(
            self._regex_t, s_b, len(s_b), start_b, region,
        )

        return _match_ret(ret, s_b, region)


class _RegSet:
    def __init__(self, patterns: Tuple[str, ...], regset_t: Any) -> None:
        self._patterns = patterns
        self._regset_t = _ffi.gc(regset_t, _lib.onig_regset_free)

    def __repr__(self) -> str:
        patterns = ', '.join(repr(pattern) for pattern in self._patterns)
        return f'{__name__}.compile_regset({patterns})'

    def search(self, s: str, start: int = 0) -> Tuple[int, Optional[_Match]]:
        s_b, start_b = _start_params(s, start)
        region = _ffi.new('OnigRegion*[1]')

        idx = _lib.onigcffi_regset_search(
            self._regset_t, s_b, len(s_b), start_b, region,
        )
        return idx, _match_ret(idx, s_b, region[0])


def _compile_regex_t(pattern: str, dest: Any) -> None:
    pattern_b = pattern.encode()

    err_info = _ffi.new('OnigErrorInfo[1]')
    ret = _lib.onigcffi_new(dest, pattern_b, len(pattern_b), err_info)
    _check(ret, err_info)


def compile(pattern: str) -> _Pattern:
    regex = _ffi.new('regex_t*[1]')
    _compile_regex_t(pattern, regex)
    return _Pattern(pattern, regex[0])


def compile_regset(*patterns: str) -> _RegSet:
    regexes = _ffi.new('regex_t*[]', len(patterns))
    for i, pattern in enumerate(patterns):
        _compile_regex_t(pattern, regexes + i)

    regset = _ffi.new('OnigRegSet*[1]')
    _check(_lib.onig_regset_new(regset, len(patterns), regexes))
    return _RegSet(patterns, regset[0])
