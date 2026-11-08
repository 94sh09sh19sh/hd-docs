# 第十九冊之一 · 抓取腳本的出錯對照與速查

版本：v0.1　文件狀態：草案（1108 由第十九冊分出）　編號：沿用第十九冊的 `B-xx`

上層手冊：《[第十九冊 · 院方 API 抓取腳本的安裝](19-hospital-fetch.md)》

> 照第十九冊做的時候，畫面上出現看不懂的訊息就查第 1 節；現場要一眼看完所有指令看第 2 節。本冊的訊息原文來自 `hd-hospital-fetch` v0.1.0，腳本改版時回頭核對。

## 1. 出錯對照

| 畫面上看到 | 意思 | 怎麼做 |
|---|---|---|
| `設定錯誤 找不到設定檔` | 不在 `<腳本資料夾>` 裡，或 第十九冊 B-14 沒做 | `cd C:\hd-hospital-fetch` 再試 |
| `設定錯誤 設定檔不是合法的 JSON` | `config.json` 寫壞了，最常見是反斜線只寫一個、少了引號或逗號 | 回第十九冊 B-14 對照範例改 |
| `設定錯誤 endpoint 要是 http 或 https 開頭` | 位址抄錯 | 對照 `values.md` |
| `失敗 重試 3 次仍失敗；最後一次：連線失敗：…` | 連不到院方 API | 確認位址；用瀏覽器開 `<院方位址>?date=2026-11-09` 看得到資料嗎；看不到就停 |
| `失敗 重試 3 次仍失敗；最後一次：HTTP 404` 或其他數字 | 院方回錯誤 | 位址的路徑抄錯（`.php` 前面那段）；對了還是錯就停 |
| `失敗 重試 3 次仍失敗；最後一次：逾時（>30 秒）` | 院方太慢 | 再試一次；連續逾時就停 |
| `失敗 回應裡找不到 JSON 內容`、`回應的 JSON 無法解析`、`回應裡沒有 data_list 陣列` | 院方回的不是透析清單（維護頁、登入頁） | 停 |
| `失敗 當月的留底檔不是 UTF-8，先用 transcode_history.py 轉檔` | 當月檔還是舊寫法 | 回第十九冊 B-12；當月檔轉不了就停 |
| `跳過 上一輪還沒結束` | 另一輪正在跑 | 正常；等一下再看 |
| `py` 說找不到指令 | 沒有 Python launcher | 換成 `python`，或用 `.exe` |
| Windows 跳出「Windows 已保護您的電腦」 | `.exe` 第一次執行 | 第十九冊 B-11 有做 `Unblock-File` 就不會出現；出現了按「其他資訊」→「仍要執行」，雜湊對過才可以 |

## 2. 一頁速查

```powershell
cd C:\hd-hospital-fetch
py transcode_history.py "<指定資料夾>"              # 轉碼預演
py transcode_history.py "<指定資料夾>" --apply      # 轉碼
py fetch_dialysis.py --dry-run                     # 抓取預演，不寫檔
py fetch_dialysis.py --once                        # 跑一輪
$LASTEXITCODE                                      # 0 成功、1 失敗、2 設定錯
Get-Content -Encoding UTF8 .\fetch-status.json     # 狀態
powershell -ExecutionPolicy Bypass -File .\install-task.ps1      # 裝排程
Get-ScheduledTaskInfo -TaskName hd-hospital-fetch                # 排程跑了沒
powershell -ExecutionPolicy Bypass -File .\uninstall-task.ps1    # 停排程
```

---

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|

[← 回第十九冊](19-hospital-fetch.md)　[← 回部署手冊總覽](index.md)
