# 第十一冊 · 容器部署：`git clone` ＋ `docker compose`（現行路線）

版本：v0.1　文件狀態：草案（0926 新增，迭代 11）　編號：`W-xx`　**這一冊要印出來帶進去**

> **0926 起這是唯一的部署路線。** 院方的條件是：以容器部署、程式以 `git clone` 取得、
> 院內網路連得出去但外面連不進來、**不准用隨身碟**、Administrator 不設密碼（《部署規範》v3.0 第 0.1 節）。
> 離線安裝包那條路因此**撤除**，不是降為備案。
>
> 規則的真本是《[部署規範](../requirements/deployment-spec.md)》v3.0；這一冊只寫手指要按什麼、每一步會怎麼壞。

> ⚠️ **本冊所有指令都在主機的 PowerShell 下。不要自己先開任何容器，也不要自己下 `docker run -v`、`-p`。**
> 容器一律由 `docker compose` 依 repo 裡的 `docker-compose.yml` 產生。
> 0922 就是在一個手動開的容器裡照步驟做，還把整顆 C 槽掛了進去（[第十冊](10-first-visit.md) F-01、F-02）。

---

## 0. 先講結論

### 0.1 這一冊取代哪些

| 冊 | 0926 起 |
|---|---|
| [第一冊](01-dev-machine.md)（安裝包建置）、[第二冊](02-dry-run.md)（乾淨機器演練）、[第五冊](05-carry-in-out.md)的隨身碟部分、[第七冊](07-git-clone.md)（clone 意外成功） | **歷史紀錄**。它們保護的是一條已經不存在的路線 |
| [第四冊](04-onsite.md) H-08～H-13（帶入安裝包、安裝、啟動） | 由本冊 W-08～W-18 取代；第四冊其餘步驟（到場、找人、冒煙測試、交接）照舊 |
| [第九冊](09-docker.md)（容器備案） | 由本冊取代。第九冊寫的是「容器是例外」時的做法：建完要關網路、要書面例外、`.env` 放在 clone 目錄裡——**這三件 v3.0 都不成立了** |
| [第三冊](03-tablet-shell.md)（平板與外殼 App） | 0927 起憑證、keystore、APK 與側載由[第十二冊](12-shell.md)取代（APK 在院內主機上建置、從下載頁安裝）；平板的採購與盤點照舊 |
| [第八冊](08-shutdown.md)（把服務關乾淨） | 原則照舊，容器版的指令在本冊第 8 節 |

### 0.2 東西放在哪裡

主機上替本系統開一個自己的目錄，例如 `D:\hd-tablet-care\`，底下三個子目錄：

| 東西 | 位置 | 為什麼 |
|---|---|---|
| 原始碼 | `D:\hd-tablet-care\repo\`（`git clone` 下來的） | 建置映像檔用；**更新時還要用** |
| 設定 | `D:\hd-tablet-care\config\.env`（AI 閘道的 `config.yaml` 之後放在 `config\ai-gateway\`） | **不在 clone 目錄裡**（DEP-08）：某一次「整個刪掉重新 clone」不能把設定一起刪掉 |
| 備份 | `D:\hd-tablet-care\backups\` | 資料卷裡的資料庫唯一看得見的出口，院方的備份軟體從這裡送往另一台機器（DEP-06） |
| 資料庫 | 具名資料卷 `hd-tablet-care-data` | **只能放資料卷，不得是 Windows 目錄**（DEP-23）。檔案總管看不到它是正常的 |
| CA、伺服器憑證、APK 簽章金鑰、下載頁 | 具名資料卷 `hd-tablet-care-keys` | 私鑰不離開主機（DEP-35）。0927 起由 `shell-builder` 產生，見[第十二冊](12-shell.md) |
| 外殼 App 原始碼 | `D:\hd-tablet-care\hd-kiosk-shell\`（`git clone` 下來的） | `shell-builder` 從這裡取釘住的那一版（第十二冊 Y-02） |
| 程式 | 映像檔 `hd-tablet-care:<tag>` | 標籤就是 git tag，舊版不刪（DEP-19） |

**繫結掛載只有 `config` 與 `backups` 兩個**（DEP-37 第 3 項），`npm run check:container` 會在開發端擋住任何第三個。

### 0.3 開發機實測結果（0926）

本冊的每一條指令都在開發機上照順序跑過一次：**從 GitHub 全新 clone、全新資料卷、只用 Git 與 Docker**，
接著走完一次更新（新 tag、備份並驗證還原、套用一個新遷移）與一次回退（舊 tag、舊映像檔、還原備份）。
每一步的結果在《[部署演練紀錄](../notes/deployment-drills.md)》第 8 節。

實測抓到兩件事，都已處理：

| 問題 | 不處理會怎樣 | 處理 |
|---|---|---|
| `db:update` 以一次性容器執行時，「服務是不是還開著」問的是它自己 | 服務沒停也照樣更新——**備份與遷移之間的寫入會補不回來** | compose 給它 `UPDATE_PROBE_URL=http://api:3000/api/health`，改問正在跑的 `api`；實測服務開著時確實拒絕 |
| 還原腳本在映像檔裡跑不起來 | 回退時沒有工具可以把備份放回資料卷 | 映像檔一併帶入還原腳本需要的原始碼與設定 |

**開發機驗不到、要在院內那台驗的**：主機的 Docker 版本與資料位置、登記過的連接埠、
斷電重開後 Docker Desktop 會不會自己起來（DEP-21 第 4 項）、防毒排除（Q-27）。

### 0.4 兩個前提，先接受

| 前提 | 意思 |
|---|---|
| **連得出去，不等於資料可以出去**（DEP-14） | 部署與更新要連 GitHub、Docker Hub、npm、Prisma、Debian 套件來源；執行期零院外連線由程式擋，**建置階段不掛任何資料卷** |
| **能登入這台主機的人一律可信任**（DEP-38） | 院方決定 Administrator 不設密碼。本系統不在作業系統層級另設防線；這一條要寫進交接文件，日後帳號政策改變要重新評估 |

---

## 1. 進院前（在開發端做完）

### W-01 要交的 tag 先在開發機從零實測一次

**做什麼**：照本冊第 7 節走完整一輪（DEP-22）。**任一項不過，tag 不得交出去。**

**怎麼知道成功了**：演練紀錄第 8 節每一格都填了，而且沒有 ✗。

---

### W-02 確認 tag 在 GitHub 上

0922 院方 clone 到的 `master` 不是開發端以為的那一版（[F-04](10-first-visit.md)）。**部署一律 checkout tag，不部署分支**（DEP-44）。

**做什麼**

```powershell
git ls-remote --tags origin
```

**怎麼知道成功了**：要交的 tag 出現在清單裡，而且指向的 commit 與開發機實測的那一個相同（`git rev-parse <tag>`）。

---

### W-03 把問題清單寄給資訊室

**做什麼**：至少一週前寄出，答覆寫進演練紀錄。

| 問題 | 對應 |
|---|---|
| 主機的 Docker Desktop 與 Compose 版本？可以不升級就用嗎？ | DEP-04、Q-27 |
| Docker 的資料（WSL2 虛擬磁碟）在哪顆磁碟？剩多少空間？能加入防毒排除嗎？ | DEP-21、DEP-37 第 5 項 |
| 要給本系統哪三個連接埠？（現場看過 3000 已被佔用） | DEP-37 第 2 項、[F-17](10-first-visit.md) |
| **斷電之後誰開機、誰登入？有 UPS 嗎？** Docker Desktop 要有人登入才會起來 | DEP-21 第 4 項、[F-18、F-19](10-first-visit.md) |
| 主機上有沒有 RAM 磁碟？（有的話不得放任何資料） | [F-18](10-first-visit.md) |
| GitHub、Docker Hub、npm、Prisma 引擎、Debian 套件來源是不是常態連得到？經不經代理？ | Q-32 |
| 備份目錄的內容由誰、多久送往另一台機器一次？ | DEP-06 |

---

## 2. 主機這一層

### W-04 確認 Git 與 Docker 可以用

**本系統對主機的要求只有這兩樣**（DEP-04）。不要求、也不准自己裝 Node.js、Python 或 Android SDK。

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
| `git --version` | 有版本號 |
| `docker version` | Client 與 Server 兩段都有版本號 |
| `docker info` | `<版本> linux x86_64`（**一定要是 `linux`**） |
| `docker compose version` | **v2 以上**（0922 現場是 `v5.1.1`，是對的；[F-15](10-first-visit.md)） |

**可能怎麼壞、怎麼處理**

| 症狀 | 原因 | 處置 |
|---|---|---|
| `failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine` | Docker Desktop 沒在跑 | 從開始選單開 Docker Desktop，等它變綠再重試。**記下來：斷電重開沒人登入時就是這樣** |
| `OSType` 是 `windows` | 切到了 Windows 容器模式 | 系統匣 Docker 圖示按右鍵 → Switch to Linux containers |
| `git` 找不到 | 主機沒裝 Git | 問資訊室。**不要自己裝**，那是院方的變更流程 |
| 只有 `docker-compose`（有連字號）能用 | 舊版 Compose v1 | 請資訊室處理。v1 不支援本系統用的 `name:`、`profiles`、外部資料卷寫法 |

---

### W-05 Docker Desktop 的設定與防毒排除

**做什麼**：開 Docker Desktop → Settings，逐項看，**同機有別的專案在用時只看不改**，改動要先知會資訊室（DEP-21 最後一段）。

| # | 位置 | 應該是 | 為什麼 |
|---|---|---|---|
| 1 | General → Start Docker Desktop when you sign in | 勾 | 否則連有人登入都不會啟動 |
| 2 | General → Send usage statistics | 不勾 | 院外連線（FR-S07） |
| 3 | Software updates → Automatically check for updates | 不勾 | 更新 Docker 是院方的變更。**從 Microsoft Store 裝的**，這一項改由市集的自動更新決定，要到市集設定看（[F-16](10-first-visit.md)） |
| 4 | Resources → Advanced → Disk image location | 記下路徑 | 防毒排除要排的就是這個目錄 |

然後請資訊室把第 4 項那個目錄加入防毒排除清單（DEP-21 第 1 項）。

**怎麼知道成功了**：四項抄進演練紀錄；防毒排除清單裡看得到那個目錄。

| 症狀 | 處置 |
|---|---|
| 設定是灰的 | 院方以管理原則鎖住，記下來，由資訊室決定 |
| 資訊室不肯排除整個虛擬磁碟目錄 | 談到有結果。即時掃描正在被寫入的虛擬磁碟，會造成間歇性的鎖定與變慢 |

---

### W-06 對外連線實測

**做什麼**

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
| `github.com` | `git clone`、`git fetch`（走 SSH 時另測 `Test-NetConnection github.com -Port 22`） |
| `registry-1.docker.io`、`auth.docker.io`、`production.cloudflare.docker.com` | 下載基底映像 `node:20-bookworm-slim` |
| `deb.debian.org`（**埠 80**） | 建置時安裝 `openssl` |
| `registry.npmjs.org` | `npm ci` |
| `binaries.prisma.sh` | Prisma 引擎（只在建置時） |

**怎麼知道成功了**：全部 `TcpTestSucceeded : True`。

| 症狀 | 處置 |
|---|---|
| 經代理伺服器，`Test-NetConnection` 是 `False` | 改用 `curl.exe -I https://registry.npmjs.org` 測；Docker 另外要在 Settings → Resources → Proxies 設代理 |
| 22 不通、443 通 | 部署金鑰改走 443：`~/.ssh/config` 的 `HostName` 改成 `ssh.github.com`、加 `Port 443` |
| 有幾個不通 | 補齊再往下。建到一半才失敗更浪費時間 |

---

### W-07 連接埠

**做什麼**

```powershell
Get-NetTCPConnection -State Listen | Where-Object LocalPort -in 3000,8080,8081 | Select-Object LocalPort, OwningProcess
```

把資訊室給的三個埠（後端、護理端、病人端）也照這樣查一次。

**怎麼知道成功了**：要用的三個埠查不到任何結果。

**可能怎麼壞**：查到了——那個埠有人在用（0922 的 3000 就是）。換一個，**並回報資訊室登記**。
**不要自己下 `-p` 把埠對到別的地方**（[F-03](10-first-visit.md)、[F-17](10-first-visit.md)），埠只寫在 `.env` 裡（W-11）。

---

## 3. 取得程式碼

### W-08 建立兩個目錄

```powershell
New-Item -ItemType Directory -Force D:\hd-tablet-care\config, D:\hd-tablet-care\backups | Out-Null
```

`repo` 不先建，由 W-10 的 clone 產生。

**不可以放的地方**：雲端同步資料夾、網路磁碟機代號、RAM 磁碟、`C:\Users\<帳號>\` 底下的桌面／文件／下載（DEP-21 第 2 項、DEP-37）。

---

### W-09 產生部署金鑰（DEP-43）

私鑰在主機上產生、不離開主機；**只有公鑰**交給 repo 管理者登記。0922 那種臨時建立、事後要記得刪的個人權杖不再需要。

**做什麼**

```powershell
ssh-keygen -t ed25519 -C "hd-tablet-care@<主機名稱>" -f $HOME\.ssh\hd-tablet-care -N '""'
Get-Content $HOME\.ssh\hd-tablet-care.pub
```

把印出來的那一行交給 repo 管理者，登記到 GitHub repo 的 **Settings → Deploy keys**，**不要勾 Allow write access**。
外殼 App 的 repo 另產生一把（一把部署金鑰只能對應一個 repo），做法在[第十二冊](12-shell.md) Y-02。

再在 `$HOME\.ssh\config` 加一段，讓這把金鑰只用在這個 repo：

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

看到 `Hi <帳號>/hd-tablet-care! You've successfully authenticated, but GitHub does not provide shell access.`

| 症狀 | 處置 |
|---|---|
| `Permission denied (publickey)` | 公鑰還沒登記，或登記到別的 repo |
| `ssh-keygen` 找不到 | Windows 的 OpenSSH Client 選用功能沒裝。問資訊室 |
| 第一次連線問 `Are you sure you want to continue connecting` | 核對顯示的指紋是 GitHub 公布的那一組再回答 `yes` |

---

### W-10 clone，切到 tag

```powershell
git clone git@github-hd-tablet-care:94sh09sh19sh/hd-tablet-care.git D:\hd-tablet-care\repo
cd D:\hd-tablet-care\repo
git checkout <tag>
git describe --tags
```

**怎麼知道成功了**：`git describe --tags` 印出的正是交付的 tag，不帶 `-g<雜湊>` 尾巴。

| 症狀 | 處置 |
|---|---|
| `HEAD is now at …` 之後出現 detached HEAD 的說明 | 正常。部署本來就不在分支上（DEP-44） |
| `error: pathspec '<tag>' did not match` | tag 沒推上去，回 W-02 |

**之後本冊每一條 docker 指令都在 `D:\hd-tablet-care\repo` 底下下。**

---

## 4. 設定

### W-11 由範本填 `.env`

```powershell
Copy-Item D:\hd-tablet-care\repo\deploy\hospital.env.example D:\hd-tablet-care\config\.env
notepad D:\hd-tablet-care\config\.env
```

範本裡每一項都有說明。必填的：

| 變數 | 填什麼 |
|---|---|
| `HD_IMAGE_TAG` | 與 W-10 的 tag 相同 |
| `HD_BACKUP_DIR`、`HD_CONFIG_DIR` | `D:\hd-tablet-care\backups`、`D:\hd-tablet-care\config` |
| `HD_API_PORT`、`HD_NURSE_PORT`、`HD_PATIENT_PORT` | W-07 確認過的三個埠 |
| `HD_PUBLIC_API_URL` | 護理站連得到的後端位址，例如 `http://<主機名稱>:<後端埠>`。**建置時寫進護理端的產物**（DEP-39） |
| `CORS_ORIGINS` | 護理端的實際位址（病人端與後端同一個來源，不必列） |
| `MDM_KIOSK_BASE_URL` | 平板要連的病人端位址，**一律 `https://`**（第十二冊 Y-03） |
| `HD_SHELL_SRC_DIR`、`HD_SHELL_SIGNING` | 外殼 repo 的 clone 位置與簽章用途（第十二冊 Y-03）。**每一條 compose 指令都會檢查前者**，還沒 clone 也先填好路徑 |
| `JWT_SECRET` | 範本裡有不需要 Node.js 的產生指令 |
| `SUPER_ADMIN_*` | 第一個最高權限帳號，首次登入強制改密碼 |

`LLM_PROVIDER` 維持 `mock`。**填 `lab` 後端會拒絕啟動**（DEP-40），那是刻意的。

為了少打字，之後每次開 PowerShell 先設一個變數：

```powershell
$cfg = "D:\hd-tablet-care\config\.env"
```

**怎麼知道成功了**

```powershell
docker compose --env-file $cfg config --quiet
```

沒有任何輸出就是對的。

| 症狀 | 處置 |
|---|---|
| `required variable HD_... is missing a value: 請設定 …` | 冒號後面就是要填什麼，補上 |
| `couldn't find env file` | `$cfg` 路徑打錯，或這個 PowerShell 視窗還沒設 `$cfg` |

---

### W-12 建立兩個資料卷

```powershell
docker volume create hd-tablet-care-data
docker volume create hd-tablet-care-keys
```

**只在第一次部署時做。** 兩個都標成 external，compose 不會建立、`docker compose down -v` 也刪不掉它們（部署規範 3.3）。

**怎麼知道成功了**：`docker volume ls` 看得到兩個名字。

---

## 5. 建置與啟動

### W-13 建置映像檔

```powershell
docker compose --env-file $cfg build
```

第一次要下載基底映像與套件，約十分鐘。

**怎麼知道成功了**：最後一行 `Image hd-tablet-care:<tag> Built`；`docker images hd-tablet-care` 看得到這個標籤。

| 症狀 | 原因 | 處置 |
|---|---|---|
| `failed to resolve source metadata for docker.io/library/node` | 連不到 Docker Hub | 回 W-06 |
| `npm error code ETIMEDOUT` 或 `ECONNRESET` | 連 npm 不穩 | 再跑一次；已經下載的層會沿用 |
| `pull access denied for hd-tablet-care` | 下的是 `up` 而不是 `build` | 先 `build`。本系統的映像檔一律就地建置，不從任何地方拉（DEP-39） |

---

### W-14 套用既有遷移（DEP-31）

```powershell
docker compose --env-file $cfg run --rm --no-deps api node apps/api/scripts/prisma-cli.mjs migrate deploy --schema apps/api/prisma/schema.prisma
```

**怎麼知道成功了**：最後一行 `All migrations have been successfully applied.`

| 症狀 | 處置 |
|---|---|
| `SQLite database hd.db created at file:/data/hd.db` | 第一次部署時正常 |
| 任何提到 `binaries.prisma.sh` 的錯誤 | 映像檔建壞了（引擎沒在建置時取得）。重建，**不要在執行期開網路讓它下載**（DEP-30） |

---

### W-15 啟動

```powershell
docker compose --env-file $cfg up -d
docker compose --env-file $cfg ps
```

**怎麼知道成功了**：`api`、`nurse-web`、`patient-web` 三個都是 `Up`；`ai-gateway` 與 `shell-builder` **不在清單上是對的**（它們在 `ai`、`shell` 兩個設定檔裡，預設不啟動）。

---

### W-16 確認它是對的那一個

```powershell
curl.exe -s http://localhost:<後端埠>/api/health
docker compose --env-file $cfg logs api --tail 30
```

**怎麼知道成功了**

| 看什麼 | 應該是 |
|---|---|
| health | `{"status":"ok",…}` |
| 日誌 `已連線至 SQLite` 那一行 | `journal_mode=WAL、foreign_keys=ON、busy_timeout=5000ms、synchronous=FULL` |
| 日誌 `版本標記` | 後面寫著 `（正式環境設定）` |
| 日誌 `伺服器時區` | `Asia/Taipei`，現在時間正確 |
| 護理站瀏覽器開 `http://<主機名稱>:<護理端埠>` | 出現登入頁，用 `SUPER_ADMIN_*` 登入後被要求改密碼 |

| 症狀 | 原因 | 處置 |
|---|---|---|
| 護理站開得了頁面，登入時轉圈後失敗 | `HD_PUBLIC_API_URL` 或 `CORS_ORIGINS` 寫錯 | 改 `.env`，**`HD_PUBLIC_API_URL` 改了要重新 build**（寫在產物裡），`CORS_ORIGINS` 只要 `up -d` |
| `api` 一直 Restarting | 設定被後端拒絕 | `logs api` 最後幾行會說哪一條（時區、連接埠、`lab`…），照訊息改 |

---

### W-17 備份一次，並驗證還原得起來

「有備份」和「備份能用」是兩件事（規範 8.1）。

**做什麼**

1. 護理端 **系統管理** 按「立即備份」，記下檔名與 SHA-256
2. 還原到資料卷裡的一個測試檔，跑完整性檢查，再刪掉：

```powershell
docker compose --env-file $cfg run --rm --no-deps api node_modules/.bin/ts-node --project apps/api/tsconfig.json apps/api/scripts/restore-backup.ts --from /backups/<檔名> --to /data/restore-check.db --sha256 <雜湊>
docker compose --env-file $cfg run --rm --no-deps --entrypoint rm api /data/restore-check.db
```

**怎麼知道成功了**：`✓ 與備份歷程上的紀錄相符`、`完整性檢查：ok`；`D:\hd-tablet-care\backups\` 裡看得到那個檔。

---

### W-18 重新開機測試（DEP-21 第 4 項）

**這一條決定這條路線在院內能不能用。** `restart: unless-stopped` 只管 Docker 起來之後；Docker Desktop 是隨使用者登入啟動的程式，**沒人登入，容器就不會起來**。

**做什麼**：重新開機 → 照院方平常的方式登入（或不登入，看院方答覆）→ 等三分鐘 → `docker compose --env-file $cfg ps` 與 W-16 的 health。

**怎麼知道成功了**：三個服務自己回到 `Up`，health 正常，**中間沒有人手動開 Docker Desktop**。

**沒過的話**：記下實況（有沒有自動登入、Docker Desktop 有沒有起來），這是 Q-27 要談的事，不在現場硬改院方的登入設定。

---

## 6. 更新與回退

### W-19 更新（DEP-19，七步）

**排在非透析時段，更新後第一個班次要有人在**（DEP-32）。

```powershell
cd D:\hd-tablet-care\repo
git fetch --tags
git checkout <新 tag>
git describe --tags
```

把 `.env` 的 `HD_IMAGE_TAG` 改成新 tag，然後：

```powershell
docker compose --env-file $cfg build
docker compose --env-file $cfg stop api
docker compose --env-file $cfg run --rm --no-deps api node apps/api/scripts/db-update.mjs --note "<舊 tag> → <新 tag>"
docker compose --env-file $cfg up -d
```

`db-update.mjs` 一次做完四件事：確認 `api` 已停、更新前備份、**驗證備份還原得起來**、套用遷移，並寫進更新紀錄與稽核軌跡（規範 18.4）。任何一關沒過就停，資料庫不會被動到。

**怎麼知道成功了**：輸出最後是 `更新完成`；W-16 各項正常；護理端 **系統管理** 的「版本更新紀錄」多一筆；兩個 tag 記在稽核軌跡的說明裡（`--note`）。

| 症狀 | 處置 |
|---|---|
| `更新中止：後端服務還在執行` | 上一行的 `stop api` 沒做或沒成功。**不要加 `--allow-running`**，那是演練用的 |
| `更新中止：備份目的地可用空間 …不足` | 主機共用，先查是誰佔掉空間（DEP-37） |
| **舊的映像檔** | **不要刪**。新版穩定之前，那是唯一回得去的東西 |

---

### W-20 回退

程式可以退版，**資料庫不能把遷移倒回去**（規範 18.3、FR-S12）。這一版動過 schema 時，回退等於「舊程式＋更新前那份備份」，**更新之後寫進去的資料會一起消失**——所以才要在累積新資料之前決定。

```powershell
cd D:\hd-tablet-care\repo
git checkout <舊 tag>
```

`.env` 的 `HD_IMAGE_TAG` 改回舊 tag（舊映像檔還在，不必重建），然後：

```powershell
docker compose --env-file $cfg stop api
docker compose --env-file $cfg run --rm --no-deps --entrypoint sh api -c "mkdir -p /data/before-rollback && mv /data/hd.db /data/hd.db-wal /data/hd.db-shm /data/before-rollback/ 2>/dev/null; ls -l /data/before-rollback"
docker compose --env-file $cfg run --rm --no-deps api node_modules/.bin/ts-node --project apps/api/tsconfig.json apps/api/scripts/restore-backup.ts --from /backups/<hd-before-update-…>.db --to /data/hd.db --sha256 <雜湊>
docker compose --env-file $cfg up -d
```

備份檔名與雜湊在 W-19 `db-update` 輸出的第 3 步，也在更新紀錄裡。

**怎麼知道成功了**：還原輸出 `完整性檢查：ok`、`還原的就是 DATABASE_URL 指向的正本`；`ps` 裡三個服務的映像檔標籤是舊 tag；護理端的版本標記是舊版。

移到 `/data/before-rollback/` 的那份**先留著**，確定不需要再刪（`docker compose --env-file $cfg run --rm --no-deps --entrypoint rm api -r /data/before-rollback`）。

---

## 7. 開發機實測（DEP-22）

**每一個要交給院方的 tag，都先在開發機上照本冊走一次。** 「從零」的意思：

- **全新的 clone**，不是平常開發的那個工作目錄
- **全新的資料卷**：先確認 `docker volume ls` 裡沒有 `hd-tablet-care-*`，有就先照第 8 節撤除
- **只用 Git 與 Docker**，指令與院內一字不差；開發機上的 Node.js 在這一輪裡不得被用到
- 設定照範本另填一份，位址用 `localhost`，埠挑開發時沒在用的（例如 13000、18080、18081）

| # | 驗什麼 | 本冊步驟 |
|---|---|---|
| 1 | 從 clone 到服務起來，全程沒有人工補步驟，每一步輸出存檔 | W-08～W-17 |
| 2 | `npm run verify:iteration11 -- --live --env-file <設定目錄>\.env`：`down -v` 之後資料還在、繫結掛載只有兩個、正式環境設定拒絕 `lab` | 這一條是唯一允許用 Node 的，**它是驗收，不是部署步驟** |
| 3 | 更新一次：打一個測試 tag，照 W-19 走完 | W-19 |
| 4 | 回到上一版，資料完整 | W-20 |
| 5 | 開發手機裝外殼、釘住、護理端看得到（迭代 12 起） | [第十二冊](12-shell.md)第 7 節 |
| 6 | AI 經 SSH 通道接實驗室閘道跑一次（迭代 13 起） | — |

**在 Git Bash 裡照抄會壞的一件事**：Git Bash 會把 `/backups/…`、`/data/…` 這種參數自動轉成 Windows 路徑，
還原腳本就會回報找不到備份檔。**本冊一律用 PowerShell**；非用 Git Bash 不可時，先 `export MSYS_NO_PATHCONV=1`，
`--env-file` 也要寫成 `C:/…` 的形式。

---

## 8. 關服務

原則與三種深度見[第八冊](08-shutdown.md)，容器版的指令：

| 深度 | 指令 | 資料 |
|---|---|---|
| 暫停（維護、換版） | `docker compose --env-file $cfg stop` | 不動 |
| 停用（不再自動起來） | `docker compose --env-file $cfg down` | 不動。資料卷是 external，`down -v` 也刪不掉 |
| 撤除（試用結束） | `down` 之後先做最後一次備份並確認已送到另一台機器，再 `docker volume rm hd-tablet-care-data hd-tablet-care-keys`、刪映像檔與 `D:\hd-tablet-care\` | **刪了就沒有了**。要院方書面同意，照第八冊撤除那一節做 |

**`docker compose down` 只關得到 `hd-tablet-care` 這個專案**（專案名稱寫死在 compose 檔裡，DEP-37 第 1 項）。不要用 `docker stop $(docker ps -q)` 這種會關到別人容器的寫法。

---

## 9. 疑難排解（這一冊特有的）

| 症狀 | 原因 | 處置 |
|---|---|---|
| `Error code 14: Unable to open the database file` | 資料卷不是由 compose 掛上，或手動開的容器以 root 建了檔 | 只用本冊的指令；手動開過的容器全部刪掉，重新 `up -d` |
| `正式環境設定下不得使用 LLM_PROVIDER=lab` | `.env` 抄了開發機的設定 | 改回 `mock`（或迭代 13 之後的 `onprem`）。這是刻意擋的（DEP-40） |
| `時區…不是正式環境要求的 Asia/Taipei` | compose 的 `TZ` 被改過 | 還原 compose 檔。compose 檔不在主機上改，要改回開發端改、打新 tag |
| `docker compose --profile ai build` 失敗：找不到 Dockerfile | AI 閘道在迭代 13 才補上 | 目前預設不啟動它，正常 |
| `bind source path does not exist` | `HD_BACKUP_DIR` 或 `HD_CONFIG_DIR` 指的目錄不存在 | 回 W-08 |
| 連接埠 `address already in use` | 同機別的專案佔用 | 回 W-07 換埠，登記後改 `.env` |
| 平板或護理站開得了頁面，資料打不回來 | 產物裡寫死的後端位址不對 | W-16 表格第一列 |

---

## 10. 還沒到的部分

| 元件 | 狀態 |
|---|---|
| `ai-gateway`（AI 閘道） | 服務、設定檔掛載、`ai` 設定檔已定；程式在**迭代 13** |
| `shell-builder`（外殼 APK 建置） | **0927 迭代 12 完成**，見[第十二冊](12-shell.md) |
| 病人端下載頁、HTTPS | **0927 迭代 12 完成**，見第十二冊 Y-07 |

---

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|

[← 回部署手冊總覽](index.md)
