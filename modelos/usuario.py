from datetime import datetime


class Usuario:
    """Representa um cliente do banco."""

    def __init__(self, rg=0, cpf=0, nome="", data_nascimento=None):
        self.rg = rg
        self.cpf = cpf
        self.nome = nome
        self.data_nascimento = data_nascimento

    @property
    def rg(self):
        return self._rg

    @rg.setter
    def rg(self, rg):
        self._rg = rg

    @property
    def cpf(self):
        return self._cpf

    @cpf.setter
    def cpf(self, cpf):
        self._cpf = cpf

    @property
    def nome(self):
        return self._nome

    @nome.setter
    def nome(self, nome):
        self._nome = nome

    @property
    def data_nascimento(self):
        return self._data_nascimento

    @data_nascimento.setter
    def data_nascimento(self, data_nascimento):
        self._data_nascimento = data_nascimento

    # --- Persistência ---

    def para_dict(self):
        return {
            "rg": self.rg,
            "cpf": self.cpf,
            "nome": self.nome,
            "data_nascimento": (
                self.data_nascimento.isoformat() if self.data_nascimento else None
            ),
        }

    @classmethod
    def de_dict(cls, dados):
        nascimento = dados["data_nascimento"]
        return cls(
            dados["rg"],
            dados["cpf"],
            dados["nome"],
            datetime.fromisoformat(nascimento) if nascimento else None,
        )
