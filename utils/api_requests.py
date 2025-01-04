import aiohttp
import streamlit as st
import requests

async def fetch_temperature(session, url):
    async with session.get(url) as response:
        if response.status == 200:
            data = await response.json()
            return data['main']['temp']
        else:
            st.error(f"Ошибка API: {response.status}")
            return None

async def get_current_temperature_async(city, api_key):
    """
    - Используется aiohttp для выполнения асинхронного запроса, что позволяет не блокировать выполнение программы во время ожидания ответа от API
    - Проверяется статус ответа, и в случае ошибки выбрасывается исключение с соответствующим сообщением
    """
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    async with aiohttp.ClientSession() as session:
        return await fetch_temperature(session, url)

def get_current_temperature(city, api_key):
    """
    - Используется синхронный запрос к OpenWeatherMap API для получения текущей температуры в выбранном городе
    - В случае ошибки (например, неверный API ключ) выводится сообщение об ошибке
    """
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url)
        response.raise_for_status()  # Проверка на ошибки
        data = response.json()
        return data['main']['temp']
    except requests.exceptions.HTTPError as err:
        st.error(f"Ошибка API: {err}")
        return None