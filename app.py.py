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

st.title("Cálculo de Distâncias Rodoviárias (HERE API)")
st.write("Carregue um arquivo Excel com colunas de latitude e longitude para calcular as distâncias entre municípios e filiais.")
st.write("Arquivo de referência: https://dellavolpecombr-my.sharepoint.com/:x:/g/personal/marcos_silva_dellavolpe_com_br/EfZsiLDG_2tDuOfKbB6dBh8BJcp_EKEZoSvUlyAdDEX3Ww?e=8PqZeE .")

arquivo = st.file_uploader("📤 Faça upload do arquivo Excel", type=["xlsx"])

if arquivo is not None:
    df = pd.read_excel(arquivo)
    st.success("Arquivo carregado com sucesso!")
    
    total_registros = len(df)
    tempo_estimado_segundos = total_registros * 0.1
    tempo_estimado = timedelta(seconds=tempo_estimado_segundos)
    
    st.info(f"Tempo estimado de execução: {tempo_estimado}")
    progresso = st.progress(0)
    status = st.empty()

    distancias = []
    for idx, row in df.iterrows():
        dist = distancia_rota_here(
            row['Latitude_Filial'], row['Longitude_Filial'],
            row['Latitude_Municipio'], row['Longitude_Municipio']
        )
        distancias.append(dist)
        progresso.progress((idx + 1) / total_registros)
        status.text(f"Processando registro {idx + 1} de {total_registros}")
        time.sleep(0.1)
    
    df['Distancia_KM'] = distancias
    
    # Salvar resultado em memória para download
    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    
    st.success("Processo finalizado! Faça o download abaixo:")
    st.download_button(
        label="📥 Baixar arquivo com distâncias",
        data=output,
        file_name=f'Distancias_Rodoviarias_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
