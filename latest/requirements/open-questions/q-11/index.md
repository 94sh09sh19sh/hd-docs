# 尚待確認事項清冊 Q-11 Android Enterprise 管理權限

上層文件：《[尚待確認事項清冊](https://94sh09sh19sh.github.io/hd-docs/latest/requirements/open-questions/index.md)》第 4 章

|            |                                                       |
| ---------- | ----------------------------------------------------- |
| **問誰**   | 資訊室                                                |
| **急迫度** | C                                                     |
| **卡住**   | MDM 從模擬版換成真的控制 15 台平板                    |
| **狀態**   | 已提出（0909）。**0919 範圍大幅縮小**，原本六題剩三題 |

**背景**

**0919 起不走 MDM 了。** Android Enterprise 有三處必須連往院外（首次佈建連 Google、後端設定政策要呼叫 `googleapis.com`、遠端鎖定命令靠 FCM 送達），與「所有資料不出醫院網路」直接衝突。改走**自包 WebView 外殼＋Android 內建螢幕固定**，完整理由見《[平板管控：免 MDM 的全院內方案](https://94sh09sh19sh.github.io/hd-docs/latest/notes/mdm-offline-plan/index.md)》。

因此原本要問的「有沒有既有 MDM 方案、採購時程、Management API 的權限與申請流程」**整組不需要了**。

**具體要問的（縮小後）**

1. 15 台平板的型號與 Android 版本為何？（螢幕固定需 Android 5.0 以上）
1. 院方是否允許側載 APK，也就是開啟「允許安裝不明來源應用程式」？
1. 自簽 CA 是否符合院方資安規範？若院方堅持由內部 CA 簽發，改由院方簽發亦可，打包方式不變。

**1025 第 1 題暫答**：15 台還沒到，先用一台 Galaxy Tab S6 Lite（SM-P613），Android 13，螢幕固定與外殼都沒有障礙；**使用者更新之前正式使用只有這一台**。第 2 題（側載）同日接筆電以 adb 實測：沒有裝置擁有者或管理設定檔、擁有者帳號沒有任何使用者限制，**技術上可以側載**（《[暫用平板](https://94sh09sh19sh.github.io/hd-docs/latest/notes/interim-tablet/index.md)》第 1.2、3 節）；院方資安准不准仍要問資訊室。15 台的型號仍待回覆。

另外一題不影響路線，但仍要追蹤：閒置輪播會讓螢幕長時間亮著，**對電池與螢幕壽命的影響**，15 台的汰換成本院方可否接受。

**現況／暫代做法**

`MdmProviderPort` 介面層保留，`MockMdmProvider` 也保留，但**語意改變**：它不再是「等著被真 MDM 換掉的模擬品」，而是**裝置佈建狀態紀錄與稽核的正式實作**（FR-S01）。院方日後若已有既有 MDM 方案，再以新增一個實作的方式接上。

______________________________________________________________________

[← 回尚待確認事項清冊](https://94sh09sh19sh.github.io/hd-docs/latest/requirements/open-questions/index.md)　[← 回進度首頁](https://94sh09sh19sh.github.io/hd-docs/latest/index.md)
