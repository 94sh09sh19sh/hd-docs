# 本系統換版與退回

> - 狀態：**現行**（常備參考）。院內主機 1116 起是本系統 `v0.5.0`，下一次換版、出問題要退回，都照這一份；進院冊只寫那一趟的順序並連過來
> - 1117 由舊的第十一冊第 6 節（W-19 更新、W-20 回退）改寫，併入舊第二十三冊附錄一（退回 `v0.4.0`）、舊第十八冊附錄二（退回 `v0.3.0`）、舊第二十冊附錄二（退回 `v0.4.0`，內容與第二十三冊附錄一相同），以及舊第十八冊 J-15～J-19、舊第二十三／二十四冊 SY-04～SY-05、舊第二十冊 GO-05～GO-06 裡每次換版都一樣的出錯處置；各趟的具體版本留在第 0 節與各步驟的例子
> - 編號：沿用 `W-19`（換版）、`W-20`（退回）；W-19 底下分成 ①～⑥ 六小步
> - 分成兩份（1118 拆，每份 300 行內）：本份是第 0～2 節（現在的版本與歷次換版、換版之前、W-19 換版）；《[本系統換版與退回（第 2 份，第 3～4 節，W-20）](ref-upgrade-2.md)》是第 3～4 節（W-20 退回、🧪 開發機演練）

## 摘要

- 換版＝`git checkout <新 tag>` → 補 `.env` → `build` 新映像檔 → 停 `api`、跑 `db-update`（更新前備份＋驗證還原＋套用遷移＋寫紀錄）→ `up -d` → 確認、備份還原一次
- `db-update` 第 3 段印的備份檔名（`hd-before-update-<時間>.db`）與 SHA-256 是退回唯一的依據，一定要抄
- 舊映像檔不刪：新版穩定之前，那是唯一退得回去的東西
- 每一版要補的 `.env` 行、遷移數不一樣：開發端出發前照第 1.3 節查，歷次的實況在第 0 節
- 🏥 排在非透析時段（首波開始使用前例外，DEP-32 1116），換版後第一個班次要有人在
- 退回（W-20）與 🧪 開發機演練（第 4 節）在第 2 份：程式可以退版，資料庫不能把遷移倒回去
- 登不進去照《[護理站登不進去與主機位址](ref-login.md)》；備份還原驗證照《[備份、還原與關服務](ref-backup-shutdown.md)》

## 0. 現在的版本與歷次換版

| 日期 | 換版 | 遷移 | `.env` | 外殼／APK | 結果 |
|---|---|---|---|---|---|
| 1001 | 從零部署 `v0.3.0` | — | 全新填 | 第一次建 | 《[第二次進院紀錄（1001）](record-2-1001.md)》 |
| 1029 | `v0.3.0` → `v0.4.0` | 19 個，全部只做加法 | 多一個必填 `HD_EXPORT_DIR`，另兩行院方 API 變數留空 | 不換、APK 不重建 | 一路沒出錯；建置不到一分鐘（主機有快取），見《[第三次進院紀錄（1029）](record-3-1029.md)》 |
| 1116 | `v0.4.0` → `v0.5.0` | 3 個，只做加法（迭代 30.4 連點成畫、32 院方資料讀檔、32.1 未更新提示時段） | 補四行院方資料讀檔設定，先留空，啟用讀檔時才填 | 不換、APK 不重建 | 建置 68 秒、`db-update` 成功、讀檔啟用，見《[第五次進院紀錄（1116）](record-5-1116.md)》 |
| 下一次 | `v0.5.0` → `<新 tag>` | 1117 時 master 在 `v0.5.0` 之後沒有新遷移 | 1117 時範本只修了一行斷掉的註解（第 1.3 節） | 1117 時 compose 沒改；`restart` 預定在下一個 tag 改（舊第二十四冊 SY-M4 例外），改了要重驗重新開機 | — |

1116 之後院內主機的狀態：`api`、`nurse-web`、`patient-web` 是 `hd-tablet-care:v0.5.0`，`ai-gateway` 仍是 `v0.4.0`（兩版之間閘道沒改、AI 關著，1116 沒建它）；`.env` 的讀檔設定已填（`HD_DIALYSIS_LIST_DIR`、`COMPOSE_FILE` 帶 `docker-compose.dialysis-files.yml`）。主機現況的唯一真本是《[院內主機現況與未完成事項](ref-status.md)》。

開工三行（＝《[從零部署本系統](ref-fresh-install-3.md)》V-09；PowerShell 關掉再開就要重打，`couldn't find env file` 十次有九次是忘了這三行）：

```powershell
$root = "C:\hd\hd-tablet-care"
$cfg  = "$root\config\.env"
cd $root\repo
```

🧪 第一行改成 `$root = "C:\hd-sim"`。

## 1. 換版之前

### 1.1 規則

- DEP-19 的七步：① `git fetch` 確認新 tag 在 → ② 以新 tag 建置、映像檔標籤帶版本號、舊版不刪 → ③ 停 `api` → ④ 備份並驗證還原得起來 → ⑤ 套用遷移（DEP-31 那支）→ ⑥ 以新版啟動、確認主線功能 → ⑦ 寫進更新紀錄，含新舊兩個 tag。④⑤⑦ 由 `db-update.mjs` 一次做完（W-19 ④）
- 🏥 排在沒有透析的時段，先跟護理站講一聲；**更新後第一個班次要有人盯著**（DEP-32）：問題在累積新資料之前發現，退回的代價是零。1116 加例外：首波開始使用之前（還沒有護理師或病人靠這套系統），換版不受「非透析時段」限制，挑護理師不忙的時候；上線之後照舊排非透析時段。「第一個班次要有人在」不受例外影響
- **每一個要帶進院的 tag，都先在開發機照這一份走一次**（DEP-22；第 4 節），沒有演練過、判定通過的 tag 不准帶
- 演練中發現程式要修：修好、跑過驗收、**打下一個 tag**（例如 `v0.5.1`）重新演練。推上去的 tag 不移動、不刪掉重打（院內與紀錄都靠 tag 名字對版本）
- 指令一律在主機的 PowerShell 打，不要用 Git Bash（Git Bash 會把 `/backups/…`、`/data/…` 改寫成 Windows 路徑）；不要自己開容器、不要自己下 `docker run -v`
- compose 檔不在主機上改；要改回開發端改、打新 tag

### 1.2 要準備的

- 新 tag 已推上 GitHub，記下它的 commit 與演練判定的日期
- 🏥 約好有管理員權限的資訊室同仁、護理長；時段照 1.1
- 這一份與當趟的進院冊印好；演練紀錄空白表

### 1.3 這一版改了什麼（開發端出發前查）

在開發端的工作目錄：

```powershell
git diff --stat <舊 tag> <新 tag> -- apps/api/prisma/migrations deploy/hospital.env.example docker-compose.yml docker-compose.dialysis-files.yml docker-compose.lab-files.yml services/ai-gateway services/shell-builder/shell.pin
```

| 有變動的 | 代表 | 寫進當趟進院冊 |
|---|---|---|
| `apps/api/prisma/migrations` | 有新遷移，`db-update` 第 5 段會套用 | 幾個、是不是只做加法 |
| `deploy/hospital.env.example` | `.env` 可能要補行 | 補哪幾行、先留空還是要填、貼在哪 |
| `docker-compose*.yml` | 服務、掛載或 `restart` 變了 | 有沒有新的必填變數（compose 會停在「請設定 …」）；`restart` 變了要重驗重新開機 |
| `services/ai-gateway` | 閘道改了 | W-19 ③ 要加 `--profile ai` 一起建 |
| `services/shell-builder/shell.pin` | 外殼換版 | APK 要重建、平板要重裝（《[平板與外殼 App](ref-tablet.md)》）；沒變就不必（DEP-20） |

`v0.5.0` → master（1117）：只有 `deploy/hospital.env.example` 修了一行（`v0.5.0` 範本第 98 行斷掉的註解接回去），其他都沒變。

## 2. 換版

### W-19 換版（DEP-19）

#### ① 下載新版

```powershell
git fetch --tags
git checkout <新 tag>
git describe --tags
```

沒有建置快取、或想先把基底映像下載好（1029 有做，1116 沒做）：

```powershell
docker pull node:20-bookworm-slim
```

**成功**

| 看什麼 | 應該是 |
|---|---|
| `git checkout` | `Previous HEAD position was …` 與 `HEAD is now at …` 兩行，正常（原本就停在舊 tag，所以不會再印 `detached HEAD` 那一大段；印了也正常） |
| `git describe --tags` | **正好是** `<新 tag>`，後面沒有 `-3-g1a2b3c4` 這種尾巴 |
| `docker pull` | 最後是 `Status: Downloaded newer image for …` 或 `Status: Image is up to date for …` |

| 症狀 | 處置 |
|---|---|
| `git fetch` 說 `Permission denied (publickey)` | 部署金鑰被拿掉了。`ssh -T github-hd-tablet-care` 看一下，印出 `Hi 94sh09sh19sh/hd-tablet-care!…` 才對；不是的話打電話給開發端（repo 管理者）重新登記 |
| `Connection reset by … port 22` | 網路切斷連線，再打一次 |
| `error: pathspec '<新 tag>' did not match` | tag 沒推上去，或打錯字 |
| `git describe` 後面有尾巴（例如 `-3-gabc123`） | 不在 tag 上，重打 `git checkout <新 tag>` |
| `git checkout` 說 `Your local changes … would be overwritten` | 有人改過 repo 裡的檔案。**停手**，不要加 `--force` |
| `docker pull` 出現 `no such host` | 同 ③ 那一列 |

新版的 compose 檔多了必填變數時，從這一刻起到 ② 補好 `.env` 之前，每一條 `docker compose` 指令都會停在「請設定 …」（1029 是 `HD_EXPORT_DIR`）。這是對的，② 補上就好。

#### ② 補 `.env`

```powershell
notepad $cfg
```

1. `HD_IMAGE_TAG` 改成 `<新 tag>`
2. 照 `deploy\hospital.env.example` 補這一版新增的行（第 1.3 節查出來的）。**只貼新增的那幾行，不要整段複製範本**，貼在跟範本同樣的位置；`.env` 已經有的變數不要再貼一次
3. 存檔（記事本問編碼就選 UTF-8，不要改檔名），然後：

```powershell
docker compose --env-file $cfg config --quiet
git describe --tags
Select-String -Path $cfg -Pattern '^(HD_IMAGE_TAG|HD_EXPORT_DIR|HD_SHELL_SIGNING|LLM_PROVIDER|HOSPITAL_API_BASE_URL|HD_SIMULATION_DEPLOYMENT)='
Select-String -Path $cfg -Pattern '^[^#].*(<|>|hd-server|localhost)'
```

| 哪一條 | 應該是 |
|---|---|
| `config --quiet` | 什麼都沒印 |
| `HD_IMAGE_TAG` | 與 `git describe --tags` 一字不差 |
| `HD_EXPORT_DIR` | `C:\hd\hd-tablet-care\export` |
| `HD_SHELL_SIGNING` | `hospital`（🧪 `dev`） |
| `LLM_PROVIDER` | `mock` |
| `HOSPITAL_API_BASE_URL`、`HD_SIMULATION_DEPLOYMENT` | 等號後面空白，或根本沒有這兩行（沒寫等於空白，正是院內要的）。🧪 `HD_SIMULATION_DEPLOYMENT` 照開發端填的，不動 |
| 最後一條 | 什麼都沒印（沒有照抄範例、沒有 `localhost`、沒有忘了換掉的 `<`、`>`） |

**歷次要補的行**（例子；下一次照第 1.3 節查）：

- `v0.3.0` → `v0.4.0`（1029）：在 `HD_CONFIG_DIR=` 那一行下面加 `HD_EXPORT_DIR=C:\hd\hd-tablet-care\export`（資料夾不必先建；研究資料取出的位置，與備份資料夾分開，見《[取出資料](ref-data-export.md)》）；檔案最後加 `HOSPITAL_API_BASE_URL=`、`HD_SIMULATION_DEPLOYMENT=` 兩行，等號後面都留空（不加也能跑，加了讓 `.env` 與新版範本長得一樣）
- `v0.4.0` → `v0.5.0`（1116）：照範本「院方資料：讀抓取腳本存下的檔」那一段補四行，**都先留空**，`COMPOSE_FILE` 那一行維持註解（讀檔要等啟用前的條件都過才開，見《[讀檔：啟用、檢查、停用](ref-dialysis-files.md)》）：

```
HD_DIALYSIS_LIST_DIR=
HD_LAB_DIR=
# COMPOSE_FILE=docker-compose.yml;docker-compose.dialysis-files.yml
HOSPITAL_LAB_FIELD_MAP=
```

這四行貼在 `# --- 院方透析清單 API` 那一段的上面。🏥 院內的 `.env` 是更早的範本建的，**沒有** `# --- 院方透析清單 API` 那一段（1116 現場遇到）：貼在 `# --- 其他營運參數` 那一行的上面，`HOSPITAL_API_BASE_URL`、`HD_SIMULATION_DEPLOYMENT` 也不用補。`v0.5.0` 範本那一段的第 98 行是一行斷掉的註解「aw_txt 與 hb-status.json）」（`hospital_dataset\raw_txt` 的 `\r` 寫入時被當成換行），整段複製會帶進來、compose 就讀不到 `.env`（1116 模擬實測）；master 已修，下一個 tag 起的範本沒有這一行

| 症狀 | 處置 |
|---|---|
| `required variable HD_… is missing a value: 請設定 …` | 冒號後面寫的就是還缺什麼，照範本補上 |
| `failed to read …\.env: line N: unexpected character … in variable name …` | `.env` 第 N 行不是註解也不是「名稱=值」。最常見是整段複製了 `v0.5.0` 範本、帶進那一行斷掉的「aw_txt 與 hb-status.json）」。`notepad $cfg` 刪掉第 N 行（或在開頭加 `# `），再打 `config --quiet` |
| `couldn't find env file` | `$cfg` 路徑打錯，或這個 PowerShell 視窗還沒輸入開工三行 |
| `HD_SHELL_SIGNING` 不是 `hospital`（🏥） | **停手**，不要改它 |
| `HD_SIMULATION_DEPLOYMENT` 有值（🏥） | 清空。院內主機這一格永遠空白 |
| 有 `HIGH_RISK_WRITTEN_CONFIRMATION` 或 `SHOWCASE_MODE` 這一行 | 刪掉（`v0.4.0` 起不讀，留著只會讓人看不懂） |

#### ③ 建置

```powershell
docker compose --env-file $cfg build
docker images hd-tablet-care
```

主機有之前建置的快取時一分鐘左右就好（1029 不到一分鐘、1116 68 秒），看到 `Built` 就算有建；沒有快取約十分鐘，畫面一直捲動是正常的。

**成功**：最後出現 `Image hd-tablet-care:<新 tag> Built`；`docker images` 看得到舊 tag 與 `<新 tag>` **兩個**。**舊 tag 的映像檔不要刪**（W-20 要用）。到這裡為止服務還是舊版在跑，護理站照樣用得了。

AI 閘道：`git diff` 看到 `services/ai-gateway` 有改、而且閘道在跑（`docker ps` 有 `ai-gateway`），`build` 與之後的 `up -d` 都加 `--profile ai`，閘道才會跟著換新版（1029 J-20 起的規則）。閘道沒改、AI 關著，可以不建它，閘道留在舊版（1116 的做法：`ai-gateway` 仍是 `v0.4.0`）。

| 症狀 | 處置 |
|---|---|
| `failed to resolve source metadata for docker.io/library/node`，後面有 `no such host` | Docker 查不到 Docker Hub 的網域。依序：① 同一條再打一次；② 工作列的 Docker 圖示按右鍵 → Restart，等變綠再打；③ 仍不行，請資訊室看院內 DNS。用了哪一個辦法才過，寫進紀錄 |
| `npm error code ETIMEDOUT` 或 `ECONNRESET` | 網路不穩，再打一次；已下載的層會沿用 |
| `pull access denied for hd-tablet-care` | 打成 `up` 了，先 `build`。本系統的映像檔一律就地建置，不從任何地方拉（DEP-39） |
| 任何提到 `binaries.prisma.sh` 的錯誤 | 映像檔建壞了（引擎沒在建置時取得）。重建，**不要在執行期開網路讓它下載**（DEP-30） |

#### ④ 停後端、更新資料庫

🏥 先確認現在沒有透析、已經跟護理站講過（1029 在治療中停了後端、沒先講，舊第十八冊之一 O-08）。這一步到 ⑤ `up -d` 之間護理站會看到斷線紅框，`up -d` 之後就會消失。

三行，第三行是一整行，不要斷開：

```powershell
$tag = git describe --tags
docker compose --env-file $cfg stop api
docker compose --env-file $cfg run --rm --no-deps api node apps/api/scripts/db-update.mjs --note "<舊 tag> → $($tag)（第 N 次進院）"
```

第一行把 ① 確認過的版本存進 `$tag`，`--note` 的說明就自動帶上，**不必手改**（1029 照抄成字面的 `<新 tag>`）。打 `$tag` 看一下，應該正好是 `<新 tag>`。`--note` 只改 `<舊 tag>` 與 `第 N 次進院`，例如 1116 是 `"v0.4.0 → $($tag)（第五次進院）"`。

`db-update.mjs` 先量備份目的地的空間（`備份目的地可用 … MB，這次更新需要 … MB，夠`），印 `版本更新流程（《資料庫使用規範》第 18 條）`、執行身分、目標版本（`package.json` 的號碼加「｜正式環境設定」），接著六段，任何一段沒過就停，資料庫不會被動到：

| 段 | 標題 | 會印 |
|---|---|---|
| `[1]` | 確認服務已停止（DEP-19 第 1 步） | `沒有服務在回應，可以繼續`。它問的是 compose 給的 `UPDATE_PROBE_URL=http://api:3000/api/health`（正在跑的 `api`），不是一次性容器自己 |
| `[2]` | 開啟更新紀錄（規範 18.4） | `前一次成功更新的版本：…`（第一次是「這是第一次留下紀錄」） |
| `[3]` | 更新前備份（規範 18.1 第 1 關） | `hd-before-update-<時間>.db（… bytes）`、`SHA-256：<64 碼>`。**這兩樣抄下來**，W-20 要用。檔名時間是 UTC，比台灣少 8 小時（台灣 15:10 是 `…T0710…`） |
| `[4]` | 驗證備份還原得起來 | 換上的 tag 是 `v0.5.0` 以前：`完整性檢查 ok；護理端帳號 N、病人 N、綁定 N、求助 N、稽核紀錄 N`，帳號數連登入不了的系統帳號一起算（1116 印 3，實際能登入的只有管理者一個）。換上的 tag 帶了迭代 32.3（1124 起的 master）：印三行 `完整性檢查 ok；病人 N、綁定 N、求助 N、稽核紀錄 N`、`能登入的帳號 N`（有待審核或停用的另外括號寫）、`系統帳號 M`（院方資料同步這類登入不了的，通常 1～3） |
| `[5]` | 套用既有遷移（DEP-31：不是開發用的那支） | `套用了 N 個遷移：…`，或 `沒有待套用的遷移` |
| `[6]` | 寫入更新紀錄 | `更新紀錄與稽核軌跡都已寫入` |

**成功**：最後印出「**更新完成。接下來的三件事是人要做的：**」（啟動服務確認主線功能、舊版映像檔先留著、第一個班次要有人盯著），再一句「要退回去的話：程式可以退版，資料庫不行退版」與這次的備份檔名。

| 症狀 | 處置 |
|---|---|
| `更新中止：後端服務還在執行。…` | 上一行的 `stop api` 沒做或沒成功，再打一次 `stop api`。**不要加 `--allow-running`**，那是演練用的 |
| `更新中止：備份目的地可用空間 … MB，不足以完成這次更新。需要 … MB…` | 需要＝資料庫大小 ×2＋保留下限 `DB_DISK_MIN_FREE_MB`（預設 1024 MB）。主機共用，先問資訊室是誰佔掉空間；不要自己刪別人的東西（DEP-37） |
| `更新中止：備份沒有成功完成，更新到此為止：…` | 備份目錄寫不進去或空間不夠。這一關不過就不往下走 |
| `更新中止：備份還原後的完整性檢查未通過：…`、`…是一顆空的資料庫，這份備份不可信。` | 資料庫本身可能有問題。**不要往下換**，整段抄下來打電話給開發端 |
| `更新中止：DATABASE_URL 指向的資料庫檔案不存在，這不是一次更新，是一次全新安裝。` | 資料卷不是原本那一個，或 `/data/hd.db` 不見了。**停手**，`docker volume ls --filter name=hd-tablet-care` 抄下來 |
| `更新中止：套用遷移失敗（結束狀態 N）：…` | 備份已做、已驗證，資料庫在遷移那一步停下。整段抄下來，照下一列讓舊版回來 |
| 其他任何「中止」 | 每一種都會接一句「資料庫沒有被改動」。整段抄下來，`HD_IMAGE_TAG` 改回舊 tag、`git checkout <舊 tag>`、`docker compose --env-file $cfg up -d` 讓舊版的後端回來，打電話給開發端 |

「中止」之後重跑：排除原因後再打一次第三行（訊息裡寫的 `npm run db:update` 是開發機的寫法，主機上一律用上面那條 `docker compose … run`）。

#### ⑤ 啟動新版、確認

```powershell
docker compose --env-file $cfg up -d
docker ps --format "{{.Names}}  {{.Image}}  {{.Status}}"
curl.exe -s http://localhost:13000/api/health
curl.exe -s -i -H "Origin: http://<IP>:18080" http://<IP>:13000/api/health | Select-String Access-Control-Allow-Origin
[Console]::OutputEncoding = [Text.Encoding]::UTF8; docker compose --env-file $cfg logs api --tail 40
```

| 看什麼 | 應該是 |
|---|---|
| `docker ps` | `api`、`nurse-web`、`patient-web` 的映像檔是 `hd-tablet-care:<新 tag>`、`Up`；`ai-gateway` 沒跟著建的話仍是舊 tag，正常 |
| health | `{"status":"ok",…}` |
| 放行檢查 | `Access-Control-Allow-Origin: http://<IP>:18080` |
| 日誌 | 「已連線至 SQLite」帶 `journal_mode=WAL、foreign_keys=ON、busy_timeout=5000ms、synchronous=FULL`；「伺服器時區」`Asia/Taipei`；版本標記後面寫「（正式環境設定）」；沒有紅色的 `ERROR`（部署規範第 11 章第 3、7 條） |

然後在護理站的電腦（🏥 要 Windows 密碼、會休眠，請護理師輸入；🧪 連同一個 Wi-Fi 的手機，沒有 Ctrl＋F5，改成關掉分頁重開）：

1. Ctrl＋F5 強制重新整理（舊版的網頁還留在瀏覽器裡），開 `http://<IP>:18080` 用管理者登入；帳號密碼是換版前的（換版不改密碼，登得進去也證明資料留住了）
2. 系統管理 → 稽核軌跡：用途「系統維運」、動作「版本更新完成」那一筆寫著 `--note` 的說明（例如 `v0.4.0 → v0.5.0（第五次進院）`）。「版本更新紀錄」那張表**沒有說明欄**，版本欄是 `apps/api/package.json` 的號碼、不是 git tag：主機第一次更新顯示 `— → 0.1.0`，之後是 `0.1.0 → 0.1.0`，都正常。要對版本看 `docker ps` 的映像檔名稱
3. 功能開關：**全部是關的**（DEP-29、部署規範第 11 章第 18 條；`v0.4.0` 起多了遊戲化、獎勵制度、跑馬燈等很多開關，照預設關著，要開得先讓長者、社工、護理部看過，1014、1018 的決定）。從零建置或換版後有兩項預設是開的：「本次透析」面板、現有功能的小幅遊戲化，這兩項也關（面板等對真實資料驗過才開；遊戲化等長者、社工、護理部看過才開。1116 模擬實測）。1116 院內只關了遊戲化，面板照使用者判斷留著（《[第五次進院紀錄（1116）](record-5-1116.md)》SR-10）
4. 新版自己帶的設定（例子）：`v0.5.0` 系統管理 → 營運參數與選項清單：「院方資料未更新提示的起始時刻」`8`、「結束時刻」`23`（迭代 32.1 的預設，不必改）；「院方床位轉床號的方式」是 `0`（不是就改回 `0`，記下原本是多少）

新版第一次啟動時可能**自己**補進一些東西（`v0.4.0` 是隨版本帶入的衛教草稿、四條判斷規則的草稿、記憶相簿的預設圖卡、指標定義的變更紀錄），**都不必處理**。

| 症狀 | 處置 |
|---|---|
| `api` 一直 `Restarting` | `docker compose --env-file $cfg logs api --tail 30` 抄最後幾行，那裡會說是哪一條設定被拒。看不懂就照 W-20 退回 |
| 日誌的「伺服器時區」不是 `Asia/Taipei` | 後端會拒絕啟動。不要自己改主機時區，找資訊室 |
| 放行檢查什麼都沒印、護理站 `Failed to fetch` | Ctrl＋F5；仍不行照《[護理站登不進去與主機位址](ref-login.md)》 |
| 護理站 `工作ID 或密碼錯誤` | 有連到後端，帳號或密碼不對；換版不會改密碼 |
| 登入後畫面壞掉、某個頁面打不開 | 抄下畫面上的字與網址。主線（登入、簡易版、系統管理）能用就繼續，不能用就照 W-20 退回 |
| 有功能開關是開的（上面那兩項以外） | 關掉，記下是哪一個，回來告訴開發端 |

#### ⑥ 換版之後

1. 備份一次並證明還原得回來：照《[備份、還原與關服務](ref-backup-shutdown.md)》第 1 節
2. 院方准的話做一次重新開機測試（compose 的 `restart` 改過的版本一定要做）：照《[從零部署本系統之二：容器路線的原冊](ref-fresh-install-detail-2.md)》W-18
3. 🏥 第一個班次留人；紀錄寫下 `<新 tag>`、它的 commit、更新前備份的檔名（雜湊只寫演練紀錄與私人紀錄）、建置與 `db-update` 的時間

---

下一份：《[本系統換版與退回（第 2 份，第 3～4 節，W-20）](ref-upgrade-2.md)》｜[部署手冊目錄](index.md)

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|
| [1118](https://94sh09sh19sh.github.io/hd-docs/1118/deployment/ref-upgrade/) | 2026-11-18 | 首次定版。1117 部署手冊整套重寫時由舊冊改寫而成（舊冊號見目錄最後的對照），步驟編號不變；1118 照每份約 300 行的上限拆檔，後段移到同一套的下一份 |

[← 回部署手冊目錄](index.md)
