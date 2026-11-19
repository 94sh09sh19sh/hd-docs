# 第三次進院（1029）· 接手 v0.3.0、換成 IP、換版之四：詳細版（J-15～J-21）

上層文件：《[第三次進院（1029）· 接手 v0.3.0、換成 IP、換版](visit-3-system.md)》

> - 狀態：**已照做 1029，凍結**。B 級部分成功，實際結果與要改的 13 處（O-13，1116 已改回）見《[第三次進院紀錄（1029，部分成功）](record-3-1029.md)》；改寫來源（1117）：第十八冊、第十七冊第 3、4 節；編號：沿用主文件的 `J-xx`，開發機才做的 `I-xx` 在之七～之九

詳細版共六份（之一～之六），這一份是第 4 節（J-15～J-21）；第 0 節（讀之前：時間怎麼排、名詞、停手條件）在《[…之一：詳細版（第 0 節、J-01～J-03）](visit-3-system-detail.md)》，附錄一～四（步驟對照、退回 `v0.3.0`、登不進去、一張紙）在《[…之六：詳細版（J-30～J-33、附錄）](visit-3-system-detail-6.md)》。

## 摘要

- 這一份是第 4 節：換到新版；19 個資料庫遷移只做加法，`.env` 多一個必填的 `HD_EXPORT_DIR`，外殼不換版、APK 不必重建
- 排在沒有透析的時段做，更新後第一個班次要有人盯著（DEP-32）
- J-15 下載新 tag、先下載基底映像；J-16 補 `.env` 並打四條檢查
- J-17 建置新版，`v0.3.0` 的映像檔不刪（附錄二退回要用）
- J-18 停後端、更新資料庫，抄下更新前備份的檔名與 SHA-256
- J-19 啟動新版、護理站再登入；功能開關一個都不開；壞了照附錄二（之六）退回
- J-20 AI 閘道換新版，印出 `503`「base_url 尚未填寫」是對的；J-21 取出資料只打 `--help`

---

## 4. 換到新版

這一段是換版（W-19，現在在《[本系統換版與退回](ref-upgrade.md)》）的「更新」，套在院內主機上。從 `v0.3.0` 到 `<新 tag>`：**19 個資料庫遷移，全部只做加法**；`.env` **多一個必填的 `HD_EXPORT_DIR`**，另有兩個院方 API 的變數（院內一律空白）；外殼不換版、**APK 不必重建**、平板不必重裝。

> ⚠️ **排在沒有透析的時段做。** 更新後第一個班次要有人盯著（DEP-32）：新版的問題要在累積新資料之前發現，退回的代價才是零。

### J-15 下載新版的程式碼，先把基底映像下載好（＝W-19 第一段、V-06 第二段）

**做什麼**

```powershell
git fetch --tags
git checkout <新 tag>
git describe --tags
docker pull node:20-bookworm-slim
```

**怎麼知道成功了**

| 看什麼 | 應該是 |
|---|---|
| `git checkout` | `Previous HEAD position was …` 與 `HEAD is now at …` 兩行，**正常**（原本就停在 `v0.3.0`，所以不會再印 `detached HEAD` 那一大段；印了也正常） |
| `git describe --tags` | **正好是** `<新 tag>`，後面沒有 `-3-g1a2b3c4` 這種尾巴 |
| `docker pull` | 最後是 `Status: Downloaded newer image for …` 或 `Status: Image is up to date for …` |

> ⚠️ **從這一刻起到 J-16 改完 `.env` 之前，每一條 `docker compose` 指令都會停在「請設定 HD_EXPORT_DIR」。** 這是對的，J-16 補上就好。

| 症狀 | 處置 |
|---|---|
| `git fetch` 說 `Permission denied (publickey)` | 部署金鑰被拿掉了。`ssh -T github-hd-tablet-care` 看一下，印出 `Hi 94sh09sh19sh/hd-tablet-care!…` 才對；不是的話打電話給開發端（repo 管理者）重新登記 |
| `Connection reset by … port 22` | 網路切斷連線，再打一次 |
| `error: pathspec '<新 tag>' did not match` | tag 沒推上去，或打錯字。回 J-01 |
| `git checkout` 說 `Your local changes … would be overwritten` | 有人改過 repo 裡的檔案（J-05 應該已經看到）。**停手**，不要加 `--force` |
| `docker pull` 出現 `no such host` | 同 J-11 那一列：再打一次 → Restart Docker → 找資訊室 |

**🧪 開發機演練**：照做，`<新 tag>` 是之七 I-01 打的。看到「請設定 HD_EXPORT_DIR」要等到 J-16 之後才消失——**確認真的會出現**（隨便打一條 `docker compose --env-file $cfg config --quiet`）。

---

### J-16 補 `.env`（＝《`.env` 怎麼填》的「院內主機上已經有一份」、版本、主機目錄、院方透析清單 API）

`.env` 每一格的填法現在在《[`.env` 怎麼填](ref-env.md)》；這裡是 1029 這一趟從 `v0.3.0` 的 `.env` 補到新版要改的三處。

**做什麼**

```powershell
notepad $cfg
```

改三處：

1. `HD_IMAGE_TAG=v0.3.0` 改成 `HD_IMAGE_TAG=<新 tag>`。
2. 在 `HD_CONFIG_DIR=` 那一行**下面**加一行：

   ```
   HD_EXPORT_DIR=C:\hd\hd-tablet-care\export
   ```

   資料夾不必先建。它是研究資料取出的位置，**與備份資料夾分開**（《[取出資料](ref-data-export.md)》）。
3. 在檔案最後加兩行，**等號後面都留空白**：

   ```
   HOSPITAL_API_BASE_URL=
   HD_SIMULATION_DEPLOYMENT=
   ```

   這兩行不加也能跑（空白就是預設），加了是讓這份 `.env` 與新版範本長得一樣，日後有人看得懂。**院方 API 的位址這一次不寫進來**，第 6 節當場輸入。

存檔，關掉記事本。

**怎麼知道成功了**

```powershell
docker compose --env-file $cfg config --quiet
git describe --tags
Select-String -Path $cfg -Pattern '^(HD_IMAGE_TAG|HD_EXPORT_DIR|HD_SHELL_SIGNING|LLM_PROVIDER|HOSPITAL_API_BASE_URL|HD_SIMULATION_DEPLOYMENT)='
Select-String -Path $cfg -Pattern '^[^#].*(<|>|hd-server|localhost)'
```

| 哪一條 | 應該是 |
|---|---|
| `config --quiet` | 什麼都沒印 |
| `HD_IMAGE_TAG` | 與 `git describe --tags` 一字不差 |
| `HD_EXPORT_DIR` | `C:\hd\hd-tablet-care\export` |
| `HD_SHELL_SIGNING` | `hospital` |
| `LLM_PROVIDER` | `mock` |
| `HOSPITAL_API_BASE_URL`、`HD_SIMULATION_DEPLOYMENT` | 等號後面空白 |
| 最後一條 | 什麼都沒印 |

| 症狀 | 處置 |
|---|---|
| `required variable HD_… is missing a value: 請設定 …` | 冒號後面寫的就是還缺什麼，補上 |
| `HD_SHELL_SIGNING` 不是 `hospital` | **停手**，不要改它 |
| `HD_SIMULATION_DEPLOYMENT` 有值 | 清空。院內主機這一格永遠空白 |
| 有 `HIGH_RISK_WRITTEN_CONFIRMATION` 或 `SHOWCASE_MODE` 這一行 | 刪掉（新版不讀，留著只會讓人看不懂） |

**🧪 開發機演練**：`HD_EXPORT_DIR=C:\hd-sim\export`；其餘照做，兩個院方 API 的變數也先留空白。檢查表的 `HD_SHELL_SIGNING` 這裡是 `dev`（院內是 `hospital`）。

---

### J-17 建置新版的映像檔（＝W-19、V-14）

**做什麼**（記下開始時間）

```powershell
docker compose --env-file $cfg build
```

主機上有之前建置的快取時**一分鐘內**就好（1029 實測不到一分鐘）；沒有快取約十分鐘，畫面一直捲動是正常的。

**怎麼知道成功了**：最後出現 `Image hd-tablet-care:<新 tag> Built`。再打：

```powershell
docker images hd-tablet-care
```

看得到 `v0.3.0` 與 `<新 tag>` **兩個**。記下結束時間。

> ⚠️ **`v0.3.0` 的映像檔不要刪。** 新版穩定之前，那是唯一退得回去的東西（附錄二）。

| 症狀 | 處置 |
|---|---|
| `no such host` | 同 J-11 那一列 |
| `ETIMEDOUT`、`ECONNRESET` | 再打一次 |
| `pull access denied for hd-tablet-care` | 打成 `up` 了，先 `build` |

到這裡為止，**服務還是 `v0.3.0` 在跑**，護理站照樣用得了。

**🧪 開發機演練**：照做。記下**耗時**；`docker images hd-tablet-care` 看得到兩個 tag。

---

### J-18 停後端、更新資料庫（＝W-19）

> ⚠️ **先確認現在沒有透析、已經跟護理站講過。** 1029 在治療中停了後端、沒先講（《[第三次進院紀錄（1029，部分成功）](record-3-1029.md)》O-08）；系統開始使用之後，這一步停的是護理站正在看的畫面。

**做什麼**（三行，第三行是一整行，不要斷開）

```powershell
$tag = git describe --tags
docker compose --env-file $cfg stop api
docker compose --env-file $cfg run --rm --no-deps api node apps/api/scripts/db-update.mjs --note "v0.3.0 → $($tag)（第三次進院）"
```

第一行把 J-15 確認過的版本存進 `$tag`，第三行的說明就自動帶上，**不必手改**。1029 照抄成字面的 `<新 tag>`（O-13 第 1 列）。打 `$tag` 看一下，應該正好是 `<新 tag>`。

這一條一次做完五件事，每一件印一段 `[1]`～`[5]`：確認後端已停、開更新紀錄、**更新前備份**、**驗證備份還原得起來**、套用遷移。任何一關沒過就停，資料庫不會被動到。

**怎麼知道成功了**：最後印出「**更新完成。接下來的三件事是人要做的**」。往上找第 3 段，**把更新前備份的檔名（`hd-before-update-<時間>.db`）與 SHA-256 抄下來**——附錄二退回時要用。

| 症狀 | 處置 |
|---|---|
| `更新中止：後端服務還在執行` | 第一行沒成功，再打一次 `stop api`。**不要加 `--allow-running`**，那是演練用的 |
| `更新中止：備份目的地可用空間 …不足` | 主機共用，問資訊室是誰佔掉空間；不要自己刪別人的東西 |
| 其他任何「中止」 | 資料庫沒被動到。整段抄下來，`docker compose --env-file $cfg up -d` 讓舊版的後端回來（`.env` 先把 `HD_IMAGE_TAG` 改回 `v0.3.0`、`git checkout v0.3.0`），打電話給開發端 |

> 護理站在這一步的期間會看到斷線紅框，`up -d` 之後就會消失。先跟護理站講一聲。

**🧪 開發機演練**：照做。第 [5] 段寫套用了 **19 個**遷移（從 `iteration15_hospital_api` 到 `iteration31_connect_dots_norm`）；**更新前備份的檔名與 SHA-256 抄下來，之九 I-15 要用**。

---

### J-19 啟動新版，確認還是登得進去（＝W-19、V-17）

**做什麼**

```powershell
docker compose --env-file $cfg up -d
docker ps --format "{{.Names}}  {{.Image}}  {{.Status}}"
curl.exe -s http://localhost:13000/api/health
docker compose --env-file $cfg exec nurse-web grep -rhoE 'https?://[A-Za-z0-9.-]+:[0-9]+' apps/nurse-pwa/dist/assets
curl.exe -s -i -H "Origin: http://<IP>:18080" http://<IP>:13000/api/health | Select-String Access-Control-Allow-Origin
docker compose --env-file $cfg logs api --tail 40
```

**怎麼知道成功了**

| 看什麼 | 應該是 |
|---|---|
| `docker ps` | `api`、`nurse-web`、`patient-web` 三列的映像檔是 `hd-tablet-care:<新 tag>`，狀態 `Up` |
| health | `{"status":"ok",…}` |
| 網頁裡的後端位址 | `http://<IP>:13000` |
| 放行檢查 | `Access-Control-Allow-Origin: http://<IP>:18080` |
| 日誌 | 有「已連線至 SQLite」（帶 `synchronous=FULL`）、「伺服器時區」是 `Asia/Taipei`、版本標記後面寫「（正式環境設定）」；沒有紅色的 `ERROR` |

然後**在護理站的電腦**：

1. 按 Ctrl＋F5 強制重新整理（舊版的網頁還留在瀏覽器裡）。
2. 用護理長的新密碼再登入一次。
3. 護理端 → **系統管理** → 「**版本更新紀錄**」：多了一筆。這張表**沒有說明欄**，版本欄寫的是 `apps/api/package.json` 的號碼，不是 git tag：主機第一次更新顯示 `— → 0.1.0`，之後是 `0.1.0 → 0.1.0`，都正常（1029 實測，紀錄 O-12）。`--note` 的說明在**稽核軌跡**：用途選「系統維運」、動作選「版本更新完成」，那一筆寫著 `v0.3.0 → <新 tag>（第三次進院）`。要對版本，看第一條 `docker ps` 的映像檔名稱。

新版第一次啟動時會**自己**補進一些東西：隨版本帶入的衛教草稿（待核准，病人端看不到）、四條判斷規則的草稿、記憶相簿的預設圖卡、指標定義的變更紀錄。**都不必處理**。

> ⚠️ **新版多了很多功能開關**（遊戲化、獎勵制度、跑馬燈等），**照預設關著，一個都不要開**。要開得先讓長者、社工、護理部看過（1014、1018 的決定）。

| 症狀 | 處置 |
|---|---|
| `api` 一直 `Restarting` | `docker compose --env-file $cfg logs api --tail 30` 抄最後幾行。看不懂就照附錄二退回 `v0.3.0` |
| 護理站 `Failed to fetch` | Ctrl＋F5；仍不行照附錄三 |
| 登入後畫面壞掉、某個頁面打不開 | 抄下畫面上的字與網址。主線（登入、簡易版、系統管理）能用就繼續，不能用就照附錄二退回 |

**🧪 開發機演練**：照做；「護理站」是手機，沒有 Ctrl＋F5：關掉分頁重開，或在瀏覽器的網站設定清除這個網站的資料。要確認：三個服務的映像檔是新 tag；手機重新整理後用改過的密碼登得進去（**資料留住了**：帳號與密碼是更新前的）；版本更新紀錄有一筆。

---

### J-20 AI 閘道換成新版（＝V-29、V-30）

首波 AI 是關的。這一步只讓閘道就位、確認它清楚回報「設定還沒填」，**不接任何模型**。

**做什麼**

1. 設定檔：J-07 第 5 條是 `False`（沒有設定檔）才打這兩行；是 `True` 就跳過，**不要蓋掉它**：

   ```powershell
   New-Item -ItemType Directory -Force $root\config\ai-gateway | Out-Null
   Copy-Item services\ai-gateway\config.hospital.example.yaml $root\config\ai-gateway\config.yaml
   ```

   範本的 `base_url` 與 `model` 刻意留空，**保持空白**。**絕對不要填實驗室的位址**——那是把資料往院外送。
2. 建置並啟動：

   ```powershell
   docker compose --env-file $cfg --profile ai build ai-gateway
   docker compose --env-file $cfg --profile ai up -d ai-gateway
   docker compose --env-file $cfg exec -T api node -e "fetch('http://ai-gateway:8000/health').then(async r=>console.log(r.status, await r.text()))"
   ```

**怎麼知道成功了**：建置最後印出 `全部通過`；最後一條印出

```
503 {"status":"error","config":"error","detail":"base_url 尚未填寫（推論端點的位址）"}
```

**503 在這裡是對的**：閘道在、後端連得到它、它清楚說出還缺什麼。

| 症狀 | 處置 |
|---|---|
| `fetch failed` | 閘道沒起來，`docker compose --env-file $cfg --profile ai logs ai-gateway` |
| `找不到設定檔` | 第 1 步的路徑不對，必須是 `config\ai-gateway\config.yaml` |
| 建置時 `no such host` | 同 J-11 那一列 |

> ⚠️ 從現在起，**日後更新時 `build` 與 `up -d` 都要加 `--profile ai`**，閘道才會跟著換新版。閘道的其他做法見《[AI 閘道](ref-ai-gateway.md)》。

**🧪 開發機演練**：照做（之八 I-11 做過，J-07 第 5 條是 `True`，所以跳過複製設定檔）。要確認：503 那一行；`docker ps` 裡 `ai-gateway` 的映像檔是新 tag。

---

### J-21 確認資料取出的指令在（只印說明，不取任何資料）

研究與後續計畫的資料取出是新版才有的（《[取出資料](ref-data-export.md)》），**沒有院方核准不得執行**。這一步只確認它在，交接時說得出來。

**做什麼**

```powershell
docker compose --env-file $cfg --profile export run --rm data-export --help
```

**怎麼知道成功了**：印出一大段說明，第一行是「研究與後續計畫的資料取出（部署手冊第十六冊「取出資料」）」。**只打 `--help`，不要加任何別的參數。**

| 症狀 | 處置 |
|---|---|
| `請設定 HD_EXPORT_DIR` | J-16 的第 2 處沒加，回去補 |
| 說匯出目錄與備份目錄重疊 | `HD_EXPORT_DIR` 寫成了 `backups` 底下，改成 `C:\hd\hd-tablet-care\export` |

**🧪 開發機演練**：照做。說明的第一行對得上上面寫的。

---

上一份：《[…之三：詳細版（J-09～J-14）](visit-3-system-detail-3.md)》；下一份：《[…之五：詳細版（J-22～J-29）](visit-3-system-detail-5.md)》；主文件：《[第三次進院（1029）· 接手 v0.3.0、換成 IP、換版](visit-3-system.md)》

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|
| [1118](https://94sh09sh19sh.github.io/hd-docs/1118/deployment/visit-3-system-detail-4/) | 2026-11-18 | 首次定版。1118 照每份約 300 行的上限由《第三次進院（1029）· 接手 v0.3.0、換成 IP、換版之一：詳細版》拆出，內容與步驟編號不動 |

[← 回部署手冊目錄](index.md)
