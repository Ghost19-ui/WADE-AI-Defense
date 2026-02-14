import whois
from datetime import datetime

def get_domain_age(url):
    try:
        domain = url.split("//")[-1].split("/")[0]
        w = whois.whois(domain)
        creation_date = w.creation_date
        
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
            
        if creation_date:
            age = (datetime.now() - creation_date).days
            return {"age_days": age}
    except:
        pass
    return {"age_days": -1}