# form_categoria_detalhes_transacoes.py
import customtkinter
import datetime
import re
import sys
import os

# --- INÍCIO DA CORREÇÃO PARA PYLANCE E EXECUÇÃO DIRETA ---
# Adiciona o diretório do script atual (que deve ser 'App') ao sys.path.
# Isso ajuda o Pylance a encontrar módulos no mesmo diretório e também
# permite que o script seja executado diretamente para testes, resolvendo importações locais.
script_directory = os.path.dirname(os.path.abspath(__file__))
if script_directory not in sys.path:
    sys.path.append(script_directory)
# --- FIM DA CORREÇÃO ---

import Database
from form_consulta_transacao import FormConsultaTransacaoWindow
# Definições de fonte padrão
FONTE_FAMILIA = "Segoe UI"
FONTE_TITULO_FORM = (FONTE_FAMILIA, 16, "bold")
FONTE_LABEL_NORMAL = (FONTE_FAMILIA, 12)
FONTE_LABEL_BOLD = (FONTE_FAMILIA, 12, "bold")
FONTE_LABEL_PEQUENA = (FONTE_FAMILIA, 10)

class FormCategoriaDetalhesTransacoesWindow(customtkinter.CTkToplevel):
    def __init__(self, master, user_id, year, category_id, category_name, month_number=None, month_name=None):
        super().__init__(master)
        self.user_id = user_id
        self.year = year
        self.month_number = month_number
        self.month_name = month_name
        self.category_id = category_id
        self.category_name = category_name

        period_str = f"{self.month_name}/{self.year}" if self.month_name else str(self.year)
        self.title(f"Transações - {self.category_name} ({period_str})")
        self.geometry("800x500")
        self.configure(fg_color="#1c1c1c")
        self.lift()
        self.attributes("-topmost", True)
        self.grab_set()

        self.transactions = []
        self.sort_state = {'column': None, 'direction': 'asc'}
        self.form_consulta_transacao_window = None

        self._setup_ui()
        self._load_and_display_transactions()

    def _setup_ui(self):
        main_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=10, pady=10)

        title_label = customtkinter.CTkLabel(main_frame, text=f"Detalhes da Categoria: {self.category_name}", font=FONTE_TITULO_FORM)
        title_label.pack(pady=(0, 10), anchor="w")

        self.scrollable_frame = customtkinter.CTkScrollableFrame(main_frame, fg_color="gray17")
        self.scrollable_frame.pack(expand=True, fill="both")
        # self.scrollable_frame.grid_columnconfigure(0, weight=1) # Removido: a configuração da coluna será feita em _populate_transaction_table

        close_button = customtkinter.CTkButton(main_frame, text="Fechar", command=self.destroy, width=100)
        close_button.pack(pady=(10,0))

    def _load_and_display_transactions(self):
        self.transactions = Database.get_transactions_for_category_period(
            self.user_id, self.category_id, self.year, self.month_number
        )
        self._populate_transaction_table()

    def _sort_table(self, event, header_text):
        if self.sort_state['column'] == header_text:
            self.sort_state['direction'] = 'desc' if self.sort_state['direction'] == 'asc' else 'asc'
        else:
            self.sort_state['column'] = header_text
            self.sort_state['direction'] = 'asc'
        self._populate_transaction_table()

    def _populate_transaction_table(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        display_transactions = list(self.transactions)
        if self.sort_state['column']:
            sort_column = self.sort_state['column']
            sort_direction = self.sort_state['direction']
            sort_key_map = {
                "Data": ('due_date', 'date'), "Descrição": ('description', 'string'),
                "V. Parcela": ('value', 'number'), "V. Total": ('value', 'total_value'),
                "Status": ('status', 'string'), "Modalidade": ('modality', 'string'),
                "Parcela": ('installments', 'installment_number'), "Forma Pag.": ('payment_method', 'string')
            }
            sort_info = sort_key_map.get(sort_column)
            if sort_info:
                sort_db_key, sort_type = sort_info
                def get_sort_value(trans):
                    if sort_type == 'date':
                        return datetime.datetime.strptime(trans.get(sort_db_key, '1900-01-01'), "%Y-%m-%d").date() if trans.get(sort_db_key) else datetime.date.min
                    elif sort_type == 'number':
                        return trans.get(sort_db_key, 0.0)
                    elif sort_type == 'total_value':
                        return trans.get('value', 0.0) * int(trans.get('installments', '1/1').split('/')[1]) if '/' in trans.get('installments', '1/1') else trans.get('value', 0.0)
                    elif sort_type == 'installment_number':
                        return int(trans.get(sort_db_key, '0/1').split('/')[0]) if '/' in trans.get(sort_db_key, '0/1') else 0
                    return str(trans.get(sort_db_key, '')).lower()
                display_transactions = sorted(display_transactions, key=get_sort_value, reverse=(sort_direction == 'desc'))

        # Cabeçalhos
        headers = ["Data", "Descrição", "V. Parcela", "V. Total", "Status", "Modalidade", "Parcela", "Forma Pag."]
        col_weights = [1, 3, 1, 1, 1, 1, 1, 1] # Ajustar pesos conforme necessário

        # Configurar pesos das colunas diretamente no scrollable_frame
        for i, header_text in enumerate(headers):
            self.scrollable_frame.grid_columnconfigure(i, weight=col_weights[i])
            sort_indicator = ""
            if self.sort_state['column'] == header_text:
                sort_indicator = " ▲" if self.sort_state['direction'] == 'asc' else " ▼"
            
            header_label = customtkinter.CTkLabel(
                self.scrollable_frame, # Adicionado diretamente ao scrollable_frame
                text=f"{header_text}{sort_indicator}", 
                font=FONTE_LABEL_PEQUENA, 
                anchor="center", 
                cursor="hand2"
            )
            header_label.grid(row=0, column=i, sticky="nsew", padx=2, pady=(5,2))
            header_label.bind("<Button-1>", lambda e, ht=header_text: self._sort_table(e, ht))

        if not self.transactions:
            customtkinter.CTkLabel(
                self.scrollable_frame, 
                text="Nenhuma transação encontrada para esta categoria no período.", 
                font=FONTE_LABEL_NORMAL, 
                text_color="gray60", 
                anchor="w"
            ).grid(row=1, column=0, columnspan=len(headers), pady=20, padx=10, sticky="ew")
            return

        # Linhas de Transação
        for row_idx, trans in enumerate(display_transactions, start=1): # Começa da linha 1
            widgets_in_row = [] # Para aplicar o bind de clique

            # Data
            try:
                due_date_obj = datetime.datetime.strptime(trans['due_date'], "%Y-%m-%d")
                formatted_date = due_date_obj.strftime("%d/%m/%Y")
            except (ValueError, TypeError):
                formatted_date = trans['due_date']
            widgets_in_row.append(customtkinter.CTkLabel(self.scrollable_frame, text=formatted_date, font=FONTE_LABEL_PEQUENA, anchor="w"))

            # Descrição
            original_description = trans['description']
            display_description = re.sub(r'\s*\(\d+/\d+\)$', '', original_description)
            widgets_in_row.append(customtkinter.CTkLabel(self.scrollable_frame, text=display_description, font=FONTE_LABEL_PEQUENA, anchor="w"))

            # V. Parcela
            valor_parcela = trans['value']
            text_color_val = "tomato" if trans['category_type'] == "Despesa" else "lightgreen"
            widgets_in_row.append(customtkinter.CTkLabel(self.scrollable_frame, text=f"R$ {valor_parcela:.2f}", font=FONTE_LABEL_PEQUENA, text_color=text_color_val, anchor="w"))

            # V. Total
            installments_str = trans.get('installments', "1/1")
            total_installments_num = 1
            if installments_str and "/" in installments_str:
                try: total_installments_num = int(installments_str.split('/')[1])
                except (ValueError, IndexError): pass # Mais específico
            valor_total_transacao = valor_parcela * total_installments_num
            widgets_in_row.append(customtkinter.CTkLabel(self.scrollable_frame, text=f"R$ {valor_total_transacao:.2f}", font=FONTE_LABEL_PEQUENA, text_color=text_color_val, anchor="w"))

            # Status
            widgets_in_row.append(customtkinter.CTkLabel(self.scrollable_frame, text=trans.get('status', 'N/A'), font=FONTE_LABEL_PEQUENA, anchor="w"))
            # Modalidade
            widgets_in_row.append(customtkinter.CTkLabel(self.scrollable_frame, text=trans.get('modality', 'N/A'), font=FONTE_LABEL_PEQUENA, anchor="w"))
            # Parcela
            widgets_in_row.append(customtkinter.CTkLabel(self.scrollable_frame, text=trans.get('installments', '-'), font=FONTE_LABEL_PEQUENA, anchor="w"))
            # Forma Pag.
            payment_method_display = trans.get('payment_method', '-') if trans.get('status') == 'Pago' else '-'
            widgets_in_row.append(customtkinter.CTkLabel(self.scrollable_frame, text=payment_method_display, font=FONTE_LABEL_PEQUENA, anchor="w"))

            # Bind click para abrir consulta da transação
            transaction_id = trans['id'] # Renomeado para consistência
            for col_idx, widget_in_cell in enumerate(widgets_in_row):
                widget_in_cell.grid(row=row_idx, column=col_idx, sticky="nsew", padx=2, pady=1)
                widget_in_cell.bind("<Button-1>", lambda e, t_id=transaction_id: self._open_consulta_transacao(t_id))

    def _open_consulta_transacao(self, transaction_id):
        if self.form_consulta_transacao_window is None or not self.form_consulta_transacao_window.winfo_exists():
            self.form_consulta_transacao_window = FormConsultaTransacaoWindow(
                master=self, # Master é esta janela de detalhes da categoria
                transaction_id=transaction_id,
                on_action_completed_callback=self._refresh_on_action_completed # Callback para recarregar
            )
            if getattr(self.form_consulta_transacao_window, '_initialization_successful', False) and \
               self.form_consulta_transacao_window.winfo_exists():
                self.form_consulta_transacao_window.focus()
        else:
            if self.form_consulta_transacao_window.winfo_exists():
                self.form_consulta_transacao_window.focus()

    def _refresh_on_action_completed(self):
        """Recarrega os dados da lista de transações após uma ação na janela de consulta."""
        print("DEBUG FormCategoriaDetalhes: _refresh_on_action_completed called.")
        self._load_and_display_transactions()

if __name__ == '__main__':
    # Exemplo de uso (para teste)
    app = customtkinter.CTk()
    app.withdraw() # Esconde a janela root principal

    # Simular dados para teste
    test_user_id = "test_user_01" # Substitua por um ID de usuário válido
    test_year = 2024
    test_category_id = "cat_despesa_01" # Substitua por um ID de categoria válido
    test_category_name = "Alimentação"
    test_month_number = 5 # Maio
    test_month_name = "Maio"

    # Certifique-se de que Database.py está acessível e o DB existe
    # e que há transações para os IDs de teste.

    # Teste para visualização mensal
    # details_window = FormCategoriaDetalhesTransacoesWindow(app, test_user_id, test_year, test_category_id, test_category_name, test_month_number, test_month_name)
    
    # Teste para visualização anual (sem month_number e month_name)
    details_window_annual = FormCategoriaDetalhesTransacoesWindow(app, test_user_id, test_year, test_category_id, test_category_name)
    
    app.mainloop()