import os
import sys
from abc import ABC, abstractmethod
from datetime import datetime

from brazilcep import exceptions, get_address_from_cep
from colorama import Fore, Style, init

from decoradores import emitir_mensagem
from menu import exibir_menu

init(autoreset=True)


class Cliente:
    """
    #### Representa um cliente bancário, armazenando suas informações pessoais e contas associadas.

    A classe permite que o cliente realize transações bancárias e gerencie suas contas cadastradas.
    """

    def __init__(self, endereco, numero, cep):
        """
        #### Inicializa um cliente bancário com endereço, número e CEP.

        Parâmetros:
        ---
            endereco (str): Endereço residencial do cliente.
            numero (str): Número da residência.
            cep (str): Código postal (CEP) do cliente.

        Retorna:
        ---
            None
        """
        self.endereco = endereco
        self.numero = numero
        self.cep = cep
        self.contas = []

    def realizar_transacao(self, conta, transacao_cls, valor):
        """
        #### Registra uma transação bancária na conta do cliente.

        O método utiliza a classe de transação informada para registrar um depósito, saque
        ou outra movimentação financeira na conta especificada.

        Parâmetros:
        ---
            conta (Conta): Conta bancária onde a transação será aplicada.
            transacao_cls (class): Classe da transação a ser registrada (exemplo: Deposito, Saque).
            valor (float): Valor da transação a ser processada.

        Retorna:
        ---
            None

        Exemplo:
        ---
            >>> cliente.realizar_transacao(conta, Deposito, 200)
            Depósito de R$ 200 registrado com sucesso.
        """
        transacao_cls.registrar(conta, valor)

    def adicionar_conta(self, conta):
        """
        #### Associa uma conta bancária ao cliente.

        Este método permite que um cliente possua múltiplas contas bancárias, armazenando
        todas elas em uma lista de contas associadas ao cliente.

        Parâmetros:
        ---
            conta (Conta): Conta bancária a ser vinculada ao cliente.

        Retorna:
        ---
            None

        Exemplo:
        ---
            >>> cliente.adicionar_conta(conta_corrente)
            Conta adicionada com sucesso.
        """
        self.contas.append(conta)


class PessoaFisica(Cliente):
    """
    #### Solicita ao usuário o tipo de conta a ser criada.

    Este método exibe um menu para o usuário selecionar entre conta corrente e conta poupança.

    Retorna:
    ---
        str: O tipo de conta selecionado, "corrente" ou "poupanca".

    Exemplo:
    ---
        >>> tipo_conta = _selecionar_tipo_conta()
        >>> print(tipo_conta)
        "corrente"
    """

    def __init__(self, nome, data_nascimento, cpf, endereco, numero, cep):
        """
        #### Inicializa um cliente Pessoa Física com suas informações pessoais e bancárias.

        Parâmetros:
        ---
            nome (str): Nome completo do cliente.
            data_nascimento (str): Data de nascimento do cliente no formato 'DD/MM/AAAA'.
            cpf (str): Número do CPF do cliente.
            endereco (str): Endereço residencial do cliente.
            numero (str): Número da residência.
            cep (str): Código postal (CEP) do cliente.

        Retorna:
        ---
            None
        """
        super().__init__(endereco, numero, cep)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf


class PessoaJuridica(Cliente):
    """
    #### Representa um cliente do tipo Pessoa Jurídica.

    A classe `PessoaJuridica` herda de `Cliente` e armazena informações empresariais como razão social e CNPJ, além dos dados herdados da classe base.

    Atributos:
    ---
        razao_social (str): Nome da empresa registrado legalmente.
        cnpj (str): Número do CNPJ da empresa.

    Métodos:
    ---
        Nenhum método adicional além dos herdados da classe `Cliente`.
    """

    def __init__(self, razao_social, cnpj, endereco, numero, cep):
        """
        #### Inicializa um cliente Pessoa Jurídica com suas informações empresariais e bancárias.

        Parâmetros:
        ---
            razao_social (str): Nome da empresa registrado legalmente.
            cnpj (str): Número do CNPJ da empresa.
            endereco (str): Endereço da sede da empresa.
            numero (str): Número do endereço.
            cep (str): Código postal (CEP) da empresa.

        Retorna:
        ---
            None
        """
        super().__init__(endereco, numero, cep)
        self.razao_social = razao_social
        self.cnpj = cnpj


class ContaBancaria:
    """
    #### Representa uma conta bancária genérica.

    Essa classe serve como base para diferentes tipos de contas bancárias e
    fornece funcionalidades comuns, como saques, depósitos e geração de extrato.
    """
    contador_contas = {"corrente": [1234, 0], "poupanca": [4321, 0]}

    def __init__(self, cliente):
        """
        #### Inicializa uma conta bancária associada a um cliente.

        Parâmetros:
        ---
            cliente (Cliente): O cliente ao qual a conta está vinculada.

        Retorna:
        ---
            None
        """
        self._agencia = '0001'
        self._cliente = cliente
        self._numero_conta = ''
        self._saldo = 0
        self._extrato = ImprimirExtrato()

    @classmethod
    def criar_nova_conta(cls, cliente, tipo_conta: str):
        """
        #### Cria uma nova conta bancária associada a um cliente.

        Este método cria uma conta do tipo especificado (corrente ou poupança) e a associa ao cliente fornecido.
        O número da conta é gerado dinamicamente com base no tipo de conta.

        Parâmetros:
        ---
            cliente (Cliente): O cliente ao qual a conta será vinculada.
            tipo_conta (str): O tipo de conta a ser criada. Deve ser "corrente" ou "poupanca".

        Retorna:
        ---
            ContaBancaria: Uma instância de ContaCorrente ou ContaPoupanca, dependendo do tipo especificado.

        Lança:
        ---
            ValueError: Se o tipo de conta fornecido não for válido.

        Exemplo:
        ---
            >>> cliente = PessoaFisica(nome="João", data_nascimento="01/01/1990", cpf="12345678900", endereco="Rua A", numero="10", cep="12345-678")
            >>> conta = ContaBancaria.criar_nova_conta(cliente, "corrente")
            >>> print(conta.numero_conta)
            1234-0
        """
        if tipo_conta not in cls.contador_contas:
            raise ValueError(" Tipo de conta inválido.")

        numero_conta = cls.gerar_numero_conta(tipo_conta)

        if tipo_conta == "corrente":
            conta = ContaCorrente(cliente=cliente)
        else:
            conta = ContaPoupanca(cliente=cliente)

        conta._numero_conta = numero_conta
        return conta
        # return (cliente, numero_conta)

    @property
    def saldo(self):
        return self._saldo

    @saldo.setter
    def saldo(self, valor):
        """
        #### Define o saldo da conta bancária.

        Este método permite atualizar o saldo da conta. Deve ser usado com cuidado para evitar inconsistências.

        Parâmetros:
        ---
            valor (float): O novo saldo a ser definido.

        Lança:
        ---
            ValueError: Se o valor fornecido for inválido (opcional, caso queira adicionar validação futura).

        Retorna:
        ---
            float: O saldo atual da conta.
        """
        self._saldo = valor

    @property
    def agencia(self):
        """
        #### Obtém o número da agência da conta bancária.

        Retorna:
        ---
            str: O número da agência associada à conta.
        """
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def extrato(self):
        return self._extrato

    @classmethod
    def gerar_numero_conta(cls, tipo_conta):
        """
        #### Gera um número de conta único com base no tipo de conta.

        Este método utiliza um contador interno para criar um número de conta formatado como "XXXX-YYYY",
        onde XXXX é o prefixo e YYYY é o sufixo. O sufixo é incrementado a cada nova conta criada do mesmo tipo.

        Parâmetros:
        ---
            tipo_conta (str): O tipo de conta para o qual o número está sendo gerado. Pode ser "corrente" ou "poupanca".

        Retorna:
        ---
            str: O número da conta formatado como "XXXX-YYYY".

        Exemplo:
        ---
            >>> numero_conta = ContaBancaria.gerar_numero_conta("corrente")
            >>> print(numero_conta)
            1234-0
        """
        prefixo, sufixo = cls.contador_contas[tipo_conta]
        numero_conta = f"{prefixo}-{sufixo}"
        cls.contador_contas[tipo_conta][1] += 1
        return numero_conta

    @property
    def numero_conta(self):
        return self._numero_conta

    def sacar(self, *, valor: float):
        """
        #### Realiza um saque na conta bancária.

        Este método permite retirar um valor do saldo da conta, desde que o saldo seja suficiente e o valor seja válido.

        Parâmetros:
        ---
            valor (float): O valor a ser sacado.

        Retorna:
        ---
            bool: `True` se o saque for realizado com sucesso, `False` caso contrário.

        Exibe:
        ---
            Mensagens de sucesso ou erro, dependendo do resultado da operação.

        Exemplo:
        ---
            >>> conta.sacar(valor=100.0)
            Sucesso: Saque de R$100.00 realizado! Saldo atual: R$900.00.
        """
        if valor > self.saldo:
            print(emitir_mensagem(
                ('Alerta', f'Saldo insuficiente. Saldo atual: R$ {self.saldo:.2f}.')))
        elif valor > 0:
            # Realiza o saque
            self.saldo -= valor
            print(emitir_mensagem(
                ('Sucesso', f'Saque de R${valor} realizado! Saldo atual: R$ {self.saldo:.2f}.')))
            return True
        else:
            print(emitir_mensagem(
                ('Erro', 'Operação falhou! O valor informado é inválido.')))
        return False

    def depositar(self, valor: float):
        """
        #### Realiza um depósito na conta bancária.

        Este método permite adicionar um valor ao saldo da conta, desde que o valor seja válido.

        Parâmetros:
        ---
            valor (float): O valor a ser depositado.

        Retorna:
        ---
            bool: `True` se o depósito for realizado com sucesso, `False` caso contrário.

        Exibe:
        ---
            Mensagens de sucesso ou erro, dependendo do resultado da operação.

        Exemplo:
        ---
            >>> conta.depositar(valor=200.0)
            Sucesso: Depósito de R$200.00 realizado! Saldo atual: R$1200.00.
        """
        if valor <= 0:
            print(emitir_mensagem(
                ('Erro', 'Operação falhou! O valor informado é inválido.')))
        else:
            # Realiza o depósito
            self.saldo += valor
            print(emitir_mensagem(
                ('Sucesso', f'Depósito de R${valor} realizado! Saldo atual: R$ {self.saldo:.2f}.')))
            return True
        return False


class ContaCorrente(ContaBancaria):
    """
    #### Representa uma conta corrente.

    A classe `ContaCorrente` herda de `ContaBancaria` e adiciona funcionalidades específicas, como limite de saque e número máximo de saques diários.

    Atributos:
    ---
        cliente (Cliente): O cliente associado à conta.
        limite (float): O limite máximo permitido para saques.
        limite_saque (int): O número máximo de saques permitidos por dia.

    Métodos:
    ---
        sacar(valor: float): Realiza um saque na conta, respeitando o limite e o número máximo de saques diários.
        __str__(): Retorna uma representação textual da conta corrente.
    """

    def __init__(self, cliente, limite=500, limite_saque=3):
        """
        #### Inicializa uma conta corrente.

        Parâmetros:
        ---
            cliente (Cliente): O cliente associado à conta.
            limite (float, opcional): O limite máximo permitido para saques. Padrão é R$ 500,00.
            limite_saque (int, opcional): O número máximo de saques permitidos por dia. Padrão é 3.

        Retorna:
        ---
            None
        """
        super().__init__(cliente)
        self.limite = limite
        self.limite_saque = limite_saque

    def sacar(self, *, valor):
        """
        #### Realiza um saque na conta corrente.

        Este método verifica se o saque respeita o limite máximo permitido e o número máximo de saques diários.
        Caso as condições sejam atendidas, o saque é realizado.

        Parâmetros:
        ---
            valor (float): O valor a ser sacado.

        Retorna:
        ---
            bool: `True` se o saque for realizado com sucesso, `False` caso contrário.

        Exibe:
        ---
            Mensagens de erro ou sucesso, dependendo do resultado da operação.

        Exemplo:
        ---
            >>> conta_corrente.sacar(valor=200.0)
            Sucesso: Saque de R$200.00 realizado! Saldo atual: R$800.00.
        """
        numero_saques = len(
            [transacao for transacao in self.extrato.transacoes if transacao["tipo"]
                == Saque.__name__]
        )

        excedeu_limite = valor > self.limite
        excedeu_saques = numero_saques >= self.limite_saque

        if excedeu_limite:
            print(emitir_mensagem(
                ('Alerta', f'Operação falhou! O saque excede o limite de R$ {self.limite:.2f}.')))

        elif excedeu_saques:
            print(emitir_mensagem(
                ('Alerta', 'Operação falhou! Número máximo de saques diário excedido.')))

        else:
            return super().sacar(valor=valor)

        return False

    def __str__(self):
        """
        #### Retorna uma representação textual da conta corrente.

        A representação inclui informações como agência, número da conta, tipo de conta, titular e limite de saque.

        Retorna:
        ---
            str: Uma string formatada com as informações da conta corrente.

        Exemplo:
        ---
            >>> print(conta_corrente)
            Agência:        0001
            C/C:            1234-0
            Tipo:           Conta Corrente
            Titular:        Fulano de Tal
            Limite Saque:   R$ 500.00
        """
        titular = self.cliente.nome if hasattr(
            self.cliente, "nome") else self.cliente.razao_social
        return f"""
            Agência:\t\t{self.agencia}
            C/C:\t\t{self._numero_conta}
            Tipo:\t\tConta Corrente
            Titular:\t\t{titular}
            Limite Saque:\tR$ {self.limite:.2f}
        """


class ContaPoupanca(ContaBancaria):
    """
    #### Representa uma conta poupança.

    A classe `ContaPoupanca` herda de `ContaBancaria` e adiciona funcionalidades específicas, como a exigência de um depósito mínimo inicial.

    Atributos:
    ---
        cliente (Cliente): O cliente associado à conta.
        deposito_minimo (float): O valor mínimo exigido para o depósito inicial.

    Métodos:
    ---
        depositar(valor: float): Realiza um depósito na conta, verificando se o valor é válido.
        numero_deposito: Retorna o número total de depósitos realizados na conta.
        __str__(): Retorna uma representação textual da conta poupança.
    """

    def __init__(self, cliente, deposito_minimo=100):
        """
        #### Inicializa uma conta poupança.

        Parâmetros:
        ---
            cliente (Cliente): O cliente associado à conta.
            deposito_minimo (float, opcional): O valor mínimo exigido para o depósito inicial. Padrão é R$ 100,00.

        Retorna:
        ---
            None
        """
        super().__init__(cliente)
        self.deposito_minimo = deposito_minimo

    def depositar(self, valor):
        """
        #### Realiza um depósito na conta poupança.

        Este método permite adicionar um valor ao saldo da conta, desde que o valor seja válido.

        Parâmetros:
        ---
            valor (float): O valor a ser depositado.

        Retorna:
        ---
            bool: `True` se o depósito for realizado com sucesso, `False` caso contrário.

        Exibe:
        ---
            Mensagens de erro ou sucesso, dependendo do resultado da operação.

        Exemplo:
        ---
            >>> conta_poupanca.depositar(valor=200.0)
            Sucesso: Depósito de R$200.00 realizado! Saldo atual: R$1200.00.
        """
        if valor > 0:
            super().depositar(valor)
            return True
        else:
            print(emitir_mensagem(
                ('Erro', 'Operação falhou! O valor informado é inválido.')))
        return False

    @property
    def numero_deposito(self):
        """
        #### Retorna o número total de depósitos realizados na conta poupança.

        Este método verifica o extrato da conta e conta todas as transações do tipo "Depósito".

        Retorna:
        ---
            int: O número total de depósitos realizados.

        Exemplo:
        ---
            >>> conta_poupanca.numero_deposito
            5
        """
        return len([
            transacao for transacao in self.extrato.transacoes
            if transacao["tipo"] == Deposito.__name__
        ])

    def __str__(self):
        """
        #### Retorna uma representação textual da conta poupança.

        A representação inclui informações como agência, número da conta, tipo de conta, titular e valor do depósito mínimo.

        Retorna:
        ---
            str: Uma string formatada com as informações da conta poupança.

        Exemplo:
        ---
            >>> print(conta_poupanca)
                Agência:        0001
                C/P:            4321-0
                Tipo:           Conta Poupança
                Titular:        João Silva
                Depósito Mínimo: R$ 100.00
        """
        titular = self.cliente.nome if hasattr(
            self.cliente, "nome") else self.cliente.razao_social
        return f"""
             Agência:\t\t{self.agencia}
             C/P:\t\t{self._numero_conta}
             Tipo:\t\tConta Poupança
             Titular:\t\t{titular}
             Depósito Mínimo:\tR$ {self.deposito_minimo:.2f}
        """


class Banco:
    """
    #### Representa o banco e gerencia clientes e contas.

    A classe `Banco` é responsável por armazenar os clientes cadastrados e fornecer métodos para gerenciar
    tanto os clientes quanto as contas associadas a eles.

    Atributos:
    ---
        _clientes (list): Lista de clientes cadastrados no banco.

    Métodos:
    ---
        adicionar_cliente(cliente): Adiciona um cliente à lista de clientes do banco.
        listar_clientes(): Retorna a lista de clientes cadastrados.
        listar_contas(): Retorna uma lista de todas as contas associadas aos clientes do banco.
    """

    def __init__(self):
        """
        #### Inicializa a classe `Banco`.

        Este método cria uma lista vazia para armazenar os clientes cadastrados no banco.

        Retorna:
        ---
            None
        """
        self._clientes = []

    def adicionar_cliente(self, cliente):
        """
        #### Adiciona um cliente à lista de clientes do banco.

        Este método permite cadastrar um novo cliente no banco.

        Parâmetros:
        ---
            cliente (Cliente): O cliente a ser adicionado.

        Retorna:
        ---
            None

        Exemplo:
        ---
            >>> banco.adicionar_cliente(cliente)
            Cliente adicionado com sucesso.
        """
        self._clientes.append(cliente)

    def listar_clientes(self):
        """
        #### Retorna a lista de clientes cadastrados no banco.

        Este método fornece acesso à lista de clientes armazenados no banco.

        Retorna:
        ---
            list: Uma lista contendo os clientes cadastrados.

        Exemplo:
        ---
            >>> clientes = banco.listar_clientes()
            >>> for cliente in clientes:
            ...     print(cliente.nome)
        """
        return self._clientes

    def listar_contas(self):
        """
        #### Retorna uma lista de todas as contas associadas aos clientes do banco.

        Este método percorre todos os clientes cadastrados e retorna uma lista com todas as contas vinculadas a eles.

        Retorna:
        ---
            list: Uma lista contendo todas as contas associadas aos clientes.

        Exemplo:
        ---
            >>> contas = banco.listar_contas()
            >>> for conta in contas:
            ...     print(conta.numero_conta)
        """
        return [conta for cliente in self._clientes for conta in cliente.contas]


class ImprimirExtrato:
    def __init__(self):
        """
        #### Inicializa a classe `ImprimirExtrato`.

        Este método cria uma lista vazia para armazenar as transações realizadas na conta.

        Retorna:
        ---
            None
        """
        self._transacoes = []

    @property
    def transacoes(self):
        """
        #### Retorna a lista de transações realizadas na conta.

        Retorna:
        ---
            list: Uma lista contendo as transações realizadas.

        Exemplo:
        ---
            >>> transacoes = conta.extrato.transacoes
            >>> for transacao in transacoes:
            ...     print(transacao)
        """
        return self._transacoes

    def adicionar_transacao(self, transacao):
        """
        #### Adiciona uma transação ao extrato da conta.

        Este método registra uma nova transação no extrato da conta, incluindo o tipo, valor e data da transação.

        Parâmetros:
        ---
            transacao (Transacao): A transação a ser registrada.

        Retorna:
        ---
            None

        Exemplo:
        ---
            >>> conta.extrato.adicionar_transacao(transacao)
            Transação registrada com sucesso.
        """
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            }
        )


class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        """
        #### Retorna o valor da transação.

        Este método deve ser implementado pelas subclasses de `Transacao`.

        Retorna:
        ---
            float: O valor da transação.
        """

    @classmethod
    @abstractmethod
    def registrar(cls, conta, valor):
        """
        #### Registra uma transação na conta.

        Este método deve ser implementado pelas subclasses de `Transacao` para registrar uma transação específica.

        Parâmetros:
        ---
            conta (ContaBancaria): A conta onde a transação será registrada.
            valor (float): O valor da transação.

        Retorna:
        ---
            Transacao: A transação registrada, ou `None` se a transação falhar.
        """


class Saque(Transacao):
    def __init__(self, valor):
        """
        #### Inicializa uma transação de saque.

        Parâmetros:
        ---
            valor (float): O valor do saque.

        Retorna:
        ---
            None
        """
        self._valor = valor

    @property
    def valor(self):
        """
        #### Retorna o valor do saque.

        Retorna:
        ---
            float: O valor do saque.
        """
        return self._valor

    @classmethod
    def registrar(cls, conta, valor):
        """
        #### Registra uma transação de saque na conta.

        Este método realiza um saque na conta e registra a transação no extrato, caso o saque seja bem-sucedido.

        Parâmetros:
        ---
            conta (ContaBancaria): A conta onde o saque será realizado.
            valor (float): O valor do saque.

        Retorna:
        ---
            Saque: A transação de saque registrada, ou `None` se o saque falhar.

        Exemplo:
        ---
            >>> transacao = Saque.registrar(conta, 100.0)
            >>> if transacao:
            ...     print("Saque realizado com sucesso.")
        """
        sucesso_transacao = conta.sacar(valor=valor)

        if sucesso_transacao:
            transacao = cls(valor)
            conta.extrato.adicionar_transacao(transacao)
            return transacao
        return None


class Deposito(Transacao):
    def __init__(self, valor):
        """
        #### Inicializa uma transação de depósito.

        Parâmetros:
        ---
            valor (float): O valor do depósito.

        Retorna:
        ---
            None
        """
        self._valor = valor

    @property
    def valor(self):
        """
        #### Retorna o valor do depósito.

        Retorna:
        ---
            float: O valor do depósito.
        """
        return self._valor

    @classmethod
    def registrar(cls, conta, valor):
        """
        #### Registra uma transação de depósito na conta.

        Este método realiza um depósito na conta e registra a transação no extrato, caso o depósito seja bem-sucedido.

        Parâmetros:
        ---
            conta (ContaBancaria): A conta onde o depósito será realizado.
            valor (float): O valor do depósito.

        Retorna:
        ---
            Deposito: A transação de depósito registrada, ou `None` se o depósito falhar.

        Exemplo:
        ---
            >>> transacao = Deposito.registrar(conta, 200.0)
            >>> if transacao:
            ...     print("Depósito realizado com sucesso.")
        """
        sucesso_transacao = conta.depositar(valor)

        if sucesso_transacao:
            transacao = cls(valor)
            conta.extrato.adicionar_transacao(transacao)
            return transacao
        return None


def obter_valor_float(mensagem: str) -> float:
    """
    #### Solicita ao usuário um valor numérico e garante que seja um número válido.

    Parâmetros:
    ---
        mensagem (str): Mensagem a ser exibida ao solicitar a entrada do usuário.

    Retorna:
    ---
        float: O valor inserido pelo usuário.
    """

    while True:
        try:
            return float(input(mensagem).strip())
        except ValueError:
            print(emitir_mensagem(('Aviso', 'Digite um valor válido.')))


def buscar_conta(conta_bancaria, numero_conta):
    """
    #### Busca uma conta bancária pelo número da conta.

    Este método percorre a lista de contas bancárias e retorna a conta correspondente ao número informado.

    Parâmetros:
    ---
        conta_bancaria (list): Lista de contas bancárias.
        numero_conta (str): O número da conta a ser buscado.

    Retorna:
    ---
        ContaBancaria: A conta correspondente ao número informado, ou `None` se não for encontrada.

    Exemplo:
    ---
        >>> conta = buscar_conta(contas, "1234-0")
        >>> if conta:
        ...     print("Conta encontrada.")
    """
    for conta in conta_bancaria:
        if str(conta.numero_conta) == numero_conta:
            return conta
    return None


def filtrar_cliente(identificador, clientes):
    """
    #### Busca um cliente pelo CPF ou CNPJ.

    Este método percorre a lista de clientes e retorna o cliente correspondente ao identificador informado.

    Parâmetros:
    ---
        identificador (str): O CPF ou CNPJ do cliente.
        clientes (list): Lista de clientes cadastrados.

    Retorna:
    ---
        Cliente: O cliente correspondente ao identificador informado, ou `None` se não for encontrado.

    Exemplo:
    ---
        >>> cliente = filtrar_cliente("12345678900", clientes)
        >>> if cliente:
        ...     print("Cliente encontrado.")
    """
    for cliente in clientes:
        if hasattr(cliente, "cpf") and cliente.cpf == identificador:
            return cliente
        elif hasattr(cliente, "cnpj") and cliente.cnpj == identificador:
            return cliente
    return None


def cadastrar_cliente(clientes, identificador=None):
    while True:
        tipo_pessoa = input(
            '\t Digite (F) para Pessoa Física ou (J) para Pessoa Jurídica: ').strip().lower()
        if tipo_pessoa in ['f', 'j']:
            break
        print(emitir_mensagem(
            ('Erro', 'Opção inválida. Escolha "F" para Pessoa Física ou "J" para Pessoa Jurídica.')))

    if identificador is None:
        identificador = input(
            '\t Informe o CPF/CNPJ  (Somente Números): ').strip()

    tipo_pessoa = 'fisica' if tipo_pessoa == 'f' else 'juridica'

    # Pessoa Física
    # if tipo_pessoa == 'fisica' and len(identificador) != 11:
    #     print(emitir_mensagem(('Erro', 'CPF inválido.')))
    if tipo_pessoa == 'fisica':
        if filtrar_cliente(identificador, clientes):
            print('\t Cliente já cadastrado.')
            return

        nome = input('\t Informe o nome completo: ')
        data_nascimento = input(
            '\t Informe a data de nascimento (dd/mm/aaaa): ')
        try:
            cep = input('\t Informe o CEP: ')
            endereco = get_address_from_cep(cep)
            numero = input('\t Número da residência: ')

            print('\n\t'+'─' * 50)
            print(f'\t Rua: {endereco["street"]}, Número: {numero}')
            print(
                f'\t Bairro: {endereco["district"]} - CEP: {endereco["cep"]}')
            print(f'\t Cidade: {endereco["city"]}/{endereco["uf"]}')
            print('\t'+'─' * 50)

            # endereco_completo = (endereco["street"], numero, endereco["district"] + "\n\t " +
            #                      endereco["city"] + "/" + endereco["uf"] + " ─ " + cep)
            endereco_completo = (
                f"{endereco['street']}, {numero}, {endereco['district']}\n\t {endereco['city']}/{endereco['uf']} ─ {cep}").split(', ')

            cliente = PessoaFisica(nome=nome, data_nascimento=data_nascimento,
                                   cpf=identificador, endereco=endereco_completo, numero=numero, cep=cep)

        except exceptions.BrazilCEPException:
            print(emitir_mensagem(
                ('Erro', 'CEP não encontrado, informe o endereço manualmente.')))
            # endereco_manu = tuple(map(str.strip, input(
            #     '\t Informe o endereço completo (Rua, número, bairro, cidade, estado, CEP): ').split(',')))
            endereco_manu = input(
                '\t Informe o endereço completo (Rua, número, bairro, cidade, estado, CEP): ').split(', ')

            # endereco_completo = (endereco_manu[0], endereco_manu[1], endereco_manu[2] + "\n\t " +
            #                      endereco_manu[3] + "/" + endereco_manu[4] + " ─ " + endereco_manu[5])

            endereco_completo = (
                f"{endereco_manu[0]}, {endereco_manu[1]}, {endereco_manu[2]}\n\t {endereco_manu[3]}/{endereco_manu[4]} ─ {endereco_manu[5]}").split(', ')

            cliente = PessoaFisica(nome=nome, data_nascimento=data_nascimento,
                                   cpf=identificador, endereco=endereco_completo, numero=endereco_manu[1], cep=endereco_manu[5])

        clientes.append(cliente)

        print(f'\t Cliente {nome.title()} cadastrado com sucesso.\n')
        return

    # Pessoa Jurídica
    # if tipo_pessoa == 'juridica' and len(identificador) != 14:
    #     print(emitir_mensagem(('Erro', 'CNPJ inválido.')))
    if tipo_pessoa == 'juridica':
        if filtrar_cliente(identificador, clientes):
            print('\t Cliente já cadastrado.')
            return
        razao_social = input('\t Informe a razão social: ')
        try:
            cep = input('\t Informe o CEP: ')
            endereco = get_address_from_cep(cep)
            numero = input('\t Número da empresa: ')

            print('\t' + '─' * 50)
            print(f'\t Rua: {endereco["street"]}, Número: {numero}')
            print(
                f'\t Bairro: {endereco["district"]} - CEP: {endereco["cep"]}')
            print(f'\t Cidade: {endereco["city"]}/{endereco["uf"]}')
            print('\t' + '─' * 50)

            # endereco_completo = (endereco["street"], numero, endereco["district"] + "\n\t " +
            #                      endereco["city"] + "/" + endereco["uf"] + " ─ " + cep)
            endereco_completo = (
                f"{endereco['street']}, {numero}, {endereco['district']}\n\t {endereco['city']}/{endereco['uf']} ─ {cep}").split(', ')

            cliente = PessoaJuridica(razao_social=razao_social, cnpj=identificador,
                                     endereco=endereco_completo, numero=numero, cep=cep)

        except exceptions.BrazilCEPException:
            print(emitir_mensagem(
                ('Erro', 'CEP não encontrado, informe o endereço manualmente.')))
            endereco_manu = input(
                '\t Informe o endereço completo (Rua, número, bairro, cidade, estado, CEP): ').split(', ')
            endereco_completo = (
                f"{endereco_manu[0]}, {endereco_manu[1]}, {endereco_manu[2]}\n\t {endereco_manu[3]}/{endereco_manu[4]} ─ {endereco_manu[5]}").split(', ')

            cliente = PessoaJuridica(razao_social=razao_social, cnpj=identificador,
                                     endereco=endereco_completo, numero=endereco_manu[1], cep=endereco_manu[5])

        clientes.append(cliente)

        print(f'\t Cliente {razao_social.title()} cadastrado com sucesso.\n')


def depositar(conta_bancaria):
    """
    #### Realiza um depósito em uma conta bancária.

    Este método solicita o número da conta e o valor do depósito, valida as informações e realiza a transação, caso seja válida.

    Parâmetros:
    ---
        conta_bancaria (list): Lista de contas bancárias disponíveis.

    Retorna:
    ---
        bool: `True` se o depósito for realizado com sucesso, `False` caso contrário.

    Exemplo:
    ---
        >>> depositar(contas)
        Informe o número da conta: 1234-0
        Informe o valor do depósito: 200.0
        Depósito realizado com sucesso!
    """
    numero_conta = input('\t Informe o número da conta: ').strip()
    conta = buscar_conta(conta_bancaria, numero_conta=numero_conta)

    if not conta:
        print(emitir_mensagem(
            ('Erro', f'Conta {numero_conta} não encontrada.')))
        return False

    valor = obter_valor_float('\t Informe o valor do depósito: ')
    if valor <= 0:
        print(emitir_mensagem(
            ('Erro', 'Operação falhou! O valor informado é inválido.')))
        return False

    # Realiza o depósito
    transacao = Deposito.registrar(conta, valor)
    if transacao:
        return True
    else:
        return False


def sacar(conta_bancaria):
    """
    #### Realiza um saque em uma conta bancária.

    Este método solicita o número da conta e o valor do saque, valida as informações e realiza a transação, caso seja válida.

    Parâmetros:
    ---
        conta_bancaria (list): Lista de contas bancárias disponíveis.

    Retorna:
    ---
        bool: `True` se o saque for realizado com sucesso, `False` caso contrário.

    Exemplo:
    ---
        >>> sacar(contas)
        Informe o número da conta: 1234-0
        Informe o valor do saque: 100.0
        Saque realizado com sucesso!
    """
    numero_conta = input('\t Informe o número da conta: ').strip()
    conta = buscar_conta(conta_bancaria, numero_conta=numero_conta)

    if not conta:
        print(emitir_mensagem(
            ('Erro', f'Conta {numero_conta} não encontrada.')))
        return False

    valor = obter_valor_float('\t Informe o valor do saque: ')
    if valor <= 0:
        print(emitir_mensagem(
            ('Erro', 'Operação falhou! O valor informado é inválido.')))
        return False

    if valor > conta.saldo:
        print(emitir_mensagem(('Erro', 'Saldo insuficiente para realizar o saque.')))
        return False

    # Realiza o Saque
    transacao = Saque.registrar(conta, valor)
    if transacao:
        return True
    else:
        return False


def imprimir_extrato(conta_bancaria):
    """
    #### Imprime o extrato de uma conta bancária.

    Este método solicita o número da conta, valida as informações e exibe o extrato com todas as transações realizadas.

    Parâmetros:
    ---
        conta_bancaria (list): Lista de contas bancárias disponíveis.

    Retorna:
    ---
        bool: `True` se o extrato for exibido com sucesso, `False` caso contrário.

    Exemplo:
    ---
        >>> imprimir_extrato(contas)
        Informe o número da conta: 1234-0
        ╔═════════════════════ EXTRATO ═════════════════════╗
          01/04/2025 14:30:00  => Depósito:    R$ 200.00
          Saldo: R$ 200.00
        ╚══════════════════════════════════════════════════╝
    """
    numero_conta = input('\t Informe o número da conta: ').strip()
    conta = buscar_conta(conta_bancaria, numero_conta=numero_conta)

    if not conta:
        print(emitir_mensagem(
            ('Erro', f'Conta {numero_conta} não encontrada.')))
        return False

    print('\n\t╔═════════════════════ EXTRATO ═════════════════════╗\n')
    transacoes = conta.extrato.transacoes

    if not transacoes:
        print(emitir_mensagem(
            ('Aviso', 'Nenhuma transação foi realizada nesta conta.')))
    else:
        for transacao in transacoes:
            tipo = transacao['tipo']
            valor = transacao['valor']
            data = transacao['data']
            cor = Fore.RED if tipo == 'Saque' else Fore.GREEN if tipo == 'Deposito' else Fore.YELLOW
            sinal = ' <= ' if tipo == 'Saque' else ' => ' if tipo == 'Deposito' else ' == '
            nome = 'Saque:       ' if tipo == 'Saque' else 'Depósito:    ' if tipo == 'Deposito' else 'Transferência:'

            print(
                f"\t  {data}{cor}{sinal}{Style.RESET_ALL}{nome} R$ {valor:.2f}")

    n = len(f"{conta.saldo:.2f}")
    print(f'\n\t{"  "}',  '─' * (n + 13))
    print(f'\t    Saldo: R$ {conta.saldo:.2f}')
    print('\t╚' + '═' * 51 + '╝\n')
    return True


def criar_nova_conta(clientes, contas):
    """
    #### Cria uma nova conta bancária para um cliente.

    Este método solicita o CPF ou CNPJ do cliente, valida as informações e cria uma nova conta do tipo selecionado (corrente ou poupança). Para contas poupança, exige um depósito inicial mínimo.

    Parâmetros:
    ---
        clientes (list): Lista de clientes cadastrados.
        contas (list): Lista de contas bancárias existentes.

    Retorna:
    ---
        bool: `True` se a conta for criada com sucesso, `False` caso contrário.

    Exemplo:
    ---
        >>> criar_nova_conta(clientes, contas)
        Informe o CPF/CNPJ do cliente: 12345678900
        Digite (C) para conta corrente ou (P) para conta poupança: C
        Conta criada com sucesso!
    """
    identificador = input('\t Informe o CPF/CNPJ do cliente: ').strip()
    cliente = filtrar_cliente(identificador, clientes)

    if not cliente:
        print(emitir_mensagem(('Alerta', 'Cliente não encontrado!')))
        return False

    tipo_conta = _selecionar_tipo_conta()
    conta = ContaBancaria.criar_nova_conta(cliente, tipo_conta)

    # Validação do depósito inicial para Conta Poupança
    if tipo_conta == 'poupanca':
        while True:
            if conta.numero_deposito == 0:
                print(emitir_mensagem(
                    ('Aviso', f'Atenção! É necessário um depósito minimo de R$ {conta.deposito_minimo:.2f} para a criação da conta poupança.')))
                valor = obter_valor_float(
                    '\t Depósito inicial mínimo (R$ 100.00): ')

                if valor >= 100:
                    # Realiza o depósito na conta recém-criada
                    sucesso = conta.depositar(valor)

                    if sucesso:
                        break
                    else:
                        print(emitir_mensagem(
                            ('Erro', 'Falha ao processar o depósito.')))
            else:
                print(emitir_mensagem(
                    ('Erro',
                     f'Depósito mínimo não atingido. Valor informado: R$ {valor:.2f}')
                ))

    # contas.append(conta)
    cliente.adicionar_conta(conta)

    print(emitir_mensagem(
        ('Sucesso', f'Conta {conta.numero_conta} criada com sucesso!')))
    return True


def _selecionar_tipo_conta():
    """
    #### Solicita ao usuário o tipo de conta a ser criada.

    Este método exibe um menu para o usuário selecionar entre conta corrente e conta poupança.

    Retorna:
    ---
        str: O tipo de conta selecionado, "corrente" ou "poupanca".

    Exemplo:
    ---
        >>> tipo_conta = _selecionar_tipo_conta()
        >>> print(tipo_conta)
        "corrente"
    """
    while True:
        tipo_conta = input(
            '\t Digite (C) para conta corrente ou (P) para conta poupança: ').strip().lower()
        if tipo_conta in ['c', 'p']:
            break
        print(emitir_mensagem(
            ('Erro', 'Opção inválida. Escolha "C" para conta corrente ou "P" para conta poupança.')))

    tipo_conta = 'corrente' if tipo_conta == 'c' else 'poupanca'
    return tipo_conta


def listar_contas(clientes):
    """
    #### Lista todas as contas cadastradas no sistema.

    Este método exibe as informações de todas as contas associadas aos clientes cadastrados.

    Parâmetros:
    ---
        clientes (list): Lista de clientes cadastrados.

    Retorna:
    ---
        None

    Exemplo:
    ---
        >>> listar_contas(clientes)
        ══════════════════════════════════════════════════
                         CONTAS CADASTRADAS
        ══════════════════════════════════════════════════
        Conta #1
        Agência:         0001
        Nº da Conta:     1234-0
        Titular:         João Silva
        Saldo:           R$ 200.00
        Tipo de Conta:   Corrente
    """
    if not clientes:
        print(emitir_mensagem(("Alerta", "Nenhuma conta cadastrada.")))
        return

    print("\n\t" + "═" * 50)
    print("\t\t\t  CONTAS CADASTRADAS")
    print("\t" + "═" * 50)

    for cliente in clientes:
        for idx, conta in enumerate(cliente.contas, 1):
            print(f"\n\t Conta #{idx}")
            print(f"\n\t Agência:         {conta.agencia}")
            print(f"\t Nº da Conta:     {conta.numero_conta}")
            print(
                f"\t Titular:         {cliente.nome.title() if hasattr(cliente, 'nome') else cliente.razao_social.title()}")
            print(f"\t Saldo:           R$ {conta.saldo:.2f}")
            print(
                f"\t Tipo de Conta:   {'Corrente' if isinstance(conta, ContaCorrente) else 'Poupança'}")
            print('\t' + '─' * 50)


def sair() -> None:
    """
    #### Encerra a execução do sistema bancário.

    Retorna:
    ---
        None: A função encerra a execução do programa.
    """
    print("\n\t 🔹 Obrigado por usar o Banco D'Paula! Saindo! 🔹\n")
    sys.exit()


def listar_clientes(clientes):
    """
    #### Lista todos os clientes cadastrados no sistema.

    Este método exibe as informações de todos os clientes cadastrados, incluindo nome, CPF/CNPJ e endereço.

    Parâmetros:
    ---
        clientes (list): Lista de clientes cadastrados.

    Retorna:
    ---
        None

    Exemplo:
    ---
        >>> listar_clientes(clientes)
        Nome: João Silva
        CPF/CNPJ: 12345678900
        Endereço: Rua A, 10, Bairro B, Cidade/UF, CEP
    """
    if not clientes:
        print(emitir_mensagem(('Alerta', 'Nenhum cliente cadastrado.')))
        return

    for cliente in clientes:
        print('\t' + '═' * 50)
        print(
            f"\t Nome: {cliente.nome if hasattr(cliente, 'nome') else cliente.razao_social}")
        print(
            f"\t CPF/CNPJ: {cliente.cpf if hasattr(cliente, 'cpf') else cliente.cnpj}")

        print(f"\t Endereço: {', '.join(cliente.endereco)}")


def exibir_cliente(clientes):
    """
    #### Exibe as informações detalhadas de um cliente.

    Este método solicita o CPF ou CNPJ do cliente, valida as informações e exibe os dados do cliente, incluindo as contas associadas.

    Parâmetros:
    ---
        clientes (list): Lista de clientes cadastrados.

    Retorna:
    ---
        None

    Exemplo:
    ---
        >>> exibir_cliente(clientes)
        Informe o CPF ou CNPJ do cliente: 12345678900
        Nome: João Silva
        CPF: 12345678900
        Endereço: Rua A, 10, Bairro B, Cidade/UF, CEP
        Contas Vinculadas:
        ✔ 1234-0     Conta Corrente
    """
    identificador = input('\t Informe o CPF ou CNPJ do cliente: ').strip()
    cliente = filtrar_cliente(identificador, clientes)
    if cliente:
        print('\t' + '═' * 50)
        if isinstance(cliente, PessoaFisica):
            print(f"\t Nome: {cliente.nome.title()}")
            print(f"\t CPF: {cliente.cpf}")
            print(f"\t Data de Nascimento: {cliente.data_nascimento}")
        else:
            print(f"\t Razão Social: {cliente.razao_social.title()}")
            print(f"\t CNPJ: {cliente.cnpj}")

        print(f"\t Endereço: {', '.join(cliente.endereco)}")

        if cliente.contas:
            print("\n\t Contas Vinculadas:")
            print("\n\t\tNº \t      Tipo")
            print('\t' + '─' * 33)

            for conta in cliente.contas:
                tipo_conta = 'Conta Corrente' if isinstance(
                    conta, ContaCorrente) else 'Conta Poupança'
                print(
                    f"\t {Fore.GREEN} ✔ {Style.RESET_ALL}  {conta.numero_conta}     {tipo_conta}")
                # f"\t {Fore.GREEN} ✔ {Style.RESET_ALL}  {conta._numero_conta}     {conta.__class__.__name__[:5]} {conta.__class__.__name__[5:]}")
            print('\t' + '─' * 33 + '\n')
        else:
            print(emitir_mensagem(("Alerta", "Nenhuma conta vinculada ao cliente.")))
    else:
        print(emitir_mensagem(('Alerta', 'Cliente não encontrado.')))


def atualizar_cliente(clientes):
    """
    #### Atualiza as informações de um cliente.

    Este método solicita o CPF ou CNPJ do cliente, valida as informações e permite atualizar os dados pessoais e o endereço do cliente.

    Parâmetros:
    ---
        clientes (list): Lista de clientes cadastrados.

    Retorna:
    ---
        None

    Exemplo:
    ---
        >>> atualizar_cliente(clientes)
        Informe o CPF ou CNPJ do cliente: 12345678900
        Nome atual: João Silva. Novo nome: João da Silva
        Cliente atualizado com sucesso.
    """
    identificador = input("\t Informe o CPF ou CNPJ do cliente: ").strip()
    cliente = filtrar_cliente(identificador, clientes)
    if not cliente:
        print(emitir_mensagem(('Alerta', 'Cliente não encontrado.')))
        return

    print("\t Deixe em branco para manter o valor atual.")
    if isinstance(cliente, PessoaFisica):
        novo_nome = input(f"\t Nome atual: {cliente.nome}. Novo nome: ")
        if novo_nome.strip():
            cliente.nome = novo_nome.strip()

        nova_data = input(
            f"\t Data de nascimento atual: {cliente.data_nascimento}. Nova data (dd/mm/aaaa): ")
        if nova_data.strip():
            cliente.data_nascimento = nova_data.strip()
    else:
        nova_razao = input(
            f"\t Razão Social atual: {cliente.razao_social}. Nova Razão Social: ")
        if nova_razao.strip():
            cliente.razao_social = nova_razao.strip()

    atualizar_endereco = input(
        "\t Deseja atualizar o endereço? (S/N): ").strip().lower()
    if atualizar_endereco == 's':
        try:
            cep = input("\t Informe o novo CEP: ").strip()
            endereco = get_address_from_cep(cep)
            numero = input("\t Número: ").strip()
            print(f"\n\t Cidade: {endereco['city']}/{endereco['uf']}")
            print(f"\t Rua: {endereco['street']}, Número: {numero}")
            print(
                f"\t Bairro: {endereco['district']} - CEP: {endereco['cep']}\n")
            confirmar = input(
                "\t Confirmar novo endereço? (S/N): ").strip().lower()
            if confirmar == 's':
                cliente.endereco = (endereco["street"], numero, endereco["district"] + "\n" +
                                    endereco["city"] + "/" + endereco["uf"] + " ─ " + cep)
                cliente.numero = numero
                cliente.cep = cep
                print(emitir_mensagem(
                    ('Sucesso', 'Endereço atualizado com sucesso.')))
        except exceptions.BrazilCEPException:
            print(emitir_mensagem(
                ('Erro', 'CEP não encontrado. Atualização manual necessária.')))
            novo_endereco = input(
                "\t Informe o novo endereço (Rua, Número, Bairro, Cidade/UF, CEP): ")
            cliente.endereco = novo_endereco

    print(emitir_mensagem(('Sucesso', 'Cliente atualizado com sucesso.')))


def excluir_cliente(clientes, contas):
    """
    #### Exclui um cliente do sistema.

    Este método solicita o CPF ou CNPJ do cliente, valida as informações e exclui o cliente e suas contas associadas, caso existam.

    Parâmetros:
    ---
        clientes (list): Lista de clientes cadastrados.
        contas (list): Lista de contas bancárias existentes.

    Retorna:
    ---
        None

    Exemplo:
    ---
        >>> excluir_cliente(clientes, contas)
        Informe o CPF ou CNPJ do cliente: 12345678900
        Cliente excluído com sucesso.
    """
    identificador = input("\t Informe o CPF ou CNPJ do cliente: ").strip()
    cliente = filtrar_cliente(identificador, clientes)
    if not cliente:
        print(emitir_mensagem(('Alerta', 'Cliente não encontrado.')))
        return

    if cliente.contas:
        print(emitir_mensagem(
            ('Alerta', 'Cliente possui contas ativas.')))
        confirmar = input(
            "\t Deseja excluir todas as contas do cliente? (S/N): ").strip().lower()
        if confirmar == 's':
            # Exclui todas as contas do cliente
            for conta in cliente.contas[:]:
                contas.remove(conta)
                cliente.contas.remove(conta)
            print(emitir_mensagem(
                ('Sucesso', 'Todas as contas do cliente foram excluídas.')))
        else:
            print(emitir_mensagem(
                ('Alerta', 'Exclusão do cliente cancelada devido a contas ativas.')))
            return

    confirmar = input(
        "\t Tem certeza que deseja excluir o cliente? (S/N): ").strip().lower()
    if confirmar == 's':
        clientes.remove(cliente)
        print(emitir_mensagem(('Sucesso', 'Cliente excluído com sucesso.')))
    else:
        print(emitir_mensagem(('Alerta', 'Exclusão cancelada.')))


def iniciar() -> None:
    """
    #### Executa o loop principal do sistema bancário, permitindo ao usuário realizar operações.

    O sistema apresenta um menu interativo onde o usuário pode selecionar diferentes operações bancárias, como saque, depósito, impressão de extrato, criação de conta, gerenciamento de clientes e saída do sistema.

    Retorna:
    ---
        None: A função opera em um loop contínuo até que o usuário selecione a opção de saída.
    """
    banco = Banco()

    opcoes = {
        '1': lambda: sacar(banco.listar_contas()),
        '2': lambda: depositar(banco.listar_contas()),
        '3': lambda: imprimir_extrato(banco.listar_contas()),
        '4': lambda: criar_nova_conta(banco.listar_clientes(), banco.listar_contas()),
        '5':  sair,
        '6': lambda: cadastrar_cliente(banco.listar_clientes()),
        '7': lambda: exibir_cliente(banco.listar_clientes()),
        '8': lambda: atualizar_cliente(banco.listar_clientes()),
        '9': lambda: excluir_cliente(banco.listar_clientes(), banco.listar_contas()),
        '10': lambda: listar_contas(banco.listar_clientes())
    }

    os.system('cls' if os.name == 'nt' else 'clear')
    print(emitir_mensagem(('', '\n\t\t  Bem-vindo ao Banco D`Paula!')))
    while True:
        exibir_menu()
        opcao = input('\t Selecione uma operação: ')
        exibir_menu(opcao)

        if opcao in opcoes:
            resultado = opcoes[opcao]()
            if isinstance(resultado, bool) and resultado:
                pass
        else:
            print(emitir_mensagem(("Erro", "Opção inválida! Escolha novamente.")))


if __name__ == "__main__":
    iniciar()
