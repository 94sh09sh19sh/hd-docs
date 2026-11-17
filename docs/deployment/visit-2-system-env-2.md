# 第二次進院（1001）· 從零部署本系統之八：`.env` 怎麼填（填好的樣子、核對、日後修改、保管）

上層文件：[《第二次進院（1001）· 從零部署本系統》](visit-2-system.md)

> 狀態：**已照做 1001，凍結**，是 1001 照著填的那一版（當時的 tag 是 `v0.3.0`），現行填法照[《`.env` 怎麼填》](ref-env.md)；1117 由舊的第十四冊之一、之二併成；沒有步驟編號，接在 N-11

## 摘要

- 接《之七》的逐項填：第 2 節填好的樣子（🏥 院內主機、🧪 開發機各一份）
- 第 3 節填完之後核對
- 第 4 節 🏥 日後改了某一項要做什麼；第 5 節 🧪 開發機的 IP 變了
- 第 6 節 🏥／🧪 差異總表
- 第 7 節 🏥 這份檔案的保管：只存在院內主機的設定目錄，記錄時只記變數不記值

## 2. 填好的樣子

### 2.1 🏥 院內主機

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

### 2.2 🧪 開發機

只有三處要換成你自己的：`HD_IMAGE_TAG`、`MDM_KIOSK_BASE_URL` 裡的 IP、`JWT_SECRET`。其餘照抄即可：

```
HD_IMAGE_TAG=v0.2.0

HD_BACKUP_DIR=C:\hd-sim\backups
HD_CONFIG_DIR=C:\hd-sim\config

HD_API_PORT=13000
HD_NURSE_PORT=18080
HD_PATIENT_PORT=18081

HD_PUBLIC_API_URL=http://localhost:13000
CORS_ORIGINS=http://localhost:18080
MDM_KIOSK_BASE_URL=https://192.168.1.23:18081

HD_SHELL_SRC_DIR=C:\hd-sim\hd-kiosk-shell
HD_SHELL_SIGNING=dev
KIOSK_SHELL_MIN_VERSION=

JWT_SECRET=<這一輪產生的那一串>
JWT_EXPIRES_IN=8h

SUPER_ADMIN_WORK_ID=sim-admin
SUPER_ADMIN_INITIAL_PASSWORD=Sim-Init-2026
SUPER_ADMIN_DISPLAY_NAME=模擬部署管理員

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

**再用眼睛核對一次**

🏥 院內主機：

- [ ] `HD_IMAGE_TAG` 與 `git describe --tags` 相同
- [ ] 三個埠是資訊室**登記過**的，而且與位址裡的埠對得上
- [ ] `HD_PUBLIC_API_URL`、`CORS_ORIGINS` 是 `http://`，主機是**護理站**連得到的那個
- [ ] `MDM_KIOSK_BASE_URL` 是 **`https://`**，主機是**平板**連得到的那個，不是 `localhost`
- [ ] `HD_SHELL_SIGNING=hospital`
- [ ] `JWT_SECRET` 是這次新產生的
- [ ] `LLM_PROVIDER=mock`
- [ ] 整份沒有任何一個值加了引號

🧪 開發機：

- [ ] `HD_IMAGE_TAG` 與 `git describe --tags` 相同
- [ ] 三個目錄都在 `C:\hd-sim\` 底下
- [ ] 三個埠是 `13000`、`18080`、`18081`（或你 N-07 換過的），而且與位址裡的埠對得上
- [ ] `MDM_KIOSK_BASE_URL` 是 **`https://`＋Wi-Fi 那張網卡的 IP**，不是 `localhost`
- [ ] **`HD_SHELL_SIGNING=dev`**
- [ ] `LLM_PROVIDER=mock`
- [ ] 整份沒有任何一個值加了引號

---

## 4. 🏥 日後改了某一項，要做什麼

改 `.env` 本身不會生效，要看改的是哪一項：

| 改了 | 要做什麼 |
|---|---|
| `CORS_ORIGINS`、`JWT_*`、`SUPER_ADMIN_*`、`BACKUP_DAILY_AT`、`DB_DISK_MIN_FREE_MB`、`KIOSK_SHELL_MIN_VERSION`、`LLM_*`、其他營運參數 | `docker compose --env-file $cfg up -d`（compose 會自己重建設定有變的容器） |
| 三個埠 | 先向資訊室登記 → `up -d`；位址裡的埠也要一起改 |
| `HD_PUBLIC_API_URL` | `docker compose --env-file $cfg build` 再 `up -d`——**它寫在網頁檔案裡，不重建沒用** |
| `MDM_KIOSK_BASE_URL` | **原則上不改。** 非改不可時：`up -d api` → 重跑 `shell-builder`（它會重簽伺服器憑證，N-21）→ `restart patient-web`（N-23）→ **每一台平板清除資料、重新佈建**（1029 從名稱換成 IP 就是這樣做的，現行做法在[《護理站登不進去與主機位址》](ref-login.md)） |
| `HD_IMAGE_TAG` | 只在更新、回退時改，照[《本系統換版與退回》](ref-upgrade.md) W-19、W-20，不要單獨改 |
| `HD_SHELL_SIGNING` | **不准改** |
| `HD_BACKUP_DIR`、`HD_CONFIG_DIR` | `up -d`。舊資料夾裡的備份要先搬過去，並知會負責把備份送往另一台機器的人 |

---

## 5. 🧪 開發機的 IP 變了

換了 Wi-Fi、隔天重新連線，IP 都可能變。症狀是手機開不到下載頁，或外殼一片空白。

| 情況 | 做什麼 |
|---|---|
| 還在同一輪模擬部署中 | 改 `MDM_KIOSK_BASE_URL` 的 IP → `docker compose --env-file $cfg up -d api` → 重跑 `shell-builder`（N-21，它發現位址變了會重簽伺服器憑證）→ `restart patient-web`（N-23）→ 手機上的 App「清除資料」，重新註冊、佈建 |
| 這一輪已經做完 | 不必管，N-31 撤除就好。下一輪重新查 IP 再填 |

這一段在實際部署**不該發生**：院內的位址擇一之後就不再換（0.3 節）。模擬部署碰到一次，正好體會為什麼。

---

## 6. 🏥／🧪 差異總表

帶進院之前再看一次這張表：**🧪 那一欄的每一個值，都不可以出現在院內那份 `.env` 裡**——只有三個埠例外，兩邊剛好相同。

| 變數 | 🏥 實際部署 | 🧪 模擬部署 |
|---|---|---|
| `HD_BACKUP_DIR`、`HD_CONFIG_DIR`、`HD_SHELL_SRC_DIR` | `D:\hd-tablet-care\…`（依資訊室指定的磁碟；1001 實際是 `C:\hd\hd-tablet-care\…`） | `C:\hd-sim\…` |
| 三個埠 | `13000`、`18080`、`18081`（0930 資訊室確認） | 相同（例外） |
| `HD_PUBLIC_API_URL`、`CORS_ORIGINS` | 護理站連得到的主機名稱或 IP | `localhost` |
| `MDM_KIOSK_BASE_URL` | `https://<平板連得到的主機>:<病人端埠>` | `https://<開發機區網 IP>:18081` |
| `HD_SHELL_SIGNING` | **`hospital`** | **`dev`** |
| `JWT_SECRET` | 院內當場產生 | 每一輪各自產生 |
| `SUPER_ADMIN_*` | 護理長給的工號與名字、臨時密碼 | `sim-admin` 之類的虛構值 |
| 其他 | 相同 | 相同 |

> ⚠️ **不要把模擬部署的 `.env` 複製到院內再改。** 從院內主機上的範本重新複製、照本冊 🏥 那幾欄一項一項填。抄過去最常漏改的是 `HD_SHELL_SIGNING`，而它一旦讓院內主機產生了開發用金鑰，就要撤掉資料卷重來。

---

## 7. 🏥 這份檔案的保管

這份 `.env` 裡有登入簽章金鑰與初始密碼（DEP-13）：

- **只存在院內主機的設定目錄**，不提交到任何 repo、不寄出、不拍照、不複製到隨身碟或開發機。
- 需要記錄時，只記「填了哪些**變數**、由誰決定」，**不記值**。演練紀錄與交接文件都照這個原則。
- 交接文件寫明設定目錄的位置，讓資訊室知道它在哪、不能刪。

上一份：[《第二次進院（1001）· 從零部署本系統之七：`.env` 怎麼填（開始之前、逐項填）》](visit-2-system-env.md)

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|

[← 回部署手冊目錄](index.md)
