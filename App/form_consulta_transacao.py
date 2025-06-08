# form_consulta_transacao.py
import customtkinter
import sys # Para resource_path E MANIPULAÇÃO DE SYS.PATH
import os  # Para resource_path E MANIPULAÇÃO DE SYS.PATH

# --- INÍCIO DA CORREÇÃO PARA PYLANCE E EXECUÇÃO DIRETA ---
# Adiciona o diretório do script atual (que deve ser 'App') ao sys.path.
# Isso ajuda o Pylance a encontrar módulos no mesmo diretório e também
# permite que o script seja executado diretamente para testes, resolvendo importações locais.
script_directory = os.path.dirname(os.path.abspath(__file__))
if script_directory not in sys.path:
    sys.path.append(script_directory)
# --- FIM DA CORREÇÃO ---

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

def resource_path(relative_path):
    """ Obtém o caminho absoluto para o recurso, funciona para desenvolvimento e para PyInstaller """
    try:
        # PyInstaller cria uma pasta temporária e armazena o caminho em _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# Caminho para o ícone de lápis
PENCIL_ICON_PATH = resource_path("Images/pencil_icon.png")

class FormConsultaTransacaoWindow(customtkinter.CTkToplevel):
    def __init__(self, master=None, transaction_id=None, on_action_completed_callback=None):
        super().__init__(master)
        self.title("Consulta de Transação")
        self.geometry("450x680") # Aumentada a altura da janela
        self.configure(fg_color="#1c1c1c")
        # self.grab_set() # Pode causar problemas com CTkMessagebox se não gerenciado cuidadosamente

        self.transaction_id = transaction_id
        self.on_action_completed_callback = on_action_completed_callback
        self.transaction_data = None
        self.is_editing = False
        self._initialization_successful = True  # Flag to indicate successful initialization

        self.field_elements = {} # Armazenará dicts com 'display', 'input', 'icon' para campos editáveis
        self.status_var = customtkinter.StringVar()
        self.payment_method_consult_var = customtkinter.StringVar() # Para os radio buttons do meio de pagamento na consulta
        self.pencil_icon_image = None # Atributo para armazenar a imagem do ícone

        self._load_icons() # Carrega os ícones
        self.status_var.trace_add("write", self._update_payment_method_editability) # Trace para o status
        self._load_transaction_data() # This can set _initialization_successful to False

        if not self._initialization_successful:
            # If _load_transaction_data failed and scheduled destruction,
            # we should not proceed to build the UI or lift/topmost.
            return # Exit __init__ early

        # Proceed with lift, topmost, and UI setup only if initialization was successful
        self.lift()
        self.attributes("-topmost", True)
        self._setup_ui()

    def _load_icons(self):
        """Carrega as imagens dos ícones necessárias."""
        try:
            pil_pencil_image = Image.open(PENCIL_ICON_PATH)
            self.pencil_icon_image = customtkinter.CTkImage(pil_pencil_image, size=(16, 16)) # Ajuste o tamanho conforme necessário
        except FileNotFoundError:
            print(f"Erro: Ícone do lápis '{PENCIL_ICON_PATH}' não encontrado.")
            self.pencil_icon_image = None # Garante que seja None se falhar

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
        entry_widget.icursor(len(formatted_value)) # Move o cursor para o final

    def _load_transaction_data(self):
        if self.transaction_id:
            self.transaction_data = Database.get_transaction_by_id(self.transaction_id)

        if not self.transaction_data:
            self._initialization_successful = False # Signal failure
            # Only show messagebox if transaction_id was provided but failed to load
            if self.transaction_id:
                CTkMessagebox(title="Erro", message="Não foi possível carregar os dados da transação.", icon="cancel", master=self)
            else: # transaction_id was None to begin with, or some other issue
                CTkMessagebox(title="Erro", message="ID da transação inválido ou dados não encontrados.", icon="cancel", master=self)

            self.after(100, self.destroy) # Fecha a janela após um pequeno delay
            return # Return early as initialization failed

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
        # is_alterable_config: True/False ou uma condição baseada nos dados da transação
        # Novo widget_type: 'radios_payment_method'
        
        field_configs = [
            ("ID:", "id", "label_only", False),
            ("Descrição:", "description", "entry", True),
            ("Data Lançamento:", "launch_date", "label_only", False),
            ("Tipo:", "category_type", "label_only", False),
            ("Categoria:", "category_name", "combobox_category", True), # db_key é category_name para display, mas usaremos category_id para salvar
            ("Modalidade:", "modality", "label_only", False),
            ("Parcela:", "installments", "label_only", False), # Mantido como label_only
            ("Valor Total:", "total_value_compra", "label_only", False), # Mantido como label_only
            ("Valor (R$):", "value", "entry", 
                lambda data: data.get('category_type') == 'Provento' and \
                             data.get('status') == 'Em Aberto'
            ), # ALTERADO: Editável se Provento E Em Aberto
            ("Status:", "status", "radios_status", True),
            ("Data Prevista:", "due_date", "entry", True),
            ("Data Pagamento:", "payment_date", "entry", True),
            ("Meio Pagamento:", "payment_method", "radios_payment_method", lambda data: data.get('status') == 'Pago' and data.get('category_type') == 'Despesa'),
        ]
        
        transaction_category_type = self.transaction_data.get('category_type')

        current_row = 0

        for label_text, db_key, widget_type, is_alterable in field_configs:
            customtkinter.CTkLabel(main_frame, text=label_text, font=FONTE_LABEL_FORM, anchor="w").grid(row=current_row, column=0, sticky="w", padx=5, pady=(5,2))
            
            display_widget = customtkinter.CTkLabel(main_frame, text="", font=FONTE_VALOR_FORM, anchor="w", height=BOTAO_HEIGHT)
            input_widget = None
            icon_widget = None
            radios_for_status = None
            radios_for_payment_method = None

             
            # Determina se o campo é alterável para ESTA transação específica
            is_alterable_for_this_field = is_alterable # Assume o valor padrão da config
            if callable(is_alterable): # Se a config for uma função, avalia
                 is_alterable_for_this_field = is_alterable(self.transaction_data)
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
                elif widget_type == "radios_payment_method":
                    input_widget = customtkinter.CTkFrame(main_frame, fg_color="transparent") # Frame para os radios de meio de pagamento
                    radio_cartao_consult = customtkinter.CTkRadioButton(input_widget, text="Cartão de Crédito", variable=self.payment_method_consult_var, value="Cartão de Crédito", font=FONTE_LABEL_FORM, state="disabled")
                    radio_cartao_consult.pack(side="left", padx=(0,10))
                    radio_conta_consult = customtkinter.CTkRadioButton(input_widget, text="Conta Corrente", variable=self.payment_method_consult_var, value="Conta Corrente", font=FONTE_LABEL_FORM, state="disabled")
                    radio_conta_consult.pack(side="left")
                    radios_for_payment_method = [radio_cartao_consult, radio_conta_consult]
                    # A linha abaixo é importante para garantir que o frame dos rádios
                    # não esteja visível ou interferindo no layout antes da edição ser ativada.
                    input_widget.grid_remove() # Adicionado: Garante que o frame dos rádios esteja escondido inicialmente
                elif widget_type == "entry":
                    input_widget = customtkinter.CTkEntry(main_frame, font=FONTE_VALOR_FORM, state="disabled", height=BOTAO_HEIGHT)
                
                if self.pencil_icon_image and is_alterable_for_this_field: # Só mostra o ícone se for alterável para esta transação
                    icon_widget = customtkinter.CTkLabel(main_frame, text="", image=self.pencil_icon_image)
            
            self.field_elements[db_key] = {
                "display": display_widget,
                "input": input_widget, # Será None para campos 'label_only' ou se não for alterável
                "icon": icon_widget,   # Será None se não for alterável ou se for status
                "row": current_row,    # Store the row for precise placement later
                "widget_type": widget_type,
                "is_alterable_for_this_transaction": is_alterable_for_this_field # Store the specific alterable state
            }
            if radios_for_status:
                self.field_elements[db_key]["radios"] = radios_for_status
            if radios_for_payment_method: # Adicionado para payment_method
                self.field_elements[db_key]["radios_pm"] = radios_for_payment_method

            # Posiciona o display_widget (Label de visualização)
            display_widget.grid(row=current_row, column=1, sticky="e", padx=5, pady=(5,2)) # Alinhado à direita
            
            # Posiciona o ícone se existir
            if icon_widget and is_alterable_for_this_field: # Só vincula o clique se o ícone existir e o campo for alterável
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

       

    # Chamada inicial para garantir que a visibilidade do meio de pagamento esteja correta
        self._update_payment_method_editability()
    def _update_form_fields(self):
        """Atualiza os campos do formulário com os dados de self.transaction_data."""
        if not self.transaction_data:
            return

        for db_key, elements in self.field_elements.items():
            display_widget = elements["display"]
            input_widget = elements["input"]
            widget_type = elements["widget_type"]
            raw_value = self.transaction_data.get(db_key)

            is_alterable_for_this_transaction = elements.get("is_alterable_for_this_transaction", False)
            
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
            elif db_key == "value": # Valor da Transação (Parcela ou À vista)
                value_float = raw_value if raw_value is not None else 0.0
                formatted_display_value = f"{value_float:,.2f}".replace(",", "#").replace(".", ",").replace("#", ".")
                display_text = f"R$ {formatted_display_value}"
                
                # Se o campo for editável (Provento) e estiver em modo de edição,
                # preenche o entry com os dígitos para a formatação
                if is_alterable_for_this_transaction and self.is_editing and input_widget:
                     # Remove formatação para inserir apenas dígitos no entry
                     input_text_or_val = "".join(filter(str.isdigit, formatted_display_value))
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
            elif db_key == "payment_method":
                display_text = raw_value if raw_value else "N/A"
                if widget_type == "radios_payment_method":
                    # Se display_text for "N/A", self.payment_method_consult_var.get() retornará "None" (string)
                    # Se display_text for um valor válido, ele será setado.
                    # Se raw_value for None, display_text é "N/A", e setamos para "None" (string)
                    self.payment_method_consult_var.set(display_text if display_text != "N/A" else "None")
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
                
                # Aplica formatação se estiver em modo de edição E o campo for um entry
                # e for um campo de data ou o campo de valor (se editável)
                # A formatação de data é aplicada se o campo estiver ativo para edição.
                if self.is_editing and widget_type != "label_only":
                    if db_key in ["due_date", "payment_date"] and input_widget.cget("state") == "normal":
                        self.format_date_entry(None, input_widget)
        
        # Após atualizar todos os campos, reavaliar a editabilidade do meio de pagamento
        # Isso é importante se _update_form_fields for chamado após uma alteração de dados (ex: salvar)
        # self._update_payment_method_editability() # Movido para _set_all_fields_to_display_mode e _setup_ui

    def _update_payment_method_editability(self, *args):
        """Controla a visibilidade e editabilidade do campo Meio de Pagamento."""
        if not hasattr(self, 'transaction_data') or not self.transaction_data:
            return # Ainda não carregou os dados da transação

        current_status_selection = self.status_var.get()
        transaction_category_type = self.transaction_data.get('category_type')
        pm_elements = self.field_elements.get("payment_method")

        if not pm_elements or not pm_elements.get("input"):
            return

        payment_method_frame = pm_elements["input"] # CTkFrame dos rádios
        radios_pm = pm_elements.get("radios_pm", [])
        icon_pm = pm_elements.get("icon")

        # Condição para o meio de pagamento ser relevante
        is_relevant = (current_status_selection == "Pago" and transaction_category_type == "Despesa")
        # O campo de status está atualmente em modo de edição?
        status_radios = self.field_elements.get("status", {}).get("radios", [])
        status_field_is_editable = any(r.cget("state") == "normal" for r in status_radios)

        if is_relevant and status_field_is_editable:
            payment_method_frame.grid(row=pm_elements["row"], column=1, sticky="ew", padx=5, pady=(5,2))
            for radio in radios_pm:
                radio.configure(state="normal")
            if icon_pm: # O ícone de lápis para payment_method não é usual se os rádios são habilitados diretamente
                icon_pm.grid_remove() # Normalmente, não mostramos lápis para rádios que são auto-habilitados

            current_pm_value = self.payment_method_consult_var.get()
            if current_pm_value == "None" or not current_pm_value: # "None" (string) ou vazio
                self.payment_method_consult_var.set("Conta Corrente") # Padrão
        else:
            payment_method_frame.grid_remove()
            if icon_pm and icon_pm.winfo_ismapped():
                icon_pm.grid_remove()
            for radio in radios_pm:
                radio.configure(state="disabled")
            # Não resetamos o payment_method_consult_var aqui, _update_form_fields fará isso com base nos dados.

    def _save_changes(self):
        if not self.transaction_data:
            CTkMessagebox(title="Erro", message="Dados da transação não encontrados.", icon="cancel", master=self)
            return

        try:
            # Coleta apenas os dados dos campos que são alteráveis
            updated_data = {"transaction_id": self.transaction_id}

            # --- Coleta e validação do campo 'value' (Valor) ---
            if "value" in self.field_elements and self.field_elements["value"].get("is_alterable_for_this_transaction", False):
                 value_elements = self.field_elements["value"]
                 if value_elements["input"].cget("state") == "normal": # Se o campo de valor estava ativo para edição
                     value_str_formatted = value_elements["input"].get().strip()
                     # Remove formatação para converter para float
                     value_str_for_float = value_str_formatted.replace(".", "").replace(",", ".")
                     updated_data["value"] = float(value_str_for_float)

            if "description" in self.field_elements:
                desc_elements = self.field_elements["description"]
                if desc_elements["input"].cget("state") == "normal":
                    updated_data["description"] = desc_elements["input"].get().strip()
                else:
                    updated_data["description"] = self.transaction_data.get("description", "").strip()

            # Se o campo 'value' NÃO for alterável para esta transação, usa o valor original
            if "value" not in updated_data: updated_data["value"] = self.transaction_data.get("value", 0.0)
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

            
            # Adicionar category_type ao updated_data para a validação, vindo dos dados originais da transação
            updated_data["category_type"] = self.transaction_data.get("category_type")

            # --- Coleta do Meio de Pagamento ---
            pm_elements = self.field_elements.get("payment_method")
            if pm_elements and pm_elements["input"]:
                # Se o NOVO status é "Pago" E o tipo é "Despesa" E o frame dos rádios está visível
                if updated_data["status"] == "Pago" and updated_data["category_type"] == "Despesa" and pm_elements["input"].winfo_ismapped():
                    pm_value_from_var = self.payment_method_consult_var.get()
                    if pm_value_from_var == "None" or not pm_value_from_var: # String "None" ou vazio
                        updated_data["payment_method"] = None # Considera não preenchido
                    else:
                        updated_data["payment_method"] = pm_value_from_var
                elif updated_data["status"] != "Pago": # Se o novo status não é "Pago", limpa o meio de pagamento
                    updated_data["payment_method"] = None
                else: # Status é Pago, mas tipo não é Despesa, ou campo não estava visível
                      # Mantém o valor original se o tipo for Despesa, senão None.
                    original_pm = self.transaction_data.get("payment_method")
                    # Note: This logic might need refinement if you want to preserve PM for Proventos Pago
                    updated_data["payment_method"] = original_pm if updated_data["category_type"] == "Despesa" else None
            
            if "category_name" in self.field_elements: # O input widget é para category_name
                cat_elements = self.field_elements["category_name"]
                selected_category_name = ""
                if cat_elements["input"].cget("state") == "normal":
                    selected_category_name = cat_elements["input"].get()
                else:
                    selected_category_name = self.transaction_data.get("category_name", "N/A")

                original_category_id = self.transaction_data.get("category_id") # Store original category ID
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

            # Validação crucial para meio de pagamento
            if updated_data.get("status") == "Pago" and updated_data["category_type"] == "Despesa" and not updated_data.get("payment_method"):
                CTkMessagebox(title="Erro de Validação", message="Meio de pagamento é obrigatório para despesas pagas.", icon="warning", master=self)
                return
            success = Database.update_transaction(
                transaction_id=updated_data["transaction_id"],
                description=updated_data["description"],
                value=updated_data["value"],
                due_date=updated_data["due_date"],
                payment_date=updated_data["payment_date"],
                status=updated_data["status"],
                category_id=updated_data["category_id"],
                payment_method=updated_data.get("payment_method") # Passa o meio de pagamento
            )

            if success:
                message = "Transação atualizada com sucesso!"

                # --- Check if category changed for a despesa installment and update group ---
                group_id = self.transaction_data.get('transaction_group_id')
                original_modality = self.transaction_data.get('modality')
                original_category_type = self.transaction_data.get('category_type')
                new_category_id = updated_data.get('category_id')

                # Check if it's a Despesa, part of a group (likely Parcelado or Fixo), and category changed
                if original_category_type == 'Despesa' and group_id and new_category_id != original_category_id:
                    # Check if it's actually a multi-part transaction (not a single 'À vista' with a group_id)
                    is_multi_installment = original_modality == 'Parcelado' or self.transaction_data.get('installments') != '1/1'

                    if is_multi_installment:
                        print(f"DEBUG: Category changed for Despesa installment (ID: {self.transaction_id}, Group ID: {group_id}). Updating group...")
                        group_update_success = Database.update_category_for_group(group_id, new_category_id)
                        if group_update_success:
                            message += "\nCategoria atualizada para todas as parcelas."
                CTkMessagebox(title="Sucesso", message="Transação atualizada com sucesso!", icon="check", master=self)
                # Call the callback BEFORE destroying the window
                if self.on_action_completed_callback:
                    self.on_action_completed_callback()
                self.after(50, self.destroy) # Schedule destruction after a short delay
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
        is_fixed_transaction = "(Fixo)" in desc and self.transaction_data.get('transaction_group_id')

        delete_scope = "group" # Padrão para excluir o grupo (parcelados ou fixos inteiros)
        proceed_with_delete = False

        if is_fixed_transaction:
            msg_box_fixed = CTkMessagebox(
                master=self,
                title="Excluir Transação Fixa",
                message=f"'{desc}' é uma transação fixa.\nComo deseja excluir?",
                icon="question",
                options=["Apenas esta", "Todas as recorrências", "Cancelar"]
            )
            response_fixed = msg_box_fixed.get()
            if response_fixed == "Apenas esta":
                delete_scope = "single"
                proceed_with_delete = True
            elif response_fixed == "Todas as recorrências":
                delete_scope = "group"
                proceed_with_delete = True
            else: # Cancelar ou fechou
                proceed_with_delete = False
        else: # Transação não é "Fixo" (pode ser parcelado normal ou à vista)
            msg_box_normal = CTkMessagebox(
                master=self,
                title="Confirmar Exclusão",
                message=f"Tem certeza que deseja excluir a transação:\n'{desc}'?\n(Se for parcelada, todas as parcelas serão excluídas)",
                icon="warning",
                options=["Cancelar", "Excluir"] # Manter ordem para que "Excluir" seja a segunda opção
            )
            response_normal = msg_box_normal.get()
            if response_normal == "Excluir":
                delete_scope = "group" # Para parcelados, sempre exclui o grupo
                proceed_with_delete = True
            else: # Cancelar ou fechou
                proceed_with_delete = False

        if proceed_with_delete:
            print(f"DEBUG: Proceeding with delete for transaction ID: {self.transaction_id} with scope: {delete_scope}")
            try:
                success = Database.delete_transaction(self.transaction_id, scope=delete_scope, is_fixed_group=is_fixed_transaction)
                if success:
                    # Ajusta a mensagem de sucesso
                    if delete_scope == "single":
                        message_suffix = "excluída"
                    elif is_fixed_transaction and delete_scope == "group":
                        message_suffix = "e suas recorrências em aberto foram excluídas"
                    elif not is_fixed_transaction and delete_scope == "group": # Parcelamento normal
                        message_suffix = "e suas parcelas foram excluídas"
                    else: # Fallback
                        message_suffix = "processada"
                    CTkMessagebox(title="Sucesso", message=f"Transação {message_suffix} com sucesso!", icon="check", master=self.master)
                    if self.on_action_completed_callback:
                        self.on_action_completed_callback()
                    
                    # Agenda a destruição da janela após um pequeno atraso,
                    # permitindo que a CTkMessagebox finalize suas operações (como retornar o foco).
                    self.after(50, self.destroy) # Atraso de 50ms
                else:
                    CTkMessagebox(title="Erro", message="Falha ao excluir a transação.", icon="cancel", master=self)
            except Exception as e:
                print(f"ERRO CRÍTICO durante a exclusão: {e}")
                CTkMessagebox(title="Erro Crítico", message=f"Ocorreu um erro inesperado durante a exclusão:\n{e}", icon="cancel", master=self)
        else:
            print(f"DEBUG: Exclusão cancelada pelo usuário ou não aplicável.")


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
        # Após habilitar os rádios de status, atualiza a visibilidade/editabilidade do meio de pagamento
            self._update_payment_method_editability()
        elif widget_type == "radios_payment_method":
            # Esta seção é para quando o usuário clica no ÍCONE de lápis do Meio de Pagamento.
            # A editabilidade principal é controlada por _update_payment_method_editability via mudança de status.
            # Se o campo for alterável (status já é Pago e tipo Despesa), habilita os rádios.
            if elements.get("is_alterable_for_this_transaction", False):
                for radio_pm in elements.get("radios_pm", []):
                    radio_pm.configure(state="normal")
                # Garante um valor selecionado se nenhum estiver
                if self.payment_method_consult_var.get() == "None" or not self.payment_method_consult_var.get():
                    self.payment_method_consult_var.set(self.transaction_data.get("payment_method") or "Conta Corrente")
        else: # entry, combobox
            input_widget.configure(state="normal")
            input_widget.focus() # Define o foco para o campo de entrada

         # Adiciona binds de formatação se for um campo de data ou o campo de valor
        if key in ["due_date", "payment_date"]:
            input_widget.bind("<KeyRelease>", lambda e, entry=input_widget: self.format_date_entry(e, entry))
            self.format_date_entry(None, input_widget) # Aplica formatação inicial
        elif key == "value": # Apenas para o campo de valor editável
            input_widget.bind("<KeyRelease>", lambda e, entry=input_widget: self.format_currency_input(e, entry))
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
            # A desabilitação dos rádios de payment_method é feita por _update_payment_method_editability
            else: # entry, combobox
                input_widget.configure(state="disabled")
        
        self.save_button.configure(state="disabled") # Desabilita o botão Salvar
        self.is_editing = False
        self._update_form_fields() # Atualiza os labels de display com os dados atuais
        self._update_payment_method_editability() # Garante que o meio de pagamento reflita o estado atual

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