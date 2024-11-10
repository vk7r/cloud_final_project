# cloud_final_project
Advanced cloud computing - Final Poject

User/Application → Gatekeeper (validates request)
Gatekeeper → Trusted Host (internal processing)
Trusted Host → Proxy (routes request)
Proxy → Manager/Worker Node (handles read/write operation)
Response travels back: Worker/Manager → Proxy → Trusted Host → Gatekeeper → User/Application


# Expected User Responses

### What The User Sends
The user should send the following:
- operation: "READ" or "WRITE" based on the type of request
- query: The SQL query to be executed

eg:

{
    "operation": "READ",
    "query": "SELECT * FROM sakila.actor"
}

### SUCCESSFUL WRITE OPERAION:
{
    "status": "success",
    "message": "Record inserted successfully",
    "affected_rows": 1
}

### SUCCESSFUL READ OPERATION:
{
    "status": "error",
    "error": "Syntax error in SQL query",
    "details": "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version"
}



# TODO NOTES

REMOVE GUNICORN FROM APIS!!!


## Improve util functions:
* Remove / Combine unnecessary functions --> Make them general
* Fix repititions. eg. function for trusted request in gatekeeper API
* Extend the instance_ips.json? --> Each instances port that API runs on, public ip? more?

## Make global variables and improved names
* Globals: Usernamne, Password, instance names, etc
* rename gateway to gatekeepet (correct?)
* better names and keep it in the same standard (snakecase?)

## Fix file structure
* Better names
* Combine similar files
* Separate code from files that might not fit in with eachother
* New folders --> Test?

## TODO IN CODE
1. Se till att data flöder User --> Proxy --> User [KLAR]
2. Skapa 3 olika patterns (api paths) i proxy + se till att user kan skicka till respektive pattern och det hittar rätt
3. koppla proxy till databaserna --> Behöver DB en API? eller kan Proxyn sköta detta?
4. Skapa korrekta cloud patterns
5. Gör instanserna private (förutom gatekeeper) och se om det funkar