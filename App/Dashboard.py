import customtkinter
import tkinter as tk
from PIL import Image # Adicionado para carregar a imagem do logo

# Importa as funções do nosso novo módulo de banco de dados (se necessário no futuro para o Dashboard).
# import database # Descomente se o Dashboard precisar interagir diretamente com o banco.

class Dashboard(customtkinter.CTk):
    def __init__(self, user_id=None): # Adiciona user_id como parâmetro opcional.
        super().__init__()
        self.current_user_id = user_id # Armazena o ID do usuário.
        print(f"Dashboard iniciado para o usuário ID: {self.current_user_id}")
        # Configure window
        self.title("Gestão Financeira - Dashboard")
        self.geometry("1024x768") # Set a default window size
        customtkinter.set_appearance_mode("System") # Use system theme (default gray background)
        customtkinter.set_default_color_theme("blue") # Or choose another theme

        # Set grid layout for the main window (1 column for title, 2 columns below title)
        self.grid_columnconfigure(0, weight=1) # Title column spans the width
        self.grid_columnconfigure(1, weight=1) # Second column for pie chart container
        self.grid_rowconfigure(0, weight=0) # Title row
        self.grid_rowconfigure(1, weight=0) # Top months container row
        self.grid_rowconfigure(2, weight=1) # Row for list and pie chart (takes remaining space)
        self.grid_rowconfigure(3, weight=0) # New row for action buttons and logo


        # --- Title ---
        self.title_label = customtkinter.CTkLabel(self, text="Dashboard", font=customtkinter.CTkFont(size=24, weight="bold"))
        self.title_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="w") # Span across two columns


        # --- Top Container for Months ---
        self.months_container_frame = customtkinter.CTkFrame(self, corner_radius=10, border_width=2)
        self.months_container_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="nsew") # Span across two columns

        # Configure grid for months container (2 rows, 6 columns)
        self.months_container_frame.grid_rowconfigure((0, 1), weight=1)
        for i in range(6):
            self.months_container_frame.grid_columnconfigure(i, weight=1)

        # Add month placeholders
        months = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                  "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

        for i, month in enumerate(months):
            row = 0 if i < 6 else 1
            col = i % 6
            # Using a frame for each month allows adding more widgets inside later (e.g., a small chart, numbers)
            month_frame = customtkinter.CTkFrame(self.months_container_frame, corner_radius=5, fg_color="gray20") # Darker gray for month background
            month_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

            month_label = customtkinter.CTkLabel(month_frame, text=month, font=customtkinter.CTkFont(size=14, weight="bold"))
            month_label.pack(padx=5, pady=5) # Center the month name

            # Add placeholder for data within the month frame
            data_placeholder = customtkinter.CTkLabel(month_frame, text="R$ 0,00\nData Here", font=customtkinter.CTkFont(size=12), text_color="gray50")
            data_placeholder.pack(padx=5, pady=0)


        # --- Left Container for List Items ---
        self.list_container_frame = customtkinter.CTkFrame(self, corner_radius=10, border_width=2)
        self.list_container_frame.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="nsew") # Occupies the first column in row 2

        # Add list items (example)
        list_items_title = customtkinter.CTkLabel(self.list_container_frame, text="Categorias:", font=customtkinter.CTkFont(size=16, weight="bold"))
        list_items_title.pack(padx=10, pady=(10, 5), anchor="w") # Anchor west

        list_items = ["Cat1 R$ 0,00", "Cat2 R$ 0,00", "Cat3 R$ 0,00", "Cat4 R$ 0,00"]
        for item in list_items:
            item_label = customtkinter.CTkLabel(self.list_container_frame, text=item, font=customtkinter.CTkFont(size=14))
            item_label.pack(padx=20, pady=2, anchor="w") # Anchor west, add some padding


        # --- Bottom Container for Pie Chart ---
        self.pie_chart_container_frame = customtkinter.CTkFrame(self, corner_radius=10, border_width=2)
        self.pie_chart_container_frame.grid(row=2, column=1, padx=20, pady=(10, 20), sticky="nsew") # Occupies the second column in row 2

        # Placeholder for the pie chart
        pie_chart_placeholder_label = customtkinter.CTkLabel(self.pie_chart_container_frame, text="Gráfico de Pizza Placeholder", font=customtkinter.CTkFont(size=16, weight="bold"))
        pie_chart_placeholder_label.pack(expand=True, fill="both", padx=20, pady=20) # Center placeholder text

        # --- Bottom Container for Action Buttons and Logo ---
        self.actions_container_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent") # Sem cantos e transparente
        # Aumentado o pady inferior para criar mais espaço abaixo dos botões.
        self.actions_container_frame.grid(row=3, column=0, columnspan=2, padx=0, pady=(10,20), sticky="nsew")

        # Frame interno para centralizar os botões
        buttons_inner_frame = customtkinter.CTkFrame(self.actions_container_frame, fg_color="transparent")
        buttons_inner_frame.pack(expand=True, anchor="center", pady=10) # Centraliza o frame dos botões

        # Configure grid for actions container (1 row, many columns for flexibility or use pack)
        # Usaremos pack para os botões e place para o logo

        # Botões de Ação
        button_font = customtkinter.CTkFont(size=14)
        button_width = 150
        button_height = 35
        
        # Define as cores para os botões
        cor_botao_cinza = "gray30"  # Um cinza mais escuro do customtkinter
        cor_botao_azul_hover = "#2196F3" # O mesmo azul usado anteriormente para hover

        self.details_button = customtkinter.CTkButton(buttons_inner_frame, text="Detalhes",
                                                      font=button_font, width=button_width, height=button_height,
                                                      fg_color=cor_botao_cinza, hover_color=cor_botao_azul_hover)
        self.details_button.pack(side="left", padx=5) # Removido pady daqui, já está no buttons_inner_frame

        self.categories_button = customtkinter.CTkButton(buttons_inner_frame, text="Categorias",
                                                         font=button_font, width=button_width, height=button_height,
                                                         fg_color=cor_botao_cinza, hover_color=cor_botao_azul_hover)
        self.categories_button.pack(side="left", padx=5)

        self.new_expense_button = customtkinter.CTkButton(buttons_inner_frame, text="Nova Despesa",
                                                          font=button_font, width=button_width, height=button_height,
                                                          fg_color=cor_botao_cinza, hover_color=cor_botao_azul_hover)
        self.new_expense_button.pack(side="left", padx=5)

        self.new_category_button = customtkinter.CTkButton(buttons_inner_frame, text="Nova Categoria",
                                                           font=button_font, width=button_width, height=button_height,
                                                           fg_color=cor_botao_cinza, hover_color=cor_botao_azul_hover)
        self.new_category_button.pack(side="left", padx=5)

        # Logo como Marca d'água
        try:
            logo_image_path = "Images/Logo.png"
            pil_logo_image = Image.open(logo_image_path)
            # Defina o tamanho desejado para o logo. Ajuste conforme necessário.
            self.logo_ctk_image = customtkinter.CTkImage(pil_logo_image, size=(60, 60)) 
            
            self.logo_label = customtkinter.CTkLabel(self.actions_container_frame, image=self.logo_ctk_image, text="")
            # Posiciona o logo no canto inferior direito do actions_container_frame
            self.logo_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-5) # x e y para um pequeno offset da borda
        except FileNotFoundError:
            print(f"Erro: Imagem do logo '{logo_image_path}' não encontrada.")
        except Exception as e:
            print(f"Erro ao carregar a imagem do logo: {e}")

if __name__ == "__main__":
    app = Dashboard()
    app.mainloop()