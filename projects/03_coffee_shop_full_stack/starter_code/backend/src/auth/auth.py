import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen
from ..config import AUTH0_DOMAIN


AUTH0_DOMAIN = AUTH0_DOMAIN
ALGORITHMS = ['RS256']
API_AUDIENCE = 'dev'

# AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Auth Header

'''
@TODO implement get_token_auth_header() method
    it should attempt to get the header from the request
        it should raise an AuthError if no header is present
    it should attempt to split bearer and the token
        it should raise an AuthError if the header is malformed
    return the token part of the header
'''
def get_token_auth_header():
    header = request.headers.get('Authorization')
    if header is None:
        raise AuthError('Missing auth header', 401)
    token = header.split(' ')
    if len(token) != 2 or token[0] != 'Bearer' or token[1] is None:
        raise AuthError('Malformed auth header', 401)
    return token[1]


'''
@TODO implement check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    it should raise an AuthError if permissions are not included in the payload
        !!NOTE check your RBAC settings in Auth0
    it should raise an AuthError if the requested permission string is not in the payload permissions array
    return true otherwise
'''
def check_permissions(permission, payload):
    permissions = payload.get('permissions')
    if permissions is None:
        raise AuthError(
            'Invalid auth token. Unable to locate permission scopes.', 401
        )
    if permission not in permissions:
        raise AuthError(
            'Invalid permission scope. User has insufficient privileges.', 401
        )


'''
@TODO implement verify_decode_jwt(token) method
    @INPUTS
        token: a json web token (string)

    it should be an Auth0 token with key id (kid)
    it should verify the token using Auth0 /.well-known/jwks.json
    it should decode the payload from the token
    it should validate the claims
    return the decoded payload

    !!NOTE urlopen has a common certificate error described here: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
'''
def verify_decode_jwt(token):
    # Get the public key from Auth0
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())

    # Get the data in the header
    unverified_header = jwt.get_unverified_header(token)
   
    # Choose the key
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError('Invalid auth header', 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
   
    # Verify
    if rsa_key:
        try:
            # Use the key to validate the token
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload
        except jwt.ExpiredSignatureError:
            raise AuthError('Expired auth token', 401)
        except jwt.JWTClaimsError:
            raise AuthError(
                'Invalid auth claim. Check the audience and issuer.', 403
            )
        except Exception:
            raise AuthError(
                'Invalid auth header. Unable to parse auth token.', 400
            )
    raise AuthError(
        'Invalid auth header. Unable to find the appropriate key.', 400
    )


'''
@TODO implement @requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
'''
def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                token = get_token_auth_header()
                payload = verify_decode_jwt(token)
                check_permissions(permission, payload)
            except AuthError:
                raise
            return f(payload, *args, **kwargs)
        return wrapper
    return requires_auth_decorator
