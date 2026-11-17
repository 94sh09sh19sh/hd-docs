# 第三次進院（1029）· 接手 v0.3.0、換成 IP、換版之三：詳細版（J-09～J-14）

上層文件：《[第三次進院（1029）· 接手 v0.3.0、換成 IP、換版](visit-3-system.md)》

> - 狀態：**已照做 1029，凍結**。B 級部分成功，實際結果與要改的 13 處（O-13，1116 已改回）見《[第三次進院紀錄（1029，部分成功）](record-3-1029.md)》；改寫來源（1117）：第十八冊、第十七冊第 3、4 節；編號：沿用主文件的 `J-xx`，開發機才做的 `I-xx` 在之七～之九

詳細版共六份（之一～之六），這一份是第 3 節（J-09～J-14）；第 0 節（讀之前：時間怎麼排、名詞、停手條件）在《[…之一：詳細版（第 0 節、J-01～J-03）](visit-3-system-detail.md)》，附錄一～四（步驟對照、退回 `v0.3.0`、登不進去、一張紙）在《[…之六：詳細版（J-30～J-33、附錄）](visit-3-system-detail-6.md)》。

## 摘要

- 這一份是第 3 節：換成 IP、讓護理站登得進去，仍在 `v0.3.0`
- 先在舊版修登入、不一起換新版：兩件事分開，新版出問題退回的是已經登得進去的 `v0.3.0`（附錄二在之六）
- 主機位址牽動五處：`.env` 三個位址、網頁裡的後端位址、放行名單與 QR code、伺服器憑證與下載頁、金鑰備份與病人端憑證
- J-09 留一份 `.env.before-ip`；J-10 三個位址改成 `<IP>`，`CORS_ORIGINS` 只留 `http://<IP>:18080`
- J-11 重建網頁、`up -d`，在主機上確認放行
- J-12 重簽伺服器憑證：`shell-builder` 新產生的只能有伺服器憑證，看到院內 CA 或 APK 簽章金鑰就停手
- J-13 在主機上登入、改密碼；J-14 護理站的電腦登入，過了就至少 B 級
- `Failed to fetch` 試了仍不行照附錄三（之六）；一小時仍不通就停手、做 J-32

---

## 3. 換成 IP，讓護理站登得進去（仍在 `v0.3.0`）

為什麼先在舊版修登入、不一起換新版：**兩件事分開做，出錯時才分得出是哪一件**；而且新版萬一出問題，退回來的是一個已經登得進去的 `v0.3.0`（附錄二）。

改主機位址會牽動這幾處，下面五步一處都不能漏：

| 主機位址寫在哪 | 怎麼換 | 在哪一步 |
|---|---|---|
| `.env` 的三個位址 | 記事本改 | J-10 |
| 護理端網頁裡的後端位址 | `build` 時寫死進去，要重建 | J-11 |
| 後端的放行名單、平板 QR code 裡的位址 | 容器建立時讀一次，要 `up -d` | J-11 |
| 伺服器憑證、下載頁 | 重跑 `shell-builder` 會自己重簽 | J-12 |
| 金鑰備份、病人端用的憑證 | `keys-backup`、`restart patient-web` | J-12 |

### J-09 留一份改之前的 `.env`（＝T-05）

**做什麼**

```powershell
Copy-Item $cfg "$root\config\.env.before-ip"
Get-ChildItem "$root\config"
```

**怎麼知道成功了**：看得到 `.env` 與 `.env.before-ip` 兩個檔。

> ⚠️ 這一份和 `.env` 一樣有密碼與金鑰，**只留在這個資料夾**，J-14 成功後就刪掉（J-14 最後一步）。

**🧪 開發機演練**：照做。

---

### J-10 把三個位址改成 `<IP>`（＝T-06）

**做什麼**

```powershell
notepad $cfg
```

只改這三行的**主機部分**，`http://`、`https://` 與埠都不動：

```
HD_PUBLIC_API_URL=http://<IP>:13000
CORS_ORIGINS=http://<IP>:18080
MDM_KIOSK_BASE_URL=https://<IP>:18081
```

`CORS_ORIGINS` 如果用逗號多列了別的來源（例如 `localhost`），**這次一起拿掉**，只留 `http://<IP>:18080`。存檔，關掉記事本。

**怎麼知道成功了**

```powershell
docker compose --env-file $cfg config --quiet
Select-String -Path $cfg -Pattern '^(HD_PUBLIC_API_URL|CORS_ORIGINS|MDM_KIOSK_BASE_URL)='
Select-String -Path $cfg -Pattern '^[^#].*(<|>|hd-server|localhost)'
```

| 哪一條 | 應該是 |
|---|---|
| 第一條 | 什麼都沒印 |
| 第二條 | 三行，主機部分**都是 `<IP>`、一字不差**；前兩行 `http://`、第三行 `https://` |
| 第三條 | 什麼都沒印（沒有照抄範例、沒有 `localhost`、沒有忘了換掉的 `<`、`>`） |

再打一條，`<名稱>` 換成舊的那個名稱，**什麼都沒印**才對（舊名稱一處都不剩）。舊名稱是 J-07 第 1 條抄到的 `HD_PUBLIC_API_URL` 中間那一段（第 4 條 `DNS:` 後面應該是同一個）；照紙本抄，**不要重查 `hostname`**，1001 填的可能是完整網域名稱：

```powershell
Select-String -Path $cfg -Pattern '^[^#].*<名稱>'
```

| 症狀 | 處置 |
|---|---|
| 第二條有一行還是舊名稱 | 回記事本改成一字不差 |
| 記事本存檔時問編碼 | 選 UTF-8，不要改檔名 |

**🧪 開發機演練**：照做。第三條檢查原本會抓到 `hd-server`，改完要什麼都不印。

---

### J-11 重建網頁、啟動，並在主機上確認放行（＝T-07、V-17 第一、二段）

`HD_PUBLIC_API_URL` 寫死在網頁檔案裡，**只 `up -d` 沒有用，一定要先 `build`**。

**做什麼**（記下開始時間）

```powershell
docker compose --env-file $cfg build
docker compose --env-file $cfg up -d
docker compose --env-file $cfg ps
```

**怎麼知道成功了**：`build` 最後出現 `Image hd-tablet-care:v0.3.0 Built`；`ps` 的 `api`、`nurse-web`、`patient-web` 都是 `Up`。記下結束時間。主機有 1001 留下的建置快取，**一分鐘內就跑完是正常的**（1029 實測 19.8 秒），看到 `Built` 就算有建。

接著在主機上打這四條確認：

```powershell
curl.exe -s http://localhost:13000/api/health
docker compose --env-file $cfg exec nurse-web grep -rhoE 'https?://[A-Za-z0-9.-]+:[0-9]+' apps/nurse-pwa/dist/assets
curl.exe -s -i -H "Origin: http://<IP>:18080" http://<IP>:13000/api/health | Select-String Access-Control-Allow-Origin
[Console]::OutputEncoding = [Text.Encoding]::UTF8; docker compose --env-file $cfg logs api | Select-String '允許的前端來源' | Select-Object -Last 1
```

| 哪一條 | 應該是 |
|---|---|
| health | `{"status":"ok",…}` |
| 網頁裡的後端位址 | `http://<IP>:13000`，**沒有舊名稱** |
| 放行檢查 | 印出 `Access-Control-Allow-Origin: http://<IP>:18080` |
| 日誌最後一行 | `允許的前端來源：http://<IP>:18080` |

> 💡 放行檢查那一行在視窗太窄時可能只看得到後半段（例如 `…rol-Allow-Origin: http://…`），看得到 `Allow-Origin` 就算有印。**真的什麼都沒印才是沒放行**——1001 就是空的。

**可能怎麼壞**

| 症狀 | 處置 |
|---|---|
| `failed to resolve source metadata for docker.io/library/node`，後面有 `no such host` | Docker 查不到 Docker Hub 的網域。依序：① 同一條再打一次；② 工作列的 Docker 圖示按右鍵 → Restart，等變綠再打；③ 仍不行，請資訊室看院內 DNS。**用了哪一個辦法才過，寫進紀錄** |
| `npm error code ETIMEDOUT` 或 `ECONNRESET` | 網路不穩，再打一次；已下載的部分會沿用 |
| 網頁裡的後端位址還是舊名稱 | `build` 沒讀到新的 `.env`：多半是少了 `--env-file $cfg` 或忘了開工三行。補上再 `build`、`up -d` |
| 放行檢查什麼都沒印 | `CORS_ORIGINS` 不是 `http://<IP>:18080`，或改完沒 `up -d`。看日誌最後一行就知道後端手上是哪一份。先確認 `<IP>` 換成了真的位址，照抄 `<IP>` 一定什麼都不印 |
| 日誌那一條什麼都沒印 | 那一行開頭的 `[Console]::OutputEncoding = [Text.Encoding]::UTF8;` 漏打了：PowerShell 預設用 big5 讀 Docker 的輸出，中文變亂碼，`允許的前端來源` 就比對不到（1029 模擬部署實測）。補上整行再打 |
| `api` 一直是 `Restarting` | `docker compose --env-file $cfg logs api --tail 30`，最後幾行寫是哪一條設定被拒，照著改 `.env` 再 `up -d` |

**🧪 開發機演練**：照做。記下**建置耗時**；放行檢查印出 `Access-Control-Allow-Origin: http://<IP>:18080`（1029 第一輪就在這裡把角括號一起打進去過）。

---

### J-12 重簽伺服器憑證、備份金鑰、病人端換上新憑證（＝T-08、T-09、T-10）

**做什麼**（記下開始時間）

```powershell
docker compose --env-file $cfg --profile shell run --rm shell-builder
```

它會重建一次 APK（不必下載）。看「**這一次新產生：**」那一行：

| 後面出現 | 怎麼辦 |
|---|---|
| **只有**「伺服器憑證（`<IP>`）」 | **對的**，往下 |
| 「伺服器憑證（`<名稱>`）」 | `.env` 的 `MDM_KIOSK_BASE_URL` 沒改到，回 J-10 |
| 有「院內 CA」或「APK 簽章金鑰」 | **停手。** 不要往下做（0.7 節），打電話問開發端 |
| `這個金鑰資料卷是「dev」用的，設定卻是「hospital」` | **停手** |

**再打一次同一條指令**，這次要看到「**金鑰全部沿用，這一次沒有產生任何新的金鑰**」。

然後備份金鑰、讓病人端換上新憑證：

```powershell
docker compose --env-file $cfg --profile shell run --rm shell-builder keys-backup
docker compose --env-file $cfg --profile shell run --rm shell-builder keys-verify
docker compose --env-file $cfg restart patient-web
docker compose --env-file $cfg logs patient-web --tail 5
docker compose --env-file $cfg --profile shell run --rm shell-builder keys-info
```

**怎麼知道成功了**

| 看什麼 | 應該是 |
|---|---|
| `keys-backup` | 「已備份：備份目錄/keys/hd-keys-<時間>.tar.gz」，**檔名抄下來** |
| `keys-verify` | 每一項都 ✓，最後「還原得回來」 |
| `patient-web` 日誌**最後一次**出現的「靜態資源已提供於連接埠 8081」 | 後面是「（HTTPS；HTTP 只留外殼下載頁）」 |
| `keys-info` 的「伺服器憑證」 | `IP Address:<IP>` |
| `keys-info` 的院內 CA 與簽章金鑰指紋 | 與 J-07 第 4 條抄的**一模一樣** |

記下結束時間（1001 沒有計時，這一步的耗時下一次要用）。

> ⚠️ 金鑰備份裡有私鑰：**不得出院、不得寄給開發端**。1001 那份 `hd-keys-20261001-173347.tar.gz` **不要刪**。

| 症狀 | 處置 |
|---|---|
| `restart patient-web` 停在 `Restarting`、沒有 `Started` 就回到提示字元 | 畫面沒畫完，不是錯。看下一條日誌**最後一次**是不是 HTTPS；`docker compose --env-file $cfg ps patient-web` 是 `Up` 就好 |
| 日誌裡「找不到伺服器憑證」和「HTTPS」同時出現 | `--tail 5` 跨到了重新啟動之前那一次。以**最後一次**啟動的那幾行為準 |
| **最後一次**啟動是「找不到伺服器憑證…暫以 HTTP 提供」 | `shell-builder` 沒成功，或沒 `restart patient-web` |
| 日誌寫 `8081`、`http://api:3000`，不是 `18081`、`13000` | **正常**，那是容器裡面的埠 |
| 院內 CA 或簽章金鑰指紋與 J-07 不一樣 | **停手**，有新的金鑰產生了 |

**🧪 開發機演練**：照做。「這一次新產生」**只有**伺服器憑證（`<IP>`）；`keys-info` 的 CA 與簽章金鑰指紋與 J-07 一樣；記下**耗時**。

---

### J-13 在主機上登入、改密碼（＝T-11、V-17 第三段）

**做什麼**：主機的瀏覽器開 **`http://<IP>:18080`**——**不要用 `localhost`，也不要用舊名稱**。帳號密碼用 `.env` 裡的 `SUPER_ADMIN_WORK_ID` 與 `SUPER_ADMIN_INITIAL_PASSWORD`：

```powershell
Select-String -Path $cfg -Pattern '^SUPER_ADMIN_(WORK_ID|INITIAL_PASSWORD)='
```

**怎麼知道成功了**：被要求改密碼。新密碼由**護理長**決定、自己保管，你不要記在任何地方。

| 症狀 | 處置 |
|---|---|
| `Failed to fetch` | 網址列是不是 `http://<IP>:18080`（一字不差）？是的話按 Ctrl＋F5 再試；仍不行照**附錄三** |
| `工作ID 或密碼錯誤` | 有連到後端了（名單已修好）。帳號只在**第一次啟動**時照 `.env` 建立，1001 之後若有人改過 `.env` 的這兩行，不會改到已建立的帳號。把 J-07 時 `.env` 的這兩行與現在的比一下；都不對就**停手**，回去由開發端出重設的辦法，不在現場改資料庫 |
| 頁面開得到，但一直轉圈 | 按 F12 → Network，再按一次登入，抄下請求送去的網址與錯誤原文 |

**🧪 開發機演練**：開發機瀏覽器開 `http://<IP>:18080`，用 `sim-admin` / `Sim-Init-2026`；被要求改密碼，改成什麼都可以（記在紀錄紙上，撤除後就沒用了）。

之後多做一件：開發機瀏覽器**故意用 `http://localhost:18080` 開一次、按登入**；再用 `http://<名稱>:18080` 開一次、按登入。兩次都是 `Failed to fetch`：這就是院內用錯網址時會看到的畫面，看過一次到院內就認得。

---

### J-14 在護理站的電腦登入（＝T-12、V-17 第四段）

**這一步過了，這一次進院就至少是 B 級。**

**做什麼**：**護理站的電腦**開 `http://<IP>:18080`，用護理長剛改好的密碼登入（請護理長自己輸入）。

> 護理站的電腦**要 Windows 密碼才進得去，螢幕也會休眠**，休眠後要重新輸入（1029 實測）。開發端不知道這個密碼：先找好會在場、能幫忙輸入的護理師，並問清楚休眠多久，冒煙測試（J-30）也要用這一台。

**怎麼知道成功了**：登入成功，看得到護理端的畫面。**記下時間**，演練紀錄寫「護理站登入成功，＿點＿分」。

做完之後：

1. 護理站瀏覽器裡用舊名稱的書籤、桌面捷徑，**全部改成 `http://<IP>:18080`**，並告訴護理站的人：舊網址開得到頁面，但登不進去。
2. 刪掉改之前的那一份 `.env`：

   ```powershell
   Remove-Item "$root\config\.env.before-ip"
   Get-ChildItem "$root\config"
   ```

3. 照 0.3 節的取捨表決定要不要做第 4 節。

| 症狀 | 處置 |
|---|---|
| 主機上登得進去，護理站開不到頁面 | J-08 應該已經擋下來；找資訊室 |
| 護理站 `Failed to fetch` | Ctrl＋F5 強制重新整理（舊網頁可能還留在瀏覽器裡），再試；仍不行照附錄三 |
| 試了一小時仍然不通 | **停手**，照附錄三最後一段換回名稱或保留現況，做 J-32 |

**🧪 開發機演練**：用**手機瀏覽器**開 `http://<IP>:18080` 登入；登得進去。**記下從 J-04 到這裡總共多久。**

---

上一份：《[…之二：詳細版（J-04～J-08）](visit-3-system-detail-2.md)》；下一份：《[…之四：詳細版（J-15～J-21）](visit-3-system-detail-4.md)》；主文件：《[第三次進院（1029）· 接手 v0.3.0、換成 IP、換版](visit-3-system.md)》

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|

[← 回部署手冊目錄](index.md)
