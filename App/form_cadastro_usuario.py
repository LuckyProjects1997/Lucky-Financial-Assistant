# form_cadastro_usuario.py
import customtkinter
import uuid # Para gerar IDs únicos
from . import Database # Usando 'Database' com D maiúsculo conforme seu Main.py

# Definições de fonte padrão para o Formulário de Cadastro de Usuário
FONTE_FAMILIA = "Segoe UI"
FONTE_TITULO_FORM = (FONTE_FAMILIA, 18, "bold")
FONTE_LABEL_FORM = (FONTE_FAMILIA, 13)
FONTE_INPUT_FORM = (FONTE_FAMILIA, 13)
FONTE_BOTAO_FORM = (FONTE_FAMILIA, 13, "bold")
BOTAO_CORNER_RADIUS = 17 # Para cantos bem arredondados
BOTAO_FG_COLOR = "gray30" # Cor padrão dos botões (igual ao Dashboard)
BOTAO_HOVER_COLOR = "#2196F3" # Cor hover dos botões (igual ao Dashboard)
BOTAO_HEIGHT = 35

class FormCadastroUsuarioWindow(customtkinter.CTkToplevel):
    def __init__(self, master=None, on_close_callback=None):
        super().__init__(master)
        self.title("Cadastrar Usuário")
        self.geometry("400x250") # Tamanho inicial ajustado
        self.configure(fg_color="#1c1c1c") # Define o fundo da janela
        self.lift() # Traz a janela para frente
        self.attributes("-topmost", True) # Mantém no topo temporariamente
        self.grab_set() # Impede interações com a janela pai até esta ser fechada

        self.minsize(350, 200) # Define um tamanho mínimo

        self.on_close_callback = on_close_callback # Callback a ser chamado quando a janela for fechada

        self._setup_ui()

    def _setup_ui(self):
        # --- Frame Principal ---
        main_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1) # Para centralizar o conteúdo

        title_label = customtkinter.CTkLabel(main_frame, text="Cadastrar Novo Usuário", font=FONTE_TITULO_FORM)
        title_label.grid(row=0, column=0, pady=(0, 20), sticky="ew")

        # Nome do Usuário
        user_name_label = customtkinter.CTkLabel(main_frame, text="Nome do Usuário:", font=FONTE_LABEL_FORM)
        user_name_label.grid(row=1, column=0, pady=(5,2), padx=10, sticky="w")
        self.user_name_entry = customtkinter.CTkEntry(main_frame, placeholder_text="Ex: João Silva", height=35, font=FONTE_INPUT_FORM)
        self.user_name_entry.grid(row=2, column=0, sticky="ew", padx=10, pady=(0,15))

        # Frame para os botões de ação (Salvar e Fechar)
        action_buttons_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        action_buttons_frame.grid(row=3, column=0, pady=(10,0), sticky="ew")
        action_buttons_frame.grid_columnconfigure(0, weight=1) # Espaço à esquerda
        action_buttons_frame.grid_columnconfigure(1, weight=0) # Botão Salvar
        action_buttons_frame.grid_columnconfigure(2, weight=0) # Botão Fechar
        action_buttons_frame.grid_columnconfigure(3, weight=1) # Espaço à direita

        # Botão Salvar
        save_user_button = customtkinter.CTkButton(action_buttons_frame, text="Salvar", command=self.save_new_user,
                                                   height=BOTAO_HEIGHT, font=FONTE_BOTAO_FORM, corner_radius=BOTAO_CORNER_RADIUS,
                                                   fg_color=BOTAO_FG_COLOR, hover_color=BOTAO_HOVER_COLOR)
        save_user_button.grid(row=0, column=1, padx=5)

        # Botão Fechar
        close_button = customtkinter.CTkButton(action_buttons_frame, text="Fechar", command=self.handle_close_action, height=BOTAO_HEIGHT, font=FONTE_BOTAO_FORM, corner_radius=BOTAO_CORNER_RADIUS, fg_color="gray50", hover_color="gray40")
        close_button.grid(row=0, column=2, padx=5)

    def save_new_user(self):
        user_name = self.user_name_entry.get().strip()
        if not user_name:
            print("Nome do usuário não pode ser vazio.") # TODO: Mostrar alerta na GUI
            return

        new_user_id = str(uuid.uuid4())
        print(f"Tentando SALVAR novo usuário: {user_name}, ID Gerado: {new_user_id}")
        success = Database.add_user(new_user_id, user_name)

        if success:
            print("Novo usuário salvo com sucesso!") # TODO: Mostrar alerta na GUI
            self.user_name_entry.delete(0, customtkinter.END)
        else:
            print("Falha ao salvar novo usuário.") # TODO: Mostrar alerta na GUI

    def handle_close_action(self):
        if self.on_close_callback:
            self.on_close_callback()
        self.destroy()