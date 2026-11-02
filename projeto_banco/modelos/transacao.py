FORMATO_DATA = "%d/%m/%Y %H:%M:%S"


class Transacao:
    """Registra individualmente cada evento ou movimentação financeira."""

    def __init__(self, data, tipo, valor, saldo_apos, descricao):
        self.data = data
        self.tipo = tipo
        self.valor = valor          # positivo = entrada, negativo = saída, None = evento
        self.saldo_apos = saldo_apos
        self.descricao = descricao

    def __str__(self):
        valor_str = "-" if self.valor is None else f"{self.valor:+.2f}"
        return (
            f"{self.data.strftime(FORMATO_DATA)} | "
            f"{self.tipo:<22} | "
            f"{valor_str:>12} | "
            f"{self.saldo_apos:>12.2f} | "
            f"{self.descricao}"
        )
