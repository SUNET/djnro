# REST API

## Authentication

All endpoints are protected using "Token Authentication". This means
that every request must contain a valid token (associated with a known user account) in the HTTP Authorization header,
for example:

```
Authorization: Token jAvfRQY6tVxkhyjz
```

An administrator can issue tokens for a user with the included management command `gettoken`. For example:

```
python manage.py gettoken user1
```



## Endpoints
| Resource | Method | Description |
| -------- | ------ | ------------|
| /institution | GET | Returns the users institution. The result will be limited to the institution that the user ismember of. |
| /institution/\<id\> | GET | Returns a detailed result of a specific institution. |
| /location | GET | Returns the users locations. The result will be limited to locations that are connected to one of the users institutions. |
| /location/\<id\> | GET | Returns a detailed result of a specific location. |
| /location | POST | Create a new location with the supplied JSON data. |

### Creating a new location

When submitting a new location, it will automatically be associated with the institution of the user identified by the
authentication token. The following parameters are required:

* AP_no
* SSID
* address_street
* address_city
* latitude
* longitude
* NAT
* IPv6
* wired
* port_restrict
* transp_proxy

All possible parameters are described in the `service_loc` table of the
[eduroam-database model](https://monitor.eduroam.org/fact_eduroam_db.php).
