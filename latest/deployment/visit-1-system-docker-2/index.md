# 第一次進院（0922）· 部署本系統之五：git clone＋Docker 路線詳細版（D-05～D-12）

上層文件：《[第一次進院（0922）· 部署本系統](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-1-system/index.md)》

> - 狀態：**已照做 0922，凍結**，結果見《[第一次進院紀錄（0922，失敗）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/record-1-0922/index.md)》；這條路線 0926 起由《[從零部署本系統之一：容器路線的原冊](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fresh-install-detail/index.md)》取代，本冊是歷史
> - 1117 由舊的第九冊改寫（0923 定版，當時「要印出來帶進去」）
> - 編號：`D-xx`
>
> ⚠️ **0922 的教訓（F-01～F-03）**：本冊所有指令都在**主機的 PowerShell** 下，不要自己先開任何容器，也不要自己下 `-v`、`-p`；容器由 D-19 的 `docker compose up -d` 產生。本冊的指令是 0921 那一版程式的，之後程式與 `.env` 欄位改過（0926 起部署一律 checkout tag、埠只寫在 `.env`；1027 起多了必填的 `HD_EXPORT_DIR`），**不要照抄到現在的院內主機**，現行做法看《[從零部署本系統](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fresh-install/index.md)》。

接在《[之四：git clone＋Docker 路線詳細版（第 0 節、D-01～D-04）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-1-system-docker/index.md)》後面。

## 摘要

- 第 2 節進院當天先確認 Docker 這一層：H-01～H-07 照《進院當天詳細版》走，H-08～H-13 由 D-05～D-23 取代，H-14 起回去（差異在 D-27）
- D-05 開場講清楚三件代價：建置要開一段對外連線、資料庫在資料卷裡看不到、重新開機後要有人登入 Windows
- D-06 書面例外：G-09 那張表多寫五列，口頭同意不算
- D-07 確認 Docker 可以用（`OSType` 是 `linux`、Compose v2 以上）；D-08 Docker Desktop 四項設定與虛擬磁碟目錄的防毒排除
- D-09 `docker-users` 名單：能下 docker 指令的人就讀得到資料卷
- D-10 對外連線實測七個網域
- 第 3 節取得程式碼：D-11 clone 到 `C:\hd`（帶 `-c credential.helper=`）、D-12 切到交付單上的 commit、網址裡不得有權杖

## 2. 進院當天：先確認 Docker 這一層

前面照《[進院當天詳細版](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-1-system-onsite/index.md)》H-01～H-07 走（報到、找人、問問題、確認機器、盤點）。 **H-08 到 H-13 由這一冊的 D-05～D-23 取代。** H-14 起回到《進院當天詳細版》，差異寫在 D-27。

### D-05 開場時說清楚這條路線的代價

**做什麼**

對資訊室講三句話：

1. 「容器這條路我們準備好了，開發端演練過，**差別是建置要在這台機器上做，所以今天要開一段對外連線，建完就關**。」
1. 「資料庫會放在 Docker 的資料卷裡，**你們在檔案總管裡看不到它**。備份會放在一個看得到的目錄，每天一份。」
1. 「**這台機器重新開機之後，要有人登入 Windows，系統才會回來**——除非我們今天找到別的辦法。」（D-03 第 3 題）

**怎麼知道成功了**

對方聽完第三句之後，有給出答案（「會有人登入」「我們有自動登入」「用 Docker Engine」），而不是「應該沒問題」。

### D-06 取得書面例外

**做什麼**

照《[安裝包路線之七](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-installer-git-clone-2/index.md)》G-09 那張表請對方簽名，**另外多寫五列**：

| 事項                 | 內容                                                     |
| -------------------- | -------------------------------------------------------- |
| 部署形態             | 依院方要求以容器部署（《部署規範》3.3 第一種條件）       |
| 例外條款             | DEP-11（主機上建置）、DEP-04（主機上需有 Git 與 Docker） |
| 允許連線的來源       | D-10 那張表                                              |
| Docker 授權          | 由院方確認（D-03 第 2 題）                               |
| 重新開機後的啟動方式 | D-03 第 3 題的答案                                       |

**怎麼知道成功了**

手上有一張簽了名的紙。**口頭同意不算。**

**可能怎麼壞、怎麼處理**

| 症狀         | 處置                                                                                                                                                                                     |
| ------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 沒有人願意簽 | 停手。回 H-08，改走路線 B（隨身碟，《[安裝包路線](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-installer-3/index.md)》）。**隨身碟上那份安裝包照樣帶去**，就是為了這一刻 |

> 回去之後，容器備案啟用與這幾條例外要寫進《[部署規範](https://94sh09sh19sh.github.io/hd-docs/latest/requirements/deployment-spec/index.md)》。 **手冊不能替規範開例外**，它只記錄現場發生了什麼（與 G-09 同一條）。

### D-07 確認 Docker 可以用

**做什麼**

用**會實際操作 Docker 的那個帳號**登入，開 PowerShell：

```
docker version
docker info --format "{{.ServerVersion}} {{.OSType}} {{.Architecture}}"
docker compose version
wsl --status
```

**怎麼知道成功了**

| 指令                     | 應該看到                                                                                             |
| ------------------------ | ---------------------------------------------------------------------------------------------------- |
| `docker version`         | Client 與 Server 兩段都有版本號                                                                      |
| `docker info`            | `<版本> linux x86_64`（**一定要是 `linux`**）                                                        |
| `docker compose version` | `v2.` 開頭（0922 現場是 `v5.1.1`，能用；判準應為「v2 以上」，F-15，0926 改在《容器路線的原冊》W-04） |
| `wsl --status`           | 預設版本 2                                                                                           |

**可能怎麼壞、怎麼處理**

| 症狀                                                                               | 原因                                  | 處置                                                                                            |
| ---------------------------------------------------------------------------------- | ------------------------------------- | ----------------------------------------------------------------------------------------------- |
| `failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine` | Docker Desktop 沒有在跑               | 從開始選單開 Docker Desktop，等左下角變綠再重試。**記下來：這就是重新開機沒人登入時會發生的事** |
| `OSType` 是 `windows`                                                              | 切到了 Windows 容器模式               | 系統匣的 Docker 圖示按右鍵 → Switch to Linux containers                                         |
| `docker` 找不到指令                                                                | 沒裝 Docker，或這個帳號的 PATH 沒有它 | 問資訊室。**不要自己裝**，那是院方的變更流程                                                    |
| `permission denied` 或存取被拒                                                     | 這個帳號不在 `docker-users` 群組      | 請資訊室加，**並記下加了誰**（D-09）                                                            |
| `docker compose` 找不到，但 `docker-compose` 可以                                  | 舊版的 Compose v1                     | 請資訊室升級。**外部資料卷的寫法 v1 不一定支援**，不要硬用                                      |

### D-08 Docker Desktop 的四項設定，以及防毒排除

**做什麼**

開 Docker Desktop → Settings，逐項看：

| #   | 位置                                                   | 設成                                  | 為什麼                                                                        |
| --- | ------------------------------------------------------ | ------------------------------------- | ----------------------------------------------------------------------------- |
| 1   | General → **Start Docker Desktop when you sign in**    | 勾                                    | 否則連有人登入都不會啟動                                                      |
| 2   | General → **Send usage statistics**                    | 不勾                                  | 那是一條院外連線（FR-S07）                                                    |
| 3   | Software updates → **Automatically check for updates** | 不勾                                  | 同上；而且更新 Docker 是院方的變更，不該自己發生                              |
| 4   | Resources → Advanced → **Disk image location**         | 本系統自己的路徑，例如 `D:\hd-docker` | 預設在 `C:\Users\<帳號>\AppData\Local\Docker`，是個人資料夾（DEP-37 第 3 項） |

第 4 項若要搬，**要在建資料卷之前搬**；Docker Desktop 會把現有的虛擬磁碟一起搬過去，要花幾分鐘。 **同機有別的專案在用 Docker 時，第 4 項不要動**，記下現況，回去再談。

第 3 項沒寫到的情形（0922 現場，F-16）：Docker Desktop 從 Microsoft Store 裝的，設定頁會顯示要到市集管理，更新由市集的自動更新決定。

然後請資訊室把**虛擬磁碟所在的目錄**加入防毒排除清單（《[進院當天詳細版](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-1-system-onsite-2/index.md)》H-14 ① 的容器版）。

**怎麼知道成功了**

四項都是上表的值，截圖或抄下來；防毒排除清單裡看得到那個目錄。

**可能怎麼壞、怎麼處理**

| 症狀                           | 處置                                                                                                    |
| ------------------------------ | ------------------------------------------------------------------------------------------------------- |
| 設定是灰的、改不了             | 院方用管理原則鎖住了。記下來，那幾項由資訊室決定                                                        |
| 資訊室不肯排除整個虛擬磁碟目錄 | **這一條要談到有結果。** 即時掃描一個正在被寫入的虛擬磁碟，效果與掃描資料庫檔案一樣：間歇性的鎖定與變慢 |

> 1116 起的看法不同：容器路線的資料庫在 Docker 的虛擬磁碟裡，Defender 看不到 SQLite 的檔，防毒排除加不了不再停手（照架構推論，未實測），見《[進院通則](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-visit-rules/index.md)》。

### D-09 確認誰能下 docker 指令

**這是容器路線上最容易被忽略的一條**（DEP-12、DEP-37 第 4 項）。容器裡的後端雖然以低權限的 `node` 身分執行，但**任何能下 docker 指令的人，都能掛上資料卷、把資料庫整個讀出來**，不需要知道任何密碼。

**做什麼**

```
Get-LocalGroupMember -Group "docker-users"
```

**怎麼知道成功了**

名單裡只有：系統管理員、負責這個系統的人。**寫進交接文件，並寫明加人要知會誰。**

**可能怎麼壞、怎麼處理**

| 症狀                 | 處置                                                                       |
| -------------------- | -------------------------------------------------------------------------- |
| 名單裡有別的專案的人 | 共用 Docker 的代價。**當場告訴資訊室這代表什麼**，由院方決定；記進紀錄     |
| 找不到這個群組       | 裝的是 WSL2 裡的 Docker Engine。改問：誰登得進那個 WSL 發行版、誰有 `sudo` |

### D-10 對外連線實測

**做什麼**

資訊室開好連線之後，一個一個測：

```
Test-NetConnection github.com -Port 443
Test-NetConnection registry-1.docker.io -Port 443
Test-NetConnection auth.docker.io -Port 443
Test-NetConnection production.cloudflare.docker.com -Port 443
Test-NetConnection deb.debian.org -Port 80
Test-NetConnection registry.npmjs.org -Port 443
Test-NetConnection binaries.prisma.sh -Port 443
```

| 網域                                                                         | 誰要用                               |
| ---------------------------------------------------------------------------- | ------------------------------------ |
| `github.com`                                                                 | `git clone`                          |
| `registry-1.docker.io`、`auth.docker.io`、`production.cloudflare.docker.com` | 下載基底映像 `node:20-bookworm-slim` |
| `deb.debian.org`（**埠 80**）                                                | 建置時安裝 `openssl`                 |
| `registry.npmjs.org`                                                         | `npm ci`                             |
| `binaries.prisma.sh`                                                         | Prisma 引擎                          |

**怎麼知道成功了**

七個 `TcpTestSucceeded` 都是 `True`。

**可能怎麼壞、怎麼處理**

| 症狀                                          | 處置                                                                                                            |
| --------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| 經代理伺服器，`Test-NetConnection` 是 `False` | 正常，改用 `curl.exe -I https://registry.npmjs.org` 測。**Docker 另外要設代理**：Settings → Resources → Proxies |
| 只有 `deb.debian.org` 不通（只開了 443）      | 請加開 80。不能開就停下來，回去改 `Dockerfile` 換基底映像，**不要在現場改**                                     |
| 有幾個不通                                    | 補齊再往下。建到一半才失敗，比現在停下來更浪費時間                                                              |

## 3. 取得程式碼

### D-11 clone 到固定目錄

**做什麼**

```
New-Item -ItemType Directory -Force C:\hd
cd C:\hd
git -c credential.helper= clone https://github.com/<帳號>/<repo>.git hd-tablet-care
```

跳出帳號密碼時：帳號填你的 GitHub 帳號，**密碼貼 D-04 那把權杖**。 `-c credential.helper=` 是**這一次不要把憑證存進 Windows**。

**怎麼知道成功了**

`C:\hd\hd-tablet-care\` 存在，裡面看得到 `Dockerfile` 與 `docker-compose.yml`。

**可能怎麼壞、怎麼處理**

| 症狀                       | 處置                                                                                  |
| -------------------------- | ------------------------------------------------------------------------------------- |
| 跳出瀏覽器要你登入 GitHub  | Git Credential Manager 攔下來了。關掉視窗，改用上面那行（帶 `-c credential.helper=`） |
| `Authentication failed`    | 權杖貼錯、過期，或忘了勾這個 repo                                                     |
| 目錄路徑選在「文件」或桌面 | 換到 `C:\hd`。`.env` 會放在這個目錄裡，而那兩個位置常被同步到雲端（DEP-21 第 2 項）   |

### D-12 切到交付單上的那一版

**做什麼**

```
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

| 症狀              | 處置                                                                                                                  |
| ----------------- | --------------------------------------------------------------------------------------------------------------------- |
| 網址裡看得到權杖  | 有人把權杖寫進網址 clone 了。`git remote set-url origin https://github.com/<帳號>/<repo>.git`，並在 D-25 作廢那把權杖 |
| 找不到那個 commit | 遠端沒有它，回 D-01 的問題。**不要改用最新一版**                                                                      |

上一份：《[之四：git clone＋Docker 路線詳細版（第 0 節、D-01～D-04）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-1-system-docker/index.md)》｜下一份：《[之六：git clone＋Docker 路線詳細版（D-13～D-18）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-1-system-docker-3/index.md)》

## 版本歷程

| 定版 | 日期 | 異動 |
| ---- | ---- | ---- |
|      |      |      |

[← 回部署手冊目錄](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/index.md)
