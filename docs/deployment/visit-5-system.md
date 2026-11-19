# 第五次進院（1116）任務二 · 本系統換版上線

> **狀態：已照做 1116，凍結。** 結果：B 級、技術面全通（換版 `v0.5.0`、讀檔上線、第一輪對得上；平板到床、密碼移交、重新開機、交接沒做），見《[第五次進院紀錄（1116，讀檔上線、平板與交接待補）](record-5-1116.md)》。這一份不再改；院內主機現在的樣子與沒做完的步驟由《[院內主機現況與未完成事項](ref-status.md)》追蹤（下面第 0.1 節）。
>
> **從哪幾份舊冊改寫（1117）**：第二十三冊（本系統換版上線簡易版）全部；它的附錄一（退回 `v0.4.0`）改連《[本系統換版與退回](ref-upgrade.md)》、附錄二（停用讀檔）改連《[讀檔：啟用、檢查、停用](ref-dialysis-files.md)》；第十七冊第 0.6 節（1116 開發機演練）的差異收成這裡的 🧪 行，開發機的起點寫在詳細版第 1.6 節。
>
> **編號**：`SY-01`～`SY-15`，開發機才做的 `SY-M1`～`SY-M4`；子文件用同一套編號。

主文件分兩份（1118 拆檔，編號與節號不變）：

- 這一份：第 0 節開始前、SY-01～SY-07（出發前、到場先看、換到新版）
- 《[第 2 份](visit-5-system-2.md)》：SY-08～SY-15（啟用讀檔、首波上線、收尾）、第 6 節 🧪 開發機才做的 SY-M1～SY-M4、第 7 節出問題時

子文件：

- 《[之一：詳細版（讀之前、SY-01～SY-07）](visit-5-system-detail.md)》：停手條件、時間、要帶的東西、🧪 1116 開發機的起點；SY-01～SY-07 的出錯處置與為什麼
- 《[之二：詳細版（SY-08～SY-15、SY-M1～SY-M4、舊第二十冊對照）](visit-5-system-detail-2.md)》：SY-08 起每一步的出錯處置與為什麼、舊第二十冊 `GO-xx` 與 `SY-xx` 的對照
- 《[之三：上線準備清單（A-xx）](visit-5-system-prep.md)》：出發前要拿到的答案、開發端要先做完的事、床號的結論、第 11 章 26 條對現況

> **第二階段**：第一階段《[第五次進院（1116）任務一 · 抓取腳本上線](visit-5-api.md)》AF-11 三輪都成功了才做這一份；沒成功，本系統不換版。
>
> 標記：**🏥**＝院內正式主機才這樣做；**🧪**＝開發機演練才這樣做；沒標的兩邊一樣。**🧪 全程通過，`<新 tag>` 才准帶進院**（1116 帶的是 `v0.5.0`，commit `8575505`）。

> **公開範圍**：一律用代稱。值只寫在印出來的演練紀錄空白表與私人 repo 的 `deploy/records/`。可以拍照，照片只進私人 repo；`.env` 的內容、密碼、病人資料的畫面不拍。**代稱連同 `<`、`>` 一起換掉。**

## 摘要

- 這一份是索引，涵蓋第 0 節與 SY-01～SY-07；SY-08 起在《[第 2 份](visit-5-system-2.md)》
- 換版 `v0.4.0` → `<新 tag>`（1116 是 `v0.5.0`）：3 個只做加法的遷移；`.env` 多四行先留空；外殼不換、APK 不重建
- 順序：看現況 → 防毒 → 換版、確認、備份還原 → 重新開機 → 密碼移交 → 啟用讀檔、第一輪驗 → 平板 → 冒煙測試 → 交接
- 🏥 首波還沒開始用，不必避開透析（DEP-32 1116 例外），挑護理師不忙的時候；資訊室同仁、學長、護理長在場；約 4～5 小時（不含第一階段）
- 1116 實際做到 SY-11，SY-12、SY-13 做一部分；沒做完的列在第 0.1 節

## 0. 開始前

### 0.1 1116 沒做完的步驟（現在由《院內主機現況與未完成事項》追蹤）

| 步驟 | 1116 | 之後 |
|---|---|---|
| SY-02 Docker 使用統計 | 沒看 | 下次有人在主機上時看一眼 |
| SY-03 防毒排除 | 沒加（資訊室沒來） | 使用者決定：不加也能跑，出現詳細版 SY-03 那幾種現象再請資訊室加 |
| SY-05 功能開關 | 「本次透析」面板沒關（使用者判斷之後馬上要開），遊戲化關了 | 首波那一位指派之前先確認他不在目標脫水量被擋的那 3 次裡，或先關掉、SY-12 對過再開 |
| SY-06 第 3 項 | 備份送往另一台機器沒問 | 院外問資訊室 |
| SY-07 重新開機 | 沒做（同機有另一個專案，沒問院方） | 交接寫「未驗」；斷電後服務會不會自己回來仍沒實測 |
| SY-08 密碼移交 | 護理長不在，沒移交；建帳號不做（使用者決定維持一個管理者帳號） | 院外：護理長改管理者密碼、收平板 PIN |
| SY-12 平板 | 部分：`TB-00` 已註冊、固定中，留在醫師桌上，沒放到床、沒指派病人 | 院方（醫師、護理長）照 SY-12 第 1～5 項做，不需要開發端在場 |
| SY-13 冒煙測試 | 第 1～5 列 ✓，第 6～9 列沒做 | 跟交接一起補 |
| SY-14 交接 | 沒做 | 院外：交接紙與教學；開會問醫師要現場還是影片 |
| SY-15 | 沒留到第一個班次；同步卡離院前仍每 3 分鐘更新 | — |

以上的現況與誰補，以《[院內主機現況與未完成事項](ref-status.md)》為準；這一張是 1116 離院時的快照。

### 0.2 代稱

| 代稱 | 指的是 |
|---|---|
| `<IP>` | 🏥 院內主機的固定 IP（1029 換上的那一個）；🧪 開發機那張網卡的 IPv4（開發端給） |
| `<新 tag>` | 這一次要換上去的版本，出發前打好、照這一份的 🧪 整輪演練過；1116 是 `v0.5.0` |
| `$root`、`$cfg` | 開工三行設的根目錄與設定檔（SY-02） |
| `<指定資料夾>`（舊第二十冊用過） | 抓取腳本寫 `YYYY-MM.txt` 的資料夾；1114 起搬到 C 槽，1116 起固定是 `C:\API_Fetch\IDH_interface`，這一份直接寫路徑 |

### 0.3 兩邊的差別一覽

| 哪裡 | 🏥 院內正式主機 | 🧪 開發機演練 |
|---|---|---|
| 起點 | 1029 離院時的主機（`v0.4.0`、位址用 IP、登得進去、平板佈建好） | 開發端先把開發機準備成跟院內主機一樣，演練完也由開發端撤除；手冊不寫怎麼準備（詳細版第 1.6 節記 1116 那一輪的起點） |
| 根目錄 `$root` | `C:\hd\hd-tablet-care` | `C:\hd-sim` |
| `<IP>` | 院內主機的固定 IP | 開發機網卡的 IPv4（開發端給） |
| 護理站的電腦 | 護理站那台（要 Windows 密碼、會休眠，請護理師輸入） | 連同一個網路的手機瀏覽器；沒有 Ctrl＋F5，改成關掉分頁重開 |
| 平板 | `TB-00`，1029 已佈建 | 開發端佈建好的手機或暫用平板 |
| 管理者帳號 | 院內那一個 | `sim-admin`（密碼開發端給） |
| 資訊室、護理長、學長 | 在場 | 自己；要問他們的事跳過，紀錄寫「院內要問」 |
| 院方資料 | 第一階段抓取腳本寫的 `C:\API_Fetch\IDH_interface` | 模擬院方資料（SY-10 B1、B2） |
| 第一階段 | 當天先做《任務一》 | 抓取腳本照《任務一》的 🧪 另外演練，不在這一份 |
| 防毒、Docker 設定 | 請資訊室改 | 只看不改 |
| 重新開機 | 院方准才做，真的重開 | Quit Docker Desktop 再開 |
| 只有開發機才做 | — | SY-M1～SY-M4（第 6 節） |

## 1. 出發前

### SY-01 確認 tag、答案、人與時段

**做什麼**：

1. `<新 tag>` 已推上 GitHub，而且照這一份的 🧪 整輪演練過、SY-M4 判定通過
2. 病人告知（A-03）有答案，才可能做到 SY-10。防毒排除（A-01）1116 起不擋讀檔：當天請資訊室加，加不了寫進交接紙
3. 約到學長、一位有管理員權限的資訊室同仁、護理長；時段挑護理師不忙的時候（首波還沒開始用，透析時段也可以，DEP-32 1116 例外）
4. 印好：這一份、《[交接紙](ref-status-handover.md)》、演練紀錄空白表

🧪 這一輪本身就是那次演練，第 1 項跳過；第 3 項不約人。

**成功**：紀錄寫下 `<新 tag>`、它的 commit、演練判定的日期、約好的時段與在場的人。

## 2. 到場：先看

### SY-02 開工三行、看主機現況

**做什麼**：系統管理員身分的 PowerShell：

```powershell
$root = "C:\hd\hd-tablet-care"
$cfg  = "$root\config\.env"
cd $root\repo
git describe --tags
docker ps --format "{{.Names}}  {{.Image}}  {{.Status}}"
Get-ChildItem $root\backups\keys
Get-PSDrive C
```

🧪 第一行改成 `$root = "C:\hd-sim"`。

再開 Docker Desktop → Settings → General，看「Send usage statistics」有沒有勾。🏥 勾著就取消、Apply。🧪 只看。

**成功**：`v0.4.0`；本系統四個服務（含 `ai-gateway`）都是 `v0.4.0`、`Up`；抄下 `backups\keys` 的金鑰備份檔名與 C 槽剩多少；使用統計沒勾。🏥 `Up` 的時間比 1029 到今天短就是中間重開過機，記下來。

> PowerShell 重開後，先打這裡的前三行（開工三行）。

### SY-03 防毒排除

**做什麼**：系統管理員身分的 PowerShell：

```powershell
Get-MpPreference | Select-Object -ExpandProperty ExclusionPath
```

🏥 請資訊室把 Docker 的資料夾（Docker Desktop → Settings → Resources → Advanced → Disk image location 那個路徑）加進排除清單，加完再打一次。當天加不了也照樣往下（1116 定），紀錄寫「未加」，交接紙「防毒」那一列照抄詳細版 SY-03 的現象。

🧪 只看，不加。

**成功**：🏥 第二次看得到那個路徑；紀錄寫「排除清單已加，由＿＿加」，或寫「未加」。🧪 指令跑得動就好。

## 3. 換到新版

> 🏥 先跟護理站講一聲：換版與啟用時護理端會斷線一兩分鐘；首波還沒開始用，透析時段也可以做（DEP-32 1116 例外）。換版後第一個班次要有人在。

### SY-04 下載、補 `.env`、建置、更新資料庫

**做什麼**：

1. 下載新版：

   ```powershell
   git fetch --tags
   git checkout <新 tag>
   git describe --tags
   ```

2. `notepad $cfg`：`HD_IMAGE_TAG` 改成 `<新 tag>`；補下面四行，**都先留空**。**只貼這四行，不要整段複製範本**；貼在 `# --- 院方透析清單 API` 那一段的**上面**（跟範本同樣的位置），`HOSPITAL_API_BASE_URL`、`HD_SIMULATION_DEPLOYMENT` 已經有了，不要再貼一次：

   ```
   HD_DIALYSIS_LIST_DIR=
   HD_LAB_DIR=
   # COMPOSE_FILE=docker-compose.yml;docker-compose.dialysis-files.yml
   HOSPITAL_LAB_FIELD_MAP=
   ```

   🏥 找不到 `# --- 院方透析清單 API` 那一段（主機的 `.env` 是更早的範本建的，1116 現場遇到）：貼在 `# --- 其他營運參數` 那一行的上面，那兩個變數也不用補。

   `HOSPITAL_API_BASE_URL` 維持空白。🧪 `HD_SHELL_SIGNING=dev`、`HD_SIMULATION_DEPLOYMENT` 照開發端填的，不動。

   存檔後打 `docker compose --env-file $cfg config --quiet`，什麼都沒印才往下。

3. 建置：

   ```powershell
   docker compose --env-file $cfg build
   docker images hd-tablet-care
   ```

4. 停後端、更新資料庫（第三行是一整行）：

   ```powershell
   $tag = git describe --tags
   docker compose --env-file $cfg stop api
   docker compose --env-file $cfg run --rm --no-deps api node apps/api/scripts/db-update.mjs --note "v0.4.0 → $($tag)（第五次進院）"
   ```

**成功**：`git describe` 正好是 `<新 tag>`、後面沒有尾巴；建置看到 `Built`；`docker images` 有 `v0.4.0` 與 `<新 tag>` 兩個（`v0.4.0` 不要刪）；最後印出「**更新完成。接下來的三件事是人要做的**」。往上找 `[3] 更新前備份`，**抄下更新前備份的檔名（`hd-before-update-<時間>.db`）與 SHA-256**，退回時要用。

### SY-05 啟動新版、確認

**做什麼**：

```powershell
docker compose --env-file $cfg up -d
docker ps --format "{{.Names}}  {{.Image}}  {{.Status}}"
curl.exe -s http://localhost:13000/api/health
curl.exe -s -i -H "Origin: http://<IP>:18080" http://<IP>:13000/api/health | Select-String Access-Control-Allow-Origin
[Console]::OutputEncoding = [Text.Encoding]::UTF8; docker compose --env-file $cfg logs api --tail 40
```

然後在護理站的電腦開 `http://<IP>:18080`，Ctrl＋F5，用管理者登入：

1. 系統管理 → 稽核軌跡：「系統維運」「版本更新完成」那一筆寫 `v0.4.0 → <新 tag>（第五次進院）`
2. 系統管理 → 營運參數與選項清單：營運參數表裡「院方資料未更新提示的起始時刻」是 `8`、「結束時刻」是 `23`（不必改）；「院方床位轉床號的方式」是 `0`（不是就改回 `0`）。下面的「院方資料同步」卡寫「還沒有設定院方資料的來源……」
3. 功能開關全部關掉，包括換版後預設開著的兩項：「本次透析」面板、現有功能的小幅遊戲化

🧪 用手機開，Ctrl＋F5 改成關掉分頁重開。

**成功**：`api`、`nurse-web`、`patient-web` 是 `hd-tablet-care:<新 tag>`、`Up`（`ai-gateway` 仍是 `v0.4.0`，正常）；health 是 `{"status":"ok",…}`；放行檢查印出 `Access-Control-Allow-Origin: http://<IP>:18080`；日誌有「已連線至 SQLite」帶 `synchronous=FULL`、「伺服器時區」`Asia/Taipei`，沒有紅色 `ERROR`；登得進去、三項都對。「版本更新紀錄」的版本欄是 `0.1.0 → 0.1.0`，正常。

🏥 日誌的版本標記寫「（正式環境設定）」。

### SY-06 備份一次、證明還原得回來

**做什麼**：

1. 護理端 → 系統管理 →「立即備份」，再：

   ```powershell
   Get-ChildItem $root\backups\hd-backup-* | Sort-Object LastWriteTime | Select-Object -Last 1 Name
   Get-Content "$root\backups\<檔名>.sha256"
   ```

2. 還原到測試檔、刪掉測試檔（第一條是一整行，**一律用 PowerShell**）：

   ```powershell
   docker compose --env-file $cfg run --rm --no-deps api node_modules/.bin/ts-node --project apps/api/tsconfig.json apps/api/scripts/restore-backup.ts --from /backups/<檔名> --to /data/restore-check.db --sha256 <雜湊>
   docker compose --env-file $cfg run --rm --no-deps --entrypoint rm api /data/restore-check.db
   ```

3. 🏥 問資訊室：備份資料夾（連同 `keys\`）由誰、多久送往院內另一台機器。🧪 跳過

**成功**：`✓ 與備份歷程上的紀錄相符`、`完整性檢查：ok`。

### SY-07 重新開機

**做什麼**：

🏥 院方准了、挑好時段才做（同機另一個專案會一起中斷）。請護理站開著護理端看著它，記下開始時間 → 主機重新開機 → 以**平常登入的帳號**登入（知道密碼的人輸入）→ **什麼都不碰**，等三分鐘 → 開新的 PowerShell、開工三行。院方不准就跳過，交接紙寫「未驗」。

🧪 工作列右下角通知區的 Docker 鯨魚圖示（藏在 `^` 裡就先點 `^`）按右鍵 → **Quit Docker Desktop** → 從開始選單再開 → 等三分鐘。**關掉 Docker Desktop 的視窗不算**：視窗關了引擎照跑，服務不會中斷（1116 模擬實測）。

接著：

```powershell
docker ps --format "{{.Names}}  {{.Image}}  {{.Status}}"
```

**成功**：四個服務自己回到 `Up`；護理端的紅框自己消失。**記下從開始到紅框消失幾分鐘**（寫進交接紙）。

下一份：《[第 2 份：SY-08～SY-15、SY-M1～SY-M4、出問題時](visit-5-system-2.md)》

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|
| [1118](https://94sh09sh19sh.github.io/hd-docs/1118/deployment/visit-5-system/) | 2026-11-18 | 首次定版。1117 部署手冊整套重寫時由舊冊改寫而成（舊冊號見目錄最後的對照），步驟編號不變；1118 照每份約 300 行的上限拆檔，後段移到同一套的下一份 |

[← 回部署手冊目錄](index.md)
