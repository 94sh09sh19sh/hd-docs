# 從零部署本系統（第 5 份，V-18～V-24）

上層文件：《[從零部署本系統](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fresh-install/index.md)》

> **狀態：現行（常備參考）。** 改寫自第十五冊（1117）；編號 `V-xx`（沿用第十五冊），每一步下面註明對應的 `N-xx` 與 `W-xx`／`Y-xx`／`Z-xx`。1118 照步驟順序拆成七份，這是第 5 份；🧪／🏥／📍 標記的意思見第 1 份 0.2 節。

## 摘要

- 第 7 節：V-18 備份一次並證明還原得回來（一律用 PowerShell）；V-19 重新開機測試，院內到 1116 還沒驗過
- 1116 開發機實測：Quit Docker Desktop 再開，服務沒有自己回來，列為已知限制
- 第 8 節前半（外殼 App）：V-20 外殼 repo 的部署金鑰與 clone、V-21 建 `shell-builder` 的映像檔（院內實測 27～33 分鐘）
- V-22 建 APK，抄下三個 SHA-256；外殼版本是 `shell.pin` 釘的 `v0.3.0`
- V-23 備份金鑰並核對還原得回來（檔案有私鑰，不得出院）；V-24 讓病人端改走 HTTPS

______________________________________________________________________

## 7. 備份與重新開機

### V-18 備份一次，並證明還原得回來

對應：N-17、W-17

「有備份」和「備份能用」是兩件事。

**做什麼**

1. 護理端 → **系統管理** → 「立即備份」，記下畫面上的檔名（或用下面第一條找最新的一份）。備份歷程的 SHA-256 只顯示前 12 碼；完整的 64 碼到備份資料夾讀同名的 `.sha256` 檔：

```
Get-ChildItem $root\backups\hd-backup-* | Sort-Object LastWriteTime | Select-Object -Last 1 Name
Get-Content "$root\backups\<檔名>.sha256"
```

前半段就是雜湊。護理端 **稽核軌跡**（動作選「資料庫線上備份」）的說明欄也有完整的一份。 2. 把它還原到一個測試檔，確認完整，再刪掉測試檔（`<檔名>`、`<雜湊>` 換成剛剛記下的；第一條是一整行）：

```
docker compose --env-file $cfg run --rm --no-deps api node_modules/.bin/ts-node --project apps/api/tsconfig.json apps/api/scripts/restore-backup.ts --from /backups/<檔名> --to /data/restore-check.db --sha256 <雜湊>
docker compose --env-file $cfg run --rm --no-deps --entrypoint rm api /data/restore-check.db
```

**怎麼知道成功了**：輸出有 `✓ 與備份歷程上的紀錄相符` 與 `完整性檢查：ok`；`$root\backups\` 裡看得到那個檔和同名的 `.sha256`。

> 💡 **服務起不來時**：備份歷程與稽核軌跡都存在資料庫裡，打不開網頁就看不到。這時直接看資料夾： `Get-ChildItem "$root\backups\*.db" | Sort-Object LastWriteTime` 最後一個是最新的備份，雜湊在它旁邊的 `.sha256`。送往院內另一台機器時，`.sha256` 要跟著一起送。

🏥 實際部署還要**當場問清楚**：備份資料夾（連同 `keys\`）的內容由誰、多久送往院內另一台機器一次？答不出來就寫進交接文件的「已知限制」。

> ⚠️ **這一步一律用 PowerShell。** 在 Git Bash 裡打，`/backups/…` 會被自動改寫成 Windows 路徑，還原腳本就說找不到檔案。

| 症狀                             | 處置                                                      |
| -------------------------------- | --------------------------------------------------------- |
| `✗ 與備份歷程上的紀錄不符`       | 雜湊抄錯，重抄 `.sha256` 那一份；還是不符就打電話給開發端 |
| 刪測試檔那一條印「No such file」 | 前一條沒寫出測試檔，看前一條的錯誤原文                    |

> 📍 **1001**：未測。
>
> 🧪 **模擬部署**：做到還原成功即可，不必送往任何地方。

______________________________________________________________________

### V-19 重新開機測試

對應：N-18、W-18

`restart: unless-stopped` 只管 Docker 起來之後；Docker Desktop 要有人登入 Windows 才會啟動。**這一條決定這條路線在院內能不能用。**

**做什麼**：🏥 重新開機 → **以平常登入的帳號登入**（1007 答覆：斷電後由護理長重新登入，不設自動登入；這一步就是在模擬護理長）→ **之後什麼都不碰**，等三分鐘 → 開一個新的 PowerShell，先輸入開工三行，再：

```
docker compose --env-file $cfg ps
curl.exe -s http://localhost:13000/api/health
```

**怎麼知道成功了**：三個服務自己回到 `Up`、health 正常，**登入之後沒有人手動開 Docker Desktop**。

**過了之後**：交接文件寫一段給護理長看的「斷電之後」——護理端每個畫面閃紅框、平板顯示請按床邊呼叫鈴 → 到主機開機、以平常的帳號登入 → 什麼都不碰，等三分鐘 → 護理端紅框消失就好了。記下從開機到紅框消失幾分鐘。

**沒過的話**：記下實況（Docker Desktop 有沒有隨登入起來、V-05 第 1 項有沒有勾），寫進交接文件；手動開 Docker Desktop、等變綠、`docker compose --env-file $cfg up -d`。**不要在現場自己改院方的登入設定。**

> ⚠️ 🏥 主機上還有另一個專案的容器在跑。重新開機會一起中斷它，**先問資訊室可不可以、挑什麼時候**。
>
> 📍 **1001**：未測。1029、1116 也都沒做（院方還沒准），院內主機到 1116 為止**沒有驗過重新開機**。

**1116 開發機實測**：Quit Docker Desktop 再開，**服務沒有自己回來**（`docker ps -a` 全是 `Exited`）：Docker Desktop 在 Quit 時先逐一停掉容器，容器被當成「手動停止」，`restart: unless-stopped` 就不會再啟動它。院內真的重新開機時會不會一樣還沒驗過；`v0.5.0` 照帶，列為已知限制，下一個 tag 預計把 compose 的 `restart` 改成 `always` 後重驗。

> 🧪 **模擬部署**：可以跳過。開發機是你自己登入的，驗不出院內「沒人登入」的情形。要練的話：工作列右下角通知區的 Docker 鯨魚圖示（藏在 `^` 裡就先點 `^`）按右鍵 → **Quit Docker Desktop** → 從開始選單再開 → 等三分鐘；**關掉 Docker Desktop 的視窗不算**，視窗關了引擎照跑。量到的分鐘數只當參考。

______________________________________________________________________

## 8. 外殼 App 與平板

這一節做兩件事：在主機上把外殼 App（APK）建出來，然後讓平板從院內的下載頁安裝、釘住。 **私鑰全程不離開主機**，平板也不必接電腦。外殼的版本、金鑰、下載頁、重新佈建的細節在《[平板與外殼 App](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-tablet/index.md)》（`Y-xx`）。

### V-20 外殼 repo 的部署金鑰與 clone

對應：N-19、Y-02

外殼 App 在另一個 repo（`hd-kiosk-shell`），要**另一把**部署金鑰——一把部署金鑰只能給一個 repo。

**做什麼**

1. 產生並交出公鑰，登記到**外殼 repo** 的 Settings → Deploy keys，不勾 Allow write access：

```
ssh-keygen -t ed25519 -C "hd-kiosk-shell@$(hostname)" -f $HOME\.ssh\hd-kiosk-shell -N '""'
Get-Content $HOME\.ssh\hd-kiosk-shell.pub
```

1. `notepad $HOME\.ssh\config`（V-10 已經建好這個檔，直接開就好），在最後再加一段：

```
Host github-hd-kiosk-shell
    HostName github.com
    User git
    IdentityFile ~/.ssh/hd-kiosk-shell
    IdentitiesOnly yes
```

1. 確認並 clone（**不必切 tag**，`shell-builder` 會自己取出要的那一版）：

```
ssh -T github-hd-kiosk-shell
git clone git@github-hd-kiosk-shell:94sh09sh19sh/hd-kiosk-shell.git $root\hd-kiosk-shell
git -C $root\hd-kiosk-shell tag
```

**怎麼知道成功了**：`ssh -T` 印出 `Hi 94sh09sh19sh/hd-kiosk-shell!…`（**是 `hd-kiosk-shell`，不是 `hd-tablet-care`**）；`git tag` 列得出 V-03 看到的那一版。 `git tag` 會把外殼 repo 的**每一個** tag 都列出來，連以前的版本也在（1001 是 `v0.2.0`、`v0.3.0` 兩行）——**這是對的**，`shell-builder` 只取 `shell.pin` 釘住的那一個（現在是 `v0.3.0`）。

| 症狀                                                              | 處置                                                                        |
| ----------------------------------------------------------------- | --------------------------------------------------------------------------- |
| `ssh -T` 印出的是 `hd-tablet-care`                                | 設定檔兩段的 `IdentityFile` 寫反，或少了 `IdentitiesOnly yes`               |
| `Permission denied (publickey)`                                   | 公鑰登記到本系統的 repo 去了                                                |
| `ssh -T` 成功，`git clone` 卻出現 `Connection reset by … port 22` | 網路把連線切斷。刪掉殘留的資料夾再重跑；還是被切，這一段改走 443（同 V-10） |

> 🧪 **模擬部署**：與 V-10 相同，開發機上另產生一把、標題註明模擬部署。

______________________________________________________________________

### V-21 建 `shell-builder` 的映像檔

對應：N-20、Y-04

**做什麼**（**先記下開始時間**）

```
docker compose --env-file $cfg --profile shell build shell-builder
```

第一次要下載 Android SDK 與 Gradle，約 1.5 GB。**這一步要連外，而且很久**。V-06 已經先下載了 `eclipse-temurin:17-jdk-jammy`，這一步會直接沿用。

**怎麼知道成功了**：最後幾行有「✓ 外殼 v0.x.x（…，契約第 1 版）已準備好，相依已下載」（`v0.x.x` 是 `shell.pin` 釘的那一版，現在是 `v0.3.0`）。**記下結束時間**。

| 症狀                                                                                                                                      | 處置                                                                                                                  |
| ----------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `failed to resolve source metadata for docker.io/library/eclipse-temurin`，後面有 `lookup production.cloudfront.docker.com: no such host` | Docker 查不到 Docker Hub 的下載站，照 V-06 第二段那一列處理。單獨測這一段：`docker pull eclipse-temurin:17-jdk-jammy` |
| `外殼 repo 的 clone 裡沒有 tag vX.Y.Z`                                                                                                    | `git -C $root\hd-kiosk-shell fetch --tags`，再建一次                                                                  |
| 提到版本、契約版本不符，或「外殼原始碼裡有指向院外的網址」                                                                                | **開發端的問題，不在現場修。** 停手，回開發端                                                                         |
| `dl.google.com`、`services.gradle.org`、`maven.google.com` 逾時                                                                           | 對外連線被擋，請資訊室開通（Q-32）                                                                                    |
| 停在 `gradle.zip` 很久                                                                                                                    | 它會自己重試、失敗會自己結束。結束後再打一次同一條，已完成的部分不會重下載                                            |

> 📍 **1001**：遇到上表第一列，**同一條指令再打一次就過了**。這一步含出錯與重來，**院內實測 27～33 分鐘**。

______________________________________________________________________

### V-22 建 APK（第一次會產生金鑰）

對應：N-21、Y-05

**做什麼**

```
docker compose --env-file $cfg --profile shell run --rm shell-builder
```

**怎麼知道成功了**：第一次會印出「這一次新產生：院內 CA 伺服器憑證（\<主機>） APK 簽章金鑰（…）」，接著是 APK 檔名與**三個 SHA-256**（檔案、簽章憑證、院內 CA）。**把三個 SHA-256 抄下來**，🏥 實際部署要寫進交接文件。

括號裡的 `<主機>` 要是 V-08 定的那一個——伺服器憑證就簽這個名字。

**再打一次同一條指令**，這次要看到「**金鑰全部沿用，這一次沒有產生任何新的金鑰**」，而且簽章憑證的 SHA-256 與第一次相同。

> 💡 **沒抄到也查得到，不必重跑。** 瀏覽器開 `http://localhost:18081/shell/`，下載頁最下面「版本資訊」列著三個 SHA-256（同一個資料夾的 `shell.json` 也有）。每跑一次建置，下載頁上的 APK 就會換成新的一份，所以**交接文件的檔案 SHA-256 以下載頁上的為準**。 `shell-builder keys-info` 只列得出院內 CA 與簽章金鑰的指紋，而且是大寫、以冒號分隔，對照時去掉冒號、大小寫不計。

| 症狀                                                | 處置                                                                                                                                               |
| --------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| `MDM_KIOSK_BASE_URL 要以 https:// 開頭`             | `.env` 改成 `https://`，見《[`.env` 怎麼填](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-env/index.md)》1.4                        |
| `這個金鑰資料卷是「dev」用的，設定卻是「hospital」` | **停手。** 院內主機上出現了開發用的金鑰，或 `.env` 抄了開發機那一份                                                                                |
| `有 CA 憑證卻沒有私鑰` 之類                         | 資料卷不完整。**不要刪掉重來**，照《[平板與外殼 App](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-tablet/index.md)》從金鑰備份還原 |

> 📍 **1001**：做了，三個 SHA-256 沒有抄。下一次從下載頁抄。
>
> 🧪 **模擬部署**：第一次那行會寫「APK 簽章金鑰（開發用）」，是對的。

______________________________________________________________________

### V-23 備份金鑰，並核對還原得回來

對應：N-22、Y-06

**做什麼**

```
docker compose --env-file $cfg --profile shell run --rm shell-builder keys-backup
docker compose --env-file $cfg --profile shell run --rm shell-builder keys-verify
```

**怎麼知道成功了**：第一條印出「已備份：備份目錄/keys/hd-keys-\<時間>.tar.gz」；第二條每一項都 ✓，最後「還原得回來」。

> 📍 **1001**：`keys-verify` 印出 `ca/ca.key`、`ca/ca.crt`、`signing/shell-signing.p12`、`signing/keystore.pass`、「備份裡的簽章金鑰以備份裡的密碼打得開」「備份裡的 CA 私鑰完整」，最後「`hd-keys-20261001-173347.tar.gz` 還原得回來」，全部 ✓。
>
> ⚠️ **這份檔案裡有私鑰。** 🏥 實際部署：與資料庫備份一樣由院方送往院內另一台機器，**不得出院、不得寄給開發端**。金鑰遺失的後果是**每一台平板都要解除安裝重裝**。

______________________________________________________________________

### V-24 讓病人端改走 HTTPS

對應：N-23、Y-07

**做什麼**

```
docker compose --env-file $cfg restart patient-web
docker compose --env-file $cfg logs patient-web --tail 5
```

**怎麼知道成功了**：日誌**最後一次**出現的「靜態資源已提供於連接埠 8081」那一行，後面是「（HTTPS；HTTP 只留外殼下載頁）」。主機的瀏覽器開 `http://localhost:18081/shell/` 看得到下載頁；開 `http://localhost:18081/` 會被轉到 `https://` 並跳出憑證警告——

**這是對的**：主機的瀏覽器不認得院內 CA，只有平板上的外殼 App 認得。

日誌裡兩個常讓人愣一下的地方，**都是正常的**（1001 兩個都遇到了）：

- **「找不到伺服器憑證」和「HTTPS」同時出現**：`--tail 5` 取最後 5 行，常常跨到重新啟動**之前**那一次的輸出。以**最後一次**啟動的那幾行為準。
- **寫的是 `8081` 和 `http://api:3000`，不是 `18081`、`13000`**：這兩個是**容器裡面**的埠。主機的 `18081` 轉進容器的 8081； `api:3000` 是 `patient-web` 經容器之間的網路找後端的位址，不經過主機。瀏覽器和平板一律連 `18081`。

| 症狀                                                        | 處置                                          |
| ----------------------------------------------------------- | --------------------------------------------- |
| **最後一次**啟動的日誌是「找不到伺服器憑證…暫以 HTTP 提供」 | V-22 還沒成功，或做完沒重新啟動 `patient-web` |

______________________________________________________________________

上一份：《[從零部署本系統（第 4 份，V-12～V-17）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fresh-install-4/index.md)》｜下一份：《[從零部署本系統（第 6 份，V-25～V-30a）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fresh-install-6/index.md)》｜第一份（索引）：《[從零部署本系統](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fresh-install/index.md)》｜[部署手冊目錄](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/index.md)

## 版本歷程

| 定版                                                                                | 日期       | 異動                                                                             |
| ----------------------------------------------------------------------------------- | ---------- | -------------------------------------------------------------------------------- |
| [1118](https://94sh09sh19sh.github.io/hd-docs/1118/deployment/ref-fresh-install-5/) | 2026-11-18 | 首次定版。1118 照每份約 300 行的上限由《從零部署本系統》拆出，內容與步驟編號不動 |

[← 回部署手冊目錄](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/index.md)
