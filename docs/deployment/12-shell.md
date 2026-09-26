# 第十二冊 · 外殼 App：主機上建 APK、平板從下載頁安裝

版本：v0.1　文件狀態：草案（0927 新增，迭代 12）　編號：`Y-xx`　**與第十一冊一起印出來帶進去**

> **這一冊接在第十一冊 W-18 之後**：系統已經起來，接著在同一台主機上建外殼 APK、讓平板從院內下載頁安裝。
> 取代[第三冊](03-tablet-shell.md)的 K-05、K-06（憑證、keystore、在開發機上編 APK）與側載那一段。
>
> 規則的真本是《[部署規範](../requirements/deployment-spec.md)》第 7、8 章；外殼與系統之間的介面見
> 《[病人端外殼 App 契約](../reference/kiosk-shell-contract.md)》。這一冊只寫手指要按什麼、每一步會怎麼壞。

> ⚠️ **本冊所有指令都在主機的 PowerShell 下，而且都在 `D:\hd-tablet-care\repo` 底下下**（與第十一冊相同）。
> `$cfg` 是第十一冊 W-11 設的 `D:\hd-tablet-care\config\.env`。

---

## 0. 先講結論

### 0.1 這一冊做什麼

| 步驟 | 在哪裡做 | 產生什麼 |
|---|---|---|
| 取外殼原始碼 | 主機：以外殼 repo 的部署金鑰 clone | `D:\hd-tablet-care\hd-kiosk-shell\` |
| 建 APK | 主機：`shell-builder`（一次性容器，**執行時沒有網路**） | 院內 CA、伺服器憑證、簽章金鑰（**只在第一次**）、APK、下載頁 |
| 病人端改走 HTTPS | 主機：重新啟動 `patient-web` | 病人端以院內 CA 簽的伺服器憑證提供 HTTPS |
| 裝到平板 | 平板：瀏覽器開院內下載頁 | 平板上的「透析照護平板」 |

**私鑰全程不離開主機**：CA 與簽章金鑰在 `shell-builder` 裡產生、存在資料卷 `hd-tablet-care-keys`，
備份時寫到備份目錄、隨資料庫備份一起送往院內另一台機器（DEP-35）。

### 0.2 東西放在哪裡（第十一冊 0.2 之外多出來的）

| 東西 | 位置 | 為什麼 |
|---|---|---|
| 外殼原始碼 | `D:\hd-tablet-care\hd-kiosk-shell\`（`git clone` 下來的，**不必切 tag**） | `shell-builder` 自己從這份 clone 取出本系統釘住的那一版（`services\shell-builder\shell.pin`） |
| 院內 CA、伺服器憑證、簽章金鑰、下載頁 | 資料卷 `hd-tablet-care-keys` | 私鑰不離開主機；病人端靜態服務唯讀掛它，只讀得到伺服器憑證與下載頁 |
| 金鑰備份 | `D:\hd-tablet-care\backups\keys\` | **裡面有私鑰**，與資料庫備份一樣送往院內另一台機器，不得出院 |

### 0.3 開發機實測結果（0927）

見《[部署演練紀錄](../notes/deployment-drills.md)》第 9 節。

### 0.4 先接受的一件事

**平板第一次下載 APK 走的是 HTTP。** 那時平板還不信任院內 CA，下載頁若只有 HTTPS，平板的瀏覽器會先跳一個
「連線不是私人連線」給拿平板的人看。因此病人端的埠同時接 HTTP 與 HTTPS，**HTTP 只留下載頁**，其餘一律轉到 HTTPS。
下載頁上列出 APK 與簽章憑證的 SHA-256，要核對可以對照 Y-05 的輸出；Android 本身也會擋下簽章不同的覆蓋安裝。

---

## 1. 進院前（在開發端做完）

### Y-01 核對要交的 tag 釘的是哪一版外殼

在開發端，要交的那個 tag 底下：

```powershell
git show <tag>:services/shell-builder/shell.pin
```

**怎麼知道成功了**：`SHELL_TAG` 那一版外殼在 GitHub 的外殼 repo 上看得到（Tags 頁），`SHELL_CONTRACT_VERSION` 等於契約文件的版本。
兩者都已在開發機上照本冊第 7 節走過一次。

| 症狀 | 處置 |
|---|---|
| 外殼 repo 上沒有那個 tag | 外殼的 tag 沒推。推上去再進院——主機上 `git fetch --tags` 拿不到的 tag，`shell-builder` 就建不了 |

---

## 2. 主機這一層

### Y-02 外殼 repo 的部署金鑰與 clone（DEP-43）

**一把部署金鑰只能對應一個 repo**，外殼 repo 另產生一把。做法與第十一冊 W-09 相同，只是名稱不同：

```powershell
ssh-keygen -t ed25519 -C "hd-kiosk-shell@<主機名稱>" -f $HOME\.ssh\hd-kiosk-shell -N '""'
Get-Content $HOME\.ssh\hd-kiosk-shell.pub
```

把印出來的那一行交給 repo 管理者，登記到**外殼 repo**（`hd-kiosk-shell`）的 **Settings → Deploy keys**，**不要勾 Allow write access**。
`$HOME\.ssh\config` 再加一段：

```
Host github-hd-kiosk-shell
    HostName github.com
    User git
    IdentityFile ~/.ssh/hd-kiosk-shell
    IdentitiesOnly yes
```

然後 clone（**不必 checkout tag**）：

```powershell
ssh -T github-hd-kiosk-shell
git clone git@github-hd-kiosk-shell:94sh09sh19sh/hd-kiosk-shell.git D:\hd-tablet-care\hd-kiosk-shell
git -C D:\hd-tablet-care\hd-kiosk-shell tag
```

**怎麼知道成功了**：`ssh -T` 印出 `Hi <帳號>/hd-kiosk-shell!…`；`git tag` 列得出 Y-01 的那一版。

| 症狀 | 處置 |
|---|---|
| `ssh -T` 印出的是 `hd-tablet-care` 而不是 `hd-kiosk-shell` | `config` 裡兩段的 `IdentityFile` 寫反，或少了 `IdentitiesOnly yes` |
| `Permission denied (publickey)` | 公鑰登記到本系統的 repo 去了。一把金鑰只能給一個 repo |

---

### Y-03 `.env` 補三項

```powershell
notepad $cfg
```

| 變數 | 填什麼 |
|---|---|
| `HD_SHELL_SRC_DIR` | `D:\hd-tablet-care\hd-kiosk-shell` |
| `HD_SHELL_SIGNING` | 院內主機填 `hospital`（範本預設就是）；開發機實測填 `dev` |
| `MDM_KIOSK_BASE_URL` | **`https://`**`<平板要連的主機名稱或 IP>:<病人端埠>`。伺服器憑證就簽這個名字，**擇一之後不要再換** |

`KIOSK_SHELL_MIN_VERSION` 先留白（用程式內建的預設值）。

**怎麼知道成功了**：`docker compose --env-file $cfg config --quiet` 沒有輸出。

| 症狀 | 處置 |
|---|---|
| `required variable HD_SHELL_SRC_DIR is missing a value` | **每一條 compose 指令都會檢查它**，不只 `shell-builder` 那幾條。填上 |

> `MDM_KIOSK_BASE_URL` 從 `http://` 改成 `https://` 之後，護理端註冊平板時顯示的網址也跟著變。
> 它只寫在 `api` 的環境變數裡，**不必重建映像檔**，`docker compose --env-file $cfg up -d api` 即可。

---

## 3. 建置

### Y-04 建置 `shell-builder` 的映像檔

```powershell
docker compose --env-file $cfg --profile shell build shell-builder
```

第一次要下載 Android SDK、Gradle 與外殼的全部建置相依（約 1.5 GB）。**這一步可以連外、而且必須連外**；
它不掛任何資料卷（DEP-14）。建置時會核對：外殼 clone 裡有沒有釘住的 tag、tag 裡的版本與契約版本對不對、
外殼原始碼裡有沒有指向院外的網址。

**怎麼知道成功了**：輸出最後幾行有「✓ 外殼 v0.2.0（…，契約第 1 版）已準備好，相依已下載」。

| 症狀 | 處置 |
|---|---|
| `外殼 repo 的 clone 裡沒有 tag vX.Y.Z` | `git -C D:\hd-tablet-care\hd-kiosk-shell fetch --tags`，再建一次 |
| `tag … 裡的 gradle.properties 宣告的版本是 …，兩者要相同` | 外殼那一版的 tag 打錯了。**開發端的問題**，不在現場修 |
| `外殼 … 實作契約第 N 版，本系統 shell.pin 要的是第 M 版` | 本系統與外殼的版本沒配對。回開發端，不在現場修 |
| `外殼原始碼裡有指向院外的網址` | 同上。這是刻意擋的（FR-S07） |
| 下載 `dl.google.com`、`services.gradle.org`、`maven.google.com` 逾時 | 對外連線被擋。回第十一冊 W-06；外殼建置要連的網域完整清單在 Q-32 |
| 停在 `gradle.zip` 那一步很久沒有進度 | 網路太慢或連線卡住。Dockerfile 已設「60 秒內低於 1 KB/s 就中斷並重試五次」，失敗會自己結束；再跑一次 Y-04，已完成的層不會重下載 |

---

### Y-05 建 APK（第一次會產生金鑰）

```powershell
docker compose --env-file $cfg --profile shell run --rm shell-builder
```

**怎麼知道成功了**：第一次執行印出「這一次新產生：院內 CA 伺服器憑證（<主機>） APK 簽章金鑰（院內）」，
接著是 APK 檔名與三個 SHA-256（檔案、簽章憑證、院內 CA）。**把三個 SHA-256 抄進交接文件。**

**再執行一次**，要看到「**金鑰全部沿用，這一次沒有產生任何新的金鑰**」，簽章憑證的 SHA-256 與第一次相同。
這是 DEP-35 的核心：`shell-builder` 絕不覆蓋既有的 CA 與簽章金鑰。

| 症狀 | 處置 |
|---|---|
| `HD_SHELL_SIGNING 要填 dev（開發機）或 hospital（院內主機）` | Y-03 沒填 |
| `這個金鑰資料卷是「dev」用的，設定卻是「hospital」` | **資料卷是開發機那一份**，或 `.env` 抄了開發機的。**停手**：院內主機不該有開發用的金鑰 |
| `MDM_KIOSK_BASE_URL 要以 https:// 開頭` | Y-03 |
| `有 CA 憑證卻沒有私鑰`、`有簽章金鑰卻沒有它的密碼檔` | 資料卷不完整。**不要刪掉重來**——那等於換 CA、換簽章金鑰，所有平板都要重裝。從 Y-06 的備份還原，見第 6 節 |

---

### Y-06 備份金鑰，並核對還原得回來（DEP-35）

```powershell
docker compose --env-file $cfg --profile shell run --rm shell-builder keys-backup
docker compose --env-file $cfg --profile shell run --rm shell-builder keys-verify
```

**怎麼知道成功了**：第一條印出「已備份：備份目錄/keys/hd-keys-<時間>.tar.gz」；第二條逐項 ✓，最後「還原得回來」。
`D:\hd-tablet-care\backups\keys\` 底下看得到那份檔案。

**這份檔案裡有 CA 與簽章的私鑰。** 與資料庫備份一樣由院方送往院內另一台機器，不得出院、不得寄給開發端。
送過去之後，在那一台上也要能取回——每年核對一次（第 6 節）。

---

### Y-07 讓病人端改走 HTTPS

```powershell
docker compose --env-file $cfg restart patient-web
docker compose --env-file $cfg logs patient-web --tail 5
```

**怎麼知道成功了**：記錄裡有「靜態資源已提供於連接埠 8081（HTTPS；HTTP 只留外殼下載頁）」。
主機的瀏覽器開 `http://<主機>:<病人端埠>/shell/` 看得到下載頁；開 `http://<主機>:<病人端埠>/` 會被轉到 `https://`
並跳出憑證警告——**這是對的**，主機的瀏覽器不信任院內 CA，平板上的外殼才信任。

| 症狀 | 處置 |
|---|---|
| 記錄是「找不到伺服器憑證…暫以 HTTP 提供」 | Y-05 還沒跑成功，或跑完沒有重新啟動 `patient-web` |
| 下載頁顯示「外殼 App 尚未建置」 | 同上 |

> **伺服器憑證換過之後也要做這一步**：`shell-builder` 發現主機位址變了、或憑證 30 天內到期時會重新簽一張，
> `patient-web` 要重新啟動才讀得到。CA 沒變，平板不受影響。

---

### Y-08 平板連得進來

平板與主機之間要能連到病人端的埠。在主機上：

```powershell
Get-NetFirewallRule -Direction Inbound -Enabled True | Where-Object DisplayName -like "*Docker*" | Select-Object DisplayName, Profile
```

**怎麼知道成功了**：拿一台平板（或手機）連院內 Wi-Fi，瀏覽器開 `http://<主機>:<病人端埠>/shell/` 看得到下載頁。

| 症狀 | 處置 |
|---|---|
| 主機自己開得到，平板開不到 | Windows 防火牆擋了連入，或平板那個 Wi-Fi 網段到不了主機。**找資訊室**（Q-27），不要自己關防火牆 |

---

## 4. 平板（每台各做一次）

照《部署規範》8.2。**首波只佈建實際會用到的兩三台**（DEP-36）。

### Y-09 在護理端註冊平板

護理端 → 裝置管理 → 註冊新平板。**金鑰只顯示一次**，抄在佈建單上，佈建完就銷毀那張單子。
顯示的網址要以 `https://` 開頭；不是的話回 Y-03。

### Y-10 平板的系統設定

1. 設定裝置 PIN，關閉「新增使用者」
2. 設定 → 安全性 → 螢幕固定：開啟，勾選「解除固定前要求 PIN」
3. 允許瀏覽器安裝不明來源的應用程式（安裝時系統會問）

### Y-11 從下載頁安裝

平板的瀏覽器開 `http://<主機>:<病人端埠>/shell/`，按「下載 App」，安裝。

| 症狀 | 處置 |
|---|---|
| 「應用程式未安裝」「套件與現有套件衝突」 | 這台平板裝過**另一把金鑰簽的版本**（例如開發用的）。先解除安裝再裝 |
| 「應用程式未安裝」，而且沒裝過 | 版本往下覆蓋，或下載不完整。重新下載一次 |

### Y-12 首次啟動與釘選

1. 開啟「透析照護平板」，主機位址填 `https://<主機>:<病人端埠>`（與 `MDM_KIOSK_BASE_URL` 相同），序號與金鑰填 Y-09 的
2. 按「儲存並啟動」，系統跳出「要固定這個應用程式嗎」，按「確定」

**怎麼知道成功了**：畫面是病人端的等待畫面，沒有任何憑證警告；按上一頁、首頁、多工鍵都離不開。

| 症狀 | 處置 |
|---|---|
| 「主機位址要以 https:// 開頭」 | 照填 |
| 一片空白或「網頁無法使用」 | 位址打錯、或 Y-07 沒做。到系統設定 → 應用程式 → 透析照護平板 → 儲存空間 → **清除資料**，重新填 |
| 畫面上方出現琥珀色提示列「……版本不相容」 | 下載頁上的 APK 與系統的契約版本對不上。見第 5 節 |

### Y-13 核對護理端

護理端 → 裝置管理，15～30 秒內：

| 欄位 | 應該是 |
|---|---|
| 固定狀態 | 固定中 |
| 外殼版本 | 版本正常，底下一行版本號 |

把序號與床號的對應記下來。**解除一次固定**（輸入 PIN），30 秒內護理端要變成「已跳出」；再開啟 App 釘回去。

---

## 5. 換外殼版本、調高最低可用版本

### Y-14 換外殼版本（改 APK 的時候）

外殼改版是**開發端**的事：外殼 repo 打新 tag，本系統的 `shell.pin` 改成它，本系統打新 tag。主機上：

```powershell
git -C D:\hd-tablet-care\hd-kiosk-shell fetch --tags
# 本系統照第十一冊 W-19 更新到新 tag（shell.pin 跟著換）
docker compose --env-file $cfg --profile shell build shell-builder
docker compose --env-file $cfg --profile shell run --rm shell-builder
```

下載頁換成新版之後，**平板要逐台重新安裝**（覆蓋安裝即可，序號與金鑰會留著）。排在非透析時段（DEP-32）。
**只改網頁不必做這一段**——那是絕大多數的更新，平板下次載入就是新版。

### Y-15 調高最低可用版本

所有平板都換上新版之後，把舊版標成「外殼過舊」，下次有人沒換到就看得出來：

```powershell
notepad $cfg          # KIOSK_SHELL_MIN_VERSION=<新版本>
docker compose --env-file $cfg up -d api
```

**不必重建映像檔。** 護理端裝置管理 15 秒內就會標出版本低於它的平板。

---

## 6. 金鑰：每年一次，以及遺失時

| 什麼時候 | 做什麼 |
|---|---|
| 每年 | `keys-verify <那一份備份的檔名>`，對院內另一台機器上取回的那一份做（DEP-35） |
| 伺服器憑證快到期（825 天） | 直接再跑 Y-05，它會自己重新簽，然後 Y-07 |
| 金鑰資料卷壞了或被刪了 | **不要重新產生**。`docker volume create hd-tablet-care-keys` 建一個空的，再 `… run --rm shell-builder keys-restore hd-keys-<時間>.tar.gz`（只准還原到沒有金鑰的資料卷，還原完自動核對），然後 Y-05、Y-07 |
| 備份也沒了 | CA 與簽章金鑰都補不回來：重新產生、**每一台平板解除安裝後重裝**。這就是 DEP-35 說的「遺失即無法補救」 |

---

## 7. 開發機實測（DEP-22）

照第十一冊第 7 節那一輪，加上本冊：

| # | 驗什麼 | 本冊步驟 |
|---|---|---|
| 1 | `shell-builder` 從零建出 APK，第二次不重新產生金鑰 | Y-04～Y-05 |
| 2 | 金鑰備份並核對 | Y-06 |
| 3 | 開發手機從下載頁安裝、輸入序號與金鑰、釘住 | Y-09～Y-12 |
| 4 | 手機跳出螢幕固定，護理端 30 秒內看得到 | Y-13 |
| 5 | `npm run verify:iteration12 -- --live --env-file <設定目錄>\.env` | 唯一允許用 Node 的一步，**它是驗收，不是部署步驟** |

開發機上 `HD_SHELL_SIGNING=dev`、`MDM_KIOSK_BASE_URL` 用開發機的區網 IP（手機要連得到，`localhost` 不行）。
手機上的每一項見[迭代 12 測試分冊](../testing/iteration-12.md) §12.5～§12.7。

---

## 8. 疑難排解（這一冊特有的）

| 症狀 | 原因 | 處置 |
|---|---|---|
| `shell-builder` 建置很久停在 `gradle` 或 `sdkmanager` | 第一次要下載約 1.5 GB | 等。之後改版只重跑外殼那幾層，快很多 |
| 平板顯示「網頁無法使用」，主機的瀏覽器開得了 | 平板連不到主機，或 `MDM_KIOSK_BASE_URL` 是 `localhost` | Y-08；位址改成平板連得到的那一個，重跑 Y-05（憑證會重新簽）與 Y-07，平板清除資料重新佈建 |
| 平板上病人端載入了，但按求助沒反應 | `/api/` 轉送不通 | `docker compose --env-file $cfg logs patient-web`，看有沒有「/api/ 轉送至 http://api:3000」；`api` 有沒有在跑 |
| 護理端「外殼版本」一直是「未回報版本」 | 平板上裝的是迭代 12 之前的外殼，或用瀏覽器開的 | 從下載頁重裝 |
| 護理端「版本不相容」 | 平板的外殼與系統的契約版本不同 | 從下載頁重裝目前這一版 |

---

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|

[← 回部署手冊總覽](index.md)
