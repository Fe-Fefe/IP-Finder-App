import tkinter as tk
from tkinter import messagebox
import socket
from urllib.parse import urlparse
import threading

class IPFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IP Finder")
        self.root.geometry("500x450") # Aumenté un poco la altura para comodidad
        self.root.resizable(False, False)
        self.root.configure(bg="#1a1a2e")
        
        self.current_ip = ""
        self.create_widgets()
        
    def create_widgets(self):
        # Título
        tk.Label(
            self.root,
            text="🔍 IP FINDER",
            font=("Arial", 24, "bold"),
            fg="#00d9ff",
            bg="#1a1a2e"
        ).pack(pady=20)
        
        # Label instrucción
        tk.Label(
            self.root,
            text="Ingresa la URL o dominio:",
            font=("Arial", 12),
            fg="#ffffff",
            bg="#1a1a2e"
        ).pack()
        
        # Entrada de URL
        self.url_entry = tk.Entry(
            self.root,
            font=("Consolas", 14),
            width=35,
            bg="#16213e",
            fg="#ffffff",
            insertbackground="#00d9ff",
            relief="solid"
        )
        self.url_entry.pack(pady=10, ipady=8)
        self.url_entry.bind("<Return>", lambda e: self.search_ip())
        self.url_entry.focus() # Poner el foco al iniciar
        
        # Botón buscar
        self.search_btn = tk.Button(
            self.root,
            text="🔎 BUSCAR IP",
            font=("Arial", 12, "bold"),
            bg="#00d9ff",
            fg="#000000",
            width=20,
            height=1,
            cursor="hand2",
            command=self.search_ip
        )
        self.search_btn.pack(pady=15)
        
        # Frame resultado
        result_frame = tk.Frame(self.root, bg="#16213e", padx=20, pady=20)
        result_frame.pack(pady=5, padx=30, fill="x")
        
        # Dominio encontrado
        self.domain_label = tk.Label(
            result_frame,
            text="Dominio: ---",
            font=("Consolas", 11),
            fg="#888888",
            bg="#16213e"
        )
        self.domain_label.pack()
        
        # IP encontrada (GRANDE)
        self.ip_label = tk.Label(
            result_frame,
            text="---.---.---.---",
            font=("Consolas", 24, "bold"),
            fg="#666666",
            bg="#16213e"
        )
        self.ip_label.pack(pady=15)
        
        # ========================================
        # BOTÓN COPIAR - GRANDE Y VISIBLE
        # ========================================
        self.copy_btn = tk.Button(
            result_frame,
            text="📋 COPIAR IP",
            font=("Arial", 11, "bold"),
            bg="#28a745",
            fg="#ffffff",
            activebackground="#218838",
            activeforeground="#ffffff",
            width=25,
            cursor="hand2", # El cursor cambia si está activo
            state="disabled", # Desactivado por defecto
            relief="raised",
            bd=2,
            command=self.copy_ip
        )
        self.copy_btn.pack(pady=5)
        # ========================================
        
        # Status Bar
        self.status_label = tk.Label(
            self.root,
            text="Listo para buscar",
            font=("Arial", 9),
            fg="#888888",
            bg="#1a1a2e"
        )
        self.status_label.pack(side="bottom", pady=10)
        
    def extract_domain(self, url):
        """Extrae solo el dominio de la URL de forma robusta"""
        url = url.strip()
        if not url: return ""
        
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            if not domain:
                domain = parsed.path.split('/')[0]
            return domain.split(':')[0] # Remover puerto si existe
        except:
            return ""
    
    def search_ip(self):
        """Inicia la búsqueda de IP en un hilo separado"""
        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showwarning("Atención", "Por favor ingresa una URL o dominio.")
            return
        
        # Interfaz en modo 'Cargando'
        self.search_btn.config(state="disabled", text="Buscando...")
        self.copy_btn.config(state="disabled", bg="#555555") # Gris mientras busca
        self.ip_label.config(text="Buscando...", fg="#ffaa00")
        self.status_label.config(text="Resolviendo DNS...", fg="#ffaa00")
        
        # Hilo para no congelar la ventana
        thread = threading.Thread(target=self.do_search, args=(url,))
        thread.daemon = True
        thread.start()
        
    def do_search(self, url):
        """Lógica de resolución DNS"""
        domain = self.extract_domain(url)
        
        if not domain:
             self.root.after(0, self.show_result, url, None, "URL inválida")
             return

        try:
            ip_address = socket.gethostbyname(domain)
            self.root.after(0, self.show_result, domain, ip_address, None)
        except socket.gaierror:
            self.root.after(0, self.show_result, domain, None, "No se encontró el host")
        except Exception as e:
            self.root.after(0, self.show_result, domain, None, str(e))
    
    def show_result(self, domain, ip_address, error):
        """Actualiza la GUI con el resultado"""
        self.search_btn.config(state="normal", text="🔎 BUSCAR IP")
        
        if error:
            self.domain_label.config(text=f"Dominio: {domain}")
            self.ip_label.config(text="❌ ERROR", fg="#ff5555")
            self.status_label.config(text=error, fg="#ff5555")
            self.current_ip = ""
            self.copy_btn.config(state="disabled", bg="#555555")
        else:
            self.domain_label.config(text=f"Dominio: {domain}")
            self.ip_label.config(text=ip_address, fg="#00ff88")
            self.status_label.config(text="✅ Éxito", fg="#00ff88")
            self.current_ip = ip_address
            # Activar botón copiar
            self.copy_btn.config(state="normal", bg="#28a745", text="📋 COPIAR IP")
            
    def copy_ip(self):
        """Copia la IP al portapapeles y da feedback visual"""
        if self.current_ip:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.current_ip)
            self.root.update() # Asegura que el portapapeles se actualice
            
            # Feedback visual en el botón
            self.copy_btn.config(text="✅ ¡COPIADO!", bg="#00ff88", fg="#000000")
            self.status_label.config(text=f"IP {self.current_ip} copiada al portapapeles", fg="#00d9ff")
            
            # Restaurar botón después de 2 segundos
            self.root.after(2000, self.reset_copy_button)
            
    def reset_copy_button(self):
        """Restaura el estilo original del botón copiar"""
        if self.current_ip: # Solo si hay una IP válida
            self.copy_btn.config(
                text="📋 COPIAR IP",
                bg="#28a745",
                fg="#ffffff"
            )

if __name__ == "__main__":
    root = tk.Tk()
    app = IPFinderApp(root)
    root.mainloop()