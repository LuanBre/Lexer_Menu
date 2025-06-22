import sys
import ply.lex as lex

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
    r'"[^\"]+"'
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
    print(f"Caractere inválido: {t.value[0]} na linha {t.lexer.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()

tarefas = {}
lookahead = None

def match(tipo):
    global lookahead
    if lookahead and lookahead.type == tipo:
        lookahead = lexer.token()
    else:
        erro = lookahead.value if lookahead else 'EOF'
        print(f"Erro sintático. Esperado: {tipo}, encontrado: {erro}")
        sys.exit(1)

def comando():
    global lookahead
    if not lookahead:
        return

    if lookahead.type == 'CRIAR':
        match('CRIAR')
        nome = lookahead.value
        match('IDENTIFICADOR')
        match('ATRIBUICAO')
        descricao = lookahead.value
        match('STRING')
        match('FIM')
        tarefas[nome] = {'descricao': descricao, 'status': 'pendente'}
        print(f"Tarefa '{nome}' criada: {descricao}")

    elif lookahead.type == 'REMOVER':
        match('REMOVER')
        nome = lookahead.value
        match('IDENTIFICADOR')
        match('FIM')
        if nome in tarefas:
            del tarefas[nome]
            print(f"Tarefa '{nome}' removida")
        else:
            print(f"Tarefa '{nome}' não encontrada")

    elif lookahead.type == 'STATUS':
        match('STATUS')
        nome = lookahead.value
        match('IDENTIFICADOR')
        match('ATRIBUICAO')
        novo_status = lookahead.value
        match('STRING')
        match('FIM')
        if nome in tarefas:
            tarefas[nome]['status'] = novo_status
            print(f"Status da tarefa '{nome}' alterado para '{novo_status}'")
        else:
            print(f"Tarefa '{nome}' não encontrada")

    elif lookahead.type == 'MOSTRAR':
        match('MOSTRAR')
        nome = lookahead.value
        match('IDENTIFICADOR')
        match('FIM')
        if nome in tarefas:
            t = tarefas[nome]
            print(f"{nome}: {t['descricao']} (Status: {t['status']})")
        else:
            print(f"Tarefa '{nome}' não encontrada")
    else:
        print(f"Erro sintático: Comando inesperado ou token inválido '{lookahead.value}' (Tipo: {lookahead.type})")
        sys.exit(1)

def programa():
    global lookahead
    lookahead = lexer.token()
    comando()


def menu():
    while True:
        print("\nGerenciador de Tarefas")
        print("1. Criar tarefa")
        print("2. Remover tarefa")
        print("3. Alterar status de tarefa")
        print("4. Mostrar tarefa")
        print("5. Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            nome = input("Nome da tarefa: ")
            descricao = input("Descrição: ")
            comando_str = f'criar_tarefa {nome} = "{descricao}";'

        elif opcao == '2':
            nome = input("Nome da tarefa para remover: ")
            comando_str = f'remover_tarefa {nome};'

        elif opcao == '3':
            nome = input("Nome da tarefa: ")
            status = input("Novo status: ")
            comando_str = f'alterar_status {nome} = "{status}";'

        elif opcao == '4':
            nome = input("Nome da tarefa: ")
            comando_str = f'mostrar_tarefa {nome};'

        elif opcao == '5':
            print("Saindo do gerenciador. Até logo!")
            break

        else:
            print("Opção inválida. Tente novamente.")
            continue

        try:
            lexer.input(comando_str)
            programa()
        except Exception as e:
            print(f"Erro ao processar comando: {e}")


menu()