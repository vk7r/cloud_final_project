# cloud_final_project
Advanced cloud computing - Final Poject

User/Application → Gatekeeper (validates request)
Gatekeeper → Trusted Host (internal processing)
Trusted Host → Proxy (routes request)
Proxy → Manager/Worker Node (handles read/write operation)
Response travels back: Worker/Manager → Proxy → Trusted Host → Gatekeeper → User/Application