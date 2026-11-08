#!/opt/homebrew/bin/python3.11
"""Heritage guides (castles, abbey, well, cross, dyke, beach) as WordPress drafts, in the town guide format,
with the Geograph gallery. Facts researched 8 Nov 2026 from Cadw, Coflein, Flintshire County Council,
NRW, Hawarden Estate, Hope Community Council and the St Winefride's shrine.

  heritage_pages.py            create or update all (drafts)
  heritage_pages.py flint-castle
"""
import html, json, re, sys
from pathlib import Path
sys.path.insert(0, "/tmp")
import wp
G = Path.home() / "deeside-data" / "galleries"
STATE = Path.home() / "deeside-data" / "heritage_pages.json"
CSS = ("<style>.dgal{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px;margin:12px 0}"
       ".dgal figure{margin:0;background:#f4f4f2;border-radius:6px;overflow:hidden}"
       ".dgal img{width:100%;aspect-ratio:4/3;object-fit:cover;display:block}"
       ".dgal figcaption{font:13px/1.35 system-ui,sans-serif;padding:6px 8px;color:#333}"
       ".dgal figcaption small{display:block;color:#666;font-size:11.5px;margin-top:2px}"
       ".dgal-note{font:12px/1.4 system-ui,sans-serif;color:#666}</style>")
D = "https://www.deeside.com/"
CADW = "https://cadw.gov.wales/visit/places-to-visit/"
HUB = "flintshire-castles-and-heritage"

SITES = {
 "flint-castle": dict(
  title="Flint Castle: a visitor's guide", slug="flint-castle-guide", name="Flint Castle",
  intro="The first castle Edward I built in his conquest of Wales, on the edge of the Dee estuary in Flint. It is free to visit and looked after by Cadw.",
  facts=[("Run by", "Cadw"), ("Open", "10am to 4pm every day, last entry 3.30pm. Closed 24 to 26 December and 1 January"),
         ("Admission", "Free"), ("Sat nav", "CH6 5PH"), ("Nearest station", "Flint, about 270 metres away"),
         ("Terrain", "Cadw rates it level 2, easy. Dogs on short leads allowed on ground-floor levels")],
  sections=[
   ("A short history", [
    "Edward I's men started building the castle in 1277 and it was largely finished by 1284. Its great tower, or donjon, stands apart at one corner with its own moat, and its thick walls suggest it was meant as a last refuge.",
    "On Palm Sunday 1282 Dafydd ap Gruffudd attacked Flint. The rising drew in his brother, Llywelyn ap Gruffudd, and ended with Llywelyn's death later that year.",
    "In 1399 Richard II met Henry Bolingbroke, soon to be Henry IV, at Flint. Shakespeare set a scene of his play Richard II here.",
    "Royalists held the castle in the Civil War. It surrendered to Parliament in 1646, and Parliament then ordered it to be made unusable."]),
   ("Getting there", [
    "Flint is on the A548 coast road, about six miles west of Queensferry. Cadw says there are signposted public car parks in the town and one disabled space about 100 metres from the castle.",
    "Flint station, on the North Wales coast line, is a few minutes' walk away. National Cycle Network route 5 runs past the castle."]),
  ],
  faq=[("Is Flint Castle free?", "Yes. Cadw does not charge for entry."),
       ("What are the opening times?", "10am to 4pm every day, with last entry at 3.30pm. It is closed from 24 to 26 December and on 1 January."),
       ("Can I take my dog?", "Yes, on a short lead, on the ground-floor levels."),
       ("What is near Flint Castle?", f'The Flint town centre and the Dee estuary coast path. Ewloe Castle is about four and a half miles away. See our <a href="{D}flint-guide/">Flint guide</a>.')],
  news=[("In July 2017 the Welsh Government unveiled plans for a £395,000 sculpture called the Iron Ring at the castle. Critics said it celebrated Edward I's conquest of Wales, a petition against it passed 1,200 signatures in its first 24 hours, and the Welsh Government dropped the plan in September 2017, calling it divisive. Read our coverage:",
         [(D + "plans-giant-iron-ring-sculpture-costing-nearly-400000-flint-castle-unveiled-today/", "Plans for the Iron Ring sculpture unveiled (21 July 2017)"),
          (D + "petition-launched-as-locals-slam-extremely-disrespectful-395k-iron-ring-plan-for-flint-castle/", "Petition launched against the plan (24 July 2017)"),
          (D + "welsh-government-scrap-divisive-flint-castle-iron-ring-plan/", "Welsh Government scraps the plan (7 September 2017)")])],
  sources=[(CADW + "flint-castle", "Cadw: Flint Castle"), ("https://coflein.gov.uk/en/site/94448", "Coflein: Flint Castle")],
  gallery="flint-castle"),

 "ewloe-castle": dict(
  title="Ewloe Castle: a visitor's guide", slug="ewloe-castle-guide", name="Ewloe Castle",
  intro="A castle built by Welsh princes, hidden in woodland below Wepre Park between Connah's Quay and Ewloe. It is free to visit and looked after by Cadw.",
  facts=[("Run by", "Cadw"), ("Open", "All year, in reasonable daylight hours"), ("Admission", "Free"),
         ("Sat nav", "CH5 3BZ for Cadw's lay-by, or CH5 4HL for Wepre Park visitor centre"),
         ("Terrain", "Cadw rates it level 3, moderate: about 40 to 50 low steps, paths that can be boggy"),
         ("Facilities", "None at the castle. Toilets and a café at Wepre Park visitor centre")],
  sections=[
   ("A short history", [
    "Llywelyn ap Iorwerth, Llywelyn the Great, probably built the D-shaped Welsh Tower some time after 1210.",
    "Llywelyn ap Gruffudd, Llywelyn the Last, added the curtain walls and the round western tower almost 60 years later.",
    "Cadw says records from the time are thin, so these dates are not certain."]),
   ("Getting there", [
    f'Most people walk from <a href="{D}wepre-park/">Wepre Park</a> in Connah\'s Quay, following Wepre Brook up through the woods. The path has flights of steps.',
    "Parking at Wepre Park has been charged since 27 July 2026: £1 for up to two hours, £2 for up to four hours or £4 for the day, between 9am and 9pm.",
    "Cadw also lists a lay-by for about five cars, then a walk of about 500 metres across farmland on a path that can be muddy and uneven."]),
  ],
  faq=[("Is Ewloe Castle free?", "Yes. There is no charge and it is open in daylight hours all year."),
       ("Can I take my dog?", "Yes, on a short lead, on ground-floor areas."),
       ("How long is the walk?", "From the Cadw lay-by it is about 500 metres, 10 to 15 minutes. From Wepre Park visitor centre allow longer, as the path climbs through the woods."),
       ("Who built Ewloe Castle?", "Welsh princes, not the English crown: Llywelyn the Great began it and Llywelyn the Last extended it.")],
  sources=[(CADW + "ewloe-castle", "Cadw: Ewloe Castle"), ("https://www.flintshire.gov.uk/", "Flintshire County Council: Wepre Park parking charges, July 2026")],
  gallery="ewloe-castle"),

 "caergwrle-castle": dict(
  title="Caergwrle Castle: a visitor's guide", slug="caergwrle-castle-guide", name="Caergwrle Castle",
  intro="A hilltop ruin above Caergwrle, the last castle built by a native Welsh prince. It is free to visit, with views across to Hope and Wrexham.",
  facts=[("Run by", "Cadw looks after the castle; the wider site belongs to Hope Community Council"),
         ("Open", "All year, in reasonable daylight hours. Closed 24 to 26 December and 1 January"), ("Admission", "Free"),
         ("Sat nav", "LL12 9DG"), ("Nearest station", "Caergwrle, on the Wrexham to Bidston line, about a quarter of a mile away"),
         ("Terrain", "Cadw rates it level 3, moderate: a steep wooded path that can be muddy, and a drop behind the rear wall")],
  sections=[
   ("A short history", [
    "Dafydd ap Gruffudd, brother of Llywelyn ap Gruffudd, built the castle on land Edward I had given him, in about 1278 to 1282.",
    "Dafydd used it as his base for the attack on Hawarden in 1282 that started Edward's second Welsh war. The rising ended with Llywelyn's death in 1282 and Dafydd's execution at Shrewsbury in 1283.",
    "Work carried on under the Crown, but the castle was probably never finished. It was abandoned after a fire and was in ruins by 1335."]),
   ("Getting there", [
    "The castle is reached from Caergwrle on the A541, between Mold and Wrexham. Cadw says there is a public car park in the village just off the High Street, and you may need to cross busy roads to reach the path.",
    f'Caergwrle station is on the Wrexham to Bidston line. Check how the line is running on our <a href="{D}wrexham-bidston-line/">line tracker</a>.']),
  ],
  faq=[("Is Caergwrle Castle open?", "Yes. It is open all year in daylight hours and is free. An old closure notice from Storm Arwen in 2021 no longer applies."),
       ("Is it a hard walk?", "The path up is steep and can be muddy, with one set of steps near the top. Wear sensible shoes."),
       ("Who built it?", "Dafydd ap Gruffudd, the brother of Llywelyn the Last, between about 1278 and 1282.")],
  sources=[(CADW + "caergwrle-castle", "Cadw: Caergwrle Castle"), ("https://hopecommunitycouncil.gov.wales/caergwrle-castle-press-release", "Hope Community Council")],
  gallery="caergwrle-castle"),

 "hawarden-old-castle": dict(
  title="Hawarden Old Castle: a visitor's guide", slug="hawarden-old-castle-guide", name="Hawarden Old Castle",
  intro="A ruined 13th-century castle on a mound inside the private Hawarden Estate. It is only open to the public on a few open days a year.",
  facts=[("Owned by", "Hawarden Estate (private)"), ("Open", "Open days only, a few times a year. In 2026 these were Sundays, 10am to 3pm"),
         ("Admission", "Tickets online or at the gate, with money going to a chosen charity"),
         ("Way in", "The blue gates opposite the Glynne Arms in Hawarden, or the Farm Shop entrance"),
         ("Listed", "Grade I"), ("Terrain", "Steep, uneven paths up to the castle")],
  sections=[
   ("A short history", [
    "A Norman motte and bailey castle, thought to have been built by Hugh Lupus, Earl of Chester, stood here first.",
    "Llywelyn ap Gruffudd destroyed it in 1265. The stone castle that survives dates from the late 13th century. Dafydd ap Gruffudd attacked it in 1282.",
    "Parliament ordered it to be made unusable in 1647 after the Civil War. The Glynne family owned it from 1653 and it was restored in the 1860s and 1920s.",
    "The round keep is two storeys high. The newer Hawarden Castle, the house in the park, was the home of the Prime Minister William Gladstone, who married Catherine Glynne in 1839."]),
   ("Visiting", [
    "The estate announces open days on its website. Children must be with an adult and dogs on leads are welcome. Outside open days the ruin is on private land and cannot be visited."]),
  ],
  faq=[("Can I visit Hawarden Old Castle?", "Only on the estate's open days, usually a few Sundays a year. Check the Hawarden Estate website for dates."),
       ("Is it the same as Hawarden Castle?", "No. Hawarden Castle is the 18th-century house in the same park, where Gladstone lived. The Old Castle is the medieval ruin."),
       ("What else is nearby?", f'Hawarden village, the Farm Shop and Gladstone\'s Library. See our <a href="{D}hawarden-ewloe-guide/">Hawarden and Ewloe guide</a>.')],
  sources=[("https://www.hawardenestate.co.uk/", "Hawarden Estate: open days"), ("https://coflein.gov.uk/en/site/33107", "Coflein: Hawarden Castle"),
           ("https://cadwpublic-api.azurewebsites.net/reports/listedbuilding/FullReport?id=14", "Cadw listing: Hawarden Old Castle")],
  gallery="hawarden-old-castle"),

 "bailey-hill-mold": dict(
  title="Bailey Hill, Mold: a visitor's guide", slug="bailey-hill-mold-guide", name="Bailey Hill",
  intro="The site of Mold's Norman castle, now a public park in the town centre with woodland, play areas and a Gorsedd stone circle.",
  facts=[("Run by", "Flintshire County Council, with Mold Town Council and the Friends of Bailey Hill"),
         ("Address", "Bailey Hill Centre, Denbigh Road, Mold CH7 1BL"), ("Protected", "Most of the site is a scheduled monument"),
         ("Parking", "None on site. Griffiths Square pay car park is a few minutes' walk"),
         ("Nearest station", "Buckley, about four miles away"), ("Terrain", "Hilly; not fully accessible. The Bailey Hill Centre is accessible")],
  sections=[
   ("A short history", [
    "The castle was built in the early 12th century, probably by Robert de Montalt or a relative. The motte rises up to 12 metres above the inner bailey and sits on a natural ridge left by glaciers.",
    "It changed hands several times: Owain Gwynedd captured it in 1146, Llywelyn ab Iorwerth attacked it in 1199, Dafydd ap Llywelyn retook it in 1245 and Edward I recovered it in 1277.",
    "Sir Thomas Mostyn bought the site in 1809. The town bought it in 1870 and it was laid out as a park in 1920.",
    "A restoration costing more than £1.7 million, including a National Lottery grant, uncovered a wall about three metres thick, medieval arrowheads and seven skeletons."]),
   ("Getting there", [
    f'Bailey Hill is at the top of Mold High Street. Mold bus station is about half a mile away. See our <a href="{D}mold-guide/">Mold guide</a> for parking and getting to the town.']),
  ],
  faq=[("Is Bailey Hill free?", "Yes, it is a public park."),
       ("Was there a castle in Mold?", "Yes. Bailey Hill is the site of a Norman motte and bailey castle first recorded in 1146."),
       ("What is the stone circle?", "A Gorsedd circle, a modern ring of stones of the kind set up for the National Eisteddfod.")],
  sources=[("https://www.flintshire.gov.uk/", "Flintshire County Council: Bailey Hill"), ("https://coflein.gov.uk/en/site/268088/", "Coflein: Mold Castle, Bailey Hill"),
           ("https://cadw.gov.wales/open-doors-bailey-hill-centrepark-mold-castle", "Cadw Open Doors: Bailey Hill")],
  gallery="bailey-hill-mold"),

 "basingwerk-abbey": dict(
  title="Basingwerk Abbey: a visitor's guide", slug="basingwerk-abbey-guide", name="Basingwerk Abbey",
  intro="The ruins of a medieval abbey founded in 1131, at the bottom of Greenfield Valley near Holywell. It is free to visit and looked after by Cadw.",
  facts=[("Run by", "Cadw"), ("Open", "All year, in reasonable daylight hours"), ("Admission", "Free"),
         ("Sat nav", "CH8 7GH"), ("Parking", "Free car park below the abbey, with a short steep path up"),
         ("Terrain", "Cadw rates it level 1, accessible, though low thresholds can trip people. Dogs on short leads allowed")],
  sections=[
   ("A short history", [
    "Basingwerk was founded in 1131 and later became a Cistercian abbey. It was remodelled in the 13th century, and its chapter house is the oldest part still standing.",
    "The abbey sits at the foot of Greenfield Valley, which later became a busy industrial valley, with copper, brass, cotton and paper mills powered by the stream.",
    "The North Wales Pilgrim's Way starts at the abbey."]),
   ("Getting there", [
    "The abbey is just off the A548 coast road at Greenfield, about a mile north-east of Holywell. Buses run along the coast road from Deeside. The nearest station is Flint."]),
  ],
  faq=[("Is Basingwerk Abbey free?", "Yes. There is no charge and the free car park is just below the abbey."),
       ("Is it part of Greenfield Valley?", f'Yes. The abbey is at the bottom of the valley. See our <a href="{D}greenfield-valley-guide/">Greenfield Valley guide</a>.'),
       ("Is it safe to climb on the walls?", "No. Cadw warns that stones can fall in bad weather and climbing is dangerous.")],
  sources=[(CADW + "basingwerk-abbey", "Cadw: Basingwerk Abbey")],
  gallery="basingwerk-abbey"),

 "greenfield-valley": dict(
  title="Greenfield Valley Heritage Park: a visitor's guide", slug="greenfield-valley-guide", name="Greenfield Valley",
  intro="A 70-acre wooded valley running from Holywell down to the Dee estuary, with mill pools, the remains of its industrial past, a museum and farm, and Basingwerk Abbey at the bottom.",
  facts=[("Run by", "Greenfield Valley Trust, a charity, on land owned by Flintshire County Council"),
         ("Size", "About 70 acres"), ("Museum", "Reopened for the 2026 season on 28 March. Check opening days and prices before you go"),
         ("Abbey", "Basingwerk Abbey is free, all year"), ("Phone", "01352 714172")],
  sections=[
   ("A short history", [
    "The stream from St Winefride's Well powered the valley's mills. At one point it drove about 20 factories.",
    "Thomas Patten set up copper and brass works in 1753. Thomas Williams, known as the Copper King, took over in 1785, and Meadow Mill was built in 1788.",
    "Paper was made in the valley from 1771. The Abbey Paper Mills date from about 1821 and closed in 1982."]),
   ("Getting there", [
    "The valley runs between Holywell and Greenfield, off the A548 coast road. Buses run along the coast road from Connah's Quay and Flint. The nearest station is Flint."]),
  ],
  faq=[("Is Greenfield Valley free?", "Walking in the park and visiting Basingwerk Abbey is free. The museum and farm charge for entry: check current prices with the trust."),
       ("Is there a café?", "Yes, at the museum, and there is an adventure playground."),
       ("What else is nearby?", f'<a href="{D}st-winefrides-well-guide/">St Winefride\'s Well</a> at the top of the valley and <a href="{D}basingwerk-abbey-guide/">Basingwerk Abbey</a> at the bottom.')],
  sources=[("https://www.greenfieldvalley.com/", "Greenfield Valley Heritage Park"), (CADW + "basingwerk-abbey", "Cadw: Basingwerk Abbey"),
           ("https://cadw.gov.wales/sites/default/files/2022-02/Industrial%20Heritage%20-%20Greenfield%20valley%20resource%20-%20English.pdf", "Cadw: Greenfield Valley industrial heritage")],
  gallery="greenfield-valley"),

 "st-winefrides-well": dict(
  title="St Winefride's Well, Holywell: a visitor's guide", slug="st-winefrides-well-guide", name="St Winefride's Well",
  intro="A holy well and 15th-century chapel in Holywell, a pilgrimage site since at least 1115 and the National Catholic Shrine of St Winefride.",
  facts=[("Run by", "The shrine, part of the Catholic Diocese of Wrexham"),
         ("Open", "April to September 9am to 5pm; October to March 10am to 4pm. Last entry 30 minutes before closing. Closed Christmas Day and Boxing Day"),
         ("Admission", "Adult £3, child, student or over-65 £2, family £4. Disabled visitors and a companion free"),
         ("Address", "Greenfield Street, Holywell CH8 7PN"), ("Listed", "Grade I and a scheduled monument"),
         ("Facilities", "Accessible toilets, gift shop and museum. No dogs except assistance dogs")],
  sections=[
   ("A short history", [
    "Legend says the spring rose where St Beuno, a 7th-century abbot, brought his niece Winefride back to life.",
    "Pilgrims have come here since at least 1115, and it is said to be the oldest pilgrimage site in Britain visited without a break.",
    "The chapel above the well was built in the late 15th century. The well is mentioned in the medieval poem Sir Gawain and the Green Knight."]),
   ("Visiting", [
    "There is a flight of steps down to the well. The chapel is free but kept locked: ask the curator for the key, which needs a returnable deposit.",
    "In the pilgrimage season there are services and times set aside for bathing in the well. Check the shrine's website for times."]),
   ("Getting there", [
    "Holywell is off the A55 and the A5026. Buses run from Connah's Quay to Holywell bus station. The nearest station is Flint, about four miles away. Parking at the well is limited."]),
  ],
  faq=[("How much does it cost?", "£3 for adults, £2 for children, students and over-65s, or £4 for a family."),
       ("Can you bathe in the well?", "Yes, at set times in the pilgrimage season. Check with the shrine before you go."),
       ("What is nearby?", f'<a href="{D}greenfield-valley-guide/">Greenfield Valley</a> starts just below the well and runs down to <a href="{D}basingwerk-abbey-guide/">Basingwerk Abbey</a>.')],
  sources=[(CADW + "st-winefrides-chapel-and-holy-well", "Cadw: St Winefride's Chapel and Holy Well"), ("https://www.stwinefridesshrine.org/", "St Winefride's Shrine")],
  gallery="st-winefrides-well"),

 "talacre-lighthouse": dict(
  title="Talacre beach and the Point of Ayr lighthouse: a visitor's guide", slug="talacre-beach-lighthouse-guide", name="Talacre and the Point of Ayr lighthouse",
  intro="A wide sandy beach backed by dunes at the mouth of the Dee, with the old Point of Ayr lighthouse standing on the shore. It is Flintshire's best-known beach.",
  facts=[("Lighthouse", "Built in 1776, no longer in use, Grade II listed"),
         ("Parking", "Two council car parks: £1 for up to two hours, £2.50 up to four hours, £5 up to 11 hours, all year. Coins or PayByPhone"),
         ("Protected", "Gronant Dunes and Talacre Warren is a Site of Special Scientific Interest, part of the Dee Estuary special area of conservation"),
         ("Swimming", "Not safe: strong currents"), ("In an emergency", "Dial 999 and ask for the Coastguard")],
  sections=[
   ("A short history", [
    "The lighthouse was built in 1776, designed by Joseph Turner of Hawarden, after two Dublin packet ships were lost.",
    "Trinity House took it over in 1819 and gave it a new lantern. It was replaced by a new structure in 1844 and by a lightship in 1883."]),
   ("Wildlife", [
    "The dunes are the main Welsh home of the natterjack toad. Nearby Gronant has the largest little tern colony in Wales: the birds arrive in May and leave by the end of August, and parts of the beach are fenced off to protect them. Keep dogs on leads near nesting birds."]),
   ("Staying safe", [
    "The tide comes in fast across the sands and there is soft mud in places. People have been rescued after getting stuck. Check the tide times before you walk out, and if someone is in trouble dial 999 and ask for the Coastguard."]),
   ("Getting there", [
    "Talacre is off the A548 coast road beyond Mostyn. Buses on the coast road stop at the Station Road turn in Talacre. There is no station in the village."]),
  ],
  faq=[("Is Talacre beach free?", "The beach is free. The council car parks charge, from £1 for two hours."),
       ("Can you go in the lighthouse?", "No. It is a listed building and is not open to the public."),
       ("Can you swim at Talacre?", "It is not safe because of strong currents."),
       ("Are dogs allowed?", "Visitor guides say dogs are welcome, on a lead near nesting birds. Check signs on the beach in the summer.")],
  sources=[("https://cadwpublic-api.azurewebsites.net/reports/listedbuilding/FullReport?id=520", "Cadw listing: Point of Ayr lighthouse"),
           ("https://naturalresources.wales/about-us/news-and-blogs/blogs/rejuvenating-the-dunes-at-gronant-and-talacre/?lang=en", "Natural Resources Wales: Gronant and Talacre dunes"),
           ("https://www.flintshire.gov.uk/en/Resident/Streetscene/Car-parks.aspx", "Flintshire County Council: car parks")],
  gallery="talacre-lighthouse"),

 "wats-dyke": dict(
  title="Wat's Dyke in Flintshire: a guide", slug="wats-dyke-guide", name="Wat's Dyke",
  intro="An early medieval bank and ditch that runs for about 40 miles from near Basingwerk Abbey through Flintshire to Shropshire, older and lesser known than its neighbour, Offa's Dyke.",
  facts=[("What it is", "An earth bank with a ditch on its western side, facing Wales"),
         ("Length", "About 40 miles, in stretches, from Basingwerk to Maesbury in Shropshire"),
         ("Protected", "Scheduled monument in sections; most of it is on private land"),
         ("Walk it", "The Wat's Dyke Way, about 61 miles from Llanymynech to Greenfield, opened in 2008")],
  sections=[
   ("When was it built?", [
    "It was long thought to date from the 8th century. Recent research suggests it was built in the early 9th century, possibly under Coenwulf of Mercia, which would make it later than Offa's Dyke. The date is still debated."]),
   ("Where to see it in Flintshire", [
    "Stretches survive near Argoed and New Brighton, east of Mold, and near Hope, as well as west of Rhos-y-Brwyner. Much of it is in fields and gardens, so only look at it from public paths. The Wat's Dyke Way follows its line and ends at Greenfield, near Holywell."]),
  ],
  faq=[("Is Wat's Dyke the same as Offa's Dyke?", "No. Wat's Dyke runs further east, roughly parallel to Offa's Dyke, and is thought to be later."),
       ("Can I walk along it?", "Yes, using the Wat's Dyke Way and other public rights of way. Do not walk on sections on private land.")],
  sources=[("https://coflein.gov.uk/en/site/300808", "Coflein: Wat's Dyke west of Rhos-y-Brwyner"), ("https://cadw.gov.wales/", "Cadw scheduled monument records")],
  gallery="wats-dyke"),

 "maen-achwyfan": dict(
  title="Maen Achwyfan cross: a visitor's guide", slug="maen-achwyfan-guide", name="Maen Achwyfan cross",
  intro="A carved stone wheel-cross standing in a field near Whitford, more than 1,000 years old and about 3.4 metres tall. It is free to visit and looked after by Cadw.",
  facts=[("Run by", "Cadw"), ("Open", "All year, in reasonable daylight hours"), ("Admission", "Free"),
         ("Where", "About a mile west-north-west of Whitford, off the A5151. Postcode CH8 9DD"),
         ("Parking", "No dedicated parking"), ("Terrain", "Cadw rates it level 3, moderate: can be muddy, with grazing animals nearby")],
  sections=[
   ("About the cross", [
    "Cadw dates the cross to the late 10th century. It was carved from a single stone, with interlace patterns on every side and a cross on both faces of its round head.",
    "It also has stylised human and animal figures, which Cadw says show Viking influence. The name is said to mean the stone of St Cwyfan."]),
   ("Getting there", [
    "Drive through Holywell and take the A5151 towards Whitford. National Cycle Network route 5 passes nearby. Please do not climb on the stone."]),
  ],
  faq=[("How old is Maen Achwyfan?", "Cadw dates it to the late 10th century."),
       ("Is it free?", "Yes, and it is open in daylight hours all year.")],
  sources=[(CADW + "maen-achwyfan-cross", "Cadw: Maen Achwyfan Cross"), ("https://cadwpublic-api.azurewebsites.net/reports/sam/FullReport?id=416", "Cadw scheduled monument record FL005")],
  gallery="maen-achwyfan"),
}


def gallery(key, name):
    d = json.loads((G / f"{key}.json").read_text())
    figs = []
    for p in d["photos"]:
        t, by = html.escape(p["title"]), html.escape(p["by"])
        figs.append(f'<figure><a href="{p["link"]}" target="_blank" rel="noopener"><img src="{p["img"]}" alt="{t}" loading="lazy" width="213" height="160"></a>'
                    f'<figcaption>{t}<small>&copy; {by}, <a href="https://creativecommons.org/licenses/by-sa/2.0/" target="_blank" rel="noopener license">CC BY-SA 2.0</a>, via <a href="{p["link"]}" target="_blank" rel="noopener">Geograph</a></small></figcaption></figure>')
    return ("<!-- dgal start -->" + CSS + f"<h2>Photos of {html.escape(name)}</h2>" + '<div class="dgal">' + "".join(figs) + "</div>"
            '<p class="dgal-note">Photos from the <a href="https://www.geograph.org.uk/" target="_blank" rel="noopener">Geograph</a> project, '
            "shared under a Creative Commons licence. Tap a photo to see it full size. Got a better one? Send it to us.</p><!-- dgal end -->")


def content(k, s):
    out = [f"<p>{s['intro']}</p>", "<h2>Key facts</h2>", "<table>", "<tbody>"]
    out += [f"<tr><th>{a}</th><td>{b}</td></tr>" for a, b in s["facts"]]
    out += ["</tbody>", "</table>", ""]
    for h, paras in s["sections"]:
        out.append(f"<h2>{h}</h2>")
        out += [f"<p>{p}</p>" for p in paras]
        out.append("")
    for intro, links in s.get("news", []):
        out.append("<h2>In the news</h2>")
        out.append(f"<p>{intro}</p>")
        out.append("<ul>" + "".join(f'<li><a href="{u}">{t}</a></li>' for u, t in links) + "</ul>" + chr(10))
    out.append("<h2>Listed buildings and more</h2>")
    out.append(f'<p>See every Cadw listed building in Flintshire on our <a href="{D}listed-buildings/">listed buildings pages</a>, and more places to visit in our <a href="{D}{HUB}/">guide to castles and heritage in Flintshire</a>.</p>\n')
    out.append(gallery(s["gallery"], s["name"]) + "\n")
    out.append("<h2>Questions people ask</h2>")
    for q, a in s["faq"]:
        out += [f"<h3>{q}</h3>", f"<p>{a}</p>"]
    out += ["", "<h2>Sources</h2>", "<ul>"] + [f'<li><a href="{u}">{t}</a></li>' for u, t in s["sources"]] + ["</ul>", ""]
    out.append("<p><em>Checked November 2026. Opening times and prices can change, so check with the site before you travel. "
               f'Spotted something wrong? <a href="{D}contact/">Let us know</a>.</em></p>')
    return "\n".join(out)


def hub():
    rows = []
    groups = [("Castles", ["flint-castle", "ewloe-castle", "caergwrle-castle", "hawarden-old-castle", "bailey-hill-mold"]),
              ("Abbeys, wells and crosses", ["basingwerk-abbey", "st-winefrides-well", "maen-achwyfan"]),
              ("Parks, coast and countryside", ["greenfield-valley", "talacre-lighthouse", "wats-dyke"])]
    out = ["<p>Castles built by Welsh princes and English kings, a medieval abbey, a holy well said to be Britain's oldest continuously visited pilgrimage site, "
           "and a beach with an 18th-century lighthouse. Our guides to Flintshire's heritage, with opening times, parking and photos.</p>"]
    for g, keys in groups:
        out.append(f"<h2>{g}</h2>\n<ul>")
        for k in keys:
            s = SITES[k]
            out.append(f'<li><a href="{D}{s["slug"]}/"><strong>{s["name"]}</strong></a>: {s["intro"].split(". ")[0].rstrip(".")}.</li>')
        out.append("</ul>")
    out.append(f'<h2>More</h2>\n<p>Our <a href="{D}wepre-park/">Wepre Park guide</a>, <a href="{D}listed-buildings/">listed buildings in Flintshire</a> and town guides for '
               f'<a href="{D}mold-guide/">Mold</a>, <a href="{D}flint-guide/">Flint</a> and <a href="{D}hawarden-ewloe-guide/">Hawarden and Ewloe</a>.</p>')
    out.append("<p><em>Checked November 2026. Opening times and prices can change, so check before you travel.</em></p>")
    return "\n".join(out)


def save(slug, title, body, state):
    pid = state.get(slug)
    if pid:
        wp.call(f"pages/{pid}", {"title": title, "content": body})
    else:
        r = wp.call("pages", {"title": title, "slug": slug, "status": "draft", "content": body})
        pid = state[slug] = r["id"]
    print(slug, pid)


if __name__ == "__main__":
    state = json.loads(STATE.read_text()) if STATE.exists() else {}
    keys = sys.argv[1:] or list(SITES) + ["hub"]
    for k in keys:
        if k == "hub":
            save(HUB, "Castles and heritage in Flintshire", hub(), state)
        else:
            s = SITES[k]
            save(s["slug"], s["title"], content(k, s), state)
    STATE.write_text(json.dumps(state, indent=1))
