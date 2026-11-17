# 從零部署本系統（第 6 份，V-25～V-30a）

上層文件：《[從零部署本系統](ref-fresh-install.md)》

> **狀態：現行（常備參考）。** 改寫自第十五冊（1117）；編號 `V-xx`（沿用第十五冊），每一步下面註明對應的 `N-xx` 與 `W-xx`／`Y-xx`／`Z-xx`。1118 照步驟順序拆成七份，這是第 6 份；🧪／🏥／📍 標記的意思見第 1 份 0.2 節。

## 摘要

- 第 8 節後半（平板）：V-25 平板連得到主機、V-26 在護理端註冊平板（QR code 只顯示一次）、V-27 系統設定並安裝 App、V-28 第一次開啟並釘住
- 第 9 節 AI 閘道：V-29 放設定檔（`base_url`、`model` 保持空白）、V-30 建置並啟動，最後印出 503 是對的
- 第 9.5 節：院方資料 1110 起改成讀抓取腳本存下的檔（迭代 32），不打院方 API
- V-30a 改成讀檔檢查，啟用與停用照《讀檔：啟用、檢查、停用》；抓取腳本還沒在主機上跑就停在 V-30
- V-30a 的舊做法（1005～1109 直接探測院方 API）留給開發機與當時紀錄的對照

---

## 8. 外殼 App 與平板（續）

### V-25 平板連得到主機

對應：N-24、Y-08

**做什麼**：拿一台平板（或手機）連上**與平板實際使用時相同的 Wi-Fi**，用瀏覽器開 `http://<主機>:18081/shell/`。

**怎麼知道成功了**：看得到下載頁。**這也是 V-08 那個 `<主機>` 對平板來說對不對的驗證。**

| 症狀 | 處置 |
|---|---|
| 主機自己開得到，平板開不到 | Windows 防火牆擋了連入，或那個 Wi-Fi 網段到不了主機。**找資訊室**，不要自己關防火牆 |
| 平板開不到，手機在同一個 Wi-Fi 開得到 | 平板的 Wi-Fi 連錯了 |
| 平板說找不到這個主機 | `<主機>` 是名稱而平板查不到。這時要回 V-08 換成固定 IP——**而那代表 V-22 的伺服器憑證要重簽**，照《[護理站登不進去與主機位址之一：換主機位址](ref-login-switch-ip.md)》一步步換 |

> 📍 **1001**：未測。1029 換成 IP 之後護理站與手機都連得到，暫用平板佈建成功。

> 🧪 **模擬部署**：手機和開發機要連**同一個 Wi-Fi**，位址是開發機的區網 IP。手機開不到時照下面三步：
>
> 1. Windows「設定 → 網路和網際網路 → Wi-Fi → 這個網路的內容」，網路設定檔類型改成**私人**。
> 2. 仍不行的話，用**系統管理員身分**開 PowerShell，只對私人網路開放病人端那一個埠（指令在方框下面）。撤除時（第 10.2 節）記得刪掉這條規則。V-17 第四段要用手機開護理端的話，`18080`、`13000` 照樣各加一條（名稱也用 `hd-sim` 開頭）。
> 3. 學校或公司的 Wi-Fi 常常擋裝置互連，改用手機熱點或家裡的 Wi-Fi。

🧪 第 2 步的指令：

```powershell
New-NetFirewallRule -DisplayName "hd-sim patient 18081" -Direction Inbound -Protocol TCP -LocalPort 18081 -Profile Private -Action Allow
```

---

### V-26 在護理端註冊平板

對應：N-25、Y-09

**做什麼**：護理端 → **新增裝置**（1007 以前叫裝置管理） → **註冊新平板**。畫面會出現一個**佈建 QR code** 與一行文字網址。

> ⚠️ **這兩樣只顯示一次。** 這個畫面先不要關，拿著平板做完 V-27、V-28 再離開。

**怎麼知道成功了**：畫面上的網址以 `https://<主機>:18081` 開頭。不是 `https://` 的話，`.env` 的 `MDM_KIOSK_BASE_URL` 還是 `http://`，改好後 `up -d api` 再重新註冊。

---

### V-27 平板的系統設定並安裝 App

對應：N-26、Y-10、Y-11

**做什麼**

1. 平板設定裝置 PIN，關閉「新增使用者」。
2. 設定 → 安全性 → **螢幕固定**：開啟，並勾選「解除固定前要求 PIN」。（各廠牌位置略有不同，可在設定裡搜尋「固定」；實際路徑見《[平板與外殼 App](ref-tablet.md)》）
3. 平板的瀏覽器開 `http://<主機>:18081/shell/`，按「下載 App」，安裝。系統問是否允許瀏覽器安裝不明來源的應用程式時，允許。

**怎麼知道成功了**：平板上多了「透析照護平板」這個 App。

| 症狀 | 處置 |
|---|---|
| 「套件與現有套件衝突」 | 這台裝過**另一把金鑰簽的版本**（例如模擬部署時裝的開發版）。先解除安裝再裝 |
| 「應用程式未安裝」，而且沒裝過 | 下載不完整，重新下載一次 |

---

### V-28 第一次開啟並釘住

對應：N-27、Y-12、Y-13

**做什麼**

1. 開啟「透析照護平板」→ 按「**掃描 QR code**」→ 允許相機 → 對準 V-26 畫面上的 QR code。三欄會自動填好，**核對序號與這台平板的標籤一致**。（沒有相機時手動填：主機位址填 `MDM_KIOSK_BASE_URL` 的值，序號與金鑰照 V-26 畫面上的）
2. 按「儲存並啟動」→ 系統問「要固定這個應用程式嗎」→ 按「確定」。
3. 回到護理端 → 新增裝置，等 15～30 秒。
4. 在平板上**解除一次固定**（輸入 PIN），30 秒內護理端要變成「已跳出」。
5. 釘回去：解鎖後 App 還停在畫面上，但已經沒有釘住，直接點它沒用。按多工鍵把「透析照護平板」**從多工畫面滑掉**，再從桌面開啟 → 系統再問一次「要固定這個應用程式嗎」→ 按「確定」。護理端 15～30 秒內回到「固定中」。（沒跳出確認框就重新開機，App 開機後會自己起來並詢問）

**怎麼知道成功了**

| 在哪裡看 | 應該是 |
|---|---|
| 平板 | 病人端的等待畫面，**沒有任何憑證警告**；按上一頁、首頁、多工鍵都離不開 |
| 護理端「固定狀態」 | 固定中（解除時變成已跳出） |
| 護理端「外殼版本」 | 版本正常，底下有版本號 |

**把序號與床號的對應記下來。** 🏥 實際部署首波只佈建實際會用到的兩三台（DEP-36），每台做一次 V-26～V-28。

| 症狀 | 處置 |
|---|---|
| 「主機位址不是 https:// 開頭」 | 回 V-26 的處置 |
| 一片空白或「網頁無法使用」 | 位址錯或 V-24 沒做。平板「設定 → 應用程式 → 透析照護平板 → 儲存空間 → 清除資料」，重新佈建（《[平板與外殼 App](ref-tablet.md)》） |
| 上方出現琥珀色「……版本不相容」 | 下載頁的 APK 與系統版本對不上，見《[平板與外殼 App](ref-tablet.md)》 |

> 🧪 **模擬部署**：用開發用的 Android 手機代替平板。做完之後手機上的 App 要**解除安裝**，免得日後拿這支手機裝院內版時衝突（V-27 的第一列）。

---

## 9. AI 閘道：讓它就位

首波 AI 功能是關的（DEP-29）。這一節只讓閘道就位、確認它清楚回報「設定還沒填」，**不接任何模型**。閘道的設定與日後接上院內 GPU API 在《[AI 閘道](ref-ai-gateway.md)》（`Z-xx`）。

### V-29 放 AI 閘道的設定檔

對應：N-28、Z-20

**做什麼**（在 `$root\repo` 底下）

```powershell
New-Item -ItemType Directory -Force $root\config\ai-gateway | Out-Null
Copy-Item services\ai-gateway\config.hospital.example.yaml $root\config\ai-gateway\config.yaml
```

範本的 `base_url` 與 `model` 刻意留空，**保持空白**。**絕對不要填實驗室的位址**——那是把資料往院外送。

> 📍 **1001**：做了沒有，沒記到。`Test-Path $root\config\ai-gateway\config.yaml` 是 `True` 就是做過了，**不要再複製一次蓋掉它**。院內主機 1116 時 `ai-gateway` 是 `v0.4.0`、`Up`。

---

### V-30 建置並啟動閘道

對應：N-29、Z-21、Z-22

**做什麼**

```powershell
docker compose --env-file $cfg --profile ai build ai-gateway
docker compose --env-file $cfg --profile ai up -d ai-gateway
docker compose --env-file $cfg exec -T api node -e "fetch('http://ai-gateway:8000/health').then(async r=>console.log(r.status, await r.text()))"
```

**怎麼知道成功了**：建置最後印出 `全部通過`；最後一條印出

```
503 {"status":"error","config":"error","detail":"base_url 尚未填寫（推論端點的位址）"}
```

**503 在這裡是正確的**：閘道在、後端連得到它、它清楚說出還缺什麼。

| 症狀 | 處置 |
|---|---|
| `fetch failed` | 閘道沒起來，`docker compose --env-file $cfg --profile ai logs ai-gateway` |
| `找不到設定檔` | V-29 的路徑不對，必須是 `config\ai-gateway\config.yaml` |
| 建置時 `no such host` | 同 V-06 第二段那一列 |

> ⚠️ 閘道起過之後，日後更新時要不要帶 `--profile ai` 重建閘道，照《[本系統換版與退回](ref-upgrade.md)》（1116 換到 `v0.5.0` 時兩版之間閘道沒改、沒重建，`ai-gateway` 仍是 `v0.4.0`）。接上正式 GPU API 是 Q-07 有答案之後的事，見《[AI 閘道](ref-ai-gateway-3.md)》Z-23。

---

## 9.5 院方資料：讀抓取腳本存下的檔

**1110 起本系統不打院方任何 API**（迭代 32，《[實作規格書](../requirements/implementation-spec.md)》4.32）：主機上的抓取腳本 `hd-hospital-fetch` 每 3 分鐘（07:00～23:00）把院方透析清單存成檔，本系統以**唯讀**掛那個資料夾來讀，病人、床位、療程自動進來。院內主機 1116 起是 `hd-hospital-fetch` v0.3.0 在 `C:\API_Fetch`、留底檔在 `C:\API_Fetch\IDH_interface`。抓取腳本的安裝與維運在《[院方 API 抓取腳本的維運](ref-fetch-script.md)》；檢驗資料（`hb`）1111 學長答不用這邊處理，先不讀（《[檢驗資料（hb）抓取（未採用）](ref-hb-fetch.md)》）。

從零部署時，這一節**在抓取腳本已經在這台主機上跑起來之後**才做；還沒有抓取腳本，就停在 V-30，病人、床位、療程照護理師的人工操作。

### V-30a 接上讀檔並做讀檔檢查

對應：第十五冊 V-30a（1005 新增，1111 改成讀檔）；1116 院內實際照的是 SY-09～SY-11（《[第五次進院（1116）任務二 · 本系統換版上線](visit-5-system-2.md)》）

**做什麼**：啟用前的條件、`.env` 要改的五行、讀檔檢查的指令、第一輪怎麼驗、停用，**一律照《[讀檔：啟用、檢查、停用](ref-dialysis-files.md)》**。🏥 `.env` 改完的樣子：

```
HD_DIALYSIS_LIST_DIR=C:\API_Fetch\IDH_interface
HD_LAB_DIR=
COMPOSE_FILE=docker-compose.yml;docker-compose.dialysis-files.yml
HOSPITAL_API_BASE_URL=
HD_SIMULATION_DEPLOYMENT=
```

`docker compose --env-file $cfg up -d` 之後跑讀檔檢查：

```powershell
docker compose --env-file $cfg exec -T api node apps/api/dist/hospital-api-probe.js
```

**怎麼知道成功了**：標題「院方資料讀檔檢查（只讀、只印結構，不印任何一個值，也不印路徑）」；「透析清單資料夾」寫「在、讀得到」「唯讀：是」「模擬標記檔：沒有」；透析清單的狀態檔「讀得到」、結果「成功」、當天段落數、合起來的列數與每一欄的型態分布；「檢驗資料資料夾」沒設定是正常的（`HD_LAB_DIR` 留空）。最後一行「以上可以整段抄進演練紀錄」。工具只讀、不寫任何檔，**不印路徑、姓名、病歷號與檢驗值**。日誌有「院方資料同步已啟用（讀透析清單資料夾）」。

讀檔檢查不對時的處置表（資料夾不在、空資料夾、唯讀：否、模擬標記檔、狀態檔看不到、當月檔還沒建立……）在《[讀檔：啟用、檢查、停用](ref-dialysis-files.md)》。

> ⚠️ **一啟用，當天清單上所有病人的主檔與療程都會進主機**，護理端會看到整個透析室，不是只有首波那一位；床位只新增、不會自己消失，停用也不會刪掉已寫進去的。

> ⚠️ **不要用瀏覽器或 `curl` 直接打院方 API**：回應是全中心病人的姓名與病歷號，會整片印在螢幕上（《[第二次進院紀錄（1001）之一：為什麼登不進去](record-2-1001-login.md)》E-16）。

> 🧪 **模擬部署**：用模擬院方 API 寫的模擬檔，`.env` 的五行改成下面這樣，`docker compose --env-file $cfg --profile simulation up -d`，等 3 分鐘再跑同一條讀檔檢查，印出「模擬標記檔：有」是對的。接著開護理端簡易版：不必碰任何東西，床位圖上就會出現 A1、A2… 與「模擬甲」等病人（全是虛構的）。練院內那種帶空白與中文的路徑（B2）、驗「院內的設定擋得住模擬」（SY-M1），照《[讀檔：啟用、檢查、停用](ref-dialysis-files.md)》與《[`.env` 怎麼填之一：開發機演練](ref-env-simulation.md)》1.9。

🧪 模擬讀檔的五行：

```
HD_DIALYSIS_LIST_DIR=
HD_LAB_DIR=
COMPOSE_FILE=docker-compose.yml;docker-compose.hospital-files-sim.yml
HOSPITAL_API_BASE_URL=
HD_SIMULATION_DEPLOYMENT=yes
```

#### V-30a 的舊做法：直接探測院方 API（1005～1109，院內已不用）

1005～1109 院方透析清單 API 要取代護理師的手動輸入（實作規格書 4.13），這一步只**探測**、不啟用：看主機連不連得到、回應長什麼樣（透析中的結束欄位、床位格式、姓名欄），把輸出帶回來；啟用要等探測結果看過、Q-35 報備過。1029 第三次進院照這個做過一次（J-26）。**1110 起院內一律不打院方 API**，這一段留給開發機與當時紀錄的對照。

**做什麼**（在 `$root\repo` 底下；位址向資訊室或護理長問，**只在這裡當場輸入，不要寫進 `.env`、不要貼進任何紀錄**）：

```powershell
$u = Read-Host '院方透析清單 API 的位址（含 dialysislist.php，不含 ?date=）'
docker compose --env-file $cfg exec -T -e HOSPITAL_API_BASE_URL=$u api node apps/api/dist/hospital-api-probe.js
```

**怎麼知道成功了**：印出「連線：成功」、「解析：成功」，接著是每一欄的型態分布與幾段統計，最後一行「以上可以整段抄進演練紀錄」。 **整段抄進演練紀錄**——工具只印結構（型態、欄數、筆數、床位的樣式），**不印任何一個病人的值，也不印位址**，抄下來不會帶出病人資料。

| 症狀 | 處置 |
|---|---|
| `連線：失敗——找不到院方主機` 或 `連不到院方主機所在的網段` | 主機與院方 API 不在同一個網段，或名稱查不到。抄下來，回去問資訊室（Q-35）；**不要改主機的網路設定** |
| `連線：失敗——連線被拒` | 位址的埠不對，或院方服務沒開。核對位址再試一次 |
| `連線：失敗——逾時` | 院方伺服器沒有在 30 秒內回應。換個時間再試一次，兩次都逾時就抄下來 |
| `解析：失敗` | 位址打到的不是透析清單（例如少了檔名）。核對位址 |
| `模擬標頭：有` | 打到的是模擬院方 API，不是院方的——位址填錯了 |
| `沒有設定院方 API 的位址` | `Read-Host` 那一行沒有輸入東西 |

🧪 舊做法的模擬：照《[`.env` 怎麼填之一：開發機演練](ref-env-simulation.md)》1.9 的 C 把 `.env` 指向模擬院方 API（`HOSPITAL_API_BASE_URL=http://hospital-api-sim:8090/dialysislist.php`）、寫上 `HD_SIMULATION_DEPLOYMENT=yes`，然後：

```powershell
docker compose --env-file $cfg --profile simulation up -d
docker compose --env-file $cfg exec -T api node apps/api/dist/hospital-api-probe.js
```

第二行用的是 `.env` 裡的位址，所以不必輸入。印出「模擬標頭：有」是對的。接著開護理端簡易版，床位圖上就會出現 A1、A2… 與「模擬甲」等病人。最後驗「院內的設定擋得住模擬」（部署規範第 9 章第 8 項）：把 `.env` 的 `HD_SIMULATION_DEPLOYMENT` 清空，`docker compose --env-file $cfg up -d api`， `docker compose --env-file $cfg logs --tail 20 api` 要看到**拒絕啟動、指出 DEP-46**；看到之後改回 `yes`、再 `up -d api`。

---

上一份：《[從零部署本系統（第 5 份，V-18～V-24）](ref-fresh-install-5.md)》｜下一份：《[從零部署本系統（第 7 份，V-31～V-32、收尾與附錄）](ref-fresh-install-7.md)》｜第一份（索引）：《[從零部署本系統](ref-fresh-install.md)》｜[部署手冊目錄](index.md)

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|

[← 回部署手冊目錄](index.md)
