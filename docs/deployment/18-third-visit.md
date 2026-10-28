# 第十八冊 · 第三次進院：實際部署（新手版）

版本：v0.1　文件狀態：草案（1028 新增）　編號：`J-xx`　**只要印這一冊帶進去**

> **這一冊給誰**：下一次（第三次）進院、要在院內主機上動手的人，沒去過 0922、1001 也看得懂。
>
> 院內主機不是一台空機器：1001 已經把 `v0.3.0` 裝上去、三個服務還在跑，只是護理站登不進去（[第十五冊之三](15c-why-1001-failed.md)）。所以這一次**不是從零部署**，是四件事接起來做：**先抄現況 → 主機位址換成 IP、讓護理站登得進去 → 換到新版 → 備份還原、重新開機、探測院方 API**。以前這四件事分散在第十五冊、之三、之四與第十一冊 W-19，這一冊把它們排成一條線，指令全部抄進來，**現場只看這一冊就做得完**。
>
> **出發前一定要先照[第十七冊](17-rehearsal.md)在開發機上把這一冊從頭到尾演練一次**（J-01）。這一冊沒有「🧪 模擬部署」方框：模擬部署要改做什麼，全部寫在第十七冊。
>
> 指令抄自第十五冊、之三、之四與第十一冊，步驟標題後面註明出處（例如「＝T-07、V-17」），對照表在附錄一。**兩邊不一致時以原冊為準**，規則的真本是《[部署規範](../requirements/deployment-spec.md)》。

> **公開範圍**：文件站是公開的。這一冊一律用代稱，**值只寫在《[部署演練紀錄](../notes/deployment-drills.md)》第 12 節（印出來的那一份）**，不寫進任何會上站的文件、不拍照：
>
> | 代稱 | 指的是 |
> |---|---|
> | `<名稱>` | 1001 填進 `.env` 的那個主機名稱 |
> | `<IP>` | 資訊室確認、而且固定下來的院內主機 IP（1007 答覆：固定） |
> | `<新 tag>` | 這一次要換上去的版本，例如 `v0.4.0`；J-01 定下來 |
>
> 打指令時連同 `<`、`>` 一起換掉。

---

## 摘要

- 第三次進院的完整步驟，編號 `J-xx`：主機上已經有 1001 裝的 `v0.3.0`，這一次是「接著做」，不是從零部署
- 順序：出發前（第 1 節）→ 到場先看、先抄（第 2 節）→ 換成 IP、護理站登入（第 3 節）→ 換到新版（第 4 節）→ 備份、防毒、重新開機（第 5 節）→ 探測院方 API（第 6 節）→ 暫用平板（第 7 節，時間夠才做）→ 冒煙測試與交接（第 8 節）
- **先在 `v0.3.0` 上把登入修好，再換新版**：兩件事分開，出錯時分得出是哪一件；新版出問題也退得回一個登得進去的舊版
- 這一次的成敗只看一件事：**護理站的電腦登得進去**（第 0.2 節）；登入通了才往下做
- 出發前要先照第十七冊在開發機上演練一次，沒演練過的 tag 不准帶進院
- 附錄：步驟對照、新版出問題怎麼退回、護理端登不進去怎麼查、一張紙帶進去

## 0. 讀之前

### 0.1 這一次要做到什麼

| 優先 | 目標 | 在哪一節 |
|---|---|---|
| 1 | **護理站的電腦登得進去** | 第 2～3 節 |
| 2 | 換到新版（`v0.3.0` 之後 10 月做的所有功能，含 19 個資料庫遷移） | 第 4 節 |
| 3 | 備份還原、重新開機各走一次；防毒排除交給資訊室 | 第 5 節 |
| 4 | 用探測工具看一次院方透析清單 API 的實際長相（只看格式，不看內容） | 第 6 節 |
| 5 | 暫用平板（Galaxy Tab S6 Lite）佈建一台 | 第 7 節，**時間夠、院方准才做** |

**不是這一次的目標**：院方 API 正式啟用（要等探測結果與 Q-35 報備）、AI 接模型、遊戲化與獎勵制度的開關、輸入真實病人資料。

### 0.2 三種結果

| 等級 | 達成什麼 |
|---|---|
| **A 完全成功** | 優先 1～4 全部做完，冒煙測試通過、交接完成 |
| **B 部分成功** | 優先 1 做到了（護理站登得進去），其餘有做不完的。**卡在哪、要等誰**逐項寫下來 |
| **C 失敗** | 護理站仍然登不進去。照第 8 節 J-32 停手，把每一步的結果與錯誤原文全部帶回來 |

### 0.3 時間怎麼排

| 段落 | 大約時間 | 備註 |
|---|---|---|
| 第 2 節：先看、先抄 | 30 分鐘 | 不改任何東西 |
| 第 3 節：換成 IP、登入 | 60～90 分鐘 | 建置約 10 分鐘、`shell-builder` 約 5～10 分鐘 |
| 第 4 節：換到新版 | 40～60 分鐘 | 建置約 10 分鐘；Docker 查不到網域時要重打 |
| 第 5 節：備份、防毒、重新開機 | 30～40 分鐘 | 重新開機要資訊室同意時段 |
| 第 6 節：院方 API | 15 分鐘 | 要有人給位址 |
| 第 7 節：平板 | 45～60 分鐘 | 第一次做 |
| 第 8 節：冒煙測試、交接 | 45 分鐘 | |

**合計約 5～6 小時，而且這是順利的版本。** 實際時間以第十七冊演練時量到的為準，再多抓一小時。

**時間不夠時怎麼取捨**：

| 什麼時候 | 剩下的時間 | 怎麼做 |
|---|---|---|
| J-14 護理站登入成功時 | 不到 2.5 小時 | **不換新版**。直接做第 5 節（在 `v0.3.0` 上備份還原、重新開機），跳過第 4、6、7 節，再做第 8 節。新版下次再換 |
| J-19 新版登入成功時 | 不到 1.5 小時 | 第 5 節只做 J-22（備份還原），J-25 重新開機與第 7 節留到下次 |
| 任何時候 | 離下班不到 45 分鐘 | 停在目前這一步，直接做第 8 節 J-31～J-32 |

### 0.4 每一步的三塊

每一步都分三塊：**做什麼**、**怎麼知道成功了**、**可能怎麼壞**。**「怎麼知道成功了」那一塊沒看到，就是沒成功**，不要因為「好像沒出錯」就往下。

每一步開始與結束**各記一次時間**，錯誤訊息**抄原文、抄到最後一行**，寫進演練紀錄第 12 節。1001 只有一步有計時，這次估時間才只能靠猜。

### 0.5 會碰到的名詞

| 名詞 | 一句話 |
|---|---|
| **PowerShell** | Windows 內建的指令視窗，這一冊的指令都在這裡打。開法：開始選單輸入 `PowerShell` → 按「Windows PowerShell」 |
| **系統管理員身分的 PowerShell** | 開始選單對「Windows PowerShell」按右鍵 →「以系統管理員身分執行」。只有 J-24 要用 |
| **tag** | 程式碼某一版的名字，例如 `v0.3.0`。部署一律部署 tag，不部署分支 |
| **容器、映像檔** | 映像檔像安裝光碟，跑起來的那一份叫容器。本系統的容器一律由 `docker compose` 產生，**不准自己手動開** |
| **資料卷** | Docker 管理的儲存空間，資料庫就在 `hd-tablet-care-data` 裡，檔案總管看不到是正常的 |
| **`.env`** | 設定檔，放在 `C:\hd\hd-tablet-care\config\.env`。裡面有密碼與金鑰，**不拍照、不複製出去** |
| **來源、CORS** | 瀏覽器網址列上「`http://` ＋ 主機 ＋ 埠」那一段叫來源；後端只收 `.env` 的 `CORS_ORIGINS` 列出的來源，其他一律 `Failed to fetch` |
| **遷移** | 新版對資料庫結構的修改。只做加法，由 J-18 的更新指令一次套完 |

### 0.6 主機上長什麼樣

```
院內主機
│
├─ C:\hd\hd-tablet-care\        本系統的資料夾（$root）
│   ├─ repo\                    本系統的程式碼（git clone，切到某個 tag）
│   ├─ hd-kiosk-shell\          外殼 App 的程式碼
│   ├─ config\.env              設定（$cfg）
│   │   └─ ai-gateway\config.yaml   AI 閘道的設定（做過才有）
│   ├─ backups\                 資料庫備份；keys\ 底下是金鑰備份
│   └─ export\                  資料取出（新版才有，J-16 加）
│
├─ Docker 資料卷：hd-tablet-care-data（資料庫）、hd-tablet-care-keys（院內 CA、憑證、APK 簽章金鑰）
│
└─ 容器：api（後端，13000）、nurse-web（護理端，18080）、patient-web（病人端，18081）
          ai-gateway（AI 閘道，做過才有）；shell-builder 與 data-export 平時不跑
```

### 0.7 什麼時候當場停手

下列任一種出現，**停手、記錄、擇日**：

- 有人說「把網路開一下」「手動開個容器比較快」「把整顆磁碟掛進去」
- J-05 發現主機不是 1001 離開時的樣子（repo 的 tag 變了、資料卷不見了）
- J-08 護理站連不到 `<IP>`，資訊室當天處理不了
- `shell-builder` 印出「這一次新產生」裡有「院內 CA」或「APK 簽章金鑰」，或「這個金鑰資料卷是『dev』用的」
- 冒煙測試沒過，但已經到了下班時間

停手時做三件事（J-32）：**登入沒通就把服務停掉**、把現況寫進演練紀錄、當場講清楚下一次需要什麼。

---

## 1. 出發前（在開發端做完）

### J-01 確認要帶的 tag 已經照第十七冊演練過

**做什麼**：在開發機平常寫程式的工作目錄打：

```powershell
git ls-remote --tags origin
git rev-parse <新 tag>
git show <新 tag>:services/shell-builder/shell.pin
```

**怎麼知道成功了**

| 看什麼 | 應該是 |
|---|---|
| 第一條 | 清單裡看得到 `<新 tag>`，也看得到 `v0.3.0` |
| 第二條 | 與第十七冊演練時用的是同一個 commit |
| 第三條 | `SHELL_TAG=v0.3.0`（外殼不換版；換了的話第 7 節要多做外殼更新，先回開發端問） |
| 演練紀錄第 11 節 | **這個 tag** 的演練每一格都填了，最後的判定是「可以帶進院」 |

**可能怎麼壞**：`<新 tag>` 不在清單上 → 還沒推上 GitHub，`git push origin <新 tag>`。**沒演練過的 tag 不准帶進院**：1001 帶的 `v0.3.0` 就是出發前才打、沒演練過的（第十五冊之三 R6）。

---

### J-02 約人、把問題清單寄給資訊室（＝V-01、V-02）

**做什麼**：**至少一週前**，用訊息或郵件寄出下面兩張表，要文字答覆。

**約人**：

| 誰 | 為什麼 | 怎麼問 |
|---|---|---|
| 資訊室一位**能登入主機、有管理員權限**的同仁，全程在場 | 登入主機、核對 IP、加防毒排除、同意重新開機 | 「X 月 X 日 X 點到 Y 點，需要一位能登入那台主機、有管理員權限的同仁全程在旁。」**「到時候看看」當成沒約到，沒約到不出發** |
| 護理長或指定的護理師 | 在護理站的電腦試登入、收下新密碼、聽交接 | 至少 J-14 與第 8 節要在 |
| 給院方 API 位址的人（資訊室或護理長） | 第 6 節要當場輸入位址 | 問好是誰、當天在不在 |

**問資訊室的題目**（已經有答案的不必再問：三個埠 `13000`、`18080`、`18081`；對外連線常態沒有限制；IP 固定；斷電後護理長重新登入；Docker 使用統計可以關；市集自動更新先不改）：

| # | 題目 | 為什麼要問 |
|---|---|---|
| 1 | 院內主機固定的 IP 是哪一個？**護理站的電腦**與**平板要用的 Wi-Fi** 都連得到它嗎？ | 這個值就是 `<IP>`，之後不再換（J-08） |
| 2 | Docker 的資料夾能不能加入 Windows Defender 的排除清單？當天由誰加？ | 1001 查到排除清單是空的；加上之前不得輸入真實病人資料（J-24） |
| 3 | 當天可不可以重新開機一次？挑什麼時候？（主機上還有另一個專案的容器） | J-25 |
| 4 | 1001 Docker 三次查不到 Docker Hub 的網域（`production.cloudfront.docker.com`、`auth.docker.io`），院內 DNS 對這些網域穩不穩？ | J-15、J-17 要下載 |
| 5 | 本系統放在 `C:\hd\hd-tablet-care`，院方同意嗎？備份資料夾由誰、多久送往另一台機器一次？ | 交接要寫 |
| 6 | 1001 現場裝的 Git，要不要補走變更流程？ | 交接要寫 |
| 7 | 本系統讀院方透析紀錄 API，要不要報備、向誰報備？（Q-35）當天誰給位址？ | 第 6 節；正式啟用前要有答案 |
| 8 | 暫用平板（醫師給的 Galaxy Tab S6 Lite）能不能連院內 Wi-Fi？准不准從院內下載頁安裝 App？（Q-11 第 2 題） | 第 7 節；不准就不做 |

**怎麼知道成功了**：有具體的人名與時段；每一題都有答覆，或寫明「未答覆」與對方是誰。答覆抄進演練紀錄第 12 節。

---

### J-03 準備要帶的東西

| 帶什麼 | 為什麼 |
|---|---|
| **這一冊的紙本** | 現場用你自己的電腦未必能查 |
| **演練紀錄第 12 節的紙本**（空白表格） | 現場邊做邊填；值（`<IP>`、密碼）只寫在這張紙上 |
| 第十七冊演練時抄的耗時與錯誤原文 | 對照用 |
| 空白筆記本、兩支筆 | |
| 手機（充飽電） | 當碼表；**不拍 `.env` 與任何有病人資料的畫面** |
| 暫用平板＋充電器（要做第 7 節的話） | 出發前照[暫用平板紀錄](../notes/interim-tablet.md)第 4 節：**不要原廠重設**、USB 偵錯關掉、問醫師字型大小 1.1 要不要調回預設 |

**不帶**：隨身碟（院方不准）、開發機上的任何設定檔。

---

## 2. 到場：先看、先抄，不改任何東西

> ⚠️ 從這裡開始，指令都在**院內主機**的 PowerShell 裡打。**不要自己開任何容器，不要下 `docker run`。** 0922 就是這樣失敗的。

### J-04 開 PowerShell，輸入「開工三行」（＝V-09）

**做什麼**：開一個 PowerShell，輸入：

```powershell
$root = "C:\hd\hd-tablet-care"
$cfg  = "$root\config\.env"
cd $root\repo
```

前兩行設定兩個變數，之後每一條 `docker compose` 指令都寫成 `--env-file $cfg`，而且都在 `$root\repo` 底下打。

**怎麼知道成功了**：提示字元變成 `PS C:\hd\hd-tablet-care\repo>`。

> ⚠️ **PowerShell 關掉再開，這三行就要重打。** 看到 `couldn't find env file`，十次有九次是忘了這三行。

| 症狀 | 處置 |
|---|---|
| `cd` 說找不到路徑 | 根目錄被搬過或刪過。**停手**，問資訊室（0.7 節） |

---

### J-05 確認主機還是 1001 離開時的樣子（＝E-05、第十五冊 0.5 節）

**做什麼**（記下開始時間）

```powershell
git describe --tags
git status --short
docker ps -a --format "{{.Names}}  {{.Image}}  {{.Status}}"
docker volume ls --filter name=hd-tablet-care
Get-ChildItem $root\backups\keys
Get-ChildItem $root\backups -Filter *.db | Measure-Object
Get-PSDrive C
curl.exe -s http://localhost:13000/api/health
```

**怎麼知道成功了**

| 指令 | 1001 離開時 | 不一樣的話 |
|---|---|---|
| `git describe --tags` | `v0.3.0` | 有人動過 repo。**停手**，先問資訊室 |
| `git status --short` | 什麼都沒印 | 有人改過 repo 裡的檔案。把印出來的抄下來，**停手**先問 |
| `docker ps -a` | `hd-tablet-care-api-1`、`hd-tablet-care-nurse-web-1`、`hd-tablet-care-patient-web-1` 三列，映像檔 `hd-tablet-care:v0.3.0`，狀態 `Up …` | 狀態是 `Exited` → 主機中間重新開機過、服務沒有自己回來：**這就是 J-25 要的答案**，記下來，再 `docker compose --env-file $cfg up -d` |
| 同上 | 可能還有 `hd-tablet-care-ai-gateway-1`（1001 有沒有做 AI 閘道沒記到） | 有或沒有都對，**記下來**，J-20 要用 |
| 同上 | 不該有 `dialysis_system_v0` | 有的話做 J-06 |
| 同上 | 其他名字的容器 | 那是同機另一個專案的，**抄下名字，不要動** |
| `docker volume ls` | `hd-tablet-care-data`、`hd-tablet-care-keys` 兩個 | 不見了就不是 1001 的狀態，**停手** |
| `backups\keys` | 有 `hd-keys-20261001-173347.tar.gz` | 不見了，問資訊室是不是已經送往另一台機器 |
| `*.db` 的數量 | 每天 03:00 一份，1001 起約四週份 | 0 份 → 排程備份沒在跑，記下來（主機每天晚上可能都關機） |
| `Get-PSDrive C` 的 `Free` | 至少幾 GB | 不到 5 GB 就先問資訊室，J-17 建置與 J-18 的備份都要空間 |
| health | `{"status":"ok",…}` 開頭 | 看 `docker compose --env-file $cfg logs api --tail 30` 的最後幾行，抄下來 |

**可能怎麼壞**

| 症狀 | 處置 |
|---|---|
| `failed to connect to the docker API at npipe:…` | Docker Desktop 沒在跑。開始選單開啟它，等左下角變綠再重打；這也代表重新開機後它沒有自己起來，記下來給 J-25 |
| health 什麼都沒印 | 服務沒在跑。先看 `docker ps -a` 那一欄的狀態 |

---

### J-06 0922 的容器還在的話（＝L-01、L-07）

**只有 J-05 看到 `dialysis_system_v0` 才做。** 那是 0922 第一次進院手動開的容器，掛著整顆 C 槽，**沒收掉不往下做**。

**做什麼**：照[第十四冊之三](14c-cleanup-first-visit.md) L-02 起一步步收掉（那一冊要另外印；J-05 沒看到它就不用印）。收完打：

```powershell
docker ps -a --format "{{.Names}}  {{.Image}}  {{.Status}}"
```

**怎麼知道成功了**：清單裡沒有 `dialysis_system_v0`。演練紀錄寫「0922 的容器：已收（J-06）」或「J-05 時已不在」。

---

### J-07 先抄五樣（＝E-06、T-02）

**這一步最容易被跳過，也最不能跳過。** 等一下換成 IP 之後，這幾樣就再也看不到了，而它們是判斷「1001 為什麼登不進去」的唯一線索（第十五冊之三 3.2 節的可能 A 還是 B）。

**做什麼**（一條一條打，每一條的結果**原文**抄進演練紀錄第 12 節，包括正常的）

```powershell
Select-String -Path $cfg -Pattern '^(HD_PUBLIC_API_URL|CORS_ORIGINS|MDM_KIOSK_BASE_URL)='
docker compose --env-file $cfg logs api | Select-String '允許的前端來源' | Select-Object -Last 1
docker compose --env-file $cfg exec nurse-web grep -rhoE 'https?://[A-Za-z0-9.-]+:[0-9]+' apps/nurse-pwa/dist/assets
docker compose --env-file $cfg --profile shell run --rm shell-builder keys-info
Test-Path $root\config\ai-gateway\config.yaml
```

| # | 在抄什麼 |
|---|---|
| 1 | `.env` 裡的三個位址（名單寫了什麼） |
| 2 | 執行中的後端**手上那份**放行名單 |
| 3 | 護理端網頁裡寫死的後端位址 |
| 4 | 院內 CA、伺服器憑證、簽章金鑰的指紋；「伺服器憑證」那一行應該是 `DNS:<名稱>` |
| 5 | AI 閘道的設定檔在不在（`True`／`False`），J-20 要用 |

**怎麼知道成功了**：五樣都抄了。**值本身只寫演練紀錄的紙本**。

**怎麼看 1、2 兩條**（看懂就寫，看不懂照抄就好，回去再判斷）：

| 兩條比起來 | 1001 是哪一種 |
|---|---|
| 一樣，但都不是 `http://<名稱>:18080`（例如照抄了範例的 `hd-server`、寫了 `localhost`） | 可能 A：名單寫錯 |
| 第 1 條是 `http://<名稱>:18080`，第 2 條是別的值 | 可能 B：改完 `.env` 沒有 `up -d` |
| 兩條都是 `http://<名稱>:18080` | 名單沒問題，問題在網址列或網頁裡的位址（第 3 條） |

| 症狀 | 處置 |
|---|---|
| 第 2 條什麼都沒印 | 日誌被清過（例如容器重建過）。寫「沒有」就好 |
| 第 4 條「伺服器憑證」已經是 `IP Address:…` | 1001 填的其實是 IP。**停手**，第 3 節的換法要重新判斷，先打電話問開發端 |
| 第 4 條等很久、開始下載東西 | 映像檔 `hd-tablet-care-shell-builder:v0.3.0` 不見了，正在重建。等它跑完（約 30 分鐘），記下來 |

---

### J-08 確認 `<IP>`，並先從護理站連一次（＝T-03、T-04）

**做什麼**

1. 在主機上看 IP：

   ```powershell
   ipconfig /all
   ```

   找實體網卡（「乙太網路」或「Wi-Fi」）那一段，**不是** `vEthernet (WSL)`、`vEthernet (Default Switch)`，也不是 `172.` 開頭的：

   | 看什麼 | 應該是 |
   |---|---|
   | IPv4 位址 | 與資訊室給的 `<IP>` **一字不差** |
   | DHCP 已啟用 | `否`；或 `是`，但資訊室說已經在 DHCP 保留了這個 IP |

2. 到**護理站的電腦**，瀏覽器開 `http://<IP>:13000/api/health`。
3. 同一台電腦開 `http://<IP>:18080`，**看得到登入頁就好，先不要按登入**（還沒改名單，一定是 `Failed to fetch`）。
4. 有手機的話，連上**平板實際要用的那個 Wi-Fi**，瀏覽器開 `http://<IP>:18081/shell/`。

**怎麼知道成功了**：第 1 步 IP 一致；第 2 步看到 `{"status":"ok",…}`；第 3 步看到登入頁；第 4 步看到外殼下載頁（上面寫的主機位址還是 `<名稱>`，**現在是對的**，J-12 之後才會換）。

**可能怎麼壞**

| 症狀 | 處置 |
|---|---|
| 主機上的 IP 與資訊室給的不一樣 | **停手**，問清楚再做 |
| 護理站開不到 | 防火牆或網段。**找資訊室，不要自己關防火牆，也不要往下改設定**——換成 IP 也不會通 |
| 護理站開得到，手機（平板的 Wi-Fi）開不到 | 平板的網段到不了主機。第 3 節照做，第 7 節先不做，交資訊室 |

> **這一步是換位址之前的保險。** 連得到才改；連不到時改什麼都沒用。

---

## 3. 換成 IP，讓護理站登得進去（仍在 `v0.3.0`）

為什麼先在舊版修登入、不一起換新版：**兩件事分開做，出錯時才分得出是哪一件**；而且新版萬一出問題，退回來的是一個已經登得進去的 `v0.3.0`（附錄二）。

改主機位址會牽動這幾處，下面五步一處都不能漏：

| 主機位址寫在哪 | 怎麼換 | 在哪一步 |
|---|---|---|
| `.env` 的三個位址 | 記事本改 | J-10 |
| 護理端網頁裡的後端位址 | `build` 時寫死進去，要重建 | J-11 |
| 後端的放行名單、平板 QR code 裡的位址 | 容器建立時讀一次，要 `up -d` | J-11 |
| 伺服器憑證、下載頁 | 重跑 `shell-builder` 會自己重簽 | J-12 |
| 金鑰備份、病人端用的憑證 | `keys-backup`、`restart patient-web` | J-12 |

### J-09 留一份改之前的 `.env`（＝T-05）

**做什麼**

```powershell
Copy-Item $cfg "$root\config\.env.before-ip"
Get-ChildItem "$root\config"
```

**怎麼知道成功了**：看得到 `.env` 與 `.env.before-ip` 兩個檔。

> ⚠️ 這一份和 `.env` 一樣有密碼與金鑰，**只留在這個資料夾**，J-14 成功後就刪掉（J-14 最後一步）。

---

### J-10 把三個位址改成 `<IP>`（＝T-06）

**做什麼**

```powershell
notepad $cfg
```

只改這三行的**主機部分**，`http://`、`https://` 與埠都不動：

```
HD_PUBLIC_API_URL=http://<IP>:13000
CORS_ORIGINS=http://<IP>:18080
MDM_KIOSK_BASE_URL=https://<IP>:18081
```

`CORS_ORIGINS` 如果用逗號多列了別的來源（例如 `localhost`），**這次一起拿掉**，只留 `http://<IP>:18080`。存檔，關掉記事本。

**怎麼知道成功了**

```powershell
docker compose --env-file $cfg config --quiet
Select-String -Path $cfg -Pattern '^(HD_PUBLIC_API_URL|CORS_ORIGINS|MDM_KIOSK_BASE_URL)='
Select-String -Path $cfg -Pattern '^[^#].*(<|>|hd-server|localhost)'
```

| 哪一條 | 應該是 |
|---|---|
| 第一條 | 什麼都沒印 |
| 第二條 | 三行，主機部分**都是 `<IP>`、一字不差**；前兩行 `http://`、第三行 `https://` |
| 第三條 | 什麼都沒印（沒有照抄範例、沒有 `localhost`、沒有忘了換掉的 `<`、`>`） |

再打一條，`<名稱>` 換成舊的那個名稱，**什麼都沒印**才對（舊名稱一處都不剩）：

```powershell
Select-String -Path $cfg -Pattern '^[^#].*<名稱>'
```

| 症狀 | 處置 |
|---|---|
| 第二條有一行還是舊名稱 | 回記事本改成一字不差 |
| 記事本存檔時問編碼 | 選 UTF-8，不要改檔名 |

---

### J-11 重建網頁、啟動，並在主機上確認放行（＝T-07、V-17 第一、二段）

`HD_PUBLIC_API_URL` 寫死在網頁檔案裡，**只 `up -d` 沒有用，一定要先 `build`**。

**做什麼**（記下開始時間）

```powershell
docker compose --env-file $cfg build
docker compose --env-file $cfg up -d
docker compose --env-file $cfg ps
```

**怎麼知道成功了**：`build` 最後出現 `Image hd-tablet-care:v0.3.0 Built`；`ps` 的 `api`、`nurse-web`、`patient-web` 都是 `Up`。記下結束時間。

接著在主機上打這四條確認：

```powershell
curl.exe -s http://localhost:13000/api/health
docker compose --env-file $cfg exec nurse-web grep -rhoE 'https?://[A-Za-z0-9.-]+:[0-9]+' apps/nurse-pwa/dist/assets
curl.exe -s -i -H "Origin: http://<IP>:18080" http://<IP>:13000/api/health | Select-String Access-Control-Allow-Origin
docker compose --env-file $cfg logs api | Select-String '允許的前端來源' | Select-Object -Last 1
```

| 哪一條 | 應該是 |
|---|---|
| health | `{"status":"ok",…}` |
| 網頁裡的後端位址 | `http://<IP>:13000`，**沒有舊名稱** |
| 放行檢查 | 印出 `Access-Control-Allow-Origin: http://<IP>:18080` |
| 日誌最後一行 | `允許的前端來源：http://<IP>:18080` |

> 💡 放行檢查那一行在視窗太窄時可能只看得到後半段（例如 `…rol-Allow-Origin: http://…`），看得到 `Allow-Origin` 就算有印。**真的什麼都沒印才是沒放行**——1001 就是空的。

**可能怎麼壞**

| 症狀 | 處置 |
|---|---|
| `failed to resolve source metadata for docker.io/library/node`，後面有 `no such host` | Docker 查不到 Docker Hub 的網域。依序：① 同一條再打一次；② 工作列的 Docker 圖示按右鍵 → Restart，等變綠再打；③ 仍不行，請資訊室看院內 DNS。**用了哪一個辦法才過，寫進紀錄** |
| `npm error code ETIMEDOUT` 或 `ECONNRESET` | 網路不穩，再打一次；已下載的部分會沿用 |
| 網頁裡的後端位址還是舊名稱 | `build` 沒讀到新的 `.env`：多半是少了 `--env-file $cfg` 或忘了開工三行。補上再 `build`、`up -d` |
| 放行檢查什麼都沒印 | `CORS_ORIGINS` 不是 `http://<IP>:18080`，或改完沒 `up -d`。看日誌最後一行就知道後端手上是哪一份 |
| `api` 一直是 `Restarting` | `docker compose --env-file $cfg logs api --tail 30`，最後幾行寫是哪一條設定被拒，照著改 `.env` 再 `up -d` |

---

### J-12 重簽伺服器憑證、備份金鑰、病人端換上新憑證（＝T-08、T-09、T-10）

**做什麼**（記下開始時間）

```powershell
docker compose --env-file $cfg --profile shell run --rm shell-builder
```

它會重建一次 APK（不必下載）。看「**這一次新產生：**」那一行：

| 後面出現 | 怎麼辦 |
|---|---|
| **只有**「伺服器憑證（`<IP>`）」 | **對的**，往下 |
| 「伺服器憑證（`<名稱>`）」 | `.env` 的 `MDM_KIOSK_BASE_URL` 沒改到，回 J-10 |
| 有「院內 CA」或「APK 簽章金鑰」 | **停手。** 不要往下做（0.7 節），打電話問開發端 |
| `這個金鑰資料卷是「dev」用的，設定卻是「hospital」` | **停手** |

**再打一次同一條指令**，這次要看到「**金鑰全部沿用，這一次沒有產生任何新的金鑰**」。

然後備份金鑰、讓病人端換上新憑證：

```powershell
docker compose --env-file $cfg --profile shell run --rm shell-builder keys-backup
docker compose --env-file $cfg --profile shell run --rm shell-builder keys-verify
docker compose --env-file $cfg restart patient-web
docker compose --env-file $cfg logs patient-web --tail 5
docker compose --env-file $cfg --profile shell run --rm shell-builder keys-info
```

**怎麼知道成功了**

| 看什麼 | 應該是 |
|---|---|
| `keys-backup` | 「已備份：備份目錄/keys/hd-keys-<時間>.tar.gz」，**檔名抄下來** |
| `keys-verify` | 每一項都 ✓，最後「還原得回來」 |
| `patient-web` 日誌**最後一次**出現的「靜態資源已提供於連接埠 8081」 | 後面是「（HTTPS；HTTP 只留外殼下載頁）」 |
| `keys-info` 的「伺服器憑證」 | `IP Address:<IP>` |
| `keys-info` 的院內 CA 與簽章金鑰指紋 | 與 J-07 第 4 條抄的**一模一樣** |

記下結束時間（1001 沒有計時，這一步的耗時下一次要用）。

> ⚠️ 金鑰備份裡有私鑰：**不得出院、不得寄給開發端**。1001 那份 `hd-keys-20261001-173347.tar.gz` **不要刪**。

| 症狀 | 處置 |
|---|---|
| 日誌裡「找不到伺服器憑證」和「HTTPS」同時出現 | `--tail 5` 跨到了重新啟動之前那一次。以**最後一次**啟動的那幾行為準 |
| **最後一次**啟動是「找不到伺服器憑證…暫以 HTTP 提供」 | `shell-builder` 沒成功，或沒 `restart patient-web` |
| 日誌寫 `8081`、`http://api:3000`，不是 `18081`、`13000` | **正常**，那是容器裡面的埠 |
| 院內 CA 或簽章金鑰指紋與 J-07 不一樣 | **停手**，有新的金鑰產生了 |

---

### J-13 在主機上登入、改密碼（＝T-11、V-17 第三段）

**做什麼**：主機的瀏覽器開 **`http://<IP>:18080`**——**不要用 `localhost`，也不要用舊名稱**。帳號密碼用 `.env` 裡的 `SUPER_ADMIN_WORK_ID` 與 `SUPER_ADMIN_INITIAL_PASSWORD`：

```powershell
Select-String -Path $cfg -Pattern '^SUPER_ADMIN_(WORK_ID|INITIAL_PASSWORD)='
```

**怎麼知道成功了**：被要求改密碼。新密碼由**護理長**決定、自己保管，你不要記在任何地方。

| 症狀 | 處置 |
|---|---|
| `Failed to fetch` | 網址列是不是 `http://<IP>:18080`（一字不差）？是的話按 Ctrl＋F5 再試；仍不行照**附錄三** |
| `工作ID 或密碼錯誤` | 有連到後端了（名單已修好）。帳號只在**第一次啟動**時照 `.env` 建立，1001 之後若有人改過 `.env` 的這兩行，不會改到已建立的帳號。把 J-07 時 `.env` 的這兩行與現在的比一下；都不對就**停手**，回去由開發端出重設的辦法，不在現場改資料庫 |
| 頁面開得到，但一直轉圈 | 按 F12 → Network，再按一次登入，抄下請求送去的網址與錯誤原文 |

---

### J-14 在護理站的電腦登入（＝T-12、V-17 第四段）

**這一步過了，這一次進院就至少是 B 級。**

**做什麼**：**護理站的電腦**開 `http://<IP>:18080`，用護理長剛改好的密碼登入（請護理長自己輸入）。

**怎麼知道成功了**：登入成功，看得到護理端的畫面。**記下時間**，演練紀錄寫「護理站登入成功，＿點＿分」。

做完之後：

1. 護理站瀏覽器裡用舊名稱的書籤、桌面捷徑，**全部改成 `http://<IP>:18080`**，並告訴護理站的人：舊網址開得到頁面，但登不進去。
2. 刪掉改之前的那一份 `.env`：

   ```powershell
   Remove-Item "$root\config\.env.before-ip"
   Get-ChildItem "$root\config"
   ```

3. 照 0.3 節的取捨表決定要不要做第 4 節。

| 症狀 | 處置 |
|---|---|
| 主機上登得進去，護理站開不到頁面 | J-08 應該已經擋下來；找資訊室 |
| 護理站 `Failed to fetch` | Ctrl＋F5 強制重新整理（舊網頁可能還留在瀏覽器裡），再試；仍不行照附錄三 |
| 試了一小時仍然不通 | **停手**，照附錄三最後一段換回名稱或保留現況，做 J-32 |

---

## 4. 換到新版

這一段是第十一冊 W-19 的「更新」，套在院內主機上。從 `v0.3.0` 到 `<新 tag>`：**19 個資料庫遷移，全部只做加法**；`.env` **多一個必填的 `HD_EXPORT_DIR`**，另有兩個院方 API 的變數（院內一律空白）；外殼不換版、**APK 不必重建**、平板不必重裝。

> ⚠️ **排在沒有透析的時段做。** 更新後第一個班次要有人盯著（DEP-32）：新版的問題要在累積新資料之前發現，退回的代價才是零。

### J-15 下載新版的程式碼，先把基底映像下載好（＝W-19 第一段、V-06 第二段）

**做什麼**

```powershell
git fetch --tags
git checkout <新 tag>
git describe --tags
docker pull node:20-bookworm-slim
```

**怎麼知道成功了**

| 看什麼 | 應該是 |
|---|---|
| `git checkout` | 一大段 `You are in 'detached HEAD' state…`，**正常** |
| `git describe --tags` | **正好是** `<新 tag>`，後面沒有 `-3-g1a2b3c4` 這種尾巴 |
| `docker pull` | 最後是 `Status: Downloaded newer image for …` 或 `Status: Image is up to date for …` |

> ⚠️ **從這一刻起到 J-16 改完 `.env` 之前，每一條 `docker compose` 指令都會停在「請設定 HD_EXPORT_DIR」。** 這是對的，J-16 補上就好。

| 症狀 | 處置 |
|---|---|
| `git fetch` 說 `Permission denied (publickey)` | 部署金鑰被拿掉了。`ssh -T github-hd-tablet-care` 看一下，印出 `Hi 94sh09sh19sh/hd-tablet-care!…` 才對；不是的話打電話給開發端（repo 管理者）重新登記 |
| `Connection reset by … port 22` | 網路切斷連線，再打一次 |
| `error: pathspec '<新 tag>' did not match` | tag 沒推上去，或打錯字。回 J-01 |
| `git checkout` 說 `Your local changes … would be overwritten` | 有人改過 repo 裡的檔案（J-05 應該已經看到）。**停手**，不要加 `--force` |
| `docker pull` 出現 `no such host` | 同 J-11 那一列：再打一次 → Restart Docker → 找資訊室 |

---

### J-16 補 `.env`（＝第十五冊之一第 6 節、1.1、1.2、1.10）

**做什麼**

```powershell
notepad $cfg
```

改三處：

1. `HD_IMAGE_TAG=v0.3.0` 改成 `HD_IMAGE_TAG=<新 tag>`。
2. 在 `HD_CONFIG_DIR=` 那一行**下面**加一行：

   ```
   HD_EXPORT_DIR=C:\hd\hd-tablet-care\export
   ```

   資料夾不必先建。它是研究資料取出的位置，**與備份資料夾分開**（[第十六冊](16-data-export.md)）。
3. 在檔案最後加兩行，**等號後面都留空白**：

   ```
   HOSPITAL_API_BASE_URL=
   HD_SIMULATION_DEPLOYMENT=
   ```

   這兩行不加也能跑（空白就是預設），加了是讓這份 `.env` 與新版範本長得一樣，日後有人看得懂。**院方 API 的位址這一次不寫進來**，第 6 節當場輸入。

存檔，關掉記事本。

**怎麼知道成功了**

```powershell
docker compose --env-file $cfg config --quiet
git describe --tags
Select-String -Path $cfg -Pattern '^(HD_IMAGE_TAG|HD_EXPORT_DIR|HD_SHELL_SIGNING|LLM_PROVIDER|HOSPITAL_API_BASE_URL|HD_SIMULATION_DEPLOYMENT)='
Select-String -Path $cfg -Pattern '^[^#].*(<|>|hd-server|localhost)'
```

| 哪一條 | 應該是 |
|---|---|
| `config --quiet` | 什麼都沒印 |
| `HD_IMAGE_TAG` | 與 `git describe --tags` 一字不差 |
| `HD_EXPORT_DIR` | `C:\hd\hd-tablet-care\export` |
| `HD_SHELL_SIGNING` | `hospital` |
| `LLM_PROVIDER` | `mock` |
| `HOSPITAL_API_BASE_URL`、`HD_SIMULATION_DEPLOYMENT` | 等號後面空白 |
| 最後一條 | 什麼都沒印 |

| 症狀 | 處置 |
|---|---|
| `required variable HD_… is missing a value: 請設定 …` | 冒號後面寫的就是還缺什麼，補上 |
| `HD_SHELL_SIGNING` 不是 `hospital` | **停手**，不要改它 |
| `HD_SIMULATION_DEPLOYMENT` 有值 | 清空。院內主機這一格永遠空白 |
| 有 `HIGH_RISK_WRITTEN_CONFIRMATION` 或 `SHOWCASE_MODE` 這一行 | 刪掉（新版不讀，留著只會讓人看不懂） |

---

### J-17 建置新版的映像檔（＝W-19、V-14）

**做什麼**（記下開始時間）

```powershell
docker compose --env-file $cfg build
```

約十分鐘，畫面一直捲動是正常的。

**怎麼知道成功了**：最後出現 `Image hd-tablet-care:<新 tag> Built`。再打：

```powershell
docker images hd-tablet-care
```

看得到 `v0.3.0` 與 `<新 tag>` **兩個**。記下結束時間。

> ⚠️ **`v0.3.0` 的映像檔不要刪。** 新版穩定之前，那是唯一退得回去的東西（附錄二）。

| 症狀 | 處置 |
|---|---|
| `no such host` | 同 J-11 那一列 |
| `ETIMEDOUT`、`ECONNRESET` | 再打一次 |
| `pull access denied for hd-tablet-care` | 打成 `up` 了，先 `build` |

到這裡為止，**服務還是 `v0.3.0` 在跑**，護理站照樣用得了。

---

### J-18 停後端、更新資料庫（＝W-19）

**做什麼**（兩行，第二行是一整行，不要斷開）

```powershell
docker compose --env-file $cfg stop api
docker compose --env-file $cfg run --rm --no-deps api node apps/api/scripts/db-update.mjs --note "v0.3.0 → <新 tag>（第三次進院）"
```

這一條一次做完五件事，每一件印一段 `[1]`～`[5]`：確認後端已停、開更新紀錄、**更新前備份**、**驗證備份還原得起來**、套用遷移。任何一關沒過就停，資料庫不會被動到。

**怎麼知道成功了**：最後印出「**更新完成。接下來的三件事是人要做的**」。往上找第 3 段，**把更新前備份的檔名（`hd-before-update-<時間>.db`）與 SHA-256 抄下來**——附錄二退回時要用。

| 症狀 | 處置 |
|---|---|
| `更新中止：後端服務還在執行` | 第一行沒成功，再打一次 `stop api`。**不要加 `--allow-running`**，那是演練用的 |
| `更新中止：備份目的地可用空間 …不足` | 主機共用，問資訊室是誰佔掉空間；不要自己刪別人的東西 |
| 其他任何「中止」 | 資料庫沒被動到。整段抄下來，`docker compose --env-file $cfg up -d` 讓舊版的後端回來（`.env` 先把 `HD_IMAGE_TAG` 改回 `v0.3.0`、`git checkout v0.3.0`），打電話給開發端 |

> 護理站在這一步的期間會看到斷線紅框，`up -d` 之後就會消失。先跟護理站講一聲。

---

### J-19 啟動新版，確認還是登得進去（＝W-19、V-17）

**做什麼**

```powershell
docker compose --env-file $cfg up -d
docker ps --format "{{.Names}}  {{.Image}}  {{.Status}}"
curl.exe -s http://localhost:13000/api/health
docker compose --env-file $cfg exec nurse-web grep -rhoE 'https?://[A-Za-z0-9.-]+:[0-9]+' apps/nurse-pwa/dist/assets
curl.exe -s -i -H "Origin: http://<IP>:18080" http://<IP>:13000/api/health | Select-String Access-Control-Allow-Origin
docker compose --env-file $cfg logs api --tail 40
```

**怎麼知道成功了**

| 看什麼 | 應該是 |
|---|---|
| `docker ps` | `api`、`nurse-web`、`patient-web` 三列的映像檔是 `hd-tablet-care:<新 tag>`，狀態 `Up` |
| health | `{"status":"ok",…}` |
| 網頁裡的後端位址 | `http://<IP>:13000` |
| 放行檢查 | `Access-Control-Allow-Origin: http://<IP>:18080` |
| 日誌 | 有「已連線至 SQLite」（帶 `synchronous=FULL`）、「伺服器時區」是 `Asia/Taipei`、版本標記後面寫「（正式環境設定）」；沒有紅色的 `ERROR` |

然後**在護理站的電腦**：

1. 按 Ctrl＋F5 強制重新整理（舊版的網頁還留在瀏覽器裡）。
2. 用護理長的新密碼再登入一次。
3. 護理端 → **系統管理** → 「**版本更新紀錄**」：多了一筆，說明是 `v0.3.0 → <新 tag>（第三次進院）`。

新版第一次啟動時會**自己**補進一些東西：隨版本帶入的衛教草稿（待核准，病人端看不到）、四條判斷規則的草稿、記憶相簿的預設圖卡、指標定義的變更紀錄。**都不必處理**。

> ⚠️ **新版多了很多功能開關**（遊戲化、獎勵制度、跑馬燈等），**照預設關著，一個都不要開**。要開得先讓長者、社工、護理部看過（1014、1018 的決定）。

| 症狀 | 處置 |
|---|---|
| `api` 一直 `Restarting` | `docker compose --env-file $cfg logs api --tail 30` 抄最後幾行。看不懂就照附錄二退回 `v0.3.0` |
| 護理站 `Failed to fetch` | Ctrl＋F5；仍不行照附錄三 |
| 登入後畫面壞掉、某個頁面打不開 | 抄下畫面上的字與網址。主線（登入、簡易版、系統管理）能用就繼續，不能用就照附錄二退回 |

---

### J-20 AI 閘道換成新版（＝V-29、V-30）

首波 AI 是關的。這一步只讓閘道就位、確認它清楚回報「設定還沒填」，**不接任何模型**。

**做什麼**

1. 設定檔：J-07 第 5 條是 `False`（沒有設定檔）才打這兩行；是 `True` 就跳過，**不要蓋掉它**：

   ```powershell
   New-Item -ItemType Directory -Force $root\config\ai-gateway | Out-Null
   Copy-Item services\ai-gateway\config.hospital.example.yaml $root\config\ai-gateway\config.yaml
   ```

   範本的 `base_url` 與 `model` 刻意留空，**保持空白**。**絕對不要填實驗室的位址**——那是把資料往院外送。
2. 建置並啟動：

   ```powershell
   docker compose --env-file $cfg --profile ai build ai-gateway
   docker compose --env-file $cfg --profile ai up -d ai-gateway
   docker compose --env-file $cfg exec -T api node -e "fetch('http://ai-gateway:8000/health').then(async r=>console.log(r.status, await r.text()))"
   ```

**怎麼知道成功了**：建置最後印出 `全部通過`；最後一條印出

```
503 {"status":"error","config":"error","detail":"base_url 尚未填寫（推論端點的位址）"}
```

**503 在這裡是對的**：閘道在、後端連得到它、它清楚說出還缺什麼。

| 症狀 | 處置 |
|---|---|
| `fetch failed` | 閘道沒起來，`docker compose --env-file $cfg --profile ai logs ai-gateway` |
| `找不到設定檔` | 第 1 步的路徑不對，必須是 `config\ai-gateway\config.yaml` |
| 建置時 `no such host` | 同 J-11 那一列 |

> ⚠️ 從現在起，**日後更新時 `build` 與 `up -d` 都要加 `--profile ai`**，閘道才會跟著換新版。

---

### J-21 確認資料取出的指令在（只印說明，不取任何資料）

研究與後續計畫的資料取出是新版才有的（[第十六冊](16-data-export.md)），**沒有院方核准不得執行**。這一步只確認它在，交接時說得出來。

**做什麼**

```powershell
docker compose --env-file $cfg --profile export run --rm data-export --help
```

**怎麼知道成功了**：印出一大段說明，第一行是「研究與後續計畫的資料取出（部署手冊第十六冊「取出資料」）」。**只打 `--help`，不要加任何別的參數。**

| 症狀 | 處置 |
|---|---|
| `請設定 HD_EXPORT_DIR` | J-16 的第 2 處沒加，回去補 |
| 說匯出目錄與備份目錄重疊 | `HD_EXPORT_DIR` 寫成了 `backups` 底下，改成 `C:\hd\hd-tablet-care\export` |

---

## 5. 備份、防毒、重新開機

### J-22 備份一次，並證明還原得回來（＝V-18）

「有備份」和「備份能用」是兩件事。

**做什麼**

1. 護理端 → **系統管理** → 「**立即備份**」，記下畫面上的檔名（`hd-backup-<時間>.db`）。
2. 讀完整的 SHA-256（畫面上只顯示前 12 碼）：

   ```powershell
   Get-Content "$root\backups\<檔名>.sha256"
   ```

   前半段那 64 個字就是雜湊。
3. 還原到一個測試檔、確認完整，再刪掉測試檔（`<檔名>`、`<雜湊>` 換成剛剛的；第一條是一整行）：

   ```powershell
   docker compose --env-file $cfg run --rm --no-deps api node_modules/.bin/ts-node --project apps/api/tsconfig.json apps/api/scripts/restore-backup.ts --from /backups/<檔名> --to /data/restore-check.db --sha256 <雜湊>
   docker compose --env-file $cfg run --rm --no-deps --entrypoint rm api /data/restore-check.db
   ```

4. **當場問資訊室**：備份資料夾（連同 `keys\`）由誰、多久送往院內另一台機器一次？答不出來就寫進交接的「已知限制」。

**怎麼知道成功了**：第 3 步的輸出有 `✓ 與備份歷程上的紀錄相符` 與 `完整性檢查：ok`；`$root\backups\` 裡看得到那個檔和同名的 `.sha256`。

> ⚠️ 這一步**一律用 PowerShell**。在 Git Bash 裡打，`/backups/…` 會被改寫成 Windows 路徑，還原腳本就找不到檔案。

| 症狀 | 處置 |
|---|---|
| 「找不到備份檔」 | 檔名打錯，或用了 Git Bash |
| 雜湊不符 | 雜湊抄錯；用 `Get-Content` 那一條重新複製 |

---

### J-23 Docker Desktop 的四項設定，關掉使用統計（＝V-05 第一部分）

**做什麼**：開 Docker Desktop → 右上角齒輪（Settings），逐項看，抄進紀錄：

| # | 位置 | 應該是 | 這一次 |
|---|---|---|---|
| 1 | General → Start Docker Desktop when you sign in | 勾 | 沒勾的話**先不改**，記下來，J-25 會看出影響，交資訊室決定 |
| 2 | General → Send usage statistics | 不勾 | **1007 答覆可以關：取消勾選** |
| 3 | Software updates → Automatically check for updates | — | **只看不改**（1007 答覆先不改）。找不到勾選框就是從 Microsoft Store 裝的，寫「更新由市集管理」 |
| 4 | Resources → Advanced → Disk image location | — | **路徑抄下來**，J-24 要用 |

第 2 項取消勾選後，按右下角的 **Apply**（有的版本叫 **Apply & restart**：Docker 會重新啟動，三個服務中斷約一分鐘後自己回來，護理站會閃一下紅框）。

**怎麼知道成功了**：四項都抄了；演練紀錄寫「使用統計已關，＿月＿日」。如果按的是 Apply & restart，等一分鐘後打 `docker ps --format "{{.Names}}  {{.Status}}"`，三個服務都回到 `Up`。

| 症狀 | 處置 |
|---|---|
| 設定是灰的 | 院方鎖住了。記下來，不要想辦法繞過 |
| Apply & restart 之後服務沒回來 | `docker compose --env-file $cfg up -d`，並記下來 |

---

### J-24 防毒：查清楚，交給資訊室加排除（＝V-05 第二部分、E-11）

1001 查到 Windows Defender 正在運作、**排除清單是空的**：資料庫所在的 Docker 資料夾正被即時掃描，會造成不定時、很難重現的錯誤。**加上排除之前，這台主機不得輸入真實病人資料。**

**做什麼**：開一個**系統管理員身分**的 PowerShell（0.5 節），打：

```powershell
Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntivirusProduct | Select-Object displayName, @{n='hex';e={'{0:X6}' -f $_.productState}}
Get-MpPreference | Select-Object -ExpandProperty ExclusionPath
```

| 看什麼 | 怎麼判斷 |
|---|---|
| 第一條每一行的 `hex` **中間兩碼** | `10` 或 `11` 是**正在運作**；`00`、`01` 是裝了沒在跑。1001 是 `061100`（Defender 正在運作） |
| 第二條 | 每一行是一個排除的路徑；**什麼都沒印**就是沒有任何排除 |

清單裡**沒有** J-23 第 4 項那個路徑（或它的上層資料夾）的話，請資訊室把它加進排除清單。加完再打一次第二條，看得到它才算。

**怎麼知道成功了**：演練紀錄寫「防毒＝＿＿；排除清單已加，由＿＿加」，或「未加，由＿＿於＿＿前加」。

| 症狀 | 處置 |
|---|---|
| 第二條說 `Must be an administrator to view exclusions` | 不是系統管理員身分，照 0.5 節重開一個 |
| 第一條說 `Invalid namespace` | 這台是 Windows Server，改打 `Get-MpComputerStatus`，看 `AMRunningMode`、`AntivirusEnabled` |
| 資訊室當天加不了 | **不是停手的理由**（這一次不輸入真實資料），但要寫進交接的「已知限制」，並寫明誰、什麼時候加 |

---

### J-25 重新開機測試（＝V-19、W-18）

**這一條決定這條路線在院內能不能用。** `restart: unless-stopped` 只管 Docker 起來之後；Docker Desktop 要有人登入 Windows 才會啟動。1007 的答覆是：斷電後**護理長**到主機重新登入，不設自動登入。這一步就是在模擬護理長。

> ⚠️ 主機上還有另一個專案的容器，重新開機會一起中斷它。**資訊室同意了、挑好時段才做**（J-02 第 3 題）。

**做什麼**

1. 先請護理站把護理端開著，**看著它**。
2. 主機重新開機 → 以平常的帳號（Administrator）登入 → **之後什麼都不碰**，連 Docker Desktop 都不要點，等三分鐘。
3. 開一個新的 PowerShell，輸入開工三行（J-04），再打：

   ```powershell
   docker ps --format "{{.Names}}  {{.Image}}  {{.Status}}"
   curl.exe -s http://localhost:13000/api/health
   ```

**怎麼知道成功了**

| 看什麼 | 應該是 |
|---|---|
| 主機關機那段時間，護理站 | 每一個畫面閃紅框（斷線警示） |
| 三分鐘後 `docker ps` | `api`、`nurse-web`、`patient-web`（做過 J-20 的話還有 `ai-gateway`）都是 `Up`，映像檔是 `<新 tag>` |
| health | `{"status":"ok",…}` |
| 護理站 | 紅框自己消失，不必重新登入就能繼續用（或重新整理後登入） |

記下：從按下重新開機到護理站紅框消失，**總共幾分鐘**。這個數字要寫進交接給護理長。

**沒過的話**（三分鐘後服務沒有回來）：記下實況——Docker Desktop 有沒有隨登入起來、J-23 第 1 項有沒有勾。然後手動開 Docker Desktop、等變綠、`docker compose --env-file $cfg up -d`。**不要在現場改院方的登入設定或開機設定**，寫進交接的「已知限制」，交資訊室決定。

---

## 6. 院方 API：探測一次

1005 起院方透析清單 API 要取代護理師的手動輸入（《[實作規格書](../requirements/implementation-spec.md)》4.19）。**這一次只探測、不啟用**：看主機連不連得到、回應長什麼樣，把輸出帶回來。

### J-26 探測院方透析清單 API（＝V-30a、E-16）

**做什麼**：位址向 J-02 第 7 題約好的人要，**只在這裡當場輸入，不要寫進 `.env`、不要寫在紙上、不要貼進任何紀錄**：

```powershell
$u = Read-Host '院方透析清單 API 的位址（含 dialysislist.php，不含 ?date=）'
docker compose --env-file $cfg exec -T -e HOSPITAL_API_BASE_URL=$u api node apps/api/dist/hospital-api-probe.js
```

**怎麼知道成功了**：印出「連線：成功」「模擬標頭：沒有」「解析：成功，data_list 共 N 列」，接著是每一欄的型態分布與幾段統計，最後一行「以上可以整段抄進演練紀錄」。**整段抄進演練紀錄**：工具只印結構（型態、欄數、筆數、床位的樣式），**不印任何病人的值，也不印位址**。

| 症狀 | 處置 |
|---|---|
| `連線：失敗——找不到院方主機` 或 `連不到院方主機所在的網段` | 主機與院方 API 不在同一個網段，或名稱查不到。抄下來，問資訊室（Q-35）；**不要改主機的網路設定** |
| `連線：失敗——連線被拒` | 位址的埠不對，或院方服務沒開。核對位址再試一次 |
| `連線：失敗——逾時` | 30 秒內沒回應。換個時間再試，兩次都逾時就抄下來 |
| `解析：失敗` | 位址打到的不是透析清單（例如少了檔名），核對位址 |
| `模擬標頭：有` | 打到的是模擬院方 API，位址填錯了 |
| `沒有設定院方 API 的位址` | `Read-Host` 那一行沒輸入東西 |

> ⚠️ **不要用瀏覽器或 `curl` 直接打院方 API**：回應是全中心病人的姓名與病歷號，會整片印在螢幕上。

做完把 `$u` 清掉：

```powershell
Remove-Variable u
```

---

## 7. 暫用平板（時間夠、院方准才做）

醫院的 15 台平板還沒到，**目前正式使用只有醫師給的一台 Galaxy Tab S6 Lite**（[暫用平板紀錄](../notes/interim-tablet.md)）。做這一節的條件，**三條都要成立**：J-02 第 8 題院方准、J-08 第 4 步手機在平板的 Wi-Fi 上開得到下載頁、時間還剩 1.5 小時以上。不成立就跳到第 8 節，交接寫「平板未佈建」。

### J-27 平板的事前檢查

**做什麼**（在平板上）

1. **不要原廠重設**（重設會把 WebView 退回 2023 年的版本，院內沒辦法再更新）。
2. 設定 → 開發人員選項 → **USB 偵錯關掉**（出發前沒關的話）。
3. 字型大小：照醫師的答覆。醫師說可以調，就到「設定 → 顯示 → 字型大小與樣式」調回預設；醫師說不調，維持 1.1，**記下來**（病人端可能被放大 10%，J-29 時看有沒有被擠壞）。
4. 連上**院內給平板用的 Wi-Fi**，瀏覽器開 `http://<IP>:18081/shell/`。

**怎麼知道成功了**：看得到下載頁；下載頁上寫的主機位址是 `https://<IP>:18081`。最下面「版本資訊」的**三個 SHA-256 抄下來**（交接要用）。

| 症狀 | 處置 |
|---|---|
| 平板開不到，手機在同一個 Wi-Fi 開得到 | 平板的 Wi-Fi 連錯了 |
| 都開不到 | 這個 Wi-Fi 到不了主機，找資訊室，不要自己關防火牆 |
| 下載頁上的位址還是舊名稱 | 瀏覽器顯示的是舊頁面，重新整理；仍是舊的，回 J-12 |

---

### J-28 在護理端註冊、平板安裝 App（＝V-26、V-27）

**做什麼**

1. 護理站的電腦：護理端 → **新增裝置** → **註冊新平板**。畫面出現一個**佈建 QR code** 與一行網址。**這兩樣只顯示一次**，這個畫面先不要關，做完 J-29 再離開。網址要以 `https://<IP>:18081` 開頭；不是的話 `.env` 的 `MDM_KIOSK_BASE_URL` 不對，回 J-10。
2. 平板：設定裝置 PIN；關閉「新增使用者」。
3. 平板：設定 → 安全性（或在設定裡搜尋「固定」）→ **螢幕固定**：開啟，勾「解除固定前要求 PIN」。
4. 平板瀏覽器開 `http://<IP>:18081/shell/` → 「下載 App」→ 安裝。問是否允許瀏覽器安裝不明來源的 App 時，允許。

**怎麼知道成功了**：平板上多了「透析照護平板」這個 App。

| 症狀 | 處置 |
|---|---|
| 「套件與現有套件衝突」 | 這台裝過第十七冊演練時的開發版。先解除安裝再裝 |
| 「應用程式未安裝」 | 下載不完整，重新下載 |

---

### J-29 第一次開啟並釘住（＝V-28）

**做什麼**

1. 開「透析照護平板」→「**掃描 QR code**」→ 允許相機 → 對準 J-28 畫面上的 QR code。三欄自動填好，**核對序號與平板背面貼的標籤一致**（沒貼就現在貼一張，寫序號）。
2. 「儲存並啟動」→ 系統問「要固定這個應用程式嗎」→「確定」。
3. 護理端 → 新增裝置，等 15～30 秒。
4. 平板**解除一次固定**（輸入 PIN），30 秒內護理端要變成「已跳出」。
5. 釘回去：按多工鍵把「透析照護平板」從多工畫面滑掉，再從桌面開啟 → 系統再問「要固定嗎」→「確定」。15～30 秒內護理端回到「固定中」。（沒跳出確認框就重新開機，App 開機後會自己起來並詢問）

**怎麼知道成功了**

| 在哪裡看 | 應該是 |
|---|---|
| 平板 | 病人端的等待畫面，**沒有任何憑證警告**；按上一頁、首頁、多工鍵都離不開；畫面是橫的 |
| 護理端「固定狀態」 | 固定中 |
| 護理端「外殼版本」 | 版本正常，底下有版本號 |

字型大小維持 1.1 的話，多看一眼：等待畫面的字有沒有被截斷或擠成兩列，**拍下平板畫面**（等待畫面沒有病人資料才拍）。

| 症狀 | 處置 |
|---|---|
| 「主機位址不是 https:// 開頭」 | 回 J-28 第 1 步 |
| 一片空白或「網頁無法使用」 | 平板「設定 → 應用程式 → 透析照護平板 → 儲存空間 → 清除資料」，重新註冊、佈建 |
| 上方琥珀色「……版本不相容」 | 抄下原文，回開發端；平板先解除固定、交給護理長保管 |

---

## 8. 收尾

### J-30 冒煙測試（在護理站的電腦）

**不輸入任何真實病人資料、不開任何功能開關。** 在護理站的電腦上走一次：

| # | 做什麼 | 應該是 |
|---|---|---|
| 1 | 登出，再用護理長的帳號登入 | 登得進去，預設開「簡易版」 |
| 2 | 簡易版 | 看得到床位圖與旁邊的框；不必拖任何東西 |
| 3 | 切到專業版、再切回簡易版 | 兩邊都開得起來 |
| 4 | 系統管理 → 版本更新紀錄 | 有 J-18 那一筆（沒換新版就沒有，正常） |
| 5 | 系統管理 → 備份歷程 | 有 J-22 那一份 |
| 6 | 系統管理 → 營運參數與選項清單 →「院方資料同步」卡片 | 顯示還沒設定位址（這一次本來就不啟用） |
| 7 | 稽核軌跡 | 查得到今天的登入、改密碼、資料庫線上備份、版本更新 |
| 8 | 總覽螢幕：在護理長指定的那台螢幕開護理端的總覽 | 開得起來；問護理長這台螢幕會不會休眠，會的話請資訊室調電源設定 |
| 9 | J-25 時看到的斷線紅框 | 已經看過就打勾；沒做 J-25 就寫「未驗」 |
| 10 | 做過第 7 節：平板在等待畫面、護理端「固定中」 | 一致 |

**怎麼知道成功了**：每一列都打勾，或寫明為什麼沒做。任何一列「應該是」沒出現，抄下畫面上的字，寫進交接的「已知限制」。

---

### J-31 交接

**做什麼**：當場講一次、讓對方自己做一次，再把下表寫在一張紙上交給護理長與資訊室（第一行寫「**首波試用前的準備，還不是正式上線**」）。**交接紙上不寫密碼、不寫 `.env` 的值**：

| 項次 | 寫什麼 |
|---|---|
| 網址 | 護理站一律開 `http://<IP>:18080`（實際的 IP 寫在給院方的這張紙上即可）；**不要用 `localhost` 或舊名稱開**，會登不進去 |
| 帳號 | 第一個管理員帳號的工號；**密碼由護理長自己保管**，開發端不知道 |
| 版本 | 本系統 `<新 tag>`（沒換新版就寫 `v0.3.0`）；外殼 `v0.3.0` |
| 位置 | `C:\hd\hd-tablet-care` 底下的 `repo`、`hd-kiosk-shell`、`config`、`backups`、`export` 各放什麼；兩個資料卷的名字。**這些都不能刪** |
| 啟停 | 在 `C:\hd\hd-tablet-care\repo` 底下打 `docker compose --env-file C:\hd\hd-tablet-care\config\.env stop`（停）／`up -d`（啟） |
| 斷電之後 | 護理端每個畫面閃紅框、平板顯示請按床邊呼叫鈴 → 到主機開機、以 Administrator 登入 → **什麼都不碰，等三分鐘**（J-25 量到的是＿分鐘）→ 紅框消失就好了 |
| 備份 | 每天 03:00 自動備份到 `backups`；誰、多久送往另一台機器（J-22 第 4 步的答覆）；今天的金鑰備份檔名（J-12） |
| 防毒 | 排除清單加了沒有、誰加的（J-24）。**沒加之前不得輸入真實病人資料** |
| 外殼 | 下載頁的三個 SHA-256（J-27）；已佈建平板的序號與床號（第 7 節） |
| 功能開關 | 遊戲化、獎勵制度、跑馬燈、新增病人都關著；要開先讓護理部、社工、長者看過 |
| 資料取出 | 研究要取資料時照[第十六冊](16-data-export.md)在主機上做，**沒有院方核准不得執行**；取出紀錄在「系統管理 → 資料取出紀錄」 |
| 信任邊界 | 能登入這台主機的人一律可信任（DEP-38）；日後帳號政策改變要重新評估 |
| 已知限制 | AI 關閉；院方 API 未啟用（探測結果帶回去看）；J-25 若沒過的實況；未佈建的平板；Docker 查 Docker Hub 網域時好時壞（日後更新會再遇到）；Git 是否補走變更流程 |
| 聯絡方式 | 出事找誰 |

---

### J-32 離院前（＝E-10、E-12）

**做什麼**

1. 演練紀錄第 12 節每一格都填了，**每一步都有開始與結束時間**。
2. 補齊 1001 留下的空白（第十五冊之三 E-10）：0922 的容器（J-05、J-06）、Docker Desktop 四項（J-23）、三個 SHA-256（J-27；沒做平板就從主機瀏覽器開 `http://localhost:18081/shell/` 最下面抄）、Git 是誰裝的、`C:\hd` 這個位置院方同不同意。
3. **登入沒通就離院**（C 級）：把服務停掉，不要留一個看起來能用的半成品：

   ```powershell
   docker compose --env-file $cfg stop
   docker ps --format "{{.Names}}  {{.Status}}"
   ```

   清單裡不該再有 `hd-tablet-care-` 開頭的。下一次來再 `up -d`。
4. 主機上開過的 PowerShell 全部關掉（裡面有 `.env` 的內容）；主機的瀏覽器登出護理端。
5. 手機裡有沒有拍到 `.env`、病人資料、院方 API 位址的照片，有就當場刪。

**怎麼知道做完了**：上面五項都打勾。

---

### J-33 回來之後（＝E-13～E-15）

| 什麼時候 | 做什麼 |
|---|---|
| **當天晚上** | 演練紀錄補完，趁記憶還熱 |
| 三天內 | 照紀錄寫一本**第三次進院紀錄**（格式照[第十四冊之四](14d-second-visit.md)：逐步做到哪裡、主機實況、手冊要改的地方），掛進部署手冊 |
| 三天內 | 用 J-07 抄回來的前兩條，判斷 1001 是可能 A 還是 B，寫回[第十五冊之三](15c-why-1001-failed.md) 3.2 節與第十四冊之四 M-01 |
| 三天內 | J-26 的探測輸出交給開發端，對照實作規格書 4.19 的假設（下機怎麼判定、床號長什麼樣） |
| 有空時 | 手冊哪裡寫錯、少寫，改回這一冊與原冊；`deploy/hospital.env.example` 與 `docker-compose.yml` 註解裡的 `hd-server` 範例要不要改（E-14，程式檔，另外決定） |

---

## 附錄一：步驟對照

| 本冊 | 原冊 | 本冊 | 原冊 |
|---|---|---|---|
| J-01 | V-03、W-01、W-02 | J-18 | W-19 |
| J-02 | V-01、V-02、W-03、T-01 | J-19 | W-19、V-17 |
| J-03 | 第四冊 H-01 | J-20 | V-29、V-30、Z-20～Z-22 |
| J-04 | V-09 | J-21 | 第十六冊 |
| J-05 | E-05、第十五冊 0.5 節 | J-22 | V-18、W-17 |
| J-06 | L-01～L-07 | J-23 | V-05 第一部分 |
| J-07 | E-06、T-02 | J-24 | V-05 第二部分、E-11 |
| J-08 | T-03、T-04 | J-25 | V-19、W-18 |
| J-09 | T-05 | J-26 | V-30a、E-16 |
| J-10 | T-06 | J-27 | V-25、暫用平板紀錄第 4 節 |
| J-11 | T-07、V-17 | J-28 | V-26、V-27 |
| J-12 | T-08～T-10、V-22～V-24 | J-29 | V-28 |
| J-13 | T-11 | J-30 | 第十五冊 10.1 節、H-16 |
| J-14 | T-12、T-14 | J-31 | 第十五冊 10.1 節、H-21 |
| J-15 | W-19、V-06 | J-32 | E-10、E-12 |
| J-16 | 第十五冊之一第 6 節 | J-33 | E-13～E-15 |
| J-17 | W-19、V-14 | | |

`V-xx` 是第十五冊、`T-xx` 是第十五冊之四、`E-xx` 是第十五冊之三、`W-xx` 是第十一冊、`L-xx` 是第十四冊之三的步驟。演練紀錄裡寫「卡在 J-12」或「卡在 T-08」指的是同一件事。

---

## 附錄二：新版出問題，退回 `v0.3.0`（＝W-20）

**什麼時候用**：J-18 之後，新版的 `api` 起不來、或主線功能壞掉，而現場解不開。**越早決定越好**：退回會把資料庫換回 J-18 的更新前備份，**更新之後寫進去的資料會一起消失**（這一次沒有真實資料，代價是零）。

程式可以退版，**資料庫不能把遷移倒回去**，所以退回＝「舊程式＋更新前那份備份」。

**做什麼**（`<備份檔名>`、`<雜湊>` 是 J-18 抄的那一份 `hd-before-update-<時間>.db`）

1. 程式碼與設定退回：

   ```powershell
   git checkout v0.3.0
   notepad $cfg
   ```

   `HD_IMAGE_TAG` 改回 `v0.3.0`。`HD_EXPORT_DIR` 與兩個院方 API 的變數**留著沒關係**（舊版不讀）。
2. 停後端、把新版的資料庫移到旁邊、還原更新前備份（第二、三條各是一整行）：

   ```powershell
   docker compose --env-file $cfg stop api
   docker compose --env-file $cfg run --rm --no-deps --entrypoint sh api -c "mkdir -p /data/before-rollback && mv /data/hd.db /data/hd.db-wal /data/hd.db-shm /data/before-rollback/ 2>/dev/null; ls -l /data/before-rollback"
   docker compose --env-file $cfg run --rm --no-deps api node_modules/.bin/ts-node --project apps/api/tsconfig.json apps/api/scripts/restore-backup.ts --from /backups/<備份檔名> --to /data/hd.db --sha256 <雜湊>
   docker compose --env-file $cfg up -d
   ```

3. 做過 J-20 的話，閘道也退回：`docker compose --env-file $cfg --profile ai up -d ai-gateway`。

**怎麼知道成功了**：還原輸出 `完整性檢查：ok`、`還原的就是 DATABASE_URL 指向的正本`；`docker ps` 三個服務的映像檔是 `hd-tablet-care:v0.3.0`；護理站 Ctrl＋F5 後用護理長的新密碼登得進去（J-11 已經用 `<IP>` 重建過 `v0.3.0` 的網頁，所以舊版也登得進去）。

移到 `/data/before-rollback/` 的那份**先留著**，帶回新版出問題的原文給開發端判斷。新版的映像檔也不要刪。

---

## 附錄三：護理端頁面開得起來卻登不進去

### 先認清：用哪個網址開

| 開的網址 | 登得進去嗎 |
|---|---|
| `http://<IP>:18080` | 可以。在主機上開也一樣 |
| `http://localhost:18080` | **登不進去**：網址列是 `localhost`，名單上是 `<IP>` |
| `http://<名稱>:18080` | J-11 之後**登不進去**：名單上只剩 `<IP>` |

### 第 1 步：看登入鈕下面的訊息

| 訊息 | 意思 | 接著 |
|---|---|---|
| `工作ID 或密碼錯誤` | 有連到後端，帳號或密碼不對 | 見 J-13 那一列 |
| `Failed to fetch` | 瀏覽器沒拿到後端的回應：位址錯，或被放行名單擋掉 | 第 2 步 |

### 第 2 步：網址列

**把網址列上的網址原文抄下來。** 不是 `http://<IP>:18080` 就改用這個網址開，Ctrl＋F5，再登入一次。

### 第 3 步：在主機上查（照順序，結果全部抄下來，包括正常的）

```powershell
Select-String -Path $cfg -Pattern '^(HD_PUBLIC_API_URL|CORS_ORIGINS)='
docker compose --env-file $cfg exec nurse-web grep -rhoE 'https?://[A-Za-z0-9.-]+:[0-9]+' apps/nurse-pwa/dist/assets
curl.exe -s http://<IP>:13000/api/health
curl.exe -s -i -H "Origin: http://<IP>:18080" http://<IP>:13000/api/health | Select-String Access-Control-Allow-Origin
docker compose --env-file $cfg logs api | Select-String '允許的前端來源' | Select-Object -Last 1
```

| 結果 | 意思 | 處置 |
|---|---|---|
| 第二條的位址與第一條的 `HD_PUBLIC_API_URL` 不一樣 | 網頁是在改 `.env` 之前建的 | `build`、`up -d`，Ctrl＋F5 |
| 第三條沒有 `{"status":"ok",…}` | `<IP>:13000` 連不到後端 | `docker compose --env-file $cfg logs api --tail 30` 看原因 |
| 第四條印出 `Access-Control-Allow-Origin: http://<IP>:18080` | 後端有放行 | 問題不在名單：回第 2 步，或按 F12 → Network 再按一次登入，抄下請求送去的網址與錯誤原文 |
| 第四條什麼都沒印，第五條不是 `http://<IP>:18080` | 名單寫錯，或改完沒 `up -d` | 改 `.env` 的 `CORS_ORIGINS`，`docker compose --env-file $cfg up -d`，再打第四條 |

### 試了一小時仍然不通

**停手。** 兩條路擇一，問過資訊室再選：

| 路 | 什麼時候 | 做什麼 |
|---|---|---|
| 換回名稱 | 資訊室說名稱在院內 DNS 查得到，而且 J-09 那份 `.env.before-ip` 還在 | `Copy-Item "$root\config\.env.before-ip" $cfg`，`CORS_ORIGINS` 改成 `http://<名稱>:18080`（1001 填錯的就是這一行），接著 J-11、J-12 照做一次（`<IP>` 都換成 `<名稱>`；`shell-builder` 會寫「伺服器憑證（`<名稱>`）」，是對的） |
| 保留現況 | 其他情形 | 不再改任何東西，做 J-32（服務停掉、紀錄帶回） |

---

## 附錄四：一張紙帶進去

1. **先抄再改**：J-07 的五樣，原文、抄到最後一行。
2. **先從護理站連 `<IP>`**，連得到才改（J-08）。
3. **三個位址一起改，一字不差**；之後一律開 `http://<IP>:18080`，不用 `localhost`、不用舊名稱。
4. **改了 `CORS_ORIGINS` → `up -d`；改了 `HD_PUBLIC_API_URL` → `build` 再 `up -d`。** 只存檔等於沒改。
5. **`shell-builder` 新產生的只能有伺服器憑證**，看到 CA 或簽章金鑰就停手。
6. **登入通了才換新版**；換新版先補 `HD_EXPORT_DIR`，舊映像檔不刪。
7. **`Failed to fetch` ＝ 帳號密碼還沒被看過**，先查名單和位址。
8. **院方 API 只用探測工具看**，位址不寫下來。
9. **功能開關一個都不開，不輸入真實病人資料。**
10. **登入沒通就離院，服務要停掉。**

---

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|

[← 第十七冊 · 第三次進院前的模擬部署](17-rehearsal.md)　[← 回部署手冊總覽](index.md)
