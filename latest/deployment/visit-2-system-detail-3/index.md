# 第二次進院（1001）· 從零部署本系統之三：詳細版（N-13～N-18）

上層文件：[《第二次進院（1001）· 從零部署本系統》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-2-system/index.md)

> 狀態：**已照做 1001，凍結**（結果見[《第二次進院紀錄（1001，部分成功）》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/record-2-1001/index.md)）；1117 由舊的第十四冊改寫；編號與主文件相同（`N-xx`），每一步開頭的「對應」是沿用的原步驟（`W-xx`、`Y-xx`、`Z-xx` 在哪一份，見[《之一》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-2-system-detail/index.md)開頭）

## 摘要

- 第 5 節建置與啟動 N-13～N-16：建映像檔、建資料庫、啟動三個服務、用 health、日誌與登入確認它是對的
- N-16 的出錯表有 1001 卡住的「登入時轉圈後失敗」，逐步查法在《之六》的附錄
- 第 6 節 N-17 備份一次並證明還原得回來、N-18 重新開機測試（🏥 必做，🧪 可略）
- 🏥 改完初始密碼要交給院方指定的人保管
- N-12 以前在《之二》，N-19 起在《之四》

## 5. 建置與啟動

### N-13 建置映像檔

對應：W-13

**做什麼**

```
docker compose --env-file $cfg build
```

第一次約十分鐘，畫面會一直捲動，是正常的。

**怎麼知道成功了**：最後出現 `Image hd-tablet-care:<tag> Built`；再打 `docker images hd-tablet-care` 看得到這個 tag。

**可能怎麼壞**

| 症狀                                                           | 處置                                             |
| -------------------------------------------------------------- | ------------------------------------------------ |
| `failed to resolve source metadata for docker.io/library/node` | 連不到 Docker Hub，回 N-06                       |
| `npm error code ETIMEDOUT` 或 `ECONNRESET`                     | 網路不穩，再打一次同一條指令；已下載的部分會沿用 |
| `pull access denied for hd-tablet-care`                        | 打成 `up` 了。先 `build`                         |

______________________________________________________________________

### N-14 建立資料庫

對應：W-14

**做什麼**（一整行，不要斷開）

```
docker compose --env-file $cfg run --rm --no-deps api node apps/api/scripts/prisma-cli.mjs migrate deploy --schema apps/api/prisma/schema.prisma
```

**怎麼知道成功了**：中間出現 `SQLite database hd.db created at file:/data/hd.db`（第一次才會有），最後一行 `All migrations have been successfully applied.`

**可能怎麼壞**：錯誤訊息裡提到 `binaries.prisma.sh` → 映像檔建壞了，回 N-13 重建。**不要為了讓它下載而開任何網路例外。**

______________________________________________________________________

### N-15 啟動

對應：W-15

**做什麼**

```
docker compose --env-file $cfg up -d
docker compose --env-file $cfg ps
```

**怎麼知道成功了**：`api`、`nurse-web`、`patient-web` 三個的狀態都是 `Up`。`ai-gateway` 與 `shell-builder` **不在清單上是對的**，它們平時不跑。

**可能怎麼壞**

| 症狀                              | 處置                                                                                                                 |
| --------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `api` 一直是 `Restarting`         | 設定被後端拒絕。`docker compose --env-file $cfg logs api --tail 30` 最後幾行會寫是哪一條，照訊息改 `.env` 再 `up -d` |
| `address already in use`          | 埠被佔了，回 N-07                                                                                                    |
| `bind source path does not exist` | `HD_BACKUP_DIR` 或 `HD_CONFIG_DIR` 指的資料夾不存在，回 N-08                                                         |

______________________________________________________________________

### N-16 確認它是對的

對應：W-16

**做什麼**（`<後端埠>` 換成你的，就是 `.env` 的 `HD_API_PORT`；🏥 與 🧪 都是 `13000`，紀錄 M-08）

```
curl.exe -s http://localhost:<後端埠>/api/health
docker compose --env-file $cfg logs api --tail 30
```

然後用瀏覽器開護理端：🏥 在**護理站的電腦**開 `http://<主機名稱>:<護理端埠>`；🧪 在開發機開 `http://localhost:18080`。

**怎麼知道成功了**

| 看什麼                        | 應該是                                                                                                  |
| ----------------------------- | ------------------------------------------------------------------------------------------------------- |
| health                        | `{"status":"ok",…}` 開頭                                                                                |
| 日誌「已連線至 SQLite」那一行 | 有 `synchronous=FULL`                                                                                   |
| 日誌「版本標記」那一行        | 後面寫著 `（正式環境設定）`——🧪 也是這樣，**這是對的**                                                  |
| 日誌「伺服器時區」            | `Asia/Taipei`，而且時間是現在                                                                           |
| 瀏覽器                        | 出現登入頁；用 `.env` 的 `SUPER_ADMIN_WORK_ID` 與 `SUPER_ADMIN_INITIAL_PASSWORD` 登入，**被要求改密碼** |

**可能怎麼壞**

| 症狀                                   | 處置                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| -------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 頁面開得了，登入時轉圈後失敗           | `.env` 的 `HD_PUBLIC_API_URL` 或 `CORS_ORIGINS` 寫錯。改完：前者要 `build` 再 `up -d`（它寫在網頁檔案裡），後者只要 `up -d`。逐步查法見[附錄：護理端頁面開得起來卻登不進去](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-2-system-detail-6/#%E9%99%84%E9%8C%84%E8%AD%B7%E7%90%86%E7%AB%AF%E9%A0%81%E9%9D%A2%E9%96%8B%E5%BE%97%E8%B5%B7%E4%BE%86%E5%8D%BB%E7%99%BB%E4%B8%8D%E9%80%B2%E5%8E%BB)（1001 就卡在這裡，見[《第二次進院紀錄（1001）之一：為什麼登不進去》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/record-2-1001-login/index.md)） |
| 沒有帳號可以登入                       | `SUPER_ADMIN_*` 沒填。補上再 `up -d`，**資料庫不必重建**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| 護理站的電腦開不到頁面，主機自己開得到 | 防火牆或網段，找資訊室（Q-27）。**不要自己關防火牆**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |

🏥 改完密碼之後，要把新密碼交給院方指定的人保管，`.env` 裡的初始密碼可以清空（清空後 `up -d`）。

______________________________________________________________________

## 6. 備份與重新開機

### N-17 備份一次，並證明還原得回來

對應：W-17

「有備份」和「備份能用」是兩件事。

**做什麼**

1. 護理端 → **系統管理** → 「立即備份」，記下畫面上的檔名。備份歷程的 SHA-256 只顯示前 12 碼；完整的 64 碼到備份資料夾讀同名的 `.sha256` 檔：

```
Get-Content "$root\backups\<檔名>.sha256"
```

前半段就是雜湊。護理端 **稽核軌跡**（動作選「資料庫線上備份」）的說明欄也有完整的一份。 2. 把它還原到一個測試檔，確認完整，再刪掉測試檔（`<檔名>`、`<雜湊>` 換成剛剛記下的）：

```
docker compose --env-file $cfg run --rm --no-deps api node_modules/.bin/ts-node --project apps/api/tsconfig.json apps/api/scripts/restore-backup.ts --from /backups/<檔名> --to /data/restore-check.db --sha256 <雜湊>
docker compose --env-file $cfg run --rm --no-deps --entrypoint rm api /data/restore-check.db
```

**怎麼知道成功了**：輸出有 `✓ 與備份歷程上的紀錄相符` 與 `完整性檢查：ok`；`$root\backups\` 裡看得到那個檔和同名的 `.sha256`。

💡 **服務起不來時**：備份歷程與稽核軌跡都存在資料庫裡，打不開網頁就看不到。這時直接看資料夾：`Get-ChildItem "$root\backups\*.db" | Sort-Object LastWriteTime` 最後一個是最新的備份，雜湊在它旁邊的 `.sha256`。送往院內另一台機器時，`.sha256` 要跟著一起送。

🏥 還要**當場問清楚**：備份資料夾的內容由誰、多久送往院內另一台機器一次？答不出來就寫進交接文件的「已知限制」。

> ⚠️ **這一步一律用 PowerShell。** 在 Git Bash 裡打，`/backups/…` 會被自動改寫成 Windows 路徑，還原腳本就說找不到檔案。

🧪 做到還原成功即可，不必送往任何地方。

______________________________________________________________________

### N-18 重新開機測試

對應：W-18

`restart: unless-stopped` 只管 Docker 起來之後；Docker Desktop 要有人登入 Windows 才會啟動。**這一條決定這條路線在院內能不能用。**

**做什麼**：重新開機 → 照院方平常的方式登入（或不登入，看 N-02 的答覆）→ 等三分鐘 → 開一個新的 PowerShell，先輸入開工三行，再：

```
docker compose --env-file $cfg ps
curl.exe -s http://localhost:<後端埠>/api/health
```

**怎麼知道成功了**：三個服務自己回到 `Up`、health 正常，**中間沒有人手動開 Docker Desktop**。

**沒過的話**：記下實況（有沒有自動登入、Docker Desktop 有沒有起來），寫進交接文件，**不要在現場自己改院方的登入設定**。

🧪 可以跳過。開發機是你自己登入的，驗不出院內「沒人登入」的情形。

______________________________________________________________________

上一份：[《第二次進院（1001）· 從零部署本系統之二：詳細版（N-08～N-12）》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-2-system-detail-2/index.md)｜下一份：[《第二次進院（1001）· 從零部署本系統之四：詳細版（N-19～N-27）》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-2-system-detail-4/index.md)

## 版本歷程

| 定版 | 日期 | 異動 |
| ---- | ---- | ---- |
|      |      |      |

[← 回部署手冊目錄](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/index.md)
