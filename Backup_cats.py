import requests
import os
import json
from datetime import datetime


class CatImageUploader:
    def __init__(self, yandex_token):
        self.yandex_token = yandex_token
        self.group_name = "PD-140"
        self.base_url = "https://cataas.com/cat/says"
        self.yandex_api_url = "https://cloud-api.yandex.net/v1/disk/resources"
        self.json_filename = "uploaded_files.json" # Здесь собираем инфо о загруженных файлах

    def get_cat_image(self, text):
        """Получает картинку кота с текстом с cataas.com"""
        url = f"{self.base_url}/{text}"
        response = requests.get(url)

        if response.status_code == 200:
            return response.content
        else:
            raise Exception(f"Ошибка получения картинки: {response.status_code}")

    def create_yandex_folder(self):
        """Создает папку на Яндекс.Диске с названием группы"""
        headers = {
            "Authorization": f"OAuth {self.yandex_token}"
        }

        params = {
            "path": f"/{self.group_name}"
        }

        response = requests.put(self.yandex_api_url, headers=headers, params=params)

        # Папка уже существует - это нормально
        if response.status_code not in [201, 409]:
            raise Exception(f"Ошибка создания папки: {response.status_code}")

    def upload_to_yandex(self, image_data, filename):
        """Загружает картинку на Яндекс.Диск"""
        # 1. Получаем ссылку для загрузки
        headers = {
            "Authorization": f"OAuth {self.yandex_token}"
        }

        params = {
            "path": f"/{self.group_name}/{filename}.jpg",
            "overwrite": "true"
        }

        response = requests.get(f"{self.yandex_api_url}/upload",
                                headers=headers,
                                params=params)

        if response.status_code != 200:
            raise Exception(f"Ошибка получения ссылки: {response.status_code}")

        upload_url = response.json()["href"]

        # 2. Загружаем файл
        response = requests.put(upload_url, data=image_data)

        if response.status_code != 201:
            raise Exception(f"Ошибка загрузки файла: {response.status_code}")

        return True

    def get_file_size(self, filename):
        """Получает РАЗМЕР файла на Яндекс.Диске"""
        headers = {
            "Authorization": f"OAuth {self.yandex_token}"
        }

        params = {
            "path": f"/{self.group_name}/{filename}.jpg"
        }

        response = requests.get(self.yandex_api_url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            return data.get("size", 0)  # Возвращаем ТОЛЬКО размер
        return 0

    def save_to_json(self, file_size, text, filename):
        """Сохраняет информацию о РАЗМЕРЕ файла в единый JSON файл с накоплением"""
        # Подготавливаем данные (ТОЛЬКО размер и основная информация)
        new_file_data = {
            "text": text,
            "filename": f"{filename}.jpg",
            "size": file_size,  # ← ТОЛЬКО РАЗМЕР!
            "upload_timestamp": datetime.now().isoformat()
        }

        # Читаем существующие данные или создаем новые
        if os.path.exists(self.json_filename):
            try:
                with open(self.json_filename, 'r', encoding='utf-8') as f:
                    all_data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                all_data = {"files": []}
        else:
            all_data = {"files": []}

        # Добавляем новый файл
        all_data["files"].append(new_file_data)

        # Сохраняем обновленные данные
        with open(self.json_filename, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)

        print(f" Информация о размере файла добавлена в {self.json_filename}")
        print(f" Всего файлов: {len(all_data['files'])}")

        return self.json_filename

    def run(self):
        """Основной метод выполнения задания"""
        try:
            # 1. Получаем данные от пользователя
            text = input("Введите текст для картинки: ").strip()

            if not text:
                print("Текст не может быть пустым!")
                return

            # 2. Получаем картинку кота с текстом
            print("Получаем картинку с котиком...")
            image_data = self.get_cat_image(text)
            print("Картинка получена")

            # 3. Создаем папку на Яндекс.Диске
            print(f"Создаем папку '{self.group_name}' на Яндекс.Диске...")
            self.create_yandex_folder()
            print("Папка создана/проверена")

            # 4. Загружаем картинку на Яндекс.Диск
            filename = text.replace(" ", "_")  # Заменяем пробелы на подчеркивания
            print(f"Загружаем картинку '{filename}.jpg'...")
            self.upload_to_yandex(image_data, filename)
            print("Картинка загружена")

            # 5. Получаем РАЗМЕР файла
            file_size = self.get_file_size(filename)
            print(f"Размер файла: {file_size} байт")

            # 6. Сохраняем информацию о РАЗМЕРЕ в единый JSON файл
            json_file = self.save_to_json(file_size, text, filename)

            print("\n" + "=" * 50)
            print("Файл загружен!")
            print("=" * 50)
            print(f"Папка на Яндекс.Диске: {self.group_name}")
            print(f"Файл: {filename}.jpg")
            print(f"Размер: {file_size} байт")
            print(f"JSON файл: {json_file}")
            print(f"Всего записей в JSON: {len(json.load(open(json_file, 'r'))['files'])}")
            print("=" * 50)

        except Exception as e:
            print(f"Ошибка: {e}")


def main():
    # Получаем токен от пользователя
    yandex_token = input("Введите токен с Полигона Яндекс.Диска: ").strip()

    if not yandex_token:
        print("Токен не может быть пустым!")
        return

    uploader = CatImageUploader(yandex_token)
    uploader.run()


if __name__ == "__main__":
    main()