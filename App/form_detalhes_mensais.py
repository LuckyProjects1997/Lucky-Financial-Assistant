# c:\Users\lucas.couto\Downloads\form_detalhes_mensais_fixado_scroll.py
# form_detalhes_mensais.py
import customtkinter
import sys # Add
import os  # Add

# --- INÍCIO DA CORREÇÃO PARA PYLANCE E EXECUÇÃO DIRETA ---
script_directory = os.path.dirname(os.path.abspath(__file__))
if script_directory not in sys.path:
    sys.path.append(script_directory)
# --- FIM DA CORREÇÃO ---
import re # Para remover a informação de parcela da descrição
# import tkinter as tk # Para constantes de alinhamento
from Database import get_category_summary_for_month, get_transactions_for_month # Importa funções do Database
from form_categoria_detalhes_transacoes import FormCategoriaDetalhesTransacoesWindow # Importa a nova janela
from form_transacao import FormTransacaoWindow # Importa a janela de formulário de transação
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

class DetalhesMensaisView(customtkinter.CTkFrame): # ALTERADO: Herda de CTkFrame
    def __init__(self, master=None, current_user_id=None, selected_year=None, close_callback=None, main_dashboard_refresh_callback=None):
        super().__init__(master)
        self.configure(fg_color="transparent") # O frame em si será transparente
        self.close_callback = close_callback
        self.main_dashboard_refresh_callback = main_dashboard_refresh_callback

        self.current_user_id = current_user_id
        self.selected_year = selected_year
        self.months_list = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", # Mantido para lógica interna
                            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        self.current_month_name_selected = None # Para recarregar a view
        self.all_transactions_for_month = [] # Para armazenar as transações do mês selecionado
        self.form_transacao_window_ref = None # Referência para a janela de cadastro de transação
        self.form_consulta_transacao_window = None # Referência para a janela de consulta
        self.form_categoria_detalhes_window = None # Referência para a janela de detalhes da categoria

        # Dicionários para armazenar o estado de ordenação
        # { 'column': header_text, 'direction': 'asc' ou 'desc' }
        self.despesas_sort_state = {'column': None, 'direction': 'asc'}
        self.proventos_sort_state = {'column': None, 'direction': 'asc'}


        # --- Frame Principal ---
        main_frame = customtkinter.CTkFrame(self, fg_color="#1c1c1c") # Cor de fundo para a view
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        # Configurar grid para o main_frame
        main_frame.grid_columnconfigure(0, weight=1) # Coluna única para expandir
        main_frame.grid_rowconfigure(0, weight=0) # Título "Selecione o Mês"
        main_frame.grid_rowconfigure(1, weight=0) # Botões dos meses
        main_frame.grid_rowconfigure(2, weight=0) # Título "Detalhes"
        main_frame.grid_rowconfigure(3, weight=0) # Seção "Detalhes" (altura fixa)
        main_frame.grid_rowconfigure(4, weight=0) # Título "Resumo por Categoria"
        main_frame.grid_rowconfigure(5, weight=1) # summary_content_frame (expande verticalmente)
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
        details_section_container.grid_columnconfigure(2, weight=0, minsize=230) # Coluna para Totais do Mês (fixed width)
        details_section_container.grid_rowconfigure(0, weight=0) # Linha única para os scrollables

        # Scrollable frame para "Despesas" (apenas título)
        self.despesas_details_scroll_frame = customtkinter.CTkScrollableFrame(details_section_container, label_text="Despesas", label_font=FONTE_LABEL_BOLD, fg_color="gray17", height=200) # Altura aumentada
        self.despesas_details_scroll_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=0)

        # Scrollable frame para "Proventos" (apenas título)
        self.proventos_details_scroll_frame = customtkinter.CTkScrollableFrame(details_section_container, label_text="Proventos", label_font=FONTE_LABEL_BOLD, fg_color="gray17", height=200) # Altura aumentada
        self.proventos_details_scroll_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 5), pady=0)

        # Frame para "Totais do Mês" (terceira coluna)
        self.monthly_totals_display_frame = customtkinter.CTkFrame(details_section_container, fg_color="gray17", corner_radius=10, width=230)
        self.monthly_totals_display_frame.grid(row=0, column=2, sticky="ns", padx=(0,0), pady=0) # Sticky "ns" para preencher verticalmente
        self.monthly_totals_display_frame.pack_propagate(False) # Impede que os filhos alterem o tamanho
        # Placeholder inicial para o frame de totais
        self.totals_placeholder_label = customtkinter.CTkLabel(self.monthly_totals_display_frame, text="Selecione um mês.", font=FONTE_LABEL_NORMAL, text_color="gray60")
        self.totals_placeholder_label.pack(pady=20, padx=10, expand=True)


        # --- Seção de Resumo por Categoria (abaixo dos detalhes) ---
        summary_category_title_label = customtkinter.CTkLabel(main_frame, text="Resumo por Categoria", font=FONTE_LABEL_BOLD)
        summary_category_title_label.grid(row=4, column=0, pady=(15, 5), sticky="w")

        # Frame de conteúdo do Resumo por Categoria
        self.right_summary_frame = customtkinter.CTkFrame(main_frame, fg_color="gray17", corner_radius=10)
        # self.right_summary_frame.pack_propagate(False) # Removido ou ajustado se necessário
        self.right_summary_frame.grid(row=5, column=0, sticky="nsew", pady=(0,10)) # Ocupa a linha que expande


        # Configurar grid interno para o right_summary_frame (lista de categorias à esquerda, totais à direita)
        self.right_summary_frame.grid_columnconfigure(0, weight=1) # Coluna única para lista de categorias
        self.right_summary_frame.grid_rowconfigure(0, weight=1)    # Linha única para expandir verticalmente
        # Placeholder inicial
        self.right_placeholder_label = customtkinter.CTkLabel(self.right_summary_frame, text="Selecione um mês.", font=FONTE_LABEL_NORMAL, text_color="gray60")
        self.right_placeholder_label.grid(row=0, column=0, columnspan=2, pady=20, padx=10, sticky="nsew")

        # --- Frame para Botões de Ação Inferiores ---
        bottom_actions_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        bottom_actions_frame.grid(row=6, column=0, pady=(20,0), sticky="ew") # Movido para row=6
        bottom_actions_frame.grid_columnconfigure(0, weight=1) # Espaço à esquerda
        bottom_actions_frame.grid_columnconfigure(1, weight=0) # Botão Cadastrar
        bottom_actions_frame.grid_columnconfigure(2, weight=0) # Botão Fechar
        bottom_actions_frame.grid_columnconfigure(3, weight=1) # Espaço à direita

        # Botão Cadastrar Despesa/Provento
        self.add_transaction_button = customtkinter.CTkButton(
            bottom_actions_frame,
            text="Cadastrar Despesa/Provento",
            font=(FONTE_FAMILIA, 13, "bold"), # Fonte igual ao Dashboard
            height=35,                        # Altura igual ao Dashboard
            corner_radius=17,                 # Raio do canto igual ao Dashboard
            fg_color="gray30",                # Cor de fundo igual ao Dashboard
            hover_color="#2196F3",            # Cor de hover igual ao Dashboard
            command=lambda: self._open_form_transacao("Despesa") # Abre como Despesa por padrão
        )
        self.add_transaction_button.grid(row=0, column=1, padx=5)

        # Botão Fechar
        close_button = customtkinter.CTkButton(bottom_actions_frame, text="Fechar", command=self._handle_close,
                                               height=30, font=(FONTE_FAMILIA, 12, "bold"),
                                               corner_radius=BOTAO_CORNER_RADIUS, fg_color="gray50", hover_color="gray40") # Movido para row=5
        close_button.grid(row=0, column=2, padx=5) # type: ignore

    def _open_categoria_detalhes_window(self, category_id, category_name, month_number, month_name):
        """Abre a janela de detalhes de transações para uma categoria específica."""
        if self.form_categoria_detalhes_window is None or not self.form_categoria_detalhes_window.winfo_exists():
            self.form_categoria_detalhes_window = FormCategoriaDetalhesTransacoesWindow(
                master=self, # Master é esta janela de DetalhesMensais
                user_id=self.current_user_id,
                year=self.selected_year,
                category_id=category_id,
                category_name=category_name,
                month_number=month_number,
                month_name=month_name
            )
            self.form_categoria_detalhes_window.focus()
        else:
            self.form_categoria_detalhes_window.focus()

    def month_detail_selected(self, month_name, year, user_id):
        month_number = self.months_list.index(month_name) + 1
        print(f"DEBUG: month_detail_selected - Mês: {month_name}, Ano: {year}, User ID: {user_id}")
        self.current_month_name_selected = month_name # Salva para recarregar

        # Limpar placeholders e conteúdo anterior
        if hasattr(self, 'right_placeholder_label') and self.right_placeholder_label.winfo_exists():
            self.right_placeholder_label.grid_forget()
        if hasattr(self, 'totals_placeholder_label') and self.totals_placeholder_label.winfo_exists():
            self.totals_placeholder_label.pack_forget()

         # Resetar o estado de ordenação ao mudar de mês
        self.despesas_sort_state = {'column': None, 'direction': 'asc'}
        self.proventos_sort_state = {'column': None, 'direction': 'asc'}
        # Limpar conteúdo anterior das tabelas de detalhes e do resumo
        for widget in self.despesas_details_scroll_frame.winfo_children():
            widget.destroy()
        for widget in self.proventos_details_scroll_frame.winfo_children():
            widget.destroy()
        for widget in self.right_summary_frame.winfo_children():
            widget.destroy()
        for widget in self.monthly_totals_display_frame.winfo_children(): # Limpa o novo frame de totais
            widget.destroy()

        self.all_transactions_for_month = get_transactions_for_month(user_id, year, month_number)
        # self.summary_title_label.configure(text=f"Resumo de {month_name}") # Título agora é fixo "Resumo por Categoria"
        self._display_month_transactions() # Popula as tabelas de Despesas e Proventos

        # Calcular Saldo em Conta (Proventos Pagos - Despesas Pagas)
        total_proventos_pagos_valor = sum(
            t['value'] for t in self.all_transactions_for_month
            if t['category_type'] == 'Provento' and t['status'] == 'Pago'
        )
        total_despesas_pagas_valor = sum(
            t['value'] for t in self.all_transactions_for_month
            if t['category_type'] == 'Despesa' and t['status'] == 'Pago'
        )
        saldo_em_conta = total_proventos_pagos_valor - total_despesas_pagas_valor
        cor_saldo_em_conta = "lightgreen" if saldo_em_conta >= 0 else "tomato"

        # Calcular Total "A Pagar" (Despesas "Em Aberto")
        total_a_pagar_valor = sum(
            t['value'] for t in self.all_transactions_for_month
            if t['category_type'] == 'Despesa' and t['status'] == 'Em Aberto'
        )

        # Calcular Totais por Meio de Pagamento
        total_cartao_credito = sum(
            t['value'] for t in self.all_transactions_for_month if t['category_type'] == 'Despesa' and t['status'] == 'Pago' and t['payment_method'] == 'Cartão de Crédito'
        )
        total_conta_corrente = sum(
            t['value'] for t in self.all_transactions_for_month if t['category_type'] == 'Despesa' and t['status'] == 'Pago' and t['payment_method'] == 'Conta Corrente'
        )

        # --- Popular Resumo (Lista de Categorias e Totais Laterais) ---
        summary_data = get_category_summary_for_month(user_id, year, month_number)
        total_despesas = 0
        total_proventos = 0

        if not summary_data:
            customtkinter.CTkLabel(self.right_summary_frame, text="Nenhum dado de resumo de categoria encontrado.", font=FONTE_LABEL_NORMAL, text_color="gray60").grid(row=0, column=0, pady=10, padx=10, sticky="nsew")
        else:
            # Frame para a lista de categorias (coluna 0 do right_summary_frame)
            # Usaremos um CTkScrollableFrame aqui para o caso de muitas categorias
            cat_summary_scroll_frame = customtkinter.CTkScrollableFrame(self.right_summary_frame, fg_color="transparent")
            cat_summary_scroll_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0) # Coluna única

            # Frame interno para o conteúdo da lista de categorias (para usar grid)
            cat_summary_frame = customtkinter.CTkFrame(cat_summary_scroll_frame, fg_color="transparent")
            cat_summary_frame.pack(fill="x", expand=True, padx=10) # pack dentro do scrollable
            cat_summary_frame.grid_columnconfigure(0, weight=1)
            cat_summary_frame.grid_columnconfigure(1, weight=1)

            customtkinter.CTkLabel(cat_summary_frame, text="Categoria", font=FONTE_LABEL_BOLD).grid(row=0, column=0, sticky="w")
            customtkinter.CTkLabel(cat_summary_frame, text="Total Mês", font=FONTE_LABEL_BOLD).grid(row=0, column=1, sticky="e")

            current_summary_row = 1 # Começa na linha 1, após os cabeçalhos
            for i, item in enumerate(sorted(summary_data, key=lambda x: x['category_name'])):
                item_text_color = "lightgreen" # Padrão para proventos
                if item['category_type'] == 'Despesa':
                    item_text_color = "tomato"
                elif item['category_type'] == 'Provento':
                    item_text_color = "lightgreen"
                
                cat_name_label = customtkinter.CTkLabel(cat_summary_frame, text=item['category_name'], font=FONTE_LABEL_NORMAL, text_color=item_text_color, cursor="hand2")
                cat_name_label.grid(row=current_summary_row, column=0, sticky="w")
                
                total_val_label = customtkinter.CTkLabel(cat_summary_frame, text=f"R$ {item['total_value']:.2f}", font=FONTE_LABEL_NORMAL, text_color=item_text_color, cursor="hand2")
                total_val_label.grid(row=current_summary_row, column=1, sticky="e")

                # Bind click para abrir detalhes da categoria
                cat_id_for_click = item['category_id']
                cat_name_for_click = item['category_name']
                
                cat_name_label.bind("<Button-1>", lambda e, cid=cat_id_for_click, cname=cat_name_for_click, mn=month_number, mname=month_name: self._open_categoria_detalhes_window(cid, cname, mn, mname))
                total_val_label.bind("<Button-1>", lambda e, cid=cat_id_for_click, cname=cat_name_for_click, mn=month_number, mname=month_name: self._open_categoria_detalhes_window(cid, cname, mn, mname))

                current_summary_row += 1

                if item['category_type'] == 'Despesa':
                    total_despesas += item['total_value']
                elif item['category_type'] == 'Provento':
                    total_proventos += item['total_value'] # type: ignore

            # Adiciona uma linha separadora antes do TOTAL
            separator = customtkinter.CTkFrame(cat_summary_frame, height=1, fg_color="gray50")
            separator.grid(row=current_summary_row, column=0, columnspan=2, sticky="ew", pady=(5,2))
            current_summary_row +=1

            # Linha de TOTAL
            grand_total_value = total_despesas # Soma apenas das despesas listadas (ou o que for apropriado para o TOTAL)
            customtkinter.CTkLabel(cat_summary_frame, text="TOTAL", font=FONTE_LABEL_NORMAL).grid(row=current_summary_row, column=0, sticky="w")
            customtkinter.CTkLabel(cat_summary_frame, text=f"R$ {grand_total_value:.2f}", font=FONTE_LABEL_NORMAL).grid(row=current_summary_row, column=1, sticky="e")
            current_summary_row +=1

        # --- Popular o self.monthly_totals_display_frame ---
        # Limpa o placeholder se ainda existir
        if hasattr(self, 'totals_placeholder_label') and self.totals_placeholder_label.winfo_exists():
            self.totals_placeholder_label.pack_forget()

         # Título para esta seção de totais
        customtkinter.CTkLabel(self.monthly_totals_display_frame, text="Totais do Mês", font=FONTE_LABEL_BOLD).pack(anchor="w", pady=(10,10), padx=10)
    
        # Total Despesas (no frame lateral)
        customtkinter.CTkLabel(self.monthly_totals_display_frame, text=f"Total Despesas: R$ {total_despesas:.2f}", font=FONTE_LABEL_NORMAL, text_color="tomato").pack(anchor="w", padx=10, pady=(0,2)) # pady reduzido
    
    
        # Total Proventos (no frame lateral)
        customtkinter.CTkLabel(self.monthly_totals_display_frame, text=f"Total Proventos: R$ {total_proventos:.2f}", font=FONTE_LABEL_NORMAL, text_color="lightgreen").pack(anchor="w", padx=10, pady=(0,2)) # pady reduzido
    
    
        # Total Cartão de Crédito (NOVO CAMPO)
        customtkinter.CTkLabel(self.monthly_totals_display_frame, text=f"Cartão Crédito: R$ {total_cartao_credito:.2f}", font=FONTE_LABEL_NORMAL, text_color="orange").pack(anchor="w", pady=(2,2), padx=10) # pady reduzido
    
        # Total Pago em Conta (NOVO CAMPO)
        customtkinter.CTkLabel(self.monthly_totals_display_frame, text=f"Pago em Conta: R$ {total_conta_corrente:.2f}", font=FONTE_LABEL_NORMAL, text_color="cyan").pack(anchor="w", pady=(2,2), padx=10) # pady reduzido
    
        # Total "A Pagar" (NOVO CAMPO)
        customtkinter.CTkLabel(self.monthly_totals_display_frame, text=f"A Pagar: R$ {total_a_pagar_valor:.2f}", font=FONTE_LABEL_NORMAL, text_color="yellow").pack(anchor="w", pady=(2,2), padx=10) # pady reduzido
    
        # Saldo em Conta (NOVO CAMPO)
        customtkinter.CTkLabel(self.monthly_totals_display_frame, text=f"Saldo em Conta: R$ {saldo_em_conta:.2f}", font=FONTE_LABEL_NORMAL, text_color=cor_saldo_em_conta).pack(anchor="w", pady=(2,2), padx=10) # pady reduzido
    
        # Saldo (no frame lateral)
        saldo = total_proventos - total_despesas
        saldo_color = "lightgreen" if saldo >=0 else "tomato"
        customtkinter.CTkLabel(self.monthly_totals_display_frame, text=f"Saldo do Mês: R$ {saldo:.2f}", font=FONTE_LABEL_NORMAL, text_color=saldo_color).pack(anchor="w", pady=(2,5), padx=10) # pady reduzido

    def _display_month_transactions(self):
        all_despesas_raw = [t for t in self.all_transactions_for_month if t['category_type'] == 'Despesa']
        proventos = [t for t in self.all_transactions_for_month if t['category_type'] == 'Provento']

        # Separar despesas fixas das normais
        despesas_fixas = []
        despesas_normais = []

        for d in all_despesas_raw:
            # Consideramos uma despesa como fixa se "(Fixo)" estiver na descrição
            if "(Fixo)" in d.get('description', ''):
                despesas_fixas.append(d)
            else:
                despesas_normais.append(d)

        # Ordenar cada lista (opcional, mas bom para consistência, por exemplo, por data de vencimento)
        despesas_fixas_sorted = sorted(despesas_fixas, key=lambda x: x.get('due_date', ''))
        despesas_normais_sorted = sorted(despesas_normais, key=lambda x: x.get('due_date', ''))

        # Concatenar, com as fixas primeiro
        despesas_final_sorted = despesas_fixas_sorted + despesas_normais_sorted

        self._populate_transaction_table(self.despesas_details_scroll_frame, despesas_final_sorted, "Despesa")
        self._populate_transaction_table(self.proventos_details_scroll_frame, proventos, "Provento")

    def _sort_table(self, event, header_text, transaction_type):
        """Chamado quando um cabeçalho de coluna é clicado para ordenar."""
        sort_state = self.despesas_sort_state if transaction_type == "Despesa" else self.proventos_sort_state

        # Se clicar na coluna que já está sendo ordenada, inverte a direção
        if sort_state['column'] == header_text:
            sort_state['direction'] = 'desc' if sort_state['direction'] == 'asc' else 'asc'
        else:
            # Se clicar em uma nova coluna, define como a coluna de ordenação e direção ascendente
            sort_state['column'] = header_text
            sort_state['direction'] = 'asc'

        print(f"DEBUG: Sorting {transaction_type} table by '{header_text}' in '{sort_state['direction']}' order.")

        # Dispara a repopulação das tabelas, que aplicará a ordenação e os filtros
        self._display_month_transactions()

    def _populate_transaction_table(self, parent_frame, transactions, transaction_type):
        # Limpa o conteúdo anterior do frame
        for widget in parent_frame.winfo_children():
            widget.destroy()

        current_sort_state = self.despesas_sort_state if transaction_type == "Despesa" else self.proventos_sort_state

        # Cabeçalhos e colunas
        col_weights = [1, 3, 2, 1, 1, 1, 1, 1, 1] 
        headers = ["Data", "Descrição", "Categoria", "V. Parcela", "V. Total", "Status", "Modalidade", "Parcela", "Forma Pag."]

        # --- Cabeçalhos da Tabela ---
        for i, header_text in enumerate(headers):
            parent_frame.grid_columnconfigure(i, weight=col_weights[i]) # Configura peso da coluna
            anchor_val = "w" if header_text in ["Descrição", "Categoria", "V. Parcela", "V. Total", "Forma Pag."] else "center"
            
            # Adiciona indicador de ordenação se esta coluna estiver sendo ordenada
            sort_indicator = ""
            if current_sort_state['column'] == header_text:
                sort_indicator = " ▲" if current_sort_state['direction'] == 'asc' else " ▼"

            # Torna o cabeçalho clicável para ordenação
            header_label = customtkinter.CTkLabel(parent_frame, text=f"{header_text}{sort_indicator}", font=FONTE_LABEL_PEQUENA, anchor=anchor_val, cursor="hand2")
            header_label.grid(row=0, column=i, sticky="ew", padx=2) # Cabeçalhos na linha 0
            header_label.bind("<Button-1>", lambda event, ht=header_text, tt=transaction_type: self._sort_table(event, ht, tt))

        # A lista de transações não é mais filtrada por texto aqui
        filtered_transactions = list(transactions) 
        
        # --- Aplicar Ordenação ---
        if current_sort_state['column']:
            sort_column = current_sort_state['column']
            sort_direction = current_sort_state['direction']
            
            # Mapeamento de cabeçalho para chave de dados e tipo para ordenação correta
            sort_key_map = {
                "Data": ('due_date', 'date'),
                "Descrição": ('description', 'string'),
                "Categoria": ('category_name', 'string'),
                "V. Parcela": ('value', 'number'),
                "V. Total": ('value', 'total_value'), # Requer cálculo do total
                "Status": ('status', 'string'),
                "Modalidade": ('modality', 'string'),
                "Parcela": ('installments', 'installment_number'), # Requer extração do número
                "Forma Pag.": ('payment_method', 'string')
            }
            
            sort_info = sort_key_map.get(sort_column)
            if sort_info:
                sort_db_key, sort_type = sort_info
                
                def get_sort_value(trans):
                    # Lógica para extrair o valor correto para ordenação com base no tipo
                    if sort_type == 'date':
                        return datetime.datetime.strptime(trans.get(sort_db_key, '1900-01-01'), "%Y-%m-%d").date() if trans.get(sort_db_key) else datetime.date.min
                    elif sort_type == 'number':
                        return trans.get(sort_db_key, 0.0)
                    elif sort_type == 'total_value':
                         return trans.get('value', 0.0) * int(trans.get('installments', '1/1').split('/')[1]) if '/' in trans.get('installments', '1/1') else trans.get('value', 0.0)
                    elif sort_type == 'installment_number':
                         return int(trans.get(sort_db_key, '0/1').split('/')[0]) if '/' in trans.get(sort_db_key, '0/1') else 0
                    return str(trans.get(sort_db_key, '')).lower() # Default para string (case-insensitive)
                
                filtered_transactions = sorted(filtered_transactions, key=get_sort_value, reverse=(sort_direction == 'desc'))

        if not transactions:
            customtkinter.CTkLabel(
                parent_frame,
                text=f"Nenhuma transação de {transaction_type.lower()} para este mês.",
                font=FONTE_LABEL_NORMAL,
                text_color="gray60"
            ).grid(row=1, column=0, columnspan=len(headers), pady=20, padx=10) # Mensagem na linha 1 (após cabeçalhos)
            return
        
        if not filtered_transactions:
            # Esta mensagem não será mais atingida se a filtragem por texto for removida.
            customtkinter.CTkLabel(parent_frame, text="Nenhuma transação para exibir.", font=FONTE_LABEL_NORMAL, text_color="gray60").grid(row=1, column=0, columnspan=len(headers), pady=20, padx=10)
            return 

        # Linhas de Transação
        for row_idx, trans in enumerate(filtered_transactions, start=1): # Dados começam na linha 1
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

            # Forma de Pagamento (NOVA COLUNA)
            payment_method_display = trans.get('payment_method', '-') if trans.get('status') == 'Pago' else '-'
            widgets.append(customtkinter.CTkLabel(
                parent_frame, text=payment_method_display, font=FONTE_LABEL_PEQUENA, anchor="w"
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
        # Notifica o Dashboard para atualizar seus dados também, usando o callback fornecido
        if self.main_dashboard_refresh_callback:
            print("DEBUG DetalhesMensais: Calling main_dashboard_refresh_callback()")
            self.main_dashboard_refresh_callback()

    def _open_consulta_transacao(self, transaction_id):
        print(f"DEBUG DetalhesMensais: Abrindo consulta para transação ID: {transaction_id}")
        if self.form_consulta_transacao_window is None or not self.form_consulta_transacao_window.winfo_exists():
            self.form_consulta_transacao_window = FormConsultaTransacaoWindow(
                master=self.winfo_toplevel(), # CHANGED: Master is now the top-level window (Dashboard)
                transaction_id=transaction_id,
                on_action_completed_callback=self._refresh_after_action # Passa o método de refresh
            )
            # Check if the window initialized successfully and still exists before focusing
            if getattr(self.form_consulta_transacao_window, '_initialization_successful', False) and \
               self.form_consulta_transacao_window.winfo_exists():
                self.form_consulta_transacao_window.focus()
            # Else: The window might be self-destructing due to initialization failure,
            # so no need to focus it. It will show an error message and close itself.
        else:
            if self.form_consulta_transacao_window.winfo_exists(): # Good to keep this check for existing windows
                self.form_consulta_transacao_window.focus() # Se a janela já existe, apenas a traz para o foco

    def _open_form_transacao(self, tipo_transacao):
        """Abre o formulário de cadastro de transação."""
        if self.form_transacao_window_ref is None or not self.form_transacao_window_ref.winfo_exists():
            self.form_transacao_window_ref = FormTransacaoWindow(
                master=self, # O master é esta janela de DetalhesMensais
                current_user_id=self.current_user_id,
                tipo_transacao=tipo_transacao,
                on_save_callback=self._refresh_after_action # Passa o método de refresh
            )
            self.form_transacao_window_ref.focus() # Traz a nova janela para o foco
        else:
            self.form_transacao_window_ref.focus() # Se a janela já existe, apenas a traz para o foco

    def _handle_close(self):
        """Chama o callback de fechamento fornecido pelo Dashboard."""
        if self.close_callback:
            self.close_callback()
        self.destroy() # Destrói este frame de detalhes

if __name__ == '__main__':
    # Para testar esta janela isoladamente
    app_root = customtkinter.CTk()
    # app_root.withdraw() # Não precisa esconder para testar um Frame
    form_detalhes = DetalhesMensaisView(master=app_root, current_user_id="test_user_01", selected_year="2024")
    form_detalhes.pack(expand=True, fill="both")
    app_root.mainloop()
