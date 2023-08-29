<!-- markdownlint-disable -->

<a href="../flask_multipass_saml_groups/group_provider/base.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `group_provider.base`
Defines the interface for a group provider. 



---

<a href="../flask_multipass_saml_groups/group_provider/base.py#L11"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `GroupProvider`
A group provider is responsible for managing groups and their members. 

Attrs:  group_class (type): The class to use for groups. 

<a href="../flask_multipass_saml_groups/group_provider/base.py#L20"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(identity_provider: IdentityProvider)
```

Initialize the group provider. 



**Args:**
 
 - <b>`identity_provider`</b>:  The associated identity provider. Usually required because the group  needs to know the identity provider. 




---

<a href="../flask_multipass_saml_groups/group_provider/base.py#L28"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `add_group`

```python
add_group(name: str) → None
```

Add a group. 



**Args:**
 
 - <b>`name`</b>:  The name of the group. 

---

<a href="../flask_multipass_saml_groups/group_provider/base.py#L69"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `add_group_member`

```python
add_group_member(identifier: str, group_name: str) → None
```

Add a user to a group. 



**Args:**
 
 - <b>`identifier`</b>:  The unique user identifier used by the provider. 
 - <b>`group_name`</b>:  The name of the group. 

---

<a href="../flask_multipass_saml_groups/group_provider/base.py#L36"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_group`

```python
get_group(name: str) → Optional[Group]
```

Get a group. 



**Args:**
 
 - <b>`name`</b>:  The name of the group. 



**Returns:**
 The group or None if it does not exist. 

---

<a href="../flask_multipass_saml_groups/group_provider/base.py#L48"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_groups`

```python
get_groups() → Iterable[Group]
```

Get all groups. 



**Returns:**
  An iterable of all groups. 

---

<a href="../flask_multipass_saml_groups/group_provider/base.py#L57"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_user_groups`

```python
get_user_groups(identifier: str) → Iterable[Group]
```

Get all groups a user is a member of. 



**Args:**
 
 - <b>`identifier`</b>:  The unique user identifier used by the provider. 



**Returns:**
 
 - <b>`iterable`</b>:  An iterable of groups the user is a member of. 

---

<a href="../flask_multipass_saml_groups/group_provider/base.py#L78"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `remove_group_member`

```python
remove_group_member(identifier: str, group_name: str) → None
```

Remove a user from a group. 



**Args:**
 
 - <b>`identifier`</b>:  The unique user identifier used by the provider. 
 - <b>`group_name`</b>:  The name of the group. 


