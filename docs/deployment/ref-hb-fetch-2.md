# 檢驗資料（hb）抓取（未採用）（第 2 份，第 5～7 節）

上層文件：《[檢驗資料（hb）抓取（未採用）](ref-hb-fetch.md)》

> **狀態：未採用，保留為參考**——從沒在院內照做過。改寫自舊第十九冊之三。編號：`BH-xx`。這一份是退回、延後條件與狀態檔的 `reason` 對照；`$hb`、`$sf` 的設法見《第 1 份》第 1 節第 4 點。

## 5. 退回

學長說「hb 不要了」時，在 `<腳本資料夾>\hb` 裡依序做；透析清單不受影響：

```powershell
powershell -ExecutionPolicy Bypass -File .\uninstall-hb-task.ps1
Remove-Item -Force -LiteralPath (Join-Path $hb 'hb-status.json') -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force -LiteralPath (Join-Path $hb 'hb-logs') -ErrorAction SilentlyContinue
cd -LiteralPath $sf
Remove-Item -Recurse -Force .\hb
```

- **會看到**：`已移除工作 hd-hospital-fetch-hb（程式、設定、病人清單、留底、狀態檔、紀錄檔都沒動）`；其餘不印東西
- BH-05 產生了病人清單的話，問學長要不要留；不留就 `Remove-Item -LiteralPath (Join-Path $hb 'hospital_dataset\active_patients.txt')`
- BH-08 起寫進留底的筆數看各輪狀態檔的 `新`；那幾行每一行都有 `FetchedAt`（抓取時間），要不要刪由學長決定，這一份不動
- 學長的 `config.json`：BH-05 新填的才問學長要不要留；原本就有的不動

## 6. 什麼情況這一份延後（透析清單照做）

照《[院方 API 介接之四](../notes/hospital-api-fetch-methods-next-visit-plan.md)》第 6 節：

- 沒有位址可填（I-8 沒答，BH-03 也找不到實際設定）
- 主機上已有程式在寫 `<Hb_API_Fetch>`（BH-03）
- 既有留底有壞行（BH-06）
- 位址是 `http`，學長沒說可以（BH-05）
- 透析清單做完已超過約 40 分鐘，或學長要先走

延後時：BH-04 做了就照第 5 節移除 `hb` 資料夾，或留著（沒有排程就不會跑），跟學長說一聲；BH-03 的結論照記。

## 7. 狀態檔的 `reason` 與 `error_kinds`

訊息原文來自 `hd-hospital-fetch` 的 `hb\`（v0.2.0，v0.3.0 相同）；改了訊息要回頭核對這一節。

| 看到 | 意思 | 怎麼做 |
|---|---|---|
| `設定檔的 url_template 還是範本的佔位字，或少了 {MedicalId}、{start_date}、{end_date}` | 位址還沒填 | BH-05 |
| `找不到病人清單（設定檔的 patients_file）` | 病人清單不在設定指的位置 | BH-05 |
| `病人清單有不是純數字的病歷號` | 學長的程式不接受；不自動補零或去零 | 停，問學長 |
| `留底有壞行：YYYY-MM.txt 第 N 行損壞…（用 check_hb_store.py 看全部的壞行）` | 學長的程式讀不過既有留底 | BH-06 |
| `上一輪還沒結束` | 正常（排程與手動同時跑）；一直出現就看 `hb-run.lock` 的時間 | 鎖檔超過 3 小時（`--lock-stale-minutes` 預設 180）會自動接手 |
| `HTTP 需要院方核准後，才可在設定檔明確允許` | 位址是 `http`，設定沒開 | BH-05 |
| `逾時`、`URLError（…）` | 連不到或太慢 | 透析清單也連不到就是網路；只有這支連不到，問學長位址 |
| `HTTPError 404`、`HTTPError 500` 等 | 院方 API 回錯誤 | 抄下數字，問學長 |
| `回應不是 JSON` | 回了網頁或錯誤訊息 | 同上 |
| `有未知欄位，需確認 Schema 更新（不自動丟棄）` | 院方多了欄位，學長的程式拒收 | 停，問學長（I-9） |
| `回傳 MedicalId 與查詢不一致`、`回傳日期不在查詢區間內`、`未知的 API 回應格式（無法判定是否沒資料）` | 院方回的跟問的對不上 | 抄下次數，問學長 |
| `每一位都查詢失敗（種類見 error_kinds）` | 全部的人都查不到 | 停；抄 `error_kinds`，問學長（BH-07） |
| `學長的程式中途停了（…）` | 查到一半整支停（例如重建 CSV 時讀不過留底） | 看 `hb-logs\` 最新的檔，停 |
| 主控台 `… failed 找不到設定檔所在的資料夾` | `--config` 指到不存在的資料夾，連狀態檔都不寫 | 確認 `$hb` |
| 主控台 `狀態檔寫不了：…` | 狀態檔所在的資料夾寫不進去 | 看權限與磁碟空間；問學長 |

上一份：《[檢驗資料（hb）抓取（未採用）](ref-hb-fetch.md)》（第 0～3 節）；第 4 節在《[…之一：現況盤點](ref-hb-fetch-survey.md)》

---

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|
| 1118 | 2026-11-18 | 首次定版。1118 照每份約 300 行的上限由《檢驗資料（hb）抓取（未採用）》拆出，內容與步驟編號不動 |

[← 回部署手冊目錄](index.md)
