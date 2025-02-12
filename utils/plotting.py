import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
import seaborn as sns
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def plot_temperature_distribution(st, data):
    bins = np.arange(data['temperature'].min(), data['temperature'].max() + 1, 1)
    fig = px.histogram(data, x='temperature', nbins=len(bins) - 1, range_x=[data['temperature'].min(), data['temperature'].max()], title='Распределение температур')
    fig.update_layout(xaxis_title='Температура (°C)', yaxis_title='Количество')
    fig.update_traces(marker_line_color='gray', marker_line_width=1)
    st.plotly_chart(fig)

def plot_temperature(st, data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['timestamp'], y=data['temperature'], mode='lines', name='Температура'))
    fig.add_trace(go.Scatter(x=data['timestamp'], y=data['rolling_mean'], mode='lines', name='Скользящее среднее', line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=data['timestamp'][data['anomaly']], y=data['temperature'][data['anomaly']], mode='markers', name='Аномалии', marker=dict(color='red')))
    fig.update_layout(title='Температура с аномалиями', xaxis_title='Дата', yaxis_title='Температура (°C)')
    st.plotly_chart(fig)

def plot_seasonal_decompose(st, data, period='365'):    
    result = seasonal_decompose(data['temperature'], model='additive', period=int(period))    
    with st.container():
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(x=data['timestamp'], y=result.trend, mode='lines', name='Тренд'))
        fig_trend.update_layout(title='Тренд', xaxis_title='Дата', yaxis_title='Температура (°C)')
        st.plotly_chart(fig_trend, use_container_width=True)
        
        fig_seasonal = go.Figure()
        fig_seasonal.add_trace(go.Scatter(x=data['timestamp'], y=result.seasonal, mode='lines', name='Сезонность'))
        fig_seasonal.update_layout(title='Сезонность', xaxis_title='Дата', yaxis_title='Температура (°C)')
        st.plotly_chart(fig_seasonal, use_container_width=True)
        
        fig_resid = go.Figure()
        fig_resid.add_trace(go.Scatter(x=data['timestamp'], y=result.resid, mode='lines', name='Остатки'))
        fig_resid.update_layout(title='Шум', xaxis_title='Дата', yaxis_title='Температура (°C)')
        st.plotly_chart(fig_resid, use_container_width=True)
    
def plot_seasonal_heatmap(st, data):
    data = data.copy()
    
    data.loc[:, 'year'] = pd.to_datetime(data['timestamp']).dt.year
    data.loc[:, 'month'] = pd.to_datetime(data['timestamp']).dt.month
    
    heatmap_data = data.pivot_table(index='year', columns='month', values='temperature', aggfunc='mean')
    
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale='Viridis'
    ))
    fig.update_layout(title='Тепловая карта температур по месяцам и годам', xaxis_title='Месяц', yaxis_title='Год')
    st.plotly_chart(fig)