# 第一次進院（0922）· 部署本系統之八：git clone＋Docker 路線詳細版（第 9～12 節）

上層文件：《[第一次進院（0922）· 部署本系統](visit-1-system.md)》

> - 狀態：**已照做 0922，凍結**，結果見《[第一次進院紀錄（0922，失敗）](record-1-0922.md)》；這條路線 0926 起由《[從零部署本系統之一：容器路線的原冊](ref-fresh-install-detail.md)》取代，本冊是歷史
> - 1117 由舊的第九冊改寫（0923 定版，當時「要印出來帶進去」）
> - 編號：`D-xx`

> ⚠️ **0922 的教訓（F-01～F-03）**：本冊所有指令都在**主機的 PowerShell** 下，不要自己先開任何容器，也不要自己下 `-v`、`-p`；容器由 D-19 的 `docker compose up -d` 產生。本冊的指令是 0921 那一版程式的，之後程式與 `.env` 欄位改過（0926 起部署一律 checkout tag、埠只寫在 `.env`；1027 起多了必填的 `HD_EXPORT_DIR`），**不要照抄到現在的院內主機**，現行做法看《[從零部署本系統](ref-fresh-install.md)》。

接在《[之七：git clone＋Docker 路線詳細版（D-19～D-27）](visit-1-system-docker-4.md)》後面。

## 摘要

- 第 9 節關服務的容器版：暫停、停用、撤除三種深度；手動停過的容器重新開機後不會自己回來
- 撤除時不得刪資料卷（`docker volume rm`、`down -v`、`system prune --volumes`）
- 第 10 節之後的更新、回退、還原一份備份到資料卷（0921 這一版的寫法；現行做法在《本系統換版與退回》）
- 第 11 節容器路線特有的疑難排解
- 第 12 節離院前多五條，接在 H-22 的清單後面

## 9. 關服務（對照《備份、還原與關服務》）

現行的關服務做法在《[備份、還原與關服務](ref-backup-shutdown.md)》（`S-xx`）。0921 這一版的對照是：三種深度、S-01 告知病房、S-06～S-09 的撤除規則全部照用，只是指令換掉：

| 深度 | 指令 | 重新開機後 |
|---|---|---|
| **暫停** | `docker compose stop`，做完事再 `docker compose start` | **不會**自己回來（`unless-stopped` 記得你手動停過） |
| **停用** | 同暫停。另外在交接與紀錄寫明「已停用，恢復要先問 <誰>」 | 不會 |
| **撤除** | `docker compose down`，再依 S-08 那張表收拾 | — |

> **注意和安裝包路線反過來的地方**：安裝包的「暫停」在重新開機後會自己回來，這裡不會。所以這裡的暫停已經是停用的效果，**做完事一定要記得 `start`**，並確認三個都是 `Up`。

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

- **不要**下 `docker volume rm hd-tablet-care-data`、`docker compose down -v`、`docker system prune --volumes`。資料卷就是資料庫，依 S-09 由院方決定去向
- 要把資料交給院方，先照 D-23 或護理端的立即備份做一份到 `D:\hd-backup`，交出那一份

## 10. 之後的更新、回退與還原

現行做法在《[本系統換版與退回](ref-upgrade.md)》（W-19、W-20）與《[備份、還原與關服務](ref-backup-shutdown.md)》；以下是 0921 這一版的寫法。

### 更新

每一次都是**開連線 → 建新映像檔 → 關連線 → 備份與遷移 → 換版**，省不了哪一步。排在非透析時段，更新後第一個班次要有人在（DEP-32）。

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

`db-update.mjs` 會先備份並驗證還原，**沒過就停在那裡、不遷移**。 **舊版映像檔不要刪**，新版穩定之前那是唯一能退回去的東西。

### 回退

```powershell
notepad .env                        # HD_IMAGE_TAG 改回舊版標籤
docker compose up -d
```

**這一版動過資料庫結構時**，要先還原 `db-update.mjs` 印出的那一份 `hd-before-update-*.db`，再換回舊版。 **程式可以退版，資料庫不能退版**，不要試圖把遷移倒回去（規範 18.3）。

### 還原一份備份到資料卷

```powershell
docker compose down
docker run --rm --entrypoint sh -v hd-tablet-care-data:/data -v D:/hd-backup:/backups:ro hd-tablet-care:<標籤> -c "mkdir -p /data/before-restore && mv /data/hd.db* /data/before-restore/ && cp /backups/<備份檔名> /data/hd.db && ls -la /data"
docker compose up -d
```

- 原本的 `hd.db` 與 `-wal`、`-shm` **三個一起**搬進 `before-restore/`，不刪（DEP-09）
- 啟動後紀錄檔可能出現一行 `1 筆備份於上次服務停止時中斷，已標記為失敗`：那是備份當下正在進行的那一筆，**正常**
- 到護理端核對筆數與最後一筆資料的時間，確認還原的是對的那一份

## 11. 疑難排解（這一冊特有的）

一般症狀仍查《[現場疑難排解](ref-troubleshooting.md)》；以下是容器路線才有的：

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

## 12. 離院前多五條

照《[進院當天詳細版](visit-1-system-onsite-3.md)》H-22 的清單，再加：

- [ ] 對外連線已關閉，D-24 當場確認過
- [ ] 權杖已從主機上清掉（D-25），**回去當天作廢**
- [ ] `docker-users` 名單已寫進交接（D-09）
- [ ] 重新開機測試做了，結果寫進紀錄；沒做的話，**誰在什麼時候代看**（D-26）
- [ ] 交接文件寫明：資料在資料卷 `hd-tablet-care-data`、**不得執行的三個指令**（第 9 節）、備份在哪個目錄

紀錄寫進《[部署演練紀錄](../notes/deployment-drills.md)》，「交付形態」寫「git clone ＋ Docker」，每一步的耗時照記，**D-14 的建置時間尤其要記**——它決定下一次更新要留多長的時段。

上一份：《[之七：git clone＋Docker 路線詳細版（D-19～D-27）](visit-1-system-docker-4.md)》

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|
| 1118 | 2026-11-18 | 首次定版。1118 照每份約 300 行的上限由《第一次進院（0922）· 部署本系統之四：git clone＋Docker 路線詳細版》拆出，內容與步驟編號不動 |

[← 回部署手冊目錄](index.md)
