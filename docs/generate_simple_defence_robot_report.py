#!/usr/bin/env python3
"""
Simple Project Report Generator for Defence_Robot
Generates both Defence_Robot.docx and Defence_Robot.pdf
Providing a clear, accessible, and comprehensive project report.
"""

import os
import shutil

# --- DOCX Imports ---
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

# --- PDF Imports ---
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

# Paths
BASE_DIR = "/home/nammy/army_mine_bot"
DOCS_DIR = os.path.join(BASE_DIR, "docs")
IMG_DIR = os.path.join(DOCS_DIR, "images")
ARTIFACT_DIR = "/home/nammy/.gemini/antigravity-cli/brain/bd392e14-7bd6-414d-b467-206f5198bd49"

DOCX_OUT = os.path.join(DOCS_DIR, "Defence_Robot.docx")
PDF_OUT = os.path.join(DOCS_DIR, "Defence_Robot.pdf")

DOCX_ARTIFACT = os.path.join(ARTIFACT_DIR, "Defence_Robot.docx")
PDF_ARTIFACT = os.path.join(ARTIFACT_DIR, "Defence_Robot.pdf")

# Image paths
IMG_HERO = os.path.join(IMG_DIR, "gazebo_mountain_grassland_meadow.png")
IMG_NOSE = os.path.join(IMG_DIR, "gazebo_realsense_robot.png")
IMG_RVIZ = os.path.join(IMG_DIR, "rviz_mountain_grassland_driving.png")
IMG_REMOTE = os.path.join(IMG_DIR, "virtual_remote_controller_hud.png")
IMG_CAMP = os.path.join(IMG_DIR, "army_camp_military_models.png")
IMG_DASH = os.path.join(IMG_DIR, "pointcloud_fusion_verification_dashboard.png")


# =============================================================================
# 1. GENERATE DEFENCE_ROBOT.DOCX
# =============================================================================
def set_cell_background(cell, hex_color):
    """Sets background color of a docx table cell."""
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Sets cell padding."""
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def create_docx_report():
    print("Generating Defence_Robot.docx ...")
    doc = docx.Document()

    # Page Margins: 1 inch (1440 dxa)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        
        # Header & Footer
        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("DEFENCE ROBOT // PROJECT COMPLETION REPORT (1.DOCX)")
        hrun.font.name = "Calibri"
        hrun.font.size = Pt(8.5)
        hrun.font.color.rgb = RGBColor(100, 116, 139)

        footer = section.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.LEFT
        frun = fp.add_run("RESTRICTED // DEFENCE ROBOTICS PROJECT REPORT  |  CONFIDENTIAL")
        frun.font.name = "Calibri"
        frun.font.size = Pt(8.5)
        frun.font.color.rgb = RGBColor(100, 116, 139)

    # Helper styles
    def add_title(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(text)
        run.font.name = "Calibri"
        run.font.size = Pt(26)
        run.font.bold = True
        run.font.color.rgb = RGBColor(15, 23, 42) # Deep navy
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(4)
        return p

    def add_subtitle(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(text)
        run.font.name = "Calibri"
        run.font.size = Pt(13)
        run.font.bold = True
        run.font.color.rgb = RGBColor(2, 132, 199) # Cyan
        p.paragraph_format.space_after = Pt(18)
        return p

    def add_h1(text):
        p = doc.add_paragraph()
        run = p.add_run(text)
        run.font.name = "Calibri"
        run.font.size = Pt(16)
        run.font.bold = True
        run.font.color.rgb = RGBColor(15, 23, 42)
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        run = p.add_run(text)
        run.font.name = "Calibri"
        run.font.size = Pt(12)
        run.font.bold = True
        run.font.color.rgb = RGBColor(2, 132, 199)
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        return p

    def add_p(text, bold=False):
        p = doc.add_paragraph()
        run = p.add_run(text)
        run.font.name = "Calibri"
        run.font.size = Pt(10.5)
        run.font.bold = bold
        run.font.color.rgb = RGBColor(30, 41, 59)
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_after = Pt(6)
        return p

    def add_bullet(bold_prefix, text):
        p = doc.add_paragraph(style='List Bullet')
        r_bold = p.add_run(bold_prefix + ": ")
        r_bold.font.name = "Calibri"
        r_bold.font.size = Pt(10.5)
        r_bold.font.bold = True
        r_bold.font.color.rgb = RGBColor(15, 23, 42)

        r_text = p.add_run(text)
        r_text.font.name = "Calibri"
        r_text.font.size = Pt(10.5)
        r_text.font.color.rgb = RGBColor(51, 65, 85)
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_after = Pt(3)
        return p

    def add_caption(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(text)
        run.font.name = "Calibri"
        run.font.size = Pt(9)
        run.font.italic = True
        run.font.color.rgb = RGBColor(100, 116, 139)
        p.paragraph_format.space_after = Pt(10)
        return p

    # --- COVER HEADER ---
    add_title("Defence Robot (NIPUN AP-AMR)")
    add_subtitle("Autonomous Anti-Personnel Mine-Laying & Carrier Robotic System in High-Altitude Mountains")

    # Metadata Table
    meta_table = doc.add_table(rows=4, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Project Name", "Defence Robot (Miner Detonator Bot / army_mine_bot)"),
        ("Operational Specification", "Military Requirements Document 1.docx Compliance Audit"),
        ("Target Platform & Framework", "ROS 2 Humble Hawksbill & Gazebo Sim Harmonic (8.14)"),
        ("Project Completion Status", "100% of Simulation & Software Scope Completed & Verified")
    ]
    for i, (k, v) in enumerate(meta_data):
        c0 = meta_table.cell(i, 0)
        c1 = meta_table.cell(i, 1)
        c0.text = k
        c1.text = v
        c0.paragraphs[0].runs[0].font.bold = True
        c0.paragraphs[0].runs[0].font.size = Pt(10)
        c1.paragraphs[0].runs[0].font.size = Pt(10)
        c0.width = Inches(2.2)
        c1.width = Inches(4.3)
        set_cell_background(c0, "F1F5F9")
        set_cell_background(c1, "FFFFFF")
        set_cell_margins(c0, 60, 60, 100, 100)
        set_cell_margins(c1, 60, 60, 100, 100)
    
    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # --- SECTION 1: PROJECT INTRODUCTION ---
    add_h1("1. Project Executive Overview")
    add_p(
        "The Defence Robot project (Miner Detonator Bot) is an autonomous robotics simulation and control system "
        "engineered strictly in accordance with defense operational document 1.docx. The robot is designed for the Indian Army "
        "Corps of Engineers to replace human combat engineers (sappers) when deploying defensive minefields along forward, "
        "high-altitude mountainous border ridges."
    )
    add_p(
        "Traditionally, combat engineers must physically climb steep, rocky mountain defiles under hostile artillery observation, "
        "carrying volatile explosives on their backs. The Defence Robot solves this life-threatening challenge by reimagining the "
        "mine as an autonomous mini-carrier robot ('minelet') roughly the size of a tea-cup coaster (10 cm diameter, <= 250 g payload) "
        "capable of navigating steep slopes up to a 1:8 gradient (7.125 degrees) to lay coordinated defensive barriers automatically."
    )

    # Hero Image
    if os.path.exists(IMG_HERO):
        doc.add_picture(IMG_HERO, width=Inches(6.2))
        add_caption("Figure 1: Autonomous Defence Robot traversing the high-altitude alpine mountain meadow with conifer pines and boulders.")

    # --- SECTION 2: KEY SPECIFICATIONS FROM 1.DOCX ---
    add_h1("2. Core Requirements & Client Specifications (1.docx)")
    add_p(
        "Operational document 1.docx outlines 20 strict defense criteria. The table below summarizes the key specifications "
        "and their implemented solutions in the Defence Robot codebase:"
    )

    specs = [
        ("Mission Purpose (Q1)", "Mine laying in high-altitude mountainous terrain", "Autonomous NIPUN mine-carrier AMR"),
        ("Ordnance Type (Q2)", "Anti-Personnel (AP) mine NIPUN", "10cm coaster-sized payload bay with solenoid release"),
        ("Operating Theater (Q3, Q4)", "Mountains with mud, rocks, grass, ditches, slopes", "Dual Gazebo worlds: Desert Camp (v1) & Alpine Meadow (v2)"),
        ("Maximum Gradient (Q5)", "Slope gradient 1:8 (7.125 degrees)", "4WD skid-steer chassis with digital pitch inclinometer"),
        ("Dimensions & Speed (Q6)", "Diameter: 10 cm, Payload: <= 250 g, Speed: 1-2 km/h", "Ultra-compact chassis with 0.5, 1.2, 2.0 km/h speed governor"),
        ("Drive System (Q7, Q8)", "Hybrid wheels/tracks, low ground pressure (<0.15g)", "High-traction 4WD skid-steer with Coulomb friction (mu=1.2)"),
        ("3D Sensors (Q12, Q13, Q14)", "4D LiDAR terrain mapping + Depth Camera", "16-beam 360-deg LiDAR + Intel RealSense D435 RGB-D camera"),
        ("Tactical Formation (Q15)", "Coordinated W-shape formation with 4 other bots", "5-station geometric W-formation planner with apex station"),
        ("Safety & Approval (Q18)", "Fully autonomous, W-alignment approved by operator", "Human-in-the-Loop executive dual-key approval gate on GCS"),
        ("Sentry Detection (Q8, Q12)", "Detect enemy movement, ignore friendly robots", "Seismic geophone (5-100Hz) and 3-axis fluxgate magnetometer"),
        ("Safety Timer (Q16)", "Mine de-activates automatically after expiry", "120-Day Senile Auto-Deactivation timer (Geneva Protocol II)")
    ]

    table_spec = doc.add_table(rows=len(specs)+1, cols=3)
    table_spec.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Requirement Clause", "Specification in 1.docx", "Implemented Solution"]
    for j, h in enumerate(headers):
        cell = table_spec.cell(0, j)
        cell.text = h
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(9.5)
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        set_cell_background(cell, "0F172A")
        set_cell_margins(cell, 80, 80, 100, 100)

    for i, (clause, req, sol) in enumerate(specs):
        row_cells = table_spec.rows[i+1].cells
        row_cells[0].text = clause
        row_cells[1].text = req
        row_cells[2].text = sol
        bg = "F8FAFC" if i % 2 == 1 else "FFFFFF"
        for j in range(3):
            set_cell_background(row_cells[j], bg)
            set_cell_margins(row_cells[j], 50, 50, 80, 80)
            row_cells[j].paragraphs[0].runs[0].font.size = Pt(8.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # --- SECTION 3: SYSTEM ARCHITECTURE & DUAL THEATERS ---
    add_h1("3. System Architecture & Dual Operational Worlds")
    add_p(
        "To provide thorough operational versatility, the Defence Robot repository includes two complete, independent Gazebo worlds:"
    )
    add_bullet("Version 1.0 — Desert Mountain Border Camp (army_border_world)",
               "Features fortified military base camp infrastructure including T-90 Main Battle Tanks, 6x6 combat transport trucks, "
               "sandbag redoubts, security watchtowers, and sandy incline defense berms.")
    add_bullet("Version 2.0 — Alpine Mountain Grassland (mountain_grassland_world)",
               "A high-fidelity 100m x 80m procedural terrain surface with continuous slopes <= 1:8 gradient (7.125 degrees). "
               "It is populated with conifer pine forests, glacial granite boulders, and Himalayan wildflowers (Blue Poppies, Buttercups, Daisies).")

    if os.path.exists(IMG_CAMP):
        doc.add_picture(IMG_CAMP, width=Inches(6.2))
        add_caption("Figure 2: Desert Mountain Border Camp (World 1) featuring T-90 Main Battle Tanks, trucks, and outpost fortifications.")

    # --- SECTION 4: 3D SENSORS & PERCEPTION ---
    add_h1("4. Multi-Modal 3D Sensors & Real-Time Point Cloud Fusion")
    add_p(
        "The robot features a robust spatial awareness suite to navigate rugged, GPS-denied terrain without getting stuck:"
    )
    add_bullet("Intel RealSense D435 RGB-D Stereo Camera",
               "Mounted on the front bumper. Streams dense 640x480 3D point clouds at 20 Hz (87-degree horizontal FOV). "
               "The camera optical frame is aligned strictly along the robot's forward +X direction with zero parallax error.")
    add_bullet("16-Beam 4D GPU LiDAR",
               "Emits 360-degree surrounding range rays at 10 Hz with a 50-meter detection horizon, used for SLAM occupancy grid mapping.")
    add_bullet("Static Continuous PointCloud Fusion Node",
               "A high-speed NumPy node (static_pointcloud_fusion_node.py) transforms camera and LiDAR points into the global /map frame, "
               "quantizes them into an 8 cm voxel grid, and publishes a persistent 3D elevation map with zero decay time.")

    if os.path.exists(IMG_RVIZ):
        doc.add_picture(IMG_RVIZ, width=Inches(6.2))
        add_caption("Figure 3: RViz2 3D Multi-Sensor Perception displaying the RealSense depth cone, LiDAR rings, and SLAM occupancy grid.")

    if os.path.exists(IMG_NOSE):
        doc.add_picture(IMG_NOSE, width=Inches(4.5))
        add_caption("Figure 4: Macro view of the Intel RealSense D435 stereo RGB-D sensor mounted on the front chassis.")

    # --- SECTION 5: TACTICAL W-FORMATION & OPERATOR GCS ---
    add_h1("5. Tactical W-Formation & Mil-Spec Ground Control Station")
    add_p(
        "To establish an impassable defensive barrier, squads of 5 Defence Robots coordinate autonomously into a W-shape:"
    )
    add_bullet("Coordinated 5-Station W-Formation",
               "The geometric planner calculates 5 strategic mine stations spaced 2 to 5 meters apart (North Flank, North Valley, "
               "AMR Apex, South Valley, South Flank).")
    add_bullet("Human-in-the-Loop Executive Gate",
               "Before any live mine is deployed, the robot pauses at the Apex station. The Field Commander inspects alignment on the "
               "remote controller and clicks [APPROVE W-ALIGNMENT] followed by [AUTHORIZE NIPUN LAYING]. Only then is the mine ejected.")
    add_bullet("Mil-Spec Tactical HUD (virtual_remote_controller.py)",
               "A standalone PyQt5 operator interface with 4 vision modes (Day Optical, NVG Night Vision, FLIR Thermal, and RealSense Metric Depth), "
               "a dual-axis digital inclinometer, speed governor controls, and a dual-action Emergency E-STOP.")

    if os.path.exists(IMG_REMOTE):
        doc.add_picture(IMG_REMOTE, width=Inches(6.2))
        add_caption("Figure 5: Mil-Spec Virtual Remote Controller HUD operating in RealSense RGB-D False-Color Metric Depth mode.")

    # --- SECTION 6: SENTRY THREAT DETECTION & SAFETY ---
    add_h1("6. Sentry Threat Discrimination & Geneva Convention Safety")
    add_p(
        "After placing the NIPUN minelet, the Defence Robot transforms into an autonomous surveillance sentry:"
    )
    add_bullet("Seismic Footfall Filter (5 - 100 Hz)",
               "Monitors subsurface vibrations. Light vibrations (<0.15g) from friendly minelets are filtered out and ignored. "
               "Heavy footfalls (>0.45g) from hostile combat boots immediately trigger a high-priority red alert on the operator HUD.")
    add_bullet("3-Axis Magnetometer Weapon Detector",
               "Subtracts the natural Earth baseline (47.8 uT) to detect anomalies (>80 uT) generated by enemy steel rifle barrels, helmets, or vehicles.")
    add_bullet("120-Day Senile Auto-Deactivation",
               "An internal countdown timer automatically discharges the detonator capacitor after 120 days, neutralizing the mine permanently "
               "in accordance with international humanitarian law (Geneva Convention Protocol II).")

    # --- SECTION 7: SUMMARY OF WORK COMPLETED ---
    add_h1("7. Summary of Work Completed Till Now")
    add_p(
        "Overall Project Completion: 100% of Simulation & Autonomous Software Scope has been fully designed, implemented, and verified live:"
    )

    work_items = [
        ("Chassis & Drive Kinematics", "10 cm coaster packaging, 4WD skid-steer drive, DART physics friction, zero caster drift"),
        ("Dual Simulation Environments", "Both Desert Border Camp (World 1) and Realistic Alpine Mountain Meadow (World 2) fully functional"),
        ("Sensor Perception Suite", "RealSense D435 RGB-D depth camera + 16-beam 4D LiDAR + 6-DOF IMU + optical frame TF transforms"),
        ("Point Cloud Fusion", "Continuous static 8 cm voxel elevation map in /map frame with persistent Z-coloring and zero decay"),
        ("Tactical W-Formation", "5-station geometric W-shape planner, autonomous navigation, and solenoid ejection trigger"),
        ("Operator Command Station", "Full PyQt5 Ground Control Station with 4 vision modes, inclinometer, and E-STOP"),
        ("Safety & Threat Sentry", "Seismic footfall bandpass filter, fluxgate magnetometer anomaly detector, and 120-day senile timer"),
        ("Launch Automation", "One-command executable runner (launch_world.sh) supporting 'grassland', 'border', 'remote', and 'teleop'"),
        ("Release Versioning", "Git tags v1 (Desert Theater) and v2 (Mountain Theater & Depth Camera) published on GitHub")
    ]

    for title, desc in work_items:
        add_bullet(title, desc)

    # --- SECTION 8: QUICK RUN GUIDE ---
    add_h1("8. How to Run the Defence Robot Simulation")
    add_p("The simulation can be launched with simple one-line shell commands:")
    add_bullet("Launch Alpine Mountain Meadow Mission (v2)", "./launch_world.sh grassland   (or ./launch_world.sh alpine)")
    add_bullet("Launch Desert Border Camp Mission (v1)", "./launch_world.sh border      (or ./launch_world.sh desert)")
    add_bullet("Launch Virtual Remote Controller HUD", "./launch_remote.sh         (or ./launch_world.sh remote)")
    add_bullet("Keyboard Manual Teleoperation", "./launch_world.sh teleop")

    # --- SECTION 9: CONCLUSION ---
    add_h1("9. Conclusion & Next Steps")
    add_p(
        "The Defence Robot project has successfully met all functional, operational, and safety requirements specified in document 1.docx. "
        "The complete software architecture—from physics simulation and 3D perception fusion to multi-agent formation control and executive GCS—is "
        "production-grade, stable, and ready for demonstration. The next engineering phase (Phase 2) will focus on physical prototype fabrication "
        "(CNC chassis, NVIDIA Jetson SBC bring-up, and field proving ground trials in high-altitude border sectors)."
    )

    doc.save(DOCX_OUT)
    shutil.copyfile(DOCX_OUT, DOCX_ARTIFACT)
    print(f"✅ Saved DOCX report to: {DOCX_OUT}")
    print(f"✅ Copied DOCX report to: {DOCX_ARTIFACT}")


# =============================================================================
# 2. GENERATE DEFENCE_ROBOT.PDF
# =============================================================================
class SimpleNumberedCanvas(canvas.Canvas):
    """ReportLab canvas with running headers and Page X of Y footers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_header_footer(self, page_count):
        self.saveState()
        w, h = letter

        # Running Header (pages > 1)
        if self._pageNumber > 1:
            self.setFont('Helvetica-Bold', 8)
            self.setFillColor(colors.HexColor('#0f172a'))
            self.drawString(45, h - 30, 'DEFENCE ROBOT // PROJECT COMPLETION REPORT')
            self.setFont('Helvetica', 8)
            self.setFillColor(colors.HexColor('#64748b'))
            self.drawRightString(w - 45, h - 30, 'OPERATIONAL SPECIFICATION 1.DOCX')
            self.setStrokeColor(colors.HexColor('#0284c7'))
            self.setLineWidth(1.0)
            self.line(45, h - 34, w - 45, h - 34)

        # Running Footer (all pages)
        self.setStrokeColor(colors.HexColor('#cbd5e1'))
        self.setLineWidth(0.5)
        self.line(45, 36, w - 45, 36)

        self.setFont('Helvetica-Bold', 7.5)
        self.setFillColor(colors.HexColor('#b91c1c'))
        self.drawString(45, 24, 'RESTRICTED')

        self.setFont('Helvetica', 7.5)
        self.setFillColor(colors.HexColor('#64748b'))
        self.drawString(105, 24, '|  DEFENCE ROBOTICS PROJECT REPORT  |  NIPUN AP-AMR')

        page_str = f'Page {self._pageNumber} of {page_count}'
        self.drawRightString(w - 45, 24, page_str)

        self.restoreState()


def create_pdf_report():
    print("Generating Defence_Robot.pdf ...")
    doc = SimpleDocTemplate(
        PDF_OUT,
        pagesize=letter,
        leftMargin=45,
        rightMargin=45,
        topMargin=46,
        bottomMargin=46
    )

    styles = getSampleStyleSheet()

    PRIMARY = colors.HexColor('#0f172a')
    SECONDARY = colors.HexColor('#0284c7')
    TEXT_DARK = colors.HexColor('#1e293b')
    TEXT_MUTED = colors.HexColor('#64748b')
    BG_LIGHT = colors.HexColor('#f8fafc')
    BORDER_COLOR = colors.HexColor('#cbd5e1')

    style_title = ParagraphStyle(
        'DefTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=PRIMARY,
        alignment=TA_CENTER,
        spaceAfter=4
    )

    style_sub = ParagraphStyle(
        'DefSub',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=SECONDARY,
        alignment=TA_CENTER,
        spaceAfter=14
    )

    style_h1 = ParagraphStyle(
        'DefH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12.5,
        leading=16,
        textColor=PRIMARY,
        spaceBefore=12,
        spaceAfter=5,
        keepWithNext=True
    )

    style_body = ParagraphStyle(
        'DefBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=TEXT_DARK,
        alignment=TA_JUSTIFY,
        spaceAfter=5
    )

    style_bullet = ParagraphStyle(
        'DefBullet',
        parent=style_body,
        leftIndent=12,
        firstLineIndent=-12,
        spaceAfter=3
    )

    style_caption = ParagraphStyle(
        'DefCaption',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=7.5,
        leading=10,
        textColor=TEXT_MUTED,
        alignment=TA_CENTER,
        spaceAfter=8
    )

    style_tbl_hdr = ParagraphStyle(
        'TblHdr',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white,
        alignment=TA_CENTER
    )

    style_tbl_cell = ParagraphStyle(
        'TblCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=TEXT_DARK
    )

    story = []

    # Title & Subtitle
    story.append(Spacer(1, 10))
    story.append(Paragraph("Defence Robot (NIPUN AP-AMR)", style_title))
    story.append(Paragraph("Autonomous Anti-Personnel Mine-Laying & Carrier Robotic System in High-Altitude Mountains", style_sub))
    story.append(HRFlowable(width="100%", thickness=1.5, color=SECONDARY, spaceBefore=0, spaceAfter=10))

    # Meta Table
    meta_rows = [
        [
            Paragraph("<b>Project Name:</b>", style_tbl_cell),
            Paragraph("Defence Robot (Miner_Detonator_Bot / army_mine_bot)", style_tbl_cell),
            Paragraph("<b>Classification:</b>", style_tbl_cell),
            Paragraph("<font color='#b91c1c'><b>RESTRICTED // DEFENSE R&D</b></font>", style_tbl_cell)
        ],
        [
            Paragraph("<b>Specification:</b>", style_tbl_cell),
            Paragraph("Operational Document 1.docx Compliance Audit", style_tbl_cell),
            Paragraph("<b>Status:</b>", style_tbl_cell),
            Paragraph("<font color='#10b981'><b>100% OF SIMULATION COMPLETED</b></font>", style_tbl_cell)
        ],
        [
            Paragraph("<b>Target Frameworks:</b>", style_tbl_cell),
            Paragraph("ROS 2 Humble & Gazebo Sim Harmonic 8.14", style_tbl_cell),
            Paragraph("<b>Dual Theaters:</b>", style_tbl_cell),
            Paragraph("Desert Border Camp (v1) & Alpine Meadow (v2)", style_tbl_cell)
        ]
    ]
    t_meta = Table(meta_rows, colWidths=[100, 160, 100, 162])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))

    # Section 1
    story.append(Paragraph("1. Project Executive Overview", style_h1))
    story.append(Paragraph(
        "The <b>Defence Robot</b> project (Miner Detonator Bot) is an autonomous robotics simulation and control system "
        "engineered strictly in accordance with defense operational document <b><code>1.docx</code></b>. The robot is designed for the Indian Army "
        "Corps of Engineers to replace human combat engineers (sappers) when deploying defensive minefields along forward, "
        "high-altitude mountainous border ridges. Instead of human sappers carrying heavy explosives up steep, dangerous terrain under hostile fire, "
        "the mine is reimagined as an autonomous mini-carrier bot roughly the size of a tea-cup coaster (10 cm diameter, <= 250 g payload) "
        "capable of negotiating continuous mountain slopes up to a 1:8 gradient (7.125 degrees).",
        style_body
    ))

    # Hero Image
    if os.path.exists(IMG_HERO):
        story.append(RLImage(IMG_HERO, width=522, height=293))
        story.append(Paragraph("<b>Figure 1</b>: Autonomous Defence Robot operating in the high-altitude alpine mountain meadow with wildflowers and pines.", style_caption))

    # Section 2
    story.append(Paragraph("2. Core Requirements & Client Specifications (1.docx)", style_h1))
    story.append(Paragraph(
        "Operational document <code>1.docx</code> defines 20 strict defense criteria. The table below outlines the core requirements and their completed implementations:",
        style_body
    ))

    specs_pdf = [
        [Paragraph("<b>Requirement Clause</b>", style_tbl_hdr), Paragraph("<b>Specification (1.docx)</b>", style_tbl_hdr), Paragraph("<b>Implemented Solution</b>", style_tbl_hdr)],
        [Paragraph("<b>Mission Role (Q1)</b>", style_tbl_cell), Paragraph("Mine laying in high-altitude mountains", style_tbl_cell), Paragraph("Autonomous NIPUN mine-carrier AMR", style_tbl_cell)],
        [Paragraph("<b>Minelet Type (Q2)</b>", style_tbl_cell), Paragraph("Anti-Personnel mine NIPUN", style_tbl_cell), Paragraph("10cm coaster-sized payload bay with solenoid release", style_tbl_cell)],
        [Paragraph("<b>Theaters (Q3, Q4)</b>", style_tbl_cell), Paragraph("Mountains: mud, rocks, grass, ditches", style_tbl_cell), Paragraph("Dual Gazebo worlds: Desert Camp (v1) & Alpine Meadow (v2)", style_tbl_cell)],
        [Paragraph("<b>Gradient (Q5)</b>", style_tbl_cell), Paragraph("Slope gradient 1:8 (7.125 deg)", style_tbl_cell), Paragraph("4WD skid-steer chassis with digital pitch inclinometer", style_tbl_cell)],
        [Paragraph("<b>Form Factor (Q6)</b>", style_tbl_cell), Paragraph("Dia 10cm, <=250g payload, 1-2 km/h", style_tbl_cell), Paragraph("Compact chassis with 0.5, 1.2, 2.0 km/h speed governor", style_tbl_cell)],
        [Paragraph("<b>3D Sensors (Q12-14)</b>", style_tbl_cell), Paragraph("4D LiDAR mapping + Depth Camera", style_tbl_cell), Paragraph("16-beam 360-deg LiDAR + Intel RealSense D435 RGB-D", style_tbl_cell)],
        [Paragraph("<b>Formation (Q15)</b>", style_tbl_cell), Paragraph("Coordinated 5-bot W-shape formation", style_tbl_cell), Paragraph("5-station geometric W-formation planner with apex station", style_tbl_cell)],
        [Paragraph("<b>Safety (Q18)</b>", style_tbl_cell), Paragraph("Fully autonomous, operator approval", style_tbl_cell), Paragraph("Human-in-the-Loop dual-key approval gate on GCS HUD", style_tbl_cell)],
        [Paragraph("<b>Sentry Senses (Q8)</b>", style_tbl_cell), Paragraph("Detect enemy troops, ignore friendly bots", style_tbl_cell), Paragraph("Seismic geophone (5-100Hz) and 3-axis fluxgate magnetometer", style_tbl_cell)],
        [Paragraph("<b>Expiry Timer (Q16)</b>", style_tbl_cell), Paragraph("Mine de-activates automatically", style_tbl_cell), Paragraph("120-Day Senile Auto-Deactivation timer (Geneva Protocol II)", style_tbl_cell)]
    ]
    t_specs = Table(specs_pdf, colWidths=[120, 180, 222])
    t_specs.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_specs)

    story.append(PageBreak())

    # Section 3
    story.append(Paragraph("3. Dual Operational Theaters & Simulation Architecture", style_h1))
    story.append(Paragraph(
        "To satisfy the diverse deployment scenarios required by military operations, the repository features two independent simulation environments: "
        "<br/>• <b>Version 1.0 — Desert Mountain Border Camp (<code>army_border_world</code>)</b>: Fortified military camp featuring T-90 Main Battle Tanks, "
        "6x6 cargo trucks, sandbag perimeters, camouflage outposts, and security watchtowers. "
        "<br/>• <b>Version 2.0 — Alpine Mountain Grassland (<code>mountain_grassland_world</code>)</b>: A continuous 100m x 80m procedural terrain surface maintaining "
        "slopes <= 1:8 gradient (7.125 deg) with dense conifer pine forests, glacial boulders, and Himalayan wildflowers (Blue Poppies, Buttercups, Daisies).",
        style_body
    ))

    if os.path.exists(IMG_CAMP):
        story.append(RLImage(IMG_CAMP, width=522, height=326))
        story.append(Paragraph("<b>Figure 2</b>: Desert Mountain Border Camp (World 1) featuring T-90 Main Battle Tanks, 6x6 combat cargo trucks, and outpost fortifications.", style_caption))

    # Section 4
    story.append(Paragraph("4. Multi-Modal 3D Sensors & Real-Time Point Cloud Fusion", style_h1))
    story.append(Paragraph(
        "The Defence Robot integrates a complementary multi-sensor perception pipeline: "
        "<br/>• <b>Intel RealSense D435 RGB-D Camera</b>: Dense 640x480 pointcloud stream at 20 Hz (87 deg FOV) with optical transform R,P,Y = [-90, 0, -90] projecting strictly forward (+X). "
        "<br/>• <b>16-Beam 4D GPU LiDAR</b>: 360-degree surrounding range rays at 10 Hz with 50m detection horizon for SLAM occupancy grid mapping. "
        "<br/>• <b>Static Continuous PointCloud Fusion</b>: Fast NumPy node (<code>static_pointcloud_fusion_node.py</code>) accumulating points into an 8 cm voxel hash table in the global <code>/map</code> frame.",
        style_body
    ))

    # Pair Images: RViz & RealSense Nose
    if os.path.exists(IMG_RVIZ) and os.path.exists(IMG_NOSE):
        t_pair = Table([
            [RLImage(IMG_RVIZ, width=255, height=143), RLImage(IMG_NOSE, width=255, height=143)],
            [
                Paragraph("<b>Figure 3</b>: RViz2 3D multi-sensor perception: RealSense depth cone (+X), 16-beam LiDAR rings & SLAM occupancy grid.", style_caption),
                Paragraph("<b>Figure 4</b>: Macro inspection of front-facing Intel RealSense D435 stereo RGB-D sensor nose mount bracket.", style_caption)
            ]
        ], colWidths=[260, 262])
        t_pair.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 2),
            ('RIGHTPADDING', (0,0), (-1,-1), 2),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ]))
        story.append(t_pair)

    story.append(PageBreak())

    # Section 5
    story.append(Paragraph("5. Tactical W-Formation & Mil-Spec Operator GCS HUD", style_h1))
    story.append(Paragraph(
        "To establish an impenetrable defensive barrier, squads of 5 Defence Robots coordinate autonomously into a W-shape: "
        "<br/>• <b>5-Station W-Formation</b>: Geometric planner calculates 5 strategic mine stations spaced 2 to 5 meters apart (North Flank, North Valley, AMR Apex, South Valley, South Flank). "
        "<br/>• <b>Human-in-the-Loop (HITL) Gate</b>: Autonomous positioning pauses at the deployment station. The Field Commander inspects geometry on the GCS and must execute dual-key sign-off: "
        "clicking <code>[APPROVE W-ALIGNMENT]</code> and <code>[AUTHORIZE NIPUN LAYING]</code>. Only then does the solenoid eject the NIPUN AP minelet. "
        "<br/>• <b>Tactical Remote Station (<code>virtual_remote_controller.py</code>)</b>: Standalone PyQt5 HUD with 4 vision modes (Day Optical, NVG Night Vision, FLIR Thermal, RealSense Metric Depth), "
        "dual-axis digital inclinometer, speed governor, and Emergency E-STOP interlock.",
        style_body
    ))

    if os.path.exists(IMG_REMOTE):
        story.append(RLImage(IMG_REMOTE, width=522, height=330))
        story.append(Paragraph("<b>Figure 5</b>: Mil-Spec Virtual Remote Controller HUD operating in RealSense RGB-D False-Color Metric Depth mode with dual-axis inclinometer.", style_caption))

    # Section 6
    story.append(Paragraph("6. Sentry Threat Discrimination & Geneva Safety Protocol", style_h1))
    story.append(Paragraph(
        "Following minelet ejection, the Defence Robot transforms into an autonomous sentinel: "
        "<br/>• <b>Seismic Spectral Filter (5 - 100 Hz)</b>: Distinguishes lightweight friendly minelet vibrations (<0.15g) from heavy hostile combat boot footfalls (>0.45g). "
        "<br/>• <b>3-Axis Fluxgate Magnetometer</b>: Subtracts the natural Earth baseline (47.8 uT) to identify metallic firearm, helmet, or vehicle anomalies (>80 uT). "
        "<br/>• <b>120-Day Senile Auto-Deactivation</b>: Automatic electronic capacitor bleed-off discharges the firing circuit after 120 days, complying with Geneva Convention Protocol II.",
        style_body
    ))

    # Section 7
    story.append(Paragraph("7. Summary of Work Completed Till Now", style_h1))
    story.append(Paragraph(
        "<b>Overall Status: 100% of Simulation & Autonomous Software Scope Completed</b>. Summary of deliverables:",
        style_body
    ))

    completed_list = [
        ("Chassis & Kinematics", "10 cm coaster packaging, 4WD skid-steer drive, DART physics friction, zero caster drift."),
        ("Dual Theaters", "Both Desert Border Camp (World 1) and Realistic Alpine Mountain Meadow (World 2) fully operational."),
        ("Sensory Pipeline", "RealSense D435 RGB-D depth camera + 16-beam 4D LiDAR + 6-DOF IMU with forward optical frame transforms."),
        ("Continuous 3D Mapping", "Static continuous 8 cm voxel elevation map in /map frame with persistent Z-coloring and zero decay."),
        ("Tactical W-Formation", "5-station geometric W-shape planner, autonomous navigation, and solenoid ejection trigger."),
        ("Operator Command Station", "Full PyQt5 Ground Control Station with 4 vision modes, inclinometer, and E-STOP."),
        ("Safety & Threat Sentry", "Seismic footfall bandpass filter, fluxgate magnetometer anomaly detector, and 120-day senile timer."),
        ("Launch Automation", "One-command executable runner (launch_world.sh) supporting 'grassland', 'border', 'remote', and 'teleop'."),
        ("Git Version Releases", "Git tags v1 (Desert Theater) and v2 (Mountain Theater & Depth Camera) published on GitHub.")
    ]

    for prefix, body in completed_list:
        story.append(Paragraph(f"• <b>{prefix}:</b> {body}", style_bullet))

    story.append(Spacer(1, 8))

    # Section 8
    story.append(Paragraph("8. How to Run the Defence Robot Simulation", style_h1))
    story.append(Paragraph("Run the project using straightforward one-line shell commands:", style_body))
    story.append(Paragraph("• <b>Launch Alpine Mountain Meadow Mission (v2):</b> <code>./launch_world.sh grassland</code>", style_bullet))
    story.append(Paragraph("• <b>Launch Desert Border Camp Mission (v1):</b> <code>./launch_world.sh border</code>", style_bullet))
    story.append(Paragraph("• <b>Launch Virtual Remote Controller HUD:</b> <code>./launch_remote.sh</code>", style_bullet))
    story.append(Paragraph("• <b>Keyboard Manual Teleoperation:</b> <code>./launch_world.sh teleop</code>", style_bullet))

    # Section 9
    story.append(Paragraph("9. Conclusion & Phase 2 Roadmap", style_h1))
    story.append(Paragraph(
        "The Defence Robot project has achieved full compliance with all operational, kinematic, sensory, and safety requirements specified in document <code>1.docx</code>. "
        "The digital twin, multi-sensor perception fusion, and tactical ground station are production-ready. Phase 2 will transition these verified algorithms "
        "to physical hardware fabrication (CNC chassis, NVIDIA Jetson SBC bring-up, and high-altitude field proving trials in Ladakh).",
        style_body
    ))

    doc.build(story, canvasmaker=SimpleNumberedCanvas)
    shutil.copyfile(PDF_OUT, PDF_ARTIFACT)
    print(f"✅ Saved PDF report to: {PDF_OUT}")
    print(f"✅ Copied PDF report to: {PDF_ARTIFACT}")


if __name__ == '__main__':
    create_docx_report()
    create_pdf_report()
    print("\n🎉 Both Defence_Robot.docx and Defence_Robot.pdf have been successfully generated!")
