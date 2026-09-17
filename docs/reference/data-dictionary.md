# 血液透析平板照護輔助系統 — 資料字典

**範圍**：目前資料庫實際蒐集的全部資料 — 10 張表、123 個欄位、2 個 migration
**來源**：`apps/api/prisma/schema.prisma`、`apps/api/prisma/migrations/`、`packages/shared/src/constants.ts`
**環境**：Supabase PostgreSQL（`ap-northeast-1` 東京）— 測試階段暫用，見《[資料庫使用規範](../requirements/database-policy.md)》

---

## 0. 怎麼讀這份文件

每張表的欄位清單都有**兩欄說明**，寫給兩種不同的讀者：

| 欄位 | 寫給誰 | 回答什麼問題 |
|---|---|---|
| **給人看的說明** | 臨床端、專案管理、接手的人 | 這個欄位在真實世界裡是什麼？**為什麼要蒐集它？** |
| **給 Agent 的說明** | AI coding agent、寫程式的人 | 合法值有哪些？誰負責填？不變條件是什麼？**動這個欄位會踩到什麼？** |

> **給 Agent 的總則**：本文件描述的是**現況**，不是規格。若與 `schema.prisma` 不一致，以 `schema.prisma` 為準並回報本文件已過時。修改任何欄位前，先讀《[資料庫使用規範](../requirements/database-policy.md)》第 6 條與第 9 條的檢查清單。

### 全表共通的設計約束

這些約束來自《資料庫使用規範》第 6 條，目的是讓未來遷移到醫院資料庫（PostgreSQL／Oracle／MSSQL）時，理想狀況只需換連線設定加跑一次 migration：

1. **不使用 Prisma enum** — SQL Server provider 不支援。所有列舉值都是 `TEXT`，合法值由 `@hd/shared` 常數與 class-validator 在**應用層**把關。
2. **不使用 jsonb** 承載結構化關聯資料 — 一律正規化成資料表與外鍵。
3. **不使用 PostgreSQL 專屬預設值**（如 `gen_random_uuid()`）— UUID 由 Prisma client 在應用層產生。
4. **命名**：欄位 `snake_case`，表名複數 `snake_case`。
5. **稽核欄位不因測試階段省略** — 誰、何時、對誰、做了什麼，設計時就納入。
6. **級聯路徑只留一條** — SQL Server 不允許同一張表有多條級聯刪除路徑，因此除了指定的那一條外鍵，其餘一律 `NO ACTION`。

### 型別對照

| 本文件寫法 | PostgreSQL 實際型別 | Prisma 型別 | 說明 |
|---|---|---|---|
| `TEXT` | `TEXT NOT NULL` | `String` | 必填字串 |
| `TEXT?` | `TEXT`（可為 NULL） | `String?` | 選填字串 |
| `BOOL` | `BOOLEAN NOT NULL` | `Boolean` | 必填布林，皆有 DEFAULT |
| `TS` | `TIMESTAMP(3) NOT NULL` | `DateTime` | 必填時間戳，毫秒精度 |
| `TS?` | `TIMESTAMP(3)`（可為 NULL） | `DateTime?` | 選填時間戳 |

### 五類資料一覽

| 類別 | 表 | 蒐集的本質 |
|---|---|---|
| 一、帳號與登入憑證 | `nurses`、`nurse_sessions` | 誰有權操作系統，以及他現在持有哪張有效的通行證 |
| 二、主檔 | `patients`、`devices` | 系統管理的實體：人與平板 |
| 三、排班與綁定 | `treatment_sessions`、`device_bindings` | 系統核心：哪台平板在哪個時段屬於哪位病人 |
| 四、病人自述內容 | `symptom_reports`、`symptom_answers`、`help_requests` | 病人自己填的、自己按的 — **全部是自述，不含任何系統推論** |
| 五、稽核軌跡 | `audit_logs` | 上述四類發生的每一次操作留下的不可否認紀錄 |

### 每張表都有的三個欄位

以下三個欄位在多數表重複出現，個別表的欄位清單中不再逐一解釋：

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 這筆資料的唯一識別碼，系統內部使用，不對使用者顯示 | UUID v4 字串，主鍵。**由 Prisma client 在應用層產生**（`@default(uuid())`），不是資料庫函式 — 這是為了遷移相容性，不要改成 `gen_random_uuid()` |
| `created_at` | `TS` | 這筆資料被建立的時間 | `DEFAULT CURRENT_TIMESTAMP`，寫入時不要手動指定 |
| `updated_at` | `TS` | 這筆資料最後一次被修改的時間 | Prisma `@updatedAt` 自動維護。**只有會被更新的表才有這欄** — `symptom_reports`、`symptom_answers`、`audit_logs` 是唯讀事實紀錄，刻意沒有這欄 |

---

## 一、帳號與登入憑證

### `nurses` — 護理端使用者（13 欄）

**蒐集的意義**：本系統的所有寫入操作都必須追溯到一個具名的護理人員（SRS 4.1）。這張表就是「具名」的來源 — 沒有這張表，稽核軌跡上的每一筆都會變成匿名操作，整個資料治理設計就失效了。

病人**不在這張表裡**，病人不登入（SRS 4.3）。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 帳號的內部識別碼 | 主鍵，見上方共通欄位 |
| `work_id` | `TEXT` UNIQUE | 護理人員的**工作識別碼**，也就是登入時輸入的帳號。蒐集它是因為稽核軌跡必須對得上醫院的人事編制，而不是一個系統自己發明的流水號 | 唯一鍵。登入查詢的入口。**不要**用 `id` 當登入帳號 |
| `display_name` | `TEXT` | 顯示名稱，護理站主控台上看到的名字 | 僅供顯示。測試環境為 faker 合成資料 |
| `password_hash` | `TEXT` | 密碼的雜湊值。**系統不儲存密碼明文** | bcrypt 雜湊。⛔ **禁止**改用 Supabase Auth 取代（《資料庫使用規範》第 3 條）。⛔ 禁止出現在任何 API 回應或 log 中 |
| `role` | `TEXT` | 角色，決定這個人能做什麼。分三級：最高權限、護理長、一般護理師 | 合法值 `SUPER_ADMIN` / `NURSE_MANAGER` / `NURSE`，定義於 `@hd/shared` 的 `NurseRole`。⛔ 權限判斷寫在後端 service 層，**禁止**用 Supabase RLS 實作（第 4 條）。有索引 |
| `status` | `TEXT` | 帳號狀態。新註冊的人是「待審核」，要由有權限的人核准才能用；也可以被駁回或停權 | 合法值 `PENDING` / `ACTIVE` / `REJECTED` / `SUSPENDED`，見 `NurseStatus`。**只有 `ACTIVE` 能通過 `NurseAuthGuard`**。有索引 |
| `can_approve_nurses` | `BOOL` | 是否被單獨授予「審核他人註冊」的權限。這是為了讓最高權限帳號能把審核工作分出去，而不必把整個管理權限一起給出去 | `DEFAULT false`。與 `role` **正交** — 一個 `NURSE` 也可以有這個權限。對應《實作規格書》3.1 節第 4 點。授予／收回都要寫 `NURSE_PERMISSION_GRANTED` / `_REVOKED` 稽核 |
| `password_change_required` | `BOOL` | 是否強制下次登入要改密碼。用於初始帳號與管理員重設密碼後 | `DEFAULT false`。為 `true` 時應擋住一般 API，只放行改密碼端點 |
| `approved_by_id` | `TEXT?` | **是誰核准這個帳號的**。蒐集它是因為「授權可追溯到哪一位護理師核准」是 SRS 4.1 的明文要求 | 自關聯外鍵 → `nurses.id`，`ON DELETE NO ACTION`。`PENDING` 狀態時為 NULL |
| `approved_at` | `TS?` | 核准的時間 | 與 `approved_by_id` 同時寫入，不要只填其中一個 |
| `last_login_at` | `TS?` | 最後一次成功登入的時間。用於辨識長期未使用而該停權的帳號 | 只在登入**成功**時更新。失敗不動這欄（失敗記在 `audit_logs`） |
| `created_at` | `TS` | 註冊申請送出的時間 | 見共通欄位 |
| `updated_at` | `TS` | 帳號資料最後修改時間 | 見共通欄位 |

**索引**：`work_id`（唯一）、`status`、`role`
**被參照**：`nurse_sessions`、`treatment_sessions.created_by_id`、`device_bindings.bound_by_id`／`released_by_id`、`help_requests.acknowledged_by_id`／`resolved_by_id`、`audit_logs.actor_nurse_id`

---

### `nurse_sessions` — 已核發的登入憑證（9 欄）

**蒐集的意義**：JWT 本身是無狀態的，簽出去就收不回來。但本系統需要在「改密碼」「降權」「停權」時**立刻讓已核發的 token 失效**。這張表存的就是每一張已核發 token 的留底，讓後端能主動撤銷。同時它也記錄登入來源的 IP 與裝置，作為異常存取的追查依據。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 這筆憑證紀錄的內部識別碼 | 主鍵 |
| `nurse_id` | `TEXT` | 這張憑證是發給哪一位護理人員的 | 外鍵 → `nurses.id`，**`ON DELETE CASCADE`**（本表唯一的級聯來源）。有索引 |
| `token_id` | `TEXT` UNIQUE | 憑證的序號。系統靠比對這個序號來判斷一張 token 是否仍然有效 | JWT 的 `jti` claim。`NurseAuthGuard` 每次驗證都查這張表。⛔ **不存 token 本身**，只存 jti |
| `issued_at` | `TS` | 核發時間 | `DEFAULT CURRENT_TIMESTAMP` |
| `expires_at` | `TS` | 到期時間。過了就要重新登入 | 有索引，供批次清理過期紀錄。判定失效時 `expires_at` 與 `revoked_at` **兩者都要檢查** |
| `revoked_at` | `TS?` | 被提前撤銷的時間。NULL 代表未被撤銷 | 撤銷是寫入這欄，**不是刪除該列** — 刪除會讓撤銷這件事本身失去紀錄 |
| `revoked_reason` | `TEXT?` | 撤銷的原因（登出、改密碼、被停權等） | 自由文字。與 `revoked_at` 同時寫入 |
| `ip_address` | `TEXT?` | 登入來源的 IP。用於事後追查非預期的存取 | 選填，取自請求標頭。院內網路環境下可能為內網位址 |
| `user_agent` | `TEXT?` | 登入所用的瀏覽器／裝置資訊。同樣用於追查 | 選填，原樣保存不解析 |

**索引**：`token_id`（唯一）、`nurse_id`、`expires_at`
**注意**：本表沒有 `updated_at` — 憑證紀錄只會被「撤銷」一次，狀態變化由 `revoked_at` 表達。

---

## 二、主檔

### `patients` — 病人（9 欄）

**蒐集的意義**：綁定、排班、症狀回報、求助全部要指向一個明確的病人。這張表刻意**只存識別與基本人口學資料，不存任何臨床數值**（生命徵象、檢驗值、透析處方都不在此，也不在本系統任何一張表裡）。

> ⚠️ **測試階段鐵則**：Supabase 主機不在醫院內網，《資料庫使用規範》第 7 條**絕對禁止**在此放入任何接近真實病人的可識別資訊。現行測試資料由 `prisma/seed.ts` 以 `fakerZH_TW` 產生 8 筆全合成資料。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 病人的內部識別碼 | 主鍵。**跨表一律用這個**，不要用病歷號串接 |
| `medical_record_no` | `TEXT` UNIQUE | 病歷號。護理師在主控台上是用這個找病人的，蒐集它是為了讓系統對得上醫院既有的病人識別方式 | 唯一鍵。測試環境格式固定為 `HD-TEST-0001`。⛔ 產生測試資料時**只能**用這個合成格式 |
| `display_name` | `TEXT` | 病人姓名，護理站畫面與平板歡迎畫面上顯示 | ⛔ 測試環境必為 faker 假名 |
| `birth_date` | `TS?` | 出生日期。臨床上用於基本身分核對 | 選填。只有日期有意義，時間部分忽略 |
| `gender` | `TEXT?` | 性別 | 選填。seed 產生 `'M'` / `'F'`，**應用層目前未強制列舉**，屬已知粗糙處 |
| `note` | `TEXT?` | 備註欄，護理端自由填寫 | 自由文字。⛔ 不要用它承載結構化資料（違反第 6 條）— 需要結構就開欄位或開表。測試資料一律標註「合成測試資料，非真實病人」 |
| `active` | `BOOL` | 這位病人是否仍在本中心接受治療。轉院或結案的病人設為否，但資料保留 | `DEFAULT true`。有索引。**停用是設 false，不是刪除** — 刪除會連帶影響歷史綁定與稽核 |
| `created_at` | `TS` | 建檔時間 | 見共通欄位 |
| `updated_at` | `TS` | 最後修改時間 | 見共通欄位 |

**索引**：`medical_record_no`（唯一）、`active`
**被參照**：`treatment_sessions`、`device_bindings`、`symptom_reports`、`help_requests`、`audit_logs`

---

### `devices` — 病人端平板（12 欄）

**蒐集的意義**：透析中心共 15 台平板（SRS 第 9 章）。平板**沒有病人登入機制**，它憑什麼證明自己是「3 號床那台」？靠的就是這張表裡的序號與 API 金鑰雜湊。這張表同時保存 MDM（行動裝置管理）狀態，因為平板是共用裝置，必須能遠端鎖定與限制為單一 App。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 平板的內部識別碼 | 主鍵 |
| `serial_no` | `TEXT` UNIQUE | 平板序號。護理師在主控台上是靠這個認出「哪一台」，稽核紀錄也是靠這個追溯 | 唯一鍵。平板每次請求都用 `x-device-serial` 標頭帶上（`DEVICE_SERIAL_HEADER`）。SRS 4.3 步驟 9 明列為必要稽核欄位 |
| `label` | `TEXT` | 給人看的標籤，例如床號或位置。序號不好記，這欄是實際貼在機器上的名字 | 僅供顯示，不參與任何邏輯判斷 |
| `status` | `TEXT` | 平板目前的狀態：可用、使用中、已報廢 | 合法值 `AVAILABLE` / `BOUND` / `RETIRED`（`DeviceStatus`）。有索引。⚠️ `schema.prisma` 註解另列了 `LOCKED`，**那是過時的註解**，以 `@hd/shared` 常數為準 |
| `api_key_hash` | `TEXT` | 平板身分金鑰的雜湊。平板要向後端取得綁定狀態時，必須出示金鑰證明自己是登記在案的裝置 | SHA-256（金鑰是 256-bit 隨機值而非使用者密碼，故不需 bcrypt）。平板以 `x-device-key` 標頭送出。⛔ 明文金鑰只在註冊當下產生一次，不存入資料庫 |
| `mdm_enrolled` | `BOOL` | 是否已納入行動裝置管理 | `DEFAULT false`。本階段 MDM 只做**介面層**（《實作規格書》3.3），此欄反映的是介面層的狀態 |
| `mdm_enrollment_id` | `TEXT?` | MDM 系統給這台平板的註冊編號 | 選填。Android Enterprise 的識別碼，本階段為介面層預留 |
| `mdm_locked` | `BOOL` | 是否已遠端鎖定 | `DEFAULT false`。**與 `status` 正交** — 一台鎖定中的平板仍可能同時是 `BOUND`。不要把兩者合併成單一狀態機 |
| `mdm_kiosk_url` | `TEXT?` | Kiosk（單一 App）模式要鎖定顯示的網址 | 選填。設定時寫 `DEVICE_MDM_KIOSK_CONFIGURED` 稽核 |
| `last_seen_at` | `TS?` | 這台平板最後一次與後端通訊的時間。用來發現離線或故障的機器 | 平板請求時更新。⚠️ 更新頻繁，避免放進頻繁查詢的交易中 |
| `created_at` | `TS` | 建檔時間 | 見共通欄位 |
| `updated_at` | `TS` | 最後修改時間 | 見共通欄位 |

**索引**：`serial_no`（唯一）、`status`
**被參照**：`device_bindings`、`symptom_reports`、`help_requests`、`audit_logs`

---

## 三、排班與綁定（系統核心）

### `treatment_sessions` — 當日排班（10 欄）

**蒐集的意義**：綁定不能憑空發生 — SRS 4.3 要求「護理師在主控台選定當日該時段的病人」才能綁定平板。這張表就是那份當日名單（FR-N01），它同時是綁定的**前置條件**與**授權範圍的邊界**：一次綁定只在它所屬的療程時段內有效。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 這筆排班的內部識別碼 | 主鍵 |
| `patient_id` | `TEXT` | 這個時段排的是哪位病人 | 外鍵 → `patients.id`，`ON DELETE CASCADE` |
| `scheduled_date` | `TS` | 排班日期 | **只取日期部分**，實務上存當日 `00:00 UTC`。⚠️ 比較日期時務必正規化到同一時區，否則跨日邊界會錯（見 `common/date.util.ts`） |
| `shift` | `TEXT` | 班別：早班、午班、晚班。透析是固定時段輪班制，同一台機器一天服務多位病人 | 合法值 `MORNING` / `AFTERNOON` / `EVENING`（`TreatmentShift`）。中文標籤在 `TREATMENT_SHIFT_LABELS` |
| `status` | `TEXT` | 這次療程的進度：已排定、進行中、已完成、已取消 | 合法值 `SCHEDULED` / `IN_PROGRESS` / `COMPLETED` / `CANCELLED`（`TreatmentSessionStatus`）。與 `scheduled_date` 組成複合索引 |
| `started_at` | `TS?` | 實際上機時間。排定時間與實際時間常有落差，兩者分開記錄 | 轉入 `IN_PROGRESS` 時寫入 |
| `ended_at` | `TS?` | 實際下機時間 | 轉入 `COMPLETED` 時寫入 |
| `created_by_id` | `TEXT` | **是誰排的這個班**。稽核要求每筆資料都能追溯到具名操作者 | 外鍵 → `nurses.id`，`ON DELETE NO ACTION` |
| `created_at` | `TS` | 排班建立時間 | 見共通欄位 |
| `updated_at` | `TS` | 最後修改時間 | 見共通欄位 |

**唯一約束**：`(patient_id, scheduled_date, shift)` — 同一位病人在同一天的同一班別**只能有一筆排班**，從資料庫層擋掉重複排班。
**索引**：`(scheduled_date, status)` — 供「今天還有哪些班沒開始」這類查詢使用。

---

### `device_bindings` — 裝置綁定與限時憑證（16 欄）

**蒐集的意義**：**這是整個系統的核心表。** SRS 4.3 要求綁定「病人 ID ＋ 平板序號 ＋ 當次療程時段」三者，並核發限時 Session Token。它同時回答四個問題：這台平板現在屬於誰、這個授權什麼時候失效、是誰授權的、平板端的暫存資料清乾淨了沒有。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 這筆綁定的內部識別碼 | 主鍵。`symptom_reports` 與 `help_requests` 都掛在它底下 |
| `patient_id` | `TEXT` | 綁定的病人（三方之一） | 外鍵 → `patients.id`，`ON DELETE CASCADE`。與 `status` 組成複合索引 |
| `device_id` | `TEXT` | 綁定的平板（三方之二） | 外鍵 → `devices.id`，`ON DELETE CASCADE`。與 `status` 組成複合索引 |
| `treatment_session_id` | `TEXT` | 綁定的療程時段（三方之三）。少了這一項，授權就沒有時間邊界 | 外鍵 → `treatment_sessions.id`，`ON DELETE CASCADE` |
| `status` | `TEXT` | 綁定狀態：使用中、已解除、已逾時失效 | 合法值 `ACTIVE` / `RELEASED` / `EXPIRED`（`BindingStatus`）。與 `expires_at` 組成複合索引，供批次逾時掃描 |
| `session_token_id` | `TEXT` UNIQUE | 核發給平板那張憑證的序號。**憑證本身不存在資料庫裡** — 明文只在核發當下送給平板一次 | JWT 的 `jti`。⛔ **絕對不要**把 token 明文寫進本表或 log。失效判定一律回頭比對本列的 `status` 與 `expires_at`，不是解 token 就算數 |
| `bound_by_id` | `TEXT` | **是哪一位護理師按下綁定的**。SRS 4.1 要求授權可追溯到具名的人，這欄就是那項要求的具體體現 | 外鍵 → `nurses.id`，`ON DELETE NO ACTION` |
| `bound_at` | `TS` | 綁定成立的時間 | `DEFAULT CURRENT_TIMESTAMP` |
| `expires_at` | `TS` | 授權到期時間。到點自動失效，不需人工介入 | 綁定時依療程時段上限計算。**每次驗證都要檢查**，不能只靠 JWT 自己的 `exp` |
| `released_by_id` | `TEXT?` | 是誰解除的。NULL 代表尚未解除，或是系統自動逾時（此時 `release_reason` 為 `TIMEOUT`） | 外鍵 → `nurses.id`，`ON DELETE NO ACTION` |
| `released_at` | `TS?` | 解除時間 | 與 `status` 轉為 `RELEASED`／`EXPIRED` 同時寫入 |
| `release_reason` | `TEXT?` | 為什麼解除：正常下機、護理師手動提前解除、超過時間上限自動失效。三種情境的臨床意義完全不同，必須分開記錄 | 合法值 `NORMAL_DISCHARGE` / `MANUAL_RELEASE` / `TIMEOUT`（`BindingReleaseReason`），對應 SRS 4.3 步驟 7 的三種觸發條件。中文標籤在 `BINDING_RELEASE_REASON_LABELS` |
| `device_acked_at` | `TS?` | 平板**確認收到**憑證的時間。核發成功不等於平板收到，SRS 4.3 步驟 4 要求送達確認 | 平板回報時寫入，同時記 `DEVICE_SESSION_DELIVERED` 稽核 |
| `device_cleared_at` | `TS?` | 平板回報**留在平板上的暫存資料已清除**的時間。這是「下一位病人不會看到上一位資料」這件事的唯一書面證據（SRS 4.3 步驟 8） | 平板回報時寫入，同時記 `DEVICE_LOCAL_DATA_CLEARED` 稽核。⚠️ 解除綁定後這欄仍為 NULL，代表清除未被確認，是需要追查的狀況 |
| `created_at` | `TS` | 紀錄建立時間 | 見共通欄位 |
| `updated_at` | `TS` | 最後修改時間 | 見共通欄位 |

**索引**：`session_token_id`（唯一）、`(status, expires_at)`、`(patient_id, status)`、`(device_id, status)`

**兩條不變條件**（由應用層維護，違反時寫稽核而非拋錯）：

- 一位病人同時只能有一筆 `ACTIVE` 綁定 → 否則記 `BINDING_REJECTED_DUPLICATE_PATIENT`
- 一台平板同時只能有一筆 `ACTIVE` 綁定 → 否則記 `BINDING_REJECTED_DEVICE_BUSY`

---

## 四、病人自述內容

> ⚠️ **這一類全部是「病人自己說的」**。系統**不做**風險分層、不做趨勢預警、不做嚴重度推論 — 那些是刻意排除的 FR-P03／FR-P05，涉及 SaMD 認證邊界。任何看起來像「分級」的欄位（`present`、`severity`、`routed_to`）在下方都有明確說明它為什麼**不是**臨床判斷。

### `symptom_reports` — 透析前症狀問卷送出紀錄（13 欄）

**蒐集的意義**：FR-P02。病人上機前在平板上填一份結構化問卷，護理師在主控台看到彙整結果。蒐集的重點不只是答案本身，還有「**這份答案是什麼時候填的、什麼時候到的、是不是離線補傳的**」 — 因為平板在院內可能斷線，而斷線期間的資料不能遺失也不能重複。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 這份問卷的內部識別碼 | 主鍵 |
| `client_report_id` | `TEXT` UNIQUE | **平板端產生的識別碼**。平板離線時會把答案暫存，連線後補傳；補傳可能重送同一份，靠這個碼認出是同一份 | 唯一鍵，**冪等保證的關鍵**。重送時應判定為重複並記 `SYMPTOM_REPORT_DUPLICATE_IGNORED`，⛔ 不要拋錯，也不要寫入第二筆 |
| `patient_id` | `TEXT` | 這份問卷是哪位病人填的 | 外鍵 → `patients.id`，`ON DELETE NO ACTION`。與 `reported_at` 組成複合索引（趨勢查詢用） |
| `treatment_session_id` | `TEXT` | 屬於哪一次療程 | 外鍵 → `treatment_sessions.id`，`ON DELETE NO ACTION`。有索引 |
| `device_binding_id` | `TEXT` | 透過哪一次綁定送出的。這是「這份資料當時確實有合法授權」的證明 | 外鍵 → `device_bindings.id`，**`ON DELETE CASCADE`** — 本表**唯一**的級聯路徑，其餘外鍵一律 `NO ACTION`（SQL Server 相容性）。有索引 |
| `device_id` | `TEXT` | 從哪一台平板送出的 | 外鍵 → `devices.id`，`ON DELETE NO ACTION`。與 `device_binding_id` 冗餘，但可在綁定紀錄之外獨立追溯裝置 |
| `report_type` | `TEXT` | 問卷類型。目前只有「透析前」一種 | 合法值目前僅 `PRE_DIALYSIS`（`SymptomReportType`）。保留欄位以便日後加透析中／後問卷 |
| `questionnaire_version` | `TEXT` | 填答時用的是哪一版題目。題目日後改版時，舊紀錄仍能對回當時的題目 | 現值 `PRE-DIALYSIS-v1`（`SYMPTOM_QUESTIONNAIRE_VERSION`）。⛔ **題目本身不進資料庫**，它是程式版本的一部分，放在 `@hd/shared` 常數。改題目時必須同時升版本號 |
| `source` | `TEXT` | 是即時送出的，還是離線暫存後補傳的。護理師看到一份「兩小時前填的」問卷時，需要知道它為什麼現在才到 | 合法值 `ONLINE` / `OFFLINE_SYNC`（`SymptomReportSource`） |
| `reported_at` | `TS` | **病人實際在平板上填寫的時間** | 由平板端提供。離線時會早於 `received_at`。臨床判讀應以此為準 |
| `received_at` | `TS` | **後端收到的時間** | `DEFAULT CURRENT_TIMESTAMP`。與 `reported_at` 刻意分開保存，兩者皆供稽核。⛔ 不要用其中一個蓋掉另一個 |
| `note` | `TEXT?` | 病人自由補充的文字 | 自由文字，原樣保存。⛔ 不做任何解析、分類或摘要推論 |
| `created_at` | `TS` | 紀錄寫入時間 | 見共通欄位 |

**索引**：`client_report_id`（唯一）、`(patient_id, reported_at)`、`treatment_session_id`、`device_binding_id`
**注意**：本表**沒有 `updated_at`** — 送出的問卷是事實紀錄，不修改。要更正就送新的一份。

---

### `symptom_answers` — 單題作答（6 欄）

**蒐集的意義**：一份問卷有 10 題，答案沒有塞進 jsonb 而是正規化成獨立的列（《資料庫使用規範》第 6 條）。好處是可以直接用 SQL 問「這位病人最近五次有幾次回報水腫」，而且遷移到任何資料庫都不需要處理 JSON 型別差異。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 這筆作答的內部識別碼 | 主鍵 |
| `symptom_report_id` | `TEXT` | 屬於哪一份問卷 | 外鍵 → `symptom_reports.id`，`ON DELETE CASCADE` |
| `item_code` | `TEXT` | 題目代碼。10 題分別是水腫、喘、發燒、通路出血、通路紅腫痛、胸悶、頭暈、抽筋、噁心、皮膚癢 | 合法值取自 `PRE_DIALYSIS_SYMPTOM_QUESTIONS`：`EDEMA` `DYSPNEA` `FEVER` `ACCESS_BLEEDING` `ACCESS_ABNORMAL` `CHEST_DISCOMFORT` `DIZZINESS` `CRAMP` `NAUSEA` `ITCHING`。有索引。題目中文與白話說明查 `SYMPTOM_QUESTION_BY_CODE` |
| `answer_value` | `TEXT` | 病人選的答案。多數題目是四級（沒有／輕微／中等／嚴重），發燒與通路出血是二選一（沒有／有） | 合法值 `NONE` `MILD` `MODERATE` `SEVERE` `NO` `YES`（`SYMPTOM_ANSWER_VALUES`）。**量表由題目決定**：`SEVERITY` 題只能用前四個，`YES_NO` 題只能用後兩個，對照表在 `SYMPTOM_SCALE_OPTIONS` |
| `present` | `BOOL` | 病人是否表示「有這個症狀」。**這只是把答案原樣轉成是／否方便計數與顯示，不是嚴重度分級，也不是任何風險判斷** | 由 `SYMPTOM_PRESENT_VALUES`（`MILD` `MODERATE` `SEVERE` `YES`）機械式推導。⛔ **禁止**在此欄之上疊加任何加權、評分或門檻邏輯 — 那會落入已排除的 FR-P03 風險分層 |
| `created_at` | `TS` | 寫入時間 | 見共通欄位 |

**唯一約束**：`(symptom_report_id, item_code)` — 同一份問卷的同一題只能有一個答案。
**索引**：`item_code`（跨病人的單一症狀查詢用）
**注意**：無 `updated_at`，理由同 `symptom_reports`。

---

### `help_requests` — 求助按鈕與緊急通報（20 欄）

**蒐集的意義**：FR-P06（病人端求助）與 FR-N03（護理端緊急通報）是同一件事的兩端，因此共用同一筆紀錄，完整保存從「病人按下」到「護理師處理完成」的生命週期。蒐集的重點包含**兩個時間戳的差**（按下 vs 收到）— 那是 SRS 第 6 章「五秒內送達」這條非功能需求的量測依據。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 這筆通報的內部識別碼 | 主鍵 |
| `client_request_id` | `TEXT` UNIQUE | 平板端產生的識別碼。病人可能連按好幾下，或離線後補送，靠這個碼避免同一次求助變成多筆通報 | 唯一鍵，冪等保證。重送應視為同一筆 |
| `patient_id` | `TEXT` | 是哪位病人求助 | 外鍵 → `patients.id`，`ON DELETE NO ACTION`。與 `raised_at` 組成複合索引 |
| `treatment_session_id` | `TEXT` | 發生在哪一次療程 | 外鍵 → `treatment_sessions.id`，`ON DELETE NO ACTION`。有索引 |
| `device_binding_id` | `TEXT` | 透過哪一次綁定送出 | 外鍵 → `device_bindings.id`，**`ON DELETE CASCADE`** — 本表唯一級聯路徑。有索引 |
| `device_id` | `TEXT` | 從哪一台平板送出。護理師要知道跑去哪一床 | 外鍵 → `devices.id`，`ON DELETE NO ACTION` |
| `category` | `TEXT` | 求助類型，由病人自己從七個選項中挑：身體不舒服、打針處或管路有狀況、機器在叫、需要上廁所、環境調整、口渴或肚子餓、其他 | 合法值見 `HelpRequestCategory`：`PHYSICAL_DISCOMFORT` `ACCESS_PROBLEM` `MACHINE_ALARM` `TOILET` `ENVIRONMENT` `THIRST_HUNGER` `OTHER`。中文在 `HELP_REQUEST_CATEGORY_LABELS` |
| `severity` | `TEXT` | 急迫度，**由病人自己選**：非常緊急／不太舒服／不急。**不是系統依資料推論出來的分級** | 合法值 `EMERGENCY` / `URGENT` / `ROUTINE`（`HelpRequestSeverity`）。與 `status` 組成複合索引。⛔ **禁止**由系統覆寫或「修正」病人的選擇 |
| `routed_to` | `TEXT` | 這筆通報被分派給誰：緊急處置團隊、護理師、或護佐。**分派結果會被保存下來**，這樣事後查核時能看出當時套用的是哪一版規則 | 合法值 `EMERGENCY_TEAM` / `NURSE` / `NURSE_AIDE`（`HelpRequestRoute`）。由 `routeHelpRequest(category, severity)` 計算 — 那是一條**靜態規則**，輸入只有病人自選的兩個值，不讀歷史資料、不做趨勢推論，因此不屬於已排除的 FR-P03／FR-P05。⛔ 改規則要改 `@hd/shared` 那個函式，不要在各處寫死 |
| `status` | `TEXT` | 處理進度：待處理、已接收前往中、已處理完成、已取消 | 合法值 `PENDING` / `ACKNOWLEDGED` / `RESOLVED` / `CANCELLED`（`HelpRequestStatus`）。中文在 `HELP_REQUEST_STATUS_LABELS` |
| `message` | `TEXT?` | 病人自己打的補充說明 | 自由文字，原樣保存。⛔ 不做語意分析或自動分類 |
| `raised_at` | `TS` | **病人按下按鈕的時間** | 由平板端提供 |
| `received_at` | `TS` | **後端收到的時間**。與上一欄相減就是實際延遲，這是驗證「五秒內送達」的原始資料 | `DEFAULT CURRENT_TIMESTAMP`。⛔ 兩個時間戳必須分開保存，不可合併 |
| `acknowledged_by_id` | `TEXT?` | 哪一位護理師按下「我收到了，前往中」 | 外鍵 → `nurses.id`，`ON DELETE NO ACTION` |
| `acknowledged_at` | `TS?` | 接收的時間 | 與 `acknowledged_by_id` 同時寫入，並記 `HELP_REQUEST_ACKNOWLEDGED` 稽核 |
| `resolved_by_id` | `TEXT?` | 哪一位護理師結案。可能與接收者不同人 | 外鍵 → `nurses.id`，`ON DELETE NO ACTION` |
| `resolved_at` | `TS?` | 結案時間 | 與 `resolved_by_id` 同時寫入，並記 `HELP_REQUEST_RESOLVED` 稽核 |
| `resolution_note` | `TEXT?` | 護理師填寫的處理說明 | 自由文字。⛔ 這是護理紀錄的雛形，但**不是**正式護理記錄 — 正式記錄屬 Iteration 3 範圍 |
| `created_at` | `TS` | 紀錄建立時間 | 見共通欄位 |
| `updated_at` | `TS` | 最後狀態變更時間 | 見共通欄位。本類三張表中**只有這張有** — 因為通報的狀態會隨處理流程改變 |

**索引**：`client_request_id`（唯一）、`(status, severity)`、`(patient_id, raised_at)`、`treatment_session_id`、`device_binding_id`
**已知缺口**：`CANCELLED` 狀態沒有對應的 `cancelled_by_id` / `cancelled_at` 欄位，取消者只能從 `audit_logs` 的 `HELP_REQUEST_CANCELLED` 回查。

---

## 五、稽核軌跡

### `audit_logs` — 誰、何時、對誰、做了什麼（15 欄）

**蒐集的意義**：FR-S02，也是整份《資料庫使用規範》最在意的一張表。SRS 4.1 要求「存取授權可追溯到哪一位護理師、何時、為哪一位病人核准」，這張表就是那項要求真正被實現的地方。

它有兩個刻意的設計：**關聯欄位全部正規化為外鍵**（不用 jsonb，符合第 6 條），同時**冗餘保存操作者標籤與平板序號的字串** — 因為帳號可能改名、平板可能報廢，若只留外鍵，多年後回查軌跡會失真。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 這筆軌跡的內部識別碼 | 主鍵 |
| `occurred_at` | `TS` | **事件發生的時間** | `DEFAULT CURRENT_TIMESTAMP`，有索引。本表沒有 `created_at`／`updated_at`，這一欄就是時間軸 |
| `actor_type` | `TEXT` | 動作是誰做的類型：護理人員、系統自動、或平板 | 合法值 `NURSE` / `SYSTEM` / `DEVICE`（`AuditActorType`）。逾時自動失效這類事件是 `SYSTEM` |
| `actor_nurse_id` | `TEXT?` | 若是護理人員操作，是哪一位 | 外鍵 → `nurses.id`，`ON DELETE NO ACTION`，有索引。`actor_type` 非 `NURSE` 時為 NULL |
| `actor_label` | `TEXT` | **操作者當下的識別字串**，例如「N001（王小明）」。即使這個帳號日後改名或停用，軌跡上仍看得到當時是誰 | **必填**，冗餘欄位。實際格式：護理師 `工作ID（顯示名稱）`、系統 `SYSTEM`、平板 `平板 序號`（見 `audit.service.ts`）。⛔ 不要改成從 `nurses` join 出來 — 冗餘正是重點 |
| `action` | `TEXT` | 做了什麼動作，例如「裝置綁定」「登入失敗」「病人送出症狀問卷」 | 合法值目前 **32 個**，全部定義在 `AuditAction`，中文對照在 `AUDIT_ACTION_LABELS`。有索引。⛔ 新增功能時**必須**在 `@hd/shared` 補上代碼與中文標籤，不可直接寫死字串 |
| `target_type` | `TEXT?` | 這個動作作用在哪一種東西上，例如帳號、綁定紀錄 | 實際使用的值：`'Nurse'`、`'DeviceBinding'` 等（模型名，PascalCase）。⚠️ **未以常數約束**，屬已知粗糙處 |
| `target_id` | `TEXT?` | 作用對象的識別碼 | 與 `target_type` 成對使用。刻意不設外鍵 — 對象可能跨多張表 |
| `patient_id` | `TEXT?` | **這個動作牽涉到哪一位病人**。SRS 4.1「為哪一位病人」對應的欄位 | 外鍵 → `patients.id`，`ON DELETE NO ACTION`，有索引。與病人無關的動作（如護理師登入）為 NULL |
| `device_id` | `TEXT?` | 牽涉到哪一台平板 | 外鍵 → `devices.id`，`ON DELETE NO ACTION` |
| `device_serial_no` | `TEXT?` | **平板序號的字串副本**。SRS 4.3 步驟 9 明列序號為必要稽核欄位，即使該平板日後報廢除役，軌跡仍須可讀 | 冗餘欄位，**有獨立索引**（實務上是靠序號查軌跡，不是靠 `device_id`）。有 `device_id` 時應同時填這欄 |
| `outcome` | `TEXT` | 成功還是失敗。**失敗也要記** — 連續的登入失敗、被擋掉的綁定，本身就是要追查的訊號 | 合法值 `SUCCESS` / `FAILURE`（`AuditOutcome`）。⛔ 不要只在成功時寫稽核 |
| `detail` | `TEXT?` | 自由描述文字，補充上述欄位講不清楚的部分 | ⛔ **不承載結構化關聯資料**（第 6 條）。需要被查詢的資訊要開成正式欄位，不要塞進這裡 |
| `ip_address` | `TEXT?` | 操作來源 IP | 選填 |
| `user_agent` | `TEXT?` | 操作所用的瀏覽器／裝置 | 選填，原樣保存 |

**索引**：`occurred_at`、`action`、`actor_nurse_id`、`patient_id`、`device_serial_no`

**寫入原則**：

- 所有外鍵都是 `ON DELETE NO ACTION` — **軌跡不因主檔異動而消失**
- 本表**只增不改不刪**，沒有 `updated_at` 是刻意的
- 稽核寫入與即時廣播是**平行**進行的（見技術報告第 8 章），不要改成依序等待

---

## 附錄 A：資料不流向哪裡

同樣重要的是**沒有**蒐集什麼。以下都不在資料庫裡，且都是刻意的：

| 沒有蒐集 | 原因 |
|---|---|
| 生命徵象、檢驗值、透析處方 | 不在 MVP 範圍。本系統不是電子病歷 |
| 風險分數、嚴重度分級、趨勢預警 | 刻意排除的 FR-P03／FR-P05，涉及 SaMD 認證邊界 |
| 密碼明文、Session Token 明文、平板 API 金鑰明文 | 一律只存雜湊或 jti |
| 任何真實病人可識別資訊 | 《資料庫使用規範》第 7 條，測試階段鐵則 |
| 病人的登入帳號 | 病人不登入，身分由護理師觸發的裝置綁定代理（SRS 4.3） |
| 症狀問卷的題目文字 | 題目是程式版本的一部分，放在 `@hd/shared`，紀錄只存版本號 |

## 附錄 B：Agent 動 schema 前的自我檢查

摘自《[資料庫使用規範](../requirements/database-policy.md)》第 9 條，逐條確認：

- [ ] 這個改動是否讓前端直接連 Supabase？→ 改走後端 API
- [ ] 是否用 Supabase Auth 做身分驗證？→ 改用自建 Session Token
- [ ] 存取控制是否寫在 RLS／Edge Functions？→ 改寫在後端應用層
- [ ] 是否在 controller／service 直接嵌入 Supabase 專屬查詢語法？→ 改走 Repository／Prisma
- [ ] 測試資料是否為 faker 合成資料？→ 一律替換
- [ ] 新欄位是否已納入稽核軌跡（誰、何時、對誰、做了什麼）？→ 補齊再實作
- [ ] 是否用了 Prisma enum、jsonb、或 PostgreSQL 專屬預設值？→ 改成 `TEXT` ＋ 應用層常數
- [ ] 新外鍵是否在同一張表製造第二條級聯路徑？→ 除指定的那一條外一律 `NO ACTION`
- [ ] 改完後本文件是否需要同步更新？

---

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|
| 0909 | 2026-09-09 | 首次定版 |

[← 回進度首頁](../index.md)
