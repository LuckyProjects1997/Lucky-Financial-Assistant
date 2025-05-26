# form_detalhes_mensais.py
import customtkinter
import tkinter as tk # Para constantes de alinhamento
from CTkMessagebox import CTkMessagebox # Para caixas de diálogo de confirmação
import re # Para remover a informação de parcela da descrição
from Database import get_transactions_for_month, get_category_summary_for_month, delete_transaction # Importa funções do Database
from form_consulta_transacao import FormConsultaTransacaoWindow # Importa a nova janela

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

class FormDetalhesMensaisWindow(customtkinter.CTkToplevel):
    def __init__(self, master=None, current_user_id=None, selected_year=None):
        super().__init__(master)
        self.title(f"Detalhes Mensais - {selected_year}")
        self.geometry("800x600") # Aumentado para acomodar os detalhes
        self.configure(fg_color="#1c1c1c")
        self.lift()
        self.attributes("-topmost", True)
        self.grab_set()

        self.current_user_id = current_user_id
        self.selected_year = selected_year
        self.months_list = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        self.all_transactions_for_month = []
        self.selected_transaction_ids = set() # Para armazenar IDs das transações selecionadas pelos checkboxes
        self.current_filter_type = None # "Despesa", "Provento", ou None
        self.form_consulta_transacao_window = None # Referência para a janela de consulta
        self.current_month_name_selected = None # Para recarregar a view

        # --- Frame Principal ---
        main_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        # Configurar grid para o main_frame
        main_frame.grid_columnconfigure(0, weight=1) # Coluna única para expandir
        main_frame.grid_rowconfigure(0, weight=0) # Título
        main_frame.grid_rowconfigure(1, weight=0) # Botões dos meses
        main_frame.grid_rowconfigure(2, weight=1) # content_splitter_frame (expande verticalmente)
        main_frame.grid_rowconfigure(3, weight=0) # Botão Fechar

        title_label = customtkinter.CTkLabel(main_frame, text=f"Selecione o Mês ({selected_year})", font=FONTE_TITULO_FORM)
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
                command=lambda m=month_name, y=self.selected_year, u=self.current_user_id: self.month_detail_selected(m, y, u)
            ) # Passa o nome do mês, não o índice
            month_button.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        # --- Frame para dividir o conteúdo em duas colunas ---
        content_splitter_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        content_splitter_frame.grid(row=2, column=0, sticky="nsew", pady=(10,0))
        # Alterado para 1 coluna e 2 linhas para empilhar os frames
        content_splitter_frame.grid_columnconfigure(0, weight=1) # Única coluna
        content_splitter_frame.grid_rowconfigure(0, weight=2) # Linha para a lista de transações (mais peso)
        content_splitter_frame.grid_rowconfigure(1, weight=1) # Linha para o resumo

        # --- Coluna da Esquerda: Detalhamento das Transações ---
        # Agora ocupará a primeira linha do content_splitter_frame
        left_column_container_frame = customtkinter.CTkFrame(content_splitter_frame, fg_color="transparent")
        left_column_container_frame.grid(row=0, column=0, sticky="nsew", padx=0) # Removido padx
        left_column_container_frame.grid_rowconfigure(0, weight=0) # Título e botão Mostrar Todas
        left_column_container_frame.grid_rowconfigure(1, weight=1) # Lista de transações (scrollable)
        left_column_container_frame.grid_rowconfigure(2, weight=0) # Botão Fechar
        left_column_container_frame.grid_columnconfigure(0, weight=1) # Allow the single column to expand

        # Título da lista de transações e botão "Mostrar Todas"
        self.left_title_frame = customtkinter.CTkFrame(left_column_container_frame, fg_color="transparent") # Frame para o título e botões de filtro
        self.left_title_frame.grid(row=0, column=0, sticky="ew", pady=(0,5))
        # Configure columns for the title and filter buttons
        # Column 0 for the title label, allow it to take available space
        self.left_title_frame.grid_columnconfigure(0, weight=1) 
        # Columns for buttons, no weight, they will take their content size
        self.left_title_frame.grid_columnconfigure(1, weight=0)
        self.left_title_frame.grid_columnconfigure(2, weight=0)
        self.left_title_frame.grid_columnconfigure(3, weight=0)

        # Placeholder for the actual title label, will be configured in month_detail_selected
        self.transaction_list_title_label = customtkinter.CTkLabel(self.left_title_frame, text="Transações do Mês", font=FONTE_LABEL_BOLD)
        self.transaction_list_title_label.grid(row=0, column=0, sticky="w")

        # Botão Despesas
        self.despesas_button = customtkinter.CTkButton(self.left_title_frame, text="Despesas", font=(FONTE_FAMILIA, 10),
                                                       command=self._filter_by_despesa, height=25, width=80,
                                                       corner_radius=BOTAO_CORNER_RADIUS, fg_color="tomato", text_color="white", hover_color="#CD5C5C") # Vermelho escuro para hover
        self.despesas_button.grid(row=0, column=1, sticky="e", padx=(0, 5))

        # Botão Proventos
        self.proventos_button = customtkinter.CTkButton(self.left_title_frame, text="Proventos", font=(FONTE_FAMILIA, 10),
                                                        command=self._filter_by_provento, height=25, width=80,
                                                        corner_radius=BOTAO_CORNER_RADIUS, fg_color="green", text_color="white", hover_color="#2E8B57") # Verde escuro para hover
        self.proventos_button.grid(row=0, column=2, sticky="e", padx=(0, 5))

        # Botão Mostrar Todas
        self.show_all_button = customtkinter.CTkButton(self.left_title_frame, text="Mostrar Todas", font=(FONTE_FAMILIA, 10),
                                                       command=self._show_all_transactions, height=25, width=100,
                                                       corner_radius=BOTAO_CORNER_RADIUS, fg_color="gray40", hover_color="gray50")
        self.show_all_button.grid(row=0, column=3, sticky="e", padx=(0,0))

        self.left_detail_scroll_frame = customtkinter.CTkScrollableFrame(left_column_container_frame, height=150) # Adicionado height=150
        self.left_detail_scroll_frame.grid(row=1, column=0, sticky="nsew")
        # Placeholder inicial (mantido)
        self.left_placeholder_label = customtkinter.CTkLabel(self.left_detail_scroll_frame, text="Selecione um mês para ver as transações.", font=FONTE_LABEL_NORMAL, text_color="gray60")
        self.left_placeholder_label.pack(pady=20, padx=10)
        summary_section_container = customtkinter.CTkFrame(content_splitter_frame, fg_color="transparent") # Container para título e caixa de resumo
        summary_section_container.grid(row=1, column=0, sticky="nsew", pady=(10, 0)) # Ocupa a segunda linha, expande horizontalmente

        # Título para o Resumo (acima da caixa cinza)
        self.summary_title_label = customtkinter.CTkLabel(summary_section_container, text="Resumo do Mês", font=FONTE_LABEL_BOLD)
        self.summary_title_label.pack(anchor="w", pady=(0, 5)) # Empacotado no container, alinhado à esquerda

        # Frame de conteúdo do Resumo (caixa cinza) - com largura fixa de 370px
        self.right_summary_frame = customtkinter.CTkFrame(summary_section_container, fg_color="gray17", corner_radius=10, width=370)
        self.right_summary_frame.pack_propagate(False) # Impede que os widgets filhos alterem o tamanho do frame
        # Alinhado à esquerda (anchor="w"), preenche verticalmente (fill="y"), não expande horizontalmente (expand=False)
        self.right_summary_frame.pack(anchor="w", fill="y", expand=False) 
        # Placeholder inicial
        self.right_placeholder_label = customtkinter.CTkLabel(self.right_summary_frame, text="Selecione um mês.", font=FONTE_LABEL_NORMAL, text_color="gray60")
        self.right_placeholder_label.pack(pady=20, padx=10, expand=True, fill="both")

        # Botão Fechar - agora filho direto do main_frame, posicionado no final
        close_button = customtkinter.CTkButton(main_frame, text="Fechar", command=self.destroy,
                                               height=30, font=(FONTE_FAMILIA, 12, "bold"),
                                               corner_radius=BOTAO_CORNER_RADIUS, fg_color="gray50", hover_color="gray40")
        close_button.grid(row=3, column=0, pady=(20,0), sticky="s") # Posicionado na última linha do grid do main_frame

    def month_detail_selected(self, month_name, year, user_id):
        month_number = self.months_list.index(month_name) + 1
        print(f"DEBUG: month_detail_selected - Mês: {month_name}, Ano: {year}, User ID: {user_id}")
        self.current_month_name_selected = month_name # Salva para recarregar

        # Limpar placeholders e conteúdo anterior
        if hasattr(self, 'left_placeholder_label') and self.left_placeholder_label.winfo_exists():
            self.left_placeholder_label.pack_forget()
        if hasattr(self, 'right_placeholder_label') and self.right_placeholder_label.winfo_exists():
            self.right_placeholder_label.pack_forget()

        for widget in self.right_summary_frame.winfo_children():
            widget.destroy()

        self.all_transactions_for_month = get_transactions_for_month(user_id, year, month_number)
        # self.selected_transaction_ids.clear() # Não é mais necessário
        self.current_filter_type = None 
        self._display_transactions(self.all_transactions_for_month)
        self._update_action_buttons_state()

        self.transaction_list_title_label.configure(text=f"Transações de {month_name}")
        self.summary_title_label.configure(text=f"Resumo de {month_name}") # Atualiza o novo título do resumo

        # --- Popular Coluna da Direita (Resumo) ---
        summary_data = get_category_summary_for_month(user_id, year, month_number)
        total_despesas = 0
        total_proventos = 0

        # O título do resumo agora está fora do self.right_summary_frame

        if not summary_data:
            customtkinter.CTkLabel(self.left_detail_scroll_frame, text="Nenhuma transação encontrada para este mês.", font=FONTE_LABEL_NORMAL, text_color="gray60").pack(pady=20)
            customtkinter.CTkLabel(self.right_summary_frame, text="Nenhum dado de resumo encontrado.", font=FONTE_LABEL_NORMAL, text_color="gray60").pack(pady=10)
        else:
            cat_summary_frame = customtkinter.CTkFrame(self.right_summary_frame, fg_color="transparent")
            cat_summary_frame.pack(fill="x", padx=10)
            cat_summary_frame.grid_columnconfigure(0, weight=1)
            cat_summary_frame.grid_columnconfigure(1, weight=1)

            customtkinter.CTkLabel(cat_summary_frame, text="Categoria", font=FONTE_LABEL_BOLD).grid(row=0, column=0, sticky="w")
            customtkinter.CTkLabel(cat_summary_frame, text="Total Mês", font=FONTE_LABEL_BOLD).grid(row=0, column=1, sticky="e")

            for i, item in enumerate(sorted(summary_data, key=lambda x: x['category_name'])):
                item_color = "green" if item['category_type'] == 'Provento' else "white" # Cor do texto baseada no tipo
                customtkinter.CTkLabel(cat_summary_frame, text=item['category_name'], font=FONTE_LABEL_NORMAL, text_color=item_color).grid(row=i+1, column=0, sticky="w")
                customtkinter.CTkLabel(cat_summary_frame, text=f"R$ {item['total_value']:.2f}", font=FONTE_LABEL_NORMAL, text_color=item_color).grid(row=i+1, column=1, sticky="e")

                if item['category_type'] == 'Despesa':
                    total_despesas += item['total_value']
                elif item['category_type'] == 'Provento':
                    total_proventos += item['total_value']

        # Totais e Saldo
        totals_frame = customtkinter.CTkFrame(self.right_summary_frame, fg_color="transparent")
        totals_frame.pack(fill="x", padx=10, pady=(20,5))

        total_despesas_label = customtkinter.CTkLabel(totals_frame, text=f"Total Despesas: R$ {total_despesas:.2f}", font=FONTE_LABEL_BOLD, text_color="tomato", cursor="hand2")
        total_despesas_label.pack(anchor="w")
        total_despesas_label.bind("<Button-1>", self._filter_by_despesa)

        total_proventos_label = customtkinter.CTkLabel(totals_frame, text=f"Total Proventos: R$ {total_proventos:.2f}", font=FONTE_LABEL_BOLD, text_color="lightgreen", cursor="hand2")
        total_proventos_label.pack(anchor="w")
        total_proventos_label.bind("<Button-1>", self._filter_by_provento)

        saldo = total_proventos - total_despesas
        saldo_color = "lightgreen" if saldo >=0 else "tomato"
        customtkinter.CTkLabel(totals_frame, text=f"Saldo do Mês: R$ {saldo:.2f}", font=FONTE_LABEL_BOLD, text_color=saldo_color).pack(anchor="w", pady=(5,0))

    def _display_transactions(self, transactions_to_display):
        # Limpa o conteúdo anterior do scroll frame
        for widget in self.left_detail_scroll_frame.winfo_children():
            widget.destroy()

        if not transactions_to_display:
            customtkinter.CTkLabel(self.left_detail_scroll_frame, text="Nenhuma transação para exibir com o filtro atual.", font=FONTE_LABEL_NORMAL, text_color="gray60").pack(pady=20)
            return

        # Cabeçalhos
        header_frame = customtkinter.CTkFrame(self.left_detail_scroll_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(5,2))
        # Configuração de 7 colunas para os cabeçalhos
        header_frame.grid_columnconfigure(0, weight=4)  # Descrição (mais peso)
        header_frame.grid_columnconfigure(1, weight=3)  # Categoria
        header_frame.grid_columnconfigure(2, weight=2)  # Modalidade
        header_frame.grid_columnconfigure(3, weight=2)  # Valor Parcela
        header_frame.grid_columnconfigure(4, weight=2)  # Valor Total
        header_frame.grid_columnconfigure(5, weight=1)  # Parcela
        header_frame.grid_columnconfigure(6, weight=1)  # Status

        customtkinter.CTkLabel(header_frame, text="Descrição", font=FONTE_LABEL_BOLD, anchor="w").grid(row=0, column=0, sticky="ew", padx=(5, 10)) # Aumentado padx direito
        customtkinter.CTkLabel(header_frame, text="Categoria", font=FONTE_LABEL_BOLD, anchor="w").grid(row=0, column=1, sticky="ew", padx=2)
        customtkinter.CTkLabel(header_frame, text="Modalidade", font=FONTE_LABEL_BOLD, anchor="w").grid(row=0, column=2, sticky="ew", padx=2)
        customtkinter.CTkLabel(header_frame, text="V. Parcela", font=FONTE_LABEL_BOLD, anchor="e").grid(row=0, column=3, sticky="ew", padx=2)
        customtkinter.CTkLabel(header_frame, text="V. Total", font=FONTE_LABEL_BOLD, anchor="e").grid(row=0, column=4, sticky="ew", padx=(2, 10)) # Aumentado padx direito
        customtkinter.CTkLabel(header_frame, text="Parcela", font=FONTE_LABEL_BOLD, anchor="w").grid(row=0, column=5, sticky="ew", padx=2)
        customtkinter.CTkLabel(header_frame, text="Status", font=FONTE_LABEL_BOLD, anchor="w").grid(row=0, column=6, sticky="ew", padx=2)

        for trans in transactions_to_display:
            row_frame_fg_color = "transparent"
            text_color_val = "white"

            if trans['category_type'] == 'Provento':
                text_color_val = "green"
            elif trans['category_type'] == 'Despesa':
                text_color_val = "tomato" # Laranja avermelhado

            row_frame = customtkinter.CTkFrame(self.left_detail_scroll_frame, fg_color=row_frame_fg_color, corner_radius=3)
            row_frame.pack(fill="x", pady=1, padx=2)
            # Configuração de 7 colunas para os dados da transação
            row_frame.grid_columnconfigure(0, weight=4)  # Descrição
            row_frame.grid_columnconfigure(1, weight=3)  # Categoria
            row_frame.grid_columnconfigure(2, weight=2)  # Modalidade
            row_frame.grid_columnconfigure(3, weight=2)  # Valor Parcela
            row_frame.grid_columnconfigure(4, weight=2)  # Valor Total
            row_frame.grid_columnconfigure(5, weight=1)  # Parcela
            row_frame.grid_columnconfigure(6, weight=1)  # Status

            original_description = trans['description']
            display_description = re.sub(r'\s*\(\d+/\d+\)$', '', original_description)
            description_label = customtkinter.CTkLabel(row_frame, text=display_description, font=FONTE_LABEL_PEQUENA, anchor="w", cursor="hand2")
            description_label.grid(row=0, column=0, sticky="ew", padx=(5, 10)) # Aumentado padx direito

            cat_label = customtkinter.CTkLabel(row_frame, text=trans['category_name'], font=FONTE_LABEL_PEQUENA, corner_radius=3, padx=3, anchor="w", cursor="hand2")
            cat_label.grid(row=0, column=1, sticky="ew", padx=2)
            customtkinter.CTkLabel(row_frame, text=trans.get('modality', 'N/A'), font=FONTE_LABEL_PEQUENA, anchor="w", cursor="hand2").grid(row=0, column=2, sticky="ew", padx=2)
            customtkinter.CTkLabel(row_frame, text=f"R$ {trans['value']:.2f}", font=FONTE_LABEL_PEQUENA, text_color=text_color_val, anchor="e", cursor="hand2").grid(row=0, column=3, sticky="ew", padx=2)
            
            valor_parcela = trans['value']
            installments_str = trans.get('installments', "1/1")
            total_installments_num = 1
            if installments_str and "/" in installments_str:
                try:
                    total_installments_num = int(installments_str.split('/')[1])
                except (ValueError, IndexError):
                    total_installments_num = 1 # Fallback
            
            valor_total_transacao = valor_parcela * total_installments_num
            customtkinter.CTkLabel(row_frame, text=f"R$ {valor_total_transacao:.2f}", font=FONTE_LABEL_PEQUENA, text_color=text_color_val, anchor="e", cursor="hand2").grid(row=0, column=4, sticky="ew", padx=(2, 10)) # Aumentado padx direito
            customtkinter.CTkLabel(row_frame, text=trans.get('installments', '-'), font=FONTE_LABEL_PEQUENA, anchor="w", cursor="hand2").grid(row=0, column=5, sticky="ew", padx=2)
            customtkinter.CTkLabel(row_frame, text=trans.get('status', 'N/A'), font=FONTE_LABEL_PEQUENA, anchor="w", cursor="hand2").grid(row=0, column=6, sticky="ew", padx=2)
            
            row_frame.bind("<Button-1>", lambda event, t_id=trans['id']: self._open_consulta_transacao(t_id))
            for child in row_frame.winfo_children():
                child.bind("<Button-1>", lambda event, t_id=trans['id']: self._open_consulta_transacao(t_id))

    def _toggle_selection(self, transaction_id, checkbox_var):
        """
        Chamado quando um checkbox de transação é clicado/desclicado.
        """
        if checkbox_var.get() == "on":
            self.selected_transaction_ids.add(transaction_id)
            print(f"INFO: Transação ID {transaction_id} selecionada.")
        else:
            self.selected_transaction_ids.discard(transaction_id)
            print(f"INFO: Transação ID {transaction_id} desmarcada.")
        self._update_action_buttons_state()

    def _filter_by_despesa(self, event=None):
        self.current_filter_type = "Despesa"
        filtered_transactions = [t for t in self.all_transactions_for_month if t['category_type'] == "Despesa"]
        self._display_transactions(filtered_transactions)
        # self.selected_transaction_ids.clear() # Não é mais necessário

    def _filter_by_provento(self, event=None):
        self.current_filter_type = "Provento"
        filtered_transactions = [t for t in self.all_transactions_for_month if t['category_type'] == "Provento"]
        self._display_transactions(filtered_transactions)
        # self.selected_transaction_ids.clear() # Não é mais necessário
        # self._update_action_buttons_state() # Não é mais necessário
    def _show_all_transactions(self, event=None):
        self.current_filter_type = None
        self._display_transactions(self.all_transactions_for_month)
        # self.selected_transaction_ids.clear() # Não é mais necessário
        # self._update_action_buttons_state() # Não é mais necessário
    def _update_action_buttons_state(self):
        # Este método não é mais necessário pois o botão de excluir foi removido
        pass

    def _handle_delete_transaction(self):
        # Este método não é mais chamado pelo botão, mas mantido caso seja útil em outro lugar.
        if not self.selected_transaction_ids:
            CTkMessagebox(title="Nenhuma Seleção", message="Nenhuma transação selecionada para excluir.", icon="warning", master=self)
            return

        num_selected = len(self.selected_transaction_ids)
        item_text = "transação selecionada" if num_selected == 1 else f"{num_selected} transações selecionadas"

        msg = CTkMessagebox(title="Confirmar Exclusão",
                            message=f"Tem certeza que deseja excluir {item_text}?",
                            icon="warning", option_1="Cancelar", option_2="Excluir", master=self)
        
        response = msg.get()
        if response == "Excluir":
            deleted_count = 0
            failed_ids = []
            for trans_id in list(self.selected_transaction_ids): # Itera sobre uma cópia para poder modificar o set original
                if delete_transaction(trans_id):
                    deleted_count += 1
                else:
                    failed_ids.append(trans_id)
            
            if deleted_count > 0:
                success_message = f"{deleted_count} transação(ões) excluída(s) com sucesso."
                if failed_ids:
                    success_message += f"\nFalha ao excluir IDs: {', '.join(failed_ids)}"
                CTkMessagebox(title="Exclusão Concluída", message=success_message, icon="check", master=self)
            elif failed_ids:
                 CTkMessagebox(title="Falha na Exclusão", message=f"Nenhuma transação pôde ser excluída. Falha para IDs: {', '.join(failed_ids)}", icon="cancel", master=self)
            
            self._refresh_after_action() # Recarrega a lista após exclusão

    def _refresh_after_action(self):
        """Recarrega os dados do mês atual após uma ação como editar ou excluir."""
        print("DEBUG DetalhesMensais: _refresh_after_action called.")
        if self.current_month_name_selected:
            print(f"DEBUG DetalhesMensais: Refreshing for month: {self.current_month_name_selected}, year: {self.selected_year}")
            self.month_detail_selected(self.current_month_name_selected, self.selected_year, self.current_user_id)
        # Notifica o Dashboard (master) para atualizar seus dados também
        if self.master and hasattr(self.master, '_refresh_dashboard_data'):
            print("DEBUG DetalhesMensais: Calling master._refresh_dashboard_data()")
            self.master._refresh_dashboard_data()

    def _open_consulta_transacao(self, transaction_id):
        print(f"Abrindo consulta para transação ID: {transaction_id}")
        if self.form_consulta_transacao_window is None or not self.form_consulta_transacao_window.winfo_exists():
            self.form_consulta_transacao_window = FormConsultaTransacaoWindow(
                master=self, transaction_id=transaction_id, on_action_completed_callback=self._refresh_after_action
            )
            self.form_consulta_transacao_window.focus()
        else:
            self.form_consulta_transacao_window.focus()



if __name__ == '__main__':
    # Para testar esta janela isoladamente
    app_root = customtkinter.CTk()
    app_root.withdraw() # Esconde a janela root principal
    form_detalhes = FormDetalhesMensaisWindow(master=app_root, current_user_id="test_user_01", selected_year="2024")
    app_root.mainloop()