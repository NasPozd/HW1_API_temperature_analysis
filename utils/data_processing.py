import numpy as np
from joblib import Parallel, delayed
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA


def clean_data(data):
    data = data.dropna()
    return data

def analyze_historical_data(data):
    """
    - Скользящее среднее и стандартное отклонение используются для сглаживания краткосрочных колебаний температуры и выявления долгосрочных трендов
    - Группировка данных по сезонам и вычисление статистик (среднее и стандартное отклонение) выполняется параллельно для ускорения обработки
    - Температура считается аномальной, если она выходит за пределы скользящее среднее ± 2σ
    """

    data = data.copy()
    
    # Вычисление скользящего среднего и стандартного отклонения
    data['rolling_mean'] = data['temperature'].rolling(window=30).mean()
    data['rolling_std'] = data['temperature'].rolling(window=30).std()

    # Распараллеливание группировки по сезону
    def calculate_seasonal_stats(group):
        return group['temperature'].agg(['mean', 'std'])

    seasonal_stats = Parallel(n_jobs=-1)(
        delayed(calculate_seasonal_stats)(group)
        for _, group in data.groupby('season')
    )
    seasonal_stats = pd.concat(seasonal_stats, keys=data['season'].unique()).reset_index()

    # Выявление аномалий
    data['anomaly'] = np.where(
        (data['temperature'] < (data['rolling_mean'] - 2 * data['rolling_std'])) |
        (data['temperature'] > (data['rolling_mean'] + 2 * data['rolling_std'])),
        True, False
    )

    return data, seasonal_stats

def forecast_temperature(data, steps=30):
    """
    - ARIMA модель используется для прогнозирования температуры на 30 дней вперед. Порядок модели (5, 1, 0) выбран эмпирически
    - Перед прогнозированием проверяется наличие столбца temperature и достаточное количество данных (минимум 30 точек)
    - Результат прогноза возвращается в виде DataFrame с датами и прогнозируемыми значениями температуры
    """
    
    data = data.copy()
    data.loc[:, 'timestamp'] = pd.to_datetime(data['timestamp'])
    
    if 'temperature' not in data.columns:
        raise ValueError("Столбец 'temperature' отсутствует в данных.")
    
    if len(data) < 30:
        raise ValueError("Недостаточно данных для прогнозирования. Требуется минимум 30 точек.")
    
    model = ARIMA(data['temperature'], order=(5, 1, 0))
    model_fit = model.fit()
    
    forecast = model_fit.forecast(steps=steps)
    forecast_df = pd.DataFrame(forecast).rename(columns={'predicted_mean':'Прогноз'})
    forecast_df['Дата'] = pd.date_range(start=data['timestamp'].max() + pd.DateOffset(days=1), periods=steps)
    
    forecast_df = forecast_df[['Дата', 'Прогноз']].set_index("Дата")
    
    return forecast_df