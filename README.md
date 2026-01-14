# Netflix Content Strategy Analysis 

This project analyzes Netflix content data to uncover insights that can help in **content planning, release strategy, and audience targeting**.  
It supports both **CLI-based analysis** and an **interactive Streamlit dashboard**.

---

## What This Project Does

The script processes a Netflix content CSV dataset and provides:

- Total viewership analysis by **Content Type** (Movies, Series, etc.)
- Viewership trends by **Language**
- **Monthly**, **Weekly**, and **Seasonal** viewership patterns
- Trends of content types over months
- Analysis of releases around **important holidays**
- Identification of **top-performing titles**
- Interactive visualizations using **Plotly**
- Optional **web dashboard** using **Streamlit**

All plots are saved as **interactive HTML files** for easy sharing.

---

## Project Structure
```bash
Netflix-Content-Strategy-Analysis/
│
├── netflix_content.csv # Input dataset 
├── outputs/ # Auto-generated interactive plots & CSVs
├── main.py # Main analysis + dashboard script
├── README.md # Project documentation
```
---

## Key Insights Generated

- Which **content types** drive the most watch hours
- Best **months & seasons** to release new content
- Optimal **weekdays** for releases
- Performance impact of **holiday-adjacent releases**
- Languages with highest audience engagement

---

## Tech Stack

- **Python**
- **Pandas** – data cleaning & aggregation  
- **Plotly** – interactive visualizations  
- **Streamlit** – web dashboard  
- **Argparse** – CLI support  

---

## How to Run

### 1️⃣ Install Dependencies
```bash
pip install pandas plotly streamlit
```
### 2️⃣ Run CLI Analysis
Generates all plots and saves them in the outputs/ folder.

```bash

python analysis.py --file netflix_content.csv
```
Optional arguments:

```bash

--hours_col "Hours Viewed"
--date_col "Release Date"
--language_col "Language Indicator"
--top_n 5
```
### 3️⃣ Run Web Dashboard (Streamlit)
```bash

streamlit run analysis.py -- --web
```
This launches an interactive dashboard in your browser.

---

## 📊 Output
- Interactive bar & line charts (.html)

- Holiday release table (holiday_releases.csv)

- On-screen dashboard visualizations

---

## Dataset Requirements
Your CSV file should ideally include the following columns:

- Title

- Hours Viewed

- Release Date

- Content Type

- Language Indicator

(You can download the dataset from Kaggle or from my repository)

