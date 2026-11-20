import math
from datetime import datetime

from modelos.usuario import Usuario
from contas.conta import Conta
from contas.conta_poupanca import ContaPoupanca
from contas.conta_corrente import ContaCorrente
from contas.conta_especial import ContaEspecial


TIPOS_CONTA = {
    "1": "Conta",
    "2": "Conta Poupança",
    "3": "Conta Corrente",
    "4": "Conta Especial",
}

NOMES_TIPO = {
    Conta: "Conta",
    ContaPoupanca: "Conta Poupança",
    ContaCorrente: "Conta Corrente",
    ContaEspecial: "Conta Especial",
}


# ==========================================
# FUNÇÕES DE ENTRADA (com validação)
# ==========================================

def ler_texto(mensagem):
    while True:
        texto = input(mensagem).strip()
        if texto:
            return texto
        print("Entrada inválida: o campo não pode ficar vazio.")


def ler_opcao(mensagem, opcoes_validas):
    while True:
        opcao = input(mensagem).strip()
        if opcao in opcoes_validas:
            return opcao
        print("Opção inválida. Tente novamente.")


def ler_inteiro(mensagem, minimo=None, maximo=None):
    while True:
        try:
            numero = int(input(mensagem).strip())
        except ValueError:
            print("Entrada inválida: digite um número inteiro.")
            continue

        if minimo is not None and numero < minimo:
            print(f"O valor deve ser maior ou igual a {minimo}.")
        elif maximo is not None and numero > maximo:
            print(f"O valor deve ser menor ou igual a {maximo}.")
        else:
            return numero


def ler_decimal(mensagem, minimo=None):
    while True:
        texto = input(mensagem).strip().replace(",", ".")
        try:
            numero = float(texto)
        except ValueError:
            print("Entrada inválida: digite um número (ex.: 150.50).")
            continue

        if not math.isfinite(numero):
            print("Entrada inválida: digite um número válido.")
        elif minimo is not None and numero < minimo:
            print(f"O valor deve ser maior ou igual a {minimo}.")
        else:
            return numero


def ler_data(mensagem):
    while True:
        texto = input(mensagem).strip()
        try:
            return datetime.strptime(texto, "%d/%m/%Y")
        except ValueError:
            print("Data inválida. Use o formato dd/mm/aaaa.")


def ler_cpf(mensagem, usuarios):
    while True:
        cpf = input(mensagem).strip()
        if not (cpf.isdigit() and len(cpf) == 11):
            print("CPF inválido: digite 11 números, sem pontos ou traços.")
        elif cpf in usuarios:
            print("Já existe um usuário cadastrado com esse CPF.")
        else:
            return cpf


# ==========================================
# LOCALIZAÇÃO DE CONTAS (memória ou arquivo)
# ==========================================

def localizar_conta(contas, agencia, rg):
    """Procura a conta em memória; se não estiver, tenta restaurá-la do arquivo."""
    chave = Conta.montar_nome_arquivo(agencia, rg)

    if chave in contas:
        return contas[chave]

    conta = Conta.restaurar_de_arquivo(agencia, rg)
    if conta is not None:
        contas[chave] = conta
    return conta


def escolher_usuario(usuarios):
    lista = list(usuarios.values())

    print("\nUsuários cadastrados:")
    for i, usuario in enumerate(lista, start=1):
        print(f"  {i}) {usuario.nome} (CPF {usuario.cpf})")

    indice = ler_inteiro("Escolha o usuário (número): ", 1, len(lista))
    return lista[indice - 1]


# ==========================================
# AÇÕES FORA DA SESSÃO
# ==========================================

def acao_cadastrar_usuario(usuarios):
    print("\n--- Cadastro de usuário ---")
    nome = ler_texto("Nome: ")
    rg = ler_texto("RG: ")
    cpf = ler_cpf("CPF (11 números): ", usuarios)
    data_nascimento = ler_data("Data de nascimento (dd/mm/aaaa): ")

    usuarios[cpf] = Usuario(rg, cpf, nome, data_nascimento)
    print(f"Usuário {nome} cadastrado com sucesso.")


def acao_abrir_conta(usuarios, contas):
    if not usuarios:
        print("Cadastre um usuário antes de abrir uma conta.")
        return

    print("\n--- Abertura de conta ---")
    usuario = escolher_usuario(usuarios)

    print("\nTipos de conta:")
    for codigo, nome in TIPOS_CONTA.items():
        print(f"  {codigo}) {nome}")
    tipo = ler_opcao("Escolha o tipo: ", TIPOS_CONTA)

    agencia = ler_inteiro("Agência: ", minimo=0)

    chave = Conta.montar_nome_arquivo(agencia, usuario.rg)
    if chave in contas or Conta.arquivo_existe(agencia, usuario.rg):
        print(
            "Já existe uma conta com essa agência e esse RG (em memória ou salva em "
            "arquivo). Use outra agência ou efetue login nela."
        )
        return

    saldo = ler_decimal("Saldo inicial (R$): ", minimo=0)
    data_abertura = datetime.now()

    if tipo == "1":
        conta = Conta(agencia, usuario, data_abertura, saldo)
    elif tipo == "2":
        taxa_rendimento = ler_decimal("Taxa de rendimento (%): ", minimo=0)
        conta = ContaPoupanca(agencia, usuario, data_abertura, saldo, taxa_rendimento)
    elif tipo == "3":
        taxa_manutencao = ler_decimal("Taxa de manutenção (R$): ", minimo=0)
        conta = ContaCorrente(agencia, usuario, data_abertura, saldo, taxa_manutencao)
    else:
        taxa_manutencao = ler_decimal("Taxa de manutenção (R$): ", minimo=0)
        limite = ler_decimal("Limite do cheque especial (R$): ", minimo=0)
        conta = ContaEspecial(agencia, usuario, data_abertura, saldo, taxa_manutencao, limite)

    contas[chave] = conta
    print(f"{NOMES_TIPO[type(conta)]} aberta com sucesso para {usuario.nome}.")
    print("Faça login para operar. Os dados são gravados em arquivo no logoff.")


def acao_login(contas):
    print("\n--- Login ---")
    agencia = ler_inteiro("Agência: ", minimo=0)
    rg = ler_texto("RG do titular: ")

    conta = localizar_conta(contas, agencia, rg)
    if conta is None:
        print("Conta não encontrada (nem em memória, nem em arquivo).")
        return

    if conta.efetuar_login(rg):
        executar_sessao(conta, contas)


# ==========================================
# AÇÕES DENTRO DA SESSÃO (conta logada)
# ==========================================

def acao_consultar(conta):
    print()
    conta.exibir_informacoes()
    if isinstance(conta, ContaEspecial):
        print(f"Limite: R$ {conta.limite:.2f}")
        print(f"Saldo disponível (com limite): R$ {conta.consultar_limite_disponivel():.2f}")


def acao_depositar(conta):
    valor = ler_decimal("Valor do depósito (R$): ")
    conta.depositar(valor)


def acao_sacar(conta):
    valor = ler_decimal("Valor do saque (R$): ")
    conta.sacar(valor)


def acao_transferir(conta, contas):
    agencia = ler_inteiro("Agência da conta de destino: ", minimo=0)
    rg = ler_texto("RG do titular da conta de destino: ")

    destino = localizar_conta(contas, agencia, rg)
    if destino is None:
        print("Conta de destino não encontrada.")
        return

    valor = ler_decimal("Valor da transferência (R$): ")
    conta.transferir(valor, destino)


def acao_rendimento(conta):
    if not isinstance(conta, ContaPoupanca):
        print("Rendimento só pode ser aplicado em Conta Poupança.")
        return
    conta.aplicar_rendimento()


def acao_cobrar_taxa(conta):
    if not isinstance(conta, ContaCorrente):
        print("A taxa de manutenção só existe em Conta Corrente e Conta Especial.")
        return
    conta.cobrar_taxa()


def acao_encerrar(conta):
    confirmacao = ler_opcao("Confirmar o encerramento? (s/n): ", ("s", "n"))
    if confirmacao == "s":
        conta.encerrar_conta()
    else:
        print("Encerramento cancelado.")


# ==========================================
# MENUS
# ==========================================

def exibir_menu_principal():
    print("\n========== SISTEMA BANCÁRIO ==========")
    print("1) Cadastrar usuário")
    print("2) Abrir conta")
    print("3) Efetuar login")
    print("0) Sair")


def exibir_menu_sessao(conta):
    print(
        f"\n===== {NOMES_TIPO[type(conta)].upper()} | Agência {conta.agencia} | "
        f"{conta.usuario.nome} ====="
    )
    print("1) Consultar saldo / informações")
    print("2) Exibir extrato")
    print("3) Depositar")
    print("4) Sacar")
    print("5) Transferir")
    print("6) Aplicar rendimento (poupança)")
    print("7) Cobrar taxa de manutenção (corrente/especial)")
    print("8) Encerrar conta")
    print("0) Efetuar logoff (salva os dados em arquivo)")


def executar_sessao(conta, contas):
    """Menu da conta logada. O logoff grava os dados em arquivo antes de sair."""
    acoes = {
        "1": lambda: acao_consultar(conta),
        "2": lambda: conta.exibir_extrato(),
        "3": lambda: acao_depositar(conta),
        "4": lambda: acao_sacar(conta),
        "5": lambda: acao_transferir(conta, contas),
        "6": lambda: acao_rendimento(conta),
        "7": lambda: acao_cobrar_taxa(conta),
        "8": lambda: acao_encerrar(conta),
    }

    try:
        while conta.logada:
            exibir_menu_sessao(conta)
            opcao = ler_opcao("Escolha uma opção: ", list(acoes) + ["0"])

            if opcao == "0":
                conta.efetuar_logoff()
            else:
                acoes[opcao]()
    finally:
        # Se o programa for interrompido (Ctrl+C), ainda assim salva e faz o logoff
        if conta.logada:
            conta.efetuar_logoff()


def main():
    usuarios = {}   # CPF -> Usuario (cadastrados nesta execução)
    contas = {}     # nome do arquivo -> Conta (abertas ou restauradas nesta execução)

    acoes = {
        "1": lambda: acao_cadastrar_usuario(usuarios),
        "2": lambda: acao_abrir_conta(usuarios, contas),
        "3": lambda: acao_login(contas),
    }

    try:
        while True:
            exibir_menu_principal()
            opcao = ler_opcao("Escolha uma opção: ", list(acoes) + ["0"])
            if opcao == "0":
                break
            acoes[opcao]()
    except (KeyboardInterrupt, EOFError):
        print()

    print("Encerrando o sistema. Até logo!")


if __name__ == "__main__":
    main()
