# hd-tablet-care 文件鏡像

血液透析中心平板照護輔助系統的文件站原始內容。**這裡是鏡像，不是真本。**

- 真本在開發用的私有 repo `docs/` 底下，由 `npm run docs:sync` 單向複製過來
- **不要直接在這個 repo 上編輯**：下次同步會整份覆蓋
- 這裡只有文件。程式碼、環境設定、資料庫連線都留在私有 repo，不會出現在這裡

## 網址

| | 網址 | 內容 |
|---|---|---|
| 現行版 | <https://94sh09sh19sh.github.io/hd-docs/latest/> | 永遠是最新的，連結不會過期 |
| 凍結版 | `https://94sh09sh19sh.github.io/hd-docs/<週次>/` | 該週定版的樣子，之後不再變 |

右上角的版本下拉選單可以在各週定版之間切換。

每頁右下角有「問 AI」按鈕：輸入問題後另開 Claude 或 ChatGPT，由對方讀取本站的
`llms.txt`（全站目錄）與各頁的 Markdown 版來回答。站台本身沒有後端，也不收集任何內容。

## 建置

推到 `main` 會更新現行版；推一個四位數的週次 tag（例如 `0916`）會建立該週凍結版。
兩者都由 `.github/workflows/docs.yml` 自動完成，站台是 GitHub Pages。

搜尋引擎收錄以每頁的 `<meta name="robots" content="noindex">` 擋掉（`robots.txt` 放在專案路徑底下，爬蟲不讀，
只是順手留著）；網址本身是公開的，知道網址就看得到。
