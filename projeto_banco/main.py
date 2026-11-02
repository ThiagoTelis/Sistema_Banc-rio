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
# FUNÇÕES DE SELEÇÃO
# ==========================================

def escolher_usuario(usuarios):
    lista = list(usuarios.values())

    print("\nUsuários cadastrados:")
    for i, usuario in enumerate(lista, start=1):
        print(f"  {i}) {usuario.nome} (CPF {usuario.cpf})")

    indice = ler_inteiro("Escolha o usuário (número): ", 1, len(lista))
    return lista[indice - 1]


def escolher_conta(contas, titulo="Escolha a conta"):
    if not contas:
        print("Nenhuma conta aberta ainda. Abra uma conta primeiro.")
        return None

    print(f"\n{titulo}:")
    for i, conta in enumerate(contas, start=1):
        situacao = "" if conta.ativa else " [ENCERRADA]"
        print(
            f"  {i}) Agência {conta.agencia} | {NOMES_TIPO[type(conta)]} | "
            f"{conta.usuario.nome} | Saldo R$ {conta.saldo:.2f}{situacao}"
        )

    indice = ler_inteiro("Número da conta: ", 1, len(contas))
    return contas[indice - 1]


# ==========================================
# AÇÕES DO MENU
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

    contas.append(conta)
    print(f"{NOMES_TIPO[type(conta)]} aberta com sucesso para {usuario.nome}.")


def acao_depositar(contas):
    conta = escolher_conta(contas, "Conta para depósito")
    if conta:
        valor = ler_decimal("Valor do depósito (R$): ")
        conta.depositar(valor)


def acao_sacar(contas):
    conta = escolher_conta(contas, "Conta para saque")
    if conta:
        valor = ler_decimal("Valor do saque (R$): ")
        conta.sacar(valor)


def acao_transferir(contas):
    origem = escolher_conta(contas, "Conta de ORIGEM")
    if not origem:
        return
    destino = escolher_conta(contas, "Conta de DESTINO")
    if not destino:
        return
    valor = ler_decimal("Valor da transferência (R$): ")
    origem.transferir(valor, destino)


def acao_consultar(contas):
    conta = escolher_conta(contas, "Conta para consulta")
    if not conta:
        return

    print()
    conta.exibir_informacoes()
    if isinstance(conta, ContaEspecial):
        print(f"Limite: R$ {conta.limite:.2f}")
        print(f"Saldo disponível (com limite): R$ {conta.consultar_limite_disponivel():.2f}")


def acao_extrato(contas):
    conta = escolher_conta(contas, "Conta para extrato")
    if conta:
        conta.exibir_extrato()


def acao_rendimento(contas):
    conta = escolher_conta(contas, "Conta poupança")
    if not conta:
        return
    if not isinstance(conta, ContaPoupanca):
        print("Rendimento só pode ser aplicado em Conta Poupança.")
        return
    conta.aplicar_rendimento()


def acao_cobrar_taxa(contas):
    conta = escolher_conta(contas, "Conta corrente/especial")
    if not conta:
        return
    if not isinstance(conta, ContaCorrente):
        print("A taxa de manutenção só existe em Conta Corrente e Conta Especial.")
        return
    conta.cobrar_taxa()


def acao_encerrar(contas):
    conta = escolher_conta(contas, "Conta a encerrar")
    if not conta:
        return
    confirmacao = ler_opcao("Confirmar o encerramento? (s/n): ", ("s", "n"))
    if confirmacao == "s":
        conta.encerrar_conta()
    else:
        print("Encerramento cancelado.")


# ==========================================
# MENU PRINCIPAL
# ==========================================

def exibir_menu():
    print("\n========== SISTEMA BANCÁRIO ==========")
    print(" 1) Cadastrar usuário")
    print(" 2) Abrir conta")
    print(" 3) Depositar")
    print(" 4) Sacar")
    print(" 5) Transferir")
    print(" 6) Consultar saldo / informações")
    print(" 7) Exibir extrato")
    print(" 8) Aplicar rendimento (poupança)")
    print(" 9) Cobrar taxa de manutenção (corrente/especial)")
    print("10) Encerrar conta")
    print(" 0) Sair")


def main():
    usuarios = {}
    contas = []

    acoes = {
        "1": lambda: acao_cadastrar_usuario(usuarios),
        "2": lambda: acao_abrir_conta(usuarios, contas),
        "3": lambda: acao_depositar(contas),
        "4": lambda: acao_sacar(contas),
        "5": lambda: acao_transferir(contas),
        "6": lambda: acao_consultar(contas),
        "7": lambda: acao_extrato(contas),
        "8": lambda: acao_rendimento(contas),
        "9": lambda: acao_cobrar_taxa(contas),
        "10": lambda: acao_encerrar(contas),
    }

    try:
        while True:
            exibir_menu()
            opcao = ler_opcao("Escolha uma opção: ", list(acoes) + ["0"])
            if opcao == "0":
                break
            acoes[opcao]()
    except (KeyboardInterrupt, EOFError):
        print()

    print("Encerrando o sistema. Até logo!")


if __name__ == "__main__":
    main()
