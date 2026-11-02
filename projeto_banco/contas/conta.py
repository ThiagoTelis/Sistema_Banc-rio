from datetime import datetime

from modelos.transacao import FORMATO_DATA, Transacao


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

    def _verificar_ativa(self):
        if not self._ativa:
            print("Operação não permitida: conta encerrada.")
            return False
        return True

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

    # --- Operações da Conta ---

    def consultar_saldo(self):
        return self.saldo

    def depositar(self, valor):
        if not self._verificar_ativa() or not self._validar_valor_numerico(valor):
            return False

        if valor > 0:
            self._creditar(valor, "DEPOSITO", "Depósito em conta")
            print(f"Depósito de R$ {valor:.2f} realizado com sucesso.")
            return True

        print("O valor do depósito deve ser positivo.")
        return False

    def sacar(self, valor):
        if not self._verificar_ativa() or not self._validar_valor_numerico(valor):
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
        if not self._verificar_ativa() or not self._validar_valor_numerico(valor) or not self._validar_destino(conta_destino):
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
        print(f"Agência: {self.agencia}")
        print(f"Titular: {self.usuario.nome}")
        print(f"Saldo: R$ {self.saldo:.2f}")

    def exibir_extrato(self):
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
