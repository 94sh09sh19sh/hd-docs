# 第一次進院（0922）· 部署本系統之六：git clone＋Docker 路線詳細版（D-13～D-18）

上層文件：《[第一次進院（0922）· 部署本系統](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-1-system/index.md)》

> - 狀態：**已照做 0922，凍結**，結果見《[第一次進院紀錄（0922，失敗）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/record-1-0922/index.md)》；這條路線 0926 起由《[從零部署本系統之一：容器路線的原冊](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fresh-install-detail/index.md)》取代，本冊是歷史
> - 1117 由舊的第九冊改寫（0923 定版，當時「要印出來帶進去」）
> - 編號：`D-xx`
>
> ⚠️ **0922 的教訓（F-01～F-03）**：本冊所有指令都在**主機的 PowerShell** 下，不要自己先開任何容器，也不要自己下 `-v`、`-p`；容器由 D-19 的 `docker compose up -d` 產生。本冊的指令是 0921 那一版程式的，之後程式與 `.env` 欄位改過（0926 起部署一律 checkout tag、埠只寫在 `.env`；1027 起多了必填的 `HD_EXPORT_DIR`），**不要照抄到現在的院內主機**，現行做法看《[從零部署本系統](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fresh-install/index.md)》。

接在《[之五：git clone＋Docker 路線詳細版（D-05～D-12）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-1-system-docker-2/index.md)》後面。

## 摘要

- 第 4 節建置映像檔：D-13 定主機位址與三個埠（位址與後端埠會寫死進映像檔）、D-14 `docker build`（預留 30 分鐘、標籤不用 `latest`）、D-15 確認映像檔與位址寫對了
- 第 5 節設定與資料：D-16 `.env` 只填幾項、`JWT_SECRET` 在主機上產生、`docker compose config --quiet` 沒有輸出
- D-17 建外部具名資料卷與備份目錄；資料卷已經存在就停
- D-18 啟動前套用既有遷移；絕對不用 `migrate dev`、`db push`
- 0922 現場：3000、9000 被佔、D 槽只剩約 4.6%、E 槽是 RAM 磁碟

## 4. 建置映像檔

### D-13 決定位址與三個連接埠

**做什麼**

| 要定的值                   | 例子                        | 從哪來                                                           |
| -------------------------- | --------------------------- | ---------------------------------------------------------------- |
| 主機位址                   | `hd-server` 或 `192.0.2.10` | 資訊室。**要是護理站電腦與平板連得到的那一個**，不是 `localhost` |
| 後端埠 `HD_API_PORT`       | `3000`                      | 向資訊室登記（DEP-37 第 2 項）                                   |
| 護理端埠 `HD_NURSE_PORT`   | `8080`                      | 同上                                                             |
| 病人端埠 `HD_PATIENT_PORT` | `8081`                      | 同上                                                             |

先確認這三個埠在這台主機上沒人用：

```
Get-NetTCPConnection -State Listen -LocalPort 3000, 8080, 8081 -ErrorAction SilentlyContinue
```

**怎麼知道成功了**

四個值抄在筆記本上；上面那行指令什麼都沒印。

> **主機位址與後端埠會在下一步被寫死進映像檔**，之後改不了，只能重建。這是為什麼它要先定下來，而且要是別台電腦看得到的那一個。

（0922 現場：3000、9000 已被佔用，8080、8081 空著，F-03、F-17；後端埠要另挑。）

### D-14 建置

**做什麼**

```
cd C:\hd\hd-tablet-care
docker build --build-arg VITE_API_BASE_URL=http://<主機位址>:<HD_API_PORT> -t hd-tablet-care:<版本>-<commit 前 7 碼> .
```

例如 `hd-tablet-care:0.1.0-c4109fa`。**標籤不要用 `latest`**：更新之後要回得去上一版，得分得出哪一個是上一版（DEP-19）。

**預留 30 分鐘。** 開發機有快取時約 1～2 分鐘；院內第一次什麼都要下載。

**怎麼知道成功了**

最後幾行出現 `naming to docker.io/library/hd-tablet-care:<標籤> done`，而且**整段輸出裡沒有 `prisma:warn`**。

**可能怎麼壞、怎麼處理**

| 症狀                                                           | 原因                                  | 處置                                                        |
| -------------------------------------------------------------- | ------------------------------------- | ----------------------------------------------------------- |
| `failed to resolve source metadata for docker.io/library/node` | 連不到 Docker Hub                     | D-10 那三個 Docker 網域                                     |
| `apt-get` 那一步卡住或失敗                                     | `deb.debian.org` 的 80 沒開           | D-10                                                        |
| `npm ci` 出現 `ETIMEDOUT`、`ENOTFOUND registry.npmjs.org`      | 連不到 npm                            | D-10                                                        |
| `ENOTFOUND binaries.prisma.sh`                                 | 連不到 Prisma 引擎發布站              | D-10                                                        |
| 輸出裡有 `Prisma failed to detect the libssl/openssl version`  | clone 到的是 0921 之前的 `Dockerfile` | **停下來。** 這樣建出來的映像檔啟動就會倒。回 D-12 確認版本 |
| `npm ci` 說 lock 檔與 `package.json` 不一致                    | clone 到的版本不對，或有人改過檔案    | `git status --short` 應該沒有輸出                           |
| 建到一半磁碟空間不足                                           | 映像檔建完約 1GB，建置過程要更多      | 問資訊室 D-08 第 4 項那顆磁碟還有多少                       |

### D-15 確認映像檔，以及位址寫對了

**做什麼**

```
docker image ls hd-tablet-care
docker run --rm --entrypoint sh hd-tablet-care:<標籤> -c "grep -rlo '<主機位址>:<HD_API_PORT>' apps/nurse-pwa/dist apps/patient-pwa/dist"
```

**怎麼知道成功了**

- 第一行列出剛才那個標籤
- 第二行印出**兩個**檔名，一個在 `nurse-pwa`、一個在 `patient-pwa`

**可能怎麼壞、怎麼處理**

| 症狀             | 處置                                                                                     |
| ---------------- | ---------------------------------------------------------------------------------------- |
| 第二行什麼都沒印 | 位址沒寫進去，或寫成別的。**回 D-14 重建**；這一步不檢查，到 D-21 才會發現護理站登不進去 |
| 只印出一個       | 其中一個 PWA 沒建好，看 D-14 的輸出                                                      |

## 5. 設定與資料

### D-16 建立 `.env`

**做什麼**

```
cd C:\hd\hd-tablet-care
Copy-Item .env.example .env
notepad .env
```

**只填下面這些**，其他保持範本的值：

| 變數                                                                              | 填什麼                                                                  |
| --------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| `HD_IMAGE_TAG`                                                                    | D-14 的標籤，例如 `0.1.0-c4109fa`                                       |
| `HD_BACKUP_DIR`                                                                   | 備份目錄，例如 `D:/hd-backup`（D-17 會建）                              |
| `HD_API_PORT`、`HD_NURSE_PORT`、`HD_PATIENT_PORT`                                 | D-13 的三個埠                                                           |
| `CORS_ORIGINS`                                                                    | `http://<主機位址>:<HD_NURSE_PORT>,http://<主機位址>:<HD_PATIENT_PORT>` |
| `MDM_KIOSK_BASE_URL`                                                              | `http://<主機位址>:<HD_PATIENT_PORT>`                                   |
| `JWT_SECRET`                                                                      | 在主機上產生一組，見下                                                  |
| `SUPER_ADMIN_WORK_ID`、`SUPER_ADMIN_INITIAL_PASSWORD`、`SUPER_ADMIN_DISPLAY_NAME` | 第一個管理者帳號；首次登入會強制改密碼                                  |

`JWT_SECRET` 在主機上產生，**不要從開發機帶進來**：

```
docker run --rm --entrypoint node hd-tablet-care:<標籤> -e "console.log(require('crypto').randomBytes(48).toString('base64url'))"
```

> **compose 只拿 `.env` 做變數代換，不會把整份倒進容器**。所以範本裡的 `DATABASE_URL`、`API_PORT`、`BACKUP_DIR` 這些安裝包用的變數，在這條路線上**填了也沒有作用**，留空即可。容器實際拿到什麼，寫在 `docker-compose.yml` 裡。

**怎麼知道成功了**

```
docker compose config --quiet
```

沒有任何輸出。

**可能怎麼壞、怎麼處理**

| 症狀                                                 | 處置                                                                |
| ---------------------------------------------------- | ------------------------------------------------------------------- |
| `required variable HD_BACKUP_DIR is missing a value` | `HD_BACKUP_DIR` 沒填                                                |
| `請設定 CORS_ORIGINS` 或 `請設定 JWT_SECRET`         | 對應那一行沒填                                                      |
| 路徑用反斜線 `D:\hd-backup`                          | 改成 `D:/hd-backup`。斜線不會被跳脫字元誤傷                         |
| 想把資料庫也指到 `D:\hd-data`                        | **不行，DEP-23。** 這條路線上沒有「資料目錄」這個設定，是刻意拿掉的 |

### D-17 建立資料卷與備份目錄

**做什麼**

```
docker volume create hd-tablet-care-data
New-Item -ItemType Directory -Force D:\hd-backup
docker volume inspect hd-tablet-care-data --format "{{.Name}} {{.Driver}}"
```

**怎麼知道成功了**

最後一行印出 `hd-tablet-care-data local`。

**可能怎麼壞、怎麼處理**

| 症狀                               | 處置                                                                                                                                                                            |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 資料卷已經存在                     | **停。** 裡面可能有資料（前一次部署、或別人建的）。先 `docker run --rm -v hd-tablet-care-data:/data --entrypoint ls hd-tablet-care:<標籤> -la /data` 看裡面有什麼，問清楚再決定 |
| 備份目錄只能放在「文件」或共用目錄 | 當場停手的情形之一（《[進院通則](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-visit-rules/index.md)》）                                                         |

> **資料卷標成 external，是刻意的。** compose 不會替你建它，也**不會**在有人打了 `docker compose down -v` 時把它刪掉。整個透析中心的照護紀錄在裡面，刪不刪不該取決於有沒有人多打了兩個字元。

（0922 現場：D 槽只剩約 4.6%、E 槽是 RAM 磁碟，備份不能照例子放 D 槽，見《第一次進院紀錄》3.2。）

### D-18 套用既有遷移（DEP-31）

**做什麼**

```
docker compose run --rm --no-deps api node apps/api/scripts/prisma-cli.mjs migrate deploy --schema apps/api/prisma/schema.prisma
```

**要在啟動服務之前做**：第一次部署時資料庫是空的。

**怎麼知道成功了**

列出一串遷移目錄，最後一行是 `All migrations have been successfully applied.` 再跑一次同一行，應該是 `No pending migrations to apply.`

**可能怎麼壞、怎麼處理**

| 症狀                                              | 原因                                        | 處置                                         |
| ------------------------------------------------- | ------------------------------------------- | -------------------------------------------- |
| `external volume "hd-tablet-care-data" not found` | D-17 沒做                                   | 做 D-17                                      |
| `Error code 14: Unable to open the database file` | 映像檔是 0921 之前的版本，`/data` 屬於 root | 回 D-12 確認版本，重建                       |
| `ENOTFOUND binaries.prisma.sh`                    | 不該發生：引擎在建置時已經下載進映像檔      | 看 D-14 的輸出是否有 `prisma:warn`；有就重建 |
| 有人建議用 `migrate dev` 或 `db push`             | **絕對不可以**，它們可能直接重建整個資料庫  | —                                            |

上一份：《[之五：git clone＋Docker 路線詳細版（D-05～D-12）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-1-system-docker-2/index.md)》｜下一份：《[之七：git clone＋Docker 路線詳細版（D-19～D-27）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-1-system-docker-4/index.md)》

## 版本歷程

| 定版 | 日期       | 異動                                                                                                                               |
| ---- | ---------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| 1118 | 2026-11-18 | 首次定版。1118 照每份約 300 行的上限由《第一次進院（0922）· 部署本系統之四：git clone＋Docker 路線詳細版》拆出，內容與步驟編號不動 |

[← 回部署手冊目錄](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/index.md)
