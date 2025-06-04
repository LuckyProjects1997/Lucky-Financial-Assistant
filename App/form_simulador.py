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

        sugestoes_title = customtkinter.CTkLabel(sugestoes_frame_container, text="Alocações Sugeridas:", font=FONTE_LABEL_BOLD)
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

        resumo_title = customtkinter.CTkLabel(resumo_proventos_container, text="Saldos Simulados dos Proventos:", font=FONTE_LABEL_BOLD)
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
        print("--- Iniciando Simulação de Alocação ---")
        # Inicializar saldos simulados com os valores originais dos proventos
        saldos_proventos_simulados = {p['id']: p['value'] for p in self.proventos_originais}

        # Ordenar despesas por data de vencimento
        despesas_ordenadas = sorted(self.despesas_originais, key=lambda d: datetime.datetime.strptime(d['due_date'], "%Y-%m-%d").date())
        
        # Ordenar proventos por data de disponibilidade (e status 'Pago' primeiro)
        proventos_ordenados = sorted(
            self.proventos_originais,
            key=lambda p: (
                0 if p.get('status') == 'Pago' else 1, # Pagos primeiro
                self._get_provento_availability_date(p)
            )
        )
        
        print(f"Total de despesas para simular: {len(despesas_ordenadas)}")
        print(f"Total de proventos disponíveis: {len(proventos_ordenados)}")

        for despesa in despesas_ordenadas:
            despesa_vencimento = datetime.datetime.strptime(despesa['due_date'], "%Y-%m-%d").date()
            despesa_valor = despesa['value']
            alocado = False

            print(f"\nProcessando Despesa: {despesa['description']} (Venc: {despesa_vencimento}, Valor: {despesa_valor:.2f})")

            candidatos_proventos = []
            for provento in proventos_ordenados:
                provento_id = provento['id']
                provento_disponibilidade = self._get_provento_availability_date(provento)
                saldo_atual_provento = saldos_proventos_simulados.get(provento_id, 0)

                # Critério 1: Data de disponibilidade do provento <= Vencimento da despesa
                # Critério 2: Saldo do provento >= Valor da despesa
                if provento_disponibilidade <= despesa_vencimento and saldo_atual_provento >= despesa_valor:
                    candidatos_proventos.append(provento)
            
            print(f"  Proventos candidatos para '{despesa['description']}': {len(candidatos_proventos)}")

            if candidatos_proventos:
                # Estratégia de seleção:
                # 1. Priorizar pagos
                # 2. Menor saldo positivo restante após alocação
                # 3. (Desempate) Data de disponibilidade mais próxima
                
                melhor_provento = None
                menor_saldo_restante_apos_alocacao = float('inf')

                for candidato in candidatos_proventos:
                    saldo_candidato = saldos_proventos_simulados.get(candidato['id'], 0)
                    saldo_apos = saldo_candidato - despesa_valor
                    
                    # Lógica de priorização e desempate
                    if melhor_provento is None:
                        melhor_provento = candidato
                        menor_saldo_restante_apos_alocacao = saldo_apos
                    else:
                        # Prioriza pagos
                        candidato_pago = candidato.get('status') == 'Pago'
                        melhor_pago = melhor_provento.get('status') == 'Pago'

                        if candidato_pago and not melhor_pago:
                            melhor_provento = candidato
                            menor_saldo_restante_apos_alocacao = saldo_apos
                        elif not candidato_pago and melhor_pago:
                            continue # Mantém o melhor_provento atual (que é pago)
                        else: # Ambos pagos ou ambos não pagos
                            if saldo_apos < menor_saldo_restante_apos_alocacao:
                                melhor_provento = candidato
                                menor_saldo_restante_apos_alocacao = saldo_apos
                            elif saldo_apos == menor_saldo_restante_apos_alocacao:
                                # Desempate: data de disponibilidade mais próxima
                                data_candidato = self._get_provento_availability_date(candidato)
                                data_melhor = self._get_provento_availability_date(melhor_provento)
                                if data_candidato > data_melhor: # Queremos a data mais próxima, então a maior data que ainda é <= vencimento
                                    melhor_provento = candidato
                                    # menor_saldo_restante_apos_alocacao não muda
                
                if melhor_provento:
                    provento_id_escolhido = melhor_provento['id']
                    saldos_proventos_simulados[provento_id_escolhido] -= despesa_valor
                    self.sugestoes_alocacao.append((despesa, melhor_provento))
                    alocado = True
                    print(f"  ALOCADA: Despesa '{despesa['description']}' ao Provento '{melhor_provento['description']}'. Saldo provento restante: {saldos_proventos_simulados[provento_id_escolhido]:.2f}")

            if not alocado:
                self.despesas_nao_alocadas.append(despesa)
                print(f"  NÃO ALOCADA: Despesa '{despesa['description']}'")
        
        self.saldos_simulados_proventos = saldos_proventos_simulados
        print("--- Simulação Concluída ---")

    def _display_results(self):
        # Limpar frames
        for widget in self.sugestoes_scroll_frame.winfo_children():
            widget.destroy()
        for widget in self.resumo_proventos_scroll_frame.winfo_children():
            widget.destroy()

        # Exibir Sugestões de Alocação
        if not self.sugestoes_alocacao and not self.despesas_nao_alocadas:
             customtkinter.CTkLabel(self.sugestoes_scroll_frame, text="Nenhuma despesa ou provento para simular.", font=FONTE_LABEL_NORMAL, text_color="gray60").pack(pady=10)
        
        for despesa, provento_sugerido in self.sugestoes_alocacao:
            frame_sugestao = customtkinter.CTkFrame(self.sugestoes_scroll_frame, fg_color="gray22", corner_radius=6)
            frame_sugestao.pack(fill="x", pady=3, padx=5)
            
            venc_fmt = datetime.datetime.strptime(despesa['due_date'], "%Y-%m-%d").strftime("%d/%m")
            desc_text = f"Despesa: {despesa['description']} (V:{venc_fmt}, R$ {despesa['value']:.2f})"
            customtkinter.CTkLabel(frame_sugestao, text=desc_text, font=FONTE_LABEL_PEQUENA, text_color="tomato", anchor="w").pack(fill="x", padx=5, pady=(3,0))
            
            prov_disp_fmt = self._get_provento_availability_date(provento_sugerido).strftime("%d/%m")
            sug_text = f"  ↳ Pagar com: {provento_sugerido['description']} (Disp:{prov_disp_fmt}, R$ {provento_sugerido['value']:.2f})"
            customtkinter.CTkLabel(frame_sugestao, text=sug_text, font=FONTE_LABEL_PEQUENA, text_color="lightgreen", anchor="w").pack(fill="x", padx=10, pady=(0,3))

        if self.despesas_nao_alocadas:
            customtkinter.CTkLabel(self.sugestoes_scroll_frame, text="Despesas Não Alocadas:", font=FONTE_LABEL_BOLD, text_color="orange").pack(pady=(10,2), anchor="w", padx=5)
            for despesa in self.despesas_nao_alocadas:
                venc_fmt = datetime.datetime.strptime(despesa['due_date'], "%Y-%m-%d").strftime("%d/%m")
                desc_text = f"- {despesa['description']} (V:{venc_fmt}, R$ {despesa['value']:.2f})"
                customtkinter.CTkLabel(self.sugestoes_scroll_frame, text=desc_text, font=FONTE_LABEL_PEQUENA, text_color="yellow", anchor="w").pack(fill="x", padx=10, pady=1)

        # Exibir Resumo dos Proventos Pós-Simulação
        if not self.proventos_originais:
            customtkinter.CTkLabel(self.resumo_proventos_scroll_frame, text="Nenhum provento cadastrado.", font=FONTE_LABEL_NORMAL, text_color="gray60").pack(pady=10)

        for provento in self.proventos_originais: # Iterar sobre os originais para manter a ordem e todos eles
            provento_id = provento['id']
            valor_original = provento['value']
            saldo_simulado = self.saldos_simulados_proventos.get(provento_id, valor_original) # Pega o simulado, ou original se não foi tocado
            usado_simulado = valor_original - saldo_simulado

            frame_resumo = customtkinter.CTkFrame(self.resumo_proventos_scroll_frame, fg_color="gray22", corner_radius=6)
            frame_resumo.pack(fill="x", pady=3, padx=5)
            frame_resumo.grid_columnconfigure(0, weight=2) # Descrição
            frame_resumo.grid_columnconfigure(1, weight=1) # Original
            frame_resumo.grid_columnconfigure(2, weight=1) # Usado
            frame_resumo.grid_columnconfigure(3, weight=1) # Saldo Sim.

            customtkinter.CTkLabel(frame_resumo, text=provento['description'], font=FONTE_LABEL_PEQUENA, anchor="w").grid(row=0, column=0, sticky="w", padx=5)
            customtkinter.CTkLabel(frame_resumo, text=f"R$ {valor_original:.2f}", font=FONTE_LABEL_PEQUENA, anchor="e").grid(row=0, column=1, sticky="ew", padx=5)
            customtkinter.CTkLabel(frame_resumo, text=f"R$ {usado_simulado:.2f}", font=FONTE_LABEL_PEQUENA, text_color="orange", anchor="e").grid(row=0, column=2, sticky="ew", padx=5)
            
            cor_saldo_sim = "lightgreen" if saldo_simulado >= 0 else "tomato"
            customtkinter.CTkLabel(frame_resumo, text=f"R$ {saldo_simulado:.2f}", font=FONTE_LABEL_PEQUENA, text_color=cor_saldo_sim, anchor="e").grid(row=0, column=3, sticky="ew", padx=5)

