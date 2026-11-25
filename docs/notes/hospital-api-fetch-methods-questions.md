# 院方 API 介接之二：1108 給學長的問題清單

給學長直接作答用。每題為什麼要問、估算與細節在補充版《[之二之二](hospital-api-fetch-methods-questions-detail.md)》，題號相同；已答的在《[之二之一](hospital-api-fetch-methods-questions-answered.md)》。

上層文件：《[院方 API 介接](hospital-api-fetch-methods.md)》　前一份：《[之一](hospital-api-fetch-methods-status.md)》　下一份：《[之三](hospital-api-fetch-methods-monday-plan.md)》

**回法**：題號＋選項就好，例如「K-2 ①、K-7 要」。標「建議」的是這邊的預設，沒意見就照建議。

---

## 1. 還沒答：沒有了

1114 學長答了其餘 15 題（K-1、K-2、K-3、K-4、K-7、W-6、F-6、B-2、D-2～D-5、E-4、F-2、C-16、H-2），整列搬到《[之二之一](hospital-api-fetch-methods-questions-answered.md)》第 3.6 節。**剩下的 D-1、E-5 在 1118 開會由醫師答了**，不必再問學長，搬到同一份第 3.7 節。

## 2. 說明（不必回）

1116 原訂現場當面講，當天沒講到，改成這裡＋訊息告知。

- 抓取腳本已搬到 C 槽：`C:\API_Fetch\hd-hospital-fetch`，每 3 分鐘、只在 07:00～23:00 抓；D 槽舊資料夾 1116 已刪。停、改頻率、看最近一輪的指令在部署手冊《[院方 API 抓取腳本的維運](../deployment/ref-fetch-script.md)》（FS-06、FS-08、FS-03）
- APP 組讀檔的路徑改成 `C:\API_Fetch\IDH_interface`；`Hb_API_Fetch` 也一起在 C 槽，內容沒動。給 APP 組的讀檔說明在《[之五](hospital-api-fetch-methods-app-team.md)》
- W-6 學長給的去重交接文件，有一處腳本沒照做：同一筆紀錄（同一人、同一場、同一個紀錄時間）內容變了，腳本會再寫一次、讀的人以後面的為準。原因是結束體重、結束血壓、實際脫水量下機後才回填到同一場已經寫過的每一列，照「見過就跳過」的話留底永遠沒有結束體重。APP 組讀檔時同一個鍵以後面的為準

## 3. 檢驗資料（`hb`）：不必答

1111 學長答 A-5：`hb_online_v2.py` 不由這邊處理。原本列在這裡的 I 組 11 題（I-2、I-3、I-5～I-13）跟著不問，題目與答覆留在《[之二之一](hospital-api-fetch-methods-questions-answered.md)》。

## 4. 不必回

C-1～C-4、C-6～C-8、C-12、C-13、C-15 已照建議做進 `hd-hospital-fetch` v0.1.0（逾時重試、只印筆數不印個資、端點寫在設定檔等），有異議才回題號；明細在補充版第 6 節。

---

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|
| [1125](https://94sh09sh19sh.github.io/hd-docs/1125/notes/hospital-api-fetch-methods-questions/) | 2026-11-25 | 剩下的 D-1、E-5 在 1118 開會由醫師答了，沒有還沒答的題目 |
| [1118](https://94sh09sh19sh.github.io/hd-docs/1118/notes/hospital-api-fetch-methods-questions/) | 2026-11-18 | 系列 1116 改名為「院方 API 介接」；改成只列還沒答的 2 題（D-1、1116 新增的 E-5），1114 答的 15 題移到之二之一；加不必回的說明一節 |
| [1111](https://94sh09sh19sh.github.io/hd-docs/1111/notes/hospital-api-fetch-methods-questions/) | 2026-11-11 | 首次定版。給學長的問題清單：從本系統每一個用到院方資料的地方反推、分組；1109 起只列沒答的題，1111 改成只有題目與選項的簡易版（已發給學長）、I 組刪 |

[← 看補充版](hospital-api-fetch-methods-questions-detail.md)　[← 回上層文件](hospital-api-fetch-methods.md)
