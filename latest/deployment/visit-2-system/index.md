# 第二次進院（1001）· 從零部署本系統

> - 狀態：**已照做 1001，凍結**。結果見[《第二次進院紀錄（1001，部分成功）》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/record-2-1001/index.md)；登不進去的分析見[《第二次進院紀錄（1001）之一：為什麼登不進去》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/record-2-1001-login/index.md)。之後要從零部署，照[《從零部署本系統》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fresh-install/index.md)（`V-xx`）
> - 1117 由舊的第十四冊改寫；每一步的「為什麼、完整指令、會看到的原文、不對怎麼辦」在詳細版
> - 編號 `N-xx`；每一步沿用的原步驟（`W-xx`、`Y-xx`、`Z-xx`）寫在詳細版

子文件：

- [《第二次進院（1001）· 從零部署本系統之一：詳細版》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-2-system-detail/index.md)
- [《第二次進院（1001）· 從零部署本系統之二：`.env` 怎麼填》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-2-system-env/index.md)
- [《第二次進院（1001）· 從零部署本系統之三：收掉 0922 留下的東西》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-2-system-cleanup/index.md)（`L-xx`，N-04 之前做）

## 摘要

- 1001 照這一冊從一台沒部署過本系統的主機走：主機這一層 → 程式碼 → `.env` → 建置啟動 → 備份與重新開機 → 外殼與平板 → AI 閘道 → 收尾
- 同一套步驟也是開發機的模擬部署（🧪），院內正式主機標 🏥；整趟共通的差異在下面那張表
- 🏥 N-04 之前先照《之三》收掉 0922 留下的容器 `dialysis_system_v0`
- 1001 實際做到 N-23，卡在 N-16 的登入（`Failed to fetch`）；N-17、N-18、N-24～N-27 沒做
- 🧪 只在開發機做的 N-30 驗收、N-31 撤除另成最後一節
- 每一步只寫做什麼、怎樣算成功；「成功」那一格沒看到就是沒成功，不要往下

## 🏥／🧪 整趟不同的地方

| 項次                          | 🏥 院內正式主機                                                        | 🧪 開發機演練                                     | 在哪一步   |
| ----------------------------- | ---------------------------------------------------------------------- | ------------------------------------------------- | ---------- |
| 機器                          | 院內主機                                                               | 你的開發機                                        | —          |
| 0922 留下的容器與 clone       | 先收掉（《之三》）                                                     | 沒有，不必做                                      | N-04 之前  |
| Git 與 Docker                 | 資訊室已裝好，**不准自己裝**                                           | 自己裝                                            | N-04       |
| 根目錄（`$root`）             | `D:\hd-tablet-care`（1001 實際放 `C:\hd\hd-tablet-care`，見紀錄 M-03） | `C:\hd-sim`                                       | N-08       |
| 問資訊室的問題清單            | 至少一週前寄出                                                         | 不必                                              | N-02       |
| Docker Desktop 設定、防毒排除 | 逐項檢查，改動要資訊室同意                                             | 看一眼即可                                        | N-05       |
| 三個連接埠                    | `13000`、`18080`、`18081`（0930 資訊室確認）                           | 同樣用 `13000`、`18080`、`18081`，被佔用就自己換  | N-07       |
| 部署金鑰                      | 主機上產生，登記到 GitHub                                              | 開發機上另產生一把，同樣登記                      | N-09、N-19 |
| 位址                          | 主機名稱或院內 IP                                                      | 護理端用 `localhost`；平板那一條用開發機的區網 IP | N-11       |
| APK 簽章用途                  | `hospital`                                                             | `dev`                                             | N-11       |
| 平板                          | 院內的平板                                                             | 開發用的 Android 手機                             | N-24～N-27 |
| 驗收工具                      | 不跑（主機上沒有、也不准裝 Node.js）                                   | 多跑三支 `verify:iteration… --live`               | N-30       |
| 重新開機測試                  | **必做**，決定這條路線在院內能不能用                                   | 驗不出院內的情形，可略                            | N-18       |
| 備份送往另一台機器            | 院方負責，要當場確認                                                   | 不必                                              | N-17       |
| 做完之後                      | 交接，服務留著跑                                                       | **撤除乾淨**，下一次才又是「從零」                | N-31       |

從 N-04 起，所有指令都在「要部署的那台機器」的 PowerShell 裡打；不要自己開任何容器，不要下 `docker run -v`、`-p`。

## 1. 動手之前

### N-01 約好人

**做什麼**：至少一週前，向資訊室約一位能登入那台主機、有管理員權限的同仁全程在旁；另約護理長或指定的護理師，交接時要在。

**成功**：有具體的人名與時段。

🧪 跳過。

### N-02 把問題清單寄給資訊室

**做什麼**：把七個問題寄出去（0930 已有答案的不再問），答覆寫進演練紀錄。最要緊的三題：斷電之後誰開機、誰登入；Send usage statistics 能不能關；Microsoft Store 的自動更新能不能改成手動。

**成功**：每一題都有答覆，或寫明「未答覆」與對方是誰。

🧪 跳過。

### N-03 確認要交的 tag 已經模擬部署過、而且在 GitHub 上

**做什麼**：在開發機的工作目錄打：

```
git ls-remote --tags origin
git rev-parse <tag>
git show <tag>:services/shell-builder/shell.pin
```

**成功**：清單裡有要交的 tag；commit 與模擬部署時同一個；`SHELL_TAG=` 那一版在外殼 repo 的 Tags 頁看得到；演練紀錄裡這個 tag 的模擬部署沒有 ✗。

🧪 這一步就是準備要測的 tag：兩個 repo 的 tag 都要先推上 GitHub。

## 2. 主機這一層

🏥 開始之前先照[《之三》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-2-system-cleanup/index.md)收掉 0922 留下的容器 `dialysis_system_v0` 與那份 clone；容器沒收掉不開始部署。

### N-04 確認 Git 與 Docker 能用

**做什麼**

```
git --version
docker version
docker info --format "{{.ServerVersion}} {{.OSType}} {{.Architecture}}"
docker compose version
```

**成功**：Git 有版本號；`docker version` 的 `Client`、`Server` 兩段都有版本號；`docker info` 印出 `<版本> linux x86_64`（中間一定是 `linux`）；Compose 是 `v2` 以上。

🏥 `git` 或 `docker` 找不到：問資訊室，不要自己裝。

🧪 沒有就自己裝 Git for Windows 與 Docker Desktop，裝完重新開機再做一次。

### N-05 Docker Desktop 的設定與防毒排除

**做什麼**：Docker Desktop → Settings，看四項（登入時自動啟動、Send usage statistics、自動檢查更新、Disk image location），抄進演練紀錄；請資訊室把 Disk image location 那個資料夾加入防毒排除清單。

**成功**：四項抄進演練紀錄；防毒排除清單裡看得到那個資料夾。

🏥 同一台機器有別的專案在用時只看不改，要改先知會資訊室。

🧪 看一眼、抄下來即可，防毒排除不必做。

### N-06 確認連得出去

**做什麼**：對九個網址打 `Test-NetConnection`（清單在詳細版）。

**成功**：每一條最後都是 `TcpTestSucceeded : True`。

🧪 開發機通常全部通，照做一次確認即可。

### N-07 確認三個連接埠沒人用

**做什麼**

```
Get-NetTCPConnection -State Listen | Where-Object LocalPort -in 13000,18080,18081 | Select-Object LocalPort, OwningProcess
```

**成功**：什麼都沒印出來。

🏥 印出了某個埠就先停手回報資訊室，不要自己換。

🧪 被佔用就自己換一個；三個埠記下來，N-11 要用。

## 3. 取得程式碼

### N-08 建立資料夾，並設好開工三行

**做什麼**

```
$root = "D:\hd-tablet-care"          # 🧪 改成 C:\hd-sim
$cfg  = "$root\config\.env"
New-Item -ItemType Directory -Force "$root\config", "$root\backups" | Out-Null
Get-ChildItem $root
$cfg
```

**成功**：列出 `backups`、`config` 兩個資料夾，最後一行印出 `D:\hd-tablet-care\config\.env`。之後每開一個新的 PowerShell 視窗，都先打一次開工三行（`$root`、`$cfg`、`cd $root\repo`）。

🧪 根目錄是 `C:\hd-sim`，最後一行是 `C:\hd-sim\config\.env`。

### N-09 產生本系統 repo 的部署金鑰

**做什麼**：產生 `hd-tablet-care` 金鑰 → 公鑰交 repo 管理者登記到 Deploy keys（不勾 Allow write access）→ `$HOME\.ssh\config` 加 `Host github-hd-tablet-care` 那一段。

**成功**：`ssh -T github-hd-tablet-care` 最後印出 `Hi 94sh09sh19sh/hd-tablet-care! You've successfully authenticated, but GitHub does not provide shell access.`

🧪 開發機上另產生一把，不要拿平常推程式碼的金鑰頂替；登記標題寫「模擬部署（開發機）」。

### N-10 clone 程式碼，切到 tag

**做什麼**

```
git clone git@github-hd-tablet-care:94sh09sh19sh/hd-tablet-care.git $root\repo
cd $root\repo
git checkout <tag>
git describe --tags
```

**成功**：最後一行正好是那個 tag，後面沒有 `-3-g1a2b3c4` 這種尾巴。

🧪 一定要從 GitHub 全新 clone 到 `C:\hd-sim\repo`，不要複製工作目錄。

## 4. 設定

### N-11 由範本填 `.env`

**做什麼**：`Copy-Item $root\repo\deploy\hospital.env.example $cfg`、`notepad $cfg`，照[《之二》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-2-system-env/index.md)逐項填；外殼 App 那三項現在就一起填。

**成功**：`docker compose --env-file $cfg config --quiet` 什麼都沒印出來。

🏥／🧪 填的值不同，《之二》每一項都分開寫。

### N-12 建立兩個資料卷

**做什麼**：`docker volume create hd-tablet-care-data`、`docker volume create hd-tablet-care-keys`，再 `docker volume ls`。只在第一次部署時做。

**成功**：清單裡看得到這兩個名字。

🧪 做之前先 `docker volume ls`，不該已經有 `hd-tablet-care-` 開頭的；有就照 N-31 撤除再回來。

## 5. 建置與啟動

### N-13 建置映像檔

**做什麼**：`docker compose --env-file $cfg build`（第一次約十分鐘）。

**成功**：最後出現 `Image hd-tablet-care:<tag> Built`；`docker images hd-tablet-care` 看得到這個 tag。

### N-14 建立資料庫

**做什麼**（一整行）

```
docker compose --env-file $cfg run --rm --no-deps api node apps/api/scripts/prisma-cli.mjs migrate deploy --schema apps/api/prisma/schema.prisma
```

**成功**：最後一行 `All migrations have been successfully applied.`

### N-15 啟動

**做什麼**：`docker compose --env-file $cfg up -d`，再 `docker compose --env-file $cfg ps`。

**成功**：`api`、`nurse-web`、`patient-web` 三個都是 `Up`；`ai-gateway` 與 `shell-builder` 不在清單上是對的。

### N-16 確認它是對的

**做什麼**：`curl.exe -s http://localhost:13000/api/health`、看 `logs api --tail 30`，再用瀏覽器開護理端、用 `.env` 的 `SUPER_ADMIN_*` 登入。

**成功**：health 是 `{"status":"ok",…}` 開頭；日誌有 `synchronous=FULL`、`（正式環境設定）`、`Asia/Taipei`；登入後被要求改密碼。

🏥 在護理站的電腦開 `http://<主機名稱>:18080`；改完密碼把新密碼交給院方指定的人保管。

🧪 在開發機開 `http://localhost:18080`。

## 6. 備份與重新開機

### N-17 備份一次，並證明還原得回來

**做什麼**：護理端 → 系統管理 → 立即備份，記下檔名與雜湊；用 `restore-backup.ts` 還原到測試檔，再刪掉測試檔（指令在詳細版，一律用 PowerShell）。

**成功**：輸出有 `✓ 與備份歷程上的紀錄相符` 與 `完整性檢查：ok`；`$root\backups\` 有那個檔和同名的 `.sha256`。

🏥 當場問清楚備份由誰、多久送往院內另一台機器。

🧪 還原成功即可，不必送往任何地方。

### N-18 重新開機測試

**做什麼**：重新開機 → 照院方平常的方式登入（或不登入）→ 等三分鐘 → 開工三行 → `docker compose --env-file $cfg ps` 與 health。

**成功**：三個服務自己回到 `Up`、health 正常，中間沒有人手動開 Docker Desktop。

🧪 可以跳過。

## 7. 外殼 App 與平板

### N-19 外殼 repo 的部署金鑰與 clone

**做什麼**：另產生 `hd-kiosk-shell` 金鑰、登記到外殼 repo、`.ssh\config` 加 `Host github-hd-kiosk-shell`；`ssh -T` 後 clone 到 `$root\hd-kiosk-shell`（不切 tag）。

**成功**：`ssh -T github-hd-kiosk-shell` 印出 `Hi 94sh09sh19sh/hd-kiosk-shell!…`；`git -C $root\hd-kiosk-shell tag` 列得出 N-03 那一版（連舊版一起列出是對的）。

🧪 與 N-09 相同，開發機上另產生一把、標題註明模擬部署。

### N-20 建 `shell-builder` 的映像檔

**做什麼**：`docker compose --env-file $cfg --profile shell build shell-builder`（第一次下載約 1.5 GB）。

**成功**：最後幾行有「✓ 外殼 v0.x.x（…，契約第 1 版）已準備好，相依已下載」。

### N-21 建 APK（第一次會產生金鑰）

**做什麼**：`docker compose --env-file $cfg --profile shell run --rm shell-builder`，跑兩次。

**成功**：第一次印出「這一次新產生：…」、APK 檔名與三個 SHA-256（抄下來）；第二次印出「金鑰全部沿用，這一次沒有產生任何新的金鑰」，簽章憑證的 SHA-256 與第一次相同。

🧪 第一次那行寫「APK 簽章金鑰（開發用）」，是對的。

### N-22 備份金鑰，並核對還原得回來

**做什麼**：`shell-builder keys-backup`，再 `shell-builder keys-verify`。

**成功**：第一條印出「已備份：備份目錄/keys/hd-keys-\<時間>.tar.gz」；第二條每一項都 ✓，最後「還原得回來」。

### N-23 讓病人端改走 HTTPS

**做什麼**：`docker compose --env-file $cfg restart patient-web`，再看 `logs patient-web --tail 5`。

**成功**：最後一次啟動的日誌有「（HTTPS；HTTP 只留外殼下載頁）」；`http://localhost:18081/shell/` 看得到下載頁；`http://localhost:18081/` 轉到 `https://` 並跳出憑證警告是對的。

### N-24 平板連得到主機

**做什麼**：平板連上平常要用的 Wi-Fi，瀏覽器開 `http://<平板要連的位址>:18081/shell/`。

**成功**：看得到下載頁。

🧪 手機和開發機連同一個 Wi-Fi，位址是開發機的區網 IP；開不到的處置在詳細版。

### N-25 在護理端註冊平板

**做什麼**：護理端 → 新增裝置 → 註冊新平板；畫面上的 QR code 與網址只顯示一次，先不要關。

**成功**：畫面上的網址以 `https://` 開頭。

### N-26 平板的系統設定並安裝 App

**做什麼**：設裝置 PIN、關「新增使用者」；開螢幕固定並勾「解除固定前要求 PIN」；從下載頁下載並安裝 App。

**成功**：平板上多了「透析照護平板」。

### N-27 第一次開啟並釘住

**做什麼**：掃 N-25 的 QR code → 儲存並啟動 → 確定固定；解除一次、再釘回去。

**成功**：平板是病人端的等待畫面、沒有憑證警告、離不開；護理端「固定狀態」是固定中（解除時變已跳出）、「外殼版本」正常。把序號與床號的對應記下來。

🧪 用開發用的 Android 手機；做完把 App 解除安裝。

## 8. AI 閘道：讓它就位

### N-28 放 AI 閘道的設定檔

**做什麼**：建 `$root\config\ai-gateway`，把 `services\ai-gateway\config.hospital.example.yaml` 複製成 `config.yaml`。

**成功**：設定檔在 `$root\config\ai-gateway\config.yaml`，`base_url` 與 `model` 保持空白（不填任何位址）。

### N-29 建置並啟動閘道

**做什麼**：`--profile ai build ai-gateway`、`--profile ai up -d ai-gateway`，再從 `api` 容器打閘道的 health。

**成功**：建置最後印出 `全部通過`；health 印出 `503 {"status":"error","config":"error","detail":"base_url 尚未填寫（推論端點的位址）"}`。

## 9. 收尾

### 🏥 冒煙測試與交接（沒有編號）

**做什麼**：在護理站的電腦走一次主線（虛構資料）、開總覽螢幕、現場教學、寫交接文件、當天晚上補演練紀錄。

**成功**：交接文件第一行寫「首波試用、不是全單位上線」，十個項次都有內容（清單在詳細版）。

## 10. 只在開發機做（🧪）

### N-30 跑三支驗收

**做什麼**：在平常開發的工作目錄打 `npm run verify:iteration11`、`12`、`13`，都加 `-- --live --env-file C:\hd-sim\config\.env`；再各走一次更新（W-19）與退回（W-20）。

**成功**：三支都全部 ✓；結果填進演練紀錄。

### N-31 撤除

**做什麼**：`down` 全部 profile、刪兩個資料卷與 `hd-tablet-care*` 映像檔、刪 `C:\hd-sim`、刪 N-24 加過的防火牆規則、手機上的 App 解除安裝。

**成功**：`docker volume ls` 與 `docker images` 看不到 `hd-tablet-care` 開頭的東西；`C:\hd-sim` 不存在。

🏥 撤除只准在開發機做。

## 版本歷程

| 定版 | 日期 | 異動 |
| ---- | ---- | ---- |
|      |      |      |

[← 回部署手冊目錄](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/index.md)
