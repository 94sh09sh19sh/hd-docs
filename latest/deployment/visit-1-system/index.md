# 第一次進院（0922）· 部署本系統

> - 狀態：**已照做 0922，凍結**，C 級失敗，結果見《[第一次進院紀錄（0922，失敗）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/record-1-0922/index.md)》；安裝包路線 0926 撤除，這一趟的做法是歷史，現行做法看《[從零部署本系統](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fresh-install/index.md)》
> - 1117 由舊的第四冊（不含 H-08～H-13 的安裝步驟）、第九冊與舊總覽第 1、4 節（當時的已知空白與時程）改寫
> - 編號：沿用 `H-xx`（進院當天）與 `D-xx`（git clone＋Docker 路線）；🧪 對應的開發端彩排是 `R-xx`，在《[安裝包路線之三～之五：建置與開發端彩排](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-installer-build-3/index.md)》

這一套分成主文件兩份、子文件八份，第 1 份（本份）就是索引：

- 主文件第 1 份（本份）：第 0～5 節，進院前 D-01～D-04、進院當天 H-01～H-07、路線分岔 H-08～H-13
- 主文件《[第 2 份](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-1-system-2/index.md)》：第 6～9 節，容器路線 D-05～D-26、回到 H 的 H-14～H-24、隨時可以停手
- 《[之一：進院當天詳細版（H-01～H-13）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-1-system-onsite/index.md)》：當天的形狀、出門前、抵達、進到主機前面、路線 A 與路線 B 的指路
- 《[之二：進院當天詳細版（H-14～H-15）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-1-system-onsite-2/index.md)》：Windows 五件事（含自己做的時候）、防火牆與從護理站連進來
- 《[之三：進院當天詳細版（H-16～H-24）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-1-system-onsite-3/index.md)》：驗證、交接、離院前、隨時可以停手
- 《[之四：git clone＋Docker 路線詳細版（第 0 節、D-01～D-04）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-1-system-docker/index.md)》：規則哪些變、東西放哪、0921 開發端演練、進院前四步
- 《[之五：git clone＋Docker 路線詳細版（D-05～D-12）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-1-system-docker-2/index.md)》：進院當天先確認 Docker 這一層、取得程式碼
- 《[之六：git clone＋Docker 路線詳細版（D-13～D-18）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-1-system-docker-3/index.md)》：建置映像檔、設定與資料
- 《[之七：git clone＋Docker 路線詳細版（D-19～D-27）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-1-system-docker-4/index.md)》：啟動與驗證、收掉連線與憑證、回到進院當天詳細版
- 《[之八：git clone＋Docker 路線詳細版（第 9～12 節）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-1-system-docker-5/index.md)》：關服務、之後的更新回退與還原、疑難排解、離院前多五條

這是簡易版：每一步只寫做什麼、怎樣算成功；為什麼、完整指令、出錯處置在子文件同一個編號底下。

## 摘要

- 0922 這一趟的原計畫：帶隨身碟裡的離線安裝包進院，H 主流程走到底；院方若要求容器，H-08～H-13 換成 D-05～D-26，H-14 起回 H
- 實際：院方當天要求以容器部署，走 D 分支；現場沒照 D-xx 做，先手動開了一個 `python` 容器，C 級失敗
- 進院前要做完 D-01～D-04（確認要被 clone 的那一版、乾淨機器演練、寄 Docker 問題清單、唯讀權杖）；0922 都沒做到位（F-04、F-05）
- 當時的已知空白：外殼 App 沒編譯過、平板沒買、主機細節（Q-27、Q-29）沒答覆，所以目標不是全部做完
- 時程表 0926 起作廢（路線換成容器＋`git clone`）
- 🧪 安裝包路線的彩排是 `R-xx`（D-2，乾淨機器斷網）；容器路線的彩排是 D-02（乾淨機器裝 Docker Desktop，D-11 做到 D-23）
- 停手準則、三種結果、誰要在場在《[進院通則](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-visit-rules/index.md)》

## 0. 整趟共通的差異

| 事項                   | 🧪 開發端彩排                                                                                                             | 🏥 院內正式主機                                                                             |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| 時點                   | 安裝包路線 D-2（R-xx）；容器路線 D-02，進院前做完                                                                         | D 日（0922）                                                                                |
| 機器                   | 乾淨的 Windows 機器或全新 VM，`node -v` 要失敗（R-01）；容器路線另裝 Docker Desktop；沒有乾淨機器就在開發機做並在紀錄寫明 | 院內共用主機，同機另有專案在用 Docker                                                       |
| 網路                   | 安裝包路線全程斷網（R-02）；容器路線建置要連外                                                                            | 預期零院外連線；容器路線建置時臨時開、建完關（D-10、D-24）。0922 實際主機連得到院外（F-07） |
| 人                     | 自己                                                                                                                      | 資訊室有主機管理員權限的人全程在旁（H-03）；護理長收交接                                    |
| 程式怎麼進去           | 自己用隨身碟複製（R-03）                                                                                                  | 隨身碟＋掃毒（H-05）；容器路線在主機上 `git clone`，用唯讀權杖（D-04、D-11）                |
| 驗不到、只能在院內驗的 | 0921 開發機演練沒驗：主機重新開機、另一台電腦連進來、關連線後重新啟動                                                     | D-21、D-24、D-26                                                                            |
| 時間                   | R-22 量到的每一步耗時                                                                                                     | 彩排耗時 ×1.5                                                                               |

## 1. 當時的已知空白（0922 前寫的）

寫這一趟手冊的時候，有三件事還沒到位：

| 空白               | 現況                                                                                          | 對這次進院的影響                                                                                                                                                                                                                                                                                                                                                       |
| ------------------ | --------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **病人端外殼 App** | 原始碼在 `apps/kiosk-shell/`，**從來沒有編譯過**，沒有 keystore、沒有 APK                     | 平板佈建這一整段**做不了**。當時的做法在《[安裝包路線](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-installer/index.md)》（K-xx）                                                                                                                                                                                                                      |
| **醫院平板**       | **尚未購入**，型號與 Android 版本未知。**0930：尺寸確定為 10 吋**                             | 同上。現場要帶回的是「買什麼」的答案（《[平板與外殼 App](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-tablet/index.md)》）                                                                                                                                                                                                                             |
| **正式主機的細節** | Q-27（權限、帳號、連接埠、防毒、磁碟額度）與 Q-29（隨身碟、掃毒站、變更流程）**都還沒有答覆** | 進院第一件事就是問清楚，見 H-03、H-04。**0926：Q-29 作廢（不准用隨身碟）；改問 Q-27 與 Q-32，清單在《[從零部署本系統之一：容器路線的原冊](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fresh-install-detail/index.md)》W-03。0930：Q-32 已回覆（對外連線常態、沒有限制）；Q-27 的 Docker 版本與連接埠（`13000`、`18080`、`18081`）已有答案，其餘待問** |

**因此這一次進院的目標不是「全部做完」。** 目標的優先順序（A 完全成功／B 部分成功／C 失敗）寫在《[進院通則](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-visit-rules/index.md)》。

這三項之後的進展：外殼 APK 1001 在院內主機上建好、暫用平板 1029 佈建過（《[第二次進院紀錄（1001）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/record-2-1001/index.md)》《[第三次進院紀錄（1029）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/record-3-1029/index.md)》）；院內主機現在的樣子以《[院內主機現況與未完成事項](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-status/index.md)》為準。

## 2. 時程：從當時到進院

| 時點         | 做什麼                                                                                      | 在哪                                                                                                                                                                                                               |
| ------------ | ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **D-14**     | 把 Q-27 與 Q-29 的問題清單寄給資訊室（**不要等到現場才問**）；容器路線的 9 題一起寄（D-03） | H-03、H-04                                                                                                                                                                                                         |
| **D-10**     | 決定主機位址（DNS 名稱或 IP）→ 產生院內 CA 與伺服器憑證                                     | K-01～K-02，《[安裝包路線](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-installer/index.md)》                                                                                                      |
| **D-7**      | 編譯外殼 App、建立 keystore、模擬器跑通                                                     | K-03～K-05，《安裝包路線》                                                                                                                                                                                         |
| **D-3**      | 建置安裝包、驗收五項、開發端掃毒                                                            | 《[安裝包路線之一](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-installer-build/index.md)》《[之二](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-installer-build-2/index.md)》P-xx |
| **D-2**      | **在一台乾淨機器上完整演練一次**（這一步不能省）                                            | 《安裝包路線之三～之五》R-xx；容器路線 D-02                                                                                                                                                                        |
| **D-1**      | 打包實體物品、列印紙本、隨身碟備妥                                                          | C-01～C-04（隨身碟在《安裝包路線》，其餘在《[進院通則](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-visit-rules/index.md)》）                                                                      |
| **D 日**     | 進院                                                                                        | 本冊第 4～8 節                                                                                                                                                                                                     |
| **D+0 晚上** | **當天就把紀錄補完**，趁記憶還熱                                                            | H-24（舊總覽寫成 H-19，是筆誤）                                                                                                                                                                                    |

> **0926 起上表作廢**，時程改成：D-14 寄出《容器路線的原冊》W-03 的問題清單 → D-3 要交的 tag 在開發機從零實測（W-01、《容器路線的原冊》第 7 節）→ D-2 確認 tag 在 GitHub 上（W-02）→ D 日照《容器路線的原冊》W-04 起。平板那幾列等迭代 12 改寫（0927 改寫成今天的《[平板與外殼 App](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-tablet/index.md)》）。

**D-2 那次演練是整條時程裡最不該省的一步。** 理由在《安裝包路線之三》R-xx 開頭：迭代 10 的兩個缺陷，都是把安裝包真的跑起來才現形的，靜態檢查一個都抓不到。

0922 教訓（F-05、F-19）：院方有可能臨時改要求，進院前就要把容器路線 D-01～D-04 的準備做完，不管用不用得到。

## 3. 進院前（在開發端做完）

### D-01 確認要被 clone 的那一版

- **做什麼**：開發機上 `git status --short`、`git fetch origin`，比對本機與 `origin/master` 的最新 commit
- **成功**：沒有未提交的變更；本機與 `origin/master` 一模一樣、`Dockerfile` 含 `openssl`；commit 抄進交付單
- 0922 實際：0921 的容器修正只在 `docker-route` 分支，不在 `master`（F-04）

### D-02 在開發端完整演練一次

- **做什麼**：🧪 乾淨的 Windows 機器（R-01 的標準）裝好 Docker Desktop，從 D-11 做到 D-23，全程計時
- **成功**：三個容器 `Up`、存活檢查 200；另一台電腦登得進護理端；重新開機一次看 D-26 的結果
- 🧪 R-xx 是安裝包路線的同一件事：R-01 乾淨機器 → R-02 斷網 → R-03 隨身碟 → R-04、R-05 雜湊與驗收五項 → R-06～R-09 目錄、帳號、`.env`、時區 → R-10～R-16 遷移、服務、另一台機器連入、權限、重新開機 → R-17、R-18 冒煙 → R-19～R-21 更新與回退 → R-22～R-24 耗時、紀錄、留著機器（《[安裝包路線之三～之五](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-installer-build-3/index.md)》）

### D-03 把 Docker 的問題清單事先寄給資訊室

- **做什麼**：進院前兩週把 9 題（Docker 形態與版本、授權、重新開機後有沒有人登入、`docker-users`、同機其他專案、要開的網域、誰開關連線、有沒有 Git、虛擬磁碟放哪）寄出
- **成功**：有書面回覆；第 2、3 題沒答案就不能開始輸入真實病人資料

### D-04 準備一把唯讀、會過期的存取憑證

- **做什麼**：GitHub fine-grained 權杖，只勾這個 repo、Contents 唯讀、進院隔天過期；抄在交付單背面
- **成功**：用它 clone 成功、push 被拒
- 0922 實際：沒準備，現場臨時開了 classic 權杖，當天已刪除（F-11）

## 4. 進院當天：抵達到主機前面

### H-01 最後檢查

- **做什麼**：出門前 30 分鐘照打包清單逐項確認；最容易漏的五樣：隨身碟（只有兩個檔案）、印出來的五份文件＋交付單＋指令小抄、空白筆記本與兩支筆、充飽電的手機、寫著三組機密值的紙
- **成功**：五樣都在身上
- 🧪 彩排沒有這一步

### H-02 報到

- **做什麼**：依院方規定報到、領識別證、簽訪客登記
- **成功**：進得去；被要求登記的隨身物品記下來（Q-29 的答案之一）
- 🧪 彩排沒有這一步

### H-03 找到那個有權限的人

- **做什麼**：找資訊室聯絡人，確認「操作主機時您會全程在旁邊嗎」
- **成功**：有一位有主機管理員權限的人答應全程在旁，由他輸入密碼
- 🧪 彩排是自己一個人做

### H-04 開場三句話，然後把問題問完

- **做什麼**：講清楚今天要做什麼（全程不需要對外網路、自帶執行期、要建服務帳號、加防毒排除、開三個連接埠），再把 Q-27 九題、Q-29 六題、另外三題（主機固定位址、平板採購、外來筆電）一次問完；容器路線加 D-03 那 9 題
- **成功**：每一題都有答案或寫「未答覆」與對方是誰
- 🧪 彩排沒有這一步

### H-05 掃毒（DEP-26 第二次）

- **做什麼**：隨身碟送掃描站，或在主機上用院方防毒掃一次
- **成功**：結果乾淨並留存（紙本或單號）
- 🧪 R-03 只演練用隨身碟複製，沒有掃毒站

### H-06 確認這是對的那台機器

- **做什麼**：`hostname`、`systeminfo`、`Get-TimeZone`、`Get-Volume`
- **成功**：x64、記憶體 64GB 等級、兩顆 SSD 都有空間、時區 `Taipei Standard Time`
- 🧪 R-01 確認機器乾淨、R-09 確認時區

### H-07 盤點這台機器上原本有什麼

- **做什麼**：列出監聽中的埠、未停用的排程工作、`node -v`
- **成功**：知道哪些埠被佔、有哪些常駐工作、有沒有全域 Node.js
- 🧪 R-01 要的是 `node -v` 失敗；院內有全域 Node.js 不要用它也不要動它

## 5. 路線分岔

### H-08 路線 A：讓它失敗，並把失敗記下來

- **做什麼**：`git clone`、`npm install`，每一步計時、抄錯誤原文（步驟在《[安裝包路線](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-installer/index.md)》）
- **成功**：每一步都失敗，錯誤原文與耗時都抄下來
- 岔路：`git clone` 成功 → 《[安裝包路線之六](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-installer-git-clone/index.md)》G-01；**院方指定 clone 之後用 Docker 部署 → 第 6 節 D-05**
- 🧪 R-02 斷網，彩排不做路線 A
- 0922 實際：院方當天要求以容器部署，走第 6 節；主機連得到院外，路線 A 的前提不成立（F-07）

### H-09～H-13 路線 B：安裝包

- **做什麼**：解壓並核對雜湊、建 `.env`、套用遷移、建服務帳號、註冊服務並啟動（《[安裝包路線](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-installer/index.md)》）
- **成功**：排程工作 Running、執行身分是服務帳號、3 個行程、存活檢查 200
- 🧪 R-04、R-08、R-10、R-07、R-11、R-12
- 0922 實際：沒走這一段

下一份：《[第一次進院（0922）· 部署本系統（第 2 份，D-05～D-26、H-14～H-24）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-1-system-2/index.md)》

## 版本歷程

| 定版 | 日期 | 異動 |
| ---- | ---- | ---- |
|      |      |      |

[← 回部署手冊目錄](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/index.md)
