import random

adjectives = ["행복한", "귀여운", "수줍은", "익명의", "배고픈", "용감한", "무서운", "재밌는", "우울한", "따뜻한"]
animals = ["토끼", "고양이", "강아지", "펭귄", "여우", "곰", "다람쥐", "고슴도치", "호랑이", "늑대"]

def generate_random_name():
    return f"{random.choice(adjectives)}{random.choice(animals)}{random.randint(1, 999)}"