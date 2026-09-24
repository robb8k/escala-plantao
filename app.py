import streamlit as st
from datetime import datetime
import urllib.parse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

st.set_page_config(
    page_title="Escala Operacional",
    page_icon="📋",
    layout="wide"
)

# Estilização CSS Tática (Grafite e Laranja Queimado)
st.markdown("""
<style>
    .stApp {
        background-color: #1E1B1A;
        color: #E6E1E0;
    }
    h1, h2, h3 {
        color: #C2410C !important;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        background-color: #2D2827 !important;
        color: #FFFFFF !important;
        border: 1px solid #4A4240 !important;
        border-radius: 8px !important;
    }
    .stButton button[kind="primary"], div.stButton > button {
        background-color: #C2410C !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        transition: background 0.3s ease;
    }
    .stButton button:hover {
        background-color: #9A3206 !important;
    }
    hr {
        border-color: #4A4240 !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
# Escala Operacional
""")

# Campos de Cabeçalho do Plantão
col_ala, col_c1, col_c2, col_c3 = st.columns(4)

with col_ala:
    ala_selecionada = st.selectbox("Ala Operacional:", ["1ª Ala Operacional", "2ª Ala Operacional", "3ª Ala Operacional", "4ª Ala Operacional"])
with col_c1:
    cidade_local = st.text_input("Local / Cidade", value="TEÓFILO OTONI")
with col_c2:
    data_plantao = st.date_input("Data do Plantão", value=datetime.today())
with col_c3:
    chefe_servico = st.text_input("Chefe de Serviço", value="SGT MUNIZ")

acs_servico = st.text_input("ACS (Adjunto do Chefe de Serviço)", value="SGT DIONE")

st.markdown("---")

# 2. Tabela de Sentinelas e Atribuições
st.subheader("2. Escala de Sentinela / Rádio Operador e Atribuições")

colunas_tabela = st.columns([1, 2, 2, 2, 2])

with colunas_tabela[0]: st.markdown("**Nº**")
with colunas_tabela[1]: st.markdown("**Militar**")
with colunas_tabela[2]: st.markdown("**Horário**")
with colunas_tabela[3]: st.markdown("**Atribuições / Faxina**")
with colunas_tabela[4]: st.markdown("**Telefone**")

dados_iniciais = [
    ("01", chefe_servico, "08:00 / 22:00 / 05:00", "CHEFE DE SERVIÇO / VTR'S", "33 98807-9755"),
    ("02", acs_servico, "10:00 / 16:00 / 00:00", "A.C.S. / ALOJ. SGT / VTR'S", "33 99833-9415"),
    ("03", "SGT SOUZA", "14:00 / 20:00 / 01:40", "MP / COZINHA E REFEITÓRIO", "33 98864-5111"),
    ("04", "CB VASCONCELOS", "12:00 / 18:00 / 03:20", "MP / COMBATENTE / ALOJ. CB ESD", "33 98727-8403"),
    ("05", "CB HENDRIK", "BANCO DE HORAS", "XXXX", "33 98816-9539")
]

escala_linhas = []
for i, (n_padrao, militar_padrao, horario_padrao, atribuicao_padrao, tel_padrao) in enumerate(dados_iniciais):
    c1, c2, c3, c4, c5 = st.columns([1, 2, 2, 2, 2])
    with c1:
        num = st.text_input(f"N_{i}", value=n_padrao, key=f"num_{i}", label_visibility="collapsed")
    with c2:
        mil = st.text_input(f"Mil_{i}", value=militar_padrao, key=f"mil_{i}", label_visibility="collapsed")
    with c3:
        hor = st.text_input(f"Hor_{i}", value=horario_padrao, key=f"hor_{i}", label_visibility="collapsed")
    with c4:
        atr = st.text_input(f"Atr_{i}", value=atribuicao_padrao, key=f"atr_{i}", label_visibility="collapsed")
    with c5:
        tel = st.text_input(f"Tel_{i}", value=tel_padrao, key=f"tel_{i}", label_visibility="collapsed")
    
    escala_linhas.append({"num": num, "militar": mil, "horario": hor, "atribuicao": atr, "telefone": tel})

st.markdown("---")

# 3. Quadro de Guarnições
st.subheader("3. Guarnições Empenhadas")
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.markdown("##### 1ª GU BM")
    gu1_1 = st.text_input("Efetivo 1.1", value=chefe_servico)
    gu1_2 = st.text_input("Efetivo 1.2", value="CB VASCONCELOS")
    gu1_3 = st.text_input("Efetivo 1.3", value="SGT ROBSON")

with col_g2:
    st.markdown("##### 2ª GU BM")
    gu2_1 = st.text_input("Efetivo 2.1", value=acs_servico)
    gu2_2 = st.text_input("Efetivo 2.2", value="SGT ROBSON")
    gu2_3 = st.text_input("Efetivo 2.3", value="CB VASCONCELOS")

st.markdown("---")

if st.button("Gerar Escala Oficial", type="primary", use_container_width=True):
    st.success("Escala estruturada com sucesso!")
    
    data_formatada = data_plantao.strftime('%d DE %B DE %Y').upper()
    
    resultado_texto = f"""*ESCALA DE SERVIÇO - {ala_selecionada.upper()} - {cidade_local}, {data_formatada}*

*CHEFE DE SERVIÇO:* {chefe_servico}
*ACS:* {acs_servico}

*ESCALA DE SENTINELA / RÁDIO OPERADOR:*
"""
    for linha in escala_linhas:
        resultado_texto += f"- {linha['num']} | {linha['militar']} | {linha['horario']} | {linha['atribuicao']} | Tel: {linha['telefone']}\n"
    
    resultado_texto += f"""
*GUARNIÇÕES:*
*1ª GU BM:* {gu1_1}, {gu1_2}, {gu1_3}
*2ª GU BM:* {gu2_1}, {gu2_2}, {gu2_3}
"""
    
    st.code(resultado_texto, language="markdown")
    
    texto_wapp = urllib.parse.quote(resultado_texto)
    url_whatsapp = f"https://api.whatsapp.com/send?text={texto_wapp}"
    st.markdown(
        f'<a href="{url_whatsapp}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:12px; border-radius:8px; font-weight:bold; cursor:pointer;">🟢 Enviar Escala via WhatsApp</button></a>',
        unsafe_allow_html=True
    )
