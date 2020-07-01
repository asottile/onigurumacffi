import os
import sys

from cffi import FFI

CDEF = '''\
#define ONIG_MAX_ERROR_MESSAGE_LEN ...

#define ONIG_MISMATCH ...

typedef unsigned int OnigOptionType;

#define ONIG_OPTION_NONE ...
#define ONIG_OPTION_NOTBOL ...
#define ONIG_OPTION_NOTEOL ...
#define ONIG_OPTION_POSIX_REGION ...
#define ONIG_OPTION_CHECK_VALIDITY_OF_STRING ...
#define ONIG_OPTION_NOT_BEGIN_STRING ...
#define ONIG_OPTION_NOT_BEGIN_POSITION ...
#define ONIG_OPTION_NOT_END_STRING ...

typedef unsigned char OnigUChar;

int onigcffi_initialize(void);

const char* onig_version(void);

typedef struct {...;} OnigErrorInfo;
int onig_error_code_to_str(OnigUChar* s, int err_code, ...);

struct re_registers {
    int allocated;
    int num_regs;
    int* beg;
    int* end;
    ...;
};
typedef struct re_registers OnigRegion;

OnigRegion* onig_region_new(void);
void onigcffi_region_free(OnigRegion* region);

typedef ... regex_t;
int onigcffi_new(
    regex_t** reg,
    const OnigUChar* pattern, size_t len,
    OnigErrorInfo* err_info
);
void onig_free(regex_t*);

int onig_number_of_captures(regex_t* reg);

int onigcffi_match(
    regex_t* reg,
    const OnigUChar* str, size_t len, size_t start,
    OnigRegion* region,
    OnigOptionType flags
);

int onigcffi_search(
    regex_t* reg,
    const OnigUChar* str, size_t len, size_t start,
    OnigRegion* region,
    OnigOptionType flags
);

typedef ... OnigRegSet;
int onig_regset_new(OnigRegSet** rset, int n, regex_t* regs[]);
void onig_regset_free(OnigRegSet*);

int onigcffi_regset_search(
    OnigRegSet* set,
    const OnigUChar* str, size_t len, size_t start, OnigRegion** region,
    OnigOptionType flags
);
'''
SRC = '''\
#include <oniguruma.h>

int onigcffi_initialize(void) {
    OnigEncoding enc = ONIG_ENCODING_UTF8;
    return onig_initialize(&enc, 1);
}

void onigcffi_region_free(OnigRegion* region) {
    onig_region_free(region, 1);
}

int onigcffi_new(
    regex_t** reg,
    const OnigUChar* pattern, size_t len,
    OnigErrorInfo* err_info
) {
    return onig_new(
        reg,
        pattern, pattern + len,
        ONIG_OPTION_NONE,
        ONIG_ENCODING_UTF8,
        ONIG_SYNTAX_ONIGURUMA,
        err_info
    );
}

int onigcffi_match(
    regex_t* reg,
    const OnigUChar* str, size_t len, size_t start, OnigRegion* region,
    OnigOptionType flags
) {
    return onig_match(
        reg,
        str, str + len,
        str + start,
        region,
        flags
    );
}

int onigcffi_search(
    regex_t* reg,
    const OnigUChar* str, size_t len, size_t start, OnigRegion* region,
    OnigOptionType flags
) {
    return onig_search(
        reg,
        str, str + len,
        str + start, str + len,
        region,
        flags
    );
}

int onigcffi_regset_search(
    OnigRegSet* set,
    const OnigUChar* str, size_t len, size_t start, OnigRegion** region,
    OnigOptionType flags
) {
    int _unused_match_pos;
    int idx = onig_regset_search(
        set,
        str, str + len,
        str + start, str + len,
        ONIG_REGSET_POSITION_LEAD,
        flags,
        &_unused_match_pos
    );
    if (idx >= 0) {
        *region = onig_regset_get_region(set, idx);
    }
    return idx;
}
'''

ffibuilder = FFI()
ffibuilder.cdef(CDEF)

if sys.platform == 'win32':
    ffibuilder.set_source(
        '_onigurumacffi', SRC,
        libraries=['onig_s'],
        define_macros=[('ONIG_EXTERN', 'extern')],
        include_dirs=[os.path.join(os.environ['ONIGURUMA_CLONE'], 'src')],
        library_dirs=[os.environ['ONIGURUMA_CLONE']],
    )
else:
    ffibuilder.set_source('_onigurumacffi', SRC, libraries=['onig'])

if __name__ == '__main__':
    ffibuilder.compile(verbose=True)
