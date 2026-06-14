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

Este repositório contém o TDE de Compiladores. Criamos a linguagem procedural **Safira** e implementamos o seu Analisador Léxico (TDE1) e Analisador Sintático (TDE2) usando Python. 

O analisador léxico lê o código-fonte, usa Expressões Regulares (Regex) para identificar os tokens e gera a tabela de símbolos em formato HTML.
O analisador sintático valida a sequência de tokens estruturalmente usando uma abordagem preditiva por descida recursiva, gerando a Árvore Sintática Abstrata (AST) em formato JSON.

### Arquivos:

- `lexico.py`: Script principal do analisador léxico.
- `sintatico.py`: Script principal do analisador sintático.
- `documentacao.md`: Regras, palavras-chave e sintaxe da linguagem.
- `codigo_exemplo.saf`: Exemplo de código válido usando todas as estruturas da linguagem.
- `erro_teste.saf`: Arquivo com caracteres inválidos propositais para testar o analisador léxico.
- `codigo_erro_sintatico.saf`: Arquivo com erros sintáticos propositais para testar o analisador sintático.
- `testar_sintatico.py`: Script de teste automatizado para os analisadores.

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

---

## Como rodar o Analisador Sintático

### Execução

Pelo terminal, execute o analisador sintático informando o arquivo que deseja analisar:

```bash
python sintatico.py <nome_do_arquivo>
```

#### Teste 1: Código correto

```bash
python sintatico.py codigo_exemplo.saf
```

**O que vai acontecer:** O script exibirá uma mensagem de sucesso no terminal e criará o arquivo `ast.json` contendo a Árvore Sintática Abstrata (AST) do código.

#### Teste 2: Código com erro sintático

```bash
python sintatico.py codigo_erro_sintatico.saf
```

**O que vai acontecer:** O analisador sintático abortará na primeira inconsistência gramatical, apontando a linha e qual estrutura era esperada.

---

## Como rodar os Testes Automatizados

O projeto conta com um script de testes que executa automaticamente o analisador sintático em cenários de sucesso e erro, certificando a conformidade de todas as saídas e regras.

```bash
python testar_sintatico.py
```
