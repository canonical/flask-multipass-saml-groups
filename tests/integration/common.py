#  Copyright 2023 Canonical Ltd.
#  See LICENSE file for licensing details.
"""Common functions for integration tests."""

import base64
from collections import namedtuple
from typing import List

from flask.testing import FlaskClient

from flask_multipass_saml_groups.provider import SAML_GRP_ATTR_NAME

SP_ENTITY_ID = "http://localhost"

User = namedtuple("User", ["email", "identifier"])


def mk_saml_response(groups: List[str], user_email: str):
    """Create a SAML response with the given groups and user email.

    Args:
        groups: The groups to include in the response
        user_email: The user email to include in the response

    Returns:
        The SAML response
    """
    if groups:
        group_attr = f"""
            <saml:Attribute Name="{SAML_GRP_ATTR_NAME}">
               {"".join(f'<saml:AttributeValue>{grp}</saml:AttributeValue>' for grp in groups)}
            </saml:Attribute>"""
    else:
        group_attr = ""
    return f"""
<samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
                    Destination="http://localhost/multipass/saml/ubuntu/acs"
                    ID="_bcc53da5409a42dbb22461d58140d99d"
                    InResponseTo="ONELOGIN_xa4a3a3a"
                    IssueInstant="2023-07-19T13:31:09Z"
                    Version="2.0"
                    >
    <saml:Issuer xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">
    https://login.saml.com</saml:Issuer>
    <samlp:Status>
        <samlp:StatusCode Value="urn:oasis:names:tc:SAML:2.0:status:Success" />
    </samlp:Status>
    <saml:Assertion xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
                    ID="_e125c9c0cbc64cbf9de6b3ef9b2546e7"
                    IssueInstant="2023-07-19T13:31:09Z"
                    Version="2.0"
                    >
        <saml:Issuer>https://login.saml.com</saml:Issuer>
        <saml:Subject>
            <saml:NameID Format="urn:oasis:names:tc:SAML:2.0:nameid-format:email"
                         SPNameQualifier="{SP_ENTITY_ID}"
                         >{user_email}</saml:NameID>
            <saml:SubjectConfirmation Method="urn:oasis:names:tc:SAML:2.0:cm:bearer">
                <saml:SubjectConfirmationData InResponseTo="ONELOGIN_xa4a3a3a"
                                              NotOnOrAfter="2029-07-19T13:46:09Z"
                                              Recipient="http://localhost/multipass/saml/ubuntu/acs"
                                              />
            </saml:SubjectConfirmation>
        </saml:Subject>
        <saml:Conditions NotBefore="2023-07-18T13:31:09Z"
                         NotOnOrAfter="2099-07-19T13:46:09Z"
                         >
            <saml:AudienceRestriction>
                <saml:Audience>{SP_ENTITY_ID}</saml:Audience>
            </saml:AudienceRestriction>
        </saml:Conditions>
        <saml:AuthnStatement AuthnInstant="2023-07-19T13:31:09Z"
                             SessionIndex="4asddasdasd"
                             >
            <saml:AuthnContext>
                <saml:AuthnContextClassRef>urn:oasis:names:tc:SAML:2.0:ac:classes:Password</saml:AuthnContextClassRef>
            </saml:AuthnContext>
        </saml:AuthnStatement>
        <saml:AttributeStatement>
            <saml:Attribute Name="openid">
                <saml:AttributeValue>http://openid</saml:AttributeValue>
            </saml:Attribute>
            <saml:Attribute Name="userid">
                <saml:AttributeValue>{user_email}</saml:AttributeValue>
            </saml:Attribute>
            <saml:Attribute Name="username">
                <saml:AttributeValue>foo</saml:AttributeValue>
            </saml:Attribute>
            <saml:Attribute Name="email">
                <saml:AttributeValue>{user_email}</saml:AttributeValue>
            </saml:Attribute>
            <saml:Attribute Name="fullname">
                <saml:AttributeValue>foo bar</saml:AttributeValue>
            </saml:Attribute>
            {group_attr}
        </saml:AttributeStatement>
    </saml:Assertion>
</samlp:Response>"""


def login(client: FlaskClient, user_email: str, groups: List[str]):
    """Login a user with the given email and groups.

    Args:
        client: The test client
        user_email: The user email
        groups: The groups to include in the SAML response
    """
    resp = client.get("/login/ubuntu")
    assert resp.status_code == 302
    saml_response = mk_saml_response(groups=groups, user_email=user_email)
    resp = client.post(
        "/multipass/saml/ubuntu/acs",
        data={
            "SAMLResponse": base64.b64encode(saml_response.encode("utf-8")),
            "RelayState": "/login/ubuntu",
        },
    )
    assert resp.status_code == 302
