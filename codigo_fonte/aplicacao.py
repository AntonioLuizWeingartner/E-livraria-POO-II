import pickle
import tkinter as tk
from tkinter.constants import TOP
import interface
import sistema_eventos as se
import functools
import livraria
import utilidades
import json
import pickle

class Aplicacao:

    """
    Essa classe representa a aplicacao
    """

    def __init__(self):
        self.__evts = se.SistemaEventos()
        self.__layout = interface.GerenciadorDeLayout(self.__evts)
        self.carregar()
        self.__carrinho_de_compras = livraria.Venda(self.__evts)
        self.gerar_interface()

        self.__evts.transmitir("solicitar_estoque")
        self.__evts.transmitir("atualizar_dinheiro", self.__estoque.dinheiro)
        self.__evts.escutar("estoque_alterado", self.salvar)
        self.__evts.escutar("atualizar_dinheiro", self.salvar)

    def gerar_interface(self):
        """
        Este método cria todas os menus da aplicação
        """
        self.__menu_principal = interface.MenuPrincipal(self.__layout.quadro_fixo, self.__layout, self.__evts)
        self.__menu_cadastro = interface.MenuCadastro(self.__layout.quadro_fixo, self.__layout, self.__evts)
        self.__menu_remocao = interface.MenuRemocao(self.__layout.quadro_fixo, self.__layout, self.__evts)
        self.__menu_delecao = interface.MenuDelecao(self.__layout.quadro_fixo, self.__layout, self.__evts)
        self.__menu_listagem = interface.MenuListagem(self.__layout.quadro_fixo, self.__layout, self.__evts)
        self.__menu_vendas = interface.MenuVendas(self.__layout.quadro_fixo, self.__layout, self.__evts)
        self.__menu_login = interface.MenuLogin(self.__layout.quadro_fixo, self.__layout, self.__evts)

        self.__layout.adicionar_menu(self.__menu_principal, "principal")
        self.__layout.adicionar_menu(self.__menu_cadastro, "cadastro")
        self.__layout.adicionar_menu(self.__menu_remocao, "remocao")
        self.__layout.adicionar_menu(self.__menu_delecao, "delecao")
        self.__layout.adicionar_menu(self.__menu_listagem, "listagem")
        self.__layout.adicionar_menu(self.__menu_vendas, "vendas")
        self.__layout.adicionar_menu(self.__menu_login, "login")
    
    def salvar(self, *args):
        """
        Salva o estado atual da aplicação em um arquivo
        """
        arquivo = open("dados/livraria.dados", "wb")
        save_obj = (self.__estoque.livros, self.__estoque.dinheiro)
        pickle.dump(save_obj, arquivo)
        arquivo.close()

    def carregar(self):
        """
        Carrega os dados salvos
        """
        try:
            arquivo_salvo = open("dados/livraria.dados", "rb+")
            dados_salvos = pickle.load(arquivo_salvo)
            arquivo_salvo.close()
        except:
            dados_salvos = None
        if dados_salvos is not None:
            self.__estoque = livraria.EstoqueLivro(self.__evts, dados_salvos[0], dados_salvos[1])
        else:
            self.__estoque = livraria.EstoqueLivro(self.__evts)

    def iniciar(self):
        """
        Inicia o loop principal da aplicacao
        """
        self.__layout.ativar("login")
        self.__layout.iniciar_loop()


if __name__ == "__main__":
    app = Aplicacao()
    app.iniciar()