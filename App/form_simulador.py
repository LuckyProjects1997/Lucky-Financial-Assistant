# form_simulador.py
import customtkinter
import datetime
from collections import defaultdict

# Definições de fonte (similares ao form_planejamento)
FONTE_FAMILIA = "Segoe UI"
FONTE_TITULO_FORM = (FONTE_FAMILIA, 18, "bold")
FONTE_LABEL_NORMAL = (FONTE_FAMILIA, 12)
FONTE_LABEL_BOLD = (FONTE_FAMILIA, 12, "bold")
FONTE_LABEL_PEQUENA = (FONTE_FAMILIA, 10)
BOTAO_CORNER_RADIUS = 10
BOTAO_FG_COLOR = "gray25"
BOTAO_HOVER_COLOR = "#2E8B57"
BOTAO_HEIGHT = 40

class FormSimuladorWindow(customtkinter.CTkToplevel):
    def __init__(self, master, user_id, selected_year, selected_month_name, despesas_do_mes, proventos_do_mes):
        super().__init__(master)
        self.title(f"Simulador de Alocação - {selected_month_name}/{selected_year}")
        self.geometry("900x650") # Ajustar tamanho conforme necessário
        self.configure(fg_color="#1c1c1c")
        self.lift()
        self.attributes("-topmost", True)
        self.grab_set()

        self.user_id = user_id
        self.selected_year = selected_year
        self.selected_month_name = selected_month_name
        
        # Faz cópias profundas para não alterar os dados originais do form_planejamento
        self.despesas_originais = [dict(d) for d in despesas_do_mes]
        self.proventos_originais = [dict(p) for p in proventos_do_mes]

        # Dicionários para armazenar os resultados da simulação
        self.sugestoes_alocacao = [] # Lista de tuplas (despesa_obj, provento_sugerido_obj)
        self.despesas_nao_alocadas = [] # Lista de despesas_obj
        self.saldos_simulados_proventos = {} # {provento_id: saldo_simulado}

        self._setup_ui()
        self._run_simulation()
        self._display_results()

    def _setup_ui(self):
        main_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1) # Coluna para sugestões
        main_frame.grid_columnconfigure(1, weight=1) # Coluna para resumo dos proventos
        main_frame.grid_rowconfigure(0, weight=0) # Título
        main_frame.grid_rowconfigure(1, weight=1) # Conteúdo (sugestões e resumo)
        main_frame.grid_rowconfigure(2, weight=0) # Botões

        title_label = customtkinter.CTkLabel(main_frame, text=f"Sugestão de Alocação para {self.selected_month_name}/{self.selected_year}", font=FONTE_TITULO_FORM)
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 15), sticky="ew")

        # --- Painel de Sugestões de Alocação (Esquerda) ---
        sugestoes_frame_container = customtkinter.CTkFrame(main_frame, fg_color="gray17", corner_radius=8)
        sugestoes_frame_container.grid(row=1, column=0, sticky="nsew", padx=(0, 5), pady=5)
        sugestoes_frame_container.grid_columnconfigure(0, weight=1)
        sugestoes_frame_container.grid_rowconfigure(0, weight=0) # Título
        sugestoes_frame_container.grid_rowconfigure(1, weight=1) # Scrollable Frame

        sugestoes_title = customtkinter.CTkLabel(sugestoes_frame_container, text="Despesas Pendentes (Simulação):", font=FONTE_LABEL_BOLD)
        sugestoes_title.grid(row=0, column=0, padx=10, pady=(10,5), sticky="w")
        
        self.sugestoes_scroll_frame = customtkinter.CTkScrollableFrame(sugestoes_frame_container, fg_color="transparent")
        self.sugestoes_scroll_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.sugestoes_scroll_frame.grid_columnconfigure(0, weight=1)


        # --- Painel de Resumo dos Proventos Pós-Simulação (Direita) ---
        resumo_proventos_container = customtkinter.CTkFrame(main_frame, fg_color="gray17", corner_radius=8)
        resumo_proventos_container.grid(row=1, column=1, sticky="nsew", padx=(5, 0), pady=5)
        resumo_proventos_container.grid_columnconfigure(0, weight=1)
        resumo_proventos_container.grid_rowconfigure(0, weight=0) # Título
        resumo_proventos_container.grid_rowconfigure(1, weight=1) # Scrollable Frame

        resumo_title = customtkinter.CTkLabel(resumo_proventos_container, text="Alocação Detalhada por Provento (Simulação):", font=FONTE_LABEL_BOLD)
        resumo_title.grid(row=0, column=0, padx=10, pady=(10,5), sticky="w")

        self.resumo_proventos_scroll_frame = customtkinter.CTkScrollableFrame(resumo_proventos_container, fg_color="transparent")
        self.resumo_proventos_scroll_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.resumo_proventos_scroll_frame.grid_columnconfigure(0, weight=1)

        # --- Botões ---
        buttons_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.grid(row=2, column=0, columnspan=2, pady=(15,0), sticky="ew")
        buttons_frame.grid_columnconfigure(0, weight=1) # Para centralizar o botão

        close_button = customtkinter.CTkButton(buttons_frame, text="Fechar", command=self.destroy,
                                               height=BOTAO_HEIGHT, font=(FONTE_FAMILIA, 13, "bold"),
                                               corner_radius=BOTAO_CORNER_RADIUS, fg_color="gray50", hover_color="gray40")
        close_button.grid(row=0, column=0, pady=5)

    def _get_provento_availability_date(self, provento):
        """Retorna a data em que o provento se torna disponível (objeto date)."""
        date_str = provento.get('payment_date') if provento.get('status') == 'Pago' else provento.get('due_date')
        if date_str:
            return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        return datetime.date.max # Se não houver data, considera como nunca disponível

    def _run_simulation(self):
        print("--- Iniciando Simulação de Alocação (Estratégia Maior Saldo Restante) ---")
        # Inicializar saldos simulados com os valores originais dos proventos
        saldos_proventos_simulados = {p['id']: p['value'] for p in self.proventos_originais}

        # Ordenar despesas por data de vencimento
        despesas_ordenadas = sorted(self.despesas_originais, key=lambda d: datetime.datetime.strptime(d['due_date'], "%Y-%m-%d").date())
        
        # Ordenar proventos por data de disponibilidade (e status 'Pago' primeiro)
        # Não pré-ordenamos mais os proventos aqui, a seleção será dinâmica.
        
        print(f"Total de despesas para simular: {len(despesas_ordenadas)}")
        print(f"Total de proventos disponíveis (antes da simulação): {len(self.proventos_originais)}")

        self.sugestoes_alocacao = [] # Limpa sugestões anteriores
        self.despesas_nao_alocadas = [] # Limpa despesas não alocadas anteriores

        for despesa in despesas_ordenadas:
            despesa_vencimento = datetime.datetime.strptime(despesa['due_date'], "%Y-%m-%d").date()
            despesa_valor = despesa['value']
            alocado = False

            print(f"\nProcessando Despesa: {despesa['description']} (Venc: {despesa_vencimento}, Valor: {despesa_valor:.2f})")

            candidatos_proventos = []
            for provento in self.proventos_originais: # Iterar sobre a lista original de proventos
                provento_id = provento['id']
                provento_disponibilidade = self._get_provento_availability_date(provento)
                saldo_atual_provento = saldos_proventos_simulados.get(provento_id, 0)

                # Critério 1: Data de disponibilidade do provento <= Vencimento da despesa
                # Critério 2: Saldo do provento >= Valor da despesa
                if provento_disponibilidade <= despesa_vencimento and saldo_atual_provento >= despesa_valor:
                    candidatos_proventos.append(dict(provento)) # Adiciona uma cópia
            
            print(f"  Proventos candidatos para '{despesa['description']}': {len(candidatos_proventos)}")

            if candidatos_proventos:
                # Estratégia de seleção:
                # 1. Maior saldo restante no provento após alocação.
                # 2. Desempate 1: Priorizar status 'Pago'.
                # 3. Desempate 2: Data de disponibilidade mais antiga.
                
                melhor_provento_para_alocar = None
                maior_saldo_restante_calculado = -float('inf') # Começa com o menor valor possível
                status_do_melhor_provento = "" 
                data_disponibilidade_do_melhor_provento = datetime.date.max

                for candidato in candidatos_proventos:
                    saldo_candidato_simulado = saldos_proventos_simulados.get(candidato['id'], 0)
                    saldo_apos_alocacao = saldo_candidato_simulado - despesa_valor
                    status_candidato = candidato.get('status', 'Em Aberto')
                    data_disponibilidade_candidato = self._get_provento_availability_date(candidato)

                    if melhor_provento_para_alocar is None: # Primeiro candidato elegível
                        melhor_provento_para_alocar = candidato
                        maior_saldo_restante_calculado = saldo_apos_alocacao
                        status_do_melhor_provento = status_candidato
                        data_disponibilidade_do_melhor_provento = data_disponibilidade_candidato
                    else:
                        # Critério principal: Maior saldo restante
                        if saldo_apos_alocacao > maior_saldo_restante_calculado:
                            melhor_provento_para_alocar = candidato
                            maior_saldo_restante_calculado = saldo_apos_alocacao
                            status_do_melhor_provento = status_candidato
                            data_disponibilidade_do_melhor_provento = data_disponibilidade_candidato
                        elif saldo_apos_alocacao == maior_saldo_restante_calculado:
                            # Desempate 1: Status 'Pago'
                            candidato_e_pago = (status_candidato == 'Pago')
                            melhor_atual_e_pago = (status_do_melhor_provento == 'Pago')

                            if candidato_e_pago and not melhor_atual_e_pago:
                                melhor_provento_para_alocar = candidato
                                status_do_melhor_provento = status_candidato
                                data_disponibilidade_do_melhor_provento = data_disponibilidade_candidato
                            elif not candidato_e_pago and melhor_atual_e_pago:
                                pass # Mantém o atual que é pago
                            else: # Ambos pagos ou ambos não pagos, vamos para o próximo desempate
                                # Desempate 2: Data de disponibilidade mais antiga
                                if data_disponibilidade_candidato < data_disponibilidade_do_melhor_provento:
                                    melhor_provento_para_alocar = candidato
                                    data_disponibilidade_do_melhor_provento = data_disponibilidade_candidato
                
                if melhor_provento_para_alocar:
                    provento_id_escolhido = melhor_provento_para_alocar['id']
                    saldos_proventos_simulados[provento_id_escolhido] -= despesa_valor
                    self.sugestoes_alocacao.append((despesa, melhor_provento_para_alocar))
                    alocado = True
                    print(f"  ALOCADA (Estratégia Maior Saldo Restante): Despesa '{despesa['description']}' ao Provento '{melhor_provento_para_alocar['description']}'. Saldo provento restante: {saldos_proventos_simulados[provento_id_escolhido]:.2f}")
                    
            if not alocado:
                self.despesas_nao_alocadas.append(despesa)
                print(f"  NÃO ALOCADA: Despesa '{despesa['description']}'")
        
        self.saldos_simulados_proventos = saldos_proventos_simulados
        print("--- Simulação Concluída ---")

    def _display_results(self):
        # Limpar frames
        # --- Painel Esquerdo: Despesas Não Alocadas ---
        # Limpa o frame de sugestões (painel esquerdo)
        for widget in self.sugestoes_scroll_frame.winfo_children():
            widget.destroy()
        # Limpa o frame de resumo dos proventos (painel direito)
        for widget in self.resumo_proventos_scroll_frame.winfo_children():
            widget.destroy()

        if self.despesas_nao_alocadas:
            # O título já foi definido no _setup_ui
            for despesa in self.despesas_nao_alocadas:
                venc_fmt = datetime.datetime.strptime(despesa['due_date'], "%Y-%m-%d").strftime("%d/%m")
                desc_text = f"- {despesa['description']} (V:{venc_fmt}, R$ {despesa['value']:.2f})"
                customtkinter.CTkLabel(self.sugestoes_scroll_frame, text=desc_text, font=FONTE_LABEL_PEQUENA, text_color="yellow", anchor="w").pack(fill="x", padx=10, pady=1)
        elif self.sugestoes_alocacao: # Se não há não alocadas, MAS HÁ sugestões (que estarão no painel direito)
            customtkinter.CTkLabel(self.sugestoes_scroll_frame, text="Todas as despesas foram sugeridas\npara alocação (ver painel à direita).\nNão há despesas pendentes nesta simulação.", font=FONTE_LABEL_NORMAL, text_color="gray60").pack(pady=10, padx=5)
        else: # Nem não alocadas, nem sugestões (tudo vazio ou nenhuma despesa/provento original)
            if not self.proventos_originais and not self.despesas_originais:
                 customtkinter.CTkLabel(self.sugestoes_scroll_frame, text="Nenhuma despesa ou provento\npara simular.", font=FONTE_LABEL_NORMAL, text_color="gray60").pack(pady=10)
            else: # Há proventos/despesas, mas a simulação não resultou em nada
                 customtkinter.CTkLabel(self.sugestoes_scroll_frame, text="Simulação não produziu alocações\n ou despesas pendentes.", font=FONTE_LABEL_NORMAL, text_color="gray60").pack(pady=10, padx=5)


        # --- Painel Direito: Detalhes da Alocação por Provento ---
        if not self.proventos_originais:
            customtkinter.CTkLabel(self.resumo_proventos_scroll_frame, text="Nenhum provento cadastrado para simulação.", font=FONTE_LABEL_NORMAL, text_color="gray60").pack(pady=10)
            return

        # Agrupar despesas alocadas por ID do provento sugerido
        provento_id_para_despesas_sugeridas = defaultdict(list)
        for despesa, provento_sugerido in self.sugestoes_alocacao:
            provento_id_para_despesas_sugeridas[provento_sugerido['id']].append(despesa)

        alguma_alocacao_exibida_no_painel_direito = False

        for provento in sorted(self.proventos_originais, key=lambda p: self._get_provento_availability_date(p)):
            provento_id = provento['id']
            valor_original = provento['value']
            despesas_alocadas_a_este_provento = provento_id_para_despesas_sugeridas.get(provento_id, [])
            
            if not despesas_alocadas_a_este_provento:
                continue # Pula para o próximo provento se não houver despesas alocadas a este

            alguma_alocacao_exibida_no_painel_direito = True
            
            # Frame para cada provento e suas despesas
            frame_provento_detalhe = customtkinter.CTkFrame(self.resumo_proventos_scroll_frame, fg_color="gray22", corner_radius=8, border_width=1, border_color="gray30")
            frame_provento_detalhe.pack(fill="x", pady=5, padx=5)
            
            # Título do Provento
            titulo_provento_texto = f"{provento['description']} (Original: R$ {valor_original:.2f})"
            customtkinter.CTkLabel(frame_provento_detalhe, text=titulo_provento_texto, font=FONTE_LABEL_BOLD, text_color="lightgreen", anchor="w").pack(fill="x", padx=10, pady=(5,3))

            # Listar Despesas Alocadas
            total_alocado_neste_provento = 0
            for despesa_alocada in sorted(despesas_alocadas_a_este_provento, key=lambda d: datetime.datetime.strptime(d['due_date'], "%Y-%m-%d").date()):
                venc_fmt = datetime.datetime.strptime(despesa_alocada['due_date'], "%Y-%m-%d").strftime("%d/%m")
                despesa_texto = f"  - {despesa_alocada['description']} (V: {venc_fmt}, R$ {despesa_alocada['value']:.2f})"
                customtkinter.CTkLabel(frame_provento_detalhe, text=despesa_texto, font=FONTE_LABEL_PEQUENA, text_color="tomato", anchor="w").pack(fill="x", padx=15, pady=1)
                total_alocado_neste_provento += despesa_alocada['value']
            
            # Separador
            customtkinter.CTkFrame(frame_provento_detalhe, height=1, fg_color="gray40").pack(fill="x", padx=10, pady=(5,3))

            # Total Alocado e Saldo Restante para este Provento
            saldo_restante_provento = self.saldos_simulados_proventos.get(provento_id, valor_original) # Pega o saldo final simulado
            
            customtkinter.CTkLabel(frame_provento_detalhe, text=f"Total Alocado neste Provento: R$ {total_alocado_neste_provento:.2f}", font=FONTE_LABEL_NORMAL, text_color="orange", anchor="w").pack(fill="x", padx=10, pady=(2,1))
            
            cor_saldo_final = "lightgreen" if saldo_restante_provento >= 0 else "tomato"
            customtkinter.CTkLabel(frame_provento_detalhe, text=f"Saldo Restante do Provento: R$ {saldo_restante_provento:.2f}", font=FONTE_LABEL_NORMAL, text_color=cor_saldo_final, anchor="w").pack(fill="x", padx=10, pady=(1,5))

        if not alguma_alocacao_exibida_no_painel_direito and self.proventos_originais:
            customtkinter.CTkLabel(self.resumo_proventos_scroll_frame, text="Nenhuma despesa pôde ser alocada aos proventos\ndisponíveis com base na simulação.", font=FONTE_LABEL_NORMAL, text_color="gray60").pack(pady=10)
        elif not self.proventos_originais and self.despesas_originais:
             customtkinter.CTkLabel(self.resumo_proventos_scroll_frame, text="Não há proventos para alocar as despesas.", font=FONTE_LABEL_NORMAL, text_color="gray60").pack(pady=10)
