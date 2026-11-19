# `.env` 怎麼填（第 2 份，第 2～6 節）

上層文件：《[`.env` 怎麼填](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-env/index.md)》

> **狀態：現行（常備參考）。** 1117 由第十五冊之一改寫，節號沿用（這一份是第 2～6 節）；沒有步驟編號。第 0～1 節（開始之前、逐項填）在第 1 份。

## 摘要

- 第 2 節：從零部署時（讀檔還沒啟用）填好的整份樣子；啟用讀檔後只改 `HD_DIALYSIS_LIST_DIR`、`COMPOSE_FILE` 兩行
- 第 3 節：`config --quiet` 什麼都沒印、`Select-String` 查不到範例與 `localhost`，再用眼睛逐項核對
- 第 4 節：`.env` 裡有登入簽章金鑰與初始密碼，只存在院內主機的設定目錄；紀錄只記變數、不記值
- 第 5 節：改了哪一項決定要 `up -d` 還是先 `build`；`MDM_KIOSK_BASE_URL` 原則上不改、`HD_SHELL_SIGNING` 不准改
- 第 6 節：院內主機上已經有一份（1001 填的，1029、1116 補過），不要再從範本複製蓋掉，照三條指令核對
- 每一項填什麼在第 1 份第 1 節

## 2. 填好的樣子

照 0.3 節的假設、**從零部署時**（讀檔還沒啟用）填完，會像這樣（說明行省略，順序與範本相同）。**角括號那幾處要換成你自己的，`<主機>` 三處換成同一個值**：

```
HD_IMAGE_TAG=v0.5.0

HD_BACKUP_DIR=C:\hd\hd-tablet-care\backups
HD_CONFIG_DIR=C:\hd\hd-tablet-care\config
HD_EXPORT_DIR=C:\hd\hd-tablet-care\export

HD_API_PORT=13000
HD_NURSE_PORT=18080
HD_PATIENT_PORT=18081

HD_PUBLIC_API_URL=http://<主機>:13000
CORS_ORIGINS=http://<主機>:18080
MDM_KIOSK_BASE_URL=https://<主機>:18081

HD_SHELL_SRC_DIR=C:\hd\hd-tablet-care\hd-kiosk-shell
HD_SHELL_SIGNING=hospital
KIOSK_SHELL_MIN_VERSION=

JWT_SECRET=<V-12 當場產生的那一串>
JWT_EXPIRES_IN=8h

SUPER_ADMIN_WORK_ID=<護理長給的工號>
SUPER_ADMIN_INITIAL_PASSWORD=<臨時密碼>
SUPER_ADMIN_DISPLAY_NAME=<護理長給的名字>

BACKUP_DAILY_AT=03:00
DB_DISK_MIN_FREE_MB=1024

LLM_PROVIDER=mock
LLM_ENDPOINT=
LLM_API_KEY=
LLM_MODEL_ID=
LLM_TIMEOUT_SECONDS=150
LLM_HEALTH_TIMEOUT_SECONDS=5

HD_DIALYSIS_LIST_DIR=
HD_LAB_DIR=
# COMPOSE_FILE=docker-compose.yml;docker-compose.dialysis-files.yml;docker-compose.lab-files.yml
HOSPITAL_LAB_FIELD_MAP=

HOSPITAL_API_BASE_URL=
HD_SIMULATION_DEPLOYMENT=

BINDING_MAX_HOURS=6
BINDING_EXPIRY_SWEEP_SECONDS=60
SYMPTOM_TREND_WINDOW_DAYS=30
SYMPTOM_TREND_REPORT_LIMIT=10
DEVICE_ONLINE_THRESHOLD_SECONDS=90
REALTIME_HEARTBEAT_SECONDS=20
```

**啟用讀檔之後**只改這兩行（院內主機 1116 起就是這樣），其他不動：

```
HD_DIALYSIS_LIST_DIR=C:\API_Fetch\IDH_interface
COMPOSE_FILE=docker-compose.yml;docker-compose.dialysis-files.yml
```

______________________________________________________________________

## 3. 填完之後核對

**先讓 compose 檢查一次**（在 `$root\repo` 底下）：

```
docker compose --env-file $cfg config --quiet
```

什麼都沒印出來才算過。印出 `required variable … is missing a value: 請設定 …` 就照冒號後面補；印出 `failed to read …\.env: line N: unexpected character …` 就是第 N 行不是註解也不是「名稱=值」（多半是 0.1 節那一行斷掉的註解），刪掉或在開頭加 `#`。

**再查有沒有照抄範例**（只看不是 `#` 開頭的行；範本的說明行本來就寫著 `hd-server`、`localhost` 當例子）：

```
Select-String -Path $cfg -Pattern '^[^#].*(<|>|hd-server|localhost)'
```

**什麼都沒印出來**才對。印出任何一行，就是那一行還留著範例或佔位：`<…>` 沒換掉、照抄了舊版的 `hd-server`，或位址寫了 `localhost`。

**最後用眼睛核對一次**：

- `HD_IMAGE_TAG` 與 `git describe --tags` 相同
- 三個埠是資訊室**登記過**的，而且與位址裡的埠對得上
- 三個位址的主機部分**一字不差**，就是 V-08 定的那一個
- `HD_PUBLIC_API_URL`、`CORS_ORIGINS` 是 `http://`
- `MDM_KIOSK_BASE_URL` 是 **`https://`**
- `HD_SHELL_SIGNING=hospital`
- `JWT_SECRET` 是這次新產生的
- `LLM_PROVIDER=mock`
- `HOSPITAL_API_BASE_URL` 與 `HD_SIMULATION_DEPLOYMENT` **都是空白**（1005 新增；1110 起院內一律空白）
- `COMPOSE_FILE`：從零部署時維持註解；啟用讀檔後是 `docker-compose.yml;docker-compose.dialysis-files.yml`，**沒有** `;docker-compose.lab-files.yml`（1111 新增）
- `HD_LAB_DIR`、`HOSPITAL_LAB_FIELD_MAP` 空白（1111 新增）
- **沒有**一行開頭不是 `#` 的「aw_txt 與 hb-status.json）」（`v0.5.0` 範本那一行）
- **沒有** `HIGH_RISK_WRITTEN_CONFIRMATION` 這一行（1010 迭代 18.1 起拿掉；書面確認改在系統管理登記）
- **沒有** `SHOWCASE_MODE` 這一行（1010 迭代 19：那是對外展示環境用的，由 `npm run showcase` 在另一台機器上帶起來；正式環境設定下它本來就開不起來，寫了等於多一個看不懂的設定）
- 整份沒有任何一個值加了引號

______________________________________________________________________

## 4. 這份檔案的保管

這份 `.env` 裡有登入簽章金鑰與初始密碼（DEP-13）：

- **只存在院內主機的設定目錄**，不提交到任何 repo、不寄出、不拍照、不複製到隨身碟或開發機。
- 需要記錄時，只記「填了哪些**變數**、由誰決定」，**不記值**。演練紀錄與交接文件都照這個原則。例外是 `<主機>`：值不記（院內的值只進私人 repo 的 `deploy/records/`），但\*\*「用的是名稱還是 IP」要記\*\*（1001 沒記，查登入問題時就少了一條線索）。
- 交接文件寫明設定目錄的位置，讓資訊室知道它在哪、不能刪。
- 要拍照記錄現場時，**拍之前先確認畫面上沒有這份檔案的內容**。

______________________________________________________________________

## 5. 日後改了某一項，要做什麼

改 `.env` 本身不會生效：`.env` 只在**容器建立時**讀一次，執行中的服務還在用舊值。要看改的是哪一項：

| 改了                                                                                                                                 | 要做什麼                                                                                                                                                                                                                                                                                                                                                              |
| ------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `CORS_ORIGINS`、`JWT_*`、`SUPER_ADMIN_*`、`BACKUP_DAILY_AT`、`DB_DISK_MIN_FREE_MB`、`KIOSK_SHELL_MIN_VERSION`、`LLM_*`、其他營運參數 | `docker compose --env-file $cfg up -d`（compose 會自己重建設定有變的容器）                                                                                                                                                                                                                                                                                            |
| 三個埠                                                                                                                               | 先向資訊室登記 → `up -d`；位址裡的埠也要一起改                                                                                                                                                                                                                                                                                                                        |
| `HD_PUBLIC_API_URL`                                                                                                                  | `docker compose --env-file $cfg build` 再 `up -d`——**它寫在網頁檔案裡，不重建沒用**。做完用 V-17 第二段確認                                                                                                                                                                                                                                                           |
| `MDM_KIOSK_BASE_URL`                                                                                                                 | **原則上不改。** 非改不可時：`up -d api` → 重跑 `shell-builder`（它會重簽伺服器憑證，V-22）→ 重新備份金鑰（V-23）→ `restart patient-web`（V-24）→ **每一台平板清除資料、重新佈建**。三個位址的主機一起從名稱換成 IP 的完整步驟在《[護理站登不進去與主機位址之一：換主機位址](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-login-switch-ip/index.md)》 |
| `HD_IMAGE_TAG`                                                                                                                       | 只在更新、回退時改，照《[本系統換版與退回](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-upgrade/index.md)》W-19、W-20，不要單獨改                                                                                                                                                                                                                     |
| `HD_SHELL_SIGNING`                                                                                                                   | **不准改**                                                                                                                                                                                                                                                                                                                                                            |
| `HD_BACKUP_DIR`、`HD_CONFIG_DIR`                                                                                                     | `up -d`。舊資料夾裡的備份要先搬過去，並知會負責把備份送往另一台機器的人                                                                                                                                                                                                                                                                                               |
| `HD_EXPORT_DIR`                                                                                                                      | 不必重新啟動，下一次取出就寫到新位置。舊位置裡的匯出檔照《[取出資料](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-data-export/index.md)》第 7 步刪掉                                                                                                                                                                                                  |
| `HD_DIALYSIS_LIST_DIR`、`HD_LAB_DIR`、`COMPOSE_FILE`（啟用、停用讀檔）                                                               | `docker compose --env-file $cfg up -d`，再跑讀檔檢查；整套做法照《[讀檔：啟用、檢查、停用](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-dialysis-files/index.md)》。停用＝`HD_DIALYSIS_LIST_DIR` 清空、`COMPOSE_FILE` 改回註解，已經寫進主機的資料不會被刪                                                                                            |
| `HOSPITAL_LAB_FIELD_MAP`                                                                                                             | `up -d`                                                                                                                                                                                                                                                                                                                                                               |

______________________________________________________________________

## 6. 院內主機上已經有一份

1001 第二次進院已經在 `C:\hd\hd-tablet-care\config\.env` 填好一份，服務也照它跑起來了；1029 改了三個位址（換成 IP）與 `HD_IMAGE_TAG`、1116 又改了 `HD_IMAGE_TAG` 並補上讀檔的行。在那台上**不要再從範本複製**（會蓋掉它），照下面核對：

> **1027 起（迭代 28）**：1001 那一份原本沒有 `HD_EXPORT_DIR`。換到迭代 28 以後的 tag，第一行 `config --quiet` 會停在「請設定 HD_EXPORT_DIR」——照 1.2 節在 `HD_CONFIG_DIR` 下面補一行 `HD_EXPORT_DIR=C:\hd\hd-tablet-care\export` 再往下。
>
> **1111 起（迭代 32）**：換到 `v0.5.0` 以後的 tag，照範本補讀檔的四行（1.12），**都先留空、`COMPOSE_FILE` 維持註解；只貼這四行，不要整段複製範本**（0.1 節那一行斷掉的註解）。貼在 `# --- 院方透析清單 API` 那一段的上面；找不到那一段（`.env` 是更早的範本建的，1116 現場遇到），就貼在 `# --- 其他營運參數` 那一行的上面，`HOSPITAL_API_BASE_URL`、`HD_SIMULATION_DEPLOYMENT` 也不用補（1.10）。院內主機 1116 已補過並啟用讀檔。

要補的四行：

```
HD_DIALYSIS_LIST_DIR=
HD_LAB_DIR=
# COMPOSE_FILE=docker-compose.yml;docker-compose.dialysis-files.yml
HOSPITAL_LAB_FIELD_MAP=
```

**做什麼**（先輸入《[從零部署本系統](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fresh-install-3/index.md)》V-09 的開工三行）

```
docker compose --env-file $cfg config --quiet
Select-String -Path $cfg -Pattern '^[^#].*(<|>|hd-server|localhost)'
Select-String -Path $cfg -Pattern '^(HD_IMAGE_TAG|HD_BACKUP_DIR|HD_CONFIG_DIR|HD_EXPORT_DIR|HD_SHELL_SRC_DIR|HD_SHELL_SIGNING|LLM_PROVIDER|HD_PUBLIC_API_URL|CORS_ORIGINS|MDM_KIOSK_BASE_URL|HD_DIALYSIS_LIST_DIR|HD_LAB_DIR|COMPOSE_FILE|HOSPITAL_API_BASE_URL|HD_SIMULATION_DEPLOYMENT)='
```

**怎麼看**

| 看什麼                                              | 應該是                                                                                                                                                           | 不是的話                                                                                                                               |
| --------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| 第一條                                              | 什麼都沒印                                                                                                                                                       | 照訊息補                                                                                                                               |
| 第二條                                              | 什麼都沒印                                                                                                                                                       | 那一行還留著範例或 `localhost`，見下表                                                                                                 |
| `HD_IMAGE_TAG`                                      | 與 `git describe --tags` 相同（1116 起 `v0.5.0`）                                                                                                                | 不要單獨改，照《[本系統換版與退回](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-upgrade/index.md)》                    |
| 三個目錄                                            | 都在 `C:\hd\hd-tablet-care\` 底下                                                                                                                                | 問清楚是誰改的                                                                                                                         |
| `HD_SHELL_SIGNING`                                  | `hospital`                                                                                                                                                       | **停手**（1.5 節）                                                                                                                     |
| `LLM_PROVIDER`                                      | `mock`                                                                                                                                                           | 改成 `mock`，`up -d`                                                                                                                   |
| 三個位址的主機部分                                  | 一字不差，而且就是資訊室確認的那一個（1029 起是固定 IP）                                                                                                         | 見下表                                                                                                                                 |
| `HD_DIALYSIS_LIST_DIR`、`COMPOSE_FILE`              | 1116 起：`C:\API_Fetch\IDH_interface`、`docker-compose.yml;docker-compose.dialysis-files.yml`（讀檔已啟用）；停用過的話是空白、`COMPOSE_FILE` 那一行沒印（註解） | 對照《[院內主機現況與未完成事項](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-status/index.md)》；不一致就問清楚誰改的 |
| `HD_LAB_DIR`                                        | 空白                                                                                                                                                             | 1.12 節                                                                                                                                |
| `HOSPITAL_API_BASE_URL`、`HD_SIMULATION_DEPLOYMENT` | 空白，或根本沒這兩行（沒印）                                                                                                                                     | 清空，`up -d`；`HD_SIMULATION_DEPLOYMENT` 在院內出現值就停手查是誰抄了模擬設定                                                         |

**位址跟資訊室確認的不一樣時**

| 哪一項不一樣         | 要做什麼                                                                                                                                                                                                                                                                                                                                                                                                             |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 只有 `CORS_ORIGINS`  | 改好，`up -d`                                                                                                                                                                                                                                                                                                                                                                                                        |
| `HD_PUBLIC_API_URL`  | 改好，`build` 再 `up -d`，再用 V-17 第二段確認網頁裡的位址換過了                                                                                                                                                                                                                                                                                                                                                     |
| `MDM_KIOSK_BASE_URL` | **伺服器憑證已經簽了這個名字。** 照第 5 節那一列做（重跑 `shell-builder` 會重簽伺服器憑證，下載頁的 APK 也會換新），**不必**重新產生簽章金鑰；已經佈建的平板要清除資料、重新佈建。1001 時平板還沒佈建，改的代價最小；1029 起已有平板（`TB-00`）。從名稱換成 IP 的話，照《[護理站登不進去與主機位址之一：換主機位址](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-login-switch-ip/index.md)》一步步做 |

核對的結果只記「哪幾項對、哪幾項改了」，**不記值**（第 4 節）。

______________________________________________________________________

______________________________________________________________________

上一份：《[`.env` 怎麼填](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-env/index.md)》｜[部署手冊目錄](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/index.md)

## 版本歷程

| 定版                                                                      | 日期       | 異動                                                                            |
| ------------------------------------------------------------------------- | ---------- | ------------------------------------------------------------------------------- |
| [1118](https://94sh09sh19sh.github.io/hd-docs/1118/deployment/ref-env-2/) | 2026-11-18 | 首次定版。1118 照每份約 300 行的上限由《`.env` 怎麼填》拆出，內容與步驟編號不動 |

[← 回部署手冊目錄](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/index.md)
