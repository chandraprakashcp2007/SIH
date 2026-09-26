from datetime import datetime,timezone
from xml.etree.ElementTree import Element,SubElement,tostring
from backend.app.models.alerts import Alert
NS="urn:oasis:names:tc:emergency:cap:1.2"
def child(parent,name,text): e=SubElement(parent,f"{{{NS}}}{name}");e.text=str(text);return e
def build_cap(alert:Alert,languages:list[str]):
    root=Element(f"{{{NS}}}alert");identifier=f"prahari-{alert.id}-{int(datetime.now(timezone.utc).timestamp())}"
    child(root,"identifier",identifier);child(root,"sender","prahari.local@not-configured.invalid");child(root,"sent",datetime.now(timezone.utc).isoformat());child(root,"status","Actual");child(root,"msgType","Cancel" if alert.state=="RESOLVED" else "Update" if alert.state in {"ACKNOWLEDGED","MONITORING"} else "Alert");child(root,"scope","Public")
    provenance=(alert.evidence or {}).get("provenance","SIMULATION")
    for language in languages:
        info=SubElement(root,f"{{{NS}}}info");child(info,"language",language);child(info,"category","Geo");child(info,"event",alert.hazard);child(info,"urgency","Immediate" if alert.severity=="CRITICAL" else "Expected");child(info,"severity","Extreme" if alert.severity=="CRITICAL" else "Severe" if alert.severity=="WARNING" else "Moderate");child(info,"certainty","Likely")
        if language=="hi-IN": headline=f"{alert.hazard} चेतावनी";description=f"{alert.location_name} के लिए सत्यापित स्थानीय चेतावनी विवरण देखें।";instruction="स्थानीय प्रशासन के निर्देशों का पालन करें।"
        else: headline=alert.headline;description=alert.summary;instruction=alert.action_recommended
        child(info,"headline",headline);child(info,"description",description);child(info,"instruction",instruction)
        area=SubElement(info,f"{{{NS}}}area");child(area,"areaDesc",alert.location_name)
        param=SubElement(info,f"{{{NS}}}parameter");child(param,"valueName","PRAHARI_PROVENANCE");child(param,"value",provenance)
    return identifier,tostring(root,encoding="unicode",xml_declaration=True),provenance
