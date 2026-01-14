# TODO: Implement Streamlit Dashboard for Netflix Content Strategy Analysis

- [x] Add Streamlit import to main.py
- [x] Create run_dashboard function that loads data, cleans it, performs analysis, and displays results using Streamlit components (plots with st.plotly_chart, top titles with st.dataframe, etc.)
- [x] Organize dashboard with sections/tabs for each analysis (e.g., Viewership by Content Type, Monthly Trends, Top Titles)
- [x] Add --web command-line argument to argparse
- [x] Modify main function to check for --web flag and run streamlit run main.py if set, else run CLI analysis
- [x] Install Streamlit dependency (pip install streamlit)
- [ ] Test the dashboard by running with --web flag and verify plots and tables display correctly
