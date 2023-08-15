from dataclasses import dataclass, field
class GoogleDiscoveryKeys:
    AUTH_ENDPOINT = "authorization_endpoint"
    TOKEN_ENDPOINT = "token_endpoint"
    USERINFO_ENDPOINT = "userinfo_endpoint"
    REVOKE_ENDPOINT = "revocation_endpoint"

@dataclass
class GoogleAuthResponse:
    email: str
    email_verified: bool
    sub: str
    locale: str | None = field(default=None)
    family_name: str | None = field(default=None)
    given_name: str | None = field(default=None)
    name: str | None = field(default=None)
    picture: str | None = field(default=None)



# email	"arianghobadibigvand@gmail.com"
# email_verified	true
# family_name	"Ghobadibigvand"
# given_name	"Arian"
# locale	"en-GB"
# name	"Arian Ghobadibigvand"
# picture	"https://lh3.googleusercontent.com/a/AAcHTtf4hLP-R5GgU5DfKLPh2CbSVk6jqV9Jht_NPFoq0cU6=s96-c"
# sub	"112310551934329742462"    