# form_transacao.py
import customtkinter
import tkinter as tk # Necessário para o colorchooser funcionar corretamente com CTk
import re # Para verificar formatação de descrição
import datetime # Para obter a data atual
import uuid # Para gerar IDs únicos
# Importa as funções do banco de dados
import Database # Usando 'Database' com D maiúsculo conforme seu Main.py
from CTkMessagebox import CTkMessagebox # Adicionado para exibir alertas
# Importa a janela de formulário de cadastro de categoria
from form_cadastro_categoria import FormCadastroCategoriaWindow

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

# Prefixo para identificar itens não selecionáveis (títulos) no ComboBox
NON_SELECTABLE_PREFIX = "--- "

class FormTransacaoWindow(customtkinter.CTkToplevel):
    def __init__(self, master=None, current_user_id=None, tipo_transacao="Despesa", on_save_callback=None): # Adicionado on_save_callback
        super().__init__(master)
        self.title("Nova Transação")
        self.geometry("450x780") # Aumentada altura para garantir visibilidade de todos os campos
        self.configure(fg_color="#1c1c1c")
        self.lift()
        self.attributes("-topmost", True)
        self.grab_set()
        self.on_save_callback = on_save_callback # Armazena o callback

        self.minsize(400, 500)

        self.current_user_id = current_user_id
        self.tipo_transacao = tipo_transacao # Armazena o tipo para uso futuro, se necessário
        self.real_categories_map = {} # Para mapear nome de exibição para objeto de categoria real
        self.previous_category_selection = "Selecione a Categoria" # Para reverter seleção de título
        self.fixed_checkbox_var = customtkinter.BooleanVar(value=False) # Para o campo "Fixo" (Checkbox)
        self.form_cadastro_ref = None # Referência para a janela de cadastro de categoria

        # --- Frame Principal ---
        main_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        # Definindo as rows do main_frame
        main_frame.grid_rowconfigure(0, weight=0)  # title_label
        main_frame.grid_rowconfigure(1, weight=0)  # description_label
        main_frame.grid_rowconfigure(2, weight=0)  # description_entry
        main_frame.grid_rowconfigure(3, weight=0)  # category_label
        main_frame.grid_rowconfigure(4, weight=0)  # category_combobox
        main_frame.grid_rowconfigure(5, weight=0)  # link_cadastrar_categoria (Mantido na row 5)
        main_frame.grid_rowconfigure(6, weight=0)  # financial_details_frame (Movido para row 6)
        main_frame.grid_rowconfigure(7, weight=0)  # status_and_date_frame (Movido para row 7)
        main_frame.grid_rowconfigure(8, weight=0)  # fixed_checkbox_frame (NOVO: Checkbox Fixo na row 8)
        main_frame.grid_rowconfigure(9, weight=0)  # action_buttons_frame

        title_label = customtkinter.CTkLabel(main_frame, text="Cadastrar Nova Transação", font=FONTE_TITULO_FORM)
        title_label.grid(row=0, column=0, pady=(10, 20), sticky="ew")

        # Descrição
        description_label = customtkinter.CTkLabel(main_frame, text="Descrição:", font=FONTE_LABEL_FORM)
        description_label.grid(row=1, column=0, pady=(5,2), padx=10, sticky="w")
        self.description_entry = customtkinter.CTkEntry(main_frame, placeholder_text="Ex: Conta de Luz, Salário", height=BOTAO_HEIGHT, font=FONTE_INPUT_FORM)
        self.description_entry.grid(row=2, column=0, sticky="ew", padx=10, pady=(0,10))

        # Categoria
        category_label = customtkinter.CTkLabel(main_frame, text="Categoria:", font=FONTE_LABEL_FORM)
        category_label.grid(row=3, column=0, pady=(5,2), padx=10, sticky="w")

        # MOVIDO PARA CIMA: Criar self.fixed_checkbox_frame ANTES do ComboBox de categoria ser configurado com .set()
        # Isso evita AttributeError se o .set() inicial do ComboBox disparar o command que usa fixed_checkbox_frame.
        self.fixed_checkbox_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        self.fixed_checkbox_frame.grid(row=8, column=0, sticky="ew", padx=10, pady=(5,5)) # Posicionado na Row 8
        self.fixed_checkbox = customtkinter.CTkCheckBox(self.fixed_checkbox_frame, text="Fixo", variable=self.fixed_checkbox_var, font=FONTE_LABEL_FORM, command=self._fixed_checkbox_changed)
        self.fixed_checkbox.pack(anchor="w") # Alinha a checkbox à esquerda
        self.fixed_checkbox_frame.grid_forget() # Inicialmente escondido

        self.category_combobox = customtkinter.CTkComboBox(
            main_frame,
            values=["Carregando..."],
            height=BOTAO_HEIGHT,
            font=FONTE_INPUT_FORM,
            command=self.on_category_selected # Adiciona o command handler
        )
        self.category_combobox.set("Carregando...") # Este .set() pode disparar on_category_selected
        self.category_combobox.grid(row=4, column=0, sticky="ew", padx=10, pady=(0,10))

        # Link "Cadastrar Categoria"
        self.link_cadastrar_categoria = customtkinter.CTkLabel(main_frame, text="Cadastrar Nova Categoria...", font=FONTE_LINK, text_color="#8ab4f8", cursor="hand2")
        self.link_cadastrar_categoria.grid(row=5, column=0, padx=10, pady=(0,10), sticky="e") # Alinhado à direita
        self.link_cadastrar_categoria.bind("<Button-1>", self.open_form_cadastro_categoria)

        # --- Frame para Detalhes Financeiros (Valor, Modalidade, Parcelas) ---
        financial_details_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        financial_details_frame.grid(row=6, column=0, sticky="ew", padx=10, pady=(5,5)) # Posicionado na row 6

        financial_details_frame.grid_columnconfigure(0, weight=1) # Coluna para Valor (expande um pouco)
        financial_details_frame.grid_columnconfigure(1, weight=1) # Coluna para Modalidade/Parcelas

        # Valor (coluna 0, row 0 do financial_details_frame)
        value_container = customtkinter.CTkFrame(financial_details_frame, fg_color="transparent")
        value_container.grid(row=0, column=0, sticky="nw", padx=(0,10), pady=(0,5))
        value_label = customtkinter.CTkLabel(value_container, text="Valor:", font=FONTE_LABEL_FORM)
        value_label.pack(anchor="w", pady=(0,2)) # Ajustado pady
        self.value_entry = customtkinter.CTkEntry(value_container, placeholder_text="Ex: 150.75", height=BOTAO_HEIGHT, font=FONTE_INPUT_FORM, width=100) # Largura ajustada para 70px
        self.value_entry.pack(anchor="w")
        self.value_entry.bind("<KeyRelease>", self.format_currency_input) # Tenta formatar enquanto digita

        # Modalidade (coluna 1, row 0 do financial_details_frame)
        modality_container = customtkinter.CTkFrame(financial_details_frame, fg_color="transparent")
        modality_container.grid(row=0, column=1, sticky="new", padx=(0,0), pady=(0,5)) # sticky="new" para expandir horizontalmente
        modality_title_label = customtkinter.CTkLabel(modality_container, text="Modalidade:", font=FONTE_LABEL_FORM)
        modality_title_label.pack(anchor="w", pady=(0,2)) # Ajustado pady
        modality_buttons_inner_frame = customtkinter.CTkFrame(modality_container, fg_color="transparent")
        modality_buttons_inner_frame.pack(anchor="w")

        self.modality_var = customtkinter.StringVar(value="À vista")
        self.modality_radio_avista = customtkinter.CTkRadioButton(modality_buttons_inner_frame, text="À vista", variable=self.modality_var, value="À vista",
                                                                  font=FONTE_LABEL_FORM, command=self.update_installment_fields_visibility)
        self.modality_radio_avista.pack(side="left", padx=(0,10))
        self.modality_radio_parcelado = customtkinter.CTkRadioButton(modality_buttons_inner_frame, text="Parcelado", variable=self.modality_var, value="Parcelado",
                                                                    font=FONTE_LABEL_FORM, command=self.update_installment_fields_visibility)
        self.modality_radio_parcelado.pack(side="left", padx=5)

        # Parcelas (condicional, coluna 1, row 1 do financial_details_frame)
        self.installments_frame = customtkinter.CTkFrame(financial_details_frame, fg_color="transparent")
        # O grid do installments_frame (row=1, col=1 em financial_details_frame) será gerenciado por update_installment_fields_visibility
        self.installments_frame.grid_columnconfigure(0, weight=0) # Label
        self.installments_frame.grid_columnconfigure(1, weight=1) # Combobox

        installments_label = customtkinter.CTkLabel(self.installments_frame, text="Parcelas:", font=FONTE_LABEL_FORM)
        installments_label.grid(row=0, column=0, padx=(0,5), pady=(0,2), sticky="w")
        installments_values = [str(i) for i in range(2, 25)] # Aumentado de 11 para 25 (para incluir 24)
        self.installments_combobox = customtkinter.CTkComboBox(self.installments_frame, values=installments_values, height=BOTAO_HEIGHT, font=FONTE_INPUT_FORM, width=60) # Largura reduzida
        self.installments_combobox.set("2") # Valor padrão se parcelado
        self.installments_combobox.grid(row=0, column=1, padx=(0,5), pady=0, sticky="w")

        # --- Frame para Status e Datas ---
        self.status_and_date_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        self.status_and_date_frame.grid(row=7, column=0, sticky="ew", padx=10, pady=(5,5)) # Posicionado na Row 7

        # --- Elementos de Status (dentro de status_and_date_frame) ---
        status_elements_container = customtkinter.CTkFrame(self.status_and_date_frame, fg_color="transparent")
        status_elements_container.pack(anchor="w", pady=(0, 5), padx=0) # Alinha à esquerda

        status_title_label = customtkinter.CTkLabel(status_elements_container, text="Status:", font=FONTE_LABEL_FORM)
        status_title_label.pack(anchor="w", pady=(0,2)) # Ajustado pady

        status_buttons_inner_frame = customtkinter.CTkFrame(status_elements_container, fg_color="transparent")
        status_buttons_inner_frame.pack(anchor="w") # Alinhado à esquerda dentro do container

        self.status_var = customtkinter.StringVar(value="Em Aberto") # Variável para controlar o status
        self.status_radio_aberto = customtkinter.CTkRadioButton(status_buttons_inner_frame, text="Em Aberto", variable=self.status_var, value="Em Aberto",
                                                                font=FONTE_LABEL_FORM, command=self.update_date_fields_visibility)
        self.status_radio_aberto.pack(side="left", padx=(0,10))
        self.status_radio_pago = customtkinter.CTkRadioButton(status_buttons_inner_frame, text="Pago", variable=self.status_var, value="Pago",
                                                              font=FONTE_LABEL_FORM, command=self.update_date_fields_visibility)
        self.status_radio_pago.pack(side="left", padx=5)
        
        # --- Container para os campos de data ativos (dentro de status_and_date_frame, abaixo de status) ---
        self.active_date_fields_container = customtkinter.CTkFrame(self.status_and_date_frame, fg_color="transparent")
        # Empacota o container de campos de data ativos aqui, uma única vez.
        self.active_date_fields_container.pack(anchor="w", pady=(5,0), padx=0)

        # Data Prevista (elementos criados, mas não necessariamente visíveis)
        self.due_date_label_ref = customtkinter.CTkLabel(self.active_date_fields_container, text="Data Prevista:", font=FONTE_LABEL_FORM)
        self.due_date_entry = customtkinter.CTkEntry(self.active_date_fields_container, placeholder_text=datetime.date.today().strftime("%d/%m/%Y"), height=BOTAO_HEIGHT, font=FONTE_INPUT_FORM, width=110) # Largura reduzida
        self.due_date_entry.bind("<KeyRelease>", lambda e: self.format_date_entry(e, self.due_date_entry))
        self.due_date_entry.insert(0, datetime.date.today().strftime("%d/%m/%Y")) # Insere data atual como placeholder visível

        # Data de Pagamento (elementos criados, mas não necessariamente visíveis)
        self.payment_date_label_ref = customtkinter.CTkLabel(self.active_date_fields_container, text="Data Pagamento:", font=FONTE_LABEL_FORM)
        self.payment_date_entry = customtkinter.CTkEntry(self.active_date_fields_container, placeholder_text="DD/MM/AAAA", height=BOTAO_HEIGHT, font=FONTE_INPUT_FORM, width=110) # Largura reduzida
        self.payment_date_entry.bind("<KeyRelease>", lambda e: self.format_date_entry(e, self.payment_date_entry))
        # Configura o grid do container de data ativo para alinhar o label e o entry
        self.active_date_fields_container.grid_columnconfigure(0, weight=0) # Label
        self.active_date_fields_container.grid_columnconfigure(1, weight=0) # Entry

        # AGORA CHAME load_categories_for_combobox APÓS os rádios de modalidade E fixed_checkbox_frame serem criados
        self.load_categories_for_combobox()

        self.update_date_fields_visibility() # Chama para configurar o estado inicial dos campos de data
        self.update_installment_fields_visibility() # Chama para configurar o estado inicial do campo de parcelas

        # Frame para os botões Salvar e Fechar
        action_buttons_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        action_buttons_frame.grid(row=9, column=0, pady=(15,10), sticky="ew") # Movido para Row 9
        action_buttons_frame.grid_columnconfigure(0, weight=1) # Espaço antes do botão Salvar
        action_buttons_frame.grid_columnconfigure(1, weight=0) # Botão Salvar
        action_buttons_frame.grid_columnconfigure(2, weight=0) # Botão Fechar
        action_buttons_frame.grid_columnconfigure(3, weight=1) # Espaço depois do botão Fechar

        # Botão Salvar Transação (agora dentro do action_buttons_frame)
        save_button = customtkinter.CTkButton(main_frame, text="Salvar Transação", command=self.save_transaction,
                                                       height=BOTAO_HEIGHT, font=FONTE_BOTAO_FORM, corner_radius=BOTAO_CORNER_RADIUS,
                                                       fg_color=BOTAO_FG_COLOR, hover_color=BOTAO_HOVER_COLOR)
        save_button.grid(in_=action_buttons_frame, row=0, column=1, padx=5)

        # Botão Fechar (agora dentro do action_buttons_frame)
        close_button = customtkinter.CTkButton(main_frame, text="Fechar", command=self.destroy, height=BOTAO_HEIGHT, font=FONTE_BOTAO_FORM, corner_radius=BOTAO_CORNER_RADIUS, fg_color="gray50", hover_color="gray40")
        close_button.grid(in_=action_buttons_frame, row=0, column=2, padx=5)

    def on_category_selected(self, selected_value):
        """Chamado quando um item é selecionado no ComboBox de categoria."""
        if selected_value.startswith(NON_SELECTABLE_PREFIX):
            # Se um "título" for selecionado, reverte para a seleção anterior válida
            self.category_combobox.set(self.previous_category_selection)
            self._update_fixed_checkbox_visibility(None) # Esconde o campo fixo
        else:
            # Se for uma categoria real ou "Selecione...", atualiza a seleção anterior
            self.previous_category_selection = selected_value

            selected_category_obj = self.real_categories_map.get(selected_value.strip())
            # self.update_fixo_related_fields(selected_category_obj) # REMOVED: This method does not exist and logic is handled by _update_fixed_checkbox_visibility
            self._update_fixed_checkbox_visibility(selected_category_obj)

    def _update_fixed_checkbox_visibility(self, selected_category_obj):
        """Mostra/esconde o campo 'Fixo' com base na seleção de categoria."""
        is_valid_category_selected = selected_category_obj is not None
        if is_valid_category_selected:
            self.fixed_checkbox_frame.grid(row=8, column=0, sticky="ew", padx=10, pady=(5,5)) # Mostra na row 8
        else:
            self.fixed_checkbox_frame.grid_forget() # Esconde
            self.fixed_checkbox_var.set(False) # Reseta o estado da checkbox
            self._fixed_checkbox_changed() # Atualiza campos relacionados

        self.update_idletasks() # Força a atualização do layout

    def _fixed_checkbox_changed(self):
        """Ajusta campos de modalidade e parcelas com base no estado da checkbox 'Fixo'."""
        if self.fixed_checkbox_var.get(): # Se "Fixo" está marcado
            self.modality_var.set("À vista")
            self.modality_radio_avista.configure(state="disabled")
            self.modality_radio_parcelado.configure(state="disabled")
            self.installments_frame.grid_forget() # Esconde parcelas
        else: # Se "Fixo" não está marcado
            self.modality_radio_avista.configure(state="normal")
            self.modality_radio_parcelado.configure(state="normal")
            self.update_installment_fields_visibility() # Controla visibilidade de parcelas normalmente
        
        # Garante que o foco não fique preso em um radio button desabilitado
        if self.modality_radio_avista.cget("state") == "disabled":
            self.description_entry.focus()
        
    def load_categories_for_combobox(self):
        """Carrega as categorias na ComboBox, agrupadas por tipo."""
        self.category_combobox.configure(values=["Carregando..."])
        self.category_combobox.set("Carregando...")
        self.real_categories_map.clear()
        self.previous_category_selection = "Selecione a Categoria" # Reset

        if not self.current_user_id:
            self.category_combobox.configure(values=["Nenhum usuário logado"])
            self.category_combobox.set("Nenhum usuário logado")
            return

        all_categories = Database.get_categories_by_user(self.current_user_id)
        if not all_categories:
            self.category_combobox.configure(values=["Nenhuma categoria cadastrada"])
            self.category_combobox.set("Nenhuma categoria cadastrada")
            return
        
        despesa_cats = sorted([cat for cat in all_categories if cat['type'] == 'Despesa'], key=lambda x: x['name'])
        provento_cats = sorted([cat for cat in all_categories if cat['type'] == 'Provento'], key=lambda x: x['name'])

        display_values = ["Selecione a Categoria"]
        self.real_categories_map["Selecione a Categoria"] = None # Placeholder

        if despesa_cats:
            display_values.append(f"{NON_SELECTABLE_PREFIX}DESPESAS{NON_SELECTABLE_PREFIX[3:]}") # Ex: --- DESPESAS ---
            for cat in despesa_cats:
                display_name = f"  {cat['name']}" # Adiciona indentação
                display_values.append(display_name)
                self.real_categories_map[display_name.strip()] = cat # Chave sem indentação

        if provento_cats:
            display_values.append(f"{NON_SELECTABLE_PREFIX}PROVENTOS{NON_SELECTABLE_PREFIX[3:]}") # Ex: --- PROVENTOS ---
            for cat in provento_cats:
                display_name = f"  {cat['name']}" # Adiciona indentação
                display_values.append(display_name)
                self.real_categories_map[display_name.strip()] = cat # Chave sem indentação
        
        self.category_combobox.configure(values=display_values)
        self.category_combobox.set("Selecione a Categoria")
        self._update_fixed_checkbox_visibility(None) # Garante que o campo fixo esteja no estado correto

    def save_transaction(self):
        description = self.description_entry.get().strip()
        selected_category_display_name = self.category_combobox.get()
        value_str = self.value_entry.get().strip()
        due_date_input = self.due_date_entry.get().strip()
        payment_date_input = self.payment_date_entry.get().strip()
        status = self.status_var.get()
        modality = self.modality_var.get()
        fixed_selection = self.fixed_checkbox_var.get() # Obtém o estado da checkbox
        print(f"DEBUG form_transacao: Modality to be saved: '{modality}'")
        installments = None

        # Validações básicas
        if not description:
            print("Descrição é obrigatória.") # TODO: Mostrar alerta na GUI
            CTkMessagebox(title="Erro de Validação", message="Descrição é obrigatória.", icon="warning", master=self)
            return
        if selected_category_display_name in ["Selecione a Categoria", "Carregando...", "Nenhuma categoria cadastrada"] or \
           selected_category_display_name.startswith(NON_SELECTABLE_PREFIX):
            CTkMessagebox(title="Erro de Validação", message="Por favor, selecione uma categoria válida.", icon="warning", master=self)
            return
        if not value_str:
            print("Valor é obrigatório.") # TODO: Mostrar alerta na GUI
            return

        try:
            # Primeiro, remove os pontos (separadores de milhar)
            value_str_no_thousands = value_str.replace(".", "")
            # Depois, substitui a vírgula (separador decimal) por um ponto
            value_str_for_float = value_str_no_thousands.replace(",", ".")
            value = float(value_str_for_float)
        except ValueError:
            print(f"Valor inválido '{value_str}'. Após tratamento: '{value_str_for_float}'. Não foi possível converter para float.") # TODO: Mostrar alerta na GUI
            CTkMessagebox(title="Erro de Validação", message=f"Valor '{value_str}' é inválido.", icon="warning", master=self)
            return

        # Obter o objeto da categoria real
        selected_category_obj = self.real_categories_map.get(selected_category_display_name.strip())
        if not selected_category_obj:
             CTkMessagebox(title="Erro Interno", message=f"Categoria '{selected_category_display_name}' não encontrada no mapeamento.", icon="cancel", master=self)
             return

         # Se "Fixo" está marcado, ignora a modalidade da UI e força "À vista"
        if fixed_selection:
            modality = "À vista" # Força para o DB
            installments = 1
        elif modality == "Parcelado": # Se não for Provento Fixo, e for Parcelado
            installments_str = self.installments_combobox.get()
            if not installments_str.isdigit() or not (2 <= int(installments_str) <= 48): # TODO: Usar constante para max parcelas
                CTkMessagebox(title="Erro de Validação", message="Número de parcelas inválido. Deve ser um número entre 2 e 48.", icon="warning", master=self)
                return
            installments = int(installments_str)
        else: # À vista (ou Provento Fixo "Não")
            installments = 1 # Ou None, dependendo de como você quer armazenar no DB
        
        due_date_db = None
        payment_date_db = None
        error_message = None # Variável para armazenar mensagens de erro específicas

        if status == "Em Aberto":
            if not due_date_input:
                print("Data Prevista é obrigatória para status 'Em Aberto'.") # TODO: Mostrar alerta na GUI
                CTkMessagebox(title="Erro de Validação", message="Data Prevista é obrigatória para status 'Em Aberto'.", icon="warning", master=self)
                return
            try:
                due_date_db = datetime.datetime.strptime(due_date_input, "%d/%m/%Y").strftime("%Y-%m-%d")
            except ValueError:
                error_message = "Formato de Data Prevista inválido. Use DD/MM/AAAA."
                CTkMessagebox(title="Erro de Validação", message=error_message, icon="warning", master=self)
                return
        elif status == "Pago":
                        # Validações para status 'Pago'
            if not payment_date_input:
                error_message = "Data de Pagamento é obrigatória para status 'Pago'."
                return
            try:
                payment_date_db = datetime.datetime.strptime(payment_date_input, "%d/%m/%Y").strftime("%Y-%m-%d")
                # Se status é Pago, e due_date_input está vazio (porque o campo foi escondido pela UI),
                
                # --- NOVA VALIDAÇÃO: Não permitir data de pagamento futura se status for 'Pago' ---
                payment_date_obj = datetime.datetime.strptime(payment_date_input, "%d/%m/%Y").date() # Converte para objeto date para comparação
                if payment_date_obj > datetime.date.today():
                     CTkMessagebox(title="Erro de Validação", message="A Data de Pagamento não pode ser uma data futura para transações 'Pagas'.", icon="warning", master=self)
                     return # Interrompe o salvamento
                # definimos due_date_db como payment_date_db.
                # Se due_date_input não estiver vazio (cenário menos provável com a UI atual), tentamos convertê-lo.
                if due_date_input: # Caso o campo de data prevista esteja visível e preenchido
                    due_date_db = datetime.datetime.strptime(due_date_input, "%d/%m/%Y").strftime("%Y-%m-%d")
                else:
                    due_date_db = payment_date_db # Data prevista será a mesma da data de pagamento
            except ValueError:
                error_message = "Formato de Data de Pagamento (ou Data Prevista, se visível) inválido. Use DD/MM/AAAA."
                CTkMessagebox(title="Erro de Validação", message=error_message, icon="warning", master=self)
                return
        else: # Status desconhecido
            error_message = f"Status desconhecido: {status}"
            return

        if error_message:
            CTkMessagebox(title="Erro de Validação", message=error_message, icon="warning", master=self)
            return

        transaction_type_for_message = selected_category_obj['type']

        all_saves_successful = True

        if fixed_selection: # A lógica de replicação agora se aplica a qualquer transação "Fixo: Sim"
            num_fixed_transactions = 24
            original_due_date_obj = datetime.datetime.strptime(due_date_db, "%Y-%m-%d").date()
            fixed_transaction_group_id = str(uuid.uuid4()) # ID de grupo para todas as transações fixas

            for i in range(num_fixed_transactions):
                current_transaction_id = str(uuid.uuid4())
                current_description = f"{description} (Fixo)" # Alterado aqui
                
                if i == 0: # Primeira transação (a que o usuário está inserindo)
                    current_due_date_db = due_date_db
                    current_payment_date_db = payment_date_db
                    current_status = status
                else: # Transações replicadas
                    # Calcular próxima data de vencimento
                    next_due_date_obj = original_due_date_obj
                    for _ in range(i): # Adiciona 'i' meses à data original
                        new_month = next_due_date_obj.month + 1
                        new_year = next_due_date_obj.year
                        if new_month > 12:
                            new_month = 1
                            new_year += 1
                        try:
                            next_due_date_obj = next_due_date_obj.replace(year=new_year, month=new_month)
                        except ValueError: # Dia inválido para o novo mês (ex: Jan 31 -> Fev)
                            if new_month == 12: next_due_date_obj = datetime.date(new_year + 1, 1, 1) - datetime.timedelta(days=1)
                            else: next_due_date_obj = datetime.date(new_year, new_month + 1, 1) - datetime.timedelta(days=1)
                    
                    current_due_date_db = next_due_date_obj.strftime("%Y-%m-%d")
                    current_payment_date_db = None
                    current_status = "Em Aberto"

                success_repl = Database.add_transaction(
                    transaction_id_base=current_transaction_id, user_id=self.current_user_id,
                    category_id=selected_category_obj['id'], original_description=current_description,
                    total_value=value, initial_due_date=current_due_date_db,
                    initial_payment_date=current_payment_date_db, 
                    initial_status=current_status,
                    modality="À vista", num_installments=1, # Força para transação fixa
                    transaction_group_id=fixed_transaction_group_id # Passa o ID do grupo
                )
                if not success_repl: all_saves_successful = False
        else: # Transação normal (não é Provento Fixo "Sim")
            transaction_id = str(uuid.uuid4())
            group_id_for_normal = transaction_id if modality == "À vista" else transaction_id # Para parcelado, o add_transaction usará o transaction_id como base para o group_id
            all_saves_successful = Database.add_transaction(
                transaction_id_base=transaction_id, user_id=self.current_user_id,
                category_id=selected_category_obj['id'], original_description=description,
                total_value=value, initial_due_date=due_date_db,
                initial_payment_date=payment_date_db, initial_status=status,
                modality=modality, num_installments=installments,
                transaction_group_id=group_id_for_normal
            )

        if all_saves_successful:
            message = f"{transaction_type_for_message} salva com sucesso!"
            if fixed_selection: # Mensagem ajustada para qualquer transação fixa
                message = f"{num_fixed_transactions} transações de {transaction_type_for_message.lower()} fixo foram salvas!"
            CTkMessagebox(title="Sucesso", message=message, icon="check", master=self)
            # Limpar campos
            self.description_entry.delete(0, customtkinter.END)
            self.value_entry.delete(0, customtkinter.END)
            self.due_date_entry.delete(0, customtkinter.END)
            self.due_date_entry.insert(0, datetime.date.today().strftime("%d/%m/%Y")) # Reseta para data atual
            self.payment_date_entry.delete(0, customtkinter.END)
            self.status_var.set("Em Aberto") # Reseta status
            self.modality_var.set("À vista") # Reseta modalidade (isso chamará update_installment_fields_visibility)
            self.fixed_checkbox_var.set(False) # Reseta fixo para o BooleanVar
            self.installments_combobox.set("2") # Reseta parcelas
            self.update_date_fields_visibility() # Atualiza a visibilidade dos campos de data
            self.update_installment_fields_visibility() # Atualiza visibilidade do campo de parcelas
            self.description_entry.focus() # Foca no primeiro campo
            self.load_categories_for_combobox() # Recarrega e reseta o combobox de categorias (isso chamará update_fixo_related_fields)
            # self.update_fixo_related_fields(None) # Garante que campos relacionados ao fixo sejam resetados
            if self.on_save_callback: # Chama o callback se ele foi fornecido (ex: para atualizar o Dashboard)
                self.on_save_callback()
        else:
            CTkMessagebox(title="Erro", message=f"Falha ao salvar {transaction_type_for_message.lower()}. Verifique os dados e tente novamente.", icon="cancel", master=self)

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

            self.form_cadastro_ref = FormCadastroCategoriaWindow(master=self, current_user_id=self.current_user_id, on_close_callback=on_category_form_closed_callback)
            self.form_cadastro_ref.on_close_callback = on_category_form_closed_callback
            self.form_cadastro_ref.protocol("WM_DELETE_WINDOW", on_category_form_closed_callback)
            self.form_cadastro_ref.focus()
        else:
            self.form_cadastro_ref.focus() # Se já existir, apenas foca nela

    def update_installment_fields_visibility(self):
        """Controla a visibilidade do campo de parcelas com base na modalidade."""
        modality = self.modality_var.get()
        if modality == "Parcelado":
            # Só mostra se o campo "Fixo" NÃO estiver marcado
            if not self.fixed_checkbox_var.get():
                self.installments_frame.grid(row=1, column=1, sticky="nw", padx=(0,0), pady=(5,0)) # Gridding dentro de financial_details_frame, abaixo de modalidade
                self.installments_combobox.configure(state="normal")
        else: # À vista
            self.installments_frame.grid_forget() # Esconde o frame de parcelas


    def update_date_fields_visibility(self):
        """Controla a visibilidade e o estado dos campos de data com base no status."""
        # Esconde todos os campos de data e seus rótulos primeiro
        self.due_date_label_ref.grid_forget()
        self.due_date_entry.grid_forget()
        self.payment_date_label_ref.grid_forget()
        self.payment_date_entry.grid_forget()

        # Força o processamento das remoções do grid antes de adicionar novos widgets.
        self.active_date_fields_container.update_idletasks()

        status = self.status_var.get()
        if status == "Pago":
            # Configura e mostra Data Pagamento
            self.payment_date_label_ref.grid(row=0, column=0, sticky="w", pady=(0,2), padx=(0,5))
            self.payment_date_entry.grid(row=0, column=1, sticky="w", pady=(0,0))
            self.payment_date_entry.configure(state="normal") # Habilita
            if not self.payment_date_entry.get(): # Se estiver vazio, preenche com data atual
                self.payment_date_entry.insert(0, datetime.date.today().strftime("%d/%m/%Y"))
            # Garante que o campo de data prevista esteja limpo e desabilitado
            self.due_date_entry.delete(0, customtkinter.END)
            self.due_date_entry.configure(state="disabled")
        else: # Em Aberto
            # Configura e mostra Data Prevista
            self.due_date_label_ref.grid(row=0, column=0, sticky="w", pady=(0,2), padx=(0,5))
            self.due_date_entry.grid(row=0, column=1, sticky="w", pady=(0,0))
            self.due_date_entry.configure(state="normal") # Habilita
            # Garante que o campo de data de pagamento esteja limpo e desabilitado
            self.payment_date_entry.delete(0, customtkinter.END)
            self.payment_date_entry.configure(state="disabled")

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

    def format_currency_input(self, event=None):
        """Formata o valor como moeda (R$ X.XXX,XX) enquanto o usuário digita apenas números."""
        entry_widget = self.value_entry
        current_text = entry_widget.get()

        # 1. Extrair apenas os dígitos do texto atual
        digits_only = "".join(filter(str.isdigit, current_text))

        # 2. Lógica de formatação baseada no número de dígitos
        if not digits_only:
            formatted_value = "0,00"
        elif len(digits_only) == 1: # Ex: 2 -> 0,02
            formatted_value = f"0,0{digits_only}"
        elif len(digits_only) == 2: # Ex: 25 -> 0,25
            formatted_value = f"0,{digits_only}"
        else: # len(digits_only) > 2. Ex: 250 -> 2,50; 250099 -> 2.500,99
            decimal_part = digits_only[-2:]
            integer_part_str = digits_only[:-2]

            # Formatar parte inteira com separadores de milhar (ponto)
            # Remove zeros à esquerda da parte inteira, a menos que seja apenas "0"
            integer_part_str_cleaned = integer_part_str.lstrip('0')
            if not integer_part_str_cleaned: # Se ficou vazio após lstrip (ex: "00" se tornou "")
                integer_part_str_cleaned = "0"
            
            parts = []
            while integer_part_str_cleaned:
                parts.append(integer_part_str_cleaned[-3:])
                integer_part_str_cleaned = integer_part_str_cleaned[:-3]
            
            formatted_integer_part = ".".join(reversed(parts)) if parts else "0"
            formatted_value = f"{formatted_integer_part},{decimal_part}"

        entry_widget.delete(0, customtkinter.END)
        entry_widget.insert(0, formatted_value)
        entry_widget.icursor(len(formatted_value)) # Move o cursor para o final

if __name__ == '__main__':
    app = customtkinter.CTk()
    app.withdraw()
    # Teste para Despesa
    # form_trans = FormTransacaoWindow(master=app, current_user_id="01", tipo_transacao="Despesa")
    # Teste para Provento
    form_trans = FormTransacaoWindow(master=app, current_user_id="01", tipo_transacao="Provento")
    app.mainloop()