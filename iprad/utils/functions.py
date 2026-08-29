import socket

def get_flag(country_code: str) -> str:
    #Get flag from country code
    if not country_code or len(country_code) != 2:
        return ""
    
    return "".join(chr(127397 + ord(c)) for c in country_code.upper())

#Dns resolve 
def get_resolved_ip(user_inp: str) -> str | None:
    try:
        socket.inet_aton(user_inp)


        return user_inp
    
    except socket.error:
        try:
            return socket.gethostbyname(user_inp)
        except socket.gaierror:
            return None

#rdap normalize

from datetime import datetime


def normalize_rdap_data(data: dict, target: str) -> dict:
    if not isinstance(data, dict):
        return {}
    emails = []
    vcard_org = None

    entities = data.get("entities", [])
    for entity in entities:
        vcards = entity.get("vcardArray", [])
        if len(vcards) > 1:
            for item in vcards[1]:
                field_name = item[0]
                field_val = item[3]

                if field_name == "email" and field_val:
                    emails.append(str(field_val))
                elif field_name == "fn" and not vcard_org:
                    vcard_org = str(field_val)

    creation_date = "N/A"
    expiration_date = "N/A"

    for event in data.get("events", []):
        action = event.get("eventAction")
        if action in ("registration", "created"):
            creation_date = event.get("eventDate", "N/A")
        elif action in ("expiration", "expired"):
            expiration_date = event.get("eventDate", "N/A")


    normalized = {
        "domain": target,
        "registrar": data.get("port43") or "RDAP Provider",
        "org": data.get("name") or vcard_org or "N/A",
        "country": data.get("country", "N/A"),
        "city": "N/A",
        "state": "N/A",
        "emails_str": ", ".join(set(emails)) if emails else "N/A",
        "whois_server": data.get("port43", "N/A"),
        "creation_date": creation_date,
        "expiration_date": expiration_date,
        "created_at": data.get("created_at", datetime.now().isoformat())
    }

    return normalized