# 第三次進院（1029）· 接手 v0.3.0、換成 IP、換版之九：開發機才做的演練（I-13～I-17、附錄）

上層文件：《[第三次進院（1029）· 接手 v0.3.0、換成 IP、換版](visit-3-system.md)》

> - 狀態：**已照做 1029（第一輪），凍結**。第一輪做到 J-30，I-13～I-15 沒做，判定 `v0.4.0` **還不能**帶進院（《[第三次進院紀錄（1029，部分成功）](record-3-1029.md)》O-02）；改寫來源（1117）：第十七冊；編號：`I-xx`（沿用第十七冊），中間照做的是主文件的 `J-xx`

開發機演練共三份（之七～之九），這一份是第 5、6 節（I-13～I-17）與附錄；讀之前（要準備的東西、時間、規矩）與第 1 節準備在《[…之七：開發機才做的演練（第 0 節、I-01～I-05）](visit-3-system-rehearsal.md)》。

## 摘要

- 這一份是第 5 節模擬部署才做的驗收（I-13～I-16）、第 6 節撤除（I-17）與附錄步驟對照
- I-13 讓後端真的去抓模擬院方 API，並驗院內的設定擋得住它（DEP-46）
- I-14 三支 `verify --live`；這是第 2～5 節裡唯一准用開發機 Node.js 的地方
- I-15 照詳細版附錄二（之六）真的退一次 `v0.3.0`，舊版照樣登得進去
- I-16 十項判定，有一項 ✗ 就不能帶進院；1029 第一輪判定 `v0.4.0` 還不能帶
- I-17 撤除乾淨：容器、資料卷、映像檔、`C:\hd-sim`、防火牆規則、平板上的 App；撤除只准在模擬部署做

---

## 5. 模擬部署才做的驗收

### I-13 模擬院方 API 接上去，並驗院內的設定擋得住它（＝V-30a 方框、部署規範第 9 章第 8 項）

**做什麼**

1. 讓後端真的去抓模擬院方 API：

   ```powershell
   notepad $cfg
   ```

   最後那兩行改成：

   ```
   HOSPITAL_API_BASE_URL=http://hospital-api-sim:8090/dialysislist.php
   HD_SIMULATION_DEPLOYMENT=yes
   ```

   存檔，然後：

   ```powershell
   docker compose --env-file $cfg --profile simulation up -d
   docker compose --env-file $cfg exec -T api node apps/api/dist/hospital-api-probe.js
   ```

2. 手機開護理端簡易版，**什麼都不碰**，等三分鐘。
3. 驗「院內的設定擋得住模擬」：`.env` 的 `HD_SIMULATION_DEPLOYMENT=yes` **清空**（等號後面什麼都不留），存檔，然後：

   ```powershell
   docker compose --env-file $cfg up -d api
   docker compose --env-file $cfg logs --tail 20 api
   ```

4. 改回原樣：`HOSPITAL_API_BASE_URL` 與 `HD_SIMULATION_DEPLOYMENT` **兩行都清空**（和院內一樣），存檔，然後：

   ```powershell
   docker compose --env-file $cfg up -d api
   docker compose --env-file $cfg --profile simulation stop hospital-api-sim
   curl.exe -s http://localhost:13000/api/health
   ```

**怎麼知道成功了**

| 哪一步 | 應該是 |
|---|---|
| 1 | 探測印出「模擬標頭：有」，用的是 `.env` 裡的位址，所以沒問位址 |
| 2 | 床位圖上出現 A1、A2… 與「模擬甲」等虛構病人 |
| 3 | 日誌寫**拒絕啟動**，並指出 **DEP-46** |
| 4 | health 正常；院方 API 的兩行都是空白 |

> 💡 第 3 步就是院內那一道保險：院內主機的 `HD_SIMULATION_DEPLOYMENT` 永遠空白，萬一有人把模擬部署的位址抄過去，後端會拒絕啟動，而不是把假病人寫進院內的資料庫。

---

### I-14 跑三支驗收（＝V-31、《從零部署本系統之二：容器路線的原冊》的開發機實測）

**這一步是驗收，不是部署步驟**，也是整輪唯一准用 Node.js 的地方。在**平常寫程式的工作目錄**（不是 `C:\hd-sim\repo`），先切到同一個 tag 再跑：

```powershell
git switch --detach <新 tag>
npm run verify:iteration11 -- --live --env-file C:\hd-sim\config\.env
npm run verify:iteration12 -- --live --env-file C:\hd-sim\config\.env
npm run verify:iteration13 -- --live --env-file C:\hd-sim\config\.env
git switch master
```

**怎麼知道成功了**：三支都全部 ✓。第一支會執行 `down -v` 再 `up -d`，驗證「資料卷不會被 `-v` 刪掉」，**這是刻意的**。

| 症狀 | 處置 |
|---|---|
| 某一項 ✗ | 抄下原文。是驗收腳本跟不上新版（例如沒料到 `HD_EXPORT_DIR`），還是新版真的有問題？前者修腳本、後者修程式，**兩種都要打新 tag 重新演練**（I-01 那一列） |

---

### I-15 退回 `v0.3.0` 演練（＝詳細版附錄二、W-20）

院內要是新版出問題，靠的就是詳細版附錄二。這裡照它真的退一次。

**做什麼**：翻到詳細版**附錄二**，照做。`<備份檔名>`、`<雜湊>` 用 J-18 抄的那一份。

**怎麼知道成功了**

| 看什麼 | 應該是 |
|---|---|
| 還原輸出 | `完整性檢查：ok`、`還原的就是 DATABASE_URL 指向的正本` |
| `docker ps` | 三個服務的映像檔是 `hd-tablet-care:v0.3.0` |
| 手機開 `http://<IP>:18080`，重新整理後登入 | **登得進去**——證明詳細版說的「J-11 已經用 `<IP>` 重建過 `v0.3.0` 的網頁，所以舊版也登得進去」是真的 |
| 護理端「新增裝置」 | J-28 註冊的那台平板不見了（它是更新之後才註冊的，跟著資料一起退回去了）。**這是對的**，正好說明「更新之後寫進去的資料會一起消失」 |

| 症狀 | 處置 |
|---|---|
| 舊版登不進去，`Failed to fetch` | 詳細版附錄二寫錯了（舊版的網頁裡可能還是 `<名稱>`）。抄下 J-11 那條 `grep` 的結果，**回去改詳細版**，再演練一次 |

---

### I-16 寫紀錄、判定能不能帶進院

**做什麼**：把演練紀錄第 11 節填完，逐項對照下表。

| # | 判定條件 |
|---|---|
| 1 | I-12 重現了 1001（`Failed to fetch`、放行檢查空的） |
| 2 | J-07 判得出「可能 A」 |
| 3 | J-14 手機登得進去 |
| 4 | J-18 套用 19 個遷移、`更新完成` |
| 5 | J-19 新版登得進去、資料（帳號密碼）留住了 |
| 6 | J-26 探測工具跑得動；I-13 擋得住模擬 |
| 7 | J-29 平板釘住、護理端看得到 |
| 8 | I-14 三支全部 ✓ |
| 9 | I-15 退回 `v0.3.0` 之後登得進去 |
| 10 | 詳細版紙本上圈起來的地方都改回文件了（含詳細版 0.3 節的時間） |

**怎麼知道成功了**：十項都 ✓，紀錄最後一行寫「`<新 tag>` 可以帶進院，＿月＿日」。**有一項 ✗ 就不能帶**：修好、打新 tag、重新演練。

1029 第一輪：第 6 項的 I-13 那一半、第 8、9 項沒做，判定 `v0.4.0` 還不能帶進院（演練紀錄 11.1 節）。

---

## 6. 撤除

### I-17 撤除乾淨（＝V-32）

模擬部署做完**一定要撤除**，下一輪才又是從零；也免得開發機一直有服務佔著埠。

**做什麼**

```powershell
cd C:\hd-sim\repo
docker compose --env-file C:\hd-sim\config\.env --profile ai --profile shell --profile simulation down
docker volume rm hd-tablet-care-data hd-tablet-care-keys
docker images "hd-tablet-care*" --format "{{.Repository}}:{{.Tag}}" | ForEach-Object { docker rmi $_ }
cd C:\
Remove-Item -Recurse -Force C:\hd-sim
```

再開一個**系統管理員身分**的 PowerShell，刪掉 J-08 之前開的防火牆規則：

```powershell
Get-NetFirewallRule -DisplayName "hd-sim *" -ErrorAction SilentlyContinue | Remove-NetFirewallRule
```

平板或手機上：

1. 解除固定（輸入 PIN），把「透析照護平板」**解除安裝**。這是開發用金鑰簽的版本，留著的話院內裝院內版時會「套件與現有套件衝突」。
2. 用的是暫用平板的話：**不要原廠重設**；PIN 與螢幕固定可以留著（院內 J-28 本來就要設）；開發用的 Wi-Fi 可以「忘記」。

**怎麼知道成功了**

```powershell
docker volume ls --filter name=hd-tablet-care
docker images "hd-tablet-care*"
Test-Path C:\hd-sim
```

前兩條只有標題列，第三條 `False`。

部署金鑰與 `$HOME\.ssh\config` 那兩段**留著**，下一輪繼續用；兩個基底映像（`node`、`eclipse-temurin`）也可以留著。

> ⚠️ **撤除只准在模擬部署做。** 院內主機的撤除會刪掉整個透析中心的紀錄，要院方書面同意，照《[備份、還原與關服務](ref-backup-shutdown.md)》。

---

## 附錄：步驟對照

| 本冊 | 對應 | 本冊 | 對應 |
|---|---|---|---|
| I-01 | V-03、W-01、W-02 | I-10 | V-21～V-24 |
| I-02 | V-04、V-06 | I-11 | V-29、V-30 |
| I-03 | V-13 方框、V-32 | I-12 | 《第二次進院紀錄（1001）之一》的 1001 經過與直接原因 |
| I-04 | V-10、V-20 | 第 3、4 節 | 主文件與詳細版 J-04～J-30 |
| I-05 | V-08 | I-13 | V-30a 方框 |
| I-06 | V-09 | I-14 | V-31 |
| I-07 | V-11、V-20 | I-15 | 詳細版附錄二、W-20 |
| I-08 | V-12、《`.env` 怎麼填之一：開發機演練》 | I-16 | 《從零部署本系統之二：容器路線的原冊》的開發機實測 |
| I-09 | V-13～V-16 | I-17 | V-32 |

`V-xx` 在《[從零部署本系統](ref-fresh-install.md)》、`W-xx` 在《[從零部署本系統之一：容器路線的原冊](ref-fresh-install-detail.md)》（W-20 在《[本系統換版與退回](ref-upgrade-2.md)》）、`J-xx` 是主文件的步驟。

---

上一份：《[…之八：開發機才做的演練（I-06～I-12、照主文件做 J-04～J-30）](visit-3-system-rehearsal-2.md)》；主文件：《[第三次進院（1029）· 接手 v0.3.0、換成 IP、換版](visit-3-system.md)》

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|
| [1118](https://94sh09sh19sh.github.io/hd-docs/1118/deployment/visit-3-system-rehearsal-3/) | 2026-11-18 | 首次定版。1118 照每份約 300 行的上限由《第三次進院（1029）· 接手 v0.3.0、換成 IP、換版之七：開發機才做的演練》拆出，內容與步驟編號不動 |

[← 回部署手冊目錄](index.md)
