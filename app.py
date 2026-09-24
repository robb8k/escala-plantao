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

st.markdown("---")

# Gestão de Estado para as linhas dinâmicas de Militares / Atribuições
if "linhas_escala" not in st.session_state:
    st.session_state.linhas_escala = [
        {"num": "01", "militar": chefe_servico, "horario": "08:00 / 22:00 / 05:00", "atribuicao": "CHEFE DE SERVIÇO / VTR'S", "telefone": "33 98807-9755"},
        {"num": "02", "militar": "SGT DIONE", "horario": "10:00 / 16:00 / 00:00", "atribuicao": "A.C.S. / ALOJ. SGT / VTR'S", "telefone": "33 99833-9415"},
        {"num": "03", "militar": "SGT SOUZA", "horario": "14:00 / 20:00 / 01:40", "atribuicao": "MP / COZINHA E REFEITÓRIO", "telefone": "33 98864-5111"},
        {"num": "04", "militar": "CB VASCONCELOS", "horario": "12:00 / 18:00 / 03:20", "atribuicao": "MP / COMBATENTE / ALOJ. CB ESD", "telefone": "33 98727-8403"}
    ]

# Tabela Dinâmica: Militares / Atribuições
st.subheader("2. Militares / Atribuições")

colunas_tabela = st.columns([1, 2, 2, 2, 2, 1])
with colunas_tabela[0]: st.markdown("**Nº**")
with colunas_tabela[1]: st.markdown("**Militar**")
with colunas_tabela[2]: st.markdown("**Horário**")
with colunas_tabela[3]: st.markdown("**Atribuições / Faxina**")
with colunas_tabela[4]: st.markdown("**Telefone**")
with colunas_tabela[5]: st.markdown("**Ação**")

escala_atualizada = []
for i, item in enumerate(st.session_state.linhas_escala):
    c1, c2, c3, c4, c5, c6 = st.columns([1, 2, 2, 2, 2, 1])
    
    with c1:
        num = st.text_input(f"N_{i}", value=item["num"], key=f"num_{i}", label_visibility="collapsed")
    with c2:
        mil = st.text_input(f"Mil_{i}", value=item["militar"], key=f"mil_{i}", label_visibility="collapsed")
    with c3:
        hor = st.text_input(f"Hor_{i}", value=item["horario"], key=f"hor_{i}", label_visibility="collapsed")
    with c4:
        atr = st.text_input(f"Atr_{i}", value=item["atribuicao"], key=f"atr_{i}", label_visibility="collapsed")
    with c5:
        tel = st.text_input(f"Tel_{i}", value=item["telefone"], key=f"tel_{i}", label_visibility="collapsed")
    with c6:
        if st.button("❌", key=f"del_{i}"):
            pass # Tratado abaixo recriando a lista sem este índice
            
    escala_atualizada.append({"num": num, "militar": mil, "horario": hor, "atribuicao": atr, "telefone": tel, "del": c6})

# Botão para adicionar nova linha
if st.button("➕ Adicionar Militar / Atribuição"):
    novo_num = f"{len(st.session_state.linhas_escala) + 1:02d}"
    st.session_state.linhas_escala.append({"num": novo_num, "militar": "", "horario": "", "atribuicao": "", "telefone": ""})
    st.rerun()

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
    gu2_1 = st.text_input("Efetivo 2.1", value="SGT DIONE")
    gu2_2 = st.text_input("Efetivo 2.2", value="SGT ROBSON")
    gu2_3 = st.text_input("Efetivo 2.3", value="CB VASCONCELOS")

st.markdown("---")

if st.button("Gerar Escala Oficial", type="primary", use_container_width=True):
    st.success("Escala estruturada com sucesso!")
    
    data_formatada = data_plantao.strftime('%d DE %B DE %Y').upper()
    
    resultado_texto = f"""*ESCALA DE SERVIÇO - {ala_selecionada.upper()} - {cidade_local}, {data_formatada}*

*CHEFE DE SERVIÇO:* {chefe_servico}

*MILITARES / ATRIBUIÇÕES:*
"""
    for linha in st.session_state.linhas_escala:
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
        unsafe_app_html=True if 'unsafe_app_html' in globals() else True
    )
