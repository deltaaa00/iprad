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