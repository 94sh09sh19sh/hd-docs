# 第三次進院（1029）· 接手 v0.3.0、換成 IP、換版之二：詳細版（J-04～J-08）

上層文件：《[第三次進院（1029）· 接手 v0.3.0、換成 IP、換版](visit-3-system.md)》

> - 狀態：**已照做 1029，凍結**。B 級部分成功，實際結果與要改的 13 處（O-13，1116 已改回）見《[第三次進院紀錄（1029，部分成功）](record-3-1029.md)》；改寫來源（1117）：第十八冊、第十七冊第 3、4 節；編號：沿用主文件的 `J-xx`，開發機才做的 `I-xx` 在之七～之九

詳細版共六份（之一～之六），這一份是第 2 節（J-04～J-08）；第 0 節（讀之前：時間怎麼排、名詞、停手條件）在《[…之一：詳細版（第 0 節、J-01～J-03）](visit-3-system-detail.md)》，附錄一～四（步驟對照、退回 `v0.3.0`、登不進去、一張紙）在《[…之六：詳細版（J-30～J-33、附錄）](visit-3-system-detail-6.md)》。

## 摘要

- 這一份是第 2 節：到場先看、先抄，不改任何東西；從這裡起指令都在院內主機的 PowerShell 裡打，不准自己開容器、不下 `docker run`
- J-04 開工三行：`$root`、`$cfg`、`cd $root\repo`；PowerShell 關掉再開就要重打
- J-05 用八條確認主機還是 1001 離開時的樣子；對不上（tag 變了、資料卷不見）就停手
- J-06 只有看到 0922 的容器才收，照第二次進院之九 L-02 起做
- J-07 先抄五樣：換成 IP 之後就再也看不到，是判斷 1001 可能 A 還是 B 的唯一線索
- J-08 確認 `<IP>`，先從護理站連一次；🧪 先開三條只對私人網路的防火牆規則，🏥 連不到就找資訊室

---

## 2. 到場：先看、先抄，不改任何東西

> ⚠️ 從這裡開始，指令都在**院內主機**的 PowerShell 裡打。**不要自己開任何容器，不要下 `docker run`。** 0922 就是這樣失敗的。

### J-04 開 PowerShell，輸入「開工三行」（＝V-09）

**做什麼**：開一個 PowerShell，輸入：

```powershell
$root = "C:\hd\hd-tablet-care"
$cfg  = "$root\config\.env"
cd $root\repo
```

前兩行設定兩個變數，之後每一條 `docker compose` 指令都寫成 `--env-file $cfg`，而且都在 `$root\repo` 底下打。

**怎麼知道成功了**：提示字元變成 `PS C:\hd\hd-tablet-care\repo>`。

> ⚠️ **PowerShell 關掉再開，這三行就要重打。** 看到 `couldn't find env file`，十次有九次是忘了這三行。

| 症狀 | 處置 |
|---|---|
| `cd` 說找不到路徑 | 根目錄被搬過或刪過。**停手**，問資訊室（0.7 節） |

**🧪 開發機演練**：`$root = "C:\hd-sim"`，其餘照做。

---

### J-05 確認主機還是 1001 離開時的樣子（＝E-05、《從零部署本系統》的「1001 之後的院內主機」）

**做什麼**（記下開始時間）

```powershell
git describe --tags
git status --short
docker ps -a --format "{{.Names}}  {{.Image}}  {{.Status}}"
docker volume ls --filter name=hd-tablet-care
Get-ChildItem $root\backups\keys
Get-ChildItem $root\backups -Filter *.db | Measure-Object
Get-PSDrive C
curl.exe -s http://localhost:13000/api/health
```

**怎麼知道成功了**

| 指令 | 1001 離開時 | 不一樣的話 |
|---|---|---|
| `git describe --tags` | `v0.3.0` | 有人動過 repo。**停手**，先問資訊室 |
| `git status --short` | 什麼都沒印 | 有人改過 repo 裡的檔案。把印出來的抄下來，**停手**先問 |
| `docker ps -a` | `hd-tablet-care-api-1`、`hd-tablet-care-nurse-web-1`、`hd-tablet-care-patient-web-1` 三列，映像檔 `hd-tablet-care:v0.3.0`，狀態 `Up …` | 狀態是 `Exited` → 主機中間重新開機過、服務沒有自己回來：**這就是 J-25 要的答案**，記下來，再 `docker compose --env-file $cfg up -d` |
| 同上 | 可能還有 `hd-tablet-care-ai-gateway-1`（1001 有沒有做 AI 閘道沒記到） | 有或沒有都對，**記下來**，J-20 要用 |
| 同上 | 不該有 `dialysis_system_v0` | 有的話做 J-06 |
| 同上 | 其他名字的容器 | 那是同機另一個專案的，**抄下名字，不要動** |
| `docker volume ls` | `hd-tablet-care-data`、`hd-tablet-care-keys` 兩個 | 不見了就不是 1001 的狀態，**停手** |
| `backups\keys` | 有 `hd-keys-20261001-173347.tar.gz` | 不見了，問資訊室是不是已經送往另一台機器 |
| `*.db` 的數量 | 每天 03:00 一份，1001 起約四週份 | 0 份 → 排程備份沒在跑，記下來（主機每天晚上可能都關機） |
| `Get-PSDrive C` 的 `Free` | 至少幾 GB | 不到 5 GB 就先問資訊室，J-17 建置與 J-18 的備份都要空間 |
| health | `{"status":"ok",…}` 開頭 | 看 `docker compose --env-file $cfg logs api --tail 30` 的最後幾行，抄下來 |

**可能怎麼壞**

| 症狀 | 處置 |
|---|---|
| `failed to connect to the docker API at npipe:…` | Docker Desktop 沒在跑。開始選單開啟它，等左下角變綠再重打；這也代表重新開機後它沒有自己起來，記下來給 J-25 |
| health 什麼都沒印 | 服務沒在跑。先看 `docker ps -a` 那一欄的狀態 |

**🧪 開發機演練**：照做。對照上面那張表：tag `v0.3.0`、三個服務加 `ai-gateway` 都 `Up`、兩個資料卷、`backups\keys` 有一份（檔名是之八 I-10 抄的，不是 1001 那一份）、`*.db` 是 0 份（開發機剛建，正常）。**表上每一列都對得上嗎？對不上的是手冊寫錯，圈起來。**

---

### J-06 0922 的容器還在的話（＝L-01、L-07）

**只有 J-05 看到 `dialysis_system_v0` 才做。** 那是 0922 第一次進院手動開的容器，掛著整顆 C 槽，**沒收掉不往下做**。

**做什麼**：照《[第二次進院（1001）· 從零部署本系統之九：收掉 0922 留下的東西](visit-2-system-cleanup.md)》L-02 起一步步收掉（那一份要另外印；J-05 沒看到它就不用印）。收完打：

```powershell
docker ps -a --format "{{.Names}}  {{.Image}}  {{.Status}}"
```

**怎麼知道成功了**：清單裡沒有 `dialysis_system_v0`。演練紀錄寫「0922 的容器：已收（J-06）」或「J-05 時已不在」。

**🧪 開發機演練**：跳過（開發機上沒有）。想練的話照那一份的附錄做替身。

---

### J-07 先抄五樣（＝E-06、T-02）

**這一步最容易被跳過，也最不能跳過。** 等一下換成 IP 之後，這幾樣就再也看不到了，而它們是判斷「1001 為什麼登不進去」的唯一線索（《[第二次進院紀錄（1001）之一：為什麼登不進去](record-2-1001-login.md)》的可能 A 還是 B）。

**做什麼**（一條一條打，每一條的結果**原文**抄進演練紀錄第 12 節，包括正常的）

```powershell
Select-String -Path $cfg -Pattern '^(HD_PUBLIC_API_URL|CORS_ORIGINS|MDM_KIOSK_BASE_URL)='
[Console]::OutputEncoding = [Text.Encoding]::UTF8; docker compose --env-file $cfg logs api | Select-String '允許的前端來源' | Select-Object -Last 1
docker compose --env-file $cfg exec nurse-web grep -rhoE 'https?://[A-Za-z0-9.-]+:[0-9]+' apps/nurse-pwa/dist/assets
docker compose --env-file $cfg --profile shell run --rm shell-builder keys-info
Test-Path $root\config\ai-gateway\config.yaml
```

| # | 在抄什麼 |
|---|---|
| 1 | `.env` 裡的三個位址（名單寫了什麼） |
| 2 | 執行中的後端**手上那份**放行名單 |
| 3 | 護理端網頁裡寫死的後端位址 |
| 4 | 院內 CA、伺服器憑證、簽章金鑰的指紋；「伺服器憑證」那一行應該是 `DNS:<名稱>` |
| 5 | AI 閘道的設定檔在不在（`True`／`False`），J-20 要用 |

**怎麼知道成功了**：五樣都抄了。**值本身只寫演練紀錄的紙本**；要拍照也可以，照片只進私人 repo（0.0 節「公開範圍」）。第 4 條只印指紋、到期日與位址，**不會印出私鑰**；私鑰只在金鑰資料卷與 `hd-keys-*.tar.gz` 裡。

**怎麼看 1、2 兩條**（看懂就寫，看不懂照抄就好，回去再判斷）：

| 兩條比起來 | 1001 是哪一種 |
|---|---|
| 一樣，但都不是 `http://<名稱>:18080`（例如照抄了範例的 `hd-server`、寫了 `localhost`） | 可能 A：名單寫錯 |
| 第 1 條是 `http://<名稱>:18080`，第 2 條是別的值 | 可能 B：改完 `.env` 沒有 `up -d` |
| 兩條都是 `http://<名稱>:18080` | 名單沒問題，問題在網址列或網頁裡的位址（第 3 條） |

1029 落在第三列（紀錄 O-01）。

| 症狀 | 處置 |
|---|---|
| 第 2 條什麼都沒印 | 日誌被清過（例如容器重建過）。寫「沒有」就好 |
| 第 4 條「伺服器憑證」已經是 `IP Address:…` | 1001 填的其實是 IP。**停手**，第 3 節的換法要重新判斷，先打電話問開發端 |
| 第 4 條等很久、開始下載東西 | 映像檔 `hd-tablet-care-shell-builder:v0.3.0` 不見了，正在重建。等它跑完（約 30 分鐘），記下來 |

**🧪 開發機演練**：照做。第 1 條 `CORS_ORIGINS` 是 `hd-server`、第 2 條日誌也是 `hd-server` → 照上面那張判斷表，應該判成「可能 A」。**判得出來嗎？** 第 4 條伺服器憑證是 `DNS:<名稱>`。開發機可以拍照（第 4 條沒有私鑰，開發用金鑰 I-17 也會刪），但**不要拍 `notepad $cfg` 的畫面**（有 `JWT_SECRET` 與初始密碼）。

---

### J-08 確認 `<IP>`，並先從護理站連一次（＝T-03、T-04）

**做什麼**

1. 在主機上看 IP：

   ```powershell
   ipconfig /all
   ```

   找實體網卡（「乙太網路」或「Wi-Fi」）那一段，**不是** `vEthernet (WSL)`、`vEthernet (Default Switch)`，也不是 `172.` 開頭的：

   | 看什麼 | 應該是 |
   |---|---|
   | IPv4 位址 | 與資訊室給的 `<IP>` **一字不差** |
   | DHCP 已啟用 | `否`；或 `是`，但資訊室說已經在 DHCP 保留了這個 IP |

2. 到**護理站的電腦**，瀏覽器開 `http://<IP>:13000/api/health`。
3. 同一台電腦開 `http://<IP>:18080`，**看得到登入頁就好，先不要按登入**（還沒改名單，一定是 `Failed to fetch`）。
4. 有手機的話，連上**平板實際要用的那個 Wi-Fi**，瀏覽器開 `http://<IP>:18081/shell/`。

**怎麼知道成功了**：第 1 步 IP 一致；第 2 步看到 `{"status":"ok",…}`；第 3 步看到登入頁；第 4 步看到外殼下載頁（上面寫的主機位址還是 `<名稱>`，**現在是對的**，J-12 之後才會換）。

**可能怎麼壞**

| 症狀 | 處置 |
|---|---|
| 主機上的 IP 與資訊室給的不一樣 | **停手**，問清楚再做 |
| 護理站開不到 | 防火牆或網段。**找資訊室，不要自己關防火牆，也不要往下改設定**——換成 IP 也不會通 |
| 護理站開得到，手機（平板的 Wi-Fi）開不到 | 平板的網段到不了主機。第 3 節照做，第 7 節先不做，交資訊室 |

> **這一步是換位址之前的保險。** 連得到才改；連不到時改什麼都沒用。

**🧪 開發機演練**：第 1 步照做（DHCP 是「是」沒關係）；第 2～4 步用**手機瀏覽器**開，手機要開得到三個網址。開不到：防火牆規則、Wi-Fi 設定檔類型、Wi-Fi 擋裝置互連（之七 0.3 節）。

手機要連得到開發機的三個埠，先用**系統管理員身分**的 PowerShell 開三條只對私人網路的防火牆規則（撤除時之九 I-17 會刪）：

```powershell
New-NetFirewallRule -DisplayName "hd-sim api 13000" -Direction Inbound -Protocol TCP -LocalPort 13000 -Profile Private -Action Allow
New-NetFirewallRule -DisplayName "hd-sim nurse 18080" -Direction Inbound -Protocol TCP -LocalPort 18080 -Profile Private -Action Allow
New-NetFirewallRule -DisplayName "hd-sim patient 18081" -Direction Inbound -Protocol TCP -LocalPort 18081 -Profile Private -Action Allow
```

- **為什麼要「私人」**：三條規則都是 `-Profile Private`，只在網路設定檔類型是「私人」時生效。Windows 連上新的 Wi-Fi 預設是「公用」，這時規則不生效、手機連不到。不改成對所有網路放行，是因為開發機帶到咖啡廳或學校時，這三個埠會對整個網路開放
- **怎麼改**：設定 → 網路和網際網路 → Wi-Fi → 這個網路的內容 →「網路設定檔類型」選**私人網路**。或在系統管理員身分的 PowerShell 打 `Get-NetConnectionProfile`，找手機連的那個網路的 `InterfaceAlias`，再打 `Set-NetConnectionProfile -InterfaceAlias "Wi-Fi" -NetworkCategory Private`（`Wi-Fi` 換成那個 `InterfaceAlias`）；再打一次 `Get-NetConnectionProfile`，那一段的 `NetworkCategory` 是 `Private` 就好。印出 `DomainAuthenticated` 或改不了：那是學校或公司管的網路，換家裡的 Wi-Fi 或手機熱點。演練完用的是熱點或外面的網路，改回「公用」

🏥 院內不做這一步：院內主機的網路類型與防火牆歸資訊室管，連不到就找資訊室。

---

上一份：《[…之一：詳細版（第 0 節、J-01～J-03）](visit-3-system-detail.md)》；下一份：《[…之三：詳細版（J-09～J-14）](visit-3-system-detail-3.md)》；主文件：《[第三次進院（1029）· 接手 v0.3.0、換成 IP、換版](visit-3-system.md)》

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|
| [1118](https://94sh09sh19sh.github.io/hd-docs/1118/deployment/visit-3-system-detail-2/) | 2026-11-18 | 首次定版。1118 照每份約 300 行的上限由《第三次進院（1029）· 接手 v0.3.0、換成 IP、換版之一：詳細版》拆出，內容與步驟編號不動 |

[← 回部署手冊目錄](index.md)
