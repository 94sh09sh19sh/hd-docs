# 第十五冊 · 從零開始的實際部署（新手版第二版）

版本：v0.1　文件狀態：草案（1001 新增）　編號：`V-xx`　**要印出來帶進去**

> **這一冊取代[第十四冊](14-from-zero.md)。** 第十四冊是 1001 第二次進院時照著走的那一版，
> 這一冊依那一次帶回來的資料（[第十四冊之四](14d-second-visit.md)）重寫：
> 根目錄改成院內實際用的 `C:\hd\hd-tablet-care`、在填 `.env` 之前多一步「決定主機位址」、
> 建置之前先用 Docker 自己下載一次基底映像（1001 三次查不到 Docker Hub 的網域）、
> Git 沒裝時怎麼辦、防毒怎麼查、護理端登不進去怎麼查，都併進步驟本身；
> 也多了一節「**1001 之後的院內主機從哪裡接著做**」（0.5 節）。
>
> 和第十四冊一樣，這一冊給第一次部署的人：從「一台什麼都還沒動的主機」走到「護理站登得進去、平板釘住、交接完成」，
> 每一步都寫出要打什麼、畫面上應該看到什麼、沒看到時怎麼辦。讀完不需要先懂 Docker 或 Git，第 0.4 節的名詞表就夠了。
>
> 同一套步驟也用來做**模擬部署**：在自己的開發機上照走一次。兩者不同的地方，每一步都用
> **🧪 模擬部署** 的方框標出來；沒有方框的步驟，兩者一字不差。
>
> 這一冊是第十一、十二、十三冊（現行路線）的**新手導讀版**：每一步標題後面註明對應的第十四冊與原冊步驟編號（例如「＝N-13、W-13」）。
> 兩者衝突時，以原冊為準，規則的真本仍是《[部署規範](../requirements/deployment-spec.md)》v3.0。
>
> `.env` 的逐項填法另成兩冊：[第十五冊之一（實際部署）](15a-env-hospital.md)、[第十五冊之二（模擬部署）](15b-env-simulation.md)。
> 1001 為什麼登不進去、下一次要做什麼，白話版在[第十五冊之三](15c-why-1001-failed.md)。
> 院內主機的 `<主機>` 要從名稱改成 IP，照[第十五冊之四](15d-switch-host-to-ip.md)。

---

## 0. 讀之前

### 0.1 實際部署與模擬部署

| | 實際部署 | 模擬部署 |
|---|---|---|
| 是什麼 | 在**院內主機**上正式部署，之後護理師真的會用 | 在**自己的開發機**上，用同一套指令從零走一次（《部署規範》DEP-22「開發機部署實測」，第十一冊第 7 節） |
| 為什麼要做 | 這就是目的 | **每一個要交給院方的 tag，都要先模擬部署通過**，才准拿去院內（W-01）。院內出錯的代價高，開發機上出錯只是重來 |
| 什麼時候 | 進院當天 | 進院前幾天（D-3 左右），以及每次要交新 tag 之前 |
| 資料 | 真實病人資料 | **只准虛構資料** |

**第一次讀這本的正確順序：先照著做一次模擬部署，再帶著它進院做實際部署。**

> ⚠️ **1001 的教訓**：那一次帶進院的 `v0.3.0` 是出發前才打的 tag，**沒有先模擬部署過**（第十四冊之四 1.1 節）。
> 院內遇到的問題剛好都不是程式本身的問題，但這是運氣。這一條不准再跳過。

### 0.2 標記怎麼看

> 🧪 **模擬部署**：像這樣的方框，寫的是模擬部署時**要改做什麼或可以跳過什麼**。實際部署時略過不看。

> ⚠️ 這種方框是**兩者都要注意**的警告。

> 📍 **1001**：這種方框寫的是 **1001 第二次進院在院內主機上實際看到的**，讓你知道這一步在那台主機上會長什麼樣。

每一步照舊分三塊：**做什麼**、**怎麼知道成功了**、**可能怎麼壞**。
**「怎麼知道成功了」那一塊沒看到，就是沒成功**——不要因為「好像沒出錯」就往下。

### 0.3 兩者不同的地方，一張表看完

| 項次 | 實際部署 | 🧪 模擬部署 | 在哪一步 |
|---|---|---|---|
| 機器 | 院內主機 | 你的開發機 | — |
| 0922 留下的容器與 clone | 1001 是否收過**未確認**，先用[第十四冊之三](14c-cleanup-first-visit.md) L-01、L-07 看一眼 | 沒有，不必做 | V-04 之前 |
| Git 與 Docker | 資訊室裝；**1001 主機原本沒有 Git，現場裝了 2.56.0** | 自己裝 | V-04 |
| 問資訊室的問題清單 | 至少一週前寄出 | 不必 | V-02 |
| Docker Desktop 設定、防毒排除 | 逐項檢查，改動要資訊室同意；**1001：Defender 運作中、排除清單空** | 看一眼即可 | V-05 |
| 三個連接埠 | `13000`、`18080`、`18081`（0930 資訊室確認） | 同一組，被佔用就自己換 | V-07 |
| 主機位址（`<主機>`） | 護理站與平板都連得到、資訊室確認的名稱或固定 IP | 開發機 Wi-Fi 網卡的區網 IP | V-08 |
| 根目錄（`$root`） | `C:\hd\hd-tablet-care`（1001 實際用的） | `C:\hd-sim` | V-09 |
| 部署金鑰 | 主機上產生，登記到 GitHub | 開發機上另產生一把，同樣登記 | V-10、V-20 |
| APK 簽章用途 | `hospital` | `dev` | V-12 |
| 平板 | 院內的平板 | 開發用的 Android 手機 | 第 8 節 |
| 驗收工具 | 不跑（主機上沒有、也不准裝 Node.js） | 多跑三支 `verify:iteration… --live` | V-31 |
| 院方 API（1005） | 只**探測**一次，位址當場輸入、不寫進 `.env` | 開模擬院方 API，`.env` 指向它並寫 `HD_SIMULATION_DEPLOYMENT=yes` | V-30a |
| 重新開機測試 | **必做**，決定這條路線在院內能不能用 | 驗不出院內的情形，可略 | V-19 |
| 備份送往另一台機器 | 院方負責，要當場確認 | 不必 | V-18 |
| 做完之後 | 交接，服務留著跑 | **撤除乾淨**，下一次才又是「從零」 | 第 10 節 |

> 第十四冊的模擬部署，護理端用 `localhost` 開；這一冊改成用開發機的區網 IP。
> 用 `localhost` 時，「網址列的來源」與「`.env` 寫的位址」永遠一致，**1001 院內那種登不進去的情形在模擬部署裡永遠不會出現**。
> 換成區網 IP，模擬部署才和院內同一個形狀。

### 0.4 先認識十個名詞

| 名詞 | 一句話 |
|---|---|
| **PowerShell** | Windows 內建的指令視窗。本冊每一條指令都在這裡打。開法：開始選單輸入 `PowerShell` → 按「Windows PowerShell」 |
| **Git**、**clone** | Git 是管理程式碼版本的工具；`git clone` 是把 GitHub 上的程式碼整份複製到這台機器 |
| **tag** | 程式碼某一版的名字，例如 `v0.3.0`。**部署一律部署某個 tag，不部署分支**：分支會一直變，tag 不會 |
| **部署金鑰** | 一把只給這台機器、只能讀一個 repo 的鑰匙。私鑰留在機器上，只把公鑰交給 repo 管理者登記 |
| **Docker**、**映像檔**、**容器** | Docker 把程式和它需要的一切打包成**映像檔**（像安裝光碟），跑起來的那一份叫**容器**。同一個映像檔可以跑出好幾個容器 |
| **docker compose** | 照 repo 裡的 `docker-compose.yml` 一次把好幾個容器開起來、關掉。**本系統的容器一律由它產生，不准自己手動開** |
| **資料卷** | Docker 管理的一塊儲存空間。**資料庫就放在這裡**，檔案總管看不到它是正常的 |
| **繫結掛載** | 把主機上的某個資料夾借給容器用。本系統**只准兩個**：設定目錄與備份目錄 |
| **`.env`** | 一份「變數名稱＝值」的文字檔，存這次部署的設定（埠、位址、密碼）。怎麼填見第十五冊之一、之二 |
| **連接埠（埠）** | 同一台機器上區分不同服務的號碼。本系統要三個：後端、護理端、病人端 |

另外兩個在 V-17 會碰到的：

| 名詞 | 一句話 |
|---|---|
| **來源（origin）** | 瀏覽器網址列上「`http://` ＋ 主機 ＋ 埠」那一段，例如 `http://<主機>:18080`。`localhost` 與主機名稱是**兩個不同的來源**，即使指的是同一台機器 |
| **CORS** | 後端用來決定「哪些來源的網頁可以呼叫我」的規則，名單寫在 `.env` 的 `CORS_ORIGINS`。不在名單上的來源，瀏覽器會說 `Failed to fetch` |

### 0.5 1001 之後的院內主機：從哪裡接著做

1001 第二次進院做到第十四冊 N-23，離院時**三個服務還在跑**（[第十四冊之四](14d-second-visit.md)）。下一次進院不是從零開始。

**先看它是不是還是 1001 離開時的樣子**（開一個 PowerShell，這幾行的前三行就是 V-09 的開工三行）：

```powershell
$root = "C:\hd\hd-tablet-care"
$cfg  = "$root\config\.env"
cd $root\repo
git describe --tags
docker compose --env-file $cfg ps
docker volume ls --filter name=hd-tablet-care
Get-ChildItem $root\backups\keys
curl.exe -s http://localhost:13000/api/health
```

| 看什麼 | 1001 離開時 | 不一樣的話 |
|---|---|---|
| `git describe --tags` | `v0.3.0` | 有人動過 repo。**停手**，先問資訊室 |
| `ps` | `api`、`nurse-web`、`patient-web` 都是 `Up` | 主機中間重新開機過、服務沒有自己回來——**這就是 V-19 要的答案**，記下「重開機後沒有回來」，再 `docker compose --env-file $cfg up -d` |
| 資料卷 | `hd-tablet-care-data`、`hd-tablet-care-keys` 兩個 | 不見了就不是 1001 的狀態，停手 |
| `backups\keys` | 有 `hd-keys-20261001-173347.tar.gz` | 不見了先問資訊室是不是已經送往另一台機器 |
| health | `{"status":"ok",…}` | 看 `docker compose --env-file $cfg logs api --tail 30` |

**都一樣的話，從這裡接著做：**

| 步驟 | 1001 | 下一次 |
|---|---|---|
| L-01、L-07（第十四冊之三） | 未記 | **先做**，只看不動。0922 的容器還在的話照 L-02 起收掉 |
| V-01～V-03 | — | 照做。**帶去的 tag 若不是 `v0.3.0`，那是一次更新**，照[第十一冊](11-compose.md) W-19 換版，不是重新 clone |
| V-04～V-07 | 做過 | 只補 1001 沒記的：V-05 的四項設定、V-06 的連線實測（含兩條 `docker pull`） |
| V-08 | 現場用 `hostname` 決定，填的是**名稱**（1005 補記；資訊室沒有確認過） | 與資訊室確認那個值。**要改用 IP**，在 V-17 之前照[第十五冊之四](15d-switch-host-to-ip.md)做，它一併涵蓋 V-17 與 V-22～V-24 要重做的部分 |
| V-09～V-16 | 做過 | 不重做。只照[第十五冊之一](15a-env-hospital.md)第 6 節核對主機上那份 `.env` |
| **V-17** | **登入失敗** | **從這裡開始**，登入通了才往下 |
| V-18、V-19 | 未測 | 照做 |
| V-20～V-24 | 做過 | 不重做。V-22 的三個 SHA-256 從下載頁抄下來（交接要用） |
| V-25～V-28 | 未測 | 照做（要有平板） |
| V-29、V-30 | 未記 | 照做；做過的話 V-30 的最後一條會直接印出 503，就是做過了 |
| 第 10.1 節 | 沒做 | 照做 |

### 0.6 本系統在主機上長什麼樣

```
院內主機（或 🧪 開發機）
│
├─ $root\                      本系統自己的資料夾（實際 C:\hd\hd-tablet-care，模擬 C:\hd-sim）
│   ├─ repo\                   本系統的程式碼（git clone，切到 tag）
│   ├─ hd-kiosk-shell\         外殼 App 的程式碼（git clone）
│   ├─ config\.env             設定 ← 第十五冊之一、之二教你填
│   │   └─ ai-gateway\config.yaml   AI 閘道的設定（V-29）
│   └─ backups\                備份（院方從這裡送往另一台機器）
│       └─ keys\               金鑰備份（V-23）
│
├─ Docker 資料卷
│   ├─ hd-tablet-care-data     資料庫
│   └─ hd-tablet-care-keys     院內 CA、伺服器憑證、APK 簽章金鑰、下載頁
│
└─ 容器（docker compose 產生）
    ├─ api            後端           ← 後端埠 13000
    ├─ nurse-web      護理端網頁     ← 護理端埠 18080 ← 護理站的瀏覽器
    ├─ patient-web    病人端網頁     ← 病人端埠 18081 ← 平板上的外殼 App（HTTPS）
    ├─ shell-builder  建 APK（一次性，平時不跑）
    └─ ai-gateway     AI 閘道（首波不接模型，只讓它就位）
```

### 0.7 要花多久

| 段落 | 大約時間 | 備註 |
|---|---|---|
| 第 1～2 節：主機準備 | 45 分鐘 | 含 V-06 先下載兩個基底映像；主機沒有 Git、要現場裝時另加 15 分鐘；🧪 模擬部署第一次要裝 Docker Desktop，另加 30～60 分鐘 |
| 第 3 節：決定位址 | 15 分鐘 | 要資訊室在場；事先問到答案就只是核對 |
| 第 4～6 節：程式碼、設定、建置、啟動 | 40 分鐘 | 建置約 10 分鐘（1001 院內沒有計時） |
| 第 7 節：備份、重新開機 | 20 分鐘 | |
| 第 8 節：外殼 App 與平板 | 60～90 分鐘 | **`shell-builder` 的映像檔（V-21）1001 院內實測 27～33 分鐘**，含一次 DNS 出錯 |
| 第 9 節：AI 閘道 | 15 分鐘 | |
| 第 10 節：交接或撤除 | 30 分鐘 | |

**每一步都計時，開始與結束各記一次，寫進《[部署演練紀錄](../notes/deployment-drills.md)》。** 1001 只有一步有計時，下一次估時間就只能靠猜。

---

## 1. 動手之前

### V-01 約好人（＝N-01、總覽第 3 節）

**做什麼**：至少一週前，用訊息向資訊室確認：「當天 X 點到 Y 點，需要一位能登入那台主機、有管理員權限的同仁全程在旁。」
另約護理長或指定的護理師，交接時要在。

**怎麼知道成功了**：有具體的人名與時段。「到時候看看」要當成沒約到。

> 🧪 **模擬部署**：跳過。

---

### V-02 把問題清單寄給資訊室（＝N-02、W-03）

**做什麼**：把[第十一冊 W-03](11-compose.md) 那張表寄出去，答覆寫進演練紀錄。

已經有答案、不必再問的：

| 題 | 答案 | 來自 |
|---|---|---|
| 連接埠 | `13000`、`18080`、`18081` | 0930 資訊室 |
| 主機對外連線 | 常態、沒有限制 | 0930 資訊室（Q-32） |
| Docker 版本 | Docker 29.3.1、Compose v5.1.1（1001 再看一次，沒變） | 0922、1001 現場 |
| 主機上有沒有 Git | 原本沒有，1001 現場裝了 2.56.0 | 1001 現場 |
| 防毒 | Windows Defender，運作中，排除清單是空的 | 1001 現場 |
| 主機的 IP | **固定的**（第三次進院照第十五冊之四把 `<主機>` 換成 IP） | 1007（Q-27 第 12 題） |
| 斷電之後誰登入 | **護理長**：護理端出現斷線警示後到主機重新登入；不設開機自動登入 | 1007（Q-27 第 4 題） |
| Docker Desktop 的使用統計 | **關掉**（第三次進院在 V-05 關） | 1007（Q-27 第 9 題） |
| Microsoft Store 的自動更新 | **先不改**，實際使用發現嚴重影響再改 | 1007（Q-27 第 10 題） |

**還沒答、最要緊的**：

1. ~~**護理站與平板用哪個名稱或 IP 連這台主機？IP 能不能固定？**~~（**1007 已答：IP 是固定的**，見上表；護理站與平板的網段連不連得到，照第十五冊之四 T-01 再確認）
2. **Docker 的資料夾能不能加入 Defender 的排除清單、誰加？**（1001 查到排除清單是空的）
3. **1001 Docker 三次查不到 Docker Hub 的網域**（`production.cloudfront.docker.com`、`auth.docker.io`），院內 DNS 對這些網域穩不穩？（見 V-06）
4. ~~**斷電之後誰開機、誰登入？**~~（**1007 已答：護理長**，見上表）
5. 本系統放在 `C:\hd\hd-tablet-care`，院方同不同意？備份資料夾由誰、多久送往另一台機器？
6. 1001 現場裝的 Git，要不要補走院方的變更流程？
7. ~~Docker Desktop 的 **Send usage statistics** 能不能關？**Microsoft Store 的自動更新能不能改成手動？**~~（**1007 已答**：使用統計關掉、市集自動更新先不改，見上表）

**怎麼知道成功了**：每一題都有答覆，或寫明「未答覆」與對方是誰。

> 🧪 **模擬部署**：跳過。

---

### V-03 確認要交的 tag 已經模擬部署過，而且在 GitHub 上（＝N-03、W-01、W-02、Y-01）

**做什麼**：在開發機的工作目錄（平常寫程式的那個）打：

```powershell
git ls-remote --tags origin
git rev-parse <tag>
git show <tag>:services/shell-builder/shell.pin
```

**怎麼知道成功了**

| 看什麼 | 應該是 |
|---|---|
| 第一條的清單 | 看得到要交的 tag |
| 第二條 | 與模擬部署時用的是同一個 commit |
| 第三條 | `SHELL_TAG=` 那一版外殼，在 GitHub 的外殼 repo（`hd-kiosk-shell`）Tags 頁看得到 |
| 演練紀錄 | **這個 tag** 的模擬部署每一格都填了，沒有 ✗ |

**可能怎麼壞**：tag 不在清單上 → 它還沒推到 GitHub，`git push origin <tag>`。**沒模擬部署過的 tag 不准拿去院內**——出發前才打的 tag 一定沒有模擬部署過。

> 📍 **1001**：本系統 `v0.3.0`（`9992721`）、外殼 `v0.3.0`（`44b4d62`）。院內主機上現在跑的就是這一版。

> 🧪 **模擬部署**：這一步做的就是「準備一個要測的 tag」。tag 要先推上 GitHub，
> 因為模擬部署是從 GitHub 全新 clone，不是用你的工作目錄。外殼 repo 那個 tag 也一樣要推上去。

---

## 2. 主機這一層

> ⚠️ **從這裡開始，所有指令都在「要部署的那台機器」的 PowerShell 裡打**：實際部署是院內主機，🧪 模擬部署是開發機。
> **不要自己開任何容器，不要下 `docker run -v`、`-p`。** 0922 就是這樣失敗的（[第十冊](10-first-visit.md) F-01、F-02）；1001 照手冊沒有開，就沒有重演。

> ⚠️ **實際部署：做 V-04 之前，先確認 0922 留下的容器 `dialysis_system_v0` 不在了。**
> 1001 有沒有收過**沒有記到**。照[第十四冊之三](14c-cleanup-first-visit.md) L-01 看一眼：只剩標題列就是不在了，接著做 L-07；
> 還在的話照 L-02 起收掉。那個容器掛著整顆 C 槽，沒收掉不開始部署。🧪 模擬部署不必做。

### V-04 確認 Git 與 Docker 能用（＝N-04、W-04）

本系統對主機的要求**只有 Git 與 Docker 兩樣**。

**做什麼**

```powershell
git --version
docker version
docker info --format "{{.ServerVersion}} {{.OSType}} {{.Architecture}}"
docker compose version
```

**怎麼知道成功了**

| 指令 | 應該看到 |
|---|---|
| `git --version` | 一個版本號，例如 `git version 2.56.0.windows.1` |
| `docker version` | `Client` 與 `Server` 兩段都有版本號 |
| `docker info …` | `<版本> linux x86_64`，**中間一定要是 `linux`** |
| `docker compose version` | `v2` 以上 |

**可能怎麼壞**

| 症狀 | 處置 |
|---|---|
| `failed to connect to the docker API at npipe:…` | Docker Desktop 沒在跑。從開始選單開啟，等左下角變綠再重試 |
| 中間是 `windows` 不是 `linux` | 工作列右下角的 Docker 圖示按右鍵 → Switch to Linux containers |
| `git` 找不到 | 見下面「沒有 Git 時」 |
| `docker` 找不到 | 實際部署：**問資訊室，不要自己裝**。模擬部署：見下面方框 |
| 只有 `docker-compose`（有連字號）能用 | 舊版。實際部署請資訊室處理；模擬部署更新 Docker Desktop |

**沒有 Git 時**

實際部署：**請資訊室裝，或經他們同意後由你裝**，並在演練紀錄寫下是誰裝的、誰同意的。那是院方的變更流程。

裝法（資訊室問起也照這個講）：

1. 先確認處理器架構：

   ```powershell
   $env:PROCESSOR_ARCHITECTURE
   ```

   印出 `AMD64` 選 x64，印出 `ARM64` 才選 ARM64。院內主機是 `AMD64`。
2. 到 `git-scm.com` → Download for Windows，選 **x64 Setup**（standalone installer）。

   | 選項 | 選不選 | 為什麼 |
   |---|---|---|
   | **x64 Setup** | ✓ | 安裝程式會自己把 `git` 加進 PATH |
   | x64 Portable | ✗ | 不會加進 PATH，打 `git` 一樣找不到；要另外改 PATH，反而多動主機的設定 |
   | ARM64 Setup、ARM64 Portable | ✗ | 處理器架構不對 |

3. 安裝選項全部用預設值。
4. **關掉 PowerShell，開一個新的**（舊視窗不會知道新的 PATH），再打一次本步驟的四條指令。

> 📍 **1001**：院內主機原本**沒有 Git**，現場照上面裝了 x64 Setup，版本 `2.56.0.windows.1`。誰裝、資訊室是否同意沒有記到，下一次要補問。
> Docker 29.3.1（Client 與 Server 相同）、Compose v5.1.1，與 0922 相同。

> 🧪 **模擬部署**：開發機沒有的話自己裝，裝完**重新開機**再做一次本步驟。
> 1. **Git for Windows**：照上面的裝法。
> 2. **Docker Desktop**：到 `docker.com` 下載 Docker Desktop for Windows，安裝時勾「Use WSL 2」。
>    第一次開啟會要你接受使用條款；若提示要更新 WSL，照畫面指示在 PowerShell 打 `wsl --update`。
> 3. 開發機上已經有 Node.js 也沒關係，但**這一輪部署裡不准用到它**（驗收的 V-31 例外）。

---

### V-05 Docker Desktop 的設定與防毒排除（＝N-05、W-05）

**第一部分：Docker Desktop 的四項設定**

開 Docker Desktop → 右上角齒輪（Settings），逐項看。**同一台機器有別的專案在用時只看不改**，要改先知會資訊室。

| # | 位置 | 應該是 |
|---|---|---|
| 1 | General → Start Docker Desktop when you sign in | 勾 |
| 2 | General → Send usage statistics | 不勾（見下方說明） |
| 3 | Software updates → Automatically check for updates | 不勾（見下方說明） |
| 4 | Resources → Advanced → Disk image location | **把路徑抄下來**，第二部分要用 |

> **第 3 項找不到勾選框？** 這台的 Docker Desktop 是從 **Microsoft Store** 裝的，設定頁只會叫你去市集管理（第十冊 F-16，院內主機就是這種情形）。
> 更新是否自動發生，由**市集的自動更新設定**決定，而那管的是**整台主機的所有 App**，只能交給資訊室決定。
> 在演練紀錄寫下「更新由市集管理，現行設定＝＿＿」，問資訊室能不能改成手動；不行的話至少請他們避開透析時段。

> **第 2 項是開著的？** 院內主機 0922 就是開著的。它是**整台主機**的設定，同機另一個專案也受影響，~~**答覆前只看不改**~~（Q-27 第 9 題）。
> **1007 答覆可以關：第三次進院把它取消勾選**，按右下角的套用按鈕（依版本叫 **Apply** 或 **Apply & restart**；後者會讓 Docker Desktop 重新啟動、容器跟著中斷一下，挑沒有透析的時段做），演練紀錄寫「使用統計已關，＿＿月＿＿日」。
> 第 3 項（市集自動更新）**1007 答覆先不改**：照舊只看、記下現行設定。

**第二部分：防毒查哪一套、排除清單裡有什麼**（只看不改）

要請資訊室把第 4 項那個資料夾加入防毒的排除清單。開口之前先查清楚兩件事：

1. **主機上跑的是哪一套防毒**：

   ```powershell
   Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntivirusProduct |
     Select-Object displayName, productState, @{n='hex';e={'{0:X6}' -f $_.productState}}
   ```

   每一套防毒列成一行，看 `hex` 那一欄**中間兩碼**：`10` 或 `11` 是**正在運作**，排除要在這一套裡做；`00` 或 `01` 是裝了但沒在運作。
   例：`061100` 是正在運作，`060100` 是已關閉。

2. **排除清單裡有什麼**。正在運作的是 Windows Defender（`displayName` 為 `Windows Defender` 或 `Microsoft Defender Antivirus`）時，
   **用系統管理員身分開的 PowerShell**（開始選單對「Windows PowerShell」按右鍵 →「以系統管理員身分執行」）打：

   ```powershell
   Get-MpPreference | Select-Object -ExpandProperty ExclusionPath
   ```

   每一行是一個排除的路徑；**什麼都沒印出來**就是沒有任何排除。
   正在運作的是第三方防毒（趨勢、賽門鐵克等）時，PowerShell 看不到它的排除清單，直接問資訊室。

3. **對照**：清單裡有第 4 項的路徑或它的上層資料夾 → 已經排除；沒有 → 演練紀錄寫「防毒＝＿＿，排除清單未含 Docker 的資料夾」，交給資訊室加。

**怎麼知道成功了**：四項抄進演練紀錄；防毒是哪一套、排除清單有沒有那個資料夾，寫進演練紀錄；資訊室加完之後，再打一次第 2 條看得到它。

**可能怎麼壞**

| 症狀 | 處置 |
|---|---|
| 設定是灰的（院方鎖住） | 記下來，由資訊室決定 |
| 防毒第 1 條說 `Invalid namespace` | 這台是 Windows Server。改跑 `Get-MpComputerStatus`，看 `AMRunningMode` 與 `AntivirusEnabled` 兩欄；其他防毒問資訊室 |
| 防毒第 1 條什麼都沒印出來 | 沒有任何防毒向 Windows 登記。記下來，問資訊室是不是真的沒有防毒 |
| 防毒第 2 條印出 `N/A: Must be an administrator to view exclusions` | PowerShell 不是系統管理員身分，照上面的方式重開一個再打 |
| 防毒第 2 條出現 `0x800106ba` 之類的錯誤 | Defender 沒在運作，正在運作的是第三方防毒。回第 1 條確認 |

> 📍 **1001**：Windows Defender，`061100`（正在運作）；排除清單**是空的**——Docker 的資料夾沒有被排除。
> **加上排除之前，這台主機不得輸入真實病人資料**（總覽第 6 節：SQLite 被即時掃描鎖住的錯誤是間歇性的，會在一個月後才爆開）。

> 🧪 **模擬部署**：看一眼、抄下來即可，防毒排除不必做。想先熟悉指令可以在開發機上跑一次，同樣只看不改。

---

### V-06 確認連得出去，並先下載兩個基底映像（＝N-06、W-06）

建置時要從網路下載東西。先確認這些網站都連得到，免得建到一半才失敗。這一步分兩段：**Windows 連得到**，以及 **Docker 自己下載得到**。

**第一段：Windows 這一側**

```powershell
Test-NetConnection github.com -Port 22
Test-NetConnection github.com -Port 443
Test-NetConnection registry-1.docker.io -Port 443
Test-NetConnection auth.docker.io -Port 443
Test-NetConnection production.cloudflare.docker.com -Port 443
Test-NetConnection production.cloudfront.docker.com -Port 443
Test-NetConnection deb.debian.org -Port 80
Test-NetConnection registry.npmjs.org -Port 443
Test-NetConnection binaries.prisma.sh -Port 443
Test-NetConnection dl.google.com -Port 443
Test-NetConnection services.gradle.org -Port 443
Test-NetConnection maven.google.com -Port 443
```

最後三條是外殼的建置（V-21）要用的。

**第二段：Docker 這一側**——把 V-14、V-21 要用的兩個基底映像先下載下來：

```powershell
docker pull node:20-bookworm-slim
docker pull eclipse-temurin:17-jdk-jammy
```

`Test-NetConnection` 是 Windows 去查名稱、去連線；`docker pull` 是 **Docker Desktop 自己**去查、去下載，兩條路不一定同時通。
1001 就是 Windows 那一側沒測、Docker 那一側在 N-11 與 N-20 **三次查不到 Docker Hub 的網域**。這兩條先跑過，之後的建置不會半途卡在這裡，而且已下載的映像檔會直接沿用、建置也比較快。

**怎麼知道成功了**：第一段每一條最後都是 `TcpTestSucceeded : True`；第二段兩條最後都是 `Status: Downloaded newer image for …` 或 `Status: Image is up to date for …`。

**可能怎麼壞**

| 症狀 | 處置 |
|---|---|
| 22 是 `False`、443 是 `True` | 之後的部署金鑰改走 443，做法在 V-10 的出錯表 |
| 第一段出現 `Name resolution of … failed`（名稱查不到），其他都通 | 院內 DNS 查不到那個網域。試 `Resolve-DnsName <網域> -Server 8.8.8.8`，這樣查得到就是院內 DNS 的問題，請資訊室處理 |
| 第二段出現 `lookup <網域>: no such host`（網域是 `production.cloudfront.docker.com`、`auth.docker.io` 之類） | Docker 查不到 Docker Hub 的網域。依序：① 再打一次同一條；② `Resolve-DnsName <網域>`，Windows 查得到就重新啟動 Docker Desktop（工作列圖示按右鍵 → Restart）再打；③ Windows 也查不到，試 `Resolve-DnsName <網域> -Server 8.8.8.8`，這樣查得到就是院內 DNS 解析不了，請資訊室處理。**用了哪一個辦法才過，寫進演練紀錄** |
| 第二段的錯誤裡有一句 `Docker Desktop has no HTTPS proxy: connecting to … via direct connection` | 這一句只是說明「沒有設代理、直接連」，**不是錯誤本身**；錯誤在同一段最後的 `no such host` |
| 經代理伺服器，全部 `False` | 改用 `curl.exe -I https://registry.npmjs.org` 測；Docker 要在 Settings → Resources → Proxies 設代理 |
| 有幾個不通 | 請資訊室補齊再往下 |

> 📍 **1001**：第一段沒有記到結果；第二段當時還不是步驟。結果 Docker 在三個地方查不到名稱：
> N-11 用 `docker run node:20-bookworm-slim` 產生 `JWT_SECRET` 時，先是 `production.cloudfront.docker.com: no such host`、再打一次變成 `auth.docker.io: no such host`；
> N-20 建 `shell-builder` 時又是 `production.cloudfront.docker.com: no such host`，同一條指令再打一次就過了。所以是**時好時壞**，不是完全擋掉——上表的第 ① 項（再打一次）先做。
> Docker Hub 的兩個下載站（`cloudflare`、`cloudfront`）會擇一使用，**兩個都要通**。

> 🧪 **模擬部署**：開發機通常全部通，照做一次確認即可。

---

### V-07 確認三個連接埠沒人用（＝N-07、W-07）

**做什麼**

```powershell
Get-NetTCPConnection -State Listen | Where-Object LocalPort -in 13000,18080,18081 | Select-Object LocalPort, OwningProcess
```

**怎麼知道成功了**：**什麼都沒印出來**，代表三個埠都沒人在用。

**可能怎麼壞**：印出了某個埠 → 有別的程式在用它。實際部署：**先停手回報資訊室**，這三個埠是他們確認過的，不要自己換；模擬部署：自己換一個沒人用的。
**不要用 `-p` 之類的方式把埠對到別處**，埠只寫在 `.env` 裡。

> 📍 **1001**：三個埠都沒人用，服務啟動沒有撞埠。**1001 的服務還在跑的話，這三個埠會印出來，那是我們自己的**——0.5 節已經確認過就不必再做這一步。

> 🧪 **模擬部署**：三個埠記下來，V-12 填 `.env` 時要用。

---

## 3. 決定主機位址

### V-08 決定主機位址：護理站與平板用什麼連這台主機（新增）

`.env` 有三項要寫主機位址（`HD_PUBLIC_API_URL`、`CORS_ORIGINS`、`MDM_KIOSK_BASE_URL`），三項**寫同一個值**。
這個值本冊與子手冊一律寫成 `<主機>`。**它要在填 `.env` 之前定下來**，而且定了之後不要再換：平板的伺服器憑證就簽這個名字。

> ⚠️ **第十四冊之一的範例 `hd-server` 只是範例，不是要你填的值。** 1001 現場就問過「`hd-server` 要照寫嗎」。不要照抄任何範例。

**做什麼**

1. 在主機上看有哪些可以選：

   ```powershell
   hostname
   ipconfig /all
   ```

   | 看什麼 | 怎麼判斷 |
   |---|---|
   | `hostname` | 這台的電腦名稱。**只有院內 DNS 登記過這個名稱，別台機器才查得到** |
   | `ipconfig /all` 實體網卡（「乙太網路」或「Wi-Fi」）的 **IPv4 位址** | 候選的 IP。`vEthernet (WSL)`、`vEthernet (Default Switch)` 或 `172.` 開頭的是虛擬網卡，**不要選** |
   | 同一段的「DHCP 已啟用」 | `是` 表示這個 IP 可能會變。要用 IP，就要請資訊室把它固定下來。**1007 答覆院內主機的 IP 是固定的**；資訊室若是用 DHCP 保留固定的，這裡照樣顯示 `是`，不代表會變 |
   | 「主要 DNS 尾碼」 | 有的話，名稱有兩種寫法（例如 `<名稱>` 與 `<名稱>.<尾碼>`）。**只能選一種**，`CORS_ORIGINS` 要和護理站網址列上的寫法一字不差 |

2. **到護理站的電腦**上確認查得到（用名稱的話）：

   ```powershell
   Resolve-DnsName <名稱>
   ```

   查得到、而且對到主機那個 IP 才算。用 IP 的話跳過這一條。

3. 與資訊室確認：**平板的 Wi-Fi 網段也連得到同一個名稱或 IP**。平板常常查不到 Windows 的電腦名稱（院內 DNS 沒登記的話），**拿不準就用資訊室固定下來的 IP**。

**怎麼知道成功了**：一個值，資訊室點過頭；護理站查得到（用名稱時）。
演練紀錄寫「`<主機>` 用的是**名稱／IP**，由＿＿確認」——**值本身不寫進演練紀錄以外的任何文件**。

**真正的驗證在後面**：V-17 在護理站登入成功、V-25 平板開得到下載頁，這個值才算對。

**可能怎麼壞**

| 症狀 | 處置 |
|---|---|
| 護理站 `Resolve-DnsName` 說 `DNS name does not exist` | 這個名稱院內查不到。改用固定 IP，或請資訊室在 DNS 登記 |
| 資訊室說 IP 不能固定 | 用名稱，並請資訊室確認平板的網段查得到它 |
| 名稱與 IP 都不確定 | **停在這一步**。這個值填錯，之後每一台平板都要重新佈建 |

> 📍 **1001**：現場打了 `hostname`，自己決定了一個值，沒有資訊室的書面答案。當天沒有記是名稱還是 IP，1005 補記：**是名稱**（有沒有帶 DNS 尾碼未記）。
> 下一次照上面再確認一次；確認的結果是改用 IP 的話，照[第十五冊之四](15d-switch-host-to-ip.md)換。

> 🧪 **模擬部署**：`<主機>` 是開發機 **Wi-Fi 那張網卡的 IPv4 位址**（第十五冊之二 0.3 節），例如 `192.168.1.23`。
> 手機要連同一個 Wi-Fi；同一輪模擬部署之內不要換 Wi-Fi。

---

## 4. 取得程式碼

### V-09 建立資料夾，並設好「開工三行」（＝N-08、W-08）

**做什麼**

```powershell
$root = "C:\hd\hd-tablet-care"          # 🧪 模擬部署改成 C:\hd-sim
$cfg  = "$root\config\.env"
New-Item -ItemType Directory -Force "$root\config", "$root\backups" | Out-Null
Get-ChildItem $root
$cfg
```

前兩行設定兩個變數，本冊之後一直會用到：`$root` 是根目錄，`$cfg` 是 V-12 要建立的 `.env` 的位置。
本冊之後的 `docker compose` 指令都寫成 `--env-file $cfg`，而且都在 `$root\repo` 底下打。

**怎麼知道成功了**：列出 `backups`、`config` 兩個資料夾，最後一行印出 `C:\hd\hd-tablet-care\config\.env`（🧪 模擬部署是 `C:\hd-sim\config\.env`）。
`repo` 現在還沒有是對的，下一步 clone 才會產生；`.env` 也還沒有，V-12 才會建立。

**不可以放的地方**：OneDrive 之類的雲端同步資料夾、網路磁碟機、RAM 磁碟（院內主機有一顆 E 槽是 RAM 磁碟，第十冊 3.2 節）、
`C:\Users\<帳號>\` 底下的桌面／文件／下載。

> 📍 **1001**：根目錄是 `C:\hd\hd-tablet-care`。第十四冊寫的是 `D:\hd-tablet-care`，但院內主機的 D 槽 0922 時只剩約 4.6%（第十冊 3.2 節），
> C 槽空間充足、Docker 的虛擬磁碟也在 C 槽。**院方同不同意這個位置還沒有書面答覆**（V-02 第 5 題）。

> ⚠️ **開工三行**：PowerShell 關掉再開，`$root`、`$cfg` 就不見了。**之後每開一個新的 PowerShell 視窗，先輸入這三行**
> （第三行要等 V-11 clone 完才有那個資料夾）：
>
> ```powershell
> $root = "C:\hd\hd-tablet-care"          # 🧪 模擬部署改成 C:\hd-sim
> $cfg  = "$root\config\.env"
> cd $root\repo
> ```
>
> 看到 `couldn't find env file`，十次有九次是忘了這三行。

---

### V-10 產生本系統 repo 的部署金鑰（＝N-09、W-09）

這把金鑰讓這台機器可以從 GitHub **讀**本系統的程式碼，別的什麼都不能做。

**做什麼**

1. 產生金鑰。三行照抄，不用改任何字：

   ```powershell
   New-Item -ItemType Directory -Force $HOME\.ssh
   ssh-keygen -t ed25519 -C "hd-tablet-care@$(hostname)" -f $HOME\.ssh\hd-tablet-care -N '""'
   Get-Content $HOME\.ssh\hd-tablet-care.pub
   ```

   第一行是先建好 `.ssh` 資料夾：沒用過 SSH 的新帳號沒有這個資料夾，`ssh-keygen` 不會自己建。資料夾已經在的話，這一行什麼都不會動。
   `$(hostname)` 會自動換成這台機器的名字，只當註記用，讓管理者在 GitHub 上認得這把金鑰是哪台機器的。

2. 把印出來的那**一整行**（`ssh-ed25519 AAAA… hd-tablet-care@…`）交給 repo 管理者。
   管理者到 GitHub 的 `hd-tablet-care` repo → **Settings → Deploy keys → Add deploy key** 貼上，**不要勾 Allow write access**。
3. 開 SSH 的設定檔。兩行照抄：

   ```powershell
   if (-not (Test-Path $HOME\.ssh\config)) { New-Item -ItemType File $HOME\.ssh\config }
   notepad $HOME\.ssh\config
   ```

   第一行是先建好沒有副檔名的空檔：直接讓記事本建新檔，它會自作主張存成 `config.txt`，ssh 就讀不到。
   在檔案最後加上這一段，存檔關閉：

   ```
   Host github-hd-tablet-care
       HostName github.com
       User git
       IdentityFile ~/.ssh/hd-tablet-care
       IdentitiesOnly yes
   ```

**怎麼知道成功了**

```powershell
ssh -T github-hd-tablet-care
```

第一次會問 `Are you sure you want to continue connecting (yes/no)?`，核對顯示的指紋是 GitHub 公布的那一組再打 `yes`。
最後看到 `Hi 94sh09sh19sh/hd-tablet-care! You've successfully authenticated, but GitHub does not provide shell access.`

**可能怎麼壞**

| 症狀 | 處置 |
|---|---|
| `Permission denied (publickey)` | 公鑰還沒登記，或登記到別的 repo 去了 |
| `ssh-keygen` 找不到 | Windows 的 OpenSSH Client 選用功能沒裝。實際部署問資訊室；模擬部署到「設定 → 系統 → 選用功能」加裝 |
| `Saving key ... failed: No such file or directory`，接著 `Get-Content` 說 `.pub` 不存在 | 漏打了建立 `.ssh` 資料夾那一行。補打後重跑 `ssh-keygen` |
| 22 埠不通（V-06） | 設定檔那一段的 `HostName` 改成 `ssh.github.com`，並加一行 `    Port 443` |
| `Could not resolve hostname github-hd-tablet-care:` 後面接一串亂碼（那是 big5 的「無法辨別這台主機。」） | ssh 沒讀到設定檔，幾乎都是記事本存成了 `config.txt`。`Get-ChildItem $HOME\.ssh` 看得到 `config.txt` 就打 `Rename-Item $HOME\.ssh\config.txt config`，再重跑 `ssh -T` |

> 🧪 **模擬部署**：開發機上**另產生一把**，不要拿你平常推程式碼的那把 SSH 金鑰頂替——那樣走的就不是院內那條路。
> 登記時標題寫「模擬部署（開發機）」，之後可以一直留著重複使用。開發機的 `$HOME\.ssh\config` 裡已經有別的段落的話，加在最後面即可。

---

### V-11 clone 程式碼，切到 tag（＝N-10、W-10）

**做什麼**（`<tag>` 換成 V-03 確認過的那一個，例如 `v0.3.0`）

```powershell
git clone git@github-hd-tablet-care:94sh09sh19sh/hd-tablet-care.git $root\repo
cd $root\repo
git checkout <tag>
git describe --tags
```

**怎麼知道成功了**：最後一行印出的**正好是**那個 tag，後面沒有 `-3-g1a2b3c4` 這種尾巴。

**可能怎麼壞**

| 症狀 | 處置 |
|---|---|
| 一大段 `You are in 'detached HEAD' state…` | **正常**。部署本來就不在分支上 |
| `error: pathspec '<tag>' did not match` | tag 沒推上去，回 V-03 |
| `destination path … already exists` | 那個資料夾已經有東西。實際部署：**院內主機上這是 1001 clone 的那一份**，回 0.5 節，不要刪；模擬部署：上一輪沒撤除乾淨，照第 10.2 節撤除 |
| V-10 的 `ssh -T` 成功，`git clone` 卻出現 `Connection reset by … port 22` | 網路把連線切斷，不是金鑰的問題。`Test-Path $root\repo` 是 `True` 就先刪掉這次 clone 殘留的資料夾，再重跑；還是被切，就把 V-10 設定檔那一段改走 443，重跑 `ssh -T` 再 clone（見[第十一冊](11-compose.md)） |

> 📍 **1001**：`HEAD is now at 9992721 docs: 週報 0930 定版`，`git describe --tags` 印出 `v0.3.0`。

> 🧪 **模擬部署**：一定要從 GitHub **全新 clone** 到 `C:\hd-sim\repo`，不要複製你的工作目錄，也不要在工作目錄裡做。

---

## 5. 設定

### V-12 由範本填 `.env`（＝N-11、W-11、Y-03）

**做什麼**

```powershell
Copy-Item $root\repo\deploy\hospital.env.example $cfg
notepad $cfg
```

**逐項怎麼填，照另外兩冊**：

- 實際部署 → [第十五冊之一 · 實際部署的 `.env`](15a-env-hospital.md)
- 🧪 模擬部署 → [第十五冊之二 · 模擬部署的 `.env`](15b-env-simulation.md)

三個位址都寫 V-08 定下的 `<主機>`。外殼 App 那三項（`HD_SHELL_SRC_DIR`、`HD_SHELL_SIGNING`、`MDM_KIOSK_BASE_URL`）**現在就一起填好**，
雖然外殼第 8 節才做——每一條 `docker compose` 指令都會檢查它們。

`JWT_SECRET` 用 PowerShell 產生（子手冊有那一行），**不要用 `docker run node:…`**：1001 用那條，兩次都因為 Docker 查不到 Docker Hub 的網域而失敗（V-06 方框）。

**怎麼知道成功了**

```powershell
docker compose --env-file $cfg config --quiet
Select-String -Path $cfg -Pattern '^(HD_PUBLIC_API_URL|CORS_ORIGINS|MDM_KIOSK_BASE_URL)='
```

第一條**什麼都沒印出來**；第二條印出三行，**三行的主機部分都是 V-08 定的那一個**，前兩行是 `http://`、第三行是 `https://`。

**可能怎麼壞**

| 症狀 | 處置 |
|---|---|
| `required variable HD_… is missing a value: 請設定 …` | 冒號後面寫的就是還缺什麼，補上 |
| `couldn't find env file` | `$cfg` 沒設（V-09 的開工三行），或路徑打錯 |
| 第二條看到 `hd-server` | 那是舊版子手冊的範例，**照抄了**。換成 V-08 的值 |
| 實際部署，第二條看到 `localhost` | 護理站與平板連不到 `localhost`（那是它們自己）。換成 V-08 的值 |

> ⚠️ **不要拿 repo 根目錄的 `.env.example` 來填。** 那一份是日常開發（`npm run dev`）用的，變數名稱不同。
> 部署用的範本只有 `deploy\hospital.env.example` 這一份。

> 📍 **1001**：院內主機上已經有一份 `C:\hd\hd-tablet-care\config\.env`。下一次**不要再複製範本蓋掉它**，照第十五冊之一第 6 節核對。

---

### V-13 建立兩個資料卷（＝N-12、W-12）

**只在第一次部署時做。**

**做什麼**

```powershell
docker volume create hd-tablet-care-data
docker volume create hd-tablet-care-keys
docker volume ls
```

**怎麼知道成功了**：清單裡看得到這兩個名字。

> 🧪 **模擬部署**：做之前先 `docker volume ls` 看一眼，**清單裡不該已經有 `hd-tablet-care-` 開頭的**。
> 有的話是上一輪留下來的，照第 10.2 節撤除再回來，否則就不是「從零」。

---

## 6. 建置與啟動

### V-14 建置映像檔（＝N-13、W-13）

**做什麼**（**先記下開始時間**）

```powershell
docker compose --env-file $cfg build
```

第一次約十分鐘，畫面會一直捲動，是正常的。

**怎麼知道成功了**：最後出現 `Image hd-tablet-care:<tag> Built`；再打 `docker images hd-tablet-care` 看得到這個 tag。**記下結束時間**。

`HD_PUBLIC_API_URL` 就是在這一步寫進護理端網頁檔案的。**`.env` 的位址在這一步之前一定要是對的**，之後才改就要再 `build` 一次。

**可能怎麼壞**

| 症狀 | 處置 |
|---|---|
| `failed to resolve source metadata for docker.io/library/node`，後面有 `no such host` | Docker 查不到 Docker Hub 的網域，照 V-06 第二段那一列處理 |
| `npm error code ETIMEDOUT` 或 `ECONNRESET` | 網路不穩，再打一次同一條指令；已下載的部分會沿用 |
| `pull access denied for hd-tablet-care` | 打成 `up` 了。先 `build` |

> 📍 **1001**：建置成功，但耗時沒有記到。

---

### V-15 建立資料庫（＝N-14、W-14）

**做什麼**（一整行，不要斷開）

```powershell
docker compose --env-file $cfg run --rm --no-deps api node apps/api/scripts/prisma-cli.mjs migrate deploy --schema apps/api/prisma/schema.prisma
```

**怎麼知道成功了**：中間出現 `SQLite database hd.db created at file:/data/hd.db`（第一次才會有），最後一行 `All migrations have been successfully applied.`

**可能怎麼壞**：錯誤訊息裡提到 `binaries.prisma.sh` → 映像檔建壞了，回 V-14 重建。**不要為了讓它下載而開任何網路例外。**

---

### V-16 啟動（＝N-15、W-15）

**做什麼**

```powershell
docker compose --env-file $cfg up -d
docker compose --env-file $cfg ps
```

**怎麼知道成功了**：`api`、`nurse-web`、`patient-web` 三個的狀態都是 `Up`。
`ai-gateway` 與 `shell-builder` **不在清單上是對的**，它們平時不跑。

**可能怎麼壞**

| 症狀 | 處置 |
|---|---|
| `api` 一直是 `Restarting` | 設定被後端拒絕。`docker compose --env-file $cfg logs api --tail 30` 最後幾行會寫是哪一條，照訊息改 `.env` 再 `up -d` |
| `address already in use` | 埠被佔了，回 V-07 |
| `bind source path does not exist` | `HD_BACKUP_DIR` 或 `HD_CONFIG_DIR` 指的資料夾不存在，回 V-09 |

---

### V-17 確認它是對的，而且護理站登得進去（＝N-16、W-16）

這一步分四段，**照順序做**。1001 卡在這一步：登入 `Failed to fetch`，原因是第二段的 CORS 不放行（第十四冊之四 M-01）。

**第一段：後端活著**（在主機上打）

```powershell
curl.exe -s http://localhost:13000/api/health
docker compose --env-file $cfg logs api --tail 30
```

`13000` 是 `.env` 的 `HD_API_PORT`，**實際部署與模擬部署都是 `13000`**。第一條用 `localhost`，是在主機自己身上問、不經過網路與防火牆：
這一條不通，問題在服務本身；這一條通、後面不通，問題在位址或網路。

| 看什麼 | 應該是 |
|---|---|
| health | `{"status":"ok",…}` 開頭 |
| 日誌「已連線至 SQLite」那一行 | 有 `synchronous=FULL` |
| 日誌「版本標記」那一行 | 後面寫著 `（正式環境設定）`——模擬部署也是這樣，**這是對的** |
| 日誌「伺服器時區」 | `Asia/Taipei`，而且時間是現在 |

**第二段：網頁裡寫死的後端位址、後端的 CORS 都是對的**（在主機上打，不必開瀏覽器）

先看網頁會連哪裡：

```powershell
Select-String -Path $cfg -Pattern '^HD_PUBLIC_API_URL='
docker compose --env-file $cfg exec nurse-web grep -rhoE 'https?://[A-Za-z0-9.-]+:[0-9]+' apps/nurse-pwa/dist/assets
```

第二條印出的是**護理端網頁實際會去連的後端位址**（V-14 建置時寫進去的）。**兩條印出的位址要一模一樣**，例如都是 `http://<主機>:13000`。
不一樣的話，是先 `build`、之後才改了 `.env` 的位址。再建置一次：

```powershell
docker compose --env-file $cfg build
docker compose --env-file $cfg up -d
```

再看後端放不放行護理端（`<主機>` 換成 V-08 的值）：

```powershell
Select-String -Path $cfg -Pattern '^CORS_ORIGINS='
curl.exe -s -i -H "Origin: http://<主機>:18080" http://<主機>:13000/api/health | Select-String Access-Control-Allow-Origin
```

第一條要是 `CORS_ORIGINS=http://<主機>:18080`；第二條要印出 `Access-Control-Allow-Origin: http://<主機>:18080`。

第二條**什麼都沒印出來**，就是後端不放行護理端的來源，登入一定 `Failed to fetch`——**1001 就是這個結果**。
把第一條的值改對（或值是對的、只是改完還沒套用），然後 `docker compose --env-file $cfg up -d`，再打一次第二條。
`.env` 只在容器建立時讀一次，改完不 `up -d`，後端還在用舊的名單。

**第三段：在主機上用正確的網址登入**

主機的瀏覽器開 **`http://<主機>:18080`**——**不要用 `localhost`**。

> ⚠️ 實際部署用 `http://localhost:18080` 開，頁面出得來，**登入一定失敗**（`Failed to fetch`）：網址列的來源是 `localhost`，
> `CORS_ORIGINS` 寫的是 `<主機>`，後端不放行。這不是壞掉，是設計如此。1001 現場就先用 `localhost` 開過。

用 `.env` 的 `SUPER_ADMIN_WORK_ID` 與 `SUPER_ADMIN_INITIAL_PASSWORD` 登入，**被要求改密碼**。

**第四段：在護理站的電腦上登入**

在**護理站的電腦**開同一個網址 `http://<主機>:18080`，登入成功。**這一段才算數**：主機連自己不經過防火牆，在主機上登得進去，不代表護理站也登得進去。

**怎麼知道成功了**：四段都過。

**可能怎麼壞**

| 症狀 | 處置 |
|---|---|
| 頁面開得了，按登入出現 `Failed to fetch` | 照[附錄：護理端頁面開得起來卻登不進去](#附錄護理端頁面開得起來卻登不進去)逐步查 |
| 頁面開得了，出現 `工作ID 或密碼錯誤` | 有連到後端，帳號或密碼不對。第一個帳號**只在資料庫還沒有任何使用者時建立**，事後改 `.env` 不會改到已建立的帳號 |
| 沒有帳號可以登入 | `SUPER_ADMIN_*` 沒填。補上再 `up -d`，**資料庫不必重建** |
| 護理站的電腦開不到頁面，主機自己開得到 | 防火牆或網段，找資訊室（Q-27）。**不要自己關防火牆** |
| 護理站的電腦連頁面都說找不到主機 | `<主機>` 是名稱而護理站查不到，回 V-08；決定改用 IP 就照[第十五冊之四](15d-switch-host-to-ip.md) |

> 改完密碼之後，實際部署要把新密碼交給院方指定的人保管，`.env` 裡的初始密碼可以清空（清空後 `up -d`）。

> 📍 **1001**：第一段 health 正常；登入出現 `Failed to fetch`。現場查到「放不放行護理端」那一條**印出空的**——後端不放行護理端的來源，離院時未解。
> 下一次從第二段開始（0.5 節）：先看 `CORS_ORIGINS` 寫了什麼、改對後 `up -d`，再確認網頁裡的後端位址與瀏覽器網址列。

> 🧪 **模擬部署**：`<主機>` 是開發機的區網 IP，開 `http://<開發機區網 IP>:18080`。
> 登入成功之後，**故意用 `http://localhost:18080` 再開一次、按登入**，親眼看一次 `Failed to fetch` 長什麼樣——這就是院內用錯網址時會看到的。
> 看完關掉，回到用區網 IP 開的那一頁。第四段改成用手機的瀏覽器開同一個網址（要連同一個 Wi-Fi）；開不到時照 V-25 方框處理防火牆。

---

## 7. 備份與重新開機

### V-18 備份一次，並證明還原得回來（＝N-17、W-17）

「有備份」和「備份能用」是兩件事。

**做什麼**

1. 護理端 → **系統管理** → 「立即備份」，記下畫面上的檔名。
   備份歷程的 SHA-256 只顯示前 12 碼；完整的 64 碼到備份資料夾讀同名的 `.sha256` 檔：

   ```powershell
   Get-Content "$root\backups\<檔名>.sha256"
   ```

   前半段就是雜湊。護理端 **稽核軌跡**（動作選「資料庫線上備份」）的說明欄也有完整的一份。
2. 把它還原到一個測試檔，確認完整，再刪掉測試檔（`<檔名>`、`<雜湊>` 換成剛剛記下的）：

   ```powershell
   docker compose --env-file $cfg run --rm --no-deps api node_modules/.bin/ts-node --project apps/api/tsconfig.json apps/api/scripts/restore-backup.ts --from /backups/<檔名> --to /data/restore-check.db --sha256 <雜湊>
   docker compose --env-file $cfg run --rm --no-deps --entrypoint rm api /data/restore-check.db
   ```

**怎麼知道成功了**：輸出有 `✓ 與備份歷程上的紀錄相符` 與 `完整性檢查：ok`；`$root\backups\` 裡看得到那個檔和同名的 `.sha256`。

> 💡 **服務起不來時**：備份歷程與稽核軌跡都存在資料庫裡，打不開網頁就看不到。這時直接看資料夾：
> `Get-ChildItem "$root\backups\*.db" | Sort-Object LastWriteTime` 最後一個是最新的備份，雜湊在它旁邊的 `.sha256`。
> 送往院內另一台機器時，`.sha256` 要跟著一起送。

實際部署還要**當場問清楚**：備份資料夾的內容由誰、多久送往院內另一台機器一次？答不出來就寫進交接文件的「已知限制」。

> ⚠️ **這一步一律用 PowerShell。** 在 Git Bash 裡打，`/backups/…` 會被自動改寫成 Windows 路徑，還原腳本就說找不到檔案。

> 📍 **1001**：未測。

> 🧪 **模擬部署**：做到還原成功即可，不必送往任何地方。

---

### V-19 重新開機測試（＝N-18、W-18）

`restart: unless-stopped` 只管 Docker 起來之後；Docker Desktop 要有人登入 Windows 才會啟動。**這一條決定這條路線在院內能不能用。**

**做什麼**：重新開機 → **以 Administrator 登入**（1007 答覆：斷電後由護理長重新登入，不設自動登入；這一步就是在模擬護理長）→ **之後什麼都不碰**，等三分鐘 → 開一個新的 PowerShell，先輸入開工三行，再：

```powershell
docker compose --env-file $cfg ps
curl.exe -s http://localhost:13000/api/health
```

**怎麼知道成功了**：三個服務自己回到 `Up`、health 正常，**登入之後沒有人手動開 Docker Desktop**。

**過了之後**：交接文件寫一段給護理長看的「斷電之後」——護理端每個畫面閃紅框、平板顯示請按床邊呼叫鈴 → 到主機開機、以 Administrator 登入 → 什麼都不碰，等三分鐘 → 護理端紅框消失就好了。

**沒過的話**：記下實況（Docker Desktop 有沒有隨登入起來、V-05 第 1 項有沒有勾），寫進交接文件，**不要在現場自己改院方的登入設定**。

> ⚠️ 主機上還有另一個專案的容器在跑。重新開機會一起中斷它，**先問資訊室可不可以、挑什麼時候**。

> 📍 **1001**：未測。0.5 節的檢查若發現服務沒有自己回來，那就已經是這一步的答案了。

> 🧪 **模擬部署**：可以跳過。開發機是你自己登入的，驗不出院內「沒人登入」的情形。

---

## 8. 外殼 App 與平板

這一節做兩件事：在主機上把外殼 App（APK）建出來，然後讓平板從院內的下載頁安裝、釘住。
**私鑰全程不離開主機**，平板也不必接電腦。

### V-20 外殼 repo 的部署金鑰與 clone（＝N-19、Y-02）

外殼 App 在另一個 repo（`hd-kiosk-shell`），要**另一把**部署金鑰——一把部署金鑰只能給一個 repo。

**做什麼**

1. 產生並交出公鑰，登記到**外殼 repo** 的 Settings → Deploy keys，不勾 Allow write access：

   ```powershell
   ssh-keygen -t ed25519 -C "hd-kiosk-shell@$(hostname)" -f $HOME\.ssh\hd-kiosk-shell -N '""'
   Get-Content $HOME\.ssh\hd-kiosk-shell.pub
   ```

2. `notepad $HOME\.ssh\config`（V-10 已經建好這個檔，直接開就好），在最後再加一段：

   ```
   Host github-hd-kiosk-shell
       HostName github.com
       User git
       IdentityFile ~/.ssh/hd-kiosk-shell
       IdentitiesOnly yes
   ```

3. 確認並 clone（**不必切 tag**，`shell-builder` 會自己取出要的那一版）：

   ```powershell
   ssh -T github-hd-kiosk-shell
   git clone git@github-hd-kiosk-shell:94sh09sh19sh/hd-kiosk-shell.git $root\hd-kiosk-shell
   git -C $root\hd-kiosk-shell tag
   ```

**怎麼知道成功了**：`ssh -T` 印出 `Hi 94sh09sh19sh/hd-kiosk-shell!…`（**是 `hd-kiosk-shell`，不是 `hd-tablet-care`**）；`git tag` 列得出 V-03 看到的那一版。
`git tag` 會把外殼 repo 的**每一個** tag 都列出來，連以前的版本也在（1001 是 `v0.2.0`、`v0.3.0` 兩行）——**這是對的**，`shell-builder` 只取 `shell.pin` 釘住的那一個。

| 症狀 | 處置 |
|---|---|
| `ssh -T` 印出的是 `hd-tablet-care` | 設定檔兩段的 `IdentityFile` 寫反，或少了 `IdentitiesOnly yes` |
| `Permission denied (publickey)` | 公鑰登記到本系統的 repo 去了 |
| `ssh -T` 成功，`git clone` 卻出現 `Connection reset by … port 22` | 網路把連線切斷。刪掉殘留的資料夾再重跑；還是被切，這一段改走 443（同 V-10） |

> 🧪 **模擬部署**：與 V-10 相同，開發機上另產生一把、標題註明模擬部署。

---

### V-21 建 `shell-builder` 的映像檔（＝N-20、Y-04）

**做什麼**（**先記下開始時間**）

```powershell
docker compose --env-file $cfg --profile shell build shell-builder
```

第一次要下載 Android SDK 與 Gradle，約 1.5 GB。**這一步要連外，而且很久**。V-06 已經先下載了 `eclipse-temurin:17-jdk-jammy`，這一步會直接沿用。

**怎麼知道成功了**：最後幾行有「✓ 外殼 v0.x.x（…，契約第 1 版）已準備好，相依已下載」（`v0.x.x` 是 `shell.pin` 釘的那一版）。**記下結束時間**。

| 症狀 | 處置 |
|---|---|
| `failed to resolve source metadata for docker.io/library/eclipse-temurin`，後面有 `lookup production.cloudfront.docker.com: no such host` | Docker 查不到 Docker Hub 的下載站，照 V-06 第二段那一列處理。單獨測這一段：`docker pull eclipse-temurin:17-jdk-jammy` |
| `外殼 repo 的 clone 裡沒有 tag vX.Y.Z` | `git -C $root\hd-kiosk-shell fetch --tags`，再建一次 |
| 提到版本、契約版本不符，或「外殼原始碼裡有指向院外的網址」 | **開發端的問題，不在現場修。** 停手，回開發端 |
| `dl.google.com`、`services.gradle.org`、`maven.google.com` 逾時 | 對外連線被擋，請資訊室開通（Q-32） |
| 停在 `gradle.zip` 很久 | 它會自己重試、失敗會自己結束。結束後再打一次同一條，已完成的部分不會重下載 |

> 📍 **1001**：遇到上表第一列，**同一條指令再打一次就過了**。這一步含出錯與重來，**院內實測 27～33 分鐘**。

---

### V-22 建 APK（第一次會產生金鑰）（＝N-21、Y-05）

**做什麼**

```powershell
docker compose --env-file $cfg --profile shell run --rm shell-builder
```

**怎麼知道成功了**：第一次會印出「這一次新產生：院內 CA 伺服器憑證（<主機>） APK 簽章金鑰（…）」，
接著是 APK 檔名與**三個 SHA-256**（檔案、簽章憑證、院內 CA）。**把三個 SHA-256 抄下來**，實際部署要寫進交接文件。

括號裡的 `<主機>` 要是 V-08 定的那一個——伺服器憑證就簽這個名字。

**再打一次同一條指令**，這次要看到「**金鑰全部沿用，這一次沒有產生任何新的金鑰**」，而且簽章憑證的 SHA-256 與第一次相同。

> 💡 **沒抄到也查得到，不必重跑。** 瀏覽器開 `http://localhost:18081/shell/`，下載頁最下面「版本資訊」列著三個 SHA-256（同一個資料夾的 `shell.json` 也有）。
> 每跑一次建置，下載頁上的 APK 就會換成新的一份，所以**交接文件的檔案 SHA-256 以下載頁上的為準**。
> `shell-builder keys-info` 只列得出院內 CA 與簽章金鑰的指紋，而且是大寫、以冒號分隔，對照時去掉冒號、大小寫不計。

| 症狀 | 處置 |
|---|---|
| `MDM_KIOSK_BASE_URL 要以 https:// 開頭` | `.env` 改成 `https://`，見子手冊 |
| `這個金鑰資料卷是「dev」用的，設定卻是「hospital」` | **停手。** 院內主機上出現了開發用的金鑰，或 `.env` 抄了開發機那一份 |
| `有 CA 憑證卻沒有私鑰` 之類 | 資料卷不完整。**不要刪掉重來**，照第十二冊第 6 節從備份還原 |

> 📍 **1001**：做了，三個 SHA-256 沒有抄。下一次從下載頁抄。

> 🧪 **模擬部署**：第一次那行會寫「APK 簽章金鑰（開發用）」，是對的。

---

### V-23 備份金鑰，並核對還原得回來（＝N-22、Y-06）

**做什麼**

```powershell
docker compose --env-file $cfg --profile shell run --rm shell-builder keys-backup
docker compose --env-file $cfg --profile shell run --rm shell-builder keys-verify
```

**怎麼知道成功了**：第一條印出「已備份：備份目錄/keys/hd-keys-<時間>.tar.gz」；第二條每一項都 ✓，最後「還原得回來」。

> 📍 **1001**：`keys-verify` 印出 `ca/ca.key`、`ca/ca.crt`、`signing/shell-signing.p12`、`signing/keystore.pass`、
> 「備份裡的簽章金鑰以備份裡的密碼打得開」「備份裡的 CA 私鑰完整」，最後「`hd-keys-20261001-173347.tar.gz` 還原得回來」，全部 ✓。

> ⚠️ **這份檔案裡有私鑰。** 實際部署：與資料庫備份一樣由院方送往院內另一台機器，**不得出院、不得寄給開發端**。
> 金鑰遺失的後果是**每一台平板都要解除安裝重裝**。

---

### V-24 讓病人端改走 HTTPS（＝N-23、Y-07）

**做什麼**

```powershell
docker compose --env-file $cfg restart patient-web
docker compose --env-file $cfg logs patient-web --tail 5
```

**怎麼知道成功了**：日誌**最後一次**出現的「靜態資源已提供於連接埠 8081」那一行，後面是「（HTTPS；HTTP 只留外殼下載頁）」。
主機的瀏覽器開 `http://localhost:18081/shell/` 看得到下載頁；開 `http://localhost:18081/` 會被轉到 `https://` 並跳出憑證警告——
**這是對的**：主機的瀏覽器不認得院內 CA，只有平板上的外殼 App 認得。

日誌裡兩個常讓人愣一下的地方，**都是正常的**（1001 兩個都遇到了）：

- **「找不到伺服器憑證」和「HTTPS」同時出現**：`--tail 5` 取最後 5 行，常常跨到重新啟動**之前**那一次的輸出。以**最後一次**啟動的那幾行為準。
- **寫的是 `8081` 和 `http://api:3000`，不是 `18081`、`13000`**：這兩個是**容器裡面**的埠。主機的 `18081` 轉進容器的 8081；
  `api:3000` 是 `patient-web` 經容器之間的網路找後端的位址，不經過主機。瀏覽器和平板一律連 `18081`。

| 症狀 | 處置 |
|---|---|
| **最後一次**啟動的日誌是「找不到伺服器憑證…暫以 HTTP 提供」 | V-22 還沒成功，或做完沒重新啟動 `patient-web` |

---

### V-25 平板連得到主機（＝N-24、Y-08）

**做什麼**：拿一台平板（或手機）連上**與平板實際使用時相同的 Wi-Fi**，用瀏覽器開 `http://<主機>:18081/shell/`。

**怎麼知道成功了**：看得到下載頁。**這也是 V-08 那個 `<主機>` 對平板來說對不對的驗證。**

| 症狀 | 處置 |
|---|---|
| 主機自己開得到，平板開不到 | Windows 防火牆擋了連入，或那個 Wi-Fi 網段到不了主機。**找資訊室**，不要自己關防火牆 |
| 平板說找不到這個主機 | `<主機>` 是名稱而平板查不到。這時要回 V-08 換成固定 IP——**而那代表 V-22 的伺服器憑證要重簽**，照[第十五冊之四](15d-switch-host-to-ip.md)一步步換 |

> 📍 **1001**：未測。

> 🧪 **模擬部署**：手機和開發機要連**同一個 Wi-Fi**，位址是開發機的區網 IP。手機開不到時：
> 1. Windows「設定 → 網路和網際網路 → Wi-Fi → 這個網路的內容」，網路設定檔類型改成**私人**。
> 2. 仍不行的話，用**系統管理員身分**開 PowerShell，只對私人網路開放病人端那一個埠：
>    ```powershell
>    New-NetFirewallRule -DisplayName "hd-sim patient 18081" -Direction Inbound -Protocol TCP -LocalPort 18081 -Profile Private -Action Allow
>    ```
>    撤除時（第 10.2 節）記得刪掉這條規則。V-17 第四段要用手機開護理端的話，`18080`、`13000` 照樣各加一條（名稱也用 `hd-sim` 開頭）。
> 3. 學校或公司的 Wi-Fi 常常擋裝置互連，改用手機熱點或家裡的 Wi-Fi。

---

### V-26 在護理端註冊平板（＝N-25、Y-09）

**做什麼**：護理端 → **新增裝置**（1007 以前叫裝置管理） → **註冊新平板**。畫面會出現一個**佈建 QR code** 與一行文字網址。

> ⚠️ **這兩樣只顯示一次。** 這個畫面先不要關，拿著平板做完 V-27、V-28 再離開。

**怎麼知道成功了**：畫面上的網址以 `https://<主機>:18081` 開頭。不是 `https://` 的話，`.env` 的 `MDM_KIOSK_BASE_URL` 還是 `http://`，改好後 `up -d api` 再重新註冊。

---

### V-27 平板的系統設定並安裝 App（＝N-26、Y-10、Y-11）

**做什麼**

1. 平板設定裝置 PIN，關閉「新增使用者」。
2. 設定 → 安全性 → **螢幕固定**：開啟，並勾選「解除固定前要求 PIN」。（各廠牌位置略有不同，可在設定裡搜尋「固定」）
3. 平板的瀏覽器開 `http://<主機>:18081/shell/`，按「下載 App」，安裝。系統問是否允許瀏覽器安裝不明來源的應用程式時，允許。

**怎麼知道成功了**：平板上多了「透析照護平板」這個 App。

| 症狀 | 處置 |
|---|---|
| 「套件與現有套件衝突」 | 這台裝過**另一把金鑰簽的版本**（例如模擬部署時裝的開發版）。先解除安裝再裝 |
| 「應用程式未安裝」，而且沒裝過 | 下載不完整，重新下載一次 |

---

### V-28 第一次開啟並釘住（＝N-27、Y-12、Y-13）

**做什麼**

1. 開啟「透析照護平板」→ 按「**掃描 QR code**」→ 允許相機 → 對準 V-26 畫面上的 QR code。三欄會自動填好，**核對序號與這台平板的標籤一致**。
   （沒有相機時手動填：主機位址填 `MDM_KIOSK_BASE_URL` 的值，序號與金鑰照 V-26 畫面上的）
2. 按「儲存並啟動」→ 系統問「要固定這個應用程式嗎」→ 按「確定」。
3. 回到護理端 → 新增裝置，等 15～30 秒。
4. 在平板上**解除一次固定**（輸入 PIN），30 秒內護理端要變成「已跳出」。
5. 釘回去：解鎖後 App 還停在畫面上，但已經沒有釘住，直接點它沒用。按多工鍵把「透析照護平板」**從多工畫面滑掉**，
   再從桌面開啟 → 系統再問一次「要固定這個應用程式嗎」→ 按「確定」。護理端 15～30 秒內回到「固定中」。
   （沒跳出確認框就重新開機，App 開機後會自己起來並詢問）

**怎麼知道成功了**

| 在哪裡看 | 應該是 |
|---|---|
| 平板 | 病人端的等待畫面，**沒有任何憑證警告**；按上一頁、首頁、多工鍵都離不開 |
| 護理端「固定狀態」 | 固定中（解除時變成已跳出） |
| 護理端「外殼版本」 | 版本正常，底下有版本號 |

**把序號與床號的對應記下來。** 實際部署首波只佈建實際會用到的兩三台（DEP-36），每台做一次 V-26～V-28。

| 症狀 | 處置 |
|---|---|
| 「主機位址不是 https:// 開頭」 | 回 V-26 的處置 |
| 一片空白或「網頁無法使用」 | 位址錯或 V-24 沒做。平板「設定 → 應用程式 → 透析照護平板 → 儲存空間 → 清除資料」，重新佈建 |
| 上方出現琥珀色「……版本不相容」 | 下載頁的 APK 與系統版本對不上，見第十二冊第 5 節 |

> 🧪 **模擬部署**：用開發用的 Android 手機代替平板。做完之後手機上的 App 要**解除安裝**，
> 免得日後拿這支手機裝院內版時衝突（V-27 的第一列）。

---

## 9. AI 閘道：讓它就位

首波 AI 功能是關的（DEP-29）。這一節只讓閘道就位、確認它清楚回報「設定還沒填」，**不接任何模型**。

### V-29 放 AI 閘道的設定檔（＝N-28、Z-20）

**做什麼**

```powershell
New-Item -ItemType Directory -Force $root\config\ai-gateway | Out-Null
Copy-Item services\ai-gateway\config.hospital.example.yaml $root\config\ai-gateway\config.yaml
```

範本的 `base_url` 與 `model` 刻意留空，**保持空白**。**絕對不要填實驗室的位址**——那是把資料往院外送。

> 📍 **1001**：做了沒有，沒記到。`Test-Path $root\config\ai-gateway\config.yaml` 是 `True` 就是做過了，**不要再複製一次蓋掉它**。

---

### V-30 建置並啟動閘道（＝N-29、Z-21、Z-22）

**做什麼**

```powershell
docker compose --env-file $cfg --profile ai build ai-gateway
docker compose --env-file $cfg --profile ai up -d ai-gateway
docker compose --env-file $cfg exec -T api node -e "fetch('http://ai-gateway:8000/health').then(async r=>console.log(r.status, await r.text()))"
```

**怎麼知道成功了**：建置最後印出 `全部通過`；最後一條印出

```
503 {"status":"error","config":"error","detail":"base_url 尚未填寫（推論端點的位址）"}
```

**503 在這裡是正確的**：閘道在、後端連得到它、它清楚說出還缺什麼。

| 症狀 | 處置 |
|---|---|
| `fetch failed` | 閘道沒起來，`docker compose --env-file $cfg --profile ai logs ai-gateway` |
| `找不到設定檔` | V-29 的路徑不對，必須是 `config\ai-gateway\config.yaml` |
| 建置時 `no such host` | 同 V-06 第二段那一列 |

> ⚠️ 閘道起過之後，**日後更新時 `build` 與 `up -d` 都要加 `--profile ai`**，閘道才會跟著換新版。
> 接上正式 GPU API 是 Q-07 有答案之後的事，見[第十三冊](13-ai-gateway.md) Z-23。

---

## 9.5 院方 API：探測一次（1005 新增）

1005 起院方透析清單 API 要取代護理師的手動輸入（《[實作規格書](../requirements/implementation-spec.md)》4.13）。
**這一次只探測、不啟用**：看主機連不連得到、回應長什麼樣（透析中的結束欄位、床位格式、姓名欄），把輸出帶回來。
啟用（`.env` 填位址）要等探測結果看過、Q-35 報備過，見第 11 節。

### V-30a 探測院方透析清單 API（新增，第十五冊之三 E-16）

**做什麼**（在 `$root\repo` 底下；位址向資訊室或護理長問，**只在這裡當場輸入，不要寫進 `.env`、不要貼進任何紀錄**）：

```powershell
$u = Read-Host '院方透析清單 API 的位址（含 dialysislist.php，不含 ?date=）'
docker compose --env-file $cfg exec -T -e HOSPITAL_API_BASE_URL=$u api node apps/api/dist/hospital-api-probe.js
```

**怎麼知道成功了**：印出「連線：成功」、「解析：成功」，接著是每一欄的型態分布與幾段統計，最後一行「以上可以整段抄進演練紀錄」。
**整段抄進演練紀錄**——工具只印結構（型態、欄數、筆數、床位的樣式），**不印任何一個病人的值，也不印位址**，抄下來不會帶出病人資料。

| 症狀 | 處置 |
|---|---|
| `連線：失敗——找不到院方主機` 或 `連不到院方主機所在的網段` | 主機與院方 API 不在同一個網段，或名稱查不到。抄下來，回去問資訊室（Q-35）；**不要改主機的網路設定** |
| `連線：失敗——連線被拒` | 位址的埠不對，或院方服務沒開。核對位址再試一次 |
| `連線：失敗——逾時` | 院方伺服器沒有在 30 秒內回應。換個時間再試一次，兩次都逾時就抄下來 |
| `解析：失敗` | 位址打到的不是透析清單（例如少了檔名）。核對位址 |
| `模擬標頭：有` | 打到的是模擬院方 API，不是院方的——位址填錯了 |
| `沒有設定院方 API 的位址` | `Read-Host` 那一行沒有輸入東西 |

> ⚠️ **不要用瀏覽器或 `curl` 直接打院方 API**：回應是全中心病人的姓名與病歷號，會整片印在螢幕上（第十五冊之三 E-16）。

> 🧪 **模擬部署**：先照[第十五冊之二](15b-env-simulation.md) 1.9 把 `.env` 指向模擬院方 API、寫上 `HD_SIMULATION_DEPLOYMENT=yes`，然後
>
> ```powershell
> docker compose --env-file $cfg --profile simulation up -d
> docker compose --env-file $cfg exec -T api node apps/api/dist/hospital-api-probe.js
> ```
>
> 第二行用的是 `.env` 裡的位址，所以不必輸入。印出「模擬標頭：有」是對的。接著開護理端簡易版：
> 不必碰任何東西，床位圖上就會出現 A1、A2… 與「模擬甲」等病人（全是虛構的）。
> 最後驗「院內的設定擋得住模擬」（部署規範第 9 章第 8 項）：把 `.env` 的 `HD_SIMULATION_DEPLOYMENT` 清空，`docker compose --env-file $cfg up -d api`，
> `docker compose --env-file $cfg logs --tail 20 api` 要看到**拒絕啟動、指出 DEP-46**；看到之後改回 `yes`、再 `up -d api`。

---

## 10. 收尾

### 10.1 實際部署：冒煙測試與交接

| 步驟 | 做什麼 | 詳細在 |
|---|---|---|
| 冒煙測試 | 在護理站的電腦走一次主線：登入 → 建病人 → 建排班 → 指派平板 → 解除綁定 → 稽核查得到。**測試資料用虛構的**，交接時說明哪幾筆是測試資料、誰負責清掉 | [第四冊](04-onsite.md) H-16 |
| 總覽螢幕 | 在指定位置開啟護理端總覽，確認不會休眠 | 第四冊 H-18 |
| 現場教學 | 護理長、值班護理師、資訊室各教一次，**講完當場讓對方自己做一次** | 第四冊 H-20 |
| 交接文件 | 見下表 | 第四冊 H-21 |
| 當天晚上 | 把演練紀錄補完；**每一步的時間都要有** | 第四冊 H-24 |

交接文件至少要有（第一行寫「**首波試用、不是全單位上線**」）：

| 項次 | 內容 |
|---|---|
| 位置 | `C:\hd\hd-tablet-care` 底下四個資料夾各放什麼；兩個資料卷的名字 |
| 版本 | 部署的 tag；外殼版本 |
| 連接埠 | 三個埠與登記狀況 |
| 位址 | 護理站開哪個網址（`http://<主機>:18080`）；**不要用 `localhost` 開**，會登不進去 |
| 帳號 | 初始管理員的工作 ID（**密碼由院方自行保管**） |
| 啟停 | `docker compose --env-file <設定目錄>\.env stop`／`up -d`，在 `repo` 資料夾底下打 |
| 備份 | 每日幾點、落在哪、誰送往另一台機器 |
| 外殼 | V-22 的三個 SHA-256；金鑰備份的檔名 |
| 防毒 | 排除清單加了沒有、誰加的 |
| 信任邊界 | 能登入這台主機的人一律可信任（DEP-38）；日後帳號政策改變要重新評估 |
| 已知限制 | AI 關閉、V-19 若沒過的實況、尚未佈建的平板、1001 現場裝的 Git 是否走過變更流程、Docker 查 Docker Hub 網域時好時壞（日後更新會再遇到） |
| 聯絡方式 | 出事找誰 |

### 10.2 🧪 模擬部署：驗收，然後撤除乾淨

#### V-31 跑三支驗收（＝N-30、第十一冊第 7 節、第十二冊第 7 節）

**這一步是驗收，不是部署步驟**，也是整輪裡唯一准用 Node.js 的地方。
在**平常開發的工作目錄**（不是 `C:\hd-sim\repo`）打：

```powershell
npm run verify:iteration11 -- --live --env-file C:\hd-sim\config\.env
npm run verify:iteration12 -- --live --env-file C:\hd-sim\config\.env
npm run verify:iteration13 -- --live --env-file C:\hd-sim\config\.env
```

**怎麼知道成功了**：三支都全部 ✓。第一支會執行 `down -v` 再 `up -d`，驗證「資料卷不會被 `-v` 刪掉」，**這是刻意的**。

然後依第十一冊第 7 節，再各走一次**更新**（W-19，打一個測試 tag）與**回退**（W-20）。每一步的結果填進《[部署演練紀錄](../notes/deployment-drills.md)》。

#### V-32 撤除（＝N-31）

模擬部署做完**一定要撤除**，下一輪才又是從零；也免得開發機上一直有三個服務佔著埠。

```powershell
cd C:\hd-sim\repo
docker compose --env-file C:\hd-sim\config\.env --profile ai --profile shell down
docker volume rm hd-tablet-care-data hd-tablet-care-keys
docker images "hd-tablet-care*"
```

最後一條列出的映像檔，逐一 `docker rmi <名稱>:<tag>` 刪掉。接著：

```powershell
cd C:\
Remove-Item -Recurse -Force C:\hd-sim
Get-NetFirewallRule -DisplayName "hd-sim *" -ErrorAction SilentlyContinue | Remove-NetFirewallRule
```

（最後一條只有 V-25 真的加過防火牆規則時才會刪到東西，要用系統管理員身分打。）
手機上的「透析照護平板」解除安裝。部署金鑰與 `$HOME\.ssh\config` 那兩段**可以留著**，下一輪繼續用。
V-06 下載的兩個基底映像也可以留著。

**怎麼知道成功了**：`docker volume ls` 與 `docker images` 都看不到 `hd-tablet-care` 開頭的東西；`C:\hd-sim` 不存在。

> ⚠️ **撤除只准在模擬部署做。** 實際部署的撤除會刪掉整個透析中心的紀錄，要院方書面同意，照[第八冊](08-shutdown.md)與第十一冊第 8 節。

---

## 11. 之後的日常

| 要做什麼 | 照哪裡 |
|---|---|
| 換新版（更新） | [第十一冊](11-compose.md) W-19。排在非透析時段，更新後第一個班次要有人在。**更新前先照 V-06 第二段下載一次基底映像** |
| 新版有問題，退回上一版 | 第十一冊 W-20。**更新後寫進去的資料會一起消失**，要在累積新資料之前決定 |
| 暫停或停用服務 | 第十一冊第 8 節 |
| 換外殼版本、調高最低可用版本 | [第十二冊](12-shell.md) Y-14、Y-15 |
| 每年核對金鑰備份 | 第十二冊第 6 節 |
| 接上正式 GPU API | [第十三冊](13-ai-gateway.md) Z-23 |
| 接上院方 API（V-30a 探測過、Q-35 報備過之後） | 設定目錄的 `.env` 填 `HOSPITAL_API_BASE_URL`（[第十五冊之一](15a-env-hospital.md) 1.10），`docker compose --env-file $cfg up -d api`；護理端「系統管理 → 營運參數與選項清單」的「院方資料同步」卡片看到「成功」才算接上。**接上之後**，1005 之前預設的 01～15 床到同一頁的床位清單拿掉 |
| 出錯了，這本沒寫到 | 第十一冊第 9 節、第十二冊第 8 節、第十三冊第 6 節、[第六冊](06-troubleshooting.md) |

---

## 12. 什麼時候當場停手

下列任一種出現，**停手、記錄、擇日**。硬幹的代價比重來高得多（詳見[總覽](index.md)第 6 節）：

- 有人說「把網路開一下就好了」「手動開個容器比較快」「把整顆磁碟掛進去」
- 資料庫只能放在雲端同步資料夾或人人讀得到的共用資料夾
- 防毒排除當天加不了，有人說「先跑跑看」
- V-08 的主機位址沒有人能確認
- V-22 出現「這個金鑰資料卷是『dev』用的」
- 冒煙測試沒過，但已經到了下班時間

停手時做三件事：`docker compose --env-file $cfg stop` 把服務停掉、把現況寫進演練紀錄、當場講清楚下一次需要什麼。

> 📍 **1001** 離院時服務沒有停，留著在跑（第十四冊之四 M-09）。登入不通，沒有人能用，所以風險不大；
> 但從這一冊起，**登入沒通就離院時，照上面把服務停掉**，下一次來再 `up -d`。

---

## 附錄：步驟編號對照

| 本冊 | 第十四冊 | 原冊 | | 本冊 | 第十四冊 | 原冊 |
|---|---|---|---|---|---|---|
| V-01 | N-01 | 總覽第 3 節 | | V-17 | N-16 | W-16 |
| V-02 | N-02 | W-03 | | V-18 | N-17 | W-17 |
| V-03 | N-03 | W-01、W-02、Y-01 | | V-19 | N-18 | W-18 |
| V-04 | N-04 | W-04 | | V-20 | N-19 | Y-02 |
| V-05 | N-05 | W-05 | | V-21 | N-20 | Y-04 |
| V-06 | N-06 | W-06 | | V-22 | N-21 | Y-05 |
| V-07 | N-07 | W-07 | | V-23 | N-22 | Y-06 |
| **V-08** | **（新增）** | W-03 的位址一題 | | V-24 | N-23 | Y-07 |
| V-09 | N-08 | W-08 | | V-25 | N-24 | Y-08 |
| V-10 | N-09 | W-09 | | V-26 | N-25 | Y-09 |
| V-11 | N-10 | W-10 | | V-27 | N-26 | Y-10、Y-11 |
| V-12 | N-11 | W-11、Y-03 | | V-28 | N-27 | Y-12、Y-13 |
| V-13 | N-12 | W-12 | | V-29 | N-28 | Z-20 |
| V-14 | N-13 | W-13 | | V-30 | N-29 | Z-21、Z-22 |
| V-15 | N-14 | W-14 | | V-31 | N-30 | 第十一冊第 7 節、第十二冊第 7 節 |
| V-16 | N-15 | W-15 | | V-32 | N-31 | 第十一冊第 8 節 |

從 V-09 起，本冊的編號比第十四冊多一號（V-08 是新增的）。演練紀錄裡寫「卡在 V-22」或「卡在 N-21」或「卡在 Y-05」，指的是同一件事。

---

## 附錄：護理端頁面開得起來卻登不進去

V-17 用瀏覽器開護理端，登入頁出得來，按下登入卻失敗。下面的 `<主機>` 是 V-08 定的那個名稱或 IP。

### 先認清：用哪個網址開

登入時，網頁會連建置時寫進去的後端位址（`HD_PUBLIC_API_URL`）；後端只接受 `CORS_ORIGINS` 列出的來源，**主機名稱與埠要和網址列一字不差**。

| 開的網址 | 登得進去嗎 |
|---|---|
| `http://<主機>:18080` | 可以。在主機上開也一樣，網頁連後端時會連回主機自己 |
| `http://localhost:18080` | **實際部署登不進去**：網址列是 `localhost`，`CORS_ORIGINS` 寫的是 `<主機>`，後端不放行 |
| `<主機>` 的另一種寫法（名稱與 IP 互換、有沒有 DNS 尾碼） | **登不進去**，理由同上。`<主機>` 只能有一種寫法 |

> 真的需要在主機上用 `localhost` 開的話，`CORS_ORIGINS` 可以用逗號列兩個來源：`http://<主機>:18080,http://localhost:18080`，改完 `up -d` 即可，不必再 `build`。

### 第 1 步：看登入鈕下面的訊息

| 訊息 | 意思 | 接著 |
|---|---|---|
| `工作ID 或密碼錯誤` | 有連到後端，帳號或密碼不對 | 用 `.env` 的 `SUPER_ADMIN_WORK_ID`、`SUPER_ADMIN_INITIAL_PASSWORD`。第一個帳號**只在資料庫還沒有任何使用者時建立**，事後改 `.env` 不會改到已建立的帳號 |
| `Failed to fetch` | 瀏覽器沒拿到後端的回應：後端位址錯，或被 CORS 擋掉 | 第 2 步 |

### 第 2 步：網址列

**把瀏覽器網址列上的網址抄下來。** 不是 `http://<主機>:18080`（一字不差）的話，改用這個網址開，再登入一次。1001 卡住時，這一項沒有查。

### 第 3 步：網頁裡寫死的後端位址

```powershell
Select-String -Path $cfg -Pattern '^HD_PUBLIC_API_URL='
docker compose --env-file $cfg exec nurse-web grep -rhoE 'https?://[A-Za-z0-9.-]+:[0-9]+' apps/nurse-pwa/dist/assets
```

兩條印出的位址要一模一樣。不一樣 → 先 `build`、之後才改了 `.env`，再建置一次：

```powershell
docker compose --env-file $cfg build
docker compose --env-file $cfg up -d
```

做完瀏覽器按 Ctrl＋F5 重新整理，再登入一次。

（另一種看法：瀏覽器按 F12 → Network，再按一次登入，看請求送去哪個網址。）

### 第 4 步：在主機上查後端與 CORS

```powershell
Select-String -Path $cfg -Pattern '^CORS_ORIGINS='
curl.exe -s http://<主機>:13000/api/health
curl.exe -s -i -H "Origin: http://<主機>:18080" http://<主機>:13000/api/health | Select-String Access-Control-Allow-Origin
```

| 結果 | 意思 | 處置 |
|---|---|---|
| 第一條的 `CORS_ORIGINS` 不是第 2 步網址列上的來源 | CORS 寫錯 | 改 `.env`，`docker compose --env-file $cfg up -d` |
| 第二條沒有 `{"status":"ok",…}` | `<主機>:13000` 連不到後端 | `docker compose --env-file $cfg logs api --tail 30` 看原因；主機名稱查不到時，先 `Resolve-DnsName <主機>` |
| 第三條印出 `Access-Control-Allow-Origin: http://<主機>:18080` | 後端有放行這個來源 | 問題不在 CORS，回第 2、3 步 |
| 第三條什麼都沒印出來 | 後端沒放行這個來源 | `.env` 看起來對的話，多半是**改完 `.env` 還沒 `up -d`**：`.env` 只在容器建立時讀一次，執行中的後端還在用舊值。打 `up -d` 讓 compose 用新值重建後端 |

> 💡 **輸出被截斷也算有印出來。** 視窗太窄時，第三條那一行可能只看得到後半段（例如 `…rol-Allow-Origin`）。
> 看得到 `Allow-Origin` 這幾個字就是有放行；要看完整的一行，把視窗拉寬，或在指令最後加 ` | Out-String -Width 300`。
> 反過來，**真的什麼都沒印出來才是沒放行**。1001 就是空的。

**把第 2～4 步的結果全部抄進演練紀錄**，包括正常的那幾條。1001 帶回了第 4 步的第二、三條（health 正常、第三條空的），但第一條 `CORS_ORIGINS` 的內容沒帶回來，所以分不出是寫錯了還是改完沒 `up -d`。

> 🧪 **模擬部署**：`<主機>` 是開發機的區網 IP。V-17 方框那個「故意用 `localhost` 開」的練習，就是在看本附錄第一張表的第二列。

---

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|
| 1007 | 2026-10-07 | 首次定版。依 1001 帶回的資料改寫第十四冊（`V-xx`），多一步決定主機位址，現場資料以「📍 1001」標出 |

[← 第十四冊之四 · 第二次進院紀錄](14d-second-visit.md)　[← 回部署手冊總覽](index.md)
