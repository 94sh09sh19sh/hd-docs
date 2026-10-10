# 血液透析平板照護輔助系統 — 資料字典

**範圍**：目前資料庫實際蒐集的全部資料 — 67 張表、659 個欄位、17 個 migration（`init`、`iteration3_closed_network`、`iteration4_ai_content`、`iteration5_help_resolution_shifts_baseline`、`iteration6_carousel_file_import`、`iteration7_update_runs`、`iteration9_navigation_content`、`iteration9_help_category_label`、`iteration10_kiosk_foreground`、`iteration12_kiosk_shell_version`、`iteration14_beds`、`iteration15_hospital_api`、`iteration17_marquee_approval`、`iteration17_7_device_targets`、`iteration17_8_nursing_record_format`、`iteration18_rule_engine`、`iteration18_1_rule_gate`）
**來源**：`apps/api/prisma/schema.prisma`、`apps/api/prisma/migrations/`、`packages/shared/src/constants.ts`、`packages/shared/src/platform.ts`、`packages/shared/src/education.ts`、`packages/shared/src/nursing.ts`、`packages/shared/src/operations.ts`、`packages/shared/src/carousel.ts`、`packages/shared/src/rules.ts`
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
2. **不使用 JSON 欄位**承載結構化關聯資料 — 一律正規化成資料表與外鍵。唯一的例外是遊戲盤面快照（1010 起，規範 6.1 的例外段落與六條界線）；遊戲的資料表還沒建立，建立時在本文件逐欄寫明快照的格式與版本。
3. **不使用資料庫專屬預設值** — UUID 由 Prisma client 在應用層產生。
4. **命名**：欄位 `snake_case`，表名複數 `snake_case`。
5. **稽核欄位不因階段省略** — 誰、何時、對誰、做了什麼，設計時就納入。
6. **級聯路徑只留一條** — 多條級聯刪除路徑本身就難以推理。除了指定的那一條外鍵，其餘一律 `NO ACTION`。迭代 3 新增的五張表全部不帶級聯刪除。迭代 4 的十四張表只讓「主表 → 自己的明細」帶級聯（勾選欄位、測驗作答、回饋分數、文件段落、查詢引用），其餘一律 `NO ACTION`。迭代 5 的七張表同理：求助的後續追蹤沿用 `help_requests` 既有的那一條，床位分配與調班申請掛在 `nurse_shifts` 底下，其餘（選項清單、營運參數、成效基準）不帶任何級聯——它們是治理紀錄，成效基準更是過期就拿不到的一次性資料。迭代 6 的三張表同樣一條級聯都不帶：輪播內容與欄位對應是設定，瀏覽事件是成效資料。

另依規範 6.2：**任何劑量、體重、脫水量等臨床數值不得使用浮點數**，一律以整數最小單位或「整數＋小數位數」記錄。

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
| 十、護理記錄與計算（迭代 4） | `nursing_records`、`nursing_record_fields`、`nursing_record_sections`（1010 迭代 17.8）、`adequacy_calculations` | 護理師簽核的記錄與它的起點（預填文字或 AI 初稿）；依公式算出的透析適足性 |
| 十一、SOP 文件與查詢（迭代 4） | `sop_documents`、`sop_sections`、`sop_queries`、`sop_query_citations` | 查詢範圍內的文件原文，以及每一次查詢引用了哪幾段 |
| 十二、求助處理與可設定的暫代值（迭代 5） | `help_resolution_options`、`operational_settings`、`help_request_follow_ups` | 求助結案時選的是哪一項處理方式與結果、那份清單本身、以及外部答覆未到前的各項暫定參數 |
| 十三、護理師班表與成效基準（迭代 5） | `nurse_shifts`、`shift_bed_assignments`、`shift_change_requests`、`baseline_measurements` | 誰上哪一班、負責哪幾床、調班的來龍去脈；以及系統啟用前的人工量測結果 |
| 十四、閒置輪播與檔案匯入（迭代 6） | `carousel_items`、`carousel_view_events`、`import_field_mappings` | 衛教與公告播什麼（1005 起在跑馬燈播）、哪一類內容有播到、匯入檔案的欄位怎麼對上 |
| 十五、版本更新紀錄（迭代 7） | `update_runs` | 每一次版本更新前備份了什麼、驗證還原成不成功、套用了哪幾個遷移、誰執行的 |
| 十六、導覽版位與內容資料化（迭代 9） | `nav_placement_settings`、`help_categories`、`help_request_methods`、`questionnaire_*`、`quiz_*`、`feedback_form_*`、`symptom_answer_options` | 哪些功能出現在哪裡；病人與護理師看到的選項與題目是什麼，以及它們改過幾版 |
| 十七、床位圖（迭代 14） | `beds`、`carousel_item_targets`、`carousel_item_device_targets`（1007 迭代 17.7；另有 `devices.bed_no`） | 透析室有哪幾床、每台平板貼在哪一床、哪則輪播內容（1005 起是跑馬燈內容）只在哪幾床、哪幾台平板播 |
| 十八、院方 API 介接（迭代 15） | `hospital_api_fetch_runs`、`dialysis_vital_records` | 每一次抓院方 API 的結果；有綁定平板的病人在透析中的血壓、脈搏與脫水量 |
| 十九、「本次透析」面板與跑馬燈（迭代 16） | 沒有新表（讀 `dialysis_vital_records`、`clinical_values`、`carousel_items`） | 病人平板上的兩張圖、五個數字與一條跑馬燈，各從哪裡來 |
| 二十、跑馬燈內容的 AI 草稿與核准（迭代 17） | 沒有新表（`carousel_items` 加七欄） | 跑馬燈的每一則是誰生成、從哪個主題或事由來、誰核准、什麼時候上架 |

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

**1005 迭代 15 起多一列不是人的帳號**：`work_id` 為 `SYSTEM-HOSPITAL-SYNC`、顯示名稱「院方資料同步」。院方 API 自動建立療程、接上平板、
寫入臨床數值時，那幾張表的「建立者」欄位是必填的護理師外鍵，由這一列承擔。它**登入不了**（狀態 `SUSPENDED`、密碼是當場產生又丟掉的亂數），
帳號清單、審核清單與「資料庫裡有沒有使用者」（初始最高權限帳號的建立條件）都不算它；畫面與稽核顯示「院方資料同步」，不顯示它的帳號識別字。
⛔ 不要刪它、不要改它的狀態——同步會在下次啟動時找不到它而再建一列。

**1005 迭代 17 起再多一列**：`work_id` 為 `SYSTEM-RELEASE-CONTENT`、顯示名稱「隨版本帶入」。隨版本帶進院內的跑馬燈衛教草稿（`carousel_items.source = BUNDLED`）
首次啟動匯入時，`created_by_id` 由這一列承擔。規則與「院方資料同步」完全相同：登入不了、不算人、畫面顯示「隨版本帶入」。

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

### `patients` — 病人（10 欄）

**蒐集的意義**：綁定、排班、症狀回報、求助全部要指向一個明確的病人。這張表刻意**只存識別與基本人口學資料，不存臨床數值**。院方提供的少數臨床數值（理想體重、Kt/V 等）另存於第七類的 `clinical_values`，每一筆都帶資料時間與來源批次。

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
| `preferred_device_id` | `TEXT?` → `devices` | （迭代 15）~~**配給這位病人的平板**。院方資料判定透析開始時，系統就以這一台自動開始這次療程；護理師每位病人只配一次~~ **1006（迭代 17.1）起不再使用**：平板每次透析由護理師配，不長期配給病人 | `ON DELETE NO ACTION`，有索引。**程式不讀不寫**，欄位留著不刪（只做加法），已經填過的值不清；共用型別 `PatientSummary` 已沒有這個欄位。舊的 `PATIENT_PREFERRED_DEVICE_SET` 稽核照舊查得到，不會再產生新的 |
| `created_at` | `TS` | 建檔時間 | 見共通欄位 |
| `updated_at` | `TS` | 最後修改時間 | 見共通欄位 |

**1005 迭代 15 起，接了院方 API 的環境病人主檔由院方資料自動建立與更新**：以病歷號對應，沒有就建立、有就以院方資料為準更新姓名、性別（院方的「男」「女」轉成 `M`／`F`）、生日；
寫 `PATIENT_CREATED`／`PATIENT_UPDATED`，操作者「院方資料同步」。院方資料的病歷號是 8 碼數字，不是 `HD-TEST-` 格式——**接院方 API 的只有院內主機**，開發機接的模擬院方 API 用 `99` 開頭的虛構病歷號。

**索引**：`medical_record_no`（唯一）、`active`、`preferred_device_id`
**被參照**：`treatment_sessions`、`device_bindings`、`symptom_reports`、`help_requests`、`audit_logs`、`ai_invocations`、`clinical_values`；迭代 4：`ai_jobs`、`education_contents`、`education_completions`、`quiz_attempts`、`feedback_responses`、`nursing_records`、`adequacy_calculations`

---

### `devices` — 病人端平板（18 欄）

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
| `mdm_locked` | `BOOL` | 是否已停用（1006 以前畫面上叫「遠端鎖定」） | `DEFAULT false`。**與 `status` 正交**，不要把兩者合併成單一狀態機。1006（迭代 17.1）起畫面上的「停用」就是這一欄（`status` 的 `RETIRED` 沒有流程會設定）；**正在服務病人的平板後端不讓停用**，停用時 `bed_no` 一併清空。稽核動作 `DEVICE_MDM_LOCKED`／`UNLOCKED` 的中文名稱改成「停用平板」「解除停用平板」 |
| `mdm_kiosk_url` | `TEXT?` | Kiosk（單一 App）模式要鎖定顯示的網址 | 選填。設定時寫 `DEVICE_MDM_KIOSK_CONFIGURED` 稽核 |
| `last_seen_at` | `TS?` | 這台平板最後一次與後端通訊的時間。用來發現離線或故障的機器 | 平板請求時更新。⚠️ 更新頻繁，避免放進頻繁查詢的交易中 |
| `kiosk_foreground` | `BOOL?` | 平板最後一次回報時是否停在病人端畫面上（迭代 10 逸出偵測；迭代 12 起在外殼裡是「可見而且仍釘選」） | 空值＝從未回報（還沒裝外殼），與「已跳出」分開 |
| `kiosk_reported_at` | `TS?` | 最後一次收到前景回報的時間。超過 90 秒沒有回報，護理端顯示「失去回報」 | 每 30 秒更新一次 |
| `kiosk_exited_at` | `TS?` | 最後一次回報「離開前景」的時間。回到前景之後仍保留，答得出上一次是什麼時候跳出去的 | 只在回報離開時更新 |
| `shell_version` | `TEXT?` | 外殼 App 最後一次回報的自身版本，例 `0.2.0`（迭代 12，FR-S14） | 空值＝未回報版本（迭代 12 之前的外殼或一般瀏覽器）。不帶版本的回報不會把它洗掉 |
| `shell_contract_version` | `INT?` | 外殼 App 實作的契約版本。與系統的契約版本不同時，護理端標為「版本不相容」 | 與 `shell_version` 同進退；「外殼過舊」由最低可用版本設定當場推算，不存欄位 |
| `bed_no` | `TEXT?` UNIQUE | 這台平板貼在哪一床（迭代 14，簡易版床位圖）。**病人在哪一床就是看他那台平板在哪一床**，所以病人本身不存床號 | 空值＝還沒放上床位或停用後拿下。唯一（一床一台）；SQLite 允許多個空值。換床走 `POST /devices/:id/bed`，目的床有平板時兩台對調，寫 `DEVICE_BED_CHANGED`。床號要在 `beds` 的啟用清單裡 |
| `created_at` | `TS` | 建檔時間 | 見共通欄位 |
| `updated_at` | `TS` | 最後修改時間 | 見共通欄位 |

**索引**：`serial_no`（唯一）、`status`、`bed_no`（唯一）
**被參照**：`device_bindings`、`symptom_reports`、`help_requests`、`audit_logs`

---

## 三、排班與綁定（系統核心）

### `treatment_sessions` — 當日排班（15 欄）

**蒐集的意義**：綁定不能憑空發生 — SRS 4.3 要求「護理師在主控台選定當日該時段的病人」才能綁定平板。這張表就是那份當日名單（FR-N01），它同時是綁定的**前置條件**與**授權範圍的邊界**：一次綁定只在它所屬的療程時段內有效。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 這筆排班的內部識別碼 | 主鍵 |
| `patient_id` | `TEXT` | 這個時段排的是哪位病人 | 外鍵 → `patients.id`，`ON DELETE CASCADE` |
| `scheduled_date` | `TS` | 排班日期 | **只取日期部分**，實務上存當日 `00:00 UTC`。⚠️ 這個慣例不要改（規範 6.2 已踩過一次）；比較日期時務必正規化到同一時區（見 `common/date.util.ts`） |
| `shift` | `TEXT` | 班別：早班、午班、晚班。透析是固定時段輪班制，同一台機器一天服務多位病人 | 合法值 `MORNING` / `AFTERNOON` / `EVENING`（`TreatmentShift`）。中文標籤在 `TREATMENT_SHIFT_LABELS` |
| `status` | `TEXT` | 這次療程的進度：已排定、進行中、已完成、已取消 | 合法值 `SCHEDULED` / `IN_PROGRESS` / `COMPLETED` / `CANCELLED`（`TreatmentSessionStatus`）。與 `scheduled_date` 組成複合索引 |
| `started_at` | `TS?` | 實際上機時間。排定時間與實際時間常有落差，兩者分開記錄 | 轉入 `IN_PROGRESS` 時寫入 |
| `ended_at` | `TS?` | 實際下機時間 | 轉入 `COMPLETED` 時寫入。0929 起今天的療程可以**重新開啟**（誤下機），回到 `SCHEDULED` 時清為 NULL；下機時間仍留在 `audit_logs` |
| `created_by_id` | `TEXT` | **是誰排的這個班**。稽核要求每筆資料都能追溯到具名操作者 | 外鍵 → `nurses.id`，`ON DELETE NO ACTION`。院方資料帶進來的是「院方資料同步」那一列 |
| `created_at` | `TS` | 排班建立時間 | 見共通欄位 |
| `updated_at` | `TS` | 最後修改時間 | 見共通欄位 |
| `source` | `TEXT` | （迭代 15）這筆排班是護理師建的，還是院方資料帶進來的 | 合法值 `MANUAL` / `HOSPITAL_API`（`RecordSource`），`DEFAULT 'MANUAL'`。護理師今天先拖上床的那一筆，院方資料出現之後改成 `HOSPITAL_API`、由同步接手 |
| `bed_no` | `TEXT?` | （迭代 15）院方資料說病人在哪一床 | 護理師建的療程為空：病人在哪一床看他那台平板（迭代 14）。**有平板時畫面以平板所在的床為準，沒有平板時用這一欄**——沒有平板的病人也要在床位圖上 |
| `expected_end_at` | `TS?` | （迭代 15）院方資料的透析結束時間，當「預計」用 | ⚠️ 可能是預排值，**不拿它判定下機**（下機看結束體重）。~~療程進度條與「待確認下機」用它~~ **1007 迭代 17.5 起只記錄**：透析一律開始後四小時結束（院方硬性規定），進度與「待確認下機」都以 `started_at` 加四小時計 |
| `nurse_modified_at` | `TS?` | （迭代 15）護理師改過這次療程的狀態：提前結束、取消、重新開啟、確認下機 | 有值時同步就不再動這筆的狀態，也不再自動接上平板——**護理師的更正優先**（SRS FR-S15 第 1 條界線）。只標記 `HOSPITAL_API` 的療程 |
| `bed_nurse_modified_at` | `TS?` | （迭代 15）護理師把這位病人換到別床（把他的平板拖到另一床） | 有值時同步不再依院方資料換床。與上一欄分開：換了床的病人，結束體重出現時照樣要自動下機 |

**1005 迭代 15 起院方資料判斷得出來的狀態轉換由同步完成**：當天出現在院方資料就排班（`SCHEDULED`）；開始時間已過、至少一筆紀錄就開始（`IN_PROGRESS`，`started_at` 寫院方的透析開始時間）；
結束體重大於 0 就下機（`COMPLETED`）。班別依開始時間判斷（12 點前早班、17 點前午班、之後晚班，暫代值待 Q-34）；
開始時間從預排值變成實際值、跨過班別界線時，**還沒開始的那一筆換班別**，不另建一筆。

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

> ⚠️ **這一類全部是「病人自己說的」**。這幾張表**不存**風險分層、趨勢預警或嚴重度推論——那屬 FR-P03／FR-P05，**1010 迭代 18 以規則引擎實作**（0919 起編號幾度重排：7 → 11 → 15 → 18），受功能開關與書面確認閘門約束，結果另存專屬資料表（第二十一節的 `rule_evaluations`）。任何看起來像「分級」的欄位（`present`、`severity`、`routed_to`）在下方都有明確說明它為什麼**不是**臨床判斷。

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
| `present` | `BOOL` | 病人是否表示「有這個症狀」。**這只是把答案原樣轉成是／否方便計數與顯示，不是嚴重度分級，也不是任何風險判斷** | 由 `SYMPTOM_PRESENT_VALUES`（`MILD` `MODERATE` `SEVERE` `YES`）機械式推導。⛔ **禁止**在此欄之上疊加任何加權、評分或門檻邏輯 — 那屬 FR-P03 風險分層，只能經由迭代 18 的規則引擎（第二十一節） |
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
| `actor_type` | `TEXT` | 動作是誰做的類型：護理人員、系統自動、平板，或（迭代 15）院方資料同步 | 合法值 `NURSE` / `SYSTEM` / `DEVICE` / `HOSPITAL_SYNC`（`AuditActorType`）。逾時自動失效、每日排程備份這類事件是 `SYSTEM`；院方 API 自動建立病人、排班、開始療程、接上平板、下機、寫入數值是 `HOSPITAL_SYNC`，`actor_label` 為「院方資料同步」——**同一件事不論誰做都是同一個動作代號，靠這一欄分辨人與同步**（SRS FR-S15） |
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
| `flag_key` | `TEXT` UNIQUE | 開關的識別字，例如「AI 輔助功能總開關」 | 合法值見 `@hd/shared` 的 `FeatureFlagKey`：`RISK_STRATIFICATION` `INTRA_DIALYSIS_ALERT` `DOSE_REFERENCE` `AI_FEATURES` `REAL_PATIENT_DATA_TO_AI` `PERF_INDIVIDUAL_L3` `REWARD_SCORING` `HANDHELD_FEATURES` `HELP_NON_CLINICAL_GROUP`（0929）`LAB_VALUE_FEATURES`（1005，需要抽血數值的功能）`MANUAL_PATIENT_CREATE`（1007 迭代 17.7，護理師自己新增病人，預設關閉）`TODAY_PANEL` `MARQUEE`（1005 迭代 16，「本次透析」面板與跑馬燈）。後端啟動時自動補齊缺少的列，套用各自的預設值（只有 `TODAY_PANEL` 預設開啟；9.1～15 是輪播三層）。**`CAROUSEL_LAYER_1`～`3` 於 1005 停用**（`RETIRED_FEATURE_FLAG_KEYS`）：那三列與它們的切換紀錄留在表裡，後端載入時略過、畫面上不再出現 |
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
| `purpose` | `TEXT` | 哪一項功能發起的呼叫 | 合法值見 `AiPurpose`：`CONNECTIVITY_TEST`（迭代 3 的連線測試）；迭代 4 的 `EDUCATION_CONTENT`（個人化衛教）、`DISCHARGE_SUMMARY`（離院衛教重點）、`NURSING_RECORD_DRAFT`（護理記錄草擬）、`SOP_ANSWER`（SOP 查詢回答）；迭代 17 的 `MARQUEE_CONTENT`（跑馬燈內容草稿：只送主題或事由，`patient_id` 一律為空、`contains_real_patient_data` 一律為 false）。每項 AI 功能各登記一個，新增功能時在 `@hd/shared` 補上 |
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
| `output_text` | `TEXT?` | 模型回傳的內容 | 呼叫失敗或被擋下時為 NULL。**迭代 17.3 起有一種失敗有值**：輸出含簡體字或中國大陸用語而被退回重寫的那一次，記成 `FAILURE` 並留下模型寫的原文，查得到它為什麼被退回。**這幾列只在資料庫裡**，系統管理的「AI 呼叫紀錄」不列（前端不留這道把關的痕跡）|
| `error_message` | `TEXT?` | 失敗原因 | 不含推論伺服器的回應原文，避免夾帶提示內容。用語不合格被退回的，開頭固定是「輸出含簡體字或中國大陸用語：」，後面列出哪個詞改成什麼（迭代 17.3）；前端濾掉這幾列時認的就是這個開頭 |
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
| `sha256` | `TEXT?` | 備份檔的雜湊值。還原前拿來比對，確認檔案沒有損毀或被更動 | 還原腳本 `npm run db:restore -- --sha256` 會比對這個值。同一個值另存在備份旁邊的 `<檔名>.sha256`（格式同 `sha256sum`），資料庫壞掉時仍查得到 |
| `error_message` | `TEXT?` | 失敗原因 | 已把資料庫與備份目錄的實際路徑換成設定名稱 |
| `initiated_by_id` | `TEXT?` | 誰觸發的 | 外鍵 → `nurses.id`，`ON DELETE NO ACTION`。排程備份為 NULL |

**索引**：`started_at`
**注意**：備份一律用 `VACUUM INTO`，不直接複製資料庫檔案。舊備份不自動刪除，留存世代數待醫院定案（Q-05）。

---

## 七、院方臨床數值（迭代 3）

FR-S05。院方尚未確定給 API 還是 Excel（Q-09），因此先立 `ClinicalDataSourcePort` 介面層：人工輸入、檔案匯入、院方 API 三種來源**共用同一組內部資料表**，病人端面板（1005 起取代輪播）與儀表板只讀這兩張表、不認來源。迭代 3 只有人工輸入（`ManualEntryAdapter`）。
**1005 迭代 15 起院方 API（`HospitalApiAdapter`）是唯一的日常來源**：一次透析一批（全有或全無的單位），批次的 `source_type` 為 `HOSPITAL_API`、匯入者是「院方資料同步」，`content_hash` 留空（相同的值在送進來之前就濾掉了）。人工輸入與檔案匯入只留在專業版當備援。

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
| `value_code` | `TEXT` | 數值種類：理想體重、目標脫水量、血紅素、白蛋白、Kt/V；迭代 4 另加透析適足性計算的五個輸入值 | 合法值見 `CLINICAL_VALUE_DEFINITIONS`：`DRY_WEIGHT` `UF_TARGET` `HEMOGLOBIN` `ALBUMIN` `KT_V`（原輪播第三層；1005 起病人端面板只顯示理想體重與目標脫水量，抽血數值與 Kt/V 病人端不顯示）；`BUN_PRE` `BUN_POST` `WEIGHT_POST` `UF_VOLUME` `SESSION_MINUTES`（迭代 4，FR-N07 的輸入，Q-26） |
| `value_scaled` | `INT` | 數值本身 | ⛔ **不用浮點數**（規範 6.2）。以整數記錄、搭配下一欄的小數位數：理想體重 62.5 kg 存為 `625`。十進位字串與整數的轉換用 `parseScaledDecimal` / `formatScaledDecimal`，全程字串運算 |
| `value_scale` | `INT` | 小數位數 | 理想體重 1、目標脫水量 0、Kt/V 2。逐列記錄，種類定義日後改變也不影響舊資料的解讀 |
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
| `job_type` | `TEXT` | 什麼工作：產生個人化衛教、產生離院衛教重點、草擬護理記錄、（迭代 17）產生跑馬燈內容草稿 | 合法值 `EDUCATION_CONTENT` / `DISCHARGE_SUMMARY` / `NURSING_RECORD_DRAFT` / `MARQUEE_CONTENT`（`AiJobType`）。各功能模組在啟動時向 `AiJobQueueService` 登記自己的處理程式 |
| `status` | `TEXT` | 排隊中、產生中、已完成、失敗 | 合法值 `QUEUED` / `RUNNING` / `SUCCEEDED` / `FAILED`（`AiJobStatus`），與 `queued_at` 組成複合索引。只有 `QUEUED` 能被改成 `RUNNING`（條件式更新），同一件不會被處理兩次。後端重新啟動時仍為 `RUNNING` 的工作一律收斂為 `FAILED` |
| `target_type` | `TEXT` | 工作結果要寫回哪一種資料 | `EducationContent`、`NursingRecord` 或（迭代 17）`CarouselItem`（模型名）。比照 `audit_logs` 的寫法，刻意不設外鍵 |
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

### `nursing_records` — 護理記錄（21 欄；1010 迭代 17.8 加一欄）

**蒐集的意義**：FR-N04 事件記錄快速範本、FR-N05 依病人自報預填。每筆記錄一建立就有一份「預填文字」（依勾選內容或病人自述組出，不經模型）；AI 初稿是另一個起點；**護理師簽核的定稿才是正式記錄**。記下「是否採納 AI 初稿」是《資料庫使用規範》第 14 條要求永久保留的治理證據。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 內部識別碼 | 主鍵 |
| `patient_id` | `TEXT` | 哪位病人 | 外鍵 → `patients.id`，`ON DELETE NO ACTION`。與 `created_at` 組成複合索引 |
| `treatment_session_id` | `TEXT` | 哪一次療程 | 外鍵 → `treatment_sessions.id`，`ON DELETE NO ACTION`，有索引。已取消的療程不能建立記錄 |
| `record_type` | `TEXT` | 事件記錄，或依病人自報預填 | 合法值 `EVENT` / `SELF_REPORT_PREFILL`（`NursingRecordType`） |
| `template_code` | `TEXT?` | 用了哪一個事件範本 | 合法值見 `NURSING_EVENT_TEMPLATES`：`DISCOMFORT` `ACCESS_BLEEDING` `MACHINE_ALARM` `FALL` `OTHER`（待 Q-25）。自報預填為 NULL |
| `template_version` | `TEXT?` | 範本版本 | 現值 `EVENT-TEMPLATES-v2`（1005 新增「透析中低血壓處置」；之前的記錄是 v1）。範本改版後舊記錄仍能對回當時的欄位 |
| `occurred_at` | `TS?` | 事件發生時間 | 事件記錄必填，不得晚於現在（容許 5 分鐘時鐘誤差） |
| `source_symptom_report_id` | `TEXT?` | 預填所依據的那一份病人自報 | 外鍵 → `symptom_reports.id`，`ON DELETE NO ACTION` |
| `supplement_text` | `TEXT?` | 護理師補充的自由文字 | 上限 500 字，不取代結構化欄位；「其他事件」範本必填。送進模型前由閘道去識別化 |
| `prefill_text` | `TEXT` | 依勾選內容或病人自述組出的預填文字 | ⛔ **不經模型**。AI 總開關關閉時，護理師照樣可以從這段文字改起並簽核。**迭代 17.8 起**是各段（`nursing_record_sections`）以「D：」這類段名開頭、一段一行串起來的整份，與畫面上「整份複製」同一支函式（`composeNursingCopyText`）組出 |
| `record_format` | `TEXT?` | 這筆記錄用哪一種格式：DART 或 SOAP | 合法值 `DART` / `SOAP`（`NursingRecordFormat`，SRS FR-N18）。建立時照營運參數 `NURSING_RECORD_FORMAT` 決定，之後不變——切換格式只影響之後才建立的記錄。**1010 迭代 17.8 加**：之前建立的記錄為 NULL，照舊是一整段文字、沒有分段 |
| `ai_draft_text` | `TEXT?` | AI 草擬的初稿 | 只有 `DRAFT` 狀態會被寫入。AI 總開關關閉時畫面不顯示 |
| `ai_invocation_id` | `TEXT?` | 產生初稿的那一次模型呼叫 | 外鍵 → `ai_invocations.id`，`ON DELETE NO ACTION` |
| `status` | `TEXT` | 草稿或已簽核 | 合法值 `DRAFT` / `SIGNED`（`NursingRecordStatus`）。⛔ **簽核後不得再修改**：所有寫入都帶 `status=DRAFT` 條件，第二次簽核與簽核後的草擬一律回 409 |
| `final_text` | `TEXT?` | 簽核的定稿 | 上限 4000 字。迭代 17.8 起有格式的記錄由各段的定稿組出（同 `prefill_text` 的樣子），護理師「整份複製」貼進院內正式紀錄的就是這一段 |
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

### `nursing_record_sections` — 護理記錄依格式分的段（6 欄，1010 迭代 17.8）

**蒐集的意義**：SRS FR-N18（清冊 Q-37 的答覆）。院方的護理紀錄不讓本系統寫入，由護理師**複製貼上**；院內的正式紀錄是 DART 或 SOAP 的幾格，所以一段存一列，護理師可以逐段複製、貼進對應的那一格。**事件時間與院方量測值寫在段落文字裡**，不另立欄位——另立的欄位貼不過去。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 內部識別碼 | 主鍵 |
| `record_id` | `TEXT` | 屬於哪一筆記錄 | 外鍵 → `nursing_records.id`，**`ON DELETE CASCADE`**（與 `nursing_record_fields` 同一條級聯路徑的另一支，都從記錄出發，6.1 第 6 條仍是一條） |
| `section_code` | `TEXT` | 哪一段 | 合法值 `DART_D`、`DART_A`、`DART_R`、`DART_T`、`SOAP_S`、`SOAP_O`、`SOAP_A`、`SOAP_P`（`NURSING_RECORD_SECTIONS`）。兩種格式都有 A、意思不同，所以代號帶格式前綴 |
| `prefill_text` | `TEXT` | 這一段的預填 | ⛔ **不經模型**：只有護理師勾的選項、補充、病人自述、院方 API 的量測值（附量測時間，讀到 0 的不帶）。**不含姓名、病歷號**。SOAP 的 A 段只放護理師點的事件類別。「帶入處置後數值」會在 R（或 P）段後面補一句 |
| `ai_draft_text` | `TEXT?` | AI 潤飾的這一段 | 模型照段名回的文字拆回來；對不上段名的段落留空。AI 沒有時永遠是空的 |
| `final_text` | `TEXT?` | 簽核的這一段 | 未簽核為空。逐段複製的內容 |

**唯一約束**：`(record_id, section_code)`。**複製本身不存內容**：按了複製只在 `audit_logs` 記一筆 `NURSING_RECORD_COPIED`（誰、哪一筆、整份或哪一段，是不是還沒簽核），《資料庫使用規範》19.2。

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
| `weight_post_value_id` | `TEXT` | 用了哪一筆結束體重 | 同上 |
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
| `setting_key` | `TEXT` UNIQUE | 這是哪一個參數 | 合法值見 `OperationalSettingKey`：`HELP_RECURRENCE_WINDOW_HOURS`（FR-N11 的再發判定期間，暫定 72 小時）、`LABOUR_MAX_SHIFT_HOURS`、`LABOUR_MIN_REST_HOURS`、`LABOUR_MAX_DAILY_HOURS`、`LABOUR_MAX_WEEKLY_HOURS`、`LABOUR_MAX_CONSECUTIVE_DAYS`（FR-M04，暫以勞動基準法基本條件為值）。迭代 6 另加六項輪播參數：`CAROUSEL_IDLE_THRESHOLD_SECONDS`（FR-P09，預設 60 秒；0926 起用在任務畫面閒置回首頁）、`CAROUSEL_CARD_INTERVAL_SECONDS`、`CAROUSEL_DETAIL_TIMEOUT_SECONDS`（FR-P10）、`CAROUSEL_NIGHT_MODE_START_HOUR`／`CAROUSEL_NIGHT_MODE_END_HOUR`（夜間模式）、`SYMPTOM_DUE_INTERVAL_MINUTES`（透析前問卷到期的判定）。**1005 迭代 16**：卡片停留與細節頁退回兩項停用（`RETIRED_OPERATIONAL_SETTING_KEYS`，列與修改紀錄保留），另加跑馬燈三項，見第十九節。**1010 迭代 17.8**：`NURSING_RECORD_FORMAT`（護理紀錄格式，1＝DART 預設、2＝SOAP；定義帶 `choices`，畫面顯示選項名稱、不顯示數字） |
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

> **1005 迭代 16 拿掉病人端的輪播**：表不變、欄位不變。`carousel_items` 的內容改在面板底部的跑馬燈播（一則「標題：內容」，內容取 `body_text`、留白時取 `summary`），
> `carousel_view_events` 改記跑馬燈每一則的播放（`layer` 多一個值 `MARQUEE`）。下面兩張表的說明是迭代 6 寫的，與現況不同的地方各自標了 1005。
>
> **1005 迭代 17**：`carousel_items` 加七欄（核准狀態、核准者、核准時間、生成它的背景工作、公告事由、衛教主題、來源），**只播「已核准」的**；
> 「內容留白時播一句話」的退路拿掉，`summary` 不再使用。新欄位的說明在第二十節，下表的列也各自標了。

前兩張是**輪播**：第一層取自系統既有資料、第三層讀 `clinical_values`，兩層都不需要自己的表；
只有第二層（中心自己寫的衛教與公告）與瀏覽事件需要存進資料表。
第三張是**檔案匯入的欄位對應**——院方匯出檔的欄位名稱會被人改動，
那是別人的系統，不會為了我們保持不變，所以「哪一欄是理想體重」必須是資料而不是程式。

### `carousel_items` — 輪播第二層內容，1005 起是跑馬燈內容（21 欄；迭代 17 加七欄，見第二十節）

**蒐集的意義**：FR-P11 的第二層是靜態衛教與中心公告，由護理端在管理介面上架。
這是輪播三層中唯一「人自己寫」的一層，因此也是唯一需要編輯、排序與上下架的一層。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `item_kind` | `TEXT` | 這則是衛教還是公告 | 合法值 `STATIC_EDUCATION` / `ANNOUNCEMENT`（`CarouselItemKind`） |
| `title` | `TEXT` | 卡片標題 | 最長 60 字。**迭代 17 起**：上限 12 字（`marqueeLengthProblem`，以 Unicode 字元計），超過的核准不了；產生中時是空字串 |
| `summary` | `TEXT` | 卡片上顯示的一句話 | 最長 120 字。輪播畫面一次只讀得完一句。**1005**：跑馬燈只在 `body_text` 留白時播它。**迭代 17 起不再使用**：新內容一律寫空字串，舊資料保留；API 的請求與回應都沒有這個欄位。只有一句話、內容留白的舊內容整則不播。⛔ 欄位不刪（只做加法），下一版才考慮 |
| `body_text` | `TEXT?` | 點開細節頁後看到的說明 | 最長 1000 字。留空代表這張卡片不能點開（FR-P10）。**1005**：跑馬燈的「內容」——一則就是「`title`：`body_text`」，沒有細節頁。**迭代 17 起**：上限 60 字；產生中、產生失敗時為空 |
| `language` | `TEXT` | 內容語言 | BCP 47 語言標籤，預設 `zh-TW`。多語言輪播由日後的語言篩選使用 |
| `sort_order` | `INT` | 播放順序 | 小的在前；同值時以建立時間排序 |
| `active` | `BOOL` | 現在還播不播 | 預設 `true`。⛔ 不要刪列：下架即可，刪掉會讓稽核軌跡指向不存在的內容。**迭代 17 起**：只有已核准的才可能是 `true`（核准即設為 `true`；退回、撤回設為 `false`）；新列一律明確寫入 |
| `starts_at` / `ends_at` | `TS?` | 上架與下架時間 | 皆可為空，代表不限期間。過濾在資料庫做，平板拿到的就已經是「現在播得出來」的內容 |
| `created_by_id` | `TEXT` | 誰上架的 | 外鍵 → `nurses.id`，`ON DELETE NO ACTION`。**迭代 17 起**是「誰要的草稿或誰寫的公告」；隨版本帶入的是「隨版本帶入」那個系統帳號 |
| `updated_by_id` | `TEXT?` | 最後誰改的 | 外鍵 → `nurses.id`，`ON DELETE NO ACTION`。從未被改過時為空 |

**索引**：`(active, sort_order)`、（迭代 17）`(approval_status)`
**與功能開關的關係**：~~第二層開關（`CAROUSEL_LAYER_2`）的開啟條件是「至少有一則在架上的內容」——
沒有內容就開啟，病人只會看到空白的輪播，因此後端直接擋下（`FeatureFlagsService`）。~~
**1005 起**是 `MARQUEE`：開啟條件是速度經長者看過（把關在核准依據），不再以內容擋——一則都沒有時跑馬燈整條不出現，不會是空白。

### `carousel_view_events` — 輪播瀏覽事件（7 欄）

**蒐集的意義**：迭代 8 要回答「哪一類內容真的有人看」。
這張表刻意**只**回答那個問題：沒有病人、沒有綁定、沒有平板序號、沒有卡片內容。
不留可識別欄位，日後也就不會有人想從這裡回推個人行為（SRS FR-P11 補充說明）。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `occurred_at` | `TS` | 什麼時候看的 | 有索引。這是全表唯一與時間有關的欄位，且只到「事件寫入的時刻」 |
| `layer` | `TEXT` | 哪一層（1005 起：從哪裡播的） | 合法值 `LAYER_1` / `LAYER_2` / `LAYER_3`（1005 以前的輪播，由後端依 `card_kind` 推出），**1005 起另有 `MARQUEE`**（跑馬燈，`CarouselViewSource`）。一律由後端寫，不採信平板送上來的值 |
| `card_kind` | `TEXT` | 哪一類卡片（1005 起：哪一類內容） | 1005 以前是卡片種類（療程進度、今日已回報內容、衛教完成度、靜態衛教、中心公告、臨床數值）；跑馬燈只記 `STATIC_EDUCATION` / `ANNOUNCEMENT`。有索引 |
| `dwell_ms` | `INT` | 這一輪停留多久（1005 起：這一則從出現到離開多久） | 1005 以前超過 30 分鐘的一律丟棄；跑馬燈超過 10 分鐘的丟棄（標題 12 字、內容 60 字以最慢速度跑完約 73 秒，上限放寬給 1005 以前的長內容） |
| `detail_open_count` | `INT` | 這一輪被點開細節頁幾次 | 預設 0。跑馬燈沒有細節頁，一律 0 |
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
| `nav_key` | `TEXT` | 哪一個功能 | 唯一鍵。合法值為 `@hd/shared` 的 `NavItemKey`（~~17 項~~ 1007 迭代 17.6 起 16 項：`PATIENTS` 拿掉，舊環境留下的那一列不刪，載入時認不得的識別碼略過）。1006（迭代 17.1）起 `DISCHARGE_EDUCATION` 是「結束與離院衛教」頁裡的一段（定義帶 `partOf`）：沒有自己的連結，`placement` 不收 `PRIMARY`，所屬那一頁關了它也跟著關；畫面名稱 `CAROUSEL` 叫「公告與院內衛教」、`EDUCATION` 叫「結束與離院衛教」（名稱在共用常數，不在這張表） |
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

## 十七、床位圖（迭代 14）

**蒐集的意義**：護理端簡易版的畫面是一張床位圖（SRS FR-N15）。迭代 14 之前系統裡沒有「床」：
病人綁的是平板，班表記的床號只是一串字。空床也要畫得出來、平板要貼得上去、輪播內容要能只推給某一床，
床位因此成為資料。三處都**只做加法**，既有資料不必搬。

### `beds` — 床位清單（8 欄）

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 內部識別碼 | 主鍵 |
| `bed_no` | `TEXT` UNIQUE | 床號，例 `05`。只到床位層級，不含姓名與病歷號 | 格式同班表的 `BED_NO_PATTERN`（英數與連字號，最長 12 字）。一律大寫 |
| `sort_order` | `INT` | 床位圖上的順序 | 依清單順序寫 10、20、30…… |
| `active` | `BOOL` | 這一床現在在不在床位圖上 | `DEFAULT true`。**拿掉的床不刪列只停用**：舊的求助、班表紀錄寫著那個床號，要看得懂它曾經存在。有病人正在治療的床拿不掉（迭代 15 起沒有平板、院方資料說正在透析的病人也算） |
| `source` | `TEXT` | （迭代 15）這一床是護理長建的，還是院方資料帶進來的 | 合法值 `MANUAL` / `HOSPITAL_API`，`DEFAULT 'MANUAL'`。院方資料出現沒看過的床號（依營運參數 `HOSPITAL_BED_NO_FORMAT` 正規化、符合 `BED_NO_PATTERN`）就建一床、加在最後；**只新增，停用的床不會被同步再啟用** |
| `updated_by_id` | `TEXT?` → `nurses` | 最後一次調整清單的人 | 首次自動建立時為空 |
| `created_at` | `TS` | 建檔時間 | 見共通欄位 |
| `updated_at` | `TS` | 最後修改時間 | 見共通欄位 |

**預設值**：~~全新環境第一次啟動時，資料表是空的就寫入共用常數 `DEFAULT_BED_NOS`（15 床，01～15）~~。**1005 迭代 15 起後端不再預設床位**：床位由院方資料帶進來，沒接院方 API 的環境由護理長在系統管理建；`DEFAULT_BED_NOS` 只剩開發環境的 seed 在用（**1007 迭代 17.7 起是醫院的寫法**：A1、A2、A3、A5～A9、B1～B3、B5～B8 共 15 床，區碼＋數字、沒有 4 號床；原本是 01～15，已建好的開發資料庫不會自己換）。1005 之前已經建過 15 床的環境，那 15 床照舊在，接上院方資料後由護理長拿掉。床位數不設上限，床號照醫院編號。
**之後一律以資料表為準**，重新部署不會洗掉護理長的調整。整組取代走 `PUT /beds`（營運參數權限、要填理由），寫 `BEDS_UPDATED`。
**索引**：`bed_no`（唯一）、`(active, sort_order)`

### `carousel_item_targets` — 輪播內容的播放床位（5 欄）

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 內部識別碼 | 主鍵 |
| `carousel_item_id` | `TEXT` → `carousel_items` | 哪一則內容 | 內容刪除時一併刪除（實際上內容只停用不刪） |
| `bed_no` | `TEXT` | 只在這一床播 | 床號要在 `beds` 的啟用清單裡 |
| `created_by_id` | `TEXT` → `nurses` | 誰推送的 | — |
| `created_at` | `TS` | 推送時間 | — |

**一列都沒有＝全部床位**，因此迭代 14 之前的內容維持原本的行為。整組取代走 `PUT /carousel/items/:id/targets`，
寫 `CAROUSEL_ITEM_TARGETS_CHANGED`（說明寫出改前與改後的範圍）。病人端取第二層內容時，
只拿「沒有指定床位」或「指定床位裡有自己那台平板所在床號」的內容；平板沒放上床位時只看得到全部床位的內容。
**索引**：`(carousel_item_id, bed_no)`（唯一）、`bed_no`

**1007 迭代 17.7 起**另有下一張表指定平板；「一列都沒有＝全部床位」改成**兩張表都沒有列**才是全部床位。

### `carousel_item_device_targets` — 只在哪幾台平板播（5 欄，1007 迭代 17.7）

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 內部識別碼 | 主鍵 |
| `carousel_item_id` | `TEXT` → `carousel_items` | 哪一則內容 | 內容刪除時一併刪除（與上一張表同一條級聯路徑） |
| `device_id` | `TEXT` → `devices` | 只在這台平板播 | `NO ACTION`；平板要存在（`CarouselService.requireDevices`），不檢查它有沒有床號、有沒有病人 |
| `created_by_id` | `TEXT` → `nurses` | 誰推送的 | — |
| `created_at` | `TS` | 推送時間 | — |

**為什麼要這張表**：簡易版中間 1007 起是平板，把內容拖到平板時，平板不一定有床號（使用者 1007：有病人配著就要能播）。
指定的是平板，病人換床時平板跟著病人走，內容也跟著走。不改 `carousel_item_targets` 的理由：把 `bed_no` 改成可為空要重建表，違反只做加法。
寫入走同兩支端點：核准 `POST /carousel/items/:id/approve` 與播放範圍 `PUT /carousel/items/:id/targets` 的 `deviceIds`（可不帶），
與床號**一起整組取代**；稽核說明寫平板序號（「平板 DEMO-01」）。病人端的查詢（`listPlayable`）：兩張表都沒列＝全部床位；
有列時，**床號對得上或平板對得上**就播。
**索引**：`(carousel_item_id, device_id)`（唯一）、`device_id`

**`operational_settings` 多兩個鍵**（值存在既有的表裡，不是新欄位）：
`PATIENT_TASK_FEEDBACK_AFTER_MINUTES`（心情問卷在綁定後幾分鐘出現，預設 120）、
`PATIENT_TASK_EDUCATION_AFTER_MINUTES`（衛教在綁定後幾分鐘出現，預設 180）。FR-P15。
**1005 迭代 15 起兩者都從院方資料的透析開始時間起算**（沒有院方資料時仍從綁定起算），鍵與預設值不變。

---

## 十八、院方 API 介接（迭代 15）

**蒐集的意義**：1005 使用者指示院方透析清單 API **全面取代手動輸入**（SRS FR-S15、FR-S16）。病人主檔、床位、療程寫進上面幾張既有的表，
四種數值經 `ClinicalDataImportService` 寫進 `clinical_values`（來源 `HOSPITAL_API`）；這一節的兩張表只記兩件新的事：**每一次抓取的結果**，
與**有綁定平板的病人的生命徵象紀錄**。院方 API 每次回傳全中心當天到目前為止的全部紀錄，**原始回應不存**（《資料庫使用規範》第 13 條 1005 補充）。
兩張表都不帶級聯刪除：抓取紀錄是治理證據，生命徵象是照護紀錄。

### `hospital_api_fetch_runs` — 院方 API 的抓取紀錄（14 欄）

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 內部識別碼 | 主鍵 |
| `started_at` | `TS` | 這一次抓取開始的時間 | 有索引。同步現況（多久沒更新）以最近一筆成功的這一欄計算 |
| `finished_at` | `TS?` | 結束的時間 | 抓取開始時先建一列（生命徵象要指得到它），結束時補 |
| `outcome` | `TEXT` | 結果：成功、失敗、拒收 | 合法值 `SUCCESS` / `FAILED` / `REFUSED`（`HospitalFetchOutcome`）。`REFUSED`＝正式環境設定下收到模擬院方 API 的回應，整次作廢（DEP-46） |
| `attempt_count` | `INT` | 含重試共試了幾次 | 30 秒逾時、失敗再試 3 次，最多 4 |
| `http_status` | `INT?` | 院方伺服器回的狀態碼 | 連不上時為空 |
| `row_count` | `INT` | 回應裡有幾列 | `DEFAULT 0` |
| `dialysis_count` | `INT` | 回應裡有幾次透析（依病歷號＋開始時間分組） | `DEFAULT 0`。一位病人的一次透析＝全有或全無的單位 |
| `rejected_count` | `INT` | 其中幾次因格式不符整個不寫入 | `DEFAULT 0`。格式不符的每一次另寫 `HOSPITAL_API_DIALYSIS_REJECTED` 稽核（同一天同一組原因只寫一次） |
| `vital_record_count` | `INT` | 這一次新增了幾筆生命徵象紀錄 | `DEFAULT 0`。同一份回應抓兩次，第二次是 0 |
| `content_hash` | `TEXT?` | 回應內容的雜湊 | SHA-256。**原始內容不存**——同一份回應抓兩次看得出來就夠了 |
| `simulated` | `BOOL` | 回應是不是模擬院方 API 給的 | 依回應的模擬標頭（`x-hd-simulated`）判斷。開發機與模擬部署為 true |
| `error_message` | `TEXT?` | 失敗的原因，一句話 | ⛔ **不得含院方 API 的位址與任何一個欄位值**。由程式自己寫的句子組成（「逾時」「連線被拒」「回應格式不符」），不轉錄院方的回應 |
| `duration_ms` | `INT?` | 花了多久 | — |

**誰寫這張表**：只有後端的同步排程（預設每 3 分鐘，營運參數）與「立即同步」。
**稽核只寫狀態變了的那一次**：開始失敗（`HOSPITAL_API_FETCH_FAILED`）、恢復（`HOSPITAL_API_FETCH_RECOVERED`）、拒收（`HOSPITAL_API_FETCH_REFUSED`）；
每 3 分鐘一筆的成功不寫稽核，這張表本身就是紀錄。⚠️ 一天約 480 列，留存期限待 Q-05；定案前不刪。

### `dialysis_vital_records` — 院方的生命徵象紀錄（13 欄）

**只收這次療程有綁定平板的病人**（SRS FR-S16、規範第 13 條 1005 補充「最小蒐集」）：病人端「本次透析」面板只需要他們的，其餘病人的紀錄留在院方。
剛配平板的病人不會少掉前面幾點——下一次抓取本來就回傳當天全部。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 內部識別碼 | 主鍵 |
| `patient_id` | `TEXT` → `patients` | 哪一位病人 | `ON DELETE NO ACTION` |
| `treatment_session_id` | `TEXT` → `treatment_sessions` | 哪一次療程 | `ON DELETE NO ACTION`。與 `recorded_at` 組成索引，面板依它取一次療程的全部紀錄 |
| `fetch_run_id` | `TEXT` → `hospital_api_fetch_runs` | 第一次寫入這一筆的那次抓取 | 來源可追溯（規範第 13 條）。有索引 |
| `dialysis_started_at` | `TS` | 院方資料的透析開始時間 | 去重鍵的一部分。**不用透析次數去重**（參考調查 9.2 第 5 項：意義不確定） |
| `recorded_at` | `TS` | 院方資料的紀錄時間 | 沒有秒。同一分鐘兩筆只留後面那一列 |
| `sbp_mmhg` | `INT?` | 收縮壓 | 院方第 36 欄（每一筆紀錄的血壓，不是第 22～25 欄的開始／結束血壓）。空字串存空值；0 照實存，顯示時才擋 |
| `dbp_mmhg` | `INT?` | 舒張壓 | 第 37 欄。同上 |
| `pulse_bpm` | `INT?` | 脈搏 | 第 38 欄 |
| `uf_cumulative_ml` | `INT?` | 機器累計的脫水量（毫升） | 第 46 欄。⚠️ **單位當公升讀、乘 1000**，與其他容量欄同單位；第三次進院以探測工具的數值大小分布確認，錯了改換算那一行 |
| `weight_pre_g` | `INT?` | 透析前體重（公克） | 第 13 欄，透析層級的值，每一列重複；乘 1000 存公克 |
| `uf_set_ml` | `INT?` | 設定脫水量（毫升） | 第 19 欄。面板脫水量圖的參考線用它，**不用目標脫水量**（實作規格書 0.5：與機器累計同基準） |
| `created_at` | `TS` | 寫入時間 | 見共通欄位 |

**唯一約束**：`(patient_id, dialysis_started_at, recorded_at)`——資料表層的最後一道防線，同步本身先查過已寫的紀錄時間才寫。
**寫入時**推一則「有新紀錄」給那一台平板（`GET /device/stream`，事件不帶數值），並寫一筆 `HOSPITAL_VITALS_RECORDED` 稽核（一次抓取一筆，寫幾筆、幾位病人）。

**`operational_settings` 多四個鍵**：`HOSPITAL_API_FETCH_INTERVAL_MINUTES`（抓取頻率，預設 3、範圍 1～30）、
`HOSPITAL_API_STALE_ALERT_MINUTES`（多久沒更新就提示，預設 10）、`HOSPITAL_END_CONFIRM_AFTER_MINUTES`（過了預計結束多久標示待確認下機，預設 60；1007 迭代 17.5 起預計結束一律是開始後四小時）、
`HOSPITAL_BED_NO_FORMAT`（院方床位轉床號：0 原樣、1 改字母在前、2 改數字在前，預設 0）。

**院方 API 的位址不在資料庫裡**：只在主機設定目錄的 `.env`（DEP-46），不寫進資料庫、日誌、稽核或任何回應。

---

## 十九、「本次透析」面板與跑馬燈（迭代 16）——沒有新表

1005 病人端首頁中間那一區由輪播改成「本次透析」面板與跑馬燈（SRS FR-P09～P11）。**一張表、一個欄位都沒加**，讀的是既有的表：

| 畫面上的東西 | 讀哪裡 | 怎麼讀 |
|---|---|---|
| 血壓、累積脫水量兩張圖，脈搏 | `dialysis_vital_records` | 這次療程（`treatment_session_id`）的全部紀錄；值是 0 或空的那一筆不送 |
| 「預計」參考線、透析前體重 | 同上 | `uf_set_ml`、`weight_pre_g` 是透析層級的值，取最後一筆不是 0 的 |
| 理想體重 | `clinical_values` 的 `DRY_WEIGHT` | 目前有效、不是 0、最近的一筆；不限這一次透析，不是今天的畫面會帶月日 |
| 目標脫水量 | `clinical_values` 的 `UF_TARGET` | 同上，但**只認與透析開始同一天的**——上一次透析的不拿來當今天的 |
| 跑馬燈 | `carousel_items`（＋`carousel_item_targets`、`carousel_item_device_targets`） | 在架上、期間內、指定給這一床、這台平板（1007 迭代 17.7）或全部床位；夜間一則都不送 |
| 每一則的播放 | 寫 `carousel_view_events` | `layer = MARQUEE` |

**送到平板的只有畫面要用的欄位**：時間與值。SRS 取捨表標「不顯示」的東西（靜脈壓、血流速、透析液設定、體溫、肝素、透析器、血管通路、低血壓預測、姓名、病歷號）
本來就不在這幾張表裡，或在表裡但不讀。平板端的本機快取掛在 Session 前綴底下，綁定解除時一併清掉。

**`operational_settings` 多三個鍵**：`MARQUEE_CHARS_PER_MINUTE`（跑馬燈速度，預設 120 字／分鐘＝每秒 2 字，範圍 60～180）、
`MARQUEE_LEAD_PAUSE_SECONDS`（每一則開頭靜止，預設 3）、`MARQUEE_GAP_SECONDS`（兩則之間的空白，預設 5）。速度經長者試看之後，採用的值與試看結果寫在那一列的 `last_reason`。
**停用兩個鍵**：`CAROUSEL_CARD_INTERVAL_SECONDS`、`CAROUSEL_DETAIL_TIMEOUT_SECONDS`（跑馬燈不換卡、沒有細節頁）。列留在表裡，畫面上不再出現、改不到。

**`feature_flags` 多兩個鍵**：`TODAY_PANEL`（預設開啟）、`MARQUEE`（預設關閉）；**停用三個鍵**：`CAROUSEL_LAYER_1`～`3`，列與切換紀錄保留。

---

## 二十、跑馬燈內容的 AI 草稿與核准（迭代 17）——沒有新表

1005 SRS FR-N17：護理師不再寫衛教與公告，只核准 AI 生成的標題與內容；「一句話」拿掉。**只做加法**：`carousel_items` 加七欄，遷移 `iteration17_marquee_approval`。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `approval_status` | `TEXT` | 這一則現在是產生中、待核准、已核准、已退回還是產生失敗 | 合法值 `GENERATING` / `PENDING` / `APPROVED` / `REJECTED` / `FAILED`（`CarouselApprovalStatus`），預設 `PENDING`。**病人端的查詢（`listPlayable`）只撈 `APPROVED`**——沒核准的不會被讀出來，不是讀出來再藏。核准、退回都是條件式更新（只動 `PENDING` 的那一列），兩人同時按不會核准兩次。遷移時既有的列由 `UPDATE … WHERE approval_status = 'PENDING'` 改成 `APPROVED`：它們是核准制度以前護理師直接上架的，本來就在播。⛔ 預設值刻意不是 `APPROVED`：新程式忘了指定時寧可不播 |
| `approved_by_id` | `TEXT?` | 誰核准的 | 外鍵 → `nurses.id`，`ON DELETE NO ACTION`。核准制度以前上架的內容為空。撤回成待核准時清掉（原本的核准者留在稽核軌跡 `CAROUSEL_ITEM_REOPENED`） |
| `approved_at` | `TS?` | 什麼時候核准、上架 | 同上。畫面上「核准制度以前上架」就是這一欄為空的已核准內容 |
| `ai_job_id` | `TEXT?` | 生成它的那一件背景工作 | 外鍵 → `ai_jobs.id`，`ON DELETE NO ACTION`。經它找得到那一次模型呼叫（`ai_jobs.ai_invocation_id` → `ai_invocations` 的模型、提示與輸出）；重新生成過的，最後一次那一筆記在 `ai_jobs` 上，每一次都在 `ai_invocations` |
| `announcement_reason` | `TEXT?` | 公告事由：護理師輸入的那一句（例如「10/10 停診」） | 最長 100 字（`ANNOUNCEMENT_REASON_MAX_LENGTH`）。AI 只依它寫，送進模型的只有這一句。衛教與護理師直接寫的公告為空 |
| `topic_code` | `TEXT?` | 衛教草稿的主題 | 附錄 C.6 的主題識別碼（衛教題庫 `quiz_topics.code`，`EDU_*`），**只能是啟用中的主題**。刻意不設外鍵，與 `education_contents.topic_code` 同一個寫法。公告為空。挑「最久沒生成過的主題」靠這一欄 |
| `source` | `TEXT` | 這一則是怎麼來的 | 合法值 `MANUAL`（護理師撰寫，含核准制度以前的全部內容）/ `AI_GENERATED` / `BUNDLED`（隨版本帶入）（`CarouselItemSource`），預設 `MANUAL` |

**隨版本帶入的草稿**：院內推論端點就位之前（Q-07），衛教草稿由開發端事先生成、存在 `apps/api/src/modules/carousel/marquee-bundle.ts`，
**首次啟動時匯入為 `PENDING`、`source = BUNDLED`**，建立者是「隨版本帶入」那個系統帳號。每一則寫一筆 `MARQUEE_DRAFT_IMPORTED` 稽核（記下生成的模型與閘道設定），
整批再寫一筆以 `MARQUEE-BUNDLE-<版本>` 為 `target_id` 的——**有這一筆就不再匯入**，護理師全部退回之後重新啟動也不會再倒一次。

**稽核軌跡多七個動作**：`MARQUEE_DRAFT_REQUESTED`（要一份草稿）、`MARQUEE_DRAFT_GENERATED`（生成完成，記模型與次數）、`MARQUEE_DRAFT_IMPORTED`、
`CAROUSEL_ITEM_APPROVED`（記核准者、播放範圍、上下架時間；修改後核准時記下改前與改後＝留稿）、`CAROUSEL_ITEM_REJECTED`、`CAROUSEL_ITEM_REOPENED`、`CAROUSEL_ITEM_SCHEDULE_CHANGED`。
`CAROUSEL_ITEM_UPSERTED` 留著，迭代 17 起只用在「護理師寫一則公告（待核准）」。

**沒有送進模型的東西**：任何病人資料。衛教只送主題名稱與主題重點，公告只送事由；`ai_invocations.patient_id` 一律為空。

## 二十一、規則引擎與三項高風險功能（迭代 18）

**蒐集的意義**：風險分層（FR-P03）、療程中預警（FR-P05）、劑量調整參考（FR-N06）與適足性的趨勢推估（FR-N07 的預測部分）**一律由規則計算，不經語言模型**（SRS FR-R01）。
這一節的七張表記四件事（第七張 `rule_gate_changes` 是 1010 迭代 18.1 加的書面確認閘門登記紀錄）：**規則與它的每一個版本**（門檻、文字範本、書面依據出處）、**每一次比對**（對誰、用哪一版、引用了哪幾筆資料、組出什麼字）、**誰檢視過、有沒有採納**（FR-R06、FR-N13）。
規格書列的是四張；門檻值與引用的資料各拆一張明細表，不用 JSON 欄位承載（規範 6.1 第 2 條）。遷移 `iteration18_rule_engine`，只做加法。
級聯刪除只留「版本 → 門檻」「比對 → 引用資料」兩條；其餘一律 `NO ACTION`——這些是治理紀錄，留存期限定案前不刪。

> ⚠️ **這一節的表才是「系統的判讀」放的地方**。第四節的症狀與求助是病人自己說的，第十八節的生命徵象是院方量的；把它們拿來比門檻、組成文字的，只有這裡。
> 每一筆比對都標了**合成資料或真實病人**（`data_mode`）與**當時版本是草稿還是生效中**：書面確認閘門沒開（`rule_gate_changes` 最新一列不是登記；迭代 18 時看的是院內主機設定檔，18.1 起改在系統管理登記）時，`data_mode = REAL` 的列一筆都不會出現。

### `rule_definitions` — 規則（7 欄）

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 內部識別碼 | 主鍵 |
| `rule_code` | `TEXT` | 規則代號，印在每一則輸出裡（例如 RISK-IDWG-01） | 唯一。第一次啟動寫入六條預設規則（`DEFAULT_RULE_DEFINITIONS`），之後不再寫規則本身（版本見下一張表的 `created_by_id`）；畫面上沒有新增規則的入口 |
| `name` | `TEXT` | 規則名稱 | — |
| `feature` | `TEXT` | 屬於哪一項功能 | 合法值 `RISK_STRATIFICATION` / `INTRA_DIALYSIS_ALERT` / `DOSE_REFERENCE` / `ADEQUACY_PREDICTION`（`RuleFeature`，就是那一項的功能開關識別字）。有索引 |
| `kind` | `TEXT` | 比對的形態（體重增幅、收縮壓低於門檻的次數、同一時段…） | 合法值見 `RuleKind`（六種）。決定後端用哪一個評估器（`modules/rules/evaluators.ts`）；新增一種形態才要改程式 |
| `active` | `BOOL` | 整條規則還用不用 | `DEFAULT true`。目前沒有畫面會改它 |
| `created_at` | `TS` | 寫入時間 | 見共通欄位 |

### `rule_versions` — 規則版本（15 欄）

**一經使用即不可修改**（實作規格書 3.6 第 1 條）：有任何一筆 `rule_evaluations` 指向的版本，內容改不了；要改門檻就出新版本。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 內部識別碼 | 主鍵 |
| `definition_id` | `TEXT` → `rule_definitions` | 哪一條規則 | `ON DELETE NO ACTION`。與 `version_no` 唯一 |
| `version_no` | `INT` | 第幾版 | 從 1 起，新版本接在最大的後面 |
| `status` | `TEXT` | 草稿、生效中、已停用 | 合法值 `DRAFT` / `ACTIVE` / `RETIRED`（`RuleVersionStatus`），有索引。**草稿只對合成資料病人執行**；`source_citation` 是空的不得為 `ACTIVE`（FR-R02）；同一條規則同時只有一版 `ACTIVE`，新的生效時舊的改 `RETIRED`（同一個交易）；`RETIRED` 不能再生效 |
| `met_template` | `TEXT` | 符合時的文字範本 | 大括號裡是這一種規則登記過的欄位（`RULE_KIND_BY_KEY[kind].placeholders`）。⛔ 出現 `RULE_CONCLUSION_WORDS`（風險、診斷、建議、低血壓…）存不進去（FR-R04）。最長 300 字 |
| `not_met_template` | `TEXT` | 未符合時的文字範本 | 同上 |
| `source_citation` | `TEXT?` | 臨床端書面依據的出處 | 空值＝標不了生效。預設規則只有兩條收縮壓相關的有值（同院 IDH 系統） |
| `protocol_excerpt` | `TEXT?` | 逐字照抄的 protocol 條文 | 劑量調整參考（`HB_OUT_OF_RANGE`）必填；符合時原樣接在輸出後面。不受結論字詞的限制（是原文引用） |
| `note` | `TEXT?` | 備註 | 預設規則：兩條收縮壓的寫套用同院 IDH 系統；其餘四條迭代 18 寫「合成資料示範值」，**18.1 起寫「開發端依文獻選的建議值，尚未經臨床端確認，不是書面依據」與出處**（文獻不填進 `source_citation`） |
| `created_by_id` | `TEXT?` → `nurses` | 誰建立的 | `ON DELETE NO ACTION`。系統建立的為空（畫面顯示「系統預設」）：第一次啟動寫入的第 1 版，以及 **18.1 起預設規則的門檻或備註改了時，啟動時補上的草稿版本**（`RulesService.upgradeDefaults`：沒有一版的門檻與備註跟新的一樣才補，有 `ACTIVE` 版本的規則不補） |
| `created_at` | `TS` | 建立時間 | — |
| `activated_by_id` | `TEXT?` → `nurses` | 誰標為生效 | `ON DELETE NO ACTION`。只有系統管理者標得了 |
| `activated_at` | `TS?` | 什麼時候標為生效 | — |
| `activation_reason` | `TEXT?` | 標為生效的依據（誰確認的、哪一份文件） | 必填才標得了；同時寫進稽核 `RULE_VERSION_ACTIVATED` |
| `retired_at` | `TS?` | 什麼時候被較新的版本取代 | — |

### `rule_version_parameters` — 規則版本的門檻（4 欄）

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 內部識別碼 | 主鍵 |
| `version_id` | `TEXT` → `rule_versions` | 哪一版 | `ON DELETE CASCADE`（主表 → 自己的明細）。與 `param_key` 唯一 |
| `param_key` | `TEXT` | 哪一項門檻 | 合法值見那一種規則的 `params`（例如 `gainPercentTenths`、`nadirLowMmhg`）。畫面只顯示中文名稱與單位 |
| `value_scaled` | `INT` | 門檻值 | **整數＋小數位數**（小數位數由參數定義決定），不用浮點數（規範 6.2）：4.0% 存 40、1.20 存 120。超出參數定義的上下限存不進去（只擋打錯，不是臨床判斷） |

### `rule_evaluations` — 每一次比對（13 欄）

**同一版規則對同一筆資料只比一次**（`rule_version_id`＋`patient_id`＋`subject_key` 唯一）：定時比對（每 3 分鐘）與護理師按「立即比對」撞在一起，唯一鍵擋下後一筆。資料不夠（例如還沒有透析前體重）就不寫這一列。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 內部識別碼 | 主鍵 |
| `rule_version_id` | `TEXT` → `rule_versions` | 用哪一版 | `ON DELETE NO ACTION`。**永遠指向當時的版本**，之後出了新版本也不改 |
| `patient_id` | `TEXT` → `patients` | 哪一位病人 | `ON DELETE NO ACTION`。與 `evaluated_at` 組成索引 |
| `treatment_session_id` | `TEXT?` → `treatment_sessions` | 哪一次療程 | `ON DELETE NO ACTION`。風險分層與療程中預警才有；劑量調整參考與適足性推估為空 |
| `subject_key` | `TEXT` | 比的是哪一筆資料 | `session:<療程>`、`hb:<血紅素那一筆臨床數值>`、`ktv:<最近一次適足性計算>` |
| `feature` | `TEXT` | 屬於哪一項功能 | 冗餘保留，待檢視依開關篩選不必再 join 兩層 |
| `met` | `BOOL` | 符不符合 | 只有 `true` 的是要檢視的輸出；與 `evaluated_at` 組成索引 |
| `statement` | `TEXT` | 組出來的那一句事實陳述 | 由版本範本組出，**不經模型**（FR-R01、FR-R04）。不含姓名與病歷號；劑量調整參考符合時條文原樣接在後面 |
| `data_mode` | `TEXT` | 這位病人是合成資料還是真實病人 | 合法值 `SYNTHETIC` / `REAL`（`RuleDataMode`），依病歷號前綴判定（規範第 10 條）。閘門沒開時不會有 `REAL` |
| `version_status_at_run` | `TEXT` | 比對當下這一版是草稿還是生效中 | `DRAFT` 只會出現在 `SYNTHETIC` |
| `trigger` | `TEXT` | 定時比對還是有人按了立即比對 | 合法值 `SCHEDULED` / `MANUAL`（`RuleTrigger`） |
| `triggered_by_id` | `TEXT?` → `nurses` | 誰按的 | `ON DELETE NO ACTION`。定時比對為空 |
| `evaluated_at` | `TS` | 比對的時間 | — |

### `rule_evaluation_inputs` — 一次比對引用的資料（8 欄）

「點開看得到完整依據」（FR-R03）的那一半。來源不只一張表，比照 `audit_logs` 以來源型別＋識別碼記錄，**並留下當時的值**——來源那一列之後被更正，依據照樣看得到比對當下的數字。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 內部識別碼 | 主鍵 |
| `evaluation_id` | `TEXT` → `rule_evaluations` | 哪一次比對 | `ON DELETE CASCADE`（主表 → 自己的明細）。有索引 |
| `sort_order` | `INT` | 顯示順序 | 從 1 起 |
| `source_type` | `TEXT` | 資料來自哪裡 | 合法值 `VITAL_RECORD` / `CLINICAL_VALUE` / `HELP_REQUEST` / `TREATMENT_SESSION` / `ADEQUACY_CALCULATION`（`RuleInputSource`） |
| `source_id` | `TEXT` | 那一列的識別碼 | **刻意不設外鍵**（來源表不只一種）。對到 `dialysis_vital_records`、`clinical_values`、`help_requests`、`treatment_sessions`、`adequacy_calculations` 其中之一 |
| `label` | `TEXT` | 這一筆是什麼（「本次透析前體重」「求助『頭暈、冒冷汗、快昏倒』」…） | 由評估器組出；求助用按下當時的字（`help_requests.category_label`） |
| `value_text` | `TEXT` | 當時的值（含單位） | 例如「64.0 kg」「開始後第 120 分鐘 86 mmHg（開始收縮壓 130，門檻 90）」 |
| `observed_at` | `TS?` | 那一筆的時間（量測時間、按下的時間） | — |

### `rule_evaluation_reviews` — 檢視與是否採納（6 欄）

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 內部識別碼 | 主鍵 |
| `evaluation_id` | `TEXT` → `rule_evaluations` | 哪一則輸出 | `ON DELETE NO ACTION`。有索引。**一筆都沒有＝待檢視**，即時總覽一直顯示；可以不只一筆（換人看、改判斷），以最新的為準 |
| `reviewer_id` | `TEXT` → `nurses` | 誰檢視的 | `ON DELETE NO ACTION` |
| `adopted` | `BOOL` | 有沒有採納 | 只能對 `met = true` 的比對登記 |
| `not_adopted_reason` | `TEXT?` | 未採納的原因 | 選填，最長 300 字；採納時一律為空。連同採納與否寫進稽核 `RULE_OUTPUT_REVIEWED` |
| `reviewed_at` | `TS` | 檢視的時間 | — |

**稽核軌跡多九個動作**：`RULE_DEFAULTS_SEEDED`（第一次啟動寫入預設規則）、`RULE_VERSION_CREATED`、`RULE_VERSION_UPDATED`（只有沒用過的草稿）、`RULE_VERSION_ACTIVATED`、
`RULE_VERSION_CHANGE_REJECTED`（沒有出處標為生效、改用過的版本、範本有結論字詞…）、`RULE_EVALUATION_REQUESTED`（按了立即比對）、`RULE_EVALUATION_BLOCKED`（真實病人被閘門擋下；定時比對同一位病人一天記一筆）、
`RULE_OUTPUT_REVIEWED`、`RULE_GATE_STATE_RECORDED`（啟動時閘門狀態與上一次記的不同才記；**18.1 起不再產生**）。
18.1 再多一個：`RULE_GATE_CHANGED`（系統管理者登記或取消登記書面確認，記文號與理由）。預設規則補上草稿版本時沿用 `RULE_DEFAULTS_SEEDED`，`detail` 寫「補上草稿版本」與哪幾條第幾版。

### `rule_gate_changes` — 書面確認閘門的登記紀錄（6 欄，迭代 18.1）

法務／資訊室對 TFDA 分類的書面確認（SRS FR-R08）。**只增不改**：每一次登記或取消登記都是新的一列，**最新一列就是現況**；一列都沒有＝從來沒登記過（閘門沒開）。
迭代 18 時閘門是院內主機設定檔的 `HIGH_RISK_WRITTEN_CONFIRMATION`；1010 使用者指示改放進系統管理，設定檔不再有這一項。

| 欄位 | 型別 | 給人看的說明 | 給 Agent 的說明 |
|---|---|---|---|
| `id` | `TEXT` | 內部識別碼 | 主鍵 |
| `opened` | `BOOL` | 這一次是登記（開）還是取消登記（關） | 現況＝最新一列的這一欄（同時要有 `reference`） |
| `reference` | `TEXT?` | 書面確認的文號 | 登記時必填、最長 200 字（`RULE_GATE_REFERENCE_MAX_LENGTH`）；取消登記時為空。只是給人核對的字，系統不解析 |
| `reason` | `TEXT` | 理由 | 必填。連同文號寫進稽核 `RULE_GATE_CHANGED` |
| `changed_by_id` | `TEXT` → `nurses` | 誰登記或取消的 | `ON DELETE NO ACTION`。只有系統管理者（`system:configure`）做得到 |
| `changed_at` | `TS` | 什麼時候 | `DEFAULT now`，有索引（取最新一列用） |

**沒有送進模型的東西**：這一節的全部。規則模組不引用 AI 閘道與模型供應者（`verify:iteration18` 第 1 步逐檔檢查），比對前後 `ai_invocations` 一筆都不多（`verify:iteration18:api` 第 6 步）。

---

## 附錄 A：資料不流向哪裡

同樣重要的是**沒有**蒐集什麼。以下都不在資料庫裡，且都是刻意的：

| 沒有蒐集 | 原因 |
|---|---|
| 透析處方、透析機台參數；**沒有綁定平板的病人的生命徵象** | 本系統不是電子病歷；機台整合屬未來擴充。1005 迭代 15 起生命徵象只收**有綁定平板的病人**（`dialysis_vital_records`，給病人端面板用），院方 51 欄裡本系統不用的欄位（透析器、肝素、透析液參數等）一律不讀不存 |
| 院方 API 的原始回應 | 規範第 13 條 1005 補充：回應含全中心當天的資料。只留內容雜湊（`hospital_api_fetch_runs`），原始內容不寫進資料庫、日誌、備份目錄 |
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
| 病人端首頁（1005 前是輪播畫面，之後是「本次透析」面板與跑馬燈）上的病人姓名與病歷號 | 治療區內鄰床可見。床位分配只到 `bed_no` 層級（SRS 5.1 補充說明）。面板與跑馬燈由後端組好再送到平板，這條規則只在一處判定 |
| 播放紀錄（1005 前是輪播瀏覽事件）中的病人、綁定、平板與內容 | `carousel_view_events` 只回答「哪一類內容有播到」；那個問題不需要知道是誰在看 |
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
| [1007](https://94sh09sh19sh.github.io/hd-docs/1007/reference/data-dictionary/) | 2026-10-07 | 改寫到迭代 17.7：迭代 15 院方 API 介接（同步紀錄、院方紀錄的來源欄位）、迭代 16 跑馬燈播放紀錄、迭代 17 草稿核准欄位、迭代 17.7 `carousel_item_device_targets`（59 張表 593 個欄位）；開關清單補 `LAB_VALUE_FEATURES`、`TODAY_PANEL`、`MARQUEE`、`MANUAL_PATIENT_CREATE`；開發 seed 床號改成醫院格式 |
| [0930](https://94sh09sh19sh.github.io/hd-docs/0930/reference/data-dictionary/) | 2026-09-30 | 改寫到迭代 14.2：新增 `beds`、`carousel_item_targets`（56 張表 547 個欄位），平板的外殼版本與所在床位、病人端任務時點的營運參數、求助「其他」框的開關；備份另存同名 .sha256 |
| [0923](https://94sh09sh19sh.github.io/hd-docs/0923/reference/data-dictionary/) | 2026-09-23 | 補到 54 張表 529 個欄位：迭代 7 的執行環境與版本更新紀錄（第十五節）、迭代 9 的導覽版位與內容資料化（第十六節）；附錄 C 的內容全部搬進資料表，三組帶版本號的內容用同一個形狀，`help_requests` 多一欄 `category_label`，`symptom_answers` 多一張複選子表 |
| [0916](https://94sh09sh19sh.github.io/hd-docs/0916/reference/data-dictionary/) | 2026-09-16 | 補到 39 張表 408 個欄位：改述為 SQLite 現況，補上迭代 3 的五張表與迭代 4 的十四張表，新增第十二～十四節（求助處理與可設定暫代值、班表與成效基準、閒置輪播與檔案匯入）|
| [0909](https://94sh09sh19sh.github.io/hd-docs/0909/reference/data-dictionary/) | 2026-09-09 | 首次定版 |

[← 回進度首頁](../index.md)
