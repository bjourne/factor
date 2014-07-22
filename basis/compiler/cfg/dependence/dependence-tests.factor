USING: accessors assocs compiler.cfg.dependence compiler.cfg.instructions
compiler.cfg.registers namespaces sequences tools.test ;
IN: compiler.cfg.dependence.tests

: test-instructions ( -- seq )
    {
        T{ ##peek { dst 37 } { loc D 0 } }
        T{ ##peek { dst 38 } { loc D 1 } }
        T{ ##load-tagged { dst 39 } { val 0 } }
        T{ ##inc-d { n 2 } }
        T{ ##replace { src 38 } { loc D 2 } }
        T{ ##replace { src 37 } { loc D 3 } }
        T{ ##replace { src 37 } { loc D 1 } }
    } ;

{ 7 } [ test-instructions build-dependence-graph nodes get length ] unit-test
{ 2 } [
    test-instructions build-dependence-graph nodes get
    first precedes>> assoc-size
] unit-test
