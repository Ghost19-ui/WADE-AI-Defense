from fastapi import APIRouter
import random
import string

router = APIRouter()

# realistic-sounding fake data
FIRST_NAMES = ["John", "Emma", "Michael", "Sophia", "William", "Olivia", "James", "Ava"]
LAST_NAMES = ["Smith", "Johnson", "Brown", "Williams", "Jones", "Garcia", "Miller"]
DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"]

def generate_password():
    chars = string.ascii_letters + string.digits + "!@#$%"
    return "".join(random.choice(chars) for _ in range(12))

@router.get("/countermeasures/junk_data")
async def get_junk_data():
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    number = random.randint(10, 999)
    domain = random.choice(DOMAINS)
    
    email = f"{first.lower()}.{last.lower()}{number}@{domain}"
    password = generate_password()
    
    return {
        "email": email,
        "username": f"{first}{last}{number}",
        "password": password,
        "credit_card": f"4{random.randint(100,999)} {random.randint(1000,9999)} {random.randint(1000,9999)} {random.randint(1000,9999)}"
    }