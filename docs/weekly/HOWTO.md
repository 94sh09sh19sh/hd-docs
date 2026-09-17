# 每週紀錄維護流程（人用）

這頁寫給隔了一週回來、細節已經忘光的自己。從「這週做完了」到「別人點得到」，全部步驟在這裡。
給 AI agent 執行的精簡版在 [AGENT.md](AGENT.md)。

---

## 一次講完的全貌

文件的**真本在 repo**（`docs/`），HackMD 上的是**鏡像**。所有內容都先改 repo，再同步過去，
不要反過來直接在 HackMD 上編輯——那樣兩邊會分岔，下次同步就會蓋掉你在網頁上打的字。

```
docs/weekly/2026-09-14.md   ← 寫這裡
docs/index.md               ← 加一段連結
        ↓  npm run docs:hackmd
.hackmd-build/              ← 自動產生，連結已換成 HackMD 網址（不進版控）
        ↓  複製貼上
HackMD note                 ← 別人看到的
```

---

## 每週五步

### 1. 開一份新的週報

```bash
cp docs/weekly/_template.md docs/weekly/2026-09-16.md
```

檔名用**該週開會日（星期三）的 ISO 日期**。開會日就是報告日，這樣檔案列表的排序就是時間序，不用另外想辦法。

內容照模板填。第一行 `# MMDD 週報 — 一句話標題` 很重要，匯出時會用它當 HackMD 的筆記標題。

### 2. 在首頁掛上連結

打開 `docs/index.md`，找到「每週紀錄」區塊，在**最上面**插入一段（新的排在上面）：

```markdown
### [0914 — 一句話標題](weekly/2026-09-14.md)

進度：

- 三到五條重點
```

檔案裡有一行 `<!-- 新的一週請把整段複製到這一行上方 -->` 標出插入點。

**首頁只放三到五條重點，細節一律留在週報裡。** 這是這套結構唯一需要自律的地方——首頁一旦開始長內容，累積半年後就沒人讀得下去了。

### 3. 登記 HackMD 網址

打開 `docs/hackmd-map.json`，在 `notes` 裡加一行：

```json
"weekly/2026-09-14.md": "https://hackmd.io/@94sh09sh19sh/hd0914"
```

slug 規則是 **`hd` + MMDD**。網址現在還不存在沒關係，第 5 步才會真的建出來。

### 4. 產生 HackMD 版本

```bash
npm run docs:hackmd
```

它會把 repo 裡的相對連結（`../reports/progress-clinical.md`）換成 HackMD 網址，
補上 `title:` front matter，輸出到 `.hackmd-build/`。

終端機會列出每個檔案的狀態，`✗` 代表那篇還沒登記網址。最後如果有「找不到對應」的清單，
就是漏填了什麼，補進 `hackmd-map.json` 再跑一次。

### 5. 同步到 HackMD

要動兩篇：**新的週報**和**首頁**（因為首頁多了一段連結）。

> ⚠️ **一律貼 `.hackmd-build/` 底下的檔案，不要貼 `docs/` 原始檔。**
> 兩者內容幾乎一模一樣，肉眼很難分辨，貼錯也不會有任何錯誤訊息——但那篇的內部連結會維持
> `../index.md` 這種相對路徑，在 HackMD 上全部是死連結。這是最容易犯、也最不容易發現的錯。

複製內容（用 PowerShell，編碼才會對）：

```powershell
Get-Content -Raw -Encoding UTF8 .hackmd-build\weekly\2026-09-14.md | Set-Clipboard
```

然後在 HackMD：

- **新週報**：新增筆記 → `Ctrl+A` → `Ctrl+V` → 發佈、讀取權限開給所有人 → slug 填 `hd0914`
- **首頁**：開 `hd-index` → 編輯 → `Ctrl+A` → `Ctrl+V`（slug 不用再設）

最後把新筆記拖進 `dialysis_system_md` 資料夾。純收納，不影響網址。

### 6. Commit

```bash
git add docs && git commit -m "docs: 週報 0914" && git push
```

`.hackmd-build/` 已經 gitignore，不會進版控——它隨時可以重新產生。

---

## 踩過的坑

| 症狀 | 原因 | 解法 |
|---|---|---|
| 貼到 HackMD 全是亂碼 | Git Bash 的 `clip` 把 UTF-8 當成 cp950 解讀 | 用 PowerShell 的 `Set-Clipboard`，或 `iconv -f UTF-8 -t UTF-16LE 檔案 \| clip` |
| 內容對了但分頁標題是亂碼 | HackMD 的標題是獨立的中繼資料，第一次貼壞就定型了 | 匯出的檔案開頭有 `title:` front matter，重貼一次即可 |
| 在資料夾裡按「新增筆記」，建完卻不在資料夾裡 | HackMD 一律建在根目錄，資料夾要事後指定 | 建完再拖進去，或全部建完一次搬 |
| 首頁連結點了 404 | 那篇 note 還沒建，或 slug 打錯 | 對照 `hackmd-map.json`，slug 必須完全一致 |
| 改了 `docs/` 但 HackMD 沒變 | 兩邊是手動同步的 | 重跑 `npm run docs:hackmd` 再貼一次 |
| 內容全對，但點內部連結沒反應／404 | 貼到的是 `docs/` 原始檔，不是 `.hackmd-build/` 版 | 重貼 `.hackmd-build/` 底下的同名檔案。檢查法：在 HackMD 上點內部連結，網址若出現 `../` 就是貼錯了 |
| 貼上後標題列沒有 `title:` 那幾行 | 同上，原始檔沒有 front matter | 同上。build 版一定以 `---` 開頭 |

---

## 什麼時候不只是加一篇週報

- **改了需求文件或進度報告** → 那篇的 HackMD note 也要重貼
- **新增一種文件**（不是週報）→ 見[附錄的做法](../index.md)：建檔 → 首頁加連結 → map 加一行 → 匯出 → 建 note
- **那週沒進度** → 不要建空頁，首頁直接跳過該週。時間序有斷點沒關係，硬湊出來的空白紀錄才難讀

---

[← 回進度首頁](../index.md)
