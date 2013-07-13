USING:
    accessors
    alien.data alien.enums alien.strings
    assocs
    classes.struct
    combinators
    io.encodings.string
    io.encodings.utf8
    kernel
    locals
    mirrors
    sequences
    specialized-arrays.instances.alien.c-types.void*
    xml2.ffi
    ;
IN: xml2.lib

! ******************************************************************************
! Helpers
! ******************************************************************************
: enums>int ( seq -- int )
    [ enum>number ] map-sum ;

! ******************************************************************************
!  XML Builders
! ******************************************************************************
:: element ( tag -- el )
    f f tag f xmlNewDocNode ;

: new-xml-doc ( -- doc )
    f xmlNewDoc
    ! Encoding must be set. Why is explicit conversion needed?
    [ [ "UTF-8" utf8 malloc-string ] unless* ] change-encoding ;


! ******************************************************************************
! Deserializers
! ******************************************************************************
: default-html-parse-options ( -- int )
    {
        HTML_PARSE_COMPACT
        ! Proper error handling would be better.
        HTML_PARSE_NOERROR
        HTML_PARSE_NONET
        HTML_PARSE_RECOVER
    } enums>int ;

: from-html-string ( str encoding -- doc )
    ! Create a parser context
    "dummy" utf8 encode 5 htmlCreateMemoryParserCtxt -rot
    encode dup length f f default-html-parse-options htmlCtxtReadMemory ;

: from-xml-file ( file -- ctx )
    xmlParseFile  ;

: from-xml-string ( str encoding -- doc )
    {
        [ encode ]
        [ encode length ]
        ! Where does this name come from?
        [ 2drop "include.xml" ]
        [ nip <mirror> "name" swap at ]
        [ 2drop 0 ]
    } 2cleave xmlReadMemory ;

! ******************************************************************************
! XPath
! ******************************************************************************
: nodeset>array ( nodeset -- array )
    [ nodeTab>> ] [ nodeNr>> ] bi <direct-void*-array>
    [ xmlNode memory>struct ] { } map-as ;

: xpath ( expr doc -- seq )
    xmlXPathNewContext xmlXPathEvalExpression nodesetval>> nodeset>array ;
