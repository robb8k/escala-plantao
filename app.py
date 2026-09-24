import streamlit as st
from datetime import datetime
import urllib.parse
import sqlite3
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

st.set_page_config(
    page_title="Arquivo de Escalas Operacionais",
    page_icon="📋",
    layout="wide"
)

# Estilização CSS Tática (Grafite e Laranja Queimado) e máxima compactação
st.markdown("""
<style>
    .stApp {
        background-color: #1E1B1A;
        color: #E6E1E0;
    }
    .block-container {
        padding-top: 1rem !important;
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
        font-size: 13px !important;
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
        margin: 0.8rem 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Configuração da Base de Dados SQLite para o Histórico
def init_db():
    conn = sqlite3.connect("escala_historico.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS escalas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            ala TEXT,
            cidade TEXT,
            chefe TEXT,
            dados_militares TEXT,
            dados_guarnicoes TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def salvar_escala_db(data, ala, cidade, chefe, dados_mils, dados_guars):
    conn = sqlite3.connect("escala_historico.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO escalas (data, ala, cidade, chefe, dados_militares, dados_guarnicoes)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (data, ala, cidade, chefe, str(dados_mils), str(dados_guars)))
    conn.commit()
    conn.close()

def carregar_historico():
    conn = sqlite3.connect("escala_historico.db")
    df = pd.read_sql_query("SELECT * FROM escalas ORDER BY id DESC", conn)
    conn.close()
    return df

# Função para formatar automaticamente o telefone brasileiro (XX) XXXXX-XXXX
def formatar_telefone(texto):
    digitos = "".join([c for c in texto if c.isdigit()])
    if len(digitos) == 0:
        return ""
    elif len(digitos) <= 2:
        return f"({digitos}"
    elif len(digitos) <= 6:
        return f"({digitos[:2]}){digitos[2:]}"
    elif len(digitos) <= 10:
        return f"({digitos[:2]}){digitos[2:6]}-{digitos[6:]}"
    else:
        return f"({digitos[:2]}){digitos[2:7]}-{digitos[7:11]}"

# Função para gerar o PDF formatado
def gerar_pdf(cidade, data, ala, chefe, linhas_escala, guarnicoes):
    pdf_filename = "escala_operacional.pdf"
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    
    styles = getSampleStyleSheet()
    
    titulo_style = ParagraphStyle(
        'TituloPDF',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=colors.HexColor('#C2410C'),
        alignment=1,
        spaceAfter=10
    )
    
    sub_style = ParagraphStyle(
        'SubTituloPDF',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=colors.HexColor('#1E1B1A'),
        spaceAfter=6
    )

    story.append(Paragraph(f"ESCALA DE SERVIÇO - {ala.upper()} - {cidade.upper()}, {data.upper()}", titulo_style))
    story.append(Spacer(1, 10))
    
    if chefe and chefe.strip():
        story.append(Paragraph(f"<b>CHEFE DE SERVIÇO:</b> {chefe.upper()}", sub_style))
        story.append(Spacer(1, 6))

    story.append(Paragraph("MILITARES / ATRIBUIÇÕES", sub_style))
    
    tabela_data = [["Nº", "Militar", "Horário", "Atribuições", "Telefone"]]
    for item in linhas_escala:
        tabela_data.append([
            item["num"],
            item["militar"],
            item["horario"],
            item["atribuicao"],
            item["telefone"]
        ])
    
    t_militares = Table(tabela_data, colWidths=[30, 120, 100, 165, 90])
    t_militares.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#C2410C')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#4A4240')),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F4F1F0')),
    ]))
    
    story.append(t_militares)
    story.append(Spacer(1, 15))

    story.append(Paragraph("GUARNIÇÕES", sub_style))
    
    guarnicoes_data = [["Guarnição", "Efetivo / Militares Empregados"]]
    for g in guarnicoes:
        mils_str = ", ".join([m for m in g["militares"] if m.strip()])
        guarnicoes_data.append([g["nome"], mils_str])
        
    t_guarnicoes = Table(guarnicoes_data, colWidths=[100, 405])
    t_guarnicoes.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#33302E')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#4A4240')),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F4F1F0')),
    ]))
    
    story.append(t_guarnicoes)
    doc.build(story)
    return pdf_filename

st.markdown("""
# Arquivo de Escalas Operacionais
""")

# Abas de Navegação Principal
aba_nova, aba_historico = st.tabs(["📝 Nova Escala / Plantão", "🗂️ Histórico de Escalas"])

with aba_nova:
    if "mem_chefe" not in st.session_state:
        st.session_state.mem_chefe = ""
    if "mem_cidade" not in st.session_state:
        st.session_state.mem_cidade = "TEÓFILO OTONI"

    col_ala, col_c1, col_c2, col_c3 = st.columns(4)

    with col_ala:
        ala_selecionada = st.selectbox("Ala Operacional", ["1ª Ala Operacional", "2ª Ala Operacional", "3ª Ala Operacional", "4ª Ala Operacional"], key="sel_ala_nova")
    with col_c1:
        cidade_local = st.text_input("Local / Cidade", value=st.session_state.mem_cidade, key="input_cidade_nova")
        st.session_state.mem_cidade = cidade_local
    with col_c2:
        data_plantao_obj = st.date_input("Data:", value=datetime.today(), key="input_data_nova")
        data_plantao = data_plantao_obj.strftime('%d/%m/%Y')
    with col_c3:
        chefe_servico = st.text_input("Chefe de Serviço", value=st.session_state.mem_chefe, key="input_chefe_nova", placeholder="Digite o Chefe...")
        st.session_state.mem_chefe = chefe_servico

    st.markdown("---")

    if "linhas_escala" not in st.session_state:
        st.session_state.linhas_escala = [
            {"num": "01", "militar": "", "horario": "", "atribuicao": "", "telefone": ""},
            {"num": "02", "militar": "", "horario": "", "atribuicao": "", "telefone": ""},
            {"num": "03", "militar": "", "horario": "", "atribuicao": "", "telefone": ""},
            {"num": "04", "militar": "", "horario": "", "atribuicao": "", "telefone": ""}
        ]

    st.subheader("Militares / Atribuições")

    colunas_tabela = st.columns([1, 2, 2, 2, 2, 1])
    with colunas_tabela[0]: st.markdown("**Nº**")
    with colunas_tabela[1]: st.markdown("**Militar**")
    with colunas_tabela[2]: st.markdown("**Horário**")
    with colunas_tabela[3]: st.markdown("**Atribuições**")
    with colunas_tabela[4]: st.markdown("**Telefone**")
    with colunas_tabela[5]: st.markdown("**Ação**")

    linhas_temp = []
    indice_remover_militar = None

    for i, item in enumerate(st.session_state.linhas_escala):
        c1, c2, c3, c4, c5, c6 = st.columns([1, 2, 2, 2, 2, 1])
        
        with c1:
            num = st.text_input(f"N_{i}", value=item["num"], key=f"num_{i}", label_visibility="collapsed")
        with c2:
            mil = st.text_input(f"Mil_{i}", value=item["militar"], key=f"mil_{i}", label_visibility="collapsed", placeholder="Nome...")
        with c3:
            hor = st.text_input(f"Hor_{i}", value=item["horario"], key=f"hor_{i}", label_visibility="collapsed", placeholder="Ex: 08:00 / 22:00")
        with c4:
            atr = st.text_input(f"Atr_{i}", value=item["atribuicao"], key=f"atr_{i}", label_visibility="collapsed", placeholder="Atribuição...")
        with c5:
            tel_input = st.text_input(f"Tel_{i}", value=item["telefone"], key=f"tel_{i}", label_visibility="collapsed", placeholder="(33)...")
            tel = formatar_telefone(tel_input)
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

    if "lista_guarnicoes" not in st.session_state:
        st.session_state.lista_guarnicoes = [
            {"nome": "1ª GU BM", "militares": ["", ""]},
            {"nome": "2ª GU BM", "militares": ["", ""]}
        ]

    st.subheader("Guarnições")

    acao_remover_guarnicao = None
    acao_adicionar_militar_guarnicao = None
    acao_remover_militar_guarnicao = None

    cols_guarnicoes = st.columns(2)

    for g_idx, guarnicao in enumerate(st.session_state.lista_guarnicoes):
        col_alvo = cols_guarnicoes[g_idx % 2]
        
        with col_alvo:
            c_nome, c_del = st.columns([5, 1])
            with c_nome:
                guarnicao["nome"] = st.text_input("Guarnição", value=guarnicao["nome"], key=f"g_nome_{g_idx}", label_visibility="collapsed")
            with c_del:
                if st.button("🗑️", key=f"del_g_{g_idx}", help="Remover Guarnição"):
                    acao_remover_guarnicao = g_idx
            
            for m_idx, militar_nome in enumerate(guarnicao["militares"]):
                c_mil, c_del_m = st.columns([5, 1])
                with c_mil:
                    guarnicao["militares"][m_idx] = st.text_input(f"Militar {m_idx+1}", value=militar_nome, key=f"g_{g_idx}_m_{m_idx}", label_visibility="collapsed", placeholder="Militar...")
                with c_del_m:
                    if st.button("❌", key=f"del_g_{g_idx}_m_{m_idx}", help="Remover Militar"):
                        acao_remover_militar_guarnicao = (g_idx, m_idx)
            
            c_add_m, c_vazio = st.columns([3, 3])
            with c_add_m:
                if st.button("➕ Militar", key=f"add_m_g_{g_idx}", use_container_width=True):
                    acao_adicionar_militar_guarnicao = g_idx
            
            st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)

    if st.button("➕ Adicionar Guarnição"):
        nova_pos = len(st.session_state.lista_guarnicoes) + 1
        st.session_state.lista_guarnicoes.append({"nome": f"{nova_pos}ª GU BM", "militares": ["", ""]})
        st.rerun()

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

    if st.button("Salvar e Arquivar Escala Oficial", type="primary", use_container_width=True):
        salvar_escala_db(data_plantao, ala_selecionada, cidade_local, chefe_servico, st.session_state.linhas_escala, st.session_state.lista_guarnicoes)
        st.success("Escala salva e arquivada com sucesso no histórico operacional!")
        
        pdf_path = gerar_pdf(cidade_local, data_plantao, ala_selecionada, chefe_servico, st.session_state.linhas_escala, st.session_state.lista_guarnicoes)
        with open(pdf_path, "rb") as pdf_file:
            PDFbyte = pdf_file.read()
            
        st.download_button(
            label="📥 Baixar PDF Oficial",
            data=PDFbyte,
            file_name=f"Escala_{ala_selecionada.replace(' ', '_')}_{data_plantao.replace('/', '-')}.pdf",
            mime='application/pdf',
            use_container_width=True
        )
        
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

with aba_historico:
    st.subheader("Consulta de Escalas Arquivadas")
    df_hist = carregar_historico()
    
    if df_hist.empty:
        st.info("Ainda não existem escalas arquivadas na base de dados.")
    else:
        # Filtros de consulta rápida
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filtro_ala = st.selectbox("Filtrar por Ala", ["Todas"] + list(df_hist["ala"].unique()))
        with col_f2:
            filtro_data = st.selectbox("Filtrar por Data", ["Todas"] + list(df_hist["data"].unique()))
            
        df_filtrado = df_hist.copy()
        if filtro_ala != "Todas":
            df_filtrado = df_filtrado[df_filtrado["ala"] == filtro_ala]
        if filtro_data != "Todas":
            df_filtrado = df_filtrado[df_filtrado["data"] == filtro_data]
            
        for index, row in df_filtrado.iterrows():
            with st.expander(f"📅 Data: {row['data']} | 🛡️ Ala: {row['ala']} | 📍 Local: {row['cidade']} (Chefe: {row['chefe']})"):
                st.markdown(f"**Chefe de Serviço:** {row['chefe']}")
                st.markdown(f"**Militares / Atribuições:**")
                st.text(row['dados_militares'])
                st.markdown(f"**Guarnições:**")
                st.text(row['dados_guarnicoes'])
                
                # Botão para regenerar o PDF da escala consultada
                if st.button(f"📥 Baixar PDF da Escala ({row['data']} - {row['ala']})", key=f"pdf_hist_{row['id']}"):
                    import ast
                    mils_eval = ast.literal_eval(row['dados_militares'])
                    guars_eval = ast.literal_eval(row['dados_guarnicoes'])
                    pdf_path = gerar_pdf(row['cidade'], row['data'], row['ala'], row['chefe'], mils_eval, guars_eval)
                    with open(pdf_path, "rb") as pdf_file:
                        PDFbyte = pdf_file.read()
                    st.download_button(
                        label="Clique aqui para confirmar o download do PDF",
                        data=PDFbyte,
                        file_name=f"Escala_{row['ala'].replace(' ', '_')}_{row['data'].replace('/', '-')}.pdf",
                        mime='application/pdf',
                        key=f"dl_hist_{row['id']}"
                    )
