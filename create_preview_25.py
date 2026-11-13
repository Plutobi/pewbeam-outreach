"""
Creates a 25-church teaser/preview Excel workbook
for high-leverage client presentation.
"""

import os
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

sys_path = os.path.dirname(__file__)
csv_path = os.path.join(sys_path, "pewbeam_church_leads_verified_200.csv")
out_path = os.path.join(sys_path, "Pewbeam_Church_Leads_Preview_25.xlsx")

df = pd.read_csv(csv_path)

# Pick 25 top flagship churches
sample_indices = [
    0, 1, 2, 5, 7,     # Top UK (HTB, Hillsong London, All Souls, Audacious, Gas Street)
    25, 27, 34,        # Top Germany (ICF Berlin, Hillsong Germany, ICF Zurich)
    43, 44,            # Top France (Hillsong Paris, MLK Paris)
    53,                # Top Netherlands (Mozaiek0318)
    59,                # Top Spain (Hillsong Madrid)
    65,                # Top Italy (Hillsong Milan)
    92, 93, 94, 96, 98,# Top Nigeria (Elevation, Covenant Nation, Daystar, House on the Rock, COZA)
    106, 107,          # Top Ghana (Action Chapel, ICGC)
    111, 112,          # Top South Africa (Rhema, Rivers)
    118, 119, 120      # Top US (Prestonwood, Watermark, Passion City)
]

sample_df = df.iloc[[i for i in sample_indices if i < len(df)]].copy()

# Add region
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

sample_df["Region"] = sample_df["State"].apply(map_country)

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Sample Leads (25 Preview)"

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

for _, r in sample_df.iterrows():
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

for row in ws.iter_rows(min_row=2, max_row=len(sample_df)+1, min_col=1, max_col=len(cols)):
    for cell in row:
        cell.font = font_regular
        cell.border = thin_border

for col in ws.columns:
    max_len = max(len(str(cell.value or '')) for cell in col)
    col_letter = get_column_letter(col[0].column)
    ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 40)

# Also save CSV preview
csv_preview_path = os.path.join(sys_path, "pewbeam_church_leads_preview_25.csv")
sample_df.to_csv(csv_preview_path, index=False)
print(f"[+] Saved CSV preview: {csv_preview_path}")

# Also save to Desktop and Downloads
wb.save(out_path)
print(f"[+] Saved preview: {out_path}")
try:
    wb.save(os.path.expanduser("~/Desktop/Pewbeam_Church_Leads_Preview_25.xlsx"))
    wb.save(os.path.expanduser("~/Downloads/Pewbeam_Church_Leads_Preview_25.xlsx"))
    print("[+] Also copied to Desktop and Downloads!")
except Exception as e:
    pass
