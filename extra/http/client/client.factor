! Copyright (C) 2005, 2008 Slava Pestov.
! See http://factorcode.org/license.txt for BSD license.
USING: assocs http kernel math math.parser namespaces sequences
io io.sockets io.streams.string io.files io.timeouts strings
splitting calendar continuations accessors vectors math.order
io.encodings.8-bit io.encodings.binary io.streams.duplex
fry debugger inspector ;
IN: http.client

: max-redirects 10 ;

ERROR: too-many-redirects ;

M: too-many-redirects summary
    drop
    [ "Redirection limit of " % max-redirects # " exceeded" % ] "" make ;

DEFER: http-request

<PRIVATE

: parse-url ( url -- resource host port )
    "http://" ?head [ "Only http:// supported" throw ] unless
    "/" split1 [ "/" prepend ] [ "/" ] if*
    swap parse-host ;

: store-path ( request path -- request )
    "?" split1 >r >>path r> dup [ query>assoc ] when >>query ;

: request-with-url ( request url -- request )
    parse-url >r >r store-path r> >>host r> >>port ;

SYMBOL: redirects

: absolute-url? ( url -- ? )
    [ "http://" head? ] [ "https://" head? ] bi or ;

: do-redirect ( response data -- response data )
    over code>> 300 399 between? [
        drop
        redirects inc
        redirects get max-redirects < [
            request get
            swap "location" header dup absolute-url?
            [ request-with-url ] [ store-path ] if
            "GET" >>method http-request
        ] [
            too-many-redirects
        ] if
    ] when ;

PRIVATE>

: read-chunks ( -- )
    read-crlf ";" split1 drop hex> dup { f 0 } member?
    [ drop ] [ read % read-crlf "" assert= read-chunks ] if ;

: read-response-body ( response -- response data )
    dup "transfer-encoding" header "chunked" =
    [ [ read-chunks ] "" make ] [ input-stream get contents ] if ;

: http-request ( request -- response data )
    dup request [
        dup request-addr latin1 [
            1 minutes timeouts
            write-request
            read-response
            read-response-body
        ] with-client
        do-redirect
    ] with-variable ;

: <get-request> ( url -- request )
    <request>
        swap request-with-url
        "GET" >>method ;

: http-get* ( url -- response data )
    <get-request> http-request ;

: success? ( code -- ? ) 200 = ;

ERROR: download-failed response body ;

M: download-failed error.
    "HTTP download failed:" print nl
    [
        response>>
            write-response-code
            write-response-message nl
        drop
    ]
    [ body>> write ] bi ;

: check-response ( response string -- string )
    over code>> success? [ nip ] [ download-failed ] if ;

: http-get ( url -- string )
    http-get* check-response ;

: download-name ( url -- name )
    file-name "?" split1 drop "/" ?tail drop ;

: download-to ( url file -- )
    #! Downloads the contents of a URL to a file.
    >r http-get r> latin1 [ write ] with-file-writer ;

: download ( url -- )
    dup download-name download-to ;

: <post-request> ( content-type content url -- request )
    <request>
        "POST" >>method
        swap request-with-url
        swap >>post-data
        swap >>post-data-type ;

: http-post ( content-type content url -- response data )
    <post-request> http-request ;
