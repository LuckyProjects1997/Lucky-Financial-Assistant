# form_cadastro_categoria.py
import customtkinter
from tkinter.colorchooser import askcolor # Para o seletor de cores
import tkinter as tk # Necessário para o colorchooser funcionar corretamente com CTk

import uuid # Para gerar IDs únicos
import Database # Usando 'Database' com D maiúsculo conforme seu Main.py

# Definições de fonte padrão para o Formulário de Cadastro de Categoria
FONTE_FAMILIA = "Segoe UI"
FONTE_TITULO_FORM = (FONTE_FAMILIA, 18, "bold")
FONTE_LABEL_FORM = (FONTE_FAMILIA, 13)
FONTE_INPUT_FORM = (FONTE_FAMILIA, 13)
FONTE_BOTAO_FORM = (FONTE_FAMILIA, 13, "bold")
FONTE_LISTA_CATEGORIA = (FONTE_FAMILIA, 12)
BOTAO_CORNER_RADIUS = 17 # Para cantos bem arredondados
BOTAO_FG_COLOR = "gray30" # Cor padrão dos botões (igual ao Dashboard)
BOTAO_HOVER_COLOR = "#2196F3" # Cor hover dos botões (igual ao Dashboard)
BOTAO_HEIGHT = 35
COR_CONTAINER_INTERNO_FORM = "#222222" # Cinza mais escuro para containers internos

class FormCadastroCategoriaWindow(customtkinter.CTkToplevel):
    def __init__(self, master=None, current_user_id=None, on_close_callback=None):
        super().__init__(master)
        self.title("Cadastrar Categoria")
        self.geometry("400x550") # Tamanho inicial ajustado
        self.configure(fg_color="#1c1c1c") # Define o fundo da janela
        self.lift() # Traz a janela para frente
        self.attributes("-topmost", True) # Mantém no topo temporariamente
        self.grab_set() # Impede interações com a janela pai até esta ser fechada

        self.minsize(380, 450) # Define um tamanho mínimo

        self.current_user_id = current_user_id # ID do usuário logado, para vincular categorias
        self.editing_category_id = None # Para rastrear qual categoria está sendo editada
        self.on_close_callback = on_close_callback # Callback a ser chamado quando a janela for fechada
        self.selected_color_hex = "#FFFFFF" # Cor padrão (branco)

        self._setup_ui()
        self.load_categories_list() # Carrega a lista de categorias ao iniciar
        self.clear_category_form() # Limpa o formulário para um novo cadastro e ajusta botões de ação
        self._set_category_input_state("normal") # Campos começam habilitados nesta janela

    def _setup_ui(self):
        # --- Frame Principal ---
        main_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1) # Para centralizar o conteúdo
        main_frame.grid_rowconfigure(0, weight=0) # Título
        main_frame.grid_rowconfigure(1, weight=0) # Formulário
        main_frame.grid_rowconfigure(2, weight=0) # Lista Label
        main_frame.grid_rowconfigure(3, weight=1) # Lista Frame (expande)
        main_frame.grid_rowconfigure(4, weight=0) # Botão Fechar

        title_label = customtkinter.CTkLabel(main_frame, text="Cadastrar Categoria", font=FONTE_TITULO_FORM)
        title_label.grid(row=0, column=0, pady=(0, 20), sticky="ew")

        # Frame interno para o formulário de cadastro/edição de categoria
        self.category_form_content_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        self.category_form_content_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0,10))
        self.category_form_content_frame.grid_columnconfigure(0, weight=1) # Para centralizar o botão

        # Nome da Categoria
        category_name_label = customtkinter.CTkLabel(self.category_form_content_frame, text="Nome da Categoria:", font=FONTE_LABEL_FORM)
        category_name_label.grid(row=0, column=0, pady=(5,2), padx=10, sticky="w")
        self.category_name_entry = customtkinter.CTkEntry(self.category_form_content_frame, placeholder_text="Ex: Alimentação", height=35, font=FONTE_INPUT_FORM)
        self.category_name_entry.grid(row=1, column=0, sticky="ew", padx=10, pady=(0,10))

        # Tipo da Categoria
        category_type_label = customtkinter.CTkLabel(self.category_form_content_frame, text="Tipo:", font=FONTE_LABEL_FORM)
        category_type_label.grid(row=2, column=0, pady=(5,2), padx=10, sticky="w")
        self.category_type_combobox = customtkinter.CTkComboBox(self.category_form_content_frame, values=["Despesa", "Provento"], height=35, font=FONTE_INPUT_FORM)
        self.category_type_combobox.set("Despesa") # Valor padrão
        self.category_type_combobox.grid(row=3, column=0, sticky="ew", padx=10, pady=(0,10))

        # Seletor de Cor
        color_selection_frame = customtkinter.CTkFrame(self.category_form_content_frame, fg_color="transparent")
        color_selection_frame.grid(row=4, column=0, sticky="ew", padx=10, pady=(5,10))
        color_selection_frame.grid_columnconfigure(0, weight=0) # Label "Cor:"
        color_selection_frame.grid_columnconfigure(1, weight=0) # Preview da cor
        color_selection_frame.grid_columnconfigure(2, weight=1) # Botão "Escolher Cor" (expande)

        color_label = customtkinter.CTkLabel(color_selection_frame, text="Cor:", font=FONTE_LABEL_FORM)
        color_label.grid(row=0, column=0, padx=(0,5), sticky="w", pady=5)

        self.color_preview_label = customtkinter.CTkLabel(color_selection_frame, text="", fg_color=self.selected_color_hex, width=35, height=35, corner_radius=5)
        self.color_preview_label.grid(row=0, column=1, padx=(0,10), sticky="w", pady=5)
        
        choose_color_button = customtkinter.CTkButton(color_selection_frame, text="Escolher Cor", command=self.choose_color,
                                                      height=BOTAO_HEIGHT, font=FONTE_BOTAO_FORM, corner_radius=BOTAO_CORNER_RADIUS,
                                                      fg_color=BOTAO_FG_COLOR, hover_color=BOTAO_HOVER_COLOR)
        choose_color_button.grid(row=0, column=2, sticky="e", pady=5)

        # Frame para os botões de ação do formulário de categoria
        category_action_buttons_frame = customtkinter.CTkFrame(self.category_form_content_frame, fg_color="transparent")
        category_action_buttons_frame.grid(row=5, column=0, pady=(10,15), sticky="ew")
        category_action_buttons_frame.grid_columnconfigure(0, weight=1) # Espaço à esquerda
        category_action_buttons_frame.grid_columnconfigure(1, weight=0) # Botão Salvar/Atualizar
        category_action_buttons_frame.grid_columnconfigure(2, weight=0) # Botão Excluir
        category_action_buttons_frame.grid_columnconfigure(3, weight=1) # Espaço à direita


        # Botão Salvar/Atualizar
        self.save_category_button = customtkinter.CTkButton(category_action_buttons_frame, text="Salvar", command=self.save_new_category,
                                                       height=BOTAO_HEIGHT, font=FONTE_BOTAO_FORM, corner_radius=BOTAO_CORNER_RADIUS,
                                                       fg_color=BOTAO_FG_COLOR, hover_color=BOTAO_HOVER_COLOR)
        self.save_category_button.grid(row=0, column=1, padx=5)

        self.delete_category_button = customtkinter.CTkButton(category_action_buttons_frame, text="Excluir", command=self.confirm_delete_category,
                                                              height=BOTAO_HEIGHT, font=FONTE_BOTAO_FORM, corner_radius=BOTAO_CORNER_RADIUS,
                                                              fg_color="#c0392b", hover_color="#e74c3c") # Cores para indicar perigo/exclusão
        # O grid do delete_category_button será gerenciado por on_category_click e clear_category_form

        # --- Lista de Categorias Existentes ---
        category_list_label = customtkinter.CTkLabel(main_frame, text="Categorias Cadastradas:", font=FONTE_TITULO_FORM)
        category_list_label.grid(row=2, column=0, pady=(10, 5), padx=10, sticky="w")

        self.category_list_frame = customtkinter.CTkScrollableFrame(main_frame, fg_color="transparent", height=210) # Altura máxima de 210px
        self.category_list_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=(0,10)) # sticky="nsew" para expandir
        self.category_list_frame.grid_columnconfigure(0, weight=1) # Para centralizar itens na lista

        # Botão Fechar
        bottom_buttons_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        bottom_buttons_frame.grid(row=4, column=0, pady=(10,0), sticky="ew")
        bottom_buttons_frame.grid_columnconfigure(0, weight=1) # Para centralizar o botão Fechar

        close_button = customtkinter.CTkButton(bottom_buttons_frame, text="Fechar", command=self.handle_close_action,
                                                height=BOTAO_HEIGHT, font=FONTE_BOTAO_FORM, corner_radius=BOTAO_CORNER_RADIUS,
                                                fg_color="gray50", hover_color="gray40")
        close_button.grid(row=0, column=0, pady=(5,0)) # Centralizado

    def _find_widget_by_text(self, parent, text_to_find):
        """
        Busca recursivamente um widget com um texto específico dentro de um frame pai.
        Retorna o widget se encontrado, caso contrário None.
        """
        for widget in parent.winfo_children():
            if isinstance(widget, (customtkinter.CTkButton, customtkinter.CTkLabel)):
                if hasattr(widget, 'cget') and widget.cget('text') == text_to_find:
                    return widget
            if isinstance(widget, (customtkinter.CTkFrame, customtkinter.CTkScrollableFrame)):
                found = self._find_widget_by_text(widget, text_to_find)
                if found:
                    return found
        return None

    def choose_color(self):
        temp_root = tk.Tk()
        temp_root.withdraw()
        temp_root.attributes("-topmost", True)

        color_code = askcolor(title="Escolha uma cor para a categoria", parent=self)
        temp_root.destroy()

        if color_code and color_code[1]:
            self.selected_color_hex = color_code[1]
            self.color_preview_label.configure(fg_color=self.selected_color_hex)
            print(f"Cor selecionada: {self.selected_color_hex}")
        self.lift()
        self.attributes("-topmost", True)
        self.focus_force()

    def _set_category_input_state(self, state):
        """Define o estado (normal/disabled) dos campos de entrada e seleção de cor da seção de categoria."""
        self.category_name_entry.configure(state=state)
        self.category_type_combobox.configure(state=state)
        choose_color_button = self._find_widget_by_text(self.category_form_content_frame, "Escolher Cor")
        if choose_color_button:
            choose_color_button.configure(state=state)

    def save_new_category(self):
        category_name = self.category_name_entry.get().strip()
        category_type = self.category_type_combobox.get()
        category_color = self.selected_color_hex

        if not category_name:
            print("Nome da categoria não pode ser vazio.") # TODO: Mostrar alerta na GUI
            return
        
        if not self.current_user_id:
            print("Nenhum usuário logado para associar a categoria.") # TODO: Mostrar alerta na GUI
            return

        if self.editing_category_id:
            print(f"Tentando ATUALIZAR categoria ID: {self.editing_category_id} para Nome: {category_name}, Tipo: {category_type}, Cor: {category_color}")
            success = Database.update_category(self.editing_category_id, category_name, category_type, category_color)
            if success:
                print("Categoria atualizada com sucesso!") # TODO: Mostrar alerta na GUI
                self.clear_category_form()
                self.load_categories_list()
            else:
                 print("Falha ao atualizar categoria.") # TODO: Mostrar alerta na GUI
        else:
            new_category_id = str(uuid.uuid4())
            print(f"Tentando SALVAR nova categoria: {category_name}, Tipo: {category_type}, Cor: {category_color}, Usuário ID: {self.current_user_id}, ID Gerado: {new_category_id}")
            success = Database.add_category(new_category_id, self.current_user_id, category_name, category_type, category_color)
            if success:
                print("Nova categoria salva com sucesso!") # TODO: Mostrar alerta na GUI
                self.clear_category_form()
                self.load_categories_list()
            else:
                print("Falha ao salvar nova categoria.") # TODO: Mostrar alerta na GUI

    def load_categories_list(self):
        for widget in self.category_list_frame.winfo_children():
            widget.destroy()

        if not self.current_user_id:
            customtkinter.CTkLabel(self.category_list_frame, text="Nenhum usuário logado.").pack(pady=5)
            return

        categories = Database.get_categories_by_user(self.current_user_id)

        if not categories:
            customtkinter.CTkLabel(self.category_list_frame, text="Nenhuma categoria cadastrada.").pack(pady=5)
        else:
            for category in categories:
                text_color = "white"
                category_bg_color_lower = category['color'].lower()
                if category_bg_color_lower == "#ffffff" or category_bg_color_lower == "white":
                    text_color = "black"
                elif category_bg_color_lower == "#000000" or category_bg_color_lower == "black":
                    text_color = "white"

                cat_label = customtkinter.CTkLabel(self.category_list_frame, text=f"{category['name']} ({category['type']})",
                                                   fg_color=category['color'], text_color=text_color,
                                                   font=FONTE_LISTA_CATEGORIA, corner_radius=5, padx=10, pady=5)
                cat_label.pack(fill="x", pady=2, padx=5)
                cat_label.bind("<Button-1>", lambda event, cat=category: self.on_category_click(event, cat))

    def on_category_click(self, event, category_data):
        print(f"Categoria clicada: {category_data['name']}")
        self.editing_category_id = category_data['id']

        self.category_name_entry.delete(0, customtkinter.END)
        self.category_name_entry.insert(0, category_data['name'])
        
        self.category_type_combobox.set(category_data['type'])
        
        self.selected_color_hex = category_data['color']
        self.color_preview_label.configure(fg_color=self.selected_color_hex)

        self.save_category_button.configure(text="Atualizar")
        self.delete_category_button.grid(row=0, column=2, padx=5) # Mostra o botão de excluir ao lado do Salvar/Atualizar
        
    def clear_category_form(self):
        self.editing_category_id = None
        self.category_name_entry.delete(0, customtkinter.END)
        self.category_name_entry.insert(0, "")
        self.category_type_combobox.set("Despesa")
        self.selected_color_hex = "#FFFFFF"
        self.color_preview_label.configure(fg_color=self.selected_color_hex)
        self.save_category_button.configure(text="Salvar")
        self.delete_category_button.grid_remove()
        print("Formulário de categoria limpo.")

    def confirm_delete_category(self):
        if not self.editing_category_id:
            print("Nenhuma categoria selecionada para excluir.")
            return

        category_name_to_delete = self.category_name_entry.get()
        print(f"Você tem certeza que deseja excluir a categoria '{category_name_to_delete}' (ID: {self.editing_category_id})?")
        success = Database.delete_category(self.editing_category_id)
        if success:
            print("Categoria excluída com sucesso!")
            self.clear_category_form()
            self.load_categories_list()
        else:
            print("Falha ao excluir categoria.")

    def handle_close_action(self):
        if self.on_close_callback:
            self.on_close_callback()
        self.destroy()