# DBServer

A simple database i use for my projects to store/load any kind of bytes data.<br/>
**Example:**
  * server configurations
  * cache stuff
  * ...

## Getting Started

### Install:
Install with `pip`
```bash
pip install --user git+https://github.com/KnacKWursTKinG/dbserver.git
```
or
```bash
git clone https://github.com/KnacKWursTKinG/dbserver.git
cd dbserver
pip install --user .
```

### Authorization
The flask server needs some authorization from the client,<br/>
just set a environment variable named `DBAUTH`

> Needed for the [client](cli/sdbcli) and the dbserver.

```bash
export DBAUTH="username:password"
```

> see [Headers](#headers)


# Routes
> @TODO: DELETE and PUT for /db/\<group\>/\<label\>

Type | Route | Description | Headers<br/>Client | Headers<br/>Server
----|----|----|:--:|:--:
GET | /db | List groups | 1 | 3
GET | /db/\<group\> | List labels inside \<group\> | 1 | 3
DELETE | /db/\<group\> | Delete a group | 1 | 3
GET | /db/\<group\>/\<label\> | Get data from a label inside \<group\> | 1 | 2 or 3 if error
POST | /db/\<group\>/\<label\> | Post data and create the label and inside a group<br/>creating the group in not exist | 1, 2 | 3

<a name="headers"></a>
## Headers

Nr. | Headers | Note
--|---------|-----
1 | Authorization: `"Basic {}".format(base64.b64encode("<user>:<password>"))`<br/>the client [sdbcli](cli/sdbcli) reads from env var 'DBAUTH' (`export DBAUTH="<user>:<pass>"`)
2 | Content-Type: "data/bytes"
3 | Content-Type: "application/json" | for a server return:<br/>`{"error": None or str(), "data": None or Any}`
