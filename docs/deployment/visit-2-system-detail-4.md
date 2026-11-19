# 第二次進院（1001）· 從零部署本系統之四：詳細版（N-19～N-27）

上層文件：[《第二次進院（1001）· 從零部署本系統》](visit-2-system.md)

> 狀態：**已照做 1001，凍結**（結果見[《第二次進院紀錄（1001，部分成功）》](record-2-1001.md)）；1117 由舊的第十四冊改寫；編號與主文件相同（`N-xx`），每一步開頭的「對應」是沿用的原步驟（`W-xx`、`Y-xx`、`Z-xx` 在哪一份，見[《之一》](visit-2-system-detail.md)開頭）

## 摘要

- 第 7 節外殼 App 與平板：在主機上把 APK 建出來，再讓平板從院內的下載頁安裝、釘住；私鑰全程不離開主機
- N-19～N-23：外殼 repo 的部署金鑰與 clone、`shell-builder` 映像檔、建 APK（第一次產生金鑰）、金鑰備份與核對、病人端改走 HTTPS
- N-24～N-27：平板連得到主機、在護理端註冊、平板的系統設定與安裝、第一次開啟並釘住
- 🧪 用開發用的 Android 手機代替平板，做完要解除安裝；手機開不到下載頁的處置在 N-24
- 1001 做到 N-23，N-24～N-27 沒做；N-18 以前在《之三》，N-28 起在《之五》

## 7. 外殼 App 與平板

這一節做兩件事：在主機上把外殼 App（APK）建出來，然後讓平板從院內的下載頁安裝、釘住。**私鑰全程不離開主機**，平板也不必接電腦。

### N-19 外殼 repo 的部署金鑰與 clone

對應：Y-02

外殼 App 在另一個 repo（`hd-kiosk-shell`），要**另一把**部署金鑰——一把部署金鑰只能給一個 repo。

**做什麼**

1. 產生並交出公鑰，登記到**外殼 repo** 的 Settings → Deploy keys，不勾 Allow write access：

   ```powershell
   ssh-keygen -t ed25519 -C "hd-kiosk-shell@$(hostname)" -f $HOME\.ssh\hd-kiosk-shell -N '""'
   Get-Content $HOME\.ssh\hd-kiosk-shell.pub
   ```

2. `notepad $HOME\.ssh\config`（N-09 已經建好這個檔，直接開就好），在最後再加一段：

   ```
   Host github-hd-kiosk-shell
       HostName github.com
       User git
       IdentityFile ~/.ssh/hd-kiosk-shell
       IdentitiesOnly yes
   ```

3. 確認並 clone（**不必切 tag**，`shell-builder` 會自己取出要的那一版）：

   ```powershell
   ssh -T github-hd-kiosk-shell
   git clone git@github-hd-kiosk-shell:94sh09sh19sh/hd-kiosk-shell.git $root\hd-kiosk-shell
   git -C $root\hd-kiosk-shell tag
   ```

**怎麼知道成功了**：`ssh -T` 印出 `Hi 94sh09sh19sh/hd-kiosk-shell!…`（**是 `hd-kiosk-shell`，不是 `hd-tablet-care`**）；`git tag` 列得出 N-03 看到的那一版。`git tag` 會把外殼 repo 的**每一個** tag 都列出來，連以前的版本也在（例如 `v0.2.0`、`v0.3.0` 兩行）——**這是對的**，`shell-builder` 只取 `shell.pin` 釘住的那一個，其他的用不到。

| 症狀 | 處置 |
|---|---|
| `ssh -T` 印出的是 `hd-tablet-care` | 設定檔兩段的 `IdentityFile` 寫反，或少了 `IdentitiesOnly yes` |
| `Permission denied (publickey)` | 公鑰登記到本系統的 repo 去了 |
| `ssh -T` 成功，`git clone` 卻出現 `Connection reset by … port 22` | 網路把連線切斷，不是金鑰的問題。`Test-Path $root\hd-kiosk-shell` 是 `True` 就先刪掉殘留的資料夾，再重跑 clone；還是被切，就把設定檔這一段的 `HostName` 改成 `ssh.github.com`、加一行 `Port 443`，重跑 `ssh -T` 再 clone（見[《從零部署本系統之一：容器路線的原冊》](ref-fresh-install-detail.md)） |

🧪 與 N-09 相同，開發機上另產生一把、標題註明模擬部署。

---

### N-20 建 `shell-builder` 的映像檔

對應：Y-04

**做什麼**

```powershell
docker compose --env-file $cfg --profile shell build shell-builder
```

第一次要下載 Android SDK 與 Gradle，約 1.5 GB。**這一步要連外，而且可能很久**（開發機上實測過單一個檔案下載 6.6 分鐘；1001 院內含出錯與重來共 27～33 分鐘）。

**怎麼知道成功了**：最後幾行有「✓ 外殼 v0.x.x（…，契約第 1 版）已準備好，相依已下載」（`v0.x.x` 是 `shell.pin` 釘的那一版，1001 是 `v0.3.0`）。

| 症狀 | 處置 |
|---|---|
| `外殼 repo 的 clone 裡沒有 tag vX.Y.Z` | `git -C $root\hd-kiosk-shell fetch --tags`，再建一次 |
| 提到版本、契約版本不符，或「外殼原始碼裡有指向院外的網址」 | **開發端的問題，不在現場修。** 停手，回開發端 |
| `dl.google.com`、`services.gradle.org`、`maven.google.com` 逾時 | 對外連線被擋，請資訊室開通（Q-32） |
| `failed to resolve source metadata for docker.io/library/eclipse-temurin`，後面有 `lookup production.cloudfront.docker.com: no such host` | 下載基底映像時查不到 Docker Hub 的下載站（DNS）。依序：① 再打一次同一條；② `Resolve-DnsName production.cloudfront.docker.com`，查得到就重新啟動 Docker Desktop 再建；③ 主機也查不到，就試 `Resolve-DnsName production.cloudfront.docker.com -Server 8.8.8.8`，這樣查得到表示院內 DNS 解析不了這個網域，請資訊室處理。只想測這一段，可以單獨打 `docker pull eclipse-temurin:17-jdk-jammy` |
| 停在 `gradle.zip` 很久 | 它會自己重試、失敗會自己結束。結束後再打一次同一條，已完成的部分不會重下載 |

---

### N-21 建 APK（第一次會產生金鑰）

對應：Y-05

**做什麼**

```powershell
docker compose --env-file $cfg --profile shell run --rm shell-builder
```

**怎麼知道成功了**：第一次會印出「這一次新產生：院內 CA 伺服器憑證（<主機>） APK 簽章金鑰（…）」，接著是 APK 檔名與**三個 SHA-256**（檔案、簽章憑證、院內 CA）。**把三個 SHA-256 抄下來**，🏥 要寫進交接文件。

**再打一次同一條指令**，這次要看到「**金鑰全部沿用，這一次沒有產生任何新的金鑰**」，而且簽章憑證的 SHA-256 與第一次相同。

💡 **沒抄到也查得到，不必重跑。** 瀏覽器開 `http://localhost:<病人端埠>/shell/`，下載頁最下面「版本資訊」列著三個 SHA-256（同一個資料夾的 `shell.json` 也有）；`patient-web` 有在跑就開得到，不必等 N-23。每跑一次建置，下載頁上的 APK 就會換成新的一份，所以**交接文件的檔案 SHA-256 以下載頁上的為準**。`shell-builder keys-info` 只列得出院內 CA 與簽章金鑰的指紋，而且是大寫、以冒號分隔，對照時去掉冒號、大小寫不計。

| 症狀 | 處置 |
|---|---|
| `MDM_KIOSK_BASE_URL 要以 https:// 開頭` | `.env` 改成 `https://`，見[《之七》](visit-2-system-env.md) |
| `這個金鑰資料卷是「dev」用的，設定卻是「hospital」` | **停手。** 院內主機上出現了開發用的金鑰，或 `.env` 抄了開發機那一份 |
| `有 CA 憑證卻沒有私鑰` 之類 | 資料卷不完整。**不要刪掉重來**，照[《平板與外殼 App》](ref-tablet.md)的金鑰還原，從備份還原 |

🧪 第一次那行會寫「APK 簽章金鑰（開發用）」，是對的。

---

### N-22 備份金鑰，並核對還原得回來

對應：Y-06

**做什麼**

```powershell
docker compose --env-file $cfg --profile shell run --rm shell-builder keys-backup
docker compose --env-file $cfg --profile shell run --rm shell-builder keys-verify
```

**怎麼知道成功了**：第一條印出「已備份：備份目錄/keys/hd-keys-<時間>.tar.gz」；第二條每一項都 ✓，最後「還原得回來」。

> ⚠️ **這份檔案裡有私鑰。** 🏥 與資料庫備份一樣由院方送往院內另一台機器，**不得出院、不得寄給開發端**。金鑰遺失的後果是**每一台平板都要解除安裝重裝**。

---

### N-23 讓病人端改走 HTTPS

對應：Y-07

**做什麼**

```powershell
docker compose --env-file $cfg restart patient-web
docker compose --env-file $cfg logs patient-web --tail 5
```

**怎麼知道成功了**：日誌有「（HTTPS；HTTP 只留外殼下載頁）」。主機的瀏覽器開 `http://localhost:<病人端埠>/shell/` 看得到下載頁；開 `http://localhost:<病人端埠>/` 會被轉到 `https://` 並跳出憑證警告——

**這是對的**：主機的瀏覽器不認得院內 CA，只有平板上的外殼 App 認得。

日誌裡兩個常讓人愣一下的地方，**都是正常的**：

- **「找不到伺服器憑證」和「HTTPS」同時出現**：`--tail 5` 取最後 5 行，常常跨到重新啟動**之前**那一次的輸出。以**最後一次**出現的「靜態資源已提供於連接埠…」那一行為準。
- **寫的是 `8081` 和 `http://api:3000`，不是 `18081`、`13000`**：這兩個是**容器裡面**的埠。主機的 `<病人端埠>` 轉進容器的 8081；`api:3000` 是 `patient-web` 經容器之間的網路找 API 的位址，不經過主機。瀏覽器和平板一律連 `<病人端埠>`。

| 症狀 | 處置 |
|---|---|
| **最後一次**啟動的日誌是「找不到伺服器憑證…暫以 HTTP 提供」 | N-21 還沒成功，或做完沒重新啟動 `patient-web` |

---

### N-24 平板連得到主機

對應：Y-08

**做什麼**：拿一台平板（或手機）連上**與平板實際使用時相同的 Wi-Fi**，用瀏覽器開 `http://<平板要連的位址>:<病人端埠>/shell/`。

**怎麼知道成功了**：看得到下載頁。

| 症狀 | 處置 |
|---|---|
| 主機自己開得到，平板開不到 | Windows 防火牆擋了連入，或那個 Wi-Fi 網段到不了主機。**找資訊室**，不要自己關防火牆 |

🧪 手機和開發機要連**同一個 Wi-Fi**，位址是開發機的區網 IP（[《之七》](visit-2-system-env.md)教你查）。手機開不到時：

1. Windows「設定 → 網路和網際網路 → Wi-Fi → 這個網路的內容」，網路設定檔類型改成**私人**。
2. 仍不行的話，用**系統管理員身分**開 PowerShell，只對私人網路開放病人端那一個埠（N-31 撤除時記得刪掉這條規則）：

   ```powershell
   New-NetFirewallRule -DisplayName "hd-sim patient 18081" -Direction Inbound -Protocol TCP -LocalPort 18081 -Profile Private -Action Allow
   ```

3. 學校或公司的 Wi-Fi 常常擋裝置互連，改用手機熱點或家裡的 Wi-Fi。

---

### N-25 在護理端註冊平板

對應：Y-09

**做什麼**：護理端 → **新增裝置**（1007 以前叫裝置管理）→ **註冊新平板**。畫面會出現一個**佈建 QR code** 與一行文字網址。

> ⚠️ **這兩樣只顯示一次。** 這個畫面先不要關，拿著平板做完 N-26、N-27 再離開。

**怎麼知道成功了**：畫面上的網址以 `https://` 開頭。不是的話，`.env` 的 `MDM_KIOSK_BASE_URL` 還是 `http://`，改好後 `up -d api` 再重新註冊。

---

### N-26 平板的系統設定並安裝 App

對應：Y-10、Y-11

**做什麼**

1. 平板設定裝置 PIN，關閉「新增使用者」。
2. 設定 → 安全性 → **螢幕固定**：開啟，並勾選「解除固定前要求 PIN」。（各廠牌位置略有不同，可在設定裡搜尋「固定」）
3. 平板的瀏覽器開 `http://<平板要連的位址>:<病人端埠>/shell/`，按「下載 App」，安裝。系統問是否允許瀏覽器安裝不明來源的應用程式時，允許。

**怎麼知道成功了**：平板上多了「透析照護平板」這個 App。

| 症狀 | 處置 |
|---|---|
| 「套件與現有套件衝突」 | 這台裝過**另一把金鑰簽的版本**（例如模擬部署時裝的開發版）。先解除安裝再裝 |
| 「應用程式未安裝」，而且沒裝過 | 下載不完整，重新下載一次 |

---

### N-27 第一次開啟並釘住

對應：Y-12、Y-13

**做什麼**

1. 開啟「透析照護平板」→ 按「**掃描 QR code**」→ 允許相機 → 對準 N-25 畫面上的 QR code。三欄會自動填好，**核對序號與這台平板的標籤一致**。（沒有相機時手動填：主機位址填 `MDM_KIOSK_BASE_URL` 的值，序號與金鑰照 N-25 畫面上的）
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

**把序號與床號的對應記下來。** 🏥 首波只佈建實際會用到的兩三台（DEP-36），每台做一次 N-25～N-27。

| 症狀 | 處置 |
|---|---|
| 「主機位址不是 https:// 開頭」 | 回 N-25 的處置 |
| 一片空白或「網頁無法使用」 | 位址錯或 N-23 沒做。平板「設定 → 應用程式 → 透析照護平板 → 儲存空間 → 清除資料」，重新佈建 |
| 上方出現琥珀色「……版本不相容」 | 下載頁的 APK 與系統版本對不上，見[《平板與外殼 App》](ref-tablet.md)的版本相容 |

🧪 用開發用的 Android 手機代替平板。做完之後手機上的 App 要**解除安裝**，免得日後拿這支手機裝院內版時衝突（N-26 出錯表的第一列）。

---

上一份：[《第二次進院（1001）· 從零部署本系統之三：詳細版（N-13～N-18）》](visit-2-system-detail-3.md)｜下一份：[《第二次進院（1001）· 從零部署本系統之五：詳細版（N-28～N-31、日常、停手條件、編號對照）》](visit-2-system-detail-5.md)

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|
| 1118 | 2026-11-18 | 首次定版。1118 照每份約 300 行的上限由《第二次進院（1001）· 從零部署本系統之一：詳細版》拆出，內容與步驟編號不動 |

[← 回部署手冊目錄](index.md)
