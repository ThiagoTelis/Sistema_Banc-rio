# Projeto Banco: login, logoff e persistência em arquivo

Este documento explica o que foi alterado no projeto para incluir as operações **efetuar_login**, **efetuar_logoff**, **salvar_em_arquivo** e **ler_de_arquivo**.

---

## 1. Visão geral do funcionamento

```
Abrir conta ──► Efetuar login ──► Operações ──► Efetuar logoff
                    │                              │
             ler_de_arquivo()              salvar_em_arquivo()
        (carrega os dados salvos)      (grava antes de encerrar a sessão)
```

1. **Login:** o usuário informa agência e RG. O sistema confere os dados e executa `ler_de_arquivo`, que carrega o que foi salvo antes.
2. **Sessão:** com a conta logada, o usuário consulta saldo, emite extrato, deposita, saca ou transfere. Cada operação entra no extrato.
3. **Logoff:** executa `salvar_em_arquivo` imediatamente antes de encerrar a sessão.

Na primeira vez que a conta é salva, o arquivo é **criado**. Nas vezes seguintes, ele é **atualizado**.

---

## 2. Arquivos alterados

| Arquivo | Mudança |
|---|---|
| `contas/conta.py` | Sessão (login/logoff), leitura e gravação em arquivo, restauração da conta e exigência de login nas operações. |
| `contas/conta_poupanca.py` | Exige login em `aplicar_rendimento`; grava e lê `taxa_rendimento`. |
| `contas/conta_corrente.py` | Exige login em `cobrar_taxa`; grava e lê `taxa_manutencao`. |
| `contas/conta_especial.py` | Exige login em saque, transferência e extrato; grava e lê `limite` e o histórico de uso do limite. |
| `modelos/usuario.py` | Novos métodos `para_dict` e `de_dict`. |
| `modelos/transacao.py` | Novos métodos `para_dict` e `de_dict`. |
| `main.py` | Dois menus (fora e dentro da sessão), busca de contas em memória ou arquivo e verificação de contas duplicadas. |

Os dois `__init__.py` não mudaram, e nenhum arquivo novo foi criado no código. A pasta `dados/`, que guarda os arquivos das contas, é criada automaticamente.

---

## 3. Detalhes por arquivo

### 3.1 `contas/conta.py`

**Novos atributos internos**

| Atributo | Função |
|---|---|
| `_logada` | Indica se há sessão aberta. Não é gravado em arquivo. |
| `_alterada` | Indica que há mudanças em memória ainda não salvas. É ligado em `_registrar` e desligado ao salvar ou ler. |

**Novos métodos de sessão**

| Método | O que faz |
|---|---|
| `efetuar_login(rg)` | Recusa se já houver sessão ou se agência e RG não conferem. Depois executa `ler_de_arquivo()` e marca a conta como logada. |
| `efetuar_logoff()` | Executa `salvar_em_arquivo()` e só então encerra a sessão. Se o salvamento falhar, o logoff é cancelado para não perder dados. |

**Novos métodos de persistência**

| Método | O que faz |
|---|---|
| `salvar_em_arquivo(silencioso=False)` | Grava a conta em JSON. Informa "criado" na primeira vez e "atualizado" nas seguintes. Escreve primeiro em um arquivo temporário e depois o substitui, para evitar arquivo corrompido. |
| `ler_de_arquivo()` | Carrega os dados salvos, se o arquivo existir. Se não existir, mantém os dados atuais. Se houver alterações não salvas em memória, mantém a memória. |
| `restaurar_de_arquivo(agencia, rg)` | Método estático que reconstrói a conta, no tipo correto (`Conta`, `ContaPoupanca`, `ContaCorrente` ou `ContaEspecial`), a partir do arquivo. É o que permite fazer login em uma nova execução do programa. |
| `montar_nome_arquivo(agencia, rg)` | Monta o nome `agência_RG.json`, mantendo só letras e números do RG. |
| `arquivo_existe(agencia, rg)` | Verifica se já existe arquivo para aquela conta. |
| `nome_arquivo()` / `caminho_arquivo()` | Nome e caminho completo do arquivo da conta. |
| `_para_dict()` / `_aplicar_dict()` | Convertem a conta para dicionário (gravação) e de dicionário (leitura). As subclasses acrescentam seus próprios campos. |

**Exigência de login**

Foram criados `_verificar_logada()` e `_pode_operar()` (login **e** conta ativa). Passam a exigir login: `depositar`, `sacar`, `transferir`, `encerrar_conta`, `exibir_informacoes` e `exibir_extrato`. O `consultar_saldo`, que só devolve um valor, não exige.

**Transferência**

Após creditar a conta de destino, `_transferir_para` grava o arquivo dela. O titular de destino não está logado e, sem esse passo, o crédito se perderia se ele nunca fizesse login.

### 3.2 `contas/conta_poupanca.py`, `conta_corrente.py` e `conta_especial.py`

- Passaram a usar `_pode_operar()` nas operações, no lugar da verificação antiga de conta ativa.
- Sobrescrevem `_para_dict` e `_aplicar_dict` para gravar e ler seus campos específicos:
  - **Poupança:** `taxa_rendimento`
  - **Corrente:** `taxa_manutencao`
  - **Especial:** `limite` e `historico_limite` (datas de início e fim de cada uso do limite)
- Na `ContaEspecial`, o gancho `_apos_movimentacao` também marca a conta como alterada quando o uso do limite começa ou termina.

### 3.3 `modelos/usuario.py` e `modelos/transacao.py`

Receberam `para_dict()` e o método de classe `de_dict()`. Eles convertem os objetos para JSON e de volta, transformando datas em texto no formato ISO e vice-versa.

### 3.4 `main.py`

- **Menu principal (sem login):** cadastrar usuário, abrir conta, efetuar login e sair.
- **Menu da sessão (com login):** consultar saldo, extrato, depositar, sacar, transferir, aplicar rendimento, cobrar taxa, encerrar conta e efetuar logoff.
- **`localizar_conta`:** procura a conta em memória e, se não achar, tenta restaurá-la do arquivo. É usada no login e para escolher a conta de destino de uma transferência.
- **Abertura de conta:** recusa agência e RG que já existam em memória ou em arquivo, para não sobrescrever dados salvos.
- **`executar_sessao`:** usa `try/finally`. Se o programa for interrompido com Ctrl+C, ainda assim salva os dados e faz o logoff.

---

## 4. Formato e nome do arquivo

- **Pasta:** `projeto_banco/dados/`
- **Nome:** agência + RG, por exemplo `10_123456.json`
- **Formato:** JSON, com os dados da conta, o titular e o extrato completo.

Exemplo resumido:

```json
{
  "tipo": "ContaEspecial",
  "agencia": 10,
  "usuario": { "rg": "123456", "cpf": "11111111111", "nome": "João", "data_nascimento": "2000-05-10T00:00:00" },
  "data_abertura": "2026-11-15T23:29:21.012896",
  "saldo": 330.0,
  "ativa": true,
  "data_encerramento": null,
  "extrato": [
    { "data": "2026-11-15T23:29:21.012896", "tipo": "ABERTURA", "valor": null, "saldo_apos": 500.0, "descricao": "Abertura de conta com saldo inicial de R$ 500.00" }
  ],
  "taxa_manutencao": 20.0,
  "limite": 1000.0,
  "historico_limite": [ { "inicio": "2026-11-15T23:29:21", "fim": "2026-11-15T23:29:28" } ]
}
```

---

## 5. Decisões de projeto

| Decisão | Motivo |
|---|---|
| Login e nome do arquivo usam o **RG** | O enunciado aceita RG ou CPF. Trocar para CPF exige mudar `montar_nome_arquivo` e o login. |
| Não há senha | O enunciado não pede. O RG funciona apenas como identificação. |
| Login e logoff não aparecem no extrato | Manter o extrato só com movimentações da conta e o salvamento imediatamente antes do logoff. |
| Arquivo de destino gravado na transferência | Evita perder o crédito recebido por quem não fez login. |
| Bloqueio de contas duplicadas | Evita que uma conta nova sobrescreva o arquivo de uma conta já salva. |

---

## 6. Como testar

1. Cadastre dois usuários e abra uma conta para cada, com agências diferentes.
2. Faça login na primeira conta, depois um depósito, um saque e uma transferência para a segunda. Confira o extrato.
3. Faça logoff: deve aparecer **"Arquivo criado: agência_RG.json"**.
4. Faça login na segunda conta: o extrato deve mostrar a transferência recebida. Faça logoff.
5. **Feche o programa e abra de novo.** Faça login na primeira conta sem cadastrar nada: os dados e o extrato devem voltar do arquivo.
6. Faça outra operação e novo logoff: deve aparecer **"Arquivo atualizado"**.

---

## 7. Limitações

- Os usuários cadastrados no menu ficam só em memória. Os dados deles ficam salvos dentro do arquivo de cada conta.
- Cada combinação de agência e RG identifica **uma** conta. Um mesmo titular com duas contas precisa usar agências diferentes.
- Apenas uma sessão pode estar aberta por vez, e não há controle de acesso simultâneo ao mesmo arquivo.
