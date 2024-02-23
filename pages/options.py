import streamlit as st
import pandas as pd
import numpy as np

# Função para carregar e processar os dados do CSV
def carregar_dados(tipo_ativo):
    if tipo_ativo == "Açúcar":
        data = pd.read_csv('Dados Históricos - Açúcar NY nº11 Futuros (6).csv')
        valor_minimo_padrao = 20.0
        limite_inferior = 15
        limite_superior = 35
    elif tipo_ativo == "Dólar":
        data = pd.read_csv('USD_BRL Dados Históricos (2).csv')
        valor_minimo_padrao = 5.0
        limite_inferior = 4
        limite_superior = 6

    data = data.rename(columns={'Último': 'Close', 'Data': 'Date'})
    data['Date'] = pd.to_datetime(data['Date'], format='%d.%m.%Y')
    data = data.sort_values(by='Date', ascending=True)
    data['Close'] = data['Close'].str.replace(',', '.').astype(float)
    data['Daily Return'] = data['Close'].pct_change()

    return data, valor_minimo_padrao, limite_inferior, limite_superior

# Função para simulação Monte Carlo
def simulacao_monte_carlo(media_retornos_diarios, desvio_padrao_retornos_diarios, dias_simulados, num_simulacoes, limite_inferior, limite_superior, valor_strike):
    retornos_diarios_simulados = np.random.normal(media_retornos_diarios, desvio_padrao_retornos_diarios, (dias_simulados, num_simulacoes))

    preco_inicial = data['Close'].iloc[-1]
    precos_simulados = np.ones((dias_simulados + 1, num_simulacoes)) * preco_inicial

    valor_opcao = 0

    for dia in range(1, dias_simulados + 1):
        precos_simulados[dia, :] = precos_simulados[dia - 1, :] * (1 + retornos_diarios_simulados[dia - 1, :])
        precos_simulados[dia, :] = np.maximum(np.minimum(precos_simulados[dia, :], limite_superior), limite_inferior)

        valor_opcao += np.sum(np.maximum(precos_simulados[dia, :] - valor_strike, 0))

    valor_justo = valor_opcao / (num_simulacoes * dias_simulados)
    return valor_justo

# Função para simulação das calls
def simular_calls(dias_simulados, data, valor_minimo_padrao, limite_inferior, limite_superior):
    media_retornos_diarios = data['Daily Return'].mean()
    desvio_padrao_retornos_diarios = data['Daily Return'].std()
    num_simulacoes = 100000  # Alteração para 100000 simulações

    # Realizar a simulação para diferentes valores de preço da call
    precos_calls = []
    for preco_call in np.arange(limite_inferior, limite_superior + 0.25, 0.25):
        valor_justo = simulacao_monte_carlo(media_retornos_diarios, desvio_padrao_retornos_diarios, dias_simulados, num_simulacoes, limite_inferior, limite_superior, preco_call)
        precos_calls.append([preco_call, valor_justo])
    return precos_calls

# Configuração do título do aplicativo Streamlit e remoção da barra lateral
st.set_page_config(page_title="Simulação de Preços de Calls", page_icon="📈", layout="wide")

# Título do sidebar
st.sidebar.title('Simulação de Preços de Calls')

# Input dos valores desejados
tempo_desejado = st.sidebar.slider("Para quantos dias você quer avaliar o preço?", min_value=1, max_value=360, value=30)

# Carregar os dados
data, valor_minimo_padrao, limite_inferior, limite_superior = carregar_dados("Açúcar")

# Exibir a imagem
st.markdown('<img src="https://ibea.com.br/wp-content/uploads/2020/10/Capturar1.png" alt="logo" style="width:200px;">', unsafe_allow_html=True)

# Adicionar espaço antes do título
st.write("")

# Título
st.write("Preços das Calls para", tempo_desejado, "dias:")

# Botão para simular
if st.sidebar.button("Simular"):
    # Simulação das calls
    resultados = simular_calls(tempo_desejado, data, valor_minimo_padrao, limite_inferior, limite_superior)

    # Exibição dos resultados em forma de tabela
    df_resultados = pd.DataFrame(resultados, columns=["Strike", "Preço"])
    st.write(df_resultados)
