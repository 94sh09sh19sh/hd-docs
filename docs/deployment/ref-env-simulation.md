# `.env` 怎麼填之一：開發機演練（第 0～1 節）

上層文件：《[`.env` 怎麼填](ref-env.md)》

> **狀態：現行（常備參考）。** 這一份只做一件事：**🧪 開發機演練（模擬部署）時，開發機上那一份 `.env`，每一行要填什麼**。接在《[從零部署本系統](ref-fresh-install-4.md)》V-12。🏥 院內的填法看上層。
>
> **從哪幾份舊冊改寫（1117）**：第十五冊之二全部，逐項對到 `v0.5.0` 的 `deploy\hospital.env.example`（模擬讀檔改成主要做法、讀檔四行與 `COMPOSE_FILE` 寫進「填好的樣子」、差異總表補上讀檔那幾列）。
>
> **編號**：沒有步驟編號；節號沿用第十五冊之二（1.1～1.10），差異總表在第 5 節。
>
> **分成兩份**（1118 拆，每份 300 行內）：本份是第 0～1 節（開始之前、逐項填）；《[`.env` 怎麼填之二：開發機演練（第 2～5 節）](ref-env-simulation-2.md)》是第 2～5 節（填好的樣子、填完之後核對、開發機的 IP 變了、與院內的差異總表）。

模擬部署的意思是：在自己的開發機上，用與院內**一字不差的指令**從零部署一次（《[部署規範](../requirements/deployment-spec.md)》DEP-22，《[從零部署本系統之二](ref-fresh-install-detail-2.md)》第 7 節）。所以 `.env` 用的是**同一份範本、同一批變數**，只是值換成開發機的。

1001 起與第十四冊之二最大的不同：

| | 第十四冊之二 | 這一份 |
|---|---|---|
| `HD_PUBLIC_API_URL`、`CORS_ORIGINS` | `localhost` | **開發機的區網 IP**，與 `MDM_KIOSK_BASE_URL` 同一個 |

理由：1001 第二次進院卡在「護理端頁面開得起來，按登入卻 `Failed to fetch`」（《[第二次進院紀錄](record-2-1001.md)》M-01）。那是「網址列的來源」與「`.env` 寫的位址」對不上才會出的錯；模擬部署全用 `localhost` 時兩者永遠一致，**這一類錯誤在模擬部署裡永遠練不到**。改用區網 IP，模擬部署的三個位址就和院內一樣「是一個別人也連得到的位址」，院內會踩的地方在開發機上先踩一次。

這一份與 repo 裡的 `deploy\hospital.env.example` 不一致時，以範本為準（範本第 13 行的註解到 `v0.5.0` 仍寫「位址填 `localhost`」，那是舊的做法，照填也能跑，只是練不到上面那件事）。

## 摘要

- 🧪 開發機那一份 `.env` 每一行要填什麼；同一份範本、同一批變數，值換成開發機的
- 三個位址用開發機 Wi-Fi 網卡的區網 IP（用 `localhost` 永遠練不到 1001 卡住的登入問題）；先查好 tag 與 IP（0.3 節）
- 與院內不同、一定要改的：根目錄 `C:\hd-sim`、`HD_SHELL_SIGNING=dev`、`HD_SIMULATION_DEPLOYMENT=yes`、`SUPER_ADMIN_*` 用虛構值
- 院方資料（1.9）：主要做法是模擬讀檔（`docker-compose.hospital-files-sim.yml`），跟院內同一條路；直接打模擬院方 API 是舊做法，仍可用
- `v0.5.0` 範本第 98 行斷掉的註解一樣要刪（上層 0.1 節）
- 填好的樣子、核對、開發機的 IP 變了、與院內的差異總表在之二

## 0. 開始之前

### 0.1 三份很像的檔案

| 檔案 | 給誰用 | 這次要不要碰 |
|---|---|---|
| `C:\hd-sim\repo\deploy\hospital.env.example` | 部署用的**範本** | 複製它，不要直接改它 |
| `C:\hd-sim\config\.env` | 這次模擬部署的**設定** | **要填的就是這一份** |
| 你平常開發的工作目錄裡的 `.env` | 日常開發（`npm run dev`）用 | **不要碰，也不要拿來抄**。變數名稱不同，而且它的 `LLM_PROVIDER=lab` 之類的值在這裡會讓後端拒絕啟動 |

開檔的指令（V-12，先輸入《[從零部署本系統](ref-fresh-install-3.md)》V-09 的開工三行，`$root` 是 `C:\hd-sim`）：

```powershell
Copy-Item $root\repo\deploy\hospital.env.example $cfg
notepad $cfg
```

`v0.5.0` 的範本第 98 行是一行開頭沒有 `#` 的斷掉註解「aw_txt 與 hb-status.json）」，複製完**刪掉那一行**（或在開頭加 `# `），否則 compose 讀不到 `.env`（上層 0.1 節；1116 模擬實測）。

### 0.2 寫法的四條規矩

與院內相同：**等號前後不要空格、值不要加引號、密碼不要含 `$` `#` 空白與引號、`#` 開頭的說明行不要刪**。理由見上層 0.2 節。

### 0.3 要先查好的兩件事

模擬部署的值幾乎都是固定的，只有兩件要自己查：

**一、要測的 tag**：《[從零部署本系統](ref-fresh-install-2.md)》V-03 準備的那一個，也就是 V-11 `git describe --tags` 印出來的。

**二、開發機的區網 IP**——這就是模擬部署的 `<主機>`（V-08），三個位址都用它：

```powershell
ipconfig
```

找「無線區域網路介面卡 Wi-Fi」那一段的 **IPv4 位址**。

| 注意 | 為什麼 |
|---|---|
| 要用 **Wi-Fi 那一張網卡**的 IP，不是 `vEthernet (WSL)` 或 `vEthernet (Default Switch)` 那幾段 | 那幾張是 Docker 與 WSL 的虛擬網卡，手機連不到 |
| 手機要連**同一個 Wi-Fi** | 不同網段互相看不到 |
| IP 每次連線可能會變 | 變了要照第 4 節處理。**同一輪模擬部署之內不要換 Wi-Fi** |

下面用 `192.0.2.23` 當範例，**請換成你查到的**。

> 💡 這一步就是院內 V-08 的縮小版：院內要問資訊室「護理站與平板用什麼連主機」，模擬部署的答案是「開發機的 Wi-Fi IP」。院內還要多確認 IP 會不會變、護理站查不查得到名稱；開發機上只要同一輪不換 Wi-Fi 就好。

---

## 1. 逐項填

照範本由上往下的順序（範本順序：1.1～1.7、1.9 的讀檔四行、1.9 的院方 API 兩行、1.8；1.10 範本裡已經沒有）。**「與院內不同」那一欄打勾的，就是模擬部署要特別留意的地方。**

### 1.1 版本與目錄

| 變數 | 填什麼 | 與院內不同 |
|---|---|---|
| `HD_IMAGE_TAG` | 要測的 tag，例如 `v0.5.0` | |
| `HD_BACKUP_DIR` | `C:\hd-sim\backups` | ✓ 根目錄不同（院內是 `C:\hd\hd-tablet-care\…`） |
| `HD_CONFIG_DIR` | `C:\hd-sim\config` | ✓ 同上 |
| `HD_EXPORT_DIR` | `C:\hd-sim\export` | ✓ 同上；與備份資料夾分開（1027 迭代 28 起，《[取出資料](ref-data-export.md)》） |

- 要測更新演練時，會另打一個測試 tag（《[從零部署本系統之二](ref-fresh-install-detail-2.md)》第 7 節），那時照《[本系統換版與退回](ref-upgrade.md)》W-19 把 `HD_IMAGE_TAG` 改成測試 tag。
- 目錄一樣**不要放在 OneDrive 或 `C:\Users\<帳號>\` 底下的桌面／文件／下載**。模擬部署要練的就是院內那套規矩。

### 1.2 連接埠

| 變數 | 填什麼 | 與院內不同 |
|---|---|---|
| `HD_API_PORT` | `13000` | 與院內相同（院內是資訊室登記的；開發機自己挑） |
| `HD_NURSE_PORT` | `18080` | 同上 |
| `HD_PATIENT_PORT` | `18081` | 同上 |

- 故意**不用** `3000`、`5173`、`5174`：那是平常 `npm run dev` 用的，兩者同時開會撞。
- V-07 查到被佔用時，自己換一個，這一份後面所有用到那個埠的地方跟著改。

### 1.3 位址

| 變數 | 填什麼 | 與院內不同 |
|---|---|---|
| `HD_PUBLIC_API_URL` | `http://192.0.2.23:13000`（**換成你的 IP**） | ✓ 院內是 V-08 定的固定 IP |
| `CORS_ORIGINS` | `http://192.0.2.23:18080`（同一個 IP） | ✓ 同上 |
| `MDM_KIOSK_BASE_URL` | `https://192.0.2.23:18081`（同一個 IP） | ✓ 同上 |

- **三項用同一個 IP，寫法一字不差**——與院內一樣。
- 護理端在開發機自己的瀏覽器開，網址是 `http://192.0.2.23:18080`（**不是 `localhost`**）。連自己的區網 IP 不經過防火牆，不必另開規則。
- **`MDM_KIOSK_BASE_URL` 不能用 `localhost`**：手機上的 `localhost` 是手機自己。這一條與院內一樣要 **`https://`**。
- V-17 的方框會請你**故意用 `http://localhost:18080` 開一次、按登入**，看 `Failed to fetch` 長什麼樣——這正是院內用錯網址時會看到的畫面。看過一次，到院內就認得出來。

> 想照舊版用 `localhost` 也可以跑：`HD_PUBLIC_API_URL=http://localhost:13000`、`CORS_ORIGINS=http://localhost:18080`，`MDM_KIOSK_BASE_URL` 仍是區網 IP。只是那樣 V-17 的第二～四段都練不到，**交給院方的 tag 至少要有一輪是用區網 IP 跑的**。

### 1.4 外殼 App

| 變數 | 填什麼 | 與院內不同 |
|---|---|---|
| `HD_SHELL_SRC_DIR` | `C:\hd-sim\hd-kiosk-shell` | ✓ 根目錄不同 |
| `HD_SHELL_SIGNING` | **`dev`** | ✓ **院內是 `hospital`**。範本預設是 `hospital`，**這一項一定要改** |
| `KIOSK_SHELL_MIN_VERSION` | 留空 | |

- `HD_SHELL_SIGNING=dev` 讓 `shell-builder` 產生「開發用」的簽章金鑰，V-22 會印出「APK 簽章金鑰（開發用）」。這把金鑰簽出來的 APK 與院內版**不能互相覆蓋安裝**，這正是要的效果：開發用的東西不會混進院內。
- 忘了改、留著 `hospital` 跑下去的話，資料卷會記成院內用。撤除重來即可（V-32），**不要事後才改成 `dev`**——`shell-builder` 會拒絕。

### 1.5 身分驗證

| 變數 | 填什麼 | 與院內不同 |
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

| 變數 | 填什麼 | 與院內不同 |
|---|---|---|
| `BACKUP_DAILY_AT` | `03:00` | |
| `DB_DISK_MIN_FREE_MB` | `1024` | |

開發機半夜多半關機，排程備份不會跑到，沒關係：V-18 是手動按「立即備份」驗的。

### 1.7 AI

| 變數 | 填什麼 | 與院內不同 |
|---|---|---|
| `LLM_PROVIDER` | `mock` | |
| `LLM_ENDPOINT` | （空白） | |
| `LLM_API_KEY` | （空白） | |
| `LLM_MODEL_ID` | （空白） | |
| `LLM_TIMEOUT_SECONDS` | `150` | |
| `LLM_HEALTH_TIMEOUT_SECONDS` | `5` | |

- **模擬部署也不准填 `lab`**。compose 把後端固定成正式環境設定，填 `lab` 會拒絕啟動——與院內一模一樣，這正是 V-31 驗收要驗的一條。
- 想用實驗室的真模型試 AI，那不是模擬部署，是《[AI 閘道](ref-ai-gateway.md)》的開發機做法（走 `npm run dev` 與 SSH 通道，另一套設定）。

### 1.8 其他營運參數

`BINDING_MAX_HOURS` 以下六項：**全部維持範本的值**，與院內相同。

### 1.9 院方資料（1005 新增，1111 迭代 32 加讀檔）

院內 1110 起讀抓取腳本存下的檔、不打院方 API，所以模擬部署的主要做法也是**讀檔**：模擬院方 API 照抓取腳本的契約把兩種留底檔與狀態檔寫進一個具名資料卷（`hd-tablet-care-hospital-sim-files`，不是 external），`api` 以唯讀讀同一個。資料夾裡有模擬標記檔 `.hd-simulated`，所以一樣要 `HD_SIMULATION_DEPLOYMENT=yes`。`hospital-api-sim` 跟 `api` 用同一個映像檔，**只在 `--profile simulation` 時啟動**，不開埠，只有 `api` 連得到；病人全是虛構的。

三種填法，六行各自改成下表那一欄的樣子（從零部署到 V-30a 之前，先用「還沒接」那一欄）：

| 變數 | 還沒接（V-12） | A 模擬讀檔（主要做法） | B 練院內那種路徑（帶空白與中文） | C 打模擬院方 API（舊做法） |
|---|---|---|---|---|
| `HD_DIALYSIS_LIST_DIR` | （空白） | （空白） | `C:\hd-sim\院方 資料\透析清單` | （空白） |
| `HD_LAB_DIR` | （空白） | （空白） | （空白） | （空白） |
| `COMPOSE_FILE` | 維持註解 | `docker-compose.yml;docker-compose.hospital-files-sim.yml` | `docker-compose.yml;docker-compose.dialysis-files.yml` | 維持註解 |
| `HOSPITAL_LAB_FIELD_MAP` | （空白） | （空白） | （空白） | （空白） |
| `HOSPITAL_API_BASE_URL` | （空白） | （空白） | （空白） | `http://hospital-api-sim:8090/dialysislist.php` |
| `HD_SIMULATION_DEPLOYMENT` | `yes` | `yes` | `yes` | `yes` |

- **A**：改完 `docker compose --env-file $cfg --profile simulation up -d`，等 3 分鐘再跑讀檔檢查，「模擬標記檔：有」是對的。`HD_DIALYSIS_LIST_DIR`、`HD_LAB_DIR` 留空（那是院內的主機路徑，模擬的路徑由 `docker-compose.hospital-files-sim.yml` 自己帶）
- **B**：先做過 A，再把模擬的檔複製到帶空白與中文的資料夾、照院內的掛法掛一次（指令在《[讀檔：啟用、檢查、停用](ref-dialysis-files.md)》，1116 演練的 SY-10 B2）。讀檔檢查要「在、讀得到」「唯讀：是」「模擬標記檔：有」。這份是複製出來的、不會再更新，之後出現「未更新」提示是正常的
- **C**：1005～1109 的做法，院內已不用，留給對照舊紀錄與練直接探測（《[從零部署本系統](ref-fresh-install-6.md)》V-30a 的舊做法一節）
- 不管哪一種，compose 都把後端固定成正式環境設定；**沒有 `HD_SIMULATION_DEPLOYMENT=yes`**，C 是後端拒絕啟動（指出 DEP-46），A、B 是同步時整次作廢（「院方資料同步」卡最新一列「拒收（正式環境收到模擬資料）」、資料庫一筆都沒多）。院內就是靠這一條擋住抄錯的設定，演練會故意清空它驗一次（SY-M1）
- `HOSPITAL_API_BASE_URL` 與 `HD_DIALYSIS_LIST_DIR` 兩個都填，後端拒絕啟動——與院內一樣

### 1.10 判斷規則的書面確認閘門（1010 新增，同日迭代 18.1 拿掉）

**`.env` 裡沒有這一項了**（迭代 18 時是 `HIGH_RISK_WRITTEN_CONFIRMATION`）。迭代 18.1 起書面確認由系統管理者在護理端系統管理「判斷規則」登記；**模擬部署永遠不登記**。照舊版範本填過的設定目錄，那一行刪掉即可（留著不生效，後端啟動時提醒一聲）。

- 沒登記時判斷輔助只對合成資料病人執行。模擬院方 API 的病人病歷號是 99 開頭、沒有合成資料前綴，系統當真實病人看，**模擬部署上比對不到它們是對的**；要看判斷輔助的畫面，照《完整手動測試手冊》迭代 18 分冊 `ab12` 在開發機上看。

---

---

下一份：《[`.env` 怎麼填之二：開發機演練（第 2～5 節）](ref-env-simulation-2.md)》｜[部署手冊目錄](index.md)

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|
| [1118](https://94sh09sh19sh.github.io/hd-docs/1118/deployment/ref-env-simulation/) | 2026-11-18 | 首次定版。1117 部署手冊整套重寫時由舊冊改寫而成（舊冊號見目錄最後的對照），步驟編號不變；1118 照每份約 300 行的上限拆檔，後段移到同一套的下一份 |

[← 回部署手冊目錄](index.md)
