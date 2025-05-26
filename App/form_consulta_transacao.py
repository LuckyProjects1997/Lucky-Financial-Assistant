# form_consulta_transacao.py
import customtkinter
import datetime
import Database
from PIL import Image # Adicionado para carregar o ícone
from CTkMessagebox import CTkMessagebox 

# Definições de fonte padrão
FONTE_FAMILIA = "Segoe UI"
FONTE_TITULO_FORM = (FONTE_FAMILIA, 18, "bold")
FONTE_LABEL_FORM = (FONTE_FAMILIA, 13)
FONTE_VALOR_FORM = (FONTE_FAMILIA, 13)
FONTE_BOTAO_FORM = (FONTE_FAMILIA, 13, "bold")
BOTAO_CORNER_RADIUS = 17
BOTAO_FG_COLOR = "gray30"
BOTAO_HOVER_COLOR = "#2196F3"
BOTAO_HEIGHT = 35

# Caminho para o ícone de lápis (ajuste conforme necessário)
PENCIL_ICON_PATH = "Images/pencil_icon.png"

class FormConsultaTransacaoWindow(customtkinter.CTkToplevel):
    def __init__(self, master=None, transaction_id=None, on_action_completed_callback=None):
        super().__init__(master)
        self.title("Consulta de Transação")
        self.geometry("450x600")
        self.configure(fg_color="#1c1c1c")
        self.lift()
        self.attributes("-topmost", True)
        # self.grab_set() # Pode causar problemas com CTkMessagebox se não gerenciado cuidadosamente

        self.transaction_id = transaction_id
        self.on_action_completed_callback = on_action_completed_callback
        self.transaction_data = None
        self.is_editing = False

        self.field_elements = {} # Armazenará dicts com 'display', 'input', 'icon' para campos editáveis
        self.status_var = customtkinter.StringVar()

        self.pencil_icon_image = None # Atributo para armazenar a imagem do ícone

        self._load_icons() # Carrega os ícones
        self._load_transaction_data()
        self._setup_ui()

    def _load_icons(self):
        """Carrega as imagens dos ícones necessárias."""
        try:
            pil_pencil_image = Image.open(PENCIL_ICON_PATH)
            self.pencil_icon_image = customtkinter.CTkImage(pil_pencil_image, size=(16, 16)) # Ajuste o tamanho conforme necessário
        except FileNotFoundError:
            print(f"Erro: Ícone do lápis '{PENCIL_ICON_PATH}' não encontrado.")
            self.pencil_icon_image = None # Garante que seja None se falhar
    def _load_transaction_data(self):
        if self.transaction_id:
            self.transaction_data = Database.get_transaction_by_id(self.transaction_id)
        if not self.transaction_data:
            CTkMessagebox(title="Erro", message="Não foi possível carregar os dados da transação.", icon="cancel", master=self)
            self.after(100, self.destroy) # Fecha a janela após um pequeno delay

    def _setup_ui(self):
        if not self.transaction_data:
            return

        main_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

         # Configura as colunas do grid: Label (0), Widget (1), Ícone (2)
        main_frame.grid_columnconfigure(0, weight=0) # Coluna para os rótulos (não expande)
        main_frame.grid_columnconfigure(1, weight=1) # Coluna para os widgets (expande horizontalmente)
        main_frame.grid_columnconfigure(2, weight=0) # Coluna para os ícones (não expande)

        # Configuração dos campos na ordem desejada
        # (Label Text, db_key, widget_type, is_alterable)
        # widget_type: 'label_only', 'entry', 'combobox_category', 'radios_status'
        field_configs = [
            ("ID:", "id", "label_only", False),
            ("Descrição:", "description", "entry", True),
            ("Data Lançamento:", "launch_date", "label_only", False),
            ("Categoria:", "category_name", "combobox_category", True), # db_key é category_name para display, mas usaremos category_id para salvar
            ("Modalidade:", "modality", "label_only", False),
            ("Parcela:", "installments", "label_only", False),
            ("Valor Total:", "total_value_compra", "label_only", False), # Adicionado conforme descrição
            ("Valor Parcela (R$):", "value", "label_only", False), # Corrigido: Apenas uma entrada, não editável
            ("Status:", "status", "radios_status", True),
            ("Data Prevista:", "due_date", "entry", True),
            ("Data Pagamento:", "payment_date", "entry", True),
        ]
        
        current_row = 0

        for label_text, db_key, widget_type, is_alterable in field_configs:
            customtkinter.CTkLabel(main_frame, text=label_text, font=FONTE_LABEL_FORM, anchor="w").grid(row=current_row, column=0, sticky="w", padx=5, pady=(5,2))
            
            display_widget = customtkinter.CTkLabel(main_frame, text="", font=FONTE_VALOR_FORM, anchor="w", height=BOTAO_HEIGHT)
            input_widget = None
            icon_widget = None
            radios_for_status = None

            if is_alterable:
                if widget_type == "combobox_category":
                    categories = Database.get_categories_by_user(self.transaction_data.get("user_id"))
                    category_names = [cat['name'] for cat in categories]
                    input_widget = customtkinter.CTkComboBox(main_frame, values=category_names, font=FONTE_VALOR_FORM, state="disabled", height=BOTAO_HEIGHT)
                elif widget_type == "radios_status":
                    input_widget = customtkinter.CTkFrame(main_frame, fg_color="transparent")
                    radio_aberto = customtkinter.CTkRadioButton(input_widget, text="Em Aberto", variable=self.status_var, value="Em Aberto", font=FONTE_LABEL_FORM, state="disabled")
                    radio_aberto.pack(side="left", padx=(0,10))
                    radio_pago = customtkinter.CTkRadioButton(input_widget, text="Pago", variable=self.status_var, value="Pago", font=FONTE_LABEL_FORM, state="disabled")
                    radio_pago.pack(side="left")
                    radios_for_status = [radio_aberto, radio_pago]
                elif widget_type == "entry":
                    input_widget = customtkinter.CTkEntry(main_frame, font=FONTE_VALOR_FORM, state="disabled", height=BOTAO_HEIGHT)
                
                if self.pencil_icon_image:
                    icon_widget = customtkinter.CTkLabel(main_frame, text="", image=self.pencil_icon_image)
            
            self.field_elements[db_key] = {
                "display": display_widget,
                "input": input_widget, # Será None para campos 'label_only' ou se não for alterável
                "icon": icon_widget,   # Será None se não for alterável ou se for status
                "row": current_row,    # Store the row for precise placement later
                "widget_type": widget_type
            }
            if radios_for_status:
                self.field_elements[db_key]["radios"] = radios_for_status

            # Posiciona o display_widget (Label de visualização)
            display_widget.grid(row=current_row, column=1, sticky="e", padx=5, pady=(5,2)) # Alinhado à direita
            
            # Posiciona o ícone se existir
            if icon_widget:
                icon_widget.bind("<Button-1>", lambda event, k=db_key: self._enable_field_edit(k)) # Habilita edição ao clicar no ícone
                icon_widget.grid(row=current_row, column=2, sticky="w", padx=(0,5), pady=(5,2))
            
            # O input_widget não é adicionado ao grid aqui; _toggle_edit_mode fará isso.
            current_row += 1

        # Botões (posicionados após todos os campos)
        buttons_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.grid(row=current_row, column=0, columnspan=3, pady=(20,10), sticky="ew")
        buttons_frame.grid_columnconfigure(0, weight=1) # Espaço à esquerda
        buttons_frame.grid_columnconfigure(1, weight=0) # Botão Excluir
        buttons_frame.grid_columnconfigure(2, weight=0) # Botão Salvar
        buttons_frame.grid_columnconfigure(3, weight=1) # Espaço à direita

        self.delete_button = customtkinter.CTkButton(buttons_frame, text="Excluir", command=self._confirm_delete_transaction,
                                                   height=BOTAO_HEIGHT, font=FONTE_BOTAO_FORM, corner_radius=BOTAO_CORNER_RADIUS,
                                                   fg_color="tomato", hover_color="#c0392b") # Vermelho para exclusão
        self.delete_button.grid(row=0, column=1, padx=(0,5)) # À esquerda do Salvar

        self.save_button = customtkinter.CTkButton(buttons_frame, text="Salvar", command=self._save_changes,
                                                   height=BOTAO_HEIGHT, font=FONTE_BOTAO_FORM, corner_radius=BOTAO_CORNER_RADIUS,
                                                   fg_color="green", hover_color="darkgreen", state="disabled")
        self.save_button.grid(row=0, column=2, padx=(5,0)) # À direita do Excluir
        
        current_row += 1 # Próxima linha para o botão Fechar

        # Frame para o botão Fechar, para centralizá-lo
        close_button_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        close_button_frame.grid(row=current_row, column=0, columnspan=3, pady=(5,0), sticky="ew")
        close_button_frame.grid_columnconfigure(0, weight=1) # Para centralizar

        self.close_button = customtkinter.CTkButton(close_button_frame, text="Fechar", command=self.destroy,
                                                height=BOTAO_HEIGHT, font=FONTE_BOTAO_FORM, corner_radius=BOTAO_CORNER_RADIUS,
                                                fg_color="gray50", hover_color="gray40")
        self.close_button.grid(row=0, column=0, pady=(0,0)) # Centralizado no close_button_frame

        self._update_form_fields() # Carrega os dados nos campos

       

    def _update_form_fields(self):
        """Atualiza os campos do formulário com os dados de self.transaction_data."""
        if not self.transaction_data:
            return

        for db_key, elements in self.field_elements.items():
            display_widget = elements["display"]
            input_widget = elements["input"]
            widget_type = elements["widget_type"]
            raw_value = self.transaction_data.get(db_key)

            # Lógica especial para campos calculados ou com formatação específica
            display_text = ""
            input_text_or_val = None

            if db_key == "total_value_compra":
                parcel_value = self.transaction_data.get('value', 0.0)
                installments_str = self.transaction_data.get('installments', "1/1")
                total_installments = 1
                if installments_str and "/" in installments_str:
                    try:
                        total_installments = int(installments_str.split('/')[1])
                    except (ValueError, IndexError):
                        total_installments = 1
                
                total_compra_value = parcel_value * total_installments
                display_text = f"R$ {total_compra_value:,.2f}".replace(",", "#").replace(".", ",").replace("#", ".")
            elif db_key == "value": # Valor da Parcela
                value_float = raw_value if raw_value is not None else 0.0
                formatted_display_value = f"{value_float:,.2f}".replace(",", "#").replace(".", ",").replace("#", ".")
                display_text = f"R$ {formatted_display_value}"
                input_text_or_val = str(int(round(value_float * 100))) # Dígitos para formatação
            elif db_key in ["due_date", "payment_date"]:
                display_text = datetime.datetime.strptime(raw_value, "%Y-%m-%d").strftime("%d/%m/%Y") if raw_value else ""
                input_text_or_val = display_text
            elif db_key == "category_name": # Usado para display de categoria
                display_text = raw_value if raw_value else "N/A"
                if input_widget: input_text_or_val = display_text # Para ComboBox
            elif db_key == "status":
                display_text = raw_value if raw_value else "N/A"
                if widget_type == "radios_status": self.status_var.set(display_text)
            else: # Campos de texto simples ou IDs
                display_text = str(raw_value) if raw_value is not None else "N/A"
                input_text_or_val = display_text

            display_widget.configure(text=display_text)

            if input_widget:
                if widget_type == "entry":
                    input_widget.delete(0, customtkinter.END)
                    if input_text_or_val is not None: input_widget.insert(0, str(input_text_or_val))
                elif widget_type == "combobox_category":
                    if input_text_or_val: input_widget.set(str(input_text_or_val))
                
                # Aplica formatação se estiver em modo de edição
                # O campo 'value' (Valor Parcela) é label_only, não precisa de formatação de input aqui.
                # A formatação de data é aplicada se o campo estiver ativo para edição.
                if self.is_editing and widget_type != "label_only":
                    if db_key in ["due_date", "payment_date"] and input_widget.cget("state") == "normal":
                        self.format_date_entry(None, input_widget)

    def _save_changes(self):
        if not self.transaction_data:
            CTkMessagebox(title="Erro", message="Dados da transação não encontrados.", icon="cancel", master=self)
            return

        try:
            # Coleta apenas os dados dos campos que são alteráveis
            updated_data = {"transaction_id": self.transaction_id}
            
            if "description" in self.field_elements:
                desc_elements = self.field_elements["description"]
                if desc_elements["input"].cget("state") == "normal":
                    updated_data["description"] = desc_elements["input"].get().strip()
                else:
                    updated_data["description"] = self.transaction_data.get("description", "").strip()

            # Valor Parcela (R$) não é mais editável, então sempre pegamos do self.transaction_data
            updated_data["value"] = self.transaction_data.get("value", 0.0)
            date_keys_to_process = {"due_date": "due_date", "payment_date": "payment_date"}
            for form_key, db_key in date_keys_to_process.items():
                if form_key in self.field_elements:
                    date_elements = self.field_elements[form_key]
                    date_str_for_db = None
                    if date_elements["input"].cget("state") == "normal": # Se o campo de data estava ativo para edição
                        date_str_ddmmyyyy = date_elements["input"].get()
                        if date_str_ddmmyyyy:
                            try:
                                date_str_for_db = datetime.datetime.strptime(date_str_ddmmyyyy, "%d/%m/%Y").strftime("%Y-%m-%d")
                            except ValueError: # Formato inválido no input
                                CTkMessagebox(title="Erro de Formato", message=f"Formato de {form_key.replace('_', ' ').title()} inválido. Use DD/MM/AAAA.", icon="cancel", master=self)
                                return
                    else: # Se o campo de data não estava ativo, pega o valor de self.transaction_data
                        date_str_for_db = self.transaction_data.get(db_key) # Já está em YYYY-MM-DD ou None
                    updated_data[db_key] = date_str_for_db

            if "status" in self.field_elements:
                # Status é sempre lido da self.status_var, que é atualizada pelos radio buttons
                updated_data["status"] = self.status_var.get()
            
            if "category_name" in self.field_elements: # O input widget é para category_name
                cat_elements = self.field_elements["category_name"]
                selected_category_name = ""
                if cat_elements["input"].cget("state") == "normal":
                    selected_category_name = cat_elements["input"].get()
                else:
                    selected_category_name = self.transaction_data.get("category_name", "N/A")

                categories = Database.get_categories_by_user(self.transaction_data.get("user_id"))
                selected_category_obj = next((cat for cat in categories if cat['name'] == selected_category_name), None)
                if not selected_category_obj:
                    # Fallback para o ID original se o nome não for encontrado (ex: se o nome da categoria mudou no DB)
                    selected_category_obj = next((cat for cat in categories if cat['id'] == self.transaction_data.get("category_id")), None)
                    if not selected_category_obj:
                        CTkMessagebox(title="Erro de Validação", message="Categoria selecionada é inválida.", icon="cancel", master=self)
                        return
                updated_data["category_id"] = selected_category_obj['id']
            else: # Se categoria não for editável, mantenha a original
                updated_data["category_id"] = self.transaction_data.get("category_id")


            # Validações
            if not updated_data.get("description"):
                CTkMessagebox(title="Erro de Validação", message="Descrição não pode ser vazia.", icon="warning", master=self)
                return
            if updated_data.get("status") == "Em Aberto" and not updated_data.get("due_date"):
                CTkMessagebox(title="Erro de Validação", message="Data Prevista é obrigatória para status 'Em Aberto'.", icon="warning", master=self)
                return
            if updated_data.get("status") == "Pago" and not updated_data.get("payment_date"):
                CTkMessagebox(title="Erro de Validação", message="Data de Pagamento é obrigatória para status 'Pago'.", icon="warning", master=self)
                return
            if updated_data.get("status") == "Pago" and not updated_data.get("due_date"):
                updated_data["due_date"] = updated_data.get("payment_date")

            success = Database.update_transaction(
                transaction_id=updated_data["transaction_id"],
                description=updated_data["description"],
                value=updated_data["value"],
                due_date=updated_data["due_date"],
                payment_date=updated_data["payment_date"],
                status=updated_data["status"],
                category_id=updated_data["category_id"]
            )

            if success:
                CTkMessagebox(title="Sucesso", message="Transação atualizada com sucesso!", icon="check", master=self)
                if self.on_action_completed_callback:
                    self.on_action_completed_callback()
                # self._toggle_edit_mode() # Não mais necessário
                self._load_transaction_data() 
                self._set_all_fields_to_display_mode() # Volta para o modo de visualização
            else:
                CTkMessagebox(title="Erro", message="Falha ao atualizar a transação.", icon="cancel", master=self)

        except ValueError as ve:
            if "time data" in str(ve) and "does not match format" in str(ve):
                CTkMessagebox(title="Erro de Formato de Data", message="Formato de data inválido. Use DD/MM/AAAA.", icon="cancel", master=self)
            else:
                CTkMessagebox(title="Erro de Formato", message=f"Formato de dado inválido: {ve}", icon="cancel", master=self)
        except Exception as e:
            CTkMessagebox(title="Erro Inesperado", message=f"Ocorreu um erro: {e}", icon="cancel", master=self)
    def _confirm_delete_transaction(self):
        if not self.transaction_id:
            CTkMessagebox(title="Erro", message="ID da transação não encontrado.", icon="cancel", master=self)
            return

        desc = self.transaction_data.get("description", "esta transação")
        msg_box = CTkMessagebox(
            master=self, # Set master for better modality and event handling
            title="Confirmar Exclusão",
            message=f"Tem certeza que deseja excluir a transação:\n'{desc}'?",
            icon="warning",
            option_1="Cancelar",
            option_2="Excluir"
        )
        
        response = msg_box.get() # Bloqueia até o usuário clicar

        print(f"DEBUG: CTkMessagebox response: '{response}'")

        # Se o usuário clicou no botão "Excluir" do pop-up
        if response == "Excluir":
            print(f"DEBUG: Proceeding with delete for transaction ID: {self.transaction_id} because response was 'Excluir'.")
            try:
                success = Database.delete_transaction(self.transaction_id)
                if success:
                    CTkMessagebox(title="Sucesso", message="Transação excluída com sucesso!", icon="check", master=self.master) # master=self.master para aparecer sobre o Dashboard
                    if self.on_action_completed_callback: 
                        self.on_action_completed_callback()
                    self.destroy()
                else:
                    CTkMessagebox(title="Erro", message="Falha ao excluir a transação.", icon="cancel", master=self)
            except Exception as e:
                print(f"ERRO CRÍTICO durante a exclusão: {e}")
                CTkMessagebox(title="Erro Crítico", message=f"Ocorreu um erro inesperado durante a exclusão:\n{e}", icon="cancel", master=self)
        elif response == "Cancelar":
            print(f"DEBUG: Exclusão cancelada pelo usuário (response: '{response}')")
        else:
            print(f"DEBUG: Ação de exclusão não confirmada ou pop-up fechado. Resposta: '{response}'")

    def _enable_field_edit(self, key):
        if key not in self.field_elements:
            return

        elements = self.field_elements[key]
        display_widget = elements["display"]
        input_widget = elements["input"]
        row_index = elements["row"] # Use the stored row index
        icon_widget = elements.get("icon")
        widget_type = elements["widget_type"]

        if not input_widget: # Não deve acontecer para campos alteráveis
            return

        display_widget.grid_remove()
        if icon_widget:
            icon_widget.grid_remove()
        
        input_widget.grid(row=row_index, column=1, sticky="ew", padx=5, pady=(5,2))
        
        if widget_type == "radios_status":
            for radio in elements["radios"]:
                radio.configure(state="normal")
        else: # entry, combobox
            input_widget.configure(state="normal")
            input_widget.focus() # Define o foco para o campo de entrada

        # Adiciona binds de formatação
        if key in ["due_date", "payment_date"]: # Apenas para campos de data editáveis
            input_widget.bind("<KeyRelease>", lambda e, entry=input_widget: self.format_date_entry(e, entry))
            self.format_date_entry(None, input_widget)

        self.save_button.configure(state="normal") # Habilita o botão Salvar
        self.is_editing = True # Indica que pelo menos um campo está sendo editado

    def _set_all_fields_to_display_mode(self):
        for key, elements in self.field_elements.items():
            display_widget = elements["display"]
            input_widget = elements["input"]
            icon_widget = elements.get("icon")
            row_index = elements["row"] # Use the stored row index
            widget_type = elements["widget_type"]

            if widget_type == "label_only" or not input_widget:
                continue

            input_widget.grid_remove()
            display_widget.grid() 
            display_widget.grid(row=row_index, column=1, sticky="e", padx=5, pady=(5,2)) # Ensure correct placement and alignment
            if icon_widget:
                icon_widget.grid() 
                icon_widget.grid(row=row_index, column=2, sticky="w", padx=(0,5), pady=(5,2)) # Ensure correct placement

            if widget_type == "radios_status":
                for radio in elements["radios"]:
                    radio.configure(state="disabled")
            else: # entry, combobox
                input_widget.configure(state="disabled")
        
        self.save_button.configure(state="disabled") # Desabilita o botão Salvar
        self.is_editing = False
        self._update_form_fields() # Atualiza os labels de display com os dados atuais

    def format_date_entry(self, event, entry_widget):
        """Formata a entrada de data para DD/MM/AAAA enquanto o usuário digita."""
        if not entry_widget or entry_widget.cget("state") == "disabled" and event is not None: 
            return
        text = entry_widget.get()
        text = "".join(filter(str.isdigit, text))
        
        new_text = ""
        if len(text) > 0: new_text += text[:2]
        if len(text) > 2: new_text += "/" + text[2:4]
        if len(text) > 4: new_text += "/" + text[4:8]
            
        current_cursor_pos = entry_widget.index(customtkinter.INSERT)
        entry_widget.delete(0, customtkinter.END)
        entry_widget.insert(0, new_text)
        
        if event and event.keysym != 'BackSpace': 
            if len(new_text) == 2 and len(text) == 2: entry_widget.icursor(len(new_text))
            elif len(new_text) == 5 and len(text) == 4: entry_widget.icursor(len(new_text))
            else: entry_widget.icursor(len(new_text))
        elif event and event.keysym == 'BackSpace':
            entry_widget.icursor(current_cursor_pos) 
        else: 
            entry_widget.icursor(len(new_text))

    def format_currency_input(self, event=None, entry_widget_override=None):
        """Formata o valor como moeda (R$ X.XXX,XX) enquanto o usuário digita apenas números."""
        entry_widget = entry_widget_override
        if not entry_widget: # Fallback se não fornecido
            # Não há mais um campo de valor editável padrão nesta tela,
            # então este fallback pode não ser mais necessário aqui.
            # Mantido por segurança se a função for chamada inesperadamente sem override.
            entry_widget = self.field_elements.get("value", {}).get("input")
            if not entry_widget: return

        current_text = entry_widget.get()
        digits_only = "".join(filter(str.isdigit, current_text))

        if not digits_only: formatted_value = "0,00"
        elif len(digits_only) == 1: formatted_value = f"0,0{digits_only}"
        elif len(digits_only) == 2: formatted_value = f"0,{digits_only}"
        else:
            decimal_part = digits_only[-2:]
            integer_part_str = digits_only[:-2].lstrip('0') or "0"
            parts = [integer_part_str[max(0, i-3):i] for i in range(len(integer_part_str), 0, -3)]
            formatted_integer_part = ".".join(reversed(parts)) if parts else "0"
            formatted_value = f"{formatted_integer_part},{decimal_part}"
        entry_widget.delete(0, customtkinter.END)
        entry_widget.insert(0, formatted_value)
        entry_widget.icursor(len(formatted_value))

if __name__ == '__main__':  # Ensure this line has no leading spaces
    app_root = customtkinter.CTk()  # Indent with 4 spaces
    app_root.withdraw()  # Indent with 4 spaces
    
    # Substitua 'trans_consulta_01' por um ID de transação real do seu banco
    valid_transaction_id_for_test = "trans_consulta_01"  # Indent with 4 spaces
    if Database.get_transaction_by_id(valid_transaction_id_for_test):  # Indent with 4 spaces
        form_consulta = FormConsultaTransacaoWindow(master=app_root, transaction_id=valid_transaction_id_for_test)  # Indent with 8 spaces
        app_root.mainloop()  # Indent with 8 spaces
    else:  # Indent with 4 spaces
        print(f"Transação de teste com ID '{valid_transaction_id_for_test}' não encontrada. Crie-a primeiro.")  # Indent with 8 spaces
        app_root.destroy()  # Indent with 8 spaces