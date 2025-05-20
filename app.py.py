import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime, timedelta
from io import BytesIO

API_KEY = '8VsRU-7b1-Pdx6indgKBtKp0oqCC99S9ybNJh3r_tas'  # Sua chave da HERE

def distancia_rota_here(lat_origem, lon_origem, lat_destino, lon_destino):
    url = 'https://router.hereapi.com/v8/routes'
    params = {
        'transportMode': 'car',
        'origin': f'{lat_origem},{lon_origem}',
        'destination': f'{lat_destino},{lon_destino}',
        'return': 'summary',
        'apikey': API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()
    try:
        distancia_metros = data['routes'][0]['sections'][0]['summary']['length']
        return distancia_metros / 1000  # km
    except Exception as e:
        st.error(f"Erro ao obter rota HERE: {e} | Dados: {data}")
        return None

def calcular_distancias(df):
    distancias = []
    total_registros = len(df)
    progresso = st.progress(0)
    status = st.empty()
    for idx, row in df.iterrows():
        dist = distancia_rota_here(
            row['Latitude_Filial'], row['Longitude_Filial'],
            row['Latitude_Municipio'], row['Longitude_Municipio']
        )
        distancias.append(dist)
        progresso.progress((idx + 1) / total_registros)
        status.text(f"Processando registro {idx + 1} de {total_registros}")
        time.sleep(0.1)
    status.empty()
    progresso.empty()
    df['Distancia_KM'] = distancias
    return df

st.title("Cálculo de Distâncias Rodoviárias (HERE API)")
st.write("Carregue um arquivo Excel com colunas de latitude e longitude para calcular as distâncias entre municípios e filiais.")
st.markdown(
    """
    <a href="https://dellavolpecombr-my.sharepoint.com/:x:/g/personal/marcos_silva_dellavolpe_com_br/EfZsiLDG_2tDuOfKbB6dBh8BJcp_EKEZoSvUlyAdDEX3Ww?e=8PqZeE" target="_blank">
    <a href="https://dellavolpecombr-my.sharepoint.com/personal/marcos_silva_dellavolpe_com_br/_layouts/15/download.aspx?share=EfZsiLDG_2tDuOfKbB6dBh8BJcp_EKEZoSvUlyAdDEX3Ww" target="_blank">
        <button style='background-color: #F7941D; color: white; padding: 10px 24px; border: none; border-radius: 4px; cursor: pointer;'>📥 Baixar modelo de planilha</button>
    </a>
    """,
    unsafe_allow_html=True
)

arquivo = st.file_uploader("📤 Faça upload do arquivo Excel", type=["xlsx"])

if arquivo is not None:
    if 'df_com_distancias' not in st.session_state:
        df = pd.read_excel(arquivo)
        st.success("Arquivo carregado com sucesso!")

        total_registros = len(df)
        tempo_estimado_segundos = total_registros * 0.1
        tempo_estimado = timedelta(seconds=tempo_estimado_segundos)
        st.info(f"Tempo estimado de execução: {tempo_estimado}")

        df_com_distancias = calcular_distancias(df)
        st.session_state['df_com_distancias'] = df_com_distancias

        # Gerar arquivo Excel em memória e guardar no estado
        output = BytesIO()
        df_com_distancias.to_excel(output, index=False)
        output.seek(0)
        st.session_state['arquivo_excel'] = output

    else:
        st.success("Arquivo já processado!")

    st.download_button(
        label="📥 Baixar arquivo com distâncias",
        data=st.session_state['arquivo_excel'],
        file_name=f'Distancias_Rodoviarias_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
