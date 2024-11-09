# cloud_final_project
Advanced cloud computing - Final Poject

User/Application → Gatekeeper (validates request)
Gatekeeper → Trusted Host (internal processing)
Trusted Host → Proxy (routes request)
Proxy → Manager/Worker Node (handles read/write operation)
Response travels back: Worker/Manager → Proxy → Trusted Host → Gatekeeper → User/Application



# TODO NOTES

REMOVE GUNICORN FROM APIS!!!


## Improve util functions:
* Remove / Combine unnecessary functions --> Make them general

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
1. Se till att data flöder User --> Proxy --> User
2. Skapa 3 olika patterns (api paths) i proxy + se till att user kan skicka till respektive pattern och det hittar rätt
3. koppla proxy till databaserna --> Behöver DB en API? eller kan Proxyn sköta detta?
4. Skapa korrekta cloud patterns
5. Gör instanserna private (förutom gatekeeper) och se om det funkar