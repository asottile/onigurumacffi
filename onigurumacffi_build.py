from cffi import FFI

CDEF = '''\
#define ONIG_MAX_ERROR_MESSAGE_LEN ...

typedef unsigned int OnigOptionType;
#define ONIG_OPTION_NONE ...

#define ONIG_MISMATCH ...

typedef unsigned char OnigUChar;

struct re_pattern_buffer;
typedef struct re_pattern_buffer OnigRegexType;
typedef OnigRegexType regex_t;

struct OnigRegSetStruct;
typedef struct OnigRegSetStruct OnigRegSet;

typedef enum { ONIG_REGSET_POSITION_LEAD = ..., ...} OnigRegSetLead;

struct OnigEncodingTypeST{...;};
typedef struct OnigEncodingTypeST OnigEncodingType;
extern OnigEncodingType OnigEncodingUTF8;

typedef struct {...;} OnigSyntaxType;
extern OnigSyntaxType OnigSyntaxOniguruma;

typedef struct {...;} OnigErrorInfo;

struct re_registers {
    int allocated;
    int num_regs;
    int* beg;
    int* end;
    ...;
};
typedef struct re_registers OnigRegion;

OnigRegion* onig_region_new(void);
void onig_region_free(OnigRegion* region, int free_self);

int onig_initialize(OnigEncodingType* use_encodings[], int num_encodings);

int onig_error_code_to_str(OnigUChar* s, int err_code, ...);

int onig_new(
    regex_t** reg,
    const OnigUChar* pattern, const OnigUChar* pattern_end,
    OnigOptionType option,
    OnigEncodingType* enc,
    OnigSyntaxType* syntax,
    OnigErrorInfo* err_info
);

void onig_free(regex_t*);

int onig_match(
    regex_t* reg,
    const OnigUChar* str, const OnigUChar* end,
    const OnigUChar* at,
    OnigRegion* region,
    OnigOptionType option
);

int onig_search(
    regex_t* reg,
    const OnigUChar* str, const OnigUChar* end,
    const OnigUChar* start, const OnigUChar* range,
    OnigRegion* region,
    OnigOptionType option
);

int onig_regset_new(OnigRegSet** rset, int n, regex_t* regs[]);

void onig_regset_free(OnigRegSet*);

int onig_regset_search(
    OnigRegSet* set,
    const OnigUChar* str, const OnigUChar* end,
    const OnigUChar* start, const OnigUChar* range,
    OnigRegSetLead lead,
    OnigOptionType option,
    int* rmatch_pos
);

const char* onig_version(void);
'''
SRC = '#include <oniguruma.h>'

ffibuilder = FFI()
ffibuilder.cdef(CDEF)
ffibuilder.set_source('_onigurumacffi', SRC, libraries=['onig'])

if __name__ == '__main__':
    ffibuilder.compile(verbose=True)
