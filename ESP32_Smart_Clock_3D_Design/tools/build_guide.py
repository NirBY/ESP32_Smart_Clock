"""Create the illustrated English print guide. Requires requirements-docs.txt."""
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.pagesizes import A4

root = Path(__file__).resolve().parents[1]
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='TitleClock', fontName='Helvetica-Bold', fontSize=25, leading=29, textColor=colors.HexColor('#17324a'), spaceAfter=12))
styles.add(ParagraphStyle(name='SectionClock', fontName='Helvetica-Bold', fontSize=15, leading=19, textColor=colors.HexColor('#17324a'), spaceBefore=12, spaceAfter=8))
styles.add(ParagraphStyle(name='BodyClock', fontName='Helvetica', fontSize=10, leading=14, spaceAfter=8))
styles.add(ParagraphStyle(name='SmallClock', fontName='Helvetica', fontSize=8, leading=11, spaceAfter=5))
styles.add(ParagraphStyle(name='AlertClock', parent=styles['BodyClock'], backColor=colors.HexColor('#fff1cf'), borderPadding=10, spaceBefore=10, spaceAfter=15))
story=[]
def p(text,style='BodyClock'): story.append(Paragraph(text, styles[style]))
def table(rows,widths):
    data=[[Paragraph(str(c),styles['SmallClock']) for c in row] for row in rows]
    t=Table(data,colWidths=widths,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e4edf3')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,0),(-1,0),.7,colors.HexColor('#a9bdce')),('LINEBELOW',(0,1),(-1,-1),.3,colors.HexColor('#dbe4eb'))]))
    story.append(t);story.append(Spacer(1,10))
def picture(name,size=260):
    im=Image(str(root/'previews'/name),width=size,height=size);im.hAlign='CENTER';story.append(im)
def page():story.append(PageBreak())

p('ESP32 Smart Clock','TitleClock')
p('ENCLOSURE / PRINT & ASSEMBLY GUIDE / REVISION 18','SmallClock')
picture('cover.png',255)
p('Three printed parts. One rounded enclosure.','SectionClock')
p('Print one <b>body.stl</b>, one <b>lid.stl</b> and one <b>sensor_cage.stl</b>. All files use millimetres and must stay at 100% scale. The two small fit samples are optional checks, not assembly parts.')
table([['Dimension','Value'],['Body','158 x 60 x 49.7 mm'],['Overall with lid, feet and sensor cage','158 x 77.5 x 51.2 mm'],['Side walls / lid / optical front','2.25 mm / 1.5 mm / 0.6 mm']],[260,245])
p('<b>Mandatory lid pause:</b> fixed 0.15 mm layers, including the first. Pause after <b>Z 4.05 mm</b>, before Z 4.20 mm, to insert two M3 nuts. See page 3 before slicing.','AlertClock')
p('The creator tested the 0.6 mm front diffuser successfully in white PLA. The complete latest assembly and insert-pause process are geometrically checked but not physically validated. Images in this guide are CAD renders.','SmallClock')

page();p('Print setup & hardware','TitleClock')
table([['Part','Material / orientation','Layers'],['Body','White PLA; front face on bed, as supplied. At least three solid bottom layers through the diffuser.','0.20 mm first and later'],['Lid / ESP sample','PLA; outer face on bed, as supplied. Mandatory pause on page 3.','0.15 mm first and later, fixed'],['Sensor cage / power sample','PLA; supplied orientation. Inspect bridges and small openings.','0.20 mm first and later']],[93,310,102])
p('Design target: Ender-3 V3 KE. Suggested starting point: 0.4 mm nozzle, three perimeters, 20% infill. Use calibrated temperatures and speeds. Inspect bridges and overhangs, keeping supports out of the insert pockets, vents and wire routes. No validated slicing profile or G-code is supplied. Opaque black PLA blocks the display.')
p('Fasteners','SectionClock')
p('<b>14 M3 brass inserts:</b> 2.9 mm long, maximum OD 4.2 mm (root about 3.7 mm). Pilot holes are nominally 3.9 mm. Flat-underhead screws: measured head OD 5.2 mm, height 2.1 mm.')
table([['Location','Count','Screw / washer'],['Lid to body','4','M3 x 5 + 0.5 mm washer, or M3 x 4 without washer'],['Sensor cage','2','M3 x 6'],['ESP at USB side','2','M3 x 8 + 0.5 mm washer; inserts fitted mid-print'],['Other ESP posts','2','M3 x 5'],['Speaker','2','M3 x 5 + 0.5 mm washer'],['Amplifier','2','M3 x 5 + 0.5 mm washer, washer OD 7 mm']],[132,45,328])
p('Make sure each screw clamps its part before reaching the bottom of its hole. The ESP PCB thickness was inferred as 2.5 mm; confirm against your board. USB-side screw tips have about 0.9 mm nominal clearance from the closing skin.','SmallClock')
p('Test before printing the full parts','SectionClock')
p('Use <b>esp_gauge.stl</b> to check the two relieved ESP posts, button clearance and pause workflow. Use <b>power_gauge.stl</b> to check the 13.1 x 5.5 mm oblong opening with the actual snap-in socket. Do not alter model scale to correct a local fit issue.')

page();p('Lid: install two inserts mid-print','TitleClock')
p('The two rear access holes have built-in 0.6 mm closures. After the lid is complete, the narrower screw passages prevent installing these two inserts from above.','AlertClock')
table([['Feature','Height from print bed'],['Closed outside skin','0.00 to 0.60 mm'],['Insert supporting shoulder','1.05 mm'],['Top of seated 2.9 mm insert','3.95 mm'],['Pause after completed layer','4.05 mm (27 completed layers)'],['Next layer after resume','4.20 mm']],[300,205])
for t in [
'<b>1.</b> Keep the supplied lid orientation, with the outside face on the bed. Set 0.15 mm for the first and all later layers. Do not add a raft or use adaptive layers.',
'<b>2.</b> Set the pause after Z 4.05 mm and before Z 4.20 mm. Verify height in the slicer preview; some slicers number layers differently. Use the pause action supported by your printer.',
'<b>3.</b> At the pause, heat-set two M3 inserts into the open USB-side pockets. The 3.9 mm pilot is smaller than the 4.2 mm brass insert. Do not force them in cold or remove the print from the bed.',
'<b>4.</b> Seat each insert on its internal shoulder. Its top should sit at Z 3.95 mm, about 0.10 mm below the paused surface. Confirm both are below the nozzle path.',
'<b>5.</b> Resume printing. The upper post sections capture the inserts. Fit other accessible inserts after printing and cooling. Test this process on the small ESP sample first.']:p(t)
p('Lid mounting face','SectionClock')
picture('lid_inside.png',190)

page();p('Fit & assemble','TitleClock')
table([['Measured hardware','Envelope / key fit'],['MAX7219 display','132.1 x 32.1 x 17.8 mm including wires'],['ESP32 USB-C board','51.6 x 28.2 mm PCB; 53.5 mm including USB; 23 mm wired depth; hole centers 2.45 mm from adjacent edges'],['Speaker','69.7 x 31.2 x 16.6 mm; 3.3 mm holes; 1.7 mm mounting ears'],['NS4168 amplifier','38.5 x 22.4 mm PCB; 42.4 mm wired length; 10.1 mm height'],['External sensor','15 x 15 x 7.6 mm with connector; loose in cage'],['Power USB-C','Body 12.8 x 5.2 mm; depth 12.7 mm behind flange; flange 15.6 x 9.3 mm; spring span up to 15.7 mm']],[130,375])
for t in [
'<b>1.</b> Let the body cool before release; do not push on the thin front. Fit the lid and cage inserts into the body.',
'<b>2.</b> Seat the display against the diffuser between the four L-shaped stops. No display screws or snap arms are used.',
'<b>3.</b> Mount ESP, amplifier and speaker on the lid. ESP USB faces the left port. The speaker membrane faces the rear grille; speaker wires lead toward the amplifier.',
'<b>4.</b> With the lid open, insert the power socket into the opposite side opening near the speaker. Its long axis follows the depth of the case.',
'<b>5.</b> Route the connected wiring. Feed sensor wires through the body opening within the cage footprint. Close the lid without pinching wires, then fit four screws.',
'<b>6.</b> Rest the sensor on the body outside and secure the ventilated cage with two opposite screws. Do not pass M3 screws through the sensor PCB.']:p(t)
p('Validation & reuse','SectionClock')
p('All assembly meshes and fit samples are single watertight solids. Tests cover rigid component envelopes, insertion clearances, vents and connector geometry. Measurement uncertainty is about +/-1 mm; actual button shapes, spring deflection and wiring still need physical fitting. Nominal display-to-ESP wiring clearance is 5.1 mm.','SmallClock')
p('Copyright (c) 2026 NirBY. Original enclosure and revised design by NirBY, with Codex-assisted CAD preparation. Design files and guide: CC BY-NC-SA 4.0. Credit required; noncommercial use; share adaptations under the same license. Firmware is outside this design license scope.','SmallClock')
p('<link href="https://github.com/NirBY/ESP32_Smart_Clock" color="#236891">github.com/NirBY/ESP32_Smart_Clock</link><br/><link href="https://creativecommons.org/licenses/by-nc-sa/4.0/" color="#236891">creativecommons.org/licenses/by-nc-sa/4.0/</link>','SmallClock')

def footer(canvas,doc):
    canvas.setStrokeColor(colors.HexColor('#c7d5df'));canvas.line(45,38,A4[0]-45,38)
    canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#526779'))
    canvas.drawString(45,24,'NirBY | ESP32 Smart Clock | Enclosure v18 | CC BY-NC-SA 4.0')
    canvas.drawRightString(A4[0]-45,24,str(doc.page))

SimpleDocTemplate(str(root/'PRINT_GUIDE.pdf'),pagesize=A4,rightMargin=45,leftMargin=45,topMargin=40,bottomMargin=52,
                  title='ESP32 Smart Clock - Print and Assembly Guide',author='NirBY').build(story,onFirstPage=footer,onLaterPages=footer)
print(root/'PRINT_GUIDE.pdf')
