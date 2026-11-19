# 第一次進院（0922）· 部署本系統之七：git clone＋Docker 路線詳細版（D-19～D-27）

上層文件：《[第一次進院（0922）· 部署本系統](visit-1-system.md)》

> - 狀態：**已照做 0922，凍結**，結果見《[第一次進院紀錄（0922，失敗）](record-1-0922.md)》；這條路線 0926 起由《[從零部署本系統之一：容器路線的原冊](ref-fresh-install-detail.md)》取代，本冊是歷史
> - 1117 由舊的第九冊改寫（0923 定版，當時「要印出來帶進去」）
> - 編號：`D-xx`

> ⚠️ **0922 的教訓（F-01～F-03）**：本冊所有指令都在**主機的 PowerShell** 下，不要自己先開任何容器，也不要自己下 `-v`、`-p`；容器由 D-19 的 `docker compose up -d` 產生。本冊的指令是 0921 那一版程式的，之後程式與 `.env` 欄位改過（0926 起部署一律 checkout tag、埠只寫在 `.env`；1027 起多了必填的 `HD_EXPORT_DIR`），**不要照抄到現在的院內主機**，現行做法看《[從零部署本系統](ref-fresh-install.md)》。

接在《[之六：git clone＋Docker 路線詳細版（D-13～D-18）](visit-1-system-docker-3.md)》後面。

## 摘要

- 第 6 節啟動與驗證：D-19 `docker compose up -d`，三個容器 `Up`、存活檢查 200；D-20 資料庫四項設定
- D-21 從護理站連進來並走一次主線；D-22 容器重新啟動會自己回來（不證明主機重新開機沒問題）
- D-23 備份並驗證還原得起來，複製一份到院內另一台機器核對雜湊
- 第 7 節收掉連線與憑證：D-24 關對外連線並自己確認、D-25 清憑證並當天作廢權杖
- D-26 重新開機測試，決定這條路線能不能用
- 第 8 節 D-27：從《進院當天詳細版》H-14 起回去，哪些照做、哪些要換

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

紀錄檔裡會有一行黃色的 `時區來自環境變數 TZ（Asia/Taipei）……` 警告，**這在容器裡是正常的**：容器沒有「主機時區設定」可以看，時區就是 compose 給的那個 `TZ`。

**可能怎麼壞、怎麼處理**

| 症狀 | 原因 | 處置 |
|---|---|---|
| `api` 一直 `Restarting` | 啟動就倒 | `docker compose logs api --tail 80` 看最後的錯誤，對照本表與《[現場疑難排解](ref-troubleshooting.md)》 |
| `Bind for 0.0.0.0:3000 failed: port is already allocated` | 埠被別人佔了 | D-13 那行指令找出是誰，換埠，改 `.env` |
| `pull access denied for hd-tablet-care` | `HD_IMAGE_TAG` 與 D-14 的標籤不一致，compose 以為要去下載 | 改 `.env` |
| `缺少必要環境變數` | compose 沒把值傳進去 | 看 `docker-compose.yml` 的 `environment` 有沒有那一項；**不要**改成 `env_file`（檔案開頭有寫為什麼） |
| `拒絕啟動` 且提到時區 | `.env` 的 `TZ` 被改掉了 | 改回 `Asia/Taipei` |

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

### D-21 從護理站連進來

**做什麼**

照《[進院當天詳細版](visit-1-system-onsite-2.md)》H-15，請資訊室開三個埠的輸入規則，然後**到護理站那台電腦上**開 `http://<主機位址>:<HD_NURSE_PORT>`，登入。

接著照 H-16 走一次主線。

**怎麼知道成功了**

在護理站的電腦上登得進去，主線走得完。

**可能怎麼壞、怎麼處理**

| 症狀 | 原因 | 處置 |
|---|---|---|
| 畫面出得來、登入沒反應 | 映像檔裡的後端位址不對 | D-15 應該已經擋下。沒擋下就是 D-13 的主機位址給錯，**重建映像檔**（D-14～D-15），不必重做資料 |
| 主控台出現 CORS 錯誤 | `CORS_ORIGINS` 沒填對 | 改 `.env`，`docker compose up -d`（會自動重建有變動的容器） |
| 主機上連得到、別台連不到 | Windows 防火牆 | Docker Desktop 開的埠一樣要有輸入規則。請資訊室以埠號開，不要以程式開 |

### D-22 常駐：確認它會自己回來

**做什麼**

```powershell
docker compose restart
docker compose ps
curl.exe -i http://localhost:<HD_API_PORT>/api/health
```

**怎麼知道成功了**

三個都回到 `Up`，存活檢查 200。

> 這只證明「容器重新啟動沒問題」，**不證明主機重新開機沒問題**。那是 D-26。

### D-23 備份並驗證還原得起來

**做什麼**

用正式環境的更新腳本做一次「備份 → 還原驗證」。它會先備份、還原到另一個檔案做完整性檢查與筆數核對，沒有待套用的遷移時就只留下一筆紀錄：

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
| 還是 `True` | 與《[安裝包路線之八](ref-installer-git-clone-3.md)》G-17 相同：**服務可以留著，但不得開始輸入真實病人資料**，直到連線關閉 |
| 關了之後 Docker Desktop 跳出登入或更新的提示 | 關掉即可。D-08 第 2、3 項沒設好的話會一直跳 |

（後來的答案：0930 Q-32 答主機對外連線是常態、沒有限制，見《[第一次進院（0922）· 部署本系統](visit-1-system.md)》的已知空白。）

### D-25 清掉憑證

**做什麼**

```powershell
cd C:\hd\hd-tablet-care
git remote -v
git config --show-origin --get-regexp "credential"
cmdkey /list | Select-String -Pattern "git"
```

有列出東西就照《[安裝包路線之六](ref-installer-git-clone.md)》G-08 刪掉。 **clone 目錄不要刪**：更新時要在這裡 `git fetch` 與重建，`.env` 與 `docker-compose.yml` 也在這裡。

回到院外之後，**當天**到 GitHub 把 D-04 那把權杖作廢（Settings → Developer settings → Personal access tokens → Delete），不要等它自己過期。

**怎麼知道成功了**

- `git remote -v` 的網址裡沒有權杖
- 後兩行都沒有任何 `git` 或 `github` 的項次
- 交付單背面的權杖已劃掉，紀錄寫「D-04 權杖已作廢，<時間>」

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
| 登入之後 Docker 起來了，但容器沒有 | 看 `docker compose ps -a` 的狀態。`Exited` 且是你手動停的，`unless-stopped` 不會把它帶回來——**這是對的**，那是第 9 節「停用」的做法 |
| 今天沒辦法重新開機 | 記下「重新開機後未驗證」，請資訊室下次開機後代看，**並約好誰回報你** |

## 8. 回到進院當天詳細版

### D-27 回到《進院當天詳細版》：哪些照做、哪些要換

從《[進院當天詳細版](visit-1-system-onsite-2.md)》H-14 起回去，對照下表：

| 《進院當天詳細版》 | 這條路線 |
|---|---|
| H-14 ① 防毒排除資料庫目錄 | 換成 D-08 的**虛擬磁碟目錄**，再加上備份目錄 |
| H-14 ② ③ 雲端同步、網路磁碟 | 看**備份目錄**與**虛擬磁碟目錄**，不是資料目錄（資料在資料卷裡） |
| H-14 ④ ⑤ 休眠、更新時段 | 照做。**Windows 更新重新開機之後的情形，就是 D-26** |
| H-15、H-16 | 已在 D-21 做完 |
| H-17 備份與還原 | D-23 做了「還原驗證」；**真的還原一次**的做法見第 10 節 |
| H-18 起 | 照做 |
| H-21 交接文件 | 多寫四件事：clone 目錄的位置、映像檔標籤、`docker-users` 名單（D-09）、重新開機後的啟動方式（D-26） |
| 帶進去與帶出來 C-xx（《[進院通則](ref-visit-rules.md)》、隨身碟部分在《[安裝包路線](ref-installer.md)》） | 照做。隨身碟這次可能沒用上，**仍然要當場清除並寫明**（DEP-28） |

上一份：《[之六：git clone＋Docker 路線詳細版（D-13～D-18）](visit-1-system-docker-3.md)》｜下一份：《[之八：git clone＋Docker 路線詳細版（第 9～12 節）](visit-1-system-docker-5.md)》

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|
| [1118](https://94sh09sh19sh.github.io/hd-docs/1118/deployment/visit-1-system-docker-4/) | 2026-11-18 | 首次定版。1118 照每份約 300 行的上限由《第一次進院（0922）· 部署本系統之四：git clone＋Docker 路線詳細版》拆出，內容與步驟編號不動 |

[← 回部署手冊目錄](index.md)
