# form_detalhes_mensais.py
import customtkinter
import tkinter as tk # Para constantes de alinhamento
from Database import get_transactions_for_month, get_category_summary_for_month # Importa funções do Database

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

        # Coluna da Esquerda: Detalhamento das Transações
        self.left_detail_scroll_frame = customtkinter.CTkScrollableFrame(content_splitter_frame, label_text="Transações do Mês")
        self.left_detail_scroll_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        # Placeholder inicial
        self.left_placeholder_label = customtkinter.CTkLabel(self.left_detail_scroll_frame, text="Selecione um mês para ver as transações.", font=FONTE_LABEL_NORMAL, text_color="gray60")
        self.left_placeholder_label.pack(pady=20, padx=10)

        # Coluna da Direita: Resumo
        self.right_summary_frame = customtkinter.CTkFrame(content_splitter_frame, fg_color="gray17", corner_radius=10) # Cor de fundo para destaque
        self.right_summary_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
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
        # print(f"Detalhes solicitados para: Mês: {month_name}, Ano: {year}, Usuário ID: {user_id}") # Removido print de depuração
        month_number = self.months_list.index(month_name) + 1

        # Limpar placeholders e conteúdo anterior
        if hasattr(self, 'left_placeholder_label') and self.left_placeholder_label.winfo_exists():
            self.left_placeholder_label.pack_forget()
        if hasattr(self, 'right_placeholder_label') and self.right_placeholder_label.winfo_exists():
            self.right_placeholder_label.pack_forget()

        for widget in self.left_detail_scroll_frame.winfo_children():
            widget.destroy()
        for widget in self.right_summary_frame.winfo_children():
            widget.destroy()

        # --- Popular Coluna da Esquerda (Detalhes das Transações) ---
        transactions = get_transactions_for_month(user_id, year, month_number)
        self.left_detail_scroll_frame.configure(label_text=f"Transações de {month_name}")

        if not transactions:
            customtkinter.CTkLabel(self.left_detail_scroll_frame, text="Nenhuma transação encontrada para este mês.", font=FONTE_LABEL_NORMAL, text_color="gray60").pack(pady=20)
        else:
            # Cabeçalhos
            header_frame = customtkinter.CTkFrame(self.left_detail_scroll_frame, fg_color="transparent")
            header_frame.pack(fill="x", pady=(5,2))
            header_frame.grid_columnconfigure(0, weight=1) # Data
            header_frame.grid_columnconfigure(1, weight=3) # Descrição
            header_frame.grid_columnconfigure(2, weight=2) # Categoria
            header_frame.grid_columnconfigure(3, weight=1) # Valor
            header_frame.grid_columnconfigure(4, weight=1) # Status
            customtkinter.CTkLabel(header_frame, text="Data", font=FONTE_LABEL_BOLD).grid(row=0, column=0, sticky="w")
            customtkinter.CTkLabel(header_frame, text="Descrição", font=FONTE_LABEL_BOLD).grid(row=0, column=1, sticky="w")
            customtkinter.CTkLabel(header_frame, text="Categoria", font=FONTE_LABEL_BOLD).grid(row=0, column=2, sticky="w")
            customtkinter.CTkLabel(header_frame, text="Valor", font=FONTE_LABEL_BOLD).grid(row=0, column=3, sticky="e")
            customtkinter.CTkLabel(header_frame, text="Status", font=FONTE_LABEL_BOLD).grid(row=0, column=4, sticky="w", padx=2) # Adicionado padx

            for trans in transactions:
                # Definir cores com base no tipo de transação
                row_frame_fg_color = "gray10" # Cor de fundo padrão para tipos desconhecidos
                text_color_val = "white"      # Cor de texto padrão para valor

                if trans['category_type'] == 'Provento':
                    row_frame_fg_color = "transparent"
                    text_color_val = "green"
                elif trans['category_type'] == 'Despesa':
                    row_frame_fg_color = "gray25" # Um pouco mais claro que gray20 para melhor distinção
                    text_color_val = "white"
                else:
                    # Log para tipos de categoria inesperados
                    print(f"DEBUG: Tipo de categoria desconhecido encontrado: {trans['category_type']} para descrição: {trans['description']}")
                    # Mantém row_frame_fg_color="gray10" e text_color_val="white" como padrão

                row_frame = customtkinter.CTkFrame(self.left_detail_scroll_frame, fg_color=row_frame_fg_color, corner_radius=3)
                row_frame.pack(fill="x", pady=1, padx=2)
                row_frame.grid_columnconfigure(0, weight=1)
                row_frame.grid_columnconfigure(1, weight=3)
                row_frame.grid_columnconfigure(2, weight=2)
                row_frame.grid_columnconfigure(3, weight=1)
                row_frame.grid_columnconfigure(4, weight=1)

                due_date_formatted = trans['due_date'] # Manter formato YYYY-MM-DD ou formatar se necessário
                customtkinter.CTkLabel(row_frame, text=due_date_formatted, font=FONTE_LABEL_PEQUENA).grid(row=0, column=0, sticky="w", padx=2)
                customtkinter.CTkLabel(row_frame, text=trans['description'], font=FONTE_LABEL_PEQUENA, anchor="w").grid(row=0, column=1, sticky="ew", padx=2)
                cat_label = customtkinter.CTkLabel(row_frame, text=trans['category_name'], font=FONTE_LABEL_PEQUENA, fg_color=trans['category_color'], corner_radius=3, padx=3)
                cat_label.grid(row=0, column=2, sticky="w", padx=2)

                customtkinter.CTkLabel(row_frame, text=f"R$ {trans['value']:.2f}", font=FONTE_LABEL_PEQUENA, text_color=text_color_val).grid(row=0, column=3, sticky="e", padx=2)
                customtkinter.CTkLabel(row_frame, text=trans['status'], font=FONTE_LABEL_PEQUENA).grid(row=0, column=4, sticky="w", padx=2)

        # --- Popular Coluna da Direita (Resumo) ---
        summary_data = get_category_summary_for_month(user_id, year, month_number)
        total_despesas = 0
        total_proventos = 0

        customtkinter.CTkLabel(self.right_summary_frame, text=f"Resumo de {month_name}", font=FONTE_LABEL_BOLD).pack(pady=10)

        if not summary_data:
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
        customtkinter.CTkLabel(totals_frame, text=f"Total Despesas: R$ {total_despesas:.2f}", font=FONTE_LABEL_BOLD, text_color="tomato").pack(anchor="w")
        customtkinter.CTkLabel(totals_frame, text=f"Total Proventos: R$ {total_proventos:.2f}", font=FONTE_LABEL_BOLD, text_color="lightgreen").pack(anchor="w")
        saldo = total_proventos - total_despesas
        saldo_color = "lightgreen" if saldo >=0 else "tomato"
        customtkinter.CTkLabel(totals_frame, text=f"Saldo do Mês: R$ {saldo:.2f}", font=FONTE_LABEL_BOLD, text_color=saldo_color).pack(anchor="w", pady=(5,0))

if __name__ == '__main__':
    # Para testar esta janela isoladamente
    app_root = customtkinter.CTk()
    app_root.withdraw() # Esconde a janela root principal
    form_detalhes = FormDetalhesMensaisWindow(master=app_root, current_user_id="test_user_01", selected_year="2024")
    app_root.mainloop()