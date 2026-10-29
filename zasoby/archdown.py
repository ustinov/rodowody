#!/usr/bin/env python3
"""Модуль для завантаження зображень з архіву ЦДІАК."""

import argparse
import re
import sys
import urllib.error
import urllib.request

BASE_URL = "https://archium.cdiak.archives.gov.ua"


def get_images_map(url: str) -> dict:
    """
    Завантажує HTML-сторінку та формує словник {номер_сторінки: url_файлу}.
    """
    req = urllib.request.Request(
        url,
        headers={'User-Agent':
                 'Mozilla/5.0 (X11; Linux x86_64; rv:157.0)'
                 ' Gecko/20100101 Firefox/157.0'
                 }
    )
    try:
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
    except urllib.error.URLError as err:
        print(f"Помилка доступу до {url}: {err}")
        sys.exit(1)

    # Використовуємо re.compile для кращої читабельності та швидкості
    pattern = re.compile(
        r'data-observe-src="(/static/files/[^"]+)".*?'
        r'<span class="number-of-page" data-page="(\d+)">',
        re.DOTALL
    )
    matches = pattern.findall(html)

    return {int(page_str): (BASE_URL + path) for path, page_str in matches}


def download_image(img_url: str, filename: str) -> None:
    """
    Завантажує одне зображення за вказаним URL і зберігає його на диск.
    """
    req = urllib.request.Request(
        img_url,
        headers={'User-Agent':
                 'Mozilla/5.0 (X11; Linux x86_64; rv:157.0)'
                 ' Gecko/20100101 Firefox/157.0'
                }
    )
    try:
        with urllib.request.urlopen(req) as response:
            with open(filename, 'wb') as out_file:
                out_file.write(response.read())
        print(f"Завантажено {filename}")
    except urllib.error.URLError as err:
        print(f"Помилка завантаження {filename}: {err}")


def main() -> None:
    """
    Основна функція обробки аргументів командного рядка та запуску.
    """
    parser = argparse.ArgumentParser(
        description="Завантаження зображень з архіву ЦДІАК."
    )
    parser.add_argument(
        dest='group',
        type=int,
        help="Номер справи (групи) для завантаження, наприклад: 132928"
    )
    parser.add_argument(
        "-s", "--start",
        type=int,
        default=0,
        help="Початковий номер сторінки (за замовчуванням: 0)"
    )
    parser.add_argument(
        "-e", "--end",
        type=int,
        default=None,
        help="Кінцевий номер сторінки (за замовчуванням: остання сторінка)"
    )

    args = parser.parse_args()
    viewer_url = f"{BASE_URL}/file-viewer/{args.group}"

    print(f"Отримую структуру архіву з {viewer_url}...")
    images_map = get_images_map(viewer_url)

    if not images_map:
        print(f"Не знайдено жодного зображення для справи {args.group}.")
        sys.exit(1)

    start_page = args.start
    # Встановлюємо максимальний знайдений номер, якщо -e не передано явно
    end_page = args.end if args.end is not None else max(images_map.keys())

    print(f"Фільтрую діапазон {start_page}-{end_page}...\n")

    for page_num in range(start_page, end_page + 1):
        if page_num in images_map:
            img_url = images_map[page_num]
            filename = f"{args.group}_Зображення_{page_num}.jpg"
            download_image(img_url, filename)
        elif page_num > 0:
            print(f"Зображення з логічним номером {page_num} не знайдено.")

    print("\nЗавершено!")


if __name__ == "__main__":
    main()
