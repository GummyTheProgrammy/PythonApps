import sys
from PySide6.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout)
from PySide6.QtGui import QPixmap, QBitmap, QColor, QPainter, QFont, QClipboard
from PySide6.QtCore import Qt, QPoint

class SuperGummyGadget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Super Gummy Gadget")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)  # Sem bordas e sempre no topo
        self.setAttribute(Qt.WA_TranslucentBackground)  # Fundo transparente para a máscara

        self.initial_pos = None  # Para o arraste da janela

        # --- VARIÁVEIS CONFIGURÁVEIS PARA BOTÕES (POSIÇÕES, TAMANHOS E TRANSPARÊNCIA) ---
        # Transparência: 0 (totalmente transparente) a 255 (opaco). 128 é 50% opacidade.
        self.button_transparency = 0  # Valor inicial para depuração (mude para 0 para invisível)

        # Tamanhos dos botões (quadrados por padrão, mas podem ser retangulares)
        self.button_size = 20  # Tamanho padrão para largura e altura
        self.plus_button_width = self.button_size
        self.plus_button_height = self.button_size
        self.minus_button_width = self.button_size
        self.minus_button_height = 20  # Exemplo de customização
        self.copy_button_width = 95  # Exemplo de customização (talvez erro de digitação, ajuste conforme necessário)
        self.copy_button_height = self.button_size
        self.close_button_width = self.button_size
        self.close_button_height = self.button_size

        # Posições dos botões (em coordenadas relativas à janela, ex: cantos aleatórios ou específicos)
        # Exemplo: canto superior esquerdo (10,10), inferior direito (width-30, height-30), etc.
        # Use valores aleatórios ou fixos; aqui usei os fornecidos e aleatórios para os outros
        self.plus_button_x = 165
        self.plus_button_y = 85
        self.minus_button_x = 163   # Exemplo aleatório: canto superior esquerdo
        self.minus_button_y = 107
        self.copy_button_x = 60  # Exemplo aleatório: canto superior direito
        self.copy_button_y = 165
        self.close_button_x = 17
        self.close_button_y = 90

        # --- CONTADOR ---
        self.counter = 0  # Inicia em 0
        self.counter_max = 9999
        self.counter_min = 0

        # --- CARREGAR E REDIMENSIONAR A IMAGEM DE FUNDO ---
        # Certifique-se de que 'circle.png' está no mesmo diretório
        desired_size = 200  # Tamanho desejado (200x200)
        self.background_pixmap = QPixmap("circle.png")
        if self.background_pixmap.isNull():
            print("Erro: circle.png não encontrado ou não pode ser carregado.")
            # Fallback para um círculo sólido se a imagem não carregar
            self.background_pixmap = QPixmap(desired_size, desired_size)  # Tamanho padrão
            self.background_pixmap.fill(Qt.transparent)  # Fundo transparente
            painter = QPainter(self.background_pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setPen(QColor("#78a9ff"))  # Cor da borda
            painter.setBrush(QColor("#4c8df5"))  # Cor de preenchimento azul
            painter.drawEllipse(0, 0, desired_size, desired_size)  # Desenha o círculo completo
            painter.end()
        else:
            # Redimensiona a imagem carregada para 200x200, mantendo a proporção e suavizando
            self.background_pixmap = self.background_pixmap.scaled(
                desired_size, desired_size, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )

        self.resize(self.background_pixmap.size())  # Redimensiona a janela para o tamanho da imagem (agora 200x200)

        # Criar a máscara para o formato redondo
        mask = QBitmap(self.background_pixmap.size())
        mask.fill(Qt.white)  # Fundo da máscara branco (transparente)
        mask_painter = QPainter(mask)
        mask_painter.setBrush(Qt.black)  # Cor preta para o círculo (visível)
        mask_painter.drawEllipse(0, 0, self.width(), self.height())  # Desenha um círculo preto
        mask_painter.end()

        self.setMask(mask)  # Aplica a máscara à janela

        # QLabel para exibir a imagem de fundo
        self.background_label = QLabel(self)
        self.background_label.setPixmap(self.background_pixmap)
        self.background_label.setGeometry(0, 0, self.width(), self.height())

        # --- LAYOUT PRINCIPAL (OPCIONAL, MAS USADO PARA FACILITAR ALINHAMENTO) ---
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)  # Remove margens do layout

        # Título do Gadget
        #self.title_label = QLabel("SUPER GUMMY GADGETS", self)
        #self.title_label.setAlignment(Qt.AlignCenter)
        #self.title_label.setStyleSheet("color: white; font-size: 10px; font-weight: bold;")
        #self.title_label.setGeometry(0, 15, self.width(), 20)  # Posição fixa no topo

        # --- CONTADOR NO CENTRO COM FONTE 7-SEGMENT ---
        # Assumindo que a fonte "Digital-7" está instalada no sistema (baixe e instale se necessário)
        # Alternativa: use "Courier" ou outra monoespaced para simular
        self.counter_label = QLabel(f"{self.counter:04d}", self)
        self.counter_label.setAlignment(Qt.AlignCenter)
        counter_font = QFont("digital-7", 20)  # Fonte grande de 7-segment (ajuste o tamanho)
        if not counter_font.exactMatch():  # Fallback se a fonte não estiver disponível
            counter_font = QFont("Courier", 20, QFont.Bold)
        self.counter_label.setFont(counter_font)
        self.counter_label.setStyleSheet("color: white;")  # Cor do texto (ajuste conforme o fundo)
        # Posiciona no centro
        counter_width = 150  # Ajuste conforme o tamanho da fonte
        counter_height = 50
        self.counter_label.setGeometry(
            (self.width() - counter_width) // 2,
            (self.height() - counter_height) // 2,
            counter_width,
            counter_height
        )

        # --- ÁREAS DOS BOTÕES (TRANSPARENTES, SEM TEXTO OU GRÁFICOS - APENAS ÁREAS CLICÁVEIS) ---
        # Use background semi-transparente para depuração; mude transparency para 0 para invisível

        # Área Plus
        self.btn_plus_area = QLabel(self)
        self.btn_plus_area.setStyleSheet(f"""
            background-color: rgba(255, 255, 255, {self.button_transparency});
            border-radius: {self.plus_button_width // 2}px;
        """)
        self.btn_plus_area.setFixedSize(self.plus_button_width, self.plus_button_height)
        self.btn_plus_area.move(self.plus_button_x, self.plus_button_y)
        self.btn_plus_area.mousePressEvent = self.on_plus_clicked

        # Área Minus
        self.btn_minus_area = QLabel(self)
        self.btn_minus_area.setStyleSheet(f"""
            background-color: rgba(255, 255, 255, {self.button_transparency});
            border-radius: {self.minus_button_width // 2}px;
        """)
        self.btn_minus_area.setFixedSize(self.minus_button_width, self.minus_button_height)
        self.btn_minus_area.move(self.minus_button_x, self.minus_button_y)
        self.btn_minus_area.mousePressEvent = self.on_minus_clicked

        # Área Copy
        self.btn_copy_area = QLabel(self)
        self.btn_copy_area.setStyleSheet(f"""
            background-color: rgba(255, 255, 255, {self.button_transparency});
            border-radius: {self.copy_button_width // 2}px;
        """)
        self.btn_copy_area.setFixedSize(self.copy_button_width, self.copy_button_height)
        self.btn_copy_area.move(self.copy_button_x, self.copy_button_y)
        self.btn_copy_area.mousePressEvent = self.on_copy_clicked

        # Área Close
        self.btn_close_area = QLabel(self)
        self.btn_close_area.setStyleSheet(f"""
            background-color: rgba(255, 255, 255, {self.button_transparency});
            border-radius: {self.close_button_width // 2}px;
        """)
        self.btn_close_area.setFixedSize(self.close_button_width, self.close_button_height)
        self.btn_close_area.move(self.close_button_x, self.close_button_y)
        self.btn_close_area.mousePressEvent = self.on_close_clicked

    # --- EVENTOS DE ARRASTE ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Verifica se o clique não foi em uma das áreas dos botões
            if not self.is_click_on_button_area(event.pos()):
                self.initial_pos = event.globalPosition().toPoint() - self.pos()
                event.accept()
            else:
                event.ignore()  # Permite que o evento seja processado pelo widget do botão
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.initial_pos is not None and event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.initial_pos)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.initial_pos = None
        super().mouseReleaseEvent(event)

    def is_click_on_button_area(self, pos):
        # Verifica se a posição do clique está dentro de alguma área de botão
        return (self.btn_plus_area.geometry().contains(pos) or
                self.btn_minus_area.geometry().contains(pos) or
                self.btn_copy_area.geometry().contains(pos) or
                self.btn_close_area.geometry().contains(pos))

    # --- FUNÇÕES DOS BOTÕES ---
    def on_plus_clicked(self, event):
        self.counter = min(self.counter_max, self.counter + 1)
        self.update_counter()
        print("Aumentar clicado! Contador:", self.counter)

    def on_minus_clicked(self, event):
        self.counter = max(self.counter_min, self.counter - 1)
        self.update_counter()
        print("Diminuir clicado! Contador:", self.counter)

    def on_copy_clicked(self, event):
        clipboard = QApplication.clipboard()
        clipboard.setText(str(self.counter))
        print("Copiar clicado! Valor copiado:", self.counter)

    def on_close_clicked(self, event):
        print("Fechar clicado!")
        self.close()

    def update_counter(self):
        self.counter_label.setText(f"{self.counter:04d}")

# --- EXECUÇÃO DA APLICAÇÃO ---
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Crie uma imagem de fundo temporária se circle.png não existir para testar
    # REMOVA ESTE BLOCO SE VOCÊ JÁ TEM SEU circle.png
    try:
        with open("circle.png", "rb") as f:
            pass
    except FileNotFoundError:
        print("circle.png não encontrado. Criando um substituto temporário.")
        temp_pixmap = QPixmap(200, 200)
        temp_pixmap.fill(Qt.transparent)
        painter = QPainter(temp_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QColor("#78a9ff"))  # Borda clara
        painter.setBrush(QColor("#4c8df5"))  # Preenchimento
        painter.drawEllipse(0, 0, 200, 200)
        painter.end()
        temp_pixmap.save("circle.png")
    # FIM DO BLOCO DE CRIAÇÃO TEMPORÁRIA

    gadget = SuperGummyGadget()
    gadget.show()
    sys.exit(app.exec())