---

##  Usage Guide

###  Page 1: Ledger (Add Record)
- Used by on-duty officers to record new patrol or traffic stop details.  
- The form collects driver, vehicle, and violation information.  
- After submission, a **natural-language summary** of the record is automatically generated — mimicking a police report narrative.  
- Each entry is stored securely in the **MySQL database** for traceability and further analytics.

### Page 2: Analytics & Check
- Designed for supervisory officers and analysts to review field data.  
- Includes **dynamic KPIs** (Total Stops, Arrests, Average Age, Search Rate).  
- Displays **donut and bar/pie charts** with country, gender, and violation filters.  
- A **Narrative Summary** automatically updates to describe the selected dataset.  
- Quick-check mini form allows focused record lookups by country, gender, and violation.

---

##  SQL Evidence Summary

All SQL queries used for database validation and analytics are available in **`SQL_Queries.sql`**.  
The file includes:
- **6 Database Proof Queries** (structure, record count, sample data).  
- **15 Analytical Queries** (aggregations, correlations, trend analysis).

These queries were executed in **MySQL Workbench** to verify both table design and analytical integrity.

---

##  Project Deliverables

| File Name | Purpose |
|------------|----------|
| `clean_app.py` | Main Streamlit dashboard (Ledger + Analytics) |
| `cleaned_traffic_stops.csv` | Cleaned dataset used for backup visualization |
| `SQL_Queries.sql` | Database proof + analytical SQL queries |
| `README.md` | Project documentation and user guide |
| `requirements.txt` | Required Python libraries for easy environment setup |

Additionally, screenshots of:
- Streamlit Ledger page (record submission & summary)
- Streamlit Analytics page (filters, KPIs, charts)
- MySQL proof queries  
are to be included in your submission ZIP or GitHub repository.

---

##  Project Limitations & Future Enhancements

**Current Limitations:**
- `stop_time` field accepts manual input instead of a time picker.  
- Limited validation for vehicle numbers and country names.  
- Currently optimized for MySQL only (PostgreSQL support planned).

**Planned Enhancements:**
- Integrate a **time dropdown** for accurate hour analytics.  
- Add **authentication (login-based dashboard)** for different officer levels.  
- Deploy the Streamlit app to the web (using Streamlit Cloud or AWS).  
- Extend analytics to include **heatmaps** and **predictive trends** (risk-prone areas).

---

##  Quick Demo Script (for Viva or Presentation)

1. **Open the Streamlit app** (`streamlit run clean_app.py`)  
   → Show Ledger page → Add one new record.  
   → Point out the auto-generated paragraph and database entry.

2. **Switch to Analytics & Check page**  
   → Apply filters (e.g., Country = India, Violation = Speeding).  
   → Show how KPIs, charts, and the narrative summary update dynamically.

3. **Open MySQL Workbench**  
   → Run `SELECT * FROM traffic_stops ORDER BY id DESC LIMIT 5;`  
   → Show the latest record you just added.

4. **Close by summarizing:**  
   > “This Digital Ledger for Patrol Post Logs system combines Python, Streamlit, and MySQL to create a real-time, interactive reporting and analytics tool for police data — ensuring both operational efficiency and data-driven insight.”

---

## Requirements

```
streamlit
pandas
sqlalchemy
pymysql
plotly
```

All dependencies are already listed in the **requirements.txt** file.  
Install them before running the app using:  
```bash
pip install -r requirements.txt
```

---

##  Developed By
**Bharanigeswari S**  
*Data Science Project | Digital Ledger for Patrol Post Logs*

---
