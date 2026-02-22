import tkinter as tk
from pynput import keyboard
import threading

class VirtualKeyboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Виртуальная клавиатура")
        self.root.configure(bg='#1a1a2e')
        
        self.caps_lock = False
        self.shift_active = False
        self.keys = {}
        
        # Поле ввода
        self.input_text = tk.Text(root, height=3, font=('Arial', 14),
                                 bg='#2a2a3e', fg='white', insertbackground='white')
        self.input_text.pack(pady=10, padx=20, fill=tk.X)
        
        # Индикатор Caps Lock
        self.caps_label = tk.Label(root, text="caps", font=('Arial', 10),
                                  bg='#1a1a2e', fg='#4a4a6a')
        self.caps_label.pack(anchor='e', padx=20)
        
        # Раскладка
        self.layout = [
            ['Й', 'Ц', 'У', 'К', 'Е', 'Н', 'Г', 'Ш', 'Щ', 'З', 'Х', 'Ъ'],
            ['Ф', 'Ы', 'В', 'А', 'П', 'Р', 'О', 'Л', 'Д', 'Ж', 'Э'],
            ['Я', 'Ч', 'С', 'М', 'И', 'Т', 'Ь', 'Б', 'Ю', ','],
        ]
        
        self.create_keyboard()
        self.start_listener()
    
    def create_btn(self, parent, text, width, cmd=None):
        """Создаёт кнопку со стандартными параметрами"""
        btn = tk.Button(parent, text=text, width=width, font=('Arial', 14),
                       bg='#2a2a3e', fg='#c0c0c0', relief='flat',
                       highlightthickness=1, highlightbackground='#4a4a6a',
                       activebackground='#4a4a7e', activeforeground='white',
                       cursor='hand2')
        btn.pack(side=tk.LEFT, padx=3, ipady=12)
        
        if cmd:
            btn.bind('<Button-1>', cmd)
        
        btn.bind('<Enter>', lambda e, b=btn: b.configure(bg='#353555', highlightbackground='#5a5a8a'))
        btn.bind('<Leave>', lambda e, b=btn: b.configure(bg='#2a2a3e', highlightbackground='#4a4a6a'))
        
        return btn
    
    def create_keyboard(self):
        """Создаёт клавиатуру"""
        kb_frame = tk.Frame(self.root, bg='#1a1a2e')
        kb_frame.pack(pady=20)
        
        for row in self.layout:
            row_frame = tk.Frame(kb_frame, bg='#1a1a2e')
            row_frame.pack(pady=2)
            
            for key in row:
                btn = self.create_btn(row_frame, key, 5)
                self.keys[key.lower()] = btn
        
        # Нижний ряд
        row_frame = tk.Frame(kb_frame, bg='#1a1a2e')
        row_frame.pack(pady=2)
        
        self.keys['caps'] = self.create_btn(row_frame, '🔒 Caps', 10, lambda e: self.toggle_caps())
        self.keys['shift'] = self.create_btn(row_frame, '⇧ Shift', 10, lambda e: self.toggle_shift())
        self.keys['space'] = self.create_btn(row_frame, '␣', 30, lambda e: self.insert_char(' '))
        self.keys['backspace'] = self.create_btn(row_frame, '⌫', 8, lambda e: self.delete_char())
    
    def toggle_caps(self):
        """Переключает Caps Lock"""
        self.caps_lock = not self.caps_lock
        self.caps_label.configure(fg='#4a6a4a' if self.caps_lock else '#4a4a6a',
                                 text='CAPS' if self.caps_lock else 'caps')
        self.update_letters()
    
    def toggle_shift(self):
        """Переключает Shift"""
        self.shift_active = not self.shift_active
        self.update_letters()
    
    def update_letters(self):
        """Обновляет буквы на клавиатуре"""
        for key, btn in self.keys.items():
            if len(key) == 1 and key.isalpha():
                btn.configure(text=key.upper() if self.caps_lock or self.shift_active else key.lower())
    
    def highlight(self, key_name, pressed):
        """Подсветка клавиши"""
        if key_name in self.keys and key_name not in ['caps', 'shift']:
            color = '#4a4a7e' if pressed else '#2a2a3e'
            self.keys[key_name].configure(bg=color, fg='white' if pressed else '#c0c0c0')
    
    def on_press(self, key):
        """Нажатие клавиши"""
        try:
            if hasattr(key, 'char') and key.char:
                char = key.char.upper() if self.caps_lock or self.shift_active else key.char.lower()
                self.highlight(char.lower(), True)
                self.insert_char(char)
                if self.shift_active:
                    self.root.after(100, self.release_shift)
            
            if key == keyboard.Key.space:
                self.highlight('space', True)
                self.insert_char(' ')
            elif key == keyboard.Key.backspace:
                self.highlight('backspace', True)
                self.delete_char()
            elif key == keyboard.Key.caps_lock:
                self.toggle_caps()
            elif key == keyboard.Key.shift:
                self.shift_active = True
                self.update_letters()
        except: pass
    
    def on_release(self, key):
        """Отпускание клавиши"""
        try:
            if hasattr(key, 'char') and key.char:
                self.highlight(key.char.lower(), False)
            if key == keyboard.Key.space:
                self.highlight('space', False)
            elif key == keyboard.Key.backspace:
                self.highlight('backspace', False)
            elif key == keyboard.Key.shift:
                self.release_shift()
        except: pass
    
    def release_shift(self):
        """Выключает Shift"""
        self.shift_active = False
        self.update_letters()
    
    def insert_char(self, char):
        self.input_text.insert(tk.END, char)
        self.input_text.see(tk.END)
    
    def delete_char(self):
        current = self.input_text.get("1.0", tk.END)
        if len(current) > 1:
            self.input_text.delete("end-2c", "end-1c")
    
    def start_listener(self):
        def listener_thread():
            with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
                listener.join()
        
        threading.Thread(target=listener_thread, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = VirtualKeyboard(root)
    root.mainloop()