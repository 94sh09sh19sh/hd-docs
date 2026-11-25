# 從零部署本系統之二：容器路線的原冊（第 3～10 節，W-08～W-18）

上層文件：《[從零部署本系統](https://94sh09sh19sh.github.io/hd-docs/1125/deployment/ref-fresh-install/index.md)》

> **狀態：現行（常備參考）。** 容器路線（`git clone` ＋ `docker compose`）原冊的後半，改寫自第十一冊（1117）；照著做的步驟以上層的 `V-xx` 為準。編號 `W-xx`（沿用第十一冊），與上層 `V-xx` 的對照在上層《[第 7 份](https://94sh09sh19sh.github.io/hd-docs/1125/deployment/ref-fresh-install-7/index.md)》的附錄。

## 摘要

- 容器路線原冊的後半（第 3～10 節）；前半（第 0～2 節、W-01～W-07）在《之一》
- 第 3～5 節：W-08～W-18 每一步上層沒寫的內容（第十一冊當時的路徑、`.env` 必填清單、症狀的原因欄）
- 第 6 節更新與回退在《本系統換版與退回》、第 8 節關服務在《備份、還原與關服務》，這裡只留去處
- 第 7 節：開發機實測（DEP-22）「從零」的定義與六項要驗的；Git Bash 照抄會壞，一律用 PowerShell
- 第 9 節：這條路線特有的疑難排解；第 10 節：當初還沒到的元件（都已完成）

______________________________________________________________________

## 3. 取得程式碼

### W-08 建立兩個目錄

照做的步驟：上層 V-09（`$root`、`$cfg` 與開工三行）。

第十一冊當時寫在 D 槽（1001 起院內改用 `C:\hd\hd-tablet-care`）：

```
New-Item -ItemType Directory -Force D:\hd-tablet-care\config, D:\hd-tablet-care\backups | Out-Null
```

`repo` 不先建，由 W-10 的 clone 產生。

**不可以放的地方**：雲端同步資料夾、網路磁碟機代號、RAM 磁碟、`C:\Users\<帳號>\` 底下的桌面／文件／下載（DEP-21 第 2 項、DEP-37）。

______________________________________________________________________

### W-09 產生部署金鑰（DEP-43）

照做的步驟：上層 V-10（指令、SSH 設定檔、出錯表）。

私鑰在主機上產生、不離開主機；**只有公鑰**交給 repo 管理者登記。0922 那種臨時建立、事後要記得刪的個人權杖不再需要。

外殼 App 的 repo 另產生一把（一把部署金鑰只能對應一個 repo），做法在上層 V-20（Y-02）。

`ssh -T github-hd-tablet-care` 成功時看到 `Hi <帳號>/hd-tablet-care! You've successfully authenticated, but GitHub does not provide shell access.`；第一次連線問 `Are you sure you want to continue connecting` 時，核對顯示的指紋是 GitHub 公布的那一組再回答 `yes`。

______________________________________________________________________

### W-10 clone，切到 tag

照做的步驟：上層 V-11。

第十一冊當時的路徑：

```
git clone git@github-hd-tablet-care:94sh09sh19sh/hd-tablet-care.git D:\hd-tablet-care\repo
cd D:\hd-tablet-care\repo
git checkout <tag>
git describe --tags
```

**怎麼知道成功了**：`git describe --tags` 印出的正是交付的 tag，不帶 `-g<雜湊>` 尾巴。

| 症狀                                             | 處置                                 |
| ------------------------------------------------ | ------------------------------------ |
| `HEAD is now at …` 之後出現 detached HEAD 的說明 | 正常。部署本來就不在分支上（DEP-44） |
| `error: pathspec '<tag>' did not match`          | tag 沒推上去，回 W-02                |

**之後每一條 docker 指令都在 `<根目錄>\repo` 底下下。**

______________________________________________________________________

## 4. 設定

### W-11 由範本填 `.env`

照做的步驟：上層 V-12；逐項填法在《[`.env` 怎麼填](https://94sh09sh19sh.github.io/hd-docs/1125/deployment/ref-env/index.md)》（🏥）與《[之一：開發機演練](https://94sh09sh19sh.github.io/hd-docs/1125/deployment/ref-env-simulation/index.md)》（🧪）。

第十一冊當時的必填清單（每一項的範例、填錯會怎樣，在《[`.env` 怎麼填](https://94sh09sh19sh.github.io/hd-docs/1125/deployment/ref-env/index.md)》）：

| 變數                                              | 填什麼                                                                                                                                                                                |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `HD_IMAGE_TAG`                                    | 與 W-10 的 tag 相同                                                                                                                                                                   |
| `HD_BACKUP_DIR`、`HD_CONFIG_DIR`                  | `<根目錄>\backups`、`<根目錄>\config`                                                                                                                                                 |
| `HD_EXPORT_DIR`                                   | `<根目錄>\export`（1027 迭代 28 起；與備份目錄分開，只掛給一次性的 `data-export`，見《[取出資料](https://94sh09sh19sh.github.io/hd-docs/1125/deployment/ref-data-export/index.md)》） |
| `HD_API_PORT`、`HD_NURSE_PORT`、`HD_PATIENT_PORT` | W-07 確認過的三個埠                                                                                                                                                                   |
| `HD_PUBLIC_API_URL`                               | 護理站連得到的後端位址，例如 `http://<主機>:<後端埠>`。**建置時寫進護理端的產物**（DEP-39）                                                                                           |
| `CORS_ORIGINS`                                    | 護理端的實際位址（病人端與後端同一個來源，不必列）                                                                                                                                    |
| `MDM_KIOSK_BASE_URL`                              | 平板要連的病人端位址，**一律 `https://`**（Y-03）                                                                                                                                     |
| `HD_SHELL_SRC_DIR`、`HD_SHELL_SIGNING`            | 外殼 repo 的 clone 位置與簽章用途（Y-03）。**每一條 compose 指令都會檢查前者**，還沒 clone 也先填好路徑                                                                               |
| `JWT_SECRET`                                      | 範本的註解寫的是 `docker run node:…` 那一條；1001 起改用不必連網的 PowerShell 一行（《[`.env` 怎麼填](https://94sh09sh19sh.github.io/hd-docs/1125/deployment/ref-env/index.md)》1.6） |
| `SUPER_ADMIN_*`                                   | 第一個最高權限帳號，首次登入強制改密碼                                                                                                                                                |

`LLM_PROVIDER` 維持 `mock`。**填 `lab` 後端會拒絕啟動**（DEP-40），那是刻意的。

1111 迭代 32 起範本多了讀檔的四行（`HD_DIALYSIS_LIST_DIR`、`HD_LAB_DIR`、`COMPOSE_FILE`、`HOSPITAL_LAB_FIELD_MAP`），從零部署時先留空、`COMPOSE_FILE` 維持註解（《[`.env` 怎麼填](https://94sh09sh19sh.github.io/hd-docs/1125/deployment/ref-env/index.md)》1.12）。

第十一冊當時「少打字」的做法是每次開 PowerShell 先設 `$cfg = "D:\hd-tablet-care\config\.env"`；現在是上層 V-09 的開工三行。

**怎麼知道成功了**：`docker compose --env-file $cfg config --quiet` 沒有任何輸出就是對的。

| 症狀                                                    | 處置                                                 |
| ------------------------------------------------------- | ---------------------------------------------------- |
| `required variable HD_... is missing a value: 請設定 …` | 冒號後面就是要填什麼，補上                           |
| `couldn't find env file`                                | `$cfg` 路徑打錯，或這個 PowerShell 視窗還沒設 `$cfg` |

______________________________________________________________________

### W-12 建立兩個資料卷

照做的步驟：上層 V-13。

**只在第一次部署時做。** 兩個都標成 external，compose 不會建立、`docker compose down -v` 也刪不掉它們（部署規範 3.3）。

______________________________________________________________________

## 5. 建置與啟動

### W-13 建置映像檔

照做的步驟：上層 V-14。

第一次要下載基底映像與套件，約十分鐘。上層沒寫的「原因」欄：

| 症狀                                                           | 原因                       | 處置                                                             |
| -------------------------------------------------------------- | -------------------------- | ---------------------------------------------------------------- |
| `failed to resolve source metadata for docker.io/library/node` | 連不到 Docker Hub          | 回 W-06（上層 V-06 第二段）                                      |
| `npm error code ETIMEDOUT` 或 `ECONNRESET`                     | 連 npm 不穩                | 再跑一次；已經下載的層會沿用                                     |
| `pull access denied for hd-tablet-care`                        | 下的是 `up` 而不是 `build` | 先 `build`。本系統的映像檔一律就地建置，不從任何地方拉（DEP-39） |

______________________________________________________________________

### W-14 套用既有遷移（DEP-31）

照做的步驟：上層 V-15。

| 症狀                                                | 處置                                                                               |
| --------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `SQLite database hd.db created at file:/data/hd.db` | 第一次部署時正常                                                                   |
| 任何提到 `binaries.prisma.sh` 的錯誤                | 映像檔建壞了（引擎沒在建置時取得）。重建，**不要在執行期開網路讓它下載**（DEP-30） |

______________________________________________________________________

### W-15 啟動

照做的步驟：上層 V-16。

`ai-gateway` 與 `shell-builder` **不在清單上是對的**：它們在 `ai`、`shell` 兩個設定檔裡，預設不啟動（後來加的 `data-export`、`hospital-api-sim` 也一樣，在 `export`、`simulation` 設定檔裡）。

______________________________________________________________________

### W-16 確認它是對的那一個

照做的步驟：上層 V-17（四段，含網頁裡寫死的後端位址與 CORS 的查法）。

日誌 `已連線至 SQLite` 那一行完整應該是：`journal_mode=WAL、foreign_keys=ON、busy_timeout=5000ms、synchronous=FULL`。

上層沒寫的「原因」欄：

| 症狀                               | 原因                                       | 處置                                                                                                                                                                                                                  |
| ---------------------------------- | ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 護理站開得了頁面，登入時轉圈後失敗 | `HD_PUBLIC_API_URL` 或 `CORS_ORIGINS` 寫錯 | 改 `.env`，**`HD_PUBLIC_API_URL` 改了要重新 build**（寫在產物裡），`CORS_ORIGINS` 只要 `up -d`（逐步查法在《[護理站登不進去與主機位址](https://94sh09sh19sh.github.io/hd-docs/1125/deployment/ref-login/index.md)》） |
| `api` 一直 Restarting              | 設定被後端拒絕                             | `logs api` 最後幾行會說哪一條（時區、連接埠、`lab`…），照訊息改                                                                                                                                                       |

______________________________________________________________________

### W-17 備份一次，並驗證還原得起來

照做的步驟：上層 V-18。

「有備份」和「備份能用」是兩件事（規範 8.1）。

______________________________________________________________________

### W-18 重新開機測試（DEP-21 第 4 項）

照做的步驟：上層 V-19（含 1116 開發機實測：Quit Docker Desktop 後服務沒有自己回來）。

**這一條決定這條路線在院內能不能用。** `restart: unless-stopped` 只管 Docker 起來之後；Docker Desktop 是隨使用者登入啟動的程式，**沒人登入，容器就不會起來**。

第十一冊當時的做法是「照院方平常的方式登入（~~或不登入，看院方答覆~~）」；**1007 答覆**：斷電後由護理長以 Administrator 重新登入，這一步就是模擬護理長。

**沒過的話**：記下實況（有沒有自動登入、Docker Desktop 有沒有起來），這是 Q-27 要談的事，不在現場硬改院方的登入設定。

______________________________________________________________________

## 6. 更新與回退

移到《[本系統換版與退回](https://94sh09sh19sh.github.io/hd-docs/1125/deployment/ref-upgrade/index.md)》（W-19 更新七步、W-20 回退）。

______________________________________________________________________

## 7. 開發機實測（DEP-22）

**每一個要交給院方的 tag，都先在開發機上照上層走一次**（上層的 🧪 標記就是這一輪要改做的）。 「從零」的意思：

- **全新的 clone**，不是平常開發的那個工作目錄
- **全新的資料卷**：先確認 `docker volume ls` 裡沒有 `hd-tablet-care-*`，有就先照上層 V-32 撤除
- **只用 Git 與 Docker**，指令與院內一字不差；開發機上的 Node.js 在這一輪裡不得被用到
- 設定照範本另填一份，埠挑開發時沒在用的（例如 13000、18080、18081）。位址第十一冊當時寫「用 `localhost`」；**1001 起改用開發機的區網 IP**，院內那種登不進去的情形才練得到（《[`.env` 怎麼填之一：開發機演練](https://94sh09sh19sh.github.io/hd-docs/1125/deployment/ref-env-simulation/index.md)》）

| #   | 驗什麼                                                                                                                              | 步驟                                                                                                              |
| --- | ----------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| 1   | 從 clone 到服務起來，全程沒有人工補步驟，每一步輸出存檔                                                                             | W-08～W-17（上層 V-09～V-18）                                                                                     |
| 2   | `npm run verify:iteration11 -- --live --env-file <設定目錄>\.env`：`down -v` 之後資料還在、繫結掛載只有兩個、正式環境設定拒絕 `lab` | 這一條是唯一允許用 Node 的，**它是驗收，不是部署步驟**（上層 V-31，連同 `verify:iteration12`、`13`）              |
| 3   | 更新一次：打一個測試 tag，照 W-19 走完                                                                                              | 《[本系統換版與退回](https://94sh09sh19sh.github.io/hd-docs/1125/deployment/ref-upgrade/index.md)》W-19           |
| 4   | 回到上一版，資料完整                                                                                                                | 《[本系統換版與退回](https://94sh09sh19sh.github.io/hd-docs/1125/deployment/ref-upgrade-2/index.md)》W-20         |
| 5   | 開發手機裝外殼、釘住、護理端看得到（迭代 12 起）                                                                                    | 上層 V-20～V-28、《[平板與外殼 App](https://94sh09sh19sh.github.io/hd-docs/1125/deployment/ref-tablet/index.md)》 |
| 6   | AI 經 SSH 通道接實驗室閘道跑一次（迭代 13 起）                                                                                      | 《[AI 閘道](https://94sh09sh19sh.github.io/hd-docs/1125/deployment/ref-ai-gateway/index.md)》                     |

1116 起換版的開發機演練另有判定表（十一項，含驗正式設定擋得住模擬、退回演練），在《[第五次進院（1116）任務二 · 本系統換版上線](https://94sh09sh19sh.github.io/hd-docs/1125/deployment/visit-5-system-2/index.md)》SY-M1～SY-M4。

**在 Git Bash 裡照抄會壞的一件事**：Git Bash 會把 `/backups/…`、`/data/…` 這種參數自動轉成 Windows 路徑，還原腳本就會回報找不到備份檔。**一律用 PowerShell**；非用 Git Bash 不可時，先 `export MSYS_NO_PATHCONV=1`， `--env-file` 也要寫成 `C:/…` 的形式。

______________________________________________________________________

## 8. 關服務

移到《[備份、還原與關服務](https://94sh09sh19sh.github.io/hd-docs/1125/deployment/ref-backup-shutdown/index.md)》（暫停、停用、撤除三種深度的容器版指令）。

______________________________________________________________________

## 9. 疑難排解（這條路線特有的）

| 症狀                                                                       | 原因                                                                                 | 處置                                                                                                                                  |
| -------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------- |
| `Error code 14: Unable to open the database file`                          | 資料卷不是由 compose 掛上，或手動開的容器以 root 建了檔                              | 只用上層的指令；手動開過的容器全部刪掉，重新 `up -d`                                                                                  |
| `正式環境設定下不得使用 LLM_PROVIDER=lab`                                  | `.env` 抄了開發機的設定                                                              | 改回 `mock`（或迭代 13 之後的 `onprem`）。這是刻意擋的（DEP-40）                                                                      |
| `時區…不是正式環境要求的 Asia/Taipei`                                      | compose 的 `TZ` 被改過                                                               | 還原 compose 檔。compose 檔不在主機上改，要改回開發端改、打新 tag                                                                     |
| `docker compose --profile ai build` 失敗：找不到 Dockerfile                | 0926 當時 AI 閘道在迭代 13 才補上                                                    | 迭代 13 起已有閘道；現在再出現就是 clone 不完整或 tag 太舊，核對 `git describe --tags`                                                |
| `bind source path does not exist`                                          | `HD_BACKUP_DIR` 或 `HD_CONFIG_DIR` 指的目錄不存在                                    | 回 W-08（上層 V-09）                                                                                                                  |
| 連接埠 `address already in use`                                            | 同機別的專案佔用                                                                     | 回 W-07 換埠，登記後改 `.env`                                                                                                         |
| 平板或護理站開得了頁面，資料打不回來                                       | 產物裡寫死的後端位址不對                                                             | W-16 表格第一列                                                                                                                       |
| `failed to read …\.env: line N: unexpected character … in variable name …` | `.env` 第 N 行不是註解也不是「名稱=值」；`v0.5.0` 範本第 98 行就是這樣一行斷掉的註解 | 刪掉第 N 行（或開頭加 `#`），見上層 V-12                                                                                              |
| `docker-compose.lab-files.yml 要配 HD_LAB_DIR`                             | `COMPOSE_FILE` 多帶了 `docker-compose.lab-files.yml`，`HD_LAB_DIR` 卻是空的          | `COMPOSE_FILE` 只留有填的那幾個檔（《[`.env` 怎麼填](https://94sh09sh19sh.github.io/hd-docs/1125/deployment/ref-env/index.md)》1.12） |

______________________________________________________________________

## 10. 還沒到的部分（0926 當時）

0926 第十一冊寫的時候還沒做完的三個元件，現在都已完成：

| 元件                             | 0926 當時                                            | 現在                                                                                                                         |
| -------------------------------- | ---------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `ai-gateway`（AI 閘道）          | 服務、設定檔掛載、`ai` 設定檔已定；程式在**迭代 13** | 迭代 13 完成，上層 V-29、V-30；《[AI 閘道](https://94sh09sh19sh.github.io/hd-docs/1125/deployment/ref-ai-gateway/index.md)》 |
| `shell-builder`（外殼 APK 建置） | **0927 迭代 12 完成**                                | 上層 V-21～V-23；《[平板與外殼 App](https://94sh09sh19sh.github.io/hd-docs/1125/deployment/ref-tablet/index.md)》            |
| 病人端下載頁、HTTPS              | **0927 迭代 12 完成**                                | 上層 V-24（Y-07）                                                                                                            |

______________________________________________________________________

上一份：《[從零部署本系統之一：容器路線的原冊（第 0～2 節，W-01～W-07）](https://94sh09sh19sh.github.io/hd-docs/1125/deployment/ref-fresh-install-detail/index.md)》｜[部署手冊目錄](https://94sh09sh19sh.github.io/hd-docs/1125/deployment/index.md)

## 版本歷程

| 定版                                                                                       | 日期       | 異動                                                                                                 |
| ------------------------------------------------------------------------------------------ | ---------- | ---------------------------------------------------------------------------------------------------- |
| [1118](https://94sh09sh19sh.github.io/hd-docs/1118/deployment/ref-fresh-install-detail-2/) | 2026-11-18 | 首次定版。1118 照每份約 300 行的上限由《從零部署本系統之一：容器路線的原冊》拆出，內容與步驟編號不動 |

[← 回部署手冊目錄](https://94sh09sh19sh.github.io/hd-docs/1125/deployment/index.md)
