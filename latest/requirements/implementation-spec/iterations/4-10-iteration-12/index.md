# 實作規格書 4.10 迭代 12：外殼 App 獨立 repo 與整合（0926 新增，本週）

上層文件：《[實作規格書](https://94sh09sh19sh.github.io/hd-docs/latest/requirements/implementation-spec/index.md)》第 4 章

> **2026-09-27 完成實作與開發機上的建置實測。** 外殼搬到私人 repo `hd-kiosk-shell`（`git subtree split`，保留歷史），本 repo 刪除 `apps/kiosk-shell/` 與 `make-hospital-ca.mjs`；契約定為第 1 版（《[病人端外殼 App 契約](https://94sh09sh19sh.github.io/hd-docs/latest/reference/kiosk-shell-contract/index.md)》＋`packages/shared/src/kiosk-shell.ts`），外殼 `v0.2.0` 實作它，本系統以 `services/shell-builder/shell.pin` 釘住。步驟見部署手冊《[平板與外殼 App](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-tablet/index.md)》，手動測試見[迭代 12 分冊](https://94sh09sh19sh.github.io/hd-docs/latest/testing/iteration-12/index.md)（`v1`–`v48`），開發機實測結果見《[部署演練紀錄](https://94sh09sh19sh.github.io/hd-docs/latest/notes/deployment-drills/index.md)》第 9 節。
>
> | 驗收                                                      | 狀態                                                                             |
> | --------------------------------------------------------- | -------------------------------------------------------------------------------- |
> | 1. 本 repo 沒有 `apps/kiosk-shell/`；外殼 README 指向契約 | ✓ `verify:iteration12 --shell-src`                                               |
> | 2. `shell-builder` 從零建出 APK，第二次不重新產生金鑰     | ✓ 開發機實測（演練紀錄第 9 節）、`verify:iteration12 --live`                     |
> | 3. 開發手機從下載頁安裝並載入病人端                       | 下載頁、HTTPS、`/api/` 轉送已在開發機驗過；**手機本身待測**（分冊 §12.5）        |
> | 4. 釘住後退不出去、跳出 30 秒內看得到                     | 後端與網頁那一半已驗（`verify:iteration12:api`）；**手機本身待測**（分冊 §12.6） |
> | 5. 最低可用版本調高一版，護理端立刻標出                   | ✓ `verify:iteration12:api`；改 `.env` 重新啟動 api 那一次在分冊 §12.7            |
> | 6. 契約版本不合時兩邊都有明確提示                         | 系統這一邊 ✓；平板上的提示列**待手機測**（分冊 §12.7）                           |
>
> **與原定計畫不同、或規格沒寫到而補上的五處**：
>
> 1. **病人端改走 HTTPS，並與後端同一個來源。** 規格要外殼「憑證信任」，外殼因此只信任院內 CA、只准 HTTPS；但 HTTPS 頁面不准呼叫 HTTP 的後端，而規格沒寫伺服器憑證用在哪裡。做法是病人端的靜態服務以伺服器憑證提供 HTTPS，並把 `/api/` 轉送給 api——外殼只需要信任一張憑證，病人端不必再設 CORS。護理端不動。
> 1. **同一個埠同時接 HTTPS 與 HTTP，HTTP 只留下載頁。** 平板第一次下載 APK 時還不信任院內 CA；不另開埠是因為每個埠都要向資訊室登記（DEP-37）。
> 1. **外殼原始碼從主機上的 clone 帶進 `shell-builder` 的映像檔建置**（compose 的 `additional_contexts`），不是在容器裡 clone。部署金鑰因此不進映像檔；映像檔自己 checkout 釘住的 tag。執行時 `network_mode: none`，以預先下載的相依離線建置—— DEP-14「建置時碰不到資料」延伸成「掛著私鑰的時候沒有網路」。
> 1. **外殼回報「是否釘選」，網頁把它併進前景判定。** 解開螢幕固定之後 App 常常還停在前景，只看畫面可不可見會誤報成「固定中」，驗收第 4 條就驗不過。外殼也在每次啟動時請求螢幕固定，重新開機後按一下確認框即可。
> 1. **金鑰的備份、核對與還原做成 `shell-builder` 的指令**（`keys-backup`、`keys-verify`、`keys-restore`），落實 DEP-35 的「每年驗證一次」。
>
> **迭代 10 的外殼其實建不起來**：少了根目錄的 Gradle 設定與啟動圖示，`res/raw/` 裡的 `README.md` 也不是合法的資源名稱。迭代 10 沒有編譯環境、從來沒有實際建置過，這三處是這次要讓 `shell-builder` 建置時逐一核對才發現的，已在外殼 `v0.2.0` 修正。

**目標**：把 WebView 外殼開成另一個私人 repo，與本系統以契約整合，APK 在院內主機上建置、從院內下載頁安裝。

| 工作項                                                                                                                                              | 對應           | 備註                                                  |
| --------------------------------------------------------------------------------------------------------------------------------------------------- | -------------- | ----------------------------------------------------- |
| 建立新的私人 repo，搬入 `apps/kiosk-shell/`（保留歷史），本 repo 刪除該目錄                                                                         | DEP-45         | **不留兩份**                                          |
| 契約：`packages/shared` 型別＋契約文件＋契約版本號                                                                                                  | FR-S14、3.3    | 真本在本 repo                                         |
| 後端：提供契約版本與最低可用外殼版本；前景回報多收外殼版本與契約版本                                                                                | FR-S14         |                                                       |
| 護理端：裝置管理標出外殼版本過舊的平板                                                                                                              | FR-S14         | 簡易版以顏色與圖示呈現（迭代 14）                     |
| `shell-builder`：Android 建置映像檔；首次執行產生 CA、伺服器憑證、簽章金鑰並存入金鑰資料卷；clone 釘住的外殼 tag、嵌入 CA、建置、簽章、輸出到下載頁 | DEP-35、DEP-45 | 取代 `make-hospital-ca.mjs`                           |
| 病人端下載頁                                                                                                                                        | DEP-45         | 只提供 APK 與版本資訊，不需要登入，但只在院內網路可達 |
| 開發用簽章金鑰與院內簽章金鑰分開                                                                                                                    | DEP-45         | 兩者簽出的 APK 不能互相覆蓋安裝                       |
| 完成外殼功能：全螢幕、憑證信任、長按與分頁限制、常亮、開機自動啟動、版本回報                                                                        | 平板管控方案   | 迭代 10 未能實機驗的部分                              |

**Schema 變更**：裝置前景回報加外殼版本與契約版本欄位（只做加法）。

**驗收標準**：

1. 本 repo 找不到 `apps/kiosk-shell/`；外殼 repo 的 README 指向本 repo 的契約文件
1. 開發機上 `shell-builder` 從零建出 APK，金鑰資料卷裡出現 CA 與簽章金鑰；**第二次執行不重新產生金鑰**
1. 開發手機從院內下載頁（開發機）安裝 APK，輸入序號與金鑰後載入病人端
1. 開發手機釘住後退不出去，解除需 PIN；跳出固定時護理端 30 秒內看得到
1. 把最低可用外殼版本調高一版，護理端立刻標出那支手機
1. 契約版本不合時，兩邊都有明確的提示，不是靜默失敗

**外部依賴**：Q-11（平板型號、側載政策）。不擋實作，開發手機即可驗完。

______________________________________________________________________

[← 回實作規格書](https://94sh09sh19sh.github.io/hd-docs/latest/requirements/implementation-spec/index.md)　[← 回進度首頁](https://94sh09sh19sh.github.io/hd-docs/latest/index.md)
