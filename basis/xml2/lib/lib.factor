USING:
    accessors
    alien.enums alien.strings
    assocs
    classes.struct
    combinators
    io.encodings.string
    io.encodings.utf8
    kernel
    mirrors
    sequences
    specialized-arrays.instances.alien.c-types.void*
    xml2.ffi
    ;
IN: xml2.lib

: enums>int ( seq -- int )
    [ enum>number ] map-sum ;

: default-html-parse-options ( -- int )
    {
        HTML_PARSE_COMPACT
        ! Proper error handling would be better.
        HTML_PARSE_NOERROR
        HTML_PARSE_NONET
        HTML_PARSE_RECOVER
    } enums>int ;

: parse-html-string ( str encoding -- doc )
    ! Create a parser context
    "dummy" utf8 encode 5 htmlCreateMemoryParserCtxt -rot
    encode dup length f f default-html-parse-options htmlCtxtReadMemory ;

: parse-xml-file ( file -- ctx )
    xmlParseFile  ;

: parse-xml-string ( str encoding -- doc )
    {
        [ encode ]
        [ encode length ]
        ! Where does this name come from?
        [ 2drop "include.xml" ]
        [ nip <mirror> "name" swap at ]
        [ 2drop 0 ]
    } 2cleave xmlReadMemory ;

: nodeset>array ( nodeset -- array )
    [ nodeTab>> ] [ nodeNr>> ] bi <direct-void*-array>
    [ xmlNode memory>struct ] { } map-as ;

: xpath ( expr doc -- seq )
    xmlXPathNewContext xmlXPathEvalExpression nodesetval>> nodeset>array ;
