# R1L_RTM 資料庫設置指南

## 🚀 快速開始

### 方法 1: 完整自動化匯入（推薦）

```bash
cd /home/sqa_server/apps/R1L_RTM/backend

# 步驟 1: 重置資料庫（清除舊資料）
python reset_database.py

# 步驟 2: 匯入所有資料
python import_all_data.py
```

### 方法 2: 手動逐步匯入

```bash
cd /home/sqa_server/apps/R1L_RTM/backend

# 步驟 1: 重置資料庫
python3 reset_database.py

# 步驟 2: 匯入 CFTS 資料
python3 batch_import_cfts_new.py ../data/CFTS

# 步驟 3: 匯入 SYS.2 資料
python3 batch_import_sys2.py ../data/R1L_SYS.2.xlsx

# 步驟 4: 匯入 TestCase 資料
python3 batch_import_testcase.py ../data/R1L_TestCase.xlsx
```

---

## 📋 工具說明

### 1. reset_database.py - 資料庫重置工具

**功能：**
- 刪除所有現有資料表
- 使用最新的資料結構重建資料表
- 確保資料庫處於乾淨狀態

**使用時機：**
- ⚠️ **首次匯入前必須執行**
- 資料結構已更改
- 需要完全重新匯入資料
- 資料庫出現不一致的問題

**執行流程：**
1. 顯示目前資料庫狀態
2. 要求雙重確認（避免誤刪）
3. 刪除所有資料表
4. 重建資料表結構
5. 顯示重置摘要

**安全機制：**
- 需要輸入 `yes` 確認
- 需要輸入 `DELETE ALL DATA` 二次確認
- 顯示將被刪除的記錄數

```bash
python reset_database.py
```

---

### 2. import_all_data.py - 完整資料匯入工具

**功能：**
- 自動驗證所有資料檔案
- 按正確順序匯入所有資料
- 提供完整的匯入報告

**匯入順序：**
1. CFTS Requirements
2. SYS.2 Requirements
3. TestCases

**執行流程：**
1. 驗證資料檔案存在
2. 顯示檔案資訊
3. 要求確認
4. 依序匯入三個資料集
5. 顯示最終摘要

```bash
python import_all_data.py
```

**優點：**
- 一鍵完成所有匯入
- 自動錯誤檢測
- 完整的進度追蹤

---

### 3. 個別匯入工具

#### batch_import_cfts_new.py
```bash
python batch_import_cfts_new.py ../data/CFTS
```

**支援的檔案格式：**
- `CFTS###_描述_SR26.xlsx`
- `SYS1_CFTS###_描述_SR26.xlsx`

**處理方式：**
- 檢查 `req_id`，存在則更新，不存在則新增
- 預期匯入約 5,000+ 筆記錄

#### batch_import_sys2.py
```bash
python batch_import_sys2.py ../data/R1L_SYS.2.xlsx
```

**支援的欄位名稱：**
- 英文：`Melco Id`, `Requirement`, `Reason`, `Supplementary`, etc.
- 日文：`要件ID`, `要件(英語)`, `理由(英語)`, `補足(英語)`, etc.

**處理方式：**
- 檢查 `melco_id`，存在則更新，不存在則新增
- 自動從 `melco_id` 提取 `cfts_id`
- 預期匯入約 14,683 筆記錄

#### batch_import_testcase.py
```bash
python batch_import_testcase.py ../data/R1L_TestCase.xlsx
```

**處理方式：**
- 直接新增所有記錄（不檢查重複）
- **⚠️ 重複執行會產生重複資料**
- 預期匯入約 34,457 筆記錄

---

## ⚠️ 重要注意事項

### 為什麼需要重置資料庫？

#### 1. TestCase 會產生重複資料
- `batch_import_testcase.py` 不檢查重複
- 每次執行都會新增所有記錄
- **必須先清除舊資料**

#### 2. 資料結構已更改
- SYS.2 欄位從日文改為英文
- 檔案命名規則已變更
- 確保使用最新的資料結構

#### 3. 避免孤立記錄
- 舊檔案中的記錄可能在新檔案中已移除
- 清除舊資料確保資料一致性

---

## 📊 資料驗證

### 匯入後檢查

```bash
# 在 Python 中執行
from app.db.database import SessionLocal
from app.models.cfts_db import CFTSRequirementDB
from app.models.sys2_requirement import SYS2RequirementDB
from app.models.testcase import TestCaseDB

db = SessionLocal()

# 檢查記錄數
cfts_count = db.query(CFTSRequirementDB).count()
sys2_count = db.query(SYS2RequirementDB).count()
testcase_count = db.query(TestCaseDB).count()

print(f"CFTS: {cfts_count:,} records")
print(f"SYS.2: {sys2_count:,} records")
print(f"TestCases: {testcase_count:,} records")

db.close()
```

### 預期結果
- CFTS Requirements: ~5,000+ 筆
- SYS.2 Requirements: ~14,683 筆
- TestCases: ~34,457 筆

---

## 🔧 常見問題排除

### 問題 1: 資料庫連線錯誤
```
Error: could not connect to server
```

**解決方法：**
1. 檢查 PostgreSQL 是否運行
2. 檢查 `app/config.py` 中的資料庫設定
3. 確認資料庫用戶權限

### 問題 2: 檔案找不到
```
Error: ../data/CFTS is not a valid directory
```

**解決方法：**
1. 確認在 `backend` 目錄中執行
2. 檢查資料檔案路徑是否正確
3. 確認檔案名稱正確

### 問題 3: Excel 讀取錯誤
```
Error: No such file or directory: 'R1L_SYS.2.xlsx'
```

**解決方法：**
1. 確認檔案存在於 `data` 目錄
2. 檢查檔案名稱是否完全一致（區分大小寫）
3. 確認檔案格式為 `.xlsx`

### 問題 4: 重複資料
```
大量重複的 TestCase 記錄
```

**解決方法：**
1. 執行 `python reset_database.py`
2. 重新匯入資料

---

## 📁 資料檔案要求

### 檔案結構
```
/home/sqa_server/apps/R1L_RTM/data/
├── CFTS/
│   ├── SYS1_CFTS004_General Diagnostic Requirements_SR26.xlsx
│   ├── SYS1_CFTS009_Wake-up and Power-up_SR26.xlsx
│   ├── ...（共 31 個檔案）
│   └── SYS1_CFTS092_Radio Camera Management_SR26.xlsx
├── R1L_SYS.2.xlsx
└── R1L_TestCase.xlsx
```

### CFTS 檔案要求
- **格式：** `.xlsx`
- **命名：** `SYS1_CFTS###_描述_SR26.xlsx` 或 `CFTS###_描述_SR26.xlsx`
- **必要欄位：**
  - ReqIF.ForeignID
  - Source Id
  - Melco Id
  - SR26 Description
  - SR24 Description

### SYS.2 檔案要求
- **檔名：** `R1L_SYS.2.xlsx`
- **格式：** `.xlsx`
- **必要欄位（英文或日文）：**
  - Melco Id / 要件ID
  - Requirement / 要件(英語)
  - Reason / 理由(英語)
  - Supplementary / 補足(英語)
  - Verification Phase / 確認フェーズ
  - Verification Criteria / 検証基準
  - Type / 種別
  - Related Requirement ID / 関連要件ID
  - (R1L_SR21CFTS), (R1L_SR22CFTS), (R1L_SR23CFTS), (R1L_SR24CFTS)

### TestCase 檔案要求
- **檔名：** `R1L_TestCase.xlsx`
- **格式：** `.xlsx`
- **必要欄位：**
  - Feature-ID（對應 Melco ID）
  - Source, Title, Section
  - TestItem(EN)
  - Precondition/Procedure(JP)
  - Criteria(JP)
  - 其他欄位：MP, DS, DT, HDCC, RU, Specification, Priority, Test Version, Test Result, Tester, Issue ID, Note

---

## 🎯 完整工作流程

### 初次設置
```bash
# 1. 進入 backend 目錄
cd /home/sqa_server/apps/R1L_RTM/backend

# 2. 安裝相依套件
pip install -r requirements.txt

# 3. 重置資料庫
python reset_database.py

# 4. 匯入所有資料
python import_all_data.py

# 5. 啟動後端服務
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 資料更新
```bash
# 1. 備份現有資料（可選）
# pg_dump your_database > backup.sql

# 2. 重置資料庫
python reset_database.py

# 3. 匯入新資料
python import_all_data.py
```

---

## 📚 相關文件

- [DATA_RELATIONSHIP.md](./DATA_RELATIONSHIP.md) - 資料連動關係說明
- [backend/README.md](./backend/README.md) - 後端設置說明
- [frontend/README.md](./frontend/README.md) - 前端設置說明

---

## 📝 更新記錄

### 2025-10-22
- 建立資料庫重置工具 (`reset_database.py`)
- 建立完整匯入工具 (`import_all_data.py`)
- 更新 SYS.2 匯入支援單一檔案和英文欄位
- 更新 CFTS 匯入支援新的檔案命名格式
- 建立完整的設置文件
