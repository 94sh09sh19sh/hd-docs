# 第九冊 · 院方要求以 `git clone` ＋ Docker 部署

版本：v0.1　文件狀態：草案　編號：`D-xx`　**這一冊要印出來帶進去**

> 前八冊走的都是隨身碟帶離線安裝包進去、以排程工作常駐的路線（DEP-07）。
> 這一冊處理院方**指定**另一條路：**在主機上 `git clone`，再用 Docker 建置並執行。**
>
> 它和[第七冊](07-git-clone.md)不一樣。第七冊是「clone 意外成功了，接下來怎麼辦」，終點仍然是安裝包；
> 這一冊是「院方明說要容器」，那正是《部署規範》[3.3](../requirements/deployment-spec.md#33-容器備案的啟用條件)
> 列的第一種啟用條件——**容器備案正式啟用**。

---

## 0. 先講結論

### 0.1 規則哪些變、哪些不變

| 條款 | 在這條路線上 | 怎麼做到 |
|---|---|---|
| DEP-07 形態 | **改走容器**，依 3.3 第一種條件啟用 | 把院方的要求寫進書面例外（[D-06](#d-06-取得書面例外)） |
| **DEP-23** 資料庫放哪 | **一字不改，而且是這條路線上最重要的一條** | 資料庫只放具名資料卷 `hd-tablet-care-data`，**不得**掛 Windows 目錄 |
| DEP-11 不得在主機上建置 | **例外**：`docker build` 就是在主機上建置 | 書面例外寫明「建置期間」開連線，建完就關（[D-24](#d-24-關閉對外連線並當場確認)） |
| DEP-14 啟動時不連院外 | **不變** | 映像檔建好之後，啟動、遷移、備份全程不需要連線 |
| DEP-12 專用低權限帳號 | 容器內以 `node` 身分執行；主機端改看**誰能下 docker 指令** | [D-09](#d-09-確認誰能下-docker-指令) |
| DEP-15 時區 | 不變 | compose 明寫 `TZ=Asia/Taipei` |
| DEP-06 備份到另一台機器 | 不變 | 備份目錄掛主機路徑，再從那裡送走 |
| DEP-31 套用既有遷移 | 不變 | 容器裡跑同一支 `prisma-cli.mjs migrate deploy` |

> **為什麼 DEP-23 最重要。** 《部署規範》[3.1](../requirements/deployment-spec.md#31-為什麼改掉容器)
> 改掉容器的理由就是它：Docker 在 Windows 上跑在 WSL2 裡，把資料庫放在「Windows 目錄的繫結掛載」上，
> SQLite 的檔案鎖不可靠。**這種壞法平常看不出來，會在某一天兩個寫入撞在一起時毀掉資料庫。**
> 所以這條路線唯一不准商量的，就是資料庫的位置。

### 0.2 東西放在哪裡

| 東西 | 安裝包路線 | **這條路線** |
|---|---|---|
| 程式 | `C:\hd\hd-tablet-care-<版本>-<commit>\` | 映像檔 `hd-tablet-care:<版本>`，看不到檔案 |
| 原始碼 | 不在主機上 | `C:\hd\hd-tablet-care\`（clone 下來的目錄，**更新時還要用**） |
| `.env` | 安裝包目錄的上一層 | **clone 目錄裡**（compose 只從這裡讀） |
| 資料庫 | 主機上的資料目錄 | **具名資料卷** `hd-tablet-care-data`（在 WSL2 的虛擬磁碟裡） |
| 備份 | 主機上的備份目錄 | 主機上的備份目錄，掛進容器的 `/backups` |
| 常駐 | 排程工作 `HD-TabletCare` | Docker 的重新啟動策略 `unless-stopped` |
| 看狀態 | `service-status.ps1` | `docker compose ps` |

### 0.3 開發端演練結果（0921）

這一冊的每一條指令，都在開發機上以「clone → 建置 → 遷移 → 啟動 → 備份 → 更新 → 還原」的順序實際跑過一次。
**演練抓到三個會讓這條路線在院內直接倒下的問題，已在 0921 修掉**：

| 問題 | 不修會怎樣 | 修在哪 |
|---|---|---|
| 基底映像沒有 OpenSSL | 建置時只有一行警告，**啟動時一連資料庫就倒** | `Dockerfile` 兩個階段都裝 `openssl` |
| 具名資料卷的 `/data` 屬於 root | 後端以 `node` 身分執行，`Error code 14: Unable to open the database file` | `Dockerfile` 先建好 `/data`、`/backups` 並交給 `node` |
| compose 只接受繫結掛載 | 照著填 `HD_DATA_DIR` 就**直接違反 DEP-23**；填資料卷名稱則 compose 拒絕啟動 | `docker-compose.yml` 改用外部具名資料卷 |

另外補上一件：映像檔原本沒有帶 `apps/api/scripts/`，**遷移與版本更新都跑不了**，現在帶了。

**演練沒有驗到的**（開發機做不到，要在院內那台驗）：

- 主機**重新開機**之後，Docker 與三個容器會不會自己起來（[D-26](#d-26-重新開機測試這一條決定這條路線能不能用)）
- 從**另一台電腦**連進來（[D-21](#d-21-從護理站連進來)）
- 連線關閉之後重新啟動仍然正常（[D-24](#d-24-關閉對外連線並當場確認)）

> **這三條修正必須已經在 GitHub 上。** 院方 clone 到的是遠端那一版，不是你開發機上的那一版。
> [D-01](#d-01-確認要被-clone-的那一版) 就是在確認這件事。

---

## 1. 進院前（在開發端做完）

### D-01 確認要被 clone 的那一版

**做什麼**

```powershell
cd <開發機上的 repo 目錄>
git status --short
git log -1 --oneline
git fetch origin
git log -1 --oneline origin/master
```

**怎麼知道成功了**

- `git status --short` 沒有輸出
- 本機與 `origin/master` 的 commit **一模一樣**，而且這一版的 `Dockerfile` 含 `apt-get install ... openssl`
- 把這個 commit 抄進[交付單](01-dev-machine.md#p-11-寫交付單)，「交付形態」一欄寫「git clone ＋ Docker」

**可能怎麼壞、怎麼處理**

| 症狀 | 處置 |
|---|---|
| 本機比遠端新（還沒 push） | 先 push。**院方 clone 的是遠端** |
| 遠端比本機新 | 有人推了你沒驗過的東西。先拉下來，D-02 用那一版重做 |
| 想「到現場再切到某一版」 | 可以，但 commit 一定要事先寫在交付單上（[D-12](#d-12-切到交付單上的那一版)） |

---

### D-02 在開發端完整演練一次

**做什麼**

找一台**乾淨的** Windows 機器（與[第二冊](02-dry-run.md) R-01 同一個標準），裝好 Docker Desktop，
從 [D-11](#d-11-clone-到固定目錄) 一路做到 [D-23](#d-23-備份並驗證還原得起來)。**全程計時。**

**怎麼知道成功了**

- 三個容器都是 `Up`，存活檢查 HTTP 200
- 從**另一台電腦**開得了護理端、登得進去（[第二冊 R-13](02-dry-run.md#r-13--從另一台機器連進來最容易被跳過也最會出事的一步) 同一件事）
- **重新開機一次**，看 D-26 的結果

**可能怎麼壞、怎麼處理**

| 症狀 | 處置 |
|---|---|
| 沒有乾淨的機器 | 至少在開發機上做一次，並在紀錄上寫明「開發機上演練，非乾淨機器」 |
| 覺得開發機上跑過了、不必再做 | 0921 那次就是在開發機上跑的，而它抓到三個問題。**院內那台只會比它更陌生** |

---

### D-03 把 Docker 的問題清單事先寄給資訊室

**進院前兩週就要寄出**（[總覽時程](index.md#4-時程從今天到進院)的 D-14，不是本冊的 D-14），與[第四冊 H-03](04-onsite.md#h-03-找到那個有權限的人) 那份 Q-27、Q-29 清單一起。

**做什麼**

把下表貼進信裡，請資訊室逐題回答：

| # | 問題 | 為什麼要問 |
|---|---|---|
| 1 | 主機上已經裝了 Docker 嗎？是 **Docker Desktop**，還是 WSL2 裡直接裝的 Docker Engine？版本？ | 兩者的開機自動啟動方式完全不同（D-26） |
| 2 | 若是 Docker Desktop：**貴院的授權是否涵蓋這個用途？** | Docker Desktop 對一定規模以上的組織要付費訂閱。這不是你能在現場決定的事 |
| 3 | 主機**重新開機之後，有沒有人會登入**？ | **Docker Desktop 要有人登入 Windows 才會啟動**。沒有人登入，服務就不會回來 |
| 4 | 誰在 `docker-users` 群組裡？ | 在這個群組裡的人，實際上讀得到資料卷裡的病人資料（D-09） |
| 5 | 同一台主機上有沒有其他專案也在用 Docker？ | 共用同一個 Docker，別人的 `docker system prune` 會影響到本系統 |
| 6 | 建置當天對外連線要開哪些網域？（見 D-10 那張表） | 少一個就建不起來 |
| 7 | 對外連線誰開、誰關、**怎麼證明關了**？ | 與[第七冊 G-05](07-git-clone.md#g-05-問清楚這條連線的來歷) 第 4 題相同 |
| 8 | 主機上有沒有 Git？沒有的話誰裝？ | `git clone` 要有它。DEP-04 本來不允許要求院方裝東西，這一條要寫進例外 |
| 9 | Docker 的虛擬磁碟放在哪顆磁碟？ | 預設放在個人資料夾的 `AppData` 底下，那正是 DEP-37 第 3 項要避開的位置（D-08） |

**怎麼知道成功了**

有書面回覆。**第 2、3 題沒有答案，這條路線就不能開始輸入真實病人資料。**

---

### D-04 準備一把唯讀、會過期的存取憑證

這個 repo 是**私有的**，院方 clone 一定要有憑證。[第七冊 G-03](07-git-clone.md#g-03-查出是誰的憑證) 講過用錯憑證的後果。
**這一次你可以事先準備對的那一把。**

**做什麼**

在 GitHub 上建一把 **fine-grained personal access token**：

| 設定 | 值 |
|---|---|
| Repository access | **Only select repositories**，只勾這個 repo |
| Permissions | **Contents：Read-only**，其他全部 No access |
| Expiration | **進院當天的隔天** |
| 名稱 | `hospital-clone-<日期>` |

權杖**不要存在任何檔案裡**，抄在交付單背面，進院當天用完就劃掉。

**怎麼知道成功了**

在開發機上用它 clone 一次成功，而且**用它 push 會被拒絕**。

**可能怎麼壞、怎麼處理**

| 症狀 | 處置 |
|---|---|
| repo 屬於組織，組織不允許 fine-grained token | 改用唯讀的 **deploy key**（repo 設定 → Deploy keys，不勾 Allow write access），私鑰當天用完刪除 |
| 院方說要用他們自己的帳號 | 最好。請他們事先取得存取權，你不必帶任何憑證進去 |

---

## 2. 進院當天：先確認 Docker 這一層

前面照[第四冊](04-onsite.md) H-01～H-07 走（報到、找人、問問題、確認機器、盤點）。
**H-08 到 H-13 由這一冊的 D-05～D-23 取代。** H-14 起回到第四冊，差異寫在 [D-27](#d-27-回到第四冊哪些照做哪些要換)。

### D-05 開場時說清楚這條路線的代價

**做什麼**

對資訊室講三句話：

1. 「容器這條路我們準備好了，開發端演練過，**差別是建置要在這台機器上做，所以今天要開一段對外連線，建完就關**。」
2. 「資料庫會放在 Docker 的資料卷裡，**你們在檔案總管裡看不到它**。備份會放在一個看得到的目錄，每天一份。」
3. 「**這台機器重新開機之後，要有人登入 Windows，系統才會回來**——除非我們今天找到別的辦法。」（D-03 第 3 題）

**怎麼知道成功了**

對方聽完第三句之後，有給出答案（「會有人登入」「我們有自動登入」「用 Docker Engine」），而不是「應該沒問題」。

---

### D-06 取得書面例外

**做什麼**

照[第七冊 G-09](07-git-clone.md#g-09-取得書面例外) 那張表請對方簽名，**另外多寫五列**：

| 事項 | 內容 |
|---|---|
| 部署形態 | 依院方要求以容器部署（《部署規範》3.3 第一種條件） |
| 例外條款 | DEP-11（主機上建置）、DEP-04（主機上需有 Git 與 Docker） |
| 允許連線的來源 | D-10 那張表 |
| Docker 授權 | 由院方確認（D-03 第 2 題） |
| 重新開機後的啟動方式 | D-03 第 3 題的答案 |

**怎麼知道成功了**

手上有一張簽了名的紙。**口頭同意不算。**

**可能怎麼壞、怎麼處理**

| 症狀 | 處置 |
|---|---|
| 沒有人願意簽 | 停手。回第四冊 H-08，改走路線 B（隨身碟）。**隨身碟上那份安裝包照樣帶去**，就是為了這一刻 |

> 回去之後，容器備案啟用與這幾條例外要寫進《[部署規範](../requirements/deployment-spec.md)》。
> **手冊不能替規範開例外**，它只記錄現場發生了什麼（與第七冊 G-09 同一條）。

---

### D-07 確認 Docker 可以用

**做什麼**

用**會實際操作 Docker 的那個帳號**登入，開 PowerShell：

```powershell
docker version
docker info --format "{{.ServerVersion}} {{.OSType}} {{.Architecture}}"
docker compose version
wsl --status
```

**怎麼知道成功了**

| 指令 | 應該看到 |
|---|---|
| `docker version` | Client 與 Server 兩段都有版本號 |
| `docker info` | `<版本> linux x86_64`（**一定要是 `linux`**） |
| `docker compose version` | `v2.` 開頭 |
| `wsl --status` | 預設版本 2 |

**可能怎麼壞、怎麼處理**

| 症狀 | 原因 | 處置 |
|---|---|---|
| `failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine` | Docker Desktop 沒有在跑 | 從開始選單開 Docker Desktop，等左下角變綠再重試。**記下來：這就是重新開機沒人登入時會發生的事** |
| `OSType` 是 `windows` | 切到了 Windows 容器模式 | 系統匣的 Docker 圖示按右鍵 → Switch to Linux containers |
| `docker` 找不到指令 | 沒裝 Docker，或這個帳號的 PATH 沒有它 | 問資訊室。**不要自己裝**，那是院方的變更流程 |
| `permission denied` 或存取被拒 | 這個帳號不在 `docker-users` 群組 | 請資訊室加，**並記下加了誰**（D-09） |
| `docker compose` 找不到，但 `docker-compose` 可以 | 舊版的 Compose v1 | 請資訊室升級。**外部資料卷的寫法 v1 不一定支援**，不要硬用 |

---

### D-08 Docker Desktop 的四項設定，以及防毒排除

**做什麼**

開 Docker Desktop → Settings，逐項看：

| # | 位置 | 設成 | 為什麼 |
|---|---|---|---|
| 1 | General → **Start Docker Desktop when you sign in** | 勾 | 否則連有人登入都不會啟動 |
| 2 | General → **Send usage statistics** | 不勾 | 那是一條院外連線（FR-S07） |
| 3 | Software updates → **Automatically check for updates** | 不勾 | 同上；而且更新 Docker 是院方的變更，不該自己發生 |
| 4 | Resources → Advanced → **Disk image location** | 本系統自己的路徑，例如 `D:\hd-docker` | 預設在 `C:\Users\<帳號>\AppData\Local\Docker`，是個人資料夾（DEP-37 第 3 項） |

第 4 項若要搬，**要在建資料卷之前搬**；Docker Desktop 會把現有的虛擬磁碟一起搬過去，要花幾分鐘。
**同機有別的專案在用 Docker 時，第 4 項不要動**，記下現況，回去再談。

然後請資訊室把**虛擬磁碟所在的目錄**加入防毒排除清單（[H-14 ①](04-onsite.md#h-14-windows-五件事需要資訊室) 的容器版）。

**怎麼知道成功了**

四項都是上表的值，截圖或抄下來；防毒排除清單裡看得到那個目錄。

**可能怎麼壞、怎麼處理**

| 症狀 | 處置 |
|---|---|
| 設定是灰的、改不了 | 院方用管理原則鎖住了。記下來，那幾項由資訊室決定 |
| 資訊室不肯排除整個虛擬磁碟目錄 | **這一條要談到有結果。** 即時掃描一個正在被寫入的虛擬磁碟，效果與掃描資料庫檔案一樣：間歇性的鎖定與變慢 |

---

### D-09 確認誰能下 docker 指令

**這是容器路線上最容易被忽略的一條**（DEP-12、DEP-37 第 4 項）。容器裡的後端雖然以低權限的 `node` 身分執行，
但**任何能下 docker 指令的人，都能掛上資料卷、把資料庫整個讀出來**，不需要知道任何密碼。

**做什麼**

```powershell
Get-LocalGroupMember -Group "docker-users"
```

**怎麼知道成功了**

名單裡只有：系統管理員、負責這個系統的人。**寫進交接文件，並寫明加人要知會誰。**

**可能怎麼壞、怎麼處理**

| 症狀 | 處置 |
|---|---|
| 名單裡有別的專案的人 | 共用 Docker 的代價。**當場告訴資訊室這代表什麼**，由院方決定；記進紀錄 |
| 找不到這個群組 | 裝的是 WSL2 裡的 Docker Engine。改問：誰登得進那個 WSL 發行版、誰有 `sudo` |

---

### D-10 對外連線實測

**做什麼**

資訊室開好連線之後，一個一個測：

```powershell
Test-NetConnection github.com -Port 443
Test-NetConnection registry-1.docker.io -Port 443
Test-NetConnection auth.docker.io -Port 443
Test-NetConnection production.cloudflare.docker.com -Port 443
Test-NetConnection deb.debian.org -Port 80
Test-NetConnection registry.npmjs.org -Port 443
Test-NetConnection binaries.prisma.sh -Port 443
```

| 網域 | 誰要用 |
|---|---|
| `github.com` | `git clone` |
| `registry-1.docker.io`、`auth.docker.io`、`production.cloudflare.docker.com` | 下載基底映像 `node:20-bookworm-slim` |
| `deb.debian.org`（**埠 80**） | 建置時安裝 `openssl` |
| `registry.npmjs.org` | `npm ci` |
| `binaries.prisma.sh` | Prisma 引擎 |

**怎麼知道成功了**

七個 `TcpTestSucceeded` 都是 `True`。

**可能怎麼壞、怎麼處理**

| 症狀 | 處置 |
|---|---|
| 經代理伺服器，`Test-NetConnection` 是 `False` | 正常，改用 `curl.exe -I https://registry.npmjs.org` 測。**Docker 另外要設代理**：Settings → Resources → Proxies |
| 只有 `deb.debian.org` 不通（只開了 443） | 請加開 80。不能開就停下來，回去改 `Dockerfile` 換基底映像，**不要在現場改** |
| 有幾個不通 | 補齊再往下。建到一半才失敗，比現在停下來更浪費時間 |

---

## 3. 取得程式碼

### D-11 clone 到固定目錄

**做什麼**

```powershell
New-Item -ItemType Directory -Force C:\hd
cd C:\hd
git -c credential.helper= clone https://github.com/<帳號>/<repo>.git hd-tablet-care
```

跳出帳號密碼時：帳號填你的 GitHub 帳號，**密碼貼 D-04 那把權杖**。
`-c credential.helper=` 是**這一次不要把憑證存進 Windows**。

**怎麼知道成功了**

`C:\hd\hd-tablet-care\` 存在，裡面看得到 `Dockerfile` 與 `docker-compose.yml`。

**可能怎麼壞、怎麼處理**

| 症狀 | 處置 |
|---|---|
| 跳出瀏覽器要你登入 GitHub | Git Credential Manager 攔下來了。關掉視窗，改用上面那行（帶 `-c credential.helper=`） |
| `Authentication failed` | 權杖貼錯、過期，或忘了勾這個 repo |
| 目錄路徑選在「文件」或桌面 | 換到 `C:\hd`。`.env` 會放在這個目錄裡，而那兩個位置常被同步到雲端（DEP-21 第 2 項） |

---

### D-12 切到交付單上的那一版

**做什麼**

```powershell
cd C:\hd\hd-tablet-care
git checkout <交付單上的 commit>
git log -1 --oneline
git status --short
git remote -v
```

**怎麼知道成功了**

- `git log -1` 與交付單**一字不差**
- `git status --short` 沒有輸出
- `git remote -v` 的網址裡**沒有權杖**

**可能怎麼壞、怎麼處理**

| 症狀 | 處置 |
|---|---|
| 網址裡看得到權杖 | 有人把權杖寫進網址 clone 了。`git remote set-url origin https://github.com/<帳號>/<repo>.git`，並在 D-25 作廢那把權杖 |
| 找不到那個 commit | 遠端沒有它，回 D-01 的問題。**不要改用最新一版** |

---

## 4. 建置映像檔

### D-13 決定位址與三個連接埠

**做什麼**

| 要定的值 | 例子 | 從哪來 |
|---|---|---|
| 主機位址 | `hd-server` 或 `10.1.2.3` | 資訊室。**要是護理站電腦與平板連得到的那一個**，不是 `localhost` |
| 後端埠 `HD_API_PORT` | `3000` | 向資訊室登記（DEP-37 第 2 項） |
| 護理端埠 `HD_NURSE_PORT` | `8080` | 同上 |
| 病人端埠 `HD_PATIENT_PORT` | `8081` | 同上 |

先確認這三個埠在這台主機上沒人用：

```powershell
Get-NetTCPConnection -State Listen -LocalPort 3000, 8080, 8081 -ErrorAction SilentlyContinue
```

**怎麼知道成功了**

四個值抄在筆記本上；上面那行指令什麼都沒印。

> **主機位址與後端埠會在下一步被寫死進映像檔**，之後改不了，只能重建。
> 這是為什麼它要先定下來，而且要是別台電腦看得到的那一個。

---

### D-14 建置

**做什麼**

```powershell
cd C:\hd\hd-tablet-care
docker build --build-arg VITE_API_BASE_URL=http://<主機位址>:<HD_API_PORT> -t hd-tablet-care:<版本>-<commit 前 7 碼> .
```

例如 `hd-tablet-care:0.1.0-c4109fa`。**標籤不要用 `latest`**：更新之後要回得去上一版，得分得出哪一個是上一版（DEP-19）。

**預留 30 分鐘。** 開發機有快取時約 1～2 分鐘；院內第一次什麼都要下載。

**怎麼知道成功了**

最後幾行出現 `naming to docker.io/library/hd-tablet-care:<標籤> done`，而且**整段輸出裡沒有 `prisma:warn`**。

**可能怎麼壞、怎麼處理**

| 症狀 | 原因 | 處置 |
|---|---|---|
| `failed to resolve source metadata for docker.io/library/node` | 連不到 Docker Hub | D-10 那三個 Docker 網域 |
| `apt-get` 那一步卡住或失敗 | `deb.debian.org` 的 80 沒開 | D-10 |
| `npm ci` 出現 `ETIMEDOUT`、`ENOTFOUND registry.npmjs.org` | 連不到 npm | D-10 |
| `ENOTFOUND binaries.prisma.sh` | 連不到 Prisma 引擎發布站 | D-10 |
| 輸出裡有 `Prisma failed to detect the libssl/openssl version` | clone 到的是 0921 之前的 `Dockerfile` | **停下來。** 這樣建出來的映像檔啟動就會倒。回 D-12 確認版本 |
| `npm ci` 說 lock 檔與 `package.json` 不一致 | clone 到的版本不對，或有人改過檔案 | `git status --short` 應該沒有輸出 |
| 建到一半磁碟空間不足 | 映像檔建完約 1GB，建置過程要更多 | 問資訊室 D-08 第 4 項那顆磁碟還有多少 |

---

### D-15 確認映像檔，以及位址寫對了

**做什麼**

```powershell
docker image ls hd-tablet-care
docker run --rm --entrypoint sh hd-tablet-care:<標籤> -c "grep -rlo '<主機位址>:<HD_API_PORT>' apps/nurse-pwa/dist apps/patient-pwa/dist"
```

**怎麼知道成功了**

- 第一行列出剛才那個標籤
- 第二行印出**兩個**檔名，一個在 `nurse-pwa`、一個在 `patient-pwa`

**可能怎麼壞、怎麼處理**

| 症狀 | 處置 |
|---|---|
| 第二行什麼都沒印 | 位址沒寫進去，或寫成別的。**回 D-14 重建**；這一步不檢查，到 D-21 才會發現護理站登不進去 |
| 只印出一個 | 其中一個 PWA 沒建好，看 D-14 的輸出 |

---

## 5. 設定與資料

### D-16 建立 `.env`

**做什麼**

```powershell
cd C:\hd\hd-tablet-care
Copy-Item .env.example .env
notepad .env
```

**只填下面這些**，其他保持範本的值：

| 變數 | 填什麼 |
|---|---|
| `HD_IMAGE_TAG` | D-14 的標籤，例如 `0.1.0-c4109fa` |
| `HD_BACKUP_DIR` | 備份目錄，例如 `D:/hd-backup`（D-17 會建） |
| `HD_API_PORT`、`HD_NURSE_PORT`、`HD_PATIENT_PORT` | D-13 的三個埠 |
| `CORS_ORIGINS` | `http://<主機位址>:<HD_NURSE_PORT>,http://<主機位址>:<HD_PATIENT_PORT>` |
| `MDM_KIOSK_BASE_URL` | `http://<主機位址>:<HD_PATIENT_PORT>` |
| `JWT_SECRET` | 在主機上產生一組，見下 |
| `SUPER_ADMIN_WORK_ID`、`SUPER_ADMIN_INITIAL_PASSWORD`、`SUPER_ADMIN_DISPLAY_NAME` | 第一個管理者帳號；首次登入會強制改密碼 |

`JWT_SECRET` 在主機上產生，**不要從開發機帶進來**：

```powershell
docker run --rm --entrypoint node hd-tablet-care:<標籤> -e "console.log(require('crypto').randomBytes(48).toString('base64url'))"
```

> **compose 只拿 `.env` 做變數代換，不會把整份倒進容器**。所以範本裡的 `DATABASE_URL`、`API_PORT`、`BACKUP_DIR`
> 這些安裝包用的變數，在這條路線上**填了也沒有作用**，留空即可。容器實際拿到什麼，寫在 `docker-compose.yml` 裡。

**怎麼知道成功了**

```powershell
docker compose config --quiet
```

沒有任何輸出。

**可能怎麼壞、怎麼處理**

| 症狀 | 處置 |
|---|---|
| `required variable HD_BACKUP_DIR is missing a value` | `HD_BACKUP_DIR` 沒填 |
| `請設定 CORS_ORIGINS` 或 `請設定 JWT_SECRET` | 對應那一行沒填 |
| 路徑用反斜線 `D:\hd-backup` | 改成 `D:/hd-backup`。斜線不會被跳脫字元誤傷 |
| 想把資料庫也指到 `D:\hd-data` | **不行，DEP-23。** 這條路線上沒有「資料目錄」這個設定，是刻意拿掉的 |

---

### D-17 建立資料卷與備份目錄

**做什麼**

```powershell
docker volume create hd-tablet-care-data
New-Item -ItemType Directory -Force D:\hd-backup
docker volume inspect hd-tablet-care-data --format "{{.Name}} {{.Driver}}"
```

**怎麼知道成功了**

最後一行印出 `hd-tablet-care-data local`。

**可能怎麼壞、怎麼處理**

| 症狀 | 處置 |
|---|---|
| 資料卷已經存在 | **停。** 裡面可能有資料（前一次部署、或別人建的）。先 `docker run --rm -v hd-tablet-care-data:/data --entrypoint ls hd-tablet-care:<標籤> -la /data` 看裡面有什麼，問清楚再決定 |
| 備份目錄只能放在「文件」或共用目錄 | [總覽第 6 節](index.md#6-什麼情況下當場停手)的停手情形之一 |

> **資料卷標成 external，是刻意的。** compose 不會替你建它，也**不會**在有人打了 `docker compose down -v` 時把它刪掉。
> 整個透析中心的照護紀錄在裡面，刪不刪不該取決於有沒有人多打了兩個字元。

---

### D-18 套用既有遷移（DEP-31）

**做什麼**

```powershell
docker compose run --rm --no-deps api node apps/api/scripts/prisma-cli.mjs migrate deploy --schema apps/api/prisma/schema.prisma
```

**要在啟動服務之前做**：第一次部署時資料庫是空的。

**怎麼知道成功了**

列出一串遷移目錄，最後一行是 `All migrations have been successfully applied.`
再跑一次同一行，應該是 `No pending migrations to apply.`

**可能怎麼壞、怎麼處理**

| 症狀 | 原因 | 處置 |
|---|---|---|
| `external volume "hd-tablet-care-data" not found` | D-17 沒做 | 做 D-17 |
| `Error code 14: Unable to open the database file` | 映像檔是 0921 之前的版本，`/data` 屬於 root | 回 D-12 確認版本，重建 |
| `ENOTFOUND binaries.prisma.sh` | 不該發生：引擎在建置時已經下載進映像檔 | 看 D-14 的輸出是否有 `prisma:warn`；有就重建 |
| 有人建議用 `migrate dev` 或 `db push` | **絕對不可以**，它們可能直接重建整個資料庫 | — |

---

## 6. 啟動與驗證

### D-19 啟動

**做什麼**

```powershell
docker compose up -d
docker compose ps
curl.exe -i http://localhost:<HD_API_PORT>/api/health
docker compose logs api --tail 30
```

**怎麼知道成功了**

| 看什麼 | 應該看到 |
|---|---|
| `docker compose ps` | `api`、`nurse-web`、`patient-web` 三個都是 `Up`，**過一分鐘再看一次仍然是 `Up`**（不是一直 `Restarting`） |
| 存活檢查 | `HTTP/1.1 200`，內容是 `{"status":"ok",...}` |
| 紀錄檔最後幾行 | `後端服務已啟動`、`版本標記：...（正式環境設定）`、`伺服器時區：Asia/Taipei` |

紀錄檔裡會有一行黃色的 `時區來自環境變數 TZ（Asia/Taipei）……` 警告，**這在容器裡是正常的**：
容器沒有「主機時區設定」可以看，時區就是 compose 給的那個 `TZ`。

**可能怎麼壞、怎麼處理**

| 症狀 | 原因 | 處置 |
|---|---|---|
| `api` 一直 `Restarting` | 啟動就倒 | `docker compose logs api --tail 80` 看最後的錯誤，對照本表與[第六冊](06-troubleshooting.md) |
| `Bind for 0.0.0.0:3000 failed: port is already allocated` | 埠被別人佔了 | D-13 那行指令找出是誰，換埠，改 `.env` |
| `pull access denied for hd-tablet-care` | `HD_IMAGE_TAG` 與 D-14 的標籤不一致，compose 以為要去下載 | 改 `.env` |
| `缺少必要環境變數` | compose 沒把值傳進去 | 看 `docker-compose.yml` 的 `environment` 有沒有那一項；**不要**改成 `env_file`（檔案開頭有寫為什麼） |
| `拒絕啟動` 且提到時區 | `.env` 的 `TZ` 被改掉了 | 改回 `Asia/Taipei` |

---

### D-20 看一眼資料庫的四項設定

**做什麼**

在主機上開 `http://localhost:<HD_NURSE_PORT>`，用 `SUPER_ADMIN_*` 登入、改密碼，到**系統設定 → 資料庫狀態**。

**怎麼知道成功了**

| 看什麼 | 應該是 |
|---|---|
| journal mode | `WAL` |
| foreign keys | 開 |
| busy timeout | `5000` |
| synchronous | `FULL` |
| 備份目錄 | 已設定，每日 `03:00` |

**可能怎麼壞、怎麼處理**

| 症狀 | 處置 |
|---|---|
| 磁碟可用空間顯示得很大（例如上千 GB） | **正常，但要知道它量的是什麼**：它量的是 WSL2 虛擬磁碟的上限，不是 D-08 第 4 項那顆實體磁碟。實體磁碟的空間要另外請資訊室監看（DEP-37 磁碟下限） |

---

### D-21 從護理站連進來

**做什麼**

照[第四冊 H-15](04-onsite.md#h-15-防火牆與從護理站連進來)，請資訊室開三個埠的輸入規則，
然後**到護理站那台電腦上**開 `http://<主機位址>:<HD_NURSE_PORT>`，登入。

接著照 [H-16](04-onsite.md#h-16-冒煙測試) 走一次主線。

**怎麼知道成功了**

在護理站的電腦上登得進去，主線走得完。

**可能怎麼壞、怎麼處理**

| 症狀 | 原因 | 處置 |
|---|---|---|
| 畫面出得來、登入沒反應 | 映像檔裡的後端位址不對 | D-15 應該已經擋下。沒擋下就是 D-13 的主機位址給錯，**重建映像檔**（D-14～D-15），不必重做資料 |
| 主控台出現 CORS 錯誤 | `CORS_ORIGINS` 沒填對 | 改 `.env`，`docker compose up -d`（會自動重建有變動的容器） |
| 主機上連得到、別台連不到 | Windows 防火牆 | Docker Desktop 開的埠一樣要有輸入規則。請資訊室以埠號開，不要以程式開 |

---

### D-22 常駐：確認它會自己回來

**做什麼**

```powershell
docker compose restart
docker compose ps
curl.exe -i http://localhost:<HD_API_PORT>/api/health
```

**怎麼知道成功了**

三個都回到 `Up`，存活檢查 200。

> 這只證明「容器重新啟動沒問題」，**不證明主機重新開機沒問題**。那是 [D-26](#d-26-重新開機測試這一條決定這條路線能不能用)。

---

### D-23 備份並驗證還原得起來

**做什麼**

用正式環境的更新腳本做一次「備份 → 還原驗證」。它會先備份、還原到另一個檔案做完整性檢查與筆數核對，
沒有待套用的遷移時就只留下一筆紀錄：

```powershell
docker compose stop api
docker compose run --rm --no-deps api node apps/api/scripts/db-update.mjs --note "首次部署備份驗證"
docker compose start api
Get-ChildItem D:\hd-backup
```

**怎麼知道成功了**

- 輸出有 `[3] 更新前備份`（檔名與 SHA-256）、`[4] 驗證備份還原得起來`（`完整性檢查 ok` 與各表筆數）、`更新完成`
- `D:\hd-backup` 裡看得到 `hd-before-update-*.db`
- 再到護理端按一次**立即備份**，`D:\hd-backup` 多一個 `hd-backup-*.db`

然後把其中一份複製到**院內另一台機器**（DEP-06），在那邊算一次雜湊，與輸出的 SHA-256 核對：

```powershell
Get-FileHash -Algorithm SHA256 <那一份的路徑>
```

**可能怎麼壞、怎麼處理**

| 症狀 | 處置 |
|---|---|
| 腳本說服務還在跑 | 第一行沒做，或 `api` 沒停成。`docker compose ps` 確認 |
| 備份目錄是空的 | `HD_BACKUP_DIR` 指錯。`docker compose config` 看 `/backups` 對到哪裡 |
| 找不到院內另一台機器 | 規範第 9 章第 7 條不過。**記下來，這是 B 級結果**，不是今天可以跳過的事 |

---

## 7. 收掉連線與憑證

### D-24 關閉對外連線，並當場確認

**做什麼**

請資訊室依 D-06 那張紙上的方式關閉連線，然後**你自己**確認：

```powershell
Test-NetConnection github.com -Port 443
Test-NetConnection registry-1.docker.io -Port 443
Test-NetConnection registry.npmjs.org -Port 443
Test-NetConnection deb.debian.org -Port 80
```

再證明服務不需要連線也能起來：

```powershell
docker compose restart
curl.exe -i http://localhost:<HD_API_PORT>/api/health
```

**怎麼知道成功了**

四個 `TcpTestSucceeded` 都是 `False`；重新啟動後存活檢查仍是 200。

**可能怎麼壞、怎麼處理**

| 症狀 | 處置 |
|---|---|
| 還是 `True` | 與[第七冊 G-17](07-git-clone.md#g-17-關閉對外連線並當場確認) 相同：**服務可以留著，但不得開始輸入真實病人資料**，直到連線關閉 |
| 關了之後 Docker Desktop 跳出登入或更新的提示 | 關掉即可。D-08 第 2、3 項沒設好的話會一直跳 |

---

### D-25 清掉憑證

**做什麼**

```powershell
cd C:\hd\hd-tablet-care
git remote -v
git config --show-origin --get-regexp "credential"
cmdkey /list | Select-String -Pattern "git"
```

有列出東西就照[第七冊 G-08](07-git-clone.md#g-08-清掉-clone-與憑證) 刪掉。
**clone 目錄不要刪**：更新時要在這裡 `git fetch` 與重建，`.env` 與 `docker-compose.yml` 也在這裡。

回到院外之後，**當天**到 GitHub 把 D-04 那把權杖作廢（Settings → Developer settings → Personal access tokens → Delete），
不要等它自己過期。

**怎麼知道成功了**

- `git remote -v` 的網址裡沒有權杖
- 後兩行都沒有任何 `git` 或 `github` 的項次
- 交付單背面的權杖已劃掉，紀錄寫「D-04 權杖已作廢，<時間>」

---

### D-26 重新開機測試（這一條決定這條路線能不能用）

**做什麼**

挑一個**不在透析班次中**的時間，請資訊室重新開機，然後照 D-03 第 3 題的答案：

| 那台機器的做法 | 你要看的 |
|---|---|
| 會有人（或自動）登入 Windows | 登入後等 2 分鐘，不碰任何東西，`docker compose ps` |
| WSL2 裡的 Docker Engine，由開機排程工作啟動 | **不要登入**，從另一台電腦開護理端網址 |

**怎麼知道成功了**

**沒有任何人手動啟動 Docker 或下任何指令**，三個容器自己回到 `Up`，護理站連得進來。

**可能怎麼壞、怎麼處理**

| 症狀 | 處置 |
|---|---|
| 沒人登入就不會起來，而院方也不會安排人登入 | **這條路線就不適合 24 小時運作的照護系統。** 寫進紀錄與交接，列為 A 級不能成立的理由；由院方決定改用 Docker Engine、安排自動登入，或回到安裝包路線。**不要替院方決定開自動登入**：那等於把一個帳號的密碼存在主機上 |
| 登入之後 Docker 起來了，但容器沒有 | 看 `docker compose ps -a` 的狀態。`Exited` 且是你手動停的，`unless-stopped` 不會把它帶回來——**這是對的**，那是[第九節](#9-關服務對照第八冊)「停用」的做法 |
| 今天沒辦法重新開機 | 記下「重新開機後未驗證」，請資訊室下次開機後代看，**並約好誰回報你** |

---

## 8. 回到第四冊

### D-27 回到第四冊：哪些照做、哪些要換

從 [H-14](04-onsite.md#h-14-windows-五件事需要資訊室) 起回到第四冊，對照下表：

| 第四冊 | 這條路線 |
|---|---|
| H-14 ① 防毒排除資料庫目錄 | 換成 D-08 的**虛擬磁碟目錄**，再加上備份目錄 |
| H-14 ② ③ 雲端同步、網路磁碟 | 看**備份目錄**與**虛擬磁碟目錄**，不是資料目錄（資料在資料卷裡） |
| H-14 ④ ⑤ 休眠、更新時段 | 照做。**Windows 更新重新開機之後的情形，就是 D-26** |
| H-15、H-16 | 已在 D-21 做完 |
| H-17 備份與還原 | D-23 做了「還原驗證」；**真的還原一次**的做法見[第十節](#10-之後的更新回退與還原) |
| H-18 起 | 照做 |
| H-21 交接文件 | 多寫四件事：clone 目錄的位置、映像檔標籤、`docker-users` 名單（D-09）、重新開機後的啟動方式（D-26） |
| [第五冊](05-carry-in-out.md) C-xx | 照做。隨身碟這次可能沒用上，**仍然要當場清除並寫明**（DEP-28） |

---

## 9. 關服務（對照第八冊）

[第八冊](08-shutdown.md)的三種深度、S-01 告知病房、S-06～S-09 的撤除規則全部照用，只是指令換掉：

| 深度 | 指令 | 重新開機後 |
|---|---|---|
| **暫停** | `docker compose stop`，做完事再 `docker compose start` | **不會**自己回來（`unless-stopped` 記得你手動停過） |
| **停用** | 同暫停。另外在交接與紀錄寫明「已停用，恢復要先問 <誰>」 | 不會 |
| **撤除** | `docker compose down`，再依第八冊 S-08 那張表收拾 | — |

> **注意和安裝包路線反過來的地方**：安裝包的「暫停」在重新開機後會自己回來，這裡不會。
> 所以這裡的暫停已經是停用的效果，**做完事一定要記得 `start`**，並確認三個都是 `Up`。

S-04 四條判準的容器版：

```powershell
docker compose ps -a
docker ps --filter volume=hd-tablet-care-data
Get-NetTCPConnection -State Listen -LocalPort <HD_API_PORT>, <HD_NURSE_PORT>, <HD_PATIENT_PORT> -ErrorAction SilentlyContinue
```

| # | 應該看到 |
|---|---|
| 1、2 | 三個容器都是 `Exited`；第二行沒有任何容器 |
| 3 | 什麼都沒印 |
| 4 | 第二行沒有容器，就沒有任何行程開著資料庫——資料卷只有容器能掛 |

**撤除時的兩條硬規則：**

- **不要**下 `docker volume rm hd-tablet-care-data`、`docker compose down -v`、`docker system prune --volumes`。
  資料卷就是資料庫，依 S-09 由院方決定去向
- 要把資料交給院方，先照 D-23 或護理端的立即備份做一份到 `D:\hd-backup`，交出那一份

---

## 10. 之後的更新、回退與還原

### 更新

每一次都是**開連線 → 建新映像檔 → 關連線 → 備份與遷移 → 換版**，省不了哪一步。
排在非透析時段，更新後第一個班次要有人在（DEP-32）。

```powershell
cd C:\hd\hd-tablet-care
git -c credential.helper= fetch origin
git checkout <新版 commit>
docker build --build-arg VITE_API_BASE_URL=http://<主機位址>:<HD_API_PORT> -t hd-tablet-care:<新版標籤> .
# 關連線，照 D-24 確認
notepad .env                        # HD_IMAGE_TAG 改成新版標籤
docker compose stop api
docker compose run --rm --no-deps api node apps/api/scripts/db-update.mjs --note "<這次更新的說明>"
docker compose up -d
```

`db-update.mjs` 會先備份並驗證還原，**沒過就停在那裡、不遷移**。
**舊版映像檔不要刪**，新版穩定之前那是唯一能退回去的東西。

### 回退

```powershell
notepad .env                        # HD_IMAGE_TAG 改回舊版標籤
docker compose up -d
```

**這一版動過資料庫結構時**，要先還原 `db-update.mjs` 印出的那一份 `hd-before-update-*.db`，再換回舊版。
**程式可以退版，資料庫不能退版**，不要試圖把遷移倒回去（規範 18.3）。

### 還原一份備份到資料卷

```powershell
docker compose down
docker run --rm --entrypoint sh -v hd-tablet-care-data:/data -v D:/hd-backup:/backups:ro hd-tablet-care:<標籤> -c "mkdir -p /data/before-restore && mv /data/hd.db* /data/before-restore/ && cp /backups/<備份檔名> /data/hd.db && ls -la /data"
docker compose up -d
```

- 原本的 `hd.db` 與 `-wal`、`-shm` **三個一起**搬進 `before-restore/`，不刪（DEP-09）
- 啟動後紀錄檔可能出現一行 `1 筆備份於上次服務停止時中斷，已標記為失敗`：那是備份當下正在進行的那一筆，**正常**
- 到護理端核對筆數與最後一筆資料的時間，確認還原的是對的那一份

---

## 11. 疑難排解（這一冊特有的）

一般症狀仍查[第六冊](06-troubleshooting.md)；以下是容器路線才有的：

| 症狀 | 原因 | 處置 |
|---|---|---|
| `failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine` | Docker Desktop 沒在跑 | 開 Docker Desktop；**問自己為什麼它沒在跑**（D-26） |
| `external volume "hd-tablet-care-data" not found` | 資料卷不存在 | 第一次部署：D-17。**不是第一次**：有人刪了資料卷，**停下來**，從最近的備份還原，不要直接建一個新的空資料卷 |
| `service "api" refers to undefined volume` | 用的是 0921 之前的 `docker-compose.yml`，把資料卷名稱填進了舊的 `HD_DATA_DIR` | 回 D-12 確認版本 |
| `Error code 14: Unable to open the database file` | 映像檔是 0921 之前的版本 | 同上，重建 |
| `Prisma failed to detect the libssl/openssl version` | 同上 | 同上 |
| `api` 在 `Restarting` 與 `Up` 之間跳 | 啟動就倒，被重新啟動策略一直拉起來 | `docker compose logs api --tail 80` |
| 護理端出得來、資料讀不到 | 映像檔的後端位址不對，或 CORS | D-15、D-21 |
| 別的專案的人下了 `docker system prune -a` | 映像檔被清掉；**資料卷不會**（沒有 `--volumes`） | 映像檔要重建，**要開連線**。這是 D-03 第 5 題要先問的原因 |
| Docker Desktop 自己更新之後起不來 | D-08 第 3 項沒關 | 請資訊室處理；紀錄寫明更新前後的版本 |

---

## 12. 離院前多五條

照[第四冊 H-22](04-onsite.md#h-22-收尾清單離院前-30-分鐘一定要留這段時間) 的清單，再加：

- [ ] 對外連線已關閉，D-24 當場確認過
- [ ] 權杖已從主機上清掉（D-25），**回去當天作廢**
- [ ] `docker-users` 名單已寫進交接（D-09）
- [ ] 重新開機測試做了，結果寫進紀錄；沒做的話，**誰在什麼時候代看**（D-26）
- [ ] 交接文件寫明：資料在資料卷 `hd-tablet-care-data`、**不得執行的三個指令**（第九節）、備份在哪個目錄

紀錄寫進《[部署演練紀錄](../notes/deployment-drills.md)》，「交付形態」寫「git clone ＋ Docker」，
每一步的耗時照記，**D-14 的建置時間尤其要記**——它決定下一次更新要留多長的時段。

---

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|
| 0923 | 2026-09-23 | 首次定版。院方要求以 `git clone` ＋ Docker 部署時的岔路；開發端演練抓到三個會在院內倒下的問題，0921 已修 |

[← 上一冊 · 把服務關乾淨](08-shutdown.md) · [回部署手冊總覽](index.md) · [下一冊 · 第一次進院紀錄 →](10-first-visit.md) · [回進度首頁](../index.md)
