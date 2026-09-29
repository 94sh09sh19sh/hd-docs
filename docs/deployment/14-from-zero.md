# 第十四冊 · 從零開始的實際部署（新手版）

版本：v0.1　文件狀態：草案（0929 新增）　編號：`N-xx`　**要印出來帶進去**

> **這一冊給第一次部署的人。** 從「一台什麼都還沒動的主機」走到「護理站登得進去、平板釘住、交接完成」，
> 中間每一步都寫出要打什麼、畫面上應該看到什麼、沒看到時怎麼辦。
> 讀完不需要先懂 Docker 或 Git，第 0.4 節的名詞表就夠了。
>
> 同一套步驟也用來做**模擬部署**：在自己的開發機上照走一次。兩者不同的地方，每一步都用
> **🧪 模擬部署** 的方框標出來；沒有方框的步驟，兩者一字不差。
>
> 這一冊是第十一、十二、十三冊（現行路線）的**新手導讀版**：步驟相同、順序相同，
> 每一步標題後面都註明對應的原步驟編號（例如「＝W-10」）。原冊寫得比較精簡、出錯處置比較齊全；
> 兩者衝突時，以原冊為準，規則的真本仍是《[部署規範](../requirements/deployment-spec.md)》v3.0。
>
> `.env` 的逐項填法另成兩冊：[第十四冊之一（實際部署）](14a-env-hospital.md)、[第十四冊之二（模擬部署）](14b-env-simulation.md)。

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
模擬部署做過一次，實際部署當天你只是在另一台機器上重複一遍已經熟悉的動作。

### 0.2 標記怎麼看

> 🧪 **模擬部署**：像這樣的方框，寫的是模擬部署時**要改做什麼或可以跳過什麼**。實際部署時略過不看。

> ⚠️ 這種方框是**兩者都要注意**的警告。

每一步照舊分三塊：**做什麼**、**怎麼知道成功了**、**可能怎麼壞**。
**「怎麼知道成功了」那一塊沒看到，就是沒成功**——不要因為「好像沒出錯」就往下。

### 0.3 兩者不同的地方，一張表看完

| 項次 | 實際部署 | 🧪 模擬部署 | 在哪一步 |
|---|---|---|---|
| 機器 | 院內主機 | 你的開發機 | — |
| Git 與 Docker | 資訊室已裝好，**不准自己裝** | 自己裝 | N-04 |
| 根目錄（`$root`） | `D:\hd-tablet-care` | `C:\hd-sim` | N-08 |
| 問資訊室的問題清單 | 至少一週前寄出 | 不必 | N-02 |
| Docker Desktop 設定、防毒排除 | 逐項檢查，改動要資訊室同意 | 看一眼即可 | N-05 |
| 三個連接埠 | 資訊室登記給你的 | 自己挑沒人用的：`13000`、`18080`、`18081` | N-07 |
| 部署金鑰 | 主機上產生，登記到 GitHub | 開發機上另產生一把，同樣登記 | N-09、N-19 |
| 位址 | 主機名稱或院內 IP | 護理端用 `localhost`；平板那一條用開發機的區網 IP | N-11 |
| APK 簽章用途 | `hospital` | `dev` | N-11 |
| 平板 | 院內的平板 | 開發用的 Android 手機 | 第 7 節 |
| 驗收工具 | 不跑（主機上沒有、也不准裝 Node.js） | 多跑三支 `verify:iteration… --live` | N-30 |
| 重新開機測試 | **必做**，決定這條路線在院內能不能用 | 驗不出院內的情形，可略 | N-18 |
| 備份送往另一台機器 | 院方負責，要當場確認 | 不必 | N-17 |
| 做完之後 | 交接，服務留著跑 | **撤除乾淨**，下一次才又是「從零」 | 第 9 節 |

### 0.4 先認識十個名詞

| 名詞 | 一句話 |
|---|---|
| **PowerShell** | Windows 內建的指令視窗。本冊每一條指令都在這裡打。開法：開始選單輸入 `PowerShell` → 按「Windows PowerShell」 |
| **Git**、**clone** | Git 是管理程式碼版本的工具；`git clone` 是把 GitHub 上的程式碼整份複製到這台機器 |
| **tag** | 程式碼某一版的名字，例如 `v0.2.0`。**部署一律部署某個 tag，不部署分支**：分支會一直變，tag 不會 |
| **部署金鑰** | 一把只給這台機器、只能讀一個 repo 的鑰匙。私鑰留在機器上，只把公鑰交給 repo 管理者登記 |
| **Docker**、**映像檔**、**容器** | Docker 把程式和它需要的一切打包成**映像檔**（像安裝光碟），跑起來的那一份叫**容器**。同一個映像檔可以跑出好幾個容器 |
| **docker compose** | 照 repo 裡的 `docker-compose.yml` 一次把好幾個容器開起來、關掉。**本系統的容器一律由它產生，不准自己手動開** |
| **資料卷** | Docker 管理的一塊儲存空間。**資料庫就放在這裡**，檔案總管看不到它是正常的 |
| **繫結掛載** | 把主機上的某個資料夾借給容器用。本系統**只准兩個**：設定目錄與備份目錄 |
| **`.env`** | 一份「變數名稱＝值」的文字檔，存這次部署的設定（埠、位址、密碼）。怎麼填見第十四冊之一、之二 |
| **連接埠（埠）** | 同一台機器上區分不同服務的號碼。本系統要三個：後端、護理端、病人端 |

### 0.5 本系統在主機上長什麼樣

```
院內主機（或 🧪 開發機）
│
├─ $root\                      本系統自己的資料夾（實際 D:\hd-tablet-care，模擬 C:\hd-sim）
│   ├─ repo\                   本系統的程式碼（git clone，切到 tag）
│   ├─ hd-kiosk-shell\         外殼 App 的程式碼（git clone）
│   ├─ config\.env             設定 ← 第十四冊之一、之二教你填
│   │   └─ ai-gateway\config.yaml   AI 閘道的設定（N-28）
│   └─ backups\                備份（院方從這裡送往另一台機器）
│
├─ Docker 資料卷
│   ├─ hd-tablet-care-data     資料庫
│   └─ hd-tablet-care-keys     院內 CA、伺服器憑證、APK 簽章金鑰、下載頁
│
└─ 容器（docker compose 產生）
    ├─ api            後端           ← 後端埠
    ├─ nurse-web      護理端網頁     ← 護理端埠 ← 護理站的瀏覽器
    ├─ patient-web    病人端網頁     ← 病人端埠 ← 平板上的外殼 App（HTTPS）
    ├─ shell-builder  建 APK（一次性，平時不跑）
    └─ ai-gateway     AI 閘道（首波不接模型，只讓它就位）
```

### 0.6 要花多久

| 段落 | 大約時間 | 備註 |
|---|---|---|
| 第 1～2 節：主機準備 | 30 分鐘 | 🧪 模擬部署第一次要裝 Docker Desktop，另加 30～60 分鐘 |
| 第 3～5 節：程式碼、設定、建置、啟動 | 40 分鐘 | 建置約 10 分鐘 |
| 第 6 節：備份、重新開機 | 20 分鐘 | |
| 第 7 節：外殼 App 與平板 | 60～90 分鐘 | `shell-builder` 第一次要下載約 1.5 GB，**網路慢時可能更久** |
| 第 8 節：AI 閘道 | 15 分鐘 | |
| 第 9 節：交接或撤除 | 30 分鐘 | |

**每一步都計時，寫進《[部署演練紀錄](../notes/deployment-drills.md)》。** 下一次估時間就靠它。

---

## 1. 動手之前

### N-01 約好人（＝總覽第 3 節）

**做什麼**：至少一週前，用訊息向資訊室確認：「當天 X 點到 Y 點，需要一位能登入那台主機、有管理員權限的同仁全程在旁。」
另約護理長或指定的護理師，交接時要在。

**怎麼知道成功了**：有具體的人名與時段。「到時候看看」要當成沒約到。

> 🧪 **模擬部署**：跳過。

---

### N-02 把問題清單寄給資訊室（＝W-03）

**做什麼**：把[第十一冊 W-03](11-compose.md) 那張表的七個問題寄出去，答覆寫進演練紀錄。其中最要緊的三題：

1. 本系統可以用哪**三個連接埠**？（0922 看過 3000 已被佔用）
2. **斷電之後誰開機、誰登入？** Docker Desktop 要有人登入才會起來
3. GitHub、Docker Hub、npm 這些網站，主機是不是常態連得到？經不經代理伺服器？

**怎麼知道成功了**：每一題都有答覆，或寫明「未答覆」與對方是誰。

> 🧪 **模擬部署**：跳過。

---

### N-03 確認要交的 tag 已經模擬部署過，而且在 GitHub 上（＝W-01、W-02、Y-01）

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
| 演練紀錄 | 這個 tag 的模擬部署每一格都填了，沒有 ✗ |

**可能怎麼壞**：tag 不在清單上 → 它還沒推到 GitHub，`git push origin <tag>`。**沒模擬部署過的 tag 不准拿去院內。**

> 🧪 **模擬部署**：這一步做的就是「準備一個要測的 tag」。tag 要先推上 GitHub，
> 因為模擬部署是從 GitHub 全新 clone，不是用你的工作目錄。外殼 repo 那個 tag 也一樣要推上去。

---

## 2. 主機這一層

> ⚠️ **從這裡開始，所有指令都在「要部署的那台機器」的 PowerShell 裡打**：實際部署是院內主機，🧪 模擬部署是開發機。
> **不要自己開任何容器，不要下 `docker run -v`、`-p`。** 0922 就是這樣失敗的（[第十冊](10-first-visit.md) F-01、F-02）。

### N-04 確認 Git 與 Docker 能用（＝W-04）

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
| `git --version` | 一個版本號，例如 `git version 2.4x…` |
| `docker version` | `Client` 與 `Server` 兩段都有版本號 |
| `docker info …` | `<版本> linux x86_64`，**中間一定要是 `linux`** |
| `docker compose version` | `v2` 以上 |

**可能怎麼壞**

| 症狀 | 處置 |
|---|---|
| `failed to connect to the docker API at npipe:…` | Docker Desktop 沒在跑。從開始選單開啟，等左下角變綠再重試 |
| 中間是 `windows` 不是 `linux` | 工作列右下角的 Docker 圖示按右鍵 → Switch to Linux containers |
| `git` 或 `docker` 找不到 | 實際部署：**問資訊室，不要自己裝**，那是院方的變更流程。模擬部署：見下面方框 |
| 只有 `docker-compose`（有連字號）能用 | 舊版。實際部署請資訊室處理；模擬部署更新 Docker Desktop |

> 🧪 **模擬部署**：開發機沒有的話自己裝，裝完**重新開機**再做一次本步驟。
> 1. **Git for Windows**：到 `git-scm.com` 下載，安裝選項全部用預設值。
> 2. **Docker Desktop**：到 `docker.com` 下載 Docker Desktop for Windows，安裝時勾「Use WSL 2」。
>    第一次開啟會要你接受使用條款；若提示要更新 WSL，照畫面指示在 PowerShell 打 `wsl --update`。
> 3. 開發機上已經有 Node.js 也沒關係，但**這一輪部署裡不准用到它**（驗收的 N-30 例外）。

---

### N-05 Docker Desktop 的設定與防毒排除（＝W-05）

**做什麼**：開 Docker Desktop → 右上角齒輪（Settings），逐項看。**同一台機器有別的專案在用時只看不改**，要改先知會資訊室。

| # | 位置 | 應該是 |
|---|---|---|
| 1 | General → Start Docker Desktop when you sign in | 勾 |
| 2 | General → Send usage statistics | 不勾 |
| 3 | Software updates → Automatically check for updates | 不勾（見下方說明） |
| 4 | Resources → Advanced → Disk image location | **把路徑抄下來** |

> **第 3 項找不到勾選框？** 那是因為這台的 Docker Desktop 是從 **Microsoft Store** 裝的，設定頁只會叫你去市集管理，沒有勾選框可以勾（第十冊 F-16，院內主機就是這種情形）。
> 這時更新是否自動發生，由**市集的自動更新設定**決定，而市集設定管的是**整台主機的所有 App**，只能交給資訊室決定。你要做的是：
> 1. 在演練紀錄寫下「更新由市集管理，現行設定＝＿＿」。
> 2. 問資訊室能不能改成手動更新；不行的話，至少請他們避開透析時段。
>
> 不處理的後果：Docker Desktop 更新時引擎會重新啟動，容器會中斷一段時間，碰上透析班時平板就會斷線；版本也會在沒走院方變更流程的情況下自己換掉。

然後請資訊室把第 4 項那個資料夾加入防毒的排除清單。

**怎麼知道成功了**：四項抄進演練紀錄；防毒排除清單裡看得到那個資料夾。

**可能怎麼壞**：設定是灰的（院方鎖住）→ 記下來，由資訊室決定。

> 🧪 **模擬部署**：看一眼、抄下來即可，防毒排除不必做。

---

### N-06 確認連得出去（＝W-06）

建置時要從網路下載東西。先確認這些網站都連得到，免得建到一半才失敗。

**做什麼**

```powershell
Test-NetConnection github.com -Port 22
Test-NetConnection github.com -Port 443
Test-NetConnection registry-1.docker.io -Port 443
Test-NetConnection auth.docker.io -Port 443
Test-NetConnection production.cloudflare.docker.com -Port 443
Test-NetConnection deb.debian.org -Port 80
Test-NetConnection registry.npmjs.org -Port 443
Test-NetConnection binaries.prisma.sh -Port 443
```

**怎麼知道成功了**：每一條最後都是 `TcpTestSucceeded : True`。

**可能怎麼壞**

| 症狀 | 處置 |
|---|---|
| 22 是 `False`、443 是 `True` | 之後的部署金鑰改走 443，做法在 N-09 的出錯表 |
| 經代理伺服器，全部 `False` | 改用 `curl.exe -I https://registry.npmjs.org` 測；Docker 要在 Settings → Resources → Proxies 設代理 |
| 有幾個不通 | 請資訊室補齊再往下 |

> 🧪 **模擬部署**：開發機通常全部通，照做一次確認即可。

---

### N-07 確認三個連接埠沒人用（＝W-07）

**做什麼**：把要用的三個埠填進下面這一條再打（實際部署填資訊室給的，🧪 模擬部署填 `13000,18080,18081`）：

```powershell
Get-NetTCPConnection -State Listen | Where-Object LocalPort -in 13000,18080,18081 | Select-Object LocalPort, OwningProcess
```

**怎麼知道成功了**：**什麼都沒印出來**，代表三個埠都沒人在用。

**可能怎麼壞**：印出了某個埠 → 有別的程式在用它。實際部署：換一個並**回報資訊室登記**；模擬部署：自己換一個沒人用的。
**不要用 `-p` 之類的方式把埠對到別處**，埠只寫在 `.env` 裡。

> 🧪 **模擬部署**：三個埠記下來，N-11 填 `.env` 時要用。

---

## 3. 取得程式碼

### N-08 建立資料夾，並設好「開工三行」

**做什麼**

先決定根目錄。實際部署用 `D:\hd-tablet-care`；🧪 模擬部署用 `C:\hd-sim`。

```powershell
$root = "D:\hd-tablet-care"          # 🧪 模擬部署改成 C:\hd-sim
$cfg  = "$root\config\.env"
New-Item -ItemType Directory -Force "$root\config", "$root\backups" | Out-Null
Get-ChildItem $root
$cfg
```

前兩行設定兩個變數，本冊之後一直會用到：`$root` 是根目錄，`$cfg` 是 N-11 要建立的 `.env` 的位置。
本冊之後的 `docker compose` 指令都寫成 `--env-file $cfg`，而且都在 `$root\repo` 底下打。

**怎麼知道成功了**：列出 `backups`、`config` 兩個資料夾，最後一行印出 `D:\hd-tablet-care\config\.env`（🧪 模擬部署是 `C:\hd-sim\config\.env`）。
`repo` 現在還沒有是對的，下一步 clone 才會產生；`.env` 也還沒有，N-11 才會建立。

**不可以放的地方**：OneDrive 之類的雲端同步資料夾、網路磁碟機、RAM 磁碟、`C:\Users\<帳號>\` 底下的桌面／文件／下載。

> ⚠️ **開工三行**：PowerShell 關掉再開，`$root`、`$cfg` 就不見了。**之後每開一個新的 PowerShell 視窗，先打這三行**
> （第三行要等 N-10 clone 完才有那個資料夾）：
>
> ```powershell
> $root = "D:\hd-tablet-care"          # 🧪 模擬部署改成 C:\hd-sim
> $cfg  = "$root\config\.env"
> cd $root\repo
> ```
>
> 看到 `couldn't find env file`，十次有九次是忘了打這三行。

---

### N-09 產生本系統 repo 的部署金鑰（＝W-09）

這把金鑰讓這台機器可以從 GitHub **讀**本系統的程式碼，別的什麼都不能做。

**做什麼**

1. 產生金鑰。三行照抄，不用改任何字：

   ```powershell
   New-Item -ItemType Directory -Force $HOME\.ssh
   ssh-keygen -t ed25519 -C "hd-tablet-care@$(hostname)" -f $HOME\.ssh\hd-tablet-care -N '""'
   Get-Content $HOME\.ssh\hd-tablet-care.pub
   ```

   第一行是先建好 `.ssh` 資料夾：沒用過 SSH 的新帳號沒有這個資料夾，`ssh-keygen` 不會自己建。
   資料夾已經在的話，這一行什麼都不會動。
   `$(hostname)` 會自動換成這台機器的名字（想先看是什麼，單獨打 `hostname`），只當註記用，讓管理者在 GitHub 上認得這把金鑰是哪台機器的。

2. 把印出來的那**一整行**（`ssh-ed25519 AAAA… hd-tablet-care@…`）交給 repo 管理者。
   管理者到 GitHub 的 `hd-tablet-care` repo → **Settings → Deploy keys → Add deploy key** 貼上，**不要勾 Allow write access**。
3. 開 SSH 的設定檔。兩行照抄：

   ```powershell
   if (-not (Test-Path $HOME\.ssh\config)) { New-Item -ItemType File $HOME\.ssh\config }
   notepad $HOME\.ssh\config
   ```

   第一行是先建好沒有副檔名的空檔：直接讓記事本建新檔，它會自作主張存成 `config.txt`，ssh 就讀不到。
   檔案已經在的話，這一行什麼都不會動，原本的內容不會被清掉。
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
| 22 埠不通（N-06） | 設定檔那一段的 `HostName` 改成 `ssh.github.com`，並加一行 `    Port 443` |
| `Could not resolve hostname github-hd-tablet-care:` 後面接一串亂碼（那是 big5 的「無法辨別這台主機。」） | ssh 沒讀到設定檔，幾乎都是記事本存成了 `config.txt`（漏打第 3 步第一行）。`Get-ChildItem $HOME\.ssh` 看得到 `config.txt` 就打 `Rename-Item $HOME\.ssh\config.txt config`，再重跑 `ssh -T` |

> 🧪 **模擬部署**：開發機上**另產生一把**，不要拿你平常推程式碼的那把 SSH 金鑰頂替——
> 那樣走的就不是院內那條路。登記時標題寫「模擬部署（開發機）」，之後可以一直留著重複使用。
> 開發機的 `$HOME\.ssh\config` 裡如果已經有別的段落，加在最後面即可，不要動原本的。

---

### N-10 clone 程式碼，切到 tag（＝W-10）

**做什麼**（`<tag>` 換成 N-03 確認過的那一個，例如 `v0.2.0`）

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
| `error: pathspec '<tag>' did not match` | tag 沒推上去，回 N-03 |
| `destination path … already exists` | 那個資料夾已經有東西。實際部署：先弄清楚是誰放的，**不要直接刪**；模擬部署：上一輪沒撤除乾淨，照第 9.2 節撤除 |

> 🧪 **模擬部署**：一定要從 GitHub **全新 clone** 到 `C:\hd-sim\repo`，不要複製你的工作目錄，也不要在工作目錄裡做。

---

## 4. 設定

### N-11 由範本填 `.env`（＝W-11、Y-03）

**做什麼**

```powershell
Copy-Item $root\repo\deploy\hospital.env.example $cfg
notepad $cfg
```

**逐項怎麼填，照另外兩冊**：

- 實際部署 → [第十四冊之一 · 實際部署的 `.env`](14a-env-hospital.md)
- 🧪 模擬部署 → [第十四冊之二 · 模擬部署的 `.env`](14b-env-simulation.md)

外殼 App 那三項（`HD_SHELL_SRC_DIR`、`HD_SHELL_SIGNING`、`MDM_KIOSK_BASE_URL`）**現在就一起填好**，
雖然外殼第 7 節才做——每一條 `docker compose` 指令都會檢查它們。

**怎麼知道成功了**

```powershell
docker compose --env-file $cfg config --quiet
```

**什麼都沒印出來**就是對的。

**可能怎麼壞**

| 症狀 | 處置 |
|---|---|
| `required variable HD_… is missing a value: 請設定 …` | 冒號後面寫的就是還缺什麼，補上 |
| `couldn't find env file` | `$cfg` 沒設（N-08 的開工三行），或路徑打錯 |

> ⚠️ **不要拿 repo 根目錄的 `.env.example` 來填。** 那一份是日常開發（`npm run dev`）用的，變數名稱不同。
> 部署用的範本只有 `deploy\hospital.env.example` 這一份。

---

### N-12 建立兩個資料卷（＝W-12）

**只在第一次部署時做。**

**做什麼**

```powershell
docker volume create hd-tablet-care-data
docker volume create hd-tablet-care-keys
docker volume ls
```

**怎麼知道成功了**：清單裡看得到這兩個名字。

> 🧪 **模擬部署**：做之前先 `docker volume ls` 看一眼，**清單裡不該已經有 `hd-tablet-care-` 開頭的**。
> 有的話是上一輪留下來的，照第 9.2 節撤除再回來，否則就不是「從零」。

---

## 5. 建置與啟動

### N-13 建置映像檔（＝W-13）

**做什麼**

```powershell
docker compose --env-file $cfg build
```

第一次約十分鐘，畫面會一直捲動，是正常的。

**怎麼知道成功了**：最後出現 `Image hd-tablet-care:<tag> Built`；再打 `docker images hd-tablet-care` 看得到這個 tag。

**可能怎麼壞**

| 症狀 | 處置 |
|---|---|
| `failed to resolve source metadata for docker.io/library/node` | 連不到 Docker Hub，回 N-06 |
| `npm error code ETIMEDOUT` 或 `ECONNRESET` | 網路不穩，再打一次同一條指令；已下載的部分會沿用 |
| `pull access denied for hd-tablet-care` | 打成 `up` 了。先 `build` |

---

### N-14 建立資料庫（＝W-14）

**做什麼**（一整行，不要斷開）

```powershell
docker compose --env-file $cfg run --rm --no-deps api node apps/api/scripts/prisma-cli.mjs migrate deploy --schema apps/api/prisma/schema.prisma
```

**怎麼知道成功了**：中間出現 `SQLite database hd.db created at file:/data/hd.db`（第一次才會有），最後一行 `All migrations have been successfully applied.`

**可能怎麼壞**：錯誤訊息裡提到 `binaries.prisma.sh` → 映像檔建壞了，回 N-13 重建。**不要為了讓它下載而開任何網路例外。**

---

### N-15 啟動（＝W-15）

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
| `address already in use` | 埠被佔了，回 N-07 |
| `bind source path does not exist` | `HD_BACKUP_DIR` 或 `HD_CONFIG_DIR` 指的資料夾不存在，回 N-08 |

---

### N-16 確認它是對的（＝W-16）

**做什麼**（`<後端埠>` 換成你的；🧪 模擬部署是 `13000`）

```powershell
curl.exe -s http://localhost:<後端埠>/api/health
docker compose --env-file $cfg logs api --tail 30
```

然後用瀏覽器開護理端：實際部署在**護理站的電腦**開 `http://<主機名稱>:<護理端埠>`；🧪 模擬部署在開發機開 `http://localhost:18080`。

**怎麼知道成功了**

| 看什麼 | 應該是 |
|---|---|
| health | `{"status":"ok",…}` 開頭 |
| 日誌「已連線至 SQLite」那一行 | 有 `synchronous=FULL` |
| 日誌「版本標記」那一行 | 後面寫著 `（正式環境設定）`——模擬部署也是這樣，**這是對的** |
| 日誌「伺服器時區」 | `Asia/Taipei`，而且時間是現在 |
| 瀏覽器 | 出現登入頁；用 `.env` 的 `SUPER_ADMIN_WORK_ID` 與 `SUPER_ADMIN_INITIAL_PASSWORD` 登入，**被要求改密碼** |

**可能怎麼壞**

| 症狀 | 處置 |
|---|---|
| 頁面開得了，登入時轉圈後失敗 | `.env` 的 `HD_PUBLIC_API_URL` 或 `CORS_ORIGINS` 寫錯。改完：前者要 `build` 再 `up -d`（它寫在網頁檔案裡），後者只要 `up -d` |
| 沒有帳號可以登入 | `SUPER_ADMIN_*` 沒填。補上再 `up -d`，**資料庫不必重建** |
| 護理站的電腦開不到頁面，主機自己開得到 | 防火牆或網段，找資訊室（Q-27）。**不要自己關防火牆** |

> 改完密碼之後，實際部署要把新密碼交給院方指定的人保管，`.env` 裡的初始密碼可以清空（清空後 `up -d`）。

---

## 6. 備份與重新開機

### N-17 備份一次，並證明還原得回來（＝W-17）

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

> 🧪 **模擬部署**：做到還原成功即可，不必送往任何地方。

---

### N-18 重新開機測試（＝W-18）

`restart: unless-stopped` 只管 Docker 起來之後；Docker Desktop 要有人登入 Windows 才會啟動。**這一條決定這條路線在院內能不能用。**

**做什麼**：重新開機 → 照院方平常的方式登入（或不登入，看 N-02 的答覆）→ 等三分鐘 → 開一個新的 PowerShell，先輸入開工三行，再：

```powershell
docker compose --env-file $cfg ps
curl.exe -s http://localhost:<後端埠>/api/health
```

**怎麼知道成功了**：三個服務自己回到 `Up`、health 正常，**中間沒有人手動開 Docker Desktop**。

**沒過的話**：記下實況（有沒有自動登入、Docker Desktop 有沒有起來），寫進交接文件，**不要在現場自己改院方的登入設定**。

> 🧪 **模擬部署**：可以跳過。開發機是你自己登入的，驗不出院內「沒人登入」的情形。

---

## 7. 外殼 App 與平板

這一節做兩件事：在主機上把外殼 App（APK）建出來，然後讓平板從院內的下載頁安裝、釘住。
**私鑰全程不離開主機**，平板也不必接電腦。

### N-19 外殼 repo 的部署金鑰與 clone（＝Y-02）

外殼 App 在另一個 repo（`hd-kiosk-shell`），要**另一把**部署金鑰——一把部署金鑰只能給一個 repo。

**做什麼**

1. 產生並交出公鑰，登記到**外殼 repo** 的 Settings → Deploy keys，不勾 Allow write access：

   ```powershell
   ssh-keygen -t ed25519 -C "hd-kiosk-shell@$(hostname)" -f $HOME\.ssh\hd-kiosk-shell -N '""'
   Get-Content $HOME\.ssh\hd-kiosk-shell.pub
   ```

2. `notepad $HOME\.ssh\config`（N-09 已經建好這個檔，直接開就好），在最後再加一段：

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

**怎麼知道成功了**：`ssh -T` 印出 `Hi 94sh09sh19sh/hd-kiosk-shell!…`（**是 `hd-kiosk-shell`，不是 `hd-tablet-care`**）；`git tag` 列得出 N-03 看到的那一版。

| 症狀 | 處置 |
|---|---|
| `ssh -T` 印出的是 `hd-tablet-care` | 設定檔兩段的 `IdentityFile` 寫反，或少了 `IdentitiesOnly yes` |
| `Permission denied (publickey)` | 公鑰登記到本系統的 repo 去了 |
| `ssh -T` 成功，`git clone` 卻出現 `Connection reset by … port 22` | 網路把連線切斷，不是金鑰的問題。`Test-Path $root\hd-kiosk-shell` 是 `True` 就先刪掉殘留的資料夾，再重跑 clone；還是被切，就把設定檔這一段的 `HostName` 改成 `ssh.github.com`、加一行 `Port 443`，重跑 `ssh -T` 再 clone（見[第十一冊](11-compose.md)） |

> 🧪 **模擬部署**：與 N-09 相同，開發機上另產生一把、標題註明模擬部署。

---

### N-20 建 `shell-builder` 的映像檔（＝Y-04）

**做什麼**

```powershell
docker compose --env-file $cfg --profile shell build shell-builder
```

第一次要下載 Android SDK 與 Gradle，約 1.5 GB。**這一步要連外，而且可能很久**（開發機上實測過單一個檔案下載 6.6 分鐘）。

**怎麼知道成功了**：最後幾行有「✓ 外殼 v0.x.x（…，契約第 1 版）已準備好，相依已下載」。

| 症狀 | 處置 |
|---|---|
| `外殼 repo 的 clone 裡沒有 tag vX.Y.Z` | `git -C $root\hd-kiosk-shell fetch --tags`，再建一次 |
| 提到版本、契約版本不符，或「外殼原始碼裡有指向院外的網址」 | **開發端的問題，不在現場修。** 停手，回開發端 |
| `dl.google.com`、`services.gradle.org`、`maven.google.com` 逾時 | 對外連線被擋，請資訊室開通（Q-32） |
| 停在 `gradle.zip` 很久 | 它會自己重試、失敗會自己結束。結束後再打一次同一條，已完成的部分不會重下載 |

---

### N-21 建 APK（第一次會產生金鑰）（＝Y-05）

**做什麼**

```powershell
docker compose --env-file $cfg --profile shell run --rm shell-builder
```

**怎麼知道成功了**：第一次會印出「這一次新產生：院內 CA 伺服器憑證（<主機>） APK 簽章金鑰（…）」，
接著是 APK 檔名與**三個 SHA-256**（檔案、簽章憑證、院內 CA）。**把三個 SHA-256 抄下來**，實際部署要寫進交接文件。

**再打一次同一條指令**，這次要看到「**金鑰全部沿用，這一次沒有產生任何新的金鑰**」，而且簽章憑證的 SHA-256 與第一次相同。

| 症狀 | 處置 |
|---|---|
| `MDM_KIOSK_BASE_URL 要以 https:// 開頭` | `.env` 改成 `https://`，見子手冊 |
| `這個金鑰資料卷是「dev」用的，設定卻是「hospital」` | **停手。** 院內主機上出現了開發用的金鑰，或 `.env` 抄了開發機那一份 |
| `有 CA 憑證卻沒有私鑰` 之類 | 資料卷不完整。**不要刪掉重來**，照第十二冊第 6 節從備份還原 |

> 🧪 **模擬部署**：第一次那行會寫「APK 簽章金鑰（開發用）」，是對的。

---

### N-22 備份金鑰，並核對還原得回來（＝Y-06）

**做什麼**

```powershell
docker compose --env-file $cfg --profile shell run --rm shell-builder keys-backup
docker compose --env-file $cfg --profile shell run --rm shell-builder keys-verify
```

**怎麼知道成功了**：第一條印出「已備份：備份目錄/keys/hd-keys-<時間>.tar.gz」；第二條每一項都 ✓，最後「還原得回來」。

> ⚠️ **這份檔案裡有私鑰。** 實際部署：與資料庫備份一樣由院方送往院內另一台機器，**不得出院、不得寄給開發端**。
> 金鑰遺失的後果是**每一台平板都要解除安裝重裝**。

---

### N-23 讓病人端改走 HTTPS（＝Y-07）

**做什麼**

```powershell
docker compose --env-file $cfg restart patient-web
docker compose --env-file $cfg logs patient-web --tail 5
```

**怎麼知道成功了**：日誌有「（HTTPS；HTTP 只留外殼下載頁）」。
主機的瀏覽器開 `http://localhost:<病人端埠>/shell/` 看得到下載頁；開 `http://localhost:<病人端埠>/` 會被轉到 `https://` 並跳出憑證警告——
**這是對的**：主機的瀏覽器不認得院內 CA，只有平板上的外殼 App 認得。

| 症狀 | 處置 |
|---|---|
| 日誌是「找不到伺服器憑證…暫以 HTTP 提供」 | N-21 還沒成功，或做完沒重新啟動 `patient-web` |

---

### N-24 平板連得到主機（＝Y-08）

**做什麼**：拿一台平板（或手機）連上**與平板實際使用時相同的 Wi-Fi**，用瀏覽器開 `http://<平板要連的位址>:<病人端埠>/shell/`。

**怎麼知道成功了**：看得到下載頁。

| 症狀 | 處置 |
|---|---|
| 主機自己開得到，平板開不到 | Windows 防火牆擋了連入，或那個 Wi-Fi 網段到不了主機。**找資訊室**，不要自己關防火牆 |

> 🧪 **模擬部署**：手機和開發機要連**同一個 Wi-Fi**，位址是開發機的區網 IP（第十四冊之二會教你查）。手機開不到時：
> 1. Windows「設定 → 網路和網際網路 → Wi-Fi → 這個網路的內容」，網路設定檔類型改成**私人**。
> 2. 仍不行的話，用**系統管理員身分**開 PowerShell，只對私人網路開放病人端那一個埠：
>    ```powershell
>    New-NetFirewallRule -DisplayName "hd-sim patient 18081" -Direction Inbound -Protocol TCP -LocalPort 18081 -Profile Private -Action Allow
>    ```
>    撤除時（第 9.2 節）記得刪掉這條規則。
> 3. 學校或公司的 Wi-Fi 常常擋裝置互連，改用手機熱點或家裡的 Wi-Fi。

---

### N-25 在護理端註冊平板（＝Y-09）

**做什麼**：護理端 → **裝置管理** → **註冊新平板**。畫面會出現一個**佈建 QR code** 與一行文字網址。

> ⚠️ **這兩樣只顯示一次。** 這個畫面先不要關，拿著平板做完 N-26、N-27 再離開。

**怎麼知道成功了**：畫面上的網址以 `https://` 開頭。不是的話，`.env` 的 `MDM_KIOSK_BASE_URL` 還是 `http://`，改好後 `up -d api` 再重新註冊。

---

### N-26 平板的系統設定並安裝 App（＝Y-10、Y-11）

**做什麼**

1. 平板設定裝置 PIN，關閉「新增使用者」。
2. 設定 → 安全性 → **螢幕固定**：開啟，並勾選「解除固定前要求 PIN」。（各廠牌位置略有不同，可在設定裡搜尋「固定」）
3. 平板的瀏覽器開 `http://<平板要連的位址>:<病人端埠>/shell/`，按「下載 App」，安裝。系統問是否允許瀏覽器安裝不明來源的應用程式時，允許。

**怎麼知道成功了**：平板上多了「透析照護平板」這個 App。

| 症狀 | 處置 |
|---|---|
| 「套件與現有套件衝突」 | 這台裝過**另一把金鑰簽的版本**（例如模擬部署時裝的開發版）。先解除安裝再裝 |
| 「應用程式未安裝」，而且沒裝過 | 下載不完整，重新下載一次 |

---

### N-27 第一次開啟並釘住（＝Y-12、Y-13）

**做什麼**

1. 開啟「透析照護平板」→ 按「**掃描 QR code**」→ 允許相機 → 對準 N-25 畫面上的 QR code。三欄會自動填好，**核對序號與這台平板的標籤一致**。
   （沒有相機時手動填：主機位址填 `MDM_KIOSK_BASE_URL` 的值，序號與金鑰照 N-25 畫面上的）
2. 按「儲存並啟動」→ 系統問「要固定這個應用程式嗎」→ 按「確定」。
3. 回到護理端 → 裝置管理，等 15～30 秒。
4. 在平板上**解除一次固定**（輸入 PIN），30 秒內護理端要變成「已跳出」；再開啟 App 釘回去。

**怎麼知道成功了**

| 在哪裡看 | 應該是 |
|---|---|
| 平板 | 病人端的等待畫面，**沒有任何憑證警告**；按上一頁、首頁、多工鍵都離不開 |
| 護理端「固定狀態」 | 固定中（解除時變成已跳出） |
| 護理端「外殼版本」 | 版本正常，底下有版本號 |

**把序號與床號的對應記下來。** 實際部署首波只佈建實際會用到的兩三台（DEP-36），每台做一次 N-25～N-27。

| 症狀 | 處置 |
|---|---|
| 「主機位址不是 https:// 開頭」 | 回 N-25 的處置 |
| 一片空白或「網頁無法使用」 | 位址錯或 N-23 沒做。平板「設定 → 應用程式 → 透析照護平板 → 儲存空間 → 清除資料」，重新佈建 |
| 上方出現琥珀色「……版本不相容」 | 下載頁的 APK 與系統版本對不上，見第十二冊第 5 節 |

> 🧪 **模擬部署**：用開發用的 Android 手機代替平板。做完之後手機上的 App 要**解除安裝**，
> 免得日後拿這支手機裝院內版時衝突（N-26 的第一列）。

---

## 8. AI 閘道：讓它就位

首波 AI 功能是關的（DEP-29）。這一節只讓閘道就位、確認它清楚回報「設定還沒填」，**不接任何模型**。

### N-28 放 AI 閘道的設定檔（＝Z-20）

**做什麼**

```powershell
New-Item -ItemType Directory -Force $root\config\ai-gateway | Out-Null
Copy-Item services\ai-gateway\config.hospital.example.yaml $root\config\ai-gateway\config.yaml
```

範本的 `base_url` 與 `model` 刻意留空，**保持空白**。**絕對不要填實驗室的位址**——那是把資料往院外送。

---

### N-29 建置並啟動閘道（＝Z-21、Z-22）

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
| `找不到設定檔` | N-28 的路徑不對，必須是 `config\ai-gateway\config.yaml` |

> ⚠️ 閘道起過之後，**日後更新時 `build` 與 `up -d` 都要加 `--profile ai`**，閘道才會跟著換新版。
> 接上正式 GPU API 是 Q-07 有答案之後的事，見[第十三冊](13-ai-gateway.md) Z-23。

---

## 9. 收尾

### 9.1 實際部署：冒煙測試與交接

| 步驟 | 做什麼 | 詳細在 |
|---|---|---|
| 冒煙測試 | 在護理站的電腦走一次主線：登入 → 建病人 → 建排班 → 指派平板 → 解除綁定 → 稽核查得到。**測試資料用虛構的**，交接時說明哪幾筆是測試資料、誰負責清掉 | [第四冊](04-onsite.md) H-16 |
| 總覽螢幕 | 在指定位置開啟護理端總覽，確認不會休眠 | 第四冊 H-18 |
| 現場教學 | 護理長、值班護理師、資訊室各教一次，**講完當場讓對方自己做一次** | 第四冊 H-20 |
| 交接文件 | 見下表 | 第四冊 H-21 |
| 當天晚上 | 把演練紀錄補完 | 第四冊 H-24 |

交接文件至少要有（第一行寫「**首波試用、不是全單位上線**」）：

| 項次 | 內容 |
|---|---|
| 位置 | `$root` 底下四個資料夾各放什麼；兩個資料卷的名字 |
| 版本 | 部署的 tag；外殼版本 |
| 連接埠 | 三個埠與登記狀況 |
| 帳號 | 初始管理員的工作 ID（**密碼由院方自行保管**） |
| 啟停 | `docker compose --env-file <設定目錄>\.env stop`／`up -d`，在 `repo` 資料夾底下打 |
| 備份 | 每日幾點、落在哪、誰送往另一台機器 |
| 外殼 | N-21 的三個 SHA-256；金鑰備份的檔名 |
| 信任邊界 | 能登入這台主機的人一律可信任（DEP-38）；日後帳號政策改變要重新評估 |
| 已知限制 | AI 關閉、N-18 若沒過的實況、尚未佈建的平板 |
| 聯絡方式 | 出事找誰 |

### 9.2 🧪 模擬部署：驗收，然後撤除乾淨

#### N-30 跑三支驗收（＝第十一冊第 7 節、第十二冊第 7 節）

**這一步是驗收，不是部署步驟**，也是整輪裡唯一准用 Node.js 的地方。
在**平常開發的工作目錄**（不是 `C:\hd-sim\repo`）打：

```powershell
npm run verify:iteration11 -- --live --env-file C:\hd-sim\config\.env
npm run verify:iteration12 -- --live --env-file C:\hd-sim\config\.env
npm run verify:iteration13 -- --live --env-file C:\hd-sim\config\.env
```

**怎麼知道成功了**：三支都全部 ✓。第一支會執行 `down -v` 再 `up -d`，驗證「資料卷不會被 `-v` 刪掉」，**這是刻意的**。

然後依第十一冊第 7 節，再各走一次**更新**（W-19，打一個測試 tag）與**回退**（W-20）。每一步的結果填進《[部署演練紀錄](../notes/deployment-drills.md)》。

#### N-31 撤除

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
Remove-NetFirewallRule -DisplayName "hd-sim patient 18081"
```

（最後一條只有 N-24 真的加過防火牆規則時才需要，要用系統管理員身分打。）
手機上的「透析照護平板」解除安裝。部署金鑰與 `$HOME\.ssh\config` 那兩段**可以留著**，下一輪繼續用。

**怎麼知道成功了**：`docker volume ls` 與 `docker images` 都看不到 `hd-tablet-care` 開頭的東西；`C:\hd-sim` 不存在。

> ⚠️ **撤除只准在模擬部署做。** 實際部署的撤除會刪掉整個透析中心的紀錄，要院方書面同意，照[第八冊](08-shutdown.md)與第十一冊第 8 節。

---

## 10. 之後的日常

| 要做什麼 | 照哪裡 |
|---|---|
| 換新版（更新） | [第十一冊](11-compose.md) W-19。排在非透析時段，更新後第一個班次要有人在 |
| 新版有問題，退回上一版 | 第十一冊 W-20。**更新後寫進去的資料會一起消失**，要在累積新資料之前決定 |
| 暫停或停用服務 | 第十一冊第 8 節 |
| 換外殼版本、調高最低可用版本 | [第十二冊](12-shell.md) Y-14、Y-15 |
| 每年核對金鑰備份 | 第十二冊第 6 節 |
| 接上正式 GPU API | [第十三冊](13-ai-gateway.md) Z-23 |
| 出錯了，這本沒寫到 | 第十一冊第 9 節、第十二冊第 8 節、第十三冊第 6 節、[第六冊](06-troubleshooting.md) |

---

## 11. 什麼時候當場停手

下列任一種出現，**停手、記錄、擇日**。硬幹的代價比重來高得多（詳見[總覽](index.md)第 6 節）：

- 有人說「把網路開一下就好了」「手動開個容器比較快」「把整顆磁碟掛進去」
- 資料庫只能放在雲端同步資料夾或人人讀得到的共用資料夾
- 防毒排除當天加不了，有人說「先跑跑看」
- N-21 出現「這個金鑰資料卷是『dev』用的」
- 冒煙測試沒過，但已經到了下班時間

停手時做三件事：`docker compose --env-file $cfg stop` 把服務停掉、把現況寫進演練紀錄、當場講清楚下一次需要什麼。

---

## 附錄：步驟編號對照

| 本冊 | 原冊 | | 本冊 | 原冊 |
|---|---|---|---|---|
| N-01 | 總覽第 3 節 | | N-17 | W-17 |
| N-02 | W-03 | | N-18 | W-18 |
| N-03 | W-01、W-02、Y-01 | | N-19 | Y-02 |
| N-04 | W-04 | | N-20 | Y-04 |
| N-05 | W-05 | | N-21 | Y-05 |
| N-06 | W-06 | | N-22 | Y-06 |
| N-07 | W-07 | | N-23 | Y-07 |
| N-08 | W-08 | | N-24 | Y-08 |
| N-09 | W-09 | | N-25 | Y-09 |
| N-10 | W-10 | | N-26 | Y-10、Y-11 |
| N-11 | W-11、Y-03 | | N-27 | Y-12、Y-13 |
| N-12 | W-12 | | N-28 | Z-20 |
| N-13 | W-13 | | N-29 | Z-21、Z-22 |
| N-14 | W-14 | | N-30 | 第十一冊第 7 節、第十二冊第 7 節 |
| N-15 | W-15 | | N-31 | 第十一冊第 8 節 |
| N-16 | W-16 | | | |

在演練紀錄裡寫「卡在 N-21」或「卡在 Y-05」都可以，兩者指的是同一件事。

---

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|

[← 回部署手冊總覽](index.md)
