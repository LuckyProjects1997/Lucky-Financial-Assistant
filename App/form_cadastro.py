# form_cadastro.py
import customtkinter
from tkinter.colorchooser import askcolor # Para o seletor de cores
import tkinter as tk # Necessário para o colorchooser funcionar corretamente com CTk

import datetime # Para obter a data atual
import uuid # Para gerar IDs únicos
# Importa as funções do banco de dados
import Database # Usando 'Database' com D maiúsculo conforme seu Main.py

# Definições de fonte padrão para o Formulário de Cadastro
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
COR_CONTAINER_INTERNO_FORM = "#222222" # Cinza mais escuro para containers internos, próximo ao fundo da janela

class FormCadastroWindow(customtkinter.CTkToplevel):
    def __init__(self, master=None, current_user_id=None):
        super().__init__(master)
        self.title("Cadastros")
        self.geometry("500x600") # Tamanho inicial da janela
        self.configure(fg_color="#1c1c1c") # Define o fundo da janela de cadastro
        self.lift() # Traz a janela para frente
        # self.attributes("-topmost", True) # Pode ser irritante, remover ou usar com cautela
        self.attributes("-topmost", True) # Mantém no topo temporariamente
        self.grab_set() # Impede interações com a janela pai até esta ser fechada

        self.minsize(480, 500) # Define um tamanho mínimo para a janela de formulário

        self.current_user_id = current_user_id # ID do usuário logado, para vincular categorias
        self.editing_category_id = None # Para rastrear qual categoria está sendo editada
        self.on_close_callback = None # Callback a ser chamado quando a janela for fechada

        # --- Frame Principal ---
        # Adicionando um pouco de padding interno ao frame principal da janela
        main_frame = customtkinter.CTkFrame(self, fg_color="transparent") # Tornando transparente para usar a cor da janela
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        # Configurar as linhas do main_frame para que o category_content_frame possa expandir
        main_frame.grid_rowconfigure(0, weight=0) # user_toggle_button
        main_frame.grid_rowconfigure(1, weight=0) # user_form_content_frame (se visível)
        main_frame.grid_rowconfigure(2, weight=0) # category_toggle_button
        main_frame.grid_rowconfigure(3, weight=1) # category_content_frame (se visível, deve expandir)
        # main_frame.grid_rowconfigure(4, weight=0) # Linha removida para transaction_toggle_button
        main_frame.grid_rowconfigure(4, weight=0) # close_button
        main_frame.grid_columnconfigure(0, weight=1) # Para centralizar o conteúdo que usa grid

        # --- Seção de Cadastro de Usuário ---
        # Botão para expandir/colapsar a seção de usuário
        self.user_toggle_button = customtkinter.CTkButton(main_frame, text="Usuário", font=FONTE_TITULO_FORM,
                                                          command=self.toggle_user_form, corner_radius=10, fg_color=COR_CONTAINER_INTERNO_FORM,
                                                          hover_color="#333333") # Um hover sutil
        self.user_toggle_button.grid(row=0, column=0, pady=(0, 5), sticky="ew", padx=10)

        # Frame que contém o formulário de usuário (inicialmente escondido)
        self.user_form_content_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent") # Transparente para usar a cor do toggle button
        # Não empacotamos aqui; será feito em toggle_user_form

        user_name_label = customtkinter.CTkLabel(self.user_form_content_frame, text="Nome do Usuário:", font=FONTE_LABEL_FORM)
        user_name_label.pack(pady=(5,2), padx=20, anchor="w")
        self.user_name_entry = customtkinter.CTkEntry(self.user_form_content_frame, placeholder_text="Ex: João Silva", height=35, font=FONTE_INPUT_FORM)
        self.user_name_entry.pack(fill="x", padx=20, pady=(0,15))

        # TODO: Adicionar campo para ID do usuário se for manual, ou gerar automaticamente.
        # Por enquanto, vamos focar no nome.

        save_user_button = customtkinter.CTkButton(self.user_form_content_frame, text="Salvar Usuário", command=self.save_new_user,
                                                   height=BOTAO_HEIGHT, font=FONTE_BOTAO_FORM, corner_radius=BOTAO_CORNER_RADIUS,
                                                   fg_color=BOTAO_FG_COLOR, hover_color=BOTAO_HOVER_COLOR)
        save_user_button.pack(pady=(0,15))

        # --- Seção de Cadastro de Categoria ---
        # Botão para expandir/colapsar a seção de categoria
        self.category_toggle_button = customtkinter.CTkButton(main_frame, text="Categoria", font=FONTE_TITULO_FORM,
                                                              command=self.toggle_category_form, corner_radius=10, fg_color=COR_CONTAINER_INTERNO_FORM,
                                                              hover_color="#333333") # Um hover sutil
        self.category_toggle_button.grid(row=2, column=0, pady=(10, 5), sticky="ew", padx=10)

        # Frame que contém o formulário de categoria E a lista (inicialmente escondido)
        self.category_content_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent") # Transparente para usar a cor do toggle button
        self.category_content_frame.grid_columnconfigure(0, weight=1) # Para centralizar o botão
        self.category_content_frame.grid_rowconfigure(0, weight=0) # category_form_content_frame
        self.category_content_frame.grid_rowconfigure(1, weight=0) # category_list_label
        self.category_content_frame.grid_rowconfigure(2, weight=1) # category_list_frame (esta linha deve expandir)
        # Não empacotamos aqui; será feito em toggle_category_form

        # Frame interno para o formulário de cadastro/edição de categoria
        self.category_form_content_frame = customtkinter.CTkFrame(self.category_content_frame, fg_color="transparent")
        self.category_form_content_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(0,10))
        self.category_form_content_frame.grid_columnconfigure(0, weight=1) # Para centralizar o botão

        category_name_label = customtkinter.CTkLabel(self.category_form_content_frame, text="Nome da Categoria:", font=FONTE_LABEL_FORM)
        category_name_label.grid(row=0, column=0, pady=(5,2), padx=10, sticky="w")
        self.category_name_entry = customtkinter.CTkEntry(self.category_form_content_frame, placeholder_text="Ex: Alimentação", height=35, font=FONTE_INPUT_FORM)
        self.category_name_entry.grid(row=1, column=0, sticky="ew", padx=10, pady=(0,10))

        category_type_label = customtkinter.CTkLabel(self.category_form_content_frame, text="Tipo:", font=FONTE_LABEL_FORM)
        category_type_label.grid(row=2, column=0, pady=(5,2), padx=10, sticky="w")
        self.category_type_combobox = customtkinter.CTkComboBox(self.category_form_content_frame, values=["Despesa", "Provento"], height=35, font=FONTE_INPUT_FORM)
        self.category_type_combobox.set("Despesa") # Valor padrão
        self.category_type_combobox.grid(row=3, column=0, sticky="ew", padx=10, pady=(0,10))

        # Seletor de Cor
        color_selection_frame = customtkinter.CTkFrame(self.category_form_content_frame, fg_color="transparent")
        color_selection_frame.grid(row=4, column=0, sticky="ew", padx=10, pady=(5,10))
        # Configurar colunas para o frame de seleção de cor para alinhar os elementos
        color_selection_frame.grid_columnconfigure(0, weight=0) # Label "Cor:"
        color_selection_frame.grid_columnconfigure(1, weight=0) # Preview da cor
        color_selection_frame.grid_columnconfigure(2, weight=1) # Botão "Escolher Cor" (expande para preencher)

        color_label = customtkinter.CTkLabel(color_selection_frame, text="Cor:", font=FONTE_LABEL_FORM)
        color_label.grid(row=0, column=0, padx=(0,5), sticky="w", pady=5)

        self.selected_color_hex = "#FFFFFF" # Cor padrão (branco)
        self.color_preview_label = customtkinter.CTkLabel(color_selection_frame, text="", fg_color=self.selected_color_hex, width=35, height=35, corner_radius=5)
        self.color_preview_label.grid(row=0, column=1, padx=(0,10), sticky="w", pady=5)
        
        choose_color_button = customtkinter.CTkButton(color_selection_frame, text="Escolher Cor", command=self.choose_color,
                                                      height=BOTAO_HEIGHT, font=FONTE_BOTAO_FORM, corner_radius=BOTAO_CORNER_RADIUS,
                                                      fg_color=BOTAO_FG_COLOR, hover_color=BOTAO_HOVER_COLOR)
        choose_color_button.grid(row=0, column=2, sticky="e", pady=5)

        # TODO: Adicionar campo para ID da categoria se for manual, ou gerar automaticamente.

        self.save_category_button = customtkinter.CTkButton(self.category_form_content_frame, text="Salvar Categoria", command=self.save_new_category,
                                                       height=BOTAO_HEIGHT, font=FONTE_BOTAO_FORM, corner_radius=BOTAO_CORNER_RADIUS,
                                                       fg_color=BOTAO_FG_COLOR, hover_color=BOTAO_HOVER_COLOR)
        self.save_category_button.grid(row=5, column=0, pady=(5,15)) # Centralizado por padrão

        # Botão para Excluir Categoria (inicialmente escondido)
        self.delete_category_button = customtkinter.CTkButton(self.category_form_content_frame, text="Excluir Categoria", command=self.confirm_delete_category,
                                                              height=BOTAO_HEIGHT, font=FONTE_BOTAO_FORM, corner_radius=BOTAO_CORNER_RADIUS,
                                                              fg_color="#c0392b", hover_color="#e74c3c") # Cores para indicar perigo/exclusão
        # Não usamos grid() aqui, ele será gerenciado dinamicamente

        # --- Lista de Categorias Existentes ---
        category_list_label = customtkinter.CTkLabel(self.category_content_frame, text="Categorias Cadastradas:", font=FONTE_TITULO_FORM)
        category_list_label.grid(row=1, column=0, pady=(10, 5), padx=10, sticky="w")

        self.category_list_frame = customtkinter.CTkScrollableFrame(self.category_content_frame, fg_color="transparent", height=210) # Altura máxima de 210px
        self.category_list_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0,10)) # sticky="nsew" para expandir
        self.category_list_frame.grid_columnconfigure(0, weight=1) # Para centralizar itens na lista

        # Carregar a lista de categorias ao abrir a seção
        # self.load_categories_list() # Carregado quando a seção de categoria é expandida

        # Botão Fechar
        close_button = customtkinter.CTkButton(main_frame, text="Fechar", command=self.handle_close_action, height=BOTAO_HEIGHT, font=FONTE_BOTAO_FORM, corner_radius=BOTAO_CORNER_RADIUS, fg_color=BOTAO_FG_COLOR, hover_color=BOTAO_HOVER_COLOR)
        close_button.grid(row=4, column=0, pady=(20,0), sticky="s") # Usa grid, sticky="s" para alinhar ao sul (bottom)

    def choose_color(self):
        # É necessário um root Tkinter temporário para o color chooser funcionar bem com CTk Toplevel
        # Esta é uma peculiaridade do colorchooser do tkinter.
        temp_root = tk.Tk()
        temp_root.withdraw() # Esconde a janela root do Tkinter
        temp_root.attributes("-topmost", True) # Tenta manter o color chooser no topo

        color_code = askcolor(title="Escolha uma cor para a categoria", parent=self) # parent=self para tentar associar ao CTkToplevel
        temp_root.destroy() # Destrói a janela root temporária

        if color_code and color_code[1]: # color_code[1] é o código hexadecimal
            self.selected_color_hex = color_code[1]
            self.color_preview_label.configure(fg_color=self.selected_color_hex)
            print(f"Cor selecionada: {self.selected_color_hex}")
        self.lift() # Traz a janela de cadastro de volta para frente
        self.attributes("-topmost", True) # Reafirma que está no topo
        self.focus_force() # Força o foco de volta

    def toggle_user_form(self):
        """Expande ou colapsa a seção de cadastro de usuário."""
        if self.user_form_content_frame.winfo_ismapped(): # Verifica se o frame está visível
            self.user_form_content_frame.grid_forget() # Esconde o frame
            self.user_toggle_button.configure(text="Usuário")
        else:
            self.user_form_content_frame.grid(row=1, column=0, pady=(0, 10), sticky="ew", padx=10) # Mostra o frame
            self.user_toggle_button.configure(text="Usuário ")
            self.user_form_content_frame.lift() # Garante que está acima de outros widgets no main_frame

    def toggle_category_form(self):
        """Expande ou colapsa a seção de gerenciamento de categorias."""
        if self.category_content_frame.winfo_ismapped(): # Verifica se o frame está visível
            self.category_content_frame.grid_forget() # Esconde o frame
            self.category_toggle_button.configure(text="Categoria")
        else:
            self.category_content_frame.grid(row=3, column=0, pady=10, sticky="ew", padx=10) # Mostra o frame, mas não expande verticalmente além do seu conteúdo
            self.category_toggle_button.configure(text="Categoria")
            self.category_content_frame.lift() # Garante que está acima de outros widgets no main_frame
            self.load_categories_list() # Carrega a lista quando a seção é expandida

    def save_new_user(self):
        user_name = self.user_name_entry.get().strip() # Obtém o nome e remove espaços em branco
        if not user_name:
            print("Nome do usuário não pode ser vazio.") # TODO: Mostrar alerta na GUI
            return

        # Gera um ID único para o novo usuário
        new_user_id = str(uuid.uuid4()) # Gera um UUID único

        print(f"Tentando SALVAR novo usuário: {user_name}, ID Gerado: {new_user_id}")
        success = Database.add_user(new_user_id, user_name)

        if success:
            print("Novo usuário salvo com sucesso!") # TODO: Mostrar alerta na GUI
            self.user_name_entry.delete(0, customtkinter.END) # Limpa o campo de nome
            # TODO: Mecanismo para atualizar a ComboBox de usuários na tela de Login (complexo devido às bibliotecas diferentes)
            # Por enquanto, o novo usuário aparecerá na próxima vez que a tela de Login for aberta.
        else:
            print("Falha ao salvar novo usuário (possivelmente ID já existe, embora UUID seja improvável).") # TODO: Mostrar alerta na GUI


    def save_new_category(self):
        category_name = self.category_name_entry.get().strip() # Remove espaços em branco
        category_type = self.category_type_combobox.get()
        category_color = self.selected_color_hex

        if not category_name:
            print("Nome da categoria não pode ser vazio.") # TODO: Mostrar alerta na GUI
            return
        
        if not self.current_user_id:
            print("Nenhum usuário logado para associar a categoria.") # TODO: Mostrar alerta na GUI
            return

        # TODO: Lógica para gerar/solicitar ID da categoria.
        if self.editing_category_id:
            # Atualizar categoria existente
            print(f"Tentando ATUALIZAR categoria ID: {self.editing_category_id} para Nome: {category_name}, Tipo: {category_type}, Cor: {category_color}")
            success = Database.update_category(self.editing_category_id, category_name, category_type, category_color)
            if success:
                print("Categoria atualizada com sucesso!") # TODO: Mostrar alerta na GUI
                self.clear_category_form() # Limpa o formulário após atualizar
                self.load_categories_list() # Recarrega a lista
            else:
                 print("Falha ao atualizar categoria.") # TODO: Mostrar alerta na GUI
        else:
            # Salvar nova categoria
            # TODO: Gerar um ID único para a nova categoria
            # Exemplo simples (NÃO USAR EM PRODUÇÃO sem garantir unicidade):
            import uuid
            new_category_id = str(uuid.uuid4()) # Gera um UUID único

            print(f"Tentando SALVAR nova categoria: {category_name}, Tipo: {category_type}, Cor: {category_color}, Usuário ID: {self.current_user_id}, ID Gerado: {new_category_id}")
            success = Database.add_category(new_category_id, self.current_user_id, category_name, category_type, category_color)
            if success:
                print("Nova categoria salva com sucesso!") # TODO: Mostrar alerta na GUI
                self.clear_category_form() # Limpa o formulário após salvar
                self.load_categories_list() # Recarrega a lista
            else:
                print("Falha ao salvar nova categoria.") # TODO: Mostrar alerta na GUI

    def load_categories_list(self):
        """Carrega e exibe a lista de categorias para o usuário atual."""
        # Limpa a lista atual
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
                # Define a cor do texto com base na cor de fundo da categoria
                text_color = "white" # Padrão para a maioria das cores de fundo
                category_bg_color_lower = category['color'].lower()
                if category_bg_color_lower == "#ffffff" or category_bg_color_lower == "white":
                    text_color = "black"
                elif category_bg_color_lower == "#000000" or category_bg_color_lower == "black":
                    text_color = "white"

                # Cria um label para cada categoria com a cor de fundo e associa o clique
                cat_label = customtkinter.CTkLabel(self.category_list_frame, text=f"{category['name']} ({category['type']})",
                                                   fg_color=category['color'], text_color=text_color,
                                                   font=FONTE_LISTA_CATEGORIA, corner_radius=5, padx=10, pady=5)
                cat_label.pack(fill="x", pady=2, padx=5)
                # Associa o clique ao método on_category_click, passando os dados da categoria
                cat_label.bind("<Button-1>", lambda event, cat=category: self.on_category_click(event, cat))

    def on_category_click(self, event, category_data):
        """Preenche o formulário de categoria com os dados da categoria clicada."""
        print(f"Categoria clicada: {category_data['name']}")
        self.editing_category_id = category_data['id'] # Define o ID da categoria que está sendo editada

        # Preenche os campos do formulário
        self.category_name_entry.delete(0, customtkinter.END)
        self.category_name_entry.insert(0, category_data['name'])
        
        self.category_type_combobox.set(category_data['type'])
        
        self.selected_color_hex = category_data['color']
        self.color_preview_label.configure(fg_color=self.selected_color_hex)

        # Altera o texto do botão para indicar que está atualizando
        self.save_category_button.configure(text="Atualizar Categoria")
        self.delete_category_button.grid(row=7, column=0, pady=(0,15))

    def clear_category_form(self):
        """Limpa o formulário de categoria para adicionar uma nova."""
        self.editing_category_id = None # Reseta o ID de edição
        self.category_name_entry.delete(0, customtkinter.END)
        self.category_name_entry.insert(0, "") # Limpa o campo de nome
        self.category_type_combobox.set("Despesa") # Reseta para o valor padrão
        self.selected_color_hex = "#FFFFFF" # Reseta a cor para branco
        self.color_preview_label.configure(fg_color=self.selected_color_hex)
        self.save_category_button.configure(text="Salvar Categoria") # Reseta o texto do botão
        # Esconde o botão Excluir
        self.delete_category_button.grid_remove()
        print("Formulário de categoria limpo.")

    def confirm_delete_category(self):
        """Pede confirmação antes de excluir uma categoria."""
        if not self.editing_category_id:
            print("Nenhuma categoria selecionada para excluir.")
            return

        # TODO: Usar uma caixa de diálogo de confirmação mais robusta (ex: CTkMessagebox)
        # Por enquanto, usando um print e procedendo. Em um app real, uma confirmação visual é crucial.
        category_name_to_delete = self.category_name_entry.get()
        print(f"Você tem certeza que deseja excluir a categoria '{category_name_to_delete}' (ID: {self.editing_category_id})?")
        # if messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir a categoria '{category_name_to_delete}'?"):
        success = Database.delete_category(self.editing_category_id)
        if success:
            print("Categoria excluída com sucesso!")
            self.clear_category_form()
            self.load_categories_list()
        else:
            print("Falha ao excluir categoria.")

    def handle_close_action(self):
        """Executa o callback de fechamento, se houver, e destrói a janela."""
        if self.on_close_callback:
            self.on_close_callback()
        self.destroy()

if __name__ == '__main__':
    # Para testar esta janela isoladamente
    app = customtkinter.CTk() # Precisa de uma janela root CTk para CTkToplevel
    app.withdraw() # Esconde a janela root principal
    form_window = FormCadastroWindow(master=app, current_user_id="test_user_01")
    form_window.mainloop() # CTkToplevel não tem seu próprio mainloop, mas isso mantém o script rodando para a janela
    # A linha acima é um pouco estranha para CTkToplevel, geralmente ele depende do mainloop do seu pai.
    # Se o pai (app) fechar, o toplevel também fecha.
    # Para teste autônomo, manter o app.mainloop() do root seria mais comum após criar o toplevel.
    # app.mainloop() # Se você quiser que a janela root (invisível) mantenha o programa rodando.
    pass # Usamos grab_set, então o mainloop do root não é estritamente necessário para manter o toplevel aberto.