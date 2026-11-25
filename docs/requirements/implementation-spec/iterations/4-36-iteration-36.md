# 實作規格書 4.36 迭代 36：護理端意見表單連結（含 36.1）

上層文件：《[實作規格書](../../implementation-spec.md)》第 4 章

## 摘要

- 範圍：迭代 36 護理端意見表單連結與 36.1 容器重新啟動策略改 `always`；兩者都沒有相依，做好進下一個 tag，院內換版後才生效
- 4.36（1125 規劃、完成）：FR-N23 第一段，營運參數「意見表單網址」預設空白、只收 `https://`；護理端專業版與簡易版各一個「意見」入口，網址空白就不出現、新分頁開啟且不帶任何參數；後端與畫面都不連該網址，`check:egress` 為 0 筆；病人端拿不到
- 4.36 驗收：`verify:iteration36` 七步與 `:api` 五步通過，護理端 1366×768 與 1280×800 截圖看過；院內能不能開外部表單看 Q-42 第 5 題，開不了就不填網址
- 4.36.1（36.1，1126 完成）：`api`、`nurse-web`、`patient-web`、`hospital-api-sim`、`ai-gateway`、`speech-gateway` 六個常駐服務的 `restart` 由 `unless-stopped` 改 `always`，一次性工作不動，`check:container` 新增檢查
- 4.36.1 代價：`docker compose stop` 暫停期間若 Docker 重新啟動，服務會自己回來，備份與還原期間不要重開 Docker Desktop，要不回來一律 `down`
- 4.36.1 實測：開發機停了再開 Docker Desktop 三個服務自己回來、對照組不回來；沒做的是 Windows 真的重新開機（ST-09，院內）與護理端紅框消失時間，且 `always` 管不到沒人登入 Windows 的情形

## 4.36 迭代 36：護理端意見表單連結（1125 新增）

> 來源：1125 開會醫師建議（清冊 Q-42 第 1 題）：護理師上班不能用手機，系統放表單連結比掃 QR code 成本低。SRS FR-N23 第一段、0.13 第 1 列；做法規劃在《[護理師回饋](../../../notes/nurse-feedback-plan.md)》6.1。**1125 使用者開口、同日做完**（做法與驗收現況在本節最後）。

**範圍**：

| # | 改什麼 | 36 |
|---|---|---|
| 1 | 營運參數 | 新增「意見表單網址」，預設空白；只收 `https://` 開頭、500 字以內；改的時候照其他營運參數填理由、寫稽核 |
| 2 | 護理端入口 | 專業版導覽列最右側固定區（使用者名稱旁）、簡易版登出旁，一項「意見」；**網址空白就不出現**；不進主列（設計基準 N-2）、不主動跳出、沒有紅點 |
| 3 | 點了 | 新分頁開那個網址（`target="_blank"`、`rel="noopener noreferrer"`），不帶任何參數：不附病人、床號、帳號、畫面名稱 |
| 4 | 零院外連線 | 網址只存在營運參數，程式、`.env` 範本、映像檔裡都沒有；後端與前端都不去抓它（不預覽、不檢查連不連得上）；`check:egress` 照舊 0 筆 |
| 5 | 誰看得到 | 所有登入的護理端角色；病人端沒有 |

**實作時要確認的**：

- 營運參數放在哪一組、網址欄的驗證錯誤怎麼寫（給護理長看，不寫技術字）；改了之後護理端多久看到（首頁資料或設定的推送）
- 入口的圖示與字樣先登記進《介面設計基準》與 `hd-uiux`；簡易版的登出旁有沒有位置（1366×768 與 1280×800 都要看）
- 導覽版位設定（FR-S11）要不要多一項：網址空白就不出現已經等於關，傾向不加
- 驗收：`verify:iteration36`（網址驗證、空白不出現）與 `verify:iteration36:api`（營運參數讀寫、稽核、護理端拿得到網址、病人端拿不到）；測試手冊分冊預定 `at`，護理端照 1366×768 截圖

**排在哪裡**：沒有相依，做好進下一個 tag。院內能不能用看護理站電腦開不開得了外部表單（Q-42 第 5 題），開不了就不填網址、入口不出現，不必回退。上線一個月後看表單與紙卡收得如何，再決定 FR-N23 第二段排不排、紙卡留不留。

**做法（1125）**：

- 共用（`packages/shared/src/operations.ts`）：營運參數多一組「文字參數」`OperationalTextSettingKey`，目前只有 `NURSE_FEEDBACK_FORM_URL`（意見表單網址、500 字）；網址檢查 `feedbackFormUrlProblem` 前後端共用：空白可以存（等於關掉）、只收 `https://`、不能有空白與換行、不能帶帳號密碼、要有帶點的網域
- 第 1 列：存在 `operational_settings` 新加的 `text_value` 欄（遷移 `20261127120000_iteration36_feedback_form_url`，只加一欄；文字參數那一列 `value` 固定 0），整數參數的清單與 `valueOf` 讀不到它；資料取出歸「一般」。改的時候要理由、寫稽核（沿用「營運參數變更」，寫新舊值，空的寫「空白」）。端點 `GET`／`PUT /api/operational-text-settings[/:key]`，要營運參數的管理權限
- 第 1 列（畫面）：系統管理「營運參數與選項清單」分頁最上面多一張「意見表單網址」卡（`SystemFeedbackFormCard.tsx`）：網址框、理由框、儲存；不合格的按不下、底下寫原因；提醒先在護理站電腦點一次網址
- 第 2、3 列：`apps/nurse-pwa/src/feedback-link.tsx` 的 `FeedbackLink`，專業版放右上角「系統管理」與「變更密碼」之間、簡易版放登出左邊（`.wb-feedback`，與登出同樣的按鈕框）；網址空白就不畫；`<a target="_blank" rel="noopener noreferrer">`，網址照存的原樣
- 第 3 列（拿網址）：`GET /api/nurse-feedback-link` 只回 `{ url }`，所有登入的護理端帳號都拿得到（含唯讀角色），平板的身分拿不到；讀出來再檢查一次，資料庫裡的壞網址回 `null`。改了之後同一台電腦立刻看到、別台一分鐘內或切回視窗時看到
- 第 4 列：後端與畫面都不去連那個網址；程式、`.env` 範本、compose 檔沒有任何表單網址；`check:egress` 0 筆
- 實作時要確認的四題：參數放在營運參數分頁、驗證錯誤用給護理長看的話（例：「網址要以 https:// 開頭（表單服務的分享連結都是）」）；入口只用字「意見」、不加圖示（旁邊的「系統管理」「變更密碼」「登出」都是字），登記在《介面設計基準》3.2 與 `hd-uiux`；簡易版 1366×768 與 1280×800 都放得下、不捲動；導覽版位不加一項（網址空白就等於關）

**驗收現況（1125）**：`npm run verify:iteration36` 七步全部通過（網址檢查實際跑；文字與整數參數分開；入口沒填不出現、新分頁、不帶參數、只在最右側固定區；系統管理同一個權限、要理由；零院外連線；病人端拿不到；遷移只加一欄、資料取出登記、介面檢查與迭代 14、17.2、17.6）；`npm run verify:iteration36:api` 五步全部通過（全新資料庫：預設空白；六種不合格的寫法擋下、沒填理由擋下；存了之後稽核與護理端拿到的網址；一般護理師與醫院管理層拿得到、一般護理師改不了、沒登入與平板拿不到；資料庫裡的壞網址不出現、清空、整數參數照舊）。回歸：`verify:iteration14:api`、`17-8:api`、`27-1:api`、`33:api`、`check:all` 通過。手動測試在《[迭代 36](../../../testing/iteration-36.md)》（`at1`～`at12`）。院內要換到含迭代 36 的 tag 才有，填網址前先確認護理站電腦開得了（Q-42 第 5 題）

**與上面範圍表不同的地方**：

- 第 2 列寫「使用者名稱旁」：專業版右上角原本的順序是名稱、系統管理、變更密碼、登出，「意見」放在系統管理與變更密碼之間（還是那一區）
- 第 5 列寫「所有登入的護理端角色」：唯讀角色（醫院管理層、稽核、社工、醫師）的端點預設全擋，這一支明確放行（回應只有網址，沒有病人資料）


## 4.36.1 迭代 36.1：容器的重新啟動策略改成 `always`（1126 新增，1126 完成）

> 來源：1116 第五次進院前的開發機演練 SY-07（《[部署演練紀錄](../../../notes/deployment-drills.md)》11.2）：Quit Docker Desktop 再開，`docker ps -a` 全是 `Exited`，服務沒有自己回來。Docker Desktop 在 Quit 時先逐一停掉容器、引擎才關，容器被當成「手動停止」，`restart: unless-stopped` 就不再啟動它。1116 定為已知限制、`v0.5.0` 照帶，等院內重新開機實測（ST-09）再議；院內 1116 沒做重新開機。**1126 使用者改定不等實測**（0.12 第 9 列、《[院內主機現況](../../../deployment/ref-status.md)》ST-24）。

**範圍**：

| # | 改什麼 | 現況 | 36.1 |
|---|---|---|---|
| 1 | 常駐服務的 `restart` | `docker-compose.yml` 的共用區塊 `x-app`（`api`、`nurse-web`、`patient-web`，與只在模擬部署起的 `hospital-api-sim`）、`ai-gateway`、`speech-gateway` 都是 `unless-stopped` | 全部改成 **`always`** |
| 2 | 一次性工作 | `data-export`、`shell-builder` 是 `"no"` | **不動**（`check:container` 照舊要求 `data-export` 是 `"no"`） |
| 3 | 檢查 | `check:container` 只查 `data-export` 的 `restart` | 加一條：上面六個常駐服務一定是 `always`，寫錯擋下 |
| 4 | 部署手冊的常備參考 | 寫 `unless-stopped` 與「暫停之後不會自己起來」 | 照 36.1 改寫；已發出的進院冊與紀錄不改（是既成紀錄） |

**兩種策略差在哪裡**（Docker 的規則；第 2、3 列要在開發機實測）：

| 情形 | `unless-stopped`（`v0.5.0`） | `always`（36.1） |
|---|---|---|
| 1 容器自己當掉 | 重新啟動 | 重新啟動 |
| 2 Quit Docker Desktop 再開、重新開機後有人登入 Windows | **不回來**（1116 實測） | 回來 |
| 3 `docker compose stop` 暫停之後，Docker 重新啟動 | 不回來 | **回來** |
| 4 `docker compose stop` 暫停之後，Docker 沒重新啟動 | 不回來 | 不回來 |
| 5 `docker compose down` 之後 | 不回來（容器刪掉了） | 不回來（容器刪掉了） |
| 6 沒人登入 Windows | 不回來 | 不回來（Docker Desktop 根本沒起來，DEP-21 第 4 項） |

**實作時要確認的**：

- 第 3 列的情形：暫停（備份、還原、資料修補、換版）期間主機重新開機或 Docker Desktop 重開、自己更新，`api` 會在作業做到一半時回來。《[備份、還原與關服務](../../../deployment/ref-backup-shutdown.md)》0.2 的「暫停」那一列照改，暫停期間不要重開 Docker Desktop；要它不回來一律 `down`（0.2「停用」本來就是 `down`）
- `db-update`、資料庫遷移是 `docker compose run --rm` 的一次性容器，`run` 不套服務的 `restart`；實測時 `docker inspect` 確認
- 迭代 32.3 的驗收腳本比對 compose「註解以外一行都沒動」，36.1 改了 `restart`，要讓它照樣通過（做法見本節最後）
- 驗收：`check:container` 新規則；開發機重做 SY-07（Quit Docker Desktop 再開，三個服務自己回來、護理端紅框消失，量幾分鐘）與上表第 3～5 列；測試手冊沿用迭代 36 的分冊 `at`，接 `at13` 起

**排在哪裡**：沒有相依，做好進下一個 tag（與 32.2～36 同一個）。院內換版後 SY-07 照部署手冊重做；院內重新開機實測（ST-09）照舊要院方准，結果寫進交接紙。

**做法（1126）**：

- 第 1 列：`docker-compose.yml` 的 `x-app` 與 `ai-gateway`、`speech-gateway` 三處改 `restart: always`，`x-app` 上面寫為什麼與代價；設定的其他行都沒動
- 第 2 列：`data-export`、`shell-builder` 照舊 `"no"`
- 第 3 列：`check:container` 加一條「常駐服務的重新啟動策略都是 always」，六個服務（含只在設定檔裡的 `ai-gateway`、`speech-gateway`、`hospital-api-sim`）任一個不是 `always` 或不見了就擋
- 第 4 列：常備參考與 `notes/` 的部署路線比較照改；已發出的進院冊與紀錄沒動
- 迭代 32.3 的驗收腳本：第 3 步原本拿**現在的** compose 比 32.3 開工前，迭代 34 加語音閘道之後這一步就一直沒過（1126 才發現，不是 36.1 造成的）；改成比 32.3 那一個 commit（`a95ece2`）與開工前，驗的還是「32.3 只改註解」

**驗收現況（1126）**：`check:container` 沒有阻擋項、新的那一條通過；`verify:iteration32-3` 四步全部通過。開發機實測（Docker Desktop 29.6.1，`v0.5.0` 映像檔配 master 的 compose，模擬部署三個服務；做完 `down`、刪掉演練用的資料卷）：

| 上面那張表 | 怎麼做 | 結果 |
|---|---|---|
| 第 2 列 | `docker desktop stop` 再 `docker desktop start`，不下 `up` | **三個服務自己回來**，Docker 起來 12 秒後 `/api/health` 回 200 |
| 第 2 列對照 | 同一套加一份把 `restart` 蓋回 `unless-stopped` 的設定檔，同樣停了再開 | 全部 `Exited (0)`，與 1116 相同：差別在策略，不在停 Docker 的方法 |
| 第 4 列 | `docker compose stop`，等 20 秒 | 全部 `Exited (0)`，沒回來 |
| 第 3 列 | 接著停了再開 Docker Desktop | **三個服務回來了**（`always` 的代價，照預期） |
| 第 5 列 | `docker compose down`，停了再開 Docker Desktop | 沒有任何容器 |
| 一次性容器 | `docker compose run -d --rm --no-deps api …` 時 `docker inspect` | 策略 `no`、`AutoRemove=true`：`db-update`、遷移不受影響 |

沒做的：從通知區按 Quit（這次用的是 `docker desktop stop`，同樣是先停容器再關引擎，對照組的結果與 1116 按 Quit 相同）；Windows 真的重新開機（ST-09，院內）；護理端紅框消失的時間沒量，只量後端健康檢查。手動測試在《[迭代 36](../../../testing/iteration-36.md)》§36.4（`at13`～`at17`）。院內換到含 36.1 的 tag 才生效。

---

[← 回實作規格書](../../implementation-spec.md)　[← 回進度首頁](../../../index.md)
