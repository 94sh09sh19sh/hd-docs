# 血液透析平板照護輔助系統 — 技術進度報告

**適用讀者**：接手或協作的工程師 **報告日期**：2026-10-18 **版本**：迭代 25 完成（master；緊急通報：頂端橫幅修剪、床邊前速覽、求助處置護理紀錄連動） **Repo**：`94sh09sh19sh/hd-tablet-care`

> **1010 補記**：同一天完成**迭代 17.8**（護理紀錄移到主列、DART／SOAP 分段與複製貼上、緊急回報的圖示自畫）、**迭代 18**（規則引擎與三項高風險功能，加上適足性推估）與**迭代 18.1**（書面確認閘門從 `.env` 改放進系統管理、四條規則換成依文獻選的建議門檻），見第 6、7 節；同日再完成**迭代 19**（管理儀表板、獎勵制度與對外揭露：資料分級守衛、十張新表、23 條路由、對外展示環境），見第 6 節「迭代 19」；遊戲化寫成兩份其他文件並排成迭代 20～23，同日完成**迭代 20**（遊戲化之一：平板現有功能的遊戲化——完成記號、我的衛教小本子、病友小撇步、跑馬燈的「你知道嗎」、被聽見的回覆；三個開關、三張新表、8 條路由），見第 6 節「迭代 20」；同日再完成**迭代 21**（遊戲化之二：透析小花園、送花、共同花園——平板與後端跑同一支計算、斷線照序號補送、JSON 盤面快照的唯一例外、程式產生的植物插畫；三個開關、六張新表、8 條路由），見第 6 節「迭代 21」。
>
> **1011 補記**：完成**迭代 22**（遊戲化之三：麻將連連看——保證有解的發牌、最多轉兩個彎的連線、卡住自動重排、CC0 牌面清過 SVG 並改深棕；今日牌局與人數門檻；狀態評估彙整讀的時候才算；社工、醫師兩個唯讀角色與「病人詳細資訊」一頁；兩個開關、`game_events` 加十二欄、6 條路由），見第 6 節「迭代 22」。
>
> 同日再完成**迭代 23.1**：迭代 23（記憶相簿）因為畫圖量大切成三次子迭代（《[迭代 23 的三次子迭代](https://94sh09sh19sh.github.io/hd-docs/latest/notes/iteration-23-split/index.md)》）。23.1 只有內容與圖：子文件《[記憶相簿的主題](https://94sh09sh19sh.github.io/hd-docs/latest/notes/dialysis-gamification-album/index.md)》、`@hd/shared` 的 `album.ts`（起始 60 張的預設內容，還沒有程式讀它）、圖卡產生器 `scripts/album-art/`（白名單元素與屬性、全部避開紅色的色票）與第一批 30 張 SVG（`apps/patient-pwa/src/assets/album/`）、`verify:iteration23-1`；**沒有新的資料表、端點與畫面**。
>
> 同日再完成**迭代 23.2**：第二批 30 張 SVG（每個主題 5 張，照子文件第 4 節的順序接在各主題第一批後面），起始 60 張畫完、合計約 500 KB；`verify:iteration23-2`（由 23-1 複製，步驟 4 改成 60 張都要有圖檔，並比對產生器的順序與 `ALBUM_SEED_CARDS` 相同）。第一批沒有改；仍然**沒有新的資料表、端點與畫面**。
>
> 同日再完成**迭代 23.3**，迭代 23 做完：四張新表只做加法（`album_cards`、每一版 `album_card_versions`、選項 `album_card_options`、每看完一張的 `album_responses`）；預設 60 張啟動時只補資料表裡還沒有的代號；開關 8 上架中不到 60 張或有主題沒有時開不了；病人端相簿（不論對錯都翻、答案只用粗框、三個貼紙、每張跳得過、沒有「錯」與輸入框）；出卡順序沒有亂數、平板與伺服器同一支計算；共同記憶照最低人數門檻、「想起某個人」不彙總；護理端「可以聊的話題」與「記憶相簿的圖卡」（改字就是新的一版、下架隨時可以）；字型子集重做。後端路由 203 → 209 條、90 張表、150 種稽核動作、九個遊戲化開關到齊。細節在實作規格書 4.23。
>
> **1017～1018 補記**：完成**迭代 24**（遊戲化之五：花園與相簿的擴充，切成四次子迭代）。24.1 花 12 → 36 種、24 種小訪客的清單與插畫；24.2、24.3 相簿第三、四批共 60 張，120 張、十二個主題畫完；24.4 程式——種子袋每次療程補到 3 顆（`@hd/shared` 的常數、不是營運參數）、小訪客（平板點開花園時送一步 `LOOK`，一半的機會加保底、照花園編號算、沒點不離開）、花園快照第 2 版（第 1 版由程式升級）、花園圖鑑照分類排並列出空格、相簿圖鑑「我的相簿」（從作答算、空格連代號都不給）；一張新表 `garden_visitors`、`game_events.visitor_code`、一支新端點（210 條路由）。見第 6 節「迭代 24」
>
> **1018 補記（迭代 25）**：緊急通報三次子迭代同一天做完（實作規格書 4.25）。25.1 `realtime-context.tsx` 的 `pruneAlerts`；25.2 院方 API 多收十二欄（`dialysis_vital_records` 加四欄、新表 `dialysis_session_settings`）、`GET /help-requests/:id/bedside`、兩版共用的 `bedside-brief.tsx`；25.3 `nursing_records.source_help_request_id` 與記錄類型 `HELP_RESPONSE`、結案同一個交易建草稿、三支護理紀錄端點。路由 210 → 214、92 張表、151 種稽核動作
>
> 本版由 0930 定版（迭代 14.5 時點）改寫。0930 之後的主要變化： **1001 第二次進院 B 級部分成功**——容器在院內主機上起來，護理端登入 `Failed to fetch`（`CORS_ORIGINS` 不放行護理端的來源），見部署手冊第十四冊之四、第十五冊之三； **1005 新版需求**：院方透析清單 API 全面取代手動輸入、輪播換成「本次透析」面板與跑馬燈、跑馬燈內容 AI 生成護理師核准，排成**迭代 15～17，同日完成**（實作規格書 0.5、4.13～4.15）。 三個迭代都在模擬院方 API 上驗收；院方 API 的實際長相要第三次進院以探測工具看一次（實作規格書 4.19）。
>
> 0909 之後的完整脈絡：需求於 0910 改為 v2.0（SaMD 三項改為有條件納入、資料庫改 SQLite、封閉網路）；迭代 3～6 完成資料層遷移、AI 輔助內容、求助處理與班表、閒置輪播與檔案匯入； 迭代 7～10 是第一次進院前的缺陷修正、介面重做、內容資料化與安裝包；**0922 第一次進院失敗之後**，迭代 11～14 把交付方式換成 Docker ＋ `git clone`、外殼 App 搬到獨立 repo、新增 Python 的 AI 閘道、介面極簡重設計，14.1～14.5 是實際操作後的修正。 迭代編號在 0919、0926、1005 各重排一次：原「規則引擎」與「管理儀表板」現在是**迭代 18、19**，對照表見實作規格書 4.0.1、4.0.3、4.0.4。1010 沒有改號，新的事排成 17.8 與 20～23（4.0.5）。

______________________________________________________________________

## 1. 專案脈絡

需求來源在 `docs/requirements/`，共六份文件。前五份**優先權不同，衝突時有明確的裁決順序**：

| 文件                                                                                                                            | 角色                                                                                                                   |
| ------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| [`srs.md`](https://94sh09sh19sh.github.io/hd-docs/latest/requirements/srs/index.md)                                             | 功能需求來源（FR 編號皆引用自此）。v2.0 共六組：P 病人端、N 護理端、M 管理與營運、X 對外揭露、S 系統、R 高風險控制措施 |
| [`implementation-spec.md`](https://94sh09sh19sh.github.io/hd-docs/latest/requirements/implementation-spec/index.md)             | 範圍界定、技術棧與迭代 3～23 規劃，**衝突時以此為準**                                                                  |
| [`database-policy.md`](https://94sh09sh19sh.github.io/hd-docs/latest/requirements/database-policy/index.md)                     | 資料治理強制規則，**優先權等同實作規格書**                                                                             |
| [`deployment-spec.md`](https://94sh09sh19sh.github.io/hd-docs/latest/requirements/deployment-spec/index.md)                     | 部署形態、環境界線與交付方式（0912 新增，0926 改版為 v3.0：Docker ＋ `git clone`），**優先權等同實作規格書**           |
| [`fde-assessment.md`](https://94sh09sh19sh.github.io/hd-docs/latest/requirements/fde-assessment/index.md)                       | 背景脈絡與選型理由                                                                                                     |
| [`open-questions.md`](https://94sh09sh19sh.github.io/hd-docs/latest/requirements/open-questions/index.md)                       | 唯一的待確認事項總表（Q-01～Q-37）。程式裡的暫定值多半對應其中一項                                                     |
| [`../notes/uiux-design-baseline.md`](https://94sh09sh19sh.github.io/hd-docs/latest/notes/uiux-design-baseline/index.md)         | 介面設計基準（0919 新增，0927 改為極簡方向）。**動介面前先讀**，可執行版在 `.claude/skills/hd-uiux/`                   |
| [`../reference/kiosk-shell-contract.md`](https://94sh09sh19sh.github.io/hd-docs/latest/reference/kiosk-shell-contract/index.md) | 病人端外殼 App 契約（0927 新增）。外殼在另一個私人 repo，兩邊只靠這一份帶版本號的契約對齊                              |

動工前請至少讀完前三份。這個專案有不少「看起來繞路」的設計，幾乎都源自這些文件的硬性約束。系統實體與邏輯架構見[架構圖](https://94sh09sh19sh.github.io/hd-docs/latest/requirements/architecture-diagrams/index.md)（**2026-09-29 依 0926 改版重繪**：應用伺服器改為 Docker 容器・`git clone`，後端與 AI 推論端點之間多一格 AI 閘道服務，過渡期的線改為「開發機 → SSH 通道 → 實驗室個人容器裡的 AI 閘道」，並把建置期才有的對外連線與執行期零連外分開畫；**1005 補上迭代 15、16**：臨床資料匯入改標院方資料同步、平板多一條院內 SSE，兩張圖都只改標籤）。圖片走 repo 相對路徑，文件站上就是 repo 裡的這兩個檔案。

______________________________________________________________________

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

npm workspaces monorepo，另有兩個容器服務。約 58,500 行 TypeScript（版控內全部 `.ts`／`.tsx`，含驗收腳本與產生的圖示資料；用同樣的計數方式，0930 時約 50,800 行、0923 時約 44,600 行）＋約 900 行 Python（AI 閘道）。 compose 另有一個只在 `simulation` 設定檔才起來的 `hospital-api-sim`（模擬院方 API，與 `api` 同一個映像檔，不開埠）。 外殼 App（Kotlin）在另一個私人 repo `hd-kiosk-shell`，本 repo 以 `services/shell-builder/shell.pin` 釘住它的 tag（目前 `v0.3.0`）。

**技術棧**：NestJS 11 · Prisma 6 · SQLite（測試與正式皆同）· React 19 · Vite 6 · TypeScript 5.7 · dnd-kit（簡易版拖曳）· Lucide 圖示與 Noto Sans TC 子集（自帶，不經 CDN） **部署與周邊**：Docker ＋ compose（專案名稱固定 `hd-tablet-care`，資料與金鑰兩個 external 資料卷）· AI 閘道 Python ＋ FastAPI ＋ LangChain · 外殼 App Android（Kotlin）

### 資料流

```
病人端 PWA ─┐                   ┌─→ Repository 層 ─→ Prisma ─→ SQLite 檔案（專案目錄外）
            ├─→ 後端 API ───────┤
護理端 PWA ─┘  （SSE 回推）     ├─→ AiGatewayService ─→ LlmProviderPort ─→ mock
                                │                                       └─→ lab／onprem ─→ ai-gateway 容器 ─→ 推論端點
                                └─← HospitalSyncService ←─ 院方透析清單 API（每 3 分鐘、唯讀）
                                                         └ 開發與模擬部署：hospital-api-sim
```

**前端一律不直接碰資料庫，也不直接碰模型。** 兩個 PWA 都沒有資料庫或模型相關套件；後端是唯一開啟資料庫檔案的常駐寫入行程，也是唯一呼叫模型的地方。 **0927 起後端也不直接連推論端點**（DEP-41）：`lab`／`onprem` 一律打 AI 閘道，模型名稱只寫在閘道的 `config.yaml`。 病人端的正式建置與後端同一個來源：`patient-web` 以伺服器憑證提供 HTTPS，並把 `/api/` 轉送給 `api`（迭代 12），外殼只需信任一張院內 CA。 **1005 迭代 15 起院方 API 由後端拉取**（本系統不回寫院方任何資料）；同步寫入的每一筆都走與護理師操作相同的服務，見 5.21。平板除了原本每 3 秒的輪詢，另訂閱 `GET /device/stream`（SSE，事件只通知「有新資料」、不帶數值）。

______________________________________________________________________

## 3. 七條不可違反的約束

前五條出自《資料庫使用規範》，後兩條出自 SRS v2.0 的 FR-S07 與 FR-S03／S06。動任何一處之前先確認不會踩到：

| #   | 約束                                  | 為什麼                                                                     | 現況                                                                                |
| --- | ------------------------------------- | -------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| 1   | **前端不得直接碰資料庫**              | 授權與驗證只能發生在後端                                                   | 兩個 PWA 只呼叫後端 REST                                                            |
| 2   | **身分驗證一律自建**                  | 病人不登入的身分模型與任何託管身分服務都不合；託管服務也都在院外           | 自建 JWT ＋ `nurse_sessions` 表（可主動作廢）；病人端用裝置綁定核發的 Session Token |
| 3   | **存取控制寫在後端應用層**            | 授權必須可追溯到「哪位護理師、何時、為哪位病人」，要在自己可掌控的程式碼裡 | 全部在守衛 ＋ service 層；唯讀角色由全域守衛預設全擋                                |
| 4   | **不得在業務邏輯中嵌入資料庫語法**    | 換 ORM／資料庫時的隔離層                                                   | `PrismaService` **只注入 Repository 層**，controller/service 一律不得取用           |
| 5   | **測試資料必須虛構**                  | 開發機不是院內環境；過渡期 AI 走院外實驗室 API                             | seed 用 faker，病歷號固定 `HD-TEST-*`；院外 provider 由 AI 閘道強制合成資料檢查     |
| 6   | **零院外連線**                        | 所有資料不出醫院網路（FR-S07）                                             | `npm run check:egress` 盤點 0 筆；推播整條移除，即時通知只走院內 SSE                |
| 7   | **模型呼叫一律經 `AiGatewayService`** | 去識別化、合成資料檢查、呼叫紀錄必須集中在一處，漏一處就等於沒有           | 業務模組只注入閘道，不得直接注入 provider                                           |

額外：**即時同步不依賴任何資料庫平台功能**（第 3 條的延伸）。即時狀態快取層是行程內實作。

### 不被任何一種資料庫綁死的設計

正式環境原訂為醫院 MSSQL，0910 改為 SQLite。當初為相容 SQL Server 設下的約束全部保留，理由改為「萬一日後要遷，不要被卡死」：

- **不使用 Prisma `enum`** — 狀態欄位以字串承載，合法值由 `@hd/shared` 常數 ＋ class-validator 在應用層把關
- **不使用 JSON 欄位** — 結構化關聯資料一律正規化。例如問卷答案是獨立的 `symptom_answers` 表，護理記錄的範本勾選是獨立的 `nursing_record_fields` 表
- **不使用資料庫專屬預設值** — UUID 由 Prisma client 產生
- **控制級聯路徑** — 同一張表只留一條級聯刪除路徑，其餘外鍵一律 `NoAction`
- **不用 `Float` 承載臨床數值**（《資料庫使用規範》6.2）— 目前 schema 裡沒有任何 `Float` 欄位；適足性等計算結果以整數存

______________________________________________________________________

## 4. 資料模型

共 86 張表，20 個 migration：`init`、`iteration3_closed_network`、`iteration4_ai_content`、`iteration5_help_resolution_shifts_baseline`、`iteration6_carousel_file_import`、`iteration7_update_runs`、`iteration9_navigation_content`、`iteration9_help_category_label`、`iteration10_kiosk_foreground`、`iteration12_kiosk_shell_version`、`iteration14_beds`、`iteration15_hospital_api`、`iteration17_marquee_approval`、`iteration17_7_device_targets`、`iteration17_8_nursing_record_format`、`iteration18_rule_engine`、`iteration18_1_rule_gate`、`iteration19_performance_rewards_external`、`iteration20_gamification_existing`、`iteration21_garden_gifts_shared`（前五個是 SQLite 遷移時整組重建的，舊資料依《資料庫使用規範》第 15 條不搬；迭代 7 起一律只做加法，`check:migration` 把關）。逐欄說明見《[資料字典](https://94sh09sh19sh.github.io/hd-docs/latest/reference/data-dictionary/index.md)》。

| 分類                                                                                                 | 表                                                                                                                                      | 加入於    |
| ---------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| 帳號與登入憑證                                                                                       | `nurses`、`nurse_sessions`                                                                                                              | 迭代 1    |
| 主檔                                                                                                 | `patients`、`devices`                                                                                                                   | 迭代 1    |
| 排班與綁定                                                                                           | `treatment_sessions`、`device_bindings`                                                                                                 | 迭代 1    |
| 稽核軌跡                                                                                             | `audit_logs`                                                                                                                            | 迭代 1    |
| 病人自述內容                                                                                         | `symptom_reports`、`symptom_answers`、`help_requests`                                                                                   | 迭代 2    |
| 系統治理                                                                                             | `feature_flags`、`ai_invocations`、`backup_runs`                                                                                        | 迭代 3    |
| 院方臨床數值                                                                                         | `clinical_value_imports`、`clinical_values`                                                                                             | 迭代 3    |
| 背景佇列                                                                                             | `ai_jobs`                                                                                                                               | 迭代 4    |
| 衛教、測驗與回饋                                                                                     | `education_contents`、`education_completions`、`quiz_attempts`、`quiz_answers`、`feedback_responses`、`feedback_answers`                | 迭代 4    |
| 護理記錄與計算                                                                                       | `nursing_records`、`nursing_record_fields`、`adequacy_calculations`                                                                     | 迭代 4    |
| SOP 文件與查詢                                                                                       | `sop_documents`、`sop_sections`、`sop_queries`、`sop_query_citations`                                                                   | 迭代 4    |
| 求助處理與可設定暫代值                                                                               | `help_resolution_options`、`operational_settings`、`help_request_follow_ups`                                                            | 迭代 5    |
| 護理師班表與成效基準                                                                                 | `nurse_shifts`、`shift_bed_assignments`、`shift_change_requests`、`baseline_measurements`                                               | 迭代 5    |
| 閒置輪播與檔案匯入                                                                                   | `carousel_items`、`carousel_view_events`、`import_field_mappings`                                                                       | 迭代 6    |
| 版本更新紀錄                                                                                         | `update_runs`                                                                                                                           | 迭代 7    |
| 導覽版位                                                                                             | `nav_placement_settings`                                                                                                                | 迭代 9    |
| 求助類別與處理方式                                                                                   | `help_categories`、`help_request_methods`                                                                                               | 迭代 9    |
| 透析前問卷（版本化）                                                                                 | `questionnaire_versions`、`questionnaire_items`、`questionnaire_item_options`、`questionnaire_item_triggers`、`symptom_answer_options`  | 迭代 9    |
| 衛教題庫（版本化）                                                                                   | `quiz_topics`、`quiz_bank_versions`、`quiz_bank_questions`、`quiz_bank_question_options`                                                | 迭代 9    |
| 回饋題目（版本化）                                                                                   | `feedback_form_versions`、`feedback_form_items`                                                                                         | 迭代 9    |
| 床位與輪播播放範圍                                                                                   | `beds`、`carousel_item_targets`                                                                                                         | 迭代 14   |
| 院方資料同步                                                                                         | `hospital_api_fetch_runs`、`dialysis_vital_records`                                                                                     | 迭代 15   |
| 跑馬燈只在某幾台平板播                                                                               | `carousel_item_device_targets`                                                                                                          | 迭代 17.7 |
| 護理記錄依格式分段（DART／SOAP）                                                                     | `nursing_record_sections`                                                                                                               | 迭代 17.8 |
| 規則引擎（判斷輔助）                                                                                 | `rule_definitions`、`rule_versions`、`rule_version_parameters`、`rule_evaluations`、`rule_evaluation_inputs`、`rule_evaluation_reviews` | 迭代 18   |
| 書面確認閘門的登記紀錄（只增不改）                                                                   | `rule_gate_changes`                                                                                                                     | 迭代 18.1 |
| 指標與每日快照（全單位、透析班別；不記個人）                                                         | `metric_definitions`、`metric_snapshots`                                                                                                | 迭代 19   |
| 獎勵制度（沒有總分、沒有排名欄）                                                                     | `reward_rules`、`reward_periods`、`reward_scores`、`score_disputes`                                                                     | 迭代 19   |
| 臨時調動候補的技能標記                                                                               | `nurse_skill_tags`                                                                                                                      | 迭代 19   |
| 對外報表（只存聚合值）                                                                               | `external_reports`、`external_report_metrics`、`external_report_items`                                                                  | 迭代 19   |
| 平板現有功能的遊戲化（預設小撇步、病人選的小撇步、護理師的回覆；沒有自由文字欄）                     | `peer_tip_presets`、`peer_tip_submissions`、`nurse_replies`                                                                             | 迭代 20   |
| 透析小花園、送花、共同花園（盤面快照是 JSON 的唯一例外；送花沒有護理師欄、共同花園的格子沒有病人欄） | `game_saves`、`game_events`、`garden_collection`、`flower_gifts`、`shared_gardens`、`shared_garden_plots`                               | 迭代 21   |
| 麻將連連看（沒有新表：`game_events` 加十二欄；狀態評估陳述讀的時候才算，不存）                       | `game_saves`、`game_events`                                                                                                             | 迭代 22   |
| 老台灣記憶相簿（圖卡是資料、改字就是新的一版；「想起某個人」不彙總、沒有護理師欄位）                 | `album_cards`、`album_card_versions`、`album_card_options`、`album_responses`、`game_saves`                                             | 迭代 23   |

迭代 10、12 沒有新表，只在 `devices` 加欄位：前景回報三欄（迭代 10）、`shell_version` 與 `shell_contract_version`（迭代 12）；迭代 14 另加 `devices.bed_no`。 迭代 15 除了兩張新表，另加 `patients.preferred_device_id`（配給病人的平板）、`treatment_sessions` 五欄（`source`、`bed_no`、`expected_end_at`、`nurse_modified_at`、`bed_nurse_modified_at`）與 `beds.source`； 迭代 16 沒有動 schema（跑馬燈播放紀錄沿用 `carousel_view_events`）；迭代 17 在 `carousel_items` 加七欄（核准狀態、核准者、核准時間、生成它的背景工作、公告事由、衛教主題、來源）；迭代 17.8 在 `nursing_records` 加 `record_format`，並以一次性的遷移把護理長沒改過的護理紀錄版位移到主列；迭代 18 只有六張新表（規格書列四張，門檻與引用資料各拆一張明細表）；迭代 20 另在 `carousel_items` 加 `peer_tip_preset_id`（可為空），我的衛教小本子不另存、由作答紀錄算。全部只做加法。

### 值得注意的地方

| 表                                                          | 值得注意的地方                                                                                                                                                                                                                                                                           |
| ----------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `nurses`                                                    | `role` / `status` 為字串；`canApproveNurses` 支援單獨分享審核權限                                                                                                                                                                                                                        |
| `nurse_sessions`                                            | 存 JWT 的 `jti`，讓 token **可被主動作廢**（變更密碼、降權時）                                                                                                                                                                                                                           |
| `devices`                                                   | `apiKeyHash` 用 SHA-256（金鑰是 256-bit 隨機值，非使用者密碼）；MDM 狀態欄位。`bed_no`（迭代 14）＝平板貼在哪一床，**病人本身不存床號**：病人在哪一床＝他那台平板在哪一床                                                                                                                |
| `treatment_sessions`                                        | `@@unique([patientId, scheduledDate, shift])`                                                                                                                                                                                                                                            |
| `device_bindings`                                           | 綁定「病人＋平板＋療程時段」三者；`sessionTokenId` 存 jti，token 本身不寫入資料庫                                                                                                                                                                                                        |
| `symptom_reports`                                           | `clientReportId` **唯一鍵** → 離線補傳的冪等保證；`reportedAt`（病人填寫時間）與 `receivedAt`（伺服器收到）分開存                                                                                                                                                                        |
| `help_requests`                                             | `clientRequestId` 唯一鍵防重複；`routedTo` 記錄當下計算的分派結果供事後稽核                                                                                                                                                                                                              |
| `audit_logs`                                                | 關聯欄位皆正規化為外鍵；另冗餘記錄 `actorLabel`、`deviceSerialNo`，避免帳號日後異動導致軌跡失真                                                                                                                                                                                          |
| `ai_invocations`                                            | 每次模型呼叫一列（provider、模型、耗時、是否去識別化、是否被擋）。迭代 4 的每一份 AI 產出都要能追回對應的一列                                                                                                                                                                            |
| `clinical_values`                                           | 每筆帶資料時間；覆蓋時保留前一版                                                                                                                                                                                                                                                         |
| `ai_jobs`                                                   | 重新啟動時仍在執行的工作標為失敗，不會卡在「產生中」                                                                                                                                                                                                                                     |
| `nursing_records`                                           | 簽核後不可改；記下起點（AI 初稿／預填／手寫）與 AI 初稿的處置（原樣採用／修改後採用／未採用）                                                                                                                                                                                            |
| `adequacy_calculations`                                     | 結果以整數存，並指回五筆原始 `clinical_values`；記公式版本 `DAUGIRDAS2-SPKTV-v1`                                                                                                                                                                                                         |
| `quiz_attempts`、`education_contents`、`feedback_responses` | 記下當時的題庫、主題、規則版本字串；暫定內容換掉後舊紀錄仍可回溯                                                                                                                                                                                                                         |
| `help_requests`                                             | 迭代 5 擴充五欄。`arrivedAt` 與 `acknowledgedAt` **是兩個獨立欄位，不互相填補**——理由見 5.15                                                                                                                                                                                             |
| `help_resolution_options`、`operational_settings`           | Q-13／Q-14 的暫代值存這裡，不寫死在程式。停用選項不刪列，既有紀錄才查得到文字；`operational_settings.updatedAt` 可為空，空＝從未被改過                                                                                                                                                   |
| `nurse_shifts`                                              | 起訖時間逐筆存，不由班別反推（跨日班與臨時調整都靠它）；取消不刪列。屬 L2，一般護理師只查得到自己的                                                                                                                                                                                      |
| `baseline_measurements`                                     | **只新增不覆寫**，舊版標 `superseded` 保留；估算值（`source=ESTIMATED`）在所有畫面帶警告；背書者必填                                                                                                                                                                                     |
| `carousel_view_events`                                      | **沒有病人、綁定、平板或卡片內容欄位**，這是刻意的（見 5.19）。要做個人層級的閱讀分析前，先回頭讀規範第 11 條                                                                                                                                                                            |
| `import_field_mappings`                                     | 檔案欄位名稱是資料不是程式；`(profile_code, target_field)` 唯一。兩個目標欄位不得同時對應到同一個檔案欄位，設定時就擋下                                                                                                                                                                  |
| `backup_runs`                                               | `sha256` 存完整雜湊；0929 起同一串另寫在 `BACKUP_DIR` 裡的 `<檔名>.sha256`（格式同 `sha256sum`）。**資料庫壞掉、服務起不來時這張表就查不到**，還原時的雜湊從那個檔拿                                                                                                                     |
| `beds`                                                      | 床位清單是資料（系統管理可改）。~~預設 15 床~~ 1005 迭代 15 起全新環境不預設，院方資料出現的床號自動加進來（只新增、不再啟用停用的床）。有病人正在治療的床拿不掉，否則那位病人會從床位圖上消失                                                                                           |
| `treatment_sessions`                                        | 迭代 14.2 起可「重新開啟」：今天已下機或已取消的療程回到已排班、`ended_at` 清空，**沿用同一筆**（唯一鍵不動），當天的症狀回報與求助仍掛在它底下                                                                                                                                          |
| `treatment_sessions`                                        | 迭代 15：`source` 分人工與院方；`expected_end_at` 只當「預計結束」，**不拿它判定下機**（可能是預排值，院方欄位要第三次進院確認；1007 迭代 17.5 起只記錄，透析一律開始後四小時結束）；`nurse_modified_at`／`bed_nurse_modified_at` 有值時，同步不再改它的狀態／床位——**護理師的更正優先** |
| `hospital_api_fetch_runs`                                   | 每次抓取一列（結果、重試次數、筆數、被拒的透析數、耗時、是否模擬），回應只存雜湊、**不存本文**——院方回應裡有姓名與病歷號                                                                                                                                                                 |
| `dialysis_vital_records`                                    | 院方每一筆血壓、脈搏與累積脫水量，掛在療程與那一次抓取底下；**只收有綁定平板的病人**，沒配平板的病人的數值不寫進資料庫                                                                                                                                                                   |
| `carousel_items`                                            | 迭代 17 起 `approval_status` 是病人端唯一的閘門：`listPlayable` 只取 `APPROVED`。既有內容遷移時標為已核准，新列預設待核准                                                                                                                                                                |

______________________________________________________________________

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
1. **Session Token** — 綁定核發的限時 JWT，`x-session-token`

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

**0919 起這一層的語意變了，介面沒變。** 平板管控改走免 MDM 路線（自包 WebView 外殼＋Android 內建螢幕固定）， 因此 `MockMdmProvider` **不再是「等著被真 MDM 換掉的模擬品」，它就是這項功能的正式實作**： 裝置佈建狀態的紀錄與稽核（FR-S01）。稽核說明欄的 `[mock]` 前綴要移除——它已經不是模擬品， 而且那個前綴會出現在護理師看得到的畫面上（FR-S10）。

原因：Android Enterprise 有三處必須連往院外（首次佈建連 Google、後端設定政策要呼叫 `googleapis.com`、遠端鎖定命令靠 FCM 送達），與封閉網路前提直接衝突。 完整選型見《[平板管控：免 MDM 的全院內方案](https://94sh09sh19sh.github.io/hd-docs/latest/notes/mdm-offline-plan/index.md)》。

取得 Android Enterprise 權限（Q-11）後，新增一個實作同介面的 provider 並替換 `MdmModule` 的注入即可，**其餘商業邏輯與稽核軌跡不需更動**。

**迭代 12 起外殼 App 另有契約**（見 6「迭代 12」）：前景回報多帶外殼版本、契約版本與是否釘選，護理端裝置管理據此標出「版本正常／外殼過舊／版本不相容／未回報版本」。 **迭代 14.1 補了兩件模擬 MDM 的事**：`MdmProviderPort` 新增 `simulated` 與選用的 `restoreDevice`，後端啟動時把資料庫的納管狀態交回模擬 MDM（不分環境；否則重新啟動後已納管的平板鎖不了、解不開）；開發環境另外自動納管 seed 的平板，照樣經介面、照樣寫稽核，**正式環境不做**。

### 5.7 SQLite 連線與唯讀通道（迭代 3）

- 連線時套用並回讀四項必開設定（`journal_mode=WAL`、`foreign_keys=ON`、`busy_timeout=5000`、`synchronous=FULL`），缺一項就拒絕啟動
- **寫入連線固定一條**：實測 Prisma 預設連線池有多條連線時，事後下的 PRAGMA 只會落在其中一條
- 統計、報表、稽核查詢、AI 呼叫紀錄、備份歷程清單走 `query_only` 的唯讀連線，不與臨床寫入競爭
- 資料庫檔案與 `BACKUP_DIR` 必須在**專案目錄外的本機磁碟**；相對路徑、專案目錄內、網路路徑、雲端同步資料夾，後端與 seed 一律拒絕啟動
- Prisma CLI 以 `CHECKPOINT_DISABLE=1` 關閉使用統計回報，否則 `prisma generate` 會連到院外

### 5.8 功能開關中心（FR-S08，迭代 3）

`modules/feature-flags/`，定義在 `shared/platform.ts`。

- 迭代 3 的十個開關：高風險三項（`RISK_STRATIFICATION`、`INTRA_DIALYSIS_ALERT`、`DOSE_REFERENCE`）、AI 兩項（`AI_FEATURES`、`REAL_PATIENT_DATA_TO_AI`）、輪播三層、績效兩項（`PERF_INDIVIDUAL_L3`、`REWARD_SCORING`）。**全部預設關閉**。之後又加三個：迭代 9 的 `HANDHELD_FEATURES`，迭代 14.2 的 `HELP_NON_CLINICAL_GROUP`（求助畫面顯示「其他」那一框，預設關閉），1005 的 `LAB_VALUE_FEATURES`（需要抽血數值的功能：透析適足性，預設關閉；院方透析清單 API 沒有抽血數值），1007 迭代 17.7 的 `MANUAL_PATIENT_CREATE`（護理師自己新增病人，預設關閉；兩個版本同一個開關，**新增病人的端點不跟著擋**，見實作規格書 3.7）。 **1005 迭代 16**：輪播三層停用（`RETIRED_FEATURE_FLAG_KEYS`，資料表的列與切換紀錄保留、後端載入時略過），換成 `TODAY_PANEL`（「本次透析」面板，**預設開啟**——9.1 起「預設全關」的唯一例外由它承接）與 `MARQUEE`（跑馬燈，預設關閉，速度要先經長者看過）
- **`HELP_NON_CLINICAL_GROUP` 是唯一不擋後端的開關**：它只決定平板上有幾顆按鈕。平板停在舊畫面時病人按下去的求助照樣要送到，擋掉就是把求助丟掉
- 開啟條件由後端逐項判定，不靠人記得。例如 `REAL_PATIENT_DATA_TO_AI` 只在 `LLM_PROVIDER=onprem` 時可開；高風險三項（1010 迭代 18 起加上 `ADEQUACY_PREDICTION`，共四項）只要求那一項有規則版本——**書面確認閘門（18.1 起在系統管理登記，存 `rule_gate_changes`；18 時是 `.env` 的 `HIGH_RISK_WRITTEN_CONFIRMATION`）與書面依據擋在每一次比對**，缺一則真實病人一律擋下、只對合成資料執行（見第 7 節）
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

`modules/clinical-data/`：`ClinicalDataSourcePort` ＋ `ManualEntryAdapter` ＋ `FileImportAdapter`（迭代 6）＋ **`HospitalApiAdapter`（迭代 15，在 `modules/hospital-sync/`）**，三者共用 `clinical_value_imports`／`clinical_values`。 1005 起院方 API 是唯一的日常來源，人工輸入與檔案匯入只留在專業版當備援（FR-S05）；院方 API 那一支的同步機制見 5.21。

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

______________________________________________________________________

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
1. **估算值要標得出來**：來不及實測時的退路（`source=ESTIMATED`）是允許的，但該筆在所有畫面上都帶著「引用時必須標明是估算」的提示。把退路做進系統，是為了讓它留下痕跡，不是讓它變方便
1. **背書者必填**：沒有出處的數字，被院長室問到「這數字哪來的」就答不出來

數值以「整數＋小數位數」記錄（規範 6.2），小數位數超過指標定義時視為格式錯誤、**不四捨五入**。同一指標同一班次再次建檔時舊版標記 `superseded` 保留，不覆寫。

### 5.19 閒置輪播（FR-P09～P11、FR-P13，迭代 6）

> **1005 迭代 16 拿掉輪播**，下面是迭代 6～15 的做法，留著對帳用。現行的病人端首頁見本節末「迭代 16 起：本次透析面板與跑馬燈」； 「卡片在後端組好」「開關關閉時後端不送」「`muted` 與 `helpButtonAlwaysVisible` 寫進契約」三個決定原樣沿用。

`modules/carousel/` ＋ `patient-pwa/CarouselScreen.tsx`。三層內容、一個端點： `GET /device/carousel` 回傳行為參數、開著的層、組好的卡片，以及 `questionnaireDue`。

三個決定值得知道：

- **卡片在後端組好**。FR-P11 要求輪播畫面不得出現姓名與病歷號，把這條規則放在後端就只在一處判定； 放在前端，就得寄望每一個畫面元件都記得它。驗收腳本因此能直接掃描回應內容來驗這一條。
- **開關關閉時後端不送該層的卡片**，不是前端不顯示。`enabledLayers` 與 `cards` 同時為空。
- **`muted` 與 `helpButtonAlwaysVisible` 是回應的一部分**，值固定為 `true`。 它們不是設定，是把 FR-P13 的兩條 P0 要求寫進契約——契約裡有，驗收腳本就驗得到。

行為參數（閒置門檻 60 秒、卡片間隔、細節頁逾時、夜間模式起訖、問卷到期間隔）全部走迭代 5 的 `operational_settings`，不另立設定表。夜間模式的起始晚於結束時代表跨過午夜， 這是「18 時到隔天 7 時」最自然的寫法。

病人端的閒置偵測在 `App.tsx`：`pointerdown`／`keydown`／`touchstart` 三種事件在**捕捉階段**重設計時器； 輪播畫面本身也在捕捉階段收下 `pointerdown`，點在卡片以外的任何地方立即退出，**沒有確認對話框**。 求助按鈕不在輪播元件裡——它留在主畫面原處，輪播進行中只是把 `z-index` 抬到遮罩之上， 因此位置與尺寸完全不變。

**迭代 16 起：本次透析面板與跑馬燈**（SRS FR-P09～P11 的 1005 改寫）。`modules/patient-home/` ＋ `patient-pwa/TodayPanel.tsx`、`LineChart.tsx`、`Marquee.tsx`。 `GET /device/home` 回傳行為參數、面板、跑馬燈與 `questionnaireDue`：

- **面板只有畫面要用的欄位**：開始與預計結束時間、血壓與累積脫水量的點（只有時間與值）、設定脫水量、五個數字（各帶資料時間）。 取捨表標「不顯示」的東西沒有欄位可以放，後端也不讀。讀到 0 的一律不送。資料是這次療程的 `dialysis_vital_records`（迭代 15）與 `clinical_values`
- **跑馬燈**：在架上、指定給這一床或全部床位的衛教與公告，一則「標題：內容」；**夜間一則都不送**。速度、開頭靜止、兩則間隔是營運參數（`MARQUEE_*`）
- **圖自己用 SVG 畫**，字是疊在上面的 HTML、以像素定位（不用 `viewBox` 縮放）；**沒有刻度、格線、警戒線、正常範圍**，線的顏色是 `--c-chart-line` 不是語意色（`check:ui:design` 擋）
- **跑馬燈用 Web Animations**：先靜止、再以「每秒幾字 × 字級」等速左移到整則離開、空白、下一則；不能點（`pointer-events: none`）；沒有內容、夜間、減少動態效果時整條不出現
- **即時**：迭代 15 的 `VITALS_UPDATED` 推送一到平板就重取；推送斷了還有每分鐘一次的保底
- 播放紀錄寫進原本的 `carousel_view_events`，`layer` 記 `MARQUEE`（**Schema 不變**）；`POST /device/marquee/plays`

### 5.20 檔案匯入與可設定的欄位對應（FR-S05，迭代 6）

`FileImportAdapter` 收的是寬表：一列一位病人在某個資料時間的多項數值。

- **欄位名稱不寫死**：`import_field_mappings` 一列一個目標欄位，比對時忽略大小寫與全形半形空白。 院方把「理想體重」改成「理想體重(kg)」那天，改的是一列設定
- **Excel 用 `exceljs`，CSV 自己解析**（約二十行，支援引號與欄內逗號）。 「欄位裡有逗號就靜默切錯」這種錯誤不會有任何錯誤訊息，值得用那二十行換掉
- **Excel 日期儲存格**在 exceljs 會以 UTC 解讀，但檔案上寫的是現場的時刻， 因此把 UTC 的年月日時分當成當地時間重組一次，與班表匯入的處理一致
- **全有或全無**與重複匯入偵測沿用迭代 3 的 `ClinicalDataImportService`，一行都沒改： adapter 只負責「把來源轉成標準化數值並逐列指出格式問題」
- 檔案以 base64 夾在 JSON 裡送上來，不走 multipart。上限 2 MB，少一種請求形式就少一套解析與錯誤處理

### 5.21 院方資料同步（FR-S15／S16，迭代 15）

判準只有一句：**院方 API 判斷得出來的事，就不要求護理師操作。** `modules/hospital-sync/` 依營運參數的頻率（預設 3 分鐘）向院方透析清單 API 拉一次， 把病人主檔、床位、病人在哪一床、療程開始與下機、四種數值一律由 API 判斷；護理師只做三件事：每位病人配一次平板、更正、以及 API 判斷不了時的處理。

- **格式是讀同院 IDH 系統的程式推出來的**，不是院方文件：陣列沒有欄位名稱，只能靠位置認欄位（`@hd/shared` 的 `hospital-api.ts`，51 欄）。少欄或多欄的列不認，**那一次透析整個不寫入**——臨床數值只對一半比沒有更危險
- **同步不另開寫入路徑**：建排班、綁定、換床、寫數值都呼叫護理師拖曳時用的那幾支服務，操作者是登入不了的系統帳號 `SYSTEM-HOSPITAL-SYNC`，稽核記成「院方資料同步」。簡易版與專業版因此看到的是同一套資料、同一種稽核
- **護理師的更正優先**：提前結束或換床之後，同一筆療程的狀態與床位不再被同步改回去（`nurse_modified_at`、`bed_nurse_modified_at`）
- **判斷不了的標出來，不猜**：預計結束時間可能是預排值，不拿它判定下機，過了很久還沒有結束體重就標「待確認下機」（1007 迭代 17.5 起「預計結束」一律是開始後四小時）；平板沒自動接上時標出原因（平板正在別人的療程中、不在線上、停用或尚未佈建、院方的床位是停用的床或認不出來）；**還沒配平板的病人不算問題**，首波只有少數病人用平板，其餘只出現在床位圖上；超過設定時間沒更新，床位圖上方出現提示，這段期間護理師可到專業版手動處理
- **正式環境的兩道防線**：啟動時位址的主機是 `hospital-api-sim` 就拒絕；抓到的回應帶 `x-hd-simulated` 就整次作廢。模擬部署要以 `HD_SIMULATION_DEPLOYMENT=yes` 明示
- **推送**：有新資料時護理端串流多一種 `HOSPITAL_SYNC` 事件；平板訂閱 `GET /device/stream`，**事件只說「有新資料」、不帶數值**，平板收到後自己重取 `GET /device/home`
- **探測工具** `npm run probe:hospital-api` 與同步共用解析程式，**只印結構與型別，不印任何值與位址**；位址在探測時當場輸入，不寫進 `.env`（部署手冊第十五冊 V-30a）

實作位置與開發機怎麼開見 6「迭代 15」。

______________________________________________________________________

## 6. 已完成範圍

> **迭代 1～23 收在子文件**：《[技術端進度報告之一：迭代 1～23 的完成範圍](https://94sh09sh19sh.github.io/hd-docs/latest/reports/progress-technical-iterations-1-23/index.md)》，各迭代的小節標題照舊； 本報告其他地方寫的「見第 6 節「迭代 19」」，到子文件找同名的小節。
>
> **收入方式：一次性收入**（1015）。**迭代 24 起做完的迭代照舊寫在本節**、排在「規模」之前，不再搬進子文件；子文件不再追加，只在更正時改。 下方「規模」與「共用常數的角色」是跨迭代的總表，留在本節，照舊每個迭代補一欄。

### 迭代 24（1017～1018）：遊戲化之五——花園與相簿的擴充

使用者 1015 看過迭代 21～23 之後的六個決定（《[透析中的遊戲化之四](https://94sh09sh19sh.github.io/hd-docs/latest/notes/dialysis-gamification-expansion/index.md)》），實作規格書 4.24。畫圖的量大，照迭代 23 的做法切成四次子迭代：

| 子迭代       | 做了什麼                                                                                                                                  | 驗收                                           |
| ------------ | ----------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| 24.1（1017） | `garden.ts` 的花 12 → 36 種、`VISITOR_CATALOG` 24 種；插畫拆成畫具與色票、起始 12 種、新的 24 種花、24 種訪客四支；「欒」「蕎」進字型子集 | `verify:iteration24-1`                         |
| 24.2（1017） | 相簿第三批 30 張（學校、街上與市場、田裡與海邊）；開關的門檻只看起始的六個主題                                                            | `verify:iteration24-2`                         |
| 24.3（1017） | 相簿第四批 30 張（聽的看的、穿的戴的、洗澡與打扮），120 張八週不重複                                                                      | `verify:iteration24-3`                         |
| 24.4（1018） | 種子袋、小訪客、兩個圖鑑；`garden_visitors` 與 `game_events.visitor_code`；`GET /device/games/album/collection`                           | `verify:iteration24`、`verify:iteration24:api` |

**接手時要知道的幾件事**：

- **袋子裡有幾顆不存**：快照只存「第幾次療程種了幾顆」（`sown`），換了一次療程自然是 3 顆——這就是「補到」而不是「累加」，不靠任何上限判斷
- **小訪客的判斷是平板送的一步**（`LOOK`），不是伺服器讀花園時自己算：斷線時點開花園照樣會來，連線後伺服器照序號重算出同一隻（月份也照那一步的時間）。來不來、來哪一隻照快照裡的花園編號（`key`）與第幾次療程的雜湊，**沒有亂數**
- **第一次點開花園就寫存檔**（原本第一步之後才寫）：花園編號是伺服器給的亂數，要寫下來才固定
- 門口一欄改成 240px、澆水與養分兩欄；最壞的情形量過剛好不捲動，**門口再加東西要先量**
- 相簿圖鑑要連線（平板快照沒有貼紙）；花園圖鑑把平板快照裡的 `bloomed`、`met` 疊上去，斷線照樣翻得到

### 迭代 25（1018）：緊急通報——頂端橫幅、床邊前速覽、護理紀錄連動

使用者 1015 操作護理端後提出的四件事（《[緊急通報的處理流程與護理紀錄連動](https://94sh09sh19sh.github.io/hd-docs/latest/notes/emergency-handling-redesign/index.md)》），實作規格書 4.25。三次子迭代同一天做完、程式一筆 commit：

| 子迭代 | 做了什麼                                                                                                                                                                                                                                                                        | 驗收                                                               |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| 25.1   | `realtime-context.tsx` 的 `pruneAlerts`：開場快照、狀態推送、求助推送、輪詢補位快照四處修剪頂端橫幅；`HelpRequestAlerts` 不動                                                                                                                                                   | `verify:iteration25` 步驟 1、`verify:iteration14-4`                |
| 25.2   | `HospitalApiColumn` 多十二個位置、`hospital-api.format.ts` 多讀；`dialysis_vital_records` 加四欄、新表 `dialysis_session_settings`；`GET /help-requests/:id/bedside`（`help-bedside.service.ts`）；`bedside-brief.tsx`；簡易版紅框與格子只開速覽、`id-card`；專業版「病人簡介」 | `verify:iteration25` 步驟 2～4、`verify:iteration25:api` 步驟 2、3 |
| 25.3   | `nursing_records.source_help_request_id`（唯一）、`HELP_RESPONSE`；`HelpResponseDraftService`、`nursing-records/help-response.ts`；結案同一個交易建草稿、補改重組；`help-candidates`、`help-responses`、`:id/template` 三支                                                     | `verify:iteration25` 步驟 5、6、`verify:iteration25:api` 步驟 4～8 |

**接手時要知道的幾件事**：

- **橫幅的修剪有 5 秒寬限**（`PRUNE_GRACE_MS`）：後端寫進資料庫到快取更新之間有幾毫秒，那段時間發出的快照時間已晚於送到時間、裡面卻還沒有它；沒有寬限的話，那一則緊急的會被誤拿掉
- **速覽只讀**：不寫稽核、不改狀態；整個簡易版只有速覽的「我接手」呼叫 `actions.acknowledge`（`verify:iteration25` 數這個）
- **蓋在平板區上的層要寫明格子**：`.wb-brief-layer` 用 `grid-row: -2 / -1`，所以 `.wb > .wb-map`、`.wb > .wb-rail` 也寫明自己的格子，不然自動排版把平板區擠到右欄
- **段落在交易之前組好**（要讀院方量測與問卷），`resolveWithFollowUps` 多收一個 `draft`、在同一個交易裡 `createNursingRecordIn`；唯一鍵擋下時整筆不成立、回 409
- **改套範本之後補改不重組**（`regenerate` 看 `templateCode`）；`recompose` 只動草稿、AI 初稿作廢、呼叫紀錄照留
- **速覽的院方欄位認不出就當沒有值**（`lenient`），不像其他欄位整次透析退回；第三次進院用探測工具看它們的實際單位

### 規模

| 量測     | Iteration 2 時點 | 迭代 4 完成 | 迭代 5 完成 | 迭代 6 完成 | 迭代 7 完成 | 迭代 9 完成 | 迭代 10 完成 | 迭代 14.5 完成 | 迭代 17 完成 | 迭代 18.1 完成 | 迭代 19 完成 | 迭代 21 完成 | 迭代 22 完成 | 迭代 23 完成 | 迭代 24 完成 | 迭代 25 完成 |
| -------- | ---------------- | ----------- | ----------- | ----------- | ----------- | ----------- | ------------ | -------------- | ------------ | -------------- | ------------ | ------------ | ------------ | ------------ | ------------ | ------------ |
| API 路由 | 43               | 78          | 90          | 107         | 109         | 116         | 117          | 124            | 136          | 158            | 181          | 197          | 203          | 209          | 210          | 214          |
| 資料表   | 10               | 29          | 36          | 39          | 40          | 54          | 54           | 56             | 58           | 67             | 77           | 86           | 86           | 90           | 91           | 92           |
| 稽核動作 | 32               | 52          | 66          | 68          | 74          | 82          | 84           | 90             | 109          | 121            | 141          | 145          | 147          | 150          | 150          | 151          |
| 權限碼   | 9                | 17          | 20          | 21          | 21          | 23          | 23           | 23             | 23           | 23             | 30           | 30           | 31           | 31           | 31           | 31           |
| 角色     | 3                | 6           | 6           | 6           | 6           | 6           | 6            | 6              | 6            | 6              | 6            | 6            | 8            | 8            | 8            | 8            |
| 功能開關 | —                | 10          | 10          | 10          | 10          | 11          | 11           | 12             | 12           | 14             | 14           | 20           | 22           | 23           | 23           | 23           |
| 營運參數 | —                | —           | 6           | 12          | 12          | 20          | 20           | 22             | 27           | 28             | 28           | 34           | 41           | 41           | 41           | 41           |

（迭代 21 那一欄含迭代 20：遊戲化兩個迭代合起來多 16 條路由、9 張表、4 種稽核動作（迭代 21 的送花與種花刻意不寫稽核，每一步在 `game_events`）、6 個功能開關、6 個營運參數。迭代 22 沒有新表，`game_events` 加十二欄。迭代 23 四張表、3 種稽核動作、1 個功能開關，沒有新的營運參數（共同記憶沿用迭代 21 的兩個門檻）。）

（迭代 6 沒有新增功能開關：輪播三層的開關在迭代 3 就已建好並預設關閉，這次做的是把它們的 「開啟條件」從「功能尚未實作」換成實際判定。迭代 7 只多一張 `update_runs` 與兩個維運端點， 新增的六種稽核動作全是更新流程與遷移防呆留下的軌跡。DEP-37 的三處補做沒有動到任何一張表， 改的是啟動時的判定與兩個維運端點多回傳的幾個欄位。**迭代 8 一張表都沒動、一個端點都沒加**， 因此表上沒有它那一欄。）

**迭代 9 一次多了 14 張表**，但它們幾乎都是同一個形狀：三組「版本表加題目表加選項表」。 新增的 8 個營運參數也是同一類東西——**「其他」的提醒門檻、每月加問的間隔、趨勢偏離的三個門檻、 抽題規則的三個上限**，全部是護理長會想調、而工程師不該替他決定的數字。

**迭代 10 幾乎沒有動資料模型**：`devices` 多三個欄位、一個平板端端點、兩種稽核動作， 就這樣。它的工作量全在 repo 之外——**把已經做好的東西變成一份帶得進院內的檔案**， 以及把「帶進去之後會發生什麼」實際試一次。

**迭代 11～14.5 合起來只多 7 條路由、2 張表、6 種稽核動作**，而且全部是加法： 迭代 11、13 一條都沒加（它們的工作量在 compose、映像檔與 `services/`）；迭代 12 加一條外殼契約端點； 迭代 14 加四條（床位、平板換床、輪播播放範圍、結案後補改處理結果），14.2 加一條重新開啟療程；兩張表是 `beds` 與 `carousel_item_targets`。 新增的兩個營運參數是病人端任務的時點（心情、衛教），新增的開關是求助畫面的「其他」那一框。 **簡易版整個工作台沒有新增任何一條「專業版做得到、只是換個端點」的路由**——那是刻意的，見 6「迭代 14」。

**迭代 15～17 合起來多 12 條路由（淨增）、2 張表、19 種稽核動作**： 迭代 15 加六條（院方資料同步的狀態、紀錄、手動再抓一次，配平板，帶入最近一筆血壓，平板的推送串流）與兩張表； 迭代 16 加兩條（`GET /device/home`、`POST /device/marquee/plays`）、拿掉兩條（`GET /device/carousel`、`POST /device/carousel/view-events`），**一張表都沒加**； 迭代 17 加六條（草稿主題、要一份草稿、核准、退回、撤回、上下架時間），在 `carousel_items` 加七欄。 功能開關的數字沒變，是因為輪播三層的開關停用、換成面板與跑馬燈，再加上 1005 的「需要抽血數值的功能」（三減三加）； 營運參數淨增五個：院方 API 四個（抓取頻率、多久沒更新要提示、待確認下機的時間、床號格式），跑馬燈三個（速度、開頭靜止、兩則間隔），輪播的卡片停留與細節頁退回兩個停用。 （路由數 0930 以前沿用各迭代新增的端點累加；迭代 17 那一欄改以控制器實際的路由裝飾器計數，兩種計法在 14.5 時點一致。）

**迭代 17.1～18.1 合起來多 22 條路由、9 張表、12 種稽核動作**：17.1～17.7 多的是平板與內容指定的端點、`carousel_item_device_targets`； 17.8 加兩條（帶入處置後數值、記下複製）與 `nursing_record_sections`、一個營運參數（護理紀錄格式）；18 加九條與六張表、一個開關（`ADEQUACY_PREDICTION`）；18.1 加一條（`PUT /rules/gate`）與 `rule_gate_changes`。 17.7 另加開關 `MANUAL_PATIENT_CREATE`。路由數照後端啟動時印出的清單與路由裝飾器兩種計法對過（1010 都是 158）；測試手冊附錄之前寫的 146 是少算，18.1 收尾時更正。

**迭代 19 多 23 條路由、10 張表、20 種稽核動作、7 個權限碼**，功能開關與營運參數沒有增加（績效兩個開關迭代 3 就建好了，這次把「尚未實作」換成實際的開啟條件）。路由照後端啟動時印出的清單重數：181，與測試手冊附錄逐條對齊。

### 共用常數的角色

`packages/shared` 不只是型別。以下**業務規則**放在這裡，前後端共用同一份定義：

- `navigation.ts` — 迭代 9：17 項功能的**預設版位**與主列上限。只在第一次啟動時寫進資料表
- `content.ts` — 迭代 9：SRS 附錄 C 的全部預設內容（求助類別、處理方式與結果、問卷題目、 衛教題庫 35 題、回饋題目）。**這是「第一次啟動時寫進資料表的預設值」，不是執行期的資料來源**
- `routeHelpRequest()` — 求助分派規則。前端顯示的分派結果與後端計算結果保證一致。 迭代 9 起輸入從「類別」換成「組別」，組別存在資料表裡
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

**迭代 4 的暫定內容原本全部在這裡並標版本字串**，改內容要改常數並升版。 **迭代 9 把這件事整個翻過來**：內容搬進資料表，護理長在畫面上改、立刻生效，不必重新部署。

`PRE_DIALYSIS_SYMPTOM_QUESTIONS`、`QUIZ_QUESTIONS`、`FEEDBACK_ITEMS`、`EDUCATION_TOPICS`、 `HELP_REQUEST_CATEGORY_LABELS` 這幾份**還在檔案裡，但只剩一個用途**： 把迭代 9 之前那一版補寫成第 1 版，讓既有作答還原得出當時的題目。 執行期沒有任何一行程式讀它們——依 3.14 第 5 條，**不得留下「程式讀常數、介面讀資料表」的雙軌**。 依《資料庫使用規範》18.2「一次更新只做加法」，它們在下一版才移除。

**改動 `packages/shared` 後必須重跑 `npm run build:shared`**（`npm run dev` 會自動先跑一次）。

______________________________________________________________________

## 7. 🔒 高風險三項：有條件納入，1010 迭代 18 完成實作（原迭代 7 → 11 → 15）

> **編號重排過兩次**：0919 部署前的四個修正迭代占用了 7～10，規則引擎順延為迭代 11；0926 第一次進院失敗之後的四件事又占用了 11～14，再順延為迭代 15；1005 院方 API 等三件事占用 15～17，又順延為**迭代 18**。內容一字未改，只是往後挪。0916 以前的紀錄裡「迭代 7」、0923 以前的「迭代 11」、1005 以前的「迭代 15」指的都是本節，對帳時看實作規格書 4.0.1、4.0.3、4.0.4 的對照表。
>
> **首波試用期間一律不提供服務**：~~這三項尚未實作~~ 1010 起已實作，但開關預設關閉；關著時介面上不出現入口，後端端點一併擋下（DEP-34）。不做灰色按鈕、不做「敬請期待」。

**FR-P03**（風險分層）、**FR-P05**（預警）、**FR-N06**（劑量建議）在 Iteration 2 時因高 SaMD 風險整條排除。0910 起改為**納入**，現排在迭代 18，以自建規則引擎實作並受 FR-R01～R08 約束（實作規格書 1.4、3.6、4.16）。

目前狀態（1010 迭代 18 完成，細節見實作規格書 3.6 末段與 4.16）：

- 後端 `modules/rules/`：評估器是純函式（`evaluators.ts`，六種比對形態），服務只負責挑版本、讀歷史資料、寫執行紀錄與檢視紀錄。**模組不引用 AI 閘道與模型供應者**（`verify:iteration18` 逐檔檢查），文字一律由版本範本組出
- 六條預設規則第一次啟動寫入，**全部是草稿**；兩條收縮壓相關的出處寫同院 IDH 系統、標得了生效，其餘四條沒有出處（迭代 18 是示範值，**18.1 換成依文獻選的建議值**，寫在備註，出處照樣空著；既有資料庫啟動時補一個草稿版本）
- **挑版本**：真實病人只用生效中的版本；合成資料病人有生效的用生效的，沒有就用最新的草稿
- ~~**書面確認閘門在 `.env`**（`HIGH_RISK_WRITTEN_CONFIRMATION`，空值＝沒開），畫面只看得到。~~ **18.1 起閘門在系統管理「判斷規則」登記**（系統管理者、文號＋理由、`rule_gate_changes` 只增不改、寫稽核），設定檔不再有這一項。沒開時真實病人整位不比對：立即比對回 403＋稽核、定時比對略過（一天記一筆）
- 版本一經使用就改不了（條件寫在同一個 `updateMany` 的 where 裡）；沒有出處標不了生效；範本出現結論字詞存不進去
- 每 3 分鐘定時比對＋「立即比對」；同一版規則對同一筆資料（`subject_key`）只比一次，唯一鍵擋重複
- 介面只在專業版：即時總覽的待檢視、病人趨勢的判斷輔助、系統管理「判斷規則」；簡易版、病人端、總覽螢幕都沒有
- FR-N07 的「預測」部分另立開關 `ADEQUACY_PREDICTION`，還要 `LAB_VALUE_FEATURES` 開著
- 對真實病人啟用仍要兩個外部答覆：TFDA 分類書面確認（Q-02，18.1 起文號在系統管理登記）與臨床端的規則門檻值（Q-03，新版本附出處後標為生效）

迭代 18 以外的現有功能照舊維持這條線：

- 求助分派 `routeHelpRequest()` 的輸入**只有**病人自選的類型與急迫度，不讀歷史資料
- 症狀趨勢摘要只做原樣列出與次數統計，不加權、不分級、不預測、不產生建議文字
- 總覽的「病人自述症狀」是把答案原樣呈現，不是系統評估
- 心理社會趨勢只陳述比對事實，不判斷心理狀態、不自動轉介
- 適足性趨勢圖不畫目標線、不標正常範圍
- 相關畫面與每一處 AI 產出固定顯示非診斷結果提示

**接手時請維持這條線。** 若某個需求疑似需要「依資料做出會影響臨床判斷的建議或分級」，而該功能未列於 SRS 5.6 節，應先停下來確認。

______________________________________________________________________

## 8. 效能觀察

**端到端延遲幾乎全部來自資料庫往返，不是即時同步機制。** 這條結論在三種資料庫位置下都成立：

| 量測內容                        | Supabase 孟買    | Supabase 東京    | 本機 SQLite  |
| ------------------------------- | ---------------- | ---------------- | ------------ |
| 驗收腳本量測的單次 API 請求     | 1,741 – 2,249 ms | 702 ms           | **約 2 ms**  |
| 端到端（平板送出 → 護理端收到） | 4,710 – 5,899 ms | 1,856 – 1,893 ms | **約 10 ms** |
| 其中即時狀態同步本身            | 1 – 3 ms         | 2 – 3 ms         | —            |

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

______________________________________________________________________

## 9. ⚠️ 已知粗糙處

以下都是實測確認過的，不是猜測。第 1～4 項自 Iteration 2 起未處理，2026-09-29 重新確認第 1～3 項仍在。優先權不高但接手時值得知道：

| #   | 問題                            | 現況                                                                                                                                             | 建議                                                                           |
| --- | ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------ |
| 1   | **重複病歷號回 500**            | `PatientsService.create` 沒攔 Prisma `P2002`，唯一鍵衝突直接冒成 500                                                                             | 攔截後改回 409 ＋ 中文訊息，與其他地方一致                                     |
| 2   | **DevicesPage 未依權限隱藏 UI** | 一般護理師看得到註冊表單~~與 MDM 按鈕~~，按下去才 403（1007 迭代 17.6 起這一頁的佈建按鈕都移到系統管理，那裡本來就只給有權限的帳號；剩註冊表單） | 加 `can(Permission.DEVICE_MANAGE)` 條件渲染                                    |
| 3   | **專業版取消排班無 UI**         | `POST /treatment-sessions/:id/cancel` 端點存在；迭代 14 起簡易版「病人上床」的復原會呼叫它，**專業版仍沒有按鈕**                                 | 在 `ConsolePage` 補一顆按鈕                                                    |
| 4   | **總覽無日期選擇器**            | `GET /overview?date=` 支援查其他日期，UI 只看當日                                                                                                | 視需求補                                                                       |
| 5   | **總覽螢幕 8 小時後要重新登入** | `JWT_EXPIRES_IN` 預設 8 小時，全天開著的總覽螢幕到期後出現逾時提示                                                                               | 待 Q-10 確認螢幕位置與使用方式後，再決定是否給總覽螢幕專用的長效帳號或延長機制 |

| 6 | **目標平板型號未定**（0930 已確定 10 吋；1014 確定正式版固定橫放） | 「不出現捲軸」在開發機 1280×800、800×1280 驗過（14.5 起以無頭瀏覽器精確開這兩個尺寸）；實機沒驗過。1014 起只驗 1280×800，直放的排法留著、不再驗 | 待 Q-33 的型號；定了之後在實機重做截圖驗收（`x150`）。院方若統一調過系統顯示大小，短邊就不是 800 | | 7 | ~~**既有驗收腳本有一處環境相依**~~ **1005 迭代 16 解除** | `verify:iteration14:api` 步驟 4 預設「第二層輪播」開著，但 `verify:iteration6` 跑完會把它關回去，而第二層要有上架中的內容才准開。先跑過迭代 6 的環境裡這一步不通過 | 迭代 16 輪播拿掉、那一步改讀跑馬燈，腳本自己開跑馬燈與取消夜間時段、跑完改回（實作規格書 1.1 的表） | | 8 | **`verify:iteration13` 第 2 步誤判** | 這一步在 `apps/` 底下找 Ollama 字樣（後端不得直接連推論端點），找到的是迭代 13 自己的驗收程式 `verify-iteration13.ts`，於是不通過。迭代 16 的回歸清單沒有它，迭代 17 回歸時發現（實作規格書 4.15 驗收現況） | 掃描範圍排除驗收程式本身；依實作規格書 1.1，改既有腳本要記下理由 |

**授權判斷本身沒有問題** — 全部在後端把關，前端只是沒藏好入口。

______________________________________________________________________

## 10. 開發環境

```
npm install
cp .env.example .env        # 填 DATABASE_URL / JWT_SECRET / SUPER_ADMIN_*，建議一併填 BACKUP_DIR
npm run build:shared
npm run prisma:migrate
npm run db:seed             # 含 4 份虛構 SOP 文件
npm run dev                 # api:3000 · nurse:5173 · patient:5174
```

**必填環境變數**：`DATABASE_URL`（`file:` 加絕對路徑）、`JWT_SECRET`、`SUPER_ADMIN_WORK_ID`、`SUPER_ADMIN_INITIAL_PASSWORD`。

**常用選填**：`BACKUP_DIR`（備份輸出）、`LLM_PROVIDER`（`mock`／`lab`／`onprem`，預設 `mock`）與 `LLM_ENDPOINT`／`LLM_API_KEY`／`LLM_MODEL_ID`、`LLM_MOCK_LATENCY_MS`（預設 1200）、`JWT_EXPIRES_IN`（預設 8 小時）、`BINDING_MAX_HOURS`（預設 6）。

**迭代 8、9 都沒有新增任何環境變數。** 迭代 8 一個端點都沒加； 迭代 9 加了不少端點，但它新增的每一個數字都是**營運參數**—— 「其他」的提醒門檻、每月加問的間隔、趨勢偏離的三個門檻、抽題規則的三個上限， 一律存在 `operational_settings`，在護理端改，不在 `.env` 改。 **會被護理長調整的東西不該放在只有工程師動得到的地方。**

**迭代 7 新增的五個（只有正式環境會用到）**：`DEPLOYMENT_ENV=production` 把這台機器標成正式環境（時區不符即拒絕啟動、開發用的遷移指令被擋下、`API_PORT` 沒填即拒絕啟動）、`REQUIRED_TIME_ZONE`（預設 `Asia/Taipei`）、`PRISMA_ENGINES_DIR`（指向安裝包內的 Prisma 引擎，DEP-30；**迭代 11 隨安裝包撤除**）、`LLM_HEALTH_TIMEOUT_SECONDS`（健康檢查逾時，預設 5 秒，與單次生成的 `LLM_TIMEOUT_SECONDS` 分開）、`DB_DISK_MIN_FREE_MB`（資料庫磁碟保留空間下限，預設 1024，DEP-37）。

既有的 `API_PORT` 在正式環境的行為也變了：**開發機留空照舊用 3000，正式環境留空即拒絕啟動**（DEP-37 第 2 項）。

**迭代 11 起院內部署另有一份範本** `deploy/hospital.env.example`，只列 compose 要代換的變數（`HD_IMAGE_TAG`、`HD_BACKUP_DIR`、`HD_CONFIG_DIR`、三個 `HD_*_PORT`、`HD_PUBLIC_API_URL`、`MDM_KIOSK_BASE_URL`、`HD_SHELL_SRC_DIR`、`HD_SHELL_SIGNING` 等），逐項填法見部署手冊第十五冊之一（1001 起取代第十四冊之一）；迭代 15 多了 `HOSPITAL_API_BASE_URL` 與 `HD_SIMULATION_DEPLOYMENT` 兩個。**compose 不整份倒進容器**（DEP-13），容器要什麼在 `docker-compose.yml` 明寫；`UPDATE_PROBE_URL` 由 compose 直接給 `db:update`。 迭代 12 新增 `KIOSK_SHELL_MIN_VERSION`（最低可用外殼版本，留空用程式預設）；`MDM_KIOSK_BASE_URL` 在正式環境**必須是 `https://`**（迭代 14.1 的佈建 QR code 就是它）。 迭代 13 起 `LLM_ENDPOINT` 指向 AI 閘道、`LLM_MODEL_ID` 留空，`LLM_TIMEOUT_SECONDS` 要比閘道 `config.yaml` 的逾時大。 迭代 15 新增 `HOSPITAL_API_BASE_URL`（院方 API 的端點，**空白就是不抓**，簡易版照人工流程；院內的值不進 repo、不寫進任何文件）與 `SIMULATION_DEPLOYMENT`（compose 由 `HD_SIMULATION_DEPLOYMENT` 帶入，模擬部署填 `yes` 才准位址指向模擬院方 API）。抓取頻率是營運參數，不在 `.env`。 迭代 16、17 沒有新增環境變數：跑馬燈的速度與間隔都是營運參數。

> 資料庫檔案與 `BACKUP_DIR` 必須在**專案目錄外的本機磁碟**。相對路徑、專案目錄內、網路路徑、雲端同步資料夾，後端與 seed 一律拒絕啟動。 後端是唯一的寫入者：跑 `prisma:migrate`、`db:seed`、`db:restore` 或任何資料修補腳本前，**先停掉後端**。

### 驗收

```
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
npm run verify:iteration17-5  # 17.5 — 6 步（不需後端）
npm run verify:iteration17-6  # 17.6 — 6 步（不需後端）
npm run verify:iteration17-7  # 17.7 — 5 步（不需後端；先 build:shared）
npm run zh-tw:data          # 17.3：改了 packages/shared/zh-tw/ 的詞庫之後重新產生資料檔；-- --check 只比對
npm run demo:patient        # 17.1：一鍵展示病人端（模擬院方資料、另一個全新的資料庫）；-- --screenshot <檔名> 直接截圖
npm run check:all           # 六支盤點腳本（不需後端），0926 起多了 check:container
```

腳本都會建立少量標記過的合成資料並逐項斷言，涵蓋主線流程、錯誤路徑、權限隔離、冪等去重、稽核事件。**改動後請全部跑過。**

最近一次執行（2026-10-05，迭代 17 完成時）：迭代 15～17 各自的腳本與 `:api` 全綠；既有腳本回歸（`verify:acceptance`、`verify:iteration2`～`12`、`14` 系列與各自的 `:api`、`check:all` 六支）全綠，依實作規格書 1.1 改寫的幾支一併重跑。 **例外是 `verify:iteration13`**：它的第 2 步在 `apps/` 底下找 Ollama 字樣，找到的是迭代 13 自己那支驗收程式，與迭代 15～17 無關，見第 9 節第 8 項；`verify:iteration13:api` 要 Docker Desktop，這次沒跑（迭代 15～17 沒有動 AI 閘道）。結果記在實作規格書 4.13～4.15 各節的「驗收現況」。 0930 那一次（迭代 14.5）：`build`、`check:all` 六支、`verify:iteration8`、`verify:iteration14`、`14-1`～`14-5` 全綠。第 9 節第 7 項的環境相依迭代 16 已解除。

0919 的紀錄仍然成立：九支皆全數通過（`verify:iteration8` 不需要後端在跑，它驗的東西全部在前端原始碼與樣式表裡）；**盤點腳本全綠**——介面技術識別從 22 筆降到 0，遷移安全改成只掃上一次部署之後新增的那幾份（已經套用出去的遷移改不動，把它們掃出來只會得到一份改不動的清單，而**一支永遠是紅的檢查跟沒有那支檢查一樣：沒有人會再看它一眼**）。

**迭代 9 動了六支既有的驗收腳本，而且是非動不可的。** 題目與選項改成資料之後， 那幾支腳本原本照共用常數湊一份答案出來，送出去會被後端以「版本不符」擋下——**而擋下是對的**。 改法是加一支共用的填答器（`scripts/lib/questionnaire.ts`）：先問後端「現在生效的是哪一版、有哪幾題」， 再照那一份填。**斷言一條都沒有放寬**，改的只是「答案從哪裡來」。 另外 `verify:iteration4`、`verify:iteration5` 各多了一段： 離院衛教與班表、成效基準首波是關閉的，因此先確認關著時真的擋得住，再暫時提供、驗完關回去—— **驗收腳本不該因為預設是關的就跳過那一段，也不該把它留在開著的狀態。**

其中 `verify:iteration2` 改了一處，而且只有這一處：FR-N10 讓「只填自由文字即可結案」不再成立，那一段跟著改成新的結案方式。**迭代 2 原本要驗的行為一條都沒有放寬**——狀態轉換、留下處理者、總覽不再顯示待處理，斷言全部保留。這是目前唯一一次刻意改動既有驗收腳本，理由記在《實作規格書》1.1 節；其餘情況一律不得以「配合新功能」為由修改既有腳本。迭代 6 與迭代 7 都沒有再動過任何一支——迭代 7 的解除綁定回應只多了兩個欄位，既有欄位一個都沒有動，因此既有斷言原封不動仍然成立。

完整的手動測試步驟另有[測試手冊](https://94sh09sh19sh.github.io/hd-docs/latest/testing/manual-test-guide/index.md)：主手冊加迭代 3～17 二十一本分冊，**共 1051 個可勾選的測試項**（主手冊 156 項，分冊從迭代 3 的 66 項到迭代 14.5 的 11 項；0930 定版時 894 項）。迭代 17 起項次改用兩個字母（`aa`）。 0919 以前那幾冊要人眼與實機的部分仍然成立（迭代 3 的總覽螢幕連續 4 小時與拔網路、迭代 6 輪播的四節手指確認、迭代 8 標 ⚠️ 的十一項、迭代 9 的三條畫面護欄）， 0926 之後的幾冊，**腳本驗不到、還沒走的**集中在這幾處：

- **[迭代 11 分冊](https://94sh09sh19sh.github.io/hd-docs/latest/testing/iteration-11/index.md)** 的 43 項，對應的實測已在開發機走過一輪（演練紀錄第 8 節）；**斷電重開後服務自己回來**只能在院內那台主機驗（Q-27）
- **[迭代 12 分冊](https://94sh09sh19sh.github.io/hd-docs/latest/testing/iteration-12/index.md)** 的 48 項：開發手機從下載頁安裝、釘住後退不出去、契約版本不合時平板上的提示列（§12.5～§12.7）——**要一支真的手機**
- **[迭代 13 分冊](https://94sh09sh19sh.github.io/hd-docs/latest/testing/iteration-13/index.md)** 的 47 項：實驗室上的真模型實測與繁中品質紀錄（§13.4），等實驗室連線
- **[迭代 14 分冊](https://94sh09sh19sh.github.io/hd-docs/latest/testing/iteration-14/index.md)** 的 56 項：九項任務由第三者一個動作完成並錄影（`x39`，Q-31）、開發機＋開發手機走一次部署一輪（`x56`）
- **[迭代 15](https://94sh09sh19sh.github.io/hd-docs/latest/testing/iteration-15/index.md)～[17](https://94sh09sh19sh.github.io/hd-docs/latest/testing/iteration-17/index.md)** 共 126 項：模擬部署（`--profile simulation`）走一輪、第三次進院在院內跑探測工具；**長者看跑馬燈速度**（迭代 16 §16.10，做完之前院內的開關保持關閉）；簡易版草稿卡在護理站解析度下實際看過（`aa9`～`aa26`）；實驗室模型重寫隨版本帶入的草稿（`aa32`、`aa33`）
- **[迭代 14.1](https://94sh09sh19sh.github.io/hd-docs/latest/testing/iteration-14-1/index.md)～[14.5](https://94sh09sh19sh.github.io/hd-docs/latest/testing/iteration-14-5/index.md)** 共 95 項：真的平板掃佈建 QR code（`x72`～`x77`）、直式實機（Q-33）、14.3 的四種斷線情境在瀏覽器實際看一次（`x111`～`x128`）、14.4 一次送出九則求助在兩種尺寸下看一次（`x131`～`x139`）、14.5 在暗的透析室裡由醫護看一次白底（`x146`）與 10 吋實機（`x150`）

______________________________________________________________________

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

______________________________________________________________________

## 12. 下一階段

迭代 15～17 已完成（2026-10-05）。成效基準的建檔介面自迭代 5 就緒，**現在等的仍是現場的數字**：

> ⏰ **成效基準的量測（Q-01）有時效性。** 這不是開發端能做的事。系統正式啟用前沒測到，之後所有「省下 X 分鐘」的說法都只能靠估算。

### 第三次進院之前

1001 第二次進院 B 級部分成功，卡在護理端登入（`CORS_ORIGINS` 不放行護理端的來源）。第三次進院的目標與順序在實作規格書 4.19：

| 要做的事                                                                                                                                                 | 在哪裡                                       | 卡在誰                                      |
| -------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------- | ------------------------------------------- |
| **主機位址由名稱換成 IP**                                                                                                                                | 部署手冊第十五冊之四、清冊 Q-27 第 12 題     | 現場。**1007 答覆 IP 是固定的**，前提成立   |
| 關掉 Docker Desktop 的使用統計（市集自動更新照舊不改）                                                                                                   | 第十五冊 V-05、清冊 Q-27 第 9、10 題         | 現場（1007 答覆可以關）                     |
| 帶去的 tag 在開發機用 IP 模擬部署一次（含 `--profile simulation`），並故意用 `localhost` 開一次重現 `Failed to fetch`                                    | 第十五冊之三 E-02；部署規範第 9 章第 8 項    | 開發端（要開 Docker Desktop）               |
| 帶新 tag 是一次**更新**（迭代 15、17 各有一個遷移），照第十一冊 W-19 換版，不是重新 clone                                                                | 第十五冊之三 E-04                            | 開發端                                      |
| 院內護理站的電腦登入成功之後，備份還原與重新開機各走一次；重新開機照 1007 的答覆測：開機、以 Administrator 登入（模擬護理長），之後不碰任何東西          | 第十五冊 V-19、第十五冊之三 E-09             | 現場                                        |
| 探測院方 API：只印結構、位址當場輸入不寫進 `.env`                                                                                                        | 第十五冊 V-30a、清冊 Q-09 第 9 題            | 現場；**本系統能不能用、要不要報備待 Q-35** |
| 1001 那台主機有 15 床的預設床位（迭代 15 以前的版本建的），接上院方資料後到系統管理把 `01`～`15` 拿掉                                                    | 實作規格書 4.13 待做                         | 現場                                        |
| Defender 排除、主機上的 Git、Docker Hub 的 DNS（斷電重開、Docker Desktop 兩項設定 1007 已答）                                                            | 清冊 Q-27 其餘各題                           | 院方。不擋登入，但首波試用前要有答案        |
| ~~沒有預計結束時間時三處進度統一用開始後 4 小時（1007 決定）~~ **1007 迭代 17.5 已完成**                                                                 | 迭代 17.5 修正紀錄                           | —                                           |
| ~~專業版總覽與常駐總覽螢幕要不要也改成透析進度；沒有預計結束時要不要用開始後四小時判定「待確認下機」~~ **1007 使用者決定全面套用，迭代 17.5 追加已完成** | 迭代 17.5 修正紀錄                           | —                                           |
| 開發手機上的外殼實機驗收、真的平板掃佈建 QR code                                                                                                         | 迭代 12 §12.5～§12.7、迭代 14.1 `x72`～`x77` | 開發端                                      |
| 實驗室上的真模型實測；用 `marquee:bundle` 重寫隨版本帶入的草稿                                                                                           | 部署手冊第十三冊、迭代 17 `aa32`、`aa33`     | 實驗室連線（Q-08）                          |

第三次進院照部署手冊**第十五冊**（新手版第二版）與之三、之四走。

### 迭代 15～23（1005 第三次重排，1010 補 17.8 與 20～23）

| 迭代       | 主題                                                       | 可否立即開始                                                                                                                                                                                                                                           | 啟用前要等的外部答覆                                                                      |
| ---------- | ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------- |
| ~~15~~     | ~~院方 API 介接與自動化（1005）~~                          | **實作完成（1005）**，模擬院方 API 上驗收通過                                                                                                                                                                                                          | 對真實資料啟用：第三次進院的探測（Q-09 第 9 題）、使用報備與連線（Q-35）                  |
| ~~16~~     | ~~病人端「本次透析」面板與跑馬燈（1005）~~                 | **實作完成（1005）**，模擬院方 API 上驗收與開發機截圖通過；跑馬燈速度待長者試看                                                                                                                                                                        | 無；實機待 Q-33，病人試看待 Q-31                                                          |
| ~~17~~     | ~~跑馬燈內容由 AI 生成、護理師核准（1005）~~               | **實作完成（1005）**，驗收通過；隨版本帶入的草稿待實驗室模型重寫                                                                                                                                                                                       | 正式環境的 AI 需 Q-07；在那之前用隨版本帶入的草稿；核准權限 1007 已答（所有護理師，Q-28） |
| ~~17.8~~   | ~~護理紀錄補上線前的缺口、緊急回報的圖示（1010）~~         | **已完成（1010）**，腳本驗收通過                                                                                                                                                                                                                       | 無（Q-37 已結案）                                                                         |
| ~~18~~     | ~~規則引擎與三項高風險功能（原 7 → 11 → 15）~~             | **已完成（1010）**，合成資料驗收與開發機截圖通過；臨床端逐句讀輸出待做                                                                                                                                                                                 | 對真實病人啟用：法務書面確認（Q-02）＋臨床端門檻值（Q-03）                                |
| ~~18.1~~   | ~~書面確認閘門改放進系統管理、四條規則的建議門檻（1010）~~ | **已完成（1010）**，腳本驗收通過                                                                                                                                                                                                                       | 四條規則的門檻請醫師確認（1014 週報、Q-03）                                               |
| ~~19~~     | ~~管理儀表板、獎勵、對外揭露（原 8 → 12 → 16）~~           | **已完成（1010）**                                                                                                                                                                                                                                     | L3 啟用需護理部同意（Q-04）；指標定義（Q-20）與核准角色（Q-21）                           |
| ~~20~~     | ~~遊戲化之一：平板現有功能的遊戲化（1010）~~               | **已完成（1010）**，腳本驗收與開發機截圖通過                                                                                                                                                                                                           | 無；長者在床上看過（Q-31 第 8 題）、預設小撇步與回覆的措辭請護理部看過                    |
| ~~21~~     | ~~遊戲化之二：透析小花園、送花、匿名彙總（1010）~~         | **已完成（1010）**，腳本驗收與開發機截圖通過                                                                                                                                                                                                           | 無；長者看插畫（Q-31 第 8 題）、台灣百合收不收請護理部看                                  |
| ~~22～23~~ | ~~遊戲化之三、之四（1010）：麻將連連看、記憶相簿~~         | **已完成（1011）**；23 切成三次子迭代（《[迭代 23 的三次子迭代](https://94sh09sh19sh.github.io/hd-docs/latest/notes/iteration-23-split/index.md)》），23.1 子文件、60 張的資料、圖卡產生器與第一批 30 張圖、23.2 第二批 30 張圖、23.3 程式 1011 都完成 | 無；開給病人前要長者實際玩過（Q-31 第 8 題）                                              |

迭代 15 的第一項是院方 API 探測工具，要趕在第三次進院前完成（實作規格書 4.19）——**1005 已完成**，指令在部署手冊第十五冊 V-30a；迭代 16、17 都不擋第三次進院。三個迭代的實作位置見 6「迭代 15」～「迭代 17」。

~~迭代 18 與其他迭代沒有相依，外部答覆若提早到齊可隨時往前插隊。~~ 迭代 18 與 18.1 已於 1010 完成，對真實病人啟用仍等 Q-02、Q-03。 ~~迭代 19 的成效指標會吃迭代 6 產生的 `carousel_view_events`（迭代 16 起改記跑馬燈每一則的播放），但那張表刻意不含個人層級資料， 因此它只回答得了「哪一類內容有人看」這種問題。~~ 迭代 19 已於 1010 完成：九個成效指標讀的是求助、護理紀錄、衛教完成、症狀問卷的時間戳，**沒有用到播放紀錄**（它只回答得了「哪一類內容有人看」，不是成效）。

**1010 的順序**（實作規格書 4.0.5）：17.8 → 18 → 19 → 20～23；~~**做到 21**，下一個是 22（麻將連連看：牌面先用 FluffyStuff 的 CC0 牌面，「萬」字與紅中改深棕）。~~ **1011 全部做完**。**這一次沒有改號**：排在 18 前面的只有小迭代 17.8。 17.8 的兩個技術重點：院內以 `http://<IP>` 開護理端，不是安全來源，**複製要退回 `document.execCommand('copy')`**；護理紀錄的預設版位改主列，但既有環境的版位存在資料表、不會被預設值覆蓋，要一次性的資料遷移。 院方建議的血壓正常區間判斷不做（SRS FR-P11 補充說明），程式不動。

**接手時最容易搞混的一件事**：迭代編號重排過三次（0919、0926、1005）。 0916 以前的紀錄裡「迭代 7」、0923 以前的「迭代 11」、1005 以前的「迭代 15」指的都是規則引擎；0923 週報寫的「迭代 11、12 依原排程開始」也是既成紀錄。 **那些舊紀錄不回頭改寫**，對帳時看實作規格書 4.0.1、4.0.3、4.0.4 的對照表。

### 迭代 24～27（1015、1017 排定；1018 迭代 24、25 與 26.1 完成）

| 迭代 | 主題                                                                                                                             | 可否立即開始                                                                                                                                        | 啟用前要等的外部答覆                                                                                       |
| ---- | -------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| 24   | 遊戲化之五：花園與相簿的擴充（1015）——種子袋、小訪客、兩個圖鑑照分類排、花 36 種、圖卡 120 張；切成四次子迭代（實作規格書 4.24） | **1018 完成**（四次子迭代，見第 6 節「迭代 24」）；長者在床上看新的內容待做                                                                         | 無；新內容開給病人前請社工、護理部、長者看過（Q-31 第 9 題）                                               |
| 25   | 緊急通報：頂端橫幅、床邊前速覽、護理紀錄連動（1015）；切成三次子迭代（4.25）                                                     | 可以，從 25.1 開始；25.1 很小，可以插在 24 前面                                                                                                     | 無；速覽多讀的院方欄位，真實格式等第三次進院的探測（Q-09 第 9 題）                                         |
| 26   | 管理儀表板、獎勵制度與對外揭露的更新與修正（1017）；切成三次子迭代（4.26）                                                       | **26.1 1018 完成**（52 條指標、平板連線紀錄、定義變更紀錄、對外報表的次要遮蔽與跨報表比對、依月份、附基準）；26.2、26.3 接著做（25 已完成，不再等） | 不擋實作；獎勵制度開關開給護理師前要護理部同意試行，定義與權重、未指名比例的門檻（Q-20），核准角色（Q-21） |
| 27   | 病人平板固定橫放：外殼鎖橫向、拿掉直放排法、麻將放寬（1014 定、1017 排）（4.27）                                                 | 可以；外殼在另一個 repo，兩邊一起改，**只改外殼內部、不動契約**                                                                                     | 無；實機待 Q-33 的型號                                                                                     |

**順序**：四個迭代彼此只有 26 依賴 25；**27 最好排在第三次進院帶去的 tag 之前**——院內還沒佈建任何平板，那時裝的就是鎖橫向的外殼，不必逐台重裝（部署規範 DEP-20）。測試分冊的項次 24 用 `ah`、25 用 `ai`、26 用 `aj`、27 用 `ak`。

______________________________________________________________________

## 13. 每次動工前的自我檢查

摘自《實作規格書》第 5 章與《資料庫使用規範》第 16 條：

- 新增的資料表／欄位是否已對照 SRS 與稽核軌跡欄位需求
- 有沒有前端程式碼企圖直接碰資料庫檔案
- 存取控制是否寫在後端應用層（不依賴檔案權限或前端隱藏）
- 是否在業務邏輯中直接寫 SQL 或 SQLite 方言
- 新增的臨床數值欄位是否誤用浮點數
- 是否新增了第二個會寫入資料庫的常駐行程
- 是否有任何相依指向院外網域（跑 `npm run check:egress`）
- 呼叫語言模型是否一律經 `AiGatewayService`
- 是否在資料庫交易內等待模型回應
- 本次功能是否觸及有條件納入的項次；若是，功能開關是否預設關閉、前後端是否都擋
- 測試資料是否為虛構合成資料
- MDM 呼叫是否皆透過 `MdmProviderPort`
- schema 是否維持相容約束（無 enum、無 JSON 欄位、單一級聯路徑）
- 新畫面有沒有掛上導覽版位（`@RequireNavItem()`），還是又多了一個關不掉的功能
- 新增的選項或題目是不是寫進資料表，而不是又回到程式常數（跑 `npm run check:ui`）
- 護理長會想調的數字，有沒有放在只有工程師動得到的地方（`.env` 而非營運參數）
- 簡易版要做的事，是不是只呼叫專業版原有的端點；真的要加端點，是不是只做加法（`npm run verify:iteration14`）
- 用到的圖示有沒有在介面設計基準 4.6 登記、由 `sync-icons.mjs` 產生，而不是從套件或 CDN 直接引入
- 動了 `docker-compose.yml`、`Dockerfile` 或 `deploy/hospital.env.example`，有沒有回頭核對部署手冊第十一、十五冊與兩本 `.env` 子手冊（第十五冊之一、之二）（`npm run check:container`）
- 動了外殼契約，有沒有三處一起改：契約文件、`kiosk-shell.ts`、`shell.pin`（`npm run verify:iteration12`）
- 院方 API 判斷得出來的事，有沒有又要求護理師操作（SRS FR-S15）；同步要寫的東西，是不是走護理師操作時同一支服務
- 病人端面板有沒有出現判讀：警戒線、正常範圍、紅色、預測（`npm run check:ui:design`）
- 送進 AI 的東西有沒有任何病人資料；病人端看得到的 AI 產出，是不是一定先經護理師核准

______________________________________________________________________

## 版本歷程

| 定版                                                                            | 日期       | 異動                                                                                                                                                                                                                                                       |
| ------------------------------------------------------------------------------- | ---------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [1014](https://94sh09sh19sh.github.io/hd-docs/1014/reports/progress-technical/) | 2026-10-14 | 對到迭代 23：規則引擎與書面確認閘門、對外報表與展示環境、遊戲化四款的模組與離線補送、病人詳細資訊與社工醫師唯讀帳號；1014 正式版病人平板固定橫放                                                                                                           |
| [1007](https://94sh09sh19sh.github.io/hd-docs/1007/reports/progress-technical/) | 2026-10-07 | 改寫到迭代 17.7：迭代 15～17 的架構、資料表與端點；17.1～17.7 工程上要知道的事（每一次一張表）；資料表 59 張、遷移 14 個；驗收腳本清單補到 `verify:iteration17-7`；開放議題與下次進院清單更新                                                              |
| [0930](https://94sh09sh19sh.github.io/hd-docs/0930/reports/progress-technical/) | 2026-09-30 | 改寫到迭代 14.5：迭代 11～14 與 14.1～14.5 的實作、規模表、驗收腳本清單與手動測試 894 項；已知問題第 6 項改為平板型號未定（尺寸 0930 已確定）；Q-27、Q-32 的 0930 答覆                                                                                     |
| [0923](https://94sh09sh19sh.github.io/hd-docs/0923/reports/progress-technical/) | 2026-09-23 | 補上迭代 7～10：部署前的缺陷修正與資料保護、兩端介面重新設計、導覽版位與內容資料化、離線安裝包與平板佈建。規模表加一欄（資料表 40 → 54、營運參數 12 → 20），共用常數那一節改寫——附錄 C 的內容搬進資料表之後，那幾份常數只剩「把舊版補寫成第 1 版」一個用途 |
| [0916](https://94sh09sh19sh.github.io/hd-docs/0916/reports/progress-technical/) | 2026-09-16 | 改寫到迭代 6：封閉網路化、AI 輔助與護理記錄、求助處理與班表、閒置輪播與檔案匯入；資料庫改為 SQLite、推播改為院內 SSE 與常駐總覽螢幕，並換上重繪的架構圖                                                                                                    |
| [0909](https://94sh09sh19sh.github.io/hd-docs/0909/reports/progress-technical/) | 2026-09-09 | 首次定版                                                                                                                                                                                                                                                   |

[← 回進度首頁](https://94sh09sh19sh.github.io/hd-docs/latest/index.md)
