"""
generate_dashboard.py
Generates an Excel workbook with monthly-aggregated sales data for 2023 & 2024 and a dashboard.
Requirements:
    pip install pandas numpy XlsxWriter
Run:
    python generate_dashboard.py
Output:
    EmmanuelNyamekye_SalesDashboard_2023_2024.xlsx
"""
import pandas as pd
import numpy as np
from datetime import datetime

# ---------------------- Configuration ----------------------
OUTPUT_XLSX = "EmmanuelNyamekye_SalesDashboard_2023_2024.xlsx"
PRODUCTS = ["Laptop", "Smartphone", "Headphones", "Tablet", "Smartwatch", "Monitor"]
REGIONS = ["Accra", "Kumasi", "Takoradi", "Tamale", "Cape Coast"]
MONTHS = ["January","February","March","April","May","June","July","August","September","October","November","December"]
GROWTH_MIN = 0.10  # 10%
GROWTH_MAX = 0.15  # 15%
SEED = 42

np.random.seed(SEED)

# Helper to build monthly aggregated data for a given year
def build_year_data(year, growth_factor=0.0):
    records = []
    for month_index, month_name in enumerate(MONTHS, start=1):
        for product in PRODUCTS:
            for region in REGIONS:
                # Base units and price vary by product and month for realism
                # Units: 80-400 depending on product
                base_units = np.random.randint(80, 400)
                # Introduce a small seasonal factor
                season_multiplier = 1.0 + 0.05 * np.sin(2 * np.pi * (month_index/12))
                units = int(base_units * season_multiplier * (1 + growth_factor))
                # Unit price by product
                base_price = {
                    "Laptop": 1200,
                    "Smartphone": 800,
                    "Headphones": 120,
                    "Tablet": 600,
                    "Smartwatch": 250,
                    "Monitor": 350
                }.get(product, 300)
                # Add small variability to price
                price = int(base_price * np.random.uniform(0.9, 1.15))
                revenue = units * price
                profit = revenue * np.random.uniform(0.10, 0.25)
                date = datetime(year, month_index, 1)
                records.append({
                    "Date": date,
                    "Year": year,
                    "Month": month_name,
                    "Product": product,
                    "Region": region,
                    "Units_Sold": units,
                    "Unit_Price": price,
                    "Revenue": int(revenue),
                    "Profit": int(profit)
                })
    return pd.DataFrame.from_records(records)

# Build 2023 (base) and 2024 (with growth)
df_2023 = build_year_data(2023, growth_factor=0.0)
# apply growth between GROWTH_MIN and GROWTH_MAX randomly for realism per product/region/month
growth_factor = np.random.uniform(GROWTH_MIN, GROWTH_MAX)
df_2024 = build_year_data(2024, growth_factor=growth_factor)

# Combined sheet
df_all = pd.concat([df_2023, df_2024], ignore_index=True)

# Reorder columns for readability
cols = ["Date","Year","Month","Product","Region","Units_Sold","Unit_Price","Revenue","Profit"]
df_2023 = df_2023[cols]
df_2024 = df_2024[cols]
df_all = df_all[cols]

# ---------------------- Write to Excel with Dashboard ----------------------
with pd.ExcelWriter(OUTPUT_XLSX, engine="xlsxwriter", datetime_format="yyyy-mm-dd") as writer:
    # Write data sheets
    df_2023.to_excel(writer, sheet_name="Sales 2023", index=False)
    df_2024.to_excel(writer, sheet_name="Sales 2024", index=False)
    df_all.to_excel(writer, sheet_name="All Data", index=False)

    workbook = writer.book
    dashboard = workbook.add_worksheet("Dashboard")

    # Formats
    title_fmt = workbook.add_format({'bold': True, 'font_size': 16, 'font_color': '#1F4E78'})
    subtitle_fmt = workbook.add_format({'italic': True, 'font_size': 10, 'font_color': '#4F81BD'})
    bold = workbook.add_format({'bold': True})
    kpi_fmt = workbook.add_format({'bold': True, 'font_size': 12, 'align': 'center', 'valign': 'vcenter'})
    money_fmt = workbook.add_format({'num_format': '#,##0', 'bold': False})
    percent_fmt = workbook.add_format({'num_format':'0.0%','bold':True})
    header_fmt = workbook.add_format({'bold': True, 'bg_color': '#EAF1FB'})

    # Title & subtitle
    dashboard.write("A1", "Sales Performance Dashboard (2023–2024)", title_fmt)
    dashboard.write("A2", "Prepared by Emmanuel Nyamekye | Data Analyst", subtitle_fmt)

    # KPI labels
    dashboard.write("A4", "KPI", header_fmt)
    dashboard.write("B4", "Value", header_fmt)
    dashboard.write("A5", "Total Revenue (2023)", bold)
    dashboard.write_formula("B5", "=SUMIFS('All Data'!H:H,'All Data'!B:B,2023)", money_fmt)
    dashboard.write("A6", "Total Revenue (2024)", bold)
    dashboard.write_formula("B6", "=SUMIFS('All Data'!H:H,'All Data'!B:B,2024)", money_fmt)
    dashboard.write("A7", "YoY Revenue Growth", bold)
    dashboard.write_formula("B7", "=(B6-B5)/IF(B5=0,1,B5)", percent_fmt)
    dashboard.write("A8", "Total Profit (2024)", bold)
    dashboard.write_formula("B8", "=SUMIFS('All Data'!I:I,'All Data'!B:B,2024)", money_fmt)
    dashboard.write("A9", "Total Units Sold (2024)", bold)
    dashboard.write_formula("B9", "=SUMIFS('All Data'!F:F,'All Data'!B:B,2024)", money_fmt)

    # Build a small monthly summary table on Dashboard for charting (Jan-Dec)
    dashboard.write("A12", "Month", header_fmt)
    dashboard.write("B12", "Revenue 2023", header_fmt)
    dashboard.write("C12", "Revenue 2024", header_fmt)
    # Write months and formulas to pull monthly sums
    for i, month in enumerate(MONTHS, start=1):
        row = 12 + i
        dashboard.write(row-1, 0, month)  # A13..A24
        # SUMIFS over All Data: Revenue where Year=2023 and Month=month
        formula_2023 = "=SUMIFS('All Data'!H:H,'All Data'!B:B,2023,'All Data'!C:C,\"{m}\")".format(m=month)
        formula_2024 = "=SUMIFS('All Data'!H:H,'All Data'!B:B,2024,'All Data'!C:C,\"{m}\")".format(m=month)
        dashboard.write_formula(row-1, 1, formula_2023, money_fmt)
        dashboard.write_formula(row-1, 2, formula_2024, money_fmt)

    # Create Line chart for monthly revenue trend (2023 vs 2024)
    chart_line = workbook.add_chart({'type': 'line'})
    # categories: Dashboard!$A$13:$A$24
    chart_line.add_series({
        'name':       'Revenue 2023',
        'categories': ['Dashboard', 12, 0, 23, 0],
        'values':     ['Dashboard', 12, 1, 23, 1],
        'marker':     {'type': 'circle'}
    })
    chart_line.add_series({
        'name':       'Revenue 2024',
        'categories': ['Dashboard', 12, 0, 23, 0],
        'values':     ['Dashboard', 12, 2, 23, 2],
        'marker':     {'type': 'diamond'}
    })
    chart_line.set_title({'name': 'Monthly Revenue Trend (2023 vs 2024)'})
    chart_line.set_x_axis({'name': 'Month'})
    chart_line.set_y_axis({'name': 'Revenue'})
    chart_line.set_style(12)
    dashboard.insert_chart('E12', chart_line, {'x_scale': 1.6, 'y_scale': 1.4})

    # Top Products (Revenue 2024) table on dashboard
    prod_start_row = 26
    dashboard.write(prod_start_row-1, 0, "Top Products (2024)", header_fmt)
    dashboard.write(prod_start_row-1, 1, "Revenue", header_fmt)
    for i, prod in enumerate(PRODUCTS):
        r = prod_start_row + i
        dashboard.write(r-1, 0, prod)
        formula = "=SUMIFS('All Data'!H:H,'All Data'!D:D,\"{p}\",'All Data'!B:B,2024)".format(p=prod)
        dashboard.write_formula(r-1, 1, formula, money_fmt)

    # Column chart for top products
    chart_col = workbook.add_chart({'type': 'column'})
    chart_col.add_series({
        'name': 'Revenue by Product (2024)',
        'categories': ['Dashboard', prod_start_row-1, 0, prod_start_row-1+len(PRODUCTS)-1, 0],
        'values': ['Dashboard', prod_start_row-1, 1, prod_start_row-1+len(PRODUCTS)-1, 1],
    })
    chart_col.set_title({'name': 'Revenue by Product (2024)'})
    chart_col.set_style(11)
    dashboard.insert_chart('E30', chart_col, {'x_scale': 1.4, 'y_scale': 1.1})

    # Revenue by Region (2024) table and pie chart
    region_start_row = prod_start_row + len(PRODUCTS) + 2
    dashboard.write(region_start_row-1, 0, "Revenue by Region (2024)", header_fmt)
    dashboard.write(region_start_row-1, 1, "Revenue", header_fmt)
    for i, reg in enumerate(REGIONS):
        r = region_start_row + i
        dashboard.write(r-1, 0, reg)
        formula = "=SUMIFS('All Data'!H:H,'All Data'!E:E,\"{r}\",'All Data'!B:B,2024)".format(r=reg)
        dashboard.write_formula(r-1, 1, formula, money_fmt)

    chart_pie = workbook.add_chart({'type': 'pie'})
    chart_pie.add_series({
        'name': 'Revenue by Region (2024)',
        'categories': ['Dashboard', region_start_row-1, 0, region_start_row-1+len(REGIONS)-1, 0],
        'values': ['Dashboard', region_start_row-1, 1, region_start_row-1+len(REGIONS)-1, 1],
    })
    chart_pie.set_title({'name': 'Revenue by Region (2024)'})
    chart_pie.set_style(10)
    dashboard.insert_chart('K4', chart_pie, {'x_scale': 1.0, 'y_scale': 1.0})

    # Set column widths for neat appearance
    dashboard.set_column('A:A', 20)
    dashboard.set_column('B:C', 18)
    dashboard.set_column('E:E', 40)
    dashboard.set_column('K:K', 18)

    # Freeze panes to keep title visible
    dashboard.freeze_panes(11, 0)

print(f"Saved: {OUTPUT_XLSX}")
