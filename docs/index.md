# 血液透析中心平板照護輔助系統 — 進度首頁

> 每週的工作紀錄以子頁面形式掛在下方，最新的排在最上面。

---

## Link

#### [臨床端進度報告](reports/progress-clinical.md) — 給醫師、護理部、法規窗口
#### [技術端進度報告](reports/progress-technical.md) — 給接手或協作的工程師
#### [完整手動測試手冊](testing/manual-test-guide.md) — 從 clone 到每個細節功能，149 項逐條驗證
#### [架構圖](requirements/architecture-diagrams.md)
#### [資料字典](reference/data-dictionary.md) — 資料庫蒐集了哪些資料，10 張表 123 個欄位逐欄說明
#### [這套系統是用什麼蓋的](reference/tech-stack-explained.md) — 用蓋房子的比喻講技術架構，給非技術背景的人看

### 需求文件

四份文件**優先權不同，衝突時有明確的裁決順序**：

| 文件 | 角色 |
|---|---|
| [軟體需求規格書（SRS）](requirements/srs.md) | 功能需求來源（FR 編號出處） |
| [實作規格書](requirements/implementation-spec.md) | 範圍與技術選型，**衝突時以此為準** |
| [資料庫使用規範](requirements/database-policy.md) | 資料治理強制規則，優先權等同實作規格書 |
| [FDE 數位化評估報告](requirements/fde-assessment.md) | 背景脈絡與選型理由 |

---

## 每週紀錄

### [0909 — Iteration 1＋2 完成、核心流程可完整執行](weekly/2026-09-09.md)

進度：

- 核心流程「指派平板 → 病人回報 → 護理站即時處理」已可從頭到尾完整執行，全程留下稽核紀錄
- 涉及臨床判斷的三項功能刻意排除，等待 SaMD 認證邊界確認
- 目前仍在開發者本機測試環境，尚未進入臨床試用
- 待臨床端回覆六項協助事項，才排得出下一階段

<!-- 新的一週請把整段複製到這一行上方，維持由新到舊排列 -->

---

## 目錄結構

```
docs/
├── index.md                    本頁
├── requirements/               需求文件（原 demand_v1/）
│   ├── srs.md
│   ├── implementation-spec.md
│   ├── database-policy.md
│   ├── fde-assessment.md
│   ├── architecture-diagrams.md
│   └── images/                 架構圖原始檔
├── reports/                    階段性進度報告
│   ├── progress-clinical.md
│   └── progress-technical.md
├── reference/                  參考文件（隨程式碼變動）
│   ├── data-dictionary.md      資料字典，逐欄說明資料庫蒐集的資料
│   └── tech-stack-explained.md 技術架構白話版，給非技術背景的人看
├── testing/                    測試文件
│   └── manual-test-guide.md    完整手動測試手冊（可勾選）
└── weekly/                     每週紀錄（子頁面）
    ├── _template.md            新一週的空白範本
    ├── HOWTO.md                維護流程（人用）
    ├── AGENT.md                維護作業指示（agent 用）
    └── YYYY-MM-DD.md
```

需求文件是**已定稿的輸入**，原則上不再改動；每週的變化寫在 `weekly/`，階段性總結寫在 `reports/`。
測試手冊隨功能增減而更新，每完成一個 iteration 就補上該階段的驗證項目。
`reference/` 是從程式碼實況整理出來的參考資料，schema 一改就要跟著更新，不是定稿文件。

---

## 附錄

#### [每週紀錄維護流程（人用）](weekly/HOWTO.md)
#### [文件維護作業指示（agent 用）](weekly/AGENT.md)

每週要做的事：複製 `weekly/_template.md` 成該週開會日（星期三）日期的檔案並填寫 → 在上面「每週紀錄」
最上方插入一段連結與三到五條重點 → `npm run docs:hackmd` → 把新週報與本頁同步到 HackMD。
細節、slug 命名規則與踩過的雷都寫在上面兩份文件裡。
