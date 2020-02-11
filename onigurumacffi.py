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

    def group(self, n: int = 0) -> str:
        return self._s_b[self._begs[n]:self._ends[n]].decode()

    def __getitem__(self, n: int) -> str:
        return self.group(n)

    def start(self, n: int = 0) -> int:
        return len(self._s_b[:self._begs[n]].decode())

    def end(self, n: int = 0) -> int:
        return len(self._s_b[:self._ends[n]].decode())

    def expand(self, s: str) -> str:
        return _BACKREF_RE.sub(lambda m: f'{m[1]}{self[int(m[2])]}', s)


def _region_free(region: Any) -> None:
    _lib.onig_region_free(region, 1)


class _Pattern:
    def __init__(self, pattern: str, regex_t: Any) -> None:
        self._pattern = pattern
        self._regex_t = _ffi.gc(regex_t, _lib.onig_free)

    def __repr__(self) -> str:
        return f'{__name__}.compile({self._pattern!r})'

    @staticmethod
    def _params(s: str, start: int) -> Tuple[bytes, int, Any, Any]:
        s_b = s.encode()
        start_b = len(s[:start].encode())
        s_buf = _ffi.new('OnigUChar[]', s_b)
        region = _ffi.gc(_lib.onig_region_new(), _region_free)
        return s_b, start_b, s_buf, region

    @staticmethod
    def _match_ret(ret: int, s_b: bytes, region: Any) -> Optional[_Match]:
        if ret == _lib.ONIG_MISMATCH:
            return None
        else:
            _check(ret)

        begs = tuple(region[0].beg[i] for i in range(region[0].num_regs))
        ends = tuple(region[0].end[i] for i in range(region[0].num_regs))
        return _Match(s_b, begs, ends)

    def match(self, s: str, start: int = 0) -> Optional[_Match]:
        s_b, start_b, s_buf, region = self._params(s, start)

        ret = _lib.onig_match(
            self._regex_t,
            s_buf, s_buf + len(s_b),
            s_buf + start_b,
            region,
            _lib.ONIG_OPTION_NONE,
        )

        return self._match_ret(ret, s_b, region)

    def search(self, s: str, start: int = 0) -> Optional[_Match]:
        s_b, start_b, s_buf, region = self._params(s, start)

        ret = _lib.onig_search(
            self._regex_t,
            s_buf, s_buf + len(s_b),
            s_buf + start_b, s_buf + len(s_b),
            region,
            _lib.ONIG_OPTION_NONE,
        )

        return self._match_ret(ret, s_b, region)


def compile(pattern: str) -> _Pattern:
    pattern_b = pattern.encode()

    regex = _ffi.new('regex_t*[1]')
    pattern_buf = _ffi.new('OnigUChar[]', pattern_b)
    err_info = _ffi.new('OnigErrorInfo[1]')

    ret = _lib.onig_new(
        regex,
        pattern_buf, pattern_buf + len(pattern_b),
        _lib.ONIG_OPTION_NONE,
        _UTF8,
        _SYNTAX,
        err_info,
    )
    _check(ret, err_info)
    return _Pattern(pattern, regex[0])
