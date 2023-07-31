# Flask-Multipass-SAML-Groups

This package provides an identity provider for [Flask-Multipass](https://github.com/indico/flask-multipass),
which allows you to use SAML groups. It is designed to be used
as a plugin for [Indico](https://github.com/indico/indico).

> **Warning**
> The current code base has not been extensively tested and should be considered experimental.


## Motivation

The current SAML identity provider in Flask-Multipass does not support groups (see [issue](https://github.com/indico/flask-multipass/issues/66)),
but groups are a very useful feature for Indico. This plugin provides a solution to this problem.


## Installation

### Package installation
You need to install the package on the same virtual environment as your Indico instance.
You might use the following commands to switch to the Indico environment

```bash
su - indico
source ~/.venv/bin/activate
```

Some of the dependencies, like [xmlsec](https://xmlsec.readthedocs.io/en/stable/install.html),
require native libraries to be installed on the system. To install these libraries on an
Ubuntu system, you can use the `install-packages.sh` file:

```bash
sudo bash install-libs.sh
```

You can then install this package either via local source:

```bash
git clone https://github.com/canonical/flask-multipass-saml-groups.git
cd flask-multipass-saml-groups
python setup.py install 
```

or with pip:

```bash
pip install git+https://github.com/canonical/flask-multipass-saml-groups.git
```


### Indico setup

In your Indico setup, you should see that the plugin is now available:

```bash
indico setup list-plugins
```

In order to activate the plugin, you must add it to the list of active plugins in your Indico configuration file:

```python
PLUGINS = { ..., 'saml_groups' }
```

Beyond that, the plugin uses its own database tables to persist the groups. Therefore you need to run

```bash
indico db --all-plugins upgrade
```
See [here](https://docs.getindico.io/en/latest/installation/plugins/) for more information on installing
Indico plugins.


### Identity provider configuration
The configuration is almost identical to the SAML identity provider in Flask-Multipass,
but you should use the type `saml_groups` instead of `saml`. The identity provider must be used
together with the SAML auth Provider, in order to receive the SAML groups in the authentication
data.

The following is an example section in `indico.conf`:
```python

_my_saml_config = {
    'sp': {
        'entityId': 'https://events.example.com',
        'x509cert': '',
        'privateKey': '',
    },
    'idp': {
        'entityId': 'https://login.example.com',
        'x509cert': 'YmFzZTY0IGVuY29kZWQgY2VydAo',
        'singleSignOnService': {
            'url': 'https://login.example.com/saml/',
            'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'
        },
        'singleLogoutService': {
            'url': 'https://login.example.com/+logout',
            'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'
        }
    },
    'security': {
        'nameIdEncrypted': False,
        'authnRequestsSigned': False,
        'logoutRequestSigned': False,
        'logoutResponseSigned': False,
        'signMetadata': False,
        'wantMessagesSigned': False,
        'wantAssertionsSigned': False,
        'wantNameId' : False,
        'wantNameIdEncrypted': False,
        'wantAssertionsEncrypted': False,
        'allowSingleLabelDomains': False,
        'signatureAlgorithm': 'http://www.w3.org/2001/04/xmldsig-more#rsa-sha256',
        'digestAlgorithm': 'http://www.w3.org/2001/04/xmlenc#sha256'
    },
}

MULTIPASS_AUTH_PROVIDERS = {
    'ubuntu': {
        'type': 'saml',
        'title': 'SAML SSO',
        'saml_config': _my_saml_config,
    },
}
IDENTITY_PROVIDERS = {
"ubuntu": {
            "type": "saml_groups",
            "trusted_email": True,
            "mapping": {
                "user_name": "username",
                "first_name": "fullname",
                "last_name": "",
                "email": "email",
            },
            "identifier_field": "openid",
       }
}
```