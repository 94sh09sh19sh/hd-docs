# 文件維護作業指示（agent 用）

給接手維護 `docs/` 的 AI agent。人用的完整說明在 [HOWTO.md](HOWTO.md)，本頁只寫可執行的規則。

---

## 前提

- 文件真本在 `docs/`；HackMD 是**單向鏡像**（repo → HackMD）。不要以 HackMD 的內容為準。
- `.hackmd-build/` 是產物，不進版控，不要手動編輯。
- 需要登入 HackMD 的動作（建立 note、發佈、設定 slug、上傳圖片）**agent 一律不做**，
  產出檔案後把待辦交給使用者。

## 目錄職責

| 路徑 | 內容 | 可否修改 |
|---|---|---|
| `docs/index.md` | 導覽首頁 | 可，但只加連結與三到五條重點 |
| `docs/weekly/YYYY-MM-DD.md` | 每週紀錄，檔名用該週開會日（星期三） | 可新增；既有的不回頭改 |
| `docs/reports/` | 階段性報告 | 需求明確時才改 |
| `docs/requirements/` | 已定稿的需求文件 | **預設不改**，要改先問 |
| `docs/hackmd-map.json` | 檔案路徑 → HackMD 網址 | 新增檔案時補一行 |
| `scripts/hackmd-export.mjs` | 匯出工具 | 有需要才動 |

## 新增一篇週報

1. `cp docs/weekly/_template.md docs/weekly/<該週開會日（星期三）的 ISO 日期>.md`，填內容。
   第一行必須是 `# MMDD 週報 — <標題>`，匯出時會取它當 note 標題。
2. `docs/index.md` 的「每週紀錄」區塊**最上方**（`<!-- 新的一週… -->` 註解上方）插入：
   ```markdown
   ### [MMDD — <標題>](weekly/<檔名>)

   進度：

   - <三到五條>
   ```
3. `docs/hackmd-map.json` 的 `notes` 加 `"weekly/<檔名>": "https://hackmd.io/@94sh09sh19sh/hd<MMDD>"`。
   slug 規則：`hd` + MMDD。
4. `npm run docs:hackmd`，確認輸出沒有「找不到對應」的項目。
5. commit（訊息 `docs: 週報 MMDD`）。**push 要先問過使用者。**
6. 回報使用者要手動做的事：貼上新週報建 note（slug 為何）、重貼首頁 note。
   **每一項都寫出完整檔案路徑，且一律是 `.hackmd-build/` 底下的檔案。**

## 新增其他文件

同上，差別只在放置目錄與 slug 命名（自訂，沿用 `hd-` 前綴），並在 `docs/index.md`
的對應區塊（Link 或附錄）加連結。

## 硬性規則

- **連結一律用相對路徑**寫在 `docs/` 裡。HackMD 的絕對網址只出現在 `hackmd-map.json`，
  不要把 `https://hackmd.io/...` 直接寫進 `docs/` 的內文。
- 只存在於 repo、不會有對應 note 的連結目標（例如 `../README.md`），
  加進 `hackmd-map.json` 的 `strip`，匯出時會退成純文字，避免鏡像上出現死連結。
- **根目錄 `README.md` 不上 HackMD，`docs/` 裡也不要連它、不要提它。**
  它含環境變數清單、資料庫連線設定與內部取捨，HackMD 的自訂網址等同公開連結，
  不適合放這些內容。`strip` 只是最後一道防線，正確做法是一開始就不要寫這個連結。
  需要指路時寫「見專案 repo」即可，不要放路徑。
- **交給使用者貼上 HackMD 的內容，一律取自 `.hackmd-build/`，絕不能給 `docs/` 原始檔。**
  兩者只差連結改寫與 front matter，長度往往只差幾十個字元，肉眼難辨，貼錯也不會有錯誤訊息，
  但那篇的內部連結會全部變成 `../xxx.md` 死連結。分辨法：**build 版第一行必為 `---`**，
  原始檔第一行必為 `#`。複製到剪貼簿時：

  ```powershell
  Get-Content -Raw -Encoding UTF8 .hackmd-build\<路徑> | Set-Clipboard
  ```

  省略 `-Encoding UTF8` 會依系統預設編碼頁（本機為 big5）讀取，中文全部變亂碼。
- 底線開頭的檔案（`_template.md`）不會被匯出，是刻意的。
- 改了 `docs/` 底下任何已鏡像的檔案，就要提醒使用者重貼那一篇；只改 repo 不算完成。
- 需求文件（`docs/requirements/`）與已發佈的週報視為既成紀錄。要修正就在新的一週寫明，
  不要靜默改寫歷史。

## 驗收

```bash
npm run docs:hackmd    # 不應出現「找不到對應」
git status --short     # 應只有預期中的檔案

# 交付前確認給的是 build 版：每一行都應該是 ---
head -1 .hackmd-build/<要交付的每一個檔案>
```

相對連結是否還指得到檔案，可用：

```bash
cd docs && for f in $(find . -name '*.md'); do d=$(dirname "$f"); \
  grep -o '](\([^)]*\))' "$f" | sed 's/.*](//;s/)$//' | while read -r l; do \
    case "$l" in http*|\#*) continue;; esac; t="${l%%#*}"; [ -z "$t" ] && continue; \
    [ -e "$d/$t" ] || echo "MISS $f -> $l"; done; done
```

（`weekly/YYYY-MM-DD.md` 是說明文字裡的佔位字串，出現在結果裡屬正常。）

---

[← 回進度首頁](../index.md)
