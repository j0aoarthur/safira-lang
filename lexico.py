import sys
import re

# 1. DEFINIÇÃO DA GRAMÁTICA LÉXICA COM REGEX
# A ordem é estritamente importante: padrões mais específicos/maiores vêm primeiro!
REGRAS_LEXICAS = [
    # 1. Ignorados (Comentários e Espaços)
    (r'\/\*[\s\S]*?\*\/', None),          # Comentários de múltiplas linhas /* ... */
    (r'\/\/.*', None),                    # Comentários de linha única // ...
    (r'\s+', None),                       # Espaços em branco, tabs, quebras de linha

    # 2. Palavras-Chave (Usando \b para garantir que são palavras inteiras)
    (r'\b(int|float|string)\b', 'TIPO_DADO'),
    (r'\b(if|else|switch|case|default)\b', 'CONTROLE_FLUXO'),
    (r'\b(while|for)\b', 'ESTRUTURA_LOOP'),
    (r'\b(break|continue)\b', 'CONTROLE_LOOP'),
    (r'\b(function|task|return)\b', 'SUBROTINA'),
    (r'\b(attempt|fallback)\b', 'BLOCO_SEGURO'), # NOSSA INOVAÇÃO
    (r'\b(and|or|not)\b', 'OP_LOGICO'),

    # 3. Literais (Valores)
    (r'"[^"]*"', 'LITERAL_STRING'),       # Cadeia de caracteres
    (r'\d+\.\d+', 'LITERAL_FLOAT'),       # Números com ponto flutuante
    (r'\d+', 'LITERAL_INT'),              # Números inteiros

    # 4. Inovação: Operador de Pipeline
    (r'\|>', 'OP_PIPELINE'),              # Pipeline |>

    # 5. Operadores de Comparação (2 caracteres primeiro)
    (r'==|!=|>=|<=', 'OP_COMPARACAO'),
    (r'>|<', 'OP_COMPARACAO'),

    # 6. Operadores Aritméticos e Atribuição
    (r'\+', 'OP_SOMA'),
    (r'-', 'OP_SUBTRACAO'),
    (r'\*', 'OP_MULTIPLICACAO'),
    (r'/', 'OP_DIVISAO'),
    (r'%', 'OP_RESTO'),
    (r'=', 'OP_ATRIBUICAO'),

    # 7. Delimitadores
    (r'\{', 'ABRE_CHAVE'),
    (r'\}', 'FECHA_CHAVE'),
    (r'\(', 'ABRE_PARENTESES'),
    (r'\)', 'FECHA_PARENTESES'),
    (r';', 'PONTO_VIRGULA'),
    (r':', 'DOIS_PONTOS'),
    (r',', 'VIRGULA'),

    # 8. Identificadores (Nomes de variáveis e funções)
    (r'[a-zA-Z_][a-zA-Z0-9_]*', 'IDENTIFICADOR')
]

def gerar_html(tabela, nome_arquivo="tabela_simbolos.html"):
    """Gera um arquivo HTML com a tabela de símbolos (Requisito do TDE)"""
    html = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Tabela de Símbolos - Analisador Léxico</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f9f9f9; }
            h2 { color: #333; }
            table { border-collapse: collapse; width: 80%; background-color: #fff; box-shadow: 0px 0px 10px rgba(0,0,0,0.1); }
            th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
            th { background-color: #004080; color: white; }
            tr:nth-child(even) { background-color: #f2f2f2; }
            .token-type { font-weight: bold; color: #d9534f; }
        </style>
    </head>
    <body>
        <h2>Tabela de Símbolos - Analisador Léxico</h2>
        <table>
            <tr><th>Tipo do Token</th><th>Valor (Lexema)</th><th>Linha</th></tr>
    """
    for token in tabela:
        html += f"<tr><td class='token-type'>{token['tipo']}</td><td>{token['valor']}</td><td>{token['linha']}</td></tr>\n"
    
    html += """
        </table>
    </body>
    </html>
    """
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        f.write(html)

def analise(pathArquivo):
    with open(pathArquivo, 'r', encoding='utf-8') as f:
        codigo = f.read()
    
    tabela = []
    erros = []
    posicao = 0
    linha_atual = 1

    while posicao < len(codigo):
        deuMatch = False
        
        for regra, tipo in REGRAS_LEXICAS:
            regex = re.compile(regra)
            match = regex.match(codigo, posicao)
            
            if match:
                valor_match = match.group(0)
                
                # Se o tipo não for None, adicionamos à tabela (ignora comentários e espaços)
                if tipo:
                    tabela.append({"tipo": tipo, "valor": valor_match, "linha": linha_atual})
                
                # Atualiza contagem de linhas baseado nos '\n' contidos no match (importante para comentários multiline)
                linha_atual += valor_match.count('\n')
                posicao = match.end()
                deuMatch = True
                break
                
        if not deuMatch:
            # Erro Léxico detectado
            caractere_invalido = codigo[posicao]
            erros.append(f"Erro léxico na linha {linha_atual}. Caractere inesperado: '{caractere_invalido}'")
            # Para evitar loop infinito, avançamos 1 caractere no erro
            if caractere_invalido == '\n':
                linha_atual += 1
            posicao += 1

    return tabela, erros

# ================= EXECUÇÃO =================
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso correto: python lexico.py <arquivo.saf>")
        sys.exit(1)
        
    arquivo_entrada = sys.argv[1]
    tabela_tokens, lista_erros = analise(arquivo_entrada)

    # Exibir no Terminal
    print(f"{'Tipo do Token':<25} | {'Valor (Lexema)':<20} | {'Linha':<5}")
    print('-'*60)
    for token in tabela_tokens:
        print(f"{token['tipo']:<25} | {token['valor']:<20} | {token['linha']:<5}")

    print("\n=== STATUS DA ANÁLISE ===")
    if lista_erros:
        print("Erros encontrados:")
        for e in lista_erros:
            print(f" -> {e}")
    else:
        print("Sucesso! Nenhum erro léxico encontrado.")
        
    # Gera o arquivo HTML (Requisito da Fase 2)
    gerar_html(tabela_tokens)
    print("-> Arquivo 'tabela_simbolos.html' exportado com sucesso!\n")