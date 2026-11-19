# 從零部署本系統（第 2 份，V-01～V-05）

上層文件：《[從零部署本系統](ref-fresh-install.md)》

> **狀態：現行（常備參考）。** 改寫自第十五冊（1117）；編號 `V-xx`（沿用第十五冊），每一步下面註明對應的 `N-xx` 與 `W-xx`／`Y-xx`／`Z-xx`。1118 照步驟順序拆成七份，這是第 2 份；🧪／🏥／📍 標記的意思見第 1 份 0.2 節。

## 摘要

- 第 1 節 動手之前：V-01 約好資訊室與護理長、V-02 把問題清單寄給資訊室（已有答案的整理與還沒答的）、V-03 確認要交的 tag 已模擬部署過而且在 GitHub 上
- 沒模擬部署過的 tag 不准拿去院內；`v0.5.0` 是附註標籤，commit 要用 `<tag>^{commit}` 查
- 第 2 節起所有指令都在要部署的那台機器打，不自己開任何容器；換一台主機時先確認 0922 的容器不在
- V-04 確認 Git 與 Docker（`docker info` 中間要是 `linux`）；沒有 Git 時 🏥 請資訊室裝或經同意後裝 x64 Setup
- V-05 Docker Desktop 的四項設定、查防毒是哪一套與排除清單；1116 起防毒排除不擋上線

---

## 1. 動手之前

### V-01 約好人

對應：N-01、《[進院通則](ref-visit-rules.md)》（舊總覽第 3 節）

**做什麼**：至少一週前，用訊息向資訊室確認：「當天 X 點到 Y 點，需要一位能登入那台主機、有管理員權限的同仁全程在旁。」另約護理長或指定的護理師，交接時要在。

**怎麼知道成功了**：有具體的人名與時段。「到時候看看」要當成沒約到。

> 🧪 **模擬部署**：跳過。

---

### V-02 把問題清單寄給資訊室

對應：N-02、W-03

**做什麼**：把《[從零部署本系統之一](ref-fresh-install-detail.md)》W-03 那張表寄出去，答覆寫進演練紀錄。

已經有答案、不必再問的：

| 題 | 答案 | 來自 |
|---|---|---|
| 連接埠 | `13000`、`18080`、`18081` | 0930 資訊室 |
| 主機對外連線 | 常態、沒有限制 | 0930 資訊室（Q-32） |
| Docker 版本 | Docker 29.3.1、Compose v5.1.1（1001 再看一次，沒變） | 0922、1001 現場 |
| 主機上有沒有 Git | 原本沒有，1001 現場裝了 2.56.0 | 1001 現場 |
| 防毒 | Windows Defender，運作中，排除清單是空的 | 1001 現場 |
| 主機的 IP | **固定的**；1029 第三次進院已把 `<主機>` 換成 IP（實體有線網卡、DHCP 否） | 1007（Q-27 第 12 題）、1029 現場 |
| 斷電之後誰登入 | **護理長**：護理端出現斷線警示後到主機重新登入；不設開機自動登入 | 1007（Q-27 第 4 題） |
| Docker Desktop 的使用統計 | **關掉**（第三次進院在 V-05 關） | 1007（Q-27 第 9 題） |
| Microsoft Store 的自動更新 | **先不改**，實際使用發現嚴重影響再改 | 1007（Q-27 第 10 題） |
| 防毒排除擋不擋上線 | **不擋**：不加也能跑，出現現象再請資訊室加（V-05） | 1116 使用者決定 |

**還沒答、最要緊的**（1116 為止仍未答的，在《[院內主機現況與未完成事項](ref-status.md)》）：

1. ~~**護理站與平板用哪個名稱或 IP 連這台主機？IP 能不能固定？**~~（**1007 已答：IP 是固定的**；1029 換成 IP，護理站與手機都連得到）
2. **Docker 的資料夾能不能加入 Defender 的排除清單、誰加？**（1001 查到排除清單是空的；1116 定為不擋上線，仍沒加）
3. **1001 Docker 三次查不到 Docker Hub 的網域**（`production.cloudfront.docker.com`、`auth.docker.io`），院內 DNS 對這些網域穩不穩？（見 V-06）
4. ~~**斷電之後誰開機、誰登入？**~~（**1007 已答：護理長**，見上表）
5. 本系統放在 `C:\hd\hd-tablet-care`，院方同不同意？備份資料夾由誰、多久送往另一台機器？（1029 仍沒問到）
6. 1001 現場裝的 Git，要不要補走院方的變更流程？（1029 仍沒問到）
7. ~~Docker Desktop 的 **Send usage statistics** 能不能關？**Microsoft Store 的自動更新能不能改成手動？**~~（**1007 已答**：使用統計關掉、市集自動更新先不改，見上表）

**怎麼知道成功了**：每一題都有答覆，或寫明「未答覆」與對方是誰。

> 🧪 **模擬部署**：跳過。

---

### V-03 確認要交的 tag 已經模擬部署過，而且在 GitHub 上

對應：N-03、W-01、W-02、Y-01

**做什麼**：在開發機的工作目錄（平常寫程式的那個）打：

```powershell
git ls-remote --tags origin
git rev-parse "<tag>^{commit}"
git show <tag>:services/shell-builder/shell.pin
```

**怎麼知道成功了**

| 看什麼 | 應該是 |
|---|---|
| 第一條的清單 | 看得到要交的 tag |
| 第二條 | 與模擬部署時用的是同一個 commit |
| 第三條 | `SHELL_TAG=` 那一版外殼，在 GitHub 的外殼 repo（`hd-kiosk-shell`）Tags 頁看得到 |
| 演練紀錄 | **這個 tag** 的模擬部署每一格都填了，沒有 ✗ |

第二條寫成 `<tag>^{commit}`：`v0.5.0` 是附註標籤，直接打 `git rev-parse v0.5.0` 印出的是**標籤物件**（`0ef8663…`），不是 commit（`8575505…`）；`git ls-remote` 的清單裡兩個都會列，帶 `^{}` 的那一行才是 commit。

**可能怎麼壞**：tag 不在清單上 → 它還沒推到 GitHub，`git push origin <tag>`。**沒模擬部署過的 tag 不准拿去院內**——出發前才打的 tag 一定沒有模擬部署過。

> 📍 **1001**：本系統 `v0.3.0`（`9992721`）、外殼 `v0.3.0`（`44b4d62`）。當時院內主機上跑的就是這一版。

現在（1116 起）：院內主機跑本系統 `v0.5.0`（標籤物件 `0ef8663`、commit `8575505`），`shell.pin` 仍釘外殼 `v0.3.0`、契約第 1 版；外殼 1001 起沒換過。

> 🧪 **模擬部署**：這一步做的就是「準備一個要測的 tag」。tag 要先推上 GitHub，因為模擬部署是從 GitHub 全新 clone，不是用你的工作目錄。外殼 repo 那個 tag 也一樣要推上去。

---

## 2. 主機這一層

> ⚠️ **從這裡開始，所有指令都在「要部署的那台機器」的 PowerShell 裡打**：🏥 實際部署是院內主機，🧪 模擬部署是開發機。 **不要自己開任何容器，不要下 `docker run -v`、`-p`。** 0922 就是這樣失敗的（《[第一次進院紀錄（0922，失敗）](record-1-0922.md)》F-01、F-02）；1001 照手冊沒有開，就沒有重演。

> ⚠️ 🏥 **實際部署：做 V-04 之前，先確認 0922 留下的容器 `dialysis_system_v0` 不在了。** 院內那一台 1001 有沒有收過**沒有記到**，1029 J-05 確認已經不在。換一台主機時照《[收掉 0922 留下的東西](visit-2-system-cleanup.md)》L-01 看一眼：只剩標題列就是不在了，接著做 L-07；還在的話照 L-02 起收掉。那個容器掛著整顆 C 槽，沒收掉不開始部署。🧪 模擬部署不必做。

### V-04 確認 Git 與 Docker 能用

對應：N-04、W-04

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
| `docker` 找不到 | 🏥 實際部署：**問資訊室，不要自己裝**。🧪 模擬部署：見下面方框 |
| 只有 `docker-compose`（有連字號）能用 | 舊版。🏥 請資訊室處理；🧪 更新 Docker Desktop |

**沒有 Git 時**

🏥 實際部署：**請資訊室裝，或經他們同意後由你裝**，並在演練紀錄寫下是誰裝的、誰同意的。那是院方的變更流程。

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

> 📍 **1001**：院內主機原本**沒有 Git**，現場照上面裝了 x64 Setup，版本 `2.56.0.windows.1`。誰裝、資訊室是否同意沒有記到，下一次要補問。 Docker 29.3.1（Client 與 Server 相同）、Compose v5.1.1，與 0922 相同。

> 🧪 **模擬部署**：開發機沒有的話自己裝，裝完**重新開機**再做一次本步驟。
>
> 1. **Git for Windows**：照上面的裝法。
> 2. **Docker Desktop**：到 `docker.com` 下載 Docker Desktop for Windows，安裝時勾「Use WSL 2」。第一次開啟會要你接受使用條款；若提示要更新 WSL，照畫面指示在 PowerShell 打 `wsl --update`。
> 3. 開發機上已經有 Node.js 也沒關係，但**這一輪部署裡不准用到它**（驗收的 V-31 例外）。

---

### V-05 Docker Desktop 的設定與防毒排除

對應：N-05、W-05

**第一部分：Docker Desktop 的四項設定**

開 Docker Desktop → 右上角齒輪（Settings），逐項看。**同一台機器有別的專案在用時只看不改**，要改先知會資訊室。

| # | 位置 | 應該是 |
|---|---|---|
| 1 | General → Start Docker Desktop when you sign in | 勾 |
| 2 | General → Send usage statistics | 不勾（見下方說明） |
| 3 | Software updates → Automatically check for updates | 不勾（見下方說明） |
| 4 | Resources → Advanced → Disk image location | **把路徑抄下來**，第二部分要用 |

> **第 3 項找不到勾選框？** 這台的 Docker Desktop 是從 **Microsoft Store** 裝的，設定頁只會叫你去市集管理（《[第一次進院紀錄（0922，失敗）](record-1-0922.md)》F-16，院內主機就是這種情形）。更新是否自動發生，由**市集的自動更新設定**決定，而那管的是**整台主機的所有 App**，只能交給資訊室決定。在演練紀錄寫下「更新由市集管理，現行設定＝＿＿」，問資訊室能不能改成手動；不行的話至少請他們避開透析時段。

> **第 2 項是開著的？** 院內主機 0922 就是開著的。它是**整台主機**的設定，同機另一個專案也受影響，~~**答覆前只看不改**~~（Q-27 第 9 題）。 **1007 答覆可以關：把它取消勾選**，按右下角的套用按鈕（依版本叫 **Apply** 或 **Apply & restart**；後者會讓 Docker Desktop 重新啟動、容器跟著中斷一下約一分鐘後自己回來，挑沒有透析的時段做；沒回來就 `docker compose --env-file $cfg up -d`），演練紀錄寫「使用統計已關，＿＿月＿＿日」。第 3 項（市集自動更新）**1007 答覆先不改**：照舊只看、記下現行設定。

**第二部分：防毒查哪一套、排除清單裡有什麼**（只看不改）

要請資訊室把第 4 項那個資料夾加入防毒的排除清單。開口之前先查清楚兩件事：

1. **主機上跑的是哪一套防毒**：

   ```powershell
   Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntivirusProduct |
     Select-Object displayName, productState, @{n='hex';e={'{0:X6}' -f $_.productState}}
   ```

   每一套防毒列成一行，看 `hex` 那一欄**中間兩碼**：`10` 或 `11` 是**正在運作**，排除要在這一套裡做；`00` 或 `01` 是裝了但沒在運作。例：`061100` 是正在運作，`060100` 是已關閉。

2. **排除清單裡有什麼**。正在運作的是 Windows Defender（`displayName` 為 `Windows Defender` 或 `Microsoft Defender Antivirus`）時， **用系統管理員身分開的 PowerShell**（開始選單對「Windows PowerShell」按右鍵 →「以系統管理員身分執行」，或開始 → 打 `powershell` → `Ctrl+Shift+Enter`）打：

   ```powershell
   Get-MpPreference | Select-Object -ExpandProperty ExclusionPath
   ```

   每一行是一個排除的路徑；**什麼都沒印出來**就是沒有任何排除。正在運作的是第三方防毒（趨勢、賽門鐵克等）時，PowerShell 看不到它的排除清單，直接問資訊室。

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
| 資訊室當天加不了 | **照樣往下**（1116 改），寫進交接文件的「防毒」那一列 |

> 📍 **1001**：Windows Defender，`061100`（正在運作）；排除清單**是空的**——Docker 的資料夾沒有被排除。 **加上排除之前，這台主機不得輸入真實病人資料**（舊總覽第 6 節：SQLite 被即時掃描鎖住的錯誤是間歇性的，會在一個月後才爆開）。

**1116 更新：防毒排除不再擋上線。** 資料庫在 Docker 的具名資料卷裡，實體是 Docker 資料夾裡的一個虛擬磁碟檔（`ext4.vhdx`），Defender 的即時掃描看不到裡面的 `hd.db`；所以上面那條「加上排除之前不得輸入真實病人資料」在容器路線不成立（照架構推的，**沒有在開著即時掃描的主機上實測過**）。照樣請資訊室加，加不了就照樣往下，出現現象再加；沒排除時可能看到的現象與處置在《[第五次進院（1116）任務二 · 本系統換版上線之一：詳細版](visit-5-system-detail.md)》SY-03。院內主機 1116 照這個決定沒加（《[第五次進院紀錄](record-5-1116.md)》SR-11）。

> 🧪 **模擬部署**：看一眼、抄下來即可，防毒排除不必做。想先熟悉指令可以在開發機上跑一次，同樣只看不改。

---

上一份：《[從零部署本系統](ref-fresh-install.md)》｜下一份：《[從零部署本系統（第 3 份，V-06～V-11）](ref-fresh-install-3.md)》｜[部署手冊目錄](index.md)

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|
| 1118 | 2026-11-18 | 首次定版。1118 照每份約 300 行的上限由《從零部署本系統》拆出，內容與步驟編號不動 |

[← 回部署手冊目錄](index.md)
