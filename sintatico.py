import sys
import json
import os
from lexico import analise

class SafiraSyntaxError(Exception):
    def __init__(self, linha, mensagem):
        self.linha = linha
        self.mensagem = mensagem
        super().__init__(f"Erro sintático na linha {linha}: {mensagem}")

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.total_tokens = len(tokens)

    def peek(self):
        if self.pos < self.total_tokens:
            return self.tokens[self.pos]
        return None

    def previous(self):
        if self.pos > 0:
            return self.tokens[self.pos - 1]
        return None

    def is_at_end(self):
        return self.pos >= self.total_tokens

    def advance(self):
        if not self.is_at_end():
            self.pos += 1
        return self.previous()

    def check(self, tipo, valor=None):
        token = self.peek()
        if token is None:
            return False
        if token["tipo"] != tipo:
            return False
        if valor is not None and token["valor"] != valor:
            return False
        return True

    def match(self, tipo, valor=None):
        if self.check(tipo, valor):
            self.advance()
            return True
        return False

    def current_line(self):
        token = self.peek()
        if token:
            return token["linha"]
        prev = self.previous()
        if prev:
            return prev["linha"]
        return 1

    def consume(self, tipo, valor=None, error_msg=None):
        if self.check(tipo, valor):
            return self.advance()
        token = self.peek()
        line = token["linha"] if token else self.current_line()
        found_val = f"'{token['valor']}'" if token else "fim do arquivo"
        expected_val = f"'{valor}'" if valor else tipo
        msg = error_msg or f"Esperado {expected_val}, mas encontrado {found_val}."
        raise SafiraSyntaxError(line, msg)

    # 1. ESTRUTURA DO PROGRAMA
    def parse_program(self):
        body = []
        while not self.is_at_end():
            body.append(self.parse_top_level_decl())
        return {
            "type": "Program",
            "body": body,
            "line": 1
        }

    def parse_top_level_decl(self):
        token = self.peek()
        if token is None:
            raise SafiraSyntaxError(self.current_line(), "Declaração de nível superior esperada.")
            
        if token["tipo"] == "SUBROTINA" and token["valor"] == "function":
            return self.parse_function_decl()
        elif token["tipo"] == "SUBROTINA" and token["valor"] == "task":
            return self.parse_task_decl()
        elif token["tipo"] == "TIPO_DADO":
            return self.parse_global_var_decl()
        else:
            raise SafiraSyntaxError(
                token["linha"],
                f"Sintaxe inválida no nível superior: apenas declarações de variáveis globais, funções ou tasks são permitidas. Encontrado '{token['valor']}'."
            )

    # 2. DECLARAÇÕES
    def parse_global_var_decl(self):
        line = self.peek()["linha"]
        tipo = self.consume("TIPO_DADO")["valor"]
        name = self.consume("IDENTIFICADOR", error_msg="Nome de variável esperado após tipo de dado.")["valor"]
        
        initializer = None
        if self.match("OP_ATRIBUICAO"):
            initializer = self.parse_expression()
            
        self.consume("PONTO_VIRGULA", error_msg="Ponto e vírgula esperado no final da declaração de variável.")
        
        return {
            "type": "VariableDeclaration",
            "var_type": tipo,
            "name": name,
            "initializer": initializer,
            "line": line
        }

    def parse_local_var_decl(self):
        line = self.peek()["linha"]
        tipo = self.consume("TIPO_DADO")["valor"]
        name = self.consume("IDENTIFICADOR", error_msg="Nome de variável esperado após tipo de dado.")["valor"]
        
        initializer = None
        if self.match("OP_ATRIBUICAO"):
            initializer = self.parse_expression()
            
        self.consume("PONTO_VIRGULA", error_msg="Ponto e vírgula esperado no final da linha.")
        
        return {
            "type": "VariableDeclaration",
            "var_type": tipo,
            "name": name,
            "initializer": initializer,
            "line": line
        }

    def parse_function_decl(self):
        line = self.peek()["linha"]
        self.consume("SUBROTINA", "function")
        return_type = self.consume("TIPO_DADO", error_msg="Tipo de retorno esperado após 'function'.")["valor"]
        name = self.consume("IDENTIFICADOR", error_msg="Nome de função esperado após tipo de retorno.")["valor"]
        
        self.consume("ABRE_PARENTESES", error_msg="Parênteses '(' esperados após nome da função.")
        params = []
        if not self.check("FECHA_PARENTESES"):
            params = self.parse_parameters()
        self.consume("FECHA_PARENTESES", error_msg="Parênteses ')' esperados para fechar a lista de parâmetros.")
        
        body = self.parse_block("Corpo da função deve ser delimitado por chaves '{}'.")
        
        return {
            "type": "FunctionDeclaration",
            "return_type": return_type,
            "name": name,
            "parameters": params,
            "body": body,
            "line": line
        }

    def parse_task_decl(self):
        line = self.peek()["linha"]
        self.consume("SUBROTINA", "task")
        name = self.consume("IDENTIFICADOR", error_msg="Nome da task esperado após 'task'.")["valor"]
        
        self.consume("ABRE_PARENTESES", error_msg="Parênteses '(' esperados após nome da task.")
        params = []
        if not self.check("FECHA_PARENTESES"):
            params = self.parse_parameters()
        self.consume("FECHA_PARENTESES", error_msg="Parênteses ')' esperados para fechar a lista de parâmetros.")
        
        body = self.parse_block("Corpo da task deve ser delimitado por chaves '{}'.")
        
        return {
            "type": "TaskDeclaration",
            "name": name,
            "parameters": params,
            "body": body,
            "line": line
        }

    def parse_parameters(self):
        params = []
        params.append(self.parse_parameter())
        while self.match("VIRGULA"):
            params.append(self.parse_parameter())
        return params

    def parse_parameter(self):
        line = self.peek()["linha"]
        tipo = self.consume("TIPO_DADO", error_msg="Tipo de dado esperado para o parâmetro.")["valor"]
        name = self.consume("IDENTIFICADOR", error_msg="Nome de identificador esperado para o parâmetro.")["valor"]
        return {
            "type": "Parameter",
            "var_type": tipo,
            "name": name,
            "line": line
        }

    # 3. COMANDOS (STATEMENTS)
    def parse_block(self, custom_error=None):
        line = self.peek()["linha"] if self.peek() else self.current_line()
        self.consume("ABRE_CHAVE", error_msg=custom_error or "Esperado '{' para iniciar bloco.")
        statements = []
        while not self.check("FECHA_CHAVE") and not self.is_at_end():
            statements.append(self.parse_statement())
        self.consume("FECHA_CHAVE", error_msg="Esperado '}' para fechar bloco.")
        return {
            "type": "Block",
            "statements": statements,
            "line": line
        }

    def parse_statement(self):
        token = self.peek()
        if token is None:
            raise SafiraSyntaxError(self.current_line(), "Comando esperado, fim de arquivo alcançado.")
        
        if token["tipo"] == "ABRE_CHAVE":
            return self.parse_block()
        
        if token["tipo"] == "TIPO_DADO":
            return self.parse_local_var_decl()
            
        if token["tipo"] == "CONTROLE_FLUXO":
            if token["valor"] == "if":
                return self.parse_if_stmt()
            elif token["valor"] == "switch":
                return self.parse_switch_stmt()
            else:
                raise SafiraSyntaxError(token["linha"], f"Comando de controle de fluxo inesperado: '{token['valor']}'.")
                
        if token["tipo"] == "ESTRUTURA_LOOP":
            if token["valor"] == "while":
                return self.parse_while_stmt()
            elif token["valor"] == "for":
                return self.parse_for_stmt()
                
        if token["tipo"] == "CONTROLE_LOOP":
            if token["valor"] == "break":
                return self.parse_break_stmt()
            elif token["valor"] == "continue":
                return self.parse_continue_stmt()
                
        if token["tipo"] == "SUBROTINA" and token["valor"] == "return":
            return self.parse_return_stmt()
            
        if token["tipo"] == "BLOCO_SEGURO" and token["valor"] == "attempt":
            return self.parse_attempt_stmt()
            
        if token["tipo"] == "IDENTIFICADOR":
            next_token = self.tokens[self.pos + 1] if self.pos + 1 < self.total_tokens else None
            if next_token and next_token["tipo"] == "OP_ATRIBUICAO":
                return self.parse_assignment()
            else:
                return self.parse_expr_stmt()
                
        return self.parse_expr_stmt()

    def parse_assignment(self):
        line = self.peek()["linha"]
        name = self.consume("IDENTIFICADOR")["valor"]
        self.consume("OP_ATRIBUICAO")
        value = self.parse_expression()
        self.consume("PONTO_VIRGULA", error_msg="Ponto e vírgula esperado no final da linha.")
        return {
            "type": "Assignment",
            "name": name,
            "value": value,
            "line": line
        }

    def parse_expr_stmt(self):
        line = self.peek()["linha"]
        expr = self.parse_expression()
        self.consume("PONTO_VIRGULA", error_msg="Ponto e vírgula esperado no final da linha.")
        return {
            "type": "ExpressionStatement",
            "expression": expr,
            "line": line
        }

    def parse_if_stmt(self):
        line = self.peek()["linha"]
        self.consume("CONTROLE_FLUXO", "if")
        
        if not self.check("ABRE_PARENTESES"):
            raise SafiraSyntaxError(line, "Parênteses () esperados após if.")
        self.consume("ABRE_PARENTESES")
        
        condition = self.parse_expression()
        
        self.consume("FECHA_PARENTESES", error_msg="Parênteses ')' esperados para fechar a condição do if.")
        
        then_branch = self.parse_statement()
        
        else_branch = None
        if self.match("CONTROLE_FLUXO", "else"):
            else_branch = self.parse_statement()
            
        return {
            "type": "IfStatement",
            "condition": condition,
            "then_branch": then_branch,
            "else_branch": else_branch,
            "line": line
        }

    def parse_switch_stmt(self):
        line = self.peek()["linha"]
        self.consume("CONTROLE_FLUXO", "switch")
        
        if not self.check("ABRE_PARENTESES"):
            raise SafiraSyntaxError(line, "Parênteses () esperados após switch.")
        self.consume("ABRE_PARENTESES")
        
        expr = self.parse_expression()
        
        self.consume("FECHA_PARENTESES", error_msg="Parênteses ')' esperados após a expressão do switch.")
        self.consume("ABRE_CHAVE", error_msg="Chave '{' esperada para abrir o bloco switch.")
        
        cases = []
        default_case = None
        
        while self.match("CONTROLE_FLUXO", "case"):
            case_line = self.previous()["linha"]
            case_expr = self.parse_expression()
            self.consume("DOIS_PONTOS", error_msg="Dois pontos ':' esperados após o valor do case.")
            
            case_stmts = []
            while not self.check("CONTROLE_FLUXO", "case") and not self.check("CONTROLE_FLUXO", "default") and not self.check("FECHA_CHAVE") and not self.is_at_end():
                case_stmts.append(self.parse_statement())
                
            cases.append({
                "type": "SwitchCase",
                "expression": case_expr,
                "statements": case_stmts,
                "line": case_line
            })
            
        if self.match("CONTROLE_FLUXO", "default"):
            default_line = self.previous()["linha"]
            self.consume("DOIS_PONTOS", error_msg="Dois pontos ':' esperados após 'default'.")
            
            default_stmts = []
            while not self.check("FECHA_CHAVE") and not self.is_at_end():
                default_stmts.append(self.parse_statement())
                
            default_case = {
                "type": "SwitchDefault",
                "statements": default_stmts,
                "line": default_line
            }
            
        self.consume("FECHA_CHAVE", error_msg="Chave '}' esperada para fechar o bloco switch.")
        
        return {
            "type": "SwitchStatement",
            "expression": expr,
            "cases": cases,
            "default_case": default_case,
            "line": line
        }

    def parse_while_stmt(self):
        line = self.peek()["linha"]
        self.consume("ESTRUTURA_LOOP", "while")
        
        if not self.check("ABRE_PARENTESES"):
            raise SafiraSyntaxError(line, "Parênteses () esperados após while.")
        self.consume("ABRE_PARENTESES")
        
        condition = self.parse_expression()
        
        self.consume("FECHA_PARENTESES", error_msg="Parênteses ')' esperados após a condição do while.")
        
        body = self.parse_statement()
        
        return {
            "type": "WhileStatement",
            "condition": condition,
            "body": body,
            "line": line
        }

    def parse_for_stmt(self):
        line = self.peek()["linha"]
        self.consume("ESTRUTURA_LOOP", "for")
        
        if not self.check("ABRE_PARENTESES"):
            raise SafiraSyntaxError(line, "Parênteses () esperados após for.")
        self.consume("ABRE_PARENTESES")
        
        initializer = None
        if not self.check("PONTO_VIRGULA"):
            if self.check("TIPO_DADO"):
                init_line = self.peek()["linha"]
                tipo = self.consume("TIPO_DADO")["valor"]
                name = self.consume("IDENTIFICADOR", error_msg="Nome de variável esperado no inicializador do loop for.")["valor"]
                init_val = None
                if self.match("OP_ATRIBUICAO"):
                    init_val = self.parse_expression()
                initializer = {
                    "type": "VariableDeclaration",
                    "var_type": tipo,
                    "name": name,
                    "initializer": init_val,
                    "line": init_line
                }
            else:
                token = self.peek()
                next_token = self.tokens[self.pos + 1] if self.pos + 1 < self.total_tokens else None
                if token and token["tipo"] == "IDENTIFICADOR" and next_token and next_token["tipo"] == "OP_ATRIBUICAO":
                    init_line = token["linha"]
                    name = self.consume("IDENTIFICADOR")["valor"]
                    self.consume("OP_ATRIBUICAO")
                    value = self.parse_expression()
                    initializer = {
                        "type": "Assignment",
                        "name": name,
                        "value": value,
                        "line": init_line
                    }
                else:
                    initializer = self.parse_expression()
                    
        self.consume("PONTO_VIRGULA", error_msg="Ponto e vírgula esperado no loop for.")
        
        condition = None
        if not self.check("PONTO_VIRGULA"):
            condition = self.parse_expression()
            
        self.consume("PONTO_VIRGULA", error_msg="Ponto e vírgula esperado no loop for.")
        
        step = None
        if not self.check("FECHA_PARENTESES"):
            token = self.peek()
            next_token = self.tokens[self.pos + 1] if self.pos + 1 < self.total_tokens else None
            if token and token["tipo"] == "IDENTIFICADOR" and next_token and next_token["tipo"] == "OP_ATRIBUICAO":
                step_line = token["linha"]
                name = self.consume("IDENTIFICADOR")["valor"]
                self.consume("OP_ATRIBUICAO")
                value = self.parse_expression()
                step = {
                    "type": "Assignment",
                    "name": name,
                    "value": value,
                    "line": step_line
                }
            else:
                step = self.parse_expression()
                
        self.consume("FECHA_PARENTESES", error_msg="Parênteses ')' esperados após as cláusulas do loop for.")
        
        body = self.parse_statement()
        
        return {
            "type": "ForStatement",
            "initializer": initializer,
            "condition": condition,
            "step": step,
            "body": body,
            "line": line
        }

    def parse_break_stmt(self):
        line = self.peek()["linha"]
        self.consume("CONTROLE_LOOP", "break")
        self.consume("PONTO_VIRGULA", error_msg="Ponto e vírgula esperado no final da linha.")
        return {
            "type": "BreakStatement",
            "line": line
        }

    def parse_continue_stmt(self):
        line = self.peek()["linha"]
        self.consume("CONTROLE_LOOP", "continue")
        self.consume("PONTO_VIRGULA", error_msg="Ponto e vírgula esperado no final da linha.")
        return {
            "type": "ContinueStatement",
            "line": line
        }

    def parse_return_stmt(self):
        line = self.peek()["linha"]
        self.consume("SUBROTINA", "return")
        expr = None
        if not self.check("PONTO_VIRGULA"):
            expr = self.parse_expression()
        self.consume("PONTO_VIRGULA", error_msg="Ponto e vírgula esperado no final da linha.")
        return {
            "type": "ReturnStatement",
            "expression": expr,
            "line": line
        }

    def parse_attempt_stmt(self):
        line = self.peek()["linha"]
        self.consume("BLOCO_SEGURO", "attempt")
        attempt_block = self.parse_block("Bloco attempt deve ser delimitado por chaves '{}'.")
        
        self.consume("BLOCO_SEGURO", "fallback", error_msg="Bloco 'fallback' esperado após o bloco 'attempt'.")
        fallback_block = self.parse_block("Bloco fallback deve ser delimitado por chaves '{}'.")
        
        return {
            "type": "AttemptFallback",
            "attempt_block": attempt_block,
            "fallback_block": fallback_block,
            "line": line
        }

    # 4. EXPRESSÕES (PRECEDÊNCIA)
    def parse_expression(self):
        return self.parse_pipeline()

    def parse_pipeline(self):
        expr = self.parse_logical_or()
        while self.match("OP_PIPELINE"):
            line = self.previous()["linha"]
            right = self.parse_logical_or()
            expr = {
                "type": "PipelineExpression",
                "left": expr,
                "right": right,
                "line": line
            }
        return expr

    def parse_logical_or(self):
        expr = self.parse_logical_and()
        while self.match("OP_LOGICO", "or"):
            line = self.previous()["linha"]
            right = self.parse_logical_and()
            expr = {
                "type": "BinaryExpression",
                "operator": "or",
                "left": expr,
                "right": right,
                "line": line
            }
        return expr

    def parse_logical_and(self):
        expr = self.parse_logical_not()
        while self.match("OP_LOGICO", "and"):
            line = self.previous()["linha"]
            right = self.parse_logical_not()
            expr = {
                "type": "BinaryExpression",
                "operator": "and",
                "left": expr,
                "right": right,
                "line": line
            }
        return expr

    def parse_logical_not(self):
        if self.match("OP_LOGICO", "not"):
            line = self.previous()["linha"]
            arg = self.parse_logical_not()
            return {
                "type": "UnaryExpression",
                "operator": "not",
                "argument": arg,
                "line": line
            }
        return self.parse_comparison()

    def parse_comparison(self):
        expr = self.parse_addition()
        while self.check("OP_COMPARACAO"):
            op_token = self.advance()
            line = op_token["linha"]
            op = op_token["valor"]
            right = self.parse_addition()
            expr = {
                "type": "BinaryExpression",
                "operator": op,
                "left": expr,
                "right": right,
                "line": line
            }
        return expr

    def parse_addition(self):
        expr = self.parse_multiplication()
        while self.check("OP_SOMA") or self.check("OP_SUBTRACAO"):
            op_token = self.advance()
            line = op_token["linha"]
            op = op_token["valor"]
            right = self.parse_multiplication()
            expr = {
                "type": "BinaryExpression",
                "operator": op,
                "left": expr,
                "right": right,
                "line": line
            }
        return expr

    def parse_multiplication(self):
        expr = self.parse_unary()
        while self.check("OP_MULTIPLICACAO") or self.check("OP_DIVISAO") or self.check("OP_RESTO"):
            op_token = self.advance()
            line = op_token["linha"]
            op = op_token["valor"]
            right = self.parse_unary()
            expr = {
                "type": "BinaryExpression",
                "operator": op,
                "left": expr,
                "right": right,
                "line": line
            }
        return expr

    def parse_unary(self):
        if self.check("OP_SUBTRACAO") or self.check("OP_SOMA"):
            op_token = self.advance()
            line = op_token["linha"]
            op = op_token["valor"]
            arg = self.parse_unary()
            return {
                "type": "UnaryExpression",
                "operator": op,
                "argument": arg,
                "line": line
            }
        return self.parse_primary()

    def parse_primary(self):
        token = self.peek()
        if token is None:
            raise SafiraSyntaxError(self.current_line(), "Expressão esperada, mas fim do arquivo alcançado.")
            
        if self.match("LITERAL_INT"):
            val_str = self.previous()["valor"]
            return {
                "type": "LiteralInt",
                "value": int(val_str),
                "line": self.previous()["linha"]
            }
            
        if self.match("LITERAL_FLOAT"):
            val_str = self.previous()["valor"]
            return {
                "type": "LiteralFloat",
                "value": float(val_str),
                "line": self.previous()["linha"]
            }
            
        if self.match("LITERAL_STRING"):
            val_str = self.previous()["valor"]
            if val_str.startswith('"') and val_str.endswith('"'):
                val_str = val_str[1:-1]
            return {
                "type": "LiteralString",
                "value": val_str,
                "line": self.previous()["linha"]
            }
            
        if self.match("IDENTIFICADOR"):
            name_token = self.previous()
            name = name_token["valor"]
            line = name_token["linha"]
            
            if self.match("ABRE_PARENTESES"):
                args = []
                if not self.check("FECHA_PARENTESES"):
                    args.append(self.parse_expression())
                    while self.match("VIRGULA"):
                        args.append(self.parse_expression())
                self.consume("FECHA_PARENTESES", error_msg="Parênteses ')' esperados para fechar chamada de função.")
                return {
                    "type": "CallExpression",
                    "callee": name,
                    "arguments": args,
                    "line": line
                }
                
            return {
                "type": "Identifier",
                "name": name,
                "line": line
            }
            
        if self.match("ABRE_PARENTESES"):
            expr = self.parse_expression()
            self.consume("FECHA_PARENTESES", error_msg="Parênteses ')' esperados para fechar a expressão.")
            return expr
            
        raise SafiraSyntaxError(
            token["linha"],
            f"Fator de expressão inesperado: '{token['valor']}'."
        )

# ================= EXECUÇÃO =================
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso correto: python sintatico.py <arquivo.saf>")
        sys.exit(1)
        
    arquivo_entrada = sys.argv[1]
    
    # 1. Análise Léxica
    tabela_tokens, lista_erros = analise(arquivo_entrada)
    
    if lista_erros:
        print("Erro Léxico detectado! A análise sintática foi abortada.")
        for e in lista_erros:
            print(f" -> {e}")
        sys.exit(1)
        
    # 2. Análise Sintática
    parser = Parser(tabela_tokens)
    try:
        ast = parser.parse_program()
        print("Sucesso! Análise sintática concluída sem erros.")
        
        # 3. Exportar AST em JSON
        nome_ast = "ast.json"
        with open(nome_ast, "w", encoding="utf-8") as f:
            json.dump(ast, f, indent=2, ensure_ascii=False)
        print(f"-> Arquivo '{nome_ast}' exportado com sucesso!\n")
        sys.exit(0)
        
    except SafiraSyntaxError as e:
        print(f"Erro Sintático detectado:")
        print(f" -> {e}")
        sys.exit(1)
