import streamlit as st
import google.generativeai as genai
import tempfile
import os
import time

# --- 1. CONFIGURAÇÕES GERAIS ---
st.set_page_config(
    page_title="AtaPro.PT - Atas com IA",
    page_icon="🇵🇹",
    layout="centered"
)

# --- 2. DADOS DO NEGÓCIO (EDITAR AQUI) ---
# Substitua pelo seu número real para receber os MB WAYs
SEU_NUMERO_MBWAY = "91 000 00 00" 
PRECO_SERVICO = "9,90€"
# Link para o seu WhatsApp (Cria uma conversa automática)
LINK_WHATSAPP = f"https://wa.me/351{SEU_NUMERO_MBWAY.replace(' ', '')}?text=Olá,%20envio%20aqui%20o%20comprovativo%20do%20pagamento%20da%20Ata."

# --- 3. AUTENTICAÇÃO API (SEGURANÇA) ---
# Tenta buscar a chave aos "Secrets" do Streamlit (Produção)
# Se não encontrar, tenta usar uma variável local (Desenvolvimento)
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    # Apenas para não dar erro se testar localmente sem configurar secrets
    # Na produção, configure sempre os Secrets no painel do Streamlit!
    st.warning("⚠️ Aviso: API Key não detetada nos Secrets. Configure-a no Streamlit Cloud.")
    st.stop()

genai.configure(api_key=api_key)

# --- 4. O CÉREBRO (PROMPT JURÍDICO ATUALIZADO) ---
SYSTEM_PROMPT = """
Tu és o "AtaPro", um assistente profissional de administração de condomínios em Portugal.
A tua função é ouvir a gravação de uma assembleia e redigir uma ATA JURIDICAMENTE VÁLIDA.

⚠️ REGRAS CRÍTICAS DE SEGURANÇA E LEI (PORTUGAL):
1. **Identificação:** Identifica quem fala (ex: "Condómino do 1º Esq"). Se não souberes, usa "Um condómino".
2. **Filtro de Ruído:** Remove estritamente conversas paralelas, futebol ou insultos. Mantém apenas o relevante para as decisões.
3. **Inaudibilidade:** Se não se perceber a decisão devido a barulho, escreve: "[NOTA: Discussão inaudível. Requer validação manual pela Mesa]". Não inventes.
4. **Citações Legais:**
   - Obras conservação: cita Art. 1424.º do Código Civil.
   - Regulamento: cita Art. 1429.º-A.
   - Administração: cita Art. 1435.º.

ESTRUTURA DA ATA (Markdown):
# ATA DA ASSEMBLEIA DE CONDÓMINOS
**Data/Hora/Local:** [Preencher Manualmente]

## 1. ORDEM DE TRABALHOS
(Lista os tópicos)

## 2. DELIBERAÇÕES
### Ponto Um: [Título]
**Resumo:** [Resumo formal e imparcial]
**Votação:** [Aprovado/Rejeitado] (Detalhar votos contra se audível).

## 3. ENCERRAMENTO
Nada mais havendo a tratar, a reunião foi encerrada.
---
*Rascunho gerado por IA. Requer validação humana.*
"""

# --- 5. INTERFACE DO UTILIZADOR ---

# Cabeçalho
st.title("🇵🇹 AtaPro.PT")
st.markdown("### O seu Secretário de Atas Automático")
st.markdown(
    """
    Transforme a gravação da reunião numa **Ata Jurídica** em minutos.
    1. Carregue o áudio 📂
    2. A IA escreve a ata ✍️
    3. Pague por MB WAY e descarregue ✅
    """
)

# Sidebar (Informações)
with st.sidebar:
    st.header("ℹ️ Como Funciona")
    st.info("O nosso sistema usa Inteligência Artificial avançada para filtrar discussões e formatar a ata segundo a lei portuguesa.")
    st.write("---")
    st.header("💰 Custo do Serviço")
    st.metric(label="Preço por Ata", value=PRECO_SERVICO)
    st.write("Pagamento simples via **MB WAY**.")
    st.write("---")
    st.markdown("🔒 **Privacidade:** O áudio é eliminado imediatamente após o processamento.")

# Estado da Sessão (Para não perder a ata se clicar noutro botão)
if "ata_texto" not in st.session_state:
    st.session_state.ata_texto = None

# Área de Upload
uploaded_file = st.file_uploader("Carregue o áudio da reunião (MP3, WAV, M4A)", type=["mp3", "wav", "m4a", "ogg"])

# Checkbox Legal (Obrigatório)
termos = st.checkbox("✅ Declaro que tenho autorização da Assembleia para processar esta gravação para efeitos de ata.")

# Lógica de Processamento
if uploaded_file is not None and termos:
    
    # Botão de Ação
    if st.button("🚀 Gerar Ata Agora", type="primary"):
        with st.spinner('A ouvir a reunião, a ignorar o barulho e a consultar o Código Civil... (Aguarde 1-2 min)'):
            try:
                # 1. Criar ficheiro temporário
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name

                # 2. Upload para Gemini
                myfile = genai.upload_file(tmp_path)
                
                # Loop de espera (processamento do áudio do lado do Google)
                while myfile.state.name == "PROCESSING":
                    time.sleep(2)
                    myfile = genai.get_file(myfile.name)

                # 3. Gerar Texto (Modelo Flash para rapidez)
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content([SYSTEM_PROMPT, myfile])
                
                # 4. Guardar no Session State
                st.session_state.ata_texto = response.text

                # 5. Limpeza de Segurança (Apagar ficheiros)
                os.remove(tmp_path)
                genai.delete_file(myfile.name)
                
            except Exception as e:
                st.error(f"Ocorreu um erro técnico: {e}")

# --- 6. EXIBIÇÃO DO RESULTADO E PAGAMENTO ---

if st.session_state.ata_texto:
    st.success("✅ Ata gerada com sucesso!")
    
    st.divider()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📄 Pré-visualização")
        # Mostra a ata numa caixa com scroll
        st.text_area("Texto da Ata (Editável)", value=st.session_state.ata_texto, height=400)
        
        # Botão de Download
        st.download_button(
            label="📥 Descarregar Ata (.md)",
            data=st.session_state.ata_texto,
            file_name="ata_condominio_final.md",
            mime="text/markdown"
        )
        st.caption("Dica: Abra o ficheiro no Bloco de Notas ou Word.")

    with col2:
        # CAIXA DE PAGAMENTO MB WAY (Estilo Card)
        st.markdown(
            f"""
            <div style="background-color:#f0fdf4; padding:20px; border-radius:10px; border:1px solid #bbf7d0;">
                <h3 style="color:#166534; margin-top:0;">💳 Pagamento</h3>
                <p>O serviço foi útil? Para manter o projeto ativo, agradecemos o pagamento.</p>
                <h2 style="text-align:center;">{PRECO_SERVICO}</h2>
                <hr>
                <p style="text-align:center;"><strong>MB WAY</strong></p>
                <h3 style="text-align:center; color:#E6007E;">{SEU_NUMERO_MBWAY}</h3>
                <p style="font-size:12px; text-align:center; color:gray;">Enviar comprovativo para libertar suporte premium.</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        st.write("") # Espaço
        st.link_button("📲 Enviar Comprovativo (WhatsApp)", LINK_WHATSAPP)

elif uploaded_file and not termos:
    st.warning("⚠️ Por favor, aceite os termos de autorização para continuar.")
