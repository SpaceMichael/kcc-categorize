# categorize_logs.py

中文說明
---------
簡介
這是一個簡單的日誌分類腳本。它會將多行堆疊依事件（基於時間戳或日誌級別）重組，篩選包含 `ERROR`/`Exception`/`Traceback` 的事件，並排除同時包含 `404 NOT_FOUND` 與 `InfusionPatientDrug` 的條目。最後按關鍵字正則表達式分派到多個分類檔，並輸出合併檔與摘要檔，便於後續分析。

需求
- Python 3.6+
- 日誌為純文字檔（建議 UTF-8），腳本使用 `errors='replace'` 以容錯非 UTF-8 編碼。

用法
```powershell
python categorize_logs.py <log1> <log2> ... -o <輸出目錄>
```
示例
```powershell
python D:\Users\ttk799\workspace\kcc-categorize\categorize_logs.py "D:\Users\ttk799\Downloads\qeh-chemo-booking-svc-....log" -o "D:\Users\ttk799\Downloads\categorized-by-python-run"
```

輸出說明
- <category>.txt：每個分類的檔案（例如 `infusion-patient-drug.txt`、`resource-not-found.txt` 等）
- combined-<timestamp>.txt：合併所有被分類的事件片段
- summary-<timestamp>.txt：分類計數與生成檔案列表

自訂
在 `categorize_logs.py` 頂部的 `categories` 列表中定義分類及其對應的正則。可在此新增或修改模式。排除規則由 `exclude_404` 與 `exclude_ipd` 控制（同時匹配則跳過該事件）。

注意
請小心處理含敏感訊息的日誌，避免上傳到公用服務。

---

English
-------
Description
A simple log classification script. It reassembles multi-line stack traces into events (by timestamp or log level), filters events containing `ERROR`/`Exception`/`Traceback`, excludes entries that contain both `404 NOT_FOUND` and `InfusionPatientDrug`, and classifies events using keyword regex patterns. Outputs per-category files, a combined file, and a summary file for analysis.

Requirements
- Python 3.6+
- Logs are text files (UTF-8 recommended). The script uses `errors='replace'` to tolerate encoding issues.

Usage
```powershell
python categorize_logs.py <log1> <log2> ... -o <output_dir>
```
Example
```powershell
python D:\Users\ttk799\workspace\kcc-categorize\categorize_logs.py "D:\Users\ttk799\Downloads\qeh-chemo-booking-svc-....log" -o "D:\Users\ttk799\Downloads\categorized-by-python-run"
```

Outputs
- <category>.txt — files for each category (e.g., `infusion-patient-drug.txt`)
- combined-<timestamp>.txt — all matched blocks combined
- summary-<timestamp>.txt — counts and file list

Customization
Edit the `categories` list at the top of `categorize_logs.py` to change or add classification patterns. The exclusion is controlled by `exclude_404` and `exclude_ipd`.

License / Notes
Provided as-is. Handle sensitive logs with care.
