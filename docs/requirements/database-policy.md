# 血液透析平板照護輔助系統 — 資料庫使用規範（測試階段：Supabase）

版本：v1.0　適用範圍：本專案所有開發者與AI coding agents
目的：測試階段暫用Supabase，但確保未來能以最低成本轉移至醫院正式資料庫

---

## 0. 背景與核心原則

正式上線時，所有資料將存放於醫院系統資料庫。目前尚未取得醫院資料庫存取權，暫時使用 **Supabase（PostgreSQL）** 作為測試階段的資料儲存。

**核心原則：Supabase在本專案中只能被當作「一個暫時的PostgreSQL主機」使用，不得成為系統邏輯的一部分。** 所有驗證、存取控制、業務邏輯必須留在自建後端程式碼中，不可依賴或耦合Supabase平台的專屬功能。任何AI agent在協助開發時，都必須遵守以下規則，即使Supabase官方文件或範例建議了更方便的做法。

---

## 1. 為什麼選Supabase而非Firebase

- Supabase底層是標準PostgreSQL，屬於關聯式資料庫，與醫院內部資料庫（Oracle/MSSQL/PostgreSQL/MySQL等）的資料模型一致，轉移時本質是「換一個PostgreSQL主機」或做SQL方言轉換。
- 本系統核心資料（病人-平板-療程時段綁定、稽核軌跡）具有強關聯性，天生適合關聯式資料庫，不適合NoSQL文件資料庫（如Firestore）。
- **Agent行為規則**：不得為了方便額外導入Firebase/Firestore或其他NoSQL服務作為主要資料儲存。

---

## 2. 資料庫存取必須收斂在後端一層

- **禁止**前端（病人端PWA、護理端PWA）使用Supabase client SDK直接連線資料庫。
- 所有資料流向必須是：**前端 → 自建後端API（API Gateway/BFF）→ Supabase**。
- 原因：這樣未來替換底層資料庫時，只需修改後端連線邏輯，前端程式碼完全不需變動。

**Agent行為規則**：

- 生成前端程式碼時，不得引入 `@supabase/supabase-js` 或任何Supabase前端SDK。
- 所有資料庫查詢/寫入邏輯只能出現在後端服務程式碼中。

---

## 3. 不使用Supabase Auth，繼續採用自建裝置綁定機制

- 本系統的身分機制是「病人不登入，由護理師在護理站主控台觸發裝置綁定，核發限時Session Token」，此邏輯與Supabase內建的使用者登入系統（Supabase Auth／JWT使用者表）完全不同，**不可**將病人身分掛載在Supabase Auth的user表上。
- Supabase只能拿來存放資料，不能拿來做使用者驗證或Session管理。

**Agent行為規則**：

- 不得建議或實作 `supabase.auth.signIn()`、`supabase.auth.signUp()` 等Supabase Auth相關功能作為病人或護理師的身分驗證機制。
- Session Token的產生、驗證、失效邏輯必須由後端裝置綁定服務（Device Binding Service）自行實作與管理。

---

## 4. 存取控制邏輯必須寫在後端應用層，不寫在資料庫平台專屬功能中

**禁止使用或依賴以下Supabase/Firebase平台專屬功能作為核心邏輯**：

| 功能 | 說明 | 規則 |
|---|---|---|
| Row Level Security（RLS） | Supabase資料庫層級的存取規則 | 不可用來實作「哪一位護理師能看哪一位病人資料」的核心邏輯 |
| Realtime訂閱 | Supabase即時資料推送 | 若使用，僅能作為輔助通知，核心狀態同步邏輯仍須經後端 |
| Edge Functions | Supabase的serverless函式 | 不可將AI Proxy、裝置綁定等核心服務邏輯寫在此處 |
| Firebase Security Rules / Cloud Functions | 同上（若日後考慮Firebase） | 同上，禁止用作核心邏輯載體 |

- 原因：本系統要求「存取授權可追溯到哪一位護理師、何時、為哪一位病人核准」（SRS 4.1），此邏輯必須在自己可完全掌控、可稽核、可日後搬遷的後端程式碼中，不能外包給資料庫平台的規則引擎。

**Agent行為規則**：

- 實作存取控制（誰能讀寫哪些資料）時，一律寫在後端應用邏輯（API層的authorization middleware / service層），不得建議用RLS政策取代。
- 若使用RLS，僅能作為「防禦性最後一道防線」（defense in depth），不能是唯一或主要的存取控制機制。

---

## 5. 統一資料存取層（Repository層 / ORM）

- 使用ORM（如Prisma、SQLAlchemy、TypeORM、Drizzle等）或自建Repository層包裝所有資料庫操作。
- 業務邏輯程式碼中不得直接寫入Supabase專屬語法（如 `.from('table').select()` 這類PostgREST風格呼叫）散落在各處。

**Agent行為規則**：

- 新增資料庫操作時，一律透過既有Repository/DAO層的介面，不得在controller、service、路由處理函式中直接嵌入資料庫查詢語法。
- 若專案尚未建立Repository層，第一次遇到資料庫操作需求時應先建立此抽象層，再實作功能。

---

## 6. Schema設計原則

- 現在設計的資料表結構，應直接對應SRS中定義的正式需求，特別是：
  - 病人-平板-療程時段綁定紀錄
  - Session Token（含病人ID、平板序號、時段、狀態、建立/失效時間）
  - 稽核軌跡（操作護理師帳號、時間戳、病人ID、平板序號、動作類型）
- 不因為是測試階段而簡化或省略稽核相關欄位，避免正式轉移時發現schema需要重新設計。

**Agent行為規則**：

- 設計或修改資料表時，需同時確認是否已涵蓋稽核軌跡所需欄位（誰、何時、對誰、做了什麼動作）。
- 使用標準SQL資料型別與命名慣例（snake_case、明確的外鍵關聯），避免使用PostgreSQL方言中在其他資料庫不支援的特殊型別（如非必要不使用 `jsonb` 承載結構化關聯資料，改用正規化資料表）。

---

## 7. 測試資料規範（重要）

- **絕對禁止**在Supabase測試環境中使用任何接近真實病人的可識別資訊（真實姓名、真實病歷號、真實生命徵象數值組合）。
- 測試資料一律使用**完全虛構的合成資料**：假名、隨機生成的病歷號格式、隨機生成的生命徵象數值。
- 原因：Supabase伺服器位置不在醫院內部網路範圍內，不符合SRS中「病人可識別資訊不得傳送至外部服務」之原則，測試階段更應嚴格遵守，避免養成用真實資料測試的習慣。

**Agent行為規則**：

- 產生測試資料/seed data腳本時，一律使用假資料產生器（如faker.js/Faker）產生合成資料，不得使用或建議使用任何真實或看似真實的病人資訊。
- 若使用者提供看起來像真實病人資料的內容作為測試輸入，應提醒使用者改用合成資料。

---

## 8. 未來遷移路徑準備

- Supabase底層為PostgreSQL，可用 `pg_dump` 匯出標準SQL，理論上可直接還原至醫院PostgreSQL，或作為schema對照手動遷移至Oracle/MSSQL。
- 建議定期（如每個開發里程碑）確認以下三件事，確保遷移路徑暢通：
  1. 是否有任何前端程式碼直接呼叫Supabase SDK（違反第2條）
  2. 是否有任何核心邏輯寫在RLS/Edge Functions中（違反第4條）
  3. Schema是否仍與SRS需求一致（第6條）

**Agent行為規則**：

- 在重大功能完成後，若被要求做程式碼review，應主動檢查上述三項是否有違規之處，並提出警示。

---

## 9. 快速檢查清單（給Agent的執行前自我檢查）

在協助撰寫任何與資料庫相關的程式碼前，Agent應自我確認：

- [ ] 這段程式碼是否讓前端直接連Supabase？→ 若是，改為透過後端API
- [ ] 這段程式碼是否使用Supabase Auth做身分驗證？→ 若是，改用自建Session Token機制
- [ ] 存取控制邏輯是否寫在RLS/Edge Functions？→ 若是，改寫在後端應用層
- [ ] 是否直接在業務邏輯中寫死Supabase專屬查詢語法？→ 若是，改走Repository/ORM層
- [ ] 測試資料是否為虛構合成資料？→ 若不是，一律替換為假資料
- [ ] Schema是否包含稽核軌跡所需欄位？→ 若無，補齊後再實作功能

---

## 10. 總結

Supabase在本專案中的角色僅止於「測試階段的PostgreSQL資料儲存」。所有驗證、授權、業務邏輯、Session管理都必須留在自建後端，確保未來轉移至醫院正式資料庫時，理想狀況下只需要：**更換資料庫連線設定＋執行一次schema migration**，而不需要重寫應用邏輯。

---

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|
| 0909 | 2026-09-09 | 首次定版 |

[← 回進度首頁](../index.md)
