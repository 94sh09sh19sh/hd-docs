# 血液透析平板照護輔助系統 — 技術進度報告

**閱讀對象**：接手或協作的工程師
**報告日期**：2026-09-07
**版本**：Iteration 2 完成（commit `3fe9d5d`，master）
**Repo**：`94sh09sh19sh/hd-tablet-care`

---

## 1. 專案脈絡

需求來源在 [`docs/requirements/`](../index.md)（原 `demand_v1/`），共四份文件，**優先權不同，衝突時有明確的裁決順序**：

| 文件 | 角色 |
|---|---|
| [`srs.md`](../requirements/srs.md) | 功能需求來源（FR 編號皆引用自此） |
| [`implementation-spec.md`](../requirements/implementation-spec.md) | 範圍界定與技術棧決策，**衝突時以此為準** |
| [`database-policy.md`](../requirements/database-policy.md) | 資料治理強制規則，**優先權等同實作規格書** |
| [`fde-assessment.md`](../requirements/fde-assessment.md) | 背景脈絡與選型理由 |

動工前請至少讀完前三份。這個專案有不少「看起來繞路」的設計，幾乎都源自這些文件的硬性約束。

---

## 2. 架構

```
v0/
├── apps/
│   ├── api/            NestJS — API Gateway/BFF、裝置綁定服務、症狀回報、
│   │                            緊急通報、即時狀態快取層、稽核軌跡、MDM 介面層
│   ├── nurse-pwa/      React PWA — 護理站主控台（:5173）
│   └── patient-pwa/    React PWA — 病人端平板 Kiosk（:5174）
├── packages/
│   └── shared/         前後端共用型別與常數（@hd/shared）
└── docs/               進度報告
```

npm workspaces monorepo。約 10,000 行 TypeScript（不含 dist／node_modules）。

**技術棧**：NestJS 11 · Prisma 6 · PostgreSQL（測試階段用 Supabase）· React 19 · Vite 6 · TypeScript 5.7

### 資料流

```
病人端 PWA ─┐
            ├─→ 後端 API ─→ Repository 層 ─→ Prisma ─→ PostgreSQL
護理端 PWA ─┘
```

**前端一律不直接碰資料庫。** 兩個 PWA 都沒有 `@supabase/supabase-js` 依賴。

---

## 3. 五條不可違反的約束

這些是《資料庫使用規範》的硬性規則。動任何一處之前先確認不會踩到：

| # | 約束 | 為什麼 | 現況 |
|---|---|---|---|
| 1 | **前端不得直接連資料庫** | 未來換資料庫時前端不需改動 | 兩個 PWA 只呼叫後端 REST |
| 2 | **不得使用 Supabase Auth** | 病人不登入的身分模型與它完全不同 | 自建 JWT ＋ `nurse_sessions` 表（可主動撤銷）；病人端用裝置綁定核發的 Session Token |
| 3 | **存取控制不得寫在 RLS／Edge Functions** | 授權必須可追溯到「哪位護理師、何時、為哪位病人」，要在自己可掌控的程式碼裡 | 全部在 `PermissionsGuard` ＋ service 層。**零 RLS 政策** |
| 4 | **不得在業務邏輯中嵌入資料庫語法** | 換 ORM／資料庫時的隔離層 | `PrismaService` **只注入 Repository 層**，controller/service 一律不得取用 |
| 5 | **測試資料必須虛構** | Supabase 在院外 | seed 用 faker，病歷號固定 `HD-TEST-*` |

額外：**即時同步也沒有用 Supabase Realtime**（第 3 條的延伸）。即時狀態快取層是行程內實作。

### 未來遷移至 MSSQL 的相容性設計

醫院正式環境是 MSSQL。schema 設計時已避開會導致大改的東西：

- **不使用 Prisma `enum`** — SQL Server provider 不支援。狀態欄位以字串承載，合法值由 `@hd/shared` 常數 ＋ class-validator 在應用層把關
- **不使用 `jsonb`** — 結構化關聯資料一律正規化。例如問卷答案是獨立的 `symptom_answers` 表，不是塞在一個 JSON 欄位裡
- **不使用 PostgreSQL 專屬預設值** — UUID 由 Prisma client 產生，不用 `gen_random_uuid()`
- **控制級聯路徑** — SQL Server 不允許同一張表存在多條級聯刪除路徑。Iteration 2 新增的兩張表只讓 `device_bindings` 那一條帶 `Cascade`，其餘外鍵一律 `NoAction`

---

## 4. 資料模型

10 張表，2 個 migration。

| 表 | 用途 | 值得注意的地方 |
|---|---|---|
| `nurses` | 護理端使用者 | `role` / `status` 為字串；`canApproveNurses` 支援單獨分享審核權限 |
| `nurse_sessions` | 已核發的登入憑證 | 存 JWT 的 `jti`，讓 token **可被主動撤銷**（變更密碼、降權時） |
| `patients` | 病人（合成資料） | |
| `devices` | 15 台平板 | `apiKeyHash` 用 SHA-256（金鑰是 256-bit 隨機值，非使用者密碼）；MDM 狀態欄位 |
| `treatment_sessions` | 當日排班 | `@@unique([patientId, scheduledDate, shift])` |
| `device_bindings` | 綁定紀錄與限時憑證 | 綁定「病人＋平板＋療程時段」三者；`sessionTokenId` 存 jti，token 本身不寫入資料庫 |
| `symptom_reports` | 症狀問卷送出紀錄 | `clientReportId` **唯一鍵** → 離線補傳的冪等保證；`reportedAt`（病人填寫時間）與 `receivedAt`（伺服器收到）分開存 |
| `symptom_answers` | 單題作答 | 正規化，不用 jsonb。`present` 只是答案的原樣布林化，供計數用 |
| `help_requests` | 求助／緊急通報 | `clientRequestId` 唯一鍵防重複；`routedTo` 保存當下計算的分派結果供事後稽核 |
| `audit_logs` | 稽核軌跡 | 關聯欄位皆正規化為外鍵；另冗餘保存 `actorLabel`、`deviceSerialNo`，避免帳號日後異動導致軌跡失真 |

---

## 5. 幾個關鍵機制

### 5.1 護理端身份驗證（自建）

`.env` 的 `SUPER_ADMIN_WORK_ID` / `SUPER_ADMIN_INITIAL_PASSWORD` 只在**資料庫尚無任何使用者**時觸發 bootstrap，建立第一個 `SUPER_ADMIN` 並標記 `passwordChangeRequired`。

一般護理師以工作ID 申請 → `PENDING` → 管理者核准 → `ACTIVE` 才能登入。

登入態 = JWT ＋ `nurse_sessions` 表比對。這讓 token 可以被主動撤銷：**變更密碼**與**權限縮減**都會呼叫 `revokeAllForNurse()`，避免舊 token 沿用舊權限。

登入失敗時，帳號不存在與密碼錯誤回傳**完全相同**的訊息，且帳號不存在時仍會比對一次假雜湊，讓回應時間對齊 — 不從時間差洩漏帳號是否存在。

### 5.2 裝置綁定（SRS 4.3／4.4）

九步驟完整實作。三種失效條件：正常下機、手動解除、逾時（`BINDING_MAX_HOURS` 預設 6）。

**重複綁定阻擋**在 Repository 層以 **Serializable 交易** 完成：衝突檢查與寫入在同一個交易裡，避免兩個並行請求同時通過檢查。序列化失敗（`P2034`）會退避重試最多 4 次 — 交易是原子的，中止後沒有殘留寫入，所以重試安全。

被擋下的嘗試**本身也寫稽核**（`BINDING_REJECTED_DUPLICATE_PATIENT` / `BINDING_REJECTED_DEVICE_BUSY`）。

### 5.3 病人端授權

兩層：

1. **裝置身分** — `x-device-serial` ＋ `x-device-key`（MDM 佈建時寫入 Kiosk 網址）
2. **Session Token** — 綁定核發的限時 JWT，`x-session-token`

寫入端點用 `DeviceSessionGuard`，**一次查詢同時完成兩層驗證**：綁定紀錄本身已 include device，所以裝置金鑰比對不需要再查一次 `devices` 表。這是為了延遲刻意做的最佳化（見第 8 節）。

病人ID、療程時段、平板序號**一律由後端從綁定紀錄取得**，平板送上來的 body 不能指定要寫給哪一位病人。

### 5.4 即時狀態快取層

`modules/realtime/realtime-state.service.ts`。設計要點：

- **只服務當日**排班（透析中心的看板本來就只看當班），跨日自動重建；查其他日期直接回頭讀資料庫
- **write-through**：任何寫入方（症狀回報、求助、綁定異動、排班異動）寫完資料庫後呼叫 `refreshTreatmentSession()`，由本層重算該列並廣播
- 傳輸用 **SSE**。護理端以 `fetch` ＋ `ReadableStream` 消費而非 `EventSource`，因為 EventSource 無法設定 `Authorization` 標頭（用網址參數傳 token 會讓權杖出現在存取紀錄裡）
- 前端有 15 秒輪詢作為串流不可用時的保險，以及指數退避重連

**要橫向擴充時**：把 `Map` 換成 Redis hash、`Subject` 換成 Redis pub/sub，呼叫端介面不變。

### 5.5 離線韌性（病人端）

`offline-queue.ts` ＋ `symptom-sync.ts`。

**症狀回報：先入列、再送出。** 即使當下網路正常，也一律先寫進 IndexedDB 才發請求，成功才移除。這樣平板在請求途中斷電或被 Kiosk 重新載入，資料仍在。後端以 `clientReportId` 去重。

補傳時若綁定仍是同一筆，會改用**最新的** Session Token（避免暫存期間 token 已輪替）。

**求助不入列。** SRS 4.4 明文要求離線期間須明確提示無法通知護理站 — 讓病人誤以為已送達比誠實說明更危險。

綁定失效時：盡力補傳 → 清空佇列（平板是共用裝置，前一位病人的資料不得殘留）。

### 5.6 MDM 介面層

`MdmProviderPort` 抽象介面 ＋ `MockMdmProvider`。所有 MDM 呼叫一律經介面，業務邏輯不碰實作細節。

取得 Android Enterprise 權限後，新增一個實作同介面的 provider 並替換 `MdmModule` 的注入即可，**其餘商業邏輯與稽核軌跡不需更動**。

---

## 6. 已完成範圍

### Iteration 1

| 項目 | 位置 |
|---|---|
| Repository/DAO 抽象層 | `apps/api/src/repositories/` |
| 護理端身份驗證（bootstrap、註冊、審核、權限分享） | `modules/auth/`、`modules/nurses/` |
| FR-N01 排班與裝置指派 | `modules/schedule/`、`nurse-pwa/pages/ConsolePage.tsx` |
| 裝置綁定服務（SRS 4.3 九步驟＋4.4 例外） | `modules/binding/` |
| FR-P01 病人端中性等待畫面 | `patient-pwa/src/App.tsx` |
| FR-S02 稽核軌跡 | `modules/audit/`、`pages/AuditPage.tsx` |
| FR-S01 MDM 介面層 | `modules/mdm/` |

### Iteration 2

| 項目 | 位置 |
|---|---|
| FR-P02 症狀問卷 | `modules/symptoms/`、`patient-pwa/SymptomQuestionnaire.tsx` |
| FR-P06 求助按鈕 | `modules/help-requests/`、`patient-pwa/HelpRequestScreen.tsx` |
| FR-N02 即時總覽 | `nurse-pwa/pages/OverviewPage.tsx` |
| FR-N03 緊急通報與分級路由 | `nurse-pwa/pages/HelpRequestsPage.tsx`、`shared` 的 `routeHelpRequest()` |
| 即時狀態快取層 | `modules/realtime/realtime-state.service.ts` |
| 離線韌性 | `patient-pwa/offline-queue.ts`、`symptom-sync.ts` |

**規模**：43 條 API 路由、10 張表、32 種稽核動作、9 個權限碼。

### 共用常數的角色

`packages/shared` 不只是型別。以下**業務規則**放在這裡，前後端共用同一份定義：

- `PRE_DIALYSIS_SYMPTOM_QUESTIONS` — 10 題題庫。放前端才能離線作答，後端用 `questionnaireVersion` 驗證版本一致
- `routeHelpRequest()` — 求助分派規則。前端顯示的分派對象與後端計算結果保證一致
- `AuditAction` / `Permission` — 動作代碼與權限碼
- `SYMPTOM_TREND_DISCLAIMER` — 非診斷結果提示文字

**改動 `packages/shared` 後必須重跑 `npm run build:shared`**（`npm run dev` 會自動先跑一次）。

---

## 7. ⛔ 刻意排除的範圍

**FR-P03**（風險分層）、**FR-P05**（預警）、**FR-N06**（劑量建議）三項因高 SaMD 風險整條排除，**一行程式碼都沒寫**，等待與醫院法務／資訊室確認 TFDA 認證邊界。

這個約束**影響了現有功能的實作方式**，不只是「少做三個功能」：

- 求助分派 `routeHelpRequest()` 的輸入**只有**病人自選的類型與急迫度，不讀歷史資料
- 症狀趨勢摘要只做原樣列出與次數統計，不加權、不分級、不預測、不產生建議文字
- 總覽的「病人自述症狀」是把答案原樣呈現，不是系統評估
- 相關畫面固定顯示非診斷結果提示

**接手時請維持這條線。** 若某個需求疑似需要「依資料做出會影響臨床判斷的建議或分級」，即使規格書沒標註，也應先停下來確認。

---

## 8. 效能觀察

**症狀回報送出到護理端接收的端到端延遲，幾乎全部來自資料庫往返，不是即時同步機制。**

### 資料庫已搬遷（2026-09-07）

`ap-south-1`（孟買）→ **`ap-northeast-1`（東京）**。Supabase 不支援原地換區，做法是開新專案 ＋ `migrate deploy` ＋ `db:seed`，舊資料未搬移。

| 量測項目 | 孟買 | 東京 | 改善 |
|---|---|---|---|
| 純資料庫查詢往返（`patient.count()`，暖機後 5 次中位數） | — | **237 ms** | — |
| 驗收腳本量測值（一次已驗證的 API 請求，含 3 次查詢） | 1,741 – 2,249 ms | **702 ms** | ~2.8× |
| 端到端（平板送出 → 護理端收到） | 4,710 – 5,899 ms | **1,856 – 1,893 ms** | ~3× |
| **其中即時狀態同步本身** | 1 – 3 ms | **2 – 3 ms** | 不變 |

SRS 第 6 章要求 < 5 秒。搬遷前在門檻邊緣浮動、偶爾超標（驗收腳本會列為「環境相關觀察」）；**搬遷後該警告已消失**，兩支驗收腳本皆全數通過。

> 驗收腳本印出的「單次資料庫查詢往返」其實是一次**完整的已驗證 API 請求**，包含 `NurseAuthGuard` 的 2 次查詢加上端點本身的查詢 — 所以是純查詢往返的約 3 倍（237 × 3 ≈ 702）。判讀數字時要注意這一點。

### 寫入路徑的往返次數

端到端 1.9 秒 ≈ 3 趟資料庫往返 × ~237 ms ＋ 應用層處理。已做的優化：

- **合併裝置驗證查詢** — `DeviceSessionGuard` 一次查詢同時完成裝置身分與 Session Token 驗證（綁定紀錄已 include device），省一趟往返
- **稽核寫入與即時廣播平行進行**
- **`refreshTreatmentSession()` 的四筆查詢併為一批平行發出**
- **清單頁面一律批次查詢**，避免 15 台平板的看板產生 N+1

剩下的 3 趟是：授權查綁定 → 寫入 → 重算狀態。要再壓縮就得動快取或合併寫入，目前沒有必要。

> 搬遷步驟見測試手冊 §12。`.env` 已 gitignore，換區域不產生任何需要提交的程式碼變更。

### 下一步：測試資料庫改回本機 SQLite（預計下週）

東京把延遲壓進了 SRS 門檻，但 Supabase 主機在院外，測試資料只能維持全合成。下一步是把測試階段的
資料庫換成**開發者本機的 SQLite**，讓測試資料完全不離開本機。

- `schema.prisma` 的 `datasource.provider` 由 `postgresql` 改為 `sqlite`，`DATABASE_URL` 指向本機檔案，
  `DIRECT_URL` 與 pooler 參數不再需要
- 既有 migration 是 PostgreSQL 方言，換 provider 要重新產生一份，舊資料同樣不搬（本就是合成資料）
- schema 本身沒有用 Prisma enum，也沒有 PostgreSQL 專屬型別，這是當初為了相容 SQL Server 留的餘裕，
  換到 SQLite 一併受用
- 網路往返消失，端到端延遲預期會低於東京的 1.9 秒；換完後兩支驗收腳本都要重跑確認
- 《[資料庫使用規範](../requirements/database-policy.md)》第 2–4 條（不碰 Supabase Auth／RLS／Realtime、
  一律走後端 Repository）本來就沒讓任何邏輯耦合到平台，這次換 provider 不影響業務邏輯

正式環境仍以院內資料庫為準，孟買→東京與東京→本機 SQLite 都只是測試階段的過渡。

## 9. ⚠️ 已知粗糙處

以下都是實測確認過的，不是猜測。優先權不高但接手時值得知道：

| # | 問題 | 現況 | 建議 |
|---|---|---|---|
| 1 | **重複病歷號回 500** | `PatientsService.create` 沒攔 Prisma `P2002`，唯一鍵衝突直接冒成 500 | 攔截後改回 409 ＋ 中文訊息，與其他地方一致 |
| 2 | **DevicesPage 未依權限隱藏 UI** | 一般護理師看得到註冊表單與 MDM 按鈕，按下去才 403 | 加 `can(Permission.DEVICE_MANAGE)` 條件渲染（`PatientsPage` 已經這樣做了） |
| 3 | **取消排班無 UI** | `POST /treatment-sessions/:id/cancel` 端點存在，護理端沒有按鈕 | 在 `ConsolePage` 補一顆按鈕 |
| 4 | **總覽無日期選擇器** | `GET /overview?date=` 支援查其他日期，UI 只看當日 | 視需求補 |

**授權判斷本身沒有問題** — 全部在後端把關，前端只是沒藏好入口。

---

## 10. 開發環境

```bash
npm install
cp .env.example .env        # 填 DATABASE_URL / DIRECT_URL / JWT_SECRET / SUPER_ADMIN_*
npm run build:shared
npm run prisma:migrate
npm run db:seed
npm run dev                 # api:3000 · nurse:5173 · patient:5174
```

**必填環境變數**：`DATABASE_URL`（Transaction pooler, 6543, 加 `?pgbouncer=true&connection_limit=5`）、`DIRECT_URL`（Session pooler, 5432）、`JWT_SECRET`、`SUPER_ADMIN_WORK_ID`、`SUPER_ADMIN_INITIAL_PASSWORD`。

> `DIRECT_URL` **不要**用 Supabase 的 Direct connection（`db.<ref>.supabase.co`）— 只有 IPv6 記錄，IPv4 網路會 `P1001`。

`.env.example` 裡的 `SUPABASE_PROJECT_URL` / `SUPABASE_SERVICE_ROLE_KEY` **沒有任何程式碼引用**，只是依規格書保留的欄位。

### 驗收

```bash
npm run verify:acceptance   # Iteration 1 — 13 步驟
npm run verify:iteration2   # Iteration 2 — 11 步驟
```

兩支腳本都會建立少量標記過的合成資料並逐項斷言，涵蓋主線流程、錯誤路徑、權限隔離、冪等去重、稽核事件。**改動後請兩支都跑過。**

最近一次執行（2026-09-07，東京資料庫）：**兩支皆全數通過，無環境相關觀察**。

完整的手動測試步驟（13 章、149 個可勾選項目）另有測試手冊，涵蓋從 clone 到每個細節功能、離線情境、關閉與重新啟動、疑難排解。

---

## 11. 下一階段（Iteration 3）

接入 AI Proxy Service 與 Anthropic 模型，完成所有「生成／草擬輔助」性質但不涉及臨床判斷分級的功能。

**需要新增的核心元件**：

- `AiProxyService` — 封裝所有 LLM 呼叫。前端不持有任何金鑰（FR-S03）
- **PII/PHI 過濾層** — 呼叫外部 LLM 前必須去識別化（FR-S04）。這是硬性要求，不是選配
- 模型與思考程度的設定介面，設定存於後端
- AI 呼叫的稽核記錄（含使用的模型、是否觸發 PII 過濾）

**功能**：FR-P04（個人化衛教）、FR-P07（離院衛教與自適應測驗）、FR-P08（情緒回饋）、FR-N04（事件記錄草擬）、FR-N05（護理記錄預填）、FR-N07（Kt/V、URR 計算）、FR-N08（心理社會趨勢）、FR-N09（SOP 查詢，先用虛構文件）

**預設模型**：`claude-sonnet-4-6`（介面顯示為 Sonnet 5），使用者可切換模型與思考程度。

**介面要求**：AI 輸出須標示「僅供決策輔助，非診斷結果」。AI 草擬的護理記錄由護理師審閱簽核，**AI 不取代簽核責任**。

---

## 12. 每次動工前的自我檢查

沿用《資料庫使用規範》第 9 條：

- [ ] 新增的資料表／欄位是否已對照 SRS 與稽核軌跡欄位需求
- [ ] 有沒有前端程式碼企圖直接呼叫 Supabase SDK
- [ ] 有沒有邏輯企圖依賴 Supabase Auth
- [ ] 有沒有存取控制寫在 RLS／Edge Functions
- [ ] 本次功能是否誤觸 FR-P03／FR-P05／FR-N06
- [ ] 測試資料是否為虛構合成資料
- [ ] MDM 呼叫是否皆透過 `MdmProviderPort`
- [ ] schema 是否維持 MSSQL 相容（無 enum、無 jsonb、單一級聯路徑）

---

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|
| 0909 | 2026-09-09 | 首次定版 |

[← 回進度首頁](../index.md)
