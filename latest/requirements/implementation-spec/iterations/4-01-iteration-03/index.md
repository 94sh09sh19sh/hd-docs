# 實作規格書 4.1 迭代 3：封閉網路化與資料層遷移

上層文件：《[實作規格書](https://94sh09sh19sh.github.io/hd-docs/latest/requirements/implementation-spec/index.md)》第 4 章

**目標**：讓系統符合「所有資料不出醫院網路」與「資料庫是 SQLite」兩個新前提，並把後續每個迭代都要用到的三個介面層與開關機制先立起來。此迭代**不新增任何使用者可見的臨床功能**，但沒有它，後面五個迭代都會踩在錯的地基上。

| 工作項             | 內容                                                                                                             | 對應                       |
| ------------------ | ---------------------------------------------------------------------------------------------------------------- | -------------------------- |
| SQLite 遷移        | Prisma provider 改 `sqlite`、migration 目錄重建、四項 `PRAGMA` 套用、資料庫檔案移到專案目錄外並確認 `.gitignore` | 《資料庫使用規範》第 7 條  |
| 唯讀連線           | 統計與報表用的唯讀連線通道                                                                                       | 《資料庫使用規範》7.1      |
| Supabase 撤出      | 移除套件相依與環境變數、seed 腳本改在 SQLite 重建、停用並刪除 Supabase 專案                                      | 《資料庫使用規範》第 15 條 |
| 零院外連線盤點     | 可重複執行的檢查腳本，掃出任何指向院外網域的相依（含字型、CDN）                                                  | FR-S07                     |
| 常駐總覽螢幕       | 護理端新路由：不休眠、大字級、音效提示、斷線示警與自動重連                                                       | FR-N12（P0）               |
| 模型供應者介面層   | `LlmProviderPort` 三個實作，`MockLlmProvider` 為預設；合成資料檢查                                               | FR-S06                     |
| 臨床資料來源介面層 | `ClinicalDataSourcePort` 介面＋`ManualEntryAdapter`＋內部資料表                                                  | FR-S05                     |
| 功能開關中心       | 3.7 節全部開關，預設全關，切換寫稽核                                                                             | FR-S08                     |
| 備份與還原         | 線上備份（`VACUUM INTO`）、備份歷程檢視、備份寫稽核                                                              | FR-S09                     |
| 稽核軌跡擴充       | 開關切換、備份、匯入、AI 呼叫四類新事件                                                                          | FR-S02                     |

**Schema 變更**：migration 整組重建；新增 `feature_flags`、`ai_invocations`、`backup_runs`、`clinical_values`、`clinical_value_imports`。既有十張表的結構**不改**（僅型別對照因 provider 改變而變動）。

**驗收標準**：

1. 全新環境 clone 之後，只設定 `DATABASE_URL` 指向本機檔案，跑完 migration 與 seed 就能啟動，**全程不需要任何網路連線**
1. 既有 `verify:acceptance` 與 `verify:iteration2` 兩支腳本全綠——遷移不得改變任何既有行為
1. 零院外連線檢查腳本回報 0 筆
1. 三台裝置同時操作（一台送問卷、一台按求助、一台開總覽）不出現 `SQLITE_BUSY` 造成的操作失敗
1. 常駐總覽螢幕連續執行 4 小時不休眠、不斷線；手動拔網路後畫面明顯示警，恢復後自動重連
1. 所有功能開關預設為關，開啟任一項都能在稽核軌跡查到紀錄
1. 備份可實際產生檔案，並能還原到另一個路徑後正常啟動

**外部依賴**：無。**這個迭代可以立刻開始，不必等任何人回覆。**

______________________________________________________________________

[← 回實作規格書](https://94sh09sh19sh.github.io/hd-docs/latest/requirements/implementation-spec/index.md)　[← 回進度首頁](https://94sh09sh19sh.github.io/hd-docs/latest/index.md)
