import streamlit as st
import pandas as pd
from utils.data_processing import clean_data, analyze_historical_data, forecast_temperature
from utils.api_requests import get_current_temperature, get_current_temperature_async
from utils.plotting import plot_seasonal_heatmap, plot_temperature_distribution, plot_temperature, plot_seasonal_decompose
import asyncio
import time

# Инициализация сессионных состояний
if 'api_key' not in st.session_state:
    st.session_state.api_key = None

if 'period' not in st.session_state:
    st.session_state.period = '365'

if 'city_data' not in st.session_state:
    st.session_state.city_data = None

if 'current_temp' not in st.session_state:
    st.session_state.current_temp = None

# Основной код приложения
st.title("Мониторинг температуры")

# Загрузка файла с историческими данными
uploaded_file = st.file_uploader("Загрузите файл с историческими данными", type=["csv"])
if uploaded_file is not None:
    st.session_state.city_data = pd.read_csv(uploaded_file)
    st.success("Файл успешно загружен!")
    st.write(st.session_state.city_data.head())

# Выбор города из загруженного файла
if st.session_state.city_data is not None:
    # Извлекаем уникальные города из данных
    cities = st.session_state.city_data['city'].unique()
    city = st.selectbox("Выберите город", options=cities)
else:
    st.warning("Загрузите файл с историческими данными, чтобы выбрать город")

# Ввод API-ключа
api_key = st.text_input("Введите ваш API-ключ OpenWeatherMap", value=st.session_state.api_key)
if api_key:
    st.session_state.api_key = api_key

# Получение текущей температуры (синхронно)
if st.button("Получить текущую температуру (синхронно)"):
    if st.session_state.api_key:
        start_time = time.time()
        st.session_state.current_temp = get_current_temperature(city, st.session_state.api_key)
        end_time = time.time()
        if st.session_state.current_temp is not None:
            st.write(f"Текущая температура в {city}: {st.session_state.current_temp} °C")
            st.write(f"Время работы: {end_time - start_time:.2f} секунд")
            # Проверка на аномальность
            if st.session_state.city_data is not None:
                city_data = st.session_state.city_data[st.session_state.city_data['city'] == city]
                historical_mean = city_data['temperature'].mean()
                historical_std = city_data['temperature'].std()
                if (st.session_state.current_temp < (historical_mean - 2 * historical_std)) or (st.session_state.current_temp > (historical_mean + 2 * historical_std)):
                    st.warning("Текущая температура является аномальной для этого сезона")
                else:
                    st.success("Текущая температура в пределах нормы для этого сезона")
    else:
        st.error("Пожалуйста, введите API-ключ")

# Получение текущей температуры (асинхронно)
if st.button("Получить текущую температуру (асинхронно)"):
    if st.session_state.api_key:
        start_time = time.time()
        async def get_temp_async():
            st.session_state.current_temp = await get_current_temperature_async(city, st.session_state.api_key)
            end_time = time.time()
            if st.session_state.current_temp is not None:
                st.write(f"Текущая температура в {city}: {st.session_state.current_temp} °C")
                st.write(f"Время работы: {end_time - start_time:.2f} секунд")
                # Проверка на аномальность
                if st.session_state.city_data is not None:
                    city_data = st.session_state.city_data[st.session_state.city_data['city'] == city]
                    historical_mean = city_data['temperature'].mean()
                    historical_std = city_data['temperature'].std()
                    if (st.session_state.current_temp < (historical_mean - 2 * historical_std)) or (st.session_state.current_temp > (historical_mean + 2 * historical_std)):
                        st.warning("Текущая температура является аномальной для этого сезона")
                    else:
                        st.success("Текущая температура в пределах нормы для этого сезона")

        asyncio.run(get_temp_async())
    else:
        st.error("Пожалуйста, введите API-ключ")

# Отображение статистики по историческим данным
if st.session_state.city_data is not None:
    cleaned_data = clean_data(st.session_state.city_data)
    city_data = cleaned_data[cleaned_data['city'] == city]  # Фильтрация данных по выбранному городу
    analysis_results, seasonal_stats = analyze_historical_data(city_data)  # Анализ данных для выбранного города
    show_anomalies = st.checkbox("Показать только аномалии")

    if show_anomalies:
        analysis_results = analysis_results[analysis_results['anomaly'] == True]

    st.write("Результаты анализа исторических данных:")
    st.write(analysis_results)
    st.write("Сезонная статистика:")
    st.write(seasonal_stats)

    # Построение графиков
    period = st.text_input("Введите период для сезонного разложения (например, 365)", value=st.session_state.period)
    st.session_state.period = period

    if st.button("Построить графики"):
        if not analysis_results.empty:
            required_columns = ['timestamp', 'temperature', 'rolling_mean', 'anomaly']
            if all(col in analysis_results.columns for col in required_columns):
                plot_seasonal_heatmap(st, city_data)
                plot_temperature_distribution(st, city_data)
                plot_temperature(st, analysis_results)
                try:
                    plot_seasonal_decompose(st, analysis_results, period=st.session_state.period)
                except Exception as e:
                    st.warning(f"Ошибка при построении сезонного разложения: {e}")
            else:
                st.warning("Отсутствуют необходимые столбцы для построения графиков")
        else:
            st.warning("Нет данных для построения графиков")
    
    if st.button("Прогнозировать температуру на 30 дней"):
        forecast = forecast_temperature(city_data)
        st.write("Прогноз температуры на следующие 30 дней:")
        st.write(forecast)