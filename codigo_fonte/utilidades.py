import tkinter as tk

def exibir_componente(componente: tk.Widget, **opcoes):
    componente.pack(**opcoes)

def esconder_componente(componente: tk.Widget):
    componente.pack_forget()

def limpar_frame(componente: tk.Frame):
    for componente_filho in componente.winfo_children():
        componente_filho.pack_forget()