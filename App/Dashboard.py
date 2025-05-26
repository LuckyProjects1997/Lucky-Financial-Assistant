import customtkinter
import tkinter as tk
from PIL import Image # Adicionado para carregar a imagem do logo
import datetime # Para obter o ano atual 
# from form_cadastro import FormCadastroWindow # Removido
from form_cadastro_categoria import FormCadastroCategoriaWindow # Importa o formulário de categoria
from form_detalhes_mensais import FormDetalhesMensaisWindow # Importa a nova janela de detalhes

from form_transacao import FormTransacaoWindow # Importa a nova janela de formulário de transação
# Importa as funções do nosso novo módulo de banco de dados (se necessário no futuro para o Dashboard).
import Database # Usando 'Database' com D maiúsculo conforme seu Main.py

import matplotlib
matplotlib.use('TkAgg') # Backend para tkinter
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk # Opcional para toolbar
from customtkinter.windows.widgets.theme import ThemeManager # Para cores de texto consistentes

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
        self.current_user_id = user_id # Armazena o ID do usuário logado.
        self.form_cadastro_window = None # Referência para a janela de cadastro
        self.form_transacao_window = None # Referência para a janela de transação
        self.form_detalhes_mensais_window = None # Referência para a janela de detalhes mensais
        self.request_restart_on_close = False # Sinalizador para reinício
        # self.main_app_window = master # Removido, pois 'master' não é passado e a lógica de voltar já funciona
        self.months_list = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        self.selected_month_index = None # Para rastrear o mês selecionado (0-11)
        self.list_container_title_label = None # Label para o título do list_container_frame
        print(f"Dashboard iniciado para o usuário ID: {self.current_user_id}")
        
        # Configurações globais do CustomTkinter (podem permanecer no início)
        customtkinter.set_appearance_mode("Dark") # Forçar tema escuro para um visual mais "high-tech"
        customtkinter.set_default_color_theme("blue") # Or choose another theme


        # Set grid layout for the main window (1 column for title, 2 columns below title)
        self.grid_columnconfigure(0, weight=1) # Title column spans the width
        self.grid_columnconfigure(1, weight=1) # Second column for pie chart container
        self.grid_rowconfigure(0, weight=0) # Title row
        self.grid_rowconfigure(1, weight=0) # Row for month buttons
        self.grid_rowconfigure(2, weight=1) # Row for list_container_frame (monthly details)
        self.grid_rowconfigure(3, weight=1) # Row for pie_chart_container_frame (monthly pie)
        self.grid_rowconfigure(4, weight=0) # Row for "Resumo Anual" title
        self.grid_rowconfigure(5, weight=1) # Row for annual_list_container_frame (TABLES) and annual_pie_chart_container_frame
        self.grid_rowconfigure(6, weight=0) # NEW: Row for annual_totals_display_frame (TOTALS)
        self.grid_rowconfigure(7, weight=0) # Row for action buttons and logo


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

        # --- Left Container for Annual Summary List (TABLES ONLY) ---
        self.annual_list_container_frame = customtkinter.CTkFrame(self, corner_radius=10, fg_color=COR_CONTAINER_INTERNO) # No border_width
        self.annual_list_container_frame.grid(row=5, column=0, padx=(20,10), pady=(10, 0), sticky="nsew") # pady bottom reduced
        # Configurar grid para o annual_list_container_frame gerenciar seu filho (tables_display_frame)
        self.annual_list_container_frame.grid_rowconfigure(0, weight=1)  # Single row for tables_display_frame
        self.annual_list_container_frame.grid_columnconfigure(0, weight=1) # Coluna única para expandir os frames internos

        # --- New Container for Annual Summary TOTALS (WITH BORDER) ---
        self.annual_totals_display_frame = customtkinter.CTkFrame(self, corner_radius=10, border_width=2, fg_color=COR_CONTAINER_INTERNO)
        self.annual_totals_display_frame.grid(row=6, column=0, padx=(20,10), pady=(5, 20), sticky="w") # Changed sticky to "w"
        # Configure grid for annual_totals_display_frame to manage its children (the totals_summary_frame)
        self.annual_totals_display_frame.grid_rowconfigure(0, weight=0) # For totals_summary_frame
        self.annual_totals_display_frame.grid_columnconfigure(0, weight=0) # Changed weight to 0

        self.load_annual_category_summaries() # Carrega os resumos anuais AQUI

        # --- Right Container for Annual Summary Pie Chart ---
        self.annual_pie_chart_container_frame = customtkinter.CTkFrame(self, corner_radius=10, border_width=2, fg_color=COR_CONTAINER_INTERNO)
        self.annual_pie_chart_container_frame.grid(row=5, column=1, padx=(10,20), pady=(10, 20), sticky="nsew")
        # Placeholder removido, será populado pelo gráfico
        self._load_annual_pie_chart_data() # Carrega o gráfico anual

        # --- Bottom Container for Action Buttons and Logo ---
        self.actions_container_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent") # Sem cantos e transparente
        self.actions_container_frame.grid(row=7, column=0, columnspan=2, padx=0, pady=(10,20), sticky="nsew") # Movido para row 7


        # Frame interno para centralizar os botões
        buttons_inner_frame = customtkinter.CTkFrame(self.actions_container_frame, fg_color="transparent")
        buttons_inner_frame.pack(expand=True, anchor="center", pady=10) # Centraliza o frame dos botões

        # --- Left Container for List Items ---
        # Transformado em CTkScrollableFrame
        self.list_container_frame = customtkinter.CTkScrollableFrame(self, corner_radius=10, border_width=2, fg_color=COR_CONTAINER_INTERNO)
        self.list_container_frame.grid(row=3, column=0, padx=(20,10), pady=(0, 20), sticky="nsew") # pady superior ajustado
        
        self.list_container_title_label = customtkinter.CTkLabel(self, text="Detalhes por Categoria (Mês)", font=FONTE_TITULO_MEDIO)
        self.list_container_title_label.grid(row=2, column=0, padx=(20,10), pady=(10,0), sticky="sw") # Acima do list_container_frame
        self.load_monthly_details_for_list_container() # Carrega os detalhes mensais


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

        # Placeholder removido, será populado pelo gráfico
        self._load_monthly_pie_chart_data() # Carrega o gráfico mensal

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
                                                      fg_color=cor_botao_cinza, hover_color=cor_botao_azul_hover,
                                                      command=self.open_form_detalhes_mensais)
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

        # Pré-seleciona Janeiro ao iniciar
        if self.months_list: # Garante que a lista de meses exista
            self.month_button_clicked(0) # 0 é o índice para Janeiro

        # Configurações da janela principal (movidas para o final do __init__)
        self.title("Gestão Financeira - Dashboard")
        # self.geometry("1024x768") # Mantido comentado
        self.configure(fg_color="#1c1c1c") # Define o fundo da janela principal do Dashboard
        # Define o tamanho da janela igual à resolução da tela do usuário
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}")

    def open_form_cadastro(self):
        if self.form_cadastro_window is None or not self.form_cadastro_window.winfo_exists(): # Verifica se a janela não existe ou foi fechada
            # Função a ser chamada quando o formulário de categoria for fechado
            def on_category_form_closed_callback():
                print("Formulário de cadastro de categoria fechado. Recarregando dados do Dashboard...")
                self._refresh_dashboard_data() # Recarrega os dados do dashboard (incluindo categorias)
                self.form_cadastro_window = None # Limpa a referência

            self.form_cadastro_window = FormCadastroCategoriaWindow(master=self, current_user_id=self.current_user_id, on_close_callback=on_category_form_closed_callback) # Abre o formulário de categoria
            self.form_cadastro_window.focus() # Traz a nova janela para o foco
        else:
            self.form_cadastro_window.focus() # Se a janela já existe, apenas a traz para o foco

    def open_form_detalhes_mensais(self):
        selected_year = self.year_combobox.get()
        if not self.current_user_id or not selected_year:
            print("Dashboard: Usuário ou ano não selecionado para abrir detalhes.")
            # Poderia mostrar um CTkMessagebox aqui
            return

        if self.form_detalhes_mensais_window is None or not self.form_detalhes_mensais_window.winfo_exists():
            self.form_detalhes_mensais_window = FormDetalhesMensaisWindow(master=self, current_user_id=self.current_user_id, selected_year=selected_year)
            self.form_detalhes_mensais_window.focus()
        else:
            self.form_detalhes_mensais_window.focus()

    def open_form_transacao(self, tipo_transacao):
        if self.form_transacao_window is None or not self.form_transacao_window.winfo_exists():
            self.form_transacao_window = FormTransacaoWindow(master=self, current_user_id=self.current_user_id, tipo_transacao=tipo_transacao, on_save_callback=self._refresh_dashboard_data)
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
        self.load_annual_category_summaries() # Recarrega os resumos anuais
        self.load_monthly_details_for_list_container() # Recarrega os detalhes mensais
        self._load_annual_pie_chart_data()
        self._load_monthly_pie_chart_data()

    def month_button_clicked(self, month_index):
        self.selected_month_index = month_index
        month_name = self.months_list[month_index]
        print(f"Botão do mês '{month_name}' (índice {month_index}) clicado.")
        self.list_container_title_label.configure(text=f"Detalhes de {month_name}")
        self.load_monthly_details_for_list_container()
        self._load_monthly_pie_chart_data()


    def load_annual_category_summaries(self):
        # Limpa o conteúdo anterior do annual_list_container_frame (tabelas)
        for widget in self.annual_list_container_frame.winfo_children():
            widget.destroy()
        # Limpa o conteúdo anterior do annual_totals_display_frame (totais)
        for widget in self.annual_totals_display_frame.winfo_children():
            widget.destroy()

        selected_year = self.year_combobox.get()
        if not self.current_user_id or not selected_year:
            message = "Selecione um usuário e ano para o resumo anual."
            no_data_label = customtkinter.CTkLabel(self.annual_list_container_frame, text=message, font=FONTE_NORMAL, text_color="gray50")
            no_data_label.pack(pady=20, padx=10)
            customtkinter.CTkLabel(self.annual_totals_display_frame, text="", font=FONTE_NORMAL).pack() # Placeholder for totals frame
            return

        # Frame para conter as duas tabelas (Despesa e Provento) lado a lado
        tables_display_frame = customtkinter.CTkFrame(self.annual_list_container_frame, fg_color="transparent") # Child of annual_list_container_frame
        tables_display_frame.grid(row=0, column=0, sticky="nsew") # pady removed, parent handles
        tables_display_frame.grid_columnconfigure(0, weight=1)  # Coluna para tabela de Despesas
        tables_display_frame.grid_columnconfigure(1, weight=1)  # Coluna para tabela de Proventos
        tables_display_frame.grid_rowconfigure(0, weight=1)     # Linha única para as tabelas expandirem verticalmente

        # Scrollable frame para Despesas
        despesa_scroll_frame = customtkinter.CTkScrollableFrame(tables_display_frame, label_text="Despesas", label_font=FONTE_NORMAL_BOLD, fg_color="transparent")
        despesa_scroll_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        # Scrollable frame para Proventos
        provento_scroll_frame = customtkinter.CTkScrollableFrame(tables_display_frame, label_text="Proventos", label_font=FONTE_NORMAL_BOLD, fg_color="transparent")
        provento_scroll_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))


        # Função auxiliar para criar a seção de tabela (Despesa ou Provento)
        def create_summary_section(parent_scroll_frame, category_type):
            section_total = 0.0

            # 0. Limpar conteúdo anterior do scroll_frame específico (caso seja chamado múltiplas vezes)
            for widget in parent_scroll_frame.winfo_children():
                widget.destroy()
            # 1. Obter todas as categorias do usuário para o tipo especificado
            all_user_categories_for_type = [
                cat for cat in Database.get_categories_by_user(self.current_user_id)
                if cat['type'] == category_type
            ]

            if not all_user_categories_for_type:
                customtkinter.CTkLabel(parent_scroll_frame, text=f"Nenhuma categoria de {category_type.lower()} cadastrada.", font=FONTE_NORMAL, text_color="gray60").pack(pady=5, padx=10, anchor="w")
                return section_total # Retorna 0.0

            # 2. Obter os totais anuais (esta função pode retornar apenas categorias com transações)
            annual_transaction_totals_raw = Database.get_category_totals_for_year(self.current_user_id, selected_year, category_type)

            # 3. Criar um mapa dos totais para fácil consulta
            annual_totals_map = {item['category_name']: item['total_value'] for item in annual_transaction_totals_raw}

            table_frame = customtkinter.CTkFrame(parent_scroll_frame, fg_color="transparent")
            table_frame.pack(fill="x", padx=10)
            table_frame.grid_columnconfigure(0, weight=3) # Coluna para nome da categoria
            table_frame.grid_columnconfigure(1, weight=1) # Coluna para valor

            # Cabeçalhos
            customtkinter.CTkLabel(table_frame, text="Categoria", font=FONTE_NORMAL_BOLD, text_color="gray60").grid(row=0, column=0, sticky="w", pady=(0,2))
            customtkinter.CTkLabel(table_frame, text="Total Anual", font=FONTE_NORMAL_BOLD, text_color="gray60").grid(row=0, column=1, sticky="e", pady=(0,2))

            # 4. Iterar sobre todas as categorias relevantes do usuário
            for i, category_data in enumerate(sorted(all_user_categories_for_type, key=lambda x: x['name'])):
                category_name = category_data["name"]
                total_value_for_year = annual_totals_map.get(category_name, 0.0) # Default para 0.0
                section_total += total_value_for_year

                cat_name_label = customtkinter.CTkLabel(table_frame, text=category_name, font=FONTE_NORMAL, anchor="w")
                cat_name_label.grid(row=i + 1, column=0, sticky="ew", pady=1)
                
                total_val_label = customtkinter.CTkLabel(table_frame, text=f"R$ {total_value_for_year:.2f}", font=FONTE_NORMAL, anchor="e")
                total_val_label.grid(row=i + 1, column=1, sticky="ew", pady=1)
            return section_total

        # Popular tabela de Despesas e obter total
        total_despesas = create_summary_section(despesa_scroll_frame, "Despesa")

        # Popular tabela de Proventos e obter total
        total_proventos = create_summary_section(provento_scroll_frame, "Provento")

        # Frame para exibir os totais - AGORA FILHO DE self.annual_totals_display_frame
        totals_summary_frame = customtkinter.CTkFrame(self.annual_totals_display_frame, fg_color="transparent")
        totals_summary_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(5, 5)) # pady ajustado para novo pai
        # Configurar colunas para alinhar texto à esquerda e valor à esquerda da sua coluna
        totals_summary_frame.grid_columnconfigure(0, weight=0) # Coluna para o texto do label (e.g., "Total Proventos:")
        totals_summary_frame.grid_columnconfigure(1, weight=1) # Coluna para o valor (e.g., "R$ 100.00")

        # Total Proventos
        total_proventos_label_text = customtkinter.CTkLabel(totals_summary_frame, text="Total Proventos Anual:", font=FONTE_NORMAL_BOLD, anchor="w")
        total_proventos_label_text.grid(row=0, column=0, sticky="w", padx=(0,10), pady=(0,2)) # padx à direita para separar do valor
        total_proventos_label_value = customtkinter.CTkLabel(totals_summary_frame, text=f"R$ {total_proventos:.2f}", font=FONTE_NORMAL_BOLD, text_color="lightgreen", anchor="w")
        total_proventos_label_value.grid(row=0, column=1, sticky="w", pady=(0,2))

        # Total Despesas
        total_despesas_label_text = customtkinter.CTkLabel(totals_summary_frame, text="Total Despesas Anual:", font=FONTE_NORMAL_BOLD, anchor="w")
        total_despesas_label_text.grid(row=1, column=0, sticky="w", padx=(0,10), pady=(0,2))
        total_despesas_label_value = customtkinter.CTkLabel(totals_summary_frame, text=f"R$ {total_despesas:.2f}", font=FONTE_NORMAL_BOLD, text_color="tomato", anchor="w")
        total_despesas_label_value.grid(row=1, column=1, sticky="w", pady=(0,2))

        # Saldo Total Anual
        saldo_anual = total_proventos - total_despesas
        cor_saldo = "lightgreen" if saldo_anual >= 0 else "tomato"

        saldo_total_label_text = customtkinter.CTkLabel(totals_summary_frame, text="Saldo Total Anual:", font=FONTE_NORMAL_BOLD, anchor="w")
        saldo_total_label_text.grid(row=2, column=0, sticky="w", padx=(0,10), pady=(2,0)) # pady superior para separar
        saldo_total_label_value = customtkinter.CTkLabel(totals_summary_frame, text=f"R$ {saldo_anual:.2f}", font=FONTE_NORMAL_BOLD, text_color=cor_saldo, anchor="w")
        saldo_total_label_value.grid(row=2, column=1, sticky="w", pady=(2,0))

    def load_monthly_details_for_list_container(self):
        # Limpa o conteúdo anterior do list_container_frame
        for widget in self.list_container_frame.winfo_children():
            widget.destroy()

        if self.selected_month_index is None:
            self.list_container_title_label.configure(text="Detalhes por Categoria (Mês)")
            customtkinter.CTkLabel(self.list_container_frame, text="Selecione um mês para ver os detalhes.", font=FONTE_NORMAL, text_color="gray60").pack(pady=20, padx=10)
            return

        selected_year = self.year_combobox.get()
        month_number = self.selected_month_index + 1 # Meses são 1-12 no banco

        if not self.current_user_id or not selected_year:
            customtkinter.CTkLabel(self.list_container_frame, text="Usuário ou ano não selecionado.", font=FONTE_NORMAL, text_color="gray60").pack(pady=20, padx=10)
            return

        # Busca todas as categorias do usuário
        all_user_categories = Database.get_categories_by_user(self.current_user_id)
        if not all_user_categories:
            customtkinter.CTkLabel(self.list_container_frame, text="Nenhuma categoria cadastrada.", font=FONTE_NORMAL, text_color="gray60").pack(pady=20, padx=10)
            return

        # Busca os totais do mês selecionado para cada categoria
        monthly_data_raw = Database.get_category_summary_for_month(self.current_user_id, selected_year, month_number)
        
        # Mapeia os totais por nome da categoria e tipo para fácil acesso
        monthly_totals_map = {}
        for item in monthly_data_raw:
            key = (item['category_name'], item['category_type'])
            monthly_totals_map[key] = item['total_value']

        # Cabeçalhos
        header_frame = customtkinter.CTkFrame(self.list_container_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(5,2))
        header_frame.grid_columnconfigure(0, weight=3) # Categoria (mais peso)
        header_frame.grid_columnconfigure(1, weight=1) # Valor no Mês
        customtkinter.CTkLabel(header_frame, text="Categoria", font=FONTE_NORMAL_BOLD, text_color="gray60").grid(row=0, column=0, sticky="w")
        customtkinter.CTkLabel(header_frame, text="Valor no Mês", font=FONTE_NORMAL_BOLD, text_color="gray60").grid(row=0, column=1, sticky="e")

        for category in sorted(all_user_categories, key=lambda x: x['name']): # Ordena por nome
            category_name = category['name']
            category_type = category['type']
            total_value_for_month = monthly_totals_map.get((category_name, category_type), 0.0)
            
            # Define a cor da fonte com base no tipo da categoria
            font_color = "tomato" if category_type == "Despesa" else "lightgreen" if category_type == "Provento" else ThemeManager.theme["CTkLabel"]["text_color"]
            # Se for um tipo não esperado, usa a cor padrão do tema para labels

            item_frame = customtkinter.CTkFrame(self.list_container_frame, fg_color="transparent")
            item_frame.pack(fill="x", padx=10, pady=0) # Reduzido pady de 1 para 0
            item_frame.grid_columnconfigure(0, weight=3) # Categoria
            item_frame.grid_columnconfigure(1, weight=1) # Valor

            # Label da Categoria com a cor da fonte definida
            customtkinter.CTkLabel(item_frame, text=f"{category_name}", font=FONTE_NORMAL, anchor="w", text_color=font_color, corner_radius=3, padx=3).grid(row=0, column=0, sticky="ew")
            # Label do Valor com a cor da fonte definida
            customtkinter.CTkLabel(item_frame, text=f"R$ {total_value_for_month:.2f}", font=FONTE_NORMAL, anchor="e", text_color=font_color).grid(row=0, column=1, sticky="ew")

    def _create_pie_chart(self, parent_frame, data_values, data_labels, data_colors_hex, chart_title=""):
        # Limpar o frame pai
        for widget in parent_frame.winfo_children():
            widget.destroy()

        fig = Figure(figsize=(4, 3), dpi=100, facecolor=parent_frame.cget("fg_color")) # Usar a cor de fundo do frame CTk
        ax = fig.add_subplot(111)

        # Filtrar itens com valor zero para não poluir o gráfico
        filtered_labels = []
        filtered_values = []
        filtered_colors = []
        for label, value, color in zip(data_labels, data_values, data_colors_hex):
            if value > 0:
                filtered_labels.append(label)
                filtered_values.append(value)
                filtered_colors.append(color)
        
        # Se não houver dados filtrados, o gráfico será desenhado vazio.
        # As configurações de explode e autopct só fazem sentido se houver dados.
        if filtered_values:
            explode_value = 0.03 # Pequeno explode para todas as fatias
            explode = [explode_value] * len(filtered_values)

            wedges, texts, autotexts = ax.pie(filtered_values,
                                              colors=filtered_colors,
                                              autopct='%1.1f%%',
                                              shadow=True,
                                              startangle=90,
                                              pctdistance=0.85,
                                              explode=explode)

            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontsize(7)
                autotext.set_fontweight('bold')
        else:
            # Desenha um círculo vazio se não houver dados.
            # Usamos a cor de fundo do frame para o círculo.
            ax.pie([1], colors=[parent_frame.cget("fg_color")], startangle=90) # Desenha um círculo da cor do fundo

        # Determina a cor do texto do título com base no tema atual
        title_text_color_val = ThemeManager.theme["CTkLabel"]["text_color"]
        
        if isinstance(title_text_color_val, list):
            # Determina o modo de aparência atual para escolher a cor correta
            current_mode = customtkinter.get_appearance_mode()
            if current_mode == "Dark":
                final_color_str = title_text_color_val[0]
            elif current_mode == "Light" and len(title_text_color_val) > 1:
                final_color_str = title_text_color_val[1]
            else: # Fallback se o modo for inesperado ou a lista tiver apenas um item
                final_color_str = title_text_color_val[0]
        else:
            final_color_str = title_text_color_val

        # Converte nomes de cores como "gray10" para formato compatível com Matplotlib (ex: "0.10")
        # Verifica se não é um código hexadecimal antes de tentar converter
        if not final_color_str.startswith('#'):
            if final_color_str.lower().startswith("gray") and final_color_str[4:].isdigit():
                try:
                    percentage = int(final_color_str[4:])
                    final_color_str = f"{percentage/100.0:.2f}" 
                except ValueError: pass # Mantém original se a conversão falhar
            elif final_color_str.lower().startswith("grey") and final_color_str[4:].isdigit(): # Lida com 'grey' também
                try:
                    percentage = int(final_color_str[4:])
                    final_color_str = f"{percentage/100.0:.2f}"
                except ValueError: pass

        ax.set_title(chart_title, color=final_color_str, fontsize=10)
        fig.tight_layout() # Ajusta o layout para evitar sobreposição

        canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def _load_monthly_pie_chart_data(self):
        if self.selected_month_index is None or not self.current_user_id:
            self._create_pie_chart(self.pie_chart_container_frame, [], [], [], "Despesas do Mês")
            return

        selected_year = self.year_combobox.get()
        month_number = self.selected_month_index + 1
        
        monthly_expenses_raw = Database.get_category_summary_for_month(self.current_user_id, selected_year, month_number)
        expenses_data = [item for item in monthly_expenses_raw if item['category_type'] == 'Despesa' and item['total_value'] > 0]

        labels = [item['category_name'] for item in expenses_data]
        sizes = [item['total_value'] for item in expenses_data]
        colors = [item['category_color'] for item in expenses_data]
        self._create_pie_chart(self.pie_chart_container_frame, sizes, labels, colors, f"Despesas de {self.months_list[self.selected_month_index]}")

    def _load_annual_pie_chart_data(self):
        selected_year = self.year_combobox.get()
        if not self.current_user_id or not selected_year:
            self._create_pie_chart(self.annual_pie_chart_container_frame, [], [], [], f"Despesas Anuais ({selected_year})")
            return
        
        annual_expenses_raw = Database.get_category_totals_for_year(self.current_user_id, selected_year, "Despesa")
        # A função get_category_totals_for_year já filtra por valor > 0 (HAVING SUM(t.value) IS NOT NULL)
        labels = [item['category_name'] for item in annual_expenses_raw]
        sizes = [item['total_value'] for item in annual_expenses_raw]
        colors = [item['category_color'] for item in annual_expenses_raw]
        self._create_pie_chart(self.annual_pie_chart_container_frame, sizes, labels, colors, f"Despesas Anuais ({selected_year})")

    def _refresh_dashboard_data(self):
        """
        Chamado para atualizar os dados exibidos no Dashboard.
        Isso é útil após salvar uma nova transação, por exemplo.
        """
        print("Dashboard: _refresh_dashboard_data chamado. Atualizando dados...")
        self.load_annual_category_summaries()
        self.load_monthly_details_for_list_container() # Atualiza a lista mensal se um mês estiver selecionado
        self._load_annual_pie_chart_data()
        self._load_monthly_pie_chart_data() # Atualiza o gráfico mensal se um mês estiver selecionado
if __name__ == "__main__":
    app = Dashboard(user_id="test_user_01") # Passa um user_id para teste
    app.mainloop()