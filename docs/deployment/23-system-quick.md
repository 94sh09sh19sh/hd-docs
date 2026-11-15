# 第二十三冊 · 本系統換版上線（簡易版）

版本：v0.1　文件狀態：草案（1116 由第二十冊與第十七冊 0.6 節整理）　編號：`SY-xx`　詳細版：《[第二十四冊](24-system-detail.md)》（同一套編號）

> **這一冊只回答：本系統要按什麼、怎樣算成功、模擬和正式哪裡不同。** 出錯怎麼辦、為什麼、交接紙都在第二十四冊同一個編號底下。這一趟部署只看第二十一～二十四冊，其他冊不必翻。
>
> **第二階段**：第一階段《[第二十一冊](21-api-quick.md)》AF-11 三輪都成功了才做這一冊；沒成功，本系統不換版。
>
> 標記：**🏥 正式**＝院內主機才這樣做；**🧪 模擬**＝開發機上演練才這樣做；沒標的兩邊一樣。🧪 演練開始前，開發機已由開發端準備成跟院內主機一樣（1029 離院時的 `v0.4.0`、位址用 IP、登得進去、平板佈建好），演練完也由開發端撤除，手冊不寫。**模擬全程通過，`<新 tag>` 才准帶進院。**

> **公開範圍**：一律用代稱。值只寫在印出來的演練紀錄空白表與私人 repo 的 `deploy/records/`。可以拍照，照片只進私人 repo；`.env` 的內容、密碼、病人資料的畫面不拍。**代稱連同 `<`、`>` 一起換掉。**

## 摘要

- 換版 `v0.4.0` → `<新 tag>`（1116 起是 `v0.5.0`）：3 個只做加法的遷移；`.env` 多四行先留空；外殼不換、APK 不重建
- 順序：看現況 → 防毒 → 換版、確認、備份還原 → 重新開機 → 密碼移交 → 啟用讀檔、第一輪驗 → 平板 → 冒煙測試 → 交接
- **啟用讀檔是分界線**：一啟用，當天清單上所有病人都進主機；SY-09 四條沒全過就不啟用（B 級）
- 🧪 讀檔改用模擬的檔（SY-10 🧪），另多四步只有模擬才做：驗正式設定擋得住模擬、三支驗收、退回演練、判定（SY-M1～SY-M4）
- 🏥 首波還沒開始用，不必避開透析（DEP-32 1116 例外），挑護理師不忙的時候；資訊室同仁、學長、護理長在場；約 4～5 小時（不含第一階段）
- 出問題：退回 `v0.4.0` 在附錄一，停用讀檔在附錄二

## 0. 兩邊的差別一覽

| 哪裡 | 🏥 正式 | 🧪 模擬 |
|---|---|---|
| 根目錄 `$root` | `C:\hd\hd-tablet-care` | `C:\hd-sim` |
| `<IP>` | 院內主機的固定 IP | 開發機 Wi-Fi 網卡的 IPv4（開發端給） |
| 護理站的電腦 | 護理站那台（要 Windows 密碼、會休眠，請護理師輸入） | 連同一個 Wi-Fi 的手機瀏覽器；沒有 Ctrl＋F5，改成關掉分頁重開 |
| 平板 | `TB-00`，1029 已佈建 | 開發端佈建好的手機或暫用平板 |
| 管理者帳號 | 院內那一個 | `sim-admin`（密碼開發端給） |
| 資訊室、護理長、學長 | 在場 | 自己；要問他們的事跳過，紀錄寫「院內要問」 |
| 院方資料 | 第一階段抓取腳本寫的 `C:\API_Fetch\IDH_interface` | 模擬院方資料（SY-10 🧪） |
| 防毒、Docker 設定 | 請資訊室改 | 只看不改 |
| 重新開機 | 院方准才做，真的重開 | Quit Docker Desktop 再開 |

## 1. 出發前

### SY-01 確認 tag、答案、人與時段

**做什麼**：

1. `<新 tag>` 已推上 GitHub，而且照這一冊的 🧪 整輪演練過、SY-M4 判定通過。🧪 這一輪本身就是那次演練，跳過
2. 病人告知（A-03）有答案，才可能做到 SY-10。防毒排除（A-01）1116 起不擋讀檔：當天請資訊室加，加不了寫進交接紙（第二十四冊 SY-03）
3. 🏥 約到學長、一位有管理員權限的資訊室同仁、護理長；時段挑護理師不忙的時候（首波還沒開始用，透析時段也可以，DEP-32 1116 例外）
4. 印好：這一冊、第二十四冊附錄一的交接紙、演練紀錄空白表

**成功**：紀錄寫下 `<新 tag>`、它的 commit、演練判定的日期、約好的時段與在場的人。

## 2. 到場：先看

### SY-02 開工三行、看主機現況

**做什麼**：系統管理員身分的 PowerShell（🧪 `$root` 改成 `"C:\hd-sim"`）：

```powershell
$root = "C:\hd\hd-tablet-care"
$cfg  = "$root\config\.env"
cd $root\repo
git describe --tags
docker ps --format "{{.Names}}  {{.Image}}  {{.Status}}"
Get-ChildItem $root\backups\keys
Get-PSDrive C
```

再開 Docker Desktop → Settings → General，看「Send usage statistics」有沒有勾。

**成功**：`v0.4.0`；本系統四個服務（含 `ai-gateway`）都是 `v0.4.0`、`Up`；抄下 `backups\keys` 的金鑰備份檔名與 C 槽剩多少。🏥 `Up` 的時間比 1029 到今天短就是中間重開過機，記下來。使用統計沒勾；🏥 勾著就取消、Apply；🧪 只看。

> PowerShell 重開後，先打這裡的前三行（開工三行）。

### SY-03 防毒排除

**做什麼**：系統管理員身分的 PowerShell：

```powershell
Get-MpPreference | Select-Object -ExpandProperty ExclusionPath
```

🏥 請資訊室把 Docker 的資料夾（Docker Desktop → Settings → Resources → Advanced → Disk image location 那個路徑）加進排除清單，加完再打一次。🧪 只看，不加。

**成功**：🏥 第二次看得到那個路徑；紀錄寫「排除清單已加，由＿＿加」。當天加不了也照樣往下：紀錄與交接紙寫「未加，由＿＿於＿＿前加」（SY-09 第 1 條）；沒加會出現什麼現象見第二十四冊 SY-03。🧪 指令跑得動就好。

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

2. `notepad $cfg`：`HD_IMAGE_TAG` 改成 `<新 tag>`；照 `deploy\hospital.env.example` 的「院方資料：讀抓取腳本存下的檔」那一段補四行，**都先留空**。**只貼這四行，不要整段複製範本**（`v0.5.0` 範本那一段的第 98 行是一行斷掉的註解「aw_txt 與 hb-status.json）」，貼進來 compose 就讀不到 `.env`，1116 模擬實測）；貼在 `# --- 院方透析清單 API` 那一段的**上面**（跟範本同樣的位置），`HOSPITAL_API_BASE_URL`、`HD_SIMULATION_DEPLOYMENT` 已經有了，不要再貼一次：

   ```
   HD_DIALYSIS_LIST_DIR=
   HD_LAB_DIR=
   # COMPOSE_FILE=docker-compose.yml;docker-compose.dialysis-files.yml
   HOSPITAL_LAB_FIELD_MAP=
   ```

   `HOSPITAL_API_BASE_URL` 維持空白。🧪 `HD_SHELL_SIGNING=dev`、`HD_SIMULATION_DEPLOYMENT` 照開發端填的，不動。存檔後打 `docker compose --env-file $cfg config --quiet`，什麼都沒印才往下。
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

**成功**：`git describe` 正好是 `<新 tag>`、後面沒有尾巴；建置看到 `Built`；`docker images` 有 `v0.4.0` 與 `<新 tag>` 兩個（`v0.4.0` 不要刪）；最後印出「**更新完成。接下來的三件事是人要做的**」。往上找第 3 段，**抄下更新前備份的檔名（`hd-before-update-<時間>.db`）與 SHA-256**，附錄一要用。

### SY-05 啟動新版、確認

**做什麼**：

```powershell
docker compose --env-file $cfg up -d
docker ps --format "{{.Names}}  {{.Image}}  {{.Status}}"
curl.exe -s http://localhost:13000/api/health
curl.exe -s -i -H "Origin: http://<IP>:18080" http://<IP>:13000/api/health | Select-String Access-Control-Allow-Origin
[Console]::OutputEncoding = [Text.Encoding]::UTF8; docker compose --env-file $cfg logs api --tail 40
```

然後在護理站的電腦（🧪 手機）開 `http://<IP>:18080`，Ctrl＋F5（🧪 關掉分頁重開），用管理者登入：

1. 系統管理 → 稽核軌跡：「系統維運」「版本更新完成」那一筆寫 `v0.4.0 → <新 tag>（第五次進院）`
2. 系統管理 → 營運參數與選項清單：營運參數表裡「院方資料未更新提示的起始時刻」是 `8`、「結束時刻」是 `23`（迭代 32.1 的預設，不必改）；「院方床位轉床號的方式」是 `0`（不是就改回 `0`）。下面的「院方資料同步」卡寫「還沒有設定院方資料的來源……」（提示時段那一行要到 SY-10 接上資料夾後才出現，1116 模擬實測）
3. 功能開關全部關掉。從零建置或換版後有兩項預設是開的：「本次透析」面板、現有功能的小幅遊戲化，**這兩項也關**（DEP-29：面板等 SY-11 對真實資料驗過才開；遊戲化等長者、社工、護理部看過才開。1116 模擬實測）

**成功**：`api`、`nurse-web`、`patient-web` 是 `hd-tablet-care:<新 tag>`、`Up`（`ai-gateway` 仍是 `v0.4.0`，正常：兩版之間閘道沒改、AI 關著，SY-04 不建它）；health 是 `{"status":"ok",…}`；放行檢查印出 `Access-Control-Allow-Origin: http://<IP>:18080`；日誌有「已連線至 SQLite」帶 `synchronous=FULL`、「伺服器時區」`Asia/Taipei`，沒有紅色 `ERROR`（🏥 版本標記寫「（正式環境設定）」）；登得進去、三項都對。「版本更新紀錄」的版本欄是 `0.1.0 → 0.1.0`，正常。

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

- 🏥 院方准了、挑好時段才做（同機另一個專案會一起中斷）。請護理站開著護理端看著它，記下開始時間 → 主機重新開機 → 以**平常登入的帳號**登入（知道密碼的人輸入）→ **什麼都不碰**，等三分鐘 → 開新的 PowerShell、開工三行
- 🧪 工作列右下角通知區的 Docker 鯨魚圖示（藏在 `^` 裡就先點 `^`）按右鍵 → **Quit Docker Desktop** → 從開始選單再開 → 等三分鐘。**關掉 Docker Desktop 的視窗不算**：視窗關了引擎照跑，服務不會中斷（1116 模擬實測）

接著：

```powershell
docker ps --format "{{.Names}}  {{.Image}}  {{.Status}}"
```

**成功**：四個服務自己回到 `Up`；護理端的紅框自己消失。**記下從開始到紅框消失幾分鐘**（寫進交接紙）。🏥 院方不准就跳過，交接紙寫「未驗」。

## 4. 啟用讀檔、首波上線

### SY-08 密碼移交、建帳號

**做什麼**：

1. 🏥 護理長在護理站的電腦用管理者登入，**自己改掉管理者密碼**；開發端從此不知道。🧪 自己改
2. 用管理者替護理長與首波護理師各建一個帳號，請他們各自登入一次、改掉臨時密碼。🧪 建一個測試護理師帳號，登入一次
3. 🏥 平板 PIN 交給護理長

**成功**：稽核軌跡查得到改密碼與建帳號。

### SY-09 啟用前再確認一次

四條**全部**成立才往下，有一條不成立就停在這裡（B 級），跳到 SY-13：

| # | 條件 | 🧪 模擬 |
|---|---|---|
| 1 | SY-03 有結論：排除已加，或沒加但交接紙已寫「由＿＿於＿＿前加」 | 寫「院內要問」，照樣往下 |
| 2 | 病人告知有答案（涵蓋，或已補公告） | 同上 |
| 3 | 第二十一冊 AF-11 三輪都成功 | 第二十一冊的模擬做過就算 |
| 4 | 「院方床位轉床號的方式」是 `0`；首波還沒開始用（透析時段也可以，DEP-32 1116 例外） | 只看前半 |

> 🏥 **一啟用，當天清單上所有病人的主檔與療程都會進主機**，護理端會看到整個透析室，不是只有首波那一位。先讓首波護理師知道。

### SY-10 接上院方資料、讀檔檢查

**🏥 正式只做 A。🧪 模擬不做 A，改做 B1、B2。** 兩邊都是改 `.env` 的同五行（`HD_DIALYSIS_LIST_DIR`、`HD_LAB_DIR`、`COMPOSE_FILE`、`HOSPITAL_API_BASE_URL`、`HD_SIMULATION_DEPLOYMENT`），各自改成下面方框的樣子；其他行不動。

讀檔檢查（A、B1、B2 都用這一條）：

```powershell
docker compose --env-file $cfg exec -T api node apps/api/dist/hospital-api-probe.js
```

#### A（🏥）接上抓取腳本的資料夾

1. `notepad $cfg`，五行改成這樣（`COMPOSE_FILE` 開頭沒有 `# `，後面**沒有** `;docker-compose.lab-files.yml`；路徑照寫、不加引號）：

   ```
   HD_DIALYSIS_LIST_DIR=C:\API_Fetch\IDH_interface
   HD_LAB_DIR=
   COMPOSE_FILE=docker-compose.yml;docker-compose.dialysis-files.yml
   HOSPITAL_API_BASE_URL=
   HD_SIMULATION_DEPLOYMENT=
   ```

2. `docker compose --env-file $cfg up -d`，再跑讀檔檢查。

**成功**：標題「院方資料讀檔檢查（只讀、只印結構……）」；「透析清單資料夾」寫「在、讀得到」「唯讀：是」「**模擬標記檔：沒有**」；狀態檔「讀得到」、結果「成功」；有當天段落數與列數；「檢驗資料資料夾」沒設定是正常的。**整段抄進紀錄**（工具不印路徑、姓名、病歷號）。日誌有「院方資料同步已啟用（讀透析清單資料夾）」。

#### B1（🧪）接上模擬院方資料

1. `notepad $cfg`，五行改成這樣：

   ```
   HD_DIALYSIS_LIST_DIR=
   HD_LAB_DIR=
   COMPOSE_FILE=docker-compose.yml;docker-compose.hospital-files-sim.yml
   HOSPITAL_API_BASE_URL=
   HD_SIMULATION_DEPLOYMENT=yes
   ```

2. `docker compose --env-file $cfg --profile simulation up -d`，等 3 分鐘，再跑讀檔檢查。

**成功**：「模擬標記檔：有」（模擬是對的）。

#### B2（🧪）練院內那種掛法：路徑帶空白與中文

1. 把模擬的檔複製一份出來：

   ```powershell
   New-Item -ItemType Directory -Force "C:\hd-sim\院方 資料" | Out-Null
   docker compose --env-file $cfg cp api:/hospital-sim/dialysis-list "C:\hd-sim\院方 資料\透析清單"
   ```

2. `notepad $cfg`，五行改成這樣（跟 A 一樣的掛法，只是路徑換成上面那個、`HD_SIMULATION_DEPLOYMENT` 留 `yes`）：

   ```
   HD_DIALYSIS_LIST_DIR=C:\hd-sim\院方 資料\透析清單
   HD_LAB_DIR=
   COMPOSE_FILE=docker-compose.yml;docker-compose.dialysis-files.yml
   HOSPITAL_API_BASE_URL=
   HD_SIMULATION_DEPLOYMENT=yes
   ```

3. `docker compose --env-file $cfg up -d`，再跑讀檔檢查。

**成功**：「在、讀得到」「唯讀：是」「模擬標記檔：有」。這份是複製出來的、不會再更新，之後出現「未更新」提示是正常的。

### SY-11 第一輪怎麼驗

**做什麼**（護理站的電腦／🧪 手機）：

1. 系統管理 →「院方資料同步」卡：「資料來源：抓取腳本的檔」「每 3 分鐘讀一次」「抓取腳本最近一輪：成功」。按「立即同步」，卡片上方出現綠色的「已同步：N 次透析……」或「已重讀：內容與上一次相同，沒有要寫入的」，下面表格最上面多一列「成功」（內容沒變的會標「內容沒變」）。兩種都算成功；🧪 B2 的資料夾是複製出來的、不會再變，所以一定是「內容沒變」
2. 對數字（不抄病人的值）：
   - 透析次數：卡片表格「透析次數」那一欄，跟 SY-10 讀檔檢查的當天段落數、列數差不多
   - 床號：系統管理 →「床位清單」卡，院方資料出現的床號會自動加在最後面，是 `A1`～`E9` 這種字母開頭（`1A`～`3D` 與 `99` 原樣出現，不要改設定）。簡易版只顯示平板編號與病人姓名，看不到床號（1116 模擬實測）
   - 療程：切到專業版，首頁「即時總覽（日期）」列出今天的療程；🏥 問護理師「現在在透析的有幾床、今天排了幾床」，跟即時總覽對得上
3. 系統管理 → 稽核軌跡，看有沒有動作是「院方資料格式不符，該次透析未寫入」的紀錄（卡片表格的「格式不符」欄也是這個數）。🏥 應該沒有；有的話抄原因（不含病歷號）。🧪 每一輪都會有 1 筆，是模擬資料故意放的壞資料（模擬辛，每列少兩欄），正常
4. 等 3 分鐘，卡片表格最上面一列的時間往前跳

**成功**：四項都對。🏥 卡片最上面**沒有**「目前接的是模擬院方 API」；🧪 **有**這一行才對，簡易版的病人是模擬甲、模擬乙……這些虛構病人（沒有模擬辛）。🏥 床號或療程對不上就照附錄二停用，記下實況（B 級）。

### SY-12 平板帶回指定的床

**做什麼**：

1. 🏥 `TB-00` 放到指定的床、插電（不必重新註冊）。🧪 用開發端佈建好的那台
2. 護理端「新增裝置」看得到它、「固定中」、外殼版本正常
3. 🏥 Wi-Fi 實測：床邊與透析區另一頭都開得到等待畫面
4. 功能開關把「本次透析」面板開啟（SY-11 四項都對了才開，DEP-29；沒啟用讀檔就維持關，這一步只看平板固定）
5. 在護理端把平板指派給一位病人（🏥 首波那一床；🧪 一位模擬病人）→ 療程進行中面板有數字。🏥 跟著真實療程，等不到就留到第一個班次

**成功**：平板顯示病人端首頁、本次透析面板有數字；護理端看得到平板在那一床。🏥 Wi-Fi 不通：護理端照用、病人端不開，寫進交接紙。

## 5. 收尾

### SY-13 冒煙測試

**不輸入任何真實病人資料、不開任何功能開關。** 在護理站的電腦（🧪 手機）：

| # | 做什麼 | 應該是 |
|---|---|---|
| 1 | 用護理長的帳號（🧪 測試護理師）登入 | 登得進去，預設開「簡易版」 |
| 2 | 簡易版、專業版切換一次 | 兩邊都開得起來 |
| 3 | 系統管理 → 備份歷程 | 有 SY-06 那一份 |
| 4 | 「院方資料同步」卡 | 啟用了：最近一輪成功；沒啟用：還沒設定資料夾 |
| 5 | 稽核軌跡 | 查得到今天的改密碼、建帳號、備份、版本更新 |
| 6 | 🏥 總覽螢幕：在護理長指定的那台開護理端總覽 | 開得起來、不休眠 |
| 7 | SY-07 的紅框 | 看過就打勾；沒做寫「未驗」 |
| 8 | 平板 | 在指定的床、「固定中」 |
| 9 | 🏥 磁碟門檻：跟資訊室議定剩多少就通知、誰監看 | 寫進交接紙（開發端建議剩 50 GB） |

**成功**：每一列打勾，或寫明為什麼沒做。

### SY-14 交接（🏥）

**做什麼**：填好第二十四冊附錄一的交接紙，當場講一次、讓對方自己做一次「啟停」與「斷電之後」，交給護理長與資訊室各一份。🧪 跳過，但把交接紙從頭到尾讀一遍，看不懂的圈起來。

### SY-15 離院前、第一個班次（🏥）

**做什麼**：

1. 開發端**留到第一個班次結束**：「院方資料同步」卡每 3 分鐘有新的一列、平板面板有更新
2. PowerShell 關掉、瀏覽器登出；手機裡含院內資料的照片移進私人 repo 後刪掉
3. 當天晚上補完紀錄，照第二十四冊 SY-15 寫進院紀錄

## 6. 🧪 模擬才做：驗收與判定

### SY-M1 驗院內的設定擋得住模擬，再停用讀檔

**做什麼**：`notepad $cfg`，`HD_SIMULATION_DEPLOYMENT` 清空（等號後面什麼都不留），然後 `docker compose --env-file $cfg up -d api`，等一輪（3 分鐘）看「院方資料同步」卡。接著照附錄二停用讀檔。最後 `HD_SIMULATION_DEPLOYMENT` 改回 `yes`，`docker compose --env-file $cfg up -d`。

**成功**：卡片最新一列是「拒收（正式環境收到模擬資料）」、資料庫一筆都沒多；停用後卡片回到還沒設定資料夾。

### SY-M2 跑三支驗收

**做什麼**：在**平常寫程式的工作目錄**（不是 `C:\hd-sim\repo`）：

```powershell
git switch --detach <新 tag>
npm run verify:iteration11 -- --live --env-file C:\hd-sim\config\.env
npm run verify:iteration12 -- --live --env-file C:\hd-sim\config\.env
npm run verify:iteration13 -- --live --env-file C:\hd-sim\config\.env
git switch master
```

**成功**：三支都全部 ✓。第一支會 `down -v` 再 `up -d`，是刻意的（驗資料卷不會被刪）。

### SY-M3 退回 `v0.4.0` 演練

**做什麼**：照附錄一真的退一次，`<備份檔名>`、`<雜湊>` 用 SY-04 抄的。

**成功**：`完整性檢查：ok`；三個服務是 `hd-tablet-care:v0.4.0`；手機重開分頁後登得進去。SY-04 之後註冊或建的東西不見了，是對的。

### SY-M4 判定能不能帶進院

| # | 條件 |
|---|---|
| 1 | SY-04 `更新完成`，更新前備份的檔名與雜湊抄到了 |
| 2 | SY-05 新版登得進去，帳號密碼是更新前的（資料留住了） |
| 3 | SY-06 還原 ✓ |
| 4 | SY-07 服務自己回來，量到幾分鐘 |
| 5 | SY-10 🧪 兩段都對，帶空白與中文的路徑是「唯讀：是」 |
| 6 | SY-11 卡片、床位清單、即時總覽對 |
| 7 | SY-M1 擋得住模擬 |
| 8 | SY-12 平板（做了的話）顯示面板 |
| 9 | SY-M2 三支全部 ✓ |
| 10 | SY-M3 退回後登得進去 |
| 11 | 紙本上圈起來的地方都改回文件了 |

**成功**：十一項都 ✓，紀錄最後寫「`<新 tag>` 可以帶進院，＿月＿日」。有一項 ✗ 就不能帶：修好、打新 tag、重新演練。

## 附錄一：新版出問題，退回 `v0.4.0`

**什麼時候用**：SY-04 之後，新版 `api` 起不來或主線壞掉，現場解不開。**越早越好**：資料庫會換回 SY-04 的更新前備份，之後寫進去的（含啟用讀檔後同步進來的、改過的密碼與帳號）都會消失。

**做什麼**：

1. `git checkout v0.4.0`；`notepad $cfg`：`HD_IMAGE_TAG` 改回 `v0.4.0`，`HD_DIALYSIS_LIST_DIR` 清空、`COMPOSE_FILE` 那一行改回註解（開頭加 `# `）
2. 停後端、把新版的資料庫移到旁邊、還原、啟動（第二、三條各是一整行）：

   ```powershell
   docker compose --env-file $cfg stop api
   docker compose --env-file $cfg run --rm --no-deps --entrypoint sh api -c "mkdir -p /data/before-rollback && mv /data/hd.db /data/hd.db-wal /data/hd.db-shm /data/before-rollback/ 2>/dev/null; ls -l /data/before-rollback"
   docker compose --env-file $cfg run --rm --no-deps api node_modules/.bin/ts-node --project apps/api/tsconfig.json apps/api/scripts/restore-backup.ts --from /backups/<備份檔名> --to /data/hd.db --sha256 <雜湊>
   docker compose --env-file $cfg up -d
   ```

**成功**：`完整性檢查：ok`；`docker ps` 三個服務是 `hd-tablet-care:v0.4.0`；護理站 Ctrl＋F5 後登得進去。抓取腳本不受影響、照跑。`/data/before-rollback/` 那份留著，帶回給開發端。

## 附錄二：停用讀檔

**什麼時候用**：SY-10 的檢查不對、SY-11 床號或療程對不上、院方要求先停，或 🧪 SY-M1。

**做什麼**：`notepad $cfg`，`HD_DIALYSIS_LIST_DIR` 清空、`COMPOSE_FILE` 那一行改回註解，然後：

```powershell
docker compose --env-file $cfg up -d
```

**成功**：「院方資料同步」卡寫還沒設定資料夾；日誌沒有「院方資料同步已啟用」。之後病人、床位、療程回到護理師的人工操作。已經寫進主機的資料不會被刪，**現場不要自己刪**（第二十四冊附錄二）。

---

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|

[← 第二十二冊 · 抓取腳本上線（詳細版）](22-api-detail.md)　[← 回部署手冊總覽](index.md)　[第二十四冊 · 本系統換版上線（詳細版） →](24-system-detail.md)
