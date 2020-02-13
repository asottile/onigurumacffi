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


_UTF8 = _ffi.addressof(_lib.OnigEncodingUTF8)
_SYNTAX = _ffi.addressof(_lib.OnigSyntaxOniguruma)
_check(_lib.onig_initialize([_UTF8], 1))
__onig_version__ = _ffi.string(_lib.onig_version()).decode()


class _Match:
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

    def __getitem__(self, n: int) -> str:
        return self.group(n)

    def start(self, n: int = 0) -> int:
        return len(self._s_b[:self._begs[n]].decode())

    def end(self, n: int = 0) -> int:
        return len(self._s_b[:self._ends[n]].decode())

    def span(self, n: int = 0) -> Tuple[int, int]:
        return self.start(n), self.end(n)

    def expand(self, s: str) -> str:
        return _BACKREF_RE.sub(lambda m: f'{m[1]}{self[int(m[2])]}', s)


def _region_free(region: Any) -> None:
    _lib.onig_region_free(region, 1)


def _start_params(s: str, start: int) -> Tuple[bytes, int, Any]:
    s_b = s.encode()
    start_b = len(s[:start].encode())
    s_buf = _ffi.new('OnigUChar[]', s_b)
    return s_b, start_b, s_buf


def _region() -> Any:
    return _ffi.gc(_lib.onig_region_new(), _region_free)


def _match_ret(ret: int, s_b: bytes, region: Any) -> Optional[_Match]:
    if ret == _lib.ONIG_MISMATCH:
        return None
    else:
        _check(ret)

    begs = tuple(region[0].beg[i] for i in range(region[0].num_regs))
    ends = tuple(region[0].end[i] for i in range(region[0].num_regs))

    return _Match(s_b, begs, ends)


class _Pattern:
    def __init__(self, pattern: str, regex_t: Any) -> None:
        self._pattern = pattern
        self._regex_t = _ffi.gc(regex_t, _lib.onig_free)

    def __repr__(self) -> str:
        return f'{__name__}.compile({self._pattern!r})'

    def match(self, s: str, start: int = 0) -> Optional[_Match]:
        s_b, start_b, s_buf = _start_params(s, start)
        region = _region()

        ret = _lib.onig_match(
            self._regex_t,
            s_buf, s_buf + len(s_b),
            s_buf + start_b,
            region,
            _lib.ONIG_OPTION_NONE,
        )

        return _match_ret(ret, s_b, region)

    def search(self, s: str, start: int = 0) -> Optional[_Match]:
        s_b, start_b, s_buf = _start_params(s, start)
        region = _region()

        ret = _lib.onig_search(
            self._regex_t,
            s_buf, s_buf + len(s_b),
            s_buf + start_b, s_buf + len(s_b),
            region,
            _lib.ONIG_OPTION_NONE,
        )

        return _match_ret(ret, s_b, region)


class _RegSet:
    def __init__(
            self,
            patterns: Tuple[str, ...],
            regset_t: Any,
            regexes: Any,
    ) -> None:
        self._patterns = patterns
        self._regset_t = _ffi.gc(regset_t, _lib.onig_regset_free)
        self._regexes = regexes

    def __repr__(self) -> str:
        patterns = ', '.join(repr(pattern) for pattern in self._patterns)
        return f'{__name__}.compile_regset({patterns})'

    def search(self, s: str, start: int = 0) -> Tuple[int, Optional[_Match]]:
        s_b, start_b, s_buf = _start_params(s, start)
        pos = _ffi.new('int[1]')

        idx = _lib.onig_regset_search(
            self._regset_t,
            s_buf, s_buf + len(s_b),
            s_buf + start_b, s_buf + len(s_b),
            _lib.ONIG_REGSET_POSITION_LEAD,
            _lib.ONIG_OPTION_NONE,
            pos,
        )
        if idx == _lib.ONIG_MISMATCH:
            return idx, None
        else:
            _check(idx)

        region = _region()
        ret = _lib.onig_search(
            self._regexes[idx],
            s_buf, s_buf + len(s_b),
            s_buf + pos[0], s_buf + len(s_b),
            region,
            _lib.ONIG_OPTION_NONE,
        )
        return idx, _match_ret(ret, s_b, region)


def _compile_regex_t(pattern: str, dest: Any) -> None:
    pattern_b = pattern.encode()

    pattern_buf = _ffi.new('OnigUChar[]', pattern_b)
    err_info = _ffi.new('OnigErrorInfo[1]')

    ret = _lib.onig_new(
        dest,
        pattern_buf, pattern_buf + len(pattern_b),
        _lib.ONIG_OPTION_NONE,
        _UTF8,
        _SYNTAX,
        err_info,
    )
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
    ret = _lib.onig_regset_new(regset, len(patterns), regexes)
    _check(ret)
    return _RegSet(patterns, regset[0], regexes)
