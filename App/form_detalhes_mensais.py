# form_detalhes_mensais.py
import customtkinter
import tkinter as tk # Para constantes de alinhamento
from CTkMessagebox import CTkMessagebox # Para caixas de diálogo de confirmação
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

        title_label = customtkinter.CTkLabel(main_frame, text=f"Selecione o Mês ({selected_year})", font=FONTE_TITULO_FORM)
        title_label.pack(pady=(0, 20))

        # Frame para os botões dos meses
        month_buttons_container = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        month_buttons_container.pack(pady=(0,10), fill="x")

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
        content_splitter_frame.pack(expand=True, fill="both", pady=(10,0))
        content_splitter_frame.grid_columnconfigure(0, weight=2) # Coluna da esquerda (detalhes)
        content_splitter_frame.grid_columnconfigure(1, weight=1) # Coluna da direita (resumo)
        content_splitter_frame.grid_rowconfigure(0, weight=1)

        # --- Coluna da Esquerda: Detalhamento das Transações ---
        left_column_container_frame = customtkinter.CTkFrame(content_splitter_frame, fg_color="transparent")
        left_column_container_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_column_container_frame.grid_rowconfigure(0, weight=0) # Título e botão Mostrar Todas
        left_column_container_frame.grid_rowconfigure(1, weight=1) # Lista de transações (scrollable)
        left_column_container_frame.grid_rowconfigure(2, weight=0) # Botões Editar/Excluir
        left_column_container_frame.grid_columnconfigure(0, weight=1)

        # Título da lista de transações e botão "Mostrar Todas"
        left_title_frame = customtkinter.CTkFrame(left_column_container_frame, fg_color="transparent")
        left_title_frame.grid(row=0, column=0, sticky="ew", pady=(0,5))
        left_title_frame.grid_columnconfigure(0, weight=1) # Label do título
        left_title_frame.grid_columnconfigure(1, weight=0) # Botão Mostrar Todas

        self.transaction_list_title_label = customtkinter.CTkLabel(left_title_frame, text="Transações do Mês", font=FONTE_LABEL_BOLD)
        self.transaction_list_title_label.grid(row=0, column=0, sticky="w")

        self.show_all_button = customtkinter.CTkButton(left_title_frame, text="Mostrar Todas", font=(FONTE_FAMILIA, 10),
                                                       command=self._show_all_transactions, height=25, width=100,
                                                       corner_radius=BOTAO_CORNER_RADIUS, fg_color="gray40", hover_color="gray50")
        self.show_all_button.grid(row=0, column=1, sticky="e", padx=(5,0))

        self.left_detail_scroll_frame = customtkinter.CTkScrollableFrame(left_column_container_frame) # Removido label_text
        self.left_detail_scroll_frame.grid(row=1, column=0, sticky="nsew")
        # Placeholder inicial
        self.left_placeholder_label = customtkinter.CTkLabel(self.left_detail_scroll_frame, text="Selecione um mês para ver as transações.", font=FONTE_LABEL_NORMAL, text_color="gray60")
        self.left_placeholder_label.pack(pady=20, padx=10)

        # Botões Editar e Excluir
        edit_delete_buttons_frame = customtkinter.CTkFrame(left_column_container_frame, fg_color="transparent")
        edit_delete_buttons_frame.grid(row=2, column=0, sticky="ew", pady=(10,0))
        self.delete_button = customtkinter.CTkButton(edit_delete_buttons_frame, text="Excluir Selecionadas", command=self._handle_delete_transaction, state="disabled", width=180, height=30, corner_radius=BOTAO_CORNER_RADIUS, fg_color="gray10", hover_color="gray17") # Cor inicial desabilitada
        self.delete_button.pack(side="left", padx=5) # Ajustar posicionamento se necessário

        # --- Coluna da Direita: Resumo ---
        self.right_summary_frame = customtkinter.CTkFrame(content_splitter_frame, fg_color="gray17", corner_radius=10) # Cor de fundo para destaque
        self.right_summary_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 0)) # Removido padx=(5,0)
        # Placeholder inicial
        self.right_placeholder_label = customtkinter.CTkLabel(self.right_summary_frame, text="Selecione um mês para ver o resumo.", font=FONTE_LABEL_NORMAL, text_color="gray60")
        self.right_placeholder_label.pack(pady=20, padx=10, expand=True, fill="both")


        # Botão Fechar
        close_button = customtkinter.CTkButton(main_frame, text="Fechar", command=self.destroy,
                                               height=30, font=(FONTE_FAMILIA, 12, "bold"),
                                               corner_radius=BOTAO_CORNER_RADIUS,
                                               fg_color="gray50", hover_color="gray40")
        close_button.pack(pady=(10,0), side="bottom")

    def month_detail_selected(self, month_name, year, user_id):
        month_number = self.months_list.index(month_name) + 1
        self.current_month_name_selected = month_name # Salva para recarregar

        # Limpar placeholders e conteúdo anterior
        if hasattr(self, 'left_placeholder_label') and self.left_placeholder_label.winfo_exists():
            self.left_placeholder_label.pack_forget()
        if hasattr(self, 'right_placeholder_label') and self.right_placeholder_label.winfo_exists():
            self.right_placeholder_label.pack_forget()

        for widget in self.right_summary_frame.winfo_children():
            widget.destroy()

        self.all_transactions_for_month = get_transactions_for_month(user_id, year, month_number)
        self.selected_transaction_ids.clear() # Limpa seleções anteriores
        self.current_filter_type = None # Reseta o filtro
        self._display_transactions(self.all_transactions_for_month)
        self._update_action_buttons_state()

        self.transaction_list_title_label.configure(text=f"Transações de {month_name}")

        # --- Popular Coluna da Direita (Resumo) ---
        summary_data = get_category_summary_for_month(user_id, year, month_number)
        total_despesas = 0
        total_proventos = 0

        customtkinter.CTkLabel(self.right_summary_frame, text=f"Resumo de {month_name}", font=FONTE_LABEL_BOLD).pack(pady=10)

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
        header_frame.grid_columnconfigure(0, weight=0) # Checkbox (Sel.)
        header_frame.grid_columnconfigure(1, weight=2) # Data
        header_frame.grid_columnconfigure(2, weight=4) # Descrição
        header_frame.grid_columnconfigure(3, weight=3) # Categoria
        header_frame.grid_columnconfigure(4, weight=2) # Valor
        header_frame.grid_columnconfigure(5, weight=1) # Status
        customtkinter.CTkLabel(header_frame, text="Sel.", font=FONTE_LABEL_BOLD).grid(row=0, column=0, sticky="w", padx=(5,2))
        customtkinter.CTkLabel(header_frame, text="Data", font=FONTE_LABEL_BOLD).grid(row=0, column=1, sticky="w", padx=2)
        customtkinter.CTkLabel(header_frame, text="Descrição", font=FONTE_LABEL_BOLD).grid(row=0, column=2, sticky="ew", padx=2)
        customtkinter.CTkLabel(header_frame, text="Categoria", font=FONTE_LABEL_BOLD).grid(row=0, column=3, sticky="ew", padx=2)
        customtkinter.CTkLabel(header_frame, text="Valor", font=FONTE_LABEL_BOLD).grid(row=0, column=4, sticky="e", padx=2)
        customtkinter.CTkLabel(header_frame, text="Status", font=FONTE_LABEL_BOLD).grid(row=0, column=5, sticky="w", padx=2)

        for trans in transactions_to_display:
            row_frame_fg_color = "transparent"
            text_color_val = "white"

            if trans['category_type'] == 'Provento':
                text_color_val = "green"
            elif trans['category_type'] == 'Despesa':
                text_color_val = "tomato"
            else:
                print(f"DEBUG: Tipo de categoria desconhecido: {trans['category_type']}")
                row_frame_fg_color = "gray10"

            row_frame = customtkinter.CTkFrame(self.left_detail_scroll_frame, fg_color=row_frame_fg_color, corner_radius=3)
            row_frame.pack(fill="x", pady=1, padx=2)
             # Configuração de colunas para os elementos dentro de row_frame
            row_frame.grid_columnconfigure(0, weight=0)  # Checkbox (Sel.)
            row_frame.grid_columnconfigure(1, weight=2)  # Data Venc.
            row_frame.grid_columnconfigure(2, weight=4)  # Descrição
            row_frame.grid_columnconfigure(3, weight=3)  # Categoria
            row_frame.grid_columnconfigure(4, weight=1)  # Parcelas
            row_frame.grid_columnconfigure(5, weight=2)  # Valor
            row_frame.grid_columnconfigure(6, weight=1)  # Status
            row_frame.grid_columnconfigure(7, weight=2)  # Data Lanç.

            # Checkbox para seleção
            checkbox_var = customtkinter.StringVar(value="off")
            checkbox = customtkinter.CTkCheckBox(row_frame, text="", variable=checkbox_var, onvalue="on", offvalue="off",
                                                 command=lambda t_id=trans['id'], var=checkbox_var: self._toggle_selection(t_id, var),
                                                 width=20) 
            checkbox.grid(row=0, column=0, sticky="w", padx=(5,2)) # Padronizado padx
            if trans['id'] in self.selected_transaction_ids: # Mantém estado do checkbox ao redesenhar
                checkbox_var.set("on")

            # Labels dentro do row_frame
            # Tornar os labels clicáveis também, ou o frame inteiro
            due_date_label = customtkinter.CTkLabel(row_frame, text=trans.get('due_date', 'N/A'), font=FONTE_LABEL_PEQUENA, cursor="hand2")
            due_date_label.grid(row=0, column=1, sticky="w", padx=2)
            description_label = customtkinter.CTkLabel(row_frame, text=trans['description'], font=FONTE_LABEL_PEQUENA, anchor="w", cursor="hand2")
            description_label.grid(row=0, column=2, sticky="ew", padx=2)# Categoria sem cor de fundo, usa cor de texto padrão
            cat_label = customtkinter.CTkLabel(row_frame, text=trans['category_name'], font=FONTE_LABEL_PEQUENA, corner_radius=3, padx=3, anchor="w", cursor="hand2")
            cat_label.grid(row=0, column=3, sticky="ew", padx=2) # Alterado para sticky="ew"
            customtkinter.CTkLabel(row_frame, text=trans.get('installments', '-'), font=FONTE_LABEL_PEQUENA, cursor="hand2").grid(row=0, column=4, sticky="w", padx=2)
            customtkinter.CTkLabel(row_frame, text=f"R$ {trans['value']:.2f}", font=FONTE_LABEL_PEQUENA, text_color=text_color_val, cursor="hand2").grid(row=0, column=5, sticky="e", padx=2)
            customtkinter.CTkLabel(row_frame, text=trans.get('status', 'N/A'), font=FONTE_LABEL_PEQUENA, cursor="hand2").grid(row=0, column=6, sticky="w", padx=2)
            customtkinter.CTkLabel(row_frame, text=trans.get('launch_date', 'N/A'), font=FONTE_LABEL_PEQUENA, cursor="hand2").grid(row=0, column=7, sticky="w", padx=2)
            
            # Bind click event to the entire row_frame
            row_frame.bind("<Button-1>", lambda event, t_id=trans['id']: self._open_consulta_transacao(t_id))
            for child in row_frame.winfo_children(): # Bind para os filhos também, exceto o checkbox
                if not isinstance(child, customtkinter.CTkCheckBox):
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
        self.selected_transaction_ids.clear() # Limpa seleção ao filtrar
        self._update_action_buttons_state()

    def _filter_by_provento(self, event=None):
        self.current_filter_type = "Provento"
        filtered_transactions = [t for t in self.all_transactions_for_month if t['category_type'] == "Provento"]
        self._display_transactions(filtered_transactions)
        self.selected_transaction_ids.clear()
        self._update_action_buttons_state()

    def _show_all_transactions(self, event=None):
        self.current_filter_type = None
        self._display_transactions(self.all_transactions_for_month)
        self.selected_transaction_ids.clear()
        self._update_action_buttons_state()

    def _update_action_buttons_state(self):
        if self.selected_transaction_ids:
            self.delete_button.configure(state="normal", fg_color="#2196F3", hover_color="#1A78C2") # Azul quando habilitado
        else:
            self.delete_button.configure(state="disabled", fg_color="gray10", hover_color="gray17") # Cinza escuro quando desabilitado

    def _handle_delete_transaction(self):
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
            
            self._refresh_after_action()

    def _refresh_after_action(self):
        """Recarrega os dados do mês atual após uma ação como editar ou excluir."""
        if self.current_month_name_selected:
            self.month_detail_selected(self.current_month_name_selected, self.selected_year, self.current_user_id)

    def _open_consulta_transacao(self, transaction_id):
        print(f"Abrindo consulta para transação ID: {transaction_id}")
        if self.form_consulta_transacao_window is None or not self.form_consulta_transacao_window.winfo_exists():
            self.form_consulta_transacao_window = FormConsultaTransacaoWindow(
                master=self, transaction_id=transaction_id, on_save_callback=self._refresh_after_action
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