# 第十四冊之一 · 實際部署的 `.env` 怎麼填

版本：v0.1　文件狀態：草案（0929 新增）　**與第十四冊一起印出來帶進去**

> **1001 起由[第十五冊之一](15a-env-hospital.md)取代。** 這一冊是 1001 第二次進院時照著填的那一版，保留為紀錄、不再改寫。
> 本冊的範例 `hd-server` **不是院內主機的名字**；根目錄 1001 實際用的是 `C:\hd\hd-tablet-care`。

> 這一冊只做一件事：**院內主機上那一份 `.env`，每一行要填什麼**。
> 它接在[第十四冊](14-from-zero.md) N-11（＝第十一冊 W-11、第十二冊 Y-03）。
> 模擬部署的填法不同，看[第十四冊之二](14b-env-simulation.md)。
>
> 變數的真本是 repo 裡的 `deploy\hospital.env.example`（每一項上面都有註解），規則的真本是《[部署規範](../requirements/deployment-spec.md)》v3.0。
> 本冊與範本不一致時，以範本為準。

---

## 0. 開始之前

### 0.1 有三份很像的檔案，只有一份是對的

| 檔案 | 給誰用 | 這次要不要碰 |
|---|---|---|
| `repo\deploy\hospital.env.example` | 部署用的**範本** | 複製它，**不要直接改它** |
| `$root\config\.env`（例如 `D:\hd-tablet-care\config\.env`） | 部署用的**設定**，由上面那份複製來 | **要填的就是這一份** |
| `repo\.env.example` | 日常開發（`npm run dev`）用 | **不要碰**。變數名稱不同，抄過來會壞 |

開檔的指令（N-11）：

```powershell
Copy-Item $root\repo\deploy\hospital.env.example $cfg
notepad $cfg
```

### 0.2 寫法的四條規矩

| 規矩 | 對 | 錯 |
|---|---|---|
| 一行一個，等號前後**不要空格** | `HD_API_PORT=13000` | `HD_API_PORT = 13000` |
| 值**不要加引號** | `HD_BACKUP_DIR=D:\hd-tablet-care\backups` | `HD_BACKUP_DIR="D:\hd-tablet-care\backups"`（雙引號裡的 `\` 會被當成跳脫字元） |
| 密碼類的值**不要含** `$`、`#`、空白、引號 | `Hd-Init-2026x` | `Hd$Init#2026`（`$` 會被當成變數、`#` 之後會被當成註解） |
| `#` 開頭的行是說明，**不要刪**，也不要把值寫在它後面 | | |

存檔時用記事本預設的 UTF-8 即可。

### 0.3 進院前要先拿到的答案

`.env` 有幾項不是你能自己決定的。**下面這張表空著一格，就填不完 `.env`**——所以它們都在 N-02 的問題清單裡，要在進院前問到：

| 要什麼 | 誰給 | 用在哪幾項 |
|---|---|---|
| 三個連接埠（後端、護理端、病人端） | 資訊室。**0930 已確認**：`13000`、`18080`、`18081` | `HD_API_PORT`、`HD_NURSE_PORT`、`HD_PATIENT_PORT`，以及所有位址 |
| 主機的名稱或 IP（**護理站電腦**用哪個連得到） | 資訊室 | `HD_PUBLIC_API_URL`、`CORS_ORIGINS` |
| 主機的名稱或 IP（**平板**用哪個連得到） | 資訊室 | `MDM_KIOSK_BASE_URL` |
| 放本系統的磁碟 | 資訊室 | `HD_BACKUP_DIR`、`HD_CONFIG_DIR`、`HD_SHELL_SRC_DIR` |
| 要交付的 tag | 你自己（N-03） | `HD_IMAGE_TAG` |
| 第一個管理員帳號的工號與名字 | 護理長 | `SUPER_ADMIN_WORK_ID`、`SUPER_ADMIN_DISPLAY_NAME` |

> ⚠️ **主機名稱還是 IP，擇一之後不要再換。** 平板的伺服器憑證就簽這個名字；換了要重簽憑證、每一台平板重新佈建。
> 選的原則：平板與護理站在院內網路上**確定連得到、而且不會變**的那一個。IP 由 DHCP 發的話可能會變，要請資訊室固定下來。

下面的範例一律假設：主機名稱 `hd-server`、三個埠 `13000`、`18080`、`18081`（0930 資訊室確認的實際值）、根目錄 `D:\hd-tablet-care`、tag `v0.2.0`。
**這些只是範例，請換成你拿到的答案。**

---

## 1. 逐項填

照範本由上往下的順序。每一項都寫：**填什麼、範例、填錯會怎樣**。

### 1.1 版本

| 變數 | 填什麼 | 範例 |
|---|---|---|
| `HD_IMAGE_TAG` | 與 N-10 `git describe --tags` 印出來的**完全相同** | `v0.2.0` |

- 映像檔的名字會帶這個值（`hd-tablet-care:v0.2.0`）。舊版映像檔不刪，回退時才找得到。
- **填錯**：與 checkout 的 tag 不同 → 建出來的映像檔名字和內容對不上，日後沒人說得清它是哪一版。
- 之後只在**更新或回退**時改它（第十一冊 W-19、W-20）。

### 1.2 主機目錄

| 變數 | 填什麼 | 範例 |
|---|---|---|
| `HD_BACKUP_DIR` | 備份資料夾的**完整路徑** | `D:\hd-tablet-care\backups` |
| `HD_CONFIG_DIR` | 這份 `.env` 所在的資料夾 | `D:\hd-tablet-care\config` |

- 兩個資料夾都要先存在（N-08 建的）。**填錯**：`bind source path does not exist`。
- 不准放在雲端同步資料夾、網路磁碟機、RAM 磁碟、`C:\Users\<帳號>\` 底下的桌面／文件／下載（DEP-21、DEP-37）。
- `HD_CONFIG_DIR` **不能是 `repo` 底下**：某一次「整個刪掉重新 clone」會把設定一起刪掉（DEP-08）。

### 1.3 連接埠

| 變數 | 填什麼 | 範例 |
|---|---|---|
| `HD_API_PORT` | 資訊室給的**後端**埠 | `13000` |
| `HD_NURSE_PORT` | 資訊室給的**護理端**埠 | `18080` |
| `HD_PATIENT_PORT` | 資訊室給的**病人端**埠 | `18081` |

- 三個都必填、沒有預設值。**填之前照 N-07 確認沒人在用**。
- **填錯**：與別的專案撞到 → `address already in use`；更糟的是現在沒撞、某次重新開機兩邊啟動順序對調才撞。所以一定要**登記**，不是「看起來沒人用」就好。

### 1.4 位址

這三項最容易填錯，填錯的症狀都是「頁面開得了，但資料打不回來」。

| 變數 | 填什麼 | 範例 |
|---|---|---|
| `HD_PUBLIC_API_URL` | **護理站電腦**連得到的後端位址：`http://<主機>:<後端埠>` | `http://hd-server:13000` |
| `CORS_ORIGINS` | **護理端**的位址：`http://<主機>:<護理端埠>` | `http://hd-server:18080` |
| `MDM_KIOSK_BASE_URL` | **平板**要連的病人端位址，**一律 `https://`**：`https://<主機>:<病人端埠>` | `https://hd-server:18081` |

- `HD_PUBLIC_API_URL` **會在建置時寫進護理端的網頁檔案裡**。事後改它，要重新 `build` 再 `up -d`，只重新啟動沒有用。
- `CORS_ORIGINS` 的主機與埠要與護理站瀏覽器網址列上看到的**一字不差**（`hd-server` 與 `hd-server.hospital.local` 算兩個不同的來源）。
  病人端與後端同一個來源，**不必列**。
- `MDM_KIOSK_BASE_URL`：
  - 開頭**一定是 `https://`**。寫成 `http://`，`shell-builder` 會拒絕、平板的外殼也會拒收 QR code。
  - **不能是 `localhost`**：平板上的 `localhost` 是平板自己。
  - 埠與 `HD_PATIENT_PORT` 相同。
  - 結尾不要加 `/`。

### 1.5 外殼 App

| 變數 | 填什麼 | 範例 |
|---|---|---|
| `HD_SHELL_SRC_DIR` | 外殼 repo 的 clone 位置（N-19 會 clone 到這裡） | `D:\hd-tablet-care\hd-kiosk-shell` |
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

> 舊版手冊用 `docker run --rm node:20-bookworm-slim …` 產生。那條指令要先從 Docker Hub 下載映像檔，
> 第一次跑會先印出 `Unable to find image 'node:20-bookworm-slim' locally`，網路不通就停在那裡。改用上面這一行就沒有這個問題。

- `JWT_SECRET` 是**登入憑證的簽章金鑰**。每次部署產生新的，**不要沿用模擬部署那一串，也不要寫在任何別的地方**。
  事後換掉它，所有人會被登出，要重新登入。
- `SUPER_ADMIN_*` **只在資料庫裡一個使用者都沒有時**才用得到：第一次啟動時建立這個帳號，第一次登入強制改密碼。
  改完密碼之後，這兩行可以清空（清空後 `docker compose --env-file $cfg up -d`）。
- **填錯**：沒填 `SUPER_ADMIN_WORK_ID` 或密碼 → 沒有任何帳號能登入。補上再 `up -d`，資料庫不必重建。

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

---

## 2. 填好的樣子

以 0.3 節的範例假設填完，會像這樣（說明行省略）。**你的值要換成自己的**：

```
HD_IMAGE_TAG=v0.2.0

HD_BACKUP_DIR=D:\hd-tablet-care\backups
HD_CONFIG_DIR=D:\hd-tablet-care\config

HD_API_PORT=13000
HD_NURSE_PORT=18080
HD_PATIENT_PORT=18081

HD_PUBLIC_API_URL=http://hd-server:13000
CORS_ORIGINS=http://hd-server:18080
MDM_KIOSK_BASE_URL=https://hd-server:18081

HD_SHELL_SRC_DIR=D:\hd-tablet-care\hd-kiosk-shell
HD_SHELL_SIGNING=hospital
KIOSK_SHELL_MIN_VERSION=

JWT_SECRET=<N-11 當場產生的那一串>
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

**再用眼睛核對一次**：

- [ ] `HD_IMAGE_TAG` 與 `git describe --tags` 相同
- [ ] 三個埠是資訊室**登記過**的，而且與位址裡的埠對得上
- [ ] `HD_PUBLIC_API_URL`、`CORS_ORIGINS` 是 `http://`，主機是**護理站**連得到的那個
- [ ] `MDM_KIOSK_BASE_URL` 是 **`https://`**，主機是**平板**連得到的那個，不是 `localhost`
- [ ] `HD_SHELL_SIGNING=hospital`
- [ ] `JWT_SECRET` 是這次新產生的
- [ ] `LLM_PROVIDER=mock`
- [ ] 整份沒有任何一個值加了引號

---

## 4. 日後改了某一項，要做什麼

改 `.env` 本身不會生效，要看改的是哪一項：

| 改了 | 要做什麼 |
|---|---|
| `CORS_ORIGINS`、`JWT_*`、`SUPER_ADMIN_*`、`BACKUP_DAILY_AT`、`DB_DISK_MIN_FREE_MB`、`KIOSK_SHELL_MIN_VERSION`、`LLM_*`、其他營運參數 | `docker compose --env-file $cfg up -d`（compose 會自己重建設定有變的容器） |
| 三個埠 | 先向資訊室登記 → `up -d`；位址裡的埠也要一起改 |
| `HD_PUBLIC_API_URL` | `docker compose --env-file $cfg build` 再 `up -d`——**它寫在網頁檔案裡，不重建沒用** |
| `MDM_KIOSK_BASE_URL` | **原則上不改。** 非改不可時：`up -d api` → 重跑 `shell-builder`（它會重簽伺服器憑證，N-21）→ `restart patient-web`（N-23）→ **每一台平板清除資料、重新佈建** |
| `HD_IMAGE_TAG` | 只在更新、回退時改，照第十一冊 W-19、W-20，不要單獨改 |
| `HD_SHELL_SIGNING` | **不准改** |
| `HD_BACKUP_DIR`、`HD_CONFIG_DIR` | `up -d`。舊資料夾裡的備份要先搬過去，並知會負責把備份送往另一台機器的人 |

---

## 5. 這份檔案的保管

這份 `.env` 裡有登入簽章金鑰與初始密碼（DEP-13）：

- **只存在院內主機的設定目錄**，不提交到任何 repo、不寄出、不拍照、不複製到隨身碟或開發機。
- 需要記錄時，只記「填了哪些**變數**、由誰決定」，**不記值**。演練紀錄與交接文件都照這個原則。
- 交接文件寫明設定目錄的位置，讓資訊室知道它在哪、不能刪。

---

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|
| [1007](https://94sh09sh19sh.github.io/hd-docs/1007/deployment/14a-env-hospital/) | 2026-10-07 | `JWT_SECRET` 改用 PowerShell 產生；1001 起由第十五冊之一取代，開頭標明 |
| [0930](https://94sh09sh19sh.github.io/hd-docs/0930/deployment/14a-env-hospital/) | 2026-09-30 | 首次定版。0929 新增：實際部署的 .env 逐項填法；0930 連接埠改為院方定的 13000、18080、18081 |

[← 回第十四冊](14-from-zero.md)　[← 回部署手冊總覽](index.md)
