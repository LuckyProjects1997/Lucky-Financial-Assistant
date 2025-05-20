# form_cadastro.py
import customtkinter
from tkinter.colorchooser import askcolor # Para o seletor de cores
import tkinter as tk # Necessário para o colorchooser funcionar corretamente com CTk

# Importa as funções do banco de dados
import Database # Usando 'Database' com D maiúsculo conforme seu Main.py

# Definições de fonte padrão para o Formulário de Cadastro
FONTE_FAMILIA = "Segoe UI"
FONTE_TITULO_FORM = (FONTE_FAMILIA, 18, "bold")
FONTE_LABEL_FORM = (FONTE_FAMILIA, 13)
FONTE_INPUT_FORM = (FONTE_FAMILIA, 13)
FONTE_BOTAO_FORM = (FONTE_FAMILIA, 13, "bold")
BOTAO_CORNER_RADIUS = 17 # Para cantos bem arredondados
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

        self.current_user_id = current_user_id # ID do usuário logado, para vincular categorias

        # --- Frame Principal ---
        # Adicionando um pouco de padding interno ao frame principal da janela
        main_frame = customtkinter.CTkFrame(self, fg_color="transparent") # Tornando transparente para usar a cor da janela
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1) # Para centralizar o conteúdo que usa grid

        # --- Seção de Cadastro de Usuário ---
        user_section_frame = customtkinter.CTkFrame(main_frame, corner_radius=10, fg_color=COR_CONTAINER_INTERNO_FORM) # Frame com cantos arredondados
        user_section_frame.pack(pady=(0, 20), fill="x", padx=10)
        user_section_frame.grid_columnconfigure(0, weight=1) # Para centralizar o botão

        user_title_label = customtkinter.CTkLabel(user_section_frame, text="Cadastrar Novo Usuário", font=FONTE_TITULO_FORM)
        user_title_label.grid(row=0, column=0, pady=(15, 10), sticky="ew")

        user_name_label = customtkinter.CTkLabel(user_section_frame, text="Nome do Usuário:", font=FONTE_LABEL_FORM)
        user_name_label.grid(row=1, column=0, pady=(5,2), padx=20, sticky="w")
        self.user_name_entry = customtkinter.CTkEntry(user_section_frame, placeholder_text="Ex: João Silva", height=35, font=FONTE_INPUT_FORM)
        self.user_name_entry.grid(row=2, column=0, sticky="ew", padx=20, pady=(0,15))

        # TODO: Adicionar campo para ID do usuário se for manual, ou gerar automaticamente.
        # Por enquanto, vamos focar no nome.

        save_user_button = customtkinter.CTkButton(user_section_frame, text="Salvar Usuário", command=self.save_new_user, height=35, font=FONTE_BOTAO_FORM, corner_radius=BOTAO_CORNER_RADIUS)
        save_user_button.grid(row=3, column=0, pady=(0,15)) # Centralizado por padrão no grid de 1 coluna

        # --- Seção de Cadastro de Categoria ---
        category_section_frame = customtkinter.CTkFrame(main_frame, corner_radius=10, fg_color=COR_CONTAINER_INTERNO_FORM) # Frame com cantos arredondados
        category_section_frame.pack(pady=10, fill="x", padx=10)
        category_section_frame.grid_columnconfigure(0, weight=1) # Para centralizar o botão
        
        category_title_label = customtkinter.CTkLabel(category_section_frame, text="Cadastrar Nova Categoria", font=FONTE_TITULO_FORM)
        category_title_label.grid(row=0, column=0, pady=(15, 10), sticky="ew")

        category_name_label = customtkinter.CTkLabel(category_section_frame, text="Nome da Categoria:", font=FONTE_LABEL_FORM)
        category_name_label.grid(row=1, column=0, pady=(5,2), padx=20, sticky="w")
        self.category_name_entry = customtkinter.CTkEntry(category_section_frame, placeholder_text="Ex: Alimentação", height=35, font=FONTE_INPUT_FORM)
        self.category_name_entry.grid(row=2, column=0, sticky="ew", padx=20, pady=(0,10))

        category_type_label = customtkinter.CTkLabel(category_section_frame, text="Tipo:", font=FONTE_LABEL_FORM)
        category_type_label.grid(row=3, column=0, pady=(5,2), padx=20, sticky="w")
        self.category_type_combobox = customtkinter.CTkComboBox(category_section_frame, values=["Despesa", "Provento"], height=35, font=FONTE_INPUT_FORM)
        self.category_type_combobox.set("Despesa") # Valor padrão
        self.category_type_combobox.grid(row=4, column=0, sticky="ew", padx=20, pady=(0,10))

        # Seletor de Cor
        color_selection_frame = customtkinter.CTkFrame(category_section_frame, fg_color="transparent")
        color_selection_frame.grid(row=5, column=0, sticky="ew", padx=20, pady=(5,10))
        # Configurar colunas para o frame de seleção de cor para alinhar os elementos
        color_selection_frame.grid_columnconfigure(0, weight=0) # Label "Cor:"
        color_selection_frame.grid_columnconfigure(1, weight=0) # Preview da cor
        color_selection_frame.grid_columnconfigure(2, weight=1) # Botão "Escolher Cor" (expande para preencher)

        color_label = customtkinter.CTkLabel(color_selection_frame, text="Cor:", font=FONTE_LABEL_FORM)
        color_label.grid(row=0, column=0, padx=(0,5), sticky="w")

        self.selected_color_hex = "#FFFFFF" # Cor padrão (branco)
        self.color_preview_label = customtkinter.CTkLabel(color_selection_frame, text="", fg_color=self.selected_color_hex, width=35, height=35, corner_radius=5)
        self.color_preview_label.grid(row=0, column=1, padx=(0,10), sticky="w")
        
        choose_color_button = customtkinter.CTkButton(color_selection_frame, text="Escolher Cor", command=self.choose_color, height=35, font=FONTE_BOTAO_FORM, corner_radius=BOTAO_CORNER_RADIUS)
        choose_color_button.grid(row=0, column=2, sticky="e")

        # TODO: Adicionar campo para ID da categoria se for manual, ou gerar automaticamente.

        save_category_button = customtkinter.CTkButton(category_section_frame, text="Salvar Categoria", command=self.save_new_category, height=35, font=FONTE_BOTAO_FORM, corner_radius=BOTAO_CORNER_RADIUS)
        save_category_button.grid(row=6, column=0, pady=(5,15)) # Centralizado por padrão

        # Botão Fechar
        close_button = customtkinter.CTkButton(main_frame, text="Fechar", command=self.destroy, height=35, fg_color="gray50", hover_color="gray40", font=FONTE_BOTAO_FORM, corner_radius=BOTAO_CORNER_RADIUS)
        close_button.pack(pady=(10,0), side="bottom") # Posiciona na parte inferior do main_frame

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

    def save_new_user(self):
        user_name = self.user_name_entry.get()
        if not user_name:
            print("Nome do usuário não pode ser vazio.") # TODO: Mostrar alerta na GUI
            return

        # TODO: Lógica para gerar/solicitar ID do usuário.
        # Por enquanto, vamos simular um ID simples.
        # Em um sistema real, você precisaria de uma forma robusta de gerar IDs únicos.
        # Poderia ser um contador, um UUID, ou o próximo número disponível no banco.
        # Para este exemplo, vamos apenas imprimir.
        print(f"Tentando salvar novo usuário: {user_name}")
        # Database.add_user(novo_id_gerado, user_name)
        # self.master.master.load_users_into_combobox() # Tentativa de atualizar combobox no Main.py (complexo)
        print("Funcionalidade de salvar usuário a ser implementada com IDs e atualização da lista.")

    def save_new_category(self):
        category_name = self.category_name_entry.get()
        category_type = self.category_type_combobox.get()
        category_color = self.selected_color_hex

        if not category_name:
            print("Nome da categoria não pode ser vazio.") # TODO: Mostrar alerta na GUI
            return
        
        if not self.current_user_id:
            print("Nenhum usuário logado para associar a categoria.") # TODO: Mostrar alerta na GUI
            return

        # TODO: Lógica para gerar/solicitar ID da categoria.
        print(f"Tentando salvar nova categoria: {category_name}, Tipo: {category_type}, Cor: {category_color}, Usuário ID: {self.current_user_id}")
        # Database.add_category(novo_id_categoria, self.current_user_id, category_name, category_type, category_color)
        print("Funcionalidade de salvar categoria a ser implementada com IDs.")

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