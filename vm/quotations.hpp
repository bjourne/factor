namespace factor {

/**
 * Simple non-optimizing compiler.
 *
 * This is one of the two compilers implementing Factor; the
 * second one is written in Factor and performs advanced
 * optimizations. See basis/compiler/compiler.factor.
 *
 * The non-optimizing compiler compiles a quotation at a time by
 * concatenating machine code chunks; prolog, epilog, call word,
 * jump to word, etc. These machine code chunks are generated from
 * Factor code in basis/cpu/.../bootstrap.factor.
 *
 * Calls to words and constant quotations (referenced by
 * conditionals and dips) are direct jumps to machine code
 * blocks. Literals are also referenced directly without going
 * through the literal table.
 *
 * It actually does do a little bit of very simple optimization:
 *
 * 1. Tail call optimization.
 *
 * 2. If a quotation is determined to not call any other words
 * (except for a few special words which are open-coded, see
 * below), then no prolog/epilog is generated.
 *
 * 3. When in tail position and immediately preceded by literal
 * arguments, the 'if' is generated inline, instead of as a call
 * to the 'if' word.
 *
 * 4. When preceded by a quotation, calls to 'dip', '2dip' and
 * '3dip' are open-coded as retain stack manipulation surrounding
 * a subroutine call.
 *
 * 5. Sub-primitives are primitive words which are implemented in
 * assembly and not in the VM. They are open-coded and no
 * subroutine call is generated. This includes stack shufflers,
 * some fixnum arithmetic words, and words such as tag, slot and
 * eq?. A primitive call is relatively expensive (two subroutine
 * calls) so this results in a big speedup for relatively little
 * effort.
 */
struct quotation_jit : public jit {
  data_root<array> elements;
  bool compiling, relocate;

  quotation_jit(cell owner, bool compiling, bool relocate, factor_vm* vm)
      : jit(code_block_unoptimized, owner, vm),
        elements(false_object, vm),
        compiling(compiling),
        relocate(relocate) {}
  ;

  void init_quotation(cell quot);
  void emit_mega_cache_lookup(cell methods, fixnum index, cell cache);
  bool primitive_call_p(cell i, cell length);
  bool trivial_quotation_p(array* elements);
  void emit_quot(cell quot);
  void emit_prolog(bool safepoint, bool stack_frame);
  void emit_epilog(bool safepoint, bool stack_frame);
  bool fast_if_p(cell i, cell length);
  bool fast_dip_p(cell i, cell length);
  bool fast_2dip_p(cell i, cell length);
  bool fast_3dip_p(cell i, cell length);
  bool mega_lookup_p(cell i, cell length);
  bool declare_p(cell i, cell length);
  bool special_subprimitive_p(cell obj);
  bool word_stack_frame_p(cell obj);
  cell word_stack_frame_size(cell obj);
  bool word_safepoint_p(cell obj);
  bool stack_frame_p();
  bool safepoint_p();
  void iterate_quotation();
};

VM_C_API cell lazy_jit_compile(cell quot, factor_vm* parent);

}
