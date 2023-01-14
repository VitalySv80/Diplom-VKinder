import requests


class VkInfo:
    url = 'https://api.vk.com/method/'
    VERSION = '5.131'

    def __init__(self, token):
        self.token = token
        self.version = self.VERSION
        self.params = {'access_token': self.token,
                       'v': self.version
                       }

    def check_token(self, id=1):
        check_url = self.url + 'users.get'
        user_params = {'user_ids': id}
        response = requests.get(check_url, params={**self.params, **user_params})
        result = response.json()
        if 'error' in result:
            return 'error'
        else:
            return id

    def get_user_info(self, id_vk):
        """Получаем информацию о пользователе и возвращаем значения пола, города и возраста.
            Если какого-то значения нет возвращается ошибка"""
        user_url = self.url + 'users.get'
        user_params = {'user_ids': id_vk,
                       'fields': 'sex, bdate, city'
                       }
        response = requests.get(user_url, params={**self.params, **user_params})
        result = response.json()
        if 'error' in result:
            return 'error'
        if 'sex' not in result['response'][0]:
            return 'error'
        else:
            user_sex = result['response'][0]['sex']
        if 'city' not in result['response'][0]:
            return 'error'
        else:
            user_city = result['response'][0]['city']['id']
        if 'bdate' not in result['response'][0] or len(result['response'][0]['bdate'].split('.')[-1]) != 4:
            return 'error'
        else:
            user_year = result['response'][0]['bdate'].split('.')[-1]
        if user_sex == 1:
            user_sex = 2
        else:
            user_sex = 1
        return user_sex, user_city, user_year

    def search_users(self, user_sex, user_city, user_year):
        """Ищем людей по заданным параметрам. Статус по умолчанию выставлен 'В активном поиске'.
           Возвращаем список ID найденных пользователей"""
        search_url = self.url + 'users.search'
        user_params = {'sex': user_sex,
                       'birth_year': user_year,
                       'status': '6',
                       'city': user_city,
                       'count': 1000,
                       'has_photo': 1
                       }
        response = requests.get(search_url, params={**self.params, **user_params})
        result = response.json()
        users_list_id = []
        for el in result['response']['items']:
            if el['can_access_closed'] == True:
                users_list_id.append(int(el['id']))
        return users_list_id

    def get_city(self, title):
        """На вход получаем название города, возвращаем id"""
        city_url = self.url + 'database.getCities'
        city_params = {"q": title,
                       "country_id": 1,
                       "count": 1}
        response = requests.get(city_url, params={**self.params, **city_params})
        result = response.json()
        city_id = result['response']['items'][0]['id']
        return city_id

    def find_user_by_name(self, name):
        """Ищем пользователя по фамилии и имени. Если пользователь не найден
            или пользователей больше 1 возвращается ошибка"""
        user_url = self.url + 'users.search'
        user_params = {"q": name}
        response = requests.get(user_url, params={**self.params, **user_params})
        result = response.json()
        if 'error' in result or result['response']['count'] == 0 or result['response']['count'] > 1:
            return 'error'
        user_id = result['response']['items'][0]['id']
        return user_id

    def get_photos(self, id_vk):
        """Получаем не более 3 фотографий наилучшего качества. Метод возвращает ссписок названия фотографий
            для дальнейшего их использования в чат-боте VK"""
        photos_url = self.url + 'photos.get'
        photos_params = {'owner_id': id_vk,
                         'album_id': 'profile',
                         'photo_sizes': 1,
                         'extended': 1
                        }
        response = requests.get(photos_url, params={**self.params, **photos_params})
        result = response.json()
        user_list = []
        final_list = []
        for photo in result['response']['items']:
            user_dict = {}
            sorted_list = sorted(photo['sizes'], key=lambda m: m['width'], reverse=True)
            user_dict['rating'] = photo['comments']['count'] + photo['likes']['count']
            user_dict['link'] = sorted_list[0]['url']
            user_dict['owner_id'] = photo['owner_id']
            user_dict['id'] = photo ['id']
            user_list.append(user_dict)
        user_list = sorted(user_list, key=lambda k: k['rating'], reverse=True)
        for i in user_list[0:3]:
            photo = 'photo' + str(i['owner_id']) + '_' + str(i['id'])
            final_list.append(photo)
        return final_list
