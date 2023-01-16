from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from config import group_token, access_token
from constants import seeker_fields


class ApiVk:
    """Класс работы с API"""

    def __init__(self) -> None:
        """Инициализируем работу с АПИ"""
        self.vk_group = vk_api.VkApi(token=group_token)
        self.vk_seeker = vk_api.VkApi(token=access_token)
        self.longpoll = VkLongPoll(self.vk_group)

    def listen_answer(self) -> tuple:
        """Слушаем ответ от пользователя"""
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    text = event.text.lower()
                    
                    return text, event


    def write_msg(self, user_id: str, message: str) -> int:
        """Ответ бота"""
        res = self.vk_group.method(
            "messages.send", 
            {
                "user_id": user_id, 
                "message": message, 
                "random_id": randrange(10 ** 7),
            }
            )
        return res

    def users_get(self, seeker: str) -> list:
        """Собираем информацию о пользователе"""
        res = self.vk_group.method(
            "users.get", 
            {
                "user_ids": seeker,
                "fields": seeker_fields,
            }
            )
        return res

    def users_search(
            self, bdate: int, sex: int, city_id: int, relation: int, 
            count: int) -> dict:
        """Ищем подходящие пары для пользователя"""
        res = self.vk_seeker.method(
            "users.search", 
            {
                "fields": seeker_fields, 
                "city": city_id, 
                "sex": sex, 
                "count": count, 
                "status": relation, 
                "birth_year": bdate, 
                "has_photo": 1
            }
            )
        return res

    def get_city(self, city: str) -> dict:
        """Находим id города по его названию"""
        res = self.vk_seeker.method("database.getCities", {"q": city,})
        return res

    def photos_get(self, couple_id: int) -> dict:
        """Получает информацию о фотографиях пары"""
        res = self.vk_seeker.method(
            "photos.get", 
            {
                "owner_id": couple_id, 
                "album_id": "profile", 
                "rev": 1, 
                "extended": 1
            }
            )
        return res