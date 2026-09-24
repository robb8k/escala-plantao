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

# Estilização CSS Tática (Grafite e Laranja Queimado) e compactação de margens e inputs
st.markdown("""
<style>
    .stApp {
        background-color: #1E1B1A;
        color: #E6E1E0;
    }
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
    }
    h1, h2, h3 {
        color: #C2410C !important;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        background-color: #2D2827 !important;
        color: #FFFFFF !important;
        border: 1px solid #4A4240 !important;
        border-radius: 6px !important;
        padding: 4px 8px !important;
        font-size: 14px !important;
    }
    .stButton button[kind="primary"], div.stButton > button {
        background-color: #C2410C !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: bold !important;
        transition: background 0.3s ease;
    }
    .stButton button:hover {
        background-color: #9A3206 !important;
    }
    hr {
        border-color: #4A4240 !important;
        margin: 1rem 0 !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
# Escala Operacional
""")

# Campos de Cabeçalho do Plantão
col_ala, col_c1, col_c2, col_c3 = st.columns(4)

with col_ala:
    ala_selecionada = st.selectbox("Ala Operacional", ["1ª Ala Operacional", "2ª Ala Operacional", "3ª Ala Operacional", "4ª Ala Operacional"])
with col_c1:
    cidade_local = st.text_input("Local / Cidade", value="TEÓFILO OTONI")
with col_c2:
    data_plantao = st.text_input("Data:", value=datetime.today().strftime('%d/%m/%Y'))
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
st.subheader("Militares / Atribuições")

colunas_tabela = st.columns([1, 2, 2, 2, 2, 1])
with colunas_tabela[0]: st.markdown("**Nº**")
with colunas_tabela[1]: st.markdown("**Militar**")
with colunas_tabela[2]: st.markdown("**Horário**")
with colunas_tabela[3]: st.markdown("**Atribuições / Faxina**")
with colunas_tabela[4]: st.markdown("**Telefone**")
with colunas_tabela[5]: st.markdown("**Ação**")

linhas_temp = []
indice_remover_militar = None

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
        if st.button("❌", key=f"del_mil_{i}"):
            indice_remover_militar = i
            
    linhas_temp.append({"num": num, "militar": mil, "horario": hor, "atribuicao": atr, "telefone": tel})

if indice_remover_militar is not None:
    st.session_state.linhas_escala.pop(indice_remover_militar)
    st.rerun()
else:
    st.session_state.linhas_escala = linhas_temp

if st.button("Adicionar"):
    novo_num = f"{len(st.session_state.linhas_escala) + 1:02d}"
    st.session_state.linhas_escala.append({"num": novo_num, "militar": "", "horario": "", "atribuicao": "", "telefone": ""})
    st.rerun()

st.markdown("---")

# Gestão de Estado para Guarnições Dinâmicas e Compactas Lado a Lado
if "lista_guarnicoes" not in st.session_state:
    st.session_state.lista_guarnicoes = [
        {"nome": "1ª GU BM", "militares": [chefe_servico, "CB VASCONCELOS"]},
        {"nome": "2ª GU BM", "militares": ["SGT DIONE", "SGT ROBSON"]}
    ]

st.subheader("Guarnições")

acao_remover_guarnicao = None
acao_adicionar_militar_guarnicao = None
acao_remover_militar_guarnicao = None

# Exibição lado a lado em 2 colunas de cartões compactos
cols_guarnicoes = st.columns(2)

for g_idx, guarnicao in enumerate(st.session_state.lista_guarnicoes):
    col_alvo = cols_guarnicoes[g_idx % 2]
    
    with col_alvo:
        with st.container(border=True):
            # Cabeçalho da Guarnição super compacto
            c_nome, c_del = st.columns([5, 1])
            with c_nome:
                guarnicao["nome"] = st.text_input("Guarnição", value=guarnicao["nome"], key=f"g_nome_{g_idx}", label_visibility="collapsed")
            with c_del:
                if st.button("🗑️", key=f"del_g_{g_idx}", help="Remover Guarnição"):
                    acao_remover_guarnicao = g_idx
            
            # Militares da Guarnição em lista compacta
            for m_idx, militar_nome in enumerate(guarnicao["militares"]):
                c_mil, c_del_m = st.columns([6, 1])
                with c_mil:
                    guarnicao["militares"][m_idx] = st.text_input(f"Militar {m_idx+1}", value=militar_nome, key=f"g_{g_idx}_m_{m_idx}", label_visibility="collapsed")
                with c_del_m:
                    if st.button("❌", key=f"del_g_{g_idx}_m_{m_idx}", help="Remover Militar"):
                        acao_remover_militar_guarnicao = (g_idx, m_idx)
            
            # Botão minimalista para adicionar militar dentro do cartão
            if st.button("➕ Militar", key=f"add_m_g_{g_idx}", use_container_width=True):
                acao_adicionar_militar_guarnicao = g_idx

st.markdown("")
if st.button("➕ Adicionar Guarnição"):
    nova_pos = len(st.session_state.lista_guarnicoes) + 1
    st.session_state.lista_guarnicoes.append({"nome": f"{nova_pos}ª GU BM", "militares": ["", ""]})
    st.rerun()

# Processamento de Ações das Guarnições
if acao_remover_guarnicao is not None:
    st.session_state.lista_guarnicoes.pop(acao_remover_guarnicao)
    st.rerun()

if acao_adicionar_militar_guarnicao is not None:
    st.session_state.lista_guarnicoes[acao_adicionar_militar_guarnicao]["militares"].append("")
    st.rerun()

if acao_remover_militar_guarnicao is not None:
    g_idx, m_idx = acao_remover_militar_guarnicao
    if len(st.session_state.lista_guarnicoes[g_idx]["militares"]) > 1:
        st.session_state.lista_guarnicoes[g_idx]["militares"].pop(m_idx)
        st.rerun()
    else:
        st.warning("Cada guarnição deve ter pelo menos um militar.")

st.markdown("---")

if st.button("Gerar Escala Oficial", type="primary", use_container_width=True):
    st.success("Escala estruturada com sucesso!")
    
    resultado_texto = f"""*ESCALA DE SERVIÇO - {ala_selecionada.upper()} - {cidade_local}, {data_plantao}*

*CHEFE DE SERVIÇO:* {chefe_servico}

*MILITARES / ATRIBUIÇÕES:*
"""
    for linha in st.session_state.linhas_escala:
        resultado_texto += f"- {linha['num']} | {linha['militar']} | {linha['horario']} | {linha['atribuicao']} | Tel: {linha['telefone']}\n"
    
    resultado_texto += "\n*GUARNIÇÕES:*\n"
    for guarnicao in st.session_state.lista_guarnicoes:
        mils_str = ", ".join([m for m in guarnicao["militares"] if m.strip()])
        resultado_texto += f"*{guarnicao['nome']}:* {mils_str}\n"
    
    st.code(resultado_texto, language="markdown")
    
    texto_wapp = urllib.parse.quote(resultado_texto)
    url_whatsapp = f"https://api.whatsapp.com/send?text={texto_wapp}"
    st.markdown(
        f'<a href="{url_whatsapp}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:12px; border-radius:8px; font-weight:bold; cursor:pointer;">🟢 Enviar Escala via WhatsApp</button></a>',
        unsafe_allow_html=True
    )
