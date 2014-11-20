namespace factor { void abort(); }

#ifdef FACTOR_DEBUG

#define FACTOR_PRINT_RAW(fmt, ...)              \
  do {                                      \
    if (factor_print_p) {                   \
      printf("%-28s %4d %-24s " fmt,   \
             __FILE__,                      \
             __LINE__,                      \
             __FUNCTION__,                  \
             __VA_ARGS__);                  \
    }                                       \
  } while (0)



#define FACTOR_PRINT(fmt, ...)              \
  do {                                      \
    if (factor_print_p) {                   \
      printf("%-28s %4d %-24s " fmt "\n",   \
             __FILE__,                      \
             __LINE__,                      \
             __FUNCTION__,                  \
             __VA_ARGS__);                  \
    }                                       \
  } while (0)
#define FACTOR_PRINT_MARK FACTOR_PRINT("%s", "")
#define FACTOR_PRINT_MARK_RAW FACTOR_PRINT_RAW("%s", "")
#define FACTOR_ASSERT(condition)                                               \
  ((condition)                                                                 \
       ? (void)0                                                               \
       : (::fprintf(stderr, "assertion \"%s\" failed: file \"%s\", line %d\n", \
                    #condition, __FILE__, __LINE__),                           \
          ::factor::abort()))

#else

#define FACTOR_PRINT(fmt, ...) ((void)0)
#define FACTOR_PRINT_MARK ((void)0)
#define FACTOR_ASSERT(condition) ((void)0)

#endif
