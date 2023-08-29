<!-- markdownlint-disable -->

<a href="../flask_multipass_saml_groups/group_provider/sql.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `group_provider.sql`
A group provider that persists groups and their members in a SQL database provided by Indico. 



---

<a href="../flask_multipass_saml_groups/group_provider/sql.py#L16"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `SQLGroup`
A group whose group membership is persisted in a SQL database. 

Attrs:  supports_member_list (bool): If the group supports getting the list of members 

<a href="../flask_multipass_saml_groups/group_provider/sql.py#L25"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(provider: IdentityProvider, name: str)
```

Initialize the group. 



**Args:**
 
 - <b>`provider`</b>:  The associated identity provider. 
 - <b>`name`</b>:  The unique, case-sensitive name of this group. 




---

<a href="../flask_multipass_saml_groups/group_provider/sql.py#L36"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_members`

```python
get_members() → Iterator[IdentityInfo]
```

Return the members of the group. 



**Returns:**
  An iterator over IdentityInfo objects. 

---

<a href="../flask_multipass_saml_groups/group_provider/sql.py#L52"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `has_member`

```python
has_member(identifier: str) → bool
```

Check if a given identity is a member of the group. 



**Args:**
 
 - <b>`identifier`</b>:  The unique user identifier used by the provider. 



**Returns:**
 True if the user is a member of the group, False otherwise. 


---

<a href="../flask_multipass_saml_groups/group_provider/sql.py#L70"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `SQLGroupProvider`
Provide access to Groups persisted with a SQL database. 

Attrs:  group_class (class): The class to use for groups. 

<a href="../flask_multipass_saml_groups/group_provider/sql.py#L82"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(identity_provider: IdentityProvider)
```

Initialize the group provider. 



**Args:**
 
 - <b>`identity_provider`</b>:  The identity provider this group provider is associated with. 




---

<a href="../flask_multipass_saml_groups/group_provider/sql.py#L91"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `add_group`

```python
add_group(name: str) → None
```

Add a group. 



**Args:**
 
 - <b>`name`</b>:  The name of the group. 

---

<a href="../flask_multipass_saml_groups/group_provider/sql.py#L144"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `add_group_member`

```python
add_group_member(identifier: str, group_name: str) → None
```

Add a user to a group. 



**Args:**
 
 - <b>`identifier`</b>:  The unique user identifier used by the provider. 
 - <b>`group_name`</b>:  The name of the group. 

---

<a href="../flask_multipass_saml_groups/group_provider/sql.py#L102"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_group`

```python
get_group(name: str) → Optional[SQLGroup]
```

Get a group. 



**Args:**
 
 - <b>`name`</b>:  The name of the group. 



**Returns:**
 The group or None if it does not exist. 

---

<a href="../flask_multipass_saml_groups/group_provider/sql.py#L116"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_groups`

```python
get_groups() → Iterable[SQLGroup]
```

Get all groups. 



**Returns:**
  An iterable of all groups. 

---

<a href="../flask_multipass_saml_groups/group_provider/sql.py#L127"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_user_groups`

```python
get_user_groups(identifier: str) → Iterable[SQLGroup]
```

Get all groups a user is a member of. 



**Args:**
 
 - <b>`identifier`</b>:  The unique user identifier used by the provider. 



**Returns:**
 
 - <b>`iterable`</b>:  An iterable of groups the user is a member of. 

---

<a href="../flask_multipass_saml_groups/group_provider/sql.py#L165"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `remove_group_member`

```python
remove_group_member(identifier: str, group_name: str) → None
```

Remove a user from a group. 



**Args:**
 
 - <b>`identifier`</b>:  The unique user identifier used by the provider. 
 - <b>`group_name`</b>:  The name of the group. 


