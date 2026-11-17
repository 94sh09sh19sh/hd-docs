# 本系統換版與退回

> - 狀態：**現行**（常備參考）。院內主機 1116 起是本系統 `v0.5.0`，下一次換版、出問題要退回，都照這一份；進院冊只寫那一趟的順序並連過來
> - 1117 由舊的第十一冊第 6 節（W-19 更新、W-20 回退）改寫，併入舊第二十三冊附錄一（退回 `v0.4.0`）、舊第十八冊附錄二（退回 `v0.3.0`）、舊第二十冊附錄二（退回 `v0.4.0`，內容與第二十三冊附錄一相同），以及舊第十八冊 J-15～J-19、舊第二十三／二十四冊 SY-04～SY-05、舊第二十冊 GO-05～GO-06 裡每次換版都一樣的出錯處置；各趟的具體版本留在第 0 節與各步驟的例子
> - 編號：沿用 `W-19`（換版）、`W-20`（退回）；W-19 底下分成 ①～⑥ 六小步

## 摘要

- 換版＝`git checkout <新 tag>` → 補 `.env` → `build` 新映像檔 → 停 `api`、跑 `db-update`（更新前備份＋驗證還原＋套用遷移＋寫紀錄）→ `up -d` → 確認、備份還原一次
- **程式可以退版，資料庫不能把遷移倒回去**：退回＝舊 tag＋舊映像檔＋更新前那份備份，換版之後寫進去的資料（含讀檔同步進來的、改過的密碼與帳號、註冊的平板）一起消失，所以越早決定越好
- `db-update` 第 3 段印的備份檔名（`hd-before-update-<時間>.db`）與 SHA-256 是退回唯一的依據，一定要抄
- 舊映像檔不刪：新版穩定之前，那是唯一退得回去的東西
- 每一版要補的 `.env` 行、遷移數不一樣：開發端出發前照第 1.3 節查，歷次的實況在第 0 節
- 🏥 排在非透析時段（首波開始使用前例外，DEP-32 1116），換版後第一個班次要有人在；🧪 每個要帶進院的 tag 先在開發機照這一份整輪走過，含真的退一次（第 4 節）
- 登不進去照《[護理站登不進去與主機位址](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-login/index.md)》；備份還原驗證照《[備份、還原與關服務](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-backup-shutdown/index.md)》

## 0. 現在的版本與歷次換版

| 日期   | 換版                  | 遷移                                                                       | `.env`                                              | 外殼／APK                                                                                          | 結果                                                                                                                                                      |
| ------ | --------------------- | -------------------------------------------------------------------------- | --------------------------------------------------- | -------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1001   | 從零部署 `v0.3.0`     | —                                                                          | 全新填                                              | 第一次建                                                                                           | 《[第二次進院紀錄（1001）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/record-2-1001/index.md)》                                             |
| 1029   | `v0.3.0` → `v0.4.0`   | 19 個，全部只做加法                                                        | 多一個必填 `HD_EXPORT_DIR`，另兩行院方 API 變數留空 | 不換、APK 不重建                                                                                   | 一路沒出錯；建置不到一分鐘（主機有快取），見《[第三次進院紀錄（1029）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/record-3-1029/index.md)》 |
| 1116   | `v0.4.0` → `v0.5.0`   | 3 個，只做加法（迭代 30.4 連點成畫、32 院方資料讀檔、32.1 未更新提示時段） | 補四行院方資料讀檔設定，先留空，啟用讀檔時才填      | 不換、APK 不重建                                                                                   | 建置 68 秒、`db-update` 成功、讀檔啟用，見《[第五次進院紀錄（1116）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/record-5-1116/index.md)》   |
| 下一次 | `v0.5.0` → `<新 tag>` | 1117 時 master 在 `v0.5.0` 之後沒有新遷移                                  | 1117 時範本只修了一行斷掉的註解（第 1.3 節）        | 1117 時 compose 沒改；`restart` 預定在下一個 tag 改（舊第二十四冊 SY-M4 例外），改了要重驗重新開機 | —                                                                                                                                                         |

1116 之後院內主機的狀態：`api`、`nurse-web`、`patient-web` 是 `hd-tablet-care:v0.5.0`，`ai-gateway` 仍是 `v0.4.0`（兩版之間閘道沒改、AI 關著，1116 沒建它）；`.env` 的讀檔設定已填（`HD_DIALYSIS_LIST_DIR`、`COMPOSE_FILE` 帶 `docker-compose.dialysis-files.yml`）。主機現況的唯一真本是《[院內主機現況與未完成事項](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-status/index.md)》。

開工三行（＝《[從零部署本系統](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fresh-install/index.md)》V-09；PowerShell 關掉再開就要重打，`couldn't find env file` 十次有九次是忘了這三行）：

```
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

```
git diff --stat <舊 tag> <新 tag> -- apps/api/prisma/migrations deploy/hospital.env.example docker-compose.yml docker-compose.dialysis-files.yml docker-compose.lab-files.yml services/ai-gateway services/shell-builder/shell.pin
```

| 有變動的                           | 代表                                | 寫進當趟進院冊                                                                                                                                     |
| ---------------------------------- | ----------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| `apps/api/prisma/migrations`       | 有新遷移，`db-update` 第 5 段會套用 | 幾個、是不是只做加法                                                                                                                               |
| `deploy/hospital.env.example`      | `.env` 可能要補行                   | 補哪幾行、先留空還是要填、貼在哪                                                                                                                   |
| `docker-compose*.yml`              | 服務、掛載或 `restart` 變了         | 有沒有新的必填變數（compose 會停在「請設定 …」）；`restart` 變了要重驗重新開機                                                                     |
| `services/ai-gateway`              | 閘道改了                            | W-19 ③ 要加 `--profile ai` 一起建                                                                                                                  |
| `services/shell-builder/shell.pin` | 外殼換版                            | APK 要重建、平板要重裝（《[平板與外殼 App](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-tablet/index.md)》）；沒變就不必（DEP-20） |

`v0.5.0` → master（1117）：只有 `deploy/hospital.env.example` 修了一行（`v0.5.0` 範本第 98 行斷掉的註解接回去），其他都沒變。

## 2. 換版

### W-19 換版（DEP-19）

#### ① 下載新版

```
git fetch --tags
git checkout <新 tag>
git describe --tags
```

沒有建置快取、或想先把基底映像下載好（1029 有做，1116 沒做）：

```
docker pull node:20-bookworm-slim
```

**成功**

| 看什麼                | 應該是                                                                                                                                 |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `git checkout`        | `Previous HEAD position was …` 與 `HEAD is now at …` 兩行，正常（原本就停在舊 tag，所以不會再印 `detached HEAD` 那一大段；印了也正常） |
| `git describe --tags` | **正好是** `<新 tag>`，後面沒有 `-3-g1a2b3c4` 這種尾巴                                                                                 |
| `docker pull`         | 最後是 `Status: Downloaded newer image for …` 或 `Status: Image is up to date for …`                                                   |

| 症狀                                                          | 處置                                                                                                                                                 |
| ------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| `git fetch` 說 `Permission denied (publickey)`                | 部署金鑰被拿掉了。`ssh -T github-hd-tablet-care` 看一下，印出 `Hi 94sh09sh19sh/hd-tablet-care!…` 才對；不是的話打電話給開發端（repo 管理者）重新登記 |
| `Connection reset by … port 22`                               | 網路切斷連線，再打一次                                                                                                                               |
| `error: pathspec '<新 tag>' did not match`                    | tag 沒推上去，或打錯字                                                                                                                               |
| `git describe` 後面有尾巴（例如 `-3-gabc123`）                | 不在 tag 上，重打 `git checkout <新 tag>`                                                                                                            |
| `git checkout` 說 `Your local changes … would be overwritten` | 有人改過 repo 裡的檔案。**停手**，不要加 `--force`                                                                                                   |
| `docker pull` 出現 `no such host`                             | 同 ③ 那一列                                                                                                                                          |

新版的 compose 檔多了必填變數時，從這一刻起到 ② 補好 `.env` 之前，每一條 `docker compose` 指令都會停在「請設定 …」（1029 是 `HD_EXPORT_DIR`）。這是對的，② 補上就好。

#### ② 補 `.env`

```
notepad $cfg
```

1. `HD_IMAGE_TAG` 改成 `<新 tag>`
1. 照 `deploy\hospital.env.example` 補這一版新增的行（第 1.3 節查出來的）。**只貼新增的那幾行，不要整段複製範本**，貼在跟範本同樣的位置；`.env` 已經有的變數不要再貼一次
1. 存檔（記事本問編碼就選 UTF-8，不要改檔名），然後：

```
docker compose --env-file $cfg config --quiet
git describe --tags
Select-String -Path $cfg -Pattern '^(HD_IMAGE_TAG|HD_EXPORT_DIR|HD_SHELL_SIGNING|LLM_PROVIDER|HOSPITAL_API_BASE_URL|HD_SIMULATION_DEPLOYMENT)='
Select-String -Path $cfg -Pattern '^[^#].*(<|>|hd-server|localhost)'
```

| 哪一條                                              | 應該是                                                                                                         |
| --------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| `config --quiet`                                    | 什麼都沒印                                                                                                     |
| `HD_IMAGE_TAG`                                      | 與 `git describe --tags` 一字不差                                                                              |
| `HD_EXPORT_DIR`                                     | `C:\hd\hd-tablet-care\export`                                                                                  |
| `HD_SHELL_SIGNING`                                  | `hospital`（🧪 `dev`）                                                                                         |
| `LLM_PROVIDER`                                      | `mock`                                                                                                         |
| `HOSPITAL_API_BASE_URL`、`HD_SIMULATION_DEPLOYMENT` | 等號後面空白，或根本沒有這兩行（沒寫等於空白，正是院內要的）。🧪 `HD_SIMULATION_DEPLOYMENT` 照開發端填的，不動 |
| 最後一條                                            | 什麼都沒印（沒有照抄範例、沒有 `localhost`、沒有忘了換掉的 `<`、`>`）                                          |

**歷次要補的行**（例子；下一次照第 1.3 節查）：

- `v0.3.0` → `v0.4.0`（1029）：在 `HD_CONFIG_DIR=` 那一行下面加 `HD_EXPORT_DIR=C:\hd\hd-tablet-care\export`（資料夾不必先建；研究資料取出的位置，與備份資料夾分開，見《[取出資料](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-data-export/index.md)》）；檔案最後加 `HOSPITAL_API_BASE_URL=`、`HD_SIMULATION_DEPLOYMENT=` 兩行，等號後面都留空（不加也能跑，加了讓 `.env` 與新版範本長得一樣）
- `v0.4.0` → `v0.5.0`（1116）：照範本「院方資料：讀抓取腳本存下的檔」那一段補四行，**都先留空**，`COMPOSE_FILE` 那一行維持註解（讀檔要等啟用前的條件都過才開，見《[讀檔：啟用、檢查、停用](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-dialysis-files/index.md)》）：

```
HD_DIALYSIS_LIST_DIR=
HD_LAB_DIR=
# COMPOSE_FILE=docker-compose.yml;docker-compose.dialysis-files.yml
HOSPITAL_LAB_FIELD_MAP=
```

這四行貼在 `# --- 院方透析清單 API` 那一段的上面。🏥 院內的 `.env` 是更早的範本建的，**沒有** `# --- 院方透析清單 API` 那一段（1116 現場遇到）：貼在 `# --- 其他營運參數` 那一行的上面，`HOSPITAL_API_BASE_URL`、`HD_SIMULATION_DEPLOYMENT` 也不用補。`v0.5.0` 範本那一段的第 98 行是一行斷掉的註解「aw_txt 與 hb-status.json）」（`hospital_dataset\raw_txt` 的 `\r` 寫入時被當成換行），整段複製會帶進來、compose 就讀不到 `.env`（1116 模擬實測）；master 已修，下一個 tag 起的範本沒有這一行

| 症狀                                                                       | 處置                                                                                                                                                                                           |
| -------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `required variable HD_… is missing a value: 請設定 …`                      | 冒號後面寫的就是還缺什麼，照範本補上                                                                                                                                                           |
| `failed to read …\.env: line N: unexpected character … in variable name …` | `.env` 第 N 行不是註解也不是「名稱=值」。最常見是整段複製了 `v0.5.0` 範本、帶進那一行斷掉的「aw_txt 與 hb-status.json）」。`notepad $cfg` 刪掉第 N 行（或在開頭加 `#`），再打 `config --quiet` |
| `couldn't find env file`                                                   | `$cfg` 路徑打錯，或這個 PowerShell 視窗還沒輸入開工三行                                                                                                                                        |
| `HD_SHELL_SIGNING` 不是 `hospital`（🏥）                                   | **停手**，不要改它                                                                                                                                                                             |
| `HD_SIMULATION_DEPLOYMENT` 有值（🏥）                                      | 清空。院內主機這一格永遠空白                                                                                                                                                                   |
| 有 `HIGH_RISK_WRITTEN_CONFIRMATION` 或 `SHOWCASE_MODE` 這一行              | 刪掉（`v0.4.0` 起不讀，留著只會讓人看不懂）                                                                                                                                                    |

#### ③ 建置

```
docker compose --env-file $cfg build
docker images hd-tablet-care
```

主機有之前建置的快取時一分鐘左右就好（1029 不到一分鐘、1116 68 秒），看到 `Built` 就算有建；沒有快取約十分鐘，畫面一直捲動是正常的。

**成功**：最後出現 `Image hd-tablet-care:<新 tag> Built`；`docker images` 看得到舊 tag 與 `<新 tag>` **兩個**。**舊 tag 的映像檔不要刪**（W-20 要用）。到這裡為止服務還是舊版在跑，護理站照樣用得了。

AI 閘道：`git diff` 看到 `services/ai-gateway` 有改、而且閘道在跑（`docker ps` 有 `ai-gateway`），`build` 與之後的 `up -d` 都加 `--profile ai`，閘道才會跟著換新版（1029 J-20 起的規則）。閘道沒改、AI 關著，可以不建它，閘道留在舊版（1116 的做法：`ai-gateway` 仍是 `v0.4.0`）。

| 症狀                                                                                  | 處置                                                                                                                                                                    |
| ------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `failed to resolve source metadata for docker.io/library/node`，後面有 `no such host` | Docker 查不到 Docker Hub 的網域。依序：① 同一條再打一次；② 工作列的 Docker 圖示按右鍵 → Restart，等變綠再打；③ 仍不行，請資訊室看院內 DNS。用了哪一個辦法才過，寫進紀錄 |
| `npm error code ETIMEDOUT` 或 `ECONNRESET`                                            | 網路不穩，再打一次；已下載的層會沿用                                                                                                                                    |
| `pull access denied for hd-tablet-care`                                               | 打成 `up` 了，先 `build`。本系統的映像檔一律就地建置，不從任何地方拉（DEP-39）                                                                                          |
| 任何提到 `binaries.prisma.sh` 的錯誤                                                  | 映像檔建壞了（引擎沒在建置時取得）。重建，**不要在執行期開網路讓它下載**（DEP-30）                                                                                      |

#### ④ 停後端、更新資料庫

🏥 先確認現在沒有透析、已經跟護理站講過（1029 在治療中停了後端、沒先講，舊第十八冊之一 O-08）。這一步到 ⑤ `up -d` 之間護理站會看到斷線紅框，`up -d` 之後就會消失。

三行，第三行是一整行，不要斷開：

```
$tag = git describe --tags
docker compose --env-file $cfg stop api
docker compose --env-file $cfg run --rm --no-deps api node apps/api/scripts/db-update.mjs --note "<舊 tag> → $($tag)（第 N 次進院）"
```

第一行把 ① 確認過的版本存進 `$tag`，`--note` 的說明就自動帶上，**不必手改**（1029 照抄成字面的 `<新 tag>`）。打 `$tag` 看一下，應該正好是 `<新 tag>`。`--note` 只改 `<舊 tag>` 與 `第 N 次進院`，例如 1116 是 `"v0.4.0 → $($tag)（第五次進院）"`。

`db-update.mjs` 先量備份目的地的空間（`備份目的地可用 … MB，這次更新需要 … MB，夠`），印 `版本更新流程（《資料庫使用規範》第 18 條）`、執行身分、目標版本（`package.json` 的號碼加「｜正式環境設定」），接著六段，任何一段沒過就停，資料庫不會被動到：

| 段    | 標題                                     | 會印                                                                                                                                                                   |
| ----- | ---------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `[1]` | 確認服務已停止（DEP-19 第 1 步）         | `沒有服務在回應，可以繼續`。它問的是 compose 給的 `UPDATE_PROBE_URL=http://api:3000/api/health`（正在跑的 `api`），不是一次性容器自己                                  |
| `[2]` | 開啟更新紀錄（規範 18.4）                | `前一次成功更新的版本：…`（第一次是「這是第一次留下紀錄」）                                                                                                            |
| `[3]` | 更新前備份（規範 18.1 第 1 關）          | `hd-before-update-<時間>.db（… bytes）`、`SHA-256：<64 碼>`。**這兩樣抄下來**，W-20 要用。檔名時間是 UTC，比台灣少 8 小時（台灣 15:10 是 `…T0710…`）                   |
| `[4]` | 驗證備份還原得起來                       | `完整性檢查 ok；護理端帳號 N、病人 N、綁定 N、求助 N、稽核紀錄 N`。帳號數是護理端帳號資料表的列數，連登入不了的系統帳號一起算（1116 印 3，實際能登入的只有管理者一個） |
| `[5]` | 套用既有遷移（DEP-31：不是開發用的那支） | `套用了 N 個遷移：…`，或 `沒有待套用的遷移`                                                                                                                            |
| `[6]` | 寫入更新紀錄                             | `更新紀錄與稽核軌跡都已寫入`                                                                                                                                           |

**成功**：最後印出「**更新完成。接下來的三件事是人要做的：**」（啟動服務確認主線功能、舊版映像檔先留著、第一個班次要有人盯著），再一句「要退回去的話：程式可以退版，資料庫不行退版」與這次的備份檔名。

| 症狀                                                                               | 處置                                                                                                                                                                          |
| ---------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `更新中止：後端服務還在執行。…`                                                    | 上一行的 `stop api` 沒做或沒成功，再打一次 `stop api`。**不要加 `--allow-running`**，那是演練用的                                                                             |
| `更新中止：備份目的地可用空間 … MB，不足以完成這次更新。需要 … MB…`                | 需要＝資料庫大小 ×2＋保留下限 `DB_DISK_MIN_FREE_MB`（預設 1024 MB）。主機共用，先問資訊室是誰佔掉空間；不要自己刪別人的東西（DEP-37）                                         |
| `更新中止：備份沒有成功完成，更新到此為止：…`                                      | 備份目錄寫不進去或空間不夠。這一關不過就不往下走                                                                                                                              |
| `更新中止：備份還原後的完整性檢查未通過：…`、`…是一顆空的資料庫，這份備份不可信。` | 資料庫本身可能有問題。**不要往下換**，整段抄下來打電話給開發端                                                                                                                |
| `更新中止：DATABASE_URL 指向的資料庫檔案不存在，這不是一次更新，是一次全新安裝。`  | 資料卷不是原本那一個，或 `/data/hd.db` 不見了。**停手**，`docker volume ls --filter name=hd-tablet-care` 抄下來                                                               |
| `更新中止：套用遷移失敗（結束狀態 N）：…`                                          | 備份已做、已驗證，資料庫在遷移那一步停下。整段抄下來，照下一列讓舊版回來                                                                                                      |
| 其他任何「中止」                                                                   | 每一種都會接一句「資料庫沒有被改動」。整段抄下來，`HD_IMAGE_TAG` 改回舊 tag、`git checkout <舊 tag>`、`docker compose --env-file $cfg up -d` 讓舊版的後端回來，打電話給開發端 |

「中止」之後重跑：排除原因後再打一次第三行（訊息裡寫的 `npm run db:update` 是開發機的寫法，主機上一律用上面那條 `docker compose … run`）。

#### ⑤ 啟動新版、確認

```
docker compose --env-file $cfg up -d
docker ps --format "{{.Names}}  {{.Image}}  {{.Status}}"
curl.exe -s http://localhost:13000/api/health
curl.exe -s -i -H "Origin: http://<IP>:18080" http://<IP>:13000/api/health | Select-String Access-Control-Allow-Origin
[Console]::OutputEncoding = [Text.Encoding]::UTF8; docker compose --env-file $cfg logs api --tail 40
```

| 看什麼      | 應該是                                                                                                                                                                                                              |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `docker ps` | `api`、`nurse-web`、`patient-web` 的映像檔是 `hd-tablet-care:<新 tag>`、`Up`；`ai-gateway` 沒跟著建的話仍是舊 tag，正常                                                                                             |
| health      | `{"status":"ok",…}`                                                                                                                                                                                                 |
| 放行檢查    | `Access-Control-Allow-Origin: http://<IP>:18080`                                                                                                                                                                    |
| 日誌        | 「已連線至 SQLite」帶 `journal_mode=WAL、foreign_keys=ON、busy_timeout=5000ms、synchronous=FULL`；「伺服器時區」`Asia/Taipei`；版本標記後面寫「（正式環境設定）」；沒有紅色的 `ERROR`（部署規範第 11 章第 3、7 條） |

然後在護理站的電腦（🏥 要 Windows 密碼、會休眠，請護理師輸入；🧪 連同一個 Wi-Fi 的手機，沒有 Ctrl＋F5，改成關掉分頁重開）：

1. Ctrl＋F5 強制重新整理（舊版的網頁還留在瀏覽器裡），開 `http://<IP>:18080` 用管理者登入；帳號密碼是換版前的（換版不改密碼，登得進去也證明資料留住了）
1. 系統管理 → 稽核軌跡：用途「系統維運」、動作「版本更新完成」那一筆寫著 `--note` 的說明（例如 `v0.4.0 → v0.5.0（第五次進院）`）。「版本更新紀錄」那張表**沒有說明欄**，版本欄是 `apps/api/package.json` 的號碼、不是 git tag：主機第一次更新顯示 `— → 0.1.0`，之後是 `0.1.0 → 0.1.0`，都正常。要對版本看 `docker ps` 的映像檔名稱
1. 功能開關：**全部是關的**（DEP-29、部署規範第 11 章第 18 條；`v0.4.0` 起多了遊戲化、獎勵制度、跑馬燈等很多開關，照預設關著，要開得先讓長者、社工、護理部看過，1014、1018 的決定）。從零建置或換版後有兩項預設是開的：「本次透析」面板、現有功能的小幅遊戲化，這兩項也關（面板等對真實資料驗過才開；遊戲化等長者、社工、護理部看過才開。1116 模擬實測）。1116 院內只關了遊戲化，面板照使用者判斷留著（《[第五次進院紀錄（1116）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/record-5-1116/index.md)》SR-10）
1. 新版自己帶的設定（例子）：`v0.5.0` 系統管理 → 營運參數與選項清單：「院方資料未更新提示的起始時刻」`8`、「結束時刻」`23`（迭代 32.1 的預設，不必改）；「院方床位轉床號的方式」是 `0`（不是就改回 `0`，記下原本是多少）

新版第一次啟動時可能**自己**補進一些東西（`v0.4.0` 是隨版本帶入的衛教草稿、四條判斷規則的草稿、記憶相簿的預設圖卡、指標定義的變更紀錄），**都不必處理**。

| 症狀                                         | 處置                                                                                                                          |
| -------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `api` 一直 `Restarting`                      | `docker compose --env-file $cfg logs api --tail 30` 抄最後幾行，那裡會說是哪一條設定被拒。看不懂就照 W-20 退回                |
| 日誌的「伺服器時區」不是 `Asia/Taipei`       | 後端會拒絕啟動。不要自己改主機時區，找資訊室                                                                                  |
| 放行檢查什麼都沒印、護理站 `Failed to fetch` | Ctrl＋F5；仍不行照《[護理站登不進去與主機位址](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-login/index.md)》 |
| 護理站 `工作ID 或密碼錯誤`                   | 有連到後端，帳號或密碼不對；換版不會改密碼                                                                                    |
| 登入後畫面壞掉、某個頁面打不開               | 抄下畫面上的字與網址。主線（登入、簡易版、系統管理）能用就繼續，不能用就照 W-20 退回                                          |
| 有功能開關是開的（上面那兩項以外）           | 關掉，記下是哪一個，回來告訴開發端                                                                                            |

#### ⑥ 換版之後

1. 備份一次並證明還原得回來：照《[備份、還原與關服務](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-backup-shutdown/index.md)》第 1 節
1. 院方准的話做一次重新開機測試（compose 的 `restart` 改過的版本一定要做）：照《[從零部署本系統之一：容器路線的原冊](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fresh-install-detail/index.md)》W-18
1. 🏥 第一個班次留人；紀錄寫下 `<新 tag>`、它的 commit、更新前備份的檔名（雜湊只寫演練紀錄與私人紀錄）、建置與 `db-update` 的時間

## 3. 退回

### W-20 退回

**什麼時候用**：W-19 ④ 之後，新版的 `api` 起不來、或主線功能壞掉，而現場解不開。**越早決定越好**：程式可以退版，**資料庫不能把遷移倒回去**（規範 18.3、FR-S12），所以這一版動過 schema 時，退回＝「舊程式＋更新前那份備份」，更新之後寫進去的資料一起消失——含啟用讀檔後同步進來的、改過的密碼與建的帳號、註冊的平板。1029 時沒有真實資料，代價是零；首波開始使用之後，代價是那段期間的所有紀錄（DEP-32）。

**要用的那份備份**：W-19 ④ 第 3 段抄的 `hd-before-update-<時間>.db` 與 SHA-256。沒抄到的話：

- 護理端還進得去：系統管理 → 稽核軌跡，「更新前強制備份：\<檔名>（… bytes，SHA-256 …）」那一筆；或「版本更新紀錄」
- 進不去：備份資料夾裡最新的一份，雜湊在旁邊同名的 `.sha256`（前半段那 64 個字）：

```
Get-ChildItem $root\backups\hd-before-update-* | Sort-Object LastWriteTime | Select-Object -Last 2 Name
Get-Content "$root\backups\<備份檔名>.sha256"
```

**做什麼**

1. 程式碼與設定退回：

```
git checkout <舊 tag>
notepad $cfg
```

`HD_IMAGE_TAG` 改回 `<舊 tag>`（舊映像檔還在，不必重建）。舊版不認得的設定照下表處理：

| 退到                     | `.env` 要改的                                                                                                                           |
| ------------------------ | --------------------------------------------------------------------------------------------------------------------------------------- |
| `v0.3.0`（1029 的例子）  | 不必改：`HD_EXPORT_DIR` 與兩個院方 API 的變數留著沒關係（舊版不讀）                                                                     |
| `v0.4.0`（1116 的例子）  | `HD_DIALYSIS_LIST_DIR` 清空、`COMPOSE_FILE` 那一行改回註解（開頭加 `#`）：`v0.4.0` 不認讀檔，也沒有 `docker-compose.dialysis-files.yml` |
| `v0.5.0`（下一次的例子） | 讀檔設定留著（`v0.5.0` 認得）；`<新 tag>` 新增的行照第 1.3 節看舊版讀不讀                                                               |

1. 停後端、把新版的資料庫移到旁邊、還原更新前備份、啟動（第二、三條各是一整行）：

```
docker compose --env-file $cfg stop api
docker compose --env-file $cfg run --rm --no-deps --entrypoint sh api -c "mkdir -p /data/before-rollback && mv /data/hd.db /data/hd.db-wal /data/hd.db-shm /data/before-rollback/ 2>/dev/null; ls -l /data/before-rollback"
docker compose --env-file $cfg run --rm --no-deps api node_modules/.bin/ts-node --project apps/api/tsconfig.json apps/api/scripts/restore-backup.ts --from /backups/<備份檔名> --to /data/hd.db --sha256 <雜湊>
docker compose --env-file $cfg up -d
```

`hd.db` 與 `-wal`、`-shm` 是一組，三個一起移（DEP-09）；`ls -l` 印得出移過去的檔才往下。

1. W-19 ③ 有把閘道一起換新版的話，閘道也退回：`docker compose --env-file $cfg --profile ai up -d ai-gateway`

**成功**

| 看什麼      | 應該是                                                                                                                              |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| 還原輸出    | `[2]` 之後有 `✓ 與備份歷程上的紀錄相符`、`[4] 完整性檢查：ok`、`[5] 下一步：還原的就是 DATABASE_URL 指向的正本，直接啟動服務即可。` |
| `docker ps` | `api`、`nurse-web`、`patient-web` 的映像檔是 `hd-tablet-care:<舊 tag>`                                                              |
| 護理端      | 版本標記是舊版；護理站 Ctrl＋F5 後登得進去                                                                                          |
| 抓取腳本    | 不受影響、照跑（它是主機上的排程，不在 compose 裡）                                                                                 |

**登入要注意**：舊映像檔裡的護理端網頁，寫死的是**建置舊映像檔當時**的 `HD_PUBLIC_API_URL`。舊映像檔建好之後才換過主機位址的話，退回後一定 `Failed to fetch`。1029 先用 `<IP>` 重建了 `v0.3.0` 的網頁才換版，所以退回 `v0.3.0` 也登得進去；1029 之後的 `v0.4.0`、`v0.5.0` 都是用 `<IP>` 建的。

**之後**

- 移到 `/data/before-rollback/` 的那份**先留著**，連同新版出問題的原文帶回給開發端判斷；確定不需要再刪：`docker compose --env-file $cfg run --rm --no-deps --entrypoint rm api -r /data/before-rollback`
- `/data/before-rollback/` 裡已經有上一次退回留下的檔時，第二條的 `mv` 會蓋過去；要留的話先帶回再退
- 新版的映像檔也不要刪
- 護理站照 W-19 ⑤ 的清單再看一次功能開關（舊備份裡的開關狀態是換版前的）

| 症狀                                                                  | 處置                                                                                                                                           |
| --------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| `還原中止：目的檔 hd.db 已存在；還原不覆蓋任何既有檔案，請換一個路徑` | 第二條沒把 `hd.db` 移走：多半是 `stop api` 沒成功、或打錯。看第二條 `ls -l` 的輸出，重打第一、二條                                             |
| `還原中止：找不到備份檔 …`                                            | 檔名打錯（要含 `.db` 的整個檔名），或用了 Git Bash                                                                                             |
| `還原中止：SHA-256 與備份歷程上的紀錄不符，備份檔可能已損毀或被更動`  | 雜湊抄錯；用 `Get-Content` 那一條重新複製。還是不符就打電話給開發端，不要換別份硬還原                                                          |
| `還原中止：完整性檢查未通過：…`                                       | 那份備份壞了。**停手**，`/data/before-rollback/` 不要動，打電話給開發端                                                                        |
| 退回後 `Failed to fetch`                                              | 看上面「登入要注意」；再照《[護理站登不進去與主機位址](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-login/index.md)》第 2 節查 |

## 4. 🧪 開發機演練

每一個要交給院方的 tag，先在開發機上照這一份走一次（DEP-22）：

| #   | 驗什麼                                                                                                                                                                                                           | 這一份的步驟 |
| --- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ |
| 1   | 開發機準備成跟院內主機一樣（上一次離院時的版本、位址用 IP、登得進去、平板佈建好）；這一段由開發端做，手冊不寫                                                                                                    | —            |
| 2   | 換版一次：`<新 tag>` 照 W-19 走完，`更新完成`、更新前備份的檔名與雜湊抄到了                                                                                                                                      | W-19         |
| 3   | 新版登得進去，帳號密碼是更新前的（資料留住了）                                                                                                                                                                   | W-19 ⑤       |
| 4   | 真的退回一次：`<備份檔名>`、`<雜湊>` 用第 2 項抄的；`完整性檢查：ok`、三個服務是舊 tag、手機重開分頁後登得進去。換版之後註冊或建的東西不見了，是對的                                                             | W-20         |
| 5   | 退回後登不進去、`Failed to fetch`：這一份的 W-20 寫錯了，抄下《[護理站登不進去與主機位址](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-login/index.md)》第 2 節第 3 步的結果，回去改這一份再演練 | W-20         |

- 🧪 根目錄 `C:\hd-sim`、管理者 `sim-admin`、`HD_SHELL_SIGNING=dev`；`HD_SIMULATION_DEPLOYMENT` 照開發端填的
- 舊冊的實例：1029 前的演練（《[第三次進院（1029）之二：開發機才做的演練](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-3-system-rehearsal/index.md)》）、1116 前的演練（《[第五次進院（1116）任務二 · 本系統換版上線](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-5-system/index.md)》SY-M3）
- **在 Git Bash 裡照抄會壞的一件事**：Git Bash 會把 `/backups/…`、`/data/…` 這種參數自動轉成 Windows 路徑，還原腳本就會回報找不到備份檔。一律用 PowerShell；非用 Git Bash 不可時，先 `export MSYS_NO_PATHCONV=1`，`--env-file` 也要寫成 `C:/…` 的形式

## 版本歷程

| 定版 | 日期 | 異動 |
| ---- | ---- | ---- |
|      |      |      |

[← 回部署手冊目錄](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/index.md)
