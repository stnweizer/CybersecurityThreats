import streamlit as st
import pandas as pd
import plotly.express as px


st.set_page_config(page_title="Анализ кибератак по странам и отраслям", layout="wide")
st.title("Анализ кибератак по странам и отраслям")


@st.cache_data
def load_data():
    df = pd.read_csv("Global_Cybersecurity_Threats_2015-2024.csv")
    return df
df = load_data()


st.sidebar.header("Фильтры")
selected_country = st.sidebar.selectbox(
    "Страна",
    options=df['Country'].unique(),
    index=0
)
selected_industry = st.sidebar.selectbox(
    "Отрасль",
    options=df['Target Industry'].unique(),
    index=0
)
selected_threat = st.sidebar.selectbox(
    "Тип угрозы",
    options=df['Attack Type'].unique(),
    index=0
)
filtered_df = df[
    (df['Country'] == selected_country) &
    (df['Target Industry'] == selected_industry) &
    (df['Attack Type'] == selected_threat)
]



data_descr = pd.DataFrame({
    "Поле": [
        "Country", "Year", "Attack Type", "Attack Vector",
        "Target Industry", "Number of Affected Users",
        "Financial Loss (in Million $)", "Severity Level",
        "Incident Resolution Time (in Hours)", "Mitigation Strategy"
    ],
    "Описание": [
        "Страна, где произошла атака",
        "Год инцидента",
        "Тип киберугрозы (например, Malware, DDoS)",
        "Метод атаки (например, Phishing, SQL Injection)",
        "Целевая отрасль (например, Finance, Healthcare)",
        "Объем скомпрометированных данных в гигабайтах",
        "Оценочные финансовые потери в миллионах долларов",
        "Уровень серьезности: Low, Medium, High, Critical",
        "Время, затраченное на устранение атаки (в часах)",
        "Принятые контрмеры"
    ]
})
st.subheader("Описание полей данных")
st.dataframe(data_descr, hide_index=True, width=1000)



st.subheader("Распределение типов угроз")
st.write("Круговая диаграмма принимает страну (Country) и отрасль (Target Industry) для просмотра типов атак")
filtered_for_pie = df[
    (df['Country'] == selected_country) &
    (df['Target Industry'] == selected_industry)
]
threat_counts = filtered_for_pie['Attack Type'].value_counts().reset_index()
threat_counts.columns = ['Attack Type', 'Count']
fig_pie = px.pie(threat_counts,
                 names='Attack Type',
                 values='Count',
                 title='Распределение типов киберугроз',
                 hole=0.9)

st.plotly_chart(fig_pie)



st.subheader("Основные метрики")
st.write("Метрики принимают все значения фильтра - страну (Country), отрасль (Target Industry) и тип угрозы (Attack Type).")
total_impact = filtered_df['Financial Loss (in Million $)'].sum()
avg_response_time = filtered_df['Incident Resolution Time (in Hours)'].mean()
total_data_breached = filtered_df['Number of Affected Users'].sum()
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Общий финансовый ущерб, $M", value=f"${round(total_impact, 2)}")
with col2:
    st.metric(label="Среднее время реагирования, ч", value=f"{round(avg_response_time, 1)}")
with col3:
    st.metric(label="Утечено данных, ГБ", value=f"{round(total_data_breached, 2)}")



st.subheader("Количество атак по годам")
attacks_by_year = filtered_df['Year'].value_counts().reset_index()
attacks_by_year.columns = ['Year', 'Count']
attacks_by_year = attacks_by_year.sort_values('Year')
fig_line = px.line(attacks_by_year, x='Year', y='Count',
                   title='Количество атак по годам',
                   markers=True)
st.plotly_chart(fig_line)




st.subheader("Отфильтрованные данные для графика")
st.dataframe(filtered_df)

