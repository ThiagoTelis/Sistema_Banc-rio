from contas.conta import Conta


class ContaPoupanca(Conta):
    """Especialização de Conta com rendimentos periódicos."""

    def __init__(self, agencia, usuario, data_abertura, saldo, taxa_rendimento):
        super().__init__(agencia, usuario, data_abertura, saldo)
        self.taxa_rendimento = taxa_rendimento

    def aplicar_rendimento(self):
        if not self._pode_operar():
            return False

        rendimento = self.saldo * self.taxa_rendimento / 100
        self._creditar(
            rendimento,
            "RENDIMENTO",
            f"Rendimento de {self.taxa_rendimento}%"
        )

        print(f"Rendimento de R$ {rendimento:.2f} aplicado na conta.")
        return True

    def _para_dict(self):
        dados = super()._para_dict()
        dados["taxa_rendimento"] = self.taxa_rendimento
        return dados

    def _aplicar_dict(self, dados):
        super()._aplicar_dict(dados)
        self.taxa_rendimento = dados["taxa_rendimento"]
