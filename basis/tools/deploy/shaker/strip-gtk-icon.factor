! Copyright (C) 2010 Philipp Brüschweiler
! See http://factorcode.org/license.txt for BSD license.
USING: kernel system tools.deploy.shaker literals namespaces
vocabs.loader io.pathnames io.files io.encodings.binary ;
IN: ui.backend.gtk

CONSTANT: get-icon-data
    $[
        deploy-vocab get
        dup vocab-dir "icon.png" append-path vocab-append-path
        [ exists? ] keep
        install-prefix "share/factor/icons/Factor_48x48.png" append-path ?
        binary file-contents
    ]
