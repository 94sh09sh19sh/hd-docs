# 血液透析平板照護輔助系統 — 資料字典

**範圍**：目前資料庫實際蒐集的全部資料 — 54 張表、534 個欄位、10 個 migration（`init`、`iteration3_closed_network`、`iteration4_ai_content`、`iteration5_help_resolution_shifts_baseline`、`iteration6_carousel_file_import`、`iteration7_update_runs`、`iteration9_navigation_content`、`iteration9_help_category_label`、`iteration10_kiosk_foreground`、`iteration12_kiosk_shell_version`）
**來源**：`apps/api/prisma/schema.prisma`、`apps/api/prisma/migrations/`、`packages/shared/src/constants.ts`、`packages/shared/src/platform.ts`、`packages/shared/src/education.ts`、`packages/shared/src/nursing.ts`、`packages/shared/src/operations.ts`、`packages/shared/src/carousel.ts`
**環境**：SQLite 單一檔案。開發階段在開發者本機、專案目錄外；正式部署在院內伺服器的本機磁碟。見《[資料庫使用規範](../requirements/database-policy.md)》

---

## 0. 怎麼讀這份文件

每張表的欄位清單都有**兩欄說明**，寫給兩種不同的讀者：

| 欄位 | 寫給誰 | 回答什麼問題 |
|---|---|---|
| **給人看的說明** | 臨床端、專案管理、接手的人 | 這個欄位在真實世界裡是什麼？**為什麼要蒐集它？** |
| **給 Agent 的說明** | AI coding agent、寫程式的人 | 合法值有哪些？誰負責填？不變條件是什麼？**動這個欄位會踩到什麼？** |

> **給 Agent 的總則**：本文件描述的是**現況**，不是規格。若與 `schema.prisma` 不一致，以 `schema.prisma` 為準並回報本文件已過時。修改任何欄位前，先讀《[資料庫使用規範](../requirements/database-policy.md)》第 6 條與第 16 條的檢查清單。

### 全表共通的設計約束

這些約束來自《資料庫使用規範》6.1。資料庫已經是 SQLite，它們的理由從「將來要遷到醫院資料庫」變成「不要被任何一種資料庫綁死」——優先權下降，但一條都不放寬：

1. **不使用 Prisma enum** — 所有列舉值都是 `TEXT`，合法值由 `@hd/shared` 常數與 class-validator 在**應用層**把關。
2. **不使用 JSON 欄位**承載結構化關聯資料 — 一律正規化成資料表與外鍵。
3. **不使用資料庫專屬預設值** — UUID 由 Prisma client 在應用層產生。
4. **命名**：欄位 `snake_case`，表名複數 `snake_case`。
5. **稽核欄位不因階段省略** — 誰、何時、對誰、做了什麼，設計時就納入。
6. **級聯路徑只留一條** — 多條級聯刪除路徑本身就難以推理。除了指定的那一條外鍵，其餘一律 `NO ACTION`。迭代 3 新增的五張表全部不帶級聯刪除。迭代 4 的十四張表只讓「主表 → 自己的明細」帶級聯（勾選欄位、測驗作答、回饋分數、文件段落、查詢引用），其餘一律 `NO ACTION`。迭代 5 的七張表同理：求助的後續追蹤沿用 `help_requests` 既有的那一條，床位分配與調班申請掛在 `nurse_shifts` 底下，其餘（選項清單、營運參數、成效基準）不帶任何級聯——它們是治理紀錄，成效基準更是過期就拿不到的一次性資料。迭代 6 的三張表同樣一條級聯都不帶：輪播內容與欄位對應是設定，瀏覽事件是成效資料。

另依規範 6.2：**任何劑量、體重、超過濾量等臨床數值不得使用浮點數**，一律以整數最小單位或「整數＋小數位數」記錄。

### 型別對照

| 本文件寫法 | migration 宣告 | SQLite 實際儲存 | Prisma 型別 | 說明 |
|---|---|---|---|---|
| `TEXT` | `TEXT NOT NULL` | TEXT | `String` | 必填字串 |
| `TEXT?` | `TEXT` | TEXT 或 NULL | `String?` | 選填字串 |
| `BOOL` | `BOOLEAN NOT NULL` | INTEGER 0／1 | `Boolean` | 必填布林，皆有 DEFAULT。程式端一律當布林用，不直接比對 0／1 |
| `TS` | `DATETIME NOT NULL` | Prisma 寫入的毫秒時間值 | `DateTime` | 必填時間戳，**一律以 UTC 寫入**，顯示時才轉當地時間 |
| `TS?` | `DATETIME` | 同上或 NULL | `DateTime?` | 選填時間戳 |
| `INT` | `INTEGER NOT NULL` | INTEGER | `Int` | 必填整數 |
| `INT?` | `INTEGER` | INTEGER 或 NULL | `Int?` | 選填整數 |
| `BIGINT?` | `BIGINT` | INTEGER 或 NULL | `BigInt?` | 選填大整數；API 回應時轉成一般數字 |

SQLite 沒有嚴格型別（未使用 STRICT 表），欄位可以塞進任何型別的值。**應用層驗證是唯一防線**，class-validator 不可省略。字串比對預設區分大小寫。

### 資料分類一覽

| 類別 | 表 | 蒐集的本質 |
|---|---|---|
| 一、帳號與登入憑證 | `nurses`、`nurse_sessions` | 誰有權操作系統，以及他現在持有哪張有效的通行證 |
| 二、主檔 | `patients`、`devices` | 系統管理的實體：人與平板 |
| 三、排班與綁定 | `treatment_sessions`、`device_bindings` | 系統核心：哪台平板在哪個時段屬於哪位病人 |
| 四、病人自述內容 | `symptom_reports`、`symptom_answers`、`help_requests` | 病人自己填的、自己按的 — **全部是自述，不含任何系統推論** |
| 五、稽核軌跡 | `audit_logs` | 所有類別發生的每一次操作留下的不可否認紀錄 |
| 六、系統治理（迭代 3） | `feature_flags`、`ai_invocations`、`backup_runs` | 哪些功能開著、AI 被呼叫過幾次送了什麼、資料庫有沒有備份 |
| 七、院方臨床數值（迭代 3） | `clinical_value_imports`、`clinical_values` | 院方提供的少數臨床數值，以及它們從哪裡、什麼時候、由誰匯入 |
| 八、背景佇列（迭代 4） | `ai_jobs` | 「可以等」的 AI 生成工作排在哪、做到哪、成功或為什麼失敗 |
| 九、衛教、測驗與病人回饋（迭代 4） | `education_contents`、`education_completions`、`quiz_attempts`、`quiz_answers`、`feedback_responses`、`feedback_answers` | AI 產生、護理師核可的衛教內容；病人讀了什麼、答對了什麼、自己填的心情與滿意度 |
| 十、護理記錄與計算（迭代 4） | `nursing_records`、`nursing_record_fields`、`adequacy_calculations` | 護理師簽核的記錄與它的起點（預填文字或 AI 初稿）；依公式算出的透析適足性 |
| 十一、SOP 文件與查詢（迭代 4） | `sop_documents`、`sop_sections`、`sop_queries`、`sop_query_citations` | 查詢範圍內的文件原文，以及每一次查詢引用了哪幾段 |
| 十二、求助處理與可設定的暫代值（迭代 5） | `help_resolution_options`、`operational_settings`、`help_request_follow_ups` | 求助結案時選的是哪一項處理方式與結果、那份清單本身、以及外部答覆未到前的各項暫定參數 |
| 十三、護理師班表與成效基準（迭代 5） | `nurse_shifts`、`shift_bed_assignments`、`shift_change_requests`、`baseline_measurements` | 誰上哪一班、負責哪幾床、調班的來龍去脈；以及系統啟用前的人工量測結果 |
| 十四、閒置輪播與檔案匯入（迭代 6） | `carousel_items`、`carousel_view_events`、`import_field_mappings` | 輪播第二層播什麼、哪一類卡片有人看、匯入檔案的欄位怎麼對上 |
| 十五、版本更新紀錄（迭代 7） | `update_runs` | 每一次版本更新前備份了什麼、驗證還原成不成功、套用了哪幾個遷移、誰執行的 |
| 十六、導覽版位與內容資料化（迭代 9） | `nav_placement_settings`、`help_categories`、`help_request_methods`、`questionnaire_*`、`quiz_*`、`feedback_form_*`、`symptom_answer_options` | 哪些功能出現在哪裡；病人與護理師看到的選項與題目是什麼，以及它們改過幾版 |

### 每張表都有的三個欄位

以下三個欄位在多數表重複出現，個別表的欄位清單中不再逐一解釋：

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 這筆資料的唯一識別碼，系統內部使用，不對使用者顯示 | UUID v4 字串，主鍵。**由 Prisma client 在應用層產生**（`@default(uuid())`），不是資料庫函式 |
| `created_at` | `TS` | 這筆資料被建立的時間 | `DEFAULT CURRENT_TIMESTAMP`，寫入時不要手動指定 |
| `updated_at` | `TS` | 這筆資料最後一次被修改的時間 | Prisma `@updatedAt` 自動維護。**只有會被更新的表才有這欄** — 事實紀錄（`symptom_reports`、`symptom_answers`、`audit_logs`）與迭代 3 的五張治理表刻意沒有這欄。迭代 4 只有會隨審閱、簽核改變狀態的 `education_contents`、`nursing_records` 有這欄。迭代 5 為 `help_resolution_options`、`nurse_shifts`、`shift_change_requests` 三張會被改動的表保留這欄；`operational_settings.updated_at` 例外——它**刻意可為空**，空代表「從未被改過」 |

---

## 一、帳號與登入憑證

### `nurses` — 護理端使用者（13 欄）

**蒐集的意義**：本系統的所有寫入操作都必須追溯到一個具名的護理人員（SRS 4.1）。這張表就是「具名」的來源 — 沒有這張表，稽核軌跡上的每一筆都會變成匿名操作，整個資料治理設計就失效了。

病人**不在這張表裡**，病人不登入（SRS 4.3）。醫院管理層與稽核角色的帳號也在這張表，以 `role` 區分。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 帳號的內部識別碼 | 主鍵，見上方共通欄位 |
| `work_id` | `TEXT` UNIQUE | 護理人員的**工作識別碼**，也就是登入時輸入的帳號。蒐集它是因為稽核軌跡必須對得上醫院的人事編制，而不是一個系統自己發明的流水號 | 唯一鍵。登入查詢的入口。**不要**用 `id` 當登入帳號。SQLite 字串比對區分大小寫 |
| `display_name` | `TEXT` | 顯示名稱，護理站主控台上看到的名字 | 僅供顯示。測試環境為 faker 合成資料 |
| `password_hash` | `TEXT` | 密碼的雜湊值。**系統不儲存密碼明文** | bcrypt 雜湊。⛔ **禁止**改用任何第三方託管身分服務（《資料庫使用規範》第 3 條）。⛔ 禁止出現在任何 API 回應或 log 中 |
| `role` | `TEXT` | 角色，決定這個人能做什麼：最高權限、護理站管理者、護理長、一般護理師，以及兩個唯讀角色——醫院管理層、稽核 | 合法值 `SUPER_ADMIN` / `NURSE_MANAGER` / `NURSE_LEAD` / `NURSE` / `HOSPITAL_VIEWER` / `AUDITOR`，定義於 `@hd/shared` 的 `NurseRole`。⛔ 權限判斷寫在後端守衛與 service 層（第 4 條）。唯讀角色由全域守衛**預設全擋**，只放行標示 `@AllowReadOnlyRoles()` 的端點。有索引 |
| `status` | `TEXT` | 帳號狀態。新註冊的人是「待審核」，要由有權限的人核准才能用；也可以被駁回或停權 | 合法值 `PENDING` / `ACTIVE` / `REJECTED` / `SUSPENDED`，見 `NurseStatus`。**只有 `ACTIVE` 能通過 `NurseAuthGuard`**。有索引 |
| `can_approve_nurses` | `BOOL` | 是否被單獨授予「審核他人註冊」的權限。這是為了讓最高權限帳號能把審核工作分出去，而不必把整個管理權限一起給出去 | `DEFAULT false`。與 `role` **正交** — 一個 `NURSE` 也可以有這個權限。唯讀角色一律為 `false`，後端拒絕授予。授予／收回都要寫 `NURSE_PERMISSION_GRANTED` / `_REVOKED` 稽核 |
| `password_change_required` | `BOOL` | 是否強制下次登入要改密碼。用於初始帳號與管理員重設密碼後 | `DEFAULT false`。為 `true` 時前端只顯示改密碼畫面 |
| `approved_by_id` | `TEXT?` | **是誰核准這個帳號的**。蒐集它是因為「授權可追溯到哪一位護理師核准」是 SRS 4.1 的明文要求 | 自關聯外鍵 → `nurses.id`，`ON DELETE NO ACTION`。`PENDING` 狀態時為 NULL |
| `approved_at` | `TS?` | 核准的時間 | 與 `approved_by_id` 同時寫入，不要只填其中一個 |
| `last_login_at` | `TS?` | 最後一次成功登入的時間。用於辨識長期未使用而該停權的帳號 | 只在登入**成功**時更新。失敗不動這欄（失敗記在 `audit_logs`） |
| `created_at` | `TS` | 註冊申請送出的時間 | 見共通欄位 |
| `updated_at` | `TS` | 帳號資料最後修改時間 | 見共通欄位 |

**索引**：`work_id`（唯一）、`status`、`role`
**被參照**：`nurse_sessions`、`treatment_sessions.created_by_id`、`device_bindings.bound_by_id`／`released_by_id`、`help_requests.acknowledged_by_id`／`resolved_by_id`、`audit_logs.actor_nurse_id`、`feature_flags.changed_by_id`、`ai_invocations.actor_nurse_id`、`backup_runs.initiated_by_id`、`clinical_value_imports.imported_by_id`；迭代 4：`ai_jobs.requested_by_id`、`education_contents.requested_by_id`／`reviewed_by_id`、`nursing_records.created_by_id`／`signed_by_id`、`adequacy_calculations.calculated_by_id`、`sop_queries.asked_by_id`；迭代 5：`help_requests.arrived_by_id`、`help_request_follow_ups.created_by_id`／`closed_by_id`、`operational_settings.updated_by_id`、`nurse_shifts.nurse_id`／`created_by_id`、`shift_bed_assignments.assigned_by_id`、`shift_change_requests.requested_by_id`／`proposed_nurse_id`／`decided_by_id`、`baseline_measurements.recorded_by_id`

---

### `nurse_sessions` — 已核發的登入憑證（9 欄）

**蒐集的意義**：JWT 本身是無狀態的，簽出去就收不回來。但本系統需要在「改密碼」「降權」「停權」時**立刻讓已核發的 token 失效**。這張表存的就是每一張已核發 token 的留底，讓後端能主動作廢。同時它也記錄登入來源的 IP 與裝置，作為非預期存取的追查依據。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 這筆憑證紀錄的內部識別碼 | 主鍵 |
| `nurse_id` | `TEXT` | 這張憑證是發給哪一位護理人員的 | 外鍵 → `nurses.id`，**`ON DELETE CASCADE`**（本表唯一的級聯來源）。有索引 |
| `token_id` | `TEXT` UNIQUE | 憑證的序號。系統靠比對這個序號來判斷一張 token 是否仍然有效 | JWT 的 `jti` claim。`NurseAuthGuard` 每次驗證都查這張表。⛔ **不存 token 本身**，只存 jti |
| `issued_at` | `TS` | 核發時間 | `DEFAULT CURRENT_TIMESTAMP` |
| `expires_at` | `TS` | 到期時間。過了就要重新登入 | 有索引，供批次清理過期紀錄。判定失效時 `expires_at` 與 `revoked_at` **兩者都要檢查** |
| `revoked_at` | `TS?` | 被提前作廢的時間。NULL 代表未被作廢 | 作廢是寫入這欄，**不是刪除該列** — 刪除會讓作廢這件事本身失去紀錄 |
| `revoked_reason` | `TEXT?` | 作廢的原因（登出、改密碼、權限異動等） | 自由文字。與 `revoked_at` 同時寫入 |
| `ip_address` | `TEXT?` | 登入來源的 IP。用於事後追查非預期的存取 | 選填，取自請求標頭。院內網路環境下為內網位址 |
| `user_agent` | `TEXT?` | 登入所用的瀏覽器／裝置資訊。同樣用於追查 | 選填，原樣記錄不解析 |

**索引**：`token_id`（唯一）、`nurse_id`、`expires_at`
**注意**：本表沒有 `updated_at` — 憑證紀錄只會被「作廢」一次，狀態變化由 `revoked_at` 表達。

---

## 二、主檔

### `patients` — 病人（9 欄）

**蒐集的意義**：綁定、排班、症狀回報、求助全部要指向一個明確的病人。這張表刻意**只存識別與基本人口學資料，不存臨床數值**。院方提供的少數臨床數值（乾體重、Kt/V 等）另存於第七類的 `clinical_values`，每一筆都帶資料時間與來源批次。

> ⚠️ **測試資料鐵則**：開發者本機不是院內環境，《資料庫使用規範》第 10 條**絕對禁止**在此放入任何接近真實病人的可識別資訊。現行測試資料由 `prisma/seed.ts` 以 `fakerZH_TW` 產生 8 筆全合成資料。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 病人的內部識別碼 | 主鍵。**跨表一律用這個**，不要用病歷號串接 |
| `medical_record_no` | `TEXT` UNIQUE | 病歷號。護理師在主控台上是用這個找病人的，蒐集它是為了讓系統對得上醫院既有的病人識別方式 | 唯一鍵。測試環境格式固定為 `HD-TEST-0001`。⛔ 產生測試資料時**只能**用這個合成格式。AI 閘道以 `HD-TEST-` 前綴判定合成資料，**無法證明是合成資料者一律視為真實病人資料**（`isSyntheticMedicalRecordNo`） |
| `display_name` | `TEXT` | 病人姓名，護理站畫面與平板歡迎畫面上顯示 | ⛔ 測試環境必為 faker 假名。送進 AI 流程前一律由去識別化移除 |
| `birth_date` | `TS?` | 出生日期。臨床上用於基本身分核對 | 選填。只有日期有意義，時間部分忽略 |
| `gender` | `TEXT?` | 性別 | 選填。seed 產生 `'M'` / `'F'`，**應用層目前未強制列舉**，屬已知粗糙處 |
| `note` | `TEXT?` | 備註欄，護理端自由填寫 | 自由文字。⛔ 不要用它承載結構化資料（違反 6.1）— 需要結構就開欄位或開表。測試資料一律標註「合成測試資料，非真實病人」 |
| `active` | `BOOL` | 這位病人是否仍在本中心接受治療。轉院或結案的病人設為否，但資料保留 | `DEFAULT true`。有索引。**停用是設 false，不是刪除** — 刪除會連帶影響歷史綁定與稽核 |
| `created_at` | `TS` | 建檔時間 | 見共通欄位 |
| `updated_at` | `TS` | 最後修改時間 | 見共通欄位 |

**索引**：`medical_record_no`（唯一）、`active`
**被參照**：`treatment_sessions`、`device_bindings`、`symptom_reports`、`help_requests`、`audit_logs`、`ai_invocations`、`clinical_values`；迭代 4：`ai_jobs`、`education_contents`、`education_completions`、`quiz_attempts`、`feedback_responses`、`nursing_records`、`adequacy_calculations`

---

### `devices` — 病人端平板（17 欄）

**蒐集的意義**：透析中心共 15 台平板（SRS 第 9 章）。平板**沒有病人登入機制**，它憑什麼證明自己是「3 號床那台」？靠的就是這張表裡的序號與 API 金鑰雜湊。這張表同時記錄 MDM（行動裝置管理）狀態，因為平板是共用裝置，必須能遠端鎖定與限制為單一 App。

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
| `kiosk_foreground` | `BOOL?` | 平板最後一次回報時是否停在病人端畫面上（迭代 10 逸出偵測；迭代 12 起在外殼裡是「可見而且仍釘選」） | 空值＝從未回報（還沒裝外殼），與「已跳出」分開 |
| `kiosk_reported_at` | `TS?` | 最後一次收到前景回報的時間。超過 90 秒沒有回報，護理端顯示「失去回報」 | 每 30 秒更新一次 |
| `kiosk_exited_at` | `TS?` | 最後一次回報「離開前景」的時間。回到前景之後仍保留，答得出上一次是什麼時候跳出去的 | 只在回報離開時更新 |
| `shell_version` | `TEXT?` | 外殼 App 最後一次回報的自身版本，例 `0.2.0`（迭代 12，FR-S14） | 空值＝未回報版本（迭代 12 之前的外殼或一般瀏覽器）。不帶版本的回報不會把它洗掉 |
| `shell_contract_version` | `INT?` | 外殼 App 實作的契約版本。與系統的契約版本不同時，護理端標為「版本不相容」 | 與 `shell_version` 同進退；「外殼過舊」由最低可用版本設定當場推算，不存欄位 |
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
| `scheduled_date` | `TS` | 排班日期 | **只取日期部分**，實務上存當日 `00:00 UTC`。⚠️ 這個慣例不要改（規範 6.2 已踩過一次）；比較日期時務必正規化到同一時區（見 `common/date.util.ts`） |
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

**兩條不變條件**（由應用層在同一個 Serializable 交易內維護，違反時寫稽核而非拋錯）：

- 一位病人同時只能有一筆 `ACTIVE` 綁定 → 否則記 `BINDING_REJECTED_DUPLICATE_PATIENT`
- 一台平板同時只能有一筆 `ACTIVE` 綁定 → 否則記 `BINDING_REJECTED_DEVICE_BUSY`

---

## 四、病人自述內容

> ⚠️ **這一類全部是「病人自己說的」**。這幾張表**不存**風險分層、趨勢預警或嚴重度推論——那屬 FR-P03／FR-P05，迭代 11 以規則引擎實作（0919 編號重排前稱迭代 7），受功能開關與書面確認閘門約束，結果另存專屬資料表。任何看起來像「分級」的欄位（`present`、`severity`、`routed_to`）在下方都有明確說明它為什麼**不是**臨床判斷。

### `symptom_reports` — 透析前症狀問卷送出紀錄（13 欄）

**蒐集的意義**：FR-P02。病人上機前在平板上填一份結構化問卷，護理師在主控台看到彙整結果。蒐集的重點不只是答案本身，還有「**這份答案是什麼時候填的、什麼時候到的、是不是離線補傳的**」 — 因為平板在院內可能斷線，而斷線期間的資料不能遺失也不能重複。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 這份問卷的內部識別碼 | 主鍵 |
| `client_report_id` | `TEXT` UNIQUE | **平板端產生的識別碼**。平板離線時會把答案暫存，連線後補傳；補傳可能重送同一份，靠這個碼認出是同一份 | 唯一鍵，**冪等保證的關鍵**。重送時應判定為重複並記 `SYMPTOM_REPORT_DUPLICATE_IGNORED`，⛔ 不要拋錯，也不要寫入第二筆 |
| `patient_id` | `TEXT` | 這份問卷是哪位病人填的 | 外鍵 → `patients.id`，`ON DELETE NO ACTION`。與 `reported_at` 組成複合索引（趨勢查詢用） |
| `treatment_session_id` | `TEXT` | 屬於哪一次療程 | 外鍵 → `treatment_sessions.id`，`ON DELETE NO ACTION`。有索引 |
| `device_binding_id` | `TEXT` | 透過哪一次綁定送出的。這是「這份資料當時確實有合法授權」的證明 | 外鍵 → `device_bindings.id`，**`ON DELETE CASCADE`** — 本表**唯一**的級聯路徑，其餘外鍵一律 `NO ACTION`。有索引 |
| `device_id` | `TEXT` | 從哪一台平板送出的 | 外鍵 → `devices.id`，`ON DELETE NO ACTION`。與 `device_binding_id` 冗餘，但可在綁定紀錄之外獨立追溯裝置 |
| `report_type` | `TEXT` | 問卷類型。目前只有「透析前」一種 | 合法值目前僅 `PRE_DIALYSIS`（`SymptomReportType`）。保留欄位以便日後加透析中／後問卷 |
| `questionnaire_version` | `TEXT` | 填答時用的是哪一版題目。題目日後改版時，舊紀錄仍能對回當時的題目 | 現值 `PRE-DIALYSIS-v1`（`SYMPTOM_QUESTIONNAIRE_VERSION`）。⛔ **題目本身不進資料庫**，它是程式版本的一部分，放在 `@hd/shared` 常數。改題目時必須同時升版本號 |
| `source` | `TEXT` | 是即時送出的，還是離線暫存後補傳的。護理師看到一份「兩小時前填的」問卷時，需要知道它為什麼現在才到 | 合法值 `ONLINE` / `OFFLINE_SYNC`（`SymptomReportSource`） |
| `reported_at` | `TS` | **病人實際在平板上填寫的時間** | 由平板端提供。離線時會早於 `received_at`。臨床判讀應以此為準 |
| `received_at` | `TS` | **後端收到的時間** | `DEFAULT CURRENT_TIMESTAMP`。與 `reported_at` 刻意分開記錄，兩者皆供稽核。⛔ 不要用其中一個蓋掉另一個 |
| `note` | `TEXT?` | 病人自由補充的文字 | 自由文字，原樣記錄。⛔ 不做任何解析、分類或摘要推論 |
| `created_at` | `TS` | 紀錄寫入時間 | 見共通欄位 |

**索引**：`client_report_id`（唯一）、`(patient_id, reported_at)`、`treatment_session_id`、`device_binding_id`
**注意**：本表**沒有 `updated_at`** — 送出的問卷是事實紀錄，不修改。要更正就送新的一份。

---

### `symptom_answers` — 單題作答（6 欄）

**蒐集的意義**：一份問卷有 10 題，答案沒有塞進 JSON 欄位而是正規化成獨立的列（《資料庫使用規範》6.1）。好處是可以直接查「這位病人最近五次有幾次回報水腫」，而且換到任何資料庫都不需要處理 JSON 型別差異。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 這筆作答的內部識別碼 | 主鍵 |
| `symptom_report_id` | `TEXT` | 屬於哪一份問卷 | 外鍵 → `symptom_reports.id`，`ON DELETE CASCADE` |
| `item_code` | `TEXT` | 題目的識別字。10 題分別是水腫、喘、發燒、通路出血、通路紅腫痛、胸悶、頭暈、抽筋、噁心、皮膚癢 | 合法值取自 `PRE_DIALYSIS_SYMPTOM_QUESTIONS`：`EDEMA` `DYSPNEA` `FEVER` `ACCESS_BLEEDING` `ACCESS_ABNORMAL` `CHEST_DISCOMFORT` `DIZZINESS` `CRAMP` `NAUSEA` `ITCHING`。有索引。題目中文與白話說明查 `SYMPTOM_QUESTION_BY_CODE` |
| `answer_value` | `TEXT` | 病人選的答案。多數題目是四級（沒有／輕微／中等／嚴重），發燒與通路出血是二選一（沒有／有） | 合法值 `NONE` `MILD` `MODERATE` `SEVERE` `NO` `YES`（`SYMPTOM_ANSWER_VALUES`）。**量表由題目決定**：`SEVERITY` 題只能用前四個，`YES_NO` 題只能用後兩個，對照表在 `SYMPTOM_SCALE_OPTIONS` |
| `present` | `BOOL` | 病人是否表示「有這個症狀」。**這只是把答案原樣轉成是／否方便計數與顯示，不是嚴重度分級，也不是任何風險判斷** | 由 `SYMPTOM_PRESENT_VALUES`（`MILD` `MODERATE` `SEVERE` `YES`）機械式推導。⛔ **禁止**在此欄之上疊加任何加權、評分或門檻邏輯 — 那屬 FR-P03 風險分層，只能經由迭代 11 的規則引擎 |
| `created_at` | `TS` | 寫入時間 | 見共通欄位 |

**唯一約束**：`(symptom_report_id, item_code)` — 同一份問卷的同一題只能有一個答案。
**索引**：`item_code`（跨病人的單一症狀查詢用）
**注意**：無 `updated_at`，理由同 `symptom_reports`。

---

### `help_requests` — 求助按鈕與緊急通報（25 欄）

**蒐集的意義**：FR-P06（病人端求助）與 FR-N03（護理端緊急通報）是同一件事的兩端，因此共用同一筆紀錄，完整記錄從「病人按下」到「護理師處理完成」的生命週期。蒐集的重點包含**兩個時間戳的差**（按下 vs 收到）— 那是 SRS 第 6 章「五秒內送達」這條非功能需求的量測依據。

迭代 5 起，這筆紀錄的生命週期是**四段**而非三段：按下求助 → 確認通報 → 到達床邊 → 結案登記處理方式與結果（FR-N10）。中間兩段刻意分開記錄，理由見下方 `arrived_at`。

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
| `routed_to` | `TEXT` | 這筆通報被分派給誰：緊急處置團隊、護理師、或護佐。**分派結果會被記錄下來**，這樣事後查核時能看出當時套用的是哪一版規則 | 合法值 `EMERGENCY_TEAM` / `NURSE` / `NURSE_AIDE`（`HelpRequestRoute`）。由 `routeHelpRequest(category, severity)` 計算 — 那是一條**靜態規則**，輸入只有病人自選的兩個值，不讀歷史資料、不做趨勢推論，因此不屬於 FR-P03／FR-P05。⛔ 改規則要改 `@hd/shared` 那個函式，不要在各處寫死 |
| `status` | `TEXT` | 處理進度：待處理、已接收前往中、已處理完成、已取消 | 合法值 `PENDING` / `ACKNOWLEDGED` / `RESOLVED` / `CANCELLED`（`HelpRequestStatus`）。中文在 `HELP_REQUEST_STATUS_LABELS` |
| `message` | `TEXT?` | 病人自己打的補充說明 | 自由文字，原樣記錄。⛔ 不做語意分析或自動分類 |
| `raised_at` | `TS` | **病人按下按鈕的時間** | 由平板端提供 |
| `received_at` | `TS` | **後端收到的時間**。與上一欄相減就是實際延遲，這是驗證「五秒內送達」的原始資料 | `DEFAULT CURRENT_TIMESTAMP`。⛔ 兩個時間戳必須分開記錄，不可合併 |
| `acknowledged_by_id` | `TEXT?` | 哪一位護理師按下「我收到了，前往中」 | 外鍵 → `nurses.id`，`ON DELETE NO ACTION` |
| `acknowledged_at` | `TS?` | 接收的時間 | 與 `acknowledged_by_id` 同時寫入，並記 `HELP_REQUEST_ACKNOWLEDGED` 稽核 |
| `arrived_by_id` | `TEXT?` | 哪一位護理師在床邊登記「我到了」（迭代 5） | 外鍵 → `nurses.id`，`ON DELETE NO ACTION` |
| `arrived_at` | `TS?` | **到達床邊的時間**（迭代 5，FR-N10） | ⛔ **必須與 `acknowledged_at` 分開記錄，不可合併、不可互相填補。**兩者的差距是資料品質的檢查點：只記確認時間的話，一旦這個數字被拿去算績效，最省力的做法就會變成「先按確認再慢慢走過去」，指標就失去意義。分開記錄讓這種情況看得見。補登記時可回填，但不得早於 `raised_at`、不得晚於現在，且同一筆只能登記一次 |
| `handling_method_code` | `TEXT?` | 處理方式（迭代 5，FR-N10） | 值為 `help_resolution_options.code`（`kind=METHOD`）。⛔ 選項清單存在資料表、**不寫死在程式裡**——實際選項待護理部確認（Q-13） |
| `outcome_code` | `TEXT?` | 處理結果（迭代 5，FR-N10） | 值為 `help_resolution_options.code`（`kind=OUTCOME`） |
| `follow_up_required` | `BOOL` | 是否需後續追蹤（迭代 5，FR-N10） | 預設 `false`。為 `true` 時必定伴隨一筆 `help_request_follow_ups`，兩者同一個交易 |
| `resolved_by_id` | `TEXT?` | 哪一位護理師結案。可能與接收者不同人 | 外鍵 → `nurses.id`，`ON DELETE NO ACTION` |
| `resolved_at` | `TS?` | 結案時間 | 與 `resolved_by_id` 同時寫入，並記 `HELP_REQUEST_RESOLVED` 稽核 |
| `resolution_note` | `TEXT?` | 護理師填寫的補充說明 | 自由文字，**選填**。⛔ 這**不是**正式護理記錄——正式記錄在迭代 4 的 `nursing_records`。⛔ 迭代 5 起它也**不能單獨用來結案**：`handling_method_code`、`outcome_code`、`follow_up_required` 三欄缺一不可，只填這一欄會被擋下（FR-N10）。理由不是刁難忙碌的護理師，而是沒有結構化欄位，求助資料就只能拿來數件數，「哪一類處置最常見、哪一類最常無法處理」全都問不出來 |
| `created_at` | `TS` | 紀錄建立時間 | 見共通欄位 |
| `updated_at` | `TS` | 最後狀態變更時間 | 見共通欄位。本類三張表中**只有這張有** — 因為通報的狀態會隨處理流程改變 |

**索引**：`client_request_id`（唯一）、`(status, severity)`、`(patient_id, raised_at)`、`(patient_id, category, raised_at)`、`treatment_session_id`、`device_binding_id`
**`(patient_id, category, raised_at)` 是給 FR-N11 用的**：同一病人、同一類別、在設定期間內的前一次求助，通報畫面要顯示它當初的處理方式。期間長度取自 `operational_settings`，不寫死（暫定 72 小時，Q-13 第 6 題）。
**FR-P12**：結案後平板顯示「已處理」與簡短結果。⛔ 送到平板的只有處理方式與結果的**文字**，不含 `resolution_note`、不含護理師工作 ID——補充是寫給護理端看的，未必適合直接呈現在病床旁的畫面上。
**已知缺口**：`CANCELLED` 狀態沒有對應的 `cancelled_by_id` / `cancelled_at` 欄位，取消者只能從 `audit_logs` 的 `HELP_REQUEST_CANCELLED` 回查。

---

## 五、稽核軌跡

### `audit_logs` — 誰、何時、對誰、做了什麼（15 欄）

**蒐集的意義**：FR-S02，也是整份《資料庫使用規範》最在意的一張表。SRS 4.1 要求「存取授權可追溯到哪一位護理師、何時、為哪一位病人核准」，這張表就是那項要求真正被實現的地方。它同時被拿去算護理師績效（規範第 11 條），因此更不能開放修改或刪除。

它有兩個刻意的設計：**關聯欄位全部正規化為外鍵**（不用 JSON 欄位，符合 6.1），同時**冗餘記錄操作者標籤與平板序號的字串** — 因為帳號可能改名、平板可能報廢，若只留外鍵，多年後回查軌跡會失真。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 這筆軌跡的內部識別碼 | 主鍵 |
| `occurred_at` | `TS` | **事件發生的時間** | `DEFAULT CURRENT_TIMESTAMP`，有索引。本表沒有 `created_at`／`updated_at`，這一欄就是時間軸 |
| `actor_type` | `TEXT` | 動作是誰做的類型：護理人員、系統自動、或平板 | 合法值 `NURSE` / `SYSTEM` / `DEVICE`（`AuditActorType`）。逾時自動失效、每日排程備份這類事件是 `SYSTEM` |
| `actor_nurse_id` | `TEXT?` | 若是護理人員操作，是哪一位 | 外鍵 → `nurses.id`，`ON DELETE NO ACTION`，有索引。`actor_type` 非 `NURSE` 時為 NULL |
| `actor_label` | `TEXT` | **操作者當下的識別字串**，例如「N001（王小明）」。即使這個帳號日後改名或停用，軌跡上仍看得到當時是誰 | **必填**，冗餘欄位。實際格式：護理師 `工作ID（顯示名稱）`、系統 `SYSTEM`、平板 `平板 序號`（見 `audit.service.ts`）。⛔ 不要改成從 `nurses` join 出來 — 冗餘正是重點 |
| `action` | `TEXT` | 做了什麼動作，例如「裝置綁定」「登入失敗」「開啟功能開關」「資料庫線上備份」 | 合法值目前 **66 個**，全部定義在 `AuditAction`，中文對照在 `AUDIT_ACTION_LABELS`。迭代 3 新增 8 個：`FEATURE_FLAG_ENABLED` `FEATURE_FLAG_DISABLED` `FEATURE_FLAG_CHANGE_REJECTED` `DATABASE_BACKUP_CREATED` `CLINICAL_VALUES_IMPORTED` `CLINICAL_VALUES_IMPORT_REJECTED` `AI_INVOKED` `AI_INVOCATION_BLOCKED`。迭代 4 新增 12 個：`EDUCATION_CONTENT_REQUESTED` `EDUCATION_CONTENT_APPROVED` `EDUCATION_CONTENT_REJECTED` `EDUCATION_CONTENT_COMPLETED` `QUIZ_SUBMITTED` `FEEDBACK_SUBMITTED` `NURSING_RECORD_CREATED` `NURSING_RECORD_DRAFT_REQUESTED` `NURSING_RECORD_SIGNED` `ADEQUACY_CALCULATED` `SOP_QUERIED` `AI_JOB_FAILED`。迭代 5 新增 14 個：`HELP_REQUEST_ARRIVED` `HELP_FOLLOW_UP_CREATED` `HELP_FOLLOW_UP_CLOSED` `HELP_RESOLUTION_OPTION_UPDATED` `OPERATIONAL_SETTING_UPDATED` `NURSE_SHIFT_CREATED` `NURSE_SHIFT_CANCELLED` `NURSE_SHIFT_REJECTED_LABOUR_RULE` `NURSE_SHIFTS_IMPORTED` `NURSE_SHIFTS_IMPORT_REJECTED` `SHIFT_BEDS_ASSIGNED` `SHIFT_CHANGE_REQUESTED` `SHIFT_CHANGE_DECIDED` `BASELINE_MEASUREMENT_RECORDED`。其中 `NURSE_SHIFT_REJECTED_LABOUR_RULE` 與 `NURSE_SHIFTS_IMPORT_REJECTED` 記的是**被擋下的嘗試**，`outcome` 為 `FAILURE`——事後檢討「那週的班為什麼排不出來」時，看得到系統擋了幾次、擋的是哪一條。有索引。⛔ 新增功能時**必須**在 `@hd/shared` 補上識別字與中文標籤，不可直接寫死字串 |
| `target_type` | `TEXT?` | 這個動作作用在哪一種東西上，例如帳號、綁定紀錄、功能開關 | 實際使用的值：`'Nurse'`、`'DeviceBinding'`、`'FeatureFlag'`、`'BackupRun'`、`'ClinicalValueImport'`、`'AiInvocation'`，迭代 4 起另有 `'AiJob'`、`'EducationContent'`、`'QuizAttempt'`、`'FeedbackResponse'`、`'NursingRecord'`、`'AdequacyCalculation'`、`'SopQuery'`，迭代 5 起另有 `'HelpRequestFollowUp'`、`'HelpResolutionOption'`、`'OperationalSetting'`、`'NurseShift'`、`'NurseShiftImport'`、`'ShiftChangeRequest'`、`'BaselineMeasurement'` 等（模型名，PascalCase）。⚠️ **未以常數約束**，屬已知粗糙處 |
| `target_id` | `TEXT?` | 作用目標的識別碼 | 與 `target_type` 成對使用。刻意不設外鍵 — 目標可能跨多張表。功能開關的 `target_id` 是開關識別字（如 `AI_FEATURES`），不是 UUID |
| `patient_id` | `TEXT?` | **這個動作牽涉到哪一位病人**。SRS 4.1「為哪一位病人」對應的欄位 | 外鍵 → `patients.id`，`ON DELETE NO ACTION`，有索引。與病人無關的動作（如護理師登入）為 NULL |
| `device_id` | `TEXT?` | 牽涉到哪一台平板 | 外鍵 → `devices.id`，`ON DELETE NO ACTION` |
| `device_serial_no` | `TEXT?` | **平板序號的字串副本**。SRS 4.3 步驟 9 明列序號為必要稽核欄位，即使該平板日後報廢除役，軌跡仍須可讀 | 冗餘欄位，**有獨立索引**（實務上是靠序號查軌跡，不是靠 `device_id`）。有 `device_id` 時應同時填這欄 |
| `outcome` | `TEXT` | 成功還是失敗。**失敗也要記** — 連續的登入失敗、被擋掉的綁定、被拒的開關切換，本身就是要追查的訊號 | 合法值 `SUCCESS` / `FAILURE`（`AuditOutcome`）。⛔ 不要只在成功時寫稽核 |
| `detail` | `TEXT?` | 自由描述文字，補充上述欄位講不清楚的部分。功能開關切換時，**核准依據**就寫在這裡 | ⛔ **不承載結構化關聯資料**（6.1）。需要被查詢的資訊要開成正式欄位，不要塞進這裡。⛔ 不得出現資料庫或備份目錄的實際路徑（規範第 9 條） |
| `ip_address` | `TEXT?` | 操作來源 IP | 選填 |
| `user_agent` | `TEXT?` | 操作所用的瀏覽器／裝置 | 選填，原樣記錄 |

**索引**：`occurred_at`、`action`、`actor_nurse_id`、`patient_id`、`device_serial_no`

**寫入與查詢原則**：

- 所有外鍵都是 `ON DELETE NO ACTION` — **軌跡不因主檔異動而消失**
- 本表**只增不改不刪**，沒有 `updated_at` 是刻意的
- 稽核寫入與即時廣播是**平行**進行的（見技術報告第 8 章），不要改成依序等待
- 查詢走 `query_only` 的唯讀連線，不佔用臨床寫入（規範 7.1）

---

## 六、系統治理（迭代 3）

這三張表記錄的是「系統本身的狀態與行為」，不是臨床資料。它們共同的原則：**只增、只標記，不刪除**——留存期限未由醫院定案前（Q-05），一律不做實際刪除（規範 8.2）。

### `feature_flags` — 功能開關目前狀態（7 欄）

**蒐集的意義**：FR-S08。三項高風險功能、AI 功能、輪播三層、個人層級績效，都要能獨立開關，而且**預設全關**。這張表只存每個開關「現在開著還是關著、最後一次是誰依什麼理由切換的」；每一次切換的完整歷程連同核准依據，一律寫進 `audit_logs`。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 內部識別碼 | 主鍵 |
| `flag_key` | `TEXT` UNIQUE | 開關的識別字，例如「AI 輔助功能總開關」 | 合法值見 `@hd/shared` 的 `FeatureFlagKey`：`RISK_STRATIFICATION` `INTRA_DIALYSIS_ALERT` `DOSE_REFERENCE` `AI_FEATURES` `REAL_PATIENT_DATA_TO_AI` `CAROUSEL_LAYER_1` `CAROUSEL_LAYER_2` `CAROUSEL_LAYER_3` `PERF_INDIVIDUAL_L3` `REWARD_SCORING`。後端啟動時自動補齊缺少的列，一律為關閉 |
| `enabled` | `BOOL` | 目前是否開啟 | `DEFAULT false`。⛔ **不得直接改資料庫開啟**——開啟必須經 `FeatureFlagsService`：它會判定開啟條件（實作規格書 3.7）、要求核准依據、寫入稽核。後端以記憶體中的狀態為準，直接改資料庫在重新啟動前也不會生效 |
| `last_reason` | `TEXT?` | 最後一次切換時登記的核准依據或理由 | 開與關都必填（FR-S08、FR-M11），長度 2～500 字 |
| `changed_by_id` | `TEXT?` | 最後一次是誰切換的 | 外鍵 → `nurses.id`，`ON DELETE NO ACTION`。從未切換過時為 NULL |
| `changed_at` | `TS?` | 最後一次切換的時間 | 從未切換過時為 NULL，藉此與「系統建立的預設值」區分 |
| `created_at` | `TS` | 這個開關列被建立的時間 | 見共通欄位 |

**唯一約束**：`flag_key`
**與功能的關係**：開關關閉時，相關介面元素完全不出現，後端端點以 `@RequireFeatureFlag()` 回應 404。

---

### `ai_invocations` — AI 呼叫紀錄（20 欄）

**蒐集的意義**：實作規格書 3.4 第 5 點、規範第 14 條。每一次經 `LlmProviderPort` 呼叫模型——不論成功、失敗、還是因為帶了真實病人資料而被擋下——都留一列。這批紀錄是三件事的依據：事後查核「當時系統對護理師說了什麼」、治理證據（有沒有去識別化、有沒有擋下）、成效與成本分析。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 內部識別碼 | 主鍵 |
| `invoked_at` | `TS` | 呼叫時間 | `DEFAULT CURRENT_TIMESTAMP`，有索引 |
| `provider` | `TEXT` | 用的是哪一種模型供應者：模擬、實驗室 API、院內推論 | 合法值 `mock` / `lab` / `onprem`（`LlmProviderId`）。與 `outcome` 組成複合索引 |
| `model_id` | `TEXT?` | 用的是哪一個模型 | 以推論端點實際回報的為準；經 AI 閘道時就是閘道 `config.yaml` 的那一個（後端 `LLM_MODEL_ID` 留空，迭代 13）。被擋下的請求沒有送出，此欄可能為空。⛔ 模型名稱只由設定提供，不寫在程式裡 |
| `purpose` | `TEXT` | 哪一項功能發起的呼叫 | 合法值見 `AiPurpose`：`CONNECTIVITY_TEST`（迭代 3 的連線測試）；迭代 4 的 `EDUCATION_CONTENT`（個人化衛教）、`DISCHARGE_SUMMARY`（離院衛教重點）、`NURSING_RECORD_DRAFT`（護理記錄草擬）、`SOP_ANSWER`（SOP 查詢回答）。每項 AI 功能各登記一個，新增功能時在 `@hd/shared` 補上 |
| `max_output_tokens` | `INT?` | 輸出長度上限 | 呼叫參數逐項成欄，不以 JSON 承載（6.1） |
| `temperature_permille` | `INT?` | 取樣溫度 | 以千分位整數記錄（200 代表 0.2），不用浮點數 |
| `reasoning_effort` | `TEXT?` | 思考程度 | `low` / `medium` / `high` |
| `outcome` | `TEXT` | 結果：成功、失敗、已擋下 | 合法值 `SUCCESS` / `FAILURE` / `BLOCKED`（`AiInvocationOutcome`） |
| `block_reason` | `TEXT?` | 被擋下的原因 | 合法值 `LAB_PROVIDER_REAL_DATA`（供應者在院外）/ `REAL_DATA_NOT_ALLOWED`（開關未開），見 `AiBlockReason` |
| `duration_ms` | `INT?` | 耗時（毫秒） | 被擋下時為 NULL |
| `deidentified` | `BOOL` | 送出前是否實際移除了可識別資訊 | `DEFAULT false`。治理證據，**永久保留** |
| `redaction_count` | `INT` | 移除了幾處可識別資訊 | `DEFAULT 0` |
| `contains_real_patient_data` | `BOOL` | 這次請求是否帶有真實病人資料 | 呼叫端宣告**或**系統依病歷號判定（無法證明是合成資料即為真實）。為 true 且供應者在院外時一律擋下 |
| `prompt_text` | `TEXT?` | 送給模型的提示，**已去識別化** | ⛔ **原始提示從不寫入資料庫**，去識別化在寫入之前完成（第 14 條）。被擋下的請求此欄為 NULL |
| `output_text` | `TEXT?` | 模型回傳的內容 | 失敗或被擋下時為 NULL |
| `error_message` | `TEXT?` | 失敗原因 | 不含推論伺服器的回應原文，避免夾帶提示內容 |
| `content_expires_at` | `TS` | 提示與輸出內容的留存到期日 | 呼叫時設為 12 個月後（規範 8.2 建議值）。**期限未定案前只標記、不實際刪除** |
| `actor_nurse_id` | `TEXT?` | 誰發起的 | 外鍵 → `nurses.id`，`ON DELETE NO ACTION` |
| `patient_id` | `TEXT?` | 與哪一位病人相關 | 外鍵 → `patients.id`，`ON DELETE NO ACTION`，有索引 |

**索引**：`invoked_at`、`(provider, outcome)`、`patient_id`
**查詢**：走唯讀連線。稽核角色可讀（實作規格書 3.1）。
**被參照**（迭代 4）：`ai_jobs`、`education_contents`、`nursing_records`、`sop_queries` 的 `ai_invocation_id`——每一段 AI 產出都能由此追到發出它的那一次呼叫（實作規格書 4.2）。

---

### `backup_runs` — 備份歷程（11 欄）

**蒐集的意義**：FR-S09、規範第 8 條。SQLite 是單一檔案，壞了就全壞；「有沒有備份、多久沒備份、備份檔有沒有被動過」必須看得見。每一次線上備份（手動或每日排程）一列。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 內部識別碼 | 主鍵 |
| `trigger` | `TEXT` | 手動觸發、每日排程，或版本更新前的強制備份 | 合法值 `MANUAL` / `SCHEDULED` / `BEFORE_UPDATE`（`BackupTrigger`）。第三種於迭代 7 新增，由更新腳本觸發（規範 18.1 第一關） |
| `status` | `TEXT` | 進行中、成功、失敗 | 合法值 `RUNNING` / `SUCCEEDED` / `FAILED`（`BackupRunStatus`）。服務在備份途中停止留下的 `RUNNING` 列，啟動時會收斂為 `FAILED` |
| `started_at` | `TS` | 開始時間 | `DEFAULT CURRENT_TIMESTAMP`，有索引 |
| `finished_at` | `TS?` | 結束時間 | |
| `duration_ms` | `INT?` | 耗時（毫秒） | |
| `file_name` | `TEXT` | 備份檔名 | ⛔ **只記檔名**，目錄由伺服器設定 `BACKUP_DIR` 決定，完整路徑不寫進資料庫（第 9 條） |
| `file_size_bytes` | `BIGINT?` | 備份檔大小 | |
| `sha256` | `TEXT?` | 備份檔的雜湊值。還原前拿來比對，確認檔案沒有損毀或被更動 | 還原腳本 `npm run db:restore -- --sha256` 會比對這個值 |
| `error_message` | `TEXT?` | 失敗原因 | 已把資料庫與備份目錄的實際路徑換成設定名稱 |
| `initiated_by_id` | `TEXT?` | 誰觸發的 | 外鍵 → `nurses.id`，`ON DELETE NO ACTION`。排程備份為 NULL |

**索引**：`started_at`
**注意**：備份一律用 `VACUUM INTO`，不直接複製資料庫檔案。舊備份不自動刪除，留存世代數待醫院定案（Q-05）。

---

## 七、院方臨床數值（迭代 3）

FR-S05。院方尚未確定給 API 還是 Excel（Q-09），因此先立 `ClinicalDataSourcePort` 介面層：人工輸入、檔案匯入、院方 API 三種來源**共用同一組內部資料表**，輪播與儀表板只讀這兩張表、不認來源。迭代 3 只有人工輸入（`ManualEntryAdapter`）。

**三條硬性規則**（實作規格書 3.5、規範第 13 條）：

- **全有或全無** — 一批之中任何一筆不合格，整批不寫入，只留一筆 `CLINICAL_VALUES_IMPORT_REJECTED` 稽核並逐列回報原因
- **每筆都有資料時間** — 呈現時必須一併顯示，避免病人看到三週前的體重以為是今天的
- **重複要擋下或明確覆蓋** — 同病人、同種數值、同資料時間已有值時預設擋下；明確勾選覆蓋時，舊值保留並指向新值

### `clinical_value_imports` — 匯入批次（8 欄）

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 內部識別碼 | 主鍵 |
| `batch_no` | `TEXT` UNIQUE | 人可讀的批次編號，例如 `CV-20260910-110540-3F2A` | UTC 時間加隨機碼，由應用層產生 |
| `source_type` | `TEXT` | 來源種類：人工輸入、檔案匯入、院方 API | 合法值 `MANUAL_ENTRY` / `FILE_IMPORT` / `HOSPITAL_API`（`ClinicalValueSourceType`） |
| `source_label` | `TEXT` | 來源描述：檔名或端點 | 人工輸入為固定字樣「護理端人工輸入」 |
| `content_hash` | `TEXT?` | 來源內容的雜湊，用來偵測同一份檔案重複匯入 | SHA-256。人工輸入為 NULL。有索引 |
| `row_count` | `INT` | 這批有幾筆 | 單批上限 200 筆（`CLINICAL_BATCH_MAX_ROWS`） |
| `imported_by_id` | `TEXT` | 誰匯入的 | 外鍵 → `nurses.id`，`ON DELETE NO ACTION` |
| `imported_at` | `TS` | 匯入時間 | `DEFAULT CURRENT_TIMESTAMP`，有索引 |

**注意**：被拒的批次**不會出現在這張表**——它們一筆都沒寫入。

### `clinical_values` — 臨床數值（11 欄）

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 內部識別碼 | 主鍵。由應用層先產生，才能在同一個交易裡把舊值指向新值 |
| `import_id` | `TEXT` | 屬於哪一批匯入 | 外鍵 → `clinical_value_imports.id`，`ON DELETE NO ACTION`。有索引 |
| `patient_id` | `TEXT` | 哪一位病人的數值 | 外鍵 → `patients.id`，`ON DELETE NO ACTION`。與 `value_code`、`measured_at` 組成複合索引 |
| `value_code` | `TEXT` | 數值種類：乾體重、本次超過濾目標、血紅素、白蛋白、Kt/V；迭代 4 另加透析適足性計算的五個輸入值 | 合法值見 `CLINICAL_VALUE_DEFINITIONS`：`DRY_WEIGHT` `UF_TARGET` `HEMOGLOBIN` `ALBUMIN` `KT_V`（輪播第三層，實際種類待院方確認，Q-09）；`BUN_PRE` `BUN_POST` `WEIGHT_POST` `UF_VOLUME` `SESSION_MINUTES`（迭代 4，FR-N07 的輸入，Q-26） |
| `value_scaled` | `INT` | 數值本身 | ⛔ **不用浮點數**（規範 6.2）。以整數記錄、搭配下一欄的小數位數：乾體重 62.5 kg 存為 `625`。十進位字串與整數的轉換用 `parseScaledDecimal` / `formatScaledDecimal`，全程字串運算 |
| `value_scale` | `INT` | 小數位數 | 乾體重 1、超過濾目標 0、Kt/V 2。逐列記錄，種類定義日後改變也不影響舊資料的解讀 |
| `unit` | `TEXT` | 單位 | 如 `kg`、`mL`、`g/dL`；Kt/V 無單位時為空字串 |
| `measured_at` | `TS` | **資料時間**：這個數值是什麼時候量的 | 必填，不得晚於現在。⛔ 呈現時必須一併顯示 |
| `superseded_by_id` | `TEXT?` | 若已被更正，指向取代它的那一列 | 自關聯外鍵 → `clinical_values.id`，`ON DELETE NO ACTION`。現行值為 NULL。**舊值保留不刪** |
| `superseded_at` | `TS?` | 被覆蓋的時間 | 與 `superseded_by_id` 同時寫入 |
| `created_at` | `TS` | 寫入時間（輸入時間） | 見共通欄位。與 `measured_at` 刻意分開 |

**索引**：`(patient_id, value_code, measured_at)`、`import_id`
**格式防呆的上下限**（`minScaled` / `maxScaled`）只用來擋漏打小數點這類輸入錯誤，**不是臨床判斷門檻**——門檻值屬 FR-R02，必須由臨床端書面提供。

---

## 八、背景佇列（迭代 4）

### `ai_jobs` — 生成類 AI 工作（12 欄）

**蒐集的意義**：實作規格書 3.4 第 6 點。衛教生成、記錄草擬這類「可以等」的工作不得阻擋 HTTP 請求，也不得在資料庫交易裡等模型回應——那會佔住 SQLite 唯一的寫入位置。這張表就是那條佇列：護理師按下「產生」時只排入一列、立刻回應；後端依序處理，前端依這一列的狀態顯示「排隊中第幾位／產生中／完成／失敗」。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 工作的內部識別碼 | 主鍵。前端以 `GET /api/ai-jobs/:id` 查進度 |
| `job_type` | `TEXT` | 什麼工作：產生個人化衛教、產生離院衛教重點、草擬護理記錄 | 合法值 `EDUCATION_CONTENT` / `DISCHARGE_SUMMARY` / `NURSING_RECORD_DRAFT`（`AiJobType`）。各功能模組在啟動時向 `AiJobQueueService` 登記自己的處理程式 |
| `status` | `TEXT` | 排隊中、產生中、已完成、失敗 | 合法值 `QUEUED` / `RUNNING` / `SUCCEEDED` / `FAILED`（`AiJobStatus`），與 `queued_at` 組成複合索引。只有 `QUEUED` 能被改成 `RUNNING`（條件式更新），同一件不會被處理兩次。後端重新啟動時仍為 `RUNNING` 的工作一律收斂為 `FAILED` |
| `target_type` | `TEXT` | 工作結果要寫回哪一種資料 | `EducationContent` 或 `NursingRecord`（模型名）。比照 `audit_logs` 的寫法，刻意不設外鍵 |
| `target_id` | `TEXT` | 要寫回的那一列 | 與 `target_type` 組成複合索引，用來找「這筆記錄最近一次的工作」 |
| `patient_id` | `TEXT?` | 與哪位病人相關 | 外鍵 → `patients.id`，`ON DELETE NO ACTION` |
| `requested_by_id` | `TEXT` | 誰按下產生的 | 外鍵 → `nurses.id`，`ON DELETE NO ACTION`。背景執行時發出的模型呼叫也記在這個人名下 |
| `ai_invocation_id` | `TEXT?` | 這件工作實際發出的那一次模型呼叫 | 外鍵 → `ai_invocations.id`，`ON DELETE NO ACTION`。被擋下或呼叫失敗時同樣有值；開關已關閉這類根本沒送出的情況為 NULL |
| `error_message` | `TEXT?` | 失敗原因 | 例如「允許真實病人資料進入 AI 流程」開關未開啟、後端重新啟動而中斷。上限 500 字 |
| `queued_at` | `TS` | 排入時間 | 排隊順位依此排序 |
| `started_at` | `TS?` | 開始處理的時間 | |
| `finished_at` | `TS?` | 完成或失敗的時間 | 驗收腳本以「下一件的 `started_at` 不早於上一件的 `finished_at`」確認工作依序處理 |

**索引**：`(status, queued_at)`、`(target_type, target_id)`
**注意**：沒有 `created_at`／`updated_at`，三個時間欄位就是完整的生命週期。失敗的工作另寫一筆 `AI_JOB_FAILED` 稽核。

---

## 九、衛教、測驗與病人回饋（迭代 4）

> ⚠️ **AI 產生的衛教內容「先審後給」**：護理師核可前，病人端看不到（Q-06 第 5 題確認前的暫代做法）。AI 總開關關閉時，已核可的 AI 內容也一併從病人端消失。測驗出題、對錯判定、知識點狀態、心理社會的趨勢比對都是固定規則，**不經模型**，比對結果也**不寫入任何資料表**。

### `education_contents` — AI 衛教內容（16 欄）

**蒐集的意義**：FR-P04 個人化衛教與 FR-P07 離院衛教重點。記下「為誰、依什麼主題、用什麼語言產生、誰審閱核可」——病人端看到的每一段 AI 文字，都能追到產生它的那一次呼叫與核可它的那一位護理師。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 內部識別碼 | 主鍵 |
| `patient_id` | `TEXT` | 給哪一位病人 | 外鍵 → `patients.id`，`ON DELETE NO ACTION`。與 `status` 組成複合索引 |
| `content_type` | `TEXT` | 個人化衛教，或這次療程的離院衛教重點 | 合法值 `PERSONALIZED` / `DISCHARGE_SUMMARY`（`EducationContentType`） |
| `topic_code` | `TEXT?` | 衛教主題（知識點），例如「水分與體重控制」 | 合法值見 `EDUCATION_TOPICS`：`FLUID_CONTROL` `DIET_POTASSIUM` `DIET_PHOSPHORUS` `ACCESS_CARE` `INTRADIALYTIC_DISCOMFORT` `MEDICATION`（版本 `EDU-TOPICS-v1`，待護理部審閱，Q-23）。離院衛教重點為 NULL |
| `treatment_session_id` | `TEXT?` | 離院衛教重點屬於哪一次療程 | 外鍵 → `treatment_sessions.id`，`ON DELETE NO ACTION`，有索引。病人端只看得到「本次療程」的離院重點 |
| `language` | `TEXT` | 內容語言 | BCP 47 標籤，合法值見 `EDUCATION_LANGUAGES`：`zh-TW` / `en` / `vi` / `id`。平板介面本身維持繁體中文 |
| `title` | `TEXT` | 標題 | 個人化衛教取主題名稱；離院重點為「今天回家要注意的事（日期）」 |
| `body_text` | `TEXT?` | 模型產生的內文 | 產生中或失敗時為 NULL。只有 `GENERATING` 狀態會被寫入（條件式更新） |
| `status` | `TEXT` | 產生中、待審閱、已核可、已退回、產生失敗 | 合法值 `GENERATING` / `PENDING_REVIEW` / `APPROVED` / `REJECTED` / `FAILED`（`EducationContentStatus`）。**只有 `APPROVED` 會出現在病人端**。審閱只能由 `PENDING_REVIEW` 轉出，兩人同時審閱只有一人成功 |
| `ai_invocation_id` | `TEXT?` | 產生這段文字的那一次模型呼叫 | 外鍵 → `ai_invocations.id`，`ON DELETE NO ACTION` |
| `requested_by_id` | `TEXT` | 誰要求產生 | 外鍵 → `nurses.id`，`ON DELETE NO ACTION` |
| `reviewed_by_id` | `TEXT?` | 誰核可或退回 | 外鍵 → `nurses.id`，`ON DELETE NO ACTION` |
| `reviewed_at` | `TS?` | 審閱時間 | |
| `review_note` | `TEXT?` | 審閱備註 | 退回時必填，上限 300 字 |
| `created_at` | `TS` | 要求產生的時間 | 見共通欄位 |
| `updated_at` | `TS` | 最後一次狀態變更 | 見共通欄位 |

**索引**：`(patient_id, status)`、`treatment_session_id`

---

### `education_completions` — 衛教完成紀錄（5 欄）

**蒐集的意義**：SRS 4.2「衛教完成度」。病人在平板上讀完一份內容、按下「我看完了」。這是個人化衛教「依衛教完成紀錄動態生成」的依據之一，也讓護理師知道哪些內容病人真的看過。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 內部識別碼 | 主鍵 |
| `education_content_id` | `TEXT` | 讀完哪一份 | 外鍵 → `education_contents.id`，`ON DELETE NO ACTION` |
| `patient_id` | `TEXT` | 哪位病人 | 外鍵 → `patients.id`，`ON DELETE NO ACTION`。與 `completed_at` 組成複合索引 |
| `device_binding_id` | `TEXT` | 在哪一次綁定讀完 | 外鍵 → `device_bindings.id`，`ON DELETE NO ACTION`。平板只能對本次綁定看得到的內容送出 |
| `completed_at` | `TS` | 讀完的時間 | `DEFAULT CURRENT_TIMESTAMP` |

**唯一約束**：`(education_content_id, device_binding_id)` — 同一次綁定重複按只記一次。

---

### `quiz_attempts` — 適性測驗作答（9 欄）

**蒐集的意義**：FR-P07「適性測驗，標記需加強衛教之知識點」。一次作答一列，答案逐題存在 `quiz_answers`。題目本身在 `@hd/shared` 的題庫常數（`QUIZ_QUESTIONS`，版本 `EDU-QUIZ-v1`，待護理部審閱，Q-23），比照症狀問卷的做法：題目是程式版本的一部分，紀錄只存版本號。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 內部識別碼 | 主鍵 |
| `client_attempt_id` | `TEXT` UNIQUE | 平板產生的識別碼 | 重送同一次作答時以此去重，回傳既有紀錄並標記 `duplicate` |
| `patient_id` | `TEXT` | 哪位病人 | 外鍵 → `patients.id`，`ON DELETE NO ACTION`。與 `submitted_at` 組成複合索引 |
| `treatment_session_id` | `TEXT` | 在哪一次療程作答 | 外鍵 → `treatment_sessions.id`，`ON DELETE NO ACTION` |
| `device_binding_id` | `TEXT` | 透過哪一次綁定送出 | 外鍵 → `device_bindings.id`，`ON DELETE NO ACTION` |
| `question_bank_version` | `TEXT` | 當時用的題庫版本 | 現值 `EDU-QUIZ-v1`（`QUIZ_BANK_VERSION`）。版本不符時拒收 |
| `question_count` | `INT` | 這次作答幾題 | 通常 5 題（`QUIZ_QUESTION_COUNT`） |
| `correct_count` | `INT` | 答對幾題 | 由後端依題庫計算。**這是病人自己的作答結果，不是對病人的評分，也不給任何人排名** |
| `submitted_at` | `TS` | 送出時間 | `DEFAULT CURRENT_TIMESTAMP` |

**索引**：`client_attempt_id`（唯一）、`(patient_id, submitted_at)`

---

### `quiz_answers` — 單題作答（6 欄）

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 內部識別碼 | 主鍵 |
| `attempt_id` | `TEXT` | 屬於哪一次作答 | 外鍵 → `quiz_attempts.id`，**`ON DELETE CASCADE`**（本表唯一的級聯） |
| `question_code` | `TEXT` | 哪一題 | 合法值見 `QUIZ_QUESTIONS`（`FLUID-01`、`K-01`、`ACCESS-02` 等 12 題） |
| `topic_code` | `TEXT` | 這一題屬於哪個衛教主題 | 冗餘保留：題庫改版後仍能還原當時考的是哪個知識點。有索引 |
| `selected_option` | `TEXT` | 病人選了哪個選項 | `A` / `B` / `C` |
| `correct` | `BOOL` | 答對了沒有 | ⛔ **由後端依題庫判定，不接受平板送上來的對錯** |

**唯一約束**：`(attempt_id, question_code)`
**知識點狀態不入庫**：「需加強／已掌握／尚未測驗」是查詢時由每一題最近一次的作答即時整理（同主題任何一題最近答錯即為需加強），不另存欄位。

---

### `feedback_responses` — 情緒／滿意度回饋（9 欄）

**蒐集的意義**：FR-P08。病人在平板上填 5 題（心情、睡眠、有人可以幫忙或聊天、對照護與環境的滿意度），分數 1～5 越高越好。護理端以此彙整心理社會趨勢（FR-N08）。**病人看不到任何比對結果。**

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 內部識別碼 | 主鍵 |
| `client_response_id` | `TEXT` UNIQUE | 平板產生的識別碼 | 重送時以此去重 |
| `patient_id` | `TEXT` | 哪位病人 | 外鍵 → `patients.id`，`ON DELETE NO ACTION`。與 `responded_at` 組成複合索引 |
| `treatment_session_id` | `TEXT` UNIQUE | 在哪一次療程填的 | 外鍵 → `treatment_sessions.id`，`ON DELETE NO ACTION`。**每次療程最多一份**，避免同一天重複填寫拉偏趨勢；第二份回 409 |
| `device_binding_id` | `TEXT` | 透過哪一次綁定送出 | 外鍵 → `device_bindings.id`，`ON DELETE NO ACTION` |
| `questionnaire_version` | `TEXT` | 題目版本 | 現值 `FEEDBACK-v1`（`FEEDBACK_QUESTIONNAIRE_VERSION`），題目待 Q-24 確認 |
| `responded_at` | `TS` | 病人在平板上填寫的時間 | 平板時間明顯超前伺服器時間時夾回現在，與症狀回報的做法一致 |
| `received_at` | `TS` | 後端收到的時間 | `DEFAULT CURRENT_TIMESTAMP` |
| `comment` | `TEXT?` | 病人寫的文字意見 | 自由文字，原樣記錄，上限 500 字。⛔ 不做語意分析或自動分類 |

**唯一約束**：`client_response_id`、`treatment_session_id`

---

### `feedback_answers` — 單題分數（4 欄）

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 內部識別碼 | 主鍵 |
| `response_id` | `TEXT` | 屬於哪一份回饋 | 外鍵 → `feedback_responses.id`，**`ON DELETE CASCADE`**（本表唯一的級聯） |
| `item_code` | `TEXT` | 哪一題 | 合法值見 `FEEDBACK_ITEMS`：`MOOD` `SLEEP` `SUPPORT`（情緒相關）、`CARE` `ENVIRONMENT`（滿意度） |
| `score` | `INT` | 分數 | 1～5，越高越好，由 DTO 把關 |

**唯一約束**：`(response_id, item_code)`
**趨勢比對不入庫**：暫定規則 `PSY-DEV-v1`（近 3 次情緒相關平均比先前最多 6 次低 1.0 分以上即列出，至少 6 份才套用，Q-24）在查詢時即時計算，結果只以事實陳述呈現給護理師，不寫入任何資料表，也不自動觸發轉介。平均分數以十分位整數計算，不用浮點數。

---

## 十、護理記錄與計算（迭代 4）

### `nursing_records` — 護理記錄（20 欄）

**蒐集的意義**：FR-N04 事件記錄快速範本、FR-N05 依病人自報預填。每筆記錄一建立就有一份「預填文字」（依勾選內容或病人自述組出，不經模型）；AI 初稿是另一個起點；**護理師簽核的定稿才是正式記錄**。記下「是否採納 AI 初稿」是《資料庫使用規範》第 14 條要求永久保留的治理證據。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 內部識別碼 | 主鍵 |
| `patient_id` | `TEXT` | 哪位病人 | 外鍵 → `patients.id`，`ON DELETE NO ACTION`。與 `created_at` 組成複合索引 |
| `treatment_session_id` | `TEXT` | 哪一次療程 | 外鍵 → `treatment_sessions.id`，`ON DELETE NO ACTION`，有索引。已取消的療程不能建立記錄 |
| `record_type` | `TEXT` | 事件記錄，或依病人自報預填 | 合法值 `EVENT` / `SELF_REPORT_PREFILL`（`NursingRecordType`） |
| `template_code` | `TEXT?` | 用了哪一個事件範本 | 合法值見 `NURSING_EVENT_TEMPLATES`：`DISCOMFORT` `ACCESS_BLEEDING` `MACHINE_ALARM` `FALL` `OTHER`（待 Q-25）。自報預填為 NULL |
| `template_version` | `TEXT?` | 範本版本 | 現值 `EVENT-TEMPLATES-v1`。範本改版後舊記錄仍能對回當時的欄位 |
| `occurred_at` | `TS?` | 事件發生時間 | 事件記錄必填，不得晚於現在（容許 5 分鐘時鐘誤差） |
| `source_symptom_report_id` | `TEXT?` | 預填所依據的那一份病人自報 | 外鍵 → `symptom_reports.id`，`ON DELETE NO ACTION` |
| `supplement_text` | `TEXT?` | 護理師補充的自由文字 | 上限 500 字，不取代結構化欄位；「其他事件」範本必填。送進模型前由閘道去識別化 |
| `prefill_text` | `TEXT` | 依勾選內容或病人自述組出的預填文字 | ⛔ **不經模型**。AI 總開關關閉時，護理師照樣可以從這段文字改起並簽核 |
| `ai_draft_text` | `TEXT?` | AI 草擬的初稿 | 只有 `DRAFT` 狀態會被寫入。AI 總開關關閉時畫面不顯示 |
| `ai_invocation_id` | `TEXT?` | 產生初稿的那一次模型呼叫 | 外鍵 → `ai_invocations.id`，`ON DELETE NO ACTION` |
| `status` | `TEXT` | 草稿或已簽核 | 合法值 `DRAFT` / `SIGNED`（`NursingRecordStatus`）。⛔ **簽核後不得再修改**：所有寫入都帶 `status=DRAFT` 條件，第二次簽核與簽核後的草擬一律回 409 |
| `final_text` | `TEXT?` | 簽核的定稿 | 上限 4000 字 |
| `ai_draft_disposition` | `TEXT?` | 是否採納 AI 初稿 | 合法值 `ADOPTED_AS_IS` / `EDITED` / `NOT_USED`（`AiDraftDisposition`），簽核時依起點與內容判定：從 AI 初稿改起且一字未改＝原樣採用；從 AI 初稿改起有修改＝修改後採用；從預填文字或自行撰寫＝未採用。簽核時沒有 AI 初稿為 NULL |
| `created_by_id` | `TEXT` | 誰建立的 | 外鍵 → `nurses.id`，`ON DELETE NO ACTION` |
| `signed_by_id` | `TEXT?` | 誰簽核的 | 外鍵 → `nurses.id`，`ON DELETE NO ACTION` |
| `signed_at` | `TS?` | 簽核時間 | |
| `created_at` | `TS` | 建立時間 | 見共通欄位 |
| `updated_at` | `TS` | 最後修改時間 | 見共通欄位 |

**索引**：`(patient_id, created_at)`、`treatment_session_id`

---

### `nursing_record_fields` — 快速範本的勾選內容（4 欄）

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 內部識別碼 | 主鍵 |
| `record_id` | `TEXT` | 屬於哪一筆記錄 | 外鍵 → `nursing_records.id`，**`ON DELETE CASCADE`**（本表唯一的級聯） |
| `field_code` | `TEXT` | 範本裡的哪一個欄位，例如「病人表現」「處置」 | 範本欄位代號（`SYMPTOMS`、`ACTIONS`、`OUTCOME` 等） |
| `option_code` | `TEXT` | 勾了哪一個選項 | 選項代號。單選欄位最多一列，必填欄位至少一列，由應用層把關 |

**唯一約束**：`(record_id, field_code, option_code)` — 一個選項一列，不以 JSON 承載（6.1）。欄位與選項的中文在 `@hd/shared` 的範本常數，紀錄只存代號加上範本版本。

---

### `adequacy_calculations` — 透析適足性計算結果（13 欄）

**蒐集的意義**：FR-N07。依院方提供（或人工輸入）的五個數值計算 URR 與 spKt/V。計算本身是公式（Daugirdas 第二代單池公式，Q-26 待確認），**不含任何判讀**；本迭代只畫趨勢，不預測（預測於迭代 11 併入規則引擎）。每一個結果都指回五筆原始數值，事後可追溯。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 內部識別碼 | 主鍵 |
| `patient_id` | `TEXT` | 哪位病人 | 外鍵 → `patients.id`，`ON DELETE NO ACTION`。與 `measured_at` 組成複合索引 |
| `formula_version` | `TEXT` | 用哪一版公式 | 現值 `DAUGIRDAS2-SPKTV-v1`。換公式時新結果用新版本，舊結果不改 |
| `measured_at` | `TS` | 這次療程的資料時間 | 取透析後 BUN 的資料時間 |
| `urr_tenths` | `INT` | 尿素下降率 URR | ⛔ 不用浮點數：68.4% 存 `684` |
| `kt_v_hundredths` | `INT` | spKt/V | 1.35 存 `135`。計算的當下才轉成數值，結果立刻四捨五入回整數 |
| `bun_pre_value_id` | `TEXT` | 用了哪一筆透析前 BUN | 外鍵 → `clinical_values.id`，`ON DELETE NO ACTION` |
| `bun_post_value_id` | `TEXT` | 用了哪一筆透析後 BUN | 同上 |
| `weight_post_value_id` | `TEXT` | 用了哪一筆透析後體重 | 同上 |
| `uf_volume_value_id` | `TEXT` | 用了哪一筆實際脫水量 | 同上 |
| `session_minutes_value_id` | `TEXT` | 用了哪一筆透析時間 | 同上。五筆必須是同一位病人、對應的數值種類、現行版本，且資料時間相差不超過 12 小時（`ADEQUACY_MAX_SPAN_HOURS`） |
| `calculated_by_id` | `TEXT` | 誰按下計算 | 外鍵 → `nurses.id`，`ON DELETE NO ACTION`。權限與臨床數值輸入相同（護理長以上） |
| `calculated_at` | `TS` | 計算時間 | `DEFAULT CURRENT_TIMESTAMP` |

**唯一約束**：五個輸入值的組合 — 同一組數值只算一次。
**輸入值被更正時**：舊結果保留；API 以「輸入值已被覆蓋」標示需重新確認，不自動重算。

---

## 十一、SOP 文件與查詢（迭代 4）

FR-N09 只能在收錄的文件範圍內回答，並標出原文出處。開發階段只有 4 份**標示為虛構**的範例文件（由 `db:seed` 建立；醫院真實文件待 Q-17）。檢索用字詞比對；**檢索不到就直接回答查無資料，不呼叫模型**，模型沒有機會在文件範圍外自行補寫。

### `sop_documents` — 查詢範圍內的文件（8 欄）

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 內部識別碼 | 主鍵 |
| `doc_code` | `TEXT` UNIQUE | 文件編號，例如 `SOP-HD-001` | seed 以此判斷文件是否已建立 |
| `title` | `TEXT` | 文件標題 | 虛構文件的標題以「【虛構範例】」開頭 |
| `version` | `TEXT` | 文件版本 | 查詢結果一併顯示 |
| `is_fictional` | `BOOL` | 是否為開發用虛構文件 | 查詢結果會標示「虛構範例」。⛔ 虛構文件的流程、藥品名稱與數值不得作為任何臨床依據 |
| `source_label` | `TEXT` | 文件來源說明 | 虛構文件為「開發用虛構範例（非院內文件，不得作為臨床依據）」 |
| `active` | `BOOL` | 是否在查詢範圍內 | `DEFAULT true`。停用的文件不列入檢索 |
| `created_at` | `TS` | 建立時間 | 見共通欄位 |

---

### `sop_sections` — 文件段落（6 欄）

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 內部識別碼 | 主鍵 |
| `document_id` | `TEXT` | 屬於哪一份文件 | 外鍵 → `sop_documents.id`，**`ON DELETE CASCADE`**（本表唯一的級聯） |
| `section_no` | `TEXT` | 第幾節 | |
| `heading` | `TEXT` | 段落標題 | 參與檢索 |
| `body_text` | `TEXT` | 段落原文 | ⛔ 查詢結果一律原樣引用，不經模型改寫。維持單一段落 |
| `sort_order` | `INT` | 在文件中的順序 | |

**唯一約束**：`(document_id, section_no)`

---

### `sop_queries` — 查詢紀錄（7 欄）

**蒐集的意義**：每一次查詢一列：誰問的、結果是什麼、引用了哪幾段。問題文字只存去識別化後的版本；模型的回答存在對應的 `ai_invocations` 列（12 個月留存），這裡不重複存。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 內部識別碼 | 主鍵 |
| `asked_by_id` | `TEXT` | 誰問的 | 外鍵 → `nurses.id`，`ON DELETE NO ACTION` |
| `question_text` | `TEXT` | 問題 | **去識別化後**才寫入（規範第 14 條）；護理師可能順手打進病人姓名或電話 |
| `outcome` | `TEXT` | 結果：已依文件回答、查無資料、僅列出原文、回答失敗 | 合法值 `ANSWERED` / `NOT_FOUND` / `PASSAGES_ONLY` / `FAILED`（`SopQueryOutcome`）。`PASSAGES_ONLY` 代表 AI 總開關關閉，只列原文 |
| `uncited` | `BOOL` | 模型的回答有沒有標出處 | `DEFAULT false`。為 true 時畫面提醒以原文為準 |
| `ai_invocation_id` | `TEXT?` | 回答來自哪一次模型呼叫 | 外鍵 → `ai_invocations.id`，`ON DELETE NO ACTION`。查無資料或只列原文時為 NULL——**沒有呼叫模型** |
| `asked_at` | `TS` | 查詢時間 | `DEFAULT CURRENT_TIMESTAMP`，有索引 |

---

### `sop_query_citations` — 查詢引用的段落（6 欄）

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 內部識別碼 | 主鍵 |
| `query_id` | `TEXT` | 屬於哪一次查詢 | 外鍵 → `sop_queries.id`，**`ON DELETE CASCADE`**（本表唯一的級聯） |
| `section_id` | `TEXT` | 檢索到的段落 | 外鍵 → `sop_sections.id`，`ON DELETE NO ACTION` |
| `rank` | `INT` | 在提示中的順位 | 1 代表引用標記 `S1` |
| `score_permille` | `INT` | 檢索分數 | 千分位整數，供事後查核「為什麼找到這一段」 |
| `cited_by_model` | `BOOL` | 模型的回答有沒有引用這一段 | 依回答中的 `[S1]` 這類標記判定 |

**唯一約束**：`(query_id, section_id)`

---

## 十二、求助處理與可設定的暫代值（迭代 5）

本節兩張表都是為了同一件事存在：**外部答覆還沒回來，但開發不能停。**

護理部尚未確認求助的處理方式與處理結果該有哪些選項（Q-13），人資也還沒給勞動條件的醫院規定（Q-14）。
把暫定值寫死在程式裡，答覆回來那天就得改程式、重新部署、重跑一次測試；
寫成資料，改的就只是幾列資料。這兩張表是那個決定的結果。

### `help_resolution_options` — 求助處理的選項清單（8 欄）

**蒐集的意義**：FR-N10 要求結案時以結構化欄位登記處理方式與結果。「結構化」的前提是有一份清單，
而這份清單的內容**不是開發端說了算**——暫定值取自 SRS 5.2 的表格，實際選項待護理部確認。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `kind` | `TEXT` | 這是「處理方式」還是「處理結果」的選項 | 合法值 `METHOD` / `OUTCOME`（`HelpResolutionOptionKind`）。與 `code` 組成唯一鍵，與 `sort_order` 組成索引 |
| `code` | `TEXT` | 選項的內部識別字，例如 `ON_SITE_CARE` | 大寫英數與底線。`help_requests.handling_method_code` / `outcome_code` 存的就是這個值 |
| `label` | `TEXT` | 護理師在結案畫面上看到的字，例如「現場處置」 | 可改。改了之後既有紀錄跟著顯示新字——因為紀錄存的是 `code` 不是文字 |
| `sort_order` | `INT` | 在選單上的排列順序 | 小的在前 |
| `active` | `BOOL` | 這個選項現在還用不用 | 預設 `true`。⛔ 不要刪列：停用即可。刪掉會讓既有紀錄的 `code` 查不到文字 |

**唯一約束**：`(kind, code)`　**索引**：`(kind, sort_order)`
**初始資料**：後端啟動時，若整張表是空的才寫入 `DEFAULT_HELP_RESOLUTION_OPTIONS`（處理方式 8 項、處理結果 6 項）。
之後一律以資料表為準，不會回頭覆蓋——護理部改過的清單不該被下一次重新啟動蓋掉。

### `operational_settings` — 可設定的營運參數（7 欄）

**蒐集的意義**：FR-N11 的「設定期間」與 FR-M04 的五條勞動條件，目前都是暫定值。
這張表讓那些數字有個可以被改、而且改了有跡可循的地方。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `setting_key` | `TEXT` UNIQUE | 這是哪一個參數 | 合法值見 `OperationalSettingKey`：`HELP_RECURRENCE_WINDOW_HOURS`（FR-N11 的再發判定期間，暫定 72 小時）、`LABOUR_MAX_SHIFT_HOURS`、`LABOUR_MIN_REST_HOURS`、`LABOUR_MAX_DAILY_HOURS`、`LABOUR_MAX_WEEKLY_HOURS`、`LABOUR_MAX_CONSECUTIVE_DAYS`（FR-M04，暫以勞動基準法基本條件為值）。迭代 6 另加六項輪播參數：`CAROUSEL_IDLE_THRESHOLD_SECONDS`（FR-P09，預設 60 秒）、`CAROUSEL_CARD_INTERVAL_SECONDS`、`CAROUSEL_DETAIL_TIMEOUT_SECONDS`（FR-P10）、`CAROUSEL_NIGHT_MODE_START_HOUR`／`CAROUSEL_NIGHT_MODE_END_HOUR`（夜間模式）、`SYMPTOM_DUE_INTERVAL_MINUTES`（FR-P13 問卷優先於輪播的判定） |
| `value` | `INT` | 目前的值 | 目前全部是整數（小時、日數）。日後若出現非整數參數，比照臨床數值改為「整數＋小數位數」，**不得改用浮點數** |
| `last_reason` | `TEXT?` | 最後一次改動時填的理由 | 必填才改得動（後端驗證 2～500 字）。理由連同新舊值另寫入 `audit_logs` 的 `OPERATIONAL_SETTING_UPDATED` |
| `updated_by_id` | `TEXT?` | 誰改的 | 外鍵 → `nurses.id`，`ON DELETE NO ACTION` |
| `updated_at` | `TS?` | 什麼時候改的 | **刻意可為空**：空代表「從未被改過，仍是預設值」，與「有人把它改回預設值」是兩件事 |

**預設值的補齊方式**：後端啟動時比對 `OPERATIONAL_SETTING_DEFINITIONS`，**缺哪一筆補哪一筆**。
既有的值不會被覆蓋，新增參數也不必另寫遷移腳本。
每個參數在程式常數中都帶著 `basis`（這個數字現在是誰說的），並原樣顯示在設定畫面上——
要改的人得先看得到「這是勞基法第 34 條」還是「這是開發端猜的」。

### `help_request_follow_ups` — 求助的後續追蹤事項（9 欄）

**蒐集的意義**：FR-N10 的「是否需後續追蹤」勾了「是」，就會落在這張表上。
結案不等於事情結束——「下次上機前確認穿刺處是否仍紅腫」這種事，沒有地方放就只會被忘記。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `help_request_id` | `TEXT` | 從哪一筆求助來的 | 外鍵 → `help_requests.id`，**`ON DELETE CASCADE`** — 本表唯一級聯路徑，沿用該筆通報既有的那一條。有索引 |
| `description` | `TEXT` | 要追蹤什麼 | 最長 300 字。結案時勾了「需追蹤」卻沒填這欄，**結案會被擋下** |
| `status` | `TEXT` | 待追蹤／已完成／已取消 | 合法值 `OPEN` / `DONE` / `CANCELLED`（`HelpFollowUpStatus`）。有索引 |
| `created_by_id` | `TEXT` | 誰開的追蹤事項 | 外鍵 → `nurses.id`，`ON DELETE NO ACTION`。與結案是同一個交易，要嘛都成立、要嘛都不成立 |
| `closed_by_id` | `TEXT?` | 誰結束的 | 外鍵 → `nurses.id`，`ON DELETE NO ACTION` |
| `closed_at` | `TS?` | 什麼時候結束的 | 與 `closed_by_id` 同時寫入，並記 `HELP_FOLLOW_UP_CLOSED` 稽核 |
| `closing_note` | `TEXT?` | 結束時的說明 | 選填自由文字 |

**索引**：`status`、`help_request_id`

---

## 十三、護理師班表與成效基準（迭代 5）

**這一節的資料級別與前面所有章節都不同。** 前十二節談的是病人的資料；這一節談的是**護理師自己的資料**，
而它的風險不在外洩，在**目的外利用**：同一批班表資料，拿來排班是管理工具，拿來算個人績效就是另一回事
（《[資料庫使用規範](../requirements/database-policy.md)》第 11 條）。

因此本節三張表一律為 **L2 班次層級**：一般護理師只看得到自己的班，看他人的班需 `shift:manage`，
而這個限制是**後端縮查詢範圍**做到的，不是前端少畫幾列。
`baseline_measurements` 是 **L1 單位聚合**，不含任何個人識別。

⛔ 本節**不得**新增以下欄位，這是硬性界線（SRS 5.3「禁止事項」）：總分、排名、
「護理師×病人臨床結果」的關聯評分、任何回寫到臨床資料表的績效彙整結果。

### `nurse_shifts` — 護理師班表（13 欄）

**蒐集的意義**：FR-M01。要協助排班、要檢查勞動條件、要知道當班的人負責哪幾床，都得先有班表。
迭代 8 的工作量實測儀表板（FR-M05）也以這張表為分母——沒有班表，「這一班有多忙」算不出來。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `nurse_id` | `TEXT` | 誰上這一班 | 外鍵 → `nurses.id`，`ON DELETE NO ACTION`。與 `shift_date` 組成索引 |
| `shift_date` | `TS` | 這一班屬於哪一天 | 正規化為當日 00:00 UTC，與 `treatment_sessions.scheduled_date` 同一套處理。有索引 |
| `shift_type` | `TEXT` | 白班／小夜班／大夜班 | 合法值 `MORNING` / `AFTERNOON` / `NIGHT`（`NurseShiftType`）。⚠️ 班別分法與起訖時間**待護理長確認（Q-15）**，目前是透析中心常見的三班制 |
| `start_at` | `TS` | 實際開始時間 | **逐筆記錄，不由班別反推**——跨日班與臨時調整都靠這兩欄。由「日期＋HH:MM」依伺服器當地時區換算後存 UTC |
| `end_at` | `TS` | 實際結束時間 | 結束不大於開始時視為跨日（大夜班），自動加一天。這是班表唯一允許的隱含推斷 |
| `status` | `TEXT` | 已排定／已取消 | 合法值 `PLANNED` / `CANCELLED`（`NurseShiftStatus`）。⛔ 取消**不刪列**，否則調班歷程追不回來 |
| `source` | `TEXT` | 手動建立還是檔案匯入 | 合法值 `MANUAL` / `FILE_IMPORT`（`NurseShiftSource`） |
| `import_batch_no` | `TEXT?` | 從哪一個匯入批次來的 | 例如 `NS-20260921-134501-9C1E`。手動建立時為空。有索引 |
| `note` | `TEXT?` | 備註，例如「代 N003」 | 自由文字 |
| `created_by_id` | `TEXT` | 誰排的班 | 外鍵 → `nurses.id`，`ON DELETE NO ACTION`。與 `nurse_id` 是不同的人：一個是排班者，一個是上班的人 |

**唯一約束**：`(nurse_id, shift_date, shift_type)` — 同一人同一天同一班別只能有一筆
**索引**：`shift_date`、`(nurse_id, shift_date)`、`import_batch_no`

**FR-M04 勞動條件檢查**：寫入前一律先跑 `evaluateLabourRules()`，違反就**擋下儲存**並逐條說明。
六條規則（單一班次工時、班距、單日工時、連續七日工時、連續出勤日數、同時段重複排班）的判定函式放在
`@hd/shared`，前後端共用同一份，畫面提示與後端擋下的理由不會不一致；
規則的數值一律從 `operational_settings` 取，**程式裡沒有寫死任何一個數字**。
被擋下的嘗試會寫入 `NURSE_SHIFT_REJECTED_LABOUR_RULE` 稽核——
事後檢討「那週的班為什麼排不出來」時，看得到系統擋了幾次、擋的是哪一條。

**檔案匯入**：全有或全無。格式、查無此人、與既有班次重複、勞動條件，任一關不過整批退回並逐列回報原因，
一筆都不寫入。⚠️ 現行班表格式待護理長提供（Q-15），目前收的是最小欄位集的 CSV。

### `shift_bed_assignments` — 當班床位分配（5 欄）

**蒐集的意義**：FR-M02。一床一列，不以 JSON 承載（規範 6.1 第 2 條）。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `nurse_shift_id` | `TEXT` | 屬於哪一個班次 | 外鍵 → `nurse_shifts.id`，**`ON DELETE CASCADE`** — 本表唯一級聯路徑 |
| `bed_no` | `TEXT` | 床號，例如 `A01` | 限英數與連字號，最長 12 字。⛔ 病人可識別資訊**只到床號層級**，姓名與病歷號不得出現在此（SRS 5.1 補充說明）。有索引 |
| `assigned_by_id` | `TEXT` | 誰指派的 | 外鍵 → `nurses.id`，`ON DELETE NO ACTION` |
| `assigned_at` | `TS` | 指派時間 | `DEFAULT CURRENT_TIMESTAMP` |

**唯一約束**：`(nurse_shift_id, bed_no)`
**一床兩主的防呆**：同一天同一班別、同一張床已指派給別人時，後端擋下並指出是誰——一床兩主等於沒有分配。
**寫入方式**：整組取代（先清後寫，同一個交易），避免出現半套的分配。

### `shift_change_requests` — 調班申請（12 欄）

**蒐集的意義**：請假與換班是班表一定會發生的事。有紀錄，事後才查得出「那天為什麼換人」。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `nurse_shift_id` | `TEXT` | 針對哪一個班次 | 外鍵 → `nurse_shifts.id`，**`ON DELETE CASCADE`**。有索引 |
| `requested_by_id` | `TEXT` | 誰提出的 | 外鍵 → `nurses.id`，`ON DELETE NO ACTION`。⛔ 後端限定**只能對自己的班次提出**，他人的班一律 403 |
| `change_type` | `TEXT` | 請假還是換班 | 合法值 `LEAVE` / `SWAP`（`ShiftChangeType`） |
| `reason` | `TEXT` | 申請理由 | 最長 300 字，必填 |
| `proposed_nurse_id` | `TEXT?` | 換班時由誰接手 | 外鍵 → `nurses.id`，`ON DELETE NO ACTION`。請假時為空 |
| `status` | `TEXT` | 待核示／已核准／已駁回／已撤回 | 合法值見 `ShiftChangeStatus`。有索引 |
| `decided_by_id` | `TEXT?` | 誰核示的 | 外鍵 → `nurses.id`，`ON DELETE NO ACTION` |
| `decided_at` | `TS?` | 核示時間 | 與 `decided_by_id` 同時寫入 |
| `decision_note` | `TEXT?` | 核示時的說明 | 選填 |

**核准的副作用**：請假核准 → 該班次轉為 `CANCELLED`；換班核准 → 班次改掛到接手的人身上，
而且**要對接手的人重跑一次勞動條件檢查**——換班最容易換出違規班表。
兩者都各自寫一筆班表異動的稽核，與「核示申請」分開記錄：查班表異動史的人不必先知道當初有一張申請單。

⚠️ **FR-M03 的候補人選排序不在本迭代**：依技能標記、連續工時、近期負荷產生排序屬 **L3 個人層級**，
須先通過規範 11.3 的啟用流程（護理部書面同意＋計分規則公告＋觀察期），留待後續迭代。

### `baseline_measurements` — 成效基準（15 欄）

**蒐集的意義**：FR-M07。這是全系統唯一「**過了時點就再也拿不到**」的資料。

系統上線後，「病人按鈴到護理師到床邊要多久」會自動被記錄；但**上線前的數字不存在於任何地方**，
它只存在於現在正在發生的紙本與口頭流程裡。紙本流程一消失，就再也無從量測。
這張表的存在理由，就是趕在那之前把數字留下來。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `metric_code` | `TEXT` | 量的是哪一件事 | 合法值見 `BASELINE_METRIC_DEFINITIONS`：`CALL_TO_BEDSIDE_MINUTES`、`EVENT_RECORD_MINUTES`、`REPEAT_EDUCATION_COUNT`、`HANDOVER_LOOKUP_MINUTES`、`LATE_CHARTING_PERCENT`（Q-01 建議量測的五項，請護理長刪減）。與 `superseded` 組成索引。⛔ 不允許自行新增指標：新增的指標沒有上線後的對照來源，會變成擺著沒用的數字 |
| `value_scaled` | `INT` | 量到的數字 | 「整數＋小數位數」，**不用浮點數**（規範 6.2）。4.2 分鐘存為 `42` + `value_scale=1` |
| `value_scale` | `INT` | 小數位數 | 隨指標定義。小數位數超過定義時視為格式錯誤，**不四捨五入** |
| `sample_size` | `INT` | 測了幾筆 | 樣本數太少的基準禁不起追問，因此與數值一起呈現，不藏起來 |
| `source` | `TEXT` | 現場實測／護理部既有指標／估算 | 合法值 `MEASURED` / `EXISTING_INDICATOR` / `ESTIMATED`（`BaselineSource`）。⛔ `ESTIMATED` 是 Q-01 的退路，這種資料在所有畫面與報表上都會標示「估算」，**引用時不得當成實測數字陳述** |
| `shift_type` | `TEXT?` | 哪一班量的 | `NurseShiftType`。全單位一起量、不分班時為空 |
| `measured_from` / `measured_to` | `TS` | 量測期間 | 起日不得晚於迄日，也不得是未來——基準記錄的是已經發生的事 |
| `method` | `TEXT` | 怎麼量的 | 例如「現場碼表抽測，分三班各 20 次」。必填 |
| `endorsed_by` | `TEXT` | 誰背書說「這是本單位認可的基準」 | **必填**（Q-01 第 6 題）。空著等於這個數字沒有出處，之後被院長室問到「這數字哪來的」就答不出來 |
| `note` | `TEXT?` | 備註 | 選填 |
| `superseded` | `BOOL` | 已被新版本取代 | ⛔ 一律**只新增不覆寫**：同一指標同一班次有新版本時，舊版標記為 `true` 保留，事後才查得出基準改過幾次 |
| `recorded_by_id` | `TEXT` | 誰建的檔 | 外鍵 → `nurses.id`，`ON DELETE NO ACTION`。權限限護理長以上（`baseline:manage`） |
| `recorded_at` | `TS` | 建檔時間 | `DEFAULT CURRENT_TIMESTAMP`。有索引 |

**索引**：`(metric_code, superseded)`、`recorded_at`
**建檔進度**：`/baselines/overview` 逐指標列出「尚未建檔」與「只有估算值」兩種缺口。
上線前只有這個畫面看得出來還差什麼——這是它比輸入表單更重要的理由。

---

## 十四、閒置輪播與檔案匯入（迭代 6）

三張表，兩件事。

前兩張是**輪播**：第一層取自系統既有資料、第三層讀 `clinical_values`，兩層都不需要自己的表；
只有第二層（中心自己寫的衛教與公告）與瀏覽事件需要存進資料表。
第三張是**檔案匯入的欄位對應**——院方匯出檔的欄位名稱會被人改動，
那是別人的系統，不會為了我們保持不變，所以「哪一欄是乾體重」必須是資料而不是程式。

### `carousel_items` — 輪播第二層內容（14 欄）

**蒐集的意義**：FR-P11 的第二層是靜態衛教與中心公告，由護理端在管理介面上架。
這是輪播三層中唯一「人自己寫」的一層，因此也是唯一需要編輯、排序與上下架的一層。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `item_kind` | `TEXT` | 這則是衛教還是公告 | 合法值 `STATIC_EDUCATION` / `ANNOUNCEMENT`（`CarouselItemKind`） |
| `title` | `TEXT` | 卡片標題 | 最長 60 字 |
| `summary` | `TEXT` | 卡片上顯示的一句話 | 最長 120 字。輪播畫面一次只讀得完一句 |
| `body_text` | `TEXT?` | 點開細節頁後看到的說明 | 最長 1000 字。留空代表這張卡片不能點開（FR-P10） |
| `language` | `TEXT` | 內容語言 | BCP 47 語言標籤，預設 `zh-TW`。多語言輪播由日後的語言篩選使用 |
| `sort_order` | `INT` | 播放順序 | 小的在前；同值時以建立時間排序 |
| `active` | `BOOL` | 現在還播不播 | 預設 `true`。⛔ 不要刪列：下架即可，刪掉會讓稽核軌跡指向不存在的內容 |
| `starts_at` / `ends_at` | `TS?` | 上架與下架時間 | 皆可為空，代表不限期間。過濾在資料庫做，平板拿到的就已經是「現在播得出來」的內容 |
| `created_by_id` | `TEXT` | 誰上架的 | 外鍵 → `nurses.id`，`ON DELETE NO ACTION` |
| `updated_by_id` | `TEXT?` | 最後誰改的 | 外鍵 → `nurses.id`，`ON DELETE NO ACTION`。從未被改過時為空 |

**索引**：`(active, sort_order)`
**與功能開關的關係**：第二層開關（`CAROUSEL_LAYER_2`）的開啟條件是「至少有一則在架上的內容」——
沒有內容就開啟，病人只會看到空白的輪播，因此後端直接擋下（`FeatureFlagsService`）。

### `carousel_view_events` — 輪播瀏覽事件（7 欄）

**蒐集的意義**：迭代 8 要回答「哪一類內容真的有人看」。
這張表刻意**只**回答那個問題：沒有病人、沒有綁定、沒有平板序號、沒有卡片內容。
不留可識別欄位，日後也就不會有人想從這裡回推個人行為（SRS FR-P11 補充說明）。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `occurred_at` | `TS` | 什麼時候看的 | 有索引。這是全表唯一與時間有關的欄位，且只到「事件寫入的時刻」 |
| `layer` | `TEXT` | 哪一層 | 合法值 `LAYER_1` / `LAYER_2` / `LAYER_3`（`CarouselLayer`），由後端依 `card_kind` 推出，不採信平板送上來的值 |
| `card_kind` | `TEXT` | 哪一類卡片 | 合法值見 `CarouselCardKind`，只到種類層級（療程進度、今日已回報內容、衛教完成度、靜態衛教、中心公告、臨床數值）。有索引 |
| `dwell_ms` | `INT` | 這一輪停留多久 | 超過 30 分鐘的一律丟棄——平板被擱著沒人看的那段時間不是「瀏覽」 |
| `detail_open_count` | `INT` | 這一輪被點開細節頁幾次 | 預設 0 |
| `night_mode` | `BOOL` | 當下是否為夜間模式 | 預設 `false`。供日後比較晚班與日班的閱讀行為 |

**⛔ 不要加欄位**：任何「哪一位病人」「哪一台平板」「哪一則內容」的欄位都會改變這張表的性質。
要做個人層級的閱讀分析，先回頭看《[資料庫使用規範](../requirements/database-policy.md)》第 11 條與 SRS 5.3。
端點的 DTO 開著 `forbidNonWhitelisted`，前端多送一個 `patientId` 會讓整包請求被擋下，而不是默默存起來。

### `import_field_mappings` — 匯入欄位對應設定（8 欄）

**蒐集的意義**：FR-S05 的檔案匯入要能對上院方的匯出檔，而那份檔案的欄位名稱不在我們手上。
把對應寫成資料，院方改名那天要改的就是一列設定，不是一次部署（實作規格書 3.5）。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `profile_code` | `TEXT` | 這組對應用在哪一種匯入 | 目前只有 `CLINICAL_VALUE`（`ImportProfileCode`）。與 `target_field` 組成唯一鍵 |
| `target_field` | `TEXT` | 系統這一側的欄位 | `MEDICAL_RECORD_NO`、`MEASURED_AT`，或 `CLINICAL_VALUE_DEFINITIONS` 的任一個 `code` |
| `column_label` | `TEXT` | 檔案裡的欄位名稱 | 比對時忽略大小寫、半形與全形空白。兩個目標欄位不得同時對應到同一個檔案欄位，設定時就擋下 |
| `active` | `BOOL` | 這一項現在還匯不匯 | 預設 `true`。病歷號與資料時間是必填欄位，停用它們等於整批匯不進來 |
| `updated_by_id` | `TEXT?` | 誰改的 | 外鍵 → `nurses.id`，`ON DELETE NO ACTION` |
| `updated_at` | `TS?` | 什麼時候改的 | 與 `operational_settings` 同樣的取捨：空代表從未被改過，仍是預設值 |

**唯一約束**：`(profile_code, target_field)`　**索引**：`(profile_code, active)`
**預設值的補齊方式**：後端啟動時缺哪一筆補哪一筆，既有設定不覆蓋。
預設欄位名稱是**開發端的猜測**，不是院方給的格式（Q-09）；每次修改連同新舊名稱寫入
`audit_logs` 的 `IMPORT_FIELD_MAPPING_UPDATED`。

---

## 十五、版本更新紀錄（迭代 7）

FR-S12、規範第 18 條。**第一次正式部署之後，每一次更新面對的都是真實病人資料，而那份資料只有一個檔案。**
這一類只有一張表，記的是「更新這件事本身」——與第八條的日常備份是兩回事。

### `update_runs` — 版本更新紀錄（14 欄）

**蒐集的意義**：規範 18.4。沒有這份紀錄，半年後發現資料對不上時，沒有人答得出「那是哪一次更新帶進來的」。
每一次執行更新流程（`npm run db:update`）留一列，**成功與中止都留**。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 內部識別碼 | 主鍵 |
| `status` | `TEXT` | 進行中、完成、中止 | 合法值 `RUNNING` / `SUCCEEDED` / `FAILED`（`UpdateRunStatus`） |
| `started_at` | `TS` | 開始時間 | `DEFAULT CURRENT_TIMESTAMP`，有索引 |
| `finished_at` | `TS?` | 結束時間 | |
| `from_version` | `TEXT?` | 更新前的版本標記 | 取自上一筆成功的 `to_version`；第一次更新為空 |
| `to_version` | `TEXT` | 更新後的版本標記 | 取自 `apps/api/package.json` 的 `version` |
| `backup_file_name` | `TEXT?` | 更新前那份備份的檔名 | ⛔ 同 `backup_runs`：**只記檔名**，目錄由 `BACKUP_DIR` 決定（第 9 條）。空代表備份根本沒做成，那次更新不該往下走 |
| `backup_size_bytes` | `BIGINT?` | 備份檔大小 | |
| `backup_sha256` | `TEXT?` | 備份檔的雜湊值 | 還原時拿來比對 |
| `backup_verified_at` | `TS?` | 備份**實際還原並通過完整性檢查**的時間 | 規範 18.1 第一關。空代表沒有通過，流程會停在遷移之前 |
| `backup_verify_result` | `TEXT?` | 驗證結果：完整性檢查與各主要資料表的筆數 | 驗證用的暫存檔檢查完即刪，只留這句結論 |
| `applied_migrations` | `TEXT?` | 這次套用了哪幾個遷移 | 以換行分隔；沒有待套用的遷移時為空字串。**這是「遷移只能前滾」留下的唯一證據** |
| `operator_label` | `TEXT` | 誰執行的 | **作業系統帳號＠主機名稱**，不是護理端帳號——更新進行時服務是停著的，沒有人登入 |
| `error_message` | `TEXT?` | 中止原因 | 已把資料庫與備份目錄的實際路徑換成設定名稱（第 9 條） |

**索引**：`started_at`
**誰寫這張表**：只有更新腳本。**後端只讀不寫**（`UpdateRunRepository` 走唯讀連線），
護理端「系統管理 → 資料庫與備份」最下方呈現它。
**同一次更新在稽核軌跡留下的**：`DATABASE_UPDATE_STARTED`、`DATABASE_BACKUP_CREATED`、
`DATABASE_BACKUP_VERIFIED`、`DATABASE_UPDATE_COMPLETED`（或 `DATABASE_UPDATE_FAILED`）。
在正式環境誤用開發用遷移指令而被擋下時，另留一筆 `DATABASE_MIGRATION_BLOCKED`。

---

## 十六、導覽版位與內容資料化（迭代 9）

FR-S11、SRS 附錄 C。**這一類的每一張表都是為了同一件事：讓「有哪些、放在哪、問什麼」
不必改程式就能改。** 寫在程式裡的選項，每改一次就要重新部署一次；
而重新部署的門檻高到最後大家就不改了——不改的結果不是穩定，是護理部放棄使用這一部分。

### `nav_placement_settings` — 導覽版位（7 欄）

**蒐集的意義**：FR-S11。半年後有人問「這個功能什麼時候不見的」要答得出來。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 內部識別碼 | 主鍵 |
| `nav_key` | `TEXT` | 哪一個功能 | 唯一鍵。合法值為 `@hd/shared` 的 `NavItemKey`（17 項） |
| `placement` | `TEXT` | 主列／更多選單／關閉 | `PRIMARY` / `MENU` / `OFF`（`NavPlacement`）。⛔ **`OFF` 不是「藏起來」**：前端不註冊路由、後端回 404 |
| `last_reason` | `TEXT?` | 上一次調整的理由 | 每次調整必填，長度下限由服務層把關 |
| `changed_by_id` | `TEXT?` | 誰調的 | → `nurses.id` |
| `changed_at` | `TS?` | 什麼時候調的 | **刻意可為空**：空代表從未被調過，與「有人把它調回預設值」是兩件事 |
| `created_at` | `TS` | 這一列建立的時間 | 第一次啟動時由 `NAV_ITEM_DEFINITIONS` 補齊 |

**誰寫這張表**：`NavigationService`。預設值來自共用常數，**只在那一列還不存在時寫入一次**——
之後一律以資料表為準，否則每次重新部署都會把護理長的調整洗掉。
**稽核**：`NAV_PLACEMENT_CHANGED`（改版位）、`NAV_ITEM_ACCESS_BLOCKED`（關閉的端點被呼叫）。

### `help_categories` — 求助類別（10 欄）

**蒐集的意義**：SRS 附錄 C.2。原為共用常數，迭代 9 起以本表為準。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `code` | `TEXT` | 識別碼 | 唯一鍵。⛔ **建立後不可編輯**——一改，這個選項之前累積的所有紀錄就與之後的對不起來（附錄 C.0 規則 1） |
| `label` | `TEXT` | 病人看到的字 | 白話症狀，不是診斷名稱。可改 |
| `group_code` | `TEXT` | 臨床／非臨床 | `CLINICAL` / `NON_CLINICAL`。分派規則的輸入之一 |
| `default_severity` | `TEXT` | 分派表預設急迫度 | ⛔ 只決定「先跳到誰的畫面上」。**病人自選的優先於它**（FR-N03） |
| `sort_order` | `INT` | 顯示順序 | 臨床組刻意依常見程度排，不依字母 |
| `active` | `BOOL` | 還在用嗎 | ⛔ **停用是唯一的移除方式**，沒有刪除 |
| `is_other` | `BOOL` | 是不是「其他」 | ⛔ 為真時不可停用（附錄 C.8 護欄 3） |
| `clinical_note` | `TEXT?` | 對應的常見併發症 | ⛔ **不顯示給病人，也不顯示給護理師**——顯示了就變成系統在給診斷提示，那是 FR-P03／P05 的範圍 |

**稽核**：`HELP_CATEGORY_UPDATED`、首次寫入時的 `CONTENT_DEFAULTS_SEEDED`。

### `help_request_methods` — 處理方式的執行順序（5 欄）

**蒐集的意義**：附錄 C.3。一次求助常常做了不只一件事，而且**順序有意義**——
「先平躺再回填食鹽水」和「先回填再平躺」是不同的處置路徑。

| 欄位 | 型別 | 說明 |
|---|---|---|
| `help_request_id` | `TEXT` | → `help_requests.id`（級聯刪除） |
| `method_code` | `TEXT` | `help_resolution_options` 中 `kind=METHOD` 的 `code` |
| `sequence` | `INT` | 1 起算的執行順序 |

`help_requests.handling_method_code` 保留為「第一個做的處置」，既有紀錄與既有查詢照舊可用。

### 三組帶版本號的內容

`questionnaire_versions` ＋ `questionnaire_items` ＋ `questionnaire_item_options` ＋ `questionnaire_item_triggers`（附錄 C.5）、
`quiz_bank_versions` ＋ `quiz_bank_questions` ＋ `quiz_bank_question_options` ＋ `quiz_topics`（附錄 C.6）、
`feedback_form_versions` ＋ `feedback_form_items`（附錄 C.7）。

**三組是同一個形狀，規則也一樣**：

| 規則 | 為什麼 |
|---|---|
| **改一題＝整份複製成新版本再套上改動**，在同一個交易裡完成 | 半成品的版本比沒有版本更難查 |
| 每一份作答記錄它當時的版本字串 | 沒有版本號，改過題目之後的趨勢圖就是把兩種不同的問題畫在同一條線上 |
| 舊版本原封不動留著 | 舊作答要還原得出當時問的是什麼 |
| 版本號從 **2** 起算 | 第 1 版留給迭代 9 之前那一版題目，**只在既有環境才寫入**（全新環境沒有人填過它）。同一個版本字串在任何一套環境裡都要指同一份題目 |
| 知識點與題目的識別碼**不可重用** | 一個識別碼一輩子只對應一個知識點，否則「這位病人在鉀離子上錯了三次」會變成假的 |

**`symptom_answer_options`** 是複選題的子表：單選題不會有這裡的資料，`answer_value` 就是答案本身；
複選題的 `answer_value` 記 `SELECTED` 或 `NONE`，選了哪幾項存在這張表，順序即病人點選的順序。

**`help_requests.category_label`**（迭代 9 新增的欄位）：按下求助的當下，病人在平板上看到的那行字。
類別的顯示文字之後可能被改掉（識別碼不動），但**這一筆紀錄要留住當時的措辭**——
事後回頭看，要知道病人按的是哪一個按鈕上的哪幾個字。迭代 9 之前的紀錄為空，顯示時退回以識別碼查目前的文字。

**趨勢偏離仍然不入庫**：規則 `PSY-DEV-v2`（這位病人自己近六次的移動中位數，
連續兩次低於它達 2 分才標示；三個門檻皆可在 `operational_settings` 調整）在查詢時即時計算，
結果只以事實陳述呈現給護理師，**不寫入任何資料表，也不自動觸發轉介**。

---

## 附錄 A：資料不流向哪裡

同樣重要的是**沒有**蒐集什麼。以下都不在資料庫裡，且都是刻意的：

| 沒有蒐集 | 原因 |
|---|---|
| 生命徵象、透析處方、透析機台參數 | 本系統不是電子病歷；機台整合屬未來擴充。院方臨床數值只收輪播第三層需要的少數幾種，且每筆帶資料時間與來源批次 |
| 風險分數、嚴重度分級、趨勢預警 | 屬 FR-P03／FR-P05／FR-N06，迭代 11 以規則引擎實作並受書面確認閘門約束，不會寫進現有的任何一張表 |
| 未去識別化的 AI 提示 | 規範第 14 條：沒有任何理由需要保留它，去識別化在寫入之前完成 |
| 密碼明文、Session Token 明文、平板 API 金鑰明文 | 一律只存雜湊或 jti |
| 資料庫檔案與備份檔的完整路徑 | 規範第 9 條：不寫進資料庫、日誌、稽核或 API 回應；`backup_runs` 只記檔名 |
| 任何真實病人可識別資訊 | 規範第 10 條，開發與測試環境鐵則 |
| 病人的登入帳號 | 病人不登入，身分由護理師觸發的裝置綁定代理（SRS 4.3） |
| 症狀問卷的題目文字 | 題目是程式版本的一部分，放在 `@hd/shared`，紀錄只存版本號。迭代 4 的衛教主題、測驗題庫、回饋題目、事件範本同樣如此 |
| 知識點狀態、心理社會的趨勢比對結果 | 查詢時由原始作答與分數即時計算，不寫入資料表；比對結果只給護理師看，不自動觸發任何動作 |
| 對病人或護理師的任何評分、排名 | 測驗的答對題數是病人自己的作答結果，不是評分；「是否採納 AI 初稿」是治理證據，不是績效指標 |
| SOP 查詢的模型回答全文 | 只存在對應的 `ai_invocations` 列（12 個月留存）；`sop_queries` 只存去識別化的問題、結果與引用段落 |
| 護理師的個人績效總分、排名、任何「護理師×病人臨床結果」的關聯評分 | SRS 5.3 的硬性禁止事項。班表是管理工具，不是計分板；排名若日後有需要，一律於查詢時即時計算，**不寫入資料表**（規範 11.2、11.3） |
| 輪播畫面上的病人姓名與病歷號 | 治療區內鄰床可見。床位分配只到 `bed_no` 層級（SRS 5.1 補充說明）。卡片由後端組好再送到平板，這條規則只在一處判定 |
| 輪播瀏覽事件中的病人、綁定、平板與卡片內容 | `carousel_view_events` 只回答「哪一類內容有人看」；那個問題不需要知道是誰在看 |
| 匯入檔案的原始內容 | 只留內容雜湊供重複匯入偵測，以及解析後寫入 `clinical_values` 的數值；檔案本身不存進資料庫 |

## 附錄 B：Agent 動 schema 前的自我檢查

摘自《[資料庫使用規範](../requirements/database-policy.md)》第 16 條，逐條確認：

- [ ] 這個改動是否讓前端直接碰資料庫檔案？→ 改走後端 API
- [ ] 存取控制是否寫在後端應用層？→ 不得依賴檔案權限或前端隱藏
- [ ] 是否在業務邏輯中直接寫 SQL 或 SQLite 方言？→ 改走 Repository／Prisma；非用不可時集中在 Repository 具名方法並標 `SQLITE-SPECIFIC`
- [ ] 新欄位若帶小數，是否誤用了浮點數？→ 臨床數值一律整數最小單位或「整數＋小數位數」
- [ ] 是否新增了第二個會寫入資料庫的常駐行程？→ 不允許
- [ ] 測試資料是否為 faker 合成資料？→ 一律替換
- [ ] 新欄位是否已納入稽核軌跡（誰、何時、對誰、做了什麼）？→ 補齊再實作
- [ ] 是否用了 Prisma enum、JSON 欄位、或資料庫專屬預設值？→ 改成 `TEXT` ＋ 應用層常數
- [ ] 新外鍵是否在同一張表製造第二條級聯路徑？→ 除指定的那一條外一律 `NO ACTION`
- [ ] 這次的功能是否會產生 L3 個人層級績效資料？→ 先確認 `PERF_INDIVIDUAL_L3` 開關
- [ ] 匯入外部資料時，是否做到全有或全無？→ 部分寫入不允許
- [ ] 改完後本文件是否需要同步更新？

---

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|
| [0923](https://94sh09sh19sh.github.io/hd-docs/0923/reference/data-dictionary/) | 2026-09-23 | 補到 54 張表 529 個欄位：迭代 7 的執行環境與版本更新紀錄（第十五節）、迭代 9 的導覽版位與內容資料化（第十六節）；附錄 C 的內容全部搬進資料表，三組帶版本號的內容用同一個形狀，`help_requests` 多一欄 `category_label`，`symptom_answers` 多一張複選子表 |
| [0916](https://94sh09sh19sh.github.io/hd-docs/0916/reference/data-dictionary/) | 2026-09-16 | 補到 39 張表 408 個欄位：改述為 SQLite 現況，補上迭代 3 的五張表與迭代 4 的十四張表，新增第十二～十四節（求助處理與可設定暫代值、班表與成效基準、閒置輪播與檔案匯入）|
| [0909](https://94sh09sh19sh.github.io/hd-docs/0909/reference/data-dictionary/) | 2026-09-09 | 首次定版 |

[← 回進度首頁](../index.md)
