# 第十五冊之一 · 實際部署的 `.env` 怎麼填

版本：v0.1　文件狀態：草案（1001 新增）　**與第十五冊一起印出來帶進去**

> 這一冊只做一件事：**院內主機上那一份 `.env`，每一行要填什麼**。
> 它接在[第十五冊](15-from-zero.md) V-12（＝第十一冊 W-11、第十二冊 Y-03）。
> 模擬部署的填法不同，看[第十五冊之二](15b-env-simulation.md)。
>
> **這一冊取代[第十四冊之一](14a-env-hospital.md)**，依 1001 第二次進院帶回來的資料（[第十四冊之四](14d-second-visit.md)）改寫：
>
> | 改了什麼 | 為什麼 |
> |---|---|
> | 根目錄改成 `C:\hd\hd-tablet-care` | 1001 實際放在這裡（M-03） |
> | 範例不再寫 `hd-server`，一律寫 `<主機>` | 1001 現場問過「`hd-server` 要照寫嗎」（M-04） |
> | `<主機>` 怎麼決定，移到第十五冊 V-08 | 它要在填 `.env` 之前定下來，而且要資訊室確認 |
> | 填完之後多一條「有沒有照抄範例」的檢查 | 同上 |
> | 新增第 6 節：主機上已經有一份 `.env` 時怎麼核對 | 1001 已經填過一份，下一次不要蓋掉它 |
>
> 變數的真本是 repo 裡的 `deploy\hospital.env.example`（每一項上面都有註解），規則的真本是《[部署規範](../requirements/deployment-spec.md)》v3.0。
> 本冊與範本不一致時，以範本為準。範本的註解裡還寫著 `hd-server` 當例子，**那一樣只是例子**。

---

## 0. 開始之前

### 0.1 有三份很像的檔案，只有一份是對的

| 檔案 | 給誰用 | 這次要不要碰 |
|---|---|---|
| `repo\deploy\hospital.env.example` | 部署用的**範本** | 複製它，**不要直接改它** |
| `$root\config\.env`（`C:\hd\hd-tablet-care\config\.env`） | 部署用的**設定**，由上面那份複製來 | **要填的就是這一份** |
| `repo\.env.example` | 日常開發（`npm run dev`）用 | **不要碰**。變數名稱不同，抄過來會壞 |

開檔的指令（V-12）：

```powershell
Copy-Item $root\repo\deploy\hospital.env.example $cfg
notepad $cfg
```

> ⚠️ **院內主機上已經有一份**（1001 填的）。`Copy-Item` 會**直接蓋掉它**，不會問。下一次進院不要打第一行，改照第 6 節核對。

### 0.2 寫法的四條規矩

| 規矩 | 對 | 錯 |
|---|---|---|
| 一行一個，等號前後**不要空格** | `HD_API_PORT=13000` | `HD_API_PORT = 13000` |
| 值**不要加引號** | `HD_BACKUP_DIR=C:\hd\hd-tablet-care\backups` | `HD_BACKUP_DIR="C:\hd\hd-tablet-care\backups"`（雙引號裡的 `\` 會被當成跳脫字元） |
| 密碼類的值**不要含** `$`、`#`、空白、引號 | `Hd-Init-2026x` | `Hd$Init#2026`（`$` 會被當成變數、`#` 之後會被當成註解） |
| `#` 開頭的行是說明，**不要刪**，也不要把值寫在它後面 | | |

存檔時用記事本預設的 UTF-8 即可。

### 0.3 進院前要先拿到的答案

`.env` 有幾項不是你能自己決定的。**下面這張表空著一格，就填不完 `.env`**——所以它們都在第十五冊 V-02 的問題清單裡，要在進院前問到：

| 要什麼 | 誰給 | 現況 | 用在哪幾項 |
|---|---|---|---|
| 三個連接埠（後端、護理端、病人端） | 資訊室 | **0930 已確認**：`13000`、`18080`、`18081` | `HD_API_PORT`、`HD_NURSE_PORT`、`HD_PATIENT_PORT`，以及所有位址 |
| 主機位址 `<主機>`：護理站與平板用哪個名稱或 IP 連得到 | 資訊室（第十五冊 V-08） | **未答**。1001 現場自己決定了一個值，是**名稱**（1005 補記）；改用 IP 照[第十五冊之四](15d-switch-host-to-ip.md) | `HD_PUBLIC_API_URL`、`CORS_ORIGINS`、`MDM_KIOSK_BASE_URL` |
| 放本系統的磁碟 | 資訊室 | 1001 放在 `C:\hd\hd-tablet-care`，院方是否同意**未答** | `HD_BACKUP_DIR`、`HD_CONFIG_DIR`、`HD_SHELL_SRC_DIR` |
| 要交付的 tag | 你自己（V-03） | 1001 是 `v0.3.0` | `HD_IMAGE_TAG` |
| 第一個管理員帳號的工號與名字 | 護理長 | — | `SUPER_ADMIN_WORK_ID`、`SUPER_ADMIN_DISPLAY_NAME` |

> ⚠️ **`<主機>` 擇一之後不要再換。** 平板的伺服器憑證就簽這個名字；換了要重簽憑證、每一台平板重新佈建。
> 怎麼選、怎麼查，寫在[第十五冊 V-08](15-from-zero.md#v-08-決定主機位址護理站與平板用什麼連這台主機新增)。

本冊的範例一律假設：三個埠 `13000`、`18080`、`18081`、根目錄 `C:\hd\hd-tablet-care`、tag `v0.3.0`。
**主機位址一律寫成 `<主機>`，填的時候整段換成 V-08 定的那一個值**——連同 `<`、`>` 一起換掉。

> 舊版（第十四冊之一）的範例寫 `hd-server`。**那不是院內主機的名字**，也不是任何人該照填的值。

---

## 1. 逐項填

照範本由上往下的順序。每一項都寫：**填什麼、範例、填錯會怎樣**。

### 1.1 版本

| 變數 | 填什麼 | 範例 |
|---|---|---|
| `HD_IMAGE_TAG` | 與 V-11 `git describe --tags` 印出來的**完全相同** | `v0.3.0` |

- 映像檔的名字會帶這個值（`hd-tablet-care:v0.3.0`）。舊版映像檔不刪，回退時才找得到。
- **填錯**：與 checkout 的 tag 不同 → 建出來的映像檔名字和內容對不上，日後沒人說得清它是哪一版。
- 之後只在**更新或回退**時改它（第十一冊 W-19、W-20）。

### 1.2 主機目錄

| 變數 | 填什麼 | 範例 |
|---|---|---|
| `HD_BACKUP_DIR` | 備份資料夾的**完整路徑** | `C:\hd\hd-tablet-care\backups` |
| `HD_CONFIG_DIR` | 這份 `.env` 所在的資料夾 | `C:\hd\hd-tablet-care\config` |

- 兩個資料夾都要先存在（V-09 建的）。**填錯**：`bind source path does not exist`。
- 不准放在雲端同步資料夾、網路磁碟機、RAM 磁碟（院內主機的 E 槽就是）、`C:\Users\<帳號>\` 底下的桌面／文件／下載（DEP-21、DEP-37）。
- `HD_CONFIG_DIR` **不能是 `repo` 底下**：某一次「整個刪掉重新 clone」會把設定一起刪掉（DEP-08）。

### 1.3 連接埠

| 變數 | 填什麼 | 範例 |
|---|---|---|
| `HD_API_PORT` | 資訊室給的**後端**埠 | `13000` |
| `HD_NURSE_PORT` | 資訊室給的**護理端**埠 | `18080` |
| `HD_PATIENT_PORT` | 資訊室給的**病人端**埠 | `18081` |

- 三個都必填、沒有預設值。**填之前照 V-07 確認沒人在用**。
- **填錯**：與別的專案撞到 → `address already in use`；更糟的是現在沒撞、某次重新開機兩邊啟動順序對調才撞。所以一定要**登記**，不是「看起來沒人用」就好。

### 1.4 位址

這三項最容易填錯，填錯的症狀都是「頁面開得了，但登不進去或資料打不回來」——1001 就是卡在這裡（M-01）。

| 變數 | 填什麼 | 範例 |
|---|---|---|
| `HD_PUBLIC_API_URL` | **護理站電腦**連得到的後端位址：`http://<主機>:<後端埠>` | `http://<主機>:13000` |
| `CORS_ORIGINS` | **護理站瀏覽器網址列上**的護理端來源：`http://<主機>:<護理端埠>` | `http://<主機>:18080` |
| `MDM_KIOSK_BASE_URL` | **平板**要連的病人端位址，**一律 `https://`**：`https://<主機>:<病人端埠>` | `https://<主機>:18081` |

- **三項的 `<主機>` 是同一個值，寫法一字不差**（名稱就都寫名稱、IP 就都寫 IP；有 DNS 尾碼就三項都有）。
- `HD_PUBLIC_API_URL` **會在建置時寫進護理端的網頁檔案裡**。事後改它，要重新 `build` 再 `up -d`，只重新啟動沒有用。
  寫進去的是什麼，可以用第十五冊 V-17 第二段那條 `grep` 直接看。
- `CORS_ORIGINS` 的主機與埠要與護理站瀏覽器網址列上看到的**一字不差**（名稱與 IP、有沒有尾碼，都算不同的來源）。
  所以護理站**一律用 `http://<主機>:18080` 開**，不要用 `localhost` 或另一種寫法。病人端與後端同一個來源，**不必列**。
  - 真的需要在主機上用 `localhost` 開，才用逗號多列一個：`http://<主機>:18080,http://localhost:18080`。
- `MDM_KIOSK_BASE_URL`：
  - 開頭**一定是 `https://`**。寫成 `http://`，`shell-builder` 會拒絕、平板的外殼也會拒收 QR code。
  - **不能是 `localhost`**：平板上的 `localhost` 是平板自己。
  - 埠與 `HD_PATIENT_PORT` 相同。
  - 結尾不要加 `/`。

### 1.5 外殼 App

| 變數 | 填什麼 | 範例 |
|---|---|---|
| `HD_SHELL_SRC_DIR` | 外殼 repo 的 clone 位置（V-20 會 clone 到這裡） | `C:\hd\hd-tablet-care\hd-kiosk-shell` |
| `HD_SHELL_SIGNING` | **`hospital`**（範本預設就是，不要改） | `hospital` |
| `KIOSK_SHELL_MIN_VERSION` | **留空** | （空白） |

- `HD_SHELL_SRC_DIR` 還沒 clone 也要**先填好路徑**：每一條 `docker compose` 指令都會檢查它有沒有填。
- `HD_SHELL_SIGNING`：院內主機一律 `hospital`。金鑰第一次產生時會記下它，**之後填別的值 `shell-builder` 會拒絕執行**。
  看到「這個金鑰資料卷是『dev』用的」就是有人把模擬部署的設定搬過來了——**停手**。
- `KIOSK_SHELL_MIN_VERSION`：留空就用程式內建的預設值。等所有平板都換上新版外殼才調高（第十二冊 Y-15）。

### 1.6 身分驗證

| 變數 | 填什麼 | 範例 |
|---|---|---|
| `JWT_SECRET` | 用下面的指令產生的一串亂碼 | `k3Jd…`（64 個字元） |
| `JWT_EXPIRES_IN` | 維持 `8h` | `8h` |
| `SUPER_ADMIN_WORK_ID` | 第一個最高權限帳號的工號 | 護理長給的 |
| `SUPER_ADMIN_INITIAL_PASSWORD` | 第一次登入用的臨時密碼 | 自己訂，遵守 0.2 節第三條 |
| `SUPER_ADMIN_DISPLAY_NAME` | 這個帳號顯示的名字 | 護理長給的 |

產生 `JWT_SECRET`（Windows 內建的 PowerShell 就做得到，不必裝 Node.js，也不必下載任何映像檔）：

```powershell
$b = New-Object byte[] 48; [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($b); [Convert]::ToBase64String($b).TrimEnd('=').Replace('+','-').Replace('/','_')
```

印出一行 64 個字元、只有英數字與 `-`、`_` 的字串。把那一整串貼在 `JWT_SECRET=` 後面。

> 舊版手冊（與範本的註解）用 `docker run --rm node:20-bookworm-slim …` 產生。1001 在院內主機上用那條，**兩次都因為 Docker 查不到 Docker Hub 的網域而失敗**
> （第十四冊之四 M-06、M-07）。上面這一行不必連網，沒有這個問題。

- `JWT_SECRET` 是**登入憑證的簽章金鑰**。每次部署產生新的，**不要沿用模擬部署那一串，也不要寫在任何別的地方**。
  事後換掉它，所有人會被登出，要重新登入。
- `SUPER_ADMIN_*` **只在資料庫裡一個使用者都沒有時**才用得到：第一次啟動時建立這個帳號，第一次登入強制改密碼。
  改完密碼之後，這兩行可以清空（清空後 `docker compose --env-file $cfg up -d`）。
- **填錯**：沒填 `SUPER_ADMIN_WORK_ID` 或密碼 → 沒有任何帳號能登入。補上再 `up -d`，資料庫不必重建。
  帳號已經建立之後才改這幾行，**不會改到已建立的帳號**。

### 1.7 備份與磁碟

| 變數 | 填什麼 | 範例 |
|---|---|---|
| `BACKUP_DAILY_AT` | 每日自動備份的時間（24 小時制 `HH:MM`），挑沒有透析的時段 | `03:00` |
| `DB_DISK_MIN_FREE_MB` | 磁碟保留空間的下限（MB），資訊室議定前維持 `1024` | `1024` |

- 低於保留空間時，護理端的資料庫狀態會亮紅、更新指令會直接停下。主機是共用的，磁碟不是本系統一個人在寫。
- **填錯**：時間寫成 `3:00` 或 `3點` → 後端拒絕啟動，日誌會說「格式須為 HH:MM」。

### 1.8 AI

**首波 AI 關閉**，這一段照下表填，不必多想：

| 變數 | 填什麼 |
|---|---|
| `LLM_PROVIDER` | `mock` |
| `LLM_ENDPOINT` | （空白） |
| `LLM_API_KEY` | （空白） |
| `LLM_MODEL_ID` | （空白） |
| `LLM_TIMEOUT_SECONDS` | `150` |
| `LLM_HEALTH_TIMEOUT_SECONDS` | `5` |

- **絕對不要填 `lab`**。實驗室在院外，後端看到 `lab` 會直接拒絕啟動（DEP-40）——那是刻意擋的，不是壞掉。
- 日後接上院內正式 GPU API 時才改成 `onprem`，做法在[第十三冊](13-ai-gateway.md) Z-23。

### 1.9 其他營運參數

`BINDING_MAX_HOURS`、`BINDING_EXPIRY_SWEEP_SECONDS`、`SYMPTOM_TREND_WINDOW_DAYS`、`SYMPTOM_TREND_REPORT_LIMIT`、
`DEVICE_ONLINE_THRESHOLD_SECONDS`、`REALTIME_HEARTBEAT_SECONDS`：**全部維持範本的值**。沒有護理長或需求文件的明確理由，不要改。

### 1.10 院方透析清單 API（1005 新增）

| 變數 | 填什麼 |
|---|---|
| `HOSPITAL_API_BASE_URL` | **（空白）**——第三次進院只探測，位址在[第十五冊](15-from-zero.md) V-30a 當場輸入，不寫進這裡 |
| `HD_SIMULATION_DEPLOYMENT` | **（空白），院內主機永遠空白** |

- **探測看過、Q-35 向資訊室報備過之後**才把位址填進來，重新啟動 `api` 就開始每 3 分鐘抓一次、病人與療程自動出現（第十五冊第 11 節）。
  這個位址**不進 repo、不寫進任何文件、不貼進任何紀錄**（DEP-46）。
- `HD_SIMULATION_DEPLOYMENT` 是模擬部署才填 `yes` 的開關。院內填了它，抄錯的模擬設定就擋不住了——後端靠它空白，才會在位址指向模擬時拒絕啟動。

---

## 2. 填好的樣子

照 0.3 節的假設填完，會像這樣（說明行省略）。**角括號那幾處要換成你自己的，`<主機>` 三處換成同一個值**：

```
HD_IMAGE_TAG=v0.3.0

HD_BACKUP_DIR=C:\hd\hd-tablet-care\backups
HD_CONFIG_DIR=C:\hd\hd-tablet-care\config

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

HOSPITAL_API_BASE_URL=
HD_SIMULATION_DEPLOYMENT=

BINDING_MAX_HOURS=6
BINDING_EXPIRY_SWEEP_SECONDS=60
SYMPTOM_TREND_WINDOW_DAYS=30
SYMPTOM_TREND_REPORT_LIMIT=10
DEVICE_ONLINE_THRESHOLD_SECONDS=90
REALTIME_HEARTBEAT_SECONDS=20
```

---

## 3. 填完之後核對

**先讓 compose 檢查一次**（在 `$root\repo` 底下）：

```powershell
docker compose --env-file $cfg config --quiet
```

什麼都沒印出來才算過。印出 `required variable … is missing a value: 請設定 …` 就照冒號後面補。

**再查有沒有照抄範例**（只看不是 `#` 開頭的行；範本的說明行本來就寫著 `hd-server`、`localhost` 當例子）：

```powershell
Select-String -Path $cfg -Pattern '^[^#].*(<|>|hd-server|localhost)'
```

**什麼都沒印出來**才對。印出任何一行，就是那一行還留著範例或佔位：`<…>` 沒換掉、照抄了舊版的 `hd-server`，或位址寫了 `localhost`。

**最後用眼睛核對一次**：

- [ ] `HD_IMAGE_TAG` 與 `git describe --tags` 相同
- [ ] 三個埠是資訊室**登記過**的，而且與位址裡的埠對得上
- [ ] 三個位址的主機部分**一字不差**，就是第十五冊 V-08 定的那一個
- [ ] `HD_PUBLIC_API_URL`、`CORS_ORIGINS` 是 `http://`
- [ ] `MDM_KIOSK_BASE_URL` 是 **`https://`**
- [ ] `HD_SHELL_SIGNING=hospital`
- [ ] `JWT_SECRET` 是這次新產生的
- [ ] `LLM_PROVIDER=mock`
- [ ] `HOSPITAL_API_BASE_URL` 與 `HD_SIMULATION_DEPLOYMENT` **都是空白**（1005 新增）
- [ ] 整份沒有任何一個值加了引號

---

## 4. 這份檔案的保管

這份 `.env` 裡有登入簽章金鑰與初始密碼（DEP-13）：

- **只存在院內主機的設定目錄**，不提交到任何 repo、不寄出、不拍照、不複製到隨身碟或開發機。
- 需要記錄時，只記「填了哪些**變數**、由誰決定」，**不記值**。演練紀錄與交接文件都照這個原則。
  例外是 `<主機>`：值不記，但**「用的是名稱還是 IP」要記**（1001 沒記，查登入問題時就少了一條線索）。
- 交接文件寫明設定目錄的位置，讓資訊室知道它在哪、不能刪。
- 要拍照記錄現場時，**拍之前先確認畫面上沒有這份檔案的內容**。

---

## 5. 日後改了某一項，要做什麼

改 `.env` 本身不會生效：`.env` 只在**容器建立時**讀一次，執行中的服務還在用舊值。要看改的是哪一項：

| 改了 | 要做什麼 |
|---|---|
| `CORS_ORIGINS`、`JWT_*`、`SUPER_ADMIN_*`、`BACKUP_DAILY_AT`、`DB_DISK_MIN_FREE_MB`、`KIOSK_SHELL_MIN_VERSION`、`LLM_*`、其他營運參數 | `docker compose --env-file $cfg up -d`（compose 會自己重建設定有變的容器） |
| 三個埠 | 先向資訊室登記 → `up -d`；位址裡的埠也要一起改 |
| `HD_PUBLIC_API_URL` | `docker compose --env-file $cfg build` 再 `up -d`——**它寫在網頁檔案裡，不重建沒用**。做完用第十五冊 V-17 第二段確認 |
| `MDM_KIOSK_BASE_URL` | **原則上不改。** 非改不可時：`up -d api` → 重跑 `shell-builder`（它會重簽伺服器憑證，V-22）→ 重新備份金鑰（V-23）→ `restart patient-web`（V-24）→ **每一台平板清除資料、重新佈建**。三個位址的主機一起從名稱換成 IP 的完整步驟在[第十五冊之四](15d-switch-host-to-ip.md) |
| `HD_IMAGE_TAG` | 只在更新、回退時改，照第十一冊 W-19、W-20，不要單獨改 |
| `HD_SHELL_SIGNING` | **不准改** |
| `HD_BACKUP_DIR`、`HD_CONFIG_DIR` | `up -d`。舊資料夾裡的備份要先搬過去，並知會負責把備份送往另一台機器的人 |

---

## 6. 院內主機上已經有一份（1001 填的）

1001 第二次進院已經在 `C:\hd\hd-tablet-care\config\.env` 填好一份，服務也照它跑起來了。下一次進院**不要再從範本複製**（會蓋掉它），照下面核對：

**做什麼**（先輸入第十五冊 V-09 的開工三行）

```powershell
docker compose --env-file $cfg config --quiet
Select-String -Path $cfg -Pattern '^[^#].*(<|>|hd-server|localhost)'
Select-String -Path $cfg -Pattern '^(HD_IMAGE_TAG|HD_BACKUP_DIR|HD_CONFIG_DIR|HD_SHELL_SRC_DIR|HD_SHELL_SIGNING|LLM_PROVIDER|HD_PUBLIC_API_URL|CORS_ORIGINS|MDM_KIOSK_BASE_URL)='
```

**怎麼看**

| 看什麼 | 應該是 | 不是的話 |
|---|---|---|
| 第一條 | 什麼都沒印 | 照訊息補 |
| 第二條 | 什麼都沒印 | 那一行還留著範例或 `localhost`，見下表 |
| `HD_IMAGE_TAG` | `v0.3.0`（與 `git describe --tags` 相同） | 不要單獨改，回第十一冊 W-19 |
| 三個目錄 | 都在 `C:\hd\hd-tablet-care\` 底下 | 問清楚是誰改的 |
| `HD_SHELL_SIGNING` | `hospital` | **停手**（1.5 節） |
| `LLM_PROVIDER` | `mock` | 改成 `mock`，`up -d` |
| 三個位址的主機部分 | 一字不差，而且就是資訊室確認的那一個（第十五冊 V-08） | 見下表 |

**位址跟資訊室確認的不一樣時**

| 哪一項不一樣 | 要做什麼 |
|---|---|
| 只有 `CORS_ORIGINS` | 改好，`up -d` |
| `HD_PUBLIC_API_URL` | 改好，`build` 再 `up -d`，再用 V-17 第二段確認網頁裡的位址換過了 |
| `MDM_KIOSK_BASE_URL` | **伺服器憑證已經在 1001 簽了這個名字。** 平板還沒佈建，所以現在改代價最小：照第 5 節那一列做（重跑 `shell-builder` 會重簽伺服器憑證，下載頁的 APK 也會換新），**不必**重新產生簽章金鑰。從名稱換成 IP 的話，照[第十五冊之四](15d-switch-host-to-ip.md)一步步做 |

核對的結果只記「哪幾項對、哪幾項改了」，**不記值**（第 4 節）。

---

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|

[← 回第十五冊](15-from-zero.md)　[← 回部署手冊總覽](index.md)
