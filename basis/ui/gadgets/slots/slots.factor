! Copyright (C) 2007, 2009 Slava Pestov.
! See http://factorcode.org/license.txt for BSD license.
USING: accessors eval kernel math.vectors parser prettyprint
refs sequences ui.commands ui.gadgets ui.gadgets.editors
ui.gadgets.scrollers ui.gadgets.toolbar ui.gadgets.tracks
ui.gestures ui.tools.common ;
IN: ui.gadgets.slots

TUPLE: update-object ;

TUPLE: update-slot ;

TUPLE: edit-slot ;

TUPLE: slot-editor < track ref close-hook update-hook text ;

: revert ( slot-editor -- )
    [ ref>> get-ref unparse-use ] [ text>> ] bi set-editor-string ;

\ revert H{
    { +description+ "Revert any uncomitted changes." }
} define-command

: close ( slot-editor -- )
    dup close-hook>> call( slot-editor -- ) ;

\ close H{
    { +description+ "Close the slot editor without saving changes." }
} define-command

: close-and-update ( slot-editor -- )
    [ update-hook>> call( -- ) ] [ close ] bi ;

: slot-editor-value ( slot-editor -- object )
    text>> control-value parse-fresh first ;

: commit ( slot-editor -- )
    [ [ slot-editor-value ] [ ref>> ] bi set-ref ]
    [ close-and-update ]
    bi ;

\ commit H{
    { +description+ "Parse the object being edited, and store the result back into the edited slot." }
} define-command

: com-eval ( slot-editor -- )
    [ [ text>> editor-string eval( -- result ) ] [ ref>> ] bi set-ref ]
    [ close-and-update ]
    bi ;

\ com-eval H{
    { +listener+ t }
    { +description+ "Parse code which evaluates to an object, and store the result back into the edited slot." }
} define-command

: delete ( slot-editor -- )
    [ ref>> delete-ref ] [ close-and-update ] bi ;

\ delete H{
    { +description+ "Delete the slot and close the slot editor." }
} define-command

: <slot-editor> ( close-hook update-hook ref -- gadget )
    vertical slot-editor new-track
        swap >>ref
        swap >>update-hook
        swap >>close-hook
        add-toolbar
        <source-editor> >>text
        dup text>> <scroller> 1 track-add
        dup revert white-interior ;

M: slot-editor pref-dim* call-next-method { 600 200 } vmin ;

M: slot-editor focusable-child* text>> ;

slot-editor "toolbar" f {
    { T{ key-down f { C+ } "RET" } commit }
    { T{ key-down f { S+ C+ } "RET" } com-eval }
    { f revert }
    { f delete }
    { T{ key-down f f "ESC" } close }
} define-command-map
