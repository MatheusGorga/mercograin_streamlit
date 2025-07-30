# funcoes_compartilhadas/cria_id.py
# -*- coding: utf-8 -*-

import socket
from datetime import datetime

def cria_id(sequencia='1', usuario=None) -> str:
    """
    Gera um ID no formato: AAMMDD_HHMMSS_USUARIO_SEQUENCIA
    """
    agora = datetime.now().strftime('%y%m%d_%H%M%S')

    if not usuario:
        try:
            # Tenta pegar o IP, se falhar, usa um padrão
            usuario = socket.gethostbyname(socket.gethostname()).replace('.', '')
        except:
            usuario = '00000000'

    return f"{agora}_{usuario}_{sequencia}"