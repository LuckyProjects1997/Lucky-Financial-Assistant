import customtkinter
import tkinter as tk
import sys  # Para resource_path e manipulação de sys.path
import os   # Para resource_path e manipulação de sys.path

# print(f"DEBUG: sys.path in Dashboard.py before imports: {sys.path}") # Optional debug print
from PIL import Image # Adicionado para carregar a imagem do logo
# --- INÍCIO DA CORREÇÃO PARA PYLANCE E EXECUÇÃO DIRETA ---
# Adiciona o diretório do script atual (que deve ser 'App') ao sys.path.
script_directory = os.path.dirname(os.path.abspath(__file__))
if script_directory not in sys.path:
    sys.path.append(script_directory)
# --- FIM DA CORREÇÃO ---

import datetime # Para obter o ano atual 
# from form_cadastro import FormCadastroWindow # Removido
from form_cadastro_categoria import FormCadastroCategoriaWindow # Importa o formulário de categoria
from form_detalhes_mensais import DetalhesMensaisView # Importa a classe de visualização de Detalhes Mensais
from form_planejamento import PlanejamentoView # Importa a nova classe de visualização de Planejamento

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

def resource_path(relative_path):
    """ Obtém o caminho absoluto para o recurso, funciona para desenvolvimento e para PyInstaller """
    try:
        # PyInstaller cria uma pasta temporária e armazena o caminho em _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError: # _MEIPASS não existe, então estamos em modo de desenvolvimento
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Dashboard(customtkinter.CTk):
    SIDEBAR_OPEN_WIDTH = 220
    SIDEBAR_CLOSED_WIDTH = 50

    def __init__(self, user_id=None): # Adiciona user_id como parâmetro opcional.
        super().__init__()
        self.current_user_id = user_id # Armazena o ID do usuário logado.
        self.form_cadastro_window = None # Referência para a janela de cadastro
        self.form_transacao_window = None # Referência para a janela de transação
        # self.form_detalhes_mensais_window = None # REMOVIDO: Não será mais uma Toplevel separada
        self.request_restart_on_close = False # Sinalizador para reinício
        # self.main_app_window = master # Removido, pois 'master' não é passado e a lógica de voltar já funciona
        self.months_list = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        self.selected_month_index = None # Para rastrear o mês selecionado (0-11)
        self.sidebar_open = False # Estado inicial do menu lateral

        # Elementos do menu lateral que precisam ser referenciados
        self.sidebar_menu_title = None
        self.sidebar_buttons = []
        self.list_container_title_label = None # Label para o título do list_container_frame
        print(f"Dashboard iniciado para o usuário ID: {self.current_user_id}")
        
        # Configurações globais do CustomTkinter (podem permanecer no início)
        customtkinter.set_appearance_mode("Dark") # Forçar tema escuro para um visual mais "high-tech"
        customtkinter.set_default_color_theme("blue") # Or choose another theme


        # Configura o grid principal para ter 2 colunas: sidebar e main_content_area
        self.grid_columnconfigure(0, weight=0, minsize=self.SIDEBAR_CLOSED_WIDTH) # Coluna para o sidebar (largura inicial)
        self.grid_columnconfigure(1, weight=1) # Coluna para a área de conteúdo principal (expansível)
        self.grid_rowconfigure(0, weight=0) # Title row
        self.grid_rowconfigure(1, weight=1) # Linha para sidebar e main_content_area (expansível)


        # --- Header Frame (Title and Year Selector) ---
        self.header_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="ew")
        # Configurar colunas do header_frame para alinhar título, seletor de ano, logo e info do usuário
        self.header_frame.grid_columnconfigure(0, weight=1) # Título e Seletor de Ano
        self.header_frame.grid_columnconfigure(1, weight=0) # Logo
        self.header_frame.grid_columnconfigure(2, weight=0) # Info do Usuário


         # Container para informações do usuário (à direita)
        user_info_container = customtkinter.CTkFrame(self.header_frame, fg_color="transparent")
        user_info_container.grid(row=0, column=2, sticky="ne", padx=(20,0)) # Alterado de pack para grid


        self.logged_user_label = customtkinter.CTkLabel(user_info_container, text="", font=FONTE_USUARIO_LOGADO, text_color="gray60")
        self.logged_user_label.pack(side="top", anchor="e", pady=(0,5))

        # Link "Sair"
        self.logout_label = customtkinter.CTkLabel(user_info_container, text="Sair", font=(FONTE_FAMILIA, 10, "underline"), text_color="#8ab4f8", cursor="hand2")
        self.logout_label.pack(side="top", anchor="e", pady=(0, 10))
        self.logout_label.bind("<Button-1>", self.handle_logout)
        self.load_logged_user_name() # Carrega o nome do usuário aqui


        # Container para o título e o seletor de ano (ocupa o espaço restante à esquerda)
        title_year_container = customtkinter.CTkFrame(self.header_frame, fg_color="transparent")
        title_year_container.grid(row=0, column=0, sticky="w") # Alinha à esquerda na primeira coluna do header
        
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

        # Logo no Header
        try:
            logo_image_path = resource_path("Images/Logo.png")
            pil_logo_image = Image.open(logo_image_path)
            self.logo_ctk_image = customtkinter.CTkImage(pil_logo_image, size=(50, 50)) 
            
            self.logo_label_header = customtkinter.CTkLabel(self.header_frame, image=self.logo_ctk_image, text="")
            self.logo_label_header.grid(row=0, column=1, padx=(10,10), sticky="e") # Alinha à direita na segunda coluna do header
        except FileNotFoundError:
            print(f"Erro: Imagem do logo '{logo_image_path}' não encontrada.")
        except Exception as e:
            print(f"Erro ao carregar a imagem do logo: {e}")

        # --- Sidebar Frame ---
        self.sidebar_frame = customtkinter.CTkFrame(self, width=self.SIDEBAR_CLOSED_WIDTH, corner_radius=0, fg_color=COR_CONTAINER_INTERNO)
        self.sidebar_frame.grid(row=1, column=0, sticky="nsw") # nsw para preencher verticalmente e ficar à esquerda
        self.sidebar_frame.grid_propagate(False) # Impede que os widgets filhos controlem o tamanho do frame

        # Botão para abrir/fechar o menu lateral
        self.sidebar_toggle_button = customtkinter.CTkButton(self.sidebar_frame, text="☰", width=40, height=40,
                                                             font=(FONTE_FAMILIA, 20), command=self.toggle_sidebar,
                                                             fg_color="transparent", hover_color="gray25")
        self.sidebar_toggle_button.pack(pady=10, padx=5, anchor="n")

        # Título "Menu" (inicialmente não visível)
        self.sidebar_menu_title = customtkinter.CTkLabel(self.sidebar_frame, text="Menu", font=FONTE_TITULO_MEDIO)
        # Não usa pack() aqui, será gerenciado por toggle_sidebar

        # Botões do menu lateral (inicialmente não visíveis)
        sidebar_button_font = FONTE_BOTAO_ACAO
        sidebar_button_height = 35
        sidebar_button_corner_radius = 17
        sidebar_button_fg_color = "gray30"
        sidebar_button_hover_color = "#2196F3"

        self.sidebar_dashboard_button = customtkinter.CTkButton(self.sidebar_frame, text="Dashboard",
                                                              font=sidebar_button_font, height=sidebar_button_height,
                                                              corner_radius=sidebar_button_corner_radius,
                                                              fg_color=sidebar_button_fg_color, hover_color=sidebar_button_hover_color,
                                                              command=self._show_dashboard_view) # Comando para mostrar a view do Dashboard
        self.sidebar_buttons.append(self.sidebar_dashboard_button)

        self.sidebar_details_button = customtkinter.CTkButton(self.sidebar_frame, text="Detalhes",
                                                              font=sidebar_button_font, height=sidebar_button_height,
                                                              corner_radius=sidebar_button_corner_radius,
                                                              fg_color=sidebar_button_fg_color, hover_color=sidebar_button_hover_color,
                                                              command=self._show_detalhes_mensais_view)
        self.sidebar_buttons.append(self.sidebar_details_button) # Keep this line

        self.sidebar_planning_button = customtkinter.CTkButton(self.sidebar_frame, text="Planejamento",
                                                              font=sidebar_button_font, height=sidebar_button_height,
                                                              corner_radius=sidebar_button_corner_radius,
                                                              fg_color=sidebar_button_fg_color, hover_color=sidebar_button_hover_color, # Comando para mostrar a view de Planejamento
                                                              command=self._show_planejamento_view)
        self.sidebar_buttons.append(self.sidebar_planning_button)


        self.sidebar_transaction_button = customtkinter.CTkButton(self.sidebar_frame, text="Nova Despesa/Provento",
                                                                  font=sidebar_button_font, height=sidebar_button_height,
                                                                  corner_radius=sidebar_button_corner_radius,
                                                                  fg_color=sidebar_button_fg_color, hover_color=sidebar_button_hover_color,
                                                                  command=lambda: self.open_form_transacao("Despesa"))
        self.sidebar_buttons.append(self.sidebar_transaction_button)

        self.sidebar_category_button = customtkinter.CTkButton(self.sidebar_frame, text="Nova Categoria",
                                                               font=sidebar_button_font, height=sidebar_button_height,
                                                               corner_radius=sidebar_button_corner_radius,
                                                               fg_color=sidebar_button_fg_color, hover_color=sidebar_button_hover_color,
                                                               command=self.open_form_cadastro)
        self.sidebar_buttons.append(self.sidebar_category_button)

        # --- Área de Conteúdo Principal ---
        self.main_content_area = customtkinter.CTkFrame(self, fg_color="transparent")
        self.main_content_area.grid(row=1, column=1, sticky="nsew", padx=0, pady=0)
        self.main_content_area.grid_columnconfigure(0, weight=1) # Para o conteúdo interno expandir
        self.main_content_area.grid_rowconfigure(0, weight=1)    # Para o conteúdo interno expandir

        # Constrói a UI inicial do Dashboard dentro da main_content_area
        self._build_dashboard_ui_elements(self.main_content_area)

        # Inicializa o estado visual do sidebar
        self._update_sidebar_visibility()

        # Configurações da janela principal (movidas para o final do __init__)
        self.title("Gestão Financeira - Dashboard")
        # self.geometry("1024x768") # Mantido comentado
        self.configure(fg_color="#1c1c1c") # Define o fundo da janela principal do Dashboard
        # Define o tamanho da janela igual à resolução da tela do usuário
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}")

        # Pré-seleciona Janeiro ao iniciar (após a UI do dashboard ser construída)
        if self.months_list:
            self.month_button_clicked(0)

    def toggle_sidebar(self):
        self.sidebar_open = not self.sidebar_open
        self._update_sidebar_visibility()

    def _update_sidebar_visibility(self):
        if self.sidebar_open:
            self.sidebar_frame.configure(width=self.SIDEBAR_OPEN_WIDTH)
            self.sidebar_toggle_button.configure(text="✕") # Ou um ícone de fechar
            self.sidebar_menu_title.pack(pady=(5, 10), padx=10, anchor="n")
            for button in self.sidebar_buttons:
                button.pack(pady=5, padx=10, fill="x", anchor="n")
        else:
            self.sidebar_frame.configure(width=self.SIDEBAR_CLOSED_WIDTH)
            self.sidebar_toggle_button.configure(text="☰") # Ícone de menu hamburger
            if self.sidebar_menu_title and self.sidebar_menu_title.winfo_ismapped():
                self.sidebar_menu_title.pack_forget()
            for button in self.sidebar_buttons:
                if button.winfo_ismapped():
                    button.pack_forget()
        
        # Força a atualização do layout do sidebar_frame
        self.sidebar_frame.update_idletasks()


    def _clear_main_content_area(self):
        """Limpa todos os widgets da área de conteúdo principal."""
        for widget in self.main_content_area.winfo_children():
            widget.destroy()

    def _build_dashboard_ui_elements(self, parent_frame):
        """Constrói ou reconstrói os elementos da UI do Dashboard dentro do parent_frame."""
        parent_frame.grid_columnconfigure(0, weight=1)
        parent_frame.grid_columnconfigure(1, weight=1)
        parent_frame.grid_columnconfigure(2, weight=1)
        parent_frame.grid_rowconfigure(0, weight=0) # Months container
        parent_frame.grid_rowconfigure(1, weight=0) # list_container_title_label
        parent_frame.grid_rowconfigure(2, weight=0) # list_container, pie_chart, monthly_summary
        parent_frame.grid_rowconfigure(3, weight=0) # annual_summary_title_label
        parent_frame.grid_rowconfigure(4, weight=1) # annual_list, annual_pie, annual_totals

        # --- Top Container for Months ---
        self.months_container_frame = customtkinter.CTkFrame(parent_frame, corner_radius=10, border_width=2, fg_color=COR_CONTAINER_INTERNO)
        self.months_container_frame.grid(row=0, column=0, columnspan=3, padx=20, pady=10, sticky="nsew")
        for i in range(2): self.months_container_frame.grid_rowconfigure(i, weight=1)
        for i in range(6): self.months_container_frame.grid_columnconfigure(i, weight=1)
        month_button_font = FONTE_NORMAL_BOLD
        month_button_corner_radius = 17
        month_button_fg_color = "gray30"
        month_button_hover_color = "#2196F3"
        for i, month_name in enumerate(self.months_list):
            row, col = i // 6, i % 6
            month_button = customtkinter.CTkButton(self.months_container_frame, text=month_name, font=month_button_font,
                                                 corner_radius=month_button_corner_radius, fg_color=month_button_fg_color,
                                                 hover_color=month_button_hover_color, command=lambda m_idx=i: self.month_button_clicked(m_idx))
            month_button.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        # --- Monthly Details Section ---
        self.list_container_title_label = customtkinter.CTkLabel(parent_frame, text="Detalhes do Mês", font=FONTE_TITULO_MEDIO)
        self.list_container_title_label.grid(row=1, column=0, padx=(20,10), pady=(10,0), sticky="sw")

        self.list_container_frame = customtkinter.CTkScrollableFrame(parent_frame, corner_radius=10, border_width=2, fg_color=COR_CONTAINER_INTERNO, height=120)
        self.list_container_frame.grid(row=2, column=0, padx=(20,10), pady=(0, 10), sticky="nsew")
        
        self.pie_chart_container_frame = customtkinter.CTkFrame(parent_frame, corner_radius=10, border_width=2, fg_color=COR_CONTAINER_INTERNO, height=120)
        self.pie_chart_container_frame.grid(row=2, column=1, padx=(10,10), pady=(0, 10), sticky="nsew")
        self.pie_chart_container_frame.grid_propagate(False)

        self.monthly_proventos_summary_frame = customtkinter.CTkFrame(parent_frame, corner_radius=10, border_width=2, fg_color=COR_CONTAINER_INTERNO, width=260, height=120)
        self.monthly_proventos_summary_frame.grid(row=2, column=2, padx=(10,20), pady=(0, 10), sticky="nsew")
        self.monthly_proventos_summary_frame.grid_columnconfigure(0, weight=0)
        self.monthly_proventos_summary_frame.grid_columnconfigure(1, weight=1)
        self.monthly_proventos_summary_frame.grid_rowconfigure(0, weight=0)
        self.monthly_proventos_summary_frame.grid_rowconfigure(1, weight=0)
        self.monthly_proventos_summary_frame.grid_rowconfigure(4, weight=1) # Aumentado para acomodar novos campos

        # --- Annual Summary Section ---
        self.annual_summary_title_label = customtkinter.CTkLabel(parent_frame, text="Resumo Anual", font=FONTE_TITULO_GRANDE)
        self.annual_summary_title_label.grid(row=3, column=0, columnspan=3, pady=(10, 5), padx=20, sticky="w")

        self.annual_list_container_frame = customtkinter.CTkFrame(parent_frame, corner_radius=10, fg_color=COR_CONTAINER_INTERNO)
        self.annual_list_container_frame.grid(row=4, column=0, padx=(20,10), pady=(10, 20), sticky="nsew")
        self.annual_list_container_frame.grid_rowconfigure(0, weight=1)
        self.annual_list_container_frame.grid_columnconfigure(0, weight=1)

        self.annual_pie_chart_container_frame = customtkinter.CTkFrame(parent_frame, corner_radius=10, border_width=2, fg_color=COR_CONTAINER_INTERNO)
        self.annual_pie_chart_container_frame.grid(row=4, column=1, padx=(10,10), pady=(10, 20), sticky="nsew")

        self.annual_totals_display_frame = customtkinter.CTkFrame(parent_frame, corner_radius=10, border_width=2, fg_color=COR_CONTAINER_INTERNO, width=260, height=120)
        self.annual_totals_display_frame.grid(row=4, column=2, padx=(10,20), pady=(10, 20), sticky="nsew")
        self.annual_totals_display_frame.grid_propagate(False)
        self.annual_totals_display_frame.grid_rowconfigure(2, weight=0) # Aumentado para acomodar novos campos
        self.annual_totals_display_frame.grid_columnconfigure(0, weight=0)

        # Carregar dados para os elementos recém-criados
        self.load_monthly_details_for_list_container()
        self.load_monthly_proventos_summary()
        self._load_monthly_pie_chart_data()
        self.load_annual_category_summaries()
        self._load_annual_pie_chart_data()

        # Pré-seleciona Janeiro se nenhum mês estiver selecionado
        if self.selected_month_index is None and self.months_list:
             self.month_button_clicked(0) # 0 é o índice para Janeiro
        elif self.selected_month_index is not None: # Garante que o título seja atualizado
            self.list_container_title_label.configure(text=f"Detalhes de {self.months_list[self.selected_month_index]}")


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
    
    def _show_dashboard_view(self):
        """Limpa a área de conteúdo e reconstrói a UI do Dashboard."""
        self._clear_main_content_area()
        # Re-exibe o header do Dashboard (o sidebar já está visível)
        self.header_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="ew")

        # Constrói os elementos internos do dashboard na área de conteúdo principal
        self._build_dashboard_ui_elements(self.main_content_area)
        self._refresh_dashboard_data() # Garante que os dados estejam atualizados

    def _show_detalhes_mensais_view(self):
        """Wrapper para _actual_show_detalhes_mensais_view para garantir o contexto 'self'."""
        selected_year = self.year_combobox.get()
        if not self.current_user_id or not selected_year:
            print("Dashboard: Usuário ou ano não selecionado para abrir detalhes.")
            # Poderia mostrar um CTkMessagebox aqui
            return
        
        # Limpa a área de conteúdo e esconde o header do Dashboard. O sidebar permanece.
        self._clear_main_content_area()
        self.header_frame.grid_remove()
        # self.actions_container_frame.grid_remove() # Não existe mais
    
        detalhes_view = DetalhesMensaisView(master=self.main_content_area, current_user_id=self.current_user_id,
                                            selected_year=selected_year, close_callback=self._show_dashboard_view,
                                            main_dashboard_refresh_callback=self._refresh_dashboard_data)
        detalhes_view.pack(expand=True, fill="both")

    def _show_planejamento_view(self):
        """Wrapper para _actual_show_planejamento_view para garantir o contexto 'self'."""
        selected_year = self.year_combobox.get()
        if not self.current_user_id or not selected_year:
            print("Dashboard: Usuário ou ano não selecionado para abrir planejamento.")
            return

        self._clear_main_content_area()
        self.header_frame.grid_remove()

        planejamento_view = PlanejamentoView(master=self.main_content_area, current_user_id=self.current_user_id,
                                             selected_year=selected_year, close_callback=self._show_dashboard_view,
                                             main_dashboard_refresh_callback=self._refresh_dashboard_data)
        planejamento_view.pack(expand=True, fill="both")

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
        self._load_annual_pie_chart_data()
        # Recarrega dados mensais somente se a view do dashboard estiver ativa
        if hasattr(self, 'list_container_frame') and self.list_container_frame.winfo_exists():
            self.load_monthly_details_for_list_container()
            self.load_monthly_proventos_summary()
            self._load_monthly_pie_chart_data()
            
    def month_button_clicked(self, month_index):
        self.selected_month_index = month_index
        month_name = self.months_list[month_index]
        print(f"Botão do mês '{month_name}' (índice {month_index}) clicado.")
        self.list_container_title_label.configure(text=f"Detalhes de {month_name}")
        self.load_monthly_details_for_list_container()
        self.load_monthly_proventos_summary()
        self._load_monthly_pie_chart_data()

    def load_monthly_proventos_summary(self):
        # Limpa o conteúdo anterior
        for widget in self.monthly_proventos_summary_frame.winfo_children():
            widget.destroy()

        if self.selected_month_index is None:
            customtkinter.CTkLabel(self.monthly_proventos_summary_frame, text="Selecione um mês", font=FONTE_NORMAL, text_color="gray60").grid(row=0, column=0, columnspan=2, padx=10, pady=5)
            return

        selected_year = self.year_combobox.get()
        month_number = self.selected_month_index + 1
        month_name = self.months_list[self.selected_month_index]

        if not self.current_user_id or not selected_year:
            customtkinter.CTkLabel(self.monthly_proventos_summary_frame, text="Usuário/Ano não definido", font=FONTE_NORMAL, text_color="gray60").grid(row=0, column=0, columnspan=2, padx=10, pady=5)
            return

        monthly_data_raw = Database.get_category_summary_for_month(self.current_user_id, selected_year, month_number)

        total_proventos_mes = sum(item['total_value'] for item in monthly_data_raw if item['category_type'] == 'Provento')

        total_despesas_mes = sum(item['total_value'] for item in monthly_data_raw if item['category_type'] == 'Despesa')
        saldo_mes = total_proventos_mes - total_despesas_mes
        cor_saldo = "lightgreen" if saldo_mes >= 0 else "tomato"
        
        # Buscar totais por meio de pagamento
        payment_method_summary = Database.get_monthly_expenses_by_payment_method(self.current_user_id, selected_year, month_number)
        total_cartao_mes = payment_method_summary.get("Cartão de Crédito", 0.0)
        total_conta_mes = payment_method_summary.get("Conta Corrente", 0.0)

        # Total Proventos
        proventos_title_text = f"Total Proventos:"
        proventos_label_text = customtkinter.CTkLabel(self.monthly_proventos_summary_frame, text=proventos_title_text, font=FONTE_NORMAL_BOLD, anchor="w")
        proventos_label_text.grid(row=0, column=0, sticky="w", padx=(10,10), pady=(2,3)) # pady ajustado
        
        proventos_label_value = customtkinter.CTkLabel(self.monthly_proventos_summary_frame, text=f"R$ {total_proventos_mes:.2f}", font=FONTE_NORMAL_BOLD, text_color="lightgreen", anchor="w")
        proventos_label_value.grid(row=0, column=1, sticky="w", padx=(0,10), pady=(2,3)) # pady ajustado

        # Total Despesas
        despesas_title_text = f"Total Despesas:"
        despesas_label_text = customtkinter.CTkLabel(self.monthly_proventos_summary_frame, text=despesas_title_text, font=FONTE_NORMAL_BOLD, anchor="w")
        despesas_label_text.grid(row=1, column=0, sticky="w", padx=(10,10), pady=5)
        despesas_label_value = customtkinter.CTkLabel(self.monthly_proventos_summary_frame, text=f"R$ {total_despesas_mes:.2f}", font=FONTE_NORMAL_BOLD, text_color="tomato", anchor="w")
        despesas_label_value.grid(row=1, column=1, sticky="w", padx=(0,10), pady=5)

        # Total Cartão de Crédito
        cartao_title_text = f"Cartão Crédito:"
        cartao_label_text = customtkinter.CTkLabel(self.monthly_proventos_summary_frame, text=cartao_title_text, font=FONTE_NORMAL_BOLD, anchor="w")
        cartao_label_text.grid(row=2, column=0, sticky="w", padx=(10,10), pady=5)
        cartao_label_value = customtkinter.CTkLabel(self.monthly_proventos_summary_frame, text=f"R$ {total_cartao_mes:.2f}", font=FONTE_NORMAL_BOLD, text_color="orange", anchor="w")
        cartao_label_value.grid(row=2, column=1, sticky="w", padx=(0,10), pady=5)

        # Total Pago em Conta
        conta_title_text = f"Pago em Conta:"
        conta_label_text = customtkinter.CTkLabel(self.monthly_proventos_summary_frame, text=conta_title_text, font=FONTE_NORMAL_BOLD, anchor="w")
        conta_label_text.grid(row=3, column=0, sticky="w", padx=(10,10), pady=5)
        conta_label_value = customtkinter.CTkLabel(self.monthly_proventos_summary_frame, text=f"R$ {total_conta_mes:.2f}", font=FONTE_NORMAL_BOLD, text_color="cyan", anchor="w")
        conta_label_value.grid(row=3, column=1, sticky="w", padx=(0,10), pady=5)

        # Saldo do Mês
        saldo_title_text = f"Saldo:"
        saldo_label_text = customtkinter.CTkLabel(self.monthly_proventos_summary_frame, text=saldo_title_text, font=FONTE_NORMAL_BOLD, anchor="w")
        saldo_label_text.grid(row=4, column=0, sticky="w", padx=(10,10), pady=5)
        saldo_label_value = customtkinter.CTkLabel(self.monthly_proventos_summary_frame, text=f"R$ {saldo_mes:.2f}", font=FONTE_NORMAL_BOLD, text_color=cor_saldo, anchor="w")
        saldo_label_value.grid(row=4, column=1, sticky="w", padx=(0,10), pady=5)


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
                return 0.0 # Retorna 0.0

            # 2. Obter os totais anuais (esta função pode retornar apenas categorias com transações)
            annual_transaction_totals_raw = Database.get_category_totals_for_year(self.current_user_id, selected_year, category_type)

            # 3. Criar um mapa dos totais para fácil consulta
            annual_totals_map = {item['category_name']: item['total_value'] for item in annual_transaction_totals_raw}

            # CALCULAR O TOTAL DA SEÇÃO ANTES DO LOOP
            # Este é o total de todas as transações para este category_type no ano.
            grand_total_for_section = sum(item['total_value'] for item in annual_transaction_totals_raw)

            

            table_frame = customtkinter.CTkFrame(parent_scroll_frame, fg_color="transparent")
            table_frame.pack(fill="x", padx=10)
            table_frame.grid_columnconfigure(0, weight=3) # Coluna para nome da categoria
            table_frame.grid_columnconfigure(1, weight=1, minsize=100) # Coluna para valor
            table_frame.grid_columnconfigure(2, weight=0, minsize=50)  # Coluna para % Ano

            # Cabeçalhos
            label_annual_header_cat = customtkinter.CTkLabel(table_frame, text="Categoria", font=FONTE_NORMAL_BOLD, text_color="gray60")
            label_annual_header_cat.grid(row=0, column=0, sticky="w", pady=(0,2), padx=(0,5))
            label_annual_header_tot = customtkinter.CTkLabel(table_frame, text="Total Anual", font=FONTE_NORMAL_BOLD, text_color="gray60")
            label_annual_header_tot.grid(row=0, column=1, sticky="e", pady=(0,2), padx=(0,5))
            label_annual_header_pct = customtkinter.CTkLabel(table_frame, text="(%) Ano", font=FONTE_NORMAL_BOLD, text_color="gray60")
            label_annual_header_pct.grid(row=0, column=2, sticky="e", pady=(0,2))


            # 4. Iterar sobre todas as categorias relevantes do usuário (aquelas cadastradas para ele)
            # E exibir seus totais anuais, mesmo que sejam zero.
            for i, category_data in enumerate(sorted(all_user_categories_for_type, key=lambda x: x['name'])):
                category_name = category_data["name"]
                # Pega o total do mapa. Se a categoria não teve transações no ano, será 0.0.
                total_value_for_year = annual_totals_map.get(category_name, 0.0)

                cat_name_label = customtkinter.CTkLabel(table_frame, text=category_name, font=FONTE_NORMAL, anchor="w")
                cat_name_label.grid(row=i + 1, column=0, sticky="ew", pady=1, padx=(0,5))
                
                total_val_label = customtkinter.CTkLabel(table_frame, text=f"R$ {total_value_for_year:.2f}", font=FONTE_NORMAL, anchor="e")
                total_val_label.grid(row=i + 1, column=1, sticky="ew", pady=1, padx=(0,5))

                # Calcula e exibe a porcentagem anual em relação ao grand_total_for_section
                percentage_of_total_year = (total_value_for_year / grand_total_for_section * 100) if grand_total_for_section > 0 else 0
                percentage_label = customtkinter.CTkLabel(table_frame, text=f"{percentage_of_total_year:.1f}%", font=FONTE_NORMAL, anchor="e")
                percentage_label.grid(row=i + 1, column=2, sticky="ew", pady=1)
            return grand_total_for_section # Retorna o total da seção para os cálculos de saldo.

        # Popular tabela de Despesas e obter total
        total_despesas = create_summary_section(despesa_scroll_frame, "Despesa")

        # Popular tabela de Proventos e obter total
        total_proventos = create_summary_section(provento_scroll_frame, "Provento")

        # Buscar totais anuais por meio de pagamento
        # (Assumindo que você implementará get_annual_expenses_by_payment_method em Database.py)
        # annual_payment_method_summary = Database.get_annual_expenses_by_payment_method(self.current_user_id, selected_year)
        # total_cartao_anual = annual_payment_method_summary.get("Cartão de Crédito", 0.0)
        # total_conta_anual = annual_payment_method_summary.get("Conta Corrente", 0.0)
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

        # Total Cartão Anual (Placeholder - requer get_annual_expenses_by_payment_method)
        # total_cartao_anual_label_text = customtkinter.CTkLabel(totals_summary_frame, text="Total Cartão Anual:", font=FONTE_NORMAL_BOLD, anchor="w")
        # total_cartao_anual_label_text.grid(row=2, column=0, sticky="w", padx=(0,10), pady=(0,2))
        # total_cartao_anual_label_value = customtkinter.CTkLabel(totals_summary_frame, text=f"R$ {total_cartao_anual:.2f}", font=FONTE_NORMAL_BOLD, text_color="orange", anchor="w")
        # total_cartao_anual_label_value.grid(row=2, column=1, sticky="w", pady=(0,2))

        # Total Pago em Conta Anual (Placeholder - requer get_annual_expenses_by_payment_method)
        # total_conta_anual_label_text = customtkinter.CTkLabel(totals_summary_frame, text="Total Pago em Conta Anual:", font=FONTE_NORMAL_BOLD, anchor="w")
        # total_conta_anual_label_text.grid(row=3, column=0, sticky="w", padx=(0,10), pady=(0,2))
        # total_conta_anual_label_value = customtkinter.CTkLabel(totals_summary_frame, text=f"R$ {total_conta_anual:.2f}", font=FONTE_NORMAL_BOLD, text_color="cyan", anchor="w")
        # total_conta_anual_label_value.grid(row=3, column=1, sticky="w", pady=(0,2))


        # Saldo Total Anual
        saldo_anual = total_proventos - total_despesas
        cor_saldo = "lightgreen" if saldo_anual >= 0 else "tomato"

        # Ajustar a linha do Saldo Total Anual se os campos de cartão/conta forem adicionados
        # saldo_row_index = 4 # Se os campos de cartão/conta forem descomentados
        saldo_row_index = 2 # Se os campos de cartão/conta permanecerem comentados
        saldo_total_label_text = customtkinter.CTkLabel(totals_summary_frame, text="Saldo Total Anual:", font=FONTE_NORMAL_BOLD, anchor="w")
        saldo_total_label_text.grid(row=saldo_row_index, column=0, sticky="w", padx=(0,10), pady=(2,0)) # pady superior para separar
        saldo_total_label_value = customtkinter.CTkLabel(totals_summary_frame, text=f"R$ {saldo_anual:.2f}", font=FONTE_NORMAL_BOLD, text_color=cor_saldo, anchor="w")
        saldo_total_label_value.grid(row=saldo_row_index, column=1, sticky="w", pady=(2,0))

    def load_monthly_details_for_list_container(self):
        # Limpa o conteúdo anterior do list_container_frame
        for widget in self.list_container_frame.winfo_children():
            widget.destroy()

        if self.selected_month_index is None:
            self.list_container_title_label.configure(text="Detalhes do Mês")
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

        # Calcula os totais de despesas e proventos do mês para o cálculo da porcentagem
        total_despesas_mes = sum(item['total_value'] for item in monthly_data_raw if item['category_type'] == 'Despesa')
        total_proventos_mes = sum(item['total_value'] for item in monthly_data_raw if item['category_type'] == 'Provento')

        # Mapeia os totais por nome da categoria e tipo para fácil acesso
        monthly_totals_map = {}
        for item in monthly_data_raw:
            key = (item['category_name'], item['category_type'])
            monthly_totals_map[key] = item['total_value']

        # Cabeçalhos
        header_frame = customtkinter.CTkFrame(self.list_container_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(5,2))
        header_frame.grid_columnconfigure(0, weight=3) # Categoria (mais peso)
        header_frame.grid_columnconfigure(1, weight=1, minsize=100) # Valor no Mês
        header_frame.grid_columnconfigure(2, weight=0, minsize=50)  # % Mês

        label_header_cat_monthly = customtkinter.CTkLabel(header_frame, text="Categoria", font=FONTE_NORMAL_BOLD, text_color="gray60")
        label_header_cat_monthly.grid(row=0, column=0, sticky="w", padx=(0,5))
        label_header_val_monthly = customtkinter.CTkLabel(header_frame, text="Valor no Mês", font=FONTE_NORMAL_BOLD, text_color="gray60")
        label_header_val_monthly.grid(row=0, column=1, sticky="e", padx=(0,5))
        label_header_pct_monthly = customtkinter.CTkLabel(header_frame, text="(%) Mês", font=FONTE_NORMAL_BOLD, text_color="gray60")
        label_header_pct_monthly.grid(row=0, column=2, sticky="e")


        has_content = False
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
            item_frame.grid_columnconfigure(1, weight=1, minsize=100) # Valor
            item_frame.grid_columnconfigure(2, weight=0, minsize=50)  # % Mês

            # Label da Categoria com a cor da fonte definida
            label_cat_item = customtkinter.CTkLabel(item_frame, text=f"{category_name}", font=FONTE_NORMAL, anchor="w", text_color=font_color, corner_radius=3)
            label_cat_item.grid(row=0, column=0, sticky="ew", padx=(3,5))
            
            # Label do Valor com a cor da fonte definida
            label_val_item = customtkinter.CTkLabel(item_frame, text=f"R$ {total_value_for_month:.2f}", font=FONTE_NORMAL, anchor="e", text_color=font_color)
            label_val_item.grid(row=0, column=1, sticky="ew", padx=(0,5))
            
            # Calcula e exibe a porcentagem mensal
            percentage_of_month_total = 0
            if category_type == "Despesa" and total_despesas_mes > 0:
                percentage_of_month_total = (total_value_for_month / total_despesas_mes * 100)
            elif category_type == "Provento" and total_proventos_mes > 0:
                percentage_of_month_total = (total_value_for_month / total_proventos_mes * 100)
            
            customtkinter.CTkLabel(item_frame, text=f"{percentage_of_month_total:.1f}%", font=FONTE_NORMAL, anchor="e", text_color=font_color).grid(row=0, column=2, sticky="ew")
            has_content = True

        if not has_content and not monthly_data_raw: # Se nenhuma categoria foi iterada E não há dados brutos
            customtkinter.CTkLabel(self.list_container_frame, text="Nenhuma transação ou categoria para este mês.", font=FONTE_NORMAL, text_color="gray60").pack(pady=20, padx=10)
            
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
        # Apenas atualiza se a UI do dashboard estiver visível (ou seja, os widgets existem)
        if hasattr(self, 'annual_list_container_frame') and self.annual_list_container_frame.winfo_exists():
            self.load_annual_category_summaries()
            self._load_annual_pie_chart_data()
            self.load_monthly_details_for_list_container()
            self.load_monthly_proventos_summary()
            self._load_monthly_pie_chart_data()

if __name__ == "__main__":
    app = Dashboard(user_id="test_user_01") # Passa um user_id para teste
    app.mainloop()