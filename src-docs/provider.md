<!-- markdownlint-disable -->

<a href="../flask_multipass_saml_groups/provider.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `provider`
SAML Groups Identity Provider. 

**Global Variables**
---------------
- **DEFAULT_IDENTIFIER_FIELD**
- **SAML_GRP_ATTR_NAME**
- **SESSION_EXPIRY_SETTING**
- **DEFAULT_SESSION_EXPIRY**
- **EXPIRY_SESSION_KEY**


---

<a href="../flask_multipass_saml_groups/provider.py#L30"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `SAMLGroupsIdentityProvider`
Provides identity information using SAML and supports groups. 

Attrs:  supports_get (bool): If the provider supports getting identity information  based from an identifier  supports_groups (bool): If the provider also provides groups and membership information  supports_get_identity_groups (bool): If the provider supports getting the list of groups an  identity belongs to  group_class (class): The class to use for groups. Defaults to flask_multipass.Group but  concrete class will be used from group_provider_class 

<a href="../flask_multipass_saml_groups/provider.py#L49"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    multipass: Multipass,
    name: str,
    settings: Dict,
    group_provider_class: Type[GroupProvider] = <class 'flask_multipass_saml_groups.group_provider.sql.SQLGroupProvider'>
)
```

Initialize the identity provider. 



**Args:**
 
 - <b>`multipass`</b>:  The Flask-Multipass instance 
 - <b>`name`</b>:  The name of this identity provider instance 
 - <b>`settings`</b>:  The settings dictionary for this identity  provider instance 
 - <b>`group_provider_class`</b>:  The class to use for the group provider. 

Raise: 
 - <b>`ValueError`</b>:  If the session_expiry setting is not a positive integer. 




---

<a href="../flask_multipass_saml_groups/provider.py#L132"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_group`

```python
get_group(name: str) → Optional[Group]
```

Return a specific group. 



**Args:**
 
 - <b>`name`</b>:  The name of the group. 



**Returns:**
 
 - <b>`group`</b>:  An instance of group_class or None if the group does not exist. 

---

<a href="../flask_multipass_saml_groups/provider.py#L82"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_identity_from_auth`

```python
get_identity_from_auth(auth_info: AuthInfo) → IdentityInfo
```

Retrieve identity information after authentication. 



**Args:**
 
 - <b>`auth_info`</b>:  An AuthInfo instance from an auth provider. 

Raise: 
 - <b>`IdentityRetrievalFailed`</b>:  If the identifier is missing or there do exist multiple  in the saml response. 



**Returns:**
 
 - <b>`IdentityInfo`</b>:  An IdentityInfo instance containing identity information  or None if no identity was found. 

---

<a href="../flask_multipass_saml_groups/provider.py#L160"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_identity_groups`

```python
get_identity_groups(identifier: str) → Iterable[Group]
```

Retrieve the groups a user identity belongs to. 



**Args:**
 
 - <b>`identifier`</b>:  The unique user identifier used by the  provider. 



**Returns:**
 
 - <b>`iterable`</b>:  An iterable of groups 

---

<a href="../flask_multipass_saml_groups/provider.py#L143"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `search_groups`

```python
search_groups(name: str, exact: bool = False) → Iterable[Group]
```

Search groups by name. 



**Args:**
 
 - <b>`name`</b>:  The name to search for. 
 - <b>`exact`</b> (bool, optional):  If True, the name needs to match exactly,  i.e., no substring matches are performed. 



**Yields:**
 a matching group_class object. 


