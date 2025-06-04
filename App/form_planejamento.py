import customtkinter
# import tkinter as tk # Para constantes de alinhamento
# Importa funções do Database (pode ser necessário no futuro para planejamento)
import Database # Importa o módulo Database para buscar transações
import datetime # Para formatação de datas
import re # Para manipulação de strings (descrição da transação)
from form_consulta_transacao import FormConsultaTransacaoWindow # Para abrir detalhes da transação
from form_simulador import FormSimuladorWindow # Importar o formulário de simulador

# Definições de fonte padrão (pode ajustar conforme necessário)
FONTE_FAMILIA = "Segoe UI"
FONTE_TITULO_FORM = (FONTE_FAMILIA, 18, "bold")
FONTE_BOTAO_MES = (FONTE_FAMILIA, 12, "bold")
FONTE_LABEL_NORMAL = (FONTE_FAMILIA, 12)
FONTE_LABEL_BOLD = (FONTE_FAMILIA, 12, "bold")
FONTE_LABEL_PEQUENA = (FONTE_FAMILIA, 10)
BOTAO_CORNER_RADIUS = 10
BOTAO_FG_COLOR = "gray25"
BOTAO_HOVER_COLOR = "#2E8B57" # Um verde para hover
BOTAO_HEIGHT = 40

# Estilos para botões de ação (copiados do Dashboard para consistência)
FONTE_BOTAO_ACAO = (FONTE_FAMILIA, 13, "bold")
BOTAO_ACAO_HEIGHT = 35
BOTAO_ACAO_CORNER_RADIUS = 17
BOTAO_ACAO_FG_COLOR = "gray30"
BOTAO_ACAO_HOVER_COLOR = "#2196F3" # Azul para hover


class PlanejamentoView(customtkinter.CTkFrame): # Herda de CTkFrame
    def __init__(self, master=None, current_user_id=None, selected_year=None, close_callback=None, main_dashboard_refresh_callback=None): # Adicionado main_dashboard_refresh_callback
        super().__init__(master)
        self.configure(fg_color="transparent") # O frame em si será transparente
        self.close_callback = close_callback
        self.main_dashboard_refresh_callback = main_dashboard_refresh_callback # Armazena o callback


        self.current_user_id = current_user_id
        self.selected_year = selected_year
        self.months_list = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        self.current_month_name_selected = None # Para rastrear o mês selecionado
        self.all_transactions_for_month = [] # Para armazenar as transações do mês selecionado
        self.form_consulta_transacao_window = None # Referência para a janela de consulta

        # --- Frame Principal ---
        main_frame = customtkinter.CTkFrame(self, fg_color="#1c1c1c") # Cor de fundo para a view
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        # Configurar grid para o main_frame
        main_frame.grid_columnconfigure(0, weight=1) # Coluna única para expandir
        main_frame.grid_rowconfigure(0, weight=0) # Título "Selecione o Mês"
        main_frame.grid_rowconfigure(1, weight=0) # Botões dos meses (altura fixa)
        main_frame.grid_rowconfigure(2, weight=0) # Seção Despesas/Proventos do Mês (altura fixa)
        main_frame.grid_rowconfigure(3, weight=0) # Título "Resultado da Alocação" (altura fixa)
        main_frame.grid_rowconfigure(3, weight=0) # Container para Título e Botão Simular
        main_frame.grid_rowconfigure(4, weight=1) # Área de Resultado da Alocação (expande verticalmente)
        # main_frame.grid_rowconfigure(5, weight=0) # REMOVIDO: Botão Executar Simulação

        title_label = customtkinter.CTkLabel(main_frame, text=f"Planejamento ({selected_year})", font=FONTE_TITULO_FORM)
        title_label.grid(row=0, column=0, pady=(0, 20), sticky="ew")

        # Frame para os botões dos meses
        month_buttons_container = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        month_buttons_container.grid(row=1, column=0, pady=(0,10), sticky="ew")

        # Configurar grid para os botões (4 linhas, 3 colunas)
        for i in range(4): # 4 linhas
            month_buttons_container.grid_rowconfigure(i, weight=1)
        for i in range(3): # 3 colunas
            month_buttons_container.grid_columnconfigure(i, weight=1)

        for i, month_name in enumerate(self.months_list):
            row = i // 3  # Calcula a linha (0 a 3)
            col = i % 3   # Calcula a coluna (0 a 2)

            month_button = customtkinter.CTkButton(
                month_buttons_container,
                text=month_name,
                font=FONTE_BOTAO_MES,
                height=BOTAO_HEIGHT,
                corner_radius=BOTAO_CORNER_RADIUS,
                fg_color=BOTAO_FG_COLOR,
                hover_color=BOTAO_HOVER_COLOR,
                command=lambda m=month_name, y=self.selected_year, u=self.current_user_id: self.month_selected_for_planning(m, y, u)
            ) # Passa o nome do mês
            month_button.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        # --- Seção "Despesas" e "Proventos" do Mês (similar à tela de Detalhes) ---
        planning_details_section_container = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        planning_details_section_container.grid(row=2, column=0, sticky="ew", pady=(10, 10))
        planning_details_section_container.grid_columnconfigure(0, weight=1) # Coluna para Despesas do Mês
        planning_details_section_container.grid_columnconfigure(1, weight=1) # Coluna para Proventos do Mês
        planning_details_section_container.grid_rowconfigure(0, weight=0) # Linha única para os scrollables

        # Scrollable frame para "Despesas do Mês"
        self.despesas_planning_scroll_frame = customtkinter.CTkScrollableFrame(planning_details_section_container, label_text="Despesas do Mês", label_font=FONTE_LABEL_BOLD, fg_color="gray17", height=150) # Altura ajustada
        self.despesas_planning_scroll_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=5)

        # Scrollable frame para "Proventos do Mês"
        self.proventos_planning_scroll_frame = customtkinter.CTkScrollableFrame(planning_details_section_container, label_text="Proventos do Mês", label_font=FONTE_LABEL_BOLD, fg_color="gray17", height=150) # Altura ajustada
        self.proventos_planning_scroll_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=5)

        # --- Container para Título "Resultado da Alocação" e Botão Simular ---
        allocation_header_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        allocation_header_frame.grid(row=3, column=0, pady=(20, 5), sticky="ew")
        allocation_header_frame.grid_columnconfigure(0, weight=1) # Coluna para o título (expande)
        allocation_header_frame.grid_columnconfigure(1, weight=0) # Coluna para o botão (fixa)

        # Título "Resultado da Alocação" (agora dentro do allocation_header_frame)
        allocation_result_title_label = customtkinter.CTkLabel(allocation_header_frame, text="Resultado da Alocação", font=FONTE_TITULO_FORM)
        allocation_result_title_label.grid(row=0, column=0, sticky="w") # Alinha à esquerda na coluna 0

        # Botão "Simular" (agora dentro do allocation_header_frame)
        self.simulate_button = customtkinter.CTkButton(
            allocation_header_frame,
            text="Simular",
            font=FONTE_BOTAO_ACAO, # Usa a fonte dos botões de ação do Dashboard
            height=BOTAO_ACAO_HEIGHT, # Usa a altura dos botões de ação do Dashboard
            corner_radius=BOTAO_ACAO_CORNER_RADIUS, # Usa o raio dos botões de ação do Dashboard
            fg_color=BOTAO_ACAO_FG_COLOR, # Usa a cor de fundo dos botões de ação do Dashboard
            hover_color=BOTAO_ACAO_HOVER_COLOR, # Usa a cor de hover dos botões de ação do Dashboard
            command=self._open_simulador_window # Define o comando para abrir a janela do simulador
        )
        self.simulate_button.grid(row=0, column=1, sticky="e", padx=(10, 0)) # Alinha à direita na coluna 1

        # --- Área de Resultado da Alocação ---
        self.allocation_result_display_frame = customtkinter.CTkScrollableFrame(main_frame, fg_color="gray20", corner_radius=10)
        self.allocation_result_display_frame.grid(row=4, column=0, sticky="nsew", pady=(0, 10))
        self.allocation_result_display_frame.grid_columnconfigure(0, weight=1) # Coluna única para conteúdo
        # Placeholder inicial
        customtkinter.CTkLabel(self.allocation_result_display_frame, text="Selecione um mês para ver os resultados da alocação.", font=FONTE_LABEL_NORMAL, text_color="gray60").pack(pady=20, padx=20)

        # --- Frame para Botões de Ação Inferiores ---
        # REMOVIDO: O botão Fechar e o frame de ações inferiores foram removidos.
        # A responsabilidade de fechar a view agora é do Dashboard que a contém,
        # geralmente chamando destroy() nesta instância de PlanejamentoView
        # quando o usuário interage com o botão "Detalhes" ou "Dashboard" no menu lateral.
        # O callback self._handle_close ainda existe e pode ser chamado pelo Dashboard.

        # Referência para a janela do simulador
        self.form_simulador_window = None

        # Armazenar referências aos comboboxes das despesas
        self.despesa_provento_comboboxes = {} # {despesa_id: combobox_widget}

    def month_selected_for_planning(self, month_name, year, user_id):
        month_number = self.months_list.index(month_name) + 1
        print(f"DEBUG: month_selected_for_planning - Mês: {month_name}, Ano: {year}, User ID: {user_id}")
        self.current_month_name_selected = month_name # Salva para referência

        # Limpa as referências dos comboboxes das despesas ANTES de repopular as tabelas
        self.despesa_provento_comboboxes.clear()

        # Limpar conteúdo anterior das áreas de Despesas/Proventos Planejados
        for widget in self.despesas_planning_scroll_frame.winfo_children():
            widget.destroy()
        for widget in self.proventos_planning_scroll_frame.winfo_children():
            widget.destroy()

        # Buscar e exibir transações do mês selecionado
        self.all_transactions_for_month = Database.get_transactions_for_month(user_id, year, month_number)
        self._display_month_transactions()

        # Limpar e atualizar a área de resultado da alocação
        self._update_allocation_results()



    def _display_month_transactions(self):
        """Filtra e exibe as transações de despesas e proventos nas tabelas correspondentes."""
        despesas = [t for t in self.all_transactions_for_month if t['category_type'] == 'Despesa']
        proventos = [t for t in self.all_transactions_for_month if t['category_type'] == 'Provento']

        self._populate_transaction_table(self.despesas_planning_scroll_frame, despesas, "Despesa", proventos_do_mes=proventos)
        self._populate_transaction_table(self.proventos_planning_scroll_frame, proventos, "Provento", proventos_do_mes=None)

    def _populate_transaction_table(self, parent_frame, transactions, transaction_type, proventos_do_mes=None):
        """Popula uma tabela (frame) com as transações fornecidas."""
        # Limpa o conteúdo anterior do frame
        for widget in parent_frame.winfo_children():
            widget.destroy()

        print(f"DEBUG PlanejamentoView: _populate_transaction_table - Tipo: {transaction_type}, Transações recebidas: {len(transactions)}")
        # REMOVIDO: self.despesa_provento_comboboxes.clear() movido para month_selected_for_planning
        # print(f"DEBUG PlanejamentoView: Limpando self.despesa_provento_comboboxes (antes: {len(self.despesa_provento_comboboxes)}).")

        if not transactions:
            customtkinter.CTkLabel(
                parent_frame,
                text=f"Nenhuma transação de {transaction_type.lower()} para este mês.",
                font=FONTE_LABEL_NORMAL,
                text_color="gray60"
            ).grid(row=1, column=0, columnspan=9 if transaction_type == "Despesa" else 8, pady=20, padx=10)
            print(f"DEBUG PlanejamentoView: _populate_transaction_table - Exibindo mensagem 'Nenhuma transação' para {transaction_type}.")
            return

        # Cabeçalhos
        if transaction_type == "Despesa":
            col_weights = [1, 2, 2, 1, 1, 1, 1, 1, 2] # 9 colunas para Despesa
            headers = ["Data", "Descrição", "Categoria", "V. Parcela", "V. Total", "Status", "Modalidade", "Parcela", "Provento Associado"]
        else: # Provento
            col_weights = [1, 3, 2, 1, 1, 1, 1, 1] # 8 colunas para Provento
            headers = ["Data", "Descrição", "Categoria", "V. Parcela", "V. Total", "Status", "Modalidade", "Parcela"]

        for i, header_text in enumerate(headers):
            parent_frame.grid_columnconfigure(i, weight=col_weights[i])
            anchor_val = "w" if header_text in ["Descrição", "Categoria", "V. Parcela", "V. Total", "Provento Associado"] else "center"
            customtkinter.CTkLabel(
                parent_frame,
                text=header_text,
                font=FONTE_LABEL_PEQUENA, # Usar FONTE_LABEL_PEQUENA para caber mais
                anchor=anchor_val
            ).grid(row=0, column=i, sticky="ew", padx=2)

        # Linhas de Transação
        for row_idx, trans in enumerate(transactions, start=1):
            print(f"DEBUG PlanejamentoView: _populate_transaction_table - Processando {transaction_type} ID: {trans.get('id')}, Desc: {trans.get('description')}")
            widgets = []
            # Data
            try:
                due_date_obj = datetime.datetime.strptime(trans['due_date'], "%Y-%m-%d")
                formatted_date = due_date_obj.strftime("%d/%m/%Y")
            except (ValueError, TypeError):
                formatted_date = trans['due_date']
            widgets.append(customtkinter.CTkLabel(parent_frame, text=formatted_date, font=FONTE_LABEL_PEQUENA, anchor="center"))

            # Descrição
            original_description = trans['description']
            display_description = re.sub(r'\s*\(\d+/\d+\)$', '', original_description) # Remove (X/Y)
            widgets.append(customtkinter.CTkLabel(parent_frame, text=display_description, font=FONTE_LABEL_PEQUENA, anchor="w"))

            # Categoria
            widgets.append(customtkinter.CTkLabel(parent_frame, text=trans['category_name'], font=FONTE_LABEL_PEQUENA, anchor="w"))

            # V. Parcela
            valor_parcela = trans['value']
            text_color_val = "tomato" if transaction_type == "Despesa" else "lightgreen"
            widgets.append(customtkinter.CTkLabel(parent_frame, text=f"R$ {valor_parcela:.2f}", font=FONTE_LABEL_PEQUENA, text_color=text_color_val, anchor="w"))

            # V. Total
            installments_str = trans.get('installments', "1/1")
            total_installments_num = 1
            if installments_str and "/" in installments_str:
                try:
                    total_installments_num = int(installments_str.split('/')[1])
                except (ValueError, IndexError):
                    total_installments_num = 1
            valor_total_transacao = valor_parcela * total_installments_num
            widgets.append(customtkinter.CTkLabel(parent_frame, text=f"R$ {valor_total_transacao:.2f}", font=FONTE_LABEL_PEQUENA, text_color=text_color_val, anchor="w"))

            # Status
            widgets.append(customtkinter.CTkLabel(parent_frame, text=trans.get('status', 'N/A'), font=FONTE_LABEL_PEQUENA, anchor="center"))
            # Modalidade
            widgets.append(customtkinter.CTkLabel(parent_frame, text=trans.get('modality', 'N/A'), font=FONTE_LABEL_PEQUENA, anchor="center"))
            # Parcela
            widgets.append(customtkinter.CTkLabel(parent_frame, text=trans.get('installments', '-'), font=FONTE_LABEL_PEQUENA, anchor="center"))

            transaction_id_for_click = trans['id']

            # Adicionar ComboBox para "Provento Associado" se for Despesa
            if transaction_type == "Despesa":
                provento_combobox_var = customtkinter.StringVar(value="Selecione")
                provento_options = ["Selecione"] + [p['description'] for p in proventos_do_mes]
                
                # Encontrar o provento associado, se houver
                associated_provento_id = trans.get('source_provento_id')
                if associated_provento_id:
                    associated_provento = next((p for p in proventos_do_mes if p['id'] == associated_provento_id), None)
                    if associated_provento:
                        provento_combobox_var.set(associated_provento['description'])

                provento_combobox = customtkinter.CTkComboBox(
                    parent_frame,
                    values=provento_options,
                    variable=provento_combobox_var,
                    font=FONTE_LABEL_PEQUENA,
                    width=120, # Ajustar largura conforme necessário
                    height=25,
                    command=lambda choice, d_id=trans['id'], d_val=trans['value']: self._handle_provento_association_change(d_id, choice, d_val, proventos_do_mes)
                )
                widgets.append(provento_combobox)
                # Armazena a referência APENAS para despesas
                print(f"DEBUG PlanejamentoView: Adicionando ComboBox para despesa ID {trans['id']} à lista de controle.")
                self.despesa_provento_comboboxes[trans['id']] = provento_combobox

            for col, widget in enumerate(widgets):
                widget.grid(row=row_idx, column=col, sticky="ew", padx=2)
                widget.bind("<Button-1>", lambda event, t_id=transaction_id_for_click: self._open_consulta_transacao(t_id))

    def _handle_provento_association_change(self, despesa_id, selected_provento_description, despesa_value, proventos_do_mes):
        """
        Chamado quando um provento é selecionado no ComboBox de uma despesa.
        Atualiza o source_provento_id da despesa no banco e recalcula os resultados.
        """
        print(f"DEBUG: Associação alterada para despesa ID {despesa_id}. Provento selecionado: '{selected_provento_description}'")
        
        selected_provento_id_to_save = None
        if selected_provento_description != "Selecione":
            provento_obj = next((p for p in proventos_do_mes if p['description'] == selected_provento_description), None)
            if provento_obj:
                selected_provento_id_to_save = provento_obj['id']
            else:
                print(f"ERRO: Provento '{selected_provento_description}' não encontrado na lista de proventos do mês.")
                # Poderia resetar o combobox ou mostrar um erro
                return

        # Atualizar no banco de dados
        # Precisamos dos outros campos da despesa para a função update_transaction
        despesa_data = next((t for t in self.all_transactions_for_month if t['id'] == despesa_id), None)
        if not despesa_data:
            print(f"ERRO: Despesa com ID {despesa_id} não encontrada para atualização.")
            return

        print(f"DEBUG: Chamando Database.update_transaction para despesa ID {despesa_id} com source_provento_id: {selected_provento_id_to_save}")
        success = Database.update_transaction(
            transaction_id=despesa_id,
            description=despesa_data['description'],
            value=despesa_data['value'], # O valor da despesa não muda aqui
            due_date=despesa_data['due_date'],
            payment_date=despesa_data.get('payment_date'),
            status=despesa_data['status'],
            category_id=despesa_data['category_id'],
            source_provento_id=selected_provento_id_to_save # Este é o campo que estamos atualizando
        )

        print(f"DEBUG: Resultado de Database.update_transaction: {success}")
        if success:
            print(f"DEBUG: Associação da despesa {despesa_id} com provento {selected_provento_id_to_save} salva no DB.")
            # Atualizar o dado localmente para refletir a mudança imediatamente
            despesa_data['source_provento_id'] = selected_provento_id_to_save
            print("DEBUG: Chamando self._update_allocation_results()")
            self._update_allocation_results()
            if self.main_dashboard_refresh_callback: # Notifica o dashboard principal
                self.main_dashboard_refresh_callback()
        else:
            print(f"ERRO: Falha ao salvar associação da despesa {despesa_id} no DB.")
            # Reverter a seleção no ComboBox para o valor anterior? (mais complexo)

    def _update_allocation_results(self):
        """
        Calcula e exibe os saldos dos proventos e as despesas pendentes.
        """
        print("-" * 30)
        print("DEBUG PlanejamentoView: Limpando área de resultados da alocação.")
        print("DEBUG PlanejamentoView: Entrando em _update_allocation_results()")
        for widget in self.allocation_result_display_frame.winfo_children():
            widget.destroy()

        if not self.all_transactions_for_month:
            customtkinter.CTkLabel(self.allocation_result_display_frame, text="Selecione um mês para ver os resultados.", font=FONTE_LABEL_NORMAL, text_color="gray60").pack(pady=20, padx=20)
            return

        # --- Frame interno para dividir a área de resultados em duas colunas ---
        results_inner_frame = customtkinter.CTkFrame(self.allocation_result_display_frame, fg_color="transparent")
        results_inner_frame.pack(fill="both", expand=True, padx=10, pady=10)
        results_inner_frame.grid_columnconfigure(0, weight=1) # Coluna esquerda (Saldos e Pendentes)
        results_inner_frame.grid_columnconfigure(1, weight=1) # Coluna direita (Detalhes por Provento)
        results_inner_frame.grid_rowconfigure(0, weight=1) # Linha única para expandir verticalmente


        print(f"DEBUG PlanejamentoView: Total de transações carregadas: {len(self.all_transactions_for_month)}")
        proventos_do_mes = [
            t for t in self.all_transactions_for_month
            if t['category_type'] == 'Provento'
        ]
        print(f"DEBUG PlanejamentoView: Total de proventos no mês: {len(proventos_do_mes)}")
        despesas_do_mes = [
            t for t in self.all_transactions_for_month
            if t['category_type'] == 'Despesa'
        ]
        print(f"DEBUG PlanejamentoView: Total de despesas no mês: {len(despesas_do_mes)}")

        # --- Frame para o painel esquerdo (Saldos e Despesas Pendentes) ---
        left_panel_frame = customtkinter.CTkFrame(results_inner_frame, fg_color="gray17", corner_radius=8)
        left_panel_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        left_panel_frame.grid_columnconfigure(0, weight=1) # Coluna única para conteúdo interno

        # --- Frame para o painel direito (Alocação Detalhada por Provento) ---
        right_panel_frame = customtkinter.CTkFrame(results_inner_frame, fg_color="gray17", corner_radius=8)
        right_panel_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        right_panel_frame.grid_columnconfigure(0, weight=1) # Coluna única para conteúdo interno
        # Usaremos pack inside this frame

        # Create a scrollable frame inside the right panel for the provento details
        provento_details_scroll_frame = customtkinter.CTkScrollableFrame(right_panel_frame, fg_color="transparent")
        provento_details_scroll_frame.pack(fill="both", expand=True, padx=5, pady=5) # Use padx/pady here for spacing inside the panel
        provento_details_scroll_frame.grid_columnconfigure(0, weight=1) # Single column for content inside the scrollable frame

        # --- Exibir Saldos dos Proventos ---
        print(f"DEBUG PlanejamentoView: Conteúdo de self.despesa_provento_comboboxes: {self.despesa_provento_comboboxes}")
        print("DEBUG PlanejamentoView: Exibindo Saldos dos Proventos...")
        saldos_title = customtkinter.CTkLabel(left_panel_frame, text="Saldos dos Proventos:", font=FONTE_LABEL_BOLD)
        saldos_title.pack(anchor="w", padx=10, pady=(10,5))

        
        # Pre-calculate allocated despesas for each provento based on source_provento_id
        # This dictionary will map provento_id to a list of allocated despesa objects
        allocated_despesas_by_provento_id = {}
        for despesa in despesas_do_mes:
            source_provento_id = despesa.get('source_provento_id')
            if source_provento_id:
                if source_provento_id not in allocated_despesas_by_provento_id:
                    allocated_despesas_by_provento_id[source_provento_id] = []
                allocated_despesas_by_provento_id[source_provento_id].append(despesa)
                print(f"DEBUG PlanejamentoView: Despesa '{despesa['description']}' (ID: {despesa['id']}) alocada a provento ID: {source_provento_id}.")

        has_allocations_to_display = False

        if not proventos_do_mes: # Este label estava no frame pai, movido para o painel esquerdo
             customtkinter.CTkLabel(left_panel_frame, text="Nenhum provento cadastrado para este mês.", font=FONTE_LABEL_NORMAL, text_color="gray60").pack(anchor="w", padx=10, pady=2)
        else:
            for provento in sorted(proventos_do_mes, key=lambda x: x['description']):
                valor_original_provento = provento['value']
                
                provento_id = provento['id']

                allocated_despesas_for_provento = allocated_despesas_by_provento_id.get(provento_id, [])
                valor_alocado_provento = sum(d['value'] for d in allocated_despesas_for_provento)

                saldo_restante_provento = valor_original_provento - valor_alocado_provento
                cor_saldo = "lightgreen" if saldo_restante_provento >=0 else "tomato"

                provento_info_frame = customtkinter.CTkFrame(left_panel_frame, fg_color="transparent")
                provento_info_frame.pack(fill="x", padx=10, pady=1)
                
                customtkinter.CTkLabel(provento_info_frame, text=f"{provento['description']}:", font=FONTE_LABEL_NORMAL, anchor="w").pack(side="left", padx=(0,5))
                customtkinter.CTkLabel(provento_info_frame, text=f"Orig: R$ {valor_original_provento:.2f}", font=FONTE_LABEL_PEQUENA, anchor="w").pack(side="left", padx=5)
                customtkinter.CTkLabel(provento_info_frame, text=f"Usado: R$ {valor_alocado_provento:.2f}", font=FONTE_LABEL_PEQUENA, text_color="orange", anchor="w").pack(side="left", padx=5)
                customtkinter.CTkLabel(provento_info_frame, text=f"Saldo: R$ {saldo_restante_provento:.2f}", font=FONTE_LABEL_PEQUENA, text_color=cor_saldo, anchor="w").pack(side="left", padx=5)

        
                # --- Display Detailed Allocation for this Provento (in the right panel's scrollable frame) ---
                if allocated_despesas_for_provento: # Only create a section if there are allocated expenses
                    has_allocations_to_display = True
                    provento_detail_frame = customtkinter.CTkFrame(provento_details_scroll_frame, fg_color="gray20", corner_radius=8, border_width=1, border_color="gray45")
                    provento_detail_frame.pack(fill="x", padx=5, pady=(5, 5), anchor="n") # Pack vertically in the scrollable frame
                    provento_detail_frame.grid_columnconfigure(0, weight=1) # Single column for content inside this detail frame

                    # Provento Title and Value
                    provento_detail_title = customtkinter.CTkLabel(provento_detail_frame, text=f"{provento['description']} (R$ {valor_original_provento:.2f})", font=FONTE_LABEL_BOLD, text_color="lightgreen")
                    provento_detail_title.pack(anchor="w", padx=10, pady=(5, 5))

                   # List allocated expenses
                    for desp in sorted(allocated_despesas_for_provento, key=lambda x: x['due_date']):
                         due_date_fmt = datetime.datetime.strptime(desp['due_date'], "%Y-%m-%d").strftime("%d/%m/%Y")
                         customtkinter.CTkLabel(provento_detail_frame, text=f"- {desp['description']} (Venc: {due_date_fmt}, Valor: R$ {desp['value']:.2f})", font=FONTE_LABEL_PEQUENA, text_color="tomato", anchor="w").pack(fill="x", padx=15, pady=1)

                    # Separator
                    separator = customtkinter.CTkFrame(provento_detail_frame, height=1, fg_color="gray50")
                    separator.pack(fill="x", padx=10, pady=(5, 5))

                    # Summary for this provento
                    customtkinter.CTkLabel(provento_detail_frame, text=f"Total Alocado: R$ {valor_alocado_provento:.2f}", font=FONTE_LABEL_NORMAL, text_color="orange", anchor="w").pack(anchor="w", padx=10, pady=(0, 2))
                    customtkinter.CTkLabel(provento_detail_frame, text=f"Saldo Restante: R$ {saldo_restante_provento:.2f}", font=FONTE_LABEL_NORMAL, text_color=cor_saldo, anchor="w").pack(anchor="w", padx=10, pady=(0, 5))


        # --- Exibir Despesas Pendentes ---
        print(f"DEBUG PlanejamentoView: Verificando despesas pendentes de {len(despesas_do_mes)} despesas totais...")
        print("DEBUG PlanejamentoView: Exibindo Despesas Pendentes de Alocação...")
        pendentes_title = customtkinter.CTkLabel(left_panel_frame, text="Despesas Pendentes de Alocação:", font=FONTE_LABEL_BOLD)
        pendentes_title.pack(anchor="w", padx=10, pady=(15,5))

        despesas_pendentes = []
        for despesa in despesas_do_mes:
            # A despesa é pendente se source_provento_id is None
            if despesa.get('source_provento_id') is None:
                 print(f"DEBUG PlanejamentoView: Despesa '{despesa['description']}' (ID: {despesa['id']}) está pendente (source_provento_id is None).")
                 despesas_pendentes.append(despesa)

        if not despesas_pendentes:
            customtkinter.CTkLabel(left_panel_frame, text="Todas as despesas foram alocadas a um provento.", font=FONTE_LABEL_NORMAL, text_color="gray60").pack(anchor="w", padx=10, pady=2)
        else:
            for desp_pendente in sorted(despesas_pendentes, key=lambda x: x['due_date']):
                due_date_fmt = datetime.datetime.strptime(desp_pendente['due_date'], "%Y-%m-%d").strftime("%d/%m/%Y") # Formato completo
                customtkinter.CTkLabel(left_panel_frame, text=f"- {desp_pendente['description']} (Venc: {due_date_fmt}, Valor: R$ {desp_pendente['value']:.2f})", font=FONTE_LABEL_NORMAL, text_color="tomato", anchor="w").pack(fill="x", padx=10, pady=1)

        # --- (Placeholder para Sugestão de Alocação Futura) ---
        print("DEBUG PlanejamentoView: Verificando se placeholder de sugestão deve ser exibido...")
        # print("DEBUG PlanejamentoView: Exibindo Placeholder para Sugestão...") # Removed placeholder
        if not has_allocations_to_display:
             # Remove the title if no allocations are displayed below it
             right_panel_title.pack_forget()
             customtkinter.CTkLabel(provento_details_scroll_frame, text="Nenhuma despesa alocada a um provento neste mês.", font=FONTE_LABEL_NORMAL, text_color="gray60").pack(pady=20, padx=20)
             
    def _open_simulador_window(self):
        """Abre a janela do formulário de simulação."""
        # Verifica se a janela já existe e está ativa
        if self.form_simulador_window is None or not self.form_simulador_window.winfo_exists():
            print("DEBUG PlanejamentoView: Abrindo janela do Simulador...")
            if not self.current_month_name_selected or not self.all_transactions_for_month:
                # (Opcional) Mostrar um CTkMessagebox informando para selecionar um mês primeiro
                print("DEBUG PlanejamentoView: Por favor, selecione um mês com transações antes de simular.")
                # from CTkMessagebox import CTkMessagebox # Importar se for usar
                # CTkMessagebox(title="Atenção", message="Selecione um mês com transações para simular.", icon="warning", master=self)
                return

            despesas_atuais = [t for t in self.all_transactions_for_month if t['category_type'] == 'Despesa']
            proventos_atuais = [t for t in self.all_transactions_for_month if t['category_type'] == 'Provento']

            self.form_simulador_window = FormSimuladorWindow(
                master=self,
                user_id=self.current_user_id,
                selected_year=self.selected_year,
                selected_month_name=self.current_month_name_selected,
                despesas_do_mes=despesas_atuais,
                proventos_do_mes=proventos_atuais
            )
            self.form_simulador_window.focus() # Traz a nova janela para o foco
        else:
            self.form_simulador_window.focus() # Se a janela já existe, apenas a traz para o foco
             
    def _open_consulta_transacao(self, transaction_id):
        """Abre a janela de consulta para uma transação específica."""
        if self.form_consulta_transacao_window is None or not self.form_consulta_transacao_window.winfo_exists():
            self.form_consulta_transacao_window = FormConsultaTransacaoWindow(
                master=self, # O master é esta janela de Planejamento
                transaction_id=transaction_id,
                on_action_completed_callback=self._refresh_after_action
            )
            self.form_consulta_transacao_window.focus()
        else:
            self.form_consulta_transacao_window.focus()

    def _handle_close(self):
        """Chama o callback de fechamento fornecido pelo Dashboard."""
        if self.close_callback:
            self.close_callback()
        self.destroy() # Destrói este frame de planejamento

    def _refresh_after_action(self):
        """Recarrega os dados do mês atual após uma ação (ex: edição em FormConsultaTransacaoWindow)."""
        print("DEBUG PlanejamentoView: _refresh_after_action called.")
        if self.current_month_name_selected:
            # Recarrega todas as transações e repopula a UI
            print(f"DEBUG PlanejamentoView: Refreshing for month: {self.current_month_name_selected}, year: {self.selected_year}")
            self.month_selected_for_planning(self.current_month_name_selected, self.selected_year, self.current_user_id)
        if self.main_dashboard_refresh_callback:
            print("DEBUG PlanejamentoView: Calling main_dashboard_refresh_callback()")
            self.main_dashboard_refresh_callback()

if __name__ == '__main__':
    # Para testar esta janela isoladamente
    app_root = customtkinter.CTk()
    # app_root.withdraw() # Não precisa esconder para testar um Frame
    # Use um user_id e ano de teste
    planejamento_view = PlanejamentoView(master=app_root, current_user_id="test_user_01", selected_year="2024")
    planejamento_view.pack(expand=True, fill="both")
    app_root.mainloop()