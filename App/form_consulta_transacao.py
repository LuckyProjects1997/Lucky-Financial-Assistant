# form_consulta_transacao.py
import customtkinter
import datetime
import Database
from CTkMessagebox import CTkMessagebox

# Definições de fonte padrão
FONTE_FAMILIA = "Segoe UI"
FONTE_TITULO_FORM = (FONTE_FAMILIA, 18, "bold")
FONTE_LABEL_FORM = (FONTE_FAMILIA, 13)
FONTE_VALOR_FORM = (FONTE_FAMILIA, 13)
FONTE_BOTAO_FORM = (FONTE_FAMILIA, 13, "bold")
BOTAO_CORNER_RADIUS = 17
BOTAO_FG_COLOR = "gray30"
BOTAO_HOVER_COLOR = "#2196F3"
BOTAO_HEIGHT = 35

class FormConsultaTransacaoWindow(customtkinter.CTkToplevel):
    def __init__(self, master=None, transaction_id=None, on_save_callback=None):
        super().__init__(master)
        self.title("Consulta de Transação")
        self.geometry("450x600")
        self.configure(fg_color="#1c1c1c")
        self.lift()
        self.attributes("-topmost", True)
        self.grab_set()

        self.transaction_id = transaction_id
        self.on_save_callback = on_save_callback
        self.transaction_data = None
        self.is_editing = False

        self.entry_widgets = {} # Para armazenar referências aos campos de entrada
        self.category_combobox = None
        self.status_var = customtkinter.StringVar()

        self._load_transaction_data()
        self._setup_ui()

    def _load_transaction_data(self):
        if self.transaction_id:
            self.transaction_data = Database.get_transaction_by_id(self.transaction_id)
        if not self.transaction_data:
            CTkMessagebox(title="Erro", message="Não foi possível carregar os dados da transação.", icon="cancel", master=self)
            self.after(100, self.destroy) # Fecha a janela após um pequeno delay

    def _setup_ui(self):
        if not self.transaction_data:
            return

        main_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        fields = [
            ("ID:", self.transaction_data.get("id", "N/A"), "id_val", False),
            ("Descrição:", self.transaction_data.get("description", "N/A"), "description", True),
            ("Data do Lançamento:", self.transaction_data.get("launch_date", "N/A"), "launch_date_val", False),
            ("Valor (R$):", f"{self.transaction_data.get('value', 0.0):.2f}", "value", True),
            ("Modalidade:", self.transaction_data.get("modality", "N/A"), "modality_val", False),
            ("Parcela:", self.transaction_data.get("installments", "N/A"), "installments_val", False),
            ("Categoria:", self.transaction_data.get("category_name", "N/A"), "category_id", True), # Será um ComboBox
            ("Status:", self.transaction_data.get("status", "N/A"), "status", True), # Será RadioButton
            ("Data Prevista:", self.transaction_data.get("due_date", "N/A"), "due_date", True),
            ("Data Pagamento:", self.transaction_data.get("payment_date", "") or "N/A", "payment_date", True),
        ]

        for i, (label_text, value_text, key, editable) in enumerate(fields):
            customtkinter.CTkLabel(main_frame, text=label_text, font=FONTE_LABEL_FORM, anchor="w").grid(row=i, column=0, sticky="w", padx=5, pady=(5,2))
            
            if key == "category_id":
                categories = Database.get_categories_by_user(self.transaction_data.get("user_id"))
                category_names = [cat['name'] for cat in categories]
                self.category_combobox = customtkinter.CTkComboBox(main_frame, values=category_names, font=FONTE_VALOR_FORM, state="disabled", height=BOTAO_HEIGHT)
                self.category_combobox.set(value_text) # Define o nome da categoria atual
                self.category_combobox.grid(row=i, column=1, sticky="ew", padx=5, pady=(5,2))
                self.entry_widgets[key] = self.category_combobox
            elif key == "status":
                self.status_var.set(value_text)
                status_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
                status_frame.grid(row=i, column=1, sticky="ew", padx=5, pady=(5,2))
                radio_aberto = customtkinter.CTkRadioButton(status_frame, text="Em Aberto", variable=self.status_var, value="Em Aberto", font=FONTE_LABEL_FORM, state="disabled")
                radio_aberto.pack(side="left", padx=(0,10))
                radio_pago = customtkinter.CTkRadioButton(status_frame, text="Pago", variable=self.status_var, value="Pago", font=FONTE_LABEL_FORM, state="disabled")
                radio_pago.pack(side="left")
                self.entry_widgets[key] = {"var": self.status_var, "radios": [radio_aberto, radio_pago]}
            else:
                entry = customtkinter.CTkEntry(main_frame, font=FONTE_VALOR_FORM, state="disabled", height=BOTAO_HEIGHT)
                entry.insert(0, str(value_text))
                entry.grid(row=i, column=1, sticky="ew", padx=5, pady=(5,2))
                if editable: # Apenas armazena os que podem ser editados
                    self.entry_widgets[key] = entry

        # Botões
        buttons_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.grid(row=len(fields), column=0, columnspan=2, pady=(20,10), sticky="ew")
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)

        self.edit_button = customtkinter.CTkButton(buttons_frame, text="Editar", command=self._toggle_edit_mode,
                                                   height=BOTAO_HEIGHT, font=FONTE_BOTAO_FORM, corner_radius=BOTAO_CORNER_RADIUS,
                                                   fg_color=BOTAO_FG_COLOR, hover_color=BOTAO_HOVER_COLOR)
        self.edit_button.grid(row=0, column=0, padx=5, sticky="e")

        self.save_button = customtkinter.CTkButton(buttons_frame, text="Salvar", command=self._save_changes,
                                                   height=BOTAO_HEIGHT, font=FONTE_BOTAO_FORM, corner_radius=BOTAO_CORNER_RADIUS,
                                                   fg_color="green", hover_color="darkgreen", state="disabled")
        self.save_button.grid(row=0, column=1, padx=5, sticky="w")

        close_button = customtkinter.CTkButton(buttons_frame, text="Fechar", command=self.destroy,
                                                height=BOTAO_HEIGHT, font=FONTE_BOTAO_FORM, corner_radius=BOTAO_CORNER_RADIUS,
                                                fg_color="gray50", hover_color="gray40")
        close_button.grid(row=1, column=0, columnspan=2, pady=(10,0))

    def _toggle_edit_mode(self):
        self.is_editing = not self.is_editing
        new_state = "normal" if self.is_editing else "disabled"

        for key, widget in self.entry_widgets.items():
            if key == "status":
                for radio in widget["radios"]:
                    radio.configure(state=new_state)
            elif isinstance(widget, customtkinter.CTkComboBox): # Categoria
                 widget.configure(state=new_state)
            elif isinstance(widget, customtkinter.CTkEntry): # Outros campos editáveis
                widget.configure(state=new_state)

        if self.is_editing:
            self.edit_button.configure(text="Cancelar Edição")
            self.save_button.configure(state="normal")
        else:
            self.edit_button.configure(text="Editar")
            self.save_button.configure(state="disabled")
            # Recarregar dados originais se o usuário cancelar
            self._load_transaction_data() # Recarrega
            self._update_form_fields()    # Atualiza a UI

    def _update_form_fields(self):
        """Atualiza os campos do formulário com os dados de self.transaction_data."""
        if not self.transaction_data:
            return

        self.entry_widgets["description"].delete(0, customtkinter.END)
        self.entry_widgets["description"].insert(0, self.transaction_data.get("description", ""))
        
        self.entry_widgets["value"].delete(0, customtkinter.END)
        self.entry_widgets["value"].insert(0, f"{self.transaction_data.get('value', 0.0):.2f}")

        self.category_combobox.set(self.transaction_data.get("category_name", "N/A"))

        self.status_var.set(self.transaction_data.get("status", "N/A"))

        self.entry_widgets["due_date"].delete(0, customtkinter.END)
        self.entry_widgets["due_date"].insert(0, self.transaction_data.get("due_date", "N/A"))

        self.entry_widgets["payment_date"].delete(0, customtkinter.END)
        self.entry_widgets["payment_date"].insert(0, self.transaction_data.get("payment_date", "") or "N/A")

        # Campos não editáveis (apenas para garantir que estejam corretos se _load_transaction_data for chamado)
        # Se você tiver labels para eles em vez de entries, precisaria atualizá-los aqui.
        # Ex: self.id_label.configure(text=self.transaction_data.get("id", "N/A"))

    def _save_changes(self):
        if not self.transaction_data:
            CTkMessagebox(title="Erro", message="Dados da transação não encontrados.", icon="cancel", master=self)
            return

        try:
            updated_data = {
                "transaction_id": self.transaction_id,
                "description": self.entry_widgets["description"].get().strip(),
                "value": float(self.entry_widgets["value"].get().replace(",", ".")),
                "due_date": datetime.datetime.strptime(self.entry_widgets["due_date"].get(), "%Y-%m-%d").strftime("%Y-%m-%d")
                            if self.entry_widgets["due_date"].get() not in ["N/A", ""] else None,
                "payment_date": datetime.datetime.strptime(self.entry_widgets["payment_date"].get(), "%Y-%m-%d").strftime("%Y-%m-%d")
                                if self.entry_widgets["payment_date"].get() not in ["N/A", ""] else None,
                "status": self.status_var.get(),
            }

            # Obter category_id a partir do nome selecionado
            selected_category_name = self.category_combobox.get()
            categories = Database.get_categories_by_user(self.transaction_data.get("user_id"))
            selected_category_obj = next((cat for cat in categories if cat['name'] == selected_category_name), None)
            if not selected_category_obj:
                CTkMessagebox(title="Erro de Validação", message="Categoria selecionada é inválida.", icon="cancel", master=self)
                return
            updated_data["category_id"] = selected_category_obj['id']

            # Validações
            if not updated_data["description"]:
                CTkMessagebox(title="Erro de Validação", message="Descrição não pode ser vazia.", icon="warning", master=self)
                return
            if updated_data["status"] == "Em Aberto" and not updated_data["due_date"]:
                CTkMessagebox(title="Erro de Validação", message="Data Prevista é obrigatória para status 'Em Aberto'.", icon="warning", master=self)
                return
            if updated_data["status"] == "Pago" and not updated_data["payment_date"]:
                CTkMessagebox(title="Erro de Validação", message="Data de Pagamento é obrigatória para status 'Pago'.", icon="warning", master=self)
                return
            if updated_data["status"] == "Pago" and not updated_data["due_date"]: # Se pago, due_date deve ser igual a payment_date se não preenchida
                updated_data["due_date"] = updated_data["payment_date"]


            # Campos não editáveis que precisam ser passados para update_transaction
            # Se sua função update_transaction precisar deles, adicione-os aqui a partir de self.transaction_data
            # Ex: updated_data["modality"] = self.transaction_data.get("modality")
            #     updated_data["installments_str"] = self.transaction_data.get("installments")
            #     updated_data["launch_date"] = self.transaction_data.get("launch_date")

            success = Database.update_transaction(
                transaction_id=updated_data["transaction_id"],
                description=updated_data["description"],
                value=updated_data["value"],
                due_date=updated_data["due_date"],
                payment_date=updated_data["payment_date"],
                status=updated_data["status"],
                category_id=updated_data["category_id"]
                # Passe outros campos se a função update_transaction os esperar
            )

            if success:
                CTkMessagebox(title="Sucesso", message="Transação atualizada com sucesso!", icon="check", master=self)
                if self.on_save_callback:
                    self.on_save_callback()
                self._toggle_edit_mode() # Volta para o modo de visualização
                self._load_transaction_data() # Recarrega os dados para mostrar os valores atualizados
                self._update_form_fields()    # Atualiza a UI com os dados recarregados
            else:
                CTkMessagebox(title="Erro", message="Falha ao atualizar a transação.", icon="cancel", master=self)

        except ValueError as ve:
            CTkMessagebox(title="Erro de Formato", message=f"Formato de dado inválido: {ve}", icon="cancel", master=self)
        except Exception as e:
            CTkMessagebox(title="Erro Inesperado", message=f"Ocorreu um erro: {e}", icon="cancel", master=self)

if __name__ == '__main__':
    # Para testar esta janela isoladamente
    # Você precisaria de um ID de transação válido do seu banco de dados
    # e garantir que Database.py esteja configurado e o DB exista.
    
    # Exemplo de como criar tabelas e adicionar uma transação para teste (execute isso uma vez)
    # Database.create_tables()
    # user_id_teste = "test_user_for_consulta"
    # Database.add_user(user_id_teste, "Usuário Teste Consulta")
    # cat_id_teste = "cat_consulta_01"
    # Database.add_category(cat_id_teste, user_id_teste, "Alimentação Consulta", "Despesa", "#FF0000")
    # trans_id_teste = "trans_consulta_01"
    # Database.add_transaction(
    #     transaction_id_base=trans_id_teste, user_id=user_id_teste, category_id=cat_id_teste,
    #     original_description="Almoço Teste Consulta", total_value=55.75,
    #     initial_due_date="2024-07-25", initial_status="Em Aberto", modality="À vista", num_installments=1,
    #     launch_date="2024-07-01"
    # )

    app_root = customtkinter.CTk()
    app_root.withdraw() 
    
    # Substitua 'trans_consulta_01' por um ID de transação real do seu banco
    valid_transaction_id_for_test = "trans_consulta_01" 
    if Database.get_transaction_by_id(valid_transaction_id_for_test):
        form_consulta = FormConsultaTransacaoWindow(master=app_root, transaction_id=valid_transaction_id_for_test)
        app_root.mainloop()
    else:
        print(f"Transação de teste com ID '{valid_transaction_id_for_test}' não encontrada. Crie-a primeiro.")
        app_root.destroy()