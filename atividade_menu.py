import sys
import ply.lex as lex

# --- Definição do Lexer ---

reservadas = {
    'criar_tarefa': 'CRIAR',
    'remover_tarefa': 'REMOVER',
    'alterar_status': 'STATUS',
    'mostrar_tarefa': 'MOSTRAR',
}

tokens = [
    'IDENTIFICADOR',
    'STRING',
    'ATRIBUICAO',
    'FIM'
] + list(reservadas.values())

t_ATRIBUICAO = r'='
t_FIM = r';'
t_ignore = ' \t'

def t_STRING(t):
    r'"[^"]+"'
    t.value = t.value.strip('"')
    return t

def t_IDENTIFICADOR(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reservadas.get(t.value, 'IDENTIFICADOR')
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Caractere inválido: '{t.value[0]}' na linha {t.lexer.lineno}")
    t.lexer.skip(1)
    sys.exit(1)

lexer = lex.lex()

# --- Analisador / Interpretador ---

tarefas = {}
lookahead = None

def match(tipo):
    global lookahead
    if lookahead and lookahead.type == tipo:
        lookahead = lexer.token()
    else:
        erro = lookahead.value if lookahead else 'EOF (Fim da Entrada)'
        print(f"Erro sintático. Esperado: '{tipo}', encontrado: '{erro}'")
        sys.exit(1)

def obter_nome_tarefa():
    global lookahead
    if lookahead.type in ('IDENTIFICADOR', 'STRING'):
        nome = lookahead.value
        match(lookahead.type)
        return nome
    else:
        print(f"Erro: Nome de tarefa inválido: '{lookahead.value}'")
        sys.exit(1)

def comando():
    global lookahead
    if not lookahead:
        return

    if lookahead.type == 'CRIAR':
        match('CRIAR')
        nome = obter_nome_tarefa()
        match('ATRIBUICAO')
        descricao = lookahead.value
        match('STRING')
        match('FIM')
        if nome in tarefas:
            print(f"Erro: Já existe uma tarefa com o nome '{nome}'.")
        else:
            tarefas[nome] = {'descricao': descricao, 'status': 'pendente'}
            print(f"Tarefa '{nome}' criada: '{descricao}'")

    elif lookahead.type == 'REMOVER':
        match('REMOVER')
        nome = obter_nome_tarefa()
        match('FIM')
        if nome in tarefas:
            del tarefas[nome]
            print(f"Tarefa '{nome}' removida")
        else:
            print(f"Erro: Tarefa '{nome}' não encontrada para remoção.")

    elif lookahead.type == 'STATUS':
        match('STATUS')
        nome = obter_nome_tarefa()
        match('ATRIBUICAO')
        novo_status = lookahead.value
        match('STRING')
        match('FIM')
        if nome in tarefas:
            status_validos = ['pendente', 'em andamento', 'finalizado']
            if novo_status not in status_validos:
                print(f"Erro: Status inválido. Use um dos seguintes: {', '.join(status_validos)}")
            else:
                tarefas[nome]['status'] = novo_status
                print(f"Status da tarefa '{nome}' alterado para '{novo_status}'")
        else:
            print(f"Erro: Tarefa '{nome}' não encontrada para alterar status.")

    elif lookahead.type == 'MOSTRAR':
        match('MOSTRAR')
        nome = obter_nome_tarefa()
        match('FIM')
        if nome in tarefas:
            t = tarefas[nome]
            print(f"{nome}: {t['descricao']} (Status: {t['status']})")
        else:
            print(f"Erro: Tarefa '{nome}' não encontrada para mostrar.")
    else:
        print(f"Erro sintático: Comando inesperado ou token inválido '{lookahead.value}' (Tipo: {lookahead.type})")
        sys.exit(1)

def programa(comando_string):
    global lookahead
    lexer.input(comando_string)
    lookahead = lexer.token()
    comando()

# --- Interface do Usuário ---

def menu():
    while True:
        print("\n--- Gerenciador de Tarefas ---")
        print("1. Criar tarefa")
        print("2. Remover tarefa")
        print("3. Alterar status de tarefa")
        print("4. Mostrar tarefa")
        print("5. Sair")

        opcao = input("Escolha uma opção: ").strip()
        comando_str = ""

        if opcao == '1':
            nome = input("Nome da tarefa: ").strip()
            descricao = input("Descrição: ").strip()
            comando_str = f'criar_tarefa "{nome}" = "{descricao}";'

        elif opcao == '2':
            nome = input("Nome da tarefa para remover: ").strip()
            comando_str = f'remover_tarefa "{nome}";'

        elif opcao == '3':
            nome = input("Nome da tarefa: ").strip()
            print("Escolha o novo status:")
            print("1. pendente")
            print("2. em andamento")
            print("3. finalizado")
            op_status = input("Opção de status: ").strip()
            status_opcoes = {'1': 'pendente', '2': 'em andamento', '3': 'finalizado'}
            status = status_opcoes.get(op_status)
            if not status:
                print("Status inválido. Tente novamente.")
                continue
            comando_str = f'alterar_status "{nome}" = "{status}";'

        elif opcao == '4':
            nome = input("Nome da tarefa: ").strip()
            comando_str = f'mostrar_tarefa "{nome}";'

        elif opcao == '5':
            print("Saindo do gerenciador. Até logo!")
            break

        else:
            print("Opção inválida. Tente novamente.")
            continue

        try:
            programa(comando_str)
        except SystemExit:
            print("Ocorreu um erro de sintaxe ou caractere inválido. Por favor, tente novamente.")
            global lexer, lookahead
            lexer = lex.lex()
            lookahead = None
            continue
        except Exception as e:
            print(f"Ocorreu um erro inesperado: {e}")

# Executa o menu
if __name__ == "__main__":
    menu()
