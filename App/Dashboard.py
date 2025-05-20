import customtkinter
import tkinter as tk
from PIL import Image # Adicionado para carregar a imagem do logo
import datetime # Para obter o ano atual 
from form_cadastro import FormCadastroWindow # Importa a nova janela de formulário de cadastro

from form_transacao import FormTransacaoWindow # Importa a nova janela de formulário de transação
# Importa as funções do nosso novo módulo de banco de dados (se necessário no futuro para o Dashboard).
import Database # Usando 'Database' com D maiúsculo conforme seu Main.py

# Definições de fonte padrão para o Dashboard
FONTE_FAMILIA = "Segoe UI"
FONTE_TITULO_GRANDE = (FONTE_FAMILIA, 24, "bold")
FONTE_TITULO_MEDIO = (FONTE_FAMILIA, 16, "bold")
FONTE_NORMAL_BOLD = (FONTE_FAMILIA, 13, "bold")
FONTE_NORMAL = (FONTE_FAMILIA, 13)
FONTE_PEQUENA = (FONTE_FAMILIA, 11)
FONTE_USUARIO_LOGADO = (FONTE_FAMILIA, 10, "italic")
FONTE_BOTAO_ACAO = (FONTE_FAMILIA, 13, "bold")

COR_CONTAINER_INTERNO = "#222222" # Cinza mais escuro para containers internos, próximo ao fundo da janela
class Dashboard(customtkinter.CTk):
    def __init__(self, user_id=None): # Adiciona user_id como parâmetro opcional.
        super().__init__()
        self.current_user_id = user_id # Armazena o ID do usuário.
        self.form_cadastro_window = None # Referência para a janela de cadastro
        self.form_transacao_window = None # Referência para a janela de transação
        self.request_restart_on_close = False # Sinalizador para reinício
        # self.main_app_window = master # Removido, pois 'master' não é passado e a lógica de voltar já funciona
        print(f"Dashboard iniciado para o usuário ID: {self.current_user_id}")
        
        # Configure window
        self.title("Gestão Financeira - Dashboard")
        self.geometry("1024x768") # Set a default window size
        self.configure(fg_color="#1c1c1c") # Define o fundo da janela principal do Dashboard
        customtkinter.set_appearance_mode("Dark") # Forçar tema escuro para um visual mais "high-tech"
        customtkinter.set_default_color_theme("blue") # Or choose another theme

        # Set grid layout for the main window (1 column for title, 2 columns below title)
        self.grid_columnconfigure(0, weight=1) # Title column spans the width
        self.grid_columnconfigure(1, weight=1) # Second column for pie chart container
        self.grid_rowconfigure(0, weight=0) # Title row
        self.grid_rowconfigure(1, weight=0) # Top months container row
        self.grid_rowconfigure(2, weight=1) # Row for list and pie chart (takes remaining space)
        self.grid_rowconfigure(3, weight=0) # New row for action buttons and logo


        # --- Header Frame (Title and Year Selector) ---
        self.header_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="ew")

        self.title_label = customtkinter.CTkLabel(self.header_frame, text="Dashboard", font=FONTE_TITULO_GRANDE)
        self.title_label.pack(side="left", anchor="w")

        # Year Selector elements
        # Frame para agrupar o nome do usuário e o seletor de ano
        user_year_frame = customtkinter.CTkFrame(self.header_frame, fg_color="transparent")
        user_year_frame.pack(side="right", anchor="ne") # Alinha à direita e ao topo do header_frame

        self.logged_user_label = customtkinter.CTkLabel(user_year_frame, text="", font=FONTE_USUARIO_LOGADO, text_color="gray60")
        self.logged_user_label.pack(side="top", anchor="e", pady=(0,5))
        self.year_selector_frame = customtkinter.CTkFrame(self.header_frame, fg_color="transparent")
        self.year_selector_frame.pack(side="right", anchor="e")

        self.year_label = customtkinter.CTkLabel(self.year_selector_frame, text="Ano Referência:", font=(FONTE_FAMILIA, 12))
        self.year_label.pack(side="left", padx=(0, 5))

        current_year = datetime.datetime.now().year
        # Gera uma lista de anos, por exemplo, 5 anos para trás e 2 para frente.
        year_options = [str(y) for y in range(current_year - 5, current_year + 3)]
        self.year_combobox = customtkinter.CTkComboBox(self.year_selector_frame, values=year_options, width=100, font=(FONTE_FAMILIA, 12), height=30)
        self.year_combobox.set(str(current_year)) # Define o ano atual como padrão
        self.year_combobox.pack(side="left")
        # Adicionar comando ao combobox se precisar reagir à mudança de ano:
        self.year_selector_frame.pack(in_=user_year_frame, side="bottom", anchor="e") # Adiciona o seletor de ano abaixo do nome do usuário
        self.load_logged_user_name()
        # self.year_combobox.configure(command=self.year_changed_event)

        # --- Top Container for Months ---
        self.months_container_frame = customtkinter.CTkFrame(self, corner_radius=10, border_width=2, fg_color=COR_CONTAINER_INTERNO)
        self.months_container_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="nsew") # Span across two columns

        # Configure grid for months container (2 rows, 6 columns)
        self.months_container_frame.grid_rowconfigure((0, 1), weight=1)
        for i in range(6):
            self.months_container_frame.grid_columnconfigure(i, weight=1)

        # Add month placeholders
        months = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                  "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

        for i, month in enumerate(months):
            row = 0 if i < 6 else 1
            col = i % 6
            # Using a frame for each month allows adding more widgets inside later (e.g., a small chart, numbers)
            month_frame = customtkinter.CTkFrame(self.months_container_frame, corner_radius=5, fg_color="#282828") # Um pouco mais claro que o COR_CONTAINER_INTERNO
            month_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

            month_label = customtkinter.CTkLabel(month_frame, text=month, font=FONTE_NORMAL_BOLD)
            month_label.pack(padx=5, pady=5) # Center the month name

            # Add placeholder for data within the month frame
            data_placeholder = customtkinter.CTkLabel(month_frame, text="R$ 0,00\nData Here", font=FONTE_PEQUENA, text_color="gray50")
            data_placeholder.pack(padx=5, pady=0)


        # --- Left Container for List Items ---
        self.list_container_frame = customtkinter.CTkFrame(self, corner_radius=10, border_width=2, fg_color=COR_CONTAINER_INTERNO)
        self.list_container_frame.grid(row=2, column=0, padx=(20,10), pady=(10, 20), sticky="nsew") # Occupies the first column in row 2

        # Add list items (example)
        list_items_title = customtkinter.CTkLabel(self.list_container_frame, text="Categorias:", font=FONTE_TITULO_MEDIO)
        list_items_title.pack(padx=10, pady=(10, 5), anchor="w") # Anchor west

        list_items = ["Cat1 R$ 0,00", "Cat2 R$ 0,00", "Cat3 R$ 0,00", "Cat4 R$ 0,00"]
        for item in list_items:
            item_label = customtkinter.CTkLabel(self.list_container_frame, text=item, font=FONTE_NORMAL)
            item_label.pack(padx=20, pady=2, anchor="w") # Anchor west, add some padding


        # --- Bottom Container for Pie Chart ---
        self.pie_chart_container_frame = customtkinter.CTkFrame(self, corner_radius=10, border_width=2, fg_color=COR_CONTAINER_INTERNO)
        self.pie_chart_container_frame.grid(row=2, column=1, padx=(10,20), pady=(10, 20), sticky="nsew") # Occupies the second column in row 2

        # Placeholder for the pie chart
        pie_chart_placeholder_label = customtkinter.CTkLabel(self.pie_chart_container_frame, text="Gráfico de Pizza Placeholder", font=FONTE_TITULO_MEDIO)
        pie_chart_placeholder_label.pack(expand=True, fill="both", padx=20, pady=20) # Center placeholder text

        # --- Bottom Container for Action Buttons and Logo ---
        self.actions_container_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent") # Sem cantos e transparente
        # Aumentado o pady inferior para criar mais espaço abaixo dos botões.
        self.actions_container_frame.grid(row=3, column=0, columnspan=2, padx=0, pady=(10,20), sticky="nsew")

        # Frame interno para centralizar os botões
        buttons_inner_frame = customtkinter.CTkFrame(self.actions_container_frame, fg_color="transparent")
        buttons_inner_frame.pack(expand=True, anchor="center", pady=10) # Centraliza o frame dos botões

        # Configure grid for actions container (1 row, many columns for flexibility or use pack)
        # Usaremos pack para os botões e place para o logo

        # Botões de Ação
        button_font = FONTE_BOTAO_ACAO
        button_width = 150
        button_height = 35 # Altura padrão dos botões
        button_corner_radius = 17 # Para cantos bem arredondados, ~metade da altura
        
        # Define as cores para os botões
        cor_botao_cinza = "gray30"  # Um cinza mais escuro do customtkinter
        cor_botao_azul_hover = "#2196F3" # O mesmo azul usado anteriormente para hover

        # Botão Voltar (agora na parte inferior com o mesmo estilo dos outros botões de ação)
        self.back_button = customtkinter.CTkButton(buttons_inner_frame, text="< Voltar",
                                                   command=self.go_back_to_main,
                                                   font=button_font, width=button_width, height=button_height, corner_radius=button_corner_radius,
                                                   fg_color=cor_botao_cinza, hover_color=cor_botao_azul_hover)
        self.back_button.pack(side="left", padx=5)

        # Movendo "Cadastrar Despesa/Provento" para ser o primeiro botão da lista
        self.transaction_button = customtkinter.CTkButton(buttons_inner_frame, text="Cadastrar Despesa/Provento",
                                                         font=button_font, width=button_width, height=button_height, corner_radius=button_corner_radius,
                                                         fg_color=cor_botao_cinza, hover_color=cor_botao_azul_hover,
                                                         command=lambda: self.open_form_transacao("Despesa")) # Abre como Despesa por padrão
        self.transaction_button.pack(side="left", padx=5)

        self.details_button = customtkinter.CTkButton(buttons_inner_frame, text="Detalhes",
                                                      font=button_font, width=button_width, height=button_height, corner_radius=button_corner_radius,
                                                      fg_color=cor_botao_cinza, hover_color=cor_botao_azul_hover)
        self.details_button.pack(side="left", padx=5) # Removido pady daqui, já está no buttons_inner_frame

        self.new_category_button = customtkinter.CTkButton(buttons_inner_frame, text="Nova Categoria",
                                                           font=button_font, width=button_width, height=button_height, corner_radius=button_corner_radius,
                                                                   fg_color=cor_botao_cinza, hover_color=cor_botao_azul_hover,
                                                           command=self.open_form_cadastro) # Adiciona comando
        self.new_category_button.pack(side="left", padx=5)

        # Logo como Marca d'água
        try:
            logo_image_path = "Images/Logo.png"
            pil_logo_image = Image.open(logo_image_path)
            # Defina o tamanho desejado para o logo. Ajuste conforme necessário.
            self.logo_ctk_image = customtkinter.CTkImage(pil_logo_image, size=(60, 60)) 
            
            self.logo_label = customtkinter.CTkLabel(self.actions_container_frame, image=self.logo_ctk_image, text="")
            # Posiciona o logo no canto inferior direito do actions_container_frame
            self.logo_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-5) # x e y para um pequeno offset da borda
        except FileNotFoundError:
            print(f"Erro: Imagem do logo '{logo_image_path}' não encontrada.")
        except Exception as e:
            print(f"Erro ao carregar a imagem do logo: {e}")

    def open_form_cadastro(self):
        if self.form_cadastro_window is None or not self.form_cadastro_window.winfo_exists(): # Verifica se a janela não existe ou foi fechada
            self.form_cadastro_window = FormCadastroWindow(master=self, current_user_id=self.current_user_id) # Cria uma nova instância da janela de cadastro
            self.form_cadastro_window.focus() # Traz a nova janela para o foco
        else:
            self.form_cadastro_window.focus() # Se a janela já existe, apenas a traz para o foco

    def open_form_transacao(self, tipo_transacao):
        if self.form_transacao_window is None or not self.form_transacao_window.winfo_exists():
            self.form_transacao_window = FormTransacaoWindow(master=self, current_user_id=self.current_user_id, tipo_transacao=tipo_transacao)
            self.form_transacao_window.focus()
        else:
            self.form_transacao_window.focus()

    def load_logged_user_name(self):
        if self.current_user_id:
            user_name = Database.get_user_name_by_id(self.current_user_id)
            if user_name:
                self.logged_user_label.configure(text=f"Usuário: {user_name}")
            else:
                self.logged_user_label.configure(text="Usuário: Desconhecido")
        else:
            self.logged_user_label.configure(text="Nenhum usuário logado")

    def go_back_to_main(self):
        """Fecha a janela do Dashboard e sinaliza para a janela principal (Login) reaparecer."""
        print("Botão Voltar clicado no Dashboard. Solicitando reinício da aplicação.")
        self.request_restart_on_close = True
        self.destroy() # Isso fará com que o mainloop() no Main.py continue.

    # def year_changed_event(self, selected_year):
    #     print(f"Ano selecionado: {selected_year}")
    #     # Aqui você adicionaria a lógica para recarregar os dados do dashboard para o ano selecionado.

if __name__ == "__main__":
    app = Dashboard(user_id="test_user_01") # Passa um user_id para teste
    app.mainloop()