import json
import os
from datetime import datetime

from modelos.transacao import FORMATO_DATA, Transacao
from modelos.usuario import Usuario

# Pasta onde os arquivos das contas são gravados: projeto_banco/dados
PASTA_DADOS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dados"
)


class Conta:
    """Classe base que define o comportamento padrão de uma conta bancária."""

    def __init__(self, agencia, usuario, data_abertura, saldo):
        self.agencia = agencia
        self.usuario = usuario
        self.data_abertura = data_abertura
        self.saldo = saldo

        self._extrato = []
        self._ativa = True
        self._data_encerramento = None
        self._logada = False       # sessão: não é gravada em arquivo
        self._alterada = False     # há mudanças ainda não salvas em arquivo

        # Registro de abertura
        self._registrar(
            "ABERTURA",
            None,
            f"Abertura de conta com saldo inicial de R$ {saldo:.2f}",
            data=data_abertura
        )

    @property
    def agencia(self):
        return self._agencia

    @agencia.setter
    def agencia(self, agencia):
        self._agencia = agencia

    @property
    def usuario(self):
        return self._usuario

    @usuario.setter
    def usuario(self, usuario):
        self._usuario = usuario

    @property
    def data_abertura(self):
        return self._data_abertura

    @data_abertura.setter
    def data_abertura(self, data_abertura):
        self._data_abertura = data_abertura

    @property
    def saldo(self):
        return self._saldo

    @saldo.setter
    def saldo(self, saldo):
        self._saldo = saldo

    @property
    def ativa(self):
        return self._ativa

    @property
    def logada(self):
        return self._logada

    @property
    def data_encerramento(self):
        return self._data_encerramento

    @property
    def extrato(self):
        return list(self._extrato)

    # --- Métodos Internos de Suporte ---

    def _registrar(self, tipo, valor, descricao, data=None):
        self._extrato.append(
            Transacao(
                data or datetime.now(),
                tipo,
                valor,
                self.saldo,
                descricao
            )
        )
        self._alterada = True

    def _verificar_ativa(self):
        if not self._ativa:
            print("Operação não permitida: conta encerrada.")
            return False
        return True

    def _verificar_logada(self):
        if not self._logada:
            print("Operação não permitida: faça login na conta primeiro.")
            return False
        return True

    def _pode_operar(self):
        """Operações que movimentam a conta exigem login e conta ativa."""
        return self._verificar_logada() and self._verificar_ativa()

    def _validar_valor_numerico(self, valor):
        if not isinstance(valor, (int, float)):
            print("Operação cancelada: o valor informado deve ser numérico.")
            return False
        return True

    def _creditar(self, valor, tipo, descricao):
        self.saldo += valor
        self._registrar(tipo, valor, descricao)
        self._apos_movimentacao()

    def _debitar(self, valor, tipo, descricao):
        self.saldo -= valor
        self._registrar(tipo, -valor, descricao)
        self._apos_movimentacao()

    def _apos_movimentacao(self):
        """Gancho para especialização nas subclasses."""
        pass

    def _validar_destino(self, conta_destino):
        if conta_destino is self:
            print("Não é possível transferir para a própria conta.")
            return False
        if not conta_destino.ativa:
            print("Conta de destino encerrada.")
            return False
        return True

    def _transferir_para(self, valor, conta_destino):
        self._debitar(
            valor,
            "TRANSFERENCIA_ENVIADA",
            f"Transferência para {conta_destino.usuario.nome} (ag. {conta_destino.agencia})"
        )
        conta_destino._creditar(
            valor,
            "TRANSFERENCIA_RECEBIDA",
            f"Transferência de {self.usuario.nome} (ag. {self.agencia})"
        )
        # O titular de destino não está logado: grava o crédito para não perdê-lo
        conta_destino.salvar_em_arquivo(silencioso=True)

    # --- Operações da Conta ---

    def consultar_saldo(self):
        return self.saldo

    def depositar(self, valor):
        if not self._pode_operar() or not self._validar_valor_numerico(valor):
            return False

        if valor > 0:
            self._creditar(valor, "DEPOSITO", "Depósito em conta")
            print(f"Depósito de R$ {valor:.2f} realizado com sucesso.")
            return True

        print("O valor do depósito deve ser positivo.")
        return False

    def sacar(self, valor):
        if not self._pode_operar() or not self._validar_valor_numerico(valor):
            return False

        if valor <= 0:
            print("O valor do saque deve ser positivo.")
        elif valor <= self.saldo:
            self._debitar(valor, "SAQUE", "Saque em conta")
            print(f"Saque de R$ {valor:.2f} realizado com sucesso.")
            return True
        else:
            print("Saldo insuficiente.")
        return False

    def transferir(self, valor, conta_destino):
        if (
            not self._pode_operar()
            or not self._validar_valor_numerico(valor)
            or not self._validar_destino(conta_destino)
        ):
            return False

        if valor <= 0:
            print("O valor da transferência deve ser positivo.")
        elif valor <= self.saldo:
            self._transferir_para(valor, conta_destino)
            print(f"Transferência de R$ {valor:.2f} realizada com sucesso.")
            return True
        else:
            print("Saldo insuficiente.")
        return False

    def encerrar_conta(self):
        if not self._verificar_logada():
            return False

        if not self._ativa:
            print("A conta já está encerrada.")
            return False

        if round(self.saldo, 2) != 0:
            print(
                "Para encerrar a conta o saldo deve estar zerado "
                f"(saldo atual: R$ {self.saldo:.2f})."
            )
            return False

        self._ativa = False
        self._data_encerramento = datetime.now()
        self._registrar(
            "ENCERRAMENTO",
            None,
            "Encerramento de conta",
            data=self._data_encerramento
        )
        print("Conta encerrada com sucesso.")
        return True

    def exibir_informacoes(self):
        if not self._verificar_logada():
            return
        print(f"Agência: {self.agencia}")
        print(f"Titular: {self.usuario.nome}")
        print(f"Saldo: R$ {self.saldo:.2f}")

    def exibir_extrato(self):
        if not self._verificar_logada():
            return

        print(
            f"\n----- EXTRATO | Agência {self.agencia} | "
            f"Titular: {self.usuario.nome} -----"
        )
        print(
            f"{'Data/Hora':<19} | {'Tipo':<22} | "
            f"{'Valor':>12} | {'Saldo':>12} | Descrição"
        )

        for transacao in self._extrato:
            print(transacao)

        print(f"Saldo atual: R$ {self.saldo:.2f}")

        situacao = "Ativa" if self._ativa else (
            f"Encerrada em {self._data_encerramento.strftime(FORMATO_DATA)}"
        )
        print(f"Situação: {situacao}")

    # --- Sessão (login / logoff) ---

    def efetuar_login(self, rg):
        """Conecta com a conta: confere o RG e carrega os dados salvos em arquivo."""
        if self._logada:
            print("Já existe uma sessão aberta nesta conta.")
            return False

        if Conta.montar_nome_arquivo(self.agencia, rg) != self.nome_arquivo():
            print("Login negado: agência ou RG não conferem.")
            return False

        self.ler_de_arquivo()
        self._logada = True
        print(f"Login efetuado. Bem-vindo(a), {self.usuario.nome}!")
        return True

    def efetuar_logoff(self):
        """Salva os dados em arquivo e encerra a sessão."""
        if not self._logada:
            print("Nenhum login ativo nesta conta.")
            return False

        # salvar_em_arquivo vem imediatamente antes do logoff
        if not self.salvar_em_arquivo():
            print("Logoff cancelado: não foi possível salvar os dados.")
            return False

        self._logada = False
        print("Logoff efetuado.")
        return True

    # --- Persistência em arquivo ---

    @staticmethod
    def montar_nome_arquivo(agencia, rg):
        """Nome do arquivo = número da agência + RG do titular (só letras e números)."""
        rg_limpo = "".join(c for c in str(rg) if c.isalnum()).upper()
        return f"{agencia}_{rg_limpo}.json"

    @staticmethod
    def arquivo_existe(agencia, rg):
        caminho = os.path.join(PASTA_DADOS, Conta.montar_nome_arquivo(agencia, rg))
        return os.path.exists(caminho)

    def nome_arquivo(self):
        return Conta.montar_nome_arquivo(self.agencia, self.usuario.rg)

    def caminho_arquivo(self):
        return os.path.join(PASTA_DADOS, self.nome_arquivo())

    def salvar_em_arquivo(self, silencioso=False):
        """Grava a conta (dados + extrato). Na primeira vez, cria o arquivo."""
        caminho = self.caminho_arquivo()
        primeira_vez = not os.path.exists(caminho)

        try:
            os.makedirs(PASTA_DADOS, exist_ok=True)
            temporario = caminho + ".tmp"
            with open(temporario, "w", encoding="utf-8") as arquivo:
                json.dump(self._para_dict(), arquivo, ensure_ascii=False, indent=2)
            os.replace(temporario, caminho)
        except OSError as erro:
            print(f"Erro ao salvar o arquivo: {erro}")
            return False

        self._alterada = False

        if not silencioso:
            acao = "criado" if primeira_vez else "atualizado"
            print(f"Arquivo {acao}: {self.nome_arquivo()}")
        return True

    def ler_de_arquivo(self):
        """Carrega os dados salvos da conta, se o arquivo existir."""
        caminho = self.caminho_arquivo()

        if not os.path.exists(caminho):
            print("Nenhum arquivo salvo para esta conta; mantendo os dados atuais.")
            return False

        if self._alterada:
            print("Há alterações em memória ainda não salvas; dados em memória mantidos.")
            return False

        try:
            with open(caminho, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
            self._aplicar_dict(dados)
        except (OSError, ValueError, KeyError, TypeError) as erro:
            print(f"Erro ao ler o arquivo: {erro}")
            return False

        print(f"Dados da conta carregados do arquivo {self.nome_arquivo()}.")
        return True

    @staticmethod
    def restaurar_de_arquivo(agencia, rg):
        """Reconstrói uma conta (do tipo correto) a partir do arquivo salvo.

        Devolve None se o arquivo não existir ou estiver inválido.
        """
        # Importações locais evitam importação circular com as subclasses
        from contas.conta_poupanca import ContaPoupanca
        from contas.conta_corrente import ContaCorrente
        from contas.conta_especial import ContaEspecial

        classes = {
            classe.__name__: classe
            for classe in (Conta, ContaPoupanca, ContaCorrente, ContaEspecial)
        }
        caminho = os.path.join(PASTA_DADOS, Conta.montar_nome_arquivo(agencia, rg))

        if not os.path.exists(caminho):
            return None

        try:
            with open(caminho, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)

            classe = classes[dados["tipo"]]
            conta = classe.__new__(classe)   # sem __init__: o estado vem do arquivo
            conta._logada = False
            conta._aplicar_dict(dados)
        except (OSError, ValueError, KeyError, TypeError) as erro:
            print(f"Erro ao restaurar a conta do arquivo: {erro}")
            return None

        return conta

    def _para_dict(self):
        return {
            "tipo": type(self).__name__,
            "agencia": self.agencia,
            "usuario": self.usuario.para_dict(),
            "data_abertura": self.data_abertura.isoformat(),
            "saldo": self.saldo,
            "ativa": self._ativa,
            "data_encerramento": (
                self._data_encerramento.isoformat() if self._data_encerramento else None
            ),
            "extrato": [transacao.para_dict() for transacao in self._extrato],
        }

    def _aplicar_dict(self, dados):
        self.agencia = dados["agencia"]
        self.usuario = Usuario.de_dict(dados["usuario"])
        self.data_abertura = datetime.fromisoformat(dados["data_abertura"])
        self.saldo = dados["saldo"]
        self._ativa = dados["ativa"]
        encerramento = dados["data_encerramento"]
        self._data_encerramento = (
            datetime.fromisoformat(encerramento) if encerramento else None
        )
        self._extrato = [Transacao.de_dict(t) for t in dados["extrato"]]
        self._alterada = False
