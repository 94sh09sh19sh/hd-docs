# 血液透析平板照護輔助系統 — 技術進度報告

**適用讀者**：接手或協作的工程師
**報告日期**：2026-10-07
**版本**：迭代 17.5 完成（master）
**Repo**：`94sh09sh19sh/hd-tablet-care`

> 本版由 0930 定版（迭代 14.5 時點）改寫。0930 之後的主要變化：
> **1001 第二次進院 B 級部分成功**——容器在院內主機上起來，護理端登入 `Failed to fetch`（`CORS_ORIGINS` 不放行護理端的來源），見部署手冊第十四冊之四、第十五冊之三；
> **1005 新版需求**：院方透析清單 API 全面取代手動輸入、輪播換成「本次透析」面板與跑馬燈、跑馬燈內容 AI 生成護理師核准，排成**迭代 15～17，同日完成**（實作規格書 0.5、4.13～4.15）。
> 三個迭代都在模擬院方 API 上驗收；院方 API 的實際長相要第三次進院以探測工具看一次（實作規格書 4.19）。
>
> 0909 之後的完整脈絡：需求於 0910 改為 v2.0（SaMD 三項改為有條件納入、資料庫改 SQLite、封閉網路）；迭代 3～6 完成資料層遷移、AI 輔助內容、求助處理與班表、閒置輪播與檔案匯入；
> 迭代 7～10 是第一次進院前的缺陷修正、介面重做、內容資料化與安裝包；**0922 第一次進院失敗之後**，迭代 11～14 把交付方式換成 Docker ＋ `git clone`、外殼 App 搬到獨立 repo、新增 Python 的 AI 閘道、介面極簡重設計，14.1～14.5 是實際操作後的修正。
> 迭代編號在 0919、0926、1005 各重排一次：原「規則引擎」與「管理儀表板」現在是**迭代 18、19**，對照表見實作規格書 4.0.1、4.0.3、4.0.4。

---

## 1. 專案脈絡

需求來源在 `docs/requirements/`，共六份文件。前五份**優先權不同，衝突時有明確的裁決順序**：

| 文件 | 角色 |
|---|---|
| [`srs.md`](../requirements/srs.md) | 功能需求來源（FR 編號皆引用自此）。v2.0 共六組：P 病人端、N 護理端、M 管理與營運、X 對外揭露、S 系統、R 高風險控制措施 |
| [`implementation-spec.md`](../requirements/implementation-spec.md) | 範圍界定、技術棧與迭代 3～19 規劃，**衝突時以此為準** |
| [`database-policy.md`](../requirements/database-policy.md) | 資料治理強制規則，**優先權等同實作規格書** |
| [`deployment-spec.md`](../requirements/deployment-spec.md) | 部署形態、環境界線與交付方式（0912 新增，0926 改版為 v3.0：Docker ＋ `git clone`），**優先權等同實作規格書** |
| [`fde-assessment.md`](../requirements/fde-assessment.md) | 背景脈絡與選型理由 |
| [`open-questions.md`](../requirements/open-questions.md) | 唯一的待確認事項總表（Q-01～Q-36）。程式裡的暫定值多半對應其中一項 |
| [`../notes/uiux-design-baseline.md`](../notes/uiux-design-baseline.md) | 介面設計基準（0919 新增，0927 改為極簡方向）。**動介面前先讀**，可執行版在 `.claude/skills/hd-uiux/` |
| [`../reference/kiosk-shell-contract.md`](../reference/kiosk-shell-contract.md) | 病人端外殼 App 契約（0927 新增）。外殼在另一個私人 repo，兩邊只靠這一份帶版本號的契約對齊 |

動工前請至少讀完前三份。這個專案有不少「看起來繞路」的設計，幾乎都源自這些文件的硬性約束。系統實體與邏輯架構見[架構圖](../requirements/architecture-diagrams.md)（**2026-09-29 依 0926 改版重繪**：應用伺服器改為 Docker 容器・`git clone`，後端與 AI 推論端點之間多一格 AI 閘道服務，過渡期的線改為「開發機 → SSH 通道 → 實驗室個人容器裡的 AI 閘道」，並把建置期才有的對外連線與執行期零連外分開畫；**1005 補上迭代 15、16**：臨床資料匯入改標院方資料同步、平板多一條院內 SSE，兩張圖都只改標籤）。圖片走 repo 相對路徑，文件站上就是 repo 裡的這兩個檔案。

---

## 2. 架構

```
v0/
├── apps/
│   ├── api/            NestJS — 後端唯一入口：身分驗證、裝置綁定、症狀回報、緊急通報、
│   │                            即時狀態、稽核、MDM／模型／臨床資料三個介面層、功能開關、
│   │                            備份、背景佇列、衛教、回饋、護理記錄、適足性、SOP 查詢、
│   │                            院方資料同步（迭代 15）、病人端首頁的面板與跑馬燈（迭代 16）；
│   │                            另有模擬院方 API 與探測工具兩支獨立進入點（迭代 15）
│   ├── nurse-pwa/      React PWA — 護理站主控台（專業版）、簡易版工作台（simple/）與常駐總覽螢幕（:5173）
│   └── patient-pwa/    React PWA — 病人端平板 Kiosk，裝在外殼 App 裡（:5174）
├── packages/
│   └── shared/         前後端共用型別、常數與業務規則（@hd/shared），含外殼契約 kiosk-shell.ts
├── services/
│   ├── ai-gateway/     Python（FastAPI ＋ LangChain）— 後端與推論端點之間的轉送，迭代 13
│   └── shell-builder/  在院內主機上離線建置、簽章外殼 APK 並寫下載頁，迭代 12；shell.pin 釘住外殼版本
├── deploy/             hospital.env.example — 院內部署的設定範本（只列容器需要的變數）
├── Dockerfile、docker-compose.yml   正式部署與開發機部署實測共用，迭代 11
├── scripts/            盤點腳本（check:*）、圖示與字型產生、文件站同步
└── docs/               需求、報告、參考、測試與部署文件
```

npm workspaces monorepo，另有兩個容器服務。約 58,500 行 TypeScript（版控內全部 `.ts`／`.tsx`，含驗收腳本與產生的圖示資料；用同樣的計數方式，0930 時約 50,800 行、0923 時約 44,600 行）＋約 900 行 Python（AI 閘道）。
compose 另有一個只在 `simulation` 設定檔才起來的 `hospital-api-sim`（模擬院方 API，與 `api` 同一個映像檔，不開埠）。
外殼 App（Kotlin）在另一個私人 repo `hd-kiosk-shell`，本 repo 以 `services/shell-builder/shell.pin` 釘住它的 tag（目前 `v0.3.0`）。

**技術棧**：NestJS 11 · Prisma 6 · SQLite（測試與正式皆同）· React 19 · Vite 6 · TypeScript 5.7 · dnd-kit（簡易版拖曳）· Lucide 圖示與 Noto Sans TC 子集（自帶，不經 CDN）
**部署與周邊**：Docker ＋ compose（專案名稱固定 `hd-tablet-care`，資料與金鑰兩個 external 資料卷）· AI 閘道 Python ＋ FastAPI ＋ LangChain · 外殼 App Android（Kotlin）

### 資料流

```
病人端 PWA ─┐                   ┌─→ Repository 層 ─→ Prisma ─→ SQLite 檔案（專案目錄外）
            ├─→ 後端 API ───────┤
護理端 PWA ─┘  （SSE 回推）     ├─→ AiGatewayService ─→ LlmProviderPort ─→ mock
                                │                                       └─→ lab／onprem ─→ ai-gateway 容器 ─→ 推論端點
                                └─← HospitalSyncService ←─ 院方透析清單 API（每 3 分鐘、唯讀）
                                                         └ 開發與模擬部署：hospital-api-sim
```

**前端一律不直接碰資料庫，也不直接碰模型。** 兩個 PWA 都沒有資料庫或模型相關套件；後端是唯一開啟資料庫檔案的常駐寫入行程，也是唯一呼叫模型的地方。
**0927 起後端也不直接連推論端點**（DEP-41）：`lab`／`onprem` 一律打 AI 閘道，模型名稱只寫在閘道的 `config.yaml`。
病人端的正式建置與後端同一個來源：`patient-web` 以伺服器憑證提供 HTTPS，並把 `/api/` 轉送給 `api`（迭代 12），外殼只需信任一張院內 CA。
**1005 迭代 15 起院方 API 由後端拉取**（本系統不回寫院方任何資料）；同步寫入的每一筆都走與護理師操作相同的服務，見 5.21。平板除了原本每 3 秒的輪詢，另訂閱 `GET /device/stream`（SSE，事件只通知「有新資料」、不帶數值）。

---

## 3. 七條不可違反的約束

前五條出自《資料庫使用規範》，後兩條出自 SRS v2.0 的 FR-S07 與 FR-S03／S06。動任何一處之前先確認不會踩到：

| # | 約束 | 為什麼 | 現況 |
|---|---|---|---|
| 1 | **前端不得直接碰資料庫** | 授權與驗證只能發生在後端 | 兩個 PWA 只呼叫後端 REST |
| 2 | **身分驗證一律自建** | 病人不登入的身分模型與任何託管身分服務都不合；託管服務也都在院外 | 自建 JWT ＋ `nurse_sessions` 表（可主動作廢）；病人端用裝置綁定核發的 Session Token |
| 3 | **存取控制寫在後端應用層** | 授權必須可追溯到「哪位護理師、何時、為哪位病人」，要在自己可掌控的程式碼裡 | 全部在守衛 ＋ service 層；唯讀角色由全域守衛預設全擋 |
| 4 | **不得在業務邏輯中嵌入資料庫語法** | 換 ORM／資料庫時的隔離層 | `PrismaService` **只注入 Repository 層**，controller/service 一律不得取用 |
| 5 | **測試資料必須虛構** | 開發機不是院內環境；過渡期 AI 走院外實驗室 API | seed 用 faker，病歷號固定 `HD-TEST-*`；院外 provider 由 AI 閘道強制合成資料檢查 |
| 6 | **零院外連線** | 所有資料不出醫院網路（FR-S07） | `npm run check:egress` 盤點 0 筆；推播整條移除，即時通知只走院內 SSE |
| 7 | **模型呼叫一律經 `AiGatewayService`** | 去識別化、合成資料檢查、呼叫紀錄必須集中在一處，漏一處就等於沒有 | 業務模組只注入閘道，不得直接注入 provider |

額外：**即時同步不依賴任何資料庫平台功能**（第 3 條的延伸）。即時狀態快取層是行程內實作。

### 不被任何一種資料庫綁死的設計

正式環境原訂為醫院 MSSQL，0910 改為 SQLite。當初為相容 SQL Server 設下的約束全部保留，理由改為「萬一日後要遷，不要被卡死」：

- **不使用 Prisma `enum`** — 狀態欄位以字串承載，合法值由 `@hd/shared` 常數 ＋ class-validator 在應用層把關
- **不使用 JSON 欄位** — 結構化關聯資料一律正規化。例如問卷答案是獨立的 `symptom_answers` 表，護理記錄的範本勾選是獨立的 `nursing_record_fields` 表
- **不使用資料庫專屬預設值** — UUID 由 Prisma client 產生
- **控制級聯路徑** — 同一張表只留一條級聯刪除路徑，其餘外鍵一律 `NoAction`
- **不用 `Float` 承載臨床數值**（《資料庫使用規範》6.2）— 目前 schema 裡沒有任何 `Float` 欄位；適足性等計算結果以整數存

---

## 4. 資料模型

共 58 張表，13 個 migration：`init`、`iteration3_closed_network`、`iteration4_ai_content`、`iteration5_help_resolution_shifts_baseline`、`iteration6_carousel_file_import`、`iteration7_update_runs`、`iteration9_navigation_content`、`iteration9_help_category_label`、`iteration10_kiosk_foreground`、`iteration12_kiosk_shell_version`、`iteration14_beds`、`iteration15_hospital_api`、`iteration17_marquee_approval`（前五個是 SQLite 遷移時整組重建的，舊資料依《資料庫使用規範》第 15 條不搬；迭代 7 起一律只做加法，`check:migration` 把關）。逐欄說明見《[資料字典](../reference/data-dictionary.md)》。

| 分類 | 表 | 加入於 |
|---|---|---|
| 帳號與登入憑證 | `nurses`、`nurse_sessions` | 迭代 1 |
| 主檔 | `patients`、`devices` | 迭代 1 |
| 排班與綁定 | `treatment_sessions`、`device_bindings` | 迭代 1 |
| 稽核軌跡 | `audit_logs` | 迭代 1 |
| 病人自述內容 | `symptom_reports`、`symptom_answers`、`help_requests` | 迭代 2 |
| 系統治理 | `feature_flags`、`ai_invocations`、`backup_runs` | 迭代 3 |
| 院方臨床數值 | `clinical_value_imports`、`clinical_values` | 迭代 3 |
| 背景佇列 | `ai_jobs` | 迭代 4 |
| 衛教、測驗與回饋 | `education_contents`、`education_completions`、`quiz_attempts`、`quiz_answers`、`feedback_responses`、`feedback_answers` | 迭代 4 |
| 護理記錄與計算 | `nursing_records`、`nursing_record_fields`、`adequacy_calculations` | 迭代 4 |
| SOP 文件與查詢 | `sop_documents`、`sop_sections`、`sop_queries`、`sop_query_citations` | 迭代 4 |
| 求助處理與可設定暫代值 | `help_resolution_options`、`operational_settings`、`help_request_follow_ups` | 迭代 5 |
| 護理師班表與成效基準 | `nurse_shifts`、`shift_bed_assignments`、`shift_change_requests`、`baseline_measurements` | 迭代 5 |
| 閒置輪播與檔案匯入 | `carousel_items`、`carousel_view_events`、`import_field_mappings` | 迭代 6 |
| 版本更新紀錄 | `update_runs` | 迭代 7 |
| 導覽版位 | `nav_placement_settings` | 迭代 9 |
| 求助類別與處理方式 | `help_categories`、`help_request_methods` | 迭代 9 |
| 透析前問卷（版本化） | `questionnaire_versions`、`questionnaire_items`、`questionnaire_item_options`、`questionnaire_item_triggers`、`symptom_answer_options` | 迭代 9 |
| 衛教題庫（版本化） | `quiz_topics`、`quiz_bank_versions`、`quiz_bank_questions`、`quiz_bank_question_options` | 迭代 9 |
| 回饋題目（版本化） | `feedback_form_versions`、`feedback_form_items` | 迭代 9 |
| 床位與輪播播放範圍 | `beds`、`carousel_item_targets` | 迭代 14 |
| 院方資料同步 | `hospital_api_fetch_runs`、`dialysis_vital_records` | 迭代 15 |

迭代 10、12 沒有新表，只在 `devices` 加欄位：前景回報三欄（迭代 10）、`shell_version` 與 `shell_contract_version`（迭代 12）；迭代 14 另加 `devices.bed_no`。
迭代 15 除了兩張新表，另加 `patients.preferred_device_id`（配給病人的平板）、`treatment_sessions` 五欄（`source`、`bed_no`、`expected_end_at`、`nurse_modified_at`、`bed_nurse_modified_at`）與 `beds.source`；
迭代 16 沒有動 schema（跑馬燈播放紀錄沿用 `carousel_view_events`）；迭代 17 在 `carousel_items` 加七欄（核准狀態、核准者、核准時間、生成它的背景工作、公告事由、衛教主題、來源）。全部只做加法。

### 值得注意的地方

| 表 | 值得注意的地方 |
|---|---|
| `nurses` | `role` / `status` 為字串；`canApproveNurses` 支援單獨分享審核權限 |
| `nurse_sessions` | 存 JWT 的 `jti`，讓 token **可被主動作廢**（變更密碼、降權時） |
| `devices` | `apiKeyHash` 用 SHA-256（金鑰是 256-bit 隨機值，非使用者密碼）；MDM 狀態欄位。`bed_no`（迭代 14）＝平板貼在哪一床，**病人本身不存床號**：病人在哪一床＝他那台平板在哪一床 |
| `treatment_sessions` | `@@unique([patientId, scheduledDate, shift])` |
| `device_bindings` | 綁定「病人＋平板＋療程時段」三者；`sessionTokenId` 存 jti，token 本身不寫入資料庫 |
| `symptom_reports` | `clientReportId` **唯一鍵** → 離線補傳的冪等保證；`reportedAt`（病人填寫時間）與 `receivedAt`（伺服器收到）分開存 |
| `help_requests` | `clientRequestId` 唯一鍵防重複；`routedTo` 記錄當下計算的分派結果供事後稽核 |
| `audit_logs` | 關聯欄位皆正規化為外鍵；另冗餘記錄 `actorLabel`、`deviceSerialNo`，避免帳號日後異動導致軌跡失真 |
| `ai_invocations` | 每次模型呼叫一列（provider、模型、耗時、是否去識別化、是否被擋）。迭代 4 的每一份 AI 產出都要能追回對應的一列 |
| `clinical_values` | 每筆帶資料時間；覆蓋時保留前一版 |
| `ai_jobs` | 重新啟動時仍在執行的工作標為失敗，不會卡在「產生中」 |
| `nursing_records` | 簽核後不可改；記下起點（AI 初稿／預填／手寫）與 AI 初稿的處置（原樣採用／修改後採用／未採用） |
| `adequacy_calculations` | 結果以整數存，並指回五筆原始 `clinical_values`；記公式版本 `DAUGIRDAS2-SPKTV-v1` |
| `quiz_attempts`、`education_contents`、`feedback_responses` | 記下當時的題庫、主題、規則版本字串；暫定內容換掉後舊紀錄仍可回溯 |
| `help_requests` | 迭代 5 擴充五欄。`arrivedAt` 與 `acknowledgedAt` **是兩個獨立欄位，不互相填補**——理由見 5.15 |
| `help_resolution_options`、`operational_settings` | Q-13／Q-14 的暫代值存這裡，不寫死在程式。停用選項不刪列，既有紀錄才查得到文字；`operational_settings.updatedAt` 可為空，空＝從未被改過 |
| `nurse_shifts` | 起訖時間逐筆存，不由班別反推（跨日班與臨時調整都靠它）；取消不刪列。屬 L2，一般護理師只查得到自己的 |
| `baseline_measurements` | **只新增不覆寫**，舊版標 `superseded` 保留；估算值（`source=ESTIMATED`）在所有畫面帶警告；背書者必填 |
| `carousel_view_events` | **沒有病人、綁定、平板或卡片內容欄位**，這是刻意的（見 5.19）。要做個人層級的閱讀分析前，先回頭讀規範第 11 條 |
| `import_field_mappings` | 檔案欄位名稱是資料不是程式；`(profile_code, target_field)` 唯一。兩個目標欄位不得同時對應到同一個檔案欄位，設定時就擋下 |
| `backup_runs` | `sha256` 存完整雜湊；0929 起同一串另寫在 `BACKUP_DIR` 裡的 `<檔名>.sha256`（格式同 `sha256sum`）。**資料庫壞掉、服務起不來時這張表就查不到**，還原時的雜湊從那個檔拿 |
| `beds` | 床位清單是資料（系統管理可改）。~~預設 15 床~~ 1005 迭代 15 起全新環境不預設，院方資料出現的床號自動加進來（只新增、不再啟用停用的床）。有病人正在治療的床拿不掉，否則那位病人會從床位圖上消失 |
| `treatment_sessions` | 迭代 14.2 起可「重新開啟」：今天已下機或已取消的療程回到已排班、`ended_at` 清空，**沿用同一筆**（唯一鍵不動），當天的症狀回報與求助仍掛在它底下 |
| `treatment_sessions` | 迭代 15：`source` 分人工與院方；`expected_end_at` 只當「預計結束」，**不拿它判定下機**（可能是預排值，院方欄位要第三次進院確認；1007 迭代 17.5 起只記錄，透析一律開始後四小時結束）；`nurse_modified_at`／`bed_nurse_modified_at` 有值時，同步不再改它的狀態／床位——**護理師的更正優先** |
| `hospital_api_fetch_runs` | 每次抓取一列（結果、重試次數、筆數、被拒的透析數、耗時、是否模擬），回應只存雜湊、**不存本文**——院方回應裡有姓名與病歷號 |
| `dialysis_vital_records` | 院方每一筆血壓、脈搏與累積脫水量，掛在療程與那一次抓取底下；**只收有綁定平板的病人**，沒配平板的病人的數值不寫進資料庫 |
| `carousel_items` | 迭代 17 起 `approval_status` 是病人端唯一的閘門：`listPlayable` 只取 `APPROVED`。既有內容遷移時標為已核准，新列預設待核准 |

---

## 5. 幾個關鍵機制

### 5.1 護理端身分驗證（自建）

`.env` 的 `SUPER_ADMIN_WORK_ID` / `SUPER_ADMIN_INITIAL_PASSWORD` 只在**資料庫尚無任何使用者**時觸發 bootstrap，建立第一個 `SUPER_ADMIN` 並標記 `passwordChangeRequired`。

一般護理師以工作ID 申請 → `PENDING` → 管理者核准 → `ACTIVE` 才能登入。

登入態 = JWT ＋ `nurse_sessions` 表比對。這讓 token 可以被主動作廢：**變更密碼**與**權限縮減**都會呼叫 `revokeAllForNurse()`，避免舊 token 沿用舊權限。

登入失敗時，帳號不存在與密碼錯誤回傳**完全相同**的訊息，且帳號不存在時仍會比對一次假雜湊，讓回應時間對齊 — 不從時間差洩漏帳號是否存在。

**角色**：0910 新增護理長、醫院管理層、稽核，共六種。`HOSPITAL_VIEWER`、`AUDITOR` 是唯讀角色，由 `common/guards/read-only-role.guard.ts` **預設全擋**，只有明確標示開放給唯讀角色的端點才放行，不靠前端藏按鈕。權限碼 17 個（Iteration 2 時 9 個）。

### 5.2 裝置綁定（SRS 4.3／4.4）

九步驟完整實作。三種失效條件：正常下機、手動解除、逾時（`BINDING_MAX_HOURS` 預設 6）。

**重複綁定阻擋**在 Repository 層以 **Serializable 交易** 完成：衝突檢查與寫入在同一個交易裡，避免兩個並行請求同時通過檢查。序列化失敗（`P2034`）會退避重試最多 4 次 — 交易是原子的，中止後沒有殘留寫入，所以重試安全。

被擋下的嘗試**本身也寫稽核**（`BINDING_REJECTED_DUPLICATE_PATIENT` / `BINDING_REJECTED_DEVICE_BUSY`）。

### 5.3 病人端授權

兩層：

1. **裝置身分** — `x-device-serial` ＋ `x-device-key`（MDM 佈建時寫入 Kiosk 網址）
2. **Session Token** — 綁定核發的限時 JWT，`x-session-token`

寫入端點用 `DeviceSessionGuard`，**一次查詢同時完成兩層驗證**：綁定紀錄本身已 include device，所以裝置金鑰比對不需要再查一次 `devices` 表。

病人ID、療程時段、平板序號**一律由後端從綁定紀錄取得**，平板送上來的 body 不能指定要寫給哪一位病人。迭代 4 的衛教閱讀、測驗、回饋端點沿用同一套守衛。

### 5.4 即時狀態快取層

`modules/realtime/realtime-state.service.ts`。設計要點：

- **只服務當日**排班（透析中心的看板本來就只看當班），跨日自動重建；查其他日期直接回頭讀資料庫
- **write-through**：任何寫入方（症狀回報、求助、綁定異動、排班異動）寫完資料庫後呼叫 `refreshTreatmentSession()`，由本層重算該列並廣播
- 傳輸用 **SSE**，全程在院內。護理端以 `fetch` ＋ `ReadableStream` 消費而非 `EventSource`，因為 EventSource 無法設定 `Authorization` 標頭（用網址參數傳 token 會讓權杖出現在存取紀錄裡）
- 前端有 15 秒輪詢作為串流不可用時的保險，以及指數退避重連

**要橫向擴充時**：把 `Map` 換成 Redis hash、`Subject` 換成 Redis pub/sub，呼叫端介面不變（Redis 同樣必須在院內）。

### 5.5 離線韌性（病人端）

`offline-queue.ts` ＋ `symptom-sync.ts`。

**症狀回報：先入列、再送出。** 即使當下網路正常，也一律先寫入 IndexedDB 才發請求，成功才移除。這樣平板在請求途中斷電或被 Kiosk 重新載入，資料仍在。後端以 `clientReportId` 去重。

補傳時若綁定仍是同一筆，會改用**最新的** Session Token（避免暫存期間 token 已輪替）。

**求助不入列。** SRS 4.4 明文要求離線期間須明確提示無法通知護理站 — 讓病人誤以為已送達比誠實說明更危險。

綁定失效時：盡力補傳 → 清空佇列（平板是共用裝置，前一位病人的資料不得殘留）。

### 5.6 裝置管控介面層（0919 起不走 MDM）

`MdmProviderPort` 抽象介面 ＋ `MockMdmProvider`。所有呼叫一律經介面，業務邏輯不碰實作細節。

**0919 起這一層的語意變了，介面沒變。** 平板管控改走免 MDM 路線（自包 WebView 外殼＋Android 內建螢幕固定），
因此 `MockMdmProvider` **不再是「等著被真 MDM 換掉的模擬品」，它就是這項功能的正式實作**：
裝置佈建狀態的紀錄與稽核（FR-S01）。稽核說明欄的 `[mock]` 前綴要移除——它已經不是模擬品，
而且那個前綴會出現在護理師看得到的畫面上（FR-S10）。

原因：Android Enterprise 有三處必須連往院外（首次佈建連 Google、後端設定政策要呼叫
`googleapis.com`、遠端鎖定命令靠 FCM 送達），與封閉網路前提直接衝突。
完整選型見《[平板管控：免 MDM 的全院內方案](../notes/mdm-offline-plan.md)》。

取得 Android Enterprise 權限（Q-11）後，新增一個實作同介面的 provider 並替換 `MdmModule` 的注入即可，**其餘商業邏輯與稽核軌跡不需更動**。

**迭代 12 起外殼 App 另有契約**（見 6「迭代 12」）：前景回報多帶外殼版本、契約版本與是否釘選，護理端裝置管理據此標出「版本正常／外殼過舊／版本不相容／未回報版本」。
**迭代 14.1 補了兩件模擬 MDM 的事**：`MdmProviderPort` 新增 `simulated` 與選用的 `restoreDevice`，後端啟動時把資料庫的納管狀態交回模擬 MDM（不分環境；否則重新啟動後已納管的平板鎖不了、解不開）；開發環境另外自動納管 seed 的平板，照樣經介面、照樣寫稽核，**正式環境不做**。

### 5.7 SQLite 連線與唯讀通道（迭代 3）

- 連線時套用並回讀四項必開設定（`journal_mode=WAL`、`foreign_keys=ON`、`busy_timeout=5000`、`synchronous=FULL`），缺一項就拒絕啟動
- **寫入連線固定一條**：實測 Prisma 預設連線池有多條連線時，事後下的 PRAGMA 只會落在其中一條
- 統計、報表、稽核查詢、AI 呼叫紀錄、備份歷程清單走 `query_only` 的唯讀連線，不與臨床寫入競爭
- 資料庫檔案與 `BACKUP_DIR` 必須在**專案目錄外的本機磁碟**；相對路徑、專案目錄內、網路路徑、雲端同步資料夾，後端與 seed 一律拒絕啟動
- Prisma CLI 以 `CHECKPOINT_DISABLE=1` 關閉使用統計回報，否則 `prisma generate` 會連到院外

### 5.8 功能開關中心（FR-S08，迭代 3）

`modules/feature-flags/`，定義在 `shared/platform.ts`。

- 迭代 3 的十個開關：高風險三項（`RISK_STRATIFICATION`、`INTRA_DIALYSIS_ALERT`、`DOSE_REFERENCE`）、AI 兩項（`AI_FEATURES`、`REAL_PATIENT_DATA_TO_AI`）、輪播三層、績效兩項（`PERF_INDIVIDUAL_L3`、`REWARD_SCORING`）。**全部預設關閉**。之後又加三個：迭代 9 的 `HANDHELD_FEATURES`，迭代 14.2 的 `HELP_NON_CLINICAL_GROUP`（求助畫面顯示「其他」那一框，預設關閉），1005 的 `LAB_VALUE_FEATURES`（需要抽血數值的功能：透析適足性，預設關閉；院方透析清單 API 沒有抽血數值）。
  **1005 迭代 16**：輪播三層停用（`RETIRED_FEATURE_FLAG_KEYS`，資料表的列與切換紀錄保留、後端載入時略過），換成 `TODAY_PANEL`（「本次透析」面板，**預設開啟**——9.1 起「預設全關」的唯一例外由它承接）與 `MARQUEE`（跑馬燈，預設關閉，速度要先經長者看過）
- **`HELP_NON_CLINICAL_GROUP` 是唯一不擋後端的開關**：它只決定平板上有幾顆按鈕。平板停在舊畫面時病人按下去的求助照樣要送到，擋掉就是把求助丟掉
- 開啟條件由後端逐項判定，不靠人記得。例如 `REAL_PATIENT_DATA_TO_AI` 只在 `LLM_PROVIDER=onprem` 時可開；高風險三項要 FR-R08 書面確認＋規則版本附有書面依據，規則引擎尚未建立，所以目前開不了
- 開關關閉時，`feature-flag.guard.ts` 讓相關端點回 404，前端相關元素**完全不渲染**（不是 disabled）
- 切換須填核准依據並寫稽核，條件不符被拒的嘗試也寫（`FEATURE_FLAG_CHANGE_REJECTED`）。AI 兩項需 `system:configure`，其餘需 `feature-flag:manage`

### 5.9 模型供應者介面層與 AI 閘道（FR-S03／S04／S06，迭代 3）

- `LlmProviderPort` 三個實作，以 `LLM_PROVIDER=mock|lab|onprem` 切換，預設 `mock`。模擬實作在 `modules/llm/mock-llm.provider.ts`，實驗室 API 與院內地端推論走 `http-llm.provider.ts`。**端點、金鑰、模型 ID 全由環境變數提供，不寫在程式碼裡**
- 所有模型呼叫一律經 `modules/ai/ai-gateway.service.ts`：合成資料檢查（院外 provider 遇到非合成資料直接擋下，記 `AI_INVOCATION_BLOCKED`）、去識別化（`deidentify.ts`）、寫一列 `ai_invocations` 與 `AI_INVOKED` 稽核
- 閘道有兩個入口：`invoke()` 給 HTTP 端點，失敗拋例外；`attempt()`（迭代 4 新增）給背景工作，被擋或失敗時也回傳該次呼叫的紀錄 id，才能寫回工作結果
- 切換 provider 只改設定：`verify:iteration4` 以備份還原檔另起一個 `LLM_PROVIDER=lab` 的後端，接到腳本內的本機假端點，驗證同一份程式只改環境變數即可切換，且帶真實病人資料的請求一次都沒送出去
- **迭代 13 起 `lab`／`onprem` 的另一端是 AI 閘道容器**，不是推論端點本身；`LLM_MODEL_ID` 接閘道時留空，`/ai/status` 顯示閘道回報的模型。正式環境設定（`DEPLOYMENT_ENV=production`）下 `LLM_PROVIDER=lab` 直接拒絕啟動（DEP-40）
- **迭代 17.3 起閘道多一道用語把關**：系統提示最後附上 `ZH_TW_SYSTEM_RULE`；輸出經 `@hd/shared` 的 `findZhTwIssues` 查到簡體字、中國大陸用語或台灣不這樣寫的字形，就記一列 `FAILURE`（留 `outputText`，`errorMessage` 開頭「輸出含簡體字或中國大陸用語」）、把 `zhTwRetryNote` 附進提示重送；背景用途最多 3 次、`SOP_ANSWER` 2 次，最後一次仍不合格也記成 `SUCCESS` 照樣交出（後端日誌留一行 `WARN`）。**前端不留痕跡**：退回的那幾列與對應的稽核在資料庫照記，`AiInvocationRepository.query`、`AuditLogRepository.query` 套 `common/zh-tw-retry.ts` 的條件濾掉；`toAiInvocationEntry` 以 `withoutZhTwRetryNote` 截掉提示後面的重寫附註

### 5.10 臨床資料來源介面層（FR-S05，迭代 3）

`modules/clinical-data/`：`ClinicalDataSourcePort` ＋ `ManualEntryAdapter` ＋ `FileImportAdapter`（迭代 6）＋ **`HospitalApiAdapter`（迭代 15，在 `modules/hospital-sync/`）**，三者共用 `clinical_value_imports`／`clinical_values`。
1005 起院方 API 是唯一的日常來源，人工輸入與檔案匯入只留在專業版當備援（FR-S05）；院方 API 那一支的同步機制見 5.21。

- 一批**全有或全無**：任何一筆驗證失敗就整批不寫入，記 `CLINICAL_VALUES_IMPORT_REJECTED`。臨床數值只對一半比完全沒有更危險
- 每筆帶資料時間；同一數值覆蓋時保留前一版
- 迭代 4 的適足性計算從這裡讀五項輸入

### 5.11 備份與還原（FR-S09，迭代 3）

`modules/ops/`。

- 用 SQLite 線上備份（`VACUUM INTO`），不用檔案複製：WAL 模式下 `-wal`／`-shm` 與主檔是一組，只複製主檔會拿到不一致的狀態
- 每日排程 ＋ 系統管理頁手動觸發，歷程寫 `backup_runs` 與稽核
- 還原用 `npm run db:restore`，還原前先停後端。演練步驟見測試手冊第 12 章
- **0929 起每份備份旁邊另寫 `<檔名>.sha256`**（線上備份與更新前強制備份都寫，備份失敗一併刪除）。備份歷程只顯示前 12 碼，而且資料庫壞掉時連歷程都看不到——還原要的雜湊從這個檔拿
- 容器部署下資料庫在 `hd-tablet-care-data` 資料卷，`BACKUP_DIR` 是繫結掛載的主機目錄——**它是資料卷裡的資料庫唯一看得見的出口**

### 5.12 常駐總覽螢幕（FR-N12，迭代 3）

護理端 `/wall` 路由（`pages/WallDisplayPage.tsx`），不帶導覽列的獨立全螢幕版面。推播移除後，這是唯一保證通報被看見的地方。

- Wake Lock 防休眠，只在 HTTPS 或 localhost 下可用；不支援時要在作業系統關閉休眠
- 新通報發提示音，無人接收時每 60 秒再提醒
- 斷線閒置看門狗：最慢 45 秒判定斷線，全畫面紅框閃爍與橫幅，指數退避重連
- 連不上伺服器時**保留登入權杖**（迭代 3 修掉的既有問題），每 5 秒重試，恢復後自動回到原畫面
- JWT 預設 8 小時到期，到期後出現全螢幕的逾時提示；長時間顯示用的帳號做法待 Q-10
- **迭代 14.3 起這套斷線示警不再只有總覽螢幕有**：專業版每一頁與簡易版都掛上 `connection-status.tsx`（閃爍紅框＋紅底橫幅，見 6「迭代 14.3」）。總覽螢幕維持原本那一套

### 5.13 背景佇列（迭代 4）

`modules/ai-jobs/`、`ai_jobs` 表，前端進度顯示在 `nurse-pwa/src/ai-job.tsx`。

- 生成類請求只在 `ai_jobs` 排入一列就回應；後端依序處理
- **模型呼叫不在任何資料庫交易內**。SQLite 只有一個寫入者，在交易裡等模型等於鎖住所有臨床寫入
- 重新啟動時，執行中被中斷的工作標為失敗（`AI_JOB_FAILED`），前端顯示「請重新送出」
- 前端依序顯示「前面還有 N 件」→「AI 產生中」→ 結果

### 5.14 零院外連線盤點（FR-S07，迭代 3）

`npm run check:egress`（`scripts/check-zero-egress.mjs`），不需啟動後端。掃程式、套件設定、Service Worker 與前端資源（字型、CDN、分析工具），找出任何指向院外網域的相依。目前 0 筆。

---
### 5.15 求助的四段生命週期（FR-N10，迭代 5）

一筆求助從三段變四段：**按下求助 → 確認通報 → 到達床邊 → 結案登記**。

`acknowledged_at` 與 `arrived_at` 是兩個獨立欄位、兩個獨立端點，刻意不合併。理由寫在 SRS 5.2：只記確認時間的話，一旦這個數字被拿去算績效，最省力的做法就會變成「先按確認再慢慢走過去」，指標就失去意義。分開記錄讓這種情況看得見。

因此程式裡有一條看起來多餘的規則：直接按「我到床邊了」而沒按過「我接手」時，系統會順手補上確認時間，但補的是**現在**、不是到達時間。兩個欄位不互相填補，否則分開記錄就失去意義了。

結案要求 `handling_method_code`、`outcome_code`、`follow_up_required` 三欄齊備，DTO 層先擋一次、service 再對 `help_resolution_options` 查一次（選項是否仍啟用）。`resolution_note` 降為選填補充。勾了「需追蹤」就必須填追蹤事項，通報更新與追蹤事項建立在**同一個交易**裡。

### 5.16 可設定的暫代值（迭代 5）

迭代 5 的外部依賴有三項還沒回覆（Q-13 選項清單與再發期間、Q-14 勞動條件、Q-15 班別）。規格說「要做成可設定，不寫死」，實作上多出兩張表：`help_resolution_options` 與 `operational_settings`。

- 啟動時 `OperationalSettingsService.onModuleInit()` **缺哪一筆補哪一筆**，既有值不覆蓋；選項清單只在整張表是空的時候才寫入預設值——護理部改過的清單不該被下一次重新啟動蓋掉
- 每個參數都帶著 `basis`（「這是勞基法第 34 條」還是「這是開發端猜的」）一起回傳，並原樣顯示在設定畫面上。要改的人得先看得到這個數字現在是誰說的
- 每次變更**必須填理由**，理由連同新舊值寫入 `OPERATIONAL_SETTING_UPDATED` 稽核

### 5.17 勞動條件硬性檢查（FR-M04，迭代 5）

這是管理與營運一節唯一的 P0 硬性擋下項。判定函式 `evaluateLabourRules()` 放在 `@hd/shared`，前後端共用同一份——畫面上的提示與後端擋下的理由不會不一致。

六條規則：單一班次工時、兩班間隔、單日工時、任意連續七日工時、連續出勤日數、同時段重複排班。**規則的數值全部從 `operational_settings` 讀，程式裡沒有寫死任何一個數字。**

回應不是一句「違反規定」，而是逐條列出規則、上限、這張班表實際會到多少：

```
【兩班之間最短間隔】兩班之間至少須間隔 11 小時，這一筆與前後班次只隔 0 小時。
【單日工時上限】2026-10-31 當日工時上限為 12 小時，加上這一筆會到 16 小時。
```

兩個容易漏掉的地方：

- **檔案匯入要把同一份檔案裡的其他班次也算進去**。否則一次匯入七天連班會整批過關，分七次匯入反而被擋——那等於沒有檢查
- **換班核准要對接手的人重跑一次檢查**。換班最容易換出違規班表

被擋下的嘗試會寫入 `NURSE_SHIFT_REJECTED_LABOUR_RULE`（`outcome=FAILURE`）。事後檢討「那週的班為什麼排不出來」時，看得到系統擋了幾次、擋的是哪一條。

### 5.18 成效基準（FR-M07，迭代 5）

全系統唯一「過了時點就再也拿不到」的資料。系統上線後「病人按鈴到護理師到床邊要多久」會自動被記錄，但**上線前的數字不存在於任何地方**——它只存在於現在正在發生的紙本與口頭流程裡。

因此這個模組的重點不在功能複雜度，在三件事：

1. **建檔進度要看得見**：`/baselines/overview` 逐指標列出「尚未建檔」與「只有估算值」兩種缺口。上線前只有這個畫面會提醒人去補
2. **估算值要標得出來**：來不及實測時的退路（`source=ESTIMATED`）是允許的，但該筆在所有畫面上都帶著「引用時必須標明是估算」的提示。把退路做進系統，是為了讓它留下痕跡，不是讓它變方便
3. **背書者必填**：沒有出處的數字，被院長室問到「這數字哪來的」就答不出來

數值以「整數＋小數位數」記錄（規範 6.2），小數位數超過指標定義時視為格式錯誤、**不四捨五入**。同一指標同一班次再次建檔時舊版標記 `superseded` 保留，不覆寫。

### 5.19 閒置輪播（FR-P09～P11、FR-P13，迭代 6）

> **1005 迭代 16 拿掉輪播**，下面是迭代 6～15 的做法，留著對帳用。現行的病人端首頁見本節末「迭代 16 起：本次透析面板與跑馬燈」；
> 「卡片在後端組好」「開關關閉時後端不送」「`muted` 與 `helpButtonAlwaysVisible` 寫進契約」三個決定原樣沿用。

`modules/carousel/` ＋ `patient-pwa/CarouselScreen.tsx`。三層內容、一個端點：
`GET /device/carousel` 回傳行為參數、開著的層、組好的卡片，以及 `questionnaireDue`。

三個決定值得知道：

- **卡片在後端組好**。FR-P11 要求輪播畫面不得出現姓名與病歷號，把這條規則放在後端就只在一處判定；
  放在前端，就得寄望每一個畫面元件都記得它。驗收腳本因此能直接掃描回應內容來驗這一條。
- **開關關閉時後端不送該層的卡片**，不是前端不顯示。`enabledLayers` 與 `cards` 同時為空。
- **`muted` 與 `helpButtonAlwaysVisible` 是回應的一部分**，值固定為 `true`。
  它們不是設定，是把 FR-P13 的兩條 P0 要求寫進契約——契約裡有，驗收腳本就驗得到。

行為參數（閒置門檻 60 秒、卡片間隔、細節頁逾時、夜間模式起訖、問卷到期間隔）全部走迭代 5 的
`operational_settings`，不另立設定表。夜間模式的起始晚於結束時代表跨過午夜，
這是「18 時到隔天 7 時」最自然的寫法。

病人端的閒置偵測在 `App.tsx`：`pointerdown`／`keydown`／`touchstart` 三種事件在**捕捉階段**重設計時器；
輪播畫面本身也在捕捉階段收下 `pointerdown`，點在卡片以外的任何地方立即退出，**沒有確認對話框**。
求助按鈕不在輪播元件裡——它留在主畫面原處，輪播進行中只是把 `z-index` 抬到遮罩之上，
因此位置與尺寸完全不變。

**迭代 16 起：本次透析面板與跑馬燈**（SRS FR-P09～P11 的 1005 改寫）。`modules/patient-home/` ＋ `patient-pwa/TodayPanel.tsx`、`LineChart.tsx`、`Marquee.tsx`。
`GET /device/home` 回傳行為參數、面板、跑馬燈與 `questionnaireDue`：

- **面板只有畫面要用的欄位**：開始與預計結束時間、血壓與累積脫水量的點（只有時間與值）、設定脫水量、五個數字（各帶資料時間）。
  取捨表標「不顯示」的東西沒有欄位可以放，後端也不讀。讀到 0 的一律不送。資料是這次療程的 `dialysis_vital_records`（迭代 15）與 `clinical_values`
- **跑馬燈**：在架上、指定給這一床或全部床位的衛教與公告，一則「標題：內容」；**夜間一則都不送**。速度、開頭靜止、兩則間隔是營運參數（`MARQUEE_*`）
- **圖自己用 SVG 畫**，字是疊在上面的 HTML、以像素定位（不用 `viewBox` 縮放）；**沒有刻度、格線、警戒線、正常範圍**，線的顏色是 `--c-chart-line` 不是語意色（`check:ui:design` 擋）
- **跑馬燈用 Web Animations**：先靜止、再以「每秒幾字 × 字級」等速左移到整則離開、空白、下一則；不能點（`pointer-events: none`）；沒有內容、夜間、減少動態效果時整條不出現
- **即時**：迭代 15 的 `VITALS_UPDATED` 推送一到平板就重取；推送斷了還有每分鐘一次的保底
- 播放紀錄寫進原本的 `carousel_view_events`，`layer` 記 `MARQUEE`（**Schema 不變**）；`POST /device/marquee/plays`

### 5.20 檔案匯入與可設定的欄位對應（FR-S05，迭代 6）

`FileImportAdapter` 收的是寬表：一列一位病人在某個資料時間的多項數值。

- **欄位名稱不寫死**：`import_field_mappings` 一列一個目標欄位，比對時忽略大小寫與全形半形空白。
  院方把「理想體重」改成「理想體重(kg)」那天，改的是一列設定
- **Excel 用 `exceljs`，CSV 自己解析**（約二十行，支援引號與欄內逗號）。
  「欄位裡有逗號就靜默切錯」這種錯誤不會有任何錯誤訊息，值得用那二十行換掉
- **Excel 日期儲存格**在 exceljs 會以 UTC 解讀，但檔案上寫的是現場的時刻，
  因此把 UTC 的年月日時分當成當地時間重組一次，與班表匯入的處理一致
- **全有或全無**與重複匯入偵測沿用迭代 3 的 `ClinicalDataImportService`，一行都沒改：
  adapter 只負責「把來源轉成標準化數值並逐列指出格式問題」
- 檔案以 base64 夾在 JSON 裡送上來，不走 multipart。上限 2 MB，少一種請求形式就少一套解析與錯誤處理

### 5.21 院方資料同步（FR-S15／S16，迭代 15）

判準只有一句：**院方 API 判斷得出來的事，就不要求護理師操作。** `modules/hospital-sync/` 依營運參數的頻率（預設 3 分鐘）向院方透析清單 API 拉一次，
把病人主檔、床位、病人在哪一床、療程開始與下機、四種數值一律由 API 判斷；護理師只做三件事：每位病人配一次平板、更正、以及 API 判斷不了時的處理。

- **格式是讀同院 IDH 系統的程式推出來的**，不是院方文件：陣列沒有欄位名稱，只能靠位置認欄位（`@hd/shared` 的 `hospital-api.ts`，51 欄）。少欄或多欄的列不認，**那一次透析整個不寫入**——臨床數值只對一半比沒有更危險
- **同步不另開寫入路徑**：建排班、綁定、換床、寫數值都呼叫護理師拖曳時用的那幾支服務，操作者是登入不了的系統帳號 `SYSTEM-HOSPITAL-SYNC`，稽核記成「院方資料同步」。簡易版與專業版因此看到的是同一套資料、同一種稽核
- **護理師的更正優先**：提前結束或換床之後，同一筆療程的狀態與床位不再被同步改回去（`nurse_modified_at`、`bed_nurse_modified_at`）
- **判斷不了的標出來，不猜**：預計結束時間可能是預排值，不拿它判定下機，過了很久還沒有結束體重就標「待確認下機」（1007 迭代 17.5 起「預計結束」一律是開始後四小時）；平板沒自動接上時標出原因（平板正在別人的療程中、不在線上、停用或尚未佈建、院方的床位是停用的床或認不出來）；**還沒配平板的病人不算問題**，首波只有少數病人用平板，其餘只出現在床位圖上；超過設定時間沒更新，床位圖上方出現提示，這段期間護理師可到專業版手動處理
- **正式環境的兩道防線**：啟動時位址的主機是 `hospital-api-sim` 就拒絕；抓到的回應帶 `x-hd-simulated` 就整次作廢。模擬部署要以 `HD_SIMULATION_DEPLOYMENT=yes` 明示
- **推送**：有新資料時護理端串流多一種 `HOSPITAL_SYNC` 事件；平板訂閱 `GET /device/stream`，**事件只說「有新資料」、不帶數值**，平板收到後自己重取 `GET /device/home`
- **探測工具** `npm run probe:hospital-api` 與同步共用解析程式，**只印結構與型別，不印任何值與位址**；位址在探測時當場輸入，不寫進 `.env`（部署手冊第十五冊 V-30a）

實作位置與開發機怎麼開見 6「迭代 15」。

---

## 6. 已完成範圍

### 迭代 1

| 功能 | 位置 |
|---|---|
| Repository/DAO 抽象層 | `apps/api/src/repositories/` |
| 護理端身分驗證（bootstrap、註冊、審核、權限分享） | `modules/auth/`、`modules/nurses/` |
| FR-N01 排班與裝置指派 | `modules/schedule/`、`nurse-pwa/pages/ConsolePage.tsx` |
| 裝置綁定服務（SRS 4.3 九步驟＋4.4 例外） | `modules/binding/` |
| FR-P01 病人端中性等待畫面 | `patient-pwa/src/App.tsx` |
| FR-S02 稽核軌跡 | `modules/audit/`、`pages/AuditPage.tsx` |
| FR-S01 MDM 介面層 | `modules/mdm/` |

### 迭代 2

| 功能 | 位置 |
|---|---|
| FR-P02 症狀問卷 | `modules/symptoms/`、`patient-pwa/SymptomQuestionnaire.tsx` |
| FR-P06 求助按鈕 | `modules/help-requests/`、`patient-pwa/HelpRequestScreen.tsx` |
| FR-N02 即時總覽 | `nurse-pwa/pages/OverviewPage.tsx` |
| FR-N03 緊急通報與分級路由 | `nurse-pwa/pages/HelpRequestsPage.tsx`、`shared` 的 `routeHelpRequest()` |
| 即時狀態快取層 | `modules/realtime/realtime-state.service.ts` |
| 離線韌性 | `patient-pwa/offline-queue.ts`、`symptom-sync.ts` |

### 迭代 3：封閉網路化與資料層遷移

依《實作規格書》v2.0 4.1 節。不新增使用者可見的臨床功能，把後續每個迭代都要用的地基先立起來。

| 功能 | 位置 |
|---|---|
| SQLite 遷移、寫入／唯讀連線、位置檢查 | `apps/api/prisma/`、`PrismaService`（見 5.7） |
| 唯讀角色預設全擋 | `common/guards/read-only-role.guard.ts` |
| FR-S07 零院外連線盤點 | `scripts/check-zero-egress.mjs` |
| FR-N12 常駐總覽螢幕 | `nurse-pwa/pages/WallDisplayPage.tsx` |
| FR-S06 模型供應者介面層與 AI 閘道 | `modules/llm/`、`modules/ai/` |
| FR-S05 臨床資料來源介面層 | `modules/clinical-data/`、`nurse-pwa/pages/ClinicalValuesPage.tsx` |
| FR-S08 功能開關中心 | `modules/feature-flags/`、`shared/platform.ts` |
| FR-S09 備份與還原 | `modules/ops/`、`npm run db:restore` |
| 系統管理頁（開關、備份、AI 呼叫紀錄） | `nurse-pwa/pages/SystemPage.tsx` |

### 迭代 4：AI 輔助內容與護理記錄

依《實作規格書》v2.0 4.2 節。所有「生成／草擬輔助」性質、不涉及臨床判斷分級的 AI 功能，全部在 `MockLlmProvider` 下完成開發與驗收。

| 功能 | 位置 | 做法重點 |
|---|---|---|
| 背景佇列 | `modules/ai-jobs/`、`nurse-pwa/src/ai-job.tsx` | 見 5.13 |
| FR-P04 個人化衛教 | `modules/education/`、`EducationPage.tsx`、`patient-pwa/EducationScreen.tsx` | 依透析史、衛教完成紀錄、測驗結果、近期自述症狀組提示；**先審後給**，護理師核可前病人看不到 |
| FR-P07 離院衛教重點＋適性測驗 | 同上、`education/quiz.ts` | 離院重點依當次自述與求助整理；出題、對錯、知識點狀態都是固定規則，不經模型 |
| FR-P08／N08 回饋與心理社會趨勢 | `modules/feedback/`、`patient-pwa/FeedbackScreen.tsx`、`TrendsPage.tsx` | 每次療程一份；暫定規則 `PSY-DEV-v1` 只做事實陳述，不自動轉介 |
| FR-N04／N05 護理記錄 | `modules/nursing-records/`、`NursingRecordsPage.tsx` | 建立當下產生預填文字（`prefill.ts`，不經 AI）；AI 初稿是另一個起點；簽核後不可改，並記錄是否採納 AI 初稿 |
| FR-N07 透析適足性 | `modules/adequacy/`（`formula.ts`）、`TrendsPage.tsx` | Daugirdas 第二代公式，結果以整數存並指回五筆原始數值；只畫趨勢，不標目標、不預測 |
| FR-N09 SOP 查詢 | `modules/sop/`（`retrieval.ts`）、`SopPage.tsx`、`prisma/sop-fixtures.ts` | 字詞比對檢索；檢索不到就不呼叫模型；回應一律附原文段落；開發用 4 份虛構文件 |

### 迭代 5：求助處理完整紀錄、護理師班表與成效基準

依《實作規格書》v2.0 4.3 節。這個迭代的三件事都不難，但**時間點不能往後挪**——後面兩個迭代要吃它們產生的資料，而成效基準過了上線時點就永遠拿不到。

| 功能 | 位置 | 做法重點 |
|---|---|---|
| FR-N10 求助結案結構化登記 | `modules/help-requests/`、`HelpRequestsPage.tsx` | 見 5.15。結構化三欄缺一不可，只填自由文字會被擋下 |
| FR-N11 再發標示 | 同上（`recurrenceFor()`） | 同病人同類別、設定期間內的前一次求助與其處理方式，直接放在通報卡片上 |
| FR-P12 結果回饋給病人 | `patient-pwa/App.tsx` | 平板顯示「已處理」與處理方式／結果的**文字**；⛔ 不含自由文字補充、不含護理師工作 ID |
| 可設定的暫代值 | `modules/operations/` | 見 5.16。Q-13 的選項清單與 Q-13／Q-14 的各項參數都存資料表 |
| FR-M01／M02 班表與床位分配 | `modules/shifts/`、`ShiftsPage.tsx` | 手動建立＋CSV 匯入（全有或全無）；床位整組取代，擋下一床兩主 |
| FR-M04 勞動條件硬性檢查 | `shared/operations.ts` 的 `evaluateLabourRules()` | 見 5.17。**擋下儲存**，不是提示 |
| FR-M07 成效基準建檔 | `modules/baseline/`、`BaselinePage.tsx` | 見 5.18。只新增不覆寫；估算值一律標示 |

**唯一刻意改動的既有行為**：FR-N10 讓「只填自由文字就結案」不再成立，`verify:iteration2` 對應段落跟著改。迭代 2 原本要驗的行為一條都沒放寬——改的是怎麼結案，不是結案之後會發生什麼事。

### 迭代 6：閒置輪播與檔案匯入

依《實作規格書》v2.0 4.4 節。**這個迭代沒有改動任何既有行為**，既有五支驗收腳本一行都沒有改。

| 功能 | 位置 | 做法重點 |
|---|---|---|
| FR-P09／P10 閒置偵測、輪播與細節頁 | `patient-pwa/App.tsx`、`CarouselScreen.tsx` | 見 5.19。捕捉階段重設計時器；細節頁逾時自動退回 |
| FR-P11 三層內容 | `modules/carousel/carousel.service.ts` | 第一層取自既有資料、第二層讀 `carousel_items`、第三層讀 `clinical_values`（只播未被覆蓋的最新一筆） |
| FR-P13 主線保護 | 同上 ＋ `styles.css` | 求助按鈕留在原處只抬 `z-index`；問卷到期由後端判定並回傳 `questionnaireDue` |
| 夜間模式 | `carousel.service.ts` | 起訖時刻可設定，跨午夜自動處理；只調暗，不改版面與字級 |
| FR-S05 檔案匯入 | `modules/clinical-data/file-import.adapter.ts` | 見 5.20。全有或全無與重複偵測沿用迭代 3 的匯入服務 |
| 欄位對應設定 | `modules/clinical-data/import-field-mapping.service.ts` | 缺哪一筆補哪一筆；同一檔案欄位不得對應兩種數值 |
| 輪播瀏覽事件 | `modules/carousel/` ＋ `carousel_view_events` | 只記卡片種類、停留時間、點開次數。DTO 的 `forbidNonWhitelisted` 讓多送的識別欄位整包被擋下 |
| 三層的開啟條件 | `modules/feature-flags/feature-flags.service.ts` | 第一層永遠就緒；第二層要有在架上的內容；第三層要有有效的臨床數值 |

### 迭代 7：擋住上線的缺陷與資料安全（0919）

依《實作規格書》4.5 節。**這個迭代沒有新增任何使用者可見的功能**，它是後面三個迭代的安全網——後面每一個都會動 schema，沒有保護機制就是在沒有安全網的情況下改資料庫。既有六支驗收腳本一行都沒有改。

| 工作項 | 位置 | 做法重點 |
|---|---|---|
| 不依日期的有效綁定清單 | `modules/binding/binding.controller.ts`（`GET /bindings?active=1`）、`nurse-pwa/pages/DevicesPage.tsx` | 原本的解除入口掛在依日期篩選的排班清單上，日期一對不上整列就消失。這份清單日期完全不參與條件 |
| 跨日提示與指派清單說明 | `nurse-pwa/pages/ConsolePage.tsx`、`common/mappers.ts` 的 `describeAssignability()` | 不可指派的平板照樣列出來、只是選不下去，並寫出原因。判斷與 `BindingService.create` 的擋下條件寫在同一個地方，避免畫面說的與後端做的走偏 |
| 解除改為冪等 | `modules/binding/binding.service.ts` | 目標狀態已達成就回報成功並說明它何時因什麼結束，同時寫一筆 `BINDING_RELEASE_NOOP` 稽核——冪等不等於什麼都沒發生 |
| Prisma 引擎隨包攜帶（後端啟動） | `infra/prisma/bundled-engines.ts`、`engine-bootstrap.ts` | `PRISMA_ENGINES_DIR` 指向包內引擎。**必須在 `@prisma/client` 載入前執行**，因此獨立成一個只有副作用的模組，由 import 順序保證 |
| Prisma 引擎隨包攜帶（指令端，0920 補） | `apps/api/scripts/prisma-cli.mjs`、`scripts/lib/prisma-engines.mjs` | 上一列只管後端啟動；`prisma migrate`、`prisma generate` 是另外開的行程，不經過它。所有 prisma 指令改從這層進去，執行前同樣依 `PRISMA_ENGINES_DIR` → `node_modules/@prisma/engines` 的順序把路徑指好 |
| 版本鎖成確定版本 | `apps/api/package.json` | `prisma` 與 `@prisma/client` 去掉 `^`。引擎與 CLI 版本必須一致，浮動範圍會在某次重裝時悄悄換掉其中一邊 |
| 更新流程 | `apps/api/scripts/db-update.mjs` | 規範 18.1 四道關卡的可執行版：備份 → **實際還原驗證** → 前滾 → 寫紀錄。純 Node.js、不依賴任何開發相依（正式主機上沒有開發環境） |
| 開發用遷移指令的防呆 | `apps/api/scripts/guard-dev-migrate.mjs` | 掛在 `prisma:migrate` 前面，偵測到正式環境設定就拒絕執行並寫稽核 |
| 更新紀錄 | `update_runs` 資料表、`modules/ops/runtime-status.service.ts` | 規範 18.4 的六項全記。後端**只讀不寫**——更新進行時服務是停著的 |
| 時區檢查改為主機時區 | `config/time-zone.ts` | 判斷寫成純函式，驗收腳本可直接餵各種情境；正式環境不符即拒絕啟動，並印出檢查時的執行帳號 |
| AI 端點不通時的行為 | `modules/llm/http-llm.provider.ts` | 健康檢查的逾時與單次生成分開（預設 5 秒）並短暫快取，端點掛掉時功能開關頁不會卡著等 |
| 共用主機上的隔離 | `config/configuration.ts`、`infra/prisma/sqlite.ts`、`scripts/db-update.mjs`、`modules/ops/*` | 0919 同日補做（見下）：埠不得沿用預設值、資料與備份不得落在共用目錄、磁碟可用空間要看得見且擋得住更新 |

**0919 同日補做：正式主機是共用的（DEP-37）。** 主機由「本專案專用」更正為「與其他專案共用」之後，
v1.0 為共用主機訂的隔離要求整條回來，只是落實方式由容器層級改為安裝包層級。這件事對本迭代的實作有三處影響，
共同點是它們原本都預設「這台機器只有本系統在用」：

| 原本 | 為什麼在共用主機上不成立 | 改成 |
|---|---|---|
| `API_PORT` 沒填就套 3000 | 與別的專案搶同一個埠，服務起不來；而且多半在某次重新開機、兩個服務的啟動順序對調時才發作，測試階段一次都不會出現 | 正式環境設定下**不套預設值**，沒填就拒絕啟動並說明要先向資訊室登記（Q-27）。開發機不受影響 |
| 資料庫與備份路徑只擋網路磁碟、專案目錄、雲端同步資料夾 | 暫存、公用、桌面、文件、下載這些位置別的專案的清理腳本掃得到，一般登入者也讀得到 | 多一條共用目錄的判定，後端啟動與 `db:update` **共用同一條規則**，兩邊不會判得不一樣 |
| 沒有人在看磁碟 | 磁碟不是本系統一個人在寫，而 SQLite 在磁碟寫滿時是**寫入失敗**，不是逐步變慢——症狀回報按下去會直接錯誤 | 可用空間與下限顯示在資料庫狀態上；更新流程在備份**之前**先量，不夠就停下，不會讓備份做到一半壞掉 |

**第 4 項（目錄權限只給服務帳號與系統管理員）程式驗不到**，它是部署當天以實際帳號確認的事，
列在部署前置檢查清單 9.1 第 9 條。磁碟下限的實際數字同樣待資訊室答覆（Q-27；埠號 0930 已定為 `13000`、`18080`、`18081`）——
數字下來之後改的是 `.env`，不是程式。

### 迭代 8：介面重新設計（0919）

依《實作規格書》4.6 節與《[介面設計基準](../notes/uiux-design-baseline.md)》。
**這個迭代沒有動任何後端行為**：沒有新端點、沒有 schema 變更、既有七支驗收腳本一行都沒有改。
它改的是「長什麼樣」；「有哪些、放在哪」是迭代 9 的事，兩件事刻意分開做——
混在一起出問題時分不清是版面壞了還是開關壞了。

**最重要的一件事是結構性的，不是視覺上的。** 0919 之前求助按鈕會蓋住輪播的字，
真正的原因不是按鈕太大：

| | 0919 之前 | 現在 |
|---|---|---|
| 求助按鈕在哪 | 首頁版面裡的第二顆按鈕，位置由首頁內容多寡決定 | **外框的一列**，位置只由 `--dock-h` 決定 |
| 輪播蓋住什麼 | 整個畫面（`position: fixed`），只能「猜」按鈕在下半部然後把卡片往上推 | **內容區**（`position: absolute` 相對 `.app-content`），下緣就是求助區的上緣 |
| 靠什麼保證不遮擋 | 輪播開始時把按鈕的 `z-index` 抬高 | 內容區的高度＝畫面高度**扣掉**求助區，結構上畫不到那裡 |

「位置固定」被實作成「層級固定」，這是兩件事。新做法讓 FR-P13 從一條要小心維護的規則，
變成一件**做不到違反**的事。瀏覽器實測：輪播中與非輪播時求助區量到的矩形完全一致
（x 0、y 532、寬 638、高 132），輪播內所有文字的最低點 464，求助區上緣 532。

| 工作項 | 位置 | 做法重點 |
|---|---|---|
| 設計語彙 | `apps/*/src/design-tokens.css` | 兩端**共用同一組語意名稱**（一般／注意／警示／完成），數值不同。色碼與字級只能出現在這兩個檔裡 |
| 求助區版面契約 | `patient-pwa/src/PatientShell.tsx` | 已綁定的每一個畫面都包在同一個外框裡；已經在求助畫面上時它留在原位改為狀態說明，不是消失也不是多一顆按鈕 |
| 未指派時沒有求助區 | `patient-pwa/src/App.tsx` | 平板還沒指派給任何人，求助送出去護理站不知道是誰按的。改成直接寫「請按床邊呼叫鈴」——**一顆按了會失敗的按鈕比沒有按鈕更糟** |
| 病人端全面重做 | 全部畫面 | 內文 20px 起、觸控 64px 起、選中的選項多一個「✓」（顏色不是唯一線索）、離線訊息改寫成人話 |
| 護理端 N-1 | `nurse-pwa/pages/OverviewPage.tsx` | 總覽最上面一條橫幅直接寫出結論。四個數字方塊回答得了「現在需要我嗎」，但要先讀完四個數字才知道哪一個重要 |
| 護理端 N-5 | `nurse-pwa/components.tsx` 的 `ConfirmButton` | 兩段式確認，第二段寫的是**後果**不是動作名稱；8 秒沒下一步自己收回（護理師常常按到一半被叫走）。解除鎖定不加阻力——那是把限制拿掉 |
| 常駐總覽螢幕 | `--wall-scale` | 整面牆的字級相對這一個倍率。觀看距離待 Q-10，確定後改一個數字，不必回頭調每一條規則 |
| 介面檢查腳本 | `scripts/check-ui-design.mjs` | 對比度、觸控目標尺寸、裸色碼 |
| `check:all` 改寫 | `scripts/check-all.mjs` | 見下 |

**為什麼不用瀏覽器的 `confirm`。** 它會凍住整個分頁——即時總覽的串流也跟著停；
而且它說的話是瀏覽器的措辭：「確定要執行此操作嗎」對護理師沒有意義，
「解除後病人的平板會立刻回到等待畫面」才有。

**順手修掉一個沉默的問題：`check:all` 從來沒有跑完過。** 它原本是五支用 `&&` 串起來的指令，
而 `check:ui` 只要還有任何一筆技術識別殘留就回結束狀態 1——那一批的清除排在迭代 9，
所以它現在必然是 1，**後面三支因此從來沒有被 `check:all` 跑到過**。
畫面上看起來只是「check:ui 有 22 筆」，不像「另外三支根本沒跑」。
改成每一支都跑完、最後給一張總表。**一支會擋住後面全部的檢查，比沒有那支檢查更糟——
它讓人以為全部都跑過了。**

### 迭代 9：導覽版位、功能開關與內容資料化（0919）

依《實作規格書》4.7 節與 SRS 附錄 C。**這個迭代的一句話是：「哪些功能出現、出現在哪裡、
選項有哪些」全部變成資料。** 迭代 8 改的是「長什麼樣」，這一個改的是「有哪些、放在哪」——
兩件事刻意分開做，混在一起出問題時分不清是版面壞了還是開關壞了。

**最重要的一件事：「關閉」不是把連結藏起來。**

| | 一般的做法 | 這裡的做法 |
|---|---|---|
| 前端 | 連結不顯示 | **路由不註冊**。網址列直接輸入會落回首頁，不是一個「功能未啟用」的空白頁 |
| 後端 | 通常沒管 | `NavItemGuard` 掛在全域，標了 `@RequireNavItem()` 的控制器一律回 404 |
| 軌跡 | 沒有 | 被擋下時留一筆。**「已實作但關閉」與「根本沒有這個功能」在稽核上是兩件事** |

只藏前端等於沒關——知道網址的人直接打得進去。這一條在 DEP-34 寫得很清楚，
但它寫的是「不要出現停用的入口」，實作時真正的難點是後端那一半。

**版本號是這個迭代的另一半。** 問卷、題庫、回饋題目三組內容各有一張版本表，
改一題不是就地改那一列，而是**整份複製成新版本再套上改動，在同一個交易裡完成**。

| 為什麼要這樣 | 不這樣會怎樣 |
|---|---|
| 舊作答仍指向舊版本 | 改過題目之後的趨勢圖就是把兩種不同的問題畫在同一條線上 |
| 版本要嘛整份成立、要嘛完全不存在 | 半成品的版本比沒有版本更難查 |
| 平板拿著舊版題目送出時擋下 | **默默拿新題目去解讀舊答案，比拒收更危險**——同一個識別碼在兩版之間可能換過選項 |

| 工作項 | 位置 | 做法重點 |
|---|---|---|
| 導覽版位 | `nav_placement_settings`、`modules/navigation/` | 17 項功能各一列，三種版位。預設值寫在共用常數，**第一次啟動時才寫進資料表**，之後一律以資料表為準——否則每次重新部署都會把護理長的調整洗掉 |
| 主列上限 | `NAV_PRIMARY_MAX = 7` | 滿了之後第 8 項移不進去，會說「請先把其中一項改到更多選單」。**上限若只寫在文件裡，半年後主列就會有 9 項** |
| 需手持裝置的功能 | 開關 `HANDHELD_FEATURES` | 一個群組一次開關（DEP-29）。它的開啟條件系統驗不到——護理師手上有沒有裝置是護理長知道、系統不知道的事實。因此條件視為成立，把關落在「切換必須登記核准依據」。**把它寫成一個永遠不成立的條件只會逼人繞過檢查** |
| 求助類別 | `help_categories` | 依附錄 C.2 重新設計，臨床 11 項、非臨床 4 項，含分派表預設急迫度。**「對應的常見併發症」那一欄不送給任何畫面**——顯示了就變成系統在給診斷提示 |
| 求助類別的文字快照 | `help_requests.category_label` | 改了類別的文字之後，既有紀錄仍顯示**按下當時**的措辭。事後回頭看要知道病人按的是哪幾個字 |
| 處理方式可複選並記順序 | `help_request_methods` | 「先平躺再回填食鹽水」和「先回填再平躺」是不同的處置路徑 |
| 三組帶版本號的內容 | `questionnaire_*`、`quiz_bank_*`、`feedback_form_*` | 見上表 |
| 代號 → 文字 | `common/content-labels.ts` | mapper 是純函式、注入不進服務，改成由呼叫端把一份快照傳進來。快取 30 秒，發布內容時直接失效——**護理長改完要立刻看到結果，TTL 只是兜底** |
| 抽題規則 | `education/quiz.ts` | 附錄 C.6 的四個順位，前三個各有一個可設定的上限。**「個人化」不是把五題全部塞給同一個知識點**，那樣病人只會看到一直重複的題目 |
| 趨勢偏離改寫 | `feedback/psychosocial-rule.ts` | 從「近三次平均比先前平均低」改成附錄 C.7：**這位病人自己**近六次的移動中位數，連續兩次低於它達 2 分才標示。三個門檻全部可設定 |
| 平板端的離線 | `patient-pwa/src/device.ts` | 題目與類別存在 `hd.content.*`，**刻意不掛在 Session 前綴底下**——它們不是病人資料；跟著清掉的話，下一位病人接手時剛好斷網就連問卷都開不出來 |
| 介面技術識別清零 | 前端各頁 | 22 筆清完，基準線降到 0 |

**四條護欄是後端擋一次、前端擋一次**，而前端那一次的做法是「按鈕不出現」，
不是「按了才說不行」：識別碼在編輯時是純文字而非輸入框、整頁沒有刪除按鈕、
「其他」那一列沒有停用按鈕、版本提示寫在按下去之前。

**介面技術識別盤點留了一份逐行列出的已知例外。** 「內容與選項」那一頁看得到識別碼，
這是刻意的：依附錄 C.0 第 1 條，**護理長看不到識別碼，就不知道自己改的是文字（安全）
還是新增了一個選項（會讓歷史資料斷開）**。例外逐行列出並寫明理由——
不開放整個檔案，也不接受「加個註解就跳過」那種寫法。

**順手修掉一件事：`check:all` 的遷移安全那一支永遠是紅的。** 它掃的是全部的遷移，
而已經套用出去的遷移改不動（規範 18.1 第 2 關），所以掃出來只會得到一份改不動的清單。
改成只掃「上一次部署之後新增的那幾份」，基準線寫在 `check-all.mjs` 裡，每次部署後往前移。
**一支永遠是紅的檢查，跟沒有那支檢查一樣：沒有人會再看它一眼。**

### 迭代 10：打包、平板佈建與部署演練（0920）

> **0926 起這一節是歷史紀錄。** 院方要求以容器部署、不准用隨身碟，離線安裝包在迭代 11 整條撤除
> （`build-offline-package.mjs`、`verify-package.mjs`、`package-templates/`、`package:*` 指令、`PRISMA_ENGINES_DIR`、`make-hospital-ca.mjs`）。
> 仍然有效的是：病人端離線快取、逸出偵測（前景回報）、`db:update` 的「先備份並驗證還原」與演練抓到的三個缺陷的修正。

依《實作規格書》4.8 節與《部署規範》第 3、6、8 章。**這個迭代的一句話是：
把系統變成一份帶得進院內的東西，並且實際試一次。**

與前九個迭代有一個根本差別：**它的驗收有一半不在開發機上**。
前面驗的是「功能對不對」，這一個驗的是「把它搬到一台什麼都沒有的機器上，還能不能動」——
而開發機正好是那個條件的反面。因此 `verify:iteration10` 刻意不湊成十條綠燈，
把結果分成「驗過了／只驗得到交付物在不在／這裡驗不到」三種印出來。

| 工作項 | 位置 | 做法重點 |
|---|---|---|
| 離線安裝包 | `scripts/build-offline-package.mjs` | 自帶 Node.js 執行期、建置產物、Prisma 引擎、遷移檔、服務腳本、版本標記。**包裡沒有 `.env`、沒有資料庫、沒有備份**（DEP-13）；資料與備份一律在包外，**因為某一次「刪掉舊資料夾再解壓新版」不會發生在第一次更新，會發生在第五次、由另一個人執行的那一次** |
| 雜湊值 | `CHECKSUMS.txt` | 逐檔 SHA-256，清單本身再取一次。防毒只回答「有沒有惡意內容」，不回答「是不是我給的那一份」 |
| 安裝包驗收 | `scripts/verify-package.mjs` | 五項，**全部用包內的東西跑**：包內的執行期、包內的套件、包內的引擎 |
| 執行期的零院外連線 | `scripts/package-templates/egress-sentinel.cjs` | 掛在 `NODE_OPTIONS` 上攔 DNS 查詢與 TCP 連線。`check:egress` 讀的是原始碼，回答「有沒有人寫了對外的網址」；**這一支回答「這個行程實際上有沒有去連過院外」**，抓得到套件在安裝後腳本裡偷跑的那種 |
| 常駐與啟停 | `scripts/package-templates/service-*.ps1` | Windows 內建的排程工作。**不是 sc.exe 的服務**——node.exe 不會回應服務控制管理員，要成為服務得外加一個包裝器，而那是另一個要送進院內、另外過資安審查的執行檔（Q-27） |
| 病人端離線快取 | `apps/patient-pwa/sw-template.js` | 畫面走網路優先、逾時退回快取；**`/api/` 一律不快取**——快取裡出現病人資料，等於把資料留在平板上，與「Session 失效即清除本地暫存」直接衝突 |
| 圖示 | `scripts/generate-icons.mjs` | 用 Node 內建的 zlib 自己組 PNG，不引入影像相依。**做成腳本而不是把圖檔丟進 repo**，是為了讓「它是怎麼來的、顏色跟誰對齊」留得住 |
| 逸出偵測 | `POST /api/device/foreground`、`DevicesPage` | 平板每 30 秒回報一次、離開前景立刻回報；護理端那一頁每 15 秒重取。**四種狀態**：固定中／已跳出／失去回報／尚未回報 |
| 自簽 CA | `scripts/make-hospital-ca.mjs` | 根憑證 10 年、伺服器憑證 825 天，主體別名要涵蓋平板實際連的位址。**不會覆蓋既有的 CA**——換 CA 等於 15 台都要重發 APK |
| 外殼 App | `apps/kiosk-shell/` | 獨立的 Android 專案，不進本 repo 的建置流程。README 寫的是兩邊的契約：載入哪個網址、序號與金鑰怎麼帶、信任哪張憑證 |

**「已跳出」與「失去回報」是兩種狀態，不是一種。** 前者是平板說的，後者是它不說話。
護理師要做的事不同：前者去床邊把螢幕固定重新釘回來，後者去看看那台平板還在不在。
「尚未回報」則是外殼 App 還沒裝，不是故障——**把三者混成一格紅字，護理師就會開始忽略它**。

**稽核只記轉折點。** 15 台每 30 秒一筆，一天四萬多筆；要回答的問題是「哪一台什麼時候跳出去的」，
答案只在轉折點上。第一次回報而且回報「我在前景」時也不記——那是 App 裝好之後的第一句話，
不是跳出去又回來。

**演練抓到三個缺陷，三個都是靜態檢查看不到的。**

| 缺陷 | 為什麼看不到 | 處置 |
|---|---|---|
| 後端在安裝包裡拒絕啟動（「找不到專案根目錄」） | 資料庫路徑檢查往上找帶 workspaces 的 `package.json`，**安裝包裡沒有那個東西**；開發機永遠找得到 | 改成兩段：先找專案根目錄，找不到就找安裝包根目錄。兩者要擋的是同一件事——資料庫不得放在「每次更新會整個換掉的那個目錄」裡 |
| `prisma migrate deploy` 在包內找不到 CLI | 指令外套只認開發機的兩個落點，安裝包少一層目錄 | 補上第三個落點 |
| `npm run db:update` 倒在套用遷移（`database is locked`） | 更新腳本為了寫更新紀錄一直開著一條連線，遷移引擎要獨占。**只有在這次更新真的帶著待套用的遷移時才發作** | 套用遷移前先放掉自己的連線 |

第三個特別值得記下來：它**會在第一次真正需要它的時候失敗**。
沒有 schema 變更的更新一路綠燈，而有 schema 變更的那一次，正是最需要備份與前滾都成功的那一次。

**已完成與未完成講清楚**：開發端的建置、驗收、離線快取、逸出偵測、更新與回退演練都做完了；
**乾淨 Windows 機器上的全程離線安裝、路線 A 與路線 B 的現場紀錄、服務以專用帳號註冊、
平板實機佈建，四項都還沒做，也不可能在開發機上做**。欄位已備在
《[部署演練紀錄](../notes/deployment-drills.md)》。

### 迭代 11：部署改為 Docker ＋ `git clone`（0926）

依《實作規格書》4.9 與《部署規範》v3.0。**起因是 0922 第一次進院失敗**：院方當天要求以容器部署，
而容器路線的修正只在另一個分支上，院方照預設 clone 拿到的是修正前的那一版（部署手冊第十冊）。

| 工作項 | 位置 | 做法重點 |
|---|---|---|
| compose 改寫 | `docker-compose.yml` | 專案名稱固定 `hd-tablet-care`（DEP-37，同機別的專案 `down` 不到我們）；**繫結掛載只剩備份與設定兩個目錄**；資料與金鑰兩個資料卷標為 `external`，compose 不會建立也不會在 `down -v` 時刪掉；映像檔標籤必帶版本號、`pull_policy: never`；`ai-gateway` 與 `shell-builder` 放在 profile 裡 |
| 院內設定範本 | `deploy/hospital.env.example` | 只列容器需要的變數，連接埠與版本標籤**沒有預設值**。根目錄的 `.env.example` 留給日常開發，兩份各填各的 |
| 正式環境拒絕 `lab` | 後端啟動檢查 | `DEPLOYMENT_ENV=production` 時 `LLM_PROVIDER=lab` 直接拒絕啟動（DEP-40） |
| 盤點腳本 | `check:egress`、`check:container`、`check:offline` | `check:egress` 範圍改為映像檔內容、compose 與 AI 閘道；**新增 `check:container`**，把部署規範「compose 不准怎麼寫」逐條變成檢查（0922 那個掛整顆 `C:\` 的 `-v` 就是它要擋的）；`check:offline` 沒刪，改成只留容器裡照樣成立的盤點項 |
| 驗收 | `verify:iteration11` | 靜態檢查；`--live` 對 Docker 實測 `down -v` 之後資料還在、繫結掛載只有兩個、正式環境拒絕 `lab` |

**實測抓到兩個只有在容器裡才會現形的缺陷**：`db:update` 以一次性容器執行時問的是自己的 `127.0.0.1`，
**服務開著也照樣更新**——改以 `UPDATE_PROBE_URL` 問 `api` 那個容器；還原腳本讀 `src/`，映像檔原本沒帶。
開發機上從 GitHub 全新 clone、全新資料卷、只用 Git 與 Docker 從零部署，更新與回退各走一次，
紀錄在《[部署演練紀錄](../notes/deployment-drills.md)》第 8 節，步驟在《[部署手冊](../deployment/index.md)》第十一冊。

**Schema 變更**：無。

### 迭代 12：外殼 App 獨立 repo 與整合（0927）

依《實作規格書》4.10。外殼以 `git subtree split` 搬到私人 repo `hd-kiosk-shell`（保留歷史），本 repo 刪除 `apps/kiosk-shell/`，
**不留兩份**。兩邊只靠《[病人端外殼 App 契約](../reference/kiosk-shell-contract.md)》對齊，契約定為第 1 版。

| 工作項 | 位置 | 做法重點 |
|---|---|---|
| 契約 | `packages/shared/src/kiosk-shell.ts` | 契約版本、最低可用外殼版本、JS 介面（`window.HdKioskShell`）、狀態推算 |
| 後端 | `GET /api/device/shell-contract`（不需驗證）、前景回報 | 前景回報多收外殼版本與契約版本，**只帶一半回 400**；版本變了才寫稽核「平板程式版本變更」；`KIOSK_SHELL_MIN_VERSION` 設定 |
| 護理端 | 裝置管理 | 「外殼版本」欄：版本正常／外殼過舊／版本不相容／未回報版本 |
| 病人端與靜態服務 | `patient-web` | **改走 HTTPS 並與後端同一個來源**：同一個埠接 HTTPS 與 HTTP（HTTP 只留 `/shell/` 下載頁），`/api/` 轉送給 `api`。外殼只信任院內 CA、只准 HTTPS，而 HTTPS 頁面不准呼叫 HTTP 的後端 |
| 建置 | `services/shell-builder/` | 映像檔建置時從主機上的 clone 取外殼原始碼（`additional_contexts`）並預先下載相依；**執行時 `network_mode: none`**——掛著私鑰的時候沒有網路。首次產生 CA、伺服器憑證、簽章金鑰並存入金鑰資料卷；`keys-backup`／`keys-verify`／`keys-restore` 落實 DEP-35 |
| 版本釘選 | `services/shell-builder/shell.pin` | 本系統的哪一版配哪一版外殼，跟著本系統的 tag 走 |

**外殼回報「是否釘選」，網頁把它併進前景判定。** 解開螢幕固定之後 App 常常還停在前景，只看畫面可不可見會誤報成「固定中」。
**迭代 10 的外殼其實建不起來**（少了根目錄的 Gradle 設定與啟動圖示、`res/raw/` 有不合法的資源名稱）——迭代 10 沒有編譯環境，這次讓 `shell-builder` 建置時逐一核對才發現，已在外殼 `v0.2.0` 修正。

**Schema 變更**：`devices` 加 `shell_version`、`shell_contract_version`（只做加法）。開發手機上的實機驗收（安裝、釘住、版本不合的提示列）待做。

### 迭代 13：AI 閘道（0927）

依《實作規格書》4.11。`services/ai-gateway`：FastAPI ＋ LangChain，`config.yaml` ＋ `llm_factory`（實驗室規範的寫法），
`provider` 可選 `ollama`（ChatOllama）或 `openai`（ChatOpenAI）。

- **對後端只有 `/v1/chat/completions`、`/v1/models`、`/health` 三個端點**，沒有任何管理模型的端點，也關掉自動產生的說明頁
- **`config.yaml` 改檔即生效，改壞了不沿用舊設定**：每個請求比對檔案修改時間；改壞時回「設定有誤」、`/health` 不通過，後端健康檢查跟著不通過，AI 總開關開不起來。院內範本因此可以把位址與模型留空（等 Q-07），閘道照樣起得來，只是明確說出還缺什麼
- **`/v1/models` 會去探推論端點**（只讀清單）。只照抄設定檔的話，SSH 轉送斷了或模型被移走時健康檢查照樣通過
- 映像檔：套件連間接相依全部鎖版本、**明寫關閉 LangSmith 追蹤**（它一開就把呼叫內容送往院外）、裝 `curl`（規範要求容器內以 `curl` 確認連線）、一般使用者執行、建置最後一步跑自我測試（內建假推論端點，不需要網路）
- 後端只改一處：`HttpLlmProvider` 的 `LLM_MODEL_ID` 改為可留空，模型只由閘道決定——否則「只改 `config.yaml` 就換得了模型」做不到

驗收 `verify:iteration13`（靜態、`--secrets` 逐字比對實驗室連線資訊、`--live` compose 實測）與 `verify:iteration13:api`（暫存資料庫＋閘道容器＋假推論端點）本機全部通過；
**實驗室上的真模型實測待連線**（部署手冊第十三冊，實驗室的位址、帳號一律不進 repo，DEP-42）。**Schema 變更**：無。

### 迭代 14：介面極簡重設計（0927）

依《實作規格書》4.12 與改版後的《[介面設計基準](../notes/uiux-design-baseline.md)》（極簡四條）。**先改基準、再動畫面。**

**病人端**：首頁只剩基本資訊、輪播、緊急回報三區，**不再顯示姓名與病歷號**；透析前問卷、心情問卷、衛教依療程時點**自動全螢幕出現一次**，
一題一頁、不捲動（衛教內文以欄分頁）。舊的四個畫面元件刪除，換成 `tasks/` 底下四個一題一頁的版本。心情與衛教的時點是新的營運參數（預設綁定後 120、180 分鐘）。

**護理端簡易版**（`apps/nurse-pwa/src/simple/`），每次登入的預設：床位圖加病人、護理師、平板、輪播內容四個框。
九項任務每項一個動作，拖曳與點選兩種做法都有、也能用鍵盤；可逆的動作做完出現 8 秒復原列，**不可逆的下機與結案改成延後 8 秒才送**，期間可改處理結果或取消。
「接緊急通報」不提供復原——確認時間是事實。**專業版不動**，只多一顆切回簡易版的按鈕。

**最重要的一條結構性決定：簡易版只呼叫專業版原有的端點。** 兩邊寫出的稽核軌跡與結構化欄位因此不可能不同；
`verify:iteration14` 會擋下簡易版呼叫清單外的端點。專業版本來就沒有的動作才加端點，而且只做加法：
`PUT /beds`、`POST /devices/:id/bed`（目的床有平板就對調）、`PUT /carousel/items/:id/targets`、`POST /help-requests/:id/outcome`（結案後 60 分鐘內補改處理結果）。

**Schema 做了加法**，原本寫「原則上無」：系統裡根本沒有「床」——病人綁的是平板，班表的床號只是一串字。
新增 `beds`、`carousel_item_targets`、`devices.bed_no`；遷移 `iteration14_beds`。

資源一律自帶：Lucide 圖示由 `scripts/sync-icons.mjs` 依登記表產生兩端的 `icon-data.ts`（**一個圖示一件事**，登記在基準 4.6）；
Noto Sans TC 以 `scripts/subset-font.py` 做成約 1.6MB 的子集。新增相依 dnd-kit。

**規格沒寫、實作時才看得出來的限制**：「班表」導覽版位關閉時（首波預設）簡易版沒有護理師框——關閉的功能就是不存在，不因換了畫面就繞過去；
有病人正在治療的床，床位清單拿不掉；拖病人上床時若當天沒有排班，自動建立的那一筆用「12 點前早班、17 點前午班、之後晚班」判斷時段（暫代值，Q-34）。

開發機在 1280×800、800×1280 截圖通過「不出現捲軸」；0930 平板確定 10 吋，這兩個尺寸即 10 吋平板的 CSS 尺寸（14.5）；**型號未定（Q-33）**，實機待做。第三者操作錄影與部署一輪待做。

### 迭代 14.1～14.5：實際操作後的修正（0928～0930）

五次都不是新的範圍，逐項紀錄在 `docs/notes/` 的五份修正紀錄。

| 迭代 | 事項 | 改了什麼 |
|---|---|---|
| 14.1 | **後端的「今天」是 UTC 日期** | 台北 00:00～08:00 即時總覽與簡易版床位圖停在前一天。`todayScheduledDate()` 改以主機時區的日界線為準（DEP-15 已保證主機是 Asia/Taipei） |
| 14.1 | 模擬 MDM 的狀態只在記憶體 | 見 5.6：啟動時交回納管狀態；開發環境自動納管 seed 的平板 |
| 14.1 | 每台平板要手打主機位址、序號、金鑰 | 裝置管理註冊成功時畫出**佈建 QR code**（`qrcode-generator`，瀏覽器裡自己畫）；外殼 `v0.3.0` 可掃描。**契約不加版號**：QR code 是既有載入網址，新舊外殼兩個方向都相容，加版號只會讓所有 0.2.0 被標成「版本不相容」 |
| 14.1 | 尚未佈建的平板看不出來 | 登記圖示 `wrench`，床位格與平板框都畫出來 |
| 14.2 | 簡易版的表單與清單被切掉 | 表單超出畫面就往上或往左長（`useStayOnScreen`）；右側框每頁幾格依框的實際大小算 |
| 14.2 | 誤下機之後排不回床上 | 加法端點 `POST /treatment-sessions/:id/reopen`：只限今天、寫稽核，沿用同一筆療程 |
| 14.2 | 簡易版不知道怎麼新增衛教；停用平板蓋住平板框 | 輪播內容框多一格「＋」；停用的平板回平板清單（排在後面、帶鎖頭） |
| 14.2 | 求助類別被切掉 | 依畫面大小分頁、每格同高；新開關 `HELP_NON_CLINICAL_GROUP`（見 5.8） |
| 14.3 | **斷線只有常駐總覽螢幕看得到** | `connection-status.tsx`：整個畫面閃爍紅框（不吃點擊）＋紅底白字橫幅，分「連線中斷／這台電腦沒有網路／登入已失效」。看得到病人的帳號沿用即時串流，**失敗過一次才算**（剛開頁面不誤報）；沒有串流的帳號每 15 秒探 `GET /api/health`、逾時 8 秒。專業版掛在主框架，與求助橫幅一起黏在上緣；簡易版獨占一列，整頁仍不捲動 |
| 14.3 | **病人端請求沒有逾時上限** | 主機斷電時請求不會出錯，只會一直等。`device.ts` 的 `deviceFetch`：16 個請求一律 8 秒逾時，最慢約 11 秒改成「請按床邊呼叫鈴」。不用 `AbortSignal.timeout()`——外殼支援到 Android 5，舊版 WebView 沒有它 |
| 14.4 | **大量求助湧入時，專業版求助橫幅蓋掉整個畫面** | 橫幅從迭代 2 起黏在上緣、一則一條、沒有上限，別處接起來的也不消失。`App.tsx` 的 `HelpRequestAlerts`：最多 `MAX_ALERT_TOASTS`（3）條，其餘收成一列「還有 N 則求助」＋「全部查看」；緊急的排前面，收掉的有緊急時那一列用警示色。快照裡狀態已不是待處理的不畫，**快照裡找不到的留著**（快照可能比求助事件舊）。不用「限制高度加捲軸」：藏在捲軸後面等於看不到 |
| 14.5 | **醫師說透析室很暗，病人端改白底** | 只動 `design-tokens.css`：底層改白色與淺灰，四種語意色換成深色系，白底上 22 組搭配全數過 7:1（最低 7.21:1）。連帶兩處：輪播自己加底色（沒有底色時夜間 `brightness` 只調暗了字）；`:active` 由調亮改成變暗。`check:ui:design` 搭配清單補 line on surface-2 |
| 14.5 | **平板確定 10 吋** | 外殼全螢幕後，10 吋 Android 平板不論面板解析度 CSS 短邊都是 800。字級、選項圖示、邊距由 `vw` 改為 `vmin`（係數 × 8 ＝ 上限）：直放時不再每一級掉到下限；橫式數值與下限不變。`--dock-h` 仍依 `vh` |

14.3 的起因值得記下：院內主機的 Docker Desktop 從 Microsoft Store 安裝，可能自己更新、自己重新啟動；主機電源也不穩。
**那一刻護理端畫面停在最後一刻的資料，看起來一切正常**——而系統依 FR-S07 不准院外推播，主動通知誰都做不到，只能讓每一個畫面都看得出來。
斷線示警是「專業版不動」（FR-N14）的第一個例外，出自使用者 0929 的指示；14.4 的求助橫幅上限是第二個，同日使用者回報後指示，同樣只改一個元件。

**同日另補一處後端**：備份另寫同名 `.sha256`（見 5.11）。

每一次都有自己的驗收腳本（`verify:iteration14-1`、`14-2`、`14-3`、`14-4`、`14-5`，前兩個另有 `:api`），並確認既有腳本全綠。
**14.5 在開發機實際看過**：合成平板綁定後，以無頭瀏覽器精確開 1280×800 與 800×1280（開發機螢幕只有 752 高，縮視窗做不出 800 高）；暗室裡看白底與 10 吋實機待做。
**14.3、14.4 還沒有在瀏覽器實際看過**（做變更的那個 clone 沒有資料庫），停掉後端、暫停後端模擬斷電、拔網路線、讓登入失效，以及一次送出九則求助，要在手動測試環境走一次。

### 迭代 15：院方 API 介接與自動化（1005）

機制見 5.21。驗收 `verify:iteration15`（7 步，不需後端）、`verify:iteration15:api`（12 步，要模擬院方 API）全綠；既有腳本兩處自身缺陷更正（迭代 4 的檔案路徑、迭代 2 的 UTC 日期），迭代 14 的端點白名單加兩支。
**模擬部署一輪與院方 API 的探測待做**（實作規格書 4.13 驗收現況、4.19）。


| 要知道的 | 在哪裡 |
|---|---|
| 抓取、解析、同步 | `apps/api/src/modules/hospital-sync/`：`hospital-api.format.ts`（純解析，探測工具共用）、`hospital-api.client.ts`（30 秒逾時、重試 3 次）、`hospital-api.adapter.ts`（`ClinicalDataSourcePort` 第三個實作）、`hospital-sync.service.ts`（排程與同步） |
| 與護理師拖曳同一條路徑 | 同步呼叫 `ScheduleService.create`、`BindingService.create`、`DevicesService.setBed`、`ClinicalDataImportService.import`，操作者是登入不了的系統帳號 `SYSTEM-HOSPITAL-SYNC`；`AuditService.recordByNurse` 認得它，稽核記成 `HOSPITAL_SYNC`／「院方資料同步」 |
| 護理師的更正優先 | `treatment_sessions.nurse_modified_at`（改狀態）與 `bed_nurse_modified_at`（換床）。兩支服務在操作者不是同步帳號時寫入 |
| 模擬院方 API、探測工具 | `apps/api/src/hospital-api-sim.ts`（`npm run dev:hospital-sim`；compose 的 `simulation` 設定檔）、`apps/api/src/hospital-api-probe.ts`（`npm run probe:hospital-api`） |
| 正式環境的兩道防線 | 啟動時：位址主機是 `hospital-api-sim` 就拒絕（`assertHospitalApiAllowed`）；抓取時：回應帶 `x-hd-simulated` 就整次作廢。模擬部署以 `HD_SIMULATION_DEPLOYMENT=yes` 明示 |
| 推送 | 護理端串流多一種事件 `HOSPITAL_SYNC`；平板 `GET /device/stream`（`DeviceEventsService`，事件不帶數值） |
| 開發機怎麼開 | `.env` 加 `HOSPITAL_API_BASE_URL=http://localhost:8090/dialysislist.php`，先 `npm run dev:hospital-sim` 再 `npm run dev:api`。不加就跟以前一樣，簡易版照人工流程 |

### 迭代 16：病人端「本次透析」面板與跑馬燈（1005）

三層輪播拿掉，病人端首頁中間改成面板、底部一條跑馬燈（機制見 5.19 末段）。驗收 `verify:iteration16`（7 步）與 `verify:iteration16:api`（8 步）全綠，五支既有腳本依實作規格書 1.1 第二次刻意改動（`verify:iteration6`、`8`、`14`、`14:api`、`14-5`），斷言沒有放寬。
開發機 1280×800 與 800×1280 截圖不捲動；**跑馬燈的速度要請長者看過**（驗收第 10 條），開關因此預設關閉。


| 要知道的 | 在哪裡 |
|---|---|
| 病人端首頁的資料 | `apps/api/src/modules/patient-home/`：`patient-home.service.ts`（面板、跑馬燈、行為參數、問卷到期；夜間判定也搬到這裡）、`device-home.controller.ts`（`GET /device/home`、`POST /device/marquee/plays`） |
| 護理端的內容管理 | `modules/carousel/` 只剩上下架、播放範圍、播放統計；路徑仍是 `/carousel`，稽核動作名稱不變 |
| 畫面 | `patient-pwa/src/TodayPanel.tsx`、`LineChart.tsx`、`Marquee.tsx`；`CarouselScreen.tsx` 已刪。樣式在 `styles.css` 第 5 節，語彙 `--c-chart-line`、`--t-marquee`、`--t-display`（原 `--t-carousel`） |
| 驗收 | `verify:iteration16`（不需後端）、`verify:iteration16:api`（要模擬院方 API，與迭代 15 相同的前提）；`check:ui:design` 多一組「面板不做判讀」 |
| 開發機看畫面 | 照迭代 15 開模擬院方 API 與後端，配一台開著的病人端給進行中的模擬病人；跑馬燈要另外開開關、上架內容 |
| 順手更正 | 營運參數的修改端點原本寫死 1～1000，0 存不進去（夜間 0 時、床號格式 0、開頭靜止 0 秒），上限 1800 的閒置門檻也到不了；改成只擋非負整數，範圍由服務依定義表檢查 |

### 迭代 17.5：透析一律開始後四小時結束（1007）

使用者決定 17.4 截圖時發現的既有問題統一用開始後四小時——本透析中心透析一律四小時，是院方硬性規定；同日追加**不管院方資料有沒有預計結束時間都是四小時**，專業版也全面套用（《[迭代 17.5 修正紀錄](../notes/iteration-17-5-fixes.md)》）。工程上要知道的：

| 要知道的 | 在哪裡 |
|---|---|
| 四小時寫在哪 | `@hd/shared` 的 `DIALYSIS_SESSION_MINUTES = 240`、`plannedDialysisEndMs(startedAtMs)`（**只收開始時間**）、`dialysisProgress(startedAtMs, nowMs)`（`hospital-api.ts`） |
| 用到的地方 | 病人端 `App.tsx` 的 `endsAt`、`TodayPanel.tsx` 的 `plannedEnd`（原本的 `DEFAULT_SESSION_MS` 拿掉）、簡易版 `TabletCell.tsx` 的 `progressOf`（起點 `state.startedAt ?? state.binding?.boundAt`）；後端 `RealtimeStateService` 的 `composeBindingProgress`（專業版 `OverviewPage`、常駐總覽 `WallDisplayPage` 畫的 `progressPercent`、`elapsedMinutes`，起點 `session.startedAt ?? binding.boundAt`）與 `awaitingDischargeConfirm`（開始後四小時加門檻） |
| 沒有動的 | 資料表、端點。`expected_end_at`／`expectedEndAt` 照樣記錄與回傳，只是不再拿來算；綁定有效期限 `expiresAt`（到期自動解除）不改 |
| 改了的驗收 | `verify:iteration15` 第 4 步改成「一律 `plannedDialysisEndMs(開始)`」；`verify:iteration15:api` 的待確認下機改成「院方預計結束已過、開始才 30 分鐘 → 不標」＋「開始 310 分鐘前、沒有預計結束 → 標」（實作規格書 1.1 第七次） |
| 驗收 | `verify:iteration17-5`（6 步，不需後端；transpile `hospital-api.ts` 實際跑一次）；`15:api`、`16:api`、`14:api`、`17:api` 對著模擬院方 API 通過 |

### 迭代 17.4：病人平板加回姓名與現在時間（1007）

使用者指示病人平板還是要有病人姓名與現在時間（《[迭代 17.4 修正紀錄](../notes/iteration-17-4-fixes.md)》）。工程上要知道的：

| 要知道的 | 在哪裡 |
|---|---|
| 姓名的來源 | `DeviceSessionState` 的 `patient.displayName`（`GET /device/session`，迭代 1 起就有）；`App.tsx` 傳給 `HomeScreen` 的 `patientName`。**`DeviceHomeView` 不加欄位**——面板的資料仍然拿不到姓名 |
| 畫面 | `HomeScreen.tsx` 的 `.home-name`（床號右邊）、`<time className="home-now">`（最右邊，`margin-left: auto`）；直放時 `styles.css` 把 `.home-progress`、`.home-tasks`、`.home-status` 排到第二列（`order: 1`） |
| 時分 | `patient-pwa/src/clock.ts` 的 `TIME`、`useMinuteClock`（每 30 秒），`TodayPanel.tsx` 也改用它 |
| 改了的驗收 | `verify:iteration14` 第 1 步：「首頁沒有姓名與病歷號」改成「首頁沒有病歷號、姓名只畫在 `.home-name` 一處」（實作規格書 1.1 第六次）。`verify:iteration6:api`、`16:api` 驗首頁資料沒有姓名，仍成立、沒改 |
| 驗收 | `verify:iteration17-4`（5 步，不需後端） |
| 沒有動的 | 後端、資料表、端點、圖示登記 |
| 截圖時發現的既有問題 | 院方資料沒有 `expectedEndAt` 時，護理端 `TabletCell` 的 `progressOf` 退回綁定進度、病人端 `App.tsx` 用 `binding.expiresAt`、`TodayPanel` 用開始後 4 小時，三處終點不同；這次沒改。**1007 使用者決定統一用開始後 4 小時**（本透析中心一律四小時，是院方硬性規定）：要改 `progressOf` 與 `App.tsx`，~~實作另排~~ **迭代 17.5 已改**（見上一節） |

### 迭代 17.3：所有 AI 生成內容禁用簡體字與中國大陸用語（1007）

使用者指示系統中所有 AI 生成的內容禁用支語與簡體字（《[迭代 17.3 修正紀錄](../notes/iteration-17-3-fixes.md)》）。工程上要知道的：

| 要知道的 | 在哪裡 |
|---|---|
| 把關在閘道 | `AiGatewayService.attempt()` 的生成迴圈（見 5.9）。全系統只有這裡呼叫 `provider.generate`，`verify:iteration17-3` 步驟 7 會掃一次 |
| 字表 | `packages/shared/zh-tw/` 三個 txt：`words.txt`（人工維護，160 組，37 個詞以註解放行）、`simplified.txt`（3795 字）、`variants.txt`（41 字），後兩份由 `scripts/zh-tw-data.mjs --opencc <目錄>` 從 OpenCC 字表產生。`npm run zh-tw:data` 產生 `packages/shared/src/zh-tw-data.ts`，**改 txt 一定要重新產生**，`-- --check` 只比對 |
| 檢查函式 | `packages/shared/src/zh-tw.ts`：`findZhTwIssues`（較長的詞命中時不另報被它包住的短詞，與 hook 相同）、`describeZhTwIssues`、`zhTwRetryNote`；字表延到第一次用到才解析 |
| 最後一次仍不合格 | 照樣交出、記成 `SUCCESS`，不會失敗；`AiAttemptFailureKind` 沒有多任何一種，也沒有 422 |
| 前端不留痕跡 | `apps/api/src/common/zh-tw-retry.ts`：`HIDE_ZH_TW_REJECTED_INVOCATIONS`、`HIDE_ZH_TW_REJECTED_AUDITS` 套在兩個 repository 的 `query`（只認錯誤訊息或稽核說明裡的「輸出含簡體字或中國大陸用語」，其他失敗照常列出）；`withoutZhTwRetryNote` 在 `toAiInvocationEntry` 截掉重寫附註。資料庫照記每一次 |
| 隨版本帶入的草稿 | 匯入時不另查用語（最初的版本有查，會讓稽核出現「因用語未匯入」，1007 追加調整時拿掉） |
| 沒有動的 | 資料表、端點、稽核動作的種類、兩端畫面都沒動 |
| 驗收 | `verify:iteration17-3`（7 步，不需後端、不需資料庫；閘道用替身組起來）；`verify:iteration3`、`4`、`17:api` 回歸未改 |

### 迭代 17.2：簡易版中間改成平板、病人框重新整理與排序（1007）

使用者看了 1006 的簡易版截圖提出兩件事（《[迭代 17.2 修正紀錄](../notes/iteration-17-2-fixes.md)》）。工程上要知道的：

| 要知道的 | 在哪裡 |
|---|---|
| 中間是平板 | `simple/TabletCell.tsx`（取代 `BedCell.tsx`）；`model.ts` 的 `shownTablets`（沒停用的、依序號）、`tabletView`、`tabletBed`（接了院方資料只有服務中的平板有床號）。平板格是 `DropZone`，`Pickable` 不再兼放置區；`DragItem` 只剩 `PATIENT`、`NEW_PATIENT`、`CONTENT`、`DRAFT`，`DropTarget` 沒有 `BED` |
| 右邊兩框 | `Trays.tsx` 拿掉 `NurseTray`、`TabletTray`、`TabletChip`；`--c-zone-nurse`、`--c-zone-tablet` 與 `check:ui:design` 的四列搭配一起拿掉；簡易版不再呼叫 `listShifts`、`assignShiftBeds` |
| 病人框順序 | `model.ts` 的 `trayOrder`：療程 `IN_PROGRESS` 的依 `startedAt` 由晚到早，其餘 `Intl.Collator('zh-TW-u-co-stroke')`；`verify:iteration17-2` 用 TypeScript 編譯器把 `model.ts` 轉成 JavaScript 載入、實際跑一次 |
| 重新整理 | `Workbench.tsx` 的 `refreshFromHospital` → `api.runHospitalSync()` → `reload()`；`POST /hospital-sync/run` 權限改 `PATIENT_MONITOR`（`HospitalSyncService.run` 本來就共用進行中的那一次）；圖示 `refresh-cw` 登記 |
| 沒接院方資料時的床 | `actions.tsx` 的 `setTabletBed`（取代 `moveTablet`，同一支 `setDeviceBed`）；`TabletCell` 的床號按鈕要 `DEVICE_MANAGE` |
| 驗收 | `verify:iteration17-2`（6 步，不需後端）；依實作規格書 1.1 第五次改寫 `verify:iteration14`、`14-1`、`14-2`、`15`、`17`、`17-1`。接了院方資料的畫面還沒在瀏覽器看過（午夜 `demo:patient` 拒跑） |

### 迭代 17.1：停用統一、把病人拖到平板、一鍵展示病人端（1006）

使用者一次提出七件事（《[迭代 17.1 修正紀錄](../notes/iteration-17-1-fixes.md)》）。工程上要知道的：

| 要知道的 | 在哪裡 |
|---|---|
| **不再自動接上平板** | `HospitalSyncService` 拿掉 `tryAutoBind`、`setPreferredDevice`；`PUT /patients/:id/preferred-device` 拿掉；`patients.preferred_device_id` 留著不讀不寫 |
| 配平板時平板跟著療程的床 | `BindingService.followSessionBed`：直接用 `DeviceRepository.moveToBed`，**不經 `DevicesService.setBed`**（那一支會標「護理師手動換床」，之後同步就不跟院方換床）；目的床的平板正在服務別人就不搬 |
| 手動解除不算更正 | `releaseByNurse` 只有 `NORMAL_DISCHARGE` 才 `markNurseModified`；手動解除後療程退回已排班，下一次同步照院方接回進行中 |
| 開始時間 | 綁定交易裡，進行中且已有開始時間的療程不覆寫；同步在院方判定開始時把先配好的療程改成院方的開始時間；跨班別時進行中的那一筆也跟著換班別 |
| 停用 | `DevicesService.setLocked`：有進行中綁定就 409；停用時清 `bed_no`。入口只剩專業版 `pages/SystemTabletsCard.tsx` |
| 簡易版 | 放置區 `TABLET_SLOT`；`Pickable` 帶 `target` 時同時是放置區（`useDraggable` 與 `useDroppable` 掛同一個節點）；`TabletChip` 兩處共用；接了院方資料時 `tabletOnBed` 只把有綁定的平板畫在床上 |
| 導覽的「一頁裡的一段」 | `NavItemDefinition.partOf`：`viewFor` 不給連結、放進 `NavigationView.sections`；`isAvailable` 連所屬頁一起看；`PRIMARY` 擋下。`DISCHARGE_EDUCATION` 是第一個 |
| 一鍵展示 | `npm run demo:patient`（`apps/api/scripts/demo-patient.ts`）：資料庫放在 `DATABASE_URL` 旁的 `demo/`（DEP-37 擋暫存目錄）、`nest build` 後以 `dist/main.js` 起後端、模擬院方 API 用新的 `HOSPITAL_API_SIM_IN_PROGRESS_MINUTES`；截圖在 Windows 經 PowerShell `Start-Process -Wait` 叫 Chrome |
| 驗收 | `verify:iteration17-1`（6 步，不需後端）；依實作規格書 1.1 第四次改寫 `verify:iteration14-1`、`14-2`、`15`、`15:api`、`16:api`。**`15:api`、`16:api` 1006 沒有跑**（午夜前後拒絕執行） |

### 迭代 17：跑馬燈內容由 AI 生成、護理師核准（1005）

護理師只核准或退回 AI 的「標題：內容」草稿；病人端只收已核准的。送進 AI 的只有衛教主題（SRS 附錄 C.6）或公告事由，**沒有任何病人資料**；格式不對或超過標題 12 字、內容 60 字就重新生成，最多三次。
「一句話」與「內容留白時播一句話」的退路一起拿掉。驗收 `verify:iteration17`（8 步）與 `verify:iteration17:api`（9 步）全綠，五支既有腳本依實作規格書 1.1 第三次跟著改（`verify:iteration6`、`14`、`14-2`、`14:api`、`16:api`）。
**隨版本帶入的草稿這一版不是實驗室模型寫的**，連上實驗室後用 `marquee:bundle` 重寫。


| 要知道的 | 在哪裡 |
|---|---|
| 草稿怎麼生出來 | `modules/carousel/marquee-draft.service.ts`（排入背景佇列、經 `AiGatewayService.attempt` 呼叫、寫回、隨版本帶入的匯入）；提示與解析在 `marquee-draft.ts`，**不碰資料庫、不呼叫模型**，驗收腳本直接拿來測「超過字數就重新生成」 |
| 核准、退回、撤回、上下架 | `modules/carousel/carousel.service.ts`；核准與退回在 `CarouselItemRepository` 是條件式更新（只動 `PENDING` 的那一列） |
| 病人端怎麼擋 | `CarouselItemRepository.listPlayable` 的條件多 `approval_status = APPROVED`——端點層擋，不是畫面藏 |
| 隨版本帶入的草稿 | `modules/carousel/marquee-bundle.ts`（資料檔）；重新生成 `npm run marquee:bundle -- --per-topic 2`（對著開發機跑著的後端要草稿，模型是模擬時拒跑；不寫入端點位址） |
| 系統帳號多一個 | `SYSTEM-RELEASE-CONTENT`「隨版本帶入」，與 `SYSTEM-HOSPITAL-SYNC` 同規則：`nurseLabel()` 顯示中文、`NurseRepository` 的 `PEOPLE_ONLY` 排除 |
| 畫面 | 簡易版 `simple/Trays.tsx` 的 `ContentTray`（草稿卡）、`actions.tsx` 的 `approveDraft`／`rejectDraft`／`requestDraft`、`Workbench.tsx` 的 `NewDraftForm`；專業版 `pages/CarouselPage.tsx` 改寫。圖示多 `check`、`ban` |
| 驗收 | `verify:iteration17`（不需後端）、`verify:iteration17:api`（後端開著、模型用模擬即可，不需模擬院方 API） |

### 規模

| 量測 | Iteration 2 時點 | 迭代 4 完成 | 迭代 5 完成 | 迭代 6 完成 | 迭代 7 完成 | 迭代 9 完成 | 迭代 10 完成 | 迭代 14.5 完成 | 迭代 17 完成 |
|---|---|---|---|---|---|---|---|---|---|
| API 路由 | 43 | 78 | 90 | 107 | 109 | 116 | 117 | 124 | 136 |
| 資料表 | 10 | 29 | 36 | 39 | 40 | 54 | 54 | 56 | 58 |
| 稽核動作 | 32 | 52 | 66 | 68 | 74 | 82 | 84 | 90 | 109 |
| 權限碼 | 9 | 17 | 20 | 21 | 21 | 23 | 23 | 23 | 23 |
| 角色 | 3 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 |
| 功能開關 | — | 10 | 10 | 10 | 10 | 11 | 11 | 12 | 12 |
| 營運參數 | — | — | 6 | 12 | 12 | 20 | 20 | 22 | 27 |

（迭代 6 沒有新增功能開關：輪播三層的開關在迭代 3 就已建好並預設關閉，這次做的是把它們的
「開啟條件」從「功能尚未實作」換成實際判定。迭代 7 只多一張 `update_runs` 與兩個維運端點，
新增的六種稽核動作全是更新流程與遷移防呆留下的軌跡。DEP-37 的三處補做沒有動到任何一張表，
改的是啟動時的判定與兩個維運端點多回傳的幾個欄位。**迭代 8 一張表都沒動、一個端點都沒加**，
因此表上沒有它那一欄。）

**迭代 9 一次多了 14 張表**，但它們幾乎都是同一個形狀：三組「版本表加題目表加選項表」。
新增的 8 個營運參數也是同一類東西——**「其他」的提醒門檻、每月加問的間隔、趨勢偏離的三個門檻、
抽題規則的三個上限**，全部是護理長會想調、而工程師不該替他決定的數字。

**迭代 10 幾乎沒有動資料模型**：`devices` 多三個欄位、一個平板端端點、兩種稽核動作，
就這樣。它的工作量全在 repo 之外——**把已經做好的東西變成一份帶得進院內的檔案**，
以及把「帶進去之後會發生什麼」實際試一次。

**迭代 11～14.5 合起來只多 7 條路由、2 張表、6 種稽核動作**，而且全部是加法：
迭代 11、13 一條都沒加（它們的工作量在 compose、映像檔與 `services/`）；迭代 12 加一條外殼契約端點；
迭代 14 加四條（床位、平板換床、輪播播放範圍、結案後補改處理結果），14.2 加一條重新開啟療程；兩張表是 `beds` 與 `carousel_item_targets`。
新增的兩個營運參數是病人端任務的時點（心情、衛教），新增的開關是求助畫面的「其他」那一框。
**簡易版整個工作台沒有新增任何一條「專業版做得到、只是換個端點」的路由**——那是刻意的，見 6「迭代 14」。

**迭代 15～17 合起來多 12 條路由（淨增）、2 張表、19 種稽核動作**：
迭代 15 加六條（院方資料同步的狀態、紀錄、手動再抓一次，配平板，帶入最近一筆血壓，平板的推送串流）與兩張表；
迭代 16 加兩條（`GET /device/home`、`POST /device/marquee/plays`）、拿掉兩條（`GET /device/carousel`、`POST /device/carousel/view-events`），**一張表都沒加**；
迭代 17 加六條（草稿主題、要一份草稿、核准、退回、撤回、上下架時間），在 `carousel_items` 加七欄。
功能開關的數字沒變，是因為輪播三層的開關停用、換成面板與跑馬燈，再加上 1005 的「需要抽血數值的功能」（三減三加）；
營運參數淨增五個：院方 API 四個（抓取頻率、多久沒更新要提示、待確認下機的時間、床號格式），跑馬燈三個（速度、開頭靜止、兩則間隔），輪播的卡片停留與細節頁退回兩個停用。
（路由數 0930 以前沿用各迭代新增的端點累加；迭代 17 那一欄改以控制器實際的路由裝飾器計數，兩種計法在 14.5 時點一致。）

### 共用常數的角色

`packages/shared` 不只是型別。以下**業務規則**放在這裡，前後端共用同一份定義：

- `navigation.ts` — 迭代 9：17 項功能的**預設版位**與主列上限。只在第一次啟動時寫進資料表
- `content.ts` — 迭代 9：SRS 附錄 C 的全部預設內容（求助類別、處理方式與結果、問卷題目、
  衛教題庫 35 題、回饋題目）。**這是「第一次啟動時寫進資料表的預設值」，不是執行期的資料來源**
- `routeHelpRequest()` — 求助分派規則。前端顯示的分派結果與後端計算結果保證一致。
  迭代 9 起輸入從「類別」換成「組別」，組別存在資料表裡
- `AuditAction` / `Permission` / `NurseRole` — 動作識別字、權限碼與角色
- `SYMPTOM_TREND_DISCLAIMER` — 非診斷結果提示文字
- `platform.ts` — 功能開關定義與開啟條件、模型與臨床資料介面層的共用型別
- `education.ts` — 衛教主題 `EDU-TOPICS-v1`、題庫 `EDU-QUIZ-v1`、回饋題目與 `PSY-DEV-v1` 偏離規則
- `nursing.ts` — 事件範本 `EVENT-TEMPLATES-v2`（1005 新增「透析中低血壓處置」）、AI 初稿處置、SOP 查詢結果類別
- `operations.ts` — 迭代 5：`evaluateLabourRules()` 勞動條件判定、班別定義、成效基準指標定義，以及三處暫代值的**預設值**（注意：只是預設值，現行值一律讀資料表）。迭代 6 另加六項輪播行為參數的定義（1005 迭代 16 停用其中兩項——卡片停留與細節頁退回，列在 `RETIRED_OPERATIONAL_SETTING_KEYS`；新增跑馬燈的速度、開頭靜止、兩則間隔三項）
- `carousel.ts` — 迭代 6：衛教與公告的內容型別與長度上限、播放紀錄的來源與種類。1005 迭代 16 起只剩護理端內容管理與統計要用的部分（病人端的輪播卡片型別拿掉），~~`marqueeBodyOf()` 決定跑馬燈那一則的「內容」~~。迭代 17 起多核准狀態、來源、長度上限（`marqueeLengthProblem()`，前後端共用）與草稿的請求型別，一句話與 `marqueeBodyOf()` 拿掉
- `hospital-api.ts` — 迭代 15：院方透析清單 API 的 51 欄位置表（**陣列沒有欄位名稱，只能靠位置認**）、同步系統帳號、模擬標頭、抓取結果與「沒有自動接上」的原因、床號正規化。同步與探測工具共用這一份
- `patient-home.ts` — 迭代 16：病人端首頁 `DeviceHomeView`、面板 `DialysisPanelView`（只有畫面要用的欄位）、跑馬燈的行為參數與一則的型別、`marqueeText()`
- `kiosk-shell.ts` — 迭代 12：外殼契約版本、JS 介面型別、由外殼版本推算「版本正常／外殼過舊／版本不相容／未回報」。**契約的程式真本**，文件真本是《病人端外殼 App 契約》，兩者與 `shell.pin` 要一起改
- `beds.ts` — 迭代 14：預設床位（15 床，`01`～`15`）。一樣只是「資料表空的時候寫入的預設值」；1005 起床號照醫院編號、不設上限（原本的 40 床上限已拿掉）

**迭代 4 的暫定內容原本全部在這裡並標版本字串**，改內容要改常數並升版。
**迭代 9 把這件事整個翻過來**：內容搬進資料表，護理長在畫面上改、立刻生效，不必重新部署。

`PRE_DIALYSIS_SYMPTOM_QUESTIONS`、`QUIZ_QUESTIONS`、`FEEDBACK_ITEMS`、`EDUCATION_TOPICS`、
`HELP_REQUEST_CATEGORY_LABELS` 這幾份**還在檔案裡，但只剩一個用途**：
把迭代 9 之前那一版補寫成第 1 版，讓既有作答還原得出當時的題目。
執行期沒有任何一行程式讀它們——依 3.14 第 5 條，**不得留下「程式讀常數、介面讀資料表」的雙軌**。
依《資料庫使用規範》18.2「一次更新只做加法」，它們在下一版才移除。

**改動 `packages/shared` 後必須重跑 `npm run build:shared`**（`npm run dev` 會自動先跑一次）。

---

## 7. 🔒 高風險三項：有條件納入，排在迭代 18（原迭代 7 → 11 → 15）

> **編號重排過兩次**：0919 部署前的四個修正迭代占用了 7～10，規則引擎順延為迭代 11；0926 第一次進院失敗之後的四件事又占用了 11～14，再順延為迭代 15；1005 院方 API 等三件事占用 15～17，又順延為**迭代 18**。內容一字未改，只是往後挪。0916 以前的紀錄裡「迭代 7」、0923 以前的「迭代 11」、1005 以前的「迭代 15」指的都是本節，對帳時看實作規格書 4.0.1、4.0.3、4.0.4 的對照表。
>
> **首波試用期間，這三項尚未實作，一律不提供服務**：介面上不出現入口，後端端點一併擋下（DEP-34）。不做灰色按鈕、不做「敬請期待」。

**FR-P03**（風險分層）、**FR-P05**（預警）、**FR-N06**（劑量建議）在 Iteration 2 時因高 SaMD 風險整條排除。0910 起改為**納入**，現排在迭代 18，以自建規則引擎實作並受 FR-R01～R08 約束（實作規格書 1.4、3.6、4.16）。

目前狀態：

- 規則引擎與三項功能**一行都還沒寫**
- 三個功能開關已在迭代 3 建好，預設關閉；開啟條件由後端判定，規則引擎不存在，所以目前開不了
- 啟用需要兩個外部答覆：TFDA 分類書面確認（Q-02）與臨床端的規則門檻值（Q-03）。**兩者不到，迭代 18 仍可完成實作與合成資料驗收**，差別只在能不能對真實病人開
- FR-N07 的「預測」部分也併入迭代 18；迭代 4 只做計算與趨勢圖

在迭代 18 之前，現有功能照舊維持這條線：

- 求助分派 `routeHelpRequest()` 的輸入**只有**病人自選的類型與急迫度，不讀歷史資料
- 症狀趨勢摘要只做原樣列出與次數統計，不加權、不分級、不預測、不產生建議文字
- 總覽的「病人自述症狀」是把答案原樣呈現，不是系統評估
- 心理社會趨勢只陳述比對事實，不判斷心理狀態、不自動轉介
- 適足性趨勢圖不畫目標線、不標正常範圍
- 相關畫面與每一處 AI 產出固定顯示非診斷結果提示

**接手時請維持這條線。** 若某個需求疑似需要「依資料做出會影響臨床判斷的建議或分級」，而該功能未列於 SRS 5.6 節，應先停下來確認。

---

## 8. 效能觀察

**端到端延遲幾乎全部來自資料庫往返，不是即時同步機制。** 這條結論在三種資料庫位置下都成立：

| 量測內容 | Supabase 孟買 | Supabase 東京 | 本機 SQLite |
|---|---|---|---|
| 驗收腳本量測的單次 API 請求 | 1,741 – 2,249 ms | 702 ms | **約 2 ms** |
| 端到端（平板送出 → 護理端收到） | 4,710 – 5,899 ms | 1,856 – 1,893 ms | **約 10 ms** |
| 其中即時狀態同步本身 | 1 – 3 ms | 2 – 3 ms | — |

SRS 第 6 章要求 < 5 秒。孟買時期在門檻邊緣浮動、偶爾超標；東京時期已有餘裕；本機 SQLite 後不再是問題。

> 驗收腳本印出的「單次資料庫查詢往返」其實是一次**完整的已驗證 API 請求**，包含 `NurseAuthGuard` 的 2 次查詢加上端點本身的查詢 — 所以東京時期是純查詢往返（237 ms）的約 3 倍。判讀數字時要注意這一點。

### 寫入路徑已做的最佳化

東京時期端到端 1.9 秒 ≈ 3 趟資料庫往返 × ~237 ms ＋ 應用層處理。當時做的優化改用 SQLite 後仍保留：

- **合併裝置驗證查詢** — `DeviceSessionGuard` 一次查詢同時完成裝置身分與 Session Token 驗證
- **稽核寫入與即時廣播平行進行**
- **`refreshTreatmentSession()` 的四筆查詢併為一批平行發出**
- **清單頁面一律批次查詢**，避免 15 台平板的看板產生 N+1

### 資料庫搬遷紀錄

- **2026-09-07**：Supabase `ap-south-1`（孟買）→ `ap-northeast-1`（東京）。Supabase 不支援原地換區，做法是開新專案 ＋ `migrate deploy` ＋ `db:seed`，舊資料未搬移
- **2026-09-10**：迭代 3 改為 SQLite，**測試與正式皆同**（測試放開發者本機、專案目錄外；正式放院內伺服器本機磁碟）。`datasource.provider` 改為 `sqlite`，移除 `directUrl` 與 pooler 參數；既有兩支驗收腳本未修改任何一行即全數通過；`verify:iteration3` 同時送出 40 個請求未出現 `SQLITE_BUSY`
- **2026-09-11**：Supabase 專案刪除，環境變數與設定範本中的 Supabase 欄位一併移除

### 迭代 4 的背景工作

- 驗收標準第 6 條（生成期間臨床寫入不受影響）由 `verify:iteration4` 驗證：背景工作執行中同時送症狀回報，總覽照常即時更新
- 模擬供應者的回應延遲 `LLM_MOCK_LATENCY_MS` 預設 1200 ms，只是讓佇列與進度提示在開發時看得見，**不代表任何真實模型的效能**。真實延遲要等院內 AI 伺服器規格（Q-07）

---

## 9. ⚠️ 已知粗糙處

以下都是實測確認過的，不是猜測。第 1～4 項自 Iteration 2 起未處理，2026-09-29 重新確認第 1～3 項仍在。優先權不高但接手時值得知道：

| # | 問題 | 現況 | 建議 |
|---|---|---|---|
| 1 | **重複病歷號回 500** | `PatientsService.create` 沒攔 Prisma `P2002`，唯一鍵衝突直接冒成 500 | 攔截後改回 409 ＋ 中文訊息，與其他地方一致 |
| 2 | **DevicesPage 未依權限隱藏 UI** | 一般護理師看得到註冊表單與 MDM 按鈕，按下去才 403 | 加 `can(Permission.DEVICE_MANAGE)` 條件渲染（`PatientsPage` 已經這樣做了） |
| 3 | **專業版取消排班無 UI** | `POST /treatment-sessions/:id/cancel` 端點存在；迭代 14 起簡易版「病人上床」的復原會呼叫它，**專業版仍沒有按鈕** | 在 `ConsolePage` 補一顆按鈕 |
| 4 | **總覽無日期選擇器** | `GET /overview?date=` 支援查其他日期，UI 只看當日 | 視需求補 |
| 5 | **總覽螢幕 8 小時後要重新登入** | `JWT_EXPIRES_IN` 預設 8 小時，全天開著的總覽螢幕到期後出現逾時提示 | 待 Q-10 確認螢幕位置與使用方式後，再決定是否給總覽螢幕專用的長效帳號或延長機制 |

| 6 | **目標平板型號未定**（0930 已確定 10 吋） | 「不出現捲軸」在開發機 1280×800、800×1280 驗過（14.5 起以無頭瀏覽器精確開這兩個尺寸）；實機沒驗過 | 待 Q-33 的型號；定了之後在實機重做截圖驗收（`x150`）。院方若統一調過系統顯示大小，短邊就不是 800 |
| 7 | ~~**既有驗收腳本有一處環境相依**~~ **1005 迭代 16 解除** | `verify:iteration14:api` 步驟 4 預設「第二層輪播」開著，但 `verify:iteration6` 跑完會把它關回去，而第二層要有上架中的內容才准開。先跑過迭代 6 的環境裡這一步不通過 | 迭代 16 輪播拿掉、那一步改讀跑馬燈，腳本自己開跑馬燈與取消夜間時段、跑完改回（實作規格書 1.1 的表） |
| 8 | **`verify:iteration13` 第 2 步誤判** | 這一步在 `apps/` 底下找 Ollama 字樣（後端不得直接連推論端點），找到的是迭代 13 自己的驗收程式 `verify-iteration13.ts`，於是不通過。迭代 16 的回歸清單沒有它，迭代 17 回歸時發現（實作規格書 4.15 驗收現況） | 掃描範圍排除驗收程式本身；依實作規格書 1.1，改既有腳本要記下理由 |

**授權判斷本身沒有問題** — 全部在後端把關，前端只是沒藏好入口。

---

## 10. 開發環境

```bash
npm install
cp .env.example .env        # 填 DATABASE_URL / JWT_SECRET / SUPER_ADMIN_*，建議一併填 BACKUP_DIR
npm run build:shared
npm run prisma:migrate
npm run db:seed             # 含 4 份虛構 SOP 文件
npm run dev                 # api:3000 · nurse:5173 · patient:5174
```

**必填環境變數**：`DATABASE_URL`（`file:` 加絕對路徑）、`JWT_SECRET`、`SUPER_ADMIN_WORK_ID`、`SUPER_ADMIN_INITIAL_PASSWORD`。

**常用選填**：`BACKUP_DIR`（備份輸出）、`LLM_PROVIDER`（`mock`／`lab`／`onprem`，預設 `mock`）與 `LLM_ENDPOINT`／`LLM_API_KEY`／`LLM_MODEL_ID`、`LLM_MOCK_LATENCY_MS`（預設 1200）、`JWT_EXPIRES_IN`（預設 8 小時）、`BINDING_MAX_HOURS`（預設 6）。

**迭代 8、9 都沒有新增任何環境變數。** 迭代 8 一個端點都沒加；
迭代 9 加了不少端點，但它新增的每一個數字都是**營運參數**——
「其他」的提醒門檻、每月加問的間隔、趨勢偏離的三個門檻、抽題規則的三個上限，
一律存在 `operational_settings`，在護理端改，不在 `.env` 改。
**會被護理長調整的東西不該放在只有工程師動得到的地方。**

**迭代 7 新增的五個（只有正式環境會用到）**：`DEPLOYMENT_ENV=production` 把這台機器標成正式環境（時區不符即拒絕啟動、開發用的遷移指令被擋下、`API_PORT` 沒填即拒絕啟動）、`REQUIRED_TIME_ZONE`（預設 `Asia/Taipei`）、`PRISMA_ENGINES_DIR`（指向安裝包內的 Prisma 引擎，DEP-30；**迭代 11 隨安裝包撤除**）、`LLM_HEALTH_TIMEOUT_SECONDS`（健康檢查逾時，預設 5 秒，與單次生成的 `LLM_TIMEOUT_SECONDS` 分開）、`DB_DISK_MIN_FREE_MB`（資料庫磁碟保留空間下限，預設 1024，DEP-37）。

既有的 `API_PORT` 在正式環境的行為也變了：**開發機留空照舊用 3000，正式環境留空即拒絕啟動**（DEP-37 第 2 項）。

**迭代 11 起院內部署另有一份範本** `deploy/hospital.env.example`，只列 compose 要代換的變數（`HD_IMAGE_TAG`、`HD_BACKUP_DIR`、`HD_CONFIG_DIR`、三個 `HD_*_PORT`、`HD_PUBLIC_API_URL`、`MDM_KIOSK_BASE_URL`、`HD_SHELL_SRC_DIR`、`HD_SHELL_SIGNING` 等），逐項填法見部署手冊第十五冊之一（1001 起取代第十四冊之一）；迭代 15 多了 `HOSPITAL_API_BASE_URL` 與 `HD_SIMULATION_DEPLOYMENT` 兩個。**compose 不整份倒進容器**（DEP-13），容器要什麼在 `docker-compose.yml` 明寫；`UPDATE_PROBE_URL` 由 compose 直接給 `db:update`。
迭代 12 新增 `KIOSK_SHELL_MIN_VERSION`（最低可用外殼版本，留空用程式預設）；`MDM_KIOSK_BASE_URL` 在正式環境**必須是 `https://`**（迭代 14.1 的佈建 QR code 就是它）。
迭代 13 起 `LLM_ENDPOINT` 指向 AI 閘道、`LLM_MODEL_ID` 留空，`LLM_TIMEOUT_SECONDS` 要比閘道 `config.yaml` 的逾時大。
迭代 15 新增 `HOSPITAL_API_BASE_URL`（院方 API 的端點，**空白就是不抓**，簡易版照人工流程；院內的值不進 repo、不寫進任何文件）與 `SIMULATION_DEPLOYMENT`（compose 由 `HD_SIMULATION_DEPLOYMENT` 帶入，模擬部署填 `yes` 才准位址指向模擬院方 API）。抓取頻率是營運參數，不在 `.env`。
迭代 16、17 沒有新增環境變數：跑馬燈的速度與間隔都是營運參數。

> 資料庫檔案與 `BACKUP_DIR` 必須在**專案目錄外的本機磁碟**。相對路徑、專案目錄內、網路路徑、雲端同步資料夾，後端與 seed 一律拒絕啟動。
> 後端是唯一的寫入者：跑 `prisma:migrate`、`db:seed`、`db:restore` 或任何資料修補腳本前，**先停掉後端**。

### 驗收

```bash
npm run verify:acceptance   # 迭代 1 — 13 步驟
npm run verify:iteration2   # 迭代 2 — 11 步驟
npm run verify:iteration3   # 迭代 3 — 10 步驟
npm run verify:iteration4   # 迭代 4 — 18 步驟（需先 db:seed，並設定 BACKUP_DIR）
npm run verify:iteration5   # 迭代 5 — 15 步驟
npm run verify:iteration6   # 迭代 6 — 15 步驟
npm run verify:iteration7   # 迭代 7 — 11 步驟
npm run verify:iteration8   # 迭代 8 — 7 步驟（不需後端）
npm run verify:iteration9   # 迭代 9 — 10 步驟
npm run verify:iteration10  # 迭代 10
npm run verify:iteration11  # 迭代 11 — 靜態；加 -- --live 對 Docker 實測
npm run verify:iteration12  # 迭代 12 — 靜態；另有 verify:iteration12:api
npm run verify:iteration13  # 迭代 13 — 靜態；另有 verify:iteration13:api（閘道容器＋假推論端點）
npm run verify:iteration14  # 迭代 14 — 不需後端；另有 verify:iteration14:api
npm run verify:iteration14-1  # 14.1 — 7 步；另有 :api（停掉後端再啟動之後跑）
npm run verify:iteration14-2  # 14.2 — 8 步；另有 :api
npm run verify:iteration14-3  # 14.3 — 6 步（不需後端）
npm run verify:iteration14-4  # 14.4 — 5 步（不需後端）
npm run verify:iteration14-5  # 14.5 — 5 步（不需後端）
npm run verify:iteration15  # 迭代 15 — 7 步（不需後端）；另有 :api 12 步（要模擬院方 API）
npm run verify:iteration16  # 迭代 16 — 7 步（不需後端）；另有 :api 8 步（要模擬院方 API）
npm run verify:iteration17  # 迭代 17 — 8 步（不需後端）；另有 :api 9 步（模型用模擬即可）
npm run verify:iteration17-1  # 17.1 — 6 步（不需後端）
npm run verify:iteration17-2  # 17.2 — 6 步（不需後端）
npm run verify:iteration17-3  # 17.3 — 7 步（不需後端、不需資料庫）
npm run verify:iteration17-4  # 17.4 — 5 步（不需後端）
npm run verify:iteration17-5  # 17.5 — 5 步（不需後端）
npm run zh-tw:data          # 17.3：改了 packages/shared/zh-tw/ 的詞庫之後重新產生資料檔；-- --check 只比對
npm run demo:patient        # 17.1：一鍵展示病人端（模擬院方資料、另一個全新的資料庫）；-- --screenshot <檔名> 直接截圖
npm run check:all           # 六支盤點腳本（不需後端），0926 起多了 check:container
```

腳本都會建立少量標記過的合成資料並逐項斷言，涵蓋主線流程、錯誤路徑、權限隔離、冪等去重、稽核事件。**改動後請全部跑過。**

最近一次執行（2026-10-05，迭代 17 完成時）：迭代 15～17 各自的腳本與 `:api` 全綠；既有腳本回歸（`verify:acceptance`、`verify:iteration2`～`12`、`14` 系列與各自的 `:api`、`check:all` 六支）全綠，依實作規格書 1.1 改寫的幾支一併重跑。
**例外是 `verify:iteration13`**：它的第 2 步在 `apps/` 底下找 Ollama 字樣，找到的是迭代 13 自己那支驗收程式，與迭代 15～17 無關，見第 9 節第 8 項；`verify:iteration13:api` 要 Docker Desktop，這次沒跑（迭代 15～17 沒有動 AI 閘道）。結果記在實作規格書 4.13～4.15 各節的「驗收現況」。
0930 那一次（迭代 14.5）：`build`、`check:all` 六支、`verify:iteration8`、`verify:iteration14`、`14-1`～`14-5` 全綠。第 9 節第 7 項的環境相依迭代 16 已解除。

0919 的紀錄仍然成立：九支皆全數通過（`verify:iteration8` 不需要後端在跑，它驗的東西全部在前端原始碼與樣式表裡）；**盤點腳本全綠**——介面技術識別從 22 筆降到 0，遷移安全改成只掃上一次部署之後新增的那幾份（已經套用出去的遷移改不動，把它們掃出來只會得到一份改不動的清單，而**一支永遠是紅的檢查跟沒有那支檢查一樣：沒有人會再看它一眼**）。

**迭代 9 動了六支既有的驗收腳本，而且是非動不可的。** 題目與選項改成資料之後，
那幾支腳本原本照共用常數湊一份答案出來，送出去會被後端以「版本不符」擋下——**而擋下是對的**。
改法是加一支共用的填答器（`scripts/lib/questionnaire.ts`）：先問後端「現在生效的是哪一版、有哪幾題」，
再照那一份填。**斷言一條都沒有放寬**，改的只是「答案從哪裡來」。
另外 `verify:iteration4`、`verify:iteration5` 各多了一段：
離院衛教與班表、成效基準首波是關閉的，因此先確認關著時真的擋得住，再暫時提供、驗完關回去——
**驗收腳本不該因為預設是關的就跳過那一段，也不該把它留在開著的狀態。**

其中 `verify:iteration2` 改了一處，而且只有這一處：FR-N10 讓「只填自由文字即可結案」不再成立，那一段跟著改成新的結案方式。**迭代 2 原本要驗的行為一條都沒有放寬**——狀態轉換、留下處理者、總覽不再顯示待處理，斷言全部保留。這是目前唯一一次刻意改動既有驗收腳本，理由記在《實作規格書》1.1 節；其餘情況一律不得以「配合新功能」為由修改既有腳本。迭代 6 與迭代 7 都沒有再動過任何一支——迭代 7 的解除綁定回應只多了兩個欄位，既有欄位一個都沒有動，因此既有斷言原封不動仍然成立。

完整的手動測試步驟另有[測試手冊](../testing/manual-test-guide.md)：主手冊加迭代 3～17 二十一本分冊，**共 1051 個可勾選的測試項**（主手冊 156 項，分冊從迭代 3 的 66 項到迭代 14.5 的 11 項；0930 定版時 894 項）。迭代 17 起項次改用兩個字母（`aa`）。
0919 以前那幾冊要人眼與實機的部分仍然成立（迭代 3 的總覽螢幕連續 4 小時與拔網路、迭代 6 輪播的四節手指確認、迭代 8 標 ⚠️ 的十一項、迭代 9 的三條畫面護欄），
0926 之後的幾冊，**腳本驗不到、還沒走的**集中在這幾處：

- **[迭代 11 分冊](../testing/iteration-11.md)** 的 43 項，對應的實測已在開發機走過一輪（演練紀錄第 8 節）；**斷電重開後服務自己回來**只能在院內那台主機驗（Q-27）
- **[迭代 12 分冊](../testing/iteration-12.md)** 的 48 項：開發手機從下載頁安裝、釘住後退不出去、契約版本不合時平板上的提示列（§12.5～§12.7）——**要一支真的手機**
- **[迭代 13 分冊](../testing/iteration-13.md)** 的 47 項：實驗室上的真模型實測與繁中品質紀錄（§13.4），等實驗室連線
- **[迭代 14 分冊](../testing/iteration-14.md)** 的 56 項：九項任務由第三者一個動作完成並錄影（`x39`，Q-31）、開發機＋開發手機走一次部署一輪（`x56`）
- **[迭代 15](../testing/iteration-15.md)～[17](../testing/iteration-17.md)** 共 126 項：模擬部署（`--profile simulation`）走一輪、第三次進院在院內跑探測工具；**長者看跑馬燈速度**（迭代 16 §16.10，做完之前院內的開關保持關閉）；簡易版草稿卡在護理站解析度下實際看過（`aa9`～`aa26`）；實驗室模型重寫隨版本帶入的草稿（`aa32`、`aa33`）
- **[迭代 14.1](../testing/iteration-14-1.md)～[14.5](../testing/iteration-14-5.md)** 共 95 項：真的平板掃佈建 QR code（`x72`～`x77`）、直式實機（Q-33）、14.3 的四種斷線情境在瀏覽器實際看一次（`x111`～`x128`）、14.4 一次送出九則求助在兩種尺寸下看一次（`x131`～`x139`）、14.5 在暗的透析室裡由醫護看一次白底（`x146`）與 10 吋實機（`x150`）

---

## 11. 迭代 3、4 接手的人值得知道的決定

**迭代 3**

- **遷移的驗收標準是「既有腳本一行不改就通過」**。日後動資料層（例如換資料庫、改連線設定）也應以此為準，不要為了讓腳本過而改腳本
- 修掉兩個既有問題：`useAsyncMessage` 每次渲染產生新函式，造成各頁無限重抓；連不上伺服器時誤清登入權杖，使總覽螢幕停在登入畫面無法自行恢復。後者在推播移除後會直接變成漏看通報
- 功能開關的「關閉時完全不出現」同時做在前後端。只做前端等於沒做，只做後端會讓使用者看到一堆按了就 404 的按鈕

**迭代 4**

- `AiGatewayService` 多了 `attempt()`：背景工作要拿到「被擋下／失敗」那一次呼叫的紀錄 id 寫回結果，不能只收到例外。HTTP 端點照舊用 `invoke()`，行為與迭代 3 相同
- 模擬供應者依 `purpose` 組出貼近該功能的範例，並有可設定的回應延遲，讓佇列與進度提示在開發時看得見。實際的推論伺服器不讀 `purpose`
- SOP 查詢是**字詞比對**，不是向量檢索。好處是不需要額外模型、結果可解釋；壞處是換個說法可能就查不到。真實 SOP（Q-17）到位、院內伺服器規格（Q-07）確定後再評估要不要換
- 暫定內容（衛教主題、題庫、回饋題目、偏離規則、事件範本、適足性公式）一律放 `packages/shared` 並標版本，不寫在資料庫種子，也不寫死在元件裡

**新增待確認事項**：Q-23（衛教主題與題庫）、Q-24（回饋題目與偏離判定）、Q-25（事件範本）、Q-26（適足性公式與輸入來源），全部為 D 級，已用暫定值實作。

---

## 12. 下一階段

迭代 15～17 已完成（2026-10-05）。成效基準的建檔介面自迭代 5 就緒，**現在等的仍是現場的數字**：

> ⏰ **成效基準的量測（Q-01）有時效性。** 這不是開發端能做的事。系統正式啟用前沒測到，之後所有「省下 X 分鐘」的說法都只能靠估算。

### 第三次進院之前

1001 第二次進院 B 級部分成功，卡在護理端登入（`CORS_ORIGINS` 不放行護理端的來源）。第三次進院的目標與順序在實作規格書 4.19：

| 要做的事 | 在哪裡 | 卡在誰 |
|---|---|---|
| **主機位址由名稱換成 IP** | 部署手冊第十五冊之四、清冊 Q-27 第 12 題 | 現場。**1007 答覆 IP 是固定的**，前提成立 |
| 關掉 Docker Desktop 的使用統計（市集自動更新照舊不改） | 第十五冊 V-05、清冊 Q-27 第 9、10 題 | 現場（1007 答覆可以關） |
| 帶去的 tag 在開發機用 IP 模擬部署一次（含 `--profile simulation`），並故意用 `localhost` 開一次重現 `Failed to fetch` | 第十五冊之三 E-02；部署規範第 9 章第 8 項 | 開發端（要開 Docker Desktop） |
| 帶新 tag 是一次**更新**（迭代 15、17 各有一個遷移），照第十一冊 W-19 換版，不是重新 clone | 第十五冊之三 E-04 | 開發端 |
| 院內護理站的電腦登入成功之後，備份還原與重新開機各走一次；重新開機照 1007 的答覆測：開機、以 Administrator 登入（模擬護理長），之後不碰任何東西 | 第十五冊 V-19、第十五冊之三 E-09 | 現場 |
| 探測院方 API：只印結構、位址當場輸入不寫進 `.env` | 第十五冊 V-30a、清冊 Q-09 第 9 題 | 現場；**本系統能不能用、要不要報備待 Q-35** |
| 1001 那台主機有 15 床的預設床位（迭代 15 以前的版本建的），接上院方資料後到系統管理把 `01`～`15` 拿掉 | 實作規格書 4.13 待做 | 現場 |
| Defender 排除、主機上的 Git、Docker Hub 的 DNS（斷電重開、Docker Desktop 兩項設定 1007 已答） | 清冊 Q-27 其餘各題 | 院方。不擋登入，但首波試用前要有答案 |
| ~~沒有預計結束時間時三處進度統一用開始後 4 小時（1007 決定）~~ **1007 迭代 17.5 已完成** | 迭代 17.5 修正紀錄 | — |
| ~~專業版總覽與常駐總覽螢幕要不要也改成透析進度；沒有預計結束時要不要用開始後四小時判定「待確認下機」~~ **1007 使用者決定全面套用，迭代 17.5 追加已完成** | 迭代 17.5 修正紀錄 | — |
| 開發手機上的外殼實機驗收、真的平板掃佈建 QR code | 迭代 12 §12.5～§12.7、迭代 14.1 `x72`～`x77` | 開發端 |
| 實驗室上的真模型實測；用 `marquee:bundle` 重寫隨版本帶入的草稿 | 部署手冊第十三冊、迭代 17 `aa32`、`aa33` | 實驗室連線（Q-08） |

第三次進院照部署手冊**第十五冊**（新手版第二版）與之三、之四走。

### 迭代 15～19（1005 第三次重排）

| 迭代 | 主題 | 可否立即開始 | 啟用前要等的外部答覆 |
|---|---|---|---|
| ~~15~~ | ~~院方 API 介接與自動化（1005）~~ | **實作完成（1005）**，模擬院方 API 上驗收通過 | 對真實資料啟用：第三次進院的探測（Q-09 第 9 題）、使用報備與連線（Q-35） |
| ~~16~~ | ~~病人端「本次透析」面板與跑馬燈（1005）~~ | **實作完成（1005）**，模擬院方 API 上驗收與開發機截圖通過；跑馬燈速度待長者試看 | 無；實機待 Q-33，病人試看待 Q-31 |
| ~~17~~ | ~~跑馬燈內容由 AI 生成、護理師核准（1005）~~ | **實作完成（1005）**，驗收通過；隨版本帶入的草稿待實驗室模型重寫 | 正式環境的 AI 需 Q-07；在那之前用隨版本帶入的草稿；核准權限 1007 已答（所有護理師，Q-28） |
| 18 | 規則引擎與三項高風險功能（原 7 → 11 → 15） | 實作可以 | 法務書面確認（Q-02）＋臨床端門檻值（Q-03） |
| 19 | 管理儀表板、獎勵、對外揭露（原 8 → 12 → 16） | 建置可以 | L3 啟用需護理部同意（Q-04）；指標定義（Q-20）與核准角色（Q-21） |

迭代 15 的第一項是院方 API 探測工具，要趕在第三次進院前完成（實作規格書 4.19）——**1005 已完成**，指令在部署手冊第十五冊 V-30a；迭代 16、17 都不擋第三次進院。三個迭代的實作位置見 6「迭代 15」～「迭代 17」。

迭代 18 與其他迭代沒有相依，外部答覆若提早到齊可隨時往前插隊。
迭代 19 的成效指標會吃迭代 6 產生的 `carousel_view_events`（迭代 16 起改記跑馬燈每一則的播放），但那張表刻意不含個人層級資料，
因此它只回答得了「哪一類內容有人看」這種問題。

**接手時最容易搞混的一件事**：迭代編號重排過三次（0919、0926、1005）。
0916 以前的紀錄裡「迭代 7」、0923 以前的「迭代 11」、1005 以前的「迭代 15」指的都是規則引擎；0923 週報寫的「迭代 11、12 依原排程開始」也是既成紀錄。
**那些舊紀錄不回頭改寫**，對帳時看實作規格書 4.0.1、4.0.3、4.0.4 的對照表。

---

## 13. 每次動工前的自我檢查

摘自《實作規格書》第 5 章與《資料庫使用規範》第 16 條：

- [ ] 新增的資料表／欄位是否已對照 SRS 與稽核軌跡欄位需求
- [ ] 有沒有前端程式碼企圖直接碰資料庫檔案
- [ ] 存取控制是否寫在後端應用層（不依賴檔案權限或前端隱藏）
- [ ] 是否在業務邏輯中直接寫 SQL 或 SQLite 方言
- [ ] 新增的臨床數值欄位是否誤用浮點數
- [ ] 是否新增了第二個會寫入資料庫的常駐行程
- [ ] 是否有任何相依指向院外網域（跑 `npm run check:egress`）
- [ ] 呼叫語言模型是否一律經 `AiGatewayService`
- [ ] 是否在資料庫交易內等待模型回應
- [ ] 本次功能是否觸及有條件納入的項次；若是，功能開關是否預設關閉、前後端是否都擋
- [ ] 測試資料是否為虛構合成資料
- [ ] MDM 呼叫是否皆透過 `MdmProviderPort`
- [ ] schema 是否維持相容約束（無 enum、無 JSON 欄位、單一級聯路徑）
- [ ] 新畫面有沒有掛上導覽版位（`@RequireNavItem()`），還是又多了一個關不掉的功能
- [ ] 新增的選項或題目是不是寫進資料表，而不是又回到程式常數（跑 `npm run check:ui`）
- [ ] 護理長會想調的數字，有沒有放在只有工程師動得到的地方（`.env` 而非營運參數）
- [ ] 簡易版要做的事，是不是只呼叫專業版原有的端點；真的要加端點，是不是只做加法（`npm run verify:iteration14`）
- [ ] 用到的圖示有沒有在介面設計基準 4.6 登記、由 `sync-icons.mjs` 產生，而不是從套件或 CDN 直接引入
- [ ] 動了 `docker-compose.yml`、`Dockerfile` 或 `deploy/hospital.env.example`，有沒有回頭核對部署手冊第十一、十五冊與兩本 `.env` 子手冊（第十五冊之一、之二）（`npm run check:container`）
- [ ] 動了外殼契約，有沒有三處一起改：契約文件、`kiosk-shell.ts`、`shell.pin`（`npm run verify:iteration12`）
- [ ] 院方 API 判斷得出來的事，有沒有又要求護理師操作（SRS FR-S15）；同步要寫的東西，是不是走護理師操作時同一支服務
- [ ] 病人端面板有沒有出現判讀：警戒線、正常範圍、紅色、預測（`npm run check:ui:design`）
- [ ] 送進 AI 的東西有沒有任何病人資料；病人端看得到的 AI 產出，是不是一定先經護理師核准

---

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|
| [0930](https://94sh09sh19sh.github.io/hd-docs/0930/reports/progress-technical/) | 2026-09-30 | 改寫到迭代 14.5：迭代 11～14 與 14.1～14.5 的實作、規模表、驗收腳本清單與手動測試 894 項；已知問題第 6 項改為平板型號未定（尺寸 0930 已確定）；Q-27、Q-32 的 0930 答覆 |
| [0923](https://94sh09sh19sh.github.io/hd-docs/0923/reports/progress-technical/) | 2026-09-23 | 補上迭代 7～10：部署前的缺陷修正與資料保護、兩端介面重新設計、導覽版位與內容資料化、離線安裝包與平板佈建。規模表加一欄（資料表 40 → 54、營運參數 12 → 20），共用常數那一節改寫——附錄 C 的內容搬進資料表之後，那幾份常數只剩「把舊版補寫成第 1 版」一個用途 |
| [0916](https://94sh09sh19sh.github.io/hd-docs/0916/reports/progress-technical/) | 2026-09-16 | 改寫到迭代 6：封閉網路化、AI 輔助與護理記錄、求助處理與班表、閒置輪播與檔案匯入；資料庫改為 SQLite、推播改為院內 SSE 與常駐總覽螢幕，並換上重繪的架構圖 |
| [0909](https://94sh09sh19sh.github.io/hd-docs/0909/reports/progress-technical/) | 2026-09-09 | 首次定版 |

[← 回進度首頁](../index.md)
