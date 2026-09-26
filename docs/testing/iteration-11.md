# 迭代 11 手動測試 — 部署改為 Docker ＋ git clone

> 《[完整手動測試手冊](manual-test-guide.md)》的分冊之一，對應《實作規格書》4.9 節。
> 共用的環境準備、啟動與疑難排解都在主手冊，這一冊只寫迭代 11 的部分。
> 操作端色籤（**護理端**／**病人端**／**終端機**／**資料庫**）的意思見主手冊 §00。

**這一冊驗的是「院內那一套指令真的走得完」。** 迭代 10 要一台乾淨的機器，是因為安裝包要證明它不依賴開發機；
容器本身就是那個乾淨環境（《部署規範》第 9 章最後一段），所以本冊**全部在開發機上做得完**，
但 §11.3 起**只准用 Git 與 Docker**，指令照抄《[部署手冊](../deployment/index.md)》第十一冊。

| 標記 | 意思 |
|---|---|
| 🖥 **開發機** | 平常的開發環境（有 Node.js），用來做檢查與驗收腳本 |
| 🐳 **開發機，只用 Git 與 Docker** | 部署實測。這一段用到 `npm`、`node` 就不算數 |

## 這一冊有什麼

| 節 | 內容 | 在哪裡做 | 對應 |
|---|---|---|---|
| §11.1 | repo 裡已經沒有安裝包 | 🖥 | 部署規範 3.5 |
| §11.2 | 容器設定盤點與零院外連線的新範圍 ⚠ | 🖥 | DEP-14、DEP-37 |
| §11.3 | 從零部署 | 🐳 | DEP-22、第十一冊 W-08～W-17 |
| §11.4 | 正式環境設定拒絕 `lab` | 🐳＋🖥 | DEP-40 |
| §11.5 | `down -v` 刪不掉資料庫 | 🐳 | 部署規範 3.3 |
| §11.6 | 更新演練 ⚠ | 🐳 | DEP-19、DEP-44、第十一冊 W-19 |
| §11.7 | 回退演練 ⚠ | 🐳 | DEP-19、規範 18.3、第十一冊 W-20 |
| §11.8 | 自動化驗收 | 🖥 | — |

**前置**：

| 要準備的 | 本冊哪裡會用到 | 怎麼弄出來 |
|---|---|---|
| Docker Desktop 在跑（Linux 容器模式） | §11.3 起 | `docker info` 看得到 `linux x86_64` |
| 一個暫存目錄，底下 `config\`、`backups\` 兩個子目錄 | §11.3 | 第十一冊 W-08，路徑換成暫存目錄 |
| 三個開發時沒在用的埠（例如 13000、18080、18081） | §11.3 | 第十一冊 W-07 |
| `docker volume ls` 裡沒有 `hd-tablet-care-*` | §11.3 | 有的話照第十一冊第 8 節撤除 |

> **全程用 PowerShell。** Git Bash 會把 `/backups/…` 這類參數轉成 Windows 路徑，§11.7 的還原會回報找不到備份檔（第十一冊第 7 節）。

---

## 11.1 · repo 裡已經沒有安裝包（部署規範 3.5）🖥

- [ ] `u1` **［終端機］** `npm run` 列出所有指令。
  → 沒有 `package:build`、`package:verify`；有 `check:container` 與 `verify:iteration11`。
- [ ] `u2` **［終端機］** 看 `scripts/` 目錄。
  → 沒有 `build-offline-package.mjs`、`verify-package.mjs`、`package-templates/`。
- [ ] `u3` **［終端機］** 在 `apps/`、`scripts/`、`deploy/` 與根目錄設定檔裡搜尋 `PRISMA_ENGINES_DIR`。
  → 只剩 `scripts/verify-iteration11.mjs`（它要列出這個名字才能檢查）。
- [ ] `u4` **［終端機］** 開 `.env.example`。
  → 沒有安裝包那兩段（包內引擎、靜態資源連接埠）；容器那一段換成一句話，指向 `deploy/hospital.env.example`。
- [ ] `u5` **［護理端］** 系統管理 → 執行環境。
  → 不再有「資料庫引擎：由安裝包自帶」那一列。

## 11.2 · 容器設定盤點與零院外連線的新範圍（DEP-14、DEP-37）🖥

- [ ] `u6` **［終端機］** `npm run check:container`
  → 全部 ✓：專案名稱固定、兩個資料卷 external、繫結掛載只有備份與設定、沒有 privileged／host 網路／Docker socket、
  沒有 `env_file`、資料卷只掛給 `api`、每個服務都寫 `TZ`、標籤帶 `HD_IMAGE_TAG`、`pull_policy: never`、五個服務齊全。
- [ ] `u7` ⚠ **［終端機］** 在 `docker-compose.yml` 的 `nurse-web` 底下暫時加一行 `volumes: ["C:/:/host"]`，再跑 `u6`。
  → **「有不允許的繫結掛載」變紅**，並寫出是哪個服務、哪個來源。改回去再跑一次確認恢復。
  *0922 的 `-v /c:/app` 就是這一行。每個檢查都要有人看過它失敗的樣子。*
- [ ] `u8` ⚠ **［終端機］** 把 `api` 的 `LLM_PROVIDER` 預設值暫時改成 `${LLM_PROVIDER:-lab}`，再跑 `u6`。
  → 「compose 的 LLM_PROVIDER 預設為 lab」變紅。改回去。
- [ ] `u9` **［終端機］** `npm run check:egress`
  → 「映像檔內容」「AI 閘道」兩列出現，都是 0 筆；已沒有「安裝包」那一列。
  AI 閘道那列會附註「尚無程式碼（迭代 13）」。
- [ ] `u10` ⚠ **［終端機］** 在 `Dockerfile` 執行階段最後暫時加一行 `COPY --from=builder /build/docs ./docs`，再跑 `u9`。
  → 「映像檔內容」變紅：`/build/docs` 不在任何一節的掃描範圍內。改回去。
- [ ] `u11` **［終端機］** `npm run check:offline`
  → 標題是「執行期不下載、遷移只前滾」，沒有「引擎檔已就位」「建置產物」「Node 版本」這幾項，沒有阻擋項。

## 11.3 · 從零部署（DEP-22）🐳

照第十一冊走，**每一步的輸出存檔**。以下只列要看的結果。

- [ ] `u12` **［終端機］** 從 GitHub **重新 clone** 到暫存目錄（不是平常的工作目錄），`git checkout <tag>`，`git describe --tags`。
  → 印出的正是要驗的 tag。
- [ ] `u13` **［終端機］** 複製 `deploy\hospital.env.example` 到暫存的 `config\.env` 並填好；`$cfg` 指向它；`docker compose --env-file $cfg config --quiet`。
  → 沒有輸出。故意把 `HD_API_PORT` 清空再跑一次：錯誤訊息寫著「請設定 HD_API_PORT（向資訊室登記過的埠）」。填回去。
- [ ] `u14` **［終端機］** `docker volume create hd-tablet-care-data`、`docker volume create hd-tablet-care-keys`
  → 兩個名字出現在 `docker volume ls`。
- [ ] `u15` **［終端機］** `docker compose --env-file $cfg build`
  → `Image hd-tablet-care:<tag> Built`。
- [ ] `u16` **［終端機］** W-14 那一行套用遷移。
  → `All migrations have been successfully applied.`，輸出裡**沒有任何** `binaries.prisma.sh`。
- [ ] `u17` **［終端機］** `docker compose --env-file $cfg up -d`，再 `ps`。
  → `api`、`nurse-web`、`patient-web` 三個 `Up`；**沒有** `ai-gateway`、`shell-builder`。
- [ ] `u18` **［終端機］** `docker compose --env-file $cfg logs api --tail 40`
  → `synchronous=FULL`；`版本標記：…（正式環境設定）`；`伺服器時區：Asia/Taipei`；
  **沒有**「時區來自環境變數 TZ…主機時區仍要…確認」那一行警告（容器裡的 TZ 就是它該看的時區）。
- [ ] `u19` **［護理端］** 瀏覽器開 `http://localhost:<護理端埠>`，用 `SUPER_ADMIN_*` 登入。
  → 被要求改密碼；改完進得去。
- [ ] `u20` **［護理端］** 系統管理 → 執行環境。
  → 伺服器時區 Asia/Taipei（由環境變數指定）、執行環境「正式」、監聽連接埠 3000（主機設定檔指定）。
- [ ] `u21` **［病人端］** 瀏覽器開 `http://localhost:<病人端埠>`。
  → 出現病人端畫面；開發者工具的網路分頁裡，API 請求打的是 `HD_PUBLIC_API_URL`，不是 `localhost:3000`。
- [ ] `u22` **［護理端］** 系統管理 → 立即備份，記下檔名與 SHA-256。
  → 暫存的 `backups\` 目錄裡出現那個檔。
- [ ] `u23` **［終端機］** 照 W-17 還原到 `/data/restore-check.db` 並刪掉。
  → SHA-256 相符、完整性檢查 ok；`rm` 成功。
- [ ] `u24` **［終端機］** `docker compose --env-file $cfg --profile ai --profile shell config --format json`，看每個服務的 `volumes`。
  → `type: bind` 的只有兩種來源：暫存的 `backups`（掛到 `/backups`）與 `config`（掛到 `/config`）。

## 11.4 · 正式環境設定拒絕 `lab`（DEP-40）🐳 ＋ 🖥

- [ ] `u25` **［終端機］** `docker compose --env-file $cfg run --rm --no-deps -e LLM_PROVIDER=lab api`
  → 後端**起不來**，結束狀態非 0；錯誤訊息寫著「正式環境設定下不得使用 LLM_PROVIDER=lab…（《部署規範》DEP-40）」。
- [ ] `u26` 🖥 **［終端機］** 開發機上 `.env` 暫時設 `DEPLOYMENT_ENV=production`、`LLM_PROVIDER=lab`，`npm run dev:api`。
  → 拒絕啟動，訊息指向 DEP-40。若先被別的正式環境檢查擋下（連接埠、時區），照訊息補齊再試。**做完兩個值都改回去。**
- [ ] `u27` 🖥 **［終端機］** 只設 `LLM_PROVIDER=lab`、`DEPLOYMENT_ENV` 留空，`npm run dev:api`。
  → 正常啟動。開發環境接實驗室是允許的（DEP-01 由合成資料檢查另外擋），改回 `mock`。

## 11.5 · `down -v` 刪不掉資料庫（部署規範 3.3）🐳

- [ ] `u28` **［護理端］** 裝置管理新增一台測試平板，序號寫 `U28-BEFORE`。
- [ ] `u29` **［終端機］** `docker compose --env-file $cfg down -v`，再 `docker volume ls`，再 `up -d`。
  → `down -v` 之後兩個資料卷**都還在**；重新啟動後登入，`U28-BEFORE` 還在。

## 11.6 · 更新演練（DEP-19、DEP-44）🐳

在暫存的 clone 裡做一個測試用的新版：改 `apps/api/package.json` 的 `version`（例如加 `-drill`），
另加一個只建一張空表的遷移，commit 後打一個本機 tag。**這個 tag 只存在暫存 clone，不要推。**

- [ ] `u30` **［終端機］** `git checkout <測試 tag>`，`.env` 的 `HD_IMAGE_TAG` 改成它，`build`。
  → `docker images hd-tablet-care` 同時看得到舊、新兩個標籤。
- [ ] `u31` ⚠ **［終端機］** **先不要停 `api`**，直接跑 W-19 的 `db-update.mjs` 那一行。
  → **更新中止：後端服務還在執行**。資料庫沒被動到。
  *這一條在迭代 11 實測前是壞的：一次性容器問的是自己的 `127.0.0.1`，永遠以為服務已停。*
- [ ] `u32` **［終端機］** `stop api`，再跑一次 `db-update.mjs`。
  → 依序：服務已停 → 更新前備份（印出檔名與 SHA-256，**抄下來**）→ 驗證還原 ok → 套用了 1 個遷移 → 寫入更新紀錄 → 更新完成。
- [ ] `u33` **［終端機］** `up -d`
  → 三個服務的映像檔都是新標籤。
- [ ] `u34` **［護理端］** 系統管理。
  → 版本標記是新版本；版本更新紀錄多一筆；`U28-BEFORE` 還在。
- [ ] `u35` **［護理端］** 裝置管理新增一台 `U35-AFTER`。（§11.7 會用它證明回退的代價）

## 11.7 · 回退演練（DEP-19、規範 18.3）🐳

- [ ] `u36` **［終端機］** `git checkout <原 tag>`，`HD_IMAGE_TAG` 改回，**不要 build**。
  → `config --quiet` 沒有輸出；舊映像檔還在，不需要重建。
- [ ] `u37` **［終端機］** 照 W-20：`stop api` → 把 `hd.db` 移到 `/data/before-rollback/` → 還原 `u32` 抄下的那份備份到 `/data/hd.db`。
  → SHA-256 相符、完整性 ok、「還原的就是 DATABASE_URL 指向的正本」。
- [ ] `u38` **［終端機］** `up -d`，再 `ps`。
  → 三個服務的映像檔都是原標籤。
- [ ] `u39` **［護理端］** 系統管理與裝置管理。
  → 版本標記回到原版本；`U28-BEFORE` 在，**`U35-AFTER` 不在**。
  *這是預期的：資料庫不能把遷移倒回去，回退等於「舊程式＋更新前那份備份」。所以回退要在累積新資料之前決定。*

## 11.8 · 自動化驗收 🖥

- [ ] `u40` **［終端機］** `npm run verify:iteration11`
  → 靜態部分全部 ✓；最後列出要看演練紀錄的幾項。
- [ ] `u41` **［終端機］** `npm run verify:iteration11 -- --live --env-file <暫存的 config\.env>`
  → 加上 Docker 上的四項也全部 ✓：`compose config` 解析後只有兩個繫結掛載、`lab` 被拒、`down -v` 後資料卷與 `hd.db` 都在、重新起來後 health 正常。
- [ ] `u42` **［終端機］** `npm run check:all`
  → 六支全綠（多了「容器設定」）。
- [ ] `u43` 收尾：照第十一冊第 8 節撤除這次實測的容器、資料卷與映像檔，**確認刪的是暫存那一套**（專案名稱一律是 `hd-tablet-care`，開發機上若另有正在用的同名專案，先停下來想清楚）。

---

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|

[← 回主手冊](manual-test-guide.md) · [← 回進度首頁](../index.md)
