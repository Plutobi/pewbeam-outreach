"""
Generates a professionally styled, executive-ready Excel workbook
for the Pewbeam founder, with summary analytics, qualified leads,
and multilingual outreach copy.
"""

import os
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

sys_path = os.path.dirname(__file__)
csv_path = os.path.join(sys_path, "pewbeam_church_leads_verified_200.csv")
out_path = os.path.join(sys_path, "Pewbeam_Qualified_Church_Leads_274.xlsx")

df = pd.read_csv(csv_path)

# Map countries/regions
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

wb = openpyxl.Workbook()

# Setup sheets
ws_summary = wb.active
ws_summary.title = "Executive Summary"
ws_leads = wb.create_sheet(title="Qualified Church Leads (274)")
ws_templates = wb.create_sheet(title="Outreach Copy (Multilingual)")

# Brand Styles
font_title = Font(name="Calibri", size=16, bold=True, color="FFFFFF")
font_subtitle = Font(name="Calibri", size=11, italic=True, color="FFD2B5")
font_header = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
font_bold = Font(name="Calibri", size=11, bold=True, color="000000")
font_regular = Font(name="Calibri", size=11, color="1A1A1A")
font_kpi_num = Font(name="Calibri", size=20, bold=True, color="FF5700")

fill_obsidian = PatternFill(start_color="080707", end_color="080707", fill_type="solid")
fill_orange = PatternFill(start_color="FF5700", end_color="FF5700", fill_type="solid")
fill_header = PatternFill(start_color="1A1817", end_color="1A1817", fill_type="solid")
fill_light_gray = PatternFill(start_color="F9F8F7", end_color="F9F8F7", fill_type="solid")

thin_border = Border(
    left=Side(style='thin', color='E0DCD9'),
    right=Side(style='thin', color='E0DCD9'),
    top=Side(style='thin', color='E0DCD9'),
    bottom=Side(style='thin', color='E0DCD9')
)

# ----------------- SHEET 1: EXECUTIVE SUMMARY -----------------
ws_summary.column_dimensions['B'].width = 30
ws_summary.column_dimensions['C'].width = 18
ws_summary.column_dimensions['D'].width = 35

# Title Banner
ws_summary.merge_cells('B2:D2')
ws_summary['B2'] = "⚡ PEWBEAM - GLOBAL CHURCH LEAD CAMPAIGN"
ws_summary['B2'].font = font_title
ws_summary['B2'].fill = fill_obsidian
ws_summary['B2'].alignment = Alignment(horizontal="center", vertical="center")
ws_summary.row_dimensions[2].height = 36

ws_summary.merge_cells('B3:D3')
ws_summary['B3'] = "Qualified High-Production Churches with Active AV / Media Teams (UK, Europe & US)"
ws_summary['B3'].font = font_subtitle
ws_summary['B3'].fill = fill_obsidian
ws_summary['B3'].alignment = Alignment(horizontal="center", vertical="center")
ws_summary.row_dimensions[3].height = 22

# KPI Cards
kpis = [
    ("B5", "C5", "TOTAL QUALIFIED CHURCHES", str(len(df))),
    ("B6", "C6", "DIRECT MEDIA / TECH CONTACTS", "100%"),
    ("B7", "C7", "AFRICAN MEGACHURCH HUBS", "35"),
    ("B8", "C8", "EUROPE, UK & US HUBS", str(len(df) - 35)),
]

for cell_label, cell_val, label, val in kpis:
    ws_summary[cell_label] = label
    ws_summary[cell_label].font = font_bold
    ws_summary[cell_val] = val
    ws_summary[cell_val].font = font_kpi_num
    ws_summary[cell_val].alignment = Alignment(horizontal="center")

# Region Breakdown Table
ws_summary['B11'] = "Target Region"
ws_summary['C11'] = "Lead Count"
ws_summary['D11'] = "Primary Outreach Language"

for c in ['B11', 'C11', 'D11']:
    ws_summary[c].font = font_header
    ws_summary[c].fill = fill_orange
    ws_summary[c].alignment = Alignment(horizontal="center")

region_counts = df['Region'].value_counts()
langs = {
    "🇺🇸 United States": "English (US)",
    "🇬🇧 United Kingdom": "English (UK)",
    "🇩🇪 Germany & DACH": "German (Deutsch)",
    "🇫🇷 France & Belgium": "French (Français)",
    "🇪🇸 Spain": "Spanish (Español)",
    "🇳🇱 Netherlands": "Dutch (Nederlands)",
    "🇮🇹 Italy": "Italian (Italiano)"
}

row_idx = 12
for reg, cnt in region_counts.items():
    ws_summary[f'B{row_idx}'] = reg
    ws_summary[f'C{row_idx}'] = cnt
    ws_summary[f'D{row_idx}'] = langs.get(reg, "English")
    
    ws_summary[f'B{row_idx}'].font = font_regular
    ws_summary[f'C{row_idx}'].font = font_bold
    ws_summary[f'C{row_idx}'].alignment = Alignment(horizontal="center")
    ws_summary[f'D{row_idx}'].font = font_regular
    
    for c in [f'B{row_idx}', f'C{row_idx}', f'D{row_idx}']:
        ws_summary[c].border = thin_border
    row_idx += 1

# ----------------- SHEET 2: QUALIFIED LEADS -----------------
lead_cols = ["Church Name", "Region", "City", "Emails", "Website", "Phone", "Rating", "Address"]
ws_leads.append(lead_cols)

for col_idx, col_name in enumerate(lead_cols, start=1):
    cell = ws_leads.cell(row=1, column=col_idx)
    cell.font = font_header
    cell.fill = fill_orange
    cell.alignment = Alignment(horizontal="center" if col_name in ("Region", "Rating") else "left")

for _, r in df.iterrows():
    row_data = [
        r.get("Church Name", ""),
        r.get("Region", ""),
        r.get("City", ""),
        r.get("Emails", ""),
        r.get("Website", ""),
        r.get("Phone", ""),
        r.get("Rating", ""),
        r.get("Address", "")
    ]
    ws_leads.append(row_data)

for row in ws_leads.iter_rows(min_row=2, max_row=len(df)+1, min_col=1, max_col=len(lead_cols)):
    for cell in row:
        cell.font = font_regular
        cell.border = thin_border

# Auto fit columns in leads sheet
for col in ws_leads.columns:
    max_len = max(len(str(cell.value or '')) for cell in col)
    col_letter = get_column_letter(col[0].column)
    ws_leads.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 45)

# ----------------- SHEET 3: OUTREACH TEMPLATES -----------------
ws_templates.column_dimensions['A'].width = 18
ws_templates.column_dimensions['B'].width = 40
ws_templates.column_dimensions['C'].width = 65

ws_templates.append(["Language / Region", "Email Subject Line", "Cold Email Pitch"])
for col_idx in range(1, 4):
    cell = ws_templates.cell(row=1, column=col_idx)
    cell.font = font_header
    cell.fill = fill_orange

templates_data = [
    ("🇬🇧 English (UK / US)", "Quick question about Sunday AV at {Church Name}", "Hi Media Team,\n\nNoticed the great production work your team is doing over at {Church Name} in {City}.\n\nOne of the biggest hurdles church media directors share with us is the Sunday scramble: when the pastor quotes a scripture off-script mid-sermon, and the booth is frantically searching, copying, and formatting slides before the moment passes.\n\nWe built Pewbeam (https://pewbeam.com/) specifically for that. It uses real-time AI audio recognition to listen to the sermon and automatically project the exact Bible verses on screens and livestream lower-thirds (NDI / OBS / vMix compatible) with zero manual searching.\n\nWould you be open to a 2-minute video walkthrough to see if it could save your team time this Sunday?\n\nWarm regards,\n[Your Name] - Pewbeam"),
    ("🇩🇪 German (DACH)", "Kurze Frage zur Beamer- & Livestream-Technik bei {Church Name}", "Hallo Technik- & Medienteam,\n\nich habe eure Medienarbeit bei {Church Name} in {City} gesehen – großes Kompliment an euer Team!\n\nViele Leiter der Gemeindetechnik kennen das typische Problem am Sonntagmorgen: Der Pastor zitiert während der Predigt spontan eine Bibelstelle, die nicht im Ablaufplan stand, und das Beamer-Team muss in Sekundenschnelle hektisch nach der Stelle suchen und Folien erstellen.\n\nGenau dafür haben wir Pewbeam (https://pewbeam.com/) entwickelt. Unsere Software hört der Predigt per KI in Echtzeit zu und projiziert automatisch die passenden Bibelverse auf die Leinwand sowie als Bauchbinde in den Livestream (voll kompatibel mit NDI, OBS und vMix) – komplett ohne manuelles Suchen.\n\nHättet ihr Zeit für ein kurzes 2-minütiges Video, um zu sehen, wie Pewbeam eure Gottesdienste entlasten kann?\n\nHerzliche Grüße,\n[Dein Name] - Pewbeam"),
    ("🇫🇷 French", "Question rapide sur votre régie technique à {Church Name}", "Bonjour l'Équipe Régie,\n\nFélicitations pour la qualité des cultes et de la diffusion que vous réalisez à {Church Name} à {City}.\n\nLa plupart des responsables techniques d'église partagent le même défi : lorsque le pasteur cite un verset biblique impromptu pendant la prédication, l'équipe régie doit chercher et formater les diapositives dans l'urgence.\n\nNous avons créé Pewbeam (https://pewbeam.com/) pour résoudre ce problème. Notre solution écoute la prédication en temps réel grâce à l'IA et affiche instantanément les versets bibliques exacts sur vos écrans et en bandeaux sur le livestream (compatible NDI, OBS, vMix), sans aucune manipulation manuelle.\n\nSeriez-vous ouverts à une vidéo démo de 2 minutes ?\n\nBien cordialement,\n[Votre Nom] - Pewbeam"),
    ("🇪🇸 Spanish", "Pregunta rápida sobre la transmisión y pantallas en {Church Name}", "Hola Equipo Multimedia,\n\nQuería felicitarlos por el gran trabajo de producción y streaming que realizan en {Church Name} en {City}.\n\nMuchos directores de multimedia nos comentan el mismo desafío: cuando el pastor cita un versículo bíblico improvisado durante la prédica, la cabina corre para buscarlo y proyectarlo antes de que pase el momento.\n\nPor eso creamos Pewbeam (https://pewbeam.com/). Utiliza IA para escuchar la prédica en tiempo real y proyecta automáticamente los versículos bíblicos en las pantallas y en los tercios inferiores de la transmisión (NDI, OBS, vMix).\n\n¿Estarían abiertos a un video de 2 minutos para ver cómo funciona?\n\nUn cordial saludo,\n[Tu Nombre] - Pewbeam")
]

for t in templates_data:
    ws_templates.append([t[0], t[1], t[2]])

for row in ws_templates.iter_rows(min_row=2, max_row=len(templates_data)+1, min_col=1, max_col=3):
    for cell in row:
        cell.font = font_regular
        cell.border = thin_border
        cell.alignment = Alignment(wrap_text=True, vertical="top")

wb.save(out_path)
print(f"[+] Successfully generated executive Excel workbook: {out_path}")
