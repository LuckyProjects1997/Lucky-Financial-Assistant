# c:\Users\lucas.couto\Downloads\form_detalhes_mensais_fixado_scroll.py
# form_detalhes_mensais.py
import customtkinter
import re # Para remover a informação de parcela da descrição
# import tkinter as tk # Para constantes de alinhamento
from Database import get_category_summary_for_month, get_transactions_for_month # Importa funções do Database
from form_consulta_transacao import FormConsultaTransacaoWindow # Importa a janela de consulta de transação
import datetime # Para formatação de datas

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
        self.current_month_name_selected = None # Para recarregar a view
        self.all_transactions_for_month = [] # Para armazenar as transações do mês selecionado
        self.form_consulta_transacao_window = None # Referência para a janela de consulta

        # --- Frame Principal ---
        main_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        # Configurar grid para o main_frame
        main_frame.grid_columnconfigure(0, weight=1) # Coluna única para expandir
        main_frame.grid_rowconfigure(0, weight=0) # Título "Selecione o Mês"
        main_frame.grid_rowconfigure(1, weight=0) # Botões dos meses
        main_frame.grid_rowconfigure(2, weight=0) # Título "Detalhes"
        main_frame.grid_rowconfigure(3, weight=0) # Seção "Detalhes" (altura fixa)
        main_frame.grid_rowconfigure(4, weight=1) # summary_section_container (expande verticalmente)
        main_frame.grid_rowconfigure(5, weight=0) # Botão Fechar

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

        # --- Título da Seção "Detalhes" ---
        details_title_label = customtkinter.CTkLabel(main_frame, text="Detalhes", font=FONTE_LABEL_BOLD)
        details_title_label.grid(row=2, column=0, pady=(10, 5), sticky="w")

        # --- Seção "Detalhes" (similar ao Resumo Anual do Dashboard, mas sem dados) ---
        details_section_container = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        details_section_container.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        details_section_container.grid_columnconfigure(0, weight=1) # Coluna para Despesas
        details_section_container.grid_columnconfigure(1, weight=1) # Coluna para Proventos
        details_section_container.grid_rowconfigure(0, weight=0) # Linha única para os scrollables

        # Scrollable frame para "Despesas" (apenas título)
        self.despesas_details_scroll_frame = customtkinter.CTkScrollableFrame(details_section_container, label_text="Despesas", label_font=FONTE_LABEL_BOLD, fg_color="gray17", height=200) # Altura aumentada
        self.despesas_details_scroll_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=5)

        # Scrollable frame para "Proventos" (apenas título)
        self.proventos_details_scroll_frame = customtkinter.CTkScrollableFrame(details_section_container, label_text="Proventos", label_font=FONTE_LABEL_BOLD, fg_color="gray17", height=200) # Altura aumentada
        self.proventos_details_scroll_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=5)

        # --- Seção de Resumo (diretamente no main_frame) ---
        summary_section_container = customtkinter.CTkFrame(main_frame, fg_color="transparent") # Container para título e caixa de resumo
        summary_section_container.grid(row=4, column=0, sticky="nsew", pady=(10, 0)) # Movido para row=4

        # Título para o Resumo (acima da caixa cinza)
        self.summary_title_label = customtkinter.CTkLabel(summary_section_container, text="Resumo do Mês", font=FONTE_LABEL_BOLD)
        self.summary_title_label.pack(anchor="w", pady=(0, 5)) # Empacotado no container, alinhado à esquerda

        # Frame de conteúdo do Resumo (caixa cinza)
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
                                               corner_radius=BOTAO_CORNER_RADIUS, fg_color="gray50", hover_color="gray40") # Movido para row=5
        close_button.grid(row=5, column=0, pady=(20,0), sticky="s")

    def month_detail_selected(self, month_name, year, user_id):
        month_number = self.months_list.index(month_name) + 1
        print(f"DEBUG: month_detail_selected - Mês: {month_name}, Ano: {year}, User ID: {user_id}")
        self.current_month_name_selected = month_name # Salva para recarregar

        # Limpar placeholders e conteúdo anterior
        if hasattr(self, 'right_placeholder_label') and self.right_placeholder_label.winfo_exists():
            self.right_placeholder_label.pack_forget()

        # Limpar conteúdo anterior das tabelas de detalhes e do resumo
        for widget in self.despesas_details_scroll_frame.winfo_children():
            widget.destroy()
        for widget in self.proventos_details_scroll_frame.winfo_children():
            widget.destroy()
        for widget in self.right_summary_frame.winfo_children():
            widget.destroy()

        self.all_transactions_for_month = get_transactions_for_month(user_id, year, month_number)
        self.summary_title_label.configure(text=f"Resumo de {month_name}") # Atualiza o novo título do resumo
        self._display_month_transactions() # Popula as tabelas de Despesas e Proventos

        # --- Popular Resumo ---
        summary_data = get_category_summary_for_month(user_id, year, month_number)
        total_despesas = 0
        total_proventos = 0

        if not summary_data:
            # Não precisa mais exibir mensagem no left_detail_scroll_frame aqui, _display_transactions já faz isso.
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

        total_despesas_label = customtkinter.CTkLabel(totals_frame, text=f"Total Despesas: R$ {total_despesas:.2f}", font=FONTE_LABEL_BOLD, text_color="tomato")
        total_despesas_label.pack(anchor="w")
        # total_despesas_label.bind("<Button-1>", self._filter_by_despesa) # Removido binding

        total_proventos_label = customtkinter.CTkLabel(totals_frame, text=f"Total Proventos: R$ {total_proventos:.2f}", font=FONTE_LABEL_BOLD, text_color="lightgreen")
        total_proventos_label.pack(anchor="w")
        # total_proventos_label.bind("<Button-1>", self._filter_by_provento) # Removido binding

        saldo = total_proventos - total_despesas
        saldo_color = "lightgreen" if saldo >=0 else "tomato"
        customtkinter.CTkLabel(totals_frame, text=f"Saldo do Mês: R$ {saldo:.2f}", font=FONTE_LABEL_BOLD, text_color=saldo_color).pack(anchor="w", pady=(5,0))

    def _display_month_transactions(self):
        despesas = [t for t in self.all_transactions_for_month if t['category_type'] == 'Despesa']
        proventos = [t for t in self.all_transactions_for_month if t['category_type'] == 'Provento']

        self._populate_transaction_table(self.despesas_details_scroll_frame, despesas, "Despesa")
        self._populate_transaction_table(self.proventos_details_scroll_frame, proventos, "Provento")

    def _populate_transaction_table(self, parent_frame, transactions, transaction_type):
        # Limpa o conteúdo anterior do frame
        for widget in parent_frame.winfo_children():
            widget.destroy()

        if not transactions:
            customtkinter.CTkLabel(
                parent_frame,
                text=f"Nenhuma transação de {transaction_type.lower()} para este mês.",
                font=FONTE_LABEL_NORMAL,
                text_color="gray60"
            ).grid(row=1, column=0, columnspan=8, pady=20, padx=10)
            return

        # Cabeçalhos
        col_weights = [1, 3, 2, 1, 1, 1, 1, 1]
        headers = ["Data", "Descrição", "Categoria", "V. Parcela", "V. Total", "Status", "Modalidade", "Parcela"]

        for i, header_text in enumerate(headers):
            parent_frame.grid_columnconfigure(i, weight=col_weights[i])
            anchor_val = "w" if header_text in ["Descrição", "Categoria", "V. Parcela", "V. Total"] else "center"
            customtkinter.CTkLabel(
                parent_frame,
                text=header_text,
                font=FONTE_LABEL_PEQUENA,
                anchor=anchor_val
            ).grid(row=0, column=i, sticky="ew", padx=2)

        # Linhas de Transação
        for row_idx, trans in enumerate(transactions, start=1):
            widgets = []
            # Data
            try:
                due_date_obj = datetime.datetime.strptime(trans['due_date'], "%Y-%m-%d")
                formatted_date = due_date_obj.strftime("%d/%m/%Y")
            except (ValueError, TypeError):
                formatted_date = trans['due_date']
            widgets.append(customtkinter.CTkLabel(
                parent_frame, text=formatted_date, font=FONTE_LABEL_PEQUENA, anchor="center"
            ))

            # Descrição
            original_description = trans['description']
            display_description = re.sub(r'\s*\(\d+/\d+\)$', '', original_description)
            widgets.append(customtkinter.CTkLabel(
                parent_frame, text=display_description, font=FONTE_LABEL_PEQUENA, anchor="w"
            ))

            # Categoria
            widgets.append(customtkinter.CTkLabel(
                parent_frame, text=trans['category_name'], font=FONTE_LABEL_PEQUENA, anchor="w"
            ))

            # V. Parcela
            valor_parcela = trans['value']
            text_color_val = "tomato" if transaction_type == "Despesa" else "lightgreen"
            widgets.append(customtkinter.CTkLabel(
                parent_frame, text=f"R$ {valor_parcela:.2f}", font=FONTE_LABEL_PEQUENA, text_color=text_color_val, anchor="w"
            ))

            # V. Total
            installments_str = trans.get('installments', "1/1")
            total_installments_num = 1
            if installments_str and "/" in installments_str:
                try:
                    total_installments_num = int(installments_str.split('/')[1])
                except (ValueError, IndexError):
                    total_installments_num = 1
            valor_total_transacao = valor_parcela * total_installments_num
            widgets.append(customtkinter.CTkLabel(
                parent_frame, text=f"R$ {valor_total_transacao:.2f}", font=FONTE_LABEL_PEQUENA, text_color=text_color_val, anchor="w"
            ))

            # Status
            widgets.append(customtkinter.CTkLabel(
                parent_frame, text=trans.get('status', 'N/A'), font=FONTE_LABEL_PEQUENA, anchor="center"
            ))

            # Modalidade
            widgets.append(customtkinter.CTkLabel(
                parent_frame, text=trans.get('modality', 'N/A'), font=FONTE_LABEL_PEQUENA, anchor="center"
            ))

            # Parcela
            widgets.append(customtkinter.CTkLabel(
                parent_frame, text=trans.get('installments', '-'), font=FONTE_LABEL_PEQUENA, anchor="center"
            ))

            # Adiciona os widgets na grid e vincula o clique
            transaction_id_for_click = trans['id']
            for col, widget in enumerate(widgets):
                widget.grid(row=row_idx, column=col, sticky="ew", padx=2)
                widget.bind("<Button-1>", lambda event, t_id=transaction_id_for_click: self._open_consulta_transacao(t_id))

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
        print(f"DEBUG DetalhesMensais: Abrindo consulta para transação ID: {transaction_id}")
        if self.form_consulta_transacao_window is None or not self.form_consulta_transacao_window.winfo_exists():
            self.form_consulta_transacao_window = FormConsultaTransacaoWindow(
                master=self, # O master é esta janela de DetalhesMensais
                transaction_id=transaction_id,
                on_action_completed_callback=self._refresh_after_action # Passa o método de refresh
            )
            self.form_consulta_transacao_window.focus() # Traz a nova janela para o foco
        else:
            self.form_consulta_transacao_window.focus() # Se a janela já existe, apenas a traz para o foco

if __name__ == '__main__':
    # Para testar esta janela isoladamente
    app_root = customtkinter.CTk()
    app_root.withdraw() # Esconde a janela root principal
    form_detalhes = FormDetalhesMensaisWindow(master=app_root, current_user_id="test_user_01", selected_year="2024")
    app_root.mainloop()
