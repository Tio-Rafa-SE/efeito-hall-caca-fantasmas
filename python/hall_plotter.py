"""
Caça-Fantasmas com Efeito Hall (Fantasma 5) - Plotter em Python
Tio Rafa - Revista Mecatrônica Jovem nº 16
Versão atualizada do projeto original do professor Newton C. Braga.

Lê as linhas "bruto,mapeado" enviadas pelo Hall.ino e desenha as duas
curvas em tempo real com Tkinter + Matplotlib.

Como usar:
    pip install -r requirements.txt
    python hall_plotter.py                 # procura o Arduino sozinho
    python hall_plotter.py --porta COM3    # Windows, porta escolhida
    python hall_plotter.py --porta /dev/ttyACM0   # Linux

Feche o Monitor Serial e o Plotter Serial da Arduino IDE antes de rodar:
só um programa por vez pode usar a porta.
"""

import argparse
import sys
import time
import tkinter as tk
from collections import deque
from pathlib import Path

import serial
import serial.tools.list_ports
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Pillow é opcional: só serve para mostrar o banner "cabecalho.png".
try:
    from PIL import Image, ImageTk
except ImportError:
    Image = ImageTk = None

TITULO_JANELA = "Caça-Fantasmas - Mecatrônica Jovem"
VELOCIDADE_PADRAO = 9600      # igual ao Hall.ino
PONTOS_NA_TELA = 50           # quantas leituras aparecem no gráfico
INTERVALO_TELA_MS = 50        # de quanto em quanto tempo a tela é atualizada
BANNER = Path(__file__).with_name("cabecalho.png")  # opcional, ao lado do script

COR_FUNDO = "#0d0d14"
COR_TEXTO = "#e6e6f0"
COR_BRUTO = "lime"
COR_MAPEADO = "fuchsia"


def interpretar_linha(texto):
    """Transforma 'bruto,mapeado' em (int, int). Devolve None se a linha for inválida."""
    partes = texto.strip().split(",")
    if len(partes) != 2:
        return None
    try:
        return int(partes[0]), int(partes[1])
    except ValueError:
        return None


def encontrar_porta():
    """Escolhe automaticamente a porta de um Arduino, se houver só uma candidata."""
    portas = list(serial.tools.list_ports.comports())
    palavras = ("arduino", "ch340", "usb serial", "usb-serial", "acm")
    candidatas = [
        p for p in portas
        if any(w in f"{p.description} {p.device}".lower() for w in palavras)
    ]
    if len(candidatas) == 1:
        return candidatas[0].device
    if portas:
        print("Não consegui escolher a porta sozinho. Portas encontradas:")
        for p in portas:
            print(f"  {p.device} - {p.description}")
    else:
        print("Nenhuma porta serial encontrada. O Arduino está conectado?")
    print("Rode de novo com:  python hall_plotter.py --porta NOME_DA_PORTA")
    return None


class Plotter:
    def __init__(self, raiz, conexao, pontos):
        self.raiz = raiz
        self.conexao = conexao
        self.contador = 0
        self.eixo_x = deque(maxlen=pontos)
        self.bruto = deque(maxlen=pontos)
        self.mapeado = deque(maxlen=pontos)

        raiz.title(TITULO_JANELA)
        raiz.configure(bg=COR_FUNDO)
        self._montar_banner()
        self._montar_grafico()
        raiz.protocol("WM_DELETE_WINDOW", self.fechar)
        raiz.after(INTERVALO_TELA_MS, self.atualizar)

    def _montar_banner(self):
        if Image is None or not BANNER.exists():
            return
        imagem = Image.open(BANNER)
        imagem.thumbnail((900, 120))
        self._banner_tk = ImageTk.PhotoImage(imagem)  # guarda a referência, senão some
        tk.Label(self.raiz, image=self._banner_tk, bg=COR_FUNDO).pack(side=tk.TOP)

    def _montar_grafico(self):
        figura = Figure(figsize=(10, 4), dpi=100, facecolor=COR_FUNDO)
        self.eixo = figura.add_subplot(111, facecolor=COR_FUNDO)
        self.eixo.tick_params(colors=COR_TEXTO)
        for borda in self.eixo.spines.values():
            borda.set_color(COR_TEXTO)
        self.eixo.set_xlabel("Leituras", color=COR_TEXTO)
        self.eixo.set_ylabel("Valor (0 a 1023)", color=COR_TEXTO)
        self.eixo.grid(alpha=0.2)

        self.curva_bruto, = self.eixo.plot([], [], color=COR_BRUTO, label="Valor analógico (A0)")
        self.curva_mapeado, = self.eixo.plot([], [], color=COR_MAPEADO, label="Valor mapeado")
        self.eixo.legend(facecolor=COR_FUNDO, labelcolor=COR_TEXTO)

        self.tela = FigureCanvasTkAgg(figura, master=self.raiz)
        self.tela.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def ler_pendentes(self):
        """Lê TODAS as linhas que chegaram, para o gráfico não ficar atrasado."""
        novas = []
        while self.conexao.in_waiting > 0:
            linha = self.conexao.readline().decode("utf-8", errors="ignore")
            valores = interpretar_linha(linha)
            if valores is not None:
                novas.append(valores)
        return novas

    def atualizar(self):
        try:
            novas = self.ler_pendentes()
        except (serial.SerialException, OSError) as erro:
            print(f"Conexão perdida: {erro}")
            self.fechar()
            return

        for valor_bruto, valor_mapeado in novas:
            self.contador += 1
            self.eixo_x.append(self.contador)
            self.bruto.append(valor_bruto)
            self.mapeado.append(valor_mapeado)

        if novas:
            self.curva_bruto.set_data(self.eixo_x, self.bruto)
            self.curva_mapeado.set_data(self.eixo_x, self.mapeado)
            inicio, fim = self.eixo_x[0], self.eixo_x[-1]
            self.eixo.set_xlim(inicio, max(fim, inicio + 1))
            todos = list(self.bruto) + list(self.mapeado)
            self.eixo.set_ylim(min(todos) - 20, max(todos) + 20)
            self.tela.draw_idle()

        self.raiz.after(INTERVALO_TELA_MS, self.atualizar)

    def fechar(self):
        if self.conexao.is_open:
            self.conexao.close()
        self.raiz.destroy()


def main():
    leitor = argparse.ArgumentParser(description="Plotter do Caça-Fantasmas com Efeito Hall")
    leitor.add_argument("--porta", help="porta serial (ex.: COM3 ou /dev/ttyACM0)")
    leitor.add_argument("--velocidade", type=int, default=VELOCIDADE_PADRAO,
                        help=f"baud rate (padrão {VELOCIDADE_PADRAO}, igual ao Hall.ino)")
    leitor.add_argument("--pontos", type=int, default=PONTOS_NA_TELA,
                        help=f"leituras visíveis no gráfico (padrão {PONTOS_NA_TELA})")
    args = leitor.parse_args()

    porta = args.porta or encontrar_porta()
    if porta is None:
        sys.exit(1)

    try:
        conexao = serial.Serial(porta, args.velocidade, timeout=1)
    except serial.SerialException as erro:
        print(f"Não consegui abrir {porta}: {erro}")
        print("Dica: feche o Monitor Serial e o Plotter Serial da Arduino IDE.")
        sys.exit(1)

    time.sleep(2)  # o UNO reinicia ao abrir a porta; espera ele acordar
    conexao.reset_input_buffer()

    raiz = tk.Tk()
    Plotter(raiz, conexao, args.pontos)
    raiz.mainloop()


if __name__ == "__main__":
    main()
