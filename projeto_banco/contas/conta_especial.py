from datetime import datetime

from modelos.transacao import FORMATO_DATA
from contas.conta_corrente import ContaCorrente


class ContaEspecial(ContaCorrente):
    """Subclasse de ContaCorrente que oferece limite de cheque especial."""

    def __init__(self, agencia, usuario, data_abertura, saldo, taxa_manutencao, limite):
        super().__init__(agencia, usuario, data_abertura, saldo, taxa_manutencao)
        self.limite = limite
        self._historico_limite = []

    @property
    def limite_em_uso(self):
        return bool(
            self._historico_limite and self._historico_limite[-1]["fim"] is None
        )

    @property
    def data_inicio_uso_limite(self):
        if self._historico_limite:
            return self._historico_limite[-1]["inicio"]
        return None

    @property
    def data_fim_uso_limite(self):
        if self._historico_limite:
            return self._historico_limite[-1]["fim"]
        return None

    @property
    def historico_limite(self):
        return [dict(periodo) for periodo in self._historico_limite]

    def _apos_movimentacao(self):
        agora = datetime.now()
        saldo_negativo = self.saldo < 0

        if saldo_negativo and not self.limite_em_uso:
            self._historico_limite.append({"inicio": agora, "fim": None})
        elif not saldo_negativo and self.limite_em_uso:
            self._historico_limite[-1]["fim"] = agora

    def consultar_saldo(self):
        return self.saldo + self.limite

    def sacar(self, valor):
        if not self._verificar_ativa() or not self._validar_valor_numerico(valor):
            return False

        if valor <= 0:
            print("O valor do saque deve ser positivo.")
        elif valor <= self.saldo + self.limite:
            self._debitar(valor, "SAQUE", "Saque em conta")
            print("Saque realizado utilizando o limite quando necessário.")
            return True
        else:
            print("Valor excede o limite disponível.")

        return False

    def transferir(self, valor, conta_destino):
        if not self._verificar_ativa() or not self._validar_valor_numerico(valor) or not self._validar_destino(conta_destino):
            return False

        if valor <= 0:
            print("O valor da transferência deve ser positivo.")
        elif valor <= self.saldo + self.limite:
            self._transferir_para(valor, conta_destino)
            print("Transferência realizada utilizando o limite quando necessário.")
            return True
        else:
            print("Valor excede o limite disponível.")

        return False

    def consultar_limite_disponivel(self):
        return self.saldo + self.limite

    def exibir_extrato(self):
        super().exibir_extrato()
        print("\n--- Histórico de Uso do Limite (Cheque Especial) ---")

        if not self._historico_limite:
            print("  Limite nunca utilizado.")
            return

        for i, periodo in enumerate(self._historico_limite, start=1):
            inicio = periodo["inicio"].strftime(FORMATO_DATA)
            fim = (
                periodo["fim"].strftime(FORMATO_DATA)
                if periodo["fim"]
                else "Em uso"
            )
            print(f"  {i}. Início: {inicio} | Fim: {fim}")
