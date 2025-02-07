import os 
import sys
import time
import threading
import tkinter as tk
from tkinter import ttk
import pyautogui
import keyboard
import cv2
import numpy as np

# Controllo e installazione delle dipendenze mancanti
try:
    import pyautogui
    import keyboard
    import cv2
    import numpy as np
except ImportError:
    print("🔄 Installazione delle dipendenze necessarie...")
    os.system(f"{sys.executable} -m pip install --upgrade pip")
    os.system(f"{sys.executable} -m pip install pyautogui keyboard opencv-python numpy pillow pyscreeze")
    print("✅ Installazione completata! Riavvia lo script.")
    sys.exit()


class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ManuLifts' AutoClicker")
        self.root.geometry("400x500")  # Aumentata per più punti e modifiche
        self.running = False
        self.points_selected = []  # Lista per memorizzare i punti selezionati
        self.selecting_points = False  # Flag per indicare se stiamo selezionando i punti
        self.click_interval = tk.DoubleVar(value=1.0)  # Tempo tra i click (sec)

        # Hotkeys default
        self.hotkeys = {
            "select_points": "F1",
            "stop_select_points": "F2",
            "start_stop_clicker": "F6"
        }

        # Titolo
        ttk.Label(root, text="AutoClicker", font=("Arial", 14)).pack(pady=5)

        # Sezione selezione punti
        self.points_frame = ttk.LabelFrame(root, text="Punti di Click")
        self.points_frame.pack(padx=10, pady=5, fill="x")

        self.points_label = ttk.Label(self.points_frame, text="Nessun punto selezionato")
        self.points_label.pack()

        self.points_modify_frame = ttk.Frame(self.points_frame)
        self.points_modify_frame.pack(pady=10)

        ttk.Button(self.points_frame, text="Avvia Selezione Punti", command=self.start_selecting_points).pack()
        ttk.Button(self.points_frame, text="Termina Selezione Punti", command=self.stop_selecting_points).pack()

        # Pulsante per cancellare tutti i punti
        ttk.Button(self.points_frame, text="Cancella Tutti i Punti", command=self.clear_points).pack(pady=10)

        # Sezione intervallo click
        self.interval_frame = ttk.LabelFrame(root, text="Intervallo tra i Click (sec)")
        self.interval_frame.pack(padx=10, pady=5, fill="x")

        ttk.Entry(self.interval_frame, textvariable=self.click_interval).pack()

        # Pulsanti Avvio/Stop
        self.control_frame = ttk.Frame(root)
        self.control_frame.pack(pady=10)

        ttk.Button(self.control_frame, text="Start/Stop Clicker", command=self.toggle_clicker).grid(row=0, column=0, padx=5)
        
        # Tasto per aprire le impostazioni delle hotkey
        ttk.Button(self.control_frame, text="Impostazioni Hotkey", command=self.open_hotkey_settings).grid(row=0, column=1, padx=5)

        # Hotkey F6 per start/stop
        keyboard.add_hotkey(self.hotkeys["start_stop_clicker"], self.toggle_clicker)

        # Hotkey F1 per selezionare un punto
        keyboard.add_hotkey(self.hotkeys["select_points"], self.select_point)

        # Hotkey F2 per terminare la selezione
        keyboard.add_hotkey(self.hotkeys["stop_select_points"], self.stop_selecting_points)

    def open_hotkey_settings(self):
        """Apre una nuova finestra per modificare le hotkey."""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Impostazioni Hotkey")
        settings_window.geometry("300x300")

        ttk.Label(settings_window, text="Seleziona le hotkey per ogni azione:").pack(pady=10)

        # Etichetta e pulsante per la selezione del tasto per selezionare un punto
        ttk.Label(settings_window, text="Seleziona un punto (F1)").pack()
        select_points_button = ttk.Button(settings_window, text="Modifica", command=lambda: self.set_hotkey("select_points"))
        select_points_button.pack(pady=5)

        # Etichetta e pulsante per la selezione del tasto per fermare la selezione
        ttk.Label(settings_window, text="Termina selezione (F2)").pack()
        stop_select_points_button = ttk.Button(settings_window, text="Modifica", command=lambda: self.set_hotkey("stop_select_points"))
        stop_select_points_button.pack(pady=5)

        # Etichetta e pulsante per la selezione del tasto per avviare/fermare il clicker
        ttk.Label(settings_window, text="Avvia/Ferma clicker (F6)").pack()
        start_stop_clicker_button = ttk.Button(settings_window, text="Modifica", command=lambda: self.set_hotkey("start_stop_clicker"))
        start_stop_clicker_button.pack(pady=5)

        # Pulsante per salvare le hotkey
        save_button = ttk.Button(settings_window, text="Salva", command=self.save_hotkeys)
        save_button.pack(pady=10)

    def set_hotkey(self, action):
        """Consente all'utente di premere una hotkey da assegnare all'azione."""
        # Mostra un messaggio che indica che l'utente deve premere un tasto
        self.hotkey_info_label = ttk.Label(self.root, text="Premi un tasto per la hotkey!")
        self.hotkey_info_label.pack(pady=10)

        # Funzione per ascoltare il tasto premuto
        def on_key_press(event):
            # Salva la hotkey per l'azione
            key_pressed = event.name
            self.hotkeys[action] = key_pressed

            # Aggiorna la GUI con la hotkey appena selezionata
            self.hotkey_info_label.config(text=f"Hotkey per {action} impostata su: {key_pressed}")
            keyboard.remove_all_hotkeys()  # Rimuovi tutte le hotkey
            self.update_hotkeys()  # Aggiungi le nuove hotkey

        # Ascolta la pressione del tasto
        keyboard.hook(on_key_press)

    def update_hotkeys(self):
        """Aggiungi tutte le hotkey definite nella mappa delle hotkey."""
        keyboard.add_hotkey(self.hotkeys["start_stop_clicker"], self.toggle_clicker)
        keyboard.add_hotkey(self.hotkeys["select_points"], self.select_point)
        keyboard.add_hotkey(self.hotkeys["stop_select_points"], self.stop_selecting_points)

    def save_hotkeys(self):
        """Salva le hotkey scelte."""
        print(f"Hotkeys salvate: {self.hotkeys}")
        
    def start_selecting_points(self):
        """Inizia la selezione dei punti premendo la hotkey scelta."""
        if not self.selecting_points:
            self.points_selected = []  # Resetta la lista dei punti
            self.points_label.config(text="Premi la hotkey per selezionare un punto...")
            self.selecting_points = True  # Abilita la selezione dei punti

    def stop_selecting_points(self):
        """Ferma la selezione dei punti e permette di modificarli manualmente."""
        if self.selecting_points:
            self.selecting_points = False  # Disabilita la selezione dei punti
            self.points_label.config(text="Selezione terminata. Modifica i punti se necessario.")
            self.display_modify_fields()

    def select_point(self):
        """Seleziona un punto sullo schermo con la hotkey."""
        if self.selecting_points:
            x, y = pyautogui.position()  # Ottieni la posizione corrente del mouse
            self.points_selected.append((x, y))  # Aggiungi il punto alla lista
            print(f"Punto selezionato: ({x}, {y})")

            # Aggiorna la label con la lista dei punti selezionati
            points_text = ', '.join([f"({x}, {y})" for x, y in self.points_selected])
            self.points_label.config(text=f"Punti selezionati: {points_text}")
            self.display_modify_fields()

    def display_modify_fields(self):
        """Visualizza i campi di modifica per ciascun punto selezionato."""
        for widget in self.points_modify_frame.winfo_children():
            widget.destroy()  # Rimuove i widget precedenti

        self.modify_entries = []  # Lista per memorizzare i campi di input

        for idx, (x, y) in enumerate(self.points_selected):
            frame = ttk.Frame(self.points_modify_frame)
            frame.pack(fill="x", pady=2)

            ttk.Label(frame, text=f"Punto {idx+1}:").pack(side="left")

            x_entry = ttk.Entry(frame)
            x_entry.insert(0, str(x))
            x_entry.pack(side="left", padx=5)

            y_entry = ttk.Entry(frame)
            y_entry.insert(0, str(y))
            y_entry.pack(side="left", padx=5)

            self.modify_entries.append((x_entry, y_entry))

        # Pulsante per salvare le modifiche
        save_button = ttk.Button(self.points_modify_frame, text="Salva modifiche", command=self.save_modifications)
        save_button.pack(pady=10)

    def save_modifications(self):
        """Salva le modifiche fatte manualmente ai punti."""
        for idx, (x_entry, y_entry) in enumerate(self.modify_entries):
            try:
                new_x = int(x_entry.get())
                new_y = int(y_entry.get())
                self.points_selected[idx] = (new_x, new_y)  # Aggiorna il punto
            except ValueError:
                print(f"Errore nei valori di input per il punto {idx+1}. Ignorato.")
        
        # Aggiorna la label con i nuovi punti
        points_text = ', '.join([f"({x}, {y})" for x, y in self.points_selected])
        self.points_label.config(text=f"Punti selezionati: {points_text}")

    def clear_points(self):
        """Cancella tutti i punti selezionati."""
        self.points_selected = []  # Svuota la lista dei punti
        self.points_label.config(text="Nessun punto selezionato")  # Aggiorna la label
        self.display_modify_fields()  # Rimuovi i campi di modifica

    def start_clicker(self):
        """Avvia il thread del clicker."""
        if not self.running:  # Prevents multiple threads
            self.running = True
            self.click_thread = threading.Thread(target=self.click_loop)
            self.click_thread.start()

    def stop_clicker(self):
        """Ferma il thread del clicker."""
        if self.running:
            self.running = False
            if hasattr(self, 'click_thread') and self.click_thread.is_alive():  # Check thread existence and status
                self.click_thread.join()  # Ensure thread stops cleanly
            print("Clicker stopped.")

    def click_loop(self):
        """Ciclo di click sui punti selezionati."""
        while self.running and self.points_selected:
            for point in self.points_selected:
                x, y = point
                pyautogui.click(x, y)
                time.sleep(self.click_interval.get())  # Usa il valore scelto dall'utente

    def toggle_clicker(self):
        """Avvia o ferma il clicker con la hotkey."""
        if self.running:
            self.stop_clicker()
        else:
            self.start_clicker()


# Avvia l'interfaccia
root = tk.Tk()
app = AutoClickerApp(root)
root.mainloop()
