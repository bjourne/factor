USING: alien.syntax assocs sequences system vocabs ;
IN: libc.types

C-TYPE: FILE

! libc.types.unix contains common types to unixlikes.
os { { linux { "libc.types.unix" "libc.types.linux"  } }
     { macosx { "libc.types.unix" "libc.types.macosx" } }
     { windows { "libc.types.windows" } }
} at [ require ] each
