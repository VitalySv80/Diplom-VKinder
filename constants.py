seeker_scopes = [
    "bdate",
    "sex",
    "city",
    "relation"
]

seeker_fields = ",".join(seeker_scopes)

seeker_info = {
    "bdate": 0,
    "sex": 0,
    "city_id": 0,
    "city": 0,
    "relation": 0
}

couple_info = {
    "first_name": 0,
    "last_name": 0,
    "id": 0
}

all_couples_info = list()

men_sex_spellings = [
    "2", "мужской", "парень", "мужик", "муж", "м", "мужчинка", "мачо", 
    "молодой человек", "дядька", "мужчина", "мэн", "дядя", "мистер", 
    "сильный пол", "man", "m", "male"
]

woman_sex_spellings = [
    "1", "женский", "женщина", "девушка", "девочка", "леди", "богиня", 
    "королева", "принцесса", "дама", "царица", "гражданка", "дева", "мадам", 
    "дамочка", "мисс", "миссис", "сударыня", "прекрасный пол", "нежный пол", 
    "слабый пол", "миледи", "woman", "girl", "female", "lady", "w", "f"
]

potential_relations = [str(x) for x in range(9)]