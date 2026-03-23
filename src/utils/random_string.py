import random
import string
import uuid
from faker import Faker

def generate_random_string(length: int) -> str:
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def generate_random_number(length: int) -> str:
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def generate_random_uuid() -> str:
    return str(uuid.uuid4())

def generate_random_address(localization: str = 'en_US') -> str:
    fake = Faker(localization)
    address = fake.address()
    return address

def generate_random_full_name(localization: str = 'en_US') -> str:
    fake = Faker(localization)
    full_name = fake.name()
    return full_name

def generate_random_mail(localization: str = 'en_US', length: int = 15) -> str:
    length = int(length)
    fake = Faker(localization)
    user_name = fake.user_name()
    
    # Đảm bảo length - len(user_name) không âm
    random_length = max(0, length - len(user_name))  # Đảm bảo không âm
    random_number = generate_random_number(random_length)
    email = user_name + random_number
    return email

def generate_random_password(length: int = 15, has_special_chars: bool = False) -> str:
    special_chars = ''
    length_value = int(length)
    characters = string.ascii_letters + string.digits

    # Loại bỏ các ký tự đặc biệt khỏi danh sách nếu không muốn chúng xuất hiện trong mật khẩu
    if not has_special_chars:
        characters = characters.replace("'", "").replace('"', "").replace("{", "").replace("}", "").replace("`", "")

    upper_case = random.choice(string.ascii_uppercase)
    lower_case = random.choice(string.ascii_lowercase)
    number = random.choice(string.digits)

    if has_special_chars:
        special_chars = random.choice(string.punctuation)
        characters += string.punctuation
    password_chars = [upper_case, lower_case, number, special_chars]
    if length_value > 4:
        for index in range(length_value - 4):
            password_chars.append(random.choice(characters))
    random.shuffle(password_chars)
    password = ''.join(password_chars)

    return password