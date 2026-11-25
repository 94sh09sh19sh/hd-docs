# 實作規格書 3.9 SQLite 連線與運作設定（取代原 Supabase 連線資訊）

上層文件：《[實作規格書](../../implementation-spec.md)》第 3 章

`.env` 由使用者填入，Agent 產生 `.env.example` 時保留空值，**不得寫入任何真實金鑰或路徑**：

```
DATABASE_URL=              # Prisma SQLite 連線字串，指向專案目錄外的本機檔案
SUPER_ADMIN_WORK_ID=
SUPER_ADMIN_INITIAL_PASSWORD=
LLM_PROVIDER=mock          # mock / lab / onprem
LLM_ENDPOINT=
LLM_API_KEY=
LLM_MODEL_ID=
BACKUP_DIR=                # 備份輸出目錄，須與資料庫檔案同機
```

**必須做到的事**（《資料庫使用規範》第 7、8 條）：

- 連線建立時套用四項 `PRAGMA`（見 2.1）
- 資料庫檔案放在**專案目錄外**，並確認已被 `.gitignore` 涵蓋
- 後端是唯一的常駐寫入行程；跑資料修補腳本前先停掉後端
- 統計與報表查詢走唯讀連線，不與臨床寫入競爭
- 備份用 SQLite 線上備份機制（`VACUUM INTO`），不用檔案複製；WAL 模式的 `-wal`／`-shm` 與主檔是一組

---

[← 回實作規格書](../../implementation-spec.md)　[← 回進度首頁](../../../index.md)
