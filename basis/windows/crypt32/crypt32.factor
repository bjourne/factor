USING:
    alien.c-types alien.syntax
    arrays
    classes.struct
    windows.types ;
IN: windows.crypt32

LIBRARY: crypt32

CONSTANT: PKCS_7_ASN_ENCODING 0x00010000
CONSTANT: X509_ASN_ENCODING   0x0000abcd

STRUCT: CRYPTOAPI_BLOB
    { cbData DWORD }
    { pbData BYTE* } ;

STRUCT: CRYPT_ALGORITHM_IDENTIFIER
    { pszObjId LPSTR }
    { Parameters CRYPTOAPI_BLOB } ;

STRUCT: CERT_INFO
    { dwVersion DWORD }
    { SerialNumber CRYPTOAPI_BLOB }
    { SignatureAlgorithm CRYPT_ALGORITHM_IDENTIFIER }
    { Issuer CRYPTOAPI_BLOB } ;

STRUCT: CERT_CONTEXT
    { dwCertEncodingType DWORD }
    { pbCertEncoded BYTE* }
    { cbCertEncoded DWORD }
    { pCertInfo CERT_INFO* }
    { hCertStore void* } ;

FUNCTION: void* CertOpenStore ( void* hCertStore, LPCWSTR proto ) ;
FUNCTION: void* CertOpenSystemStoreW ( void* hCertStore, LPCWSTR storeType ) ;
FUNCTION: bool CertCloseStore ( void *hCertStore, int flags ) ;
ALIAS: CertOpenSystemStore CertOpenSystemStoreW
FUNCTION: CERT_CONTEXT* CertEnumCertificatesInStore ( void *hCertStore,
                                                      void* prevCertContext ) ;
