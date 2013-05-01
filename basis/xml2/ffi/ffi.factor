USING:
    accessors
    alien alien.c-types alien.libraries alien.syntax
    classes.struct
    combinators
    formatting
    io
    kernel
    math
    sequences
    specialized-arrays.instances.alien.c-types.void*
    strings
    system
    unicode.case
    unicode.categories ;
IN: xml2.ffi

<< "xml2" {
    { [ os unix? ] [ "libxml2.so.2" ] }
} cond cdecl add-library >>

LIBRARY: xml2

ENUM: htmlParserOption
    { HTML_PARSE_RECOVER 1 }
    { HTML_PARSE_NODEFDTD 4 }
    { HTML_PARSE_NOERROR 32 }
    { HTML_PARSE_PEDANTIC 128 }
    { HTML_PARSE_NONET 2048 }
    { HTML_PARSE_COMPACT 65536 } ;

ENUM: xmlXPathObjectType
    XPATH_UNDEFINED
    XPATH_NODESET
    XPATH_BOOLEAN
    XPATH_NUMBER
    XPATH_STRING
    XPATH_POINT
    XPATH_RANGE
    XPATH_LOCATIONSET
    XPATH_USERS
    XPATH_XSLT_TREE ;

ENUM: xmlElementType
    { XML_ELEMENT_NODE 1 }
    { XML_ATTRIBUTE_NODE 2 }
    { XML_TEXT_NODE 3 }
    { XML_CDATA_SECTION_NODE 4 }
    { XML_ENTITY_REF_NODE 5 }
    { XML_ENTITY_NODE 6 }
    { XML_PI_NODE 7 }
    { XML_COMMENT_NODE 8 }
    { XML_DOCUMENT_NODE 9 }
    { XML_DOCUMENT_TYPE_NODE 10 }
    { XML_DOCUMENT_FRAG_NODE 11 }
    { XML_NOTATION_NODE 12 }
    { XML_HTML_DOCUMENT_NODE 13 }
    { XML_DTD_NODE 14 }
    { XML_ELEMENT_DECL 15 }
    { XML_ATTRIBUTE_DECL 16 }
    { XML_ENTITY_DECL 17 }
    { XML_NAMESPACE_DECL 18 }
    { XML_XINCLUDE_START 19 }
    { XML_XINCLUDE_END 20 }
    { XML_DOCB_DOCUMENT_NODE 21 } ;

TYPEDEF: xmlElementType xmlNsType

C-TYPE: xmlDoc
C-TYPE: xmlNs

STRUCT: xmlNs
    { next xmlNs* }
    { type xmlNsType }
    { href c-string }
    { prefix c-string }
    { private void* }
    { context xmlDoc* } ;

STRUCT: xmlNode
    { _private void* }
    { type xmlElementType }
    { name c-string }
    { children xmlNode* }
    { last xmlNode* }
    { parent xmlNode* }
    { next xmlNode* }
    { prev xmlNode* }
    { doc xmlDoc* }
    { ns xmlNs* }
    { content c-string } ;
TYPEDEF: xmlNode* xmlNodePtr

STRUCT: xmlDoc
    { _private void* }
    { type xmlElementType }
    { name c-string }
    { children xmlNodePtr }
    { last xmlNode* }
    { parent xmlNode* }
    { next xmlNode* }
    { prev xmlNode* }
    { doc xmlDoc* } ;
TYPEDEF: xmlDoc* xmlDocPtr

STRUCT: xmlXPathContext
    { doc xmlDocPtr }
    { node xmlNodePtr }
    { nb_variables_unused int }
    { max_variables_unused int } ;
TYPEDEF: xmlXPathContext* xmlXPathContextPtr

STRUCT: xmlSAXHandler
    { internalSubsetSAXFunc void* }
    { isStandaloneSAXFunc void* }
    { hasInternalSubset void* }
    { hasExternalSubset void* }
    { resolveEntity void* }
    { getEntity void* }
    { entityDecl void* }
    { notationDecl void* }
    { attributeDecl void* }
    { elementDecl void* }
    { unparsedEntityDecl void* }
    { setDocumentLocator void* }
    { startDocument void* }
    { endDocument void* }
    { startElement void* }
    { endElement void* }
    { reference void* }
    { characters void* }
    { ignorableWhitespace void* }
    { processingInstruction void* }
    { comment void* } ;
TYPEDEF: xmlSAXHandler* xmlSAXHandlerPtr


STRUCT: xmlParserInputBuffer
    { context void* } ;
TYPEDEF: xmlParserInputBuffer* xmlParserInputBufferPtr

STRUCT: xmlParserInput
    { buf xmlParserInputBufferPtr }
    { filename c-string }
    { directory c-string } ;
TYPEDEF: xmlParserInput* xmlParserInputPtr

STRUCT: xmlParserCtxt
    { sax xmlSAXHandlerPtr }
    { userData void* }
    { myDoc xmlDocPtr }
    { wellFormed int }
    { replaceEntities int }
    { version c-string }
    { encoding c-string }
    { standalone int }
    { html int }
    { input xmlParserInputPtr } ;

TYPEDEF: xmlParserCtxt* xmlParserCtxtPtr

TYPEDEF: xmlParserCtxtPtr htmlParserCtxtPtr

STRUCT: xmlNodeSet
    { nodeNr int }
    { nodeMax int }
    { nodeTab xmlNode** } ;
TYPEDEF: xmlNodeSet* xmlNodeSetPtr

STRUCT: xmlXPathObject
    { type xmlXPathObjectType }
    { nodesetval xmlNodeSetPtr } ;
TYPEDEF: xmlXPathObject* xmlXPathObjectPtr



FUNCTION: void xmlInitParser ( ) ;
FUNCTION: int xmlPedanticParserDefault ( int ) ;
FUNCTION: xmlNodePtr xmlDocGetRootElement ( xmlDocPtr ) ;
FUNCTION: xmlDocPtr xmlReadMemory ( char* buffer,
                                    int size,
                                    c-string URL,
                                    c-string encoding,
                                    int options ) ;
FUNCTION: xmlDocPtr xmlReadFile ( c-string filename,
                                  c-string encoding,
                                  int options ) ;
FUNCTION: xmlDocPtr xmlParseFile ( c-string filename ) ;
FUNCTION: int xmlSaveFormatFileEnc ( c-string filename,
                                     xmlDocPtr cur,
                                     c-string encoding,
                                     int format ) ;
FUNCTION: xmlXPathContextPtr xmlXPathNewContext ( xmlDocPtr ) ;
FUNCTION: xmlXPathObjectPtr xmlXPathEvalExpression
    ( c-string str,
      xmlXPathContextPtr ctxt ) ;
FUNCTION: xmlDocPtr htmlCtxtReadMemory ( xmlParserCtxtPtr ctxt,
                                         char* buffer,
                                         int size,
                                         char* filename,
                                         char* encoding,
                                         int options ) ;
FUNCTION: htmlParserCtxtPtr htmlCreateMemoryParserCtxt ( char* buffer,
                                                          int size ) ;
FUNCTION: htmlParserCtxtPtr htmlNewParserCtxt ( ) ;
