from typing import Callable, Dict, List

class SistemaEventos:

    """
    Instâncias desta classe representam sistemas de eventos. A finalidade principal desta classe
    é evitar o acoplamento entre objetos. Ao providenciar uma interface comum pela qual os objetos
    podem trocar mensagens, o acoplamento entre esses objetos irá reduzir significativamente
    """

    def __init__(self):
        self.__metodos_cadastrados: Dict[str, List[Callable]] = dict()

    def escutar(self, mensagem: str, metodo: Callable):
        """
        Define um novo método para escutar a mensagem identificada pelo parâmetro 'mensagem'.
        
        OBSERVAÇÃO: NÃO USE FUNÇÕES ANÔNIMAS!!
        """
        if mensagem in self.__metodos_cadastrados:
            if metodo not in self.__metodos_cadastrados[mensagem]:
                self.__metodos_cadastrados[mensagem].append(metodo)
        else:
            self.__metodos_cadastrados[mensagem] = list()
            self.__metodos_cadastrados[mensagem].append(metodo)

    def parar_escuta(self, mensagem: str, metodo: Callable):
        """
        Faz com que o método alvo para de escutar a mensagem indentificada pelo parâmetro 'mensagem'
        """
        if mensagem in self.__metodos_cadastrados:
            if metodo in self.__metodos_cadastrados[mensagem]:
                self.__metodos_cadastrados[mensagem].remove()

    def transmitir(self, mensagem: str, *args, **kwargs):
        """
        Transmite uma mensagem identificada pelo parâmetro 'mensagem'.
        """
        if mensagem in self.__metodos_cadastrados:
            for metodo in self.__metodos_cadastrados[mensagem]:
                metodo(*args, **kwargs)
    