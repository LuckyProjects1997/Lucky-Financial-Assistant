# Main.py

# Importa os módulos necessários do PySide6 para a interface gráfica.
import sys # Usado para sair da aplicação.
import os # Para interagir com o sistema operacional (reiniciar)
import subprocess # Para iniciar um novo processo (reiniciar)
from PySide6.QtWidgets import (QApplication, QWidget, QLabel, QComboBox, QMessageBox,
                               # Adicionado tk para tk.TclError
                               QPushButton, QVBoxLayout, QHBoxLayout, QFrame) # Widgets e layouts.
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont # Para imagens, pintura, cores e fontes.
from PySide6.QtCore import Qt, QSize # Para alinhamentos, tamanhos, etc.

# Importa a classe Dashboard do arquivo Dashboard.py
from Dashboard import Dashboard
# Importa a janela de formulário de cadastro
# from form_cadastro import FormCadastroWindow # Removido
from form_cadastro_usuario import FormCadastroUsuarioWindow # Importa o formulário de usuário
# Importa as funções do nosso novo módulo de banco de dados.
import tkinter as tk # Adicionado para tk.TclError
import Database

# Índice de Telas e Containers:
# Esta lista servirá como um índice para todas as telas ou containers que desenvolvermos.
# À medida que criarmos novas interfaces ou seções lógicas, vamos adicioná-las aqui.
indice_telas_containers = [
    "- Tela de Login", # Adiciona a Tela de Login ao índice.
    # Exemplo: "- Container de Cadastro de Transações",
    "- Tela Dashboard", # Adiciona a Tela Dashboard ao índice.
]

# Classe principal da janela de Login.
class LoginWindow(QWidget): # Herda de QWidget, a classe base para todos os objetos de interface do usuário.
    # Define a família de fontes padrão para esta janela
    FONTE_FAMILIA = "Segoe UI"
    FONTE_TAMANHO_LABEL = 14
    FONTE_TAMANHO_COMBO = 12
    FONTE_TAMANHO_BOTAO = 14
    SHOULD_RESTART_APP = False # Sinalizador de classe para reinício
    def __init__(self):
        super().__init__() # Chama o construtor da classe pai (QWidget).
        self.largura_janela = 940
        self.altura_janela = 940
        self.caminho_imagem_fundo = "Images/Fundo.png" # Caminho relativo para a imagem
        self.imagem_fundo = None # Atributo para armazenar o QPixmap da imagem de fundo
        self.original_imagem_fundo = None # Atributo para armazenar a imagem de fundo original não escalada

        self.dashboard_window = None # Referência para a janela do dashboard
        self.form_cadastro_win_ref = None # Referência para a janela de cadastro

        # Inicializa o banco de dados e as tabelas.
        Database.create_tables()
        self.init_ui() # Chama o método para inicializar a interface do usuário.

    def init_ui(self):
        # Configurações da janela principal.
        self.setWindowTitle("Lucky Financial Assistant - Login") # Define o título da janela.
        # Define o tamanho inicial da janela.
        self.resize(self.largura_janela, self.altura_janela)
        # Define um tamanho mínimo para a janela para garantir que os elementos não fiquem muito espremidos.
        self.setMinimumSize(600, 500) # Você pode ajustar esses valores.

        # Carrega a imagem de fundo original.
        self.original_imagem_fundo = QPixmap(self.caminho_imagem_fundo)
        if self.original_imagem_fundo.isNull(): # Verifica se a imagem foi carregada corretamente.
            print(f"Erro: A imagem de fundo '{self.caminho_imagem_fundo}' não foi encontrada ou não pôde ser carregada.")
            # Define uma cor de fundo padrão caso a imagem falhe ao carregar.
            self.setStyleSheet("background-color: #1c1c1c;") # Cinza quase preto.
            self.imagem_fundo = None # Garante que imagem_fundo seja None se a original não carregar
        else:
            # Escala a imagem de fundo para o tamanho inicial da janela.
            self.imagem_fundo = self.original_imagem_fundo.scaled(self.size(), Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
        
        # Layout principal para posicionar o conteúdo de login.
        # Usaremos fatores de stretch para empurrar o container de login para a posição vertical desejada.
        main_layout = QVBoxLayout(self) # Cria um layout vertical para a janela principal.
        # Não usaremos mais o alinhamento central geral para o main_layout, pois controlaremos a posição com stretch.
        self.setLayout(main_layout) # Define este como o layout da janela.

        # Adiciona um espaçador flexível no topo para empurrar o container de login para baixo.
        # A proporção de 6:1 (aproximadamente) com o stretch abaixo deve posicionar o conteúdo perto de 720px.
        main_layout.addStretch(7) # Aumentado de 6 para 7 para mover um pouco mais para baixo

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
        self.label_usuario.setFont(QFont(self.FONTE_FAMILIA, self.FONTE_TAMANHO_LABEL)) # Define a fonte.
        self.label_usuario.setStyleSheet("color: white; background-color: transparent;") # Cor do texto e fundo transparente.
        user_input_layout.addWidget(self.label_usuario) # Adiciona ao layout horizontal.

        # Caixa de seleção (ComboBox) para os usuários.
        self.combo_usuario = QComboBox(user_input_frame) # Cria um QComboBox.
        self.combo_usuario.setMinimumWidth(180) # Ajuste da largura mínima.
        self.combo_usuario.setFont(QFont(self.FONTE_FAMILIA, self.FONTE_TAMANHO_COMBO)) # Define a fonte.
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
        
        # Carrega os usuários do banco de dados para a ComboBox.
        self.load_users_into_combobox()

        login_elements_layout.addWidget(user_input_frame) # Adiciona o frame de input ao layout vertical.

        # Adiciona um espaçamento vertical entre o frame de input do usuário e o botão Iniciar.
        login_elements_layout.addSpacing(15) # Ajustado para aproximar o botão Iniciar do campo de usuário.

        # Botão "INICIAR".
        self.button_iniciar = QPushButton("INICIAR", login_container_widget) # Cria um QPushButton.
        # Dimensões do botão reduzidas.
        self.button_iniciar.setMinimumHeight(35) # Define altura mínima.
        self.button_iniciar.setMinimumWidth(180) # Define largura mínima.
        self.button_iniciar.setFont(QFont(self.FONTE_FAMILIA, self.FONTE_TAMANHO_BOTAO, QFont.Weight.Bold)) # Define a fonte.
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
        # Conecta o sinal clicked do botão ao método abrir_dashboard.
        self.button_iniciar.clicked.connect(self.abrir_dashboard)
        login_elements_layout.addWidget(self.button_iniciar, alignment=Qt.AlignmentFlag.AlignCenter) # Adiciona ao layout vertical, centralizado.

        # Link "Cadastrar"
        self.label_cadastrar = QLabel("Cadastrar")
        self.label_cadastrar.setFont(QFont(self.FONTE_FAMILIA, 11)) # Fonte um pouco menor
        self.label_cadastrar.setStyleSheet("""
            QLabel {
                color: #8ab4f8; /* Azul claro, similar a links */
                text-decoration: none; /* Sem sublinhado por padrão */
            }
            QLabel:hover {
                text-decoration: underline; /* Sublinhado ao passar o mouse */
            }
        """)
        self.label_cadastrar.setCursor(Qt.PointingHandCursor) # Muda o cursor para mãozinha
        self.label_cadastrar.mousePressEvent = self.abrir_formulario_cadastro_usuario # Conecta o clique
        login_elements_layout.addWidget(self.label_cadastrar, alignment=Qt.AlignmentFlag.AlignCenter)
        login_elements_layout.addSpacing(10) # Pequeno espaço abaixo do link
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
            painter.fillRect(self.rect(), QColor("#1c1c1c")) # Cinza quase preto
        super().paintEvent(event) # Chama o paintEvent da classe pai.

    def resizeEvent(self, event):
        """Chamado quando a janela é redimensionada."""
        # Redimensiona a imagem de fundo para o novo tamanho da janela, se a imagem original existir.
        if self.original_imagem_fundo and not self.original_imagem_fundo.isNull():
            self.imagem_fundo = self.original_imagem_fundo.scaled(event.size(), Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
        
        super().resizeEvent(event) # Chama o método da classe pai para processar o evento de redimensionamento.
        self.update() # Força um redesenho da janela para aplicar a imagem de fundo redimensionada.

    # Método para abrir a janela do Dashboard.
    def abrir_dashboard(self):
        # Obtém o ID do usuário selecionado na ComboBox.
        # O método currentData() retorna o dado associado ao item selecionado (que definimos como o ID do usuário).
        selected_user_id = self.combo_usuario.currentData()

        # Verifica se um usuário válido foi selecionado.
        if selected_user_id is None or self.combo_usuario.currentIndex() == 0: # O índice 0 é "Selecione o usuário"
            print("Nenhum usuário selecionado. Por favor, selecione um usuário para continuar.")
            QMessageBox.warning(self, "Seleção Inválida", "Por favor, selecione um usuário para continuar.")
            return # Não prossegue se nenhum usuário válido for selecionado.

        # Esconde a janela de login atual.
        self.hide()

        # Cria e exibe a janela do Dashboard.
        # O Dashboard (customtkinter) tem seu próprio loop de eventos (mainloop).
        try:
            print(f"Abrindo o Dashboard para o usuário ID: {selected_user_id}...")
            self.dashboard_window = Dashboard(user_id=selected_user_id) # Passa o ID do usuário para o Dashboard.
            self.dashboard_window.mainloop()    # Inicia o loop de eventos do customtkinter para o Dashboard.
        except Exception as e:
            print(f"Erro ao tentar abrir o Dashboard: {e}")
            self.show() # Se houver um erro, mostra a janela de login novamente.
        
        # Após o dashboard_window.mainloop() terminar
        should_restart = getattr(self.dashboard_window, 'request_restart_on_close', False)

        if should_restart:
            self.initiate_app_restart()
        else:
            # Se o Dashboard foi fechado normalmente (não pelo botão "Voltar" para reiniciar),
            # a LoginWindow também será fechada, terminando a aplicação.
            self.close()

    def initiate_app_restart(self):
        print("Iniciando o processo de reinício da aplicação...")
        LoginWindow.SHOULD_RESTART_APP = True
        QApplication.instance().quit() # Encerra o loop de eventos do PySide6
    def abrir_formulario_cadastro_usuario(self, event=None): # event é passado por mousePressEvent
        """Abre o formulário de cadastro de usuário."""
        self.hide() # Esconde a janela de login
        temp_ctk_root = None # Inicializa temp_ctk_root como None

        try:
            print("Abrindo formulário de cadastro...")
            import customtkinter # Importa aqui para evitar dependência no topo se não for usado
            
            temp_ctk_root = customtkinter.CTk() # Cria um root CTk temporário
            temp_ctk_root.withdraw() # Esconde o root temporário

            # Criamos uma referência mutável (lista) para temp_ctk_root
            # para que o callback possa modificá-la (definir como None após destroy)
            # Isso ajuda os blocos except a saberem se precisam limpar.
            active_temp_root_ref = [temp_ctk_root]

            # Função a ser chamada quando o formulário de cadastro for fechado
            def on_form_closed_callback():
                print("Formulário de cadastro fechado via callback.")
                if active_temp_root_ref[0] and active_temp_root_ref[0].winfo_exists():
                    active_temp_root_ref[0].destroy() # Destrói o root temporário
                active_temp_root_ref[0] = None # Sinaliza que foi tratado

            self.form_cadastro_win_ref = FormCadastroUsuarioWindow(master=active_temp_root_ref[0], on_close_callback=on_form_closed_callback)
            self.form_cadastro_win_ref.on_close_callback = on_form_closed_callback # Define o callback
            # Também lida com o fechamento pelo botão [X] da janela
            self.form_cadastro_win_ref.protocol("WM_DELETE_WINDOW", on_form_closed_callback)
            
            temp_ctk_root.mainloop() # Inicia o loop de eventos do CTk para o formulário

        except ImportError:
            print("CustomTkinter não está instalado. Não é possível abrir o formulário de cadastro.")
            QMessageBox.critical(self, "Erro de Importação", "CustomTkinter não está instalado.")
            # Limpa temp_ctk_root se foi criado antes do erro
            if active_temp_root_ref and active_temp_root_ref[0]:
                try:
                    if active_temp_root_ref[0].winfo_exists(): active_temp_root_ref[0].destroy()
                except tk.TclError: pass # Ignora se já foi destruído
                active_temp_root_ref[0] = None
        except Exception as e:
            print(f"Erro ao tentar abrir o formulário de cadastro: {e}")
            QMessageBox.critical(self, "Erro", f"Não foi possível abrir o formulário de cadastro:\n{e}")
            if active_temp_root_ref and active_temp_root_ref[0]:
                try:
                    if active_temp_root_ref[0].winfo_exists(): active_temp_root_ref[0].destroy()
                except tk.TclError: pass # Ignora se já foi destruído
                active_temp_root_ref[0] = None
        finally:
            # O mainloop de temp_ctk_root terminou, o que significa que foi destruído
            # (pelo callback ou por uma exceção e tratado no bloco except).
            # Não há necessidade de tentar destruir temp_ctk_root novamente aqui.
            print("Bloco finally executado após formulário de cadastro.")
            self.show() # Mostra a janela de login novamente
            self.load_users_into_combobox() # Recarrega os usuários, caso um novo tenha sido adicionado

    def load_users_into_combobox(self):
        """Busca usuários do banco de dados e os carrega na QComboBox."""
        print("Carregando usuários na ComboBox...")
        self.combo_usuario.clear() # Limpa itens existentes.
        
        users = Database.get_all_users() # Busca todos os usuários do banco.
        if not users:
            self.combo_usuario.addItem("     ", None) # Adiciona item placeholder se não houver usuários.
        else:
            self.combo_usuario.addItem("     Selecionar", None) # Adiciona um item inicial "Selecione".
            for user in users:
                # Adiciona o nome do usuário como texto e o ID como dado associado.
                self.combo_usuario.addItem(f"     {user['name']}", user["id"])
        print(f"{len(users)} usuários carregados.")

def main():
    # Cria a aplicação Qt.
    app = QApplication(sys.argv) # sys.argv permite argumentos de linha de comando.

    # Cria e exibe a janela de login.
    login_window = LoginWindow() # Instancia a janela de login.
    login_window.show() # Torna a janela visível.
    # Inicia o loop de eventos da aplicação.
    exit_code = app.exec() # app.exec() inicia o loop

    if LoginWindow.SHOULD_RESTART_APP:
        print("Reiniciando a aplicação...")
        python_executable = sys.executable
        script_path = os.path.abspath(__file__) # Obtém o caminho absoluto do script atual (Main.py)
        # Usar subprocess.Popen para iniciar um novo processo desanexado
        subprocess.Popen([python_executable, script_path])
        sys.exit(0) # Sai do processo atual
    else:
        sys.exit(exit_code) # Sai com o código de saída da aplicação

# Ponto de entrada do script: verifica se o arquivo está sendo executado diretamente.
if __name__ == "__main__":
    main()
