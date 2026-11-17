# 第三次進院（1029）· 接手 v0.3.0、換成 IP、換版

> - 狀態：**已照做 1029，凍結**。結果是 B 級（部分成功），見《[第三次進院紀錄（1029，部分成功）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/record-3-1029/index.md)》；紀錄要手冊改的 13 處（O-13）1116 已全部改回這一冊，之後只維護常備參考
> - 從哪幾份舊冊改寫（1117）：第十八冊（第三次進院：實際部署）、第十七冊第 3、4 節（每一步的模擬部署差異，改成各步的 🧪 行）
> - 編號：`J-xx`（沿用第十八冊）；開發機才做的步驟 `I-xx` 在之七～之九

## 摘要

- 院內主機上已經有 1001 裝的 `v0.3.0`、三個服務在跑、護理站登不進去；這一趟是「接著做」，不是從零部署
- 順序：出發前 → 到場先看、先抄 → 換成 IP、護理站登入（仍在 `v0.3.0`）→ 換到新版 → 備份、防毒、重新開機 → 探測院方 API → 暫用平板（時間夠才做）→ 冒煙測試與交接
- **先在 `v0.3.0` 上把登入修好，再換新版**；成敗只看護理站的電腦登不登得進去（J-14 過了就至少 B 級）
- 1029 結果：J-14 15:34 登入成功、換到 `v0.4.0`、備份還原、院方 API 探測、暫用平板佈建都做了；重新開機、防毒排除、交接、問資訊室的八題沒做
- 這一份：整趟共通的差異表與 J-01～J-14（出發前、到場先看先抄、換成 IP 讓護理站登入）；J-15～J-33 在第 2 份
- 🧪 開發機演練的順序：之七、之八 I-01～I-12 → 主文件 J-04～J-30 → 之九 I-13～I-17；沒通過 I-16 的 tag 不准帶進院
- 換版、退回、登不進去怎麼查、取出資料等之後還會用到的做法，現在以常備參考為準：《[本系統換版與退回](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-upgrade/index.md)》《[護理站登不進去與主機位址](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-login/index.md)》《[取出資料](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-data-export/index.md)》

## 這一套的檔案

主文件（1118 按每份約 300 行的上限拆成兩份，步驟編號與節號不變）：

- 這一份：開始之前、第 1～3 節（J-01～J-14）
- 《[…（第 2 份，J-15～J-33）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-3-system-2/index.md)》：第 4～9 節（換到新版、備份防毒重新開機、院方 API 探測、暫用平板、收尾、開發機才做的步驟）

子文件（詳細版用主文件同一套編號：每一步為什麼、完整指令、會看到的原文、不對的話怎麼辦）：

- 《[…之一：詳細版（第 0 節、J-01～J-03）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-3-system-detail/index.md)》：讀之前（目標、三種結果、時間怎麼排與取捨、每一步的三塊、名詞、主機長相、停手條件、開發機演練怎麼用）；第 1 節出發前
- 《[…之二：詳細版（J-04～J-08）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-3-system-detail-2/index.md)》：第 2 節到場先看、先抄：開工三行、確認主機現況、0922 的容器、先抄五樣、確認 `<IP>`
- 《[…之三：詳細版（J-09～J-14）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-3-system-detail-3/index.md)》：第 3 節換成 IP、讓護理站登得進去（仍在 `v0.3.0`）
- 《[…之四：詳細版（J-15～J-21）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-3-system-detail-4/index.md)》：第 4 節換到新版：下載、補 `.env`、建置、更新資料庫、啟動、AI 閘道、取出資料的指令
- 《[…之五：詳細版（J-22～J-29）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-3-system-detail-5/index.md)》：第 5～7 節：備份還原、Docker Desktop 設定、防毒、重新開機、探測院方 API、暫用平板
- 《[…之六：詳細版（J-30～J-33、附錄）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-3-system-detail-6/index.md)》：第 8 節收尾（冒煙測試、交接、離院前、回來之後）；附錄一～四：步驟對照、退回 `v0.3.0`、護理端登不進去（這一趟才有的部分）、一張紙帶進去
- 《[…之七：開發機才做的演練（第 0 節、I-01～I-05）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-3-system-rehearsal/index.md)》：演練的讀之前（要證明什麼、怎麼和主文件與詳細版一起用、準備、時間、規矩）；第 1 節準備（打 tag、工具、部署金鑰、開發機的 `<名稱>` 與 `<IP>`）
- 《[…之八：開發機才做的演練（I-06～I-12、照主文件做 J-04～J-30）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-3-system-rehearsal-2/index.md)》：第 2 節把開發機變成 1001 離院時的院內主機；第 3、4 節照主文件做 J-04～J-30
- 《[…之九：開發機才做的演練（I-13～I-17、附錄）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-3-system-rehearsal-3/index.md)》：第 5 節模擬部署才做的驗收（模擬院方 API、三支驗收、退回 `v0.3.0`、十項判定）；第 6 節撤除；附錄步驟對照

______________________________________________________________________

## 開始之前：整趟共通的差異

| 差異               | 🏥 院內正式主機                                                                                                  | 🧪 開發機演練                                                                      |
| ------------------ | ---------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `$root`            | `C:\hd\hd-tablet-care`                                                                                           | `C:\hd-sim`                                                                        |
| `<名稱>`           | 1001 填進 `.env` 的那個主機名稱                                                                                  | 開發機的電腦名稱（I-05）                                                           |
| `<IP>`             | 資訊室確認、而且固定下來的院內主機 IP                                                                            | 手機連的那個網路的網卡 IPv4 位址（I-05）                                           |
| `<新 tag>`         | J-01 定下來（1029 帶的是 `v0.4.0`）                                                                              | I-01 打的那一個                                                                    |
| 護理站的電腦       | 護理站的電腦（要 Windows 密碼、螢幕會休眠）                                                                      | 連同一個 Wi-Fi 的手機瀏覽器（必要時另一台筆電）                                    |
| 平板用的 Wi-Fi     | 院內給平板用的 Wi-Fi                                                                                             | 開發機連的同一個 Wi-Fi                                                             |
| 資訊室、護理長     | 要約好、全程在場（J-02）                                                                                         | 自己；要問他們的事跳過，紀錄裡寫「院內要問」                                       |
| 管理者帳號         | `.env` 的 `SUPER_ADMIN_WORK_ID`、`SUPER_ADMIN_INITIAL_PASSWORD`                                                  | `sim-admin` / `Sim-Init-2026`                                                      |
| `HD_SHELL_SIGNING` | `hospital`                                                                                                       | `dev`                                                                              |
| `HD_EXPORT_DIR`    | `C:\hd\hd-tablet-care\export`                                                                                    | `C:\hd-sim\export`                                                                 |
| 值寫在哪           | 《[部署演練紀錄](https://94sh09sh19sh.github.io/hd-docs/latest/notes/deployment-drills/index.md)》第 12 節的紙本 | 《部署演練紀錄》第 11 節，只寫對不對、花多久、錯誤原文                             |
| 拍照               | 可以拍，照片只進私人 repo 的 `deploy/records/`，離院前從手機刪；`.env`、密碼、病人資料的畫面不拍                 | 可以拍；不拍 `notepad $cfg` 的畫面                                                 |
| 跑哪幾步           | J-01～J-33                                                                                                       | 之七、之八 I-01～I-12 → J-04～J-30（J-01～J-03、J-31～J-33 跳過）→ 之九 I-13～I-17 |
| 時段               | J-18 排在沒有透析的時段；J-25 要資訊室同意                                                                       | 一整個下午；I-05 到 J-29 中途不換 Wi-Fi、開發機不睡眠                              |

代稱**連同 `<`、`>` 一起換掉**：`http://<IP>:18080` 要打成 `http://192.0.2.20:18080`，不是 `http://<192.0.2.20>:18080`。

從第 2 節起，指令都在主機的 PowerShell 裡打；**不要自己開任何容器，不要下 `docker run`**。每一步開始與結束各記一次時間，錯誤訊息抄原文、抄到最後一行。

______________________________________________________________________

## 1. 出發前（在開發端做完）

### J-01 確認要帶的 tag 已經演練過

**做什麼**：開發機的工作目錄打 `git ls-remote --tags origin`、`git rev-parse <新 tag>`、`git show <新 tag>:services/shell-builder/shell.pin`。

**成功**：清單有 `<新 tag>` 與 `v0.3.0`；commit 與演練時同一個；`SHELL_TAG=v0.3.0`；演練紀錄第 11 節這個 tag 的判定是「可以帶進院」。

🧪 跳過：J-01 就是之七 I-01。

### J-02 約人、把問題清單寄給資訊室

**做什麼**：至少一週前，寄出約人表與問資訊室的八題（之一 J-02），要文字答覆。

**成功**：有具體的人名與時段；每一題都有答覆，或寫明「未答覆」與對方是誰。

🧪 跳過，但問題清單照樣在出發前寄。

### J-03 準備要帶的東西

**做什麼**：照之一 J-03 的清單帶：這一冊的紙本、演練紀錄第 12 節空白表、演練時抄的耗時與錯誤原文、筆記本與筆、手機、暫用平板與充電器。

**成功**：清單上每一樣都帶了；隨身碟與開發機上的設定檔沒帶。

🧪 跳過。

______________________________________________________________________

## 2. 到場：先看、先抄，不改任何東西

### J-04 開工三行

**做什麼**：

```
$root = "C:\hd\hd-tablet-care"
$cfg  = "$root\config\.env"
cd $root\repo
```

**成功**：提示字元變成 `PS C:\hd\hd-tablet-care\repo>`。PowerShell 關掉再開就要重打。

🧪 第一行改成 `$root = "C:\hd-sim"`。

### J-05 確認主機還是 1001 離開時的樣子

**做什麼**：打之二 J-05 的八條（tag、改動、容器、資料卷、金鑰備份、備份份數、磁碟、health），結果抄下來。

**成功**：`v0.3.0`、沒有改動、三個服務 `Up`（可能還有 `ai-gateway`）、兩個資料卷、1001 的金鑰備份在、health 是 `{"status":"ok",…}`。

🧪 照做；`backups\keys` 那一份是 I-10 的，`*.db` 0 份是正常的；表上對不上的一列是手冊寫錯，圈起來。

### J-06 0922 的容器還在的話

**做什麼**：只有 J-05 看到 `dialysis_system_v0` 才做：照《[第二次進院（1001）· 從零部署本系統之九：收掉 0922 留下的東西](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-2-system-cleanup/index.md)》L-02 起收掉。

**成功**：`docker ps -a` 清單裡沒有 `dialysis_system_v0`。

🧪 跳過（開發機上沒有）；想練就照那一份的附錄做替身。

### J-07 先抄五樣

**做什麼**：打之二 J-07 的五條：`.env` 的三個位址、後端手上的放行名單、網頁裡的後端位址、`keys-info`、AI 閘道設定檔在不在。

**成功**：五樣原文都抄了；「伺服器憑證」那一行是 `DNS:<名稱>`。

🧪 照做；第 1、2 條都是 `hd-server`，照判斷表應判成「可能 A」。

### J-08 確認 `<IP>`，並先從護理站連一次

**做什麼**：主機上 `ipconfig /all` 看實體網卡的 IPv4；護理站的電腦開 `http://<IP>:13000/api/health` 與 `http://<IP>:18080`（不按登入）；手機連平板的 Wi-Fi 開 `http://<IP>:18081/shell/`。

**成功**：IP 與資訊室給的一字不差；health 是 `{"status":"ok",…}`；看得到登入頁；看得到外殼下載頁。

🧪 先開三條只對私人網路的防火牆規則、Wi-Fi 設成「私人」（之二 J-08）；第 1 步 DHCP 是「是」沒關係；第 2～4 步都用手機。

🏥 連不到就找資訊室，不自己關防火牆、不改網路類型。

______________________________________________________________________

## 3. 換成 IP，讓護理站登得進去（仍在 `v0.3.0`）

### J-09 留一份改之前的 `.env`

**做什麼**：`Copy-Item $cfg "$root\config\.env.before-ip"`，再 `Get-ChildItem "$root\config"`。

**成功**：看得到 `.env` 與 `.env.before-ip` 兩個檔。

### J-10 把三個位址改成 `<IP>`

**做什麼**：`notepad $cfg`，`HD_PUBLIC_API_URL`、`CORS_ORIGINS`、`MDM_KIOSK_BASE_URL` 三行的主機部分改成 `<IP>`，`CORS_ORIGINS` 只留 `http://<IP>:18080`；存檔後打之三 J-10 的四條檢查。

**成功**：`config --quiet` 沒印東西；三行都是 `<IP>`；範例值、`localhost`、角括號、舊名稱都搜不到。

🧪 第三條檢查原本會抓到 `hd-server`，改完要什麼都不印。

### J-11 重建網頁、啟動，並在主機上確認放行

**做什麼**：`docker compose --env-file $cfg build`、`up -d`、`ps`，再打之三 J-11 的四條確認。

**成功**：`Image hd-tablet-care:v0.3.0 Built`；三個服務 `Up`；網頁裡的後端位址是 `http://<IP>:13000`；印出 `Access-Control-Allow-Origin: http://<IP>:18080`；日誌最後一行 `允許的前端來源：http://<IP>:18080`。

🧪 記下建置耗時。

### J-12 重簽伺服器憑證、備份金鑰、病人端換上新憑證

**做什麼**：`docker compose --env-file $cfg --profile shell run --rm shell-builder` 跑兩次，再 `keys-backup`、`keys-verify`、`restart patient-web`、看日誌、`keys-info`（之三 J-12）。

**成功**：第一次「這一次新產生」**只有**伺服器憑證（`<IP>`）；第二次「金鑰全部沿用」；`keys-verify` 全 ✓；病人端最後一次啟動是 HTTPS；`keys-info` 是 `IP Address:<IP>`，CA 與簽章金鑰指紋與 J-07 一模一樣。

🧪 記下耗時。

### J-13 在主機上登入、改密碼

**做什麼**：主機的瀏覽器開 `http://<IP>:18080`，用 `SUPER_ADMIN_WORK_ID` 與 `SUPER_ADMIN_INITIAL_PASSWORD` 登入。

**成功**：被要求改密碼；新密碼由護理長決定、自己保管。

🧪 用 `sim-admin` / `Sim-Init-2026`，改成什麼都可以（記在紀錄紙上）。之後多做一件：故意用 `http://localhost:18080` 與 `http://<名稱>:18080` 各開一次、按登入，兩次都是 `Failed to fetch`。

### J-14 在護理站的電腦登入

**做什麼**：護理站的電腦開 `http://<IP>:18080`，請護理長用新密碼登入；改好舊書籤，刪掉 `.env.before-ip`。

**成功**：看得到護理端的畫面，記下時間（1029：15:34）。這一步過了就至少 B 級。

🧪 用手機瀏覽器；記下從 J-04 到這裡總共多久。

______________________________________________________________________

下一份：《[…（第 2 份，J-15～J-33）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-3-system-2/index.md)》

## 版本歷程

| 定版 | 日期 | 異動 |
| ---- | ---- | ---- |
|      |      |      |

[← 回部署手冊目錄](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/index.md)
