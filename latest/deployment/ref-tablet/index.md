# 平板與外殼 App

> **狀態：現行**（常備參考）。
>
> 1117 從三份舊冊改寫：《外殼 App：主機上建 APK、平板從下載頁安裝》全部（`Y-xx`）；《平板與外殼 App》仍有效的部分（平板盤點與採購、到貨後每台要做的、平板還沒到怎麼辦、交給護理師的每日一頁、守不住什麼，`K-xx`）；《本系統換版上線（詳細版）》附錄四（平板要重新佈建時）。舊《平板與外殼 App》已被外殼路線取代的部分（主機位址 K-01、憑證 K-02～K-03、編譯環境 K-04、自編 APK 與 keystore K-05～K-06、模擬器 K-07、交付單 K-09、側載 K-12）在[《安裝包路線（歷史）》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-installer/index.md)。
>
> 編號：`Y-xx`（外殼 App 與平板佈建）、`K-xx`（平板盤點、採購與到貨後），都沿用原編號。

## 摘要

- 院內現況（1116）：外殼 `v0.3.0`（`services/shell-builder/shell.pin` 釘的，契約第 1 版）；APK 與金鑰 1001 在院內主機上建好；暫用平板 1 台（Galaxy Tab S6 Lite，序號 `TB-00`）1029 佈建、1116 帶回，**已註冊、固定中，放在醫師桌上，還沒指派病人**（第 0.1 節）
- 外殼 APK 在院內主機上由一次性容器 `shell-builder` 離線建置與簽章，平板從病人端的院內下載頁安裝；私鑰全程不離開主機（第 0.2、0.3 節）
- 主機這一層：外殼 repo 的部署金鑰與 clone、`.env` 三項、建映像檔、建 APK、備份金鑰、病人端改走 HTTPS、平板連得進來（Y-01～Y-08）
- 讀之前：院內現況、這一份做什麼、東西放在哪、開工三行、先接受的一件事、0927 開發機實測結果（第 0 節）
- 與《從零部署本系統》的對應：Y-02～Y-13 ＝ V-20～V-28（[《從零部署本系統》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fresh-install/index.md)）；1029 現場照做的版本是 J-27～J-29（[《第三次進院之五：詳細版》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-3-system-detail-5/index.md)）

規則的真本是《[部署規範](https://94sh09sh19sh.github.io/hd-docs/latest/requirements/deployment-spec/index.md)》第 7、8 章；外殼與系統之間的介面見《[病人端外殼 App 契約](https://94sh09sh19sh.github.io/hd-docs/latest/reference/kiosk-shell-contract/index.md)》。這一份只寫手指要按什麼、每一步會怎麼壞。

## 分份

| 份                                                                                                                          | 節                                                                                         | 步驟             |
| --------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ | ---------------- |
| 《平板與外殼 App》（這一份）                                                                                                | 第 0～3 節：讀之前、進院前、主機這一層、建置                                               | Y-01～Y-08       |
| [《平板與外殼 App（第 2 份，Y-09～Y-15）》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-tablet-2/index.md) | 第 4～9 節：平板每台一次、重新佈建、換外殼版本與最低可用版本、金鑰、開發機實測、疑難排解   | Y-09～Y-15       |
| [《平板與外殼 App（第 3 份，K-08～K-16）》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-tablet-3/index.md) | 第 10～15 節：盤點與採購規格、到貨之後、平板還沒到、交給護理師的一頁、守不住什麼、完成條件 | K-08、K-10～K-16 |

______________________________________________________________________

## 0. 讀之前

### 0.1 院內現況（1116）

| 哪一樣         | 現況                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 外殼版本       | `v0.3.0`（迭代 14.1：佈建畫面可掃 QR code）。本系統 `v0.5.0` 的 `shell.pin` 仍是 `SHELL_TAG=v0.3.0`、`SHELL_CONTRACT_VERSION=1`；1018 迭代 27 起外殼本來就鎖橫向，**換版不必重建 APK、已裝的平板不必重裝**。版本以 `services/shell-builder/shell.pin` 為準                                                                                                                                                                                                              |
| APK 與金鑰     | 1001 在院內主機上第一次建（Y-04～Y-06），金鑰備份已核對還原得回來；1029 主機位址由名稱換成 IP，伺服器憑證跟著重簽、金鑰重新備份（[《護理站登不進去與主機位址》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-login/index.md)）                                                                                                                                                                                                                          |
| 位址（🏥）     | 平板連 `https://<IP>:18081`；下載頁 `http://<IP>:18081/shell/`；護理站 `http://<IP>:18080`（實際 IP 只在私人紀錄）                                                                                                                                                                                                                                                                                                                                                      |
| 平板           | 醫院採購的 15 台還沒到；先用醫師給的一台舊平板 Galaxy Tab S6 Lite（SM-P613，Android 13，One UI 5.1.1），**使用者更新前正式使用只有這一台**（《[暫用平板](https://94sh09sh19sh.github.io/hd-docs/latest/notes/interim-tablet/index.md)》）                                                                                                                                                                                                                               |
| `TB-00` 的經過 | 1029 佈建完成（等待畫面正常、沒有憑證警告、固定中；解除固定後「已跳出」，釘回去約 11 秒回到「固定中」；字型大小照醫師的答覆維持 1.1），離院時帶走、沒有床號（[《第三次進院紀錄》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/record-3-1029/index.md) O-11）；1116 帶回，**已註冊、固定中，放在醫師桌上，還沒指派給病人**（畫面是等待畫面）（[《第五次進院紀錄》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/record-5-1116/index.md) SR-10） |
| 下一步         | 醫師、護理長把平板放到首波病人的床、在護理端指派（[《第五次進院任務二》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-5-system-2/index.md) SY-12），**不需要開發端在場**；首波病人只有醫師與護理師知道。「本次透析」面板目前開著，第一次指派時就會出現：先確認那位病人不在目標脫水量被擋下的 3 次裡，或先關掉、SY-12 對過再開（SR-10）                                                                                                                |
| PIN            | 平板 PIN 與管理者密碼目前在開發端，待移交護理長（SR-11 的 SY-08）                                                                                                                                                                                                                                                                                                                                                                                                       |
| 只有一台的影響 | 同時只服務一床、沒有備品，壞了病人端就停；護理端不受影響                                                                                                                                                                                                                                                                                                                                                                                                                |

### 0.2 這一份做什麼

| 步驟             | 在哪裡做                                                | 產生什麼                                                     |
| ---------------- | ------------------------------------------------------- | ------------------------------------------------------------ |
| 取外殼原始碼     | 主機：以外殼 repo 的部署金鑰 clone                      | `$root\hd-kiosk-shell\`                                      |
| 建 APK           | 主機：`shell-builder`（一次性容器，**執行時沒有網路**） | 院內 CA、伺服器憑證、簽章金鑰（**只在第一次**）、APK、下載頁 |
| 病人端改走 HTTPS | 主機：重新啟動 `patient-web`                            | 病人端以院內 CA 簽的伺服器憑證提供 HTTPS                     |
| 裝到平板         | 平板：瀏覽器開院內下載頁                                | 平板上的「透析照護平板」                                     |

**私鑰全程不離開主機**：CA 與簽章金鑰在 `shell-builder` 裡產生、存在資料卷 `hd-tablet-care-keys`，備份時寫到備份目錄、隨資料庫備份一起送往院內另一台機器（DEP-35）。

### 0.3 東西放在哪裡（本系統之外多出來的）

| 東西                                  | 位置                                                          | 為什麼                                                                                        |
| ------------------------------------- | ------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| 外殼原始碼                            | `$root\hd-kiosk-shell\`（`git clone` 下來的，**不必切 tag**） | `shell-builder` 自己從這份 clone 取出本系統釘住的那一版（`services\shell-builder\shell.pin`） |
| 院內 CA、伺服器憑證、簽章金鑰、下載頁 | 資料卷 `hd-tablet-care-keys`                                  | 私鑰不離開主機；病人端靜態服務唯讀掛它，只讀得到伺服器憑證與下載頁                            |
| 金鑰備份                              | `$root\backups\keys\`                                         | **裡面有私鑰**，與資料庫備份一樣送往院內另一台機器，不得出院                                  |

`$root` 🏥 是 `C:\hd\hd-tablet-care`（1001 起；0927 原文寫的 `D:\hd-tablet-care` 沒用上，院內主機的 D 槽空間不夠）；🧪 開發機演練是 `C:\hd-sim`。

### 0.4 開工三行

所有指令都在主機的 PowerShell、`$root\repo` 底下下。每開一個新的 PowerShell 視窗先打（與 [《從零部署本系統》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fresh-install-3/index.md) V-09 相同）：

```
$root = "C:\hd\hd-tablet-care"          # 🧪 開發機演練改成 C:\hd-sim
$cfg  = "$root\config\.env"
cd $root\repo
```

看到 `couldn't find env file`，十次有九次是忘了這三行。

### 0.5 先接受的一件事

**平板第一次下載 APK 走的是 HTTP。** 那時平板還不信任院內 CA，下載頁若只有 HTTPS，平板的瀏覽器會先跳一個「連線不是私人連線」給拿平板的人看。因此病人端的埠同時接 HTTP 與 HTTPS，**HTTP 只留下載頁**，其餘一律轉到 HTTPS。下載頁上列出 APK 與簽章憑證的 SHA-256，要核對可以對照 Y-05 的輸出；Android 本身也會擋下簽章不同的覆蓋安裝。

### 0.6 開發機實測結果（0927）

見《[部署演練紀錄](https://94sh09sh19sh.github.io/hd-docs/latest/notes/deployment-drills/index.md)》第 9 節。

______________________________________________________________________

## 1. 進院前（在開發端做完）

### Y-01 核對要交的 tag 釘的是哪一版外殼

在開發端，要交的那個 tag 底下：

```
git show <tag>:services/shell-builder/shell.pin
```

**怎麼知道成功了**：`SHELL_TAG` 那一版外殼在 GitHub 的外殼 repo 上看得到（Tags 頁），`SHELL_CONTRACT_VERSION` 等於契約文件的版本。兩者都已在開發機上照本份第 8 節走過一次。

| 症狀                     | 處置                                                                                            |
| ------------------------ | ----------------------------------------------------------------------------------------------- |
| 外殼 repo 上沒有那個 tag | 外殼的 tag 沒推。推上去再進院——主機上 `git fetch --tags` 拿不到的 tag，`shell-builder` 就建不了 |

______________________________________________________________________

## 2. 主機這一層

### Y-02 外殼 repo 的部署金鑰與 clone（DEP-43）

**一把部署金鑰只能對應一個 repo**，外殼 repo 另產生一把。做法與本系統 repo 的部署金鑰相同（[《從零部署本系統之二：容器路線的原冊》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fresh-install-detail-2/index.md) W-09），只是名稱不同：

```
ssh-keygen -t ed25519 -C "hd-kiosk-shell@$(hostname)" -f $HOME\.ssh\hd-kiosk-shell -N '""'
Get-Content $HOME\.ssh\hd-kiosk-shell.pub
```

把印出來的那一行交給 repo 管理者，登記到**外殼 repo**（`hd-kiosk-shell`）的 **Settings → Deploy keys**，**不要勾 Allow write access**。 `$HOME\.ssh\config` 再加一段：

```
Host github-hd-kiosk-shell
    HostName github.com
    User git
    IdentityFile ~/.ssh/hd-kiosk-shell
    IdentitiesOnly yes
```

然後 clone（**不必 checkout tag**）：

```
ssh -T github-hd-kiosk-shell
git clone git@github-hd-kiosk-shell:94sh09sh19sh/hd-kiosk-shell.git $root\hd-kiosk-shell
git -C $root\hd-kiosk-shell tag
```

**怎麼知道成功了**：`ssh -T` 印出 `Hi <帳號>/hd-kiosk-shell!…`（**是 `hd-kiosk-shell`，不是 `hd-tablet-care`**）；`git tag` 列得出 Y-01 的那一版。以前的版本也會一起列出來（1001 是 `v0.2.0`、`v0.3.0` 兩行），這是正常的：`shell-builder` 只取 `shell.pin` 釘住的那一個。

| 症狀                                                       | 處置                                                               |
| ---------------------------------------------------------- | ------------------------------------------------------------------ |
| `ssh -T` 印出的是 `hd-tablet-care` 而不是 `hd-kiosk-shell` | `config` 裡兩段的 `IdentityFile` 寫反，或少了 `IdentitiesOnly yes` |
| `Permission denied (publickey)`                            | 公鑰登記到本系統的 repo 去了。一把金鑰只能給一個 repo              |

______________________________________________________________________

### Y-03 `.env` 補三項

```
notepad $cfg
```

| 變數                 | 填什麼                                                                                                                                                                                                                                                                                                 |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `HD_SHELL_SRC_DIR`   | 外殼 clone 的位置：🏥 `C:\hd\hd-tablet-care\hd-kiosk-shell`；🧪 `C:\hd-sim\hd-kiosk-shell`                                                                                                                                                                                                             |
| `HD_SHELL_SIGNING`   | 🏥 院內主機填 `hospital`（範本預設就是）；🧪 開發機演練填 `dev`                                                                                                                                                                                                                                        |
| `MDM_KIOSK_BASE_URL` | **`https://`**`<平板要連的主機名稱或 IP>:<病人端埠>`（🏥 `https://<IP>:18081`；🧪 開發機的區網 IP，手機要連得到，`localhost` 不行）。伺服器憑證就簽這個名字，**擇一之後不要再換**（要換照[《護理站登不進去與主機位址》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-login/index.md)） |

`KIOSK_SHELL_MIN_VERSION` 先留白（用程式內建的預設值）。每一行的完整填法見[《`.env` 怎麼填》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-env/index.md)。

**怎麼知道成功了**：`docker compose --env-file $cfg config --quiet` 沒有輸出。

| 症狀                                                    | 處置                                                                 |
| ------------------------------------------------------- | -------------------------------------------------------------------- |
| `required variable HD_SHELL_SRC_DIR is missing a value` | **每一條 compose 指令都會檢查它**，不只 `shell-builder` 那幾條。填上 |

> `MDM_KIOSK_BASE_URL` 從 `http://` 改成 `https://` 之後，護理端註冊平板時顯示的網址也跟著變。它只寫在 `api` 的環境變數裡，**不必重建映像檔**，`docker compose --env-file $cfg up -d api` 即可。

______________________________________________________________________

## 3. 建置

### Y-04 建置 `shell-builder` 的映像檔

```
docker compose --env-file $cfg --profile shell build shell-builder
```

第一次要下載 Android SDK、Gradle 與外殼的全部建置相依（約 1.5 GB）。**這一步可以連外、而且必須連外**；它不掛任何資料卷（DEP-14）。建置時會核對：外殼 clone 裡有沒有釘住的 tag、tag 裡的版本與契約版本對不對、外殼原始碼裡有沒有指向院外的網址。

**怎麼知道成功了**：輸出最後幾行有「✓ 外殼 v0.x.x（…，契約第 1 版）已準備好，相依已下載」（`v0.x.x` 是 `shell.pin` 釘的那一版，1001 起是 `v0.3.0`）。

| 症狀                                                                                                                                      | 處置                                                                                                                                                                                                                                                                                               |
| ----------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `外殼 repo 的 clone 裡沒有 tag vX.Y.Z`                                                                                                    | `git -C $root\hd-kiosk-shell fetch --tags`，再建一次                                                                                                                                                                                                                                               |
| `tag … 裡的 gradle.properties 宣告的版本是 …，兩者要相同`                                                                                 | 外殼那一版的 tag 打錯了。**開發端的問題**，不在現場修                                                                                                                                                                                                                                              |
| `外殼 … 實作契約第 N 版，本系統 shell.pin 要的是第 M 版`                                                                                  | 本系統與外殼的版本沒配對。回開發端，不在現場修                                                                                                                                                                                                                                                     |
| `外殼原始碼裡有指向院外的網址`                                                                                                            | 同上。這是刻意擋的（FR-S07）                                                                                                                                                                                                                                                                       |
| 下載 `dl.google.com`、`services.gradle.org`、`maven.google.com` 逾時                                                                      | 對外連線被擋。照[《從零部署本系統之一：容器路線的原冊》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fresh-install-detail/index.md) W-06 查；外殼建置要連的網域完整清單在 Q-32（0930 院方答覆：對外連線是常態、沒有限制）                                                         |
| `failed to resolve source metadata for docker.io/library/eclipse-temurin`，後面有 `lookup production.cloudfront.docker.com: no such host` | 下載基底映像時查不到 Docker Hub 的下載站（DNS，1001 院內遇過）。先重跑；`Resolve-DnsName production.cloudfront.docker.com` 查得到就重新啟動 Docker Desktop；主機也查不到、改用 `-Server 8.8.8.8` 才查得到，就是院內 DNS 的問題，找資訊室。單獨測這一段：`docker pull eclipse-temurin:17-jdk-jammy` |
| 停在 `gradle.zip` 那一步很久沒有進度                                                                                                      | 網路太慢或連線卡住。Dockerfile 已設「60 秒內低於 1 KB/s 就中斷並重試五次」，失敗會自己結束；再跑一次 Y-04，已完成的層不會重下載                                                                                                                                                                    |

______________________________________________________________________

### Y-05 建 APK（第一次會產生金鑰）

```
docker compose --env-file $cfg --profile shell run --rm shell-builder
```

**怎麼知道成功了**：第一次執行印出「這一次新產生：院內 CA 伺服器憑證（\<主機>） APK 簽章金鑰（院內）」，接著是 APK 檔名與三個 SHA-256（檔案、簽章憑證、院內 CA）。**把三個 SHA-256 抄進交接文件**（交接紙「外殼」那一列，[《院內主機現況與未完成事項之一：交接紙》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-status-handover/index.md)）。

**再執行一次**，要看到「**金鑰全部沿用，這一次沒有產生任何新的金鑰**」，簽章憑證的 SHA-256 與第一次相同。這是 DEP-35 的核心：`shell-builder` 絕不覆蓋既有的 CA 與簽章金鑰。

沒抄到也查得到，不必重跑：`http://localhost:<病人端埠>/shell/`（🏥 `http://localhost:18081/shell/`）下載頁最下面的「版本資訊」列著三個 SHA-256，同一個資料夾的 `shell.json` 也有； `patient-web` 每次都即時讀檔，不必先做 Y-07。每跑一次建置，APK 就會換成新的一份，**交接文件的檔案 SHA-256 以下載頁上的為準**。 `keys-info` 只列得出院內 CA 與簽章金鑰的指紋，格式是大寫、以冒號分隔，對照時去掉冒號、大小寫不計。

| 症狀                                                         | 處置                                                                                                     |
| ------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------- |
| `HD_SHELL_SIGNING 要填 dev（開發機）或 hospital（院內主機）` | Y-03 沒填                                                                                                |
| `這個金鑰資料卷是「dev」用的，設定卻是「hospital」`          | **資料卷是開發機那一份**，或 `.env` 抄了開發機的。**停手**：院內主機不該有開發用的金鑰                   |
| `MDM_KIOSK_BASE_URL 要以 https:// 開頭`                      | Y-03                                                                                                     |
| `有 CA 憑證卻沒有私鑰`、`有簽章金鑰卻沒有它的密碼檔`         | 資料卷不完整。**不要刪掉重來**——那等於換 CA、換簽章金鑰，所有平板都要重裝。從 Y-06 的備份還原，見第 7 節 |

______________________________________________________________________

### Y-06 備份金鑰，並核對還原得回來（DEP-35）

```
docker compose --env-file $cfg --profile shell run --rm shell-builder keys-backup
docker compose --env-file $cfg --profile shell run --rm shell-builder keys-verify
```

**怎麼知道成功了**：第一條印出「已備份：備份目錄/keys/hd-keys-\<時間>.tar.gz」；第二條逐項 ✓，最後「還原得回來」。 `$root\backups\keys\` 底下看得到那份檔案。

> 📍 **1001 院內**：`keys-verify` 印出 `ca/ca.key`、`ca/ca.crt`、`signing/shell-signing.p12`、`signing/keystore.pass`、「備份裡的簽章金鑰以備份裡的密碼打得開」「備份裡的 CA 私鑰完整」，最後「`hd-keys-<時間>.tar.gz` 還原得回來」，全部 ✓。

**這份檔案裡有 CA 與簽章的私鑰。** 與資料庫備份一樣由院方送往院內另一台機器，不得出院、不得寄給開發端。送過去之後，在那一台上也要能取回——每年核對一次（第 7 節）。

______________________________________________________________________

### Y-07 讓病人端改走 HTTPS

```
docker compose --env-file $cfg restart patient-web
docker compose --env-file $cfg logs patient-web --tail 5
```

**怎麼知道成功了**：記錄裡有「靜態資源已提供於連接埠 8081（HTTPS；HTTP 只留外殼下載頁）」。主機的瀏覽器開 `http://<主機>:<病人端埠>/shell/` 看得到下載頁；開 `http://<主機>:<病人端埠>/` 會被轉到 `https://` 並跳出憑證警告——**這是對的**，主機的瀏覽器不信任院內 CA，平板上的外殼才信任。

`--tail 5` 常常跨到重新啟動之前那一次，所以「找不到伺服器憑證」與「HTTPS」可能同時出現，以最後一次啟動的那幾行為準。記錄裡的 `8081`、`http://api:3000` 是容器裡面的埠，對應主機上的 `HD_PATIENT_PORT`、`HD_API_PORT`（🏥 `18081`、`13000`）；`api:3000` 是 `patient-web` 經容器之間的網路找後端的位址，不經過主機。平板一律連 `HD_PATIENT_PORT`。

| 症狀                                                        | 處置                                              |
| ----------------------------------------------------------- | ------------------------------------------------- |
| **最後一次**啟動的記錄是「找不到伺服器憑證…暫以 HTTP 提供」 | Y-05 還沒跑成功，或跑完沒有重新啟動 `patient-web` |
| 下載頁顯示「外殼 App 尚未建置」                             | 同上                                              |

> **伺服器憑證換過之後也要做這一步**：`shell-builder` 發現主機位址變了、或憑證 30 天內到期時會重新簽一張， `patient-web` 要重新啟動才讀得到。CA 沒變，平板不受影響。

______________________________________________________________________

### Y-08 平板連得進來

平板與主機之間要能連到病人端的埠。在主機上：

```
Get-NetFirewallRule -Direction Inbound -Enabled True | Where-Object DisplayName -like "*Docker*" | Select-Object DisplayName, Profile
```

**怎麼知道成功了**：拿一台平板（或手機）連上**與平板實際使用時相同的 Wi-Fi**，瀏覽器開 `http://<主機>:<病人端埠>/shell/` 看得到下載頁。

| 症狀                                  | 處置                                                                                                                                                                                               |
| ------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 主機自己開得到，平板開不到            | Windows 防火牆擋了連入，或平板那個 Wi-Fi 網段到不了主機。**找資訊室**（Q-27），不要自己關防火牆                                                                                                    |
| 平板開不到，手機在同一個 Wi-Fi 開得到 | 平板的 Wi-Fi 連錯了                                                                                                                                                                                |
| 🧪 開發機上手機開不到                 | 開發機的網路設定檔類型要是「私人」；仍不行，只對私人網路開放病人端那一個埠的做法在[《從零部署本系統》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fresh-install-6/index.md) V-25 |

______________________________________________________________________

下一份：[《平板與外殼 App（第 2 份，Y-09～Y-15）》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-tablet-2/index.md)・[部署手冊目錄](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/index.md)

## 版本歷程

| 定版 | 日期       | 異動                                                                                                                                            |
| ---- | ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| 1118 | 2026-11-18 | 首次定版。1117 部署手冊整套重寫時由舊冊改寫而成（舊冊號見目錄最後的對照），步驟編號不變；1118 照每份約 300 行的上限拆檔，後段移到同一套的下一份 |

[← 回部署手冊目錄](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/index.md)
