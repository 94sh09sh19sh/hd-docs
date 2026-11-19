# 第三次進院（1029）· 接手 v0.3.0、換成 IP、換版之七：開發機才做的演練（第 0 節、I-01～I-05）

上層文件：《[第三次進院（1029）· 接手 v0.3.0、換成 IP、換版](visit-3-system.md)》

> - 狀態：**已照做 1029（第一輪），凍結**。第一輪做到 J-30，I-13～I-15 沒做，判定 `v0.4.0` **還不能**帶進院；結果見《[部署演練紀錄](../notes/deployment-drills.md)》第 11.1 節與《[第三次進院紀錄（1029，部分成功）](record-3-1029.md)》O-02（沒補演練就帶進院）
> - 從哪幾份舊冊改寫（1117）：第十七冊（1028 新增、1111 首次定版）第 0 節（0.6 節除外）、第 1、2、5、6 節與附錄；第 3、4 節（每一步的模擬差異）改寫進主文件與《[…之一～之六：詳細版](visit-3-system-detail.md)》各步的 🧪；0.6 節（1116 那一輪照當時的第二十冊演練 `v0.4.0` → `v0.5.0`）收在《[第五次進院（1116）任務二 · 本系統換版上線](visit-5-system.md)》
> - 編號：`I-xx`（沿用第十七冊）；中間照做的是主文件的 `J-xx`
> - 1116 起，進院前的開發機演練改照那一趟進院冊主文件的 🧪 行做（1116 是《[第五次進院（1116）任務一 · 抓取腳本上線](visit-5-api.md)》與《第五次進院（1116）任務二 · 本系統換版上線》），開發機由開發端先準備成主機的樣子；這一冊保留為第三次進院前的紀錄

開發機演練共三份（之七～之九），這一份是第 0、1 節；第 2～4 節在《[…之八：開發機才做的演練（I-06～I-12、照主文件做 J-04～J-30）](visit-3-system-rehearsal-2.md)》，第 5、6 節與附錄在《[…之九：開發機才做的演練（I-13～I-17、附錄）](visit-3-system-rehearsal-3.md)》；詳細版是之一～之六。

## 摘要

- 第三次進院前，在開發機上把主文件整趟演練一次；編號 `I-xx`，沒通過 I-16 判定的 tag 不准帶進院
- 這一份是第 0 節讀之前與第 1 節準備（I-01～I-05）
- 0.1 節這一輪要證明的七件事；0.2 節第 3、4 節拿印好的詳細版照做 J-04～J-30，指令以詳細版為準
- 0.3 節要準備的東西、0.4 節要花多久、0.5 節規矩（只用 Git 與 Docker、一律全新 clone、只用虛構資料）
- 第 1 節準備：打 tag、確認工具、確認沒有上一輪留下的東西、兩把部署金鑰、查開發機的名稱與 IP
- 全程約 6～8 小時，第 2 節到 J-29 同一天做完、中途不換 Wi-Fi、開發機不睡眠

> **這一冊給誰**：第三次進院之前，要在自己的開發機上先把整趟演練一次的人。沒做過模擬部署、沒碰過 Docker 也看得懂。**做的時候，旁邊放一份印好的詳細版。**
>
> **為什麼要演練**：1001 帶進院的 `v0.3.0` 是出發前才打的 tag，沒有先在開發機上走過一次（《[第二次進院紀錄（1001）之一：為什麼登不進去](record-2-1001-login.md)》R6）；院內卡住的登入問題，開發機上的舊式模擬部署也練不到（R3）。這一次照部署規範 DEP-22「每一個要交給院方的 tag，都先在開發機上照手冊走一次」，而且**走的就是院內要走的那條路**。
>
> **院內那一趟不是從零部署**，是「接手一台裝著 `v0.3.0`、登不進去的主機」（主文件）。所以這一冊分三段：
>
> 1. **把開發機變成 1001 離院時的院內主機**：裝 `v0.3.0`、主機位址用名稱、故意把放行名單填錯，讓它和院內一樣登不進去（第 2 節）
> 2. **拿詳細版的紙本，從 J-04 照做到 J-30**，每一步的 🧪 寫模擬部署要改什麼（第 3、4 節）
> 3. **只有模擬部署才做的驗收**：模擬院方 API、三支驗收、退回舊版，然後撤除乾淨（第 5、6 節）
>
> 走完、紀錄填完、判定通過（I-16），這個 tag 才准帶進院。

> **公開範圍**：開發機的 IP、主機名稱、`.env` 的值不寫進任何會上站的文件，結果只寫進《[部署演練紀錄](../notes/deployment-drills.md)》第 11 節，而且只寫「對不對、花多久、錯誤原文」，不寫值。

---

## 0. 讀之前

### 0.1 這一輪要證明什麼

| # | 要證明的事 | 在哪一步看到 |
|---|---|---|
| 1 | 主文件與詳細版的每一條指令，照抄就跑得動 | J-04～J-30 每一步 |
| 2 | 1001 那種登不進去的狀態，用 J-09～J-14 修得好 | I-12 看到壞、J-14 看到好 |
| 3 | 從 `v0.3.0` 換到新 tag，19 個遷移套得上、資料留得住、登入不受影響 | J-18、J-19 |
| 4 | 新版出問題時，詳細版附錄二退得回 `v0.3.0`，而且舊版照樣登得進去 | I-15 |
| 5 | 院方 API 的探測工具在新 tag 裡、跑得起來；院內設定擋得住模擬的位址 | J-26、I-13 |
| 6 | 外殼重簽憑證之後，平板（或手機）佈建得起來 | J-12、J-27～J-29 |
| 7 | 每一步要花多久 | 每一步都計時，詳細版 0.3 節的估計以這裡量到的為準 |

### 0.2 這一冊與主文件、詳細版怎麼一起用

- **第 2 節**院內不必做（院內主機本來就是那個樣子），指令全寫在這一冊
- **第 3、4 節**拿**印出來的詳細版**照做 J-04～J-30：那份紙本就是要帶進院的那一份，演練時在紙上用筆把看不懂、打錯、寫錯的地方圈起來。每一步模擬部署要改什麼寫在那一步的「🧪 開發機演練」，**指令以詳細版為準**
- 代稱（`$root`、`<名稱>`、`<IP>`、`<新 tag>`、護理站的電腦、平板的 Wi-Fi、資訊室與護理長）怎麼換，見主文件開頭「整趟共通的差異」那張表
- 代稱**連同 `<`、`>` 一起換掉**（`http://<IP>:18080` → `http://192.0.2.20:18080`），1029 第一輪就在 J-11 把角括號一起打進去過

### 0.3 要準備的東西

| 東西 | 備註 |
|---|---|
| 開發機（Windows），裝好 Git for Windows 與 Docker Desktop | 沒裝的話照《[從零部署本系統](ref-fresh-install-2.md)》V-04 的方框裝，裝完重新開機 |
| 印好的詳細版 | 第 3、4 節照它做 |
| 印好的演練紀錄第 11 節 | 邊做邊填 |
| 一支 Android 手機，或醫師給的暫用平板（Galaxy Tab S6 Lite） | 用暫用平板最好：J-29 能順便看字型大小 1.1 會不會撐破畫面（[暫用平板紀錄](../notes/interim-tablet.md)第 6 節第 1 項）。**不要原廠重設** |
| 一個手機與開發機都連得上、而且准許裝置互連的 Wi-Fi | 學校或公司的 Wi-Fi 常擋裝置互連，改用家裡的 Wi-Fi 或手機熱點 |
| 一整個下午 | 第 2 節到 J-29 中途不換 Wi-Fi（換了 IP 就變，要重簽憑證） |

### 0.4 要花多久

| 段落 | 大約時間 |
|---|---|
| 第 1 節：準備 | 30 分鐘 |
| 第 2 節：重現 1001 | 60～90 分鐘（`shell-builder` 的映像檔第一次要下載約 1.5 GB，約 30 分鐘） |
| 第 3 節：J-04～J-21 | 2～2.5 小時 |
| 第 4 節：J-22～J-30 | 60～90 分鐘 |
| 第 5 節：模擬部署才做的驗收 | 60 分鐘 |
| 第 6 節：撤除 | 15 分鐘 |

### 0.5 規矩

- **全程只用 Git 與 Docker。** 開發機上的 Node.js 不准在第 2～4 節出現；第 5 節 I-14 是唯一例外（那是驗收，不是部署）
- **一律從 GitHub 全新 clone 到 `C:\hd-sim`**，不准用平常寫程式的工作目錄，也不准複製它
- **只用虛構資料**
- 每一步開始與結束各記一次時間；錯誤訊息抄原文、抄到最後一行

---

## 1. 準備

### I-01 選定要帶的版本、打 tag、推上 GitHub

**做什麼**（在平常寫程式的工作目錄）

1. 確認工作目錄是乾淨的、在最新的 `master`：

   ```powershell
   git status --short
   git switch master
   git pull
   ```

2. 確認最近一次全量回歸之後，程式沒有再改過。`<回歸的 commit>` 是《[技術端進度報告](../reports/progress-technical.md)》第 10 節「最近一次執行」寫的那一個：

   ```powershell
   git log --oneline <回歸的 commit>..HEAD -- apps packages services Dockerfile docker-compose.yml deploy
   ```

   **什麼都沒印**才對（只有 `docs/` 改過沒關係）。印出東西的話，先跑那幾個迭代的驗收，或重跑一次全量回歸。
3. 打 tag 並推上 GitHub（`<新 tag>` 例如 `v0.4.0`）：

   ```powershell
   git tag -a <新 tag> -m "第三次進院"
   git push origin <新 tag>
   git ls-remote --tags origin
   git show <新 tag>:services/shell-builder/shell.pin
   ```

**怎麼知道成功了**：`ls-remote` 的清單看得到 `<新 tag>` 與 `v0.3.0`；`shell.pin` 是 `SHELL_TAG=v0.3.0`（外殼不換版）。把 `<新 tag>` 與 `git rev-parse <新 tag>` 的 commit 寫進紀錄。1029 第一輪是 `v0.4.0`（`514461a`）。

| 症狀 | 處置 |
|---|---|
| `shell.pin` 不是 `v0.3.0` | 外殼換版了，主文件沒有寫外殼更新的步驟。先停下來，補上《[平板與外殼 App](ref-tablet-2.md)》Y-14 再演練 |
| 演練到一半發現程式要修 | 修好、跑過驗收，**打下一個 tag**（例如 `v0.4.1`），從 I-03 重新演練。**推上去的 tag 不要移動或刪掉重打**：院內與紀錄都靠 tag 名字對版本 |

---

### I-02 開發機的工具與網路（＝V-04、V-06）

**做什麼**

```powershell
git --version
docker version
docker info --format "{{.ServerVersion}} {{.OSType}} {{.Architecture}}"
docker compose version
docker pull node:20-bookworm-slim
docker pull eclipse-temurin:17-jdk-jammy
```

**怎麼知道成功了**

| 指令 | 應該看到 |
|---|---|
| `git --version` | 一個版本號 |
| `docker version` | `Client` 與 `Server` 兩段都有版本號 |
| `docker info …` | `<版本> linux x86_64`，中間一定是 `linux` |
| `docker compose version` | `v2` 以上 |
| 兩條 `docker pull` | 最後是 `Status: Downloaded newer image for …` 或 `Status: Image is up to date for …` |

| 症狀 | 處置 |
|---|---|
| `failed to connect to the docker API at npipe:…` | Docker Desktop 沒開。開始選單開啟，等左下角變綠 |
| 中間是 `windows` | 工作列的 Docker 圖示按右鍵 → Switch to Linux containers |
| `no such host` | 再打一次；仍不行就換個網路 |

---

### I-03 確認開發機上沒有上一輪留下的東西（＝V-13 方框、V-32）

**做什麼**

```powershell
docker volume ls --filter name=hd-tablet-care
docker ps -a --filter name=hd-tablet-care
docker images "hd-tablet-care*"
Test-Path C:\hd-sim
Get-NetTCPConnection -State Listen | Where-Object LocalPort -in 13000,18080,18081 | Select-Object LocalPort, OwningProcess
```

**怎麼知道成功了**：前三條只有標題列、第四條 `False`、最後一條什麼都沒印。

**不是的話**：上一輪沒撤除乾淨，先照第 6 節 I-17 撤除再回來。最後一條印出東西 → 有別的程式（例如 `npm run dev`）佔著那個埠，先關掉它。

---

### I-04 兩把部署金鑰（＝V-10、V-20）

模擬部署要用**專門的部署金鑰**走院內那條路，不拿平常推程式碼的那把頂替。

**做什麼**：先試試以前做過模擬部署時留下的金鑰還能不能用：

```powershell
ssh -T github-hd-tablet-care
ssh -T github-hd-kiosk-shell
```

| 印出 | 意思 |
|---|---|
| `Hi 94sh09sh19sh/hd-tablet-care! You've successfully authenticated…` 與 `Hi 94sh09sh19sh/hd-kiosk-shell! …` | 兩把都在，往下 |
| `Could not resolve hostname github-hd-tablet-care` | 沒做過，照下面建 |
| `Permission denied (publickey)` | 金鑰在，但 GitHub 上的登記被拿掉了，把 `.pub` 重新登記 |

**沒做過的話**：

1. 產生兩把金鑰，把印出來的兩整行公鑰分別登記到 GitHub 兩個 repo 的 **Settings → Deploy keys → Add deploy key**，標題寫「模擬部署（開發機）」，**不勾 Allow write access**：

   ```powershell
   New-Item -ItemType Directory -Force $HOME\.ssh
   ssh-keygen -t ed25519 -C "hd-tablet-care@$(hostname)" -f $HOME\.ssh\hd-tablet-care -N '""'
   ssh-keygen -t ed25519 -C "hd-kiosk-shell@$(hostname)" -f $HOME\.ssh\hd-kiosk-shell -N '""'
   Get-Content $HOME\.ssh\hd-tablet-care.pub
   Get-Content $HOME\.ssh\hd-kiosk-shell.pub
   ```

2. 開 SSH 設定檔（第一行先建好沒有副檔名的空檔，免得記事本存成 `config.txt`）：

   ```powershell
   if (-not (Test-Path $HOME\.ssh\config)) { New-Item -ItemType File $HOME\.ssh\config }
   notepad $HOME\.ssh\config
   ```

   在最後加上這兩段，存檔：

   ```
   Host github-hd-tablet-care
       HostName github.com
       User git
       IdentityFile ~/.ssh/hd-tablet-care
       IdentitiesOnly yes

   Host github-hd-kiosk-shell
       HostName github.com
       User git
       IdentityFile ~/.ssh/hd-kiosk-shell
       IdentitiesOnly yes
   ```

3. 再打一次本步驟最上面兩條。第一次會問 `Are you sure you want to continue connecting (yes/no)?`，打 `yes`。

**怎麼知道成功了**：兩條各印出對的 repo 名稱（**不是同一個**）。

| 症狀 | 處置 |
|---|---|
| 第二條印出的是 `hd-tablet-care` | 兩段的 `IdentityFile` 寫反，或少了 `IdentitiesOnly yes` |
| `Could not resolve hostname …` 後面接一串亂碼 | 記事本存成了 `config.txt`：`Rename-Item $HOME\.ssh\config.txt config` |

---

### I-05 查開發機的兩個位址：模擬的 `<名稱>` 與 `<IP>`（＝V-08）

院內主機 1001 用的是**名稱**，這一次要換成 **IP**。開發機上兩個都要有，才練得到「換」。

**做什麼**

```powershell
hostname
ipconfig
Resolve-DnsName (hostname) | Select-Object Name, IPAddress
```

| 抄什麼 | 從哪裡 | 這一冊叫它 |
|---|---|---|
| 電腦名稱 | `hostname` 印的那一行 | `<名稱>` |
| Wi-Fi 的 IPv4 位址 | `ipconfig` 的「無線區域網路介面卡 Wi-Fi」那一段，**不是** `vEthernet (WSL)`、`vEthernet (Default Switch)` | `<IP>` |

**怎麼知道成功了**：兩個都抄了；`Resolve-DnsName` 查得到自己的名稱（開發機自己查自己一定查得到）。手機查不到開發機的名稱是**正常的**，這正是院內平板會遇到的事，所以第三次進院要換成 IP。

> ⚠️ 開發機**同時接著有線網路與 Wi-Fi**（例如另外接了一台旅行路由器）時，`<IP>` 要抄**手機連的那個網路**的網卡，抄錯張網卡，J-12 簽出來的憑證平板就連不上。用不到的那條，演練期間先拔掉最省事。

> ⚠️ **從現在起到 J-29 做完，不要換 Wi-Fi、不要讓開發機睡眠。** IP 變了就要照《[`.env` 怎麼填之一：開發機演練](ref-env-simulation.md)》重簽憑證。

---

下一份：《[…之八：開發機才做的演練（I-06～I-12、照主文件做 J-04～J-30）](visit-3-system-rehearsal-2.md)》；主文件：《[第三次進院（1029）· 接手 v0.3.0、換成 IP、換版](visit-3-system.md)》

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|
| [1118](https://94sh09sh19sh.github.io/hd-docs/1118/deployment/visit-3-system-rehearsal/) | 2026-11-18 | 首次定版。1117 部署手冊整套重寫時由舊冊改寫而成（舊冊號見目錄最後的對照），步驟編號不變；1118 照每份約 300 行的上限拆檔，後段移到同一套的下一份 |

[← 回部署手冊目錄](index.md)
