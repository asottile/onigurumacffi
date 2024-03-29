from __future__ import annotations

import pytest

import onigurumacffi

FOO_RE = onigurumacffi.compile('^foo')
ABC_RE = onigurumacffi.compile('(a+)B+(c+)')
UNICODE_RE = onigurumacffi.compile('.*?(🙃+)')
REGSET = onigurumacffi.compile_regset('a+', 'b+', 'c+')


def test_regex_compiles():
    assert FOO_RE is not None


def test_regex_repr():
    assert repr(FOO_RE) == "onigurumacffi.compile('^foo')"


def test_regex_compile_failure():
    with pytest.raises(onigurumacffi.OnigError):
        onigurumacffi.compile('(')


def test_regex_number_of_captures():
    assert FOO_RE.number_of_captures() == 0
    assert ABC_RE.number_of_captures() == 2
    assert UNICODE_RE.number_of_captures() == 1


def test_match_failure():
    assert FOO_RE.match('bar') is None


def test_match_success():
    assert FOO_RE.match('food') is not None


def test_match_repr():
    match = FOO_RE.match('food')
    assert match is not None
    assert repr(match) == "<onigurumacffi._Match span=(0, 3) match='foo'>"


def test_match_groups():
    match = ABC_RE.match('aaaaaBBBBBcccDDD')
    assert match is not None
    assert match[0] == 'aaaaaBBBBBccc'
    assert match.group(0) == 'aaaaaBBBBBccc'
    assert match[1] == 'aaaaa'
    assert match.group(1) == 'aaaaa'
    assert match[2] == 'ccc'
    assert match.group(2) == 'ccc'
    with pytest.raises(IndexError):
        match[3]


def test_match_starts_ends_spans():
    match = ABC_RE.match('aaaBBBcccddd')
    assert match is not None
    assert match.start() == 0
    assert match.end() == 9
    assert match.span() == (0, 9)
    assert match.start(1) == 0
    assert match.end(1) == 3
    assert match.span(1) == (0, 3)
    assert match.start(2) == 6
    assert match.end(2) == 9
    assert match.span(2) == (6, 9)


def test_match_start():
    match = ABC_RE.match('aaaBBBcccddd', start=1)
    assert match is not None
    assert match.start() == 1
    assert match.end() == 9
    assert match[1] == 'aa'


def test_unicode_match():
    match = UNICODE_RE.match('ohai☃🙃🙃🙃wat')
    assert match is not None
    assert match[0] == 'ohai☃🙃🙃🙃'
    assert match[1] == '🙃🙃🙃'
    assert match.start() == 0
    assert match.end() == 8


def test_unicode_match_start():
    match = UNICODE_RE.match('☃☃☃🙃🙃🙃', start=1)
    assert match is not None
    assert match[0] == '☃☃🙃🙃🙃'


def test_re_compile_unicode_escape():
    pattern = onigurumacffi.compile(r'"\u2603++"')
    assert pattern.match('"☃☃☃☃"')


def test_search():
    match = ABC_RE.search('zzzaaaBccczzz')
    assert match is not None
    assert match.group() == 'aaaBccc'
    assert match.start() == 3


def test_search_start():
    match = ABC_RE.search('zzzaaaBccczzz', start=4)
    assert match is not None
    assert match.group() == 'aaBccc'
    assert match.start() == 4


def test_search_no_match():
    match = ABC_RE.search('zzz')
    assert match is None


def test_search_with_flags():
    reg_A = onigurumacffi.compile(r'\Afoo')
    assert reg_A.search('foo')
    assert not reg_A.search(
        'foo',
        flags=onigurumacffi.OnigSearchOption.NOT_BEGIN_STRING,
    )

    reg_G = onigurumacffi.compile(r'\Gfoo')
    assert reg_G.search('afoo', start=1)
    assert not reg_G.search(
        'afoo',
        start=1,
        flags=onigurumacffi.OnigSearchOption.NOT_BEGIN_POSITION,
    )

    reg_z = onigurumacffi.compile(r'foo\z')
    assert reg_z.search('hello foo')
    assert not reg_z.search(
        'hello foo',
        flags=onigurumacffi.OnigSearchOption.NOT_END_STRING,
    )


def test_match_expand():
    match = ABC_RE.match('aaaBccccddd')
    assert match is not None
    assert match.expand(r'foo\1\1\1') == 'fooaaaaaaaaa'
    assert match.expand(r'foo\2\1') == 'fooccccaaa'


def test_match_string():
    match = FOO_RE.match('food')
    assert match is not None
    assert match.string == 'food'


def test_match_with_flags():
    reg_A = onigurumacffi.compile(r'\Afoo')
    assert reg_A.match('foo')
    assert not reg_A.match(
        'foo',
        flags=onigurumacffi.OnigSearchOption.NOT_BEGIN_STRING,
    )

    reg_G = onigurumacffi.compile(r'\Gfoo')
    assert reg_G.match('foo')
    assert not reg_G.match(
        'foo',
        flags=onigurumacffi.OnigSearchOption.NOT_BEGIN_POSITION,
    )

    reg_not_G = onigurumacffi.compile(r'(?!\G)')
    assert not reg_not_G.match('foo')
    assert reg_not_G.match(
        'foo', flags=onigurumacffi.OnigSearchOption.NOT_BEGIN_POSITION,
    )


def test_regset_repr():
    ret = repr(onigurumacffi.compile_regset('abc', 'def'))
    assert ret == "onigurumacffi.compile_regset('abc', 'def')"


def test_regset_search_not_matching():
    idx, match = REGSET.search('zzzq')
    assert idx == -1
    assert match is None


def test_regset_search_matches_first_match():
    idx, match = REGSET.search('zzzabc')
    assert idx == 0
    assert match is not None
    assert match.group() == 'a'


def test_regset_returns_first_regex_when_equal():
    regset = onigurumacffi.compile_regset('a', '[^z]')
    idx, match = regset.search('zzza')
    assert idx == 0
    assert match is not None
    assert match.group() == 'a'


def test_regset_empty_match_at_end_of_string():
    regset = onigurumacffi.compile_regset('a', '.*')
    idx, match = regset.search('foo', start=3)
    assert idx == 1
    assert match is not None
    assert match.group() == ''


def test_regset_empty_match_empty_string():
    regset = onigurumacffi.compile_regset('a', '.*')
    idx, match = regset.search('')
    assert idx == 1
    assert match is not None
    assert match.group() == ''


def test_regset_search_with_flags():
    regset_A = onigurumacffi.compile_regset(r'\Afoo', 'foo')
    idx, match = regset_A.search('foo')
    assert idx == 0
    assert match is not None

    idx, match = regset_A.search(
        'foo',
        flags=onigurumacffi.OnigSearchOption.NOT_BEGIN_STRING,
    )
    assert idx == 1
    assert match is not None

    regset_G = onigurumacffi.compile_regset(r'\Gfoo', 'foo')
    idx, match = regset_G.search('afoo', start=1)
    assert idx == 0
    assert match is not None

    idx, match = regset_G.search(
        'afoo',
        start=1,
        flags=onigurumacffi.OnigSearchOption.NOT_BEGIN_POSITION,
    )
    assert idx == 1
    assert match is not None
