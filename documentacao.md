# Especificação da Linguagem: Vortex

## 1. Introdução
Vortex é uma linguagem de programação procedural, fortemente tipada, desenvolvida para o trabalho da disciplina de Compiladores. Ela possui uma sintaxe baseada em C e Java, mas traz alguns diferenciais práticos para tratamento de erros e fluxo de dados.

---

## 2. Tipos de Dados
A linguagem trabalha com três tipos de dados primitivos:
* **`int`**: Números inteiros (Ex: `10`, `-42`).
* **`float`**: Números reais com ponto (Ex: `3.14`, `0.0`).
* **`string`**: Texto entre aspas duplas (Ex: `"Olá, Mundo"`).

---

## 3. Palavras-Chave e Identificadores
Os nomes de variáveis e funções devem começar com letra ou underline (`_`), seguidos de letras, números ou underlines. 

As palavras reservadas da linguagem são:
* **Tipos:** `int`, `float`, `string`.
* **Controle de Fluxo:** `if`, `else`, `switch`, `case`, `default`.
* **Repetição:** `while`, `for`, `break`, `continue`.
* **Sub-rotinas:** `function`, `task`, `return`.
* **Operadores Lógicos:** `and`, `or`, `not`.
* **Tratamento de Erros:** `attempt`, `fallback`.

---

## 4. Operadores

* **Aritméticos:** `+` (Soma), `-` (Subtração), `*` (Multiplicação), `/` (Divisão), `%` (Resto). Aceita o uso de parênteses `()`.
* **Lógicos:** `and`, `or`, `not`.
* **Comparação:** `==` (Igual), `!=` (Diferente), `>` (Maior), `<` (Menor), `>=` (Maior ou igual), `<=` (Menor ou igual).
* **Atribuição:** `=`.
* **Pipeline (`|>`):** Pega o resultado do que está na esquerda e joga como argumento para o que está na direita. Exemplo: em vez de fazer `print(sqrt(25))`, o código fica `25 |> sqrt() |> print();`.

---

## 5. Estruturas de Controle e Repetição

* **Condicionais:** `if / else` tradicional e `switch / case / default` para múltiplas escolhas.
* **Laços de Repetição:** 
  * `while`: repete enquanto a condição for verdadeira.
  * `for`: loop com contador integrado.
  * O fluxo do loop pode ser alterado usando `break` e `continue`.
* **Tratamento de Exceção (`attempt / fallback`):** Funciona como uma alternativa ao try/catch. O código dentro do `attempt` é executado. Se der algum erro (ex: divisão por zero), o programa não quebra; ele desvia o fluxo para o `fallback` para tratar o problema e seguir a execução.

---

## 6. Sub-rotinas
A linguagem separa funções que têm retorno das que não têm:
* **`task`**: São procedimentos comuns. Executam uma rotina, mas não retornam nenhum valor.
* **`function`**: Funções que processam dados e obrigatoriamente devolvem um valor usando `return`.

---

## 7. Comentários
* **Linha Única:** Usando `//`.
* **Múltiplas Linhas:** Entre `/*` e `*/`.