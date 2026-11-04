"""Build redesigned 13-slide academic PPTX + PDF from verified analysis outputs.

Statistics are taken only from outputs/statistics_and_sources.json and
verified_findings.md. No new models; no invented numbers.
"""
from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

BASE = Path(__file__).resolve().parent
OUT = BASE / "outputs"
FIG = OUT / "figures"
PRESENT = FIG / "present"
DECK = OUT / "EU27_Electricity_Transition.pptx"
PDF = OUT / "EU27_Electricity_Transition.pdf"

W, H = Inches(13.333), Inches(7.5)
NAVY = RGBColor(0x1F, 0x2A, 0x37)
MUTED = RGBColor(0x5A, 0x66, 0x73)
TEAL = RGBColor(0x1A, 0x7A, 0x6D)
SOFT = RGBColor(0xE8, 0xF2, 0xEF)
PANEL = RGBColor(0xF4, 0xF7, 0xF9)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LINE = RGBColor(0xD5, 0xDE, 0xE6)
ACCENT = RGBColor(0x3D, 0x6B, 0x9A)
BROWN = RGBColor(0xB8, 0x6F, 0x50)

SOURCE_SHORT = "OWID Energy 2026-09-10 · electricity mainly Ember · gCO₂eq/kWh = lifecycle intensity"
SOURCE_URL = "https://catalog.ourworldindata.org/garden/energy/2026-09-10/owid_energy/owid_energy.csv"


def set_run(run, size=16, bold=False, color=NAVY, name="Calibri"):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = name


def add_text(slide, left, top, width, height, text, *, size=16, bold=False,
             color=NAVY, align=PP_ALIGN.LEFT, font="Calibri"):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    set_run(run, size=size, bold=bold, color=color, name=font)
    return box


def add_multiline(slide, left, top, width, height, lines, *, size=14, color=NAVY, bold_first=False):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_after = Pt(6)
        run = p.add_run()
        run.text = line
        set_run(run, size=size, bold=(bold_first and i == 0), color=color)
    return box


def rect(slide, left, top, width, height, fill, line=None):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    if line is None:
        shape.line.fill.background()
    else:
        shape.line.color.rgb = line
        shape.line.width = Pt(1)
    # tighter corners
    try:
        shape.adjustments[0] = 0.08
    except Exception:
        pass
    return shape


def blank(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, W, H)
    bg.fill.solid()
    bg.fill.fore_color.rgb = WHITE
    bg.line.fill.background()
    return slide


def chrome(slide, title: str, footer: str = SOURCE_SHORT):
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, W, Inches(0.08))
    bar.fill.solid()
    bar.fill.fore_color.rgb = TEAL
    bar.line.fill.background()
    add_text(slide, Inches(0.45), Inches(0.22), Inches(12.4), Inches(0.55),
             title, size=24, bold=True, color=NAVY)
    add_text(slide, Inches(0.45), Inches(7.08), Inches(12.4), Inches(0.3),
             footer, size=9, color=MUTED)


def picture(slide, path: Path, left, top, width=None, height=None):
    if not path.is_file():
        add_text(slide, left, top, Inches(6), Inches(0.5),
                 f"[Missing: {path.name}]", size=14, color=MUTED)
        return None
    kwargs = {}
    if width is not None:
        kwargs["width"] = width
    if height is not None:
        kwargs["height"] = height
    return slide.shapes.add_picture(str(path), left, top, **kwargs)


def callout(slide, left, top, width, height, title, body, accent=TEAL):
    rect(slide, left, top, width, height, PANEL, LINE)
    stripe = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, Inches(0.08), height)
    stripe.fill.solid()
    stripe.fill.fore_color.rgb = accent
    stripe.line.fill.background()
    add_text(slide, left + Inches(0.22), top + Inches(0.12), width - Inches(0.35), Inches(0.35),
             title, size=12, bold=True, color=accent)
    add_text(slide, left + Inches(0.22), top + Inches(0.42), width - Inches(0.35), height - Inches(0.5),
             body, size=12, color=NAVY)


def notes(slide, text: str):
    slide.notes_slide.notes_text_frame.text = text



def load_ctx():
    import json
    import pandas as pd
    stats = json.loads((OUT / "statistics_and_sources.json").read_text(encoding="utf8"))
    yearly = pd.read_csv(OUT / "yearly_coverage_and_weighted_indicators.csv")
    year = int(stats["year"])
    y0 = yearly.loc[yearly["year"] == 2010].iloc[0]
    y1 = yearly.loc[yearly["year"] == year].iloc[0]
    return {
        "year": year,
        "n_rows": 27 * (year - 2010 + 1),
        "re0": float(y0["eu_generation_weighted_renew"]),
        "nu0": float(y0["eu_generation_weighted_nuclear"]),
        "fo0": float(y0["eu_generation_weighted_fossil"]),
        "re1": float(y1["eu_generation_weighted_renew"]),
        "nu1": float(y1["eu_generation_weighted_nuclear"]),
        "fo1": float(y1["eu_generation_weighted_fossil"]),
        "int0": float(y0["eu_generation_weighted_intensity"]),
        "int1": float(y1["eu_generation_weighted_intensity"]),
        "rho_re": float(stats["renew"]["spearman_rho"]),
        "p_re": float(stats["renew"]["p_value"]),
        "rho_lc": float(stats["lowcarbon"]["spearman_rho"]),
        "p_lc": float(stats["lowcarbon"]["p_value"]),
        "k": int(stats["clustering"]["k"]),
        "sil": float(stats["clustering"]["silhouette_score"]),
        "pca": float(stats["clustering"]["pca_two_components_variance"]),
    }


def build():
    # Ensure presentation chart/diagram assets exist
    from make_presentation_assets import main as make_assets
    make_assets()
    ctx = load_ctx()
    year = ctx["year"]

    prs = Presentation()
    prs.slide_width = W
    prs.slide_height = H

    # ── 01 Cover ──────────────────────────────────────────────
    s = blank(prs)
    hero = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, W, Inches(3.1))
    hero.fill.solid()
    hero.fill.fore_color.rgb = SOFT
    hero.line.fill.background()
    add_text(s, Inches(0.6), Inches(0.7), Inches(12), Inches(0.9),
             "How green is Europe's electricity?", size=34, bold=True, color=NAVY)
    add_text(s, Inches(0.6), Inches(1.65), Inches(12), Inches(0.5),
             f"EU-27 generation mixes, lifecycle intensity, and the role of nuclear · 2010–{year}",
             size=18, color=TEAL)
    add_text(s, Inches(0.6), Inches(2.3), Inches(12), Inches(0.4),
             "Scientific Visualization", size=14, color=MUTED)

    for i, (label, value) in enumerate([
        ("Dataset", "OWID Energy\n2026-09-10"),
        ("Scope", f"EU-27 · ISO3\n2010–{year}"),
        ("Sample", f"{ctx['n_rows']} country–years\n27/27 in {year}"),
        ("Unit", "gCO₂eq / kWh\nlifecycle"),
    ]):
        left = Inches(0.6 + i * 3.1)
        rect(s, left, Inches(3.6), Inches(2.85), Inches(1.7), PANEL, LINE)
        add_text(s, left + Inches(0.2), Inches(3.75), Inches(2.5), Inches(0.35),
                 label, size=11, bold=True, color=TEAL)
        add_text(s, left + Inches(0.2), Inches(4.2), Inches(2.5), Inches(0.9),
                 value, size=14, color=NAVY)
    add_text(s, Inches(0.6), Inches(5.7), Inches(12), Inches(0.8),
             "Electricity indicators mainly from Ember, harmonized by Our World in Data.\n"
             f"{SOURCE_URL}",
             size=12, color=MUTED)
    notes(s, "State version pinning and that every number comes from the verified pipeline.")

    # ── 02 Research questions (visual) ────────────────────────
    s = blank(prs)
    chrome(s, "Research questions")
    picture(s, PRESENT / "d02_research_questions.png", Inches(0.35), Inches(0.9), width=Inches(12.5))
    notes(s, "Keep questions descriptive. Clustering is a side question with weak separation.")

    # ── 03 Provenance (visual) ────────────────────────────────
    s = blank(prs)
    chrome(s, "Source and provenance")
    picture(s, PRESENT / "d03_provenance.png", Inches(0.35), Inches(0.9), width=Inches(12.5))
    notes(s, "Credit Ember and OWID. Observation = country-year.")

    # ── 04 Variables (visual) ─────────────────────────────────
    s = blank(prs)
    chrome(s, "Variables, units and denominators")
    picture(s, PRESENT / "d04_variables.png", Inches(0.35), Inches(0.9), width=Inches(12.5))
    notes(s, "Stress: electricity shares ≠ final-energy renewables share. Intensity is lifecycle gCO2eq/kWh.")

    # ── 05 Pipeline (visual) ──────────────────────────────────
    s = blank(prs)
    chrome(s, "Cleaning and methodology")
    picture(s, PRESENT / "d05_pipeline.png", Inches(0.35), Inches(0.9), width=Inches(12.5))
    notes(s, "No imputation. Generation-weighted EU means. Spearman for association. Exploratory K-means.")

    # ── 06 Mix trend ──────────────────────────────────────────
    s = blank(prs)
    chrome(s, "How Europe's electricity mix changed")
    add_text(s, Inches(0.5), Inches(0.85), Inches(8.5), Inches(0.4),
             f"Renewables {ctx['re0']:.0f}% → {ctx['re1']:.0f}% · Fossil {ctx['fo0']:.0f}% → {ctx['fo1']:.0f}% · Nuclear {ctx['nu0']:.0f}% → {ctx['nu1']:.0f}% (generation-weighted)",
             size=13, bold=True, color=TEAL)
    picture(s, PRESENT / "01_mix_trend_annotated.png", Inches(0.35), Inches(1.25), width=Inches(9.0))
    callout(s, Inches(9.5), Inches(1.5), Inches(3.4), Inches(2.0),
            "Notice",
            "Renewables overtook fossil around 2020 after a long climb. Nuclear declined slowly but remains material.",
            TEAL)
    callout(s, Inches(9.5), Inches(3.75), Inches(3.4), Inches(2.3),
            "Method reminder",
            "EU lines are weighted by each country's electricity generation (TWh), so large systems dominate.",
            ACCENT)
    notes(s, "Walk the three lines. Mention 2021–22 pause. Weights matter.")

    # ── 07 Intensity ──────────────────────────────────────────
    s = blank(prs)
    chrome(s, "Carbon intensity through time")
    add_text(s, Inches(0.5), Inches(0.85), Inches(8.8), Inches(0.4),
             f"Lifecycle intensity fell from {ctx['int0']:.0f} to {ctx['int1']:.0f} gCO₂eq/kWh (2010→{year}), with a 2021–22 rebound",
             size=13, bold=True, color=TEAL)
    picture(s, PRESENT / "02_carbon_intensity_annotated.png", Inches(0.35), Inches(1.25), width=Inches(9.0))
    callout(s, Inches(9.5), Inches(1.5), Inches(3.4), Inches(2.2),
            "Notice",
            f"≈{100 * (1 - ctx['int1'] / ctx['int0']):.0f}% lower intensity by {year}. The 2022 rebound is visible before the later drop.",
            TEAL)
    callout(s, Inches(9.5), Inches(3.95), Inches(3.4), Inches(2.1),
            "Caveat",
            "Coverage here is 27/27 for this indicator set. Generation ≠ consumption (imports matter for demand).",
            BROWN)
    notes(s, f"Highlight 2020 trough, 2022 rebound, {year} level. Units: lifecycle gCO2eq per kWh generated.")

    # ── 08 Ranking ────────────────────────────────────────────
    s = blank(prs)
    chrome(s, f"Leaders and laggards · {year}")
    add_text(s, Inches(0.5), Inches(0.85), Inches(8.5), Inches(0.35),
             f"Low-carbon share spans Malta (~16%) to Sweden (~99%) — all 27 countries shown ({year})",
             size=13, bold=True, color=TEAL)
    picture(s, PRESENT / "03_low_carbon_ranking_present.png",
            Inches(0.3), Inches(1.2), height=Inches(5.55))
    callout(s, Inches(8.9), Inches(1.4), Inches(4.0), Inches(2.3),
            "Notice",
            "Top systems differ: Sweden (RE+nuclear), France (nuclear-led), Denmark (RE-led). Bottom: Poland, Cyprus, Malta.",
            TEAL)
    callout(s, Inches(8.9), Inches(3.95), Inches(4.0), Inches(2.1),
            "Full chart",
            "Same ranking without spotlight colours: figures/03_low_carbon_ranking.png in the repository.",
            MUTED)
    notes(s, "Do not cherry-pick. Leaders use different recipes.")

    # ── 09 Pathways ───────────────────────────────────────────
    s = blank(prs)
    chrome(s, "Three pathways to electricity generation")
    add_text(s, Inches(0.5), Inches(0.85), Inches(12), Inches(0.35),
             "Presentation spotlight of 9 representative countries · full EU-27 mix retained in the repository",
             size=13, bold=True, color=TEAL)
    picture(s, PRESENT / "06_electricity_mix_spotlight.png",
            Inches(0.35), Inches(1.25), width=Inches(9.1))
    callout(s, Inches(9.55), Inches(1.45), Inches(3.35), Inches(2.4),
            "Notice",
            "Same low fossil share can mean very different mixes: Denmark ≈ all renewables; France ≈ nuclear.",
            TEAL)
    callout(s, Inches(9.55), Inches(4.1), Inches(3.35), Inches(2.0),
            "Full visualisation",
            "All 27 stacked bars: figures/06_electricity_mix_by_country.png",
            MUTED)
    notes(s, "This sets up slides 10–11: renewables alone miss nuclear pathways.")

    # ── 10 Renewables vs intensity (story beat 1) ─────────────
    s = blank(prs)
    chrome(s, "Story beat 1 · Are renewables enough?")
    # Left narrative panel
    rect(s, Inches(0.4), Inches(1.0), Inches(4.0), Inches(5.5), PANEL, LINE)
    add_text(s, Inches(0.65), Inches(1.2), Inches(3.5), Inches(0.4),
             "Renewables only", size=18, bold=True, color=TEAL)
    add_text(s, Inches(0.65), Inches(1.75), Inches(3.5), Inches(1.2),
             f"Spearman ρ = {ctx['rho_re']:.2f}\np = {ctx['p_re']:.3g}\nn = 27 countries ({year})",
             size=16, bold=True, color=NAVY)
    add_multiline(s, Inches(0.65), Inches(3.2), Inches(3.5), Inches(3.0), [
        "What to notice",
        "• Moderate negative association only.",
        "• France: ~27% renewables, yet ~40 gCO₂eq/kWh.",
        "• Poland: modest RE share, ~608 gCO₂eq/kWh.",
        "• Renewables matter — but they are not the whole low-carbon story.",
    ], size=13, bold_first=True)
    picture(s, FIG / "04_renewables_vs_intensity.png",
            Inches(4.6), Inches(1.05), width=Inches(8.3))
    notes(s, "Make France the teaching point. Association ≠ causation. Hold for the contrast on the next slide.")

    # ── 11 Low-carbon vs intensity (story beat 2) ─────────────
    s = blank(prs)
    chrome(s, "Story beat 2 · What changes when nuclear is included?")
    rect(s, Inches(0.4), Inches(1.0), Inches(4.0), Inches(5.5), PANEL, LINE)
    add_text(s, Inches(0.65), Inches(1.2), Inches(3.5), Inches(0.4),
             "Low-carbon = RE + nuclear", size=17, bold=True, color=TEAL)
    add_text(s, Inches(0.65), Inches(1.75), Inches(3.5), Inches(1.3),
             f"Spearman ρ = {ctx['rho_lc']:.2f}\np = {ctx['p_lc']:.3g}\nn = 27 countries ({year})",
             size=16, bold=True, color=NAVY)
    add_multiline(s, Inches(0.65), Inches(3.2), Inches(3.5), Inches(3.0), [
        "Compare with previous slide",
        f"• |ρ| jumps from {abs(ctx['rho_re']):.2f} → {abs(ctx['rho_lc']):.2f}.",
        "• Nuclear closes the France / Slovakia gap.",
        "• Still descriptive — not a causal claim.",
        "• Definition: low-carbon share of electricity generation.",
    ], size=13, bold_first=True)
    picture(s, FIG / "05_lowcarbon_vs_intensity.png",
            Inches(4.6), Inches(1.05), width=Inches(8.3))
    notes(s, "Pause on the ρ contrast. Reiterate no causality. This is the main scientific-visualization insight.")

    # Optional combined story visual as extra reinforcement? User asked for 13 slides - we keep 13.
    # Slides 10-11 are the story; we could mention the combined figure in notes.
    # Actually let's add the combined figure as a small strip? Might clutter.
    # Better: keep 10 and 11 as designed. The combined asset is available if needed.

    # ── 12 Clustering ─────────────────────────────────────────
    s = blank(prs)
    chrome(s, "Country profiles · exploratory K-means + PCA")
    add_text(s, Inches(0.5), Inches(0.85), Inches(12), Inches(0.35),
             f"Best k = {ctx['k']} among 2–5, but silhouette = {ctx['sil']:.2f} (weak) · PCA 2D explains ~{100 * ctx['pca']:.0f}% variance",
             size=13, bold=True, color=BROWN)
    picture(s, FIG / "07_country_clusters_pca.png",
            Inches(0.4), Inches(1.25), width=Inches(8.8))
    callout(s, Inches(9.4), Inches(1.4), Inches(3.5), Inches(2.6),
            "Weak separation",
            "Silhouette ≈ 0.30 for every candidate k (0.28–0.30). Treat clusters as a visual aid, not natural regimes.",
            BROWN)
    callout(s, Inches(9.4), Inches(4.25), Inches(3.5), Inches(1.9),
            "Prefer",
            "Describe continuous portfolio differences (RE / nuclear / fossil) over hard cluster labels.",
            ACCENT)
    notes(s, "Be explicit: exploratory, weak silhouette, no ground-truth typology.")

    # ── 13 Conclusions ────────────────────────────────────────
    s = blank(prs)
    chrome(s, "Conclusions, limitations & sources", footer=SOURCE_URL)
    items = [
        (TEAL, "1", "EU mix transition",
         f"Generation-weighted renewables rose {ctx['re0']:.0f}%→{ctx['re1']:.0f}%; fossil fell {ctx['fo0']:.0f}%→{ctx['fo1']:.0f}%; intensity {ctx['int0']:.0f}→{ctx['int1']:.0f} gCO₂eq/kWh (2010–{year})."),
        (ACCENT, "2", "Divergent pathways",
         "Low-carbon leaders use different recipes: renewables-led, nuclear-led, or both."),
        (TEAL, "3", "Nuclear in the story",
         f"Renewables↔intensity ρ={ctx['rho_re']:.2f}; low-carbon↔intensity ρ={ctx['rho_lc']:.2f} (n=27). Descriptive, not causal."),
    ]
    for i, (color, num, title, body) in enumerate(items):
        top = Inches(1.0 + i * 1.35)
        rect(s, Inches(0.45), top, Inches(8.5), Inches(1.2), PANEL, LINE)
        circle = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.65), top + Inches(0.3), Inches(0.55), Inches(0.55))
        circle.fill.solid()
        circle.fill.fore_color.rgb = color
        circle.line.fill.background()
        add_text(s, Inches(0.65), top + Inches(0.38), Inches(0.55), Inches(0.4),
                 num, size=14, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        add_text(s, Inches(1.4), top + Inches(0.18), Inches(7.3), Inches(0.35),
                 title, size=14, bold=True, color=color)
        add_text(s, Inches(1.4), top + Inches(0.52), Inches(7.3), Inches(0.55),
                 body, size=12, color=NAVY)

    rect(s, Inches(9.2), Inches(1.0), Inches(3.7), Inches(4.0), PANEL, LINE)
    add_multiline(s, Inches(9.4), Inches(1.2), Inches(3.3), Inches(3.6), [
        "Limitations",
        "• No causal identification",
        "• Generation ≠ consumption / imports",
        "• Lifecycle ≠ stack-only CO₂",
        "• Clustering silhouette 0.30 → weak",
        "",
        "Reproducibility",
        f"analysis.py --year {year}",
        "outputs/verified_findings.md",
    ], size=12, bold_first=True)

    add_text(s, Inches(0.45), Inches(5.3), Inches(12.4), Inches(1.4),
             "Source: Our World in Data, Energy dataset version 2026-09-10 "
             "(electricity indicators mainly Ember; lifecycle intensity draws on Ember).\n"
             f"{SOURCE_URL}\n"
             "Also credit underlying providers via the OWID catalog. Full EU-27 charts remain in outputs/figures/.",
             size=11, color=MUTED)
    notes(s, "Close with three conclusions. Restate URL. Clustering is weak. No causality.")

    OUT.mkdir(parents=True, exist_ok=True)
    prs.save(DECK)
    print(f"Wrote {DECK}")
    write_backup_pdf(ctx)


def write_backup_pdf(ctx=None):
    ctx = ctx or load_ctx()
    year = ctx["year"]
    from reportlab.lib.pagesizes import landscape
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader

    page = landscape((13.333 * inch, 7.5 * inch))
    c = canvas.Canvas(str(PDF), pagesize=page)
    width, height = page

    def band(title):
        c.setFillColorRGB(0.10, 0.48, 0.43)
        c.rect(0, height - 0.1 * inch, width, 0.1 * inch, fill=1, stroke=0)
        c.setFillColorRGB(0.12, 0.16, 0.22)
        c.setFont("Helvetica-Bold", 18)
        c.drawString(0.45 * inch, height - 0.5 * inch, title)
        c.setFillColorRGB(0.35, 0.40, 0.45)
        c.setFont("Helvetica", 8)
        c.drawString(0.45 * inch, 0.25 * inch, SOURCE_SHORT + "  |  " + SOURCE_URL)

    def draw_img(path: Path, x, y, max_w, max_h):
        if not path.is_file():
            return
        img = ImageReader(str(path))
        iw, ih = img.getSize()
        scale = min(max_w / iw, max_h / ih)
        w, h = iw * scale, ih * scale
        c.drawImage(img, x, y, width=w, height=h, preserveAspectRatio=True, mask="auto")

    def text_block(lines, x, y, size=11, leading=16, color=(0.12, 0.16, 0.22)):
        c.setFillColorRGB(*color)
        c.setFont("Helvetica", size)
        yy = y
        for line in lines:
            c.drawString(x, yy, line)
            yy -= leading
        return yy

    # 1 Cover
    c.setFillColorRGB(0.91, 0.95, 0.94)
    c.rect(0, height - 3.0 * inch, width, 3.0 * inch, fill=1, stroke=0)
    c.setFillColorRGB(0.12, 0.16, 0.22)
    c.setFont("Helvetica-Bold", 28)
    c.drawString(0.6 * inch, height - 1.2 * inch, "How green is Europe's electricity?")
    c.setFillColorRGB(0.10, 0.48, 0.43)
    c.setFont("Helvetica", 13)
    c.drawString(0.6 * inch, height - 1.75 * inch,
                 f"EU-27 generation mixes, lifecycle intensity, and the role of nuclear · 2010-{year}")
    text_block([
        "Scientific Visualization  |  OWID Energy dataset version 2026-09-10",
        f"Sample: {ctx['n_rows']} country-years (EU-27 x 2010-{year}); 27/27 complete in {year} for core electricity variables",
        "Intensity unit: lifecycle gCO2eq / kWh generated  |  Electricity indicators mainly Ember via OWID",
        SOURCE_URL,
    ], 0.6 * inch, height - 3.6 * inch, size=11, leading=18)
    c.showPage()

    # 2-5 diagrams
    for title, fname in [
        ("Research questions", "d02_research_questions.png"),
        ("Source and provenance", "d03_provenance.png"),
        ("Variables, units and denominators", "d04_variables.png"),
        ("Cleaning and methodology", "d05_pipeline.png"),
    ]:
        band(title)
        draw_img(PRESENT / fname, 0.4 * inch, 0.55 * inch, 12.5 * inch, 6.0 * inch)
        c.showPage()

    # 6 mix
    band("How Europe's electricity mix changed")
    c.setFillColorRGB(0.10, 0.48, 0.43)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(0.5 * inch, height - 0.85 * inch,
                 f"Renewables {ctx['re0']:.0f}% -> {ctx['re1']:.0f}%  |  Fossil {ctx['fo0']:.0f}% -> {ctx['fo1']:.0f}%  |  Nuclear {ctx['nu0']:.0f}% -> {ctx['nu1']:.0f}% (generation-weighted)")
    draw_img(PRESENT / "01_mix_trend_annotated.png", 0.35 * inch, 0.7 * inch, 9.0 * inch, 5.5 * inch)
    c.setFillColorRGB(0.95, 0.97, 0.98)
    c.roundRect(9.6 * inch, 3.6 * inch, 3.3 * inch, 2.3 * inch, 8, fill=1, stroke=0)
    text_block([
        "Notice",
        "RE overtook fossil ~2020.",
        "Nuclear declined slowly",
        "but remains material.",
        "",
        "Weighted by TWh.",
    ], 9.8 * inch, 5.55 * inch, size=10, leading=14)
    c.showPage()

    # 7 intensity
    band("Carbon intensity through time")
    c.setFont("Helvetica-Bold", 11)
    c.setFillColorRGB(0.10, 0.48, 0.43)
    c.drawString(0.5 * inch, height - 0.85 * inch,
                 f"Lifecycle intensity {ctx['int0']:.0f} -> {ctx['int1']:.0f} gCO2eq/kWh (2010->{year}), with 2021-22 rebound")
    draw_img(PRESENT / "02_carbon_intensity_annotated.png", 0.35 * inch, 0.7 * inch, 9.0 * inch, 5.5 * inch)
    c.setFillColorRGB(0.95, 0.97, 0.98)
    c.roundRect(9.6 * inch, 3.4 * inch, 3.3 * inch, 2.5 * inch, 8, fill=1, stroke=0)
    text_block([
        "Notice",
        f"~{100 * (1 - ctx['int1'] / ctx['int0']):.0f}% lower by {year}.",
        "2022 rebound ~292.",
        "",
        "Caveat: generation",
        "!= consumption/imports.",
    ], 9.8 * inch, 5.55 * inch, size=10, leading=14)
    c.showPage()

    # 8 ranking
    band(f"Leaders and laggards · {year}")
    draw_img(PRESENT / "03_low_carbon_ranking_present.png", 0.3 * inch, 0.55 * inch, 8.5 * inch, 6.2 * inch)
    c.setFillColorRGB(0.95, 0.97, 0.98)
    c.roundRect(9.1 * inch, 3.2 * inch, 3.7 * inch, 3.0 * inch, 8, fill=1, stroke=0)
    text_block([
        "Notice",
        "Sweden ~99%, France ~95%,",
        "Denmark ~89%.",
        "Poland, Cyprus, Malta lag.",
        "",
        "Full chart also in",
        "figures/03_...png",
    ], 9.3 * inch, 5.85 * inch, size=10, leading=14)
    c.showPage()

    # 9 pathways
    band("Three pathways to electricity generation")
    draw_img(PRESENT / "06_electricity_mix_spotlight.png", 0.35 * inch, 0.7 * inch, 9.0 * inch, 5.7 * inch)
    c.setFillColorRGB(0.95, 0.97, 0.98)
    c.roundRect(9.55 * inch, 3.3 * inch, 3.35 * inch, 2.8 * inch, 8, fill=1, stroke=0)
    text_block([
        "Notice",
        "Low fossil can mean",
        "RE-led (DK) or",
        "nuclear-led (FR).",
        "",
        "Full EU-27 mix:",
        "figures/06_...png",
    ], 9.75 * inch, 5.75 * inch, size=10, leading=14)
    c.showPage()

    # 10 renewables story
    band("Story beat 1 · Are renewables enough?")
    c.setFillColorRGB(0.95, 0.97, 0.98)
    c.roundRect(0.4 * inch, 0.7 * inch, 4.0 * inch, 5.8 * inch, 10, fill=1, stroke=0)
    text_block([
        "Renewables only",
        "",
        f"Spearman rho = {ctx['rho_re']:.2f}",
        f"p = {ctx['p_re']:.3g}",
        f"n = 27 ({year})",
        "",
        "Moderate association.",
        "France: low RE share,",
        "very low intensity.",
        "Poland: high intensity.",
        "",
        "Not causal.",
    ], 0.65 * inch, 6.1 * inch, size=12, leading=18)
    draw_img(FIG / "04_renewables_vs_intensity.png", 4.6 * inch, 0.7 * inch, 8.3 * inch, 5.8 * inch)
    c.showPage()

    # 11 low-carbon story
    band("Story beat 2 · What changes when nuclear is included?")
    c.setFillColorRGB(0.95, 0.97, 0.98)
    c.roundRect(0.4 * inch, 0.7 * inch, 4.0 * inch, 5.8 * inch, 10, fill=1, stroke=0)
    text_block([
        "Low-carbon = RE + nuclear",
        "",
        f"Spearman rho = {ctx['rho_lc']:.2f}",
        f"p = {ctx['p_lc']:.3g}",
        f"n = 27 ({year})",
        "",
        f"|rho| jumps {abs(ctx['rho_re']):.2f} -> {abs(ctx['rho_lc']):.2f}.",
        "Nuclear closes the gap",
        "for FR / SK pathways.",
        "",
        "Still descriptive.",
    ], 0.65 * inch, 6.1 * inch, size=12, leading=18)
    draw_img(FIG / "05_lowcarbon_vs_intensity.png", 4.6 * inch, 0.7 * inch, 8.3 * inch, 5.8 * inch)
    c.showPage()

    # Combined comparison page? User wanted 13 slides - we stick to 13. PDF mirrors PPTX.

    # 12 clustering
    band("Country profiles · exploratory K-means + PCA")
    c.setFillColorRGB(0.72, 0.44, 0.31)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(0.5 * inch, height - 0.85 * inch,
                 f"Best k={ctx['k']} but silhouette={ctx['sil']:.2f} (WEAK)  |  PCA 2D ~{100*ctx['pca']:.0f}% variance  |  exploratory only")
    draw_img(FIG / "07_country_clusters_pca.png", 0.4 * inch, 0.65 * inch, 8.8 * inch, 5.7 * inch)
    c.setFillColorRGB(0.95, 0.97, 0.98)
    c.roundRect(9.4 * inch, 3.2 * inch, 3.5 * inch, 3.0 * inch, 8, fill=1, stroke=0)
    text_block([
        "Weak separation",
        "Silhouette ~0.30 for",
        "all k in 2..5.",
        "",
        "Visual aid only —",
        "not natural regimes.",
    ], 9.6 * inch, 5.85 * inch, size=10, leading=14)
    c.showPage()

    # 13 conclusions
    band("Conclusions, limitations & sources")
    text_block([
        f"1. EU mix transition: RE {ctx['re0']:.0f}->{ctx['re1']:.0f}%, fossil {ctx['fo0']:.0f}->{ctx['fo1']:.0f}%, intensity {ctx['int0']:.0f}->{ctx['int1']:.0f} gCO2eq/kWh (2010-{year}).",
        "2. Divergent pathways: renewables-led, nuclear-led, or both among low-carbon leaders.",
        f"3. Nuclear in the story: rho {ctx['rho_re']:.2f} (RE) vs {ctx['rho_lc']:.2f} (low-carbon); descriptive, not causal.",
        "",
        "Limitations: no causality; generation != consumption/imports; lifecycle != stack-only CO2;",
        "clustering silhouette 0.30 = weak separation.",
        "",
        "Source: Our World in Data Energy version 2026-09-10 (electricity mainly Ember).",
        SOURCE_URL,
        f"Reproducibility: python analysis.py --year {year}  |  outputs/verified_findings.md",
        "Full EU-27 charts retained in outputs/figures/; presentation variants in figures/present/.",
    ], 0.55 * inch, height - 1.2 * inch, size=11, leading=18)
    c.showPage()
    c.save()
    print(f"Wrote {PDF}")


if __name__ == "__main__":
    build()
