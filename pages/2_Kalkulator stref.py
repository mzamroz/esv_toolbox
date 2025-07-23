import streamlit as st
import pandas as pd
from workalendar.europe import Poland
from datetime import datetime, timedelta

with st.sidebar:
    st.logo(
        'img/logo.svg',
        size='large'
        
    )

st.markdown("""
    <div style='text-align: center; padding: 1rem; border-radius: 5px; margin-bottom: 2rem;'>
        <h1>Kalkulator stref</h1>
        <p>Narzędzie do analizy plików pomiarowych</p>
    </div>
    """, unsafe_allow_html=True)


pd.options.mode.copy_on_write = True

TARIFS = [
    'ENERGA_A23_B23_C23',
    'ENERGA_B22_C22a',
    'ENERGA_C22b',
    'TAURON_A23_B23_C23_C13_G13',
    'TAURON_B22_C22a',
    'TAURON_C22b',
    'PGE_A23_B23_C23',
    'PGE_B22_C22a',
    'PGE_C22b',
    'ENEA_A23_B23',
    'ENEA_B22_C22a',
    'ENEA_B12',
    'ENEA_C22b',
    'PGE_ENERGETYKA_KOLEJOWA_B23',
    'PGE_ENERGETYKA_KOLEJOWA_B22_C22',
    'PGE_ENERGETYKA_KOLEJOWA_C22b',
    'ARCELORMITTAL_B23',
    'ARCELORMITTAL_C22a',
    'ARCELORMITTAL_C22b'
]

TARIFS_WITH_HOLIDAYS = [
    'ENERGA_A23_B23_C23',
    'TAURON_A23_B23_C23_C13_G13',
    'PGE_A23_B23_C23',
    'ENEA_A23_B23',
    'PGE_ENERGETYKA_KOLEJOWA_B23',
    'ARCELORMITTAL_B23',
]

def find_holidays(start_date, end_date):
    cal = Poland()
    start_year = start_date.year
    end_year = end_date.year

    if start_year == end_year:
        holidays = cal.holidays(start_year)
    if end_year - start_year == 1:
        holidays = cal.holidays(start_year) + cal.holidays(end_year)
    if end_year - start_year > 1:
        holidays = cal.holidays(start_year)
        for year in range(start_year + 1, end_year):
            holidays += cal.holidays(year)
        holidays += cal.holidays(end_year)

    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() == 5:
            holidays.append((current_date, 'Sobota'))
        elif current_date.weekday() == 6:
            holidays.append((current_date, 'Niedziela'))
        current_date += timedelta(days=1)
    return holidays

def create_zone_dataframe(start_date, end_date, zone_name, zones):
    date_range = pd.date_range(start=start_date, end=end_date, freq='h')
    df = pd.DataFrame(date_range, columns=['Timestamp'])

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    end_date += timedelta(days=1)

    holidays = find_holidays(start_date, end_date)
    
    zone_df = None
    for zone in zones:
        if zone_name in zone:
            zone_df = zone[zone_name]
            break
    
    if zone_df is None:
        raise ValueError(f"Zone '{zone_name}' not found in zones.")
    
    zone_data = []
    for timestamp in df['Timestamp']:
        month = timestamp.month
        hour = timestamp.hour
        zone_value = zone_df.iloc[hour-1, month]
        
        if zone_name in TARIFS_WITH_HOLIDAYS:
            for holiday in holidays:
                if holiday[0] == timestamp.date():
                    zone_value = "S3"
                    break
        
        zone_data.append(zone_value)
    
    df['Zone'] = zone_data
    return df

uploaded_file = st.file_uploader("Wgraj plik xls z profilem", type=['xls', 'xlsx'])

if uploaded_file is not None:
    # Wczytanie profilu
    profil = pd.read_excel(uploaded_file)
    profil = profil.drop(columns=['P,O,B'])
    profil = profil.drop(columns=['Unnamed: 27'])
    profil = profil.transpose()
    profil.reset_index(drop=True, inplace=True)
    profil = profil.iloc[:, :-3]
    profil.columns = profil.iloc[0]
    profil = profil[1:]
    profil.columns = ['Time' if pd.isna(col) else col for col in profil.columns]
    profil.columns = profil.columns.astype(str)
    
    for col in profil.columns:
        if len(col) > 10:
            date = col[0:10]
            month = date[5:7]
            day = date[8:10]
            year = date[0:4]
            date = day + '.' + month + '.' + year
            profil.rename(columns={col: date}, inplace=True)

    # Wczytanie stref
    zones = []
    xls = pd.ExcelFile('./input/strefy_new.xlsx')
    for sheet_name in xls.sheet_names:
        a = pd.read_excel(xls, sheet_name=sheet_name)
        zones.append({sheet_name:a})

    # Wybór taryfy
    selected_tariff = st.selectbox("Wybierz OSD i grupę taryfową:", TARIFS)
    
    if selected_tariff:
        start_date = profil.columns[1]
        end_date = profil.columns[-1]

        start_date = datetime.strptime(start_date, '%d.%m.%Y')
        start_date = start_date.strftime('%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%d.%m.%Y')
        end_date += timedelta(days=1)
        end_date = end_date.strftime('%Y-%m-%d')

        zone_df = create_zone_dataframe(start_date, end_date, selected_tariff, zones)
        zone_df['ECP'] = None

        for i, row in zone_df.iterrows():
            timestamp = row['Timestamp']
            hour = timestamp.hour
            day = timestamp.day
            month = timestamp.month
            year = timestamp.year
            if hour == 0:
                hour = 24
            if hour < 10:
                hour = f"0{hour}:00"
            else:
                hour = f"{hour}:00"
            if day < 10:
                day = f"0{day}"
            if month < 10:
                month = f"0{month}"
            date = f"{day}.{month}.{year}"

            try:
                ecp_value = profil.loc[profil['Time'] == hour, date].values[0]
            except:
                ecp_value = None
                
            zone_df.at[i, 'ECP'] = ecp_value

        last_row = profil.iloc[-1]
        non_nan_values = last_row.dropna().tolist()
        ecp_value = non_nan_values[-1]

        s1_zone_df = zone_df[zone_df['Zone'] == 'S1']
        s2_zone_df = zone_df[zone_df['Zone'] == 'S2']
        s3_zone_df = zone_df[zone_df['Zone'] == 'S3']

        s1_zone_df['ECP'] = pd.to_numeric(s1_zone_df['ECP'], errors='coerce')
        s2_zone_df['ECP'] = pd.to_numeric(s2_zone_df['ECP'], errors='coerce')
        s3_zone_df['ECP'] = pd.to_numeric(s3_zone_df['ECP'], errors='coerce')

        total_ecp_sum = round(zone_df['ECP'].apply(pd.to_numeric, errors='coerce').sum() + ecp_value, 2)
        s1_ecp_sum = round(s1_zone_df['ECP'].sum(), 2)
        
        if selected_tariff in TARIFS_WITH_HOLIDAYS:
            s3_ecp_sum = round(s3_zone_df['ECP'].sum() + ecp_value, 2)
        else:
            s3_ecp_sum = 0
            
        if selected_tariff not in TARIFS_WITH_HOLIDAYS:
            s2_ecp_sum = round(s2_zone_df['ECP'].sum() + ecp_value, 2)
        else:
            s2_ecp_sum = round(s2_zone_df['ECP'].sum(), 2)

        s1_percent = round(s1_ecp_sum / total_ecp_sum * 100, 2)
        s2_percent = round(s2_ecp_sum / total_ecp_sum * 100, 2)
        try:
            s3_percent = round(s3_ecp_sum / total_ecp_sum * 100, 2)
        except:
            s3_percent = 0

        # Wyświetlenie wyników
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Zużycie energii w strefach:")
            st.write(f"S1: **{s1_ecp_sum} kWh** ({s1_percent}%)")
            st.write(f"S2: **{s2_ecp_sum} kWh** ({s2_percent}%)")
            st.write(f"S3: **{s3_ecp_sum} kWh** ({s3_percent}%)")
            st.write(f"Suma: **{total_ecp_sum} kWh**")

        with col2:
            # Możesz dodać wykres kołowy
            import plotly.graph_objects as go
            
            fig = go.Figure(data=[go.Pie(
                labels=['Strefa 1', 'Strefa 2', 'Strefa 3'],
                values=[s1_ecp_sum, s2_ecp_sum, s3_ecp_sum],
                hole=.3
            )])
            
            st.plotly_chart(fig)
