from enum import Enum

class EnumHelper(Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

class AuthTypeEnum(EnumHelper):
    
    PLAINTEXT = "PLAINTEXT"
    OAUTHBEARER = "OAUTHBEARER"
    SCRAM = "SCRAM"
    KEYCLOAK = "KEYCLOAK"
    GSSAPI = "GSSAPI"
    KERBEROS = "KERBEROS"
    SASL = "SASL"
    SSL = "SSL"
    LDAP = "LDAP"
