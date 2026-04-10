# Trabalho Discente Efetivo (TDE) - Compiladores

**Centro Universitário Nobre de Feira de Santana (UNIFAN)**  
**Disciplina:** Compiladores  
**Professor:** Thiago de Lima Mariano

## Equipe (5 Alunos)

1. João Arthur Britto
2. Wesley Rios
3. Felipe Henriques Batista
4. Yuri Pinho

---

## Sobre o Projeto

Este repositório contém a Fase 1 e 2 do TDE de Compiladores. Criamos a linguagem procedural **Safira** e implementamos o seu Analisador Léxico usando Python. O analisador lê o código-fonte, usa Expressões Regulares (Regex) para identificar os tokens e gera a tabela de símbolos em formato HTML.

### Arquivos:

- `lexico.py`: Script principal do analisador léxico.
- `documentacao.md`: Regras, palavras-chave e sintaxe da linguagem.
- `codigo_exemplo.saf`: Exemplo de código válido usando todas as estruturas da linguagem.
- `erro_teste.saf`: Arquivo com caracteres inválidos propositais para testar se o compilador acusa o erro corretamente.

---

## Como rodar o Analisador Léxico

### Requisito

- Ter o Python 3 instalado.

### Execução

Pelo terminal, navegue até a pasta do projeto e rode o comando passando o arquivo de texto que você quer analisar.

Comando:

```bash
python lexico.py <nome_do_arquivo>
```

#### Teste 1: Código correto

```bash
python lexico.py codigo_exemplo.saf
```

**O que vai acontecer:** O terminal vai listar os tokens reconhecidos e, em seguida, o script vai criar um arquivo chamado `tabela_simbolos.html` na mesma pasta (basta abrir no navegador para ver a tabela final).

#### Teste 2: Código com erro léxico

```bash
python lexico.py erro_teste.saf
```

**O que vai acontecer:** O programa vai rodar normalmente, mas no fim da execução ele vai listar no terminal quais caracteres não pertencem à linguagem e em quais linhas eles estão.

```

```
