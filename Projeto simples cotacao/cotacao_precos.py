import pandas as pd
import PySimpleGUI as sg
from utils import obter_dados_mercado


class CotacaoPrecos:
    def __init__(self):
        self.layout = [
            [sg.Text("Selecione o arquivo Excel: "), sg.Input(key="-FILE-"), sg.FileBrowse()],
            [sg.Text("Selecione o mercado: "),
             sg.Combo(['Adicione seu mercado 1 aqui', 'Adicione seu mercado 2 aqui', 'Adicione seu mercado 3 aqui'],
                      key="-MARKET-")],
            [sg.Button("Processar"), sg.Button("Cancelar"), sg.Button("Limpar"), sg.Button("Logout", visible=False)],
            [sg.Output(size=(60, 20), key="-OUTPUT-")]
        ]
        self.logged_in = False

    def validar_entrada(self, values):
        if not values["-FILE-"] or not values["-FILE-"].endswith('.xlsx'):
            sg.popup_error("Por favor, selecione um arquivo Excel válido!")
            return False
        elif not values["-MARKET-"]:
            sg.popup_error("Por favor, selecione um mercado!")
            return False
        return True

    def encontrar_melhor_preco(self, df, fornecedores):
        resultados = {}

        for index, row in df.iterrows():
            quantidade = row['QTD']
            produto = row['produto']

            melhor_preco = float("inf")
            melhor_fornecedor = ''
            preco_iguais = []

            for fornecedor in fornecedores:
                preco = row[fornecedor]

                if preco != 0:
                    if preco < melhor_preco:
                        melhor_preco = preco
                        melhor_fornecedor = fornecedor
                        preco_iguais = []
                    elif preco == melhor_preco:
                        preco_iguais.append(fornecedor)

            if melhor_fornecedor not in resultados:
                resultados[melhor_fornecedor] = []

            resultados[melhor_fornecedor].append({'Quantidade': quantidade, 'Produto': produto, 'Preço': melhor_preco,
                                                  'Fornecedores iguais': preco_iguais})

        return resultados

    def imprimir_resultados(self, resultados, market):
        for fornecedor, produtos in resultados.items():
            print(fornecedor)

            mercado = self.obter_dados_mercado(market)
            print("\n" + mercado["nome"])
            cnpj = mercado["cnpj"]

            ultimo_produto = None

            for produto in produtos:
                ultimo_produto = produto
                print(produto['Quantidade'], produto['Produto'], produto['Preço'])
                if produto['Fornecedores iguais']:
                    print("Preço igual para fornecedores:", ", ".join(produto['Fornecedores iguais']))

            if ultimo_produto:
                print(cnpj)

            print()

    def obter_dados_mercado(self, market):
        return obter_dados_mercado(market)

    def verificar_login(self, username, password):
        # Verifica se o nome de usuário e senha são válidos
        if username == "" and password == "":
            return True
        else:
            return False

    def criar_janela_login(self):
        login_layout = [
            [sg.Text("Nome de usuário:"), sg.Input(key="-USERNAME-")],
            [sg.Text("Senha:"), sg.Input(key="-PASSWORD-", password_char="*")],
            [sg.Button("Login"), sg.Button("Cancelar")]
        ]

        return sg.Window("Login", login_layout)

    def executar(self):
        # Criando a janela de login
        login_window = self.criar_janela_login()

        while True:
            event, login_values = login_window.read()

            if event == "Cancelar" or event == sg.WIN_CLOSED:
                break

            if event == "Login":
                if self.verificar_login(login_values["-USERNAME-"], login_values["-PASSWORD-"]):
                    self.logged_in = True
                    login_window.close()
                    break
                else:
                    sg.popup_error("Nome de usuário ou senha incorretos")

        if self.logged_in:
            # Criando a janela com o layout
            window = sg.Window("Cotação de Preços", self.layout)

            while True:
                event, values = window.read()

                if event == "Cancelar" or event == sg.WIN_CLOSED:
                    break

                elif event == "Processar":
                    if self.validar_entrada(values):
                        filename = values["-FILE-"]
                        market = values["-MARKET-"]

                        # Lendo o arquivo Excel
                        df = pd.read_excel(filename)
                        fornecedores = df.columns[2:]

                        # Encontrando o melhor preço para cada produto
                        resultados = self.encontrar_melhor_preco(df, fornecedores)

                        # Imprimindo os resultados
                        self.imprimir_resultados(resultados, market)

                elif event == "Limpar":
                    window["-OUTPUT-"].update("")

                elif event == "Logout":
                    self.logged_in = False
                    window["Logout"].update(visible=False)
                    break

                if self.logged_in:
                    window["Logout"].update(visible=True)

            window.close()

