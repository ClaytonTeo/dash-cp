import pandas as pd
import streamlit as st
from datetime import datetime
import calendar
import plotly.graph_objects as go

# --- Configuração da página ---
st.set_page_config(page_title="CONTROLE DE PACING", page_icon="📊", layout="wide")

# --- Box com dias restantes do mês ---
hoje = datetime.today()
ultimo_dia = calendar.monthrange(hoje.year, hoje.month)[1]
dias_restantes = ultimo_dia - hoje.day

col1, col2 = st.columns([4, 1])
with col1:
    st.title("CONTROLE DE PACING")
with col2:
    st.markdown(f"<b>Dias restantes: {dias_restantes}</b>", unsafe_allow_html=True)

# --- Dados de exemplo ---
data = {
    "CAMPAIGN": ["free-fire | search | purchase", "free-fire | youtube | purchase",
                 "free-fire | meta | consideration", "free-fire | meta | purchase",
                 "cod | search | purchase", "cod | youtube | purchase",
                 "cod | meta | consideration", "cod | meta | purchase",
                 "mobile-legends | search | purchase", "mobile-legends | meta | purchase",
                 "genshin-impact | search | purchase", "genshin-impatc | youtube | purchase",
                 "genshin-impact | meta | purchase", "valorant | search | purchase",
                 "valorant | youtube | purchase", "valorant | meta | purchase",
                 "wild rift | search | purchase", "wild rift | meta | purchase",
                 "apex | search | purchase", "apex | meta | purchase",
                 "diablo immortal | search | purchase", "diablo immortal | meta | purchase"],
    "VEÍCULO": ["GOOGLE","GOOGLE","META","META","GOOGLE","GOOGLE","META","META",
                "GOOGLE","META","GOOGLE","GOOGLE","META","GOOGLE","GOOGLE","META",
                "GOOGLE","META","GOOGLE","META","GOOGLE","META"],
    "LEAD (META)": [2105,80,294,1176,1429,654,147,1324,1800,1029,2000,22,588,429,393,74,125,368,125,368,112,714],
    "CPL (META)": [0.76,5.00,0.68,0.68,0.56,1.07,0.68,0.68,0.50,0.68,0.65,9.00,0.68,1.40,0.89,0.68,2.00,0.68,2.00,0.68,0.89,0.56],
    "BUDGET": [1600,400,200,800,800,700,100,900,900,700,1300,200,400,600,350,50,250,250,250,250,100,400],
    "VEÍCULADO": [800,230,100,450,400,370,50,480,500,350,700,100,200,300,200,30,150,150,110,110,50,250],
    "RESIDUAL": [800,170,100,350,400,330,50,420,400,350,600,100,200,300,150,20,100,100,140,140,50,150],
    "LEADS REALIZADOS": [1000,40,150,600,750,400,70,700,950,540,1100,12,350,230,200,45,65,200,65,250,65,450],
    "CPL REALIZADO": [0.80,5.75,0.67,0.75,0.53,0.93,0.71,0.69,0.53,0.65,0.64,8.33,0.57,1.30,1.00,0.67,2.31,0.75,1.69,0.44,0.77,0.56],
    "% PACING META": [47.50,50.00,51.00,51.00,52.50,61.14,47.60,52.89,52.78,52.46,55.00,54.00,59.50,53.67,50.86,61.20,52.00,54.40,52.00,68.00,57.85,63.00]
}
df = pd.DataFrame(data)

# --- Cálculos totais para indicadores ---
veiculado_total = df['VEÍCULADO'].sum()
budget_total = df['BUDGET'].sum()
leads_realizados_total = df['LEADS REALIZADOS'].sum()
leads_meta_total = df['LEAD (META)'].sum()
cpl_realizado_medio = df['CPL REALIZADO'].mean()
cpl_meta_medio = df['CPL (META)'].mean()

# --- Criar coluna de pacing ideal ---
df["PACING IDEAL/DIA"] = df["RESIDUAL"] / dias_restantes

# --- Reorganizar colunas para que fique à direita de RESIDUAL ---
cols = df.columns.tolist()
pos_residual = cols.index("RESIDUAL")
# Inserir a nova coluna logo após RESIDUAL
cols.insert(pos_residual + 1, cols.pop(cols.index("PACING IDEAL/DIA")))
df = df[cols]

# --- Bloco de 3 gráficos de “cronômetro” ---
st.subheader("Visão Geral do Pacing")
col1, col2, col3 = st.columns(3)

colors_gradient = ["#baf5e6", "#8ccebd", "#0bdfb1"]

# Função auxiliar para criar gauges
def create_gauge(value, reference, title, is_currency=False, max_factor=1.2, invert_delta=False):
    delta_config = {
        'reference': reference,
        'position': "top",
        'valueformat': ".2f" if is_currency else ",.0f",
        'prefix': "$" if is_currency else ""
    }

    # Só inverte o comportamento da seta se for CPL
    if invert_delta:
        delta_config['increasing'] = {'color': "#dc2626"}  # acima da meta = ruim (vermelho)
        delta_config['decreasing'] = {'color': "#16a34a"}  # abaixo da meta = bom (verde)

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        number={
            'prefix': "$" if is_currency else "",
            'valueformat': ".2f" if is_currency else ",.0f"
        },
        delta=delta_config,
        gauge={
            'axis': {'range': [0, reference*max_factor]},
            'bar': {'color': "#005aa3"},
            'steps': [
                {'range': [0, reference*0.5], 'color': colors_gradient[0]},
                {'range': [reference*0.5, reference*0.8], 'color': colors_gradient[1]},
                {'range': [reference*0.8, reference*max_factor], 'color': colors_gradient[2]}
            ],
        },
        title={'text': title},
        domain={'x': [0, 1], 'y': [0, 1]}
    ))
    fig.update_layout(margin={'t':50,'b':0,'l':0,'r':0})
    return fig

# 1. Veiculado x Budget (sem alteração)
col1.plotly_chart(
    create_gauge(veiculado_total, budget_total, "REALIZADO BUDGET"),
    use_container_width=True
)

# 2. Leads Realizados x Meta (sem alteração)
col2.plotly_chart(
    create_gauge(leads_realizados_total, leads_meta_total, "REALIZADO LEADS"),
    use_container_width=True
)

# 3. CPL Realizado x Meta (em USD) → seta invertida
col3.plotly_chart(
    create_gauge(
        cpl_realizado_medio,
        cpl_meta_medio,
        "REALIZADO CPL",
        is_currency=True,
        max_factor=1.5,
        invert_delta=True
    ),
    use_container_width=True
)



# --- Funções de formatação ---
def format_leads(value):
    return f"{int(value):,}".replace(",", ".")

def format_currency(value):
    return f"US$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- CSS para reduzir fonte das métricas ---
st.markdown("""
<style>
div[data-testid="stMetricValue"] { font-size: 70% !important; }
div[data-testid="stMetricLabel"] { font-size: 70% !important; }
</style>
""", unsafe_allow_html=True)

# --- Função de exibição de métricas ---
def display_platform_overview(df_platform, titulo):
    budget_total = df_platform['BUDGET'].sum()
    leads_total = df_platform['LEAD (META)'].sum()
    cpl_medio = df_platform['CPL (META)'].mean()
    leads_realizados = df_platform['LEADS REALIZADOS'].sum()
    budget_realizado = df_platform['VEÍCULADO'].sum()
    pacing_realizado = leads_realizados / leads_total * 100 if leads_total > 0 else 0

    st.markdown(f"### {titulo}")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Budget", format_currency(budget_total))
    col2.metric("Leads", format_leads(leads_total))
    col3.metric("CPL", format_currency(cpl_medio))
    col4.metric("Budget Realizado", format_currency(budget_realizado))
    col5.metric("Leads Realizados", format_leads(leads_realizados))
    col6.metric("Pacing Realizado", f"{pacing_realizado:.2f}%")

# --- Exibir métricas por plataforma ---
display_platform_overview(df[df['VEÍCULO']=="GOOGLE"], "Google Ads")
display_platform_overview(df[df['VEÍCULO']=="META"], "Meta Ads")


# --- Dias percorridos (já tem 'hoje' e 'dias_restantes' no seu código) ---
dias_percorridos = max(1, hoje.day)  # evita divisão por zero; considera o dia corrente

# (opcional) coluna de auditoria para checagem
df["PACING REAL/DIA"] = df["VEÍCULADO"] / dias_percorridos

# --- Função de cor por comparação de pacing ---
def pacing_color(real_diario, ideal_diario, tolerancia=0.05):
    # casos sem dado
    if pd.isna(real_diario) or pd.isna(ideal_diario) or ideal_diario == 0:
        return ''
    diff_rel = (real_diario - ideal_diario) / ideal_diario
    # dentro da faixa
    if abs(diff_rel) <= tolerancia:
        return 'background-color: #16a34a; color: white;'  # verde
    # abaixo do ideal -> amarelo
    if real_diario < ideal_diario:
        return 'background-color: #facc15; color: #111827;'  # amarelo (texto escuro p/ legibilidade)
    # acima do ideal -> vermelho
    return 'background-color: #dc2626; color: white;'  # vermelho

# --- Função de estilização da tabela (cor só em VEÍCULADO) ---
def style_table(df):
    df_styled = df.style

    # aplica estilo linha a linha, pintando apenas a célula da coluna VEÍCULADO
    def row_style(row):
        styles = [''] * len(row)
        # garante que as colunas existem
        if 'VEÍCULADO' in row.index and 'PACING IDEAL/DIA' in row.index:
            style_cell = pacing_color(
                real_diario = row.get('VEÍCULADO', pd.NA) / dias_percorridos,
                ideal_diario = row.get('PACING IDEAL/DIA', pd.NA),
                tolerancia = 0.05
            )
            col_idx = row.index.get_loc('VEÍCULADO')
            styles[col_idx] = style_cell
        return styles

    df_styled = df_styled.apply(row_style, axis=1)

    # cabeçalho
    df_styled = df_styled.set_table_styles([{
        'selector': 'th',
        'props': [('background-color', "#FF6A25"), ('color', 'white'), ('font-weight', 'bold')]
    }])

    # formatação (mantém a nova coluna ideal/dia sem gradiente)
    df_styled = df_styled.format({
        'BUDGET': '${:,.2f}',
        'VEÍCULADO': '${:,.2f}',
        'RESIDUAL': '${:,.2f}',
        'PACING IDEAL/DIA': '${:,.2f}',
        'PACING REAL/DIA': '${:,.2f}',  # opcional, se decidir exibir
        'CPL (META)': '${:.2f}',
        'CPL REALIZADO': '${:.2f}',
        'LEAD (META)': '{:,}',
        'LEADS REALIZADOS': '{:,}',
        '% PACING META': '{:.2f}%'
    })

    return df_styled

# --- Exibir tabela principal ---
st.subheader("Controle de Pacing - Campanhas")
st.write(style_table(df))

# --- Sidebar: pesquisa por campanha ---
st.sidebar.header("Pesquisa por Nome de Campanha")
termo_pesquisa = st.sidebar.text_input("Digite o nome ou parte do nome da campanha:")

if termo_pesquisa:
    df_filtrado = df[df['CAMPAIGN'].str.lower().str.contains(termo_pesquisa.lower())].copy()
    if not df_filtrado.empty:
        total_row = pd.DataFrame({
            'CAMPAIGN': ["TOTAL"],
            'VEÍCULO': [""],
            'LEAD (META)': [df_filtrado['LEAD (META)'].sum()],
            'CPL (META)': [df_filtrado['CPL (META)'].mean()],
            'BUDGET': [df_filtrado['BUDGET'].sum()],
            'VEÍCULADO': [df_filtrado['VEÍCULADO'].sum()],
            'RESIDUAL': [df_filtrado['RESIDUAL'].sum()],
            'LEADS REALIZADOS': [df_filtrado['LEADS REALIZADOS'].sum()],
            'CPL REALIZADO': [df_filtrado['CPL REALIZADO'].mean()],
            '% PACING META': [df_filtrado['% PACING META'].mean()]
        })
        df_filtrado = pd.concat([df_filtrado, total_row], ignore_index=True)
        st.subheader(f"Resultados da Pesquisa: '{termo_pesquisa}'")
        st.write(style_table(df_filtrado))
    else:
        st.warning("Nenhuma campanha encontrada.")
else:
    st.info("Digite um termo no campo de pesquisa para filtrar a campanha.")



