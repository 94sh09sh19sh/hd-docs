# 第十七冊 · 第三次進院前的模擬部署（新手版）

版本：v0.1　文件狀態：草案（1028 新增）　編號：`I-xx`　**做的時候，旁邊放一份印好的第十八冊**

> **這一冊給誰**：第三次進院之前，要在自己的開發機上先把整趟演練一次的人。沒做過模擬部署、沒碰過 Docker 也看得懂。
>
> **為什麼要演練**：1001 帶進院的 `v0.3.0` 是出發前才打的 tag，沒有先在開發機上走過一次（第十五冊之三 R6）；院內卡住的登入問題，開發機上的舊式模擬部署也練不到（R3）。這一次照部署規範 DEP-22「每一個要交給院方的 tag，都先在開發機上照手冊走一次」，而且**走的就是院內要走的那條路**。
>
> **院內那一趟不是從零部署**，是「接手一台裝著 `v0.3.0`、登不進去的主機」（[第十八冊](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/18-third-visit/index.md)）。所以這一冊分三段：
>
> 1. **把開發機變成 1001 離院時的院內主機**：裝 `v0.3.0`、主機位址用名稱、故意把放行名單填錯，讓它和院內一樣登不進去（第 2 節）
> 1. **拿第十八冊的紙本，從 J-04 照做到 J-29**，每一步旁邊寫模擬部署要改什麼（第 3、4 節）
> 1. **只有模擬部署才做的驗收**：模擬院方 API、三支驗收、退回舊版，然後撤除乾淨（第 5、6 節）
>
> 走完、紀錄填完、判定通過（I-16），這個 tag 才准帶進院。
>
> **公開範圍**：開發機的 IP、主機名稱、`.env` 的值不寫進任何會上站的文件，結果只寫進《[部署演練紀錄](https://94sh09sh19sh.github.io/hd-docs/latest/notes/deployment-drills/index.md)》第 11 節，而且只寫「對不對、花多久、錯誤原文」，不寫值。

______________________________________________________________________

## 摘要

- 第三次進院前，在開發機上把第十八冊整趟演練一次；編號 `I-xx`，沒通過的 tag 不准帶進院
- 第 1 節準備：打 tag、確認工具、部署金鑰、查開發機的名稱與 IP
- 第 2 節**重現 1001**：裝 `v0.3.0`、位址用名稱、放行名單故意填錯，親眼看到 `Failed to fetch`
- 第 3、4 節**拿第十八冊照做**：J-04～J-29 每一步的模擬部署差異列在一張表，指令以第十八冊為準
- 第 5 節模擬部署才做的：模擬院方 API 與 DEP-46 的阻擋、三支 `verify --live`、退回 `v0.3.0` 的演練
- 第 6 節撤除乾淨；附錄是 I、J 與原冊的步驟對照
- 全程約 6～8 小時，第 2～4 節同一天做完、中途不換 Wi-Fi

## 0. 讀之前

### 0.1 這一輪要證明什麼

| #   | 要證明的事                                                         | 在哪一步看到                                        |
| --- | ------------------------------------------------------------------ | --------------------------------------------------- |
| 1   | 第十八冊的每一條指令，照抄就跑得動                                 | 第 3、4 節每一步                                    |
| 2   | 1001 那種登不進去的狀態，用第十八冊第 3 節修得好                   | I-12 看到壞、J-14 看到好                            |
| 3   | 從 `v0.3.0` 換到新 tag，19 個遷移套得上、資料留得住、登入不受影響  | J-18、J-19                                          |
| 4   | 新版出問題時，附錄二退得回 `v0.3.0`，而且舊版照樣登得進去          | I-15                                                |
| 5   | 院方 API 的探測工具在新 tag 裡、跑得起來；院內設定擋得住模擬的位址 | J-26、I-13                                          |
| 6   | 外殼重簽憑證之後，平板（或手機）佈建得起來                         | J-12、J-27～J-29                                    |
| 7   | 每一步要花多久                                                     | 每一步都計時，第十八冊 0.3 節的估計以這裡量到的為準 |

### 0.2 這一冊與第十八冊怎麼一起用

- **第 2 節**院內不必做（院內主機本來就是那個樣子），指令全寫在這一冊。
- **第 3、4 節**拿**印出來的第十八冊**照做：那份紙本就是要帶進院的那一份，演練時在紙上用筆把看不懂、打錯、寫錯的地方圈起來。這一冊只寫「模擬部署要改什麼」，**指令以第十八冊為準**。
- 第十八冊裡的代稱，模擬部署這樣換：

| 第十八冊寫的                      | 模擬部署換成                                         |
| --------------------------------- | ---------------------------------------------------- |
| `C:\hd\hd-tablet-care`（`$root`） | `C:\hd-sim`                                          |
| `<名稱>`                          | 開發機的電腦名稱（I-05）                             |
| `<IP>`                            | 開發機 Wi-Fi 網卡的 IPv4 位址（I-05）                |
| `<新 tag>`                        | I-01 打的那一個                                      |
| 護理站的電腦                      | 連同一個 Wi-Fi 的手機瀏覽器（必要時另一台筆電）      |
| 院內給平板用的 Wi-Fi              | 開發機連的同一個 Wi-Fi                               |
| 資訊室、護理長                    | 自己。要問他們的事跳過，但**在紀錄裡寫「院內要問」** |

代稱**連同 `<`、`>` 一起換掉**（`http://<IP>:18080` → `http://192.168.1.20:18080`），1029 第一輪就在 J-11 把角括號一起打進去過。

### 0.3 要準備的東西

| 東西                                                        | 備註                                                                                                                                                                                    |
| ----------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 開發機（Windows），裝好 Git for Windows 與 Docker Desktop   | 沒裝的話照[第十五冊](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/15-from-zero/index.md) V-04 的方框裝，裝完重新開機                                                        |
| 印好的第十八冊                                              | 第 3、4 節照它做                                                                                                                                                                        |
| 印好的演練紀錄第 11 節                                      | 邊做邊填                                                                                                                                                                                |
| 一支 Android 手機，或醫師給的暫用平板（Galaxy Tab S6 Lite） | 用暫用平板最好：J-29 能順便看字型大小 1.1 會不會撐破畫面（[暫用平板紀錄](https://94sh09sh19sh.github.io/hd-docs/latest/notes/interim-tablet/index.md)第 6 節第 1 項）。**不要原廠重設** |
| 一個手機與開發機都連得上、而且准許裝置互連的 Wi-Fi          | 學校或公司的 Wi-Fi 常擋裝置互連，改用家裡的 Wi-Fi 或手機熱點                                                                                                                            |
| 一整個下午                                                  | 第 2～4 節中途不換 Wi-Fi（換了 IP 就變，要重簽憑證）                                                                                                                                    |

### 0.4 要花多久

| 段落                        | 大約時間                                                                 |
| --------------------------- | ------------------------------------------------------------------------ |
| 第 1 節：準備               | 30 分鐘                                                                  |
| 第 2 節：重現 1001          | 60～90 分鐘（`shell-builder` 的映像檔第一次要下載約 1.5 GB，約 30 分鐘） |
| 第 3 節：J-04～J-21         | 2～2.5 小時                                                              |
| 第 4 節：J-22～J-29         | 60～90 分鐘                                                              |
| 第 5 節：模擬部署才做的驗收 | 60 分鐘                                                                  |
| 第 6 節：撤除               | 15 分鐘                                                                  |

### 0.5 規矩

- **全程只用 Git 與 Docker。** 開發機上的 Node.js 不准在第 2～4 節出現；第 5 節 I-14 是唯一例外（那是驗收，不是部署）。
- **一律從 GitHub 全新 clone 到 `C:\hd-sim`**，不准用平常寫程式的工作目錄，也不准複製它。
- **只用虛構資料。**
- 每一步開始與結束各記一次時間；錯誤訊息抄原文、抄到最後一行。

______________________________________________________________________

## 1. 準備

### I-01 選定要帶的版本、打 tag、推上 GitHub

**做什麼**（在平常寫程式的工作目錄）

1. 確認工作目錄是乾淨的、在最新的 `master`：

```
git status --short
git switch master
git pull
```

1. 確認最近一次全量回歸之後，程式沒有再改過。`<回歸的 commit>` 是《[技術端進度報告](https://94sh09sh19sh.github.io/hd-docs/latest/reports/progress-technical/index.md)》第 10 節「最近一次執行」寫的那一個：

```
git log --oneline <回歸的 commit>..HEAD -- apps packages services Dockerfile docker-compose.yml deploy
```

**什麼都沒印**才對（只有 `docs/` 改過沒關係）。印出東西的話，先跑那幾個迭代的驗收，或重跑一次全量回歸。 3. 打 tag 並推上 GitHub（`<新 tag>` 例如 `v0.4.0`）：

```
git tag -a <新 tag> -m "第三次進院"
git push origin <新 tag>
git ls-remote --tags origin
git show <新 tag>:services/shell-builder/shell.pin
```

**怎麼知道成功了**：`ls-remote` 的清單看得到 `<新 tag>` 與 `v0.3.0`；`shell.pin` 是 `SHELL_TAG=v0.3.0`（外殼不換版）。把 `<新 tag>` 與 `git rev-parse <新 tag>` 的 commit 寫進紀錄。

| 症狀                      | 處置                                                                                                                                    |
| ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| `shell.pin` 不是 `v0.3.0` | 外殼換版了，第十八冊沒有寫外殼更新的步驟。先停下來，把第十八冊補上第十二冊 Y-14 再演練                                                  |
| 演練到一半發現程式要修    | 修好、跑過驗收，**打下一個 tag**（例如 `v0.4.1`），從 I-03 重新演練。**推上去的 tag 不要移動或刪掉重打**：院內與紀錄都靠 tag 名字對版本 |

______________________________________________________________________

### I-02 開發機的工具與網路（＝V-04、V-06）

**做什麼**

```
git --version
docker version
docker info --format "{{.ServerVersion}} {{.OSType}} {{.Architecture}}"
docker compose version
docker pull node:20-bookworm-slim
docker pull eclipse-temurin:17-jdk-jammy
```

**怎麼知道成功了**

| 指令                     | 應該看到                                                                             |
| ------------------------ | ------------------------------------------------------------------------------------ |
| `git --version`          | 一個版本號                                                                           |
| `docker version`         | `Client` 與 `Server` 兩段都有版本號                                                  |
| `docker info …`          | `<版本> linux x86_64`，中間一定是 `linux`                                            |
| `docker compose version` | `v2` 以上                                                                            |
| 兩條 `docker pull`       | 最後是 `Status: Downloaded newer image for …` 或 `Status: Image is up to date for …` |

| 症狀                                             | 處置                                                    |
| ------------------------------------------------ | ------------------------------------------------------- |
| `failed to connect to the docker API at npipe:…` | Docker Desktop 沒開。開始選單開啟，等左下角變綠         |
| 中間是 `windows`                                 | 工作列的 Docker 圖示按右鍵 → Switch to Linux containers |
| `no such host`                                   | 再打一次；仍不行就換個網路                              |

______________________________________________________________________

### I-03 確認開發機上沒有上一輪留下的東西（＝V-13 方框、V-32）

**做什麼**

```
docker volume ls --filter name=hd-tablet-care
docker ps -a --filter name=hd-tablet-care
docker images "hd-tablet-care*"
Test-Path C:\hd-sim
Get-NetTCPConnection -State Listen | Where-Object LocalPort -in 13000,18080,18081 | Select-Object LocalPort, OwningProcess
```

**怎麼知道成功了**：前三條只有標題列、第四條 `False`、最後一條什麼都沒印。

**不是的話**：上一輪沒撤除乾淨，先照第 6 節 I-17 撤除再回來。最後一條印出東西 → 有別的程式（例如 `npm run dev`）佔著那個埠，先關掉它。

______________________________________________________________________

### I-04 兩把部署金鑰（＝V-10、V-20）

模擬部署要用**專門的部署金鑰**走院內那條路，不拿平常推程式碼的那把頂替。

**做什麼**：先試試以前做過模擬部署時留下的金鑰還能不能用：

```
ssh -T github-hd-tablet-care
ssh -T github-hd-kiosk-shell
```

| 印出                                                                                                        | 意思                                                   |
| ----------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| `Hi 94sh09sh19sh/hd-tablet-care! You've successfully authenticated…` 與 `Hi 94sh09sh19sh/hd-kiosk-shell! …` | 兩把都在，往下                                         |
| `Could not resolve hostname github-hd-tablet-care`                                                          | 沒做過，照下面建                                       |
| `Permission denied (publickey)`                                                                             | 金鑰在，但 GitHub 上的登記被拿掉了，把 `.pub` 重新登記 |

**沒做過的話**：

1. 產生兩把金鑰，把印出來的兩整行公鑰分別登記到 GitHub 兩個 repo 的 **Settings → Deploy keys → Add deploy key**，標題寫「模擬部署（開發機）」，**不勾 Allow write access**：

```
New-Item -ItemType Directory -Force $HOME\.ssh
ssh-keygen -t ed25519 -C "hd-tablet-care@$(hostname)" -f $HOME\.ssh\hd-tablet-care -N '""'
ssh-keygen -t ed25519 -C "hd-kiosk-shell@$(hostname)" -f $HOME\.ssh\hd-kiosk-shell -N '""'
Get-Content $HOME\.ssh\hd-tablet-care.pub
Get-Content $HOME\.ssh\hd-kiosk-shell.pub
```

1. 開 SSH 設定檔（第一行先建好沒有副檔名的空檔，免得記事本存成 `config.txt`）：

```
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

1. 再打一次本步驟最上面兩條。第一次會問 `Are you sure you want to continue connecting (yes/no)?`，打 `yes`。

**怎麼知道成功了**：兩條各印出對的 repo 名稱（**不是同一個**）。

| 症狀                                          | 處置                                                                  |
| --------------------------------------------- | --------------------------------------------------------------------- |
| 第二條印出的是 `hd-tablet-care`               | 兩段的 `IdentityFile` 寫反，或少了 `IdentitiesOnly yes`               |
| `Could not resolve hostname …` 後面接一串亂碼 | 記事本存成了 `config.txt`：`Rename-Item $HOME\.ssh\config.txt config` |

______________________________________________________________________

### I-05 查開發機的兩個位址：模擬的 `<名稱>` 與 `<IP>`（＝V-08）

院內主機 1001 用的是**名稱**，這一次要換成 **IP**。開發機上兩個都要有，才練得到「換」。

**做什麼**

```
hostname
ipconfig
Resolve-DnsName (hostname) | Select-Object Name, IPAddress
```

| 抄什麼             | 從哪裡                                                                                                    | 這一冊叫它 |
| ------------------ | --------------------------------------------------------------------------------------------------------- | ---------- |
| 電腦名稱           | `hostname` 印的那一行                                                                                     | `<名稱>`   |
| Wi-Fi 的 IPv4 位址 | `ipconfig` 的「無線區域網路介面卡 Wi-Fi」那一段，**不是** `vEthernet (WSL)`、`vEthernet (Default Switch)` | `<IP>`     |

**怎麼知道成功了**：兩個都抄了；`Resolve-DnsName` 查得到自己的名稱（開發機自己查自己一定查得到）。手機查不到開發機的名稱是**正常的**，這正是院內平板會遇到的事，所以第三次進院要換成 IP。

> ⚠️ 開發機**同時接著有線網路與 Wi-Fi**（例如另外接了一台旅行路由器）時，`<IP>` 要抄**手機連的那個網路**的網卡，抄錯張網卡，J-12 簽出來的憑證平板就連不上。用不到的那條，演練期間先拔掉最省事。
>
> ⚠️ **從現在起到第 4 節做完，不要換 Wi-Fi、不要讓開發機睡眠。** IP 變了就要照[第十五冊之二](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/15b-env-simulation/index.md)第 4 節重簽憑證。

______________________________________________________________________

## 2. 把開發機變成「1001 離院時的院內主機」

這一節在開發機上重做一次 1001 那天的部署：`v0.3.0`、位址用名稱、**放行名單填錯**。做完之後，開發機會和院內主機一樣：三個服務在跑、護理端登不進去。

### I-06 建資料夾、開工三行（＝V-09）

**做什麼**

```
$root = "C:\hd-sim"
$cfg  = "$root\config\.env"
New-Item -ItemType Directory -Force "$root\config", "$root\backups" | Out-Null
Get-ChildItem $root
```

**怎麼知道成功了**：列出 `backups`、`config` 兩個資料夾。

> ⚠️ PowerShell 關掉再開，要重打 `$root`、`$cfg` 兩行，I-07 之後再加 `cd $root\repo`（就是第十八冊 J-04 的開工三行，只是根目錄換成 `C:\hd-sim`）。

______________________________________________________________________

### I-07 clone，切到 `v0.3.0`（＝V-11）

**做什麼**

```
git clone git@github-hd-tablet-care:94sh09sh19sh/hd-tablet-care.git $root\repo
git clone git@github-hd-kiosk-shell:94sh09sh19sh/hd-kiosk-shell.git $root\hd-kiosk-shell
cd $root\repo
git checkout v0.3.0
git describe --tags
```

**怎麼知道成功了**：最後一行正好是 `v0.3.0`。一大段 `detached HEAD` 是正常的。

| 症狀                                | 處置                                                                                    |
| ----------------------------------- | --------------------------------------------------------------------------------------- |
| `destination path … already exists` | 上一輪沒撤除乾淨，回 I-03                                                               |
| `Connection reset by … port 22`     | 網路切斷連線。刪掉殘留的資料夾（`Remove-Item -Recurse -Force $root\repo`）再 clone 一次 |

______________________________________________________________________

### I-08 照 1001 的樣子填 `v0.3.0` 的 `.env`

**做什麼**

```
Copy-Item $root\repo\deploy\hospital.env.example $cfg
notepad $cfg
```

這是 `v0.3.0` 的範本，**沒有** `HD_EXPORT_DIR` 與院方 API 那兩行——院內那一份也沒有，第十八冊 J-16 才補。照下面填（`<名稱>` 換成 I-05 的電腦名稱，三處都是；`JWT_SECRET` 用下一段的指令產生）：

```
HD_IMAGE_TAG=v0.3.0

HD_BACKUP_DIR=C:\hd-sim\backups
HD_CONFIG_DIR=C:\hd-sim\config

HD_API_PORT=13000
HD_NURSE_PORT=18080
HD_PATIENT_PORT=18081

HD_PUBLIC_API_URL=http://<名稱>:13000
CORS_ORIGINS=http://hd-server:18080
MDM_KIOSK_BASE_URL=https://<名稱>:18081

HD_SHELL_SRC_DIR=C:\hd-sim\hd-kiosk-shell
HD_SHELL_SIGNING=dev
KIOSK_SHELL_MIN_VERSION=

JWT_SECRET=<這一輪產生的那一串>
JWT_EXPIRES_IN=8h

SUPER_ADMIN_WORK_ID=sim-admin
SUPER_ADMIN_INITIAL_PASSWORD=Sim-Init-2026
SUPER_ADMIN_DISPLAY_NAME=模擬部署管理員
```

其餘各行（備份時間、AI、營運參數）**維持範本的值**。

產生 `JWT_SECRET`（與院內同一行 PowerShell，不用 Node.js）：

```
$b = New-Object byte[] 48; [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($b); [Convert]::ToBase64String($b).TrimEnd('=').Replace('+','-').Replace('/','_')
```

> 💡 **`CORS_ORIGINS=http://hd-server:18080` 是故意填錯的**：照抄了舊範例的 `hd-server`，就是 1001 最可能的原因（第十五冊之三 3.2 節的可能 A）。這一輪要親眼看到這個錯怎麼出現、第十八冊怎麼把它修好。
>
> ⚠️ **`HD_SHELL_SIGNING` 一定是 `dev`**，院內才是 `hospital`。忘了改、已經跑過 `shell-builder` 的話，只能撤除重來（I-17）。

**怎麼知道成功了**

```
docker compose --env-file $cfg config --quiet
Select-String -Path $cfg -Pattern '^(HD_IMAGE_TAG|HD_PUBLIC_API_URL|CORS_ORIGINS|MDM_KIOSK_BASE_URL|HD_SHELL_SIGNING)='
```

第一條什麼都沒印；第二條五行，與上面一致（`CORS_ORIGINS` 是 `hd-server`，其他兩個位址是 `<名稱>`）。

______________________________________________________________________

### I-09 建資料卷、建置、建資料庫、啟動（＝V-13～V-16）

**做什麼**（記下開始時間；第四條是一整行）

```
docker volume create hd-tablet-care-data
docker volume create hd-tablet-care-keys
docker compose --env-file $cfg build
docker compose --env-file $cfg run --rm --no-deps api node apps/api/scripts/prisma-cli.mjs migrate deploy --schema apps/api/prisma/schema.prisma
docker compose --env-file $cfg up -d
docker compose --env-file $cfg ps
curl.exe -s http://localhost:13000/api/health
```

**怎麼知道成功了**：建置最後 `Image hd-tablet-care:v0.3.0 Built`；建資料庫最後 `All migrations have been successfully applied.`；`ps` 三個服務 `Up`；health 是 `{"status":"ok",…}`。記下結束時間。

| 症狀                    | 處置                                                                   |
| ----------------------- | ---------------------------------------------------------------------- |
| `no such host`          | 再打一次                                                               |
| `api` 一直 `Restarting` | `docker compose --env-file $cfg logs api --tail 30` 看是哪一條設定被拒 |

______________________________________________________________________

### I-10 外殼：建 `shell-builder`、建 APK、備份金鑰、病人端改走 HTTPS（＝V-21～V-24）

**做什麼**（記下開始時間；第一條第一次約 30 分鐘）

```
docker compose --env-file $cfg --profile shell build shell-builder
docker compose --env-file $cfg --profile shell run --rm shell-builder
docker compose --env-file $cfg --profile shell run --rm shell-builder keys-backup
docker compose --env-file $cfg restart patient-web
docker compose --env-file $cfg --profile shell run --rm shell-builder keys-info
```

**怎麼知道成功了**

| 看什麼         | 應該是                                                                                                  |
| -------------- | ------------------------------------------------------------------------------------------------------- |
| 第一條最後幾行 | 「✓ 外殼 v0.3.0（…，契約第 1 版）已準備好，相依已下載」                                                 |
| 第二條         | 「這一次新產生：院內 CA 伺服器憑證（`<名稱>`） APK 簽章金鑰（開發用）」，接著 APK 檔名與三個 SHA-256    |
| 第三條         | 「已備份：備份目錄/keys/hd-keys-\<時間>.tar.gz」——這一份就是模擬的「1001 那份金鑰備份」，**檔名抄下來** |
| `keys-info`    | 「伺服器憑證」那一行是 `DNS:<名稱>`                                                                     |

記下結束時間。

______________________________________________________________________

### I-11 AI 閘道（舊版）（＝V-29、V-30）

1001 有沒有做這一步沒記到。這裡**做**，因為這是比較難的情形：第十八冊 J-20 要把一個舊版閘道換成新版。

**做什麼**

```
New-Item -ItemType Directory -Force $root\config\ai-gateway | Out-Null
Copy-Item services\ai-gateway\config.hospital.example.yaml $root\config\ai-gateway\config.yaml
docker compose --env-file $cfg --profile ai build ai-gateway
docker compose --env-file $cfg --profile ai up -d ai-gateway
docker compose --env-file $cfg exec -T api node -e "fetch('http://ai-gateway:8000/health').then(async r=>console.log(r.status, await r.text()))"
```

**怎麼知道成功了**：建置最後 `全部通過`；最後一條印出 `503 {"status":"error","config":"error","detail":"base_url 尚未填寫（推論端點的位址）"}`。

______________________________________________________________________

### I-12 確認重現了 1001

**做什麼**

1. 開發機的瀏覽器開 `http://<名稱>:18080`，用 `sim-admin` / `Sim-Init-2026` 登入。
1. 在 PowerShell 打放行檢查：

```
curl.exe -s -i -H "Origin: http://<名稱>:18080" http://<名稱>:13000/api/health | Select-String Access-Control-Allow-Origin
```

**怎麼知道成功了**：

| 看什麼   | 應該是                               |
| -------- | ------------------------------------ |
| 登入     | 登入鈕下面出現 **`Failed to fetch`** |
| 放行檢查 | **什麼都沒印**                       |

兩個都看到了，開發機就是「1001 離院時的院內主機」。**記下這一刻的時間**，然後**把 PowerShell 關掉**（院內到場時也是開一個新的視窗）。

| 症狀         | 處置                                                                                                   |
| ------------ | ------------------------------------------------------------------------------------------------------ |
| 竟然登得進去 | `CORS_ORIGINS` 沒有照 I-08 填成 `hd-server`，或瀏覽器用了 `localhost` 以外的寫法剛好對上。回 I-08 檢查 |

______________________________________________________________________

## 3. 拿第十八冊照做：J-04～J-21

**從這裡開始，翻開印好的第十八冊，從 J-04 一步一步照做。** 下表是每一步模擬部署要改的地方與要記下的東西；表上寫「照做」的，就是一字不差照第十八冊打（`$root` 換成 `C:\hd-sim`）。

> ⚠️ 模擬部署的「護理站的電腦」是**連同一個 Wi-Fi 的手機瀏覽器**。手機要連得到開發機的三個埠，先用**系統管理員身分**的 PowerShell 開三條只對私人網路的防火牆規則（撤除時 I-17 會刪）。
>
> **為什麼要「私人」**：三條規則都是 `-Profile Private`，只在網路設定檔類型是「私人」時生效。Windows 連上新的 Wi-Fi 預設是「公用」，這時規則不生效、手機連不到。不改成對所有網路放行，是因為開發機帶到咖啡廳或學校時，這三個埠會對整個網路開放。
>
> **怎麼改**：設定 → 網路和網際網路 → Wi-Fi → 這個網路的內容 →「網路設定檔類型」選**私人網路**。或在系統管理員身分的 PowerShell 打 `Get-NetConnectionProfile`，找手機連的那個網路的 `InterfaceAlias`，再打 `Set-NetConnectionProfile -InterfaceAlias "Wi-Fi" -NetworkCategory Private`（`Wi-Fi` 換成那個 `InterfaceAlias`）；再打一次 `Get-NetConnectionProfile`，那一段的 `NetworkCategory` 是 `Private` 就好。印出 `DomainAuthenticated` 或改不了：那是學校或公司管的網路，換家裡的 Wi-Fi 或手機熱點。演練完用的是熱點或外面的網路，改回「公用」。
>
> **院內不做這一步**：院內主機的網路類型與防火牆歸資訊室管，第十八冊 J-08 連不到就找資訊室。
>
> 三條規則：
>
> 第一條：`New-NetFirewallRule -DisplayName "hd-sim api 13000" -Direction Inbound -Protocol TCP -LocalPort 13000 -Profile Private -Action Allow`
>
> 第二條：`New-NetFirewallRule -DisplayName "hd-sim nurse 18080" -Direction Inbound -Protocol TCP -LocalPort 18080 -Profile Private -Action Allow`
>
> 第三條：`New-NetFirewallRule -DisplayName "hd-sim patient 18081" -Direction Inbound -Protocol TCP -LocalPort 18081 -Profile Private -Action Allow`

| 第十八冊                 | 模擬部署怎麼做                                                                                            | 要記下、要確認的                                                                                                                                                                                                                                                                                                      |
| ------------------------ | --------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 第 1 節 J-01～J-03       | 跳過（J-01 就是這一冊本身；J-02 的問題清單照樣在出發前寄）                                                | —                                                                                                                                                                                                                                                                                                                     |
| J-04 開工三行            | `$root = "C:\hd-sim"`，其餘照做                                                                           | —                                                                                                                                                                                                                                                                                                                     |
| J-05 先看現況            | 照做                                                                                                      | 對照第十八冊那張表：tag `v0.3.0`、三個服務加 `ai-gateway` 都 `Up`、兩個資料卷、`backups\keys` 有一份（檔名是 I-10 抄的，不是 1001 那一份）、`*.db` 是 0 份（開發機剛建，正常）。**表上每一列都對得上嗎？對不上的是手冊寫錯，圈起來**                                                                                  |
| J-06 0922 的容器         | 跳過（開發機上沒有）。想練的話照第十四冊之三的附錄做替身                                                  | —                                                                                                                                                                                                                                                                                                                     |
| J-07 先抄五樣            | 照做                                                                                                      | 第 1 條 `CORS_ORIGINS` 是 `hd-server`、第 2 條日誌也是 `hd-server` → 照第十八冊那張判斷表，應該判成「可能 A」。**判得出來嗎？** 第 4 條伺服器憑證是 `DNS:<名稱>`。模擬部署可以拍照（第 4 條沒有私鑰，開發用金鑰 I-17 也會刪），但**不要拍 `notepad $cfg` 的畫面**（有 `JWT_SECRET` 與初始密碼）；院內照第十八冊不拍照 |
| J-08 確認 IP、從護理站連 | 第 1 步照做（DHCP 是「是」沒關係）；第 2～4 步用**手機瀏覽器**開                                          | 手機開得到三個網址。開不到：防火牆規則、Wi-Fi 設定檔類型、Wi-Fi 擋裝置互連（0.3 節）                                                                                                                                                                                                                                  |
| J-09 留一份 `.env`       | 照做                                                                                                      | —                                                                                                                                                                                                                                                                                                                     |
| J-10 改三個位址          | 照做                                                                                                      | 第三條檢查原本會抓到 `hd-server`，改完要什麼都不印                                                                                                                                                                                                                                                                    |
| J-11 重建、啟動、查放行  | 照做                                                                                                      | **建置耗時**；放行檢查印出 `Access-Control-Allow-Origin: http://<IP>:18080`                                                                                                                                                                                                                                           |
| J-12 重簽憑證            | 照做                                                                                                      | 「這一次新產生」**只有**伺服器憑證（`<IP>`）；`keys-info` 的 CA 與簽章金鑰指紋與 J-07 一樣；**耗時**                                                                                                                                                                                                                  |
| J-13 主機上登入          | 開發機瀏覽器開 `http://<IP>:18080`，用 `sim-admin` / `Sim-Init-2026`                                      | 被要求改密碼，改成什麼都可以（記在紀錄紙上，撤除後就沒用了）                                                                                                                                                                                                                                                          |
| J-13 之後多做一件        | 開發機瀏覽器**故意用 `http://localhost:18080` 開一次、按登入**；再用 `http://<名稱>:18080` 開一次、按登入 | 兩次都是 `Failed to fetch`。這就是院內用錯網址時會看到的畫面，看過一次到院內就認得                                                                                                                                                                                                                                    |
| J-14 護理站登入          | 用**手機瀏覽器**開 `http://<IP>:18080` 登入                                                               | 登得進去；**記下從 J-04 到這裡總共多久**                                                                                                                                                                                                                                                                              |
| J-15 下載新版            | 照做，`<新 tag>` 是 I-01 打的                                                                             | 看到「請設定 HD_EXPORT_DIR」要等到 J-16 之後才消失——**確認真的會出現**（隨便打一條 `docker compose --env-file $cfg config --quiet`）                                                                                                                                                                                  |
| J-16 補 `.env`           | `HD_EXPORT_DIR=C:\hd-sim\export`；其餘照做，兩個院方 API 的變數也先留空白                                 | 檢查表的 `HD_SHELL_SIGNING` 這裡是 `dev`（院內是 `hospital`）                                                                                                                                                                                                                                                         |
| J-17 建置新版            | 照做                                                                                                      | **耗時**；`docker images hd-tablet-care` 看得到兩個 tag                                                                                                                                                                                                                                                               |
| J-18 更新資料庫          | 照做                                                                                                      | 第 [5] 段寫套用了 **19 個**遷移（從 `iteration15_hospital_api` 到 `iteration31_connect_dots_norm`）；**更新前備份的檔名與 SHA-256 抄下來，I-15 要用**                                                                                                                                                                 |
| J-19 啟動新版            | 照做；「護理站」是手機，沒有 Ctrl＋F5：關掉分頁重開，或在瀏覽器的網站設定清除這個網站的資料               | 三個服務的映像檔是新 tag；手機重新整理後用改過的密碼登得進去（**資料留住了**：帳號與密碼是更新前的）；版本更新紀錄有一筆                                                                                                                                                                                              |
| J-20 AI 閘道             | 照做（I-11 做過，J-07 第 5 條是 `True`，所以跳過複製設定檔）                                              | 503 那一行；`docker ps` 裡 `ai-gateway` 的映像檔是新 tag                                                                                                                                                                                                                                                              |
| J-21 取出指令            | 照做                                                                                                      | 說明的第一行對得上第十八冊寫的                                                                                                                                                                                                                                                                                        |

______________________________________________________________________

## 4. 拿第十八冊照做：J-22～J-29

| 第十八冊                          | 模擬部署怎麼做                                                                                                                                                                             | 要記下、要確認的                                                                                                                          |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------- |
| J-22 備份與還原                   | 照做（「立即備份」在開發機或手機的護理端都可以）                                                                                                                                           | 兩行 ✓；第 4 步問資訊室那一句跳過                                                                                                         |
| J-23 Docker Desktop 四項          | **只看不改**（開發機是你自己的設定）                                                                                                                                                       | 四項的位置在你這一版的 Docker Desktop 找得到嗎？名稱和第十八冊寫的一樣嗎？不一樣就把實際的名稱寫在紙本上                                  |
| J-24 防毒                         | 用系統管理員身分的 PowerShell 打那兩條，**只看不改**                                                                                                                                       | 指令跑得動；`hex` 怎麼讀看得懂                                                                                                            |
| J-25 重新開機                     | 開發機驗不出「沒人登入」的情形，改成：工作列的 Docker 圖示按右鍵 → **Quit Docker Desktop**，再從開始選單開啟，等三分鐘，打第十八冊 J-25 的兩條                                             | 所有 `hd-tablet-care-` 容器（含 `ai-gateway`）自己回到 `Up`；手機上的護理端在這段時間閃紅框、之後自己消失。**量從 Quit 到紅框消失幾分鐘** |
| J-26 探測院方 API                 | 先打 `docker compose --env-file $cfg --profile simulation up -d hospital-api-sim` 開模擬院方 API，再照第十八冊打；`Read-Host` 問位址時輸入 `http://hospital-api-sim:8090/dialysislist.php` | 「連線：成功」「解析：成功」，**「模擬標頭：有」在這裡是對的**（院內看到它就是位址填錯）；最後一行「以上可以整段抄進演練紀錄」            |
| J-27 平板事前檢查                 | 用暫用平板或手機。字型大小**不要改**（要先問醫師），維持原樣                                                                                                                               | 下載頁上的位址是 `https://<IP>:18081`；三個 SHA-256 抄得到                                                                                |
| J-28 註冊、安裝                   | 照做                                                                                                                                                                                       | 下載頁按「下載 App」裝得起來；用暫用平板的話，安裝不明來源的提示長什麼樣，寫在紙本上                                                      |
| J-29 開啟並釘住                   | 照做                                                                                                                                                                                       | 平板的等待畫面沒有憑證警告；護理端「固定中」→ 解除 →「已跳出」→ 釘回 →「固定中」                                                          |
| J-29 之後多做一件（用暫用平板時） | 護理端簡易版把一位模擬病人放到這台平板上（I-13 開了模擬院方 API 之後才有病人，可以等 I-13 做完再回來做）                                                                                   | 病人端首頁的頂列是**一列**、沒有被截斷（字型大小 1.1 的影響，暫用平板紀錄第 6 節第 1 項）。**拍照**（虛構病人，可以拍）                   |
| J-30～J-33                        | J-30 的冒煙測試照做（「護理站」是手機）；J-31～J-33 跳過                                                                                                                                   | 冒煙測試每一列對得上                                                                                                                      |

______________________________________________________________________

## 5. 模擬部署才做的驗收

### I-13 模擬院方 API 接上去，並驗院內的設定擋得住它（＝V-30a 方框、部署規範第 9 章第 8 項）

**做什麼**

1. 讓後端真的去抓模擬院方 API：

```
notepad $cfg
```

最後那兩行改成：

```
HOSPITAL_API_BASE_URL=http://hospital-api-sim:8090/dialysislist.php
HD_SIMULATION_DEPLOYMENT=yes
```

存檔，然後：

```
docker compose --env-file $cfg --profile simulation up -d
docker compose --env-file $cfg exec -T api node apps/api/dist/hospital-api-probe.js
```

1. 手機開護理端簡易版，**什麼都不碰**，等三分鐘。
1. 驗「院內的設定擋得住模擬」：`.env` 的 `HD_SIMULATION_DEPLOYMENT=yes` **清空**（等號後面什麼都不留），存檔，然後：

```
docker compose --env-file $cfg up -d api
docker compose --env-file $cfg logs --tail 20 api
```

1. 改回原樣：`HOSPITAL_API_BASE_URL` 與 `HD_SIMULATION_DEPLOYMENT` **兩行都清空**（和院內一樣），存檔，然後：

```
docker compose --env-file $cfg up -d api
docker compose --env-file $cfg --profile simulation stop hospital-api-sim
curl.exe -s http://localhost:13000/api/health
```

**怎麼知道成功了**

| 哪一步 | 應該是                                                         |
| ------ | -------------------------------------------------------------- |
| 1      | 探測印出「模擬標頭：有」，用的是 `.env` 裡的位址，所以沒問位址 |
| 2      | 床位圖上出現 A1、A2… 與「模擬甲」等虛構病人                    |
| 3      | 日誌寫**拒絕啟動**，並指出 **DEP-46**                          |
| 4      | health 正常；院方 API 的兩行都是空白                           |

> 💡 第 3 步就是院內那一道保險：院內主機的 `HD_SIMULATION_DEPLOYMENT` 永遠空白，萬一有人把模擬部署的位址抄過去，後端會拒絕啟動，而不是把假病人寫進院內的資料庫。

______________________________________________________________________

### I-14 跑三支驗收（＝V-31、第十一冊第 7 節）

**這一步是驗收，不是部署步驟**，也是整輪唯一准用 Node.js 的地方。在**平常寫程式的工作目錄**（不是 `C:\hd-sim\repo`），先切到同一個 tag 再跑：

```
git switch --detach <新 tag>
npm run verify:iteration11 -- --live --env-file C:\hd-sim\config\.env
npm run verify:iteration12 -- --live --env-file C:\hd-sim\config\.env
npm run verify:iteration13 -- --live --env-file C:\hd-sim\config\.env
git switch master
```

**怎麼知道成功了**：三支都全部 ✓。第一支會執行 `down -v` 再 `up -d`，驗證「資料卷不會被 `-v` 刪掉」，**這是刻意的**。

| 症狀     | 處置                                                                                                                                                   |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 某一項 ✗ | 抄下原文。是驗收腳本跟不上新版（例如沒料到 `HD_EXPORT_DIR`），還是新版真的有問題？前者修腳本、後者修程式，**兩種都要打新 tag 重新演練**（I-01 那一列） |

______________________________________________________________________

### I-15 退回 `v0.3.0` 演練（＝第十八冊附錄二、W-20）

院內要是新版出問題，靠的就是第十八冊附錄二。這裡照它真的退一次。

**做什麼**：翻到第十八冊**附錄二**，照做。`<備份檔名>`、`<雜湊>` 用第 3 節 J-18 抄的那一份。

**怎麼知道成功了**

| 看什麼                                     | 應該是                                                                                                                            |
| ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------- |
| 還原輸出                                   | `完整性檢查：ok`、`還原的就是 DATABASE_URL 指向的正本`                                                                            |
| `docker ps`                                | 三個服務的映像檔是 `hd-tablet-care:v0.3.0`                                                                                        |
| 手機開 `http://<IP>:18080`，重新整理後登入 | **登得進去**——證明第十八冊說的「J-11 已經用 `<IP>` 重建過 `v0.3.0` 的網頁，所以舊版也登得進去」是真的                             |
| 護理端「新增裝置」                         | J-28 註冊的那台平板不見了（它是更新之後才註冊的，跟著資料一起退回去了）。**這是對的**，正好說明「更新之後寫進去的資料會一起消失」 |

| 症狀                            | 處置                                                                                                                |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| 舊版登不進去，`Failed to fetch` | 第十八冊附錄二寫錯了（舊版的網頁裡可能還是 `<名稱>`）。抄下 J-11 那條 `grep` 的結果，**回去改第十八冊**，再演練一次 |

______________________________________________________________________

### I-16 寫紀錄、判定能不能帶進院

**做什麼**：把演練紀錄第 11 節填完，逐項對照下表。

| #   | 判定條件                                                          |
| --- | ----------------------------------------------------------------- |
| 1   | I-12 重現了 1001（`Failed to fetch`、放行檢查空的）               |
| 2   | J-07 判得出「可能 A」                                             |
| 3   | J-14 手機登得進去                                                 |
| 4   | J-18 套用 19 個遷移、`更新完成`                                   |
| 5   | J-19 新版登得進去、資料（帳號密碼）留住了                         |
| 6   | J-26 探測工具跑得動；I-13 擋得住模擬                              |
| 7   | J-29 平板釘住、護理端看得到                                       |
| 8   | I-14 三支全部 ✓                                                   |
| 9   | I-15 退回 `v0.3.0` 之後登得進去                                   |
| 10  | 第十八冊紙本上圈起來的地方都改回文件了（含第十八冊 0.3 節的時間） |

**怎麼知道成功了**：十項都 ✓，紀錄最後一行寫「`<新 tag>` 可以帶進院，＿月＿日」。**有一項 ✗ 就不能帶**：修好、打新 tag、重新演練。

______________________________________________________________________

## 6. 撤除

### I-17 撤除乾淨（＝V-32）

模擬部署做完**一定要撤除**，下一輪才又是從零；也免得開發機一直有服務佔著埠。

**做什麼**

```
cd C:\hd-sim\repo
docker compose --env-file C:\hd-sim\config\.env --profile ai --profile shell --profile simulation down
docker volume rm hd-tablet-care-data hd-tablet-care-keys
docker images "hd-tablet-care*" --format "{{.Repository}}:{{.Tag}}" | ForEach-Object { docker rmi $_ }
cd C:\
Remove-Item -Recurse -Force C:\hd-sim
```

再開一個**系統管理員身分**的 PowerShell，刪掉第 3 節開的防火牆規則：

```
Get-NetFirewallRule -DisplayName "hd-sim *" -ErrorAction SilentlyContinue | Remove-NetFirewallRule
```

平板或手機上：

1. 解除固定（輸入 PIN），把「透析照護平板」**解除安裝**。這是開發用金鑰簽的版本，留著的話院內裝院內版時會「套件與現有套件衝突」。
1. 用的是暫用平板的話：**不要原廠重設**；PIN 與螢幕固定可以留著（院內 J-28 本來就要設）；開發用的 Wi-Fi 可以「忘記」。

**怎麼知道成功了**

```
docker volume ls --filter name=hd-tablet-care
docker images "hd-tablet-care*"
Test-Path C:\hd-sim
```

前兩條只有標題列，第三條 `False`。

部署金鑰與 `$HOME\.ssh\config` 那兩段**留著**，下一輪繼續用；兩個基底映像（`node`、`eclipse-temurin`）也可以留著。

> ⚠️ **撤除只准在模擬部署做。** 院內主機的撤除會刪掉整個透析中心的紀錄，要院方書面同意，照[第八冊](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/08-shutdown/index.md)。

______________________________________________________________________

## 附錄：步驟對照

| 本冊 | 對應               | 本冊       | 對應                   |
| ---- | ------------------ | ---------- | ---------------------- |
| I-01 | V-03、W-01、W-02   | I-10       | V-21～V-24             |
| I-02 | V-04、V-06         | I-11       | V-29、V-30             |
| I-03 | V-13 方框、V-32    | I-12       | 第十五冊之三第 2、3 節 |
| I-04 | V-10、V-20         | 第 3、4 節 | 第十八冊 J-04～J-30    |
| I-05 | V-08               | I-13       | V-30a 方框             |
| I-06 | V-09               | I-14       | V-31                   |
| I-07 | V-11、V-20         | I-15       | 第十八冊附錄二、W-20   |
| I-08 | V-12、第十五冊之二 | I-16       | 第十一冊第 7 節        |
| I-09 | V-13～V-16         | I-17       | V-32                   |

`V-xx` 是第十五冊、`W-xx` 是第十一冊、`J-xx` 是第十八冊的步驟。

______________________________________________________________________

## 版本歷程

| 定版 | 日期 | 異動 |
| ---- | ---- | ---- |
|      |      |      |

[← 回部署手冊總覽](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/index.md)　[第十八冊 · 第三次進院：實際部署 →](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/18-third-visit/index.md)
