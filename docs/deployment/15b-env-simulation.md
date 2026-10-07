# 第十五冊之二 · 模擬部署的 `.env` 怎麼填

版本：v0.1　文件狀態：草案（1001 新增）

> 這一冊只做一件事：**模擬部署時，開發機上那一份 `.env`，每一行要填什麼**。
> 它接在[第十五冊](15-from-zero.md) V-12。實際部署的填法看[第十五冊之一](15a-env-hospital.md)。
>
> 模擬部署的意思是：在自己的開發機上，用與院內**一字不差的指令**從零部署一次（《部署規範》DEP-22，第十一冊第 7 節）。
> 所以 `.env` 用的是**同一份範本、同一批變數**，只是值換成開發機的。
>
> **這一冊取代[第十四冊之二](14b-env-simulation.md)**。最大的改變只有一個：
>
> | | 第十四冊之二 | 本冊 |
> |---|---|---|
> | `HD_PUBLIC_API_URL`、`CORS_ORIGINS` | `localhost` | **開發機的區網 IP**，與 `MDM_KIOSK_BASE_URL` 同一個 |
>
> 理由：1001 第二次進院卡在「護理端頁面開得起來，按登入卻 `Failed to fetch`」（[第十四冊之四](14d-second-visit.md) M-01）。
> 那是「網址列的來源」與「`.env` 寫的位址」對不上才會出的錯；模擬部署全用 `localhost` 時兩者永遠一致，**這一類錯誤在模擬部署裡永遠練不到**。
> 改用區網 IP，模擬部署的三個位址就和院內一樣「是一個別人也連得到的位址」，院內會踩的地方在開發機上先踩一次。
>
> 本冊與 repo 裡的 `deploy\hospital.env.example` 不一致時，以範本為準（範本第 13 行的註解仍寫「位址填 `localhost`」，那是舊的做法，照填也能跑，只是練不到上面那件事）。

---

## 0. 開始之前

### 0.1 三份很像的檔案

| 檔案 | 給誰用 | 這次要不要碰 |
|---|---|---|
| `C:\hd-sim\repo\deploy\hospital.env.example` | 部署用的**範本** | 複製它，不要直接改它 |
| `C:\hd-sim\config\.env` | 這次模擬部署的**設定** | **要填的就是這一份** |
| 你平常開發的工作目錄裡的 `.env` | 日常開發（`npm run dev`）用 | **不要碰，也不要拿來抄**。變數名稱不同，而且它的 `LLM_PROVIDER=lab` 之類的值在這裡會讓後端拒絕啟動 |

開檔的指令（V-12，先輸入第十五冊 V-09 的開工三行，`$root` 是 `C:\hd-sim`）：

```powershell
Copy-Item $root\repo\deploy\hospital.env.example $cfg
notepad $cfg
```

### 0.2 寫法的四條規矩

與實際部署相同：**等號前後不要空格、值不要加引號、密碼不要含 `$` `#` 空白與引號、`#` 開頭的說明行不要刪**。
理由見[第十五冊之一](15a-env-hospital.md) 0.2 節。

### 0.3 要先查好的兩件事

模擬部署的值幾乎都是固定的，只有兩件要自己查：

**一、要測的 tag**：第十五冊 V-03 準備的那一個，也就是 V-11 `git describe --tags` 印出來的。

**二、開發機的區網 IP**——這就是模擬部署的 `<主機>`（第十五冊 V-08），三個位址都用它：

```powershell
ipconfig
```

找「無線區域網路介面卡 Wi-Fi」那一段的 **IPv4 位址**，例如 `192.168.1.23`。

| 注意 | 為什麼 |
|---|---|
| 要用 **Wi-Fi 那一張網卡**的 IP，不是 `vEthernet (WSL)` 或 `vEthernet (Default Switch)` 那幾段 | 那幾張是 Docker 與 WSL 的虛擬網卡，手機連不到 |
| 手機要連**同一個 Wi-Fi** | 不同網段互相看不到 |
| IP 每次連線可能會變 | 變了要照本冊第 4 節處理。**同一輪模擬部署之內不要換 Wi-Fi** |

下面用 `192.168.1.23` 當範例，**請換成你查到的**。

> 💡 這一步就是院內 V-08 的縮小版：院內要問資訊室「護理站與平板用什麼連主機」，模擬部署的答案是「開發機的 Wi-Fi IP」。
> 院內還要多確認 IP 會不會變、護理站查不查得到名稱；開發機上只要同一輪不換 Wi-Fi 就好。

---

## 1. 逐項填

照範本由上往下的順序。**「與實際部署不同」那一欄打勾的，就是模擬部署要特別留意的地方。**

### 1.1 版本與目錄

| 變數 | 填什麼 | 與實際部署不同 |
|---|---|---|
| `HD_IMAGE_TAG` | 要測的 tag，例如 `v0.3.0` | |
| `HD_BACKUP_DIR` | `C:\hd-sim\backups` | ✓ 根目錄不同（院內是 `C:\hd\hd-tablet-care\…`） |
| `HD_CONFIG_DIR` | `C:\hd-sim\config` | ✓ 同上 |

- 要測更新演練時，會另打一個測試 tag（第十一冊第 7 節），那時照 W-19 把 `HD_IMAGE_TAG` 改成測試 tag。
- 目錄一樣**不要放在 OneDrive 或 `C:\Users\<帳號>\` 底下的桌面／文件／下載**。模擬部署要練的就是院內那套規矩。

### 1.2 連接埠

| 變數 | 填什麼 | 與實際部署不同 |
|---|---|---|
| `HD_API_PORT` | `13000` | 與院內相同（院內是資訊室登記的；開發機自己挑） |
| `HD_NURSE_PORT` | `18080` | 同上 |
| `HD_PATIENT_PORT` | `18081` | 同上 |

- 故意**不用** `3000`、`5173`、`5174`：那是平常 `npm run dev` 用的，兩者同時開會撞。
- V-07 查到被佔用時，自己換一個，本冊後面所有用到那個埠的地方跟著改。

### 1.3 位址

| 變數 | 填什麼 | 與實際部署不同 |
|---|---|---|
| `HD_PUBLIC_API_URL` | `http://192.168.1.23:13000`（**換成你的 IP**） | ✓ 院內是 V-08 定的院內名稱或 IP |
| `CORS_ORIGINS` | `http://192.168.1.23:18080`（同一個 IP） | ✓ 同上 |
| `MDM_KIOSK_BASE_URL` | `https://192.168.1.23:18081`（同一個 IP） | ✓ 同上 |

- **三項用同一個 IP，寫法一字不差**——與院內一樣。
- 護理端在開發機自己的瀏覽器開，網址是 `http://192.168.1.23:18080`（**不是 `localhost`**）。連自己的區網 IP 不經過防火牆，不必另開規則。
- **`MDM_KIOSK_BASE_URL` 不能用 `localhost`**：手機上的 `localhost` 是手機自己。這一條與實際部署一樣要 **`https://`**。
- 第十五冊 V-17 的方框會請你**故意用 `http://localhost:18080` 開一次、按登入**，看 `Failed to fetch` 長什麼樣——這正是院內用錯網址時會看到的畫面。
  看過一次，到院內就認得出來。

> 想照舊版用 `localhost` 也可以跑：`HD_PUBLIC_API_URL=http://localhost:13000`、`CORS_ORIGINS=http://localhost:18080`，`MDM_KIOSK_BASE_URL` 仍是區網 IP。
> 只是那樣 V-17 的第二～四段都練不到，**交給院方的 tag 至少要有一輪是用區網 IP 跑的**。

### 1.4 外殼 App

| 變數 | 填什麼 | 與實際部署不同 |
|---|---|---|
| `HD_SHELL_SRC_DIR` | `C:\hd-sim\hd-kiosk-shell` | ✓ 根目錄不同 |
| `HD_SHELL_SIGNING` | **`dev`** | ✓ **實際部署是 `hospital`**。範本預設是 `hospital`，**這一項一定要改** |
| `KIOSK_SHELL_MIN_VERSION` | 留空 | |

- `HD_SHELL_SIGNING=dev` 讓 `shell-builder` 產生「開發用」的簽章金鑰，V-22 會印出「APK 簽章金鑰（開發用）」。
  這把金鑰簽出來的 APK 與院內版**不能互相覆蓋安裝**，這正是要的效果：開發用的東西不會混進院內。
- 忘了改、留著 `hospital` 跑下去的話，資料卷會記成院內用。撤除重來即可（第十五冊 V-32），**不要事後才改成 `dev`**——`shell-builder` 會拒絕。

### 1.5 身分驗證

| 變數 | 填什麼 | 與實際部署不同 |
|---|---|---|
| `JWT_SECRET` | 用下面的指令產生 | |
| `JWT_EXPIRES_IN` | `8h` | |
| `SUPER_ADMIN_WORK_ID` | `sim-admin` | ✓ 虛構即可 |
| `SUPER_ADMIN_INITIAL_PASSWORD` | `Sim-Init-2026` | ✓ 虛構即可 |
| `SUPER_ADMIN_DISPLAY_NAME` | `模擬部署管理員` | ✓ 虛構即可 |

產生 `JWT_SECRET`——**跟院內用同一行 PowerShell，不要用開發機上的 Node.js**，這一輪要驗的就是「只靠 Git 與 Docker」：

```powershell
$b = New-Object byte[] 48; [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($b); [Convert]::ToBase64String($b).TrimEnd('=').Replace('+','-').Replace('/','_')
```

印出一行 64 個字元的字串，貼在 `JWT_SECRET=` 後面。

- 每一輪模擬部署都重新產生，**不要把這一串帶到院內**。
- V-17 用 `sim-admin` / `Sim-Init-2026` 登入，會被要求改密碼，改成什麼都可以，撤除時一起消失。

### 1.6 備份與磁碟

| 變數 | 填什麼 | 與實際部署不同 |
|---|---|---|
| `BACKUP_DAILY_AT` | `03:00` | |
| `DB_DISK_MIN_FREE_MB` | `1024` | |

開發機半夜多半關機，排程備份不會跑到，沒關係：V-18 是手動按「立即備份」驗的。

### 1.7 AI

| 變數 | 填什麼 | 與實際部署不同 |
|---|---|---|
| `LLM_PROVIDER` | `mock` | |
| `LLM_ENDPOINT` | （空白） | |
| `LLM_API_KEY` | （空白） | |
| `LLM_MODEL_ID` | （空白） | |
| `LLM_TIMEOUT_SECONDS` | `150` | |
| `LLM_HEALTH_TIMEOUT_SECONDS` | `5` | |

- **模擬部署也不准填 `lab`**。compose 把後端固定成正式環境設定，填 `lab` 會拒絕啟動——與院內一模一樣，這正是 V-31 驗收要驗的一條。
- 想用實驗室的真模型試 AI，那不是模擬部署，是[第十三冊](13-ai-gateway.md)第 1～4 節（走 `npm run dev` 與 SSH 通道，另一套設定）。

### 1.8 其他營運參數

`BINDING_MAX_HOURS` 以下六項：**全部維持範本的值**，與實際部署相同。

### 1.9 院方透析清單 API（1005 新增）

| 變數 | 填什麼 | 與實際部署不同 |
|---|---|---|
| `HOSPITAL_API_BASE_URL` | `http://hospital-api-sim:8090/dialysislist.php` | **不同**：院內第三次進院是空白，只探測 |
| `HD_SIMULATION_DEPLOYMENT` | `yes` | **不同**：院內永遠空白 |

- `hospital-api-sim` 是模擬院方 API，跟 `api` 用同一個映像檔，**只在 `--profile simulation` 時啟動**（第十五冊 V-30a），不開埠，只有 `api` 連得到。病人全是虛構的
- compose 把後端固定成正式環境設定，模擬部署也一樣；**沒有 `HD_SIMULATION_DEPLOYMENT=yes`，位址指向模擬時後端拒絕啟動**——院內就是靠這一條擋住抄錯的設定，V-30a 最後會故意清空它驗一次

---

## 2. 填好的樣子

只有四處要換成你自己的：`HD_IMAGE_TAG`、三個位址裡的 IP（同一個）、`JWT_SECRET`。其餘照抄即可：

```
HD_IMAGE_TAG=v0.3.0

HD_BACKUP_DIR=C:\hd-sim\backups
HD_CONFIG_DIR=C:\hd-sim\config

HD_API_PORT=13000
HD_NURSE_PORT=18080
HD_PATIENT_PORT=18081

HD_PUBLIC_API_URL=http://192.168.1.23:13000
CORS_ORIGINS=http://192.168.1.23:18080
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

HOSPITAL_API_BASE_URL=http://hospital-api-sim:8090/dialysislist.php
HD_SIMULATION_DEPLOYMENT=yes

BINDING_MAX_HOURS=6
BINDING_EXPIRY_SWEEP_SECONDS=60
SYMPTOM_TREND_WINDOW_DAYS=30
SYMPTOM_TREND_REPORT_LIMIT=10
DEVICE_ONLINE_THRESHOLD_SECONDS=90
REALTIME_HEARTBEAT_SECONDS=20
```

---

## 3. 填完之後核對

與院內用同樣的三條（第十五冊之一第 3 節）：

```powershell
docker compose --env-file $cfg config --quiet
Select-String -Path $cfg -Pattern '^[^#].*(<|>|hd-server|localhost)'
Select-String -Path $cfg -Pattern '^(HD_PUBLIC_API_URL|CORS_ORIGINS|MDM_KIOSK_BASE_URL)='
```

前兩條什麼都沒印出來才算過（第二條只看不是 `#` 開頭的行）；第三條印出三行，IP 都相同。再用眼睛核對：

- [ ] `HD_IMAGE_TAG` 與 `git describe --tags` 相同
- [ ] 三個目錄都在 `C:\hd-sim\` 底下
- [ ] 三個埠是 `13000`、`18080`、`18081`（或你 V-07 換過的），而且與位址裡的埠對得上
- [ ] 三個位址都是 **Wi-Fi 那張網卡的 IP**，一字不差；`MDM_KIOSK_BASE_URL` 是 **`https://`**
- [ ] **`HD_SHELL_SIGNING=dev`**
- [ ] `LLM_PROVIDER=mock`
- [ ] `HOSPITAL_API_BASE_URL` 指向 `hospital-api-sim`、`HD_SIMULATION_DEPLOYMENT=yes`（1005 新增）
- [ ] 整份沒有任何一個值加了引號

---

## 4. 開發機的 IP 變了

換了 Wi-Fi、隔天重新連線，IP 都可能變。症狀是護理端登入 `Failed to fetch`、手機開不到下載頁，或外殼一片空白。

| 情況 | 做什麼 |
|---|---|
| 還在同一輪模擬部署中 | 三個位址的 IP 一起改 → `docker compose --env-file $cfg build` → `up -d`（`HD_PUBLIC_API_URL` 寫在網頁檔案裡，要重建）→ 重跑 `shell-builder`（V-22，它發現位址變了會重簽伺服器憑證）→ `restart patient-web`（V-24）→ 手機上的 App「清除資料」，重新註冊、佈建 |
| 這一輪已經做完 | 不必管，V-32 撤除就好。下一輪重新查 IP 再填 |

這一段在實際部署**不該發生**：院內的位址擇一之後就不再換（第十五冊 V-08）。模擬部署碰到一次，正好體會為什麼——改一個 IP，要重建網頁、重簽憑證、每一台平板重新佈建。

---

## 5. 與實際部署的差異總表

帶進院之前再看一次這張表：**右邊那一欄的每一個值，都不可以出現在院內那份 `.env` 裡**——只有三個埠例外，兩邊剛好相同。

| 變數 | 實際部署 | 模擬部署 |
|---|---|---|
| `HD_BACKUP_DIR`、`HD_CONFIG_DIR`、`HD_SHELL_SRC_DIR` | `C:\hd\hd-tablet-care\…`（1001 院內實際用的） | `C:\hd-sim\…` |
| 三個埠 | `13000`、`18080`、`18081`（0930 資訊室確認） | 相同（例外） |
| 三個位址的主機 | V-08 定的院內名稱或 IP | 開發機的 Wi-Fi IP |
| `HD_SHELL_SIGNING` | **`hospital`** | **`dev`** |
| `HOSPITAL_API_BASE_URL`（1005） | 空白（第三次進院只探測；探測過、報備過才填院方的位址） | `http://hospital-api-sim:8090/dialysislist.php` |
| `HD_SIMULATION_DEPLOYMENT`（1005） | **永遠空白** | **`yes`** |
| `JWT_SECRET` | 院內當場產生 | 每一輪各自產生 |
| `SUPER_ADMIN_*` | 護理長給的工號與名字、臨時密碼 | `sim-admin` 之類的虛構值 |
| 其他 | 相同 | 相同 |

兩邊**形狀相同**的地方也值得記住：三個位址都是「同一個別人連得到的主機」，護理端都用 `http://<主機>:18080` 開，都不用 `localhost`。

> ⚠️ **不要把模擬部署的 `.env` 複製到院內再改。** 從院內主機上的範本重新複製、照[第十五冊之一](15a-env-hospital.md)一項一項填。
> 抄過去最常漏改的是 `HD_SHELL_SIGNING`，而它一旦讓院內主機產生了開發用金鑰，就要撤掉資料卷重來。

---

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|
| [1007](https://94sh09sh19sh.github.io/hd-docs/1007/deployment/15b-env-simulation/) | 2026-10-07 | 首次定版。第十五冊之二：模擬部署的 .env 怎麼填（取代第十四冊之二） |

[← 回第十五冊](15-from-zero.md)　[← 回部署手冊總覽](index.md)
