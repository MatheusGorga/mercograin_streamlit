# funcoes_compartilhadas/gerador_pdf.py

import io
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# --- WORKAROUND PARA PROBLEMA DE INSTALAÇÃO DO REPORTLAB ---
A4 = (595.2755905511812, 841.8897637795277)
# --- FIM DO WORKAROUND ---


# --- IMAGENS ---
# Certifique-se de que 'logo.png' e 'watermark.png' existam na pasta 'templates'.
LOGO_PATH = "templates/logo.png" 
WATERMARK_PATH = "templates/watermark.png"

def criar_contrato_pdf(dados_contrato):
    """
    Gera um contrato em PDF usando ReportLab para controle total do layout,
    garantindo máxima fidelidade ao modelo original.
    
    :param dados_contrato: Dicionário com os dados para preencher o contrato.
    :return: Bytes do PDF gerado.
    """
    try:
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # --- FUNÇÕES AUXILIARES DE DESENHO ---
        def draw_watermark(canvas_obj):
            try:
                watermark = ImageReader(WATERMARK_PATH)
                img_width = width * 0.7
                img_height = img_width
                canvas_obj.saveState()
                canvas_obj.translate(width / 2, height / 2)
                canvas_obj.setFillColor(colors.black, alpha=0.8)
                canvas_obj.drawImage(watermark, -img_width / 2, -img_height / 2, width=img_width, height=img_height, mask='auto')
                canvas_obj.restoreState()
            except IOError:
                pass # Ignora se a imagem da marca d'água não for encontrada

        def draw_header(canvas_obj):
            try:
                logo = ImageReader(LOGO_PATH)
                canvas_obj.drawImage(logo, 2*cm, height - 3.5*cm, width=3*cm, preserveAspectRatio=True, mask='auto')
            except IOError:
                pass # Ignora se a imagem do logo não for encontrada
            
            canvas_obj.setFont("Helvetica-Bold", 18)
            canvas_obj.drawCentredString(width / 2, height - 2.5*cm, "MERCO GRAIN")
            canvas_obj.setFont("Helvetica-Bold", 11)
            canvas_obj.drawCentredString(width / 2, height - 3.1*cm, "COMMODITIES AGRÍCOLAS")
            
            p.setStrokeColorRGB(0,0,0)
            p.line(2*cm, height - 4*cm, width - 2*cm, height - 4*cm)
            
            canvas_obj.setFont("Helvetica", 10)
            canvas_obj.drawString(2*cm, height - 4.5*cm, f"Data: {dados_contrato.get('DATA_CONTRATO', 'N/A')}")
            canvas_obj.drawRightString(width - 2*cm, height - 4.5*cm, f"Contrato Número: {dados_contrato.get('CONTRATO_NUMERO', 'N/A')}")

        def draw_footer(canvas_obj):
            canvas_obj.saveState()
            canvas_obj.setFont('Helvetica', 8)
            canvas_obj.setFillColor(colors.grey)
            
            footer_text = "Merco Grain Commodities Agrícolas"
            footer_text2 = "Av. Diário de Notícias 400, sala 1108 - Cristal, Ed. Diamond Tower - Porto Alegre/RS - CEP: 90810-080 - Fone (51) 3060-7700/7900"
            
            canvas_obj.drawCentredString(width / 2, 1.5*cm, footer_text)
            canvas_obj.drawCentredString(width / 2, 1.1*cm, footer_text2)
            canvas_obj.restoreState()

        # --- DESENHANDO O PDF ---
        
        draw_watermark(p)
        draw_header(p)
        draw_footer(p)

        # Define a margem inicial para o conteúdo
        y_pos = height - 5.5*cm
        left_margin = 2.5*cm
        
        # --- SEÇÃO VENDEDOR ---
        p.setFont("Helvetica-Bold", 10)
        p.drawString(left_margin, y_pos, "Vendedor:")
        y_pos -= 0.6*cm
        p.setFont("Helvetica", 10)
        p.drawString(left_margin, y_pos, dados_contrato.get('NOME_VENDEDOR', ''))
        y_pos -= 0.5*cm
        p.drawString(left_margin, y_pos, dados_contrato.get('ENDERECO_VENDEDOR', ''))
        y_pos -= 0.5*cm
        p.drawString(left_margin, y_pos, f"CNPJ: {dados_contrato.get('CNPJ_VENDEDOR', '')}")
        y_pos -= 0.5*cm
        p.drawString(left_margin, y_pos, f"IE: {dados_contrato.get('IE_VENDEDOR', '')}")

        # --- SEÇÃO COMPRADOR ---
        y_pos -= 1*cm # Espaço entre as seções
        p.setFont("Helvetica-Bold", 10)
        p.drawString(left_margin, y_pos, "Comprador:")
        y_pos -= 0.6*cm
        p.setFont("Helvetica", 10)
        p.drawString(left_margin, y_pos, dados_contrato.get('NOME_COMPRADOR', ''))
        y_pos -= 0.5*cm
        p.drawString(left_margin, y_pos, dados_contrato.get('ENDERECO_COMPRADOR', ''))
        y_pos -= 0.5*cm
        p.drawString(left_margin, y_pos, f"CNPJ: {dados_contrato.get('CNPJ_COMPRADOR', '')}")
        y_pos -= 0.5*cm
        p.drawString(left_margin, y_pos, f"IE: {dados_contrato.get('IE_COMPRADOR', '')}")

        # --- CLÁUSULAS DO CONTRATO ---
        y_pos -= 1.2*cm
        clauses = [
            ("Corretor:", "Merco Grain Commodities Agrícolas"),
            ("Mercadoria:", f"{dados_contrato.get('PRODUTO', '')}, {dados_contrato.get('SAFRA', '')}, tipo Exportação {dados_contrato.get('ANAC', '')}"),
            ("Quantidade:", f"{dados_contrato.get('QUANTIDADE', '')} {dados_contrato.get('UNIDADE', '')}"),
            ("Embalagem:", "À Granel."),
            ("Entrega:", "Imediata."),
            ("Preço:", f"R$ {dados_contrato.get('PRECO', '')} por {dados_contrato.get('UNIDADE', '')}"),
            ("Peso/Qualidade:", "A ser verificado na Fábrica da Cargill em Cachoeira do Sul/RS."),
        ]
        
        styles = getSampleStyleSheet()
        style_bold = styles['Normal']
        style_bold.fontName = 'Helvetica-Bold'
        style_normal = styles['Normal']
        style_normal.fontName = 'Helvetica'

        for label, value in clauses:
            p.setFont("Helvetica-Bold", 10)
            p.drawString(left_margin, y_pos, label)
            p.setFont("Helvetica", 10)
            p.drawString(left_margin + 3*cm, y_pos, value)
            y_pos -= 0.7*cm
            
        # --- DETALHES DO PAGAMENTO ---
        y_pos -= 0.3*cm
        p.setFont("Helvetica-Bold", 10)
        p.drawString(left_margin, y_pos, "Pagamento:")
        p.setFont("Helvetica", 10)
        p.drawString(left_margin + 3*cm, y_pos, f"Total dia {dados_contrato.get('DATA_PAGAMENTO', '30.05.2025')}.")
        y_pos -= 0.5*cm
        p.drawString(left_margin + 3*cm, y_pos, "Banco do Brasil")
        y_pos -= 0.5*cm
        p.drawString(left_margin + 3*cm, y_pos, "Ag: 4044-4 C/c: 5493-3")
        y_pos -= 0.5*cm
        p.drawString(left_margin + 3*cm, y_pos, "CNPJ: 30.011.622/0001-86")

        # --- OUTRAS CONDIÇÕES ---
        y_pos -= 1*cm
        p.setFont("Helvetica-Bold", 10)
        p.drawString(left_margin, y_pos, "Outras Condições:")
        y_pos -= 0.6*cm
        p.setFont("Helvetica", 10)
        p.drawString(left_margin, y_pos, "- Mercadoria a ser entregue na Fábrica da Cargill em Cachoeira do Sul/RS.")

        # --- ASSINATURAS ---
        y_pos = 5*cm
        p.line(3*cm, y_pos, 8*cm, y_pos)
        p.line(width - 8*cm, y_pos, width - 3*cm, y_pos)
        y_pos -= 0.5*cm
        p.setFont("Helvetica", 10)
        p.drawCentredString(5.5*cm, y_pos, dados_contrato.get('NOME_COMPRADOR', ''))
        p.drawCentredString(width - 5.5*cm, y_pos, dados_contrato.get('NOME_VENDEDOR', ''))
        y_pos -= 0.5*cm
        p.setFont("Helvetica-Bold", 10)
        p.drawCentredString(5.5*cm, y_pos, "COMPRADOR")
        p.drawCentredString(width - 5.5*cm, y_pos, "VENDEDOR")

        # Finaliza e salva o PDF
        p.showPage()
        p.save()
        
        buffer.seek(0)
        return buffer.getvalue()

    except Exception as e:
        raise Exception(f"Erro ao gerar PDF com ReportLab: {e}")
