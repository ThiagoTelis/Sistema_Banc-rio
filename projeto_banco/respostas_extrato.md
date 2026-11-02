# Questões sobre o `exibir_extrato`

## 1. Em que classe (da hierarquia) o método deve ser implementado?

Na classe base **`Conta`**.

**Justificativa**

- Todos os tipos de conta (`ContaPoupanca`, `ContaCorrente` e `ContaEspecial`) herdam de `Conta` e precisam exibir extrato, então a implementação comum fica no topo da hierarquia e é reaproveitada por herança, sem duplicar código.
- A `ContaEspecial` tem uma informação a mais (as datas de início e fim do uso do limite). Por isso ela **sobrescreve** `exibir_extrato`, chama `super().exibir_extrato()` para manter o comportamento padrão e acrescenta o histórico do cheque especial. Isso é polimorfismo: a mesma chamada, `conta.exibir_extrato()`, funciona em qualquer tipo de conta.

```python
class Conta:
    def exibir_extrato(self):
        ...  # cabeçalho, lista de transações, saldo atual e situação


class ContaEspecial(ContaCorrente):
    def exibir_extrato(self):
        super().exibir_extrato()
        ...  # histórico de uso do limite
```

---

## 2. O que deve mudar internamente na conta, para que seja possível exibir o extrato?

A conta precisa **guardar o histórico das operações**. Antes, ela só guardava o saldo atual e as operações apenas imprimiam mensagens, sem deixar rastro. As mudanças foram:

### a) Uma lista interna de transações

No construtor de `Conta` foi criada a lista `_extrato`, que armazena cada movimentação.

```python
self._extrato = []
```

### b) Uma classe para representar cada registro

A classe `Transacao` guarda os dados de cada evento: data, tipo, valor, saldo após a operação e descrição.

```python
class Transacao:
    def __init__(self, data, tipo, valor, saldo_apos, descricao):
        ...
```

### c) Um método interno para registrar

O método `_registrar` cria a `Transacao` e a adiciona à lista.

```python
def _registrar(self, tipo, valor, descricao, data=None):
    self._extrato.append(Transacao(data or datetime.now(), tipo, valor, self.saldo, descricao))
```

### d) Toda operação passa a registrar o que faz

Os métodos que alteram o saldo passaram a usar `_creditar` e `_debitar`, que atualizam o saldo **e** registram a transação ao mesmo tempo. Assim nenhuma operação deixa de aparecer no extrato:

| Operação | Tipo registrado |
|---|---|
| Depósito | `DEPOSITO` |
| Saque | `SAQUE` |
| Transferência (conta de origem) | `TRANSFERENCIA_ENVIADA` |
| Transferência (conta de destino) | `TRANSFERENCIA_RECEBIDA` |
| Rendimento da poupança | `RENDIMENTO` |
| Taxa de manutenção | `TAXA_MANUTENCAO` |

### e) Registro da criação e do encerramento

- **Criação:** o construtor registra a transação `ABERTURA` logo após inicializar a conta, usando a data de abertura.
- **Encerramento:** foi criado o método `encerrar_conta()`, que só permite encerrar com saldo zerado, marca a conta como inativa (`_ativa = False`), guarda a `_data_encerramento` e registra a transação `ENCERRAMENTO`. Depois disso, as demais operações são recusadas por `_verificar_ativa()`.

### f) Controle do limite na `ContaEspecial`

A `ContaEspecial` ganhou a lista `_historico_limite`, com os períodos em que o limite foi usado (`inicio` e `fim`). Um gancho chamado `_apos_movimentacao()` é executado após cada movimentação:

- Se o saldo ficou **negativo** e o limite não estava em uso, abre um novo período com a data de início.
- Se o saldo voltou a ser **zero ou positivo** e o limite estava em uso, fecha o período com a data de fim.

### g) Encapsulamento

O extrato é privado (`_extrato`) e é exposto por uma propriedade somente leitura que devolve uma **cópia** da lista. Assim, código externo consegue consultar o histórico, mas não adulterá-lo.

```python
@property
def extrato(self):
    return list(self._extrato)
```
