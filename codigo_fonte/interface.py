from __future__ import annotations
from abc import ABC, abstractmethod
import functools
from tkinter.constants import LEFT, TOP
from livraria import InformacaoProduto, Livro
import tkinter as tk
import utilidades
import sistema_eventos as se
from typing import Callable, Dict, Tuple, Any, List

CONFIG_BTN = {"width": 25}

def criar_campo(componente_pai, texto_label) -> Tuple[tk.Frame, tk.Entry]:
    """
    Função utilitária para a criação de labels e entries.
    """
    frame = tk.Frame(componente_pai)
    label = tk.Label(frame, text=texto_label)
    entrada = tk.Entry(frame, width=60)

    label.pack(side=tk.LEFT, fill=tk.X)
    entrada.pack(side=tk.RIGHT)
    return (frame, entrada)
    
class QuadroMenu(ABC):

    """
    Instâncias desta classe representam menus.
    """

    def __init__(self, componente_pai: tk.Widget, layout: GerenciadorDeLayout, evts: se.SistemasEventos):
        self._quadro_menu: tk.Frame = tk.Frame(componente_pai)
        self.__layout = layout
        self._evts = evts
        self.criar_layout()
    
    @abstractmethod
    def criar_layout(self):
        """
        Método polimórfico para a criação de layout para menus
        """

    def mostrar(self):
        """
        Exibe o menu
        """
        self._quadro_menu.pack(expand=True, fill=tk.X)
    
    def esconder(self):
        """
        Esconde o menu
        """
        self._quadro_menu.pack_forget()

    def adicionar_componente(self, componente: tk.Widget, **opcoes):
        """
        Adiciona um componente gráfico ao menu.
        """
        componente.master = self._quadro_menu
        componente.pack(**opcoes)

    def criar_campo(self, texto: str, **opcoes) -> tk.Entry:
        """
        Esse método cria uma label e uma entrada de texto
        """
        frame, entrada = criar_campo(self._quadro_menu, texto)
        frame.master = self._quadro_menu
        frame.pack(**opcoes)
        return entrada
    
    def criar_botao(self, texto: str, comando: Callable, opcoes_botao: Dict[str, Any] = {}, **opcoes) -> tk.Button:
        """
        Esse método cria um botão
        """
        botao = tk.Button(self._quadro_menu, text=texto, command=comando, **opcoes_botao)
        botao.pack(**opcoes)   
        return botao

    def criar_label(self, opcoes_label: Dict[str, Any]) -> tk.Label:
        
        label = tk.Label(self._quadro_menu, **opcoes_label)
        return label


    @property
    def quadro(self) -> tk.Frame:
        return self.__quadro_menu

    @property
    def layout(self) -> GerenciadorDeLayout:
        return self.__layout


class MenuLogin(QuadroMenu):

    """
    Essa classe representa um menu de login
    """

    def criar_layout(self):
        self.__entrada_usuario = self.criar_campo("Usuário: ", fill=tk.X)
        self.__entrada_senha = self.criar_campo("Senha: ", fill=tk.X)
        self.__entrada_senha.config(show="\u2022")
        self.__msg_erro_login = tk.Label(text="Usuário e/ou senha inválido(s)", bg="red")
        self.__btn_logar = self.criar_botao("Entrar", self.processar_login, pady="10")

    def processar_login(self):
        usuario = self.__entrada_usuario.get()
        senha = self.__entrada_senha.get()

        if usuario == "admin" and senha == "admin":
            self.__msg_erro_login.pack_forget()
            self.layout.ativar("principal")
        else:
            self.__msg_erro_login.pack()

class MenuPrincipal(QuadroMenu):

    def criar_layout(self):
        self.__btn_cadastro = self.criar_botao("Cadastrar livro", functools.partial(self.alterar_layout, "cadastro"), CONFIG_BTN)
        self.__btn_listagem = self.criar_botao("Listar livros", functools.partial(self.alterar_layout, "listagem"), CONFIG_BTN)
        self.__btn_remocao = self.criar_botao("Remover estoque", functools.partial(self.alterar_layout, "remocao"), CONFIG_BTN)
        self.__btn_delecao = self.criar_botao("Deletar estoque", functools.partial(self.alterar_layout, "delecao"), CONFIG_BTN)
        self.__btn_vendas = self.criar_botao("Vender", functools.partial(self.alterar_layout, "vendas"), CONFIG_BTN)
        self.__btn_sair = self.criar_botao("Sair", functools.partial(self.alterar_layout, "login"), CONFIG_BTN)

        self.__sucesso_var = tk.StringVar()
        self.__label_sucesso = self.criar_label({"textvar": self.__sucesso_var, "bg": "green"})

        self._evts.escutar("operacao_completada", self.setar_msg_sucesso)

        self.__label_dinheiro_var = tk.StringVar()
        self.__label_dinheiro_var.set("Dinheiro: R$ 0.0")
        self.__label_dinheiro_atual = self.criar_label({"textvariable": self.__label_dinheiro_var})
        self.__label_dinheiro_atual.pack()

        self._evts.escutar("atualizar_dinheiro", self.atualizar_dinheiro)

    def atualizar_dinheiro(self, quantia: float):
        self.__label_dinheiro_var.set("Dinheiro: R$ {}".format(quantia))

    def setar_msg_sucesso(self, msg: str):
        self.__sucesso_var.set(msg)
        self.__label_sucesso.pack(pady=10)
    
    def alterar_layout(self, identificador_layout: str):
        self.__label_sucesso.pack_forget()
        self.layout.ativar(identificador_layout)

    
class MenuCadastro(QuadroMenu):

    def criar_layout(self):
        self.__campo_titulo = self.criar_campo("Título: ", fill=tk.X)
        self.__campo_preco = self.criar_campo("Preço: ", fill=tk.X)
        self.__campo_quantidade = self.criar_campo("Quantidade: ", fill=tk.X)
        self.__btn_cadastrar = self.criar_botao("Cadastrar", functools.partial(self.efetuar_cadastro_livro), CONFIG_BTN, pady=5)
        self.__btn_voltar = self.criar_botao("Voltar", self.voltar, CONFIG_BTN, pady=5)

        self.__error_msg_var = tk.StringVar()
        self.__cadastro_erro_label = self.criar_label({"textvar":self.__error_msg_var, "bg": "red"})

        self._evts.escutar("erro_cadastro", self.exibir_mensagem_erro)
        self._evts.escutar("callback_cadastro", self.callback_operacao_cadastrar)

    def exibir_mensagem_erro(self, msg: str):
        self.__error_msg_var.set(msg)
        self.__cadastro_erro_label.pack()

    def remover_mensagem_erro(self):
        self.__cadastro_erro_label.pack_forget()

    def voltar(self):
        self.remover_mensagem_erro()
        self.layout.ativar("principal")

    def callback_operacao_cadastrar(self):
        self._evts.transmitir("operacao_completada", "Cadastro realizado com sucesso!")
        self.voltar()

    def efetuar_cadastro_livro(self):
        titulo = self.__campo_titulo.get()
        preco: float = None
        qtd: int = None

        try:
            preco = float(self.__campo_preco.get())
        except:
            self.exibir_mensagem_erro("O preço deve ser um número número positivo! Tente novamente!")
            return

        try:
            qtd = int(self.__campo_quantidade.get())
        except:
            self.exibir_mensagem_erro("A quantidade deve ser um número positivo! Tente novamente!")
            return

        if len(titulo) < 3:
            self.exibir_mensagem_erro("O titulo do livre deve conter pelo menos 3 caracteres!")
            return
        
        if preco <= 0:
            self.exibir_mensagem_erro("O preco do livre deve ser um número positivo!")
            return
        
        if qtd < 1:
            self.exibir_mensagem_erro("A quantidade deve ser um número positivo!")
            return
            
        pdt = Livro(preco, titulo)
        self._evts.transmitir("efetuar_cadastro", pdt, qtd)

class MenuListagem(QuadroMenu):

    def criar_layout(self):
        utilidades.limpar_frame(self._quadro_menu)
        self._evts.escutar("envio_estoque", self.criar_listagem)
        self._evts.transmitir("solicitar_estoque")
        self._evts.escutar("estoque_alterado", self.criar_layout)

    
    def criar_linha_listagem(self, titulo, preco, qtd):
        frame = tk.Frame(self._quadro_menu)
        tk.Label(frame, text="Titulo: {}".format(titulo), width=15, anchor='w').pack(side=LEFT)
        tk.Label(frame, text="Preço: {}".format(preco), width=15, anchor='w').pack(side=LEFT)
        tk.Label(frame, text="Quantidade: {}".format(qtd), width=15, anchor='w').pack(side=LEFT)
        frame.pack(side=TOP, fill=tk.X)

    def criar_listagem(self, produtos: Dict[str, InformacaoProduto]):
        utilidades.limpar_frame(self._quadro_menu)
        for info_produto in produtos.values():
            self.criar_linha_listagem(info_produto.produto.titulo, info_produto.produto.preco, info_produto.qtd)
        self._evts.transmitir("listagem_pack")
        self._botao_voltar = self.criar_botao("Voltar", functools.partial(self.layout.ativar, "principal"), CONFIG_BTN, pady=5)

class MenuRemocao(MenuListagem):

    def criar_layout(self):
        super().criar_layout()
        self.__error_var = tk.StringVar()
        self.__error_label = self.criar_label({"textvar":self.__error_var, "bg": "red"})

    def criar_linha_listagem(self, titulo: str, preco, qtd: int):
        frame = tk.Frame(self._quadro_menu)
        tk.Label(frame, text="Titulo: {}".format(titulo), width=15, anchor='w').pack(side=LEFT)
        tk.Label(frame, text="Preço: {}".format(preco), width=15, anchor='w').pack(side=LEFT)
        tk.Label(frame, text="Quantidade: {}".format(qtd), width=15, anchor='w').pack(side=LEFT)
        entrada_qtd = tk.Entry(frame, width=10)
        tk.Button(frame, text="Remover", width=10, command=functools.partial(self.iniciar_remocao_produto, titulo, entrada_qtd)).pack(side=LEFT, padx=5)
        entrada_qtd.pack(side=LEFT)
        frame.pack(side=TOP, fill=tk.X)
    
    def criar_listagem(self, produtos: Dict[str, InformacaoProduto]):
        super().criar_listagem(produtos)
        self._botao_voltar.bind("<Button-1>", self.voltar)

    def voltar(self, evt):
        self.__error_label.pack_forget()
        self.layout.ativar("principal")

    def erro_remocao_produto(self, msg: str):
        self.__error_var.set(msg)
        self.__error_label.pack_forget()
        self.__error_label.pack(pady=5)

    def iniciar_remocao_produto(self, titulo: str, entrada_qtd: str):
        quantidade = None
        try:
            quantidade = int(entrada_qtd.get())
        except:
            self.erro_remocao_produto("A quantidade deve ser um número!")
            return

        if quantidade < 1:
            self.erro_remocao_produto("A quantidade deve ser um número positivo!")
            return
            
        self._evts.transmitir("remover_estoque", titulo, quantidade)

class MenuDelecao(MenuListagem):
    
    def criar_linha_listagem(self, titulo, preco, qtd):
        frame = tk.Frame(self._quadro_menu)
        tk.Label(frame, text="Titulo: {}".format(titulo), width=15, anchor='w').pack(side=LEFT)
        tk.Label(frame, text="Preço: {}".format(preco), width=15, anchor='w').pack(side=LEFT)
        tk.Label(frame, text="Quantidade: {}".format(qtd), width=15, anchor='w').pack(side=LEFT)
        tk.Button(frame, text="Deletar item", command=functools.partial(self.iniciar_delecao_produto, titulo)).pack(side=LEFT)
        frame.pack(fill=tk.BOTH)

    def iniciar_delecao_produto(self, titulo: str):
        self._evts.transmitir("deletar_produto", titulo)

class MenuVendas(MenuListagem):

    def __init__(self, componente_pai: tk.Widget, layout: GerenciadorDeLayout, evts: se.SistemasEventos):
        self.__interface_data: Dict[str, List[Any]] = dict()
        super().__init__(componente_pai, layout, evts)
        self.__vender_btn = self.criar_botao("Finalizar venda", functools.partial(self.finalizar_venda), CONFIG_BTN)
        self.__preco_total_var = tk.StringVar()
        self.__preco_total_var.set("Total: R$ {}".format(0.0))
        self.__preco_total_label = self.criar_label({"textvariable":self.__preco_total_var, "bg": "green"})

        self._evts.escutar("listagem_pack", self.pack_widgets_adicionais)
        
        self.__changed_disp_vars = list()
        self.__changed_qtd_vars = list()

        self._evts.escutar("venda_concluida", self.venda_concluida_callback)


    def venda_concluida_callback(self):
        self._evts.transmitir("operacao_completada", "Venda concluida com sucesso!!!")
        self.layout.ativar("principal")

    def finalizar_venda(self):
        if self.computar_preco_total() == 0.0:
            return

        self._evts.transmitir("processar_venda", self.__interface_data)
        self.computar_preco_total()

    def pack_widgets_adicionais(self):
        self.__preco_total_label.pack(pady=5)
        self.__vender_btn.pack()

    def computar_preco_total(self):
        preco_total = 0
        for pdata in self.__interface_data.values():
            preco_total += pdata[0]*pdata[2]
        self.__preco_total_var.set("Total: R$ {}".format(preco_total))
        return preco_total

    def adicionar_ao_carrinho(self, titulo, disp_var, car_var):
        if self.__interface_data[titulo][1] > 0:
            self.__interface_data[titulo][1] -= 1
            self.__interface_data[titulo][2] += 1
            disp_var.set("Qtd disp.: {}".format(self.__interface_data[titulo][1]))
            car_var.set("Qtd carrinho: {}".format(self.__interface_data[titulo][2]))

            t =  (self.__interface_data[titulo][1] + self.__interface_data[titulo][2], disp_var) 
            if t not in self.__changed_disp_vars:
                self.__changed_disp_vars.append(t)
            if car_var not in self.__changed_qtd_vars:
                self.__changed_qtd_vars.append(car_var)

            self.computar_preco_total()

    def remover_do_carrinho(self, titulo, disp_var, car_var):
        if self.__interface_data[titulo][2] > 0:
            self.__interface_data[titulo][1] += 1
            self.__interface_data[titulo][2] -= 1
            disp_var.set("Qtd disp.: {}".format(self.__interface_data[titulo][1]))
            car_var.set("Qtd carrinho: {}".format(self.__interface_data[titulo][2]))
            self.computar_preco_total()

    def criar_linha_listagem(self, titulo, preco, qtd):

        frame = tk.Frame(self._quadro_menu)
        dados = list()
        dados.append(preco)
        dados.append(qtd)
        dados.append(0)
        self.__interface_data[titulo] = dados 
        tk.Label(frame, text="Titulo: {}".format(titulo), width=10, anchor='w').pack(side=LEFT, fill=tk.X)
        tk.Label(frame, text="Preço: {}".format(preco), width=10, anchor='w').pack(side=LEFT)

        disp_qtd_var = tk.StringVar()
        disp_qtd_var.set("Qtd disp.: {}".format(qtd))
        car_qtd_var = tk.StringVar()
        car_qtd_var.set("Qtd carrinho: 0")

        tk.Label(frame, textvariable=disp_qtd_var, width=20, anchor='w').pack(side=LEFT)
        tk.Label(frame, textvariable=car_qtd_var, width=20, anchor="w").pack(side=LEFT)
        tk.Button(frame, text="-", command=functools.partial(self.remover_do_carrinho, titulo, disp_qtd_var, car_qtd_var)).pack(side=LEFT)
        tk.Button(frame, text="+", command=functools.partial(self.adicionar_ao_carrinho, titulo, disp_qtd_var, car_qtd_var)).pack(side=LEFT)
        frame.pack()
        
    def criar_listagem(self, produtos: Dict[str, InformacaoProduto]):
        super().criar_listagem(produtos)
        self._botao_voltar.bind("<Button-1>", self.voltar)

    def voltar(self, evt):
        self.__preco_total_var.set("Total: R$ 0.0")

        for qtd_var in self.__changed_qtd_vars:
            qtd_var.set("Qtd carrinho: 0")

        for tup in self.__changed_disp_vars:
            tup[1].set("Qtd disp.: {}".format(tup[0]))
        

        self.__changed_qtd_vars.clear()

        for pdata in self.__interface_data.values():
            if pdata[2] != 0:
                pdata[1] += pdata[2]
                pdata[2] = 0

        self.layout.ativar("principal")

class GerenciadorDeLayout:
    """
    Instâncias desta classe podem ser utilizadas para controlar o layout de uma janela TKinter.
    Uma nova janela tkinter é criada toda vez que esta classe é instanciada.
    """

    def __init__(self, sistema_eventos: se.SistemasEventos) -> None:
        self.__janela = tk.Tk()
        self.__sistema_eventos = sistema_eventos
        self.__menus: Dict[str, QuadroMenu] = dict()
        self.__janela.geometry("500x500")
        self.__janela.resizable(0, 0)
        self.__janela.title("E-Livraria 1.0")
        self.__quadro_fixo = tk.Frame(self.__janela)
        self.__quadro_fixo.pack_propagate(0)
        self.__quadro_fixo.pack(fill=tk.BOTH, expand=True)

    
    def adicionar_menu(self, menu: QuadroMenu, identificador: str):
        if identificador not in self.__menus:
            self.__menus[identificador] = menu
        else:
            raise ValueError("Um menu com o identificador '{}' ja esta cadastrado no gerenciador de layout".format(identificador))

    def ativar(self, identificador: str):
        """
        Ativa o menu identifcado por 'identificador' e desativa todos os outros menus
        """
        if identificador in self.__menus:
            copia_menus = self.__menus.copy()
            del copia_menus[identificador]

            for menu in copia_menus.values():
                menu.esconder()
    
            self.__menus[identificador].mostrar()

        else:
            raise ValueError("Menu não encontrado! Lembre de chamar o método 'adicionar_menu' antes de usar este método.")
    
    def iniciar_loop(self):
        tk.mainloop()

    @property
    def janela(self) -> tk.Widget:
        return self.__janela

    @property
    def quadro_fixo(self) -> tk.Frame:
        return self.__quadro_fixo