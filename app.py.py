import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime, timedelta
from io import BytesIO

API_KEY = '8VsRU-7b1-Pdx6indgKBtKp0oqCC99S9ybNJh3r_tas'  # Substitua pela sua chave da HERE se necessário

def parse_float(value):
    """Converte strings com vírgula para float (ex: '19,501' -> 19.501)"""
    if isinstance(value, str):
        value = value.replace(',', '.')
    try:
        return float(value)
    except:
        return None

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

st.set_page_config(page_title="Distâncias Rodoviárias", layout="centered")

st.title("🛣️ Cálculo de Distâncias Rodoviárias (HERE API)")
st.write("Carregue um arquivo Excel com as colunas de latitude e longitude da Filial e do Município para calcular a distância via rota real.")

st.markdown(
    """
    <a href="https://dellavolpecombr-my.sharepoint.com/personal/marcos_silva_dellavolpe_com_br/_layouts/15/download.aspx?share=EfZsiLDG_2tDuOfKbB6dBh8BJcp_EKEZoSvUlyAdDEX3Ww" target="_blank">
        <button style='background-color: #F7941D; color: white; padding: 10px 24px; border: none; border-radius: 4px; cursor: pointer;'>📥 Baixar modelo de planilha</button>
    </a>
    """,
    unsafe_allow_html=True
)

arquivo = st.file_uploader("📤 Faça upload do arquivo Excel", type=["xlsx"])

if arquivo is not None:
    try:
        df = pd.read_excel(arquivo)
        st.success("Arquivo carregado com sucesso!")

        # Converter colunas de string com vírgula para float
        for coluna in ['Latitude_Filial', 'Longitude_Filial', 'Latitude_Municipio', 'Longitude_Municipio']:
            df[coluna] = df[coluna].apply(parse_float)

        # Verificar se alguma conversão falhou
        if df[['Latitude_Filial', 'Longitude_Filial', 'Latitude_Municipio', 'Longitude_Municipio']].isnull().any().any():
            st.error("Há valores inválidos nas colunas de latitude/longitude. Verifique se todas as coordenadas estão no formato numérico.")
        else:
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
                status.text(f"🔄 Processando registro {idx + 1} de {total_registros}")
                time.sleep(0.1)

            df['Distancia_KM'] = distancias

            # Salvar em memória para download
            output = BytesIO()
            df.to_excel(output, index=False)
            output.seek(0)

            st.success("✅ Processamento finalizado! Faça o download abaixo:")
            st.download_button(
                label="📥 Baixar planilha com distâncias",
                data=output,
                file_name=f'Distancias_Rodoviarias_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
