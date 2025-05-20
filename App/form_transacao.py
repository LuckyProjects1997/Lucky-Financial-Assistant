# form_transacao.py
import customtkinter
import tkinter as tk # Necessário para o colorchooser funcionar corretamente com CTk
import datetime # Para obter a data atual
import uuid # Para gerar IDs únicos
# Importa as funções do banco de dados
import Database # Usando 'Database' com D maiúsculo conforme seu Main.py
# Importa a janela de formulário de cadastro de categorias/usuários
from form_cadastro import FormCadastroWindow

# Definições de fonte padrão para o Formulário de Transação
FONTE_FAMILIA = "Segoe UI"
FONTE_TITULO_FORM = (FONTE_FAMILIA, 18, "bold")
FONTE_LABEL_FORM = (FONTE_FAMILIA, 13)
FONTE_INPUT_FORM = (FONTE_FAMILIA, 13)
FONTE_BOTAO_FORM = (FONTE_FAMILIA, 13, "bold")
BOTAO_CORNER_RADIUS = 17
BOTAO_FG_COLOR = "gray30"
BOTAO_HOVER_COLOR = "#2196F3"
BOTAO_HEIGHT = 35
FONTE_LINK = (FONTE_FAMILIA, 11, "underline") # Fonte para o link
COR_CONTAINER_INTERNO_FORM = "#222222"

class FormTransacaoWindow(customtkinter.CTkToplevel):
    def __init__(self, master=None, current_user_id=None, tipo_transacao="Despesa"): # tipo_transacao pode ser "Despesa" ou "Provento"
        super().__init__(master)
        self.title(f"Nova {tipo_transacao}")
        self.geometry("450x550")
        self.configure(fg_color="#1c1c1c")
        self.lift()
        self.attributes("-topmost", True)
        self.grab_set()

        self.minsize(400, 500)

        self.current_user_id = current_user_id
        self.tipo_transacao = tipo_transacao # Armazena o tipo para uso futuro, se necessário
        self.form_cadastro_ref = None # Referência para a janela de cadastro de categoria

        # --- Frame Principal ---
        main_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)

        title_label = customtkinter.CTkLabel(main_frame, text=f"Cadastrar Despesa/Provento", font=FONTE_TITULO_FORM)
        title_label.grid(row=0, column=0, pady=(10, 20), sticky="ew")

        # Descrição
        description_label = customtkinter.CTkLabel(main_frame, text="Descrição:", font=FONTE_LABEL_FORM)
        description_label.grid(row=1, column=0, pady=(5,2), padx=10, sticky="w")
        self.description_entry = customtkinter.CTkEntry(main_frame, placeholder_text="Ex: Conta de Luz, Salário", height=BOTAO_HEIGHT, font=FONTE_INPUT_FORM)
        self.description_entry.grid(row=2, column=0, sticky="ew", padx=10, pady=(0,10))

        # Categoria
        category_label = customtkinter.CTkLabel(main_frame, text="Categoria:", font=FONTE_LABEL_FORM)
        category_label.grid(row=3, column=0, pady=(5,2), padx=10, sticky="w")
        self.category_combobox = customtkinter.CTkComboBox(main_frame, values=["Carregando..."], height=BOTAO_HEIGHT, font=FONTE_INPUT_FORM)
        self.category_combobox.set("Carregando...")
        self.category_combobox.grid(row=4, column=0, sticky="ew", padx=10, pady=(0,10))

        # Link "Cadastrar Categoria"
        self.link_cadastrar_categoria = customtkinter.CTkLabel(main_frame, text="Cadastrar Nova Categoria...", font=FONTE_LINK, text_color="#8ab4f8", cursor="hand2")
        self.link_cadastrar_categoria.grid(row=5, column=0, padx=10, pady=(0,10), sticky="e") # Alinhado à direita
        self.link_cadastrar_categoria.bind("<Button-1>", self.open_form_cadastro_categoria)


        self.load_categories_for_combobox()

        # Frame para Valor e Status (lado a lado)
        value_status_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        value_status_frame.grid(row=6, column=0, sticky="ew", padx=0, pady=(0,10))
        value_status_frame.grid_columnconfigure(0, weight=1) # Coluna para Valor
        value_status_frame.grid_columnconfigure(1, weight=1) # Coluna para Status

        # Valor (dentro do value_status_frame)
        value_inner_frame = customtkinter.CTkFrame(value_status_frame, fg_color="transparent")
        value_inner_frame.grid(row=0, column=0, sticky="ew", padx=(10,5))
        value_label = customtkinter.CTkLabel(value_inner_frame, text="Valor:", font=FONTE_LABEL_FORM)
        value_label.pack(anchor="w", pady=(5,2))
        self.value_entry = customtkinter.CTkEntry(value_inner_frame, placeholder_text="Ex: 150.75", height=BOTAO_HEIGHT, font=FONTE_INPUT_FORM, width=170)
        self.value_entry.pack(anchor="w") # anchor="w" para não expandir horizontalmente
        self.value_entry.bind("<KeyRelease>", self.format_currency_input) # Tenta formatar enquanto digita

        # Status Radio Buttons (dentro do value_status_frame)
        status_frame = customtkinter.CTkFrame(value_status_frame, fg_color="transparent")
        status_frame.grid(row=0, column=1, sticky="ew", padx=(5,10), pady=(0,0)) # Alinhado com o valor
        # Adicionar um label vazio ou ajustar padding para alinhar verticalmente com o campo de valor, se necessário
        # Ou colocar o label "Status:" acima dos radio buttons
        status_title_label = customtkinter.CTkLabel(status_frame, text="Status:", font=FONTE_LABEL_FORM)
        status_title_label.pack(anchor="w", pady=(5,2))

        status_buttons_inner_frame = customtkinter.CTkFrame(status_frame, fg_color="transparent")
        status_buttons_inner_frame.pack(anchor="w")



        

        self.status_var = customtkinter.StringVar(value="Em Aberto") # Variável para controlar o status

        self.status_radio_aberto = customtkinter.CTkRadioButton(status_frame, text="Em Aberto", variable=self.status_var, value="Em Aberto",
                                                                font=FONTE_LABEL_FORM, command=self.update_date_fields_visibility) # Removido status_buttons_inner_frame
        self.status_radio_aberto.pack(in_=status_buttons_inner_frame, side="left", padx=5)

        self.status_radio_pago = customtkinter.CTkRadioButton(status_frame, text="Pago", variable=self.status_var, value="Pago",
                                                              font=FONTE_LABEL_FORM, command=self.update_date_fields_visibility) # Removido status_buttons_inner_frame
        self.status_radio_pago.pack(in_=status_buttons_inner_frame, side="left", padx=5)
        
        # Frame ÚNICO para os campos de data (Data Prevista OU Data Pagamento)
        self.date_input_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        self.date_input_frame.grid(row=8, column=0, sticky="ew", padx=10, pady=(0,15))
        self.date_input_frame.grid_columnconfigure(0, weight=1) # Para o entry expandir

        # Data Prevista (elementos criados, mas não necessariamente visíveis)
        self.due_date_label_ref = customtkinter.CTkLabel(self.date_input_frame, text="Data Prevista:", font=FONTE_LABEL_FORM)
        self.due_date_entry = customtkinter.CTkEntry(self.date_input_frame, placeholder_text=datetime.date.today().strftime("%d/%m/%Y"), height=BOTAO_HEIGHT, font=FONTE_INPUT_FORM, width=160)
        self.due_date_entry.bind("<KeyRelease>", lambda e: self.format_date_entry(e, self.due_date_entry))
        self.due_date_entry_ref = self.due_date_entry

        # Data de Pagamento (elementos criados, mas não necessariamente visíveis)
        self.payment_date_label_ref = customtkinter.CTkLabel(self.date_input_frame, text="Data Pagamento:", font=FONTE_LABEL_FORM)
        self.payment_date_entry = customtkinter.CTkEntry(self.date_input_frame, placeholder_text="DD/MM/AAAA", height=BOTAO_HEIGHT, font=FONTE_INPUT_FORM, width=160)
        self.payment_date_entry.bind("<KeyRelease>", lambda e: self.format_date_entry(e, self.payment_date_entry))
        self.payment_date_entry_ref = self.payment_date_entry

        self.update_date_fields_visibility() # Chama para configurar o estado inicial dos campos de data

        # Frame para os botões Salvar e Fechar
        action_buttons_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        action_buttons_frame.grid(row=11, column=0, pady=(20,10), sticky="ew") # Ajustado pady e row
        action_buttons_frame.grid_columnconfigure(0, weight=1) # Espaço antes do botão Salvar
        action_buttons_frame.grid_columnconfigure(1, weight=0) # Botão Salvar
        action_buttons_frame.grid_columnconfigure(2, weight=0) # Botão Fechar
        action_buttons_frame.grid_columnconfigure(3, weight=1) # Espaço depois do botão Fechar

        # Botão Salvar Transação (agora dentro do action_buttons_frame)
        save_button = customtkinter.CTkButton(main_frame, text=f"Salvar {tipo_transacao}", command=self.save_transaction,
                                                       height=BOTAO_HEIGHT, font=FONTE_BOTAO_FORM, corner_radius=BOTAO_CORNER_RADIUS,
                                                       fg_color=BOTAO_FG_COLOR, hover_color=BOTAO_HOVER_COLOR)
        save_button.grid(in_=action_buttons_frame, row=0, column=1, padx=5)

        # Botão Fechar (agora dentro do action_buttons_frame)
        close_button = customtkinter.CTkButton(main_frame, text="Fechar", command=self.destroy, height=BOTAO_HEIGHT, font=FONTE_BOTAO_FORM, corner_radius=BOTAO_CORNER_RADIUS, fg_color="gray50", hover_color="gray40")
        close_button.grid(in_=action_buttons_frame, row=0, column=2, padx=5)

    def load_categories_for_combobox(self):
        """Carrega as categorias na ComboBox."""
        self.category_combobox.configure(values=["Carregando..."])
        self.category_combobox.set("Carregando...")

        if not self.current_user_id:
            self.category_combobox.configure(values=["Nenhum usuário logado"])
            self.category_combobox.set("Nenhum usuário logado")
            return

        categories = Database.get_categories_by_user(self.current_user_id)
        # Filtra categorias pelo tipo_transacao se necessário, ou mostra todas
        # Para este exemplo, vamos mostrar todas e o usuário escolhe.
        # Se quisesse filtrar:
        # category_names = [cat['name'] for cat in categories if cat['type'] == self.tipo_transacao]
        category_names = [cat['name'] for cat in categories]


        if not category_names:
            self.category_combobox.configure(values=["Nenhuma categoria cadastrada"])
            self.category_combobox.set("Nenhuma categoria cadastrada")
        else:
            self.category_combobox.configure(values=["Selecione a Categoria"] + category_names)
            self.category_combobox.set("Selecione a Categoria")

    def save_transaction(self):
        description = self.description_entry.get().strip()
        selected_category_name = self.category_combobox.get()
        value_str = self.value_entry.get().strip()
        due_date_input = self.due_date_entry.get().strip()
        payment_date_input = self.payment_date_entry.get().strip()
        status = self.status_var.get()

        if not description or selected_category_name in ["Selecione a Categoria", "Carregando...", "Nenhuma categoria cadastrada"] or not value_str or not due_date_input:
            print("Descrição, Categoria, Valor e Data Prevista são obrigatórios.") # TODO: Mostrar alerta na GUI
            # Adicionar CTkMessagebox aqui seria ideal
            return

        try:
            value = float(value_str.replace(",", "."))
        except ValueError:
            print("Valor inválido. Use apenas números e ponto/vírgula.") # TODO: Mostrar alerta na GUI
            return
        
        # Converte datas de DD/MM/AAAA para YYYY-MM-DD para o banco
        try:
            due_date_db = datetime.datetime.strptime(due_date_input, "%d/%m/%Y").strftime("%Y-%m-%d")
            payment_date_db = None
            if status == "Pago" and payment_date_input:
                payment_date_db = datetime.datetime.strptime(payment_date_input, "%d/%m/%Y").strftime("%Y-%m-%d")
            elif status == "Pago" and not payment_date_input: # Se está pago mas sem data, não prosseguir
                print("Se o status é 'Pago', a Data de Pagamento é obrigatória.") # TODO: Alerta GUI
                return
        except ValueError:
            print("Formato de data inválido. Use DD/MM/AAAA.") # TODO: Alerta GUI
            return

        all_categories = Database.get_categories_by_user(self.current_user_id)
        selected_category = next((cat for cat in all_categories if cat['name'] == selected_category_name), None)

        if not selected_category:
             print(f"Categoria '{selected_category_name}' não encontrada.") # TODO: Mostrar alerta na GUI
             return

        transaction_id = str(uuid.uuid4())

        success = Database.add_transaction(transaction_id, self.current_user_id, selected_category['id'], description, value, due_date_db, payment_date_db)

        if success:
            print(f"{self.tipo_transacao} salva com sucesso!") # TODO: Mostrar alerta na GUI
            # Limpar campos
            self.description_entry.delete(0, customtkinter.END)
            self.category_combobox.set("Selecione a Categoria")
            self.value_entry.delete(0, customtkinter.END)
            self.due_date_entry.delete(0, customtkinter.END)
            self.due_date_entry.insert(0, datetime.date.today().strftime("%d/%m/%Y")) # Reseta para data atual
            self.payment_date_entry.delete(0, customtkinter.END)
            self.status_var.set("Em Aberto") # Reseta status
            self.update_date_fields_visibility() # Atualiza a visibilidade dos campos de data
            self.description_entry.focus() # Foca no primeiro campo
        else:
            print(f"Falha ao salvar {self.tipo_transacao}.") # TODO: Mostrar alerta na GUI

    def open_form_cadastro_categoria(self, event=None):
        """Abre o formulário de cadastro de categorias."""
        if self.form_cadastro_ref is None or not self.form_cadastro_ref.winfo_exists():
            # Função a ser chamada quando o formulário de cadastro de categoria for fechado
            def on_category_form_closed_callback():
                print("Formulário de cadastro de categoria fechado. Recarregando categorias...")
                self.load_categories_for_combobox()
                self.form_cadastro_ref = None # Limpa a referência
                self.attributes("-topmost", True) # Garante que a janela de transação volte ao topo
                self.focus_force() # Força o foco de volta

            self.form_cadastro_ref = FormCadastroWindow(master=self, current_user_id=self.current_user_id)
            self.form_cadastro_ref.on_close_callback = on_category_form_closed_callback
            self.form_cadastro_ref.protocol("WM_DELETE_WINDOW", on_category_form_closed_callback)
            self.form_cadastro_ref.focus()
        else:
            self.form_cadastro_ref.focus() # Se já existir, apenas foca nela


    def update_date_fields_visibility(self):
        """Controla a visibilidade e o estado dos campos de data com base no status."""
        status = self.status_var.get()
        if status == "Pago":
            # Esconde Data Prevista
            self.due_date_label_ref.grid_forget()
            self.due_date_entry_ref.grid_forget()
            # Mostra e habilita Data Pagamento, alinhado à esquerda
            self.payment_date_label_ref.grid(row=0, column=0, sticky="w", pady=(0,2))
            self.payment_date_entry_ref.grid(row=1, column=0, sticky="w") # Alterado para sticky="w"
            self.payment_date_entry_ref.configure(state="normal")
            if not self.payment_date_entry_ref.get(): # Se estiver vazio, preenche com data atual
                self.payment_date_entry_ref.insert(0, datetime.date.today().strftime("%d/%m/%Y"))
        else: # Em Aberto
            # Mostra Data Prevista, alinhado à esquerda
            self.due_date_label_ref.grid(row=0, column=0, sticky="w", pady=(0,2))
            self.due_date_entry_ref.grid(row=1, column=0, sticky="w") # Alterado para sticky="w"
            # Esconde e desabilita Data Pagamento
            self.payment_date_label_ref.grid_forget()
            self.payment_date_entry_ref.grid_forget()
            self.payment_date_entry_ref.delete(0, customtkinter.END)
            self.payment_date_entry_ref.configure(state="disabled")

    def format_date_entry(self, event, entry_widget):
        """Formata a entrada de data para DD/MM/AAAA enquanto o usuário digita."""
        # Não formata se o campo estiver desabilitado (evita problemas ao limpar)
        if entry_widget.cget("state") == "disabled":
            return
        text = entry_widget.get()
        text = "".join(filter(str.isdigit, text)) # Remove não dígitos
        
        new_text = ""
        if len(text) > 0:
            new_text += text[:2]
        if len(text) > 2:
            new_text += "/" + text[2:4]
        if len(text) > 4:
            new_text += "/" + text[4:8]
            
        entry_widget.delete(0, customtkinter.END)
        entry_widget.insert(0, new_text)
        entry_widget.icursor(len(new_text)) # Move o cursor para o final

    def format_currency_input(self, event):
        """Tenta formatar o valor como moeda (simples, sem separador de milhar por enquanto)."""
        entry_widget = self.value_entry
        current_text = entry_widget.get()
        cursor_pos = entry_widget.index(customtkinter.INSERT)

        # Remove tudo exceto dígitos e um separador decimal (vírgula ou ponto)
        clean_text = ""
        decimal_separator_found = False
        for char in current_text:
            if char.isdigit():
                clean_text += char
            elif char in [',', '.'] and not decimal_separator_found:
                clean_text += ',' # Padroniza para vírgula para a lógica de formatação
                decimal_separator_found = True
        
        # Limita a duas casas decimais
        if ',' in clean_text:
            parts = clean_text.split(',')
            integer_part = parts[0]
            decimal_part = parts[1][:2] if len(parts) > 1 else ""
            clean_text = f"{integer_part},{decimal_part}"

        if clean_text != current_text:
            entry_widget.delete(0, customtkinter.END)
            entry_widget.insert(0, clean_text)
            # Tenta restaurar a posição do cursor de forma simples
            # Isso pode não ser perfeito para todas as edições, mas ajuda.
            new_cursor_pos = cursor_pos - (len(current_text) - len(clean_text))
            entry_widget.icursor(max(0, new_cursor_pos))

if __name__ == '__main__':
    app = customtkinter.CTk()
    app.withdraw()
    # Teste para Despesa
    # form_trans = FormTransacaoWindow(master=app, current_user_id="01", tipo_transacao="Despesa")
    # Teste para Provento
    form_trans = FormTransacaoWindow(master=app, current_user_id="01", tipo_transacao="Provento")
    app.mainloop()