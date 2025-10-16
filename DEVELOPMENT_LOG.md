# Development Log

## 2025-09-10 - 2025-09-12
- FastAPI backend + Vue.js frontend structure
- Docker configuration and PostgreSQL setup
- API modules, data models, CRUD endpoints

## 2025-10-05
- FastAPI + Vue.js + PostgreSQL project structure
- Batch import with MD Scope filtering (only imports records where Scope = "Yes")
- CFTS ID and Req.ID search functionality with autocomplete APIs
- Containerized deployment configuration
- Retro-tech styled search interface with Chinese UI
- Batch import from 32 Excel files with deduplication based on req_id

## 2025-10-06
- Extract CFTS number from Excel filenames
- Re-imported data with correct CFTS classification - 31 CFTS groups with 9,111 total requirements
- CFTS ID dropdown now displays all 31 CFTS options from database
- Added column to store Polarion hyperlinks from Excel files
- Extract hyperlinks from Excel A column (Polarian ID)
- Req.ID search now shows full CFTS list instead of single row
- Simple yellow highlight with orange left border for target row
- Auto-scroll to target requirement and center it in view

## 2025-10-14
- Migrated database from SQLite to PostgreSQL
- Added SYS2 data integration with sys2_scope and melco_id fields
- Integrated CFTS021and CFTS085 with SYS2 data
- Implemented Scope display with SW highlighted in red bold text on yellow background
- Updated frontend to color scheme for better readability
- Docker services fully operational with PostgreSQL backend