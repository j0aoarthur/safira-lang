import subprocess
import os
import sys

def run_cmd(cmd, cwd="."):
    result = subprocess.run(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        errors="replace"
    )
    return result.returncode, (result.stdout or "") + (result.stderr or "")

def print_result(name, success, message=""):
    status = "[OK]" if success else "[FALHOU]"
    print(f"{status} {name}")
    if not success and message:
        print(f"   -> Detalhes: {message}")

def main():
    print("=== INICIANDO TESTES DO ANALISADOR SINTÁTICO ===")
    
    # 1. Testar código válido
    code, output = run_cmd("python sintatico.py codigo_exemplo.saf")
    success = (code == 0 and "Sucesso!" in output and os.path.exists("ast.json"))
    print_result("1. Código Válido (codigo_exemplo.saf)", success, output)
    if not success:
        sys.exit(1)
        
    # 2. Testar erro sintático 1 (Falta de parênteses no if)
    code, output = run_cmd("python sintatico.py codigo_erro_sintatico.saf")
    expected_msg = "Parênteses () esperados após if"
    success = (code == 1 and expected_msg in output)
    print_result("2. Erro Sintático 1 (Falta de parênteses no if)", success, f"Esperado contendo '{expected_msg}'. Saída obtida: {output.strip()}")
    
    # 3. Testar erro sintático 2 (Falta de ponto e vírgula)
    # Vamos gerar uma versão temporária corrigindo apenas o primeiro erro
    temp_file = "temp_erro_teste.saf"
    with open("codigo_erro_sintatico.saf", "r", encoding="utf-8") as f:
        content = f.read()
        
    # Corrigindo if a > b para if (a > b)
    content_fixed_1 = content.replace("if a > b", "if (a > b)")
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(content_fixed_1)
        
    code, output = run_cmd(f"python sintatico.py {temp_file}")
    expected_msg = "Ponto e vírgula esperado no final da linha"
    success = (code == 1 and expected_msg in output)
    print_result("3. Erro Sintático 2 (Falta de ponto e vírgula)", success, f"Esperado contendo '{expected_msg}'. Saída obtida: {output.strip()}")

    # 4. Testar erro sintático 3 (Falta de fechar parênteses na chamada de função)
    # Vamos corrigir também o ponto e vírgula
    content_fixed_2 = content_fixed_1.replace("b = 30", "b = 30;")
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(content_fixed_2)
        
    code, output = run_cmd(f"python sintatico.py {temp_file}")
    expected_msg = "Parênteses ')' esperados para fechar chamada de função"
    success = (code == 1 and expected_msg in output)
    print_result("4. Erro Sintático 3 (Falta de fechar parênteses)", success, f"Esperado contendo '{expected_msg}'. Saída obtida: {output.strip()}")

    # Limpar arquivo temporário
    if os.path.exists(temp_file):
        os.remove(temp_file)
        
    print("=== FIM DOS TESTES ===\n")

if __name__ == "__main__":
    main()
