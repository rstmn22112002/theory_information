import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from collections import Counter
import math


def file_to_binary():
    file_path = filedialog.askopenfilename()
    try:
        with open(file_path, 'rb') as file:
            content = file.read()
            binary_sequence = ''.join(format(byte, '08b') for byte in content)
            entropy = calculate_entropy(binary_sequence)
            encoded_sequence = gilbert_moore_encoding(binary_sequence)
            
            with open("encoded_sequence.txt", 'w') as encoded_file:
                encoded_file.write(encoded_sequence)
            
            entropy_encoded = calculate_entropy(encoded_sequence)
            
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, f"Двоичная последовательность:\n{binary_sequence}\n\n")
            result_text.insert(tk.END, f"Энтропия исходной последовательности: {entropy} бит/символ\n\n")
            result_text.insert(tk.END, f"Закодированная последовательность (Гилберт-Мур):\n{encoded_sequence}\n\n")
            result_text.insert(tk.END, f"Энтропия закодированной последовательности: {entropy_encoded} бит/символ\n\n")
            result_text.insert(tk.END, "Закодированная последовательность сохранена в файл 'encoded_sequence.txt'")
            
            # Calculate probabilities and display in the treeview
            probabilities = analyze_file(file_path)
            if isinstance(probabilities, dict):
                display_probabilities(probabilities)
            else:
                result_text.delete(1.0, tk.END)
                result_text.insert(tk.END, probabilities)
    except FileNotFoundError:
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "Файл не найден")

def calculate_entropy(binary_sequence):
    freq = Counter(binary_sequence)
    total_bits = len(binary_sequence)
    probabilities = [count / total_bits for count in freq.values()]
    entropy = -sum(p * math.log2(p) for p in probabilities if p != 0)
    return entropy

def gilbert_moore_encoding(binary_sequence):
    if len(binary_sequence) % 2 != 0:
        binary_sequence += '0'  # Добавляем 0, если длина нечетная для выполнения перестановки парами
        
    encoded_sequence = ''
    for i in range(0, len(binary_sequence), 2):
        encoded_sequence += binary_sequence[i + 1] + binary_sequence[i]

    return encoded_sequence

def analyze_file(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            symbol_counts = Counter(content)
            total_symbols = len(content)
            probabilities = {symbol: round(count / total_symbols, 2) for symbol, count in symbol_counts.items()}
            return probabilities
    except FileNotFoundError:
        return "Файл не найден"

def display_probabilities(probabilities):
    cum_prob = 0
    for i, (symbol, probability) in enumerate(probabilities.items(), start=1):
        cum_prob += probability
        cumulative_probability = round(cum_prob - probability, 2)
        g_m = cumulative_probability + (probability / 2)
        g_m_binary = float_to_bin_fixed(g_m, 8)  # Переводим g_m в двоичную систему счисления
        l_m = math.ceil(-math.log(probability / 2, 2))  # Рассчитываем l_m по формуле
        code_word = g_m_binary.split('.')[1][:l_m]  # Получаем l_m символов из дробной части g_m
        tree.insert('', 'end', values=(i, symbol, probability, cumulative_probability, round(g_m, 2), g_m_binary, l_m, code_word))

def float_to_bin_fixed(f, precision):
    if not math.isfinite(f):
        return repr(f)  # inf nan

    sign = '-' * (math.copysign(1.0, f) < 0)
    frac, fint = math.modf(math.fabs(f))  # split on fractional, integer parts
    n, d = frac.as_integer_ratio()  # frac = numerator / denominator
    assert d & (d - 1) == 0  # power of two
    
    binary = f'{sign}{math.floor(fint):b}.{n:0{d.bit_length()-1}b}'
    rounded_number = round(float(binary), precision)
    formatted_number = '{:.{}f}'.format(rounded_number, precision)
    return formatted_number

root = tk.Tk()
root.title("Преобразование файла в двоичную последовательность, расчет энтропии и кодирование Гилберта-Мура")
root.geometry("1100x600")  # Установка размеров окна

select_file_button = tk.Button(root, text="Выбрать файл для обработки", command=file_to_binary)
select_file_button.pack(pady=20)

result_text = tk.Text(root, height=20, width=100)
result_text.pack(padx=20, pady=10)



# Добавляем новый столбец 'l_m'
tree = ttk.Treeview(root, columns=('Number', 'Symbol', 'Probability', 'Cumulative Probability', 'Cumulative Probability 2 (g_m)', 'g_m в двоичной системе', 'Длина кодового слова l_m', 'Кодовое слово'), show='headings', selectmode='browse')
tree.heading('Number', text='№')
tree.heading('Symbol', text='Символ')
tree.heading('Probability', text='Вер-сть')
tree.heading('Cumulative Probability', text='Кумулятивная вер-сть q_m')
tree.heading('Cumulative Probability 2 (g_m)', text='Кумулятивная вер-сть g_m')
tree.heading('g_m в двоичной системе', text='g_m в двоичной системе')
tree.heading('Длина кодового слова l_m', text='Длина кодового слова l_m')
tree.heading('Кодовое слово', text='Кодовое слово')
tree.column('Number', width=30)
tree.column('Symbol', width=70)
tree.column('Probability', width=50)
tree.column('Cumulative Probability', width=170)
tree.column('Cumulative Probability 2 (g_m)', width=170)
tree.column('g_m в двоичной системе', width=150)
tree.column('Длина кодового слова l_m', width=150)
tree.column('Кодовое слово', width=150)
tree.pack(padx=20, pady=10)

root.mainloop()
