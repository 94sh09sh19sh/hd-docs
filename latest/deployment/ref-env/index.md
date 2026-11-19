# `.env` 怎麼填

> **狀態：現行（常備參考）。** 這一份只做一件事：**院內主機上那一份 `.env`，每一行要填什麼**。從零部署時接在《[從零部署本系統](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fresh-install-4/index.md)》V-12（＝W-11、Y-03）；院內主機上已經有一份，核對照第 6 節。開發機演練的填法不同，看《[`.env` 怎麼填之一：開發機演練](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-env-simulation/index.md)》。
>
> **從哪幾份舊冊改寫（1117）**：第十五冊之一全部，逐項對到 `v0.5.0` 的 `deploy\hospital.env.example`（讀檔的四行寫進「填好的樣子」、院方 API 的位址改成院內一律留空、範本第 98 行斷掉的註解）。
>
> **編號**：沒有步驟編號；節號沿用第十五冊之一（1.1～1.12），舊紀錄寫的「之一 1.12」就是這裡的 1.12。
>
> **分成幾份**（1118 拆，每份 300 行內）：本份是第 0～1 節（開始之前、逐項填）；《[`.env` 怎麼填（第 2 份，第 2～6 節）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-env-2/index.md)》是第 2～6 節（填好的樣子、填完之後核對、保管、日後改值、院內主機上已經有一份）。子文件：《[`.env` 怎麼填之一：開發機演練（第 0～1 節）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-env-simulation/index.md)》（🧪 開始之前、逐項填）、《[`.env` 怎麼填之二：開發機演練（第 2～5 節）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-env-simulation-2/index.md)》（🧪 填好的樣子、核對、開發機的 IP 變了、與院內的差異總表）。

變數的真本是 repo 裡的 `deploy\hospital.env.example`（每一項上面都有註解），規則的真本是《[部署規範](https://94sh09sh19sh.github.io/hd-docs/latest/requirements/deployment-spec/index.md)》v3.0。這一份與範本不一致時，以範本為準；**範本加、刪、改變數，這一份與之一都要跟著改**。範本的註解裡還寫著 `hd-server` 當例子，**那一樣只是例子**。

1001 起這一份取代第十四冊之一（《[第二次進院（1001）· 從零部署本系統之七、之八：`.env` 怎麼填](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-2-system-env/index.md)》），依 1001 帶回來的資料（《[第二次進院紀錄](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/record-2-1001/index.md)》）改寫：

| 改了什麼                                                                                                                               | 為什麼                                        |
| -------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------- |
| 根目錄改成 `C:\hd\hd-tablet-care`                                                                                                      | 1001 實際放在這裡（M-03）                     |
| 範例不再寫 `hd-server`，一律寫 `<主機>`                                                                                                | 1001 現場問過「`hd-server` 要照寫嗎」（M-04） |
| `<主機>` 怎麼決定，移到《[從零部署本系統](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fresh-install-3/index.md)》V-08 | 它要在填 `.env` 之前定下來，而且要資訊室確認  |
| 填完之後多一條「有沒有照抄範例」的檢查                                                                                                 | 同上                                          |
| 新增第 6 節：主機上已經有一份 `.env` 時怎麼核對                                                                                        | 1001 已經填過一份，之後不要蓋掉它             |

## 摘要

- 院內主機那一份 `.env` 每一行要填什麼；範本 `v0.5.0` 共 37 個變數，另加一行註解掉的 `COMPOSE_FILE`
- 根目錄 `C:\hd\hd-tablet-care`、tag 現在是 `v0.5.0`、主機位址 1029 起是固定 IP；範例一律寫 `<主機>`，不寫 `hd-server`
- `v0.5.0` 範本第 98 行是一行斷掉的註解，整份複製後要刪掉，否則 compose 讀不到 `.env`（0.1 節）
- 寫法的四條規矩在 0.2 節；有幾項要進院前先問到（0.3 節）
- 第 1 節逐項填（照範本由上往下）；1.12 讀檔的四行：從零部署先留空，啟用照《讀檔：啟用、檢查、停用》；院方 API 的位址 1110 起院內一律留空
- 填好的樣子、填完核對、檔案保管、日後改值、院內主機上已經有一份時怎麼核對，在第 2 份

## 0. 開始之前

### 0.1 有三份很像的檔案，只有一份是對的

| 檔案                                                      | 給誰用                             | 這次要不要碰                         |
| --------------------------------------------------------- | ---------------------------------- | ------------------------------------ |
| `repo\deploy\hospital.env.example`                        | 部署用的**範本**                   | 複製它，**不要直接改它**             |
| `$root\config\.env`（`C:\hd\hd-tablet-care\config\.env`） | 部署用的**設定**，由上面那份複製來 | **要填的就是這一份**                 |
| `repo\.env.example`                                       | 日常開發（`npm run dev`）用        | **不要碰**。變數名稱不同，抄過來會壞 |

開檔的指令（V-12）：

```
Copy-Item $root\repo\deploy\hospital.env.example $cfg
notepad $cfg
```

> ⚠️ **院內主機上已經有一份**（1001 填的，1029、1116 換版時補過）。`Copy-Item` 會**直接蓋掉它**，不會問。在院內主機上不要打第一行，改照第 6 節核對。
>
> ⚠️ **`v0.5.0` 的範本第 98 行是一行斷掉的註解**「aw_txt 與 hb-status.json）」，開頭沒有 `#`（迭代 32 寫範本時 `hospital_dataset\raw_txt` 的 `\r` 被當成換行）。整份複製後 compose 會停在 `failed to read …\.env: line 98: unexpected character … in variable name …`。複製完在記事本裡**刪掉那一行**（或在開頭加 `#`）。master 已修（`8c12505`），`v0.5.0` 之後的 tag 沒有這一行。在已經有 `.env` 的主機上只補缺的幾行時，**只貼那幾行、不要整段複製範本**（1116 模擬實測）。

### 0.2 寫法的四條規矩

| 規矩                                                 | 對                                           | 錯                                                                                |
| ---------------------------------------------------- | -------------------------------------------- | --------------------------------------------------------------------------------- |
| 一行一個，等號前後**不要空格**                       | `HD_API_PORT=13000`                          | `HD_API_PORT = 13000`                                                             |
| 值**不要加引號**                                     | `HD_BACKUP_DIR=C:\hd\hd-tablet-care\backups` | `HD_BACKUP_DIR="C:\hd\hd-tablet-care\backups"`（雙引號裡的 `\` 會被當成跳脫字元） |
| 密碼類的值**不要含** `$`、`#`、空白、引號            | `Hd-Init-2026x`                              | `Hd$Init#2026`（`$` 會被當成變數、`#` 之後會被當成註解）                          |
| `#` 開頭的行是說明，**不要刪**，也不要把值寫在它後面 |                                              |                                                                                   |

例外：讀檔的資料夾路徑（1.12）有空白與中文時**照寫、不加引號**——compose 檔用長語法掛載，一個值就是一個路徑，不會被空白拆開。

存檔時用記事本預設的 UTF-8 即可。

### 0.3 進院前要先拿到的答案

`.env` 有幾項不是你能自己決定的。**下面這張表空著一格，就填不完 `.env`**——所以它們都在《[從零部署本系統](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fresh-install-2/index.md)》V-02 的問題清單裡，要在進院前問到：

| 要什麼                                                | 誰給                 | 現況                                                                                                                                                                                                                                                   | 用在哪幾項                                                            |
| ----------------------------------------------------- | -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------- |
| 三個連接埠（後端、護理端、病人端）                    | 資訊室               | **0930 已確認**：`13000`、`18080`、`18081`                                                                                                                                                                                                             | `HD_API_PORT`、`HD_NURSE_PORT`、`HD_PATIENT_PORT`，以及所有位址       |
| 主機位址 `<主機>`：護理站與平板用哪個名稱或 IP 連得到 | 資訊室（V-08）       | **1007 答：IP 是固定的**。1001 現場自己決定了一個值，是**名稱**（1005 補記）；**1029 換成 IP**（《[護理站登不進去與主機位址之一：換主機位址](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-login-switch-ip/index.md)》），之後一律用 IP | `HD_PUBLIC_API_URL`、`CORS_ORIGINS`、`MDM_KIOSK_BASE_URL`             |
| 放本系統的磁碟                                        | 資訊室               | 1001 起放在 `C:\hd\hd-tablet-care`，院方是否同意**未答**（1116 為止）                                                                                                                                                                                  | `HD_BACKUP_DIR`、`HD_CONFIG_DIR`、`HD_EXPORT_DIR`、`HD_SHELL_SRC_DIR` |
| 要交付的 tag                                          | 你自己（V-03）       | 1001 是 `v0.3.0`、1029 `v0.4.0`、**1116 起 `v0.5.0`**                                                                                                                                                                                                  | `HD_IMAGE_TAG`                                                        |
| 第一個管理員帳號的工號與名字                          | 護理長               | —                                                                                                                                                                                                                                                      | `SUPER_ADMIN_WORK_ID`、`SUPER_ADMIN_DISPLAY_NAME`                     |
| 抓取腳本的留底資料夾（讀檔才要）                      | 學長、抓取腳本那一側 | 1116 起 `C:\API_Fetch\IDH_interface`（《[院方 API 抓取腳本的維運](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fetch-script/index.md)》）                                                                                              | `HD_DIALYSIS_LIST_DIR`                                                |

> ⚠️ **`<主機>` 擇一之後不要再換。** 平板的伺服器憑證就簽這個名字；換了要重簽憑證、每一台平板重新佈建。怎麼選、怎麼查，寫在《[從零部署本系統](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fresh-install-3/index.md)》V-08。

這一份的範例一律假設：三個埠 `13000`、`18080`、`18081`、根目錄 `C:\hd\hd-tablet-care`、tag `v0.5.0`。 **主機位址一律寫成 `<主機>`，填的時候整段換成 V-08 定的那一個值**——連同 `<`、`>` 一起換掉。

> 舊版（第十四冊之一）的範例寫 `hd-server`。**那不是院內主機的名字**，也不是任何人該照填的值。

______________________________________________________________________

## 1. 逐項填

照範本由上往下的順序（範本順序：1.1～1.8、1.12、1.10、1.9；1.11 範本裡已經沒有）。每一項都寫：**填什麼、範例、填錯會怎樣**。

### 1.1 版本

| 變數           | 填什麼                                             | 範例     |
| -------------- | -------------------------------------------------- | -------- |
| `HD_IMAGE_TAG` | 與 V-11 `git describe --tags` 印出來的**完全相同** | `v0.5.0` |

- 映像檔的名字會帶這個值（`hd-tablet-care:v0.5.0`；`ai-gateway`、`shell-builder` 的映像檔也帶它）。舊版映像檔不刪，回退時才找得到。
- **填錯**：與 checkout 的 tag 不同 → 建出來的映像檔名字和內容對不上，日後沒人說得清它是哪一版。
- 之後只在**更新或回退**時改它（《[本系統換版與退回](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-upgrade/index.md)》W-19、W-20）。

### 1.2 主機目錄

| 變數            | 填什麼                                                      | 範例                           |
| --------------- | ----------------------------------------------------------- | ------------------------------ |
| `HD_BACKUP_DIR` | 備份資料夾的**完整路徑**                                    | `C:\hd\hd-tablet-care\backups` |
| `HD_CONFIG_DIR` | 這份 `.env` 所在的資料夾                                    | `C:\hd\hd-tablet-care\config`  |
| `HD_EXPORT_DIR` | 研究與後續計畫的資料取出寫在這裡（1027 迭代 28 起，DEP-47） | `C:\hd\hd-tablet-care\export`  |

- 前兩個資料夾都要先存在（V-09 建的）。**填錯**：`bind source path does not exist`。
- 不准放在雲端同步資料夾、網路磁碟機、RAM 磁碟（院內主機的 E 槽就是）、`C:\Users\<帳號>\` 底下的桌面／文件／下載（DEP-21、DEP-37）。
- `HD_CONFIG_DIR` **不能是 `repo` 底下**：某一次「整個刪掉重新 clone」會把設定一起刪掉（DEP-08）。AI 閘道的 `config.yaml` 放在它底下的 `ai-gateway\`。
- `HD_EXPORT_DIR` **與備份資料夾分開**：不能是同一個、也不能一個在另一個裡面（備份會送往院內另一台機器，取出檔不該跟著走）；不准放的地方與上面相同，也不在 clone 目錄裡。只掛給一次性的 `data-export`，`api` 碰不到。資料夾不必先建，第一次取出時自動建立；**沒有填的話，每一個 `docker compose` 指令都會停在「請設定 HD_EXPORT_DIR」**。怎麼取資料見《[取出資料](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-data-export/index.md)》。

### 1.3 連接埠

| 變數              | 填什麼                 | 範例    |
| ----------------- | ---------------------- | ------- |
| `HD_API_PORT`     | 資訊室給的**後端**埠   | `13000` |
| `HD_NURSE_PORT`   | 資訊室給的**護理端**埠 | `18080` |
| `HD_PATIENT_PORT` | 資訊室給的**病人端**埠 | `18081` |

- 三個都必填、沒有預設值。**填之前照 V-07 確認沒人在用**。
- **填錯**：與別的專案撞到 → `address already in use`；更糟的是現在沒撞、某次重新開機兩邊啟動順序對調才撞。所以一定要**登記**，不是「看起來沒人用」就好。

### 1.4 位址

這三項最容易填錯，填錯的症狀都是「頁面開得了，但登不進去或資料打不回來」——1001 就是卡在這裡（《[第二次進院紀錄](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/record-2-1001/index.md)》M-01）。

| 變數                 | 填什麼                                                                     | 範例                   |
| -------------------- | -------------------------------------------------------------------------- | ---------------------- |
| `HD_PUBLIC_API_URL`  | **護理站電腦**連得到的後端位址：`http://<主機>:<後端埠>`                   | `http://<主機>:13000`  |
| `CORS_ORIGINS`       | **護理站瀏覽器網址列上**的護理端來源：`http://<主機>:<護理端埠>`           | `http://<主機>:18080`  |
| `MDM_KIOSK_BASE_URL` | **平板**要連的病人端位址，**一律 `https://`**：`https://<主機>:<病人端埠>` | `https://<主機>:18081` |

- **三項的 `<主機>` 是同一個值，寫法一字不差**（名稱就都寫名稱、IP 就都寫 IP；有 DNS 尾碼就三項都有）。1029 起院內是固定 IP。
- `HD_PUBLIC_API_URL` **會在建置時寫進護理端的網頁檔案裡**。事後改它，要重新 `build` 再 `up -d`，只重新啟動沒有用。寫進去的是什麼，可以用 V-17 第二段那條 `grep` 直接看。迭代 12 起病人端經病人端自己的埠轉送呼叫後端，不用這個值。
- `CORS_ORIGINS` 的主機與埠要與護理站瀏覽器網址列上看到的**一字不差**（名稱與 IP、有沒有尾碼，都算不同的來源）。所以護理站**一律用 `http://<主機>:18080` 開**，不要用 `localhost` 或另一種寫法。病人端與後端同一個來源，**不必列**。
- 真的需要在主機上用 `localhost` 開，才用逗號多列一個：`http://<主機>:18080,http://localhost:18080`。
- `MDM_KIOSK_BASE_URL`：
- 開頭**一定是 `https://`**。寫成 `http://`，`shell-builder` 會拒絕、平板的外殼也會拒收 QR code。
- **不能是 `localhost`**：平板上的 `localhost` 是平板自己。
- 埠與 `HD_PATIENT_PORT` 相同。
- 結尾不要加 `/`。
- `shell-builder` 以這裡的主機名稱或 IP 簽伺服器憑證（平板管控方案 6.1）：兩者擇一之後不要再換。

### 1.5 外殼 App

| 變數                      | 填什麼                                          | 範例                                  |
| ------------------------- | ----------------------------------------------- | ------------------------------------- |
| `HD_SHELL_SRC_DIR`        | 外殼 repo 的 clone 位置（V-20 會 clone 到這裡） | `C:\hd\hd-tablet-care\hd-kiosk-shell` |
| `HD_SHELL_SIGNING`        | **`hospital`**（範本預設就是，不要改）          | `hospital`                            |
| `KIOSK_SHELL_MIN_VERSION` | **留空**                                        | （空白）                              |

- `HD_SHELL_SRC_DIR` 還沒 clone 也要**先填好路徑**：每一條 `docker compose` 指令都會檢查它有沒有填。不必自己 checkout：`shell-builder` 會從這份 clone 取出本系統釘住的那一版（`services/shell-builder/shell.pin`，`v0.5.0` 釘外殼 `v0.3.0`）；換外殼版本前在那個目錄執行 `git fetch --tags`。
- `HD_SHELL_SIGNING`：院內主機一律 `hospital`。金鑰第一次產生時會記下它，**之後填別的值 `shell-builder` 會拒絕執行**。看到「這個金鑰資料卷是『dev』用的」就是有人把模擬部署的設定搬過來了——**停手**。
- `KIOSK_SHELL_MIN_VERSION`：留空就用程式內建的預設值。低於它的平板在護理端標為「外殼過舊」。等所有平板都換上新版外殼才調高（《[平板與外殼 App](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-tablet-2/index.md)》Y-15）；調高只要改這裡並重新啟動 `api`，不必重建映像檔。

### 1.6 身分驗證

| 變數                           | 填什麼                     | 範例                      |
| ------------------------------ | -------------------------- | ------------------------- |
| `JWT_SECRET`                   | 用下面的指令產生的一串亂碼 | `k3Jd…`（64 個字元）      |
| `JWT_EXPIRES_IN`               | 維持 `8h`                  | `8h`                      |
| `SUPER_ADMIN_WORK_ID`          | 第一個最高權限帳號的工號   | 護理長給的                |
| `SUPER_ADMIN_INITIAL_PASSWORD` | 第一次登入用的臨時密碼     | 自己訂，遵守 0.2 節第三條 |
| `SUPER_ADMIN_DISPLAY_NAME`     | 這個帳號顯示的名字         | 護理長給的                |

產生 `JWT_SECRET`（Windows 內建的 PowerShell 就做得到，不必裝 Node.js，也不必下載任何映像檔）：

```
$b = New-Object byte[] 48; [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($b); [Convert]::ToBase64String($b).TrimEnd('=').Replace('+','-').Replace('/','_')
```

印出一行 64 個字元、只有英數字與 `-`、`_` 的字串。把那一整串貼在 `JWT_SECRET=` 後面。

> 舊版手冊與範本的註解（到 `v0.5.0` 都還是）用 `docker run --rm node:20-bookworm-slim …` 產生。1001 在院內主機上用那條，**兩次都因為 Docker 查不到 Docker Hub 的網域而失敗** （《[第二次進院紀錄](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/record-2-1001/index.md)》M-06、M-07）。上面這一行不必連網，沒有這個問題。

- `JWT_SECRET` 是**登入憑證的簽章金鑰**。每次部署產生新的，**不要沿用模擬部署那一串，也不要寫在任何別的地方**。事後換掉它，所有人會被登出，要重新登入。
- `SUPER_ADMIN_*` **只在資料庫裡一個使用者都沒有時**才用得到：第一次啟動時建立這個帳號，第一次登入強制改密碼。改完密碼之後，這兩行可以清空（清空後 `docker compose --env-file $cfg up -d`）。
- **填錯**：沒填 `SUPER_ADMIN_WORK_ID` 或密碼 → 沒有任何帳號能登入。補上再 `up -d`，資料庫不必重建。帳號已經建立之後才改這幾行，**不會改到已建立的帳號**。

### 1.7 備份與磁碟

| 變數                  | 填什麼                                                                   | 範例    |
| --------------------- | ------------------------------------------------------------------------ | ------- |
| `BACKUP_DAILY_AT`     | 每日自動備份的時間（24 小時制 `HH:MM`），挑沒有透析的時段                | `03:00` |
| `DB_DISK_MIN_FREE_MB` | Docker 資料所在磁碟的保留空間下限（MB），資訊室議定前維持 `1024`（Q-27） | `1024`  |

- 低於保留空間時，護理端的資料庫狀態會亮紅、更新指令會直接停下。主機是共用的，磁碟不是本系統一個人在寫。另外要跟資訊室議定「剩多少就通知、誰監看」（開發端建議剩 50 GB），那不是這一項，寫進交接紙。
- **填錯**：時間寫成 `3:00` 或 `3點` → 後端拒絕啟動，日誌會說「格式須為 HH:MM」。

### 1.8 AI

**首波 AI 關閉**，這一段照下表填，不必多想：

| 變數                         | 填什麼   |
| ---------------------------- | -------- |
| `LLM_PROVIDER`               | `mock`   |
| `LLM_ENDPOINT`               | （空白） |
| `LLM_API_KEY`                | （空白） |
| `LLM_MODEL_ID`               | （空白） |
| `LLM_TIMEOUT_SECONDS`        | `150`    |
| `LLM_HEALTH_TIMEOUT_SECONDS` | `5`      |

- **絕對不要填 `lab`**。實驗室在院外，後端看到 `lab` 會直接拒絕啟動（DEP-40）——那是刻意擋的，不是壞掉。
- 日後接上院內正式 GPU API 時才改成 `onprem`（`LLM_ENDPOINT` 填 `http://ai-gateway:8000/v1`、以 `--profile ai` 啟動閘道），做法在《[AI 閘道](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-ai-gateway-3/index.md)》Z-23。推論端點、模型與參數不寫在這裡，寫在設定目錄底下的 `ai-gateway\config.yaml`；`LLM_MODEL_ID` 接閘道時**留空**（模型只由 `config.yaml` 決定，FR-S13）；`LLM_TIMEOUT_SECONDS` 要比 `config.yaml` 的 `timeout_seconds` 大，否則後端會比閘道先放棄。

### 1.9 其他營運參數

`BINDING_MAX_HOURS`、`BINDING_EXPIRY_SWEEP_SECONDS`、`SYMPTOM_TREND_WINDOW_DAYS`、`SYMPTOM_TREND_REPORT_LIMIT`、 `DEVICE_ONLINE_THRESHOLD_SECONDS`、`REALTIME_HEARTBEAT_SECONDS`：**全部維持範本的值**（`6`、`60`、`30`、`10`、`90`、`20`）。沒有護理長或需求文件的明確理由，不要改。範本裡這一段在最後面。

### 1.10 院方透析清單 API（1005 新增；1110 起院內不用）

| 變數                       | 填什麼                         |
| -------------------------- | ------------------------------ |
| `HOSPITAL_API_BASE_URL`    | **（空白），院內一律空白**     |
| `HD_SIMULATION_DEPLOYMENT` | **（空白），院內主機永遠空白** |

- **1110 起本系統不打院方任何 API**，院內讀抓取腳本存下的檔（1.12）。`HOSPITAL_API_BASE_URL` 與 `HD_DIALYSIS_LIST_DIR` **兩個都填，後端拒絕啟動**。
- 1005～1109 的做法（留給對照舊紀錄）：第三次進院只探測，位址在探測時當場輸入、不寫進這裡；探測看過、Q-35 向資訊室報備過之後才把位址填進來，重新啟動 `api` 就每 3 分鐘抓一次。這個位址**不進 repo、不寫進任何文件、不貼進任何紀錄**（DEP-46）。探測的做法在《[從零部署本系統](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fresh-install-6/index.md)》V-30a 的舊做法一節。
- `HD_SIMULATION_DEPLOYMENT` 是模擬部署才填 `yes` 的開關。院內填了它，抄錯的模擬設定就擋不住了——後端靠它空白，才會在位址指向模擬院方 API 時拒絕啟動、在讀到模擬標記檔時整次作廢（DEP-46）。
- 1116 現場遇到：主機的 `.env` 若是更早的範本建的、**根本沒有這兩行**，不必補——沒寫就等於空白，正是院內要的。

### 1.11 判斷規則的書面確認閘門（1010 新增，同日迭代 18.1 拿掉）

**`.env` 裡沒有這一項了。** 迭代 18 時它是 `HIGH_RISK_WRITTEN_CONFIRMATION`；1010 使用者指示改放進系統管理，迭代 18.1 起後端不讀它，範本也拿掉了。

- 法務／資訊室對 TFDA 分類的書面確認（清冊 Q-02）拿到之後，由**系統管理者在護理端系統管理「判斷規則」按「登記書面確認」**，填文號與理由；每一次登記與取消登記都寫進稽核軌跡。不必動設定檔、不必重新啟動。
- 沒登記之前，風險分層提示、療程中預警、劑量調整參考、透析適足性趨勢推估**只對合成資料病人執行**，真實病人一律擋下並寫進稽核軌跡；這四項的功能開關預設也都是關的。只登記還不夠，每一條規則另要在畫面上附出處、標為生效（清冊 Q-03）。
- **照舊版範本填過的設定目錄**，那一行留著也不會生效（後端啟動時提醒一聲），刪掉即可。

### 1.12 院方資料：讀抓取腳本存下的檔（1111 迭代 32 新增）

1110 起院內不打院方 API，讀主機上抓取腳本 `hd-hospital-fetch` 存下的檔（實作規格書 4.32）。範本裡這一段在 1.8 AI 之後、1.10 院方 API 之前。**從零部署時四行都先留空、`COMPOSE_FILE` 那一行維持註解**，病人、床位與療程照護理師的人工操作；啟用、檢查、停用照《[讀檔：啟用、檢查、停用](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-dialysis-files/index.md)》。

| 變數                     | 從零部署時                         | 啟用之後（1116 起院內現況）                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| ------------------------ | ---------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `HD_DIALYSIS_LIST_DIR`   | （空白）                           | 透析清單的指定資料夾（寫 `YYYY-MM.txt` 的那一個）的完整路徑：`C:\API_Fetch\IDH_interface`。有空白與中文照寫、不加引號；用檔案總管網址列複製貼上最不會錯。抓取腳本的 `status_file` 要指到這個資料夾裡的 `fetch-status.json`                                                                                                                                                                                                                                                                                                                                                                          |
| `HD_LAB_DIR`             | （空白）                           | **（空白）**——1111 學長答 `hb` 不用這邊處理（《[院方 API 介接之二](https://94sh09sh19sh.github.io/hd-docs/latest/notes/hospital-api-fetch-methods-questions/index.md)》A-5），檢驗資料先不讀。日後要讀才填 `Hb_API_Fetch` 的完整路徑（底下有 `hospital_dataset\raw_txt` 與 `hb-status.json`），填之前先重問《[院方 API 介接之二之一](https://94sh09sh19sh.github.io/hd-docs/latest/notes/hospital-api-fetch-methods-questions-answered/index.md)》第 3.4 節的 I-9、I-12、I-13（《[檢驗資料（hb）抓取（未採用）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-hb-fetch/index.md)》） |
| `COMPOSE_FILE`           | 維持範本那一行的註解（開頭有 `#`） | 把開頭的 `#` 拿掉，只留有填的那幾個檔：`docker-compose.yml;docker-compose.dialysis-files.yml`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| `HOSPITAL_LAB_FIELD_MAP` | （空白）                           | **（空白）**——用暫定的對照表；之二 I-9（白蛋白用哪一欄）、I-12（Kt/V 公式）答覆後才填，例如 `HOSPITAL_LAB_FIELD_MAP=ALBUMIN=ALB;KT_V=Kt/V(Daugirdas)`                                                                                                                                                                                                                                                                                                                                                                                                                                               |

- `COMPOSE_FILE` 用分號隔開，**第一個一定是 `docker-compose.yml`**；填了 `HD_DIALYSIS_LIST_DIR` 才加 `docker-compose.dialysis-files.yml`，填了 `HD_LAB_DIR` 才加 `docker-compose.lab-files.yml`。`HD_LAB_DIR` 空白卻放了 `docker-compose.lab-files.yml`，compose 會停在 `docker-compose.lab-files.yml 要配 HD_LAB_DIR`（整段複製範本那一行最容易帶進來）。**不能留成空白的一行**（`COMPOSE_FILE=`，compose 會讀不到設定檔）。
- 範本那一行（註解）的原文是 `# COMPOSE_FILE=docker-compose.yml;docker-compose.dialysis-files.yml;docker-compose.lab-files.yml`，三個檔都列著；院內只用前兩個。
- 兩個資料夾都以**唯讀**掛進 `api`，本系統不搬、不刪、不改任何留底檔（DEP-37 第 3 條的例外）。**路徑寫錯時 Docker Desktop 會替它建一個空資料夾**（`create_host_path: false` 在 Docker Desktop＋WSL2 上沒有效，1111 實測），後端讀到空資料夾，護理站出現「看不到抓取腳本的狀態」與「院方資料已 N 分鐘未更新」。
- `HOSPITAL_API_BASE_URL` 維持**空白**——與 `HD_DIALYSIS_LIST_DIR` 兩個都填，後端拒絕啟動（1.10）。
- 讀檔頻率、檢驗資料讀檔頻率、「未更新」提示時段（迭代 32.1 起預設 8～23 時）在護理端「系統管理 → 營運參數與選項清單」調，不在 `.env`。
- 範本的註解寫「路徑不進 repo、不寫進公開文件，現場值記在私人紀錄」。`C:\API_Fetch\IDH_interface` 是 1116 起抓取腳本的固定位置，已寫在進院冊與維運文件裡；其他院內路徑（例如舊的 D 槽路徑）照舊只記在私人 repo 的 `deploy/records/`。

______________________________________________________________________

下一份：《[`.env` 怎麼填（第 2 份，第 2～6 節）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-env-2/index.md)》｜[部署手冊目錄](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/index.md)

## 版本歷程

| 定版                                                                    | 日期       | 異動                                                                                                                                            |
| ----------------------------------------------------------------------- | ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| [1118](https://94sh09sh19sh.github.io/hd-docs/1118/deployment/ref-env/) | 2026-11-18 | 首次定版。1117 部署手冊整套重寫時由舊冊改寫而成（舊冊號見目錄最後的對照），步驟編號不變；1118 照每份約 300 行的上限拆檔，後段移到同一套的下一份 |

[← 回部署手冊目錄](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/index.md)
