# Main.py

# Importa os módulos necessários do PySide6 para a interface gráfica.
import sys # Usado para sair da aplicação.
from PySide6.QtWidgets import (QApplication, QWidget, QLabel, QComboBox, 
                               QPushButton, QVBoxLayout, QHBoxLayout, QFrame) # Widgets e layouts.
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont # Para imagens, pintura, cores e fontes.
from PySide6.QtCore import Qt, QSize # Para alinhamentos, tamanhos, etc.

# Índice de Telas e Containers:
# Esta lista servirá como um índice para todas as telas ou containers que desenvolvermos.
# À medida que criarmos novas interfaces ou seções lógicas, vamos adicioná-las aqui.
indice_telas_containers = [
    "- Tela de Login", # Adiciona a Tela de Login ao índice.
    # Exemplo: "- Container de Cadastro de Transações",
]

# Classe principal da janela de Login.
class LoginWindow(QWidget): # Herda de QWidget, a classe base para todos os objetos de interface do usuário.
    def __init__(self):
        super().__init__() # Chama o construtor da classe pai (QWidget).
        self.largura_janela = 940
        self.altura_janela = 940
        self.caminho_imagem_fundo = "Images/Fundo.png" # Caminho relativo para a imagem
        self.imagem_fundo = None # Atributo para armazenar o QPixmap da imagem de fundo

        self.init_ui() # Chama o método para inicializar a interface do usuário.

    def init_ui(self):
        # Configurações da janela principal.
        self.setWindowTitle("Lucky Financial Assistant - Login") # Define o título da janela.
        self.setFixedSize(self.largura_janela, self.altura_janela) # Define um tamanho fixo para a janela.

        # Carrega a imagem de fundo.
        self.imagem_fundo = QPixmap(self.caminho_imagem_fundo) # Cria um QPixmap a partir do arquivo de imagem.
        if self.imagem_fundo.isNull(): # Verifica se a imagem foi carregada corretamente.
            print(f"Erro: A imagem de fundo '{self.caminho_imagem_fundo}' não foi encontrada ou não pôde ser carregada.")
            # Define uma cor de fundo padrão caso a imagem falhe ao carregar.
            self.setStyleSheet("background-color: #2b2b2b;") # Um cinza escuro.
        
        # Layout principal para posicionar o conteúdo de login.
        # Usaremos fatores de stretch para empurrar o container de login para a posição vertical desejada.
        main_layout = QVBoxLayout(self) # Cria um layout vertical para a janela principal.
        # Não usaremos mais o alinhamento central geral para o main_layout, pois controlaremos a posição com stretch.
        self.setLayout(main_layout) # Define este como o layout da janela.

        # Adiciona um espaçador flexível no topo para empurrar o container de login para baixo.
        # A proporção de 6:1 (aproximadamente) com o stretch abaixo deve posicionar o conteúdo perto de 720px.
        main_layout.addStretch(6) 

        # Container para os elementos de login (para aplicar margens e centralização).
        # Este QWidget não terá um layout próprio, mas será posicionado pelo main_layout.
        # Seus filhos (label, combobox, button) usarão um layout interno.
        login_container_widget = QWidget(self) # Cria um widget container.
        # Para que o login_container_widget não cubra a imagem de fundo com uma cor sólida:
        login_container_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        login_container_widget.setStyleSheet("background-color: transparent;")
        login_elements_layout = QVBoxLayout(login_container_widget) # Layout para os elementos dentro do container.
        # Ajusta as margens internas. A margem superior é menor, pois o posicionamento principal vem do stretch no main_layout.
        login_elements_layout.setContentsMargins(20, 20, 20, 20) 
        login_elements_layout.setAlignment(Qt.AlignmentFlag.AlignCenter) # Alinha os elementos ao centro.

        # Frame para agrupar "Usuário:" e ComboBox horizontalmente.
        user_input_frame = QWidget(login_container_widget) # Cria um widget para o input do usuário.
        user_input_frame.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        user_input_frame.setStyleSheet("background-color: transparent;")
        user_input_layout = QHBoxLayout(user_input_frame) # Layout horizontal para este frame.
        user_input_layout.setContentsMargins(0,0,0,0) # Sem margens internas.
        user_input_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Rótulo "Usuário:".
        self.label_usuario = QLabel("Usuário:", user_input_frame) # Cria um QLabel.
        self.label_usuario.setFont(QFont("Arial", 16)) # Define a fonte.
        self.label_usuario.setStyleSheet("color: white; background-color: transparent;") # Cor do texto e fundo transparente.
        user_input_layout.addWidget(self.label_usuario) # Adiciona ao layout horizontal.

        # Caixa de seleção (ComboBox) para os usuários.
        self.combo_usuario = QComboBox(user_input_frame) # Cria um QComboBox.
        usuarios_cadastrados = ["Selecione"] # Valores de exemplo.
        self.combo_usuario.addItems(usuarios_cadastrados) # Adiciona os itens.
        # Largura mínima da caixa de seleção reduzida.
        self.combo_usuario.setMinimumWidth(160) # Define uma largura mínima.
        self.combo_usuario.setFont(QFont("Arial", 12)) # Define a fonte.
        # Estilização do ComboBox via QSS (Qt Style Sheets).
        self.combo_usuario.setStyleSheet("""
            QComboBox {
                border: 1px solid #565B5E;
                border-radius: 10px;
                padding: 5px;
                background-color: #3E3E3E; /* Cor de fundo escura, não transparente */
                color: white;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: #565B5E;
                border-left-style: solid;
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
            }
            QComboBox QAbstractItemView { /* Estilo para a lista dropdown */
                background-color: #3E3E3E;
                color: white;
                selection-background-color: #2196F3; /* Azul para item selecionado */
            }
        """)
        user_input_layout.addWidget(self.combo_usuario) # Adiciona ao layout horizontal.

        login_elements_layout.addWidget(user_input_frame) # Adiciona o frame de input ao layout vertical.

        # Adiciona um espaçamento vertical entre o frame de input do usuário e o botão Iniciar.
        login_elements_layout.addSpacing(30) # Você pode ajustar o valor '30' para mais ou menos espaço.

        # Botão "INICIAR".
        self.button_iniciar = QPushButton("INICIAR", login_container_widget) # Cria um QPushButton.
        # Dimensões do botão reduzidas.
        self.button_iniciar.setMinimumHeight(35) # Define altura mínima.
        self.button_iniciar.setMinimumWidth(180) # Define largura mínima.
        self.button_iniciar.setFont(QFont("Arial", 16, QFont.Weight.Bold)) # Define a fonte.
        # Estilização do botão via QSS.
        self.button_iniciar.setStyleSheet("""
            QPushButton {
                background-color: #E912A2; /* Rosa */
                color: white;
                border-radius: 15px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #8C15BD; /* Azul */
            }
            QPushButton:pressed {
                background-color: #1C7ECE; /* Azul um pouco mais escuro ao pressionar */
            }
        """)
        login_elements_layout.addWidget(self.button_iniciar, alignment=Qt.AlignmentFlag.AlignCenter) # Adiciona ao layout vertical, centralizado.
        # Removemos o stretch interno do login_elements_layout para que o container se ajuste ao conteúdo.

        main_layout.addWidget(login_container_widget) # Adiciona o container de login ao layout principal da janela.
        main_layout.addStretch(1) # Adiciona um espaçador flexível menor abaixo do container de login.

    # Sobrescreve o método paintEvent para desenhar a imagem de fundo.
    def paintEvent(self, event):
        painter = QPainter(self) # Cria um objeto QPainter para desenhar na janela.
        if self.imagem_fundo and not self.imagem_fundo.isNull():
            # Desenha a imagem de fundo, escalonada para preencher a janela.
            painter.drawPixmap(self.rect(), self.imagem_fundo)
        else:
            # Se a imagem não carregou, preenche com uma cor sólida (alternativa ao stylesheet).
            painter.fillRect(self.rect(), QColor("#2b2b2b"))
        super().paintEvent(event) # Chama o paintEvent da classe pai.

def main():
    # Cria a aplicação Qt.
    app = QApplication(sys.argv) # sys.argv permite argumentos de linha de comando.

    # Cria e exibe a janela de login.
    login_window = LoginWindow() # Instancia a janela de login.
    login_window.show() # Torna a janela visível.

    # Inicia o loop de eventos da aplicação.
    sys.exit(app.exec()) # app.exec() inicia o loop, sys.exit garante uma saída limpa.

# Ponto de entrada do script: verifica se o arquivo está sendo executado diretamente.
if __name__ == "__main__":
    main()
