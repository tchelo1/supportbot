import sqlite3
from datetime import datetime
import re

# Conectar ou criar o banco de dados
conn = sqlite3.connect('support.db')
cursor = conn.cursor()

# Criar a tabela de interações, se não existir
cursor.execute('''
    CREATE TABLE IF NOT EXISTS interactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT NOT NULL,
        message TEXT NOT NULL,
        response TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()

def responder(mensagem):
    mensagem = mensagem.lower()

    numeros = list(map(float, re.findall(r"\d+\.?\d*", mensagem)))

    mais_variacoes = ["mais", "soma", "somar", "adicionar", "adição"]
    menos_variacoes = ["menos", "subtrai", "subtrair", "diminuir", "reduzir"]
    vezes_variacoes = ["vezes", "multiplica", "multiplicar", "multiplicação", "x", "*"]
    dividido_variacoes = ["dividido", "divide", "dividir", "divisão", "divir", "divir por", "dividir por"]

    # Palavras-chave para problemas de maquininha
    problemas_maquininha = ["maquininha", "máquina", "terminal", "pos", "leitor"]
    problemas_maquininha_frases = ["não funciona", "nao funciona", "não liga", "nao liga", "travando", "não conecta", "nao conecta", "erro", "problema"]

    # Frases e palavras para outras situações
    bloqueio_conta = ["conta bloqueada", "minha conta está bloqueada", "minha conta bloqueada", "bloqueio", "bloqueada"]
    comprovante_perdido = ["não recebi comprovante", "nao recebi comprovante", "comprovante"]
    cobranca_duplicada = ["cobrança duplicada", "cobranca duplicada", "cobrado duas vezes", "cobrança duas vezes", "cobranca duas vezes"]
    transacao_recusada = ["transação recusada", "transacao recusada", "transação foi recusada", "transacao foi recusada", "pagamento recusado"]

    # Verificar problemas de maquininha
    if any(palavra in mensagem for palavra in problemas_maquininha) and any(frase in mensagem for frase in problemas_maquininha_frases):
        return ("Poxa, entendo que a maquininha está dando problema. "
                "Você já tentou reiniciar o aparelho e verificar a conexão? "
                "Se continuar, por favor, envie o código do erro ou mais detalhes.")

    # Frases curtas relacionadas à maquininha com problemas
    if any(frase in mensagem for frase in problemas_maquininha_frases):
        return "Pode me dar mais detalhes sobre o problema para eu ajudar melhor?"

    # Bloqueio de conta
    if any(frase in mensagem for frase in bloqueio_conta):
        return ("Sua conta pode estar bloqueada por questões de segurança. "
                "Recomendo entrar em contato com nosso suporte humano para uma análise detalhada.")

    # Comprovante perdido
    if any(frase in mensagem for frase in comprovante_perdido):
        return ("Você pode solicitar o reenvio do comprovante pelo app ou "
                "entrar em contato com o suporte para que possamos ajudar.")

    # Cobrança duplicada
    if any(frase in mensagem for frase in cobranca_duplicada):
        return ("Sentimos pelo transtorno! Por favor, envie seu comprovante para que possamos analisar e, se necessário, fazer o estorno.")

    # Transação recusada
    if any(frase in mensagem for frase in transacao_recusada):
        return ("Isso pode acontecer por vários motivos, como limite do cartão ou instabilidade. "
                "Já tentou usar outro cartão ou método de pagamento?")

    # Matemática
    if any(palavra in mensagem for palavra in mais_variacoes):
        if len(numeros) == 2:
            return f"O resultado é: {numeros[0] + numeros[1]}"
    elif any(palavra in mensagem for palavra in menos_variacoes):
        if len(numeros) == 2:
            return f"O resultado é: {numeros[0] - numeros[1]}"
    elif any(palavra in mensagem for palavra in vezes_variacoes):
        if len(numeros) == 2:
            return f"O resultado é: {numeros[0] * numeros[1]}"
    elif any(palavra in mensagem for palavra in dividido_variacoes):
        if len(numeros) == 2:
            if numeros[1] != 0:
                return f"O resultado é: {numeros[0] / numeros[1]}"
            else:
                return "Não é possível dividir por zero."
    elif "elevado" in mensagem or "potência" in mensagem or "ao quadrado" in mensagem:
        if len(numeros) == 2:
            return f"O resultado é: {numeros[0] ** numeros[1]}"
        elif len(numeros) == 1 and "ao quadrado" in mensagem:
            return f"O resultado é: {numeros[0] ** 2}"

    try:
        resultado = eval(mensagem)
        if isinstance(resultado, (int, float)):
            return f"O resultado é: {resultado}"
    except:
        pass

    # Respostas padrão
    if "problema" in mensagem:
        return "Entendo, pode me descrever melhor o problema?"
    elif "erro" in mensagem:
        return "Vamos resolver isso! Qual erro você encontrou?"
    elif "obrigado" in mensagem or "valeu" in mensagem:
        return "De nada! Qualquer outra dúvida, estou por aqui."
    elif "falar com humano" in mensagem:
        return "Um agente entrará em contato em breve. Mais alguma coisa por enquanto?"

    # Para frases curtas ou que não entendeu
    if len(mensagem.strip()) < 4:
        return "Pode explicar melhor? Quero ajudar."

    return "Desculpe, não entendi. Pode reformular?"

# Início da conversa
usuario = input("Digite seu nome: ")
print(f"\nOlá {usuario}, bem-vindo ao suporte!\nDigite 'sair' para encerrar.\n")

while True:
    mensagem = input("Você: ")
    if mensagem.lower() == 'sair':
        print("Suporte: Obrigado pelo contato. Até mais!")
        break

    resposta = responder(mensagem)
    print(f"Suporte: {resposta}")

    cursor.execute('''
        INSERT INTO interactions (user, message, response)
        VALUES (?, ?, ?)
    ''', (usuario, mensagem, resposta))
    conn.commit()

conn.close()
