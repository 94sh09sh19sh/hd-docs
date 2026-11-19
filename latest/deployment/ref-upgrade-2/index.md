# 本系統換版與退回（第 2 份，第 3～4 節，W-20）

上層文件：《[本系統換版與退回](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-upgrade/index.md)》

> - 狀態：**現行**（常備參考）；1117 由舊的第十一冊第 6 節（W-20 回退）改寫，併入各冊的退回附錄（來源全文見第 1 份）；編號沿用 `W-20`
> - 第 0～2 節（現在的版本、換版之前、W-19 換版）與開工三行在第 1 份

## 摘要

- **程式可以退版，資料庫不能把遷移倒回去**：退回＝舊 tag＋舊映像檔＋更新前那份備份，換版之後寫進去的資料（含讀檔同步進來的、改過的密碼與帳號、註冊的平板）一起消失，所以越早決定越好
- 要用的備份是 W-19 ④ 第 3 段抄的檔名與 SHA-256；沒抄到看稽核軌跡，或備份資料夾最新一份旁邊的 `.sha256`
- 退回三步：`git checkout <舊 tag>`＋改 `HD_IMAGE_TAG` → 停 `api`、新版資料庫移到 `/data/before-rollback/`、還原、`up -d` → 閘道有換才一起退
- 舊映像檔的護理端網頁寫死建置當時的 `HD_PUBLIC_API_URL`，退回後登不進去先看「登入要注意」
- 🧪 每個要帶進院的 tag 先在開發機整輪走過，含真的退一次（第 4 節）；一律用 PowerShell，不用 Git Bash

## 3. 退回

### W-20 退回

**什麼時候用**：W-19 ④ 之後，新版的 `api` 起不來、或主線功能壞掉，而現場解不開。**越早決定越好**：程式可以退版，**資料庫不能把遷移倒回去**（規範 18.3、FR-S12），所以這一版動過 schema 時，退回＝「舊程式＋更新前那份備份」，更新之後寫進去的資料一起消失——含啟用讀檔後同步進來的、改過的密碼與建的帳號、註冊的平板。1029 時沒有真實資料，代價是零；首波開始使用之後，代價是那段期間的所有紀錄（DEP-32）。

**要用的那份備份**：W-19 ④ 第 3 段抄的 `hd-before-update-<時間>.db` 與 SHA-256。沒抄到的話：

- 護理端還進得去：系統管理 → 稽核軌跡，「更新前強制備份：\<檔名>（… bytes，SHA-256 …）」那一筆；或「版本更新紀錄」
- 進不去：備份資料夾裡最新的一份，雜湊在旁邊同名的 `.sha256`（前半段那 64 個字）：

```
Get-ChildItem $root\backups\hd-before-update-* | Sort-Object LastWriteTime | Select-Object -Last 2 Name
Get-Content "$root\backups\<備份檔名>.sha256"
```

**做什麼**

1. 程式碼與設定退回：

```
git checkout <舊 tag>
notepad $cfg
```

`HD_IMAGE_TAG` 改回 `<舊 tag>`（舊映像檔還在，不必重建）。舊版不認得的設定照下表處理：

| 退到                     | `.env` 要改的                                                                                                                           |
| ------------------------ | --------------------------------------------------------------------------------------------------------------------------------------- |
| `v0.3.0`（1029 的例子）  | 不必改：`HD_EXPORT_DIR` 與兩個院方 API 的變數留著沒關係（舊版不讀）                                                                     |
| `v0.4.0`（1116 的例子）  | `HD_DIALYSIS_LIST_DIR` 清空、`COMPOSE_FILE` 那一行改回註解（開頭加 `#`）：`v0.4.0` 不認讀檔，也沒有 `docker-compose.dialysis-files.yml` |
| `v0.5.0`（下一次的例子） | 讀檔設定留著（`v0.5.0` 認得）；`<新 tag>` 新增的行照第 1.3 節看舊版讀不讀                                                               |

1. 停後端、把新版的資料庫移到旁邊、還原更新前備份、啟動（第二、三條各是一整行）：

```
docker compose --env-file $cfg stop api
docker compose --env-file $cfg run --rm --no-deps --entrypoint sh api -c "mkdir -p /data/before-rollback && mv /data/hd.db /data/hd.db-wal /data/hd.db-shm /data/before-rollback/ 2>/dev/null; ls -l /data/before-rollback"
docker compose --env-file $cfg run --rm --no-deps api node_modules/.bin/ts-node --project apps/api/tsconfig.json apps/api/scripts/restore-backup.ts --from /backups/<備份檔名> --to /data/hd.db --sha256 <雜湊>
docker compose --env-file $cfg up -d
```

`hd.db` 與 `-wal`、`-shm` 是一組，三個一起移（DEP-09）；`ls -l` 印得出移過去的檔才往下。

1. W-19 ③ 有把閘道一起換新版的話，閘道也退回：`docker compose --env-file $cfg --profile ai up -d ai-gateway`

**成功**

| 看什麼      | 應該是                                                                                                                              |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| 還原輸出    | `[2]` 之後有 `✓ 與備份歷程上的紀錄相符`、`[4] 完整性檢查：ok`、`[5] 下一步：還原的就是 DATABASE_URL 指向的正本，直接啟動服務即可。` |
| `docker ps` | `api`、`nurse-web`、`patient-web` 的映像檔是 `hd-tablet-care:<舊 tag>`                                                              |
| 護理端      | 版本標記是舊版；護理站 Ctrl＋F5 後登得進去                                                                                          |
| 抓取腳本    | 不受影響、照跑（它是主機上的排程，不在 compose 裡）                                                                                 |

**登入要注意**：舊映像檔裡的護理端網頁，寫死的是**建置舊映像檔當時**的 `HD_PUBLIC_API_URL`。舊映像檔建好之後才換過主機位址的話，退回後一定 `Failed to fetch`。1029 先用 `<IP>` 重建了 `v0.3.0` 的網頁才換版，所以退回 `v0.3.0` 也登得進去；1029 之後的 `v0.4.0`、`v0.5.0` 都是用 `<IP>` 建的。

**之後**

- 移到 `/data/before-rollback/` 的那份**先留著**，連同新版出問題的原文帶回給開發端判斷；確定不需要再刪：`docker compose --env-file $cfg run --rm --no-deps --entrypoint rm api -r /data/before-rollback`
- `/data/before-rollback/` 裡已經有上一次退回留下的檔時，第二條的 `mv` 會蓋過去；要留的話先帶回再退
- 新版的映像檔也不要刪
- 護理站照 W-19 ⑤ 的清單再看一次功能開關（舊備份裡的開關狀態是換版前的）

| 症狀                                                                  | 處置                                                                                                                                           |
| --------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| `還原中止：目的檔 hd.db 已存在；還原不覆蓋任何既有檔案，請換一個路徑` | 第二條沒把 `hd.db` 移走：多半是 `stop api` 沒成功、或打錯。看第二條 `ls -l` 的輸出，重打第一、二條                                             |
| `還原中止：找不到備份檔 …`                                            | 檔名打錯（要含 `.db` 的整個檔名），或用了 Git Bash                                                                                             |
| `還原中止：SHA-256 與備份歷程上的紀錄不符，備份檔可能已損毀或被更動`  | 雜湊抄錯；用 `Get-Content` 那一條重新複製。還是不符就打電話給開發端，不要換別份硬還原                                                          |
| `還原中止：完整性檢查未通過：…`                                       | 那份備份壞了。**停手**，`/data/before-rollback/` 不要動，打電話給開發端                                                                        |
| 退回後 `Failed to fetch`                                              | 看上面「登入要注意」；再照《[護理站登不進去與主機位址](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-login/index.md)》第 2 節查 |

## 4. 🧪 開發機演練

每一個要交給院方的 tag，先在開發機上照這一份走一次（DEP-22）：

| #   | 驗什麼                                                                                                                                                                                                           | 這一份的步驟 |
| --- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ |
| 1   | 開發機準備成跟院內主機一樣（上一次離院時的版本、位址用 IP、登得進去、平板佈建好）；這一段由開發端做，手冊不寫                                                                                                    | —            |
| 2   | 換版一次：`<新 tag>` 照 W-19 走完，`更新完成`、更新前備份的檔名與雜湊抄到了                                                                                                                                      | W-19         |
| 3   | 新版登得進去，帳號密碼是更新前的（資料留住了）                                                                                                                                                                   | W-19 ⑤       |
| 4   | 真的退回一次：`<備份檔名>`、`<雜湊>` 用第 2 項抄的；`完整性檢查：ok`、三個服務是舊 tag、手機重開分頁後登得進去。換版之後註冊或建的東西不見了，是對的                                                             | W-20         |
| 5   | 退回後登不進去、`Failed to fetch`：這一份的 W-20 寫錯了，抄下《[護理站登不進去與主機位址](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-login/index.md)》第 2 節第 3 步的結果，回去改這一份再演練 | W-20         |

- 🧪 根目錄 `C:\hd-sim`、管理者 `sim-admin`、`HD_SHELL_SIGNING=dev`；`HD_SIMULATION_DEPLOYMENT` 照開發端填的
- 舊冊的實例：1029 前的演練（《[第三次進院（1029）之七～之九：開發機才做的演練](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-3-system-rehearsal/index.md)》）、1116 前的演練（《[第五次進院（1116）任務二 · 本系統換版上線](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-5-system-2/index.md)》SY-M3）
- **在 Git Bash 裡照抄會壞的一件事**：Git Bash 會把 `/backups/…`、`/data/…` 這種參數自動轉成 Windows 路徑，還原腳本就會回報找不到備份檔。一律用 PowerShell；非用 Git Bash 不可時，先 `export MSYS_NO_PATHCONV=1`，`--env-file` 也要寫成 `C:/…` 的形式

______________________________________________________________________

上一份：《[本系統換版與退回](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-upgrade/index.md)》｜[部署手冊目錄](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/index.md)

## 版本歷程

| 定版 | 日期       | 異動                                                                               |
| ---- | ---------- | ---------------------------------------------------------------------------------- |
| 1118 | 2026-11-18 | 首次定版。1118 照每份約 300 行的上限由《本系統換版與退回》拆出，內容與步驟編號不動 |

[← 回部署手冊目錄](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/index.md)
