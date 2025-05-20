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
        self.months_list = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
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
        self.grid_rowconfigure(1, weight=0) # Row for month buttons
        self.grid_rowconfigure(2, weight=1) # Row for monthly expenses table (should expand)
        self.grid_rowconfigure(3, weight=1) # Row for current list and pie chart (takes remaining space)
        self.grid_rowconfigure(4, weight=0) # Row for "Resumo Anual" title
        self.grid_rowconfigure(5, weight=1) # Row for annual summary list and pie chart (takes remaining space)
        self.grid_rowconfigure(6, weight=0) # Row for action buttons and logo


        # --- Header Frame (Title and Year Selector) ---
        self.header_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="ew")

         # Container para informações do usuário (à direita)
        user_info_container = customtkinter.CTkFrame(self.header_frame, fg_color="transparent")
        user_info_container.pack(side="right", anchor="ne", padx=(20,0)) # Adicionado padx para separar do conteúdo à esquerda


        self.logged_user_label = customtkinter.CTkLabel(user_info_container, text="", font=FONTE_USUARIO_LOGADO, text_color="gray60")
        self.logged_user_label.pack(side="top", anchor="e", pady=(0,5))

        # Link "Sair"
        self.logout_label = customtkinter.CTkLabel(user_info_container, text="Sair", font=(FONTE_FAMILIA, 10, "underline"), text_color="#8ab4f8", cursor="hand2")
        self.logout_label.pack(side="top", anchor="e", pady=(0, 10))
        self.logout_label.bind("<Button-1>", self.handle_logout)
        self.load_logged_user_name() # Carrega o nome do usuário aqui


        # Container para o título e o seletor de ano (ocupa o espaço restante à esquerda)
        title_year_container = customtkinter.CTkFrame(self.header_frame, fg_color="transparent")
        # fill="x" e expand=True para que o title_year_container ocupe o espaço horizontal restante.
        # side="left" para que ele fique à esquerda do user_info_container.
        title_year_container.pack(side="left", fill="x", expand=True)

        self.title_label = customtkinter.CTkLabel(title_year_container, text="Dashboard", font=FONTE_TITULO_GRANDE)
        # anchor="w" para alinhar o texto à esquerda dentro do seu espaço. padx para espaçamento.
        self.title_label.pack(side="left", anchor="w", padx=(0, 30)) 

        # Year Selector elements
        self.year_selector_frame = customtkinter.CTkFrame(title_year_container, fg_color="transparent")
        self.year_selector_frame.pack(side="left", anchor="w") # Alinha à esquerda, ao lado do título
        



        self.year_label = customtkinter.CTkLabel(self.year_selector_frame, text="Ano Referência:", font=(FONTE_FAMILIA, 12))
        self.year_label.pack(side="left", padx=(0, 5))

        current_year = datetime.datetime.now().year
        year_options = [str(y) for y in range(current_year - 5, current_year + 3)]
        self.year_combobox = customtkinter.CTkComboBox(self.year_selector_frame, values=year_options, width=100, font=(FONTE_FAMILIA, 12), height=30)
        self.year_combobox.set(str(current_year)) # Define o ano atual como padrão
        self.year_combobox.pack(side="left")
        self.year_combobox.configure(command=self.year_changed_event)


        # --- Top Container for Months ---
        self.months_container_frame = customtkinter.CTkFrame(self, corner_radius=10, border_width=2, fg_color=COR_CONTAINER_INTERNO)
        self.months_container_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="nsew") # Span across two columns

        # Configura o grid dentro do months_container_frame para os botões dos meses
        for i in range(2): # 2 linhas
            self.months_container_frame.grid_rowconfigure(i, weight=1)
        for i in range(6): # 6 colunas
            self.months_container_frame.grid_columnconfigure(i, weight=1)

        # Estilo dos botões (baseado nos botões de ação)
        month_button_font = FONTE_NORMAL_BOLD # Usando uma fonte já definida, similar à dos botões de ação
        # month_button_height = 35 # Removido para que a altura se ajuste à fonte
        month_button_corner_radius = 17
        month_button_fg_color = "gray30"
        month_button_hover_color = "#2196F3"
        for i, month_name in enumerate(self.months_list):
            row = i // 6  # 0 para os primeiros 6 meses, 1 para os próximos 6
            col = i % 6   # 0 a 5 para as colunas

            month_button = customtkinter.CTkButton(
                self.months_container_frame,
                text=month_name,
                font=month_button_font,
                corner_radius=month_button_corner_radius,
                fg_color=month_button_fg_color,
                hover_color=month_button_hover_color,
                command=lambda m_idx=i: self.month_button_clicked(m_idx)
                )
            month_button.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        

        # --- Title for Annual Summary ---
        self.annual_summary_title_label = customtkinter.CTkLabel(self, text="Resumo Anual", font=FONTE_TITULO_GRANDE)
        self.annual_summary_title_label.grid(row=4, column=0, columnspan=2, pady=(20, 5), padx=20, sticky="w")

        # --- Left Container for Annual Summary List ---
        self.annual_list_container_frame = customtkinter.CTkFrame(self, corner_radius=10, border_width=2, fg_color=COR_CONTAINER_INTERNO)
        self.annual_list_container_frame.grid(row=5, column=0, padx=(20,10), pady=(10, 20), sticky="nsew")
        # Placeholder for annual list (changed text_color for better visibility if needed)
        annual_list_placeholder = customtkinter.CTkLabel(self.annual_list_container_frame, text="Lista Resumo Anual Placeholder", font=FONTE_TITULO_MEDIO, text_color="gray50")
        annual_list_placeholder.pack(expand=True, fill="both", padx=20, pady=20)

        # --- Right Container for Annual Summary Pie Chart ---
        self.annual_pie_chart_container_frame = customtkinter.CTkFrame(self, corner_radius=10, border_width=2, fg_color=COR_CONTAINER_INTERNO)
        self.annual_pie_chart_container_frame.grid(row=5, column=1, padx=(10,20), pady=(10, 20), sticky="nsew")
        # Placeholder for annual pie chart (changed text_color for better visibility if needed)
        annual_pie_placeholder = customtkinter.CTkLabel(self.annual_pie_chart_container_frame, text="Gráfico Pizza Anual Placeholder", font=FONTE_TITULO_MEDIO, text_color="gray50")
        annual_pie_placeholder.pack(expand=True, fill="both", padx=20, pady=20)

        # --- Bottom Container for Action Buttons and Logo ---
        self.actions_container_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent") # Sem cantos e transparente
        # Aumentado o pady inferior para criar mais espaço abaixo dos botões.
        self.actions_container_frame.grid(row=6, column=0, columnspan=2, padx=0, pady=(10,20), sticky="nsew") # Movido para row 6

        # Frame interno para centralizar os botões
        buttons_inner_frame = customtkinter.CTkFrame(self.actions_container_frame, fg_color="transparent")
        buttons_inner_frame.pack(expand=True, anchor="center", pady=10) # Centraliza o frame dos botões

        # --- Left Container for List Items ---
        self.list_container_frame = customtkinter.CTkFrame(self, corner_radius=10, border_width=2, fg_color=COR_CONTAINER_INTERNO)
        self.list_container_frame.grid(row=3, column=0, padx=(20,10), pady=(10, 20), sticky="nsew")

        # Add list items (example)
        list_items_title = customtkinter.CTkLabel(self.list_container_frame, text="Categorias Placeholder:", font=FONTE_TITULO_MEDIO)
        list_items_title.pack(padx=10, pady=(10, 5), anchor="w") # Anchor west

        list_items = ["Cat1 R$ 0,00", "Cat2 R$ 0,00", "Cat3 R$ 0,00", "Cat4 R$ 0,00"]
        for item in list_items:
            item_label = customtkinter.CTkLabel(self.list_container_frame, text=item, font=FONTE_NORMAL)
            item_label.pack(padx=20, pady=2, anchor="w") # Anchor west, add some padding


        # Configure grid for actions container (1 row, many columns for flexibility or use pack)
        # Usaremos pack para os botões e place para o logo

        # Botões de Ação
        button_font = FONTE_BOTAO_ACAO
        button_width = 150
        button_height = 35 # Altura padrão dos botões
        button_corner_radius = 17 # Para cantos bem arredondados, ~metade da altura

        # --- Bottom Container for Pie Chart ---
        self.pie_chart_container_frame = customtkinter.CTkFrame(self, corner_radius=10, border_width=2, fg_color=COR_CONTAINER_INTERNO)
        self.pie_chart_container_frame.grid(row=3, column=1, padx=(10,20), pady=(10, 20), sticky="nsew")

        # Placeholder for the pie chart (moved here)
        pie_chart_placeholder_label = customtkinter.CTkLabel(self.pie_chart_container_frame, text="Gráfico de Pizza Placeholder", font=FONTE_TITULO_MEDIO, text_color="gray50")
        pie_chart_placeholder_label.pack(expand=True, fill="both", padx=20, pady=20) # Center placeholder text
        button_corner_radius = 17 # Para cantos bem arredondados, ~metade da altura
        
        # Define as cores para os botões
        cor_botao_cinza = "gray30"  # Um cinza mais escuro do customtkinter
        cor_botao_azul_hover = "#2196F3" # O mesmo azul usado anteriormente para hover

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

    def handle_logout(self, event=None):
        """Fecha o Dashboard e sinaliza para Main.py reabrir a tela de Login."""
        print("Link 'Sair' clicado. Solicitando retorno para a tela de Login.")
        self.request_restart_on_close = True
        self.destroy()

    def year_changed_event(self, selected_year):
        print(f"Ano selecionado: {selected_year}")
        pass # Placeholder, nenhuma ação complexa por enquanto

    def month_button_clicked(self, month_index):
        month_name = self.months_list[month_index]
        print(f"Botão do mês '{month_name}' (índice {month_index}) clicado.")
        pass # Placeholder, nenhuma ação complexa por enquanto


if __name__ == "__main__":
    app = Dashboard(user_id="test_user_01") # Passa um user_id para teste
    app.mainloop()