USING:
    alien.c-types alien.syntax ;
IN: windows.crypt32


LIBRARY: crypt32

FUNCTION: void* CertOpenStore ( void* hprov, c-string proto ) ;
