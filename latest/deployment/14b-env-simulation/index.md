# 第十四冊之二 · 模擬部署的 `.env` 怎麼填

版本：v0.1　文件狀態：草案（0929 新增）

> **1001 起由[第十五冊之二](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/15b-env-simulation/index.md)取代。** 第十五冊之二把護理端的位址從 `localhost` 改成開發機的區網 IP， 理由在那一冊開頭（1001 院內卡在的登入問題，用 `localhost` 模擬部署永遠練不到）。這一冊保留為紀錄、不再改寫。
>
> 這一冊只做一件事：**模擬部署時，開發機上那一份 `.env`，每一行要填什麼**。 它接在[第十四冊](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/14-from-zero/index.md) N-11。實際部署的填法看[第十四冊之一](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/14a-env-hospital/index.md)。
>
> 模擬部署的意思是：在自己的開發機上，用與院內**一字不差的指令**從零部署一次（《部署規範》DEP-22，第十一冊第 7 節）。 所以 `.env` 用的是**同一份範本、同一批變數**，只是值換成開發機的。 本冊與 repo 裡的 `deploy\hospital.env.example` 不一致時，以範本為準。

______________________________________________________________________

## 0. 開始之前

### 0.1 三份很像的檔案

| 檔案                                         | 給誰用                      | 這次要不要碰                                                                                       |
| -------------------------------------------- | --------------------------- | -------------------------------------------------------------------------------------------------- |
| `C:\hd-sim\repo\deploy\hospital.env.example` | 部署用的**範本**            | 複製它，不要直接改它                                                                               |
| `C:\hd-sim\config\.env`                      | 這次模擬部署的**設定**      | **要填的就是這一份**                                                                               |
| 你平常開發的工作目錄裡的 `.env`              | 日常開發（`npm run dev`）用 | **不要碰，也不要拿來抄**。變數名稱不同，而且它的 `LLM_PROVIDER=lab` 之類的值在這裡會讓後端拒絕啟動 |

開檔的指令（N-11，先打第十四冊 N-08 的開工三行，`$root` 是 `C:\hd-sim`）：

```
Copy-Item $root\repo\deploy\hospital.env.example $cfg
notepad $cfg
```

### 0.2 寫法的四條規矩

與實際部署相同：**等號前後不要空格、值不要加引號、密碼不要含 `$` `#` 空白與引號、`#` 開頭的說明行不要刪**。 理由見[第十四冊之一](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/14a-env-hospital/index.md) 0.2 節。

### 0.3 要先查好的兩件事

模擬部署的值幾乎都是固定的，只有兩件要自己查：

**一、要測的 tag**：第十四冊 N-03 準備的那一個，也就是 N-10 `git describe --tags` 印出來的。

**二、開發機的區網 IP**（手機要用它連開發機）：

```
ipconfig
```

找「無線區域網路介面卡 Wi-Fi」那一段的 **IPv4 位址**，例如 `192.168.1.23`。

| 注意                                                                                          | 為什麼                                                      |
| --------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| 要用 **Wi-Fi 那一張網卡**的 IP，不是 `vEthernet (WSL)` 或 `vEthernet (Default Switch)` 那幾段 | 那幾張是 Docker 與 WSL 的虛擬網卡，手機連不到               |
| 手機要連**同一個 Wi-Fi**                                                                      | 不同網段互相看不到                                          |
| IP 每次連線可能會變                                                                           | 變了要照本冊第 4 節處理。**同一輪模擬部署之內不要換 Wi-Fi** |

下面用 `192.168.1.23` 當範例，**請換成你查到的**。

______________________________________________________________________

## 1. 逐項填

照範本由上往下的順序。**「與實際部署不同」那一欄打勾的，就是模擬部署要特別留意的地方。**

### 1.1 版本與目錄

| 變數            | 填什麼                    | 與實際部署不同 |
| --------------- | ------------------------- | -------------- |
| `HD_IMAGE_TAG`  | 要測的 tag，例如 `v0.2.0` |                |
| `HD_BACKUP_DIR` | `C:\hd-sim\backups`       | ✓ 根目錄不同   |
| `HD_CONFIG_DIR` | `C:\hd-sim\config`        | ✓ 根目錄不同   |

- 要測更新演練時，會另打一個測試 tag（第十一冊第 7 節），那時照 W-19 把 `HD_IMAGE_TAG` 改成測試 tag。
- 目錄一樣**不要放在 OneDrive 或 `C:\Users\<帳號>\` 底下的桌面／文件／下載**。模擬部署要練的就是院內那套規矩。

### 1.2 連接埠

| 變數              | 填什麼  | 與實際部署不同     |
| ----------------- | ------- | ------------------ |
| `HD_API_PORT`     | `13000` | ✓ 自己挑，不必登記 |
| `HD_NURSE_PORT`   | `18080` | ✓                  |
| `HD_PATIENT_PORT` | `18081` | ✓                  |

- 故意**不用** `3000`、`5173`、`5174`：那是平常 `npm run dev` 用的，兩者同時開會撞。
- N-07 查到被佔用時，自己換一個，本冊後面所有用到那個埠的地方跟著改。

### 1.3 位址

| 變數                 | 填什麼                                          | 與實際部署不同           |
| -------------------- | ----------------------------------------------- | ------------------------ |
| `HD_PUBLIC_API_URL`  | `http://localhost:13000`                        | ✓ 實際部署是院內主機名稱 |
| `CORS_ORIGINS`       | `http://localhost:18080`                        | ✓                        |
| `MDM_KIOSK_BASE_URL` | `https://192.168.1.23:18081`（**換成你的 IP**） | ✓ 用開發機的區網 IP      |

- 護理端只在開發機自己的瀏覽器開，所以用 `localhost`。
- **`MDM_KIOSK_BASE_URL` 不能用 `localhost`**：手機上的 `localhost` 是手機自己。這一條與實際部署一樣要 **`https://`**。
- 想從**另一台電腦**開護理端時，`HD_PUBLIC_API_URL` 與 `CORS_ORIGINS` 也要改成區網 IP， 而且 `HD_PUBLIC_API_URL` 改了要重新 `build`（它寫在網頁檔案裡）。一般模擬部署不需要。

### 1.4 外殼 App

| 變數                      | 填什麼                     | 與實際部署不同                                                         |
| ------------------------- | -------------------------- | ---------------------------------------------------------------------- |
| `HD_SHELL_SRC_DIR`        | `C:\hd-sim\hd-kiosk-shell` | ✓ 根目錄不同                                                           |
| `HD_SHELL_SIGNING`        | **`dev`**                  | ✓ **實際部署是 `hospital`**。範本預設是 `hospital`，**這一項一定要改** |
| `KIOSK_SHELL_MIN_VERSION` | 留空                       |                                                                        |

- `HD_SHELL_SIGNING=dev` 讓 `shell-builder` 產生「開發用」的簽章金鑰，N-21 會印出「APK 簽章金鑰（開發用）」。 這把金鑰簽出來的 APK 與院內版**不能互相覆蓋安裝**，這正是要的效果：開發用的東西不會混進院內。
- 忘了改、留著 `hospital` 跑下去的話，資料卷會記成院內用。撤除重來即可（第十四冊 N-31），**不要事後才改成 `dev`**——`shell-builder` 會拒絕。

### 1.5 身分驗證

| 變數                           | 填什麼           | 與實際部署不同 |
| ------------------------------ | ---------------- | -------------- |
| `JWT_SECRET`                   | 用下面的指令產生 |                |
| `JWT_EXPIRES_IN`               | `8h`             |                |
| `SUPER_ADMIN_WORK_ID`          | `sim-admin`      | ✓ 虛構即可     |
| `SUPER_ADMIN_INITIAL_PASSWORD` | `Sim-Init-2026`  | ✓ 虛構即可     |
| `SUPER_ADMIN_DISPLAY_NAME`     | `模擬部署管理員` | ✓ 虛構即可     |

產生 `JWT_SECRET`——**跟院內用同一行 PowerShell，不要用開發機上的 Node.js**，這一輪要驗的就是「只靠 Git 與 Docker」：

```
$b = New-Object byte[] 48; [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($b); [Convert]::ToBase64String($b).TrimEnd('=').Replace('+','-').Replace('/','_')
```

印出一行 64 個字元的字串，貼在 `JWT_SECRET=` 後面。

- 每一輪模擬部署都重新產生，**不要把這一串帶到院內**。
- N-16 用 `sim-admin` / `Sim-Init-2026` 登入，會被要求改密碼，改成什麼都可以，撤除時一起消失。

### 1.6 備份與磁碟

| 變數                  | 填什麼  | 與實際部署不同 |
| --------------------- | ------- | -------------- |
| `BACKUP_DAILY_AT`     | `03:00` |                |
| `DB_DISK_MIN_FREE_MB` | `1024`  |                |

開發機半夜多半關機，排程備份不會跑到，沒關係：N-17 是手動按「立即備份」驗的。

### 1.7 AI

| 變數                         | 填什麼   | 與實際部署不同 |
| ---------------------------- | -------- | -------------- |
| `LLM_PROVIDER`               | `mock`   |                |
| `LLM_ENDPOINT`               | （空白） |                |
| `LLM_API_KEY`                | （空白） |                |
| `LLM_MODEL_ID`               | （空白） |                |
| `LLM_TIMEOUT_SECONDS`        | `150`    |                |
| `LLM_HEALTH_TIMEOUT_SECONDS` | `5`      |                |

- **模擬部署也不准填 `lab`**。compose 把後端固定成正式環境設定，填 `lab` 會拒絕啟動——與院內一模一樣，這正是 N-30 驗收要驗的一條。
- 想用實驗室的真模型試 AI，那不是模擬部署，是[第十三冊](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/13-ai-gateway/index.md)第 1～4 節（走 `npm run dev` 與 SSH 通道，另一套設定）。

### 1.8 其他營運參數

`BINDING_MAX_HOURS` 以下六項：**全部維持範本的值**，與實際部署相同。

______________________________________________________________________

## 2. 填好的樣子

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

______________________________________________________________________

## 3. 填完之後核對

```
docker compose --env-file $cfg config --quiet
```

什麼都沒印出來才算過。再用眼睛核對：

- `HD_IMAGE_TAG` 與 `git describe --tags` 相同
- 三個目錄都在 `C:\hd-sim\` 底下
- 三個埠是 `13000`、`18080`、`18081`（或你 N-07 換過的），而且與位址裡的埠對得上
- `MDM_KIOSK_BASE_URL` 是 **`https://`＋Wi-Fi 那張網卡的 IP**，不是 `localhost`
- **`HD_SHELL_SIGNING=dev`**
- `LLM_PROVIDER=mock`
- 整份沒有任何一個值加了引號

______________________________________________________________________

## 4. 開發機的 IP 變了

換了 Wi-Fi、隔天重新連線，IP 都可能變。症狀是手機開不到下載頁，或外殼一片空白。

| 情況                 | 做什麼                                                                                                                                                                                                             |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 還在同一輪模擬部署中 | 改 `MDM_KIOSK_BASE_URL` 的 IP → `docker compose --env-file $cfg up -d api` → 重跑 `shell-builder`（N-21，它發現位址變了會重簽伺服器憑證）→ `restart patient-web`（N-23）→ 手機上的 App「清除資料」，重新註冊、佈建 |
| 這一輪已經做完       | 不必管，N-31 撤除就好。下一輪重新查 IP 再填                                                                                                                                                                        |

這一段在實際部署**不該發生**：院內的位址擇一之後就不再換（第十四冊之一 0.3 節）。模擬部署碰到一次，正好體會為什麼。

______________________________________________________________________

## 5. 與實際部署的差異總表

帶進院之前再看一次這張表：**右邊那一欄的每一個值，都不可以出現在院內那份 `.env` 裡**——只有三個埠例外，兩邊剛好相同。

| 變數                                                 | 實際部署                                     | 模擬部署                        |
| ---------------------------------------------------- | -------------------------------------------- | ------------------------------- |
| `HD_BACKUP_DIR`、`HD_CONFIG_DIR`、`HD_SHELL_SRC_DIR` | `D:\hd-tablet-care\…`（依資訊室指定的磁碟）  | `C:\hd-sim\…`                   |
| 三個埠                                               | `13000`、`18080`、`18081`（0930 資訊室確認） | 相同（例外）                    |
| `HD_PUBLIC_API_URL`、`CORS_ORIGINS`                  | 護理站連得到的主機名稱或 IP                  | `localhost`                     |
| `MDM_KIOSK_BASE_URL`                                 | `https://<平板連得到的主機>:<病人端埠>`      | `https://<開發機區網 IP>:18081` |
| `HD_SHELL_SIGNING`                                   | **`hospital`**                               | **`dev`**                       |
| `JWT_SECRET`                                         | 院內當場產生                                 | 每一輪各自產生                  |
| `SUPER_ADMIN_*`                                      | 護理長給的工號與名字、臨時密碼               | `sim-admin` 之類的虛構值        |
| 其他                                                 | 相同                                         | 相同                            |

> ⚠️ **不要把模擬部署的 `.env` 複製到院內再改。** 從院內主機上的範本重新複製、照[第十四冊之一](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/14a-env-hospital/index.md)一項一項填。 抄過去最常漏改的是 `HD_SHELL_SIGNING`，而它一旦讓院內主機產生了開發用金鑰，就要撤掉資料卷重來。

______________________________________________________________________

## 版本歷程

| 定版                                                                               | 日期       | 異動                                                                                                   |
| ---------------------------------------------------------------------------------- | ---------- | ------------------------------------------------------------------------------------------------------ |
| [1007](https://94sh09sh19sh.github.io/hd-docs/1007/deployment/14b-env-simulation/) | 2026-10-07 | `JWT_SECRET` 改用 PowerShell 產生；1001 起由第十五冊之二取代，開頭標明                                 |
| [0930](https://94sh09sh19sh.github.io/hd-docs/0930/deployment/14b-env-simulation/) | 2026-09-30 | 首次定版。0929 新增：模擬部署（開發機部署實測）的 .env 逐項填法，與實際部署的差異總表；0930 同步連接埠 |

[← 回第十四冊](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/14-from-zero/index.md)　[← 回部署手冊總覽](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/index.md)
