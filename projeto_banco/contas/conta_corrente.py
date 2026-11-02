from contas.conta import Conta


class ContaCorrente(Conta):
    """Especialização de Conta com cobrança de taxa de manutenção."""

    def __init__(self, agencia, usuario, data_abertura, saldo, taxa_manutencao):
        super().__init__(agencia, usuario, data_abertura, saldo)
        self.taxa_manutencao = taxa_manutencao

    def cobrar_taxa(self):
        if not self._verificar_ativa():
            return False

        if self.saldo >= self.taxa_manutencao:
            self._debitar(
                self.taxa_manutencao,
                "TAXA_MANUTENCAO",
                "Taxa de manutenção"
            )
            print(f"Taxa de manutenção de R$ {self.taxa_manutencao:.2f} cobrada.")
            return True

        print("Saldo insuficiente para cobrar a taxa.")
        return False
