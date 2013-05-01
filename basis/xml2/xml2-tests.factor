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

CONSTANT: base "../../xml/tests/xmltest/"

: sample-document ( -- str encoding )
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

: abspath ( file -- path )
    base swap append-path ;

! Parsing
[ XML_DOCUMENT_NODE ]
[
    sample-document parse-xml-string type>>
] unit-test

[ XML_DOCUMENT_NODE ]
[
    "xmltest.xml" abspath parse-xml-file type>>
] unit-test

! Let's see if we can parse *broken* html
[
    "Gmane -- Re: Out of memory error"
] [
    "/html/head/title/text()"
    "http://article.gmane.org/gmane.comp.lang.factor.general/6020"
    http-get nip utf8 parse-html-string xpath first content>>
] unit-test

! XPath
[ 382 ]
[
    "/TESTCASES/TEST/text()" "xmltest.xml" abspath parse-xml-file
    xpath length
] unit-test

[
    "\n    Attribute values must start with attribute names, not \"?\". "
] [
    "/TESTCASES/TEST[1]/text()"
    "xmltest.xml" abspath parse-xml-file
    xpath first content>>
] unit-test

[
    "List of people:"
] [
    "/document/p/text()" sample-document parse-xml-string xpath first content>>
] unit-test

[
    "Hello"
] [
    "/html/head/title/text()" sample-html-document
    parse-html-string xpath first content>>
] unit-test


