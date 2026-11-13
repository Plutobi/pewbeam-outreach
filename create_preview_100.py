import os
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

sys_path = os.path.dirname(__file__)
csv_path = os.path.join(sys_path, "pewbeam_church_leads_verified_200.csv")
df = pd.read_csv(csv_path)

# Map clean regions
def map_country(state):
    s = str(state).strip()
    if s in ("Nigeria", "Ghana", "Kenya", "South Africa", "Uganda", "Rwanda"):
        return f"🌍 Africa ({s})"
    elif s in ("United Kingdom", "UK"):
        return "🇬🇧 United Kingdom"
    elif s in ("Germany", "Deutschland", "Austria", "Switzerland"):
        return "🇩🇪 Germany & DACH"
    elif s in ("France", "Belgium"):
        return "🇫🇷 France & Belgium"
    elif s in ("Spain", "España"):
        return "🇪🇸 Spain"
    elif s in ("Netherlands", "Nederland"):
        return "🇳🇱 Netherlands"
    elif s in ("Italy", "Italia"):
        return "🇮🇹 Italy"
    else:
        return "🇺🇸 United States"

df["Region"] = df["State"].apply(map_country)

# Take top 100 diversified leads
# e.g., 25 UK, 25 US, 30 Africa, 20 Europe
regions = df["Region"].unique()
sample_100_parts = []
for reg in regions:
    sub = df[df["Region"] == reg]
    if "Africa" in reg:
        n = min(len(sub), 6) # across 5 African nations = ~30
    elif "United Kingdom" in reg:
        n = min(len(sub), 25)
    elif "United States" in reg:
        n = min(len(sub), 25)
    elif "Germany" in reg:
        n = min(len(sub), 10)
    elif "France" in reg:
        n = min(len(sub), 5)
    else:
        n = min(len(sub), 4)
    sample_100_parts.append(sub.head(n))

sample_100_df = pd.concat(sample_100_parts).drop_duplicates(subset=["Church Name"])

# If under 100, fill up from remaining df to exactly 100
if len(sample_100_df) < 100:
    remaining = df[~df["Church Name"].isin(sample_100_df["Church Name"])]
    sample_100_df = pd.concat([sample_100_df, remaining.head(100 - len(sample_100_df))])
elif len(sample_100_df) > 100:
    sample_100_df = sample_100_df.head(100)

print(f"[+] Selected {len(sample_100_df)} balanced preview leads")

# Save CSV
csv_out = os.path.join(sys_path, "pewbeam_church_leads_preview_100.csv")
sample_100_df.to_csv(csv_out, index=False)
print(f"[+] Saved CSV: {csv_out}")

# Save XLSX
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Sample Leads (100 Preview)"

font_header = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
font_regular = Font(name="Calibri", size=11, color="1A1A1A")
fill_orange = PatternFill(start_color="FF5700", end_color="FF5700", fill_type="solid")
thin_border = Border(
    left=Side(style='thin', color='E0DCD9'),
    right=Side(style='thin', color='E0DCD9'),
    top=Side(style='thin', color='E0DCD9'),
    bottom=Side(style='thin', color='E0DCD9')
)

cols = ["Church Name", "Region", "City", "Emails", "Website", "Phone", "Rating"]
ws.append(cols)

for col_idx in range(1, len(cols) + 1):
    c = ws.cell(row=1, column=col_idx)
    c.font = font_header
    c.fill = fill_orange

for _, r in sample_100_df.iterrows():
    row_data = [
        r.get("Church Name", ""),
        r.get("Region", ""),
        r.get("City", ""),
        r.get("Emails", ""),
        r.get("Website", ""),
        r.get("Phone", ""),
        r.get("Rating", "")
    ]
    ws.append(row_data)

for row in ws.iter_rows(min_row=2, max_row=len(sample_100_df)+1, min_col=1, max_col=len(cols)):
    for cell in row:
        cell.font = font_regular
        cell.border = thin_border

for col in ws.columns:
    max_len = max(len(str(cell.value or '')) for cell in col)
    col_letter = get_column_letter(col[0].column)
    ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 40)

xlsx_out = os.path.join(sys_path, "Pewbeam_Church_Leads_Preview_100.xlsx")
wb.save(xlsx_out)
print(f"[+] Saved Excel: {xlsx_out}")

try:
    wb.save(os.path.expanduser("~/Desktop/Pewbeam_Church_Leads_Preview_100.xlsx"))
    wb.save(os.path.expanduser("~/Downloads/Pewbeam_Church_Leads_Preview_100.xlsx"))
    print("[+] Also saved to Desktop and Downloads!")
except Exception as e:
    pass
