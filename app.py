import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3

def main():
    st.set_page_config(page_title="Анализ кибератак", layout="wide")
    connection = sqlite3.connect("cyber_attacks.db")
    cursor = connection.cursor()
    # Сайдбар с фильтрами
    st.sidebar.header("Фильтры")
    # уникальные страны для фильтра
    cursor.execute(
        "SELECT DISTINCT Country FROM attacks WHERE Country IS NOT NULL ORDER BY Country"
    )
    unique_countries = ['Все'] + [row[0] for row in cursor.fetchall()]
    country = st.sidebar.selectbox("Страна", unique_countries)
    # уникальные отрасли
    cursor.execute(
        "SELECT DISTINCT `Target Industry` FROM attacks WHERE `Target Industry` IS NOT NULL ORDER BY `Target Industry`"
    )
    unique_industries = ['Все'] + [row[0] for row in cursor.fetchall()]
    industry = st.sidebar.selectbox("Отрасль", unique_industries)
    # уникальные типы атак
    cursor.execute(
        "SELECT DISTINCT `Attack Type` FROM attacks WHERE `Attack Type` IS NOT NULL ORDER BY `Attack Type`"
    )
    unique_attack_types = ['Все'] + [row[0] for row in cursor.fetchall()]
    attack_type = st.sidebar.selectbox("Тип атаки", unique_attack_types)
    # уникальные источники атак
    cursor.execute(
        "SELECT DISTINCT `Attack Source` FROM attacks WHERE `Attack Source` IS NOT NULL ORDER BY `Attack Source`"
    )
    unique_sources = ['Все'] + [row[0] for row in cursor.fetchall()]
    source = st.sidebar.selectbox("Источник атаки", unique_sources)
    # Формируем условия для фильтрации
    where_parts = []
    if country != 'Все':
        where_parts.append(f"Country = '{country}'")
    if industry != 'Все':
        where_parts.append(f"`Target Industry` = '{industry}'")
    if attack_type != 'Все':
        where_parts.append(f"`Attack Type` = '{attack_type}'")
    if source != 'Все':
        where_parts.append(f"`Attack Source` = '{source}'")
    where_sql = " AND ".join(where_parts) if where_parts else "1=1"
    # Основные метрики
    st.header("Ключевые показатели")
    cursor.execute(f"SELECT COUNT(*) FROM attacks WHERE {where_sql}")
    total_attacks = cursor.fetchone()[0]
    cursor.execute(
        f"SELECT SUM(`Financial Loss (in Million $)`) FROM attacks WHERE {where_sql}"
    )
    financial_loss = cursor.fetchone()[0] or 0
    cursor.execute(
        f"SELECT SUM(`Number of Affected Users`) FROM attacks WHERE {where_sql}"
    )
    affected_users = cursor.fetchone()[0] or 0
    cursor.execute(
        f"SELECT AVG(`Incident Resolution Time (in Hours)`) FROM attacks WHERE {where_sql}"
    )
    resolution_time = cursor.fetchone()[0] or 0
    metric1, metric2, metric3, metric4 = st.columns(4)
    with metric1:
        st.metric("Всего атак", f"{total_attacks:,}".replace(",", " "))
    with metric2:
        st.metric(
            "Ущерб (млн)",
            f"{financial_loss:,.3f}".replace(",", " ").replace(".", " ")
        )
    with metric3:
        st.metric("Пострадало", f"{affected_users:,}".replace(",", " "))
    with metric4:
        st.metric("Время реагирования", f"{resolution_time:.1f} ч")
    st.header("Анализ по странам и специалищациям хакеров")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Топ 10 стран по количеству атак")
        cursor.execute(
            f"""
            SELECT Country, COUNT(*) as count
            FROM attacks
            WHERE {where_sql}
            GROUP BY Country
            ORDER BY count DESC
            LIMIT 10
        """
        )
        country_attacks = pd.DataFrame(cursor.fetchall(), columns=['Country', 'count'])
        if not country_attacks.empty:
            fig = px.bar(country_attacks, x='Country', y='count', color='Country')
            st.plotly_chart(fig, use_container_width=True)
            st.metric(
                f"Лидер: {country_attacks.iloc[0]['Country']}",
                f"{country_attacks.iloc[0]['count']:,} атак"
            )
        else:
            st.warning("Нет данных для отображения")
    with col2:
        st.subheader("Топ 10 стран по финансовому ущербу")
        cursor.execute(
            f"""
            SELECT Country, SUM(`Financial Loss (in Million $)`) as loss
            FROM attacks
            WHERE {where_sql}
            GROUP BY Country
            ORDER BY loss DESC
            LIMIT 10
        """
        )
        country_loss = pd.DataFrame(cursor.fetchall(), columns=['Country', 'loss'])
        if not country_loss.empty:
            fig = px.bar(country_loss, x='Country', y='loss', color='Country')
            st.plotly_chart(fig, use_container_width=True)
            st.metric(
                f"Лидер по ущербу: {country_loss.iloc[0]['Country']}",
                f"{country_loss.iloc[0]['loss']:,.3f}".replace(",", " ").replace(".", " ")
            )
        else:
            st.warning("Нет данных для отображения")

    st.subheader("Специализация хакеров по отраслям")
    cursor.execute(
        f"""
        SELECT `Attack Source`, `Target Industry`, COUNT(*) as Count
        FROM attacks
        WHERE {where_sql}
        GROUP BY `Attack Source`, `Target Industry`
        ORDER BY Count DESC
    """
    )
    hacker_specialization = pd.DataFrame(
        cursor.fetchall(),
        columns=['Attack Source', 'Target Industry', 'Count']
    )
    if not hacker_specialization.empty:
        pivot_data = hacker_specialization.pivot(
            index='Attack Source',
            columns='Target Industry',
            values='Count'
        ).fillna(0)
        fig = px.imshow(pivot_data, color_continuous_scale='Viridis')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Нет данных для отображения")
    st.header("Анализ данных по атакам")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Типы атак")
        cursor.execute(
            f"""
            SELECT `Attack Type`, COUNT(*) as count
            FROM attacks
            WHERE {where_sql}
            GROUP BY `Attack Type`
            ORDER BY count DESC
        """
        )
        attack_types = pd.DataFrame(
            cursor.fetchall(),
            columns=['Attack Type', 'count']
        )
        if not attack_types.empty:
            fig = px.pie(attack_types, names='Attack Type', values='count', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Нет данных для отображения")
    with col2:
        st.subheader("Источники атак")
        cursor.execute(
            f"""
            SELECT `Attack Source`, COUNT(*) as count
            FROM attacks
            WHERE {where_sql}
            GROUP BY `Attack Source`
            ORDER BY count DESC
        """
        )
        attack_sources = pd.DataFrame(
            cursor.fetchall(),
            columns=['Attack Source', 'count']
        )
        if not attack_sources.empty:
            fig = px.bar(attack_sources, x='Attack Source', y='count', color='Attack Source')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Нет данных для отображения")
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Атаки по годам")
        cursor.execute(
            f"""
            SELECT Year, COUNT(*) as count
            FROM attacks
            WHERE {where_sql}
            GROUP BY Year
            ORDER BY Year
        """
        )
        yearly_attacks = pd.DataFrame(
            cursor.fetchall(),
            columns=['Год', 'Число']
        )
        if not yearly_attacks.empty:
            fig = px.line(yearly_attacks, x='Год', y='Число', markers=True)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Нет данных для отображения")
    with col4:
        st.subheader("Уязвимости")
        cursor.execute(
            f"""
            SELECT `Security Vulnerability Type`, COUNT(*) as count
            FROM attacks
            WHERE {where_sql}
            GROUP BY `Security Vulnerability Type`
            ORDER BY count DESC
        """
        )
        vulnerabilities = pd.DataFrame(
            cursor.fetchall(),
            columns=['Security Vulnerability Type', 'count']
        )
        if not vulnerabilities.empty:
            fig = px.bar(
                vulnerabilities,
                x='Security Vulnerability Type',
                y='count',
                color='Security Vulnerability Type'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Нет данных для отображения")
    col5, col6 = st.columns(2)
    with col5:
        st.subheader("Ущерб по группировкам")
        cursor.execute(
            f"""
            SELECT `Attack Source`, SUM(`Financial Loss (in Million $)`) as loss
            FROM attacks
            WHERE {where_sql}
            GROUP BY `Attack Source`
            ORDER BY loss DESC
        """
        )
        source_loss = pd.DataFrame(
            cursor.fetchall(),
            columns=['Attack Source', 'loss']
        )
        if not source_loss.empty:
            fig = px.bar(source_loss, x='Attack Source', y='loss', color='Attack Source')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Нет данных для отображения")
    with col6:
        st.subheader("Финансовый ущерб по типам атак")
        cursor.execute(
            f"""
            SELECT `Attack Type`, SUM(`Financial Loss (in Million $)`) as loss
            FROM attacks
            WHERE {where_sql}
            GROUP BY `Attack Type`
            ORDER BY loss DESC
        """
        )
        attack_loss_df = pd.DataFrame(
            cursor.fetchall(),
            columns=['Attack Type', 'loss']
        )
        if not attack_loss_df.empty:
            fig = px.bar(
                attack_loss_df,
                x='Attack Type',
                y='loss',
                color='Attack Type'
            )
            st.plotly_chart(fig, use_container_width=True)
            top_attack_type = attack_loss_df.iloc[0]['Attack Type']
            top_loss_amount = attack_loss_df.iloc[0]['loss']
            st.metric(
                label="Тип атаки с наибольшим ущербом",
                value=f"{top_attack_type}: {top_loss_amount:,.3f} млн $".replace(",", " ").replace(".", " ")
            )
        else:
            st.warning("Нет данных для отображения")
    st.subheader("Тренды активности группировок по годам")
    cursor.execute(
        f"""
        SELECT Year, `Attack Source`, COUNT(*) as count
        FROM attacks
        WHERE {where_sql}
        GROUP BY Year, `Attack Source`
        ORDER BY Year
    """
    )
    trends_df = pd.DataFrame(
        cursor.fetchall(),
        columns=['Year', 'Attack Source', 'count']
    )
    if not trends_df.empty:
        fig = px.line(trends_df, x='Year', y='count', color='Attack Source', markers=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Нет данных для отображения")
    # Статистика
    st.sidebar.header("Статистика")
    cursor.execute("SELECT COUNT(*) FROM attacks")
    total_records = cursor.fetchone()[0]
    cursor.execute("SELECT MIN(Year), MAX(Year) FROM attacks")
    min_year, max_year = cursor.fetchone()
    st.sidebar.write(f"Всего записей: {total_records:,}")
    st.sidebar.write(f"Отфильтровано: {total_attacks:,}")
    st.sidebar.write(f"Охват: {min_year}-{max_year} гг.")
if __name__ == "__main__":
    conn = sqlite3.connect("cyber_attacks.db")
    df = pd.read_csv("Global_Cybersecurity_Threats_2015-2024.csv")
    df.to_sql('attacks', conn, index=False, if_exists='replace')
    conn.close()
    print("База данных создана")
    main()
