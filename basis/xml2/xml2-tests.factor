USING:
    accessors
    http.client
    io.encodings.utf8
    io.pathnames
    kernel
    tools.test
    xml2.ffi
    xml2.lib
    sequences
    ;
IN: xml2.tests

! Can you look up files relative to the file being compiled?
CONSTANT: base "../xml/tests/xmltest/"

: sample-xml-document ( -- str encoding )
    {
        "<?xml version='1.0'?>"
        "<document xmlns:xi=\"http://www.w3.org/2003/XInclude\">"
        "<p>List of people:</p>\n"
        "</document>"
    } concat utf8 ;

: sample-html-document ( -- str encoding )
    {
        "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0 Transitional//EN\">"
        "<html>"
        "<head>"
        "<title>Hello</title>"
        "</head>"
        "</html>"
    } concat utf8 ;

: sample-xml-fragment ( -- str encoding )
    {
        "<monster name='Heffalump'>"
        "<trail>Woozle</trail>"
        "<eeyore mood='boogy'/>"
        "</monster>"
    } concat utf8 ;

: abspath ( file -- path )
    base swap append-path ;

! ******************************************************************************
! Parsing
! ******************************************************************************
[ XML_DOCUMENT_NODE ]
[
    sample-xml-document from-xml-string type>>
] unit-test

[ XML_DOCUMENT_NODE ]
[
    sample-xml-fragment from-xml-string type>>
] unit-test

[ XML_DOCUMENT_NODE ]
[
    "xmltest.xml" abspath from-xml-file type>>
] unit-test

! Let's see if we can parse *broken* html
[
    "Gmane -- Re: Out of memory error"
] [
    "/html/head/title/text()"
    "http://article.gmane.org/gmane.comp.lang.factor.general/6020"
    http-get nip utf8 from-html-string xpath first content>>
] unit-test

! Entities should be translated
[
    "Factor-talk <at> lists.sourceforge.net"
] [
    "//a[@href=\"mailto:Factor-talk-5NWGOfrQmneRv+LV9MX5uipxlwaOVQ5f@public.gmane.org\"]/text()"
    "http://article.gmane.org/gmane.comp.lang.factor.general/6020"
    http-get nip utf8 from-html-string
    xpath first content>>
] unit-test

! ******************************************************************************
! XPath
! ******************************************************************************
[ 382 ]
[
    "/TESTCASES/TEST/text()" "xmltest.xml" abspath from-xml-file
    xpath length
] unit-test

[
    "\n    Attribute values must start with attribute names, not \"?\". "
] [
    "/TESTCASES/TEST[1]/text()"
    "xmltest.xml" abspath from-xml-file
    xpath first content>>
] unit-test

[
    "List of people:"
] [
    "/document/p/text()"
    sample-xml-document from-xml-string
    xpath first content>>
] unit-test

[
    "Hello"
] [
    "/html/head/title/text()" sample-html-document
    from-html-string xpath first content>>
] unit-test


! ******************************************************************************
!  Building
! ******************************************************************************
[
    "head"
] [
    "head" element name>>
] unit-test

[
    "1.0"
] [
    new-xml-doc version>>
] unit-test

[
    "UTF-8"
] [
    new-xml-doc encoding>>
] unit-test
