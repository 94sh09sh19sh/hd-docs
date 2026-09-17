# 血液透析平板照護輔助系統 — 技術進度報告

**適用讀者**：接手或協作的工程師
**報告日期**：2026-09-12
**版本**：迭代 6 完成（master）
**Repo**：`94sh09sh19sh/hd-tablet-care`

> 本版由 0909 定版（Iteration 2 時點）改寫。0909 之後的主要變化：需求於 0910 改為 v2.0（SaMD 三項改為有條件納入、資料庫改 SQLite、封閉網路）；
> 迭代 3 完成資料層遷移與四個平台機制；迭代 4 完成 AI 輔助內容與護理記錄；迭代 5 完成求助處理完整紀錄、護理師班表與成效基準；迭代 6 完成閒置輪播與檔案匯入。
> 迭代編號沿用《實作規格書》v2.0：迭代 1、2 已完成，3～8 為 0910 重排後的規劃。

---

## 1. 專案脈絡

需求來源在 `docs/requirements/`，共六份文件。前五份**優先權不同，衝突時有明確的裁決順序**：

| 文件 | 角色 |
|---|---|
| [`srs.md`](../requirements/srs.md) | 功能需求來源（FR 編號皆引用自此）。v2.0 共六組：P 病人端、N 護理端、M 管理與營運、X 對外揭露、S 系統、R 高風險控制措施 |
| [`implementation-spec.md`](../requirements/implementation-spec.md) | 範圍界定、技術棧與迭代 3～8 規劃，**衝突時以此為準** |
| [`database-policy.md`](../requirements/database-policy.md) | 資料治理強制規則，**優先權等同實作規格書** |
| [`deployment-spec.md`](../requirements/deployment-spec.md) | 部署形態、環境界線與交付方式（0912 新增），**優先權等同實作規格書** |
| [`fde-assessment.md`](../requirements/fde-assessment.md) | 背景脈絡與選型理由 |
| [`open-questions.md`](../requirements/open-questions.md) | 唯一的待確認事項總表（Q-01～Q-28）。程式裡的暫定值多半對應其中一項 |

動工前請至少讀完前三份。這個專案有不少「看起來繞路」的設計，幾乎都源自這些文件的硬性約束。系統實體與邏輯架構見[架構圖](../requirements/architecture-diagrams.md)（2026-09-12 更新至迭代 6：圖一的照護業務模組補上閒置輪播，兩張圖的正式主機標上 DGX Spark 與容器部署。迭代 6 沒有新增任何機器或網路連線，圖二的分區與線一條未改）。圖片走 repo 相對路徑，文件站上就是 repo 裡的這兩個檔案。

---

## 2. 架構

```
v0/
├── apps/
│   ├── api/            NestJS — 後端唯一入口：身分驗證、裝置綁定、症狀回報、緊急通報、
│   │                            即時狀態、稽核、MDM／模型／臨床資料三個介面層、功能開關、
│   │                            備份、背景佇列、衛教、回饋、護理記錄、適足性、SOP 查詢
│   ├── nurse-pwa/      React PWA — 護理站主控台與常駐總覽螢幕（:5173）
│   └── patient-pwa/    React PWA — 病人端平板 Kiosk（:5174）
├── packages/
│   └── shared/         前後端共用型別、常數與業務規則（@hd/shared）
├── scripts/            零院外連線盤點、文件站同步
└── docs/               需求、報告、參考與測試文件
```

npm workspaces monorepo。約 23,700 行 TypeScript（不含 dist／node_modules，含四支驗收腳本；Iteration 2 時點約 10,000 行）。

**技術棧**：NestJS 11 · Prisma 6 · SQLite（測試與正式皆同）· React 19 · Vite 6 · TypeScript 5.7

### 資料流

```
病人端 PWA ─┐                   ┌─→ Repository 層 ─→ Prisma ─→ SQLite 檔案（專案目錄外）
            ├─→ 後端 API ───────┤
護理端 PWA ─┘  （SSE 回推）     └─→ AiGatewayService ─→ LlmProviderPort ─→ mock／lab／onprem
```

**前端一律不直接碰資料庫，也不直接碰模型。** 兩個 PWA 都沒有資料庫或模型相關套件；後端是唯一開啟資料庫檔案的常駐寫入行程，也是唯一呼叫模型的地方。

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

共 39 張表，五個 migration：`init`、`iteration3_closed_network`、`iteration4_ai_content`、`iteration5_help_resolution_shifts_baseline`、`iteration6_carousel_file_import`（SQLite 遷移時整組重建，舊資料依《資料庫使用規範》第 15 條不搬）。逐欄說明見《[資料字典](../reference/data-dictionary.md)》。

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

### 值得注意的地方

| 表 | 值得注意的地方 |
|---|---|
| `nurses` | `role` / `status` 為字串；`canApproveNurses` 支援單獨分享審核權限 |
| `nurse_sessions` | 存 JWT 的 `jti`，讓 token **可被主動作廢**（變更密碼、降權時） |
| `devices` | `apiKeyHash` 用 SHA-256（金鑰是 256-bit 隨機值，非使用者密碼）；MDM 狀態欄位 |
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

### 5.6 MDM 介面層

`MdmProviderPort` 抽象介面 ＋ `MockMdmProvider`。所有 MDM 呼叫一律經介面，業務邏輯不碰實作細節。

取得 Android Enterprise 權限（Q-11）後，新增一個實作同介面的 provider 並替換 `MdmModule` 的注入即可，**其餘商業邏輯與稽核軌跡不需更動**。

### 5.7 SQLite 連線與唯讀通道（迭代 3）

- 連線時套用並回讀四項必開設定（`journal_mode=WAL`、`foreign_keys=ON`、`busy_timeout=5000`、`synchronous=FULL`），缺一項就拒絕啟動
- **寫入連線固定一條**：實測 Prisma 預設連線池有多條連線時，事後下的 PRAGMA 只會落在其中一條
- 統計、報表、稽核查詢、AI 呼叫紀錄、備份歷程清單走 `query_only` 的唯讀連線，不與臨床寫入競爭
- 資料庫檔案與 `BACKUP_DIR` 必須在**專案目錄外的本機磁碟**；相對路徑、專案目錄內、網路路徑、雲端同步資料夾，後端與 seed 一律拒絕啟動
- Prisma CLI 以 `CHECKPOINT_DISABLE=1` 關閉使用統計回報，否則 `prisma generate` 會連到院外

### 5.8 功能開關中心（FR-S08，迭代 3）

`modules/feature-flags/`，定義在 `shared/platform.ts`。

- 十個開關：高風險三項（`RISK_STRATIFICATION`、`INTRA_DIALYSIS_ALERT`、`DOSE_REFERENCE`）、AI 兩項（`AI_FEATURES`、`REAL_PATIENT_DATA_TO_AI`）、輪播三層、績效兩項（`PERF_INDIVIDUAL_L3`、`REWARD_SCORING`）。**全部預設關閉**
- 開啟條件由後端逐項判定，不靠人記得。例如 `REAL_PATIENT_DATA_TO_AI` 只在 `LLM_PROVIDER=onprem` 時可開；高風險三項要 FR-R08 書面確認＋規則版本附有書面依據，規則引擎尚未建立，所以目前開不了
- 開關關閉時，`feature-flag.guard.ts` 讓相關端點回 404，前端相關元素**完全不渲染**（不是 disabled）
- 切換須填核准依據並寫稽核，條件不符被拒的嘗試也寫（`FEATURE_FLAG_CHANGE_REJECTED`）。AI 兩項需 `system:configure`，其餘需 `feature-flag:manage`

### 5.9 模型供應者介面層與 AI 閘道（FR-S03／S04／S06，迭代 3）

- `LlmProviderPort` 三個實作，以 `LLM_PROVIDER=mock|lab|onprem` 切換，預設 `mock`。模擬實作在 `modules/llm/mock-llm.provider.ts`，實驗室 API 與院內地端推論走 `http-llm.provider.ts`。**端點、金鑰、模型 ID 全由環境變數提供，不寫在程式碼裡**
- 所有模型呼叫一律經 `modules/ai/ai-gateway.service.ts`：合成資料檢查（院外 provider 遇到非合成資料直接擋下，記 `AI_INVOCATION_BLOCKED`）、去識別化（`deidentify.ts`）、寫一列 `ai_invocations` 與 `AI_INVOKED` 稽核
- 閘道有兩個入口：`invoke()` 給 HTTP 端點，失敗拋例外；`attempt()`（迭代 4 新增）給背景工作，被擋或失敗時也回傳該次呼叫的紀錄 id，才能寫回工作結果
- 切換 provider 只改設定：`verify:iteration4` 以備份還原檔另起一個 `LLM_PROVIDER=lab` 的後端，接到腳本內的本機假端點，驗證同一份程式只改環境變數即可切換，且帶真實病人資料的請求一次都沒送出去

### 5.10 臨床資料來源介面層（FR-S05，迭代 3）

`modules/clinical-data/`：`ClinicalDataSourcePort` ＋ `ManualEntryAdapter` ＋ `FileImportAdapter`（迭代 6）。院方 API（待 Q-09）之後再加一個實作，三者共用 `clinical_value_imports`／`clinical_values`。

- 一批**全有或全無**：任何一筆驗證失敗就整批不寫入，記 `CLINICAL_VALUES_IMPORT_REJECTED`。臨床數值只對一半比完全沒有更危險
- 每筆帶資料時間；同一數值覆蓋時保留前一版
- 迭代 4 的適足性計算從這裡讀五項輸入

### 5.11 備份與還原（FR-S09，迭代 3）

`modules/ops/`。

- 用 SQLite 線上備份（`VACUUM INTO`），不用檔案複製：WAL 模式下 `-wal`／`-shm` 與主檔是一組，只複製主檔會拿到不一致的狀態
- 每日排程 ＋ 系統管理頁手動觸發，歷程寫 `backup_runs` 與稽核
- 還原用 `npm run db:restore`，還原前先停後端。演練步驟見測試手冊第 12 章

### 5.12 常駐總覽螢幕（FR-N12，迭代 3）

護理端 `/wall` 路由（`pages/WallDisplayPage.tsx`），不帶導覽列的獨立全螢幕版面。推播移除後，這是唯一保證通報被看見的地方。

- Wake Lock 防休眠，只在 HTTPS 或 localhost 下可用；不支援時要在作業系統關閉休眠
- 新通報發提示音，無人接收時每 60 秒再提醒
- 斷線閒置看門狗：最慢 45 秒判定斷線，全畫面紅框閃爍與橫幅，指數退避重連
- 連不上伺服器時**保留登入權杖**（迭代 3 修掉的既有問題），每 5 秒重試，恢復後自動回到原畫面
- JWT 預設 8 小時到期，到期後出現全螢幕的逾時提示；長時間顯示用的帳號做法待 Q-10

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

### 5.20 檔案匯入與可設定的欄位對應（FR-S05，迭代 6）

`FileImportAdapter` 收的是寬表：一列一位病人在某個資料時間的多項數值。

- **欄位名稱不寫死**：`import_field_mappings` 一列一個目標欄位，比對時忽略大小寫與全形半形空白。
  院方把「乾體重」改成「乾重(kg)」那天，改的是一列設定
- **Excel 用 `exceljs`，CSV 自己解析**（約二十行，支援引號與欄內逗號）。
  「欄位裡有逗號就靜默切錯」這種錯誤不會有任何錯誤訊息，值得用那二十行換掉
- **Excel 日期儲存格**在 exceljs 會以 UTC 解讀，但檔案上寫的是現場的時刻，
  因此把 UTC 的年月日時分當成當地時間重組一次，與班表匯入的處理一致
- **全有或全無**與重複匯入偵測沿用迭代 3 的 `ClinicalDataImportService`，一行都沒改：
  adapter 只負責「把來源轉成標準化數值並逐列指出格式問題」
- 檔案以 base64 夾在 JSON 裡送上來，不走 multipart。上限 2 MB，少一種請求形式就少一套解析與錯誤處理

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

### 規模

| 量測 | Iteration 2 時點 | 迭代 4 完成 | 迭代 5 完成 | 迭代 6 完成 |
|---|---|---|---|---|
| API 路由 | 43 | 78 | 90 | 107 |
| 資料表 | 10 | 29 | 36 | 39 |
| 稽核動作 | 32 | 52 | 66 | 68 |
| 權限碼 | 9 | 17 | 20 | 21 |
| 角色 | 3 | 6 | 6 | 6 |
| 功能開關 | — | 10 | 10 | 10 |
| 營運參數 | — | — | 6 | 12 |

（迭代 6 沒有新增功能開關：輪播三層的開關在迭代 3 就已建好並預設關閉，這次做的是把它們的
「開啟條件」從「功能尚未實作」換成實際判定。）

### 共用常數的角色

`packages/shared` 不只是型別。以下**業務規則**放在這裡，前後端共用同一份定義：

- `PRE_DIALYSIS_SYMPTOM_QUESTIONS` — 10 題題庫。放前端才能離線作答，後端用 `questionnaireVersion` 驗證版本一致
- `routeHelpRequest()` — 求助分派規則。前端顯示的分派結果與後端計算結果保證一致
- `AuditAction` / `Permission` / `NurseRole` — 動作識別字、權限碼與角色
- `SYMPTOM_TREND_DISCLAIMER` — 非診斷結果提示文字
- `platform.ts` — 功能開關定義與開啟條件、模型與臨床資料介面層的共用型別
- `education.ts` — 衛教主題 `EDU-TOPICS-v1`、題庫 `EDU-QUIZ-v1`、回饋題目與 `PSY-DEV-v1` 偏離規則
- `nursing.ts` — 事件範本 `EVENT-TEMPLATES-v1`、AI 初稿處置、SOP 查詢結果類別
- `operations.ts` — 迭代 5：`evaluateLabourRules()` 勞動條件判定、班別定義、成效基準指標定義，以及三處暫代值的**預設值**（注意：只是預設值，現行值一律讀資料表）。迭代 6 另加六項輪播行為參數的定義
- `carousel.ts` — 迭代 6：輪播的層、卡片種類、卡片與行為參數型別、第二層內容的長度上限。`CAROUSEL_CARD_KIND_LAYER` 讓後端由卡片種類推出層別，不採信平板送上來的值

**迭代 4 的暫定內容全部在這裡並標版本字串。** 臨床端回覆 Q-23～Q-26 後，改常數並升版即可，舊紀錄仍指向舊版本。

**改動 `packages/shared` 後必須重跑 `npm run build:shared`**（`npm run dev` 會自動先跑一次）。

---

## 7. 🔒 高風險三項：有條件納入，排在迭代 7

**FR-P03**（風險分層）、**FR-P05**（預警）、**FR-N06**（劑量建議）在 Iteration 2 時因高 SaMD 風險整條排除。0910 起改為**納入**，排在迭代 7，以自建規則引擎實作並受 FR-R01～R08 約束（實作規格書 1.4、3.6、4.5）。

目前狀態：

- 規則引擎與三項功能**一行都還沒寫**
- 三個功能開關已在迭代 3 建好，預設關閉；開啟條件由後端判定，規則引擎不存在，所以目前開不了
- 啟用需要兩個外部答覆：TFDA 分類書面確認（Q-02）與臨床端的規則門檻值（Q-03）。**兩者不到，迭代 7 仍可完成實作與合成資料驗收**，差別只在能不能對真實病人開
- FR-N07 的「預測」部分也併入迭代 7；迭代 4 只做計算與趨勢圖

在迭代 7 之前，現有功能照舊維持這條線：

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

以下都是實測確認過的，不是猜測。第 1～4 項自 Iteration 2 起未處理，2026-09-11 重新確認仍在。優先權不高但接手時值得知道：

| # | 問題 | 現況 | 建議 |
|---|---|---|---|
| 1 | **重複病歷號回 500** | `PatientsService.create` 沒攔 Prisma `P2002`，唯一鍵衝突直接冒成 500 | 攔截後改回 409 ＋ 中文訊息，與其他地方一致 |
| 2 | **DevicesPage 未依權限隱藏 UI** | 一般護理師看得到註冊表單與 MDM 按鈕，按下去才 403 | 加 `can(Permission.DEVICE_MANAGE)` 條件渲染（`PatientsPage` 已經這樣做了） |
| 3 | **取消排班無 UI** | `POST /treatment-sessions/:id/cancel` 端點存在，`api.ts` 也包好了，護理端沒有按鈕 | 在 `ConsolePage` 補一顆按鈕 |
| 4 | **總覽無日期選擇器** | `GET /overview?date=` 支援查其他日期，UI 只看當日 | 視需求補 |
| 5 | **總覽螢幕 8 小時後要重新登入** | `JWT_EXPIRES_IN` 預設 8 小時，全天開著的總覽螢幕到期後出現逾時提示 | 待 Q-10 確認螢幕位置與使用方式後，再決定是否給總覽螢幕專用的長效帳號或延長機制 |

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
npm run check:egress        # 零院外連線盤點（不需後端）
```

腳本都會建立少量標記過的合成資料並逐項斷言，涵蓋主線流程、錯誤路徑、權限隔離、冪等去重、稽核事件。**改動後請全部跑過。**

最近一次執行（2026-09-12，本機 SQLite，迭代 6 完成後）：**六支皆全數通過，零院外連線 0 筆**。

其中 `verify:iteration2` 改了一處，而且只有這一處：FR-N10 讓「只填自由文字即可結案」不再成立，那一段跟著改成新的結案方式。**迭代 2 原本要驗的行為一條都沒有放寬**——狀態轉換、留下處理者、總覽不再顯示待處理，斷言全部保留。這是目前唯一一次刻意改動既有驗收腳本，理由記在《實作規格書》1.1 節；其餘情況一律不得以「配合新功能」為由修改既有腳本。迭代 6 沒有再動過任何一支。

完整的手動測試步驟（17 章、286 個可勾選的測試項）另有[測試手冊](../testing/manual-test-guide.md)。其中四部分尚未執行：

- **第 13 章** 迭代 3 的兩項實機驗收（全新環境離線建置、總覽螢幕連續 4 小時與拔網路重連）— 驗收腳本代勞不了，需要實機與實際時間
- **第 14 章** 迭代 4 需要人眼確認的 27 項（非診斷標示、進度提示、病人端閱讀與作答體驗）
- **第 15 章** 迭代 5 的 50 項，其中需要人眼判斷的是：床邊按「我到床邊了」順不順手、班表被擋下時的提示讀不讀得懂、平板結案後「已處理」擺的位置對不對
- **第 16 章** 迭代 6 的 48 項，其中**四節是腳本驗不到、只能用手指確認的**：觸碰立即中止、求助按鈕位置與尺寸不變、細節頁自動退回、夜間模式調暗。輪播對病人開啟前應先走過這四節

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

迭代 6 已完成（2026-09-12）。成效基準的建檔介面自迭代 5 就緒，**現在等的仍是現場的數字**：

> ⏰ **成效基準的量測（Q-01）有時效性。** 這不是開發端能做的事。系統正式啟用前沒測到，之後所有「省下 X 分鐘」的說法都只能靠估算。

### 迭代 7～8

| 迭代 | 主題 | 可否立即開始 | 啟用前要等的外部答覆 |
|---|---|---|---|
| ~~6~~ | ~~閒置輪播~~ | **已完成** | 第二層等護理部給內容才開得起來（Q-28）；第三層的欄位對應已可設定（Q-09） |
| 7 | 規則引擎與三項高風險功能 | 實作可以 | 法務書面確認（Q-02）＋臨床端門檻值（Q-03） |
| 8 | 管理儀表板、獎勵、對外揭露 | 建置可以 | L3 啟用需護理部同意（Q-04）；指標定義（Q-20）與核准角色（Q-21） |

迭代 7 與 4～6 沒有相依，外部答覆若提早到齊可隨時往前插隊。
迭代 8 的成效指標會吃迭代 6 產生的 `carousel_view_events`，但那張表刻意不含個人層級資料，
因此它只回答得了「哪一類內容有人看」這種問題。

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

---

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|
| 0916 | 2026-09-16 | 改寫到迭代 6：封閉網路化、AI 輔助與護理記錄、求助處理與班表、閒置輪播與檔案匯入；資料庫改為 SQLite、推播改為院內 SSE 與常駐總覽螢幕，並換上重繪的架構圖 |
| 0909 | 2026-09-09 | 首次定版 |

[← 回進度首頁](../index.md)
