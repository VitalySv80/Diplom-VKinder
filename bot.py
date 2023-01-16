import vk_api
from config import count
from constants import (
    seeker_scopes, seeker_info, woman_sex_spellings,
    men_sex_spellings, potential_relations, all_couples_info
)
from db import add_couple, check_exist, create_db
from api import ApiVk


class Bot(ApiVk):
    """Базовый класс бота ВК"""

    def get_seeker_info(self) -> list:
        """
        Собираем информацию о пользователе
        для которого будем искать пару.

        """
        seeker, vk_event = self.listen_answer()
        res = self.users_get(seeker)
        if not res:
            self.write_msg(
                vk_event.user_id, 
                "Человека с таким id не существует, попробуйте ещё раз"
                )
            return self.get_seeker_info()

        return res


    def get_city_info(self) -> dict:
        """
        Повторно спрашиваем пользователя при неправильном вводе про город.

        """
        city, vk_event = self.listen_answer()
        res = self.get_city(city)
        if res["count"] == 0:
            self.write_msg(
                vk_event.user_id, 
                "Похоже такого города ВК не знает, \
                попробуйте ещё раз или введите соседний город"
                )
            res = self.get_city_info()
        
        return res

        
    def check_bdate(self) -> str:
        """
        Проверяем корректность даты рождения. 
        Если неправильный, возвращаем к вводу даты.

        """
        date, vk_event = self.listen_answer()
        try:
            date = int(date)
        except ValueError:
            self.write_msg(
                vk_event.user_id, 
                "Введите полный год рождения в формате ГГГГ"
                )
            date = self.check_bdate()
        
        if date not in range(1900, 2023):
            self.write_msg(
                vk_event.user_id, 
                "Введите адекватный (1900-2022) год рождения в формате ГГГГ"
                )
            date = self.check_bdate()

        return date


    def check_sex(self) -> str:
        """
        Проверяем корректность пола. 
        Если неправильный, возвращаем к вводу пола
        
        """
        sex, vk_event = self.listen_answer()
        if sex in woman_sex_spellings:
            sex = "1"
        elif sex in men_sex_spellings:
            sex = "2"
        else:
            self.write_msg(
                vk_event.user_id, 
                "Введите пол:\n1 - женский\n2 - мужской"
                )
            sex = self.check_sex()
        
        return sex


    def check_relation(self) -> str:
        """
        Проверяем корректность семейного положения. 
        Если неправильный, возвращаем к вводу семейного положения
        
        """
        relation, vk_event = self.listen_answer()
        if relation in potential_relations:
            return relation
            
        self.write_msg(
            vk_event.user_id, 
            "Введите цифру от 0 до 8 включительно, \
            в соответствии с указанными выше"
            )
        relation = self.check_relation()

        return relation


    def check_info_completeness(
            self, seeker_scopes: list, info: list, 
            vk_event: vk_api.longpoll.Event) -> dict:
        """
        Проверяем информацию на полноту, и если чего-то не хватает
        отправляем сообщение, что нужно дополнить в словаре seeker_info
        
        """
        for elem in seeker_scopes:
            if elem in info[0].keys():
                if elem == "bdate":
                    
                    if len(info[0]["bdate"].split(".")) < 3:
                        self.write_msg(
                            vk_event.user_id, 
                            "Не хватает информации!"
                            )
                        self.write_msg(
                            vk_event.user_id, 
                            "Введите полный год рождения (например: 1990)"
                            )
                        seeker_info["bdate"] = self.check_bdate()
                    else:
                        seeker_info["bdate"] = info[0]["bdate"].split(".")[2]

                elif elem == "sex":
                    seeker_info["sex"] = info[0].get("sex")

                elif elem == "city":
                    seeker_info["city_id"] = info[0].get("city").get("id")
                    seeker_info["city"] = info[0].get("city").get("title")

                elif elem == "relation":
                    seeker_info["relation"] = info[0].get("relation")

            else:
                self.write_msg(vk_event.user_id, "Не хватает информации!")
                if elem == "bdate":
                    self.write_msg(
                        vk_event.user_id, 
                        "Введите полный год рождения (например: 1977)"
                        )
                    seeker_info["bdate"] = self.check_bdate()
                
                elif elem == "sex":
                    self.write_msg(
                        vk_event.user_id, 
                        "Введите пол\n1 - женский\n2 - мужской"
                        )
                    seeker_info["sex"] = self.check_sex()                

                elif elem == "city":
                    self.write_msg(vk_event.user_id, "Введите город")
                    city_info = self.get_city_info()
                    seeker_info["city"] = city_info["items"][0]["title"]
                    seeker_info["city_id"] = city_info["items"][0]["id"]

                elif elem == "relation":
                    self.write_msg(
                        vk_event.user_id, 
                        """Введите cемейное положение:
                        1 — не женат/не замужем
                        2 — есть друг/есть подруга
                        3 — помолвлен/помолвлена
                        4 — женат/замужем
                        5 — всё сложно
                        6 — в активном поиске
                        7 — влюблён/влюблена
                        8 — в гражданском браке
                        0 — не указано"""
                        )
                    seeker_info["relation"] = self.check_relation()
        
        return seeker_info
                

    def find_couple(
            self, bdate: int, sex: int, city_id: int, relation: str, 
            count: int) -> list:
        """Находим подходящих людей"""
        if int(sex) == 1:
            sex = 2
        else:
            sex = 1
        couples = self.users_search(bdate, sex, city_id, relation, count)

        for elem in couples["items"]:
            couple_info_temp = {
                "first_name": 0,
                "last_name": 0,
                "id": 0
            }
            couple_info_temp["first_name"] = elem["first_name"]
            couple_info_temp["last_name"] = elem["last_name"]
            couple_info_temp["id"] = elem["id"]
            all_couples_info.append(couple_info_temp)
        
        return all_couples_info


    def show_couple(self, couple_info: dict) -> str:
        """Собираем пользователю информацию о подходящей паре"""
        res = (
            f"{couple_info['first_name']} {couple_info['last_name']}\n"
            f"https://vk.com/id{couple_info['id']}"
        )
        
        return res


    def get_photos(self, couple_id: int) -> str:
        """
        Считает количество лайков и комментов, 
        возвращает строки с url фото
        
        """
        # Исключаем падение бота от парсинга закрытого профиля ВК 
        try:
            photos_info = self.photos_get(couple_id)
        except vk_api.exceptions.ApiError:
            return "closed profile" # У этого человека закрытый профиль

        photos_amount = photos_info["count"]
        photos_info_dict = dict()
        photo_urls_list = list()

        if photos_amount < 3:
            return "low_anount" # У этого человека кол-во фото меньше 3
        elif photos_amount > 50:
            photos_amount = 50

        for i in range(photos_amount):
            photos_info_dict[photos_info["items"][i]["id"]] = (
                photos_info["items"][i]["likes"]["count"] 
                + photos_info["items"][i]["comments"]["count"]
            )

        sorted_photos_dict = dict(
            sorted(photos_info_dict.items(), key=lambda x: -x[1])
            )
        photos_ids = list(sorted_photos_dict.keys())

        for i in range(3):
            photo_id = photos_ids[i]
            photo_url = (
                f"https://vk.com/id{couple_id}?"
                f"z=photo{couple_id}_{photo_id}"
                f"%2Falbum{couple_id}_0%2Frev"
                )
            photo_urls_list.append(photo_url)
            photo_urls_str = "\n".join(photo_urls_list)
        
        return photo_urls_str


    def searching_for_user(self) -> str:
        """
        Отправляет напоминание, что может сделать юзер во время поиска пары.
        
        """
        user_answer, vk_event = self.listen_answer()
        if user_answer == "дальше":
            return "next"
        elif user_answer == "стоп":
            return "stop"
        else:
            self.write_msg(
                vk_event.user_id, 
                "Если у вас нет слов, то, наверное, стоит связаться с \
                последним человеком) Иначе напишите 'дальше' или 'стоп'"
                )
            res = self.searching_for_user()
            
        return res


    def bot_logic(self) -> None:
        """Обрабатывает сообщения от пользователя"""
        request, vk_event = self.listen_answer()

        if request == "привет":
            # Инициализируем разговор с ботом и создаём базу данных
            self.write_msg(vk_event.user_id, f"Хай, {vk_event.user_id}")
            self.write_msg(
                vk_event.user_id, 
                """Вот мои команды:
                Найди пару - начать поиск пары
                Пока - завершить работу
                """)
            # Cоздаём БД
            create_db()

        elif request == "пока":
            # Прощаемся с ботом и завершаем его работу
            # Для возобновления работы необходимо повторно запустить скрипт
            self.write_msg(vk_event.user_id, "Пока((")
            quit()

        elif request == "найди пару":
            # Обнуляем предыдущий поиск.  
            # Уже выданные пользователи сохранены в БД.  
            couple_info_list = list()

            # Собираем информацию от пользователя
            self.write_msg(
                vk_event.user_id, 
                "Для кого? Введи id пользователя"
                )
            resp = self.get_seeker_info()

            # Проверяем чего не хватает
            self.check_info_completeness(seeker_scopes, resp, vk_event)
            self.write_msg(vk_event.user_id, "Информации достаточно")
            
            # Ищем пользователю подходящих людей предоставленной информации
            couple_info_list = self.find_couple(
                seeker_info["bdate"], 
                seeker_info["sex"], 
                seeker_info["city_id"], 
                seeker_info["relation"], 
                count
                )
            
            for elem in couple_info_list:
                # Проверяем есть ли эта пара в БД. 
                # Если есть - пропускаем, если нет - добавляем в БД.
                if check_exist(elem.get("id")) == True:
                    self.write_msg(
                        vk_event.user_id, 
                        "Этого человека уже смотрели... Ищем дальше..."
                        )
                    continue
                else:
                    add_couple(elem.get("id"))

                # Выдаём результат
                show_str = self.show_couple(elem)
                self.write_msg(vk_event.user_id, f"{show_str}")
                res_get_photos = self.get_photos(elem.get('id'))
                if res_get_photos == "closed profile":
                    self.write_msg(
                        vk_event.user_id, 
                        "У этого человека закрытый профиль, но он подходит. \
                        Может быть захотите связаться с ним?.."
                        )
                    continue
                elif res_get_photos == "low_anount":
                    self.write_msg(
                        vk_event.user_id, 
                        "У этого человека недостаточно фотографий профиля \
                        для оценки, но вы можете перейти на страничку"
                        )
                    continue
                else:
                    self.write_msg(vk_event.user_id, f"{res_get_photos}")

                # Спрашиваем выдавать ли ещё результаты
                self.write_msg(
                    vk_event.user_id, 
                    "Хотите увидеть следующего человека? Напишите: дальше"
                    )
                self.write_msg(
                    vk_event.user_id, 
                    "Если хотите на этом закончить, напишите: стоп"
                    )
                res = self.searching_for_user()
                if res == "next":
                    continue
                elif res == "stop":
                    break

            
            # После окончания, либо прерывания подбора, 
            # явно сообщаем пользователю об этом.
            self.write_msg(
                vk_event.user_id, 
                "На этом пока что всё. Возвращайтесь обязательно!"
                )    


        else:
            self.write_msg(vk_event.user_id, "Не поняла вашего ответа...")
            self.write_msg(vk_event.user_id, """Вот мои команды:
            Найди пару - начать поиск пары
            Пока - завершить работу 
            """)