Streamlit Demo-site：https://cybersecurity-hw06-webcrawler-cwa.streamlit.app

[補充]
1. 與 AI Agent (Antigravity) 對話記錄請參閱 prompt 資料夾裡的 2 份 .txt files.

# CWA 氣象應用專案 (CRISP-DM)

本專案採用 CRISP-DM (跨行業資料探勘標準流程) 方法論，實作一個天氣預報儀表板系統。

## 1. 商業理解 (Business Understanding)
**目標**: 建立一個自動化系統，用於抓取、儲存並視覺化台灣主要地區的 36 小時農業天氣預報。
**背景**: 使用者需要一個集中式的儀表板來查看一週的天氣趨勢，以支援農業決策。

## 2. 資料理解 (Data Understanding)
**資料來源**: 中央氣象署 (CWA) 開放資料 API。
**資料集 ID**: `F-A0010-001` (農業氣象預報-未來1週天氣預報)。
**資料格式**: JSON。
**關鍵屬性**:
- `locationName`: 地區名稱 (例如：北部地區、中部地區、南部地區)。
- `weatherElements`: 包含每日預報 (`Wx`, `MaxT`, `MinT`)。

## 3. 資料準備 (Data Preparation)
**流程**: 資料萃取與轉換 (ETL)。
**腳本**: `fetch_data.py`
- 從 CWA API 抓取 JSON 資料。
- 解析巢狀 JSON 結構。
- **自動化**: `app.py` 包含自動更新機制，啟動時會檢查資料庫的新鮮度。

## 4. 建模 (系統架構) (Modeling)
**資料庫**: SQLite (`data.db`)
**Schema 設計** (`database.py`):
- **資料表**: `weather`
    - `id`: 主鍵 (整數, 自動遞增)
    - `location`: 地區名稱 (文字)
    - `min_temp`: 最低氣溫 (實數)
    - `max_temp`: 最高氣溫 (實數)
    - `description`: 天氣描述 (文字)
    - `forecast_date`: 日期 (文字)

## 5. 評估與部署 (Evaluation & Deployment)
**應用程式**: Streamlit Web App (`app.py`)。

### 關鍵功能 (V2 版面配置)
1.  **儀表板網格佈局**:
    *   **上方列 (空間視圖)**:
        *   **互動式地圖 (左)**: 使用 PyDeck 視覺化台灣氣溫分佈。城市依據溫度顯示顏色 (藍 -> 紅)。
        *   **單日詳細資訊 (右)**: 顯示所選地區與日期的詳細天氣指標。
    *   **下方列 (時間視圖)**:
        *   **趨勢圖 (左)**: 7日溫度趨勢折線圖 (Altair)。
        *   **數據表 (右)**: 詳細的 7日預報數據表格。
2.  **智慧自動更新**:
    *   應用程式會自動檢查數據是否遺失或過舊 (> 4小時)。
    *   如有需要，會在背景從 CWA API 抓取新資料，確保數據隨時保持最新。
3.  **視覺化**:
    *   地區對應城市映射 (Region-to-City Mapping)，提升地圖視覺效果。
    *   自訂主題配色以提升易讀性。

### 如何執行

1.  **安裝依賴套件**:
    ```bash
    pip install -r requirements.txt
    ```
    *依賴項目包含: `streamlit`, `pandas`, `altair`, `pydeck`, `requests`, `python-dotenv`.*

2.  **設定 API Key**:
    *   **本地開發**: 建立 `.env` 檔案 或 `.streamlit/secrets.toml`。
    *   **Streamlit Cloud**: 將 `CWA_API_KEY` 新增至 App Settings -> Secrets。
    ```toml
    # .streamlit/secrets.toml
    CWA_API_KEY = "your_api_key_here"
    ```

3.  **啟動應用程式**:
    ```bash
    streamlit run app.py
    ```
    *(應用程式將自動初始化資料庫，並在需要時抓取數據)*

## 參考來源
https://opendata.cwa.gov.tw/dataset/forecast/F-A0010-001