from tkinter.constants import S
from typing import Dict, List, Tuple, Optional, Any
from abc import ABC, abstractmethod
import sistema_eventos as se


class Produto:
    """
    Instancias desta classe representam produtos genéricos. Esta classe deve ser herdada para criar produtos especificos.
    """

    def __init__(self, preco: float) -> None:
        self.__preco = preco

    @property
    def preco(self) -> float:
        return self.__preco

class Livro(Produto):
    """
    Especialização da classe produto. Instâncias desta classe representam livros.
    """

    def __init__(self, preco: float, titulo: str):
        super().__init__(preco)
        self.__titulo = titulo

    @property
    def titulo(self) -> str:
        return self.__titulo

class InformacaoProduto:

    """
    Esta classe representa informacões de um produto que esta em estoque.
    """

    def __init__(self, produto: Produto, qtd: int):
        self.__produto = produto
        self.__qtd = qtd

    @property
    def produto(self) -> Produto:
        return self.__produto

    @property
    def qtd(self) -> int:
        return self.__qtd

    @qtd.setter
    def qtd(self, qtd) -> int:
        self.__qtd = qtd


class Estoque(ABC):

    """
    Esta classe abstrata deve ser herdada para criar especializações de Estoques.
    """

    @abstractmethod
    def adicionar(self):
        """
        Adiciona um produto ao estoque.
        """
        pass
    
    @abstractmethod
    def remover(self):
        """
        Remove um produto do estoque se existir. Tentar remover um produto que não existe irá resultar em um erro.
        """
        pass
    
    @abstractmethod
    def retornar_produto(self) -> Produto:
        """
        Retorna um produto, se existir, cadastrado com o identificador especificado.
        """
        pass

class EstoqueLivro(Estoque):

    """
    Especialização da classe Estoque. Esta especialização trabalha diretamente com livros.
    """

    def __init__(self, evts: se.SistemaEventos, livros_cadastrados = None, dinheiro = None):
        
        if livros_cadastrados is None:
            self.__livros_cadastrados: Dict[str, InformacaoProduto] = dict()
        else:
            self.__livros_cadastrados: Dict[str, InformacaoProduto] = livros_cadastrados

        if dinheiro is None:    
            self.__dinheiro_total: float = 0.0
        else:
            self.__dinheiro_total: float = dinheiro
        
        self.__evts: se.SistemasEventos = evts

        self.__evts.escutar("venda_finalizada", self.callback_venda_finalizada)
        self.__evts.escutar("efetuar_cadastro", self.adicionar)
        self.__evts.escutar("solicitar_estoque", self.transmitir_estoque)
        self.__evts.escutar("remover_estoque", self.remover)
        self.__evts.escutar("deletar_produto", self.deletar)

    @property
    def livros(self) -> Dict[str, InformacaoProduto]:
        return self.__livros_cadastrados
    
    @property
    def dinheiro(self) -> float:
        return self.__dinheiro_total

    def transmitir_estoque(self):
        """
        Transmite uma cópia dos livros cadastrados para qualquer objeto que estiver interessado.
        """
        self.__evts.transmitir("envio_estoque", self.__livros_cadastrados.copy())

    def adicionar(self, produto: Livro, quantidade: int):
        """
        Adiciona um produto ao estoque de livros
        """
        sucesso = False
        if produto.titulo in self.__livros_cadastrados:
            
            if produto.preco != self.__livros_cadastrados[produto.titulo].produto.preco:
                #Se um produto com o titulo especificado ja existir no estoque, e o preço do produto em
                #estoque for diferente do que esta sendo cadastrado, então lançe um erro.
                pdt = self.__livros_cadastrados[produto.titulo].produto
                self.__evts.transmitir("erro_cadastro", "Um livro com o título '{}' e preço 'R$ {}' já existe no estoque!".format(pdt.titulo, pdt.preco))
                raise ValueError("Um livro com o título '{}' e preço 'R$ {}' já existe no estoque!".format(pdt.titulo, pdt.preco))
            self.__livros_cadastrados[produto.titulo].qtd += quantidade
            sucesso = True
        else:
            self.__livros_cadastrados[produto.titulo] = InformacaoProduto(produto, quantidade)
            sucesso = True
        
        if sucesso:
            self.__evts.transmitir("callback_cadastro")
            self.__evts.transmitir("estoque_alterado")

    def remover(self, titulo: str, quantidade: int):
        """
        Remove uma quantidade especifica de livros do estoque
        """
        if titulo in self.__livros_cadastrados:
            self.__livros_cadastrados[titulo].qtd -= quantidade
            if self.__livros_cadastrados[titulo].qtd < 0:
                self.__livros_cadastrados[titulo].qtd = 0
            self.__evts.transmitir("estoque_alterado")
        else:
            raise ValueError("O produto com o título '{}' não existe no estoque!".format(titulo))

    def deletar(self, titulo: str):
        """
        Remove todos os livros do estoque que possuam o titulo especificado.
        """
        if titulo in self.__livros_cadastrados:
            del self.__livros_cadastrados[titulo]
            self.__evts.transmitir("estoque_alterado")
        else:
            raise ValueError("O produto com o título '{}' não existe no estoque!".format(titulo))

    def retornar_produto(self, titulo: str) -> Optional[InformacaoProduto]:
        """
        Pesquisa o estoque por um livro com o titulo especificado e o retorna se ele existir.
        """
        if titulo in self.__livros_cadastrados:
            return self.__livros_cadastrados[titulo]

    def adcionar_dinheiro(self, quantia: float):
        self.__dinheiro_total += quantia
        self.__evts.transmitir("dinheiro_alterado", self.__dinheiro_total)

    def callback_venda_finalizada(self, produtos_vendidos: Dict[str, InformacaoProduto], preco_total: float):
        for titulo, info_produto in produtos_vendidos.items():
            self.remover(titulo, info_produto.qtd)
        self.adcionar_dinheiro(preco_total)
        self.__evts.transmitir("venda_concluida")
        self.__evts.transmitir("atualizar_dinheiro", self.__dinheiro_total)
    

class Venda:

    """
    Esta classe representa um carrinho de compras
    """

    def __init__(self, evts: se.SistemaEventos):
        self.__carrinho_compras: Dict[str, InformacaoProduto] = dict()
        self.__preco_total: float = 0.0
        self._evts = evts
        self._evts.escutar('processar_venda', self.processar_venda)

    def computar_preco_total(self):
        """
        Computa o valor total do carrinho de compras
        """
        preco_total = 0
        for info_produto in self.__carrinho_compras.values():
            preco_total += info_produto.qtd*info_produto.produto.preco
        self.__preco_total = preco_total
        self._evts.transmitir("carrinho_alterado", self.__preco_total)

    def adicionar_item(self, produto: Livro, quantia: int):
        """
        Adiciona um item ao carrinho de compras
        """
        if produto.titulo in self.__carrinho_compras:
            self.__carrinho_compras[produto.titulo].qtd += quantia
        else:
            self.__carrinho_compras[produto.titulo] = InformacaoProduto(produto, quantia)
        self.computar_preco_total()

    def remover_item(self, produto: Livro, quantia: int):
        """
        Remove um item do carrinho de compras
        """
        if produto.titulo in self.__carrinho_compras:
            self.__carrinho_compras[produto.titulo].qtd -=  quantia
            if self.__carrinho_compras[produto.titulo].qtd < 1:
                del self.__carrinho_compras[produto.titulo]
            self.computar_preco_total()
        else:
            raise ValueError("Livro com titulo '{}' não pôde ser localizado no carrinho de compras!")

    def finalizar_venda(self):
        self._evts.transmitir("venda_finalizada", self.__carrinho_compras, self.__preco_total)
        self.__carrinho_compras.clear()
        self.__preco_total = 0

    def processar_venda(self, items: Dict[str, List[Any]]):
        for titulo, info in items.items():
            produto = Livro(float(info[0]), titulo)
            self.adicionar_item(produto, int(info[2]))
        self.finalizar_venda()
