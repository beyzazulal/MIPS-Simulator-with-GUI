import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
import ttkthemes

# 8 Register tanımı ve başlangıç değerleri
register_names = [f"R{i}" for i in range(8)]  # R0 - R7
registers = {name: 0 for name in register_names}
memory = [0] * 512  # 512 byte'lık bellek
instruction_memory = [""] * 512  # 512 byte'lık Instruction Memory
labels = {}  # Label'ların satır numaralarını tutar
pc = 0  # Program Counter
realistic_pc = 0  # Donanımsal PC
commands = []  # Komut listesi
pipeline_stages = {"IF": "Empty", "ID": "Empty", "EX": "Empty", "MEM": "Empty", "WB": "Empty"}
hazards = []




# Komutları yükleyen fonksiyon
def load_commands():
    global commands, labels, pc, realistic_pc
    global result_label
    commands = input_text.get("1.0", tk.END).strip().split("\n")
    labels = {}
    pc = 0
    realistic_pc = 0
    cleaned_commands = []

    # Instruction memory'yi temizle
    instruction_memory.clear()
    instruction_memory.extend([""] * 512)

    for i, command in enumerate(commands):
        command = command.strip()
        if ":" in command:  # Etiket var mı kontrol et
            parts = command.split(":")
            label = parts[0].strip()
            labels[label] = len(cleaned_commands)  # Etiketi geçerli komut satırına bağla
            if len(parts) > 1 and parts[1].strip():
                cleaned_commands.append(parts[1].strip())
        else:
            cleaned_commands.append(command)

    commands = cleaned_commands
    for i, command in enumerate(commands):
        if i < len(instruction_memory):
            instruction_memory[i] = command
        else:
            break

    # Pipeline'ı başlangıç durumuna getir
    if len(commands) > 0:
        pipeline_stages["IF"] = "Empty"  # İlk aşama boş başlasın
        pipeline_stages["ID"] = "Empty"
        pipeline_stages["EX"] = "Empty"
        pipeline_stages["MEM"] = "Empty"
        pipeline_stages["WB"] = "Empty"

    
    result_label.configure(text="Komutlar yüklendi!", foreground="blue")
    update_instruction_memory_display()
    update_instruction_memory_display()
    update_pipeline_stages()

def process_labels():
    global labels
    for i, command in enumerate(commands):
        command = command.strip()
        if command and command[-1] == ":":  # Etiket satırı
            label = command[:-1]  # ":" işaretini kaldır
            labels[label] = i  # Etiketi labels sözlüğüne ekle 

# Tek bir komutu işleyen fonksiyon
def step_command():
    global pc, realistic_pc
    instruction = fetch_instruction(pc)  # Instruction Memory'den komut al
    if instruction is None or instruction.strip() == "":
        result_label.configure(text="Program sonlandı.", foreground="green")
        return

    parts = instruction.strip().split()  # Komut parçalarını ayır

    
    try:
        if parts[0] == "add":  # R-Type add
            rd, rs, rt = parts[1].rstrip(","), parts[2].rstrip(","), parts[3]
            registers[rd] = registers[rs] + registers[rt]
        elif parts[0] == "sub":  # R-Type sub
            rd, rs, rt = parts[1].rstrip(","), parts[2].rstrip(","), parts[3]
            registers[rd] = registers[rs] - registers[rt]
        elif parts[0] == "and":  # R-Type and
            rd, rs, rt = parts[1].rstrip(","), parts[2].rstrip(","), parts[3]
            registers[rd] = registers[rs] & registers[rt]
        elif parts[0] == "or":  # R-Type or
            rd, rs, rt = parts[1].rstrip(","), parts[2].rstrip(","), parts[3]
            registers[rd] = registers[rs] | registers[rt]
        elif parts[0] == "slt":  # R-Type slt
            rd, rs, rt = parts[1].rstrip(","), parts[2].rstrip(","), parts[3]
            registers[rd] = 1 if registers[rs] < registers[rt] else 0
        elif parts[0] == "sll":  # R-Type sll
            rd, rt, shamt = parts[1].rstrip(","), parts[2].rstrip(","), int(parts[3])
            registers[rd] = registers[rt] << shamt
        elif parts[0] == "srl":  # R-Type srl
            rd, rt, shamt = parts[1].rstrip(","), parts[2].rstrip(","), int(parts[3])
            registers[rd] = registers[rt] >> shamt
        elif parts[0] == "addi":  # I-Type addi
            if len(parts) != 4:
                result_label.configure(text=f"Geçersiz addi komutu: {instruction}", foreground="red")
                return
            try:
                rt, rs, imm = parts[1].rstrip(","), parts[2].rstrip(","), int(parts[3])
                if rt not in registers or rs not in registers:
                    result_label.configure(text=f"Geçersiz register: {rt} veya {rs}", foreground="red")
                    return
                registers[rt] = registers[rs] + imm
            except ValueError:
                result_label.configure(text=f"Geçersiz immediate değer: {parts[3]}", foreground="red")
                return
        elif parts[0] == "sw":  # I-Type sw
            rt, offset_rs = parts[1].rstrip(","), parts[2]
            offset, rs = offset_rs.split("(")
            rs = rs.rstrip(")")
            address = registers[rs] + int(offset)
            if 0 <= address < len(memory):  # Bellek sınırı kontrolü
                memory[address] = registers[rt]
                update_memory_display()  # Belleği güncelle
            else:
                result_label.configure(text=f"Geçersiz bellek adresi: {address}", foreground="red")
                return

        elif parts[0] == "lw":  # I-Type lw
            rt, offset_rs = parts[1].rstrip(","), parts[2]
            offset, rs = offset_rs.split("(")
            rs = rs.rstrip(")")
            address = registers[rs] + int(offset)
            if 0 <= address < len(memory):  # Bellek sınırı kontrolü
                registers[rt] = memory[address]
            else:
                result_label.configure(text=f"Geçersiz bellek adresi: {address}", foreground="red")
                return

        elif parts[0] == "beq":  # I-Type beq
            rs, rt, label = parts[1].rstrip(","), parts[2].rstrip(","), parts[3]
            if registers[rs] == registers[rt]:
                if label in labels:
                    pc = labels[label]  # Etiketle yönlendir
                    realistic_pc = pc * 2  # Realistic PC'yi güncelle
                    update_pc_display()
                    update_instruction_memory_display()  # Dinamik olarak Instruction Memory'yi güncelle
                    update_register_display()

                    return
                else:
                    result_label.configure(text=f"Etiket bulunamadı: {label}", foreground="red")
                    return
            else:
                pc+=1
                realistic_pc+=2
                update_pc_display()
                return

        elif parts[0] == "bne":  # I-Type bne
            rs, rt, label = parts[1].rstrip(","), parts[2].rstrip(","), parts[3]
            if registers[rs] != registers[rt]:
                if label in labels:
                    pc = labels[label]  # Etiketle yönlendir
                    realistic_pc = pc * 2  # Realistic PC'yi güncelle
                    update_pc_display()
                    update_instruction_memory_display()  # Instruction Memory'yi güncelle
                    update_register_display()
                   
                    return
                else:
                    result_label.configure(text=f"Etiket bulunamadı: {label}", foreground="red")
                    return
            pc+=1
            realistic_pc +=1
            update_memory_display()

        elif parts[0] == "j":  # J-Type j
            label = parts[1]
            if label in labels:
                pc = labels[label]
                realistic_pc = pc * 2  # Realistic PC'yi güncelle
                update_pc_display()
                update_register_display()
           
                return
            else:
                result_label.configure(text=f"Etiket bulunamadı: {label}", foreground="red")
                return

        elif parts[0] == "jal":  # J-Type jal
            label = parts[1]
            if label in labels:
                registers["$ra"] = pc + 1  # Return Address
                pc = labels[label]
                realistic_pc = pc * 2  # Realistic PC'yi güncelle
                update_pc_display()
                update_register_display()
              
                return
            else:
                result_label.configure(text=f"Etiket bulunamadı: {label}", foreground="red")
                return

        elif parts[0] == "jr":  # J-Type jr
            rs = parts[1]
            pc = registers[rs]
            realistic_pc = pc * 2  # Realistic PC'yi güncelle
            update_pc_display()
            update_instruction_memory_display()
            update_register_display()
 
            result_label.configure(text=f"Komut işlendi: jr {rs} (Realistic PC: {realistic_pc})", foreground="blue")  # Doğru değeri yazdır
            return

        else:
            result_label.configure(text=f"Geçersiz komut: {instruction}", foreground="red")
            return
    except KeyError:
        result_label.configure(text=f"Register hatası: {instruction}", foreground="red")
        return
    except ValueError:
        result_label.configure(text=f"Geçersiz değer: {instruction}", foreground="red")
        return

    pc += 1  # Bir sonraki komuta geç
    realistic_pc +=2
    update_pc_display()
    update_register_display()
    update_instruction_memory_display()
   
    result_label.configure(text=f"Komut işlendi: {instruction}", foreground="blue")

        # Dallanma kontrolü ile Instruction Memory güncelleme
    if pc in labels.values():
        update_instruction_memory_display()


def run_command():
    global pc, realistic_pc

    executed_instructions = 0  # İşlenen komutları takip etmek için sayaç

    while True:
        instruction = fetch_instruction(pc)  # Instruction Memory'den komut al
        if instruction is None or instruction.strip() == "":
            result_label.configure(text=f"Program sonlandı. İşlenen komut sayısı: {executed_instructions}. Realistic PC: {realistic_pc}", foreground="green")
            break

        parts = instruction.strip().split()  # Komut parçalarını ayır

        try:
            if parts[0] == "add":  # R-Type add
                rd, rs, rt = parts[1].rstrip(","), parts[2].rstrip(","), parts[3]
                registers[rd] = registers[rs] + registers[rt]
            elif parts[0] == "sub":  # R-Type sub
                rd, rs, rt = parts[1].rstrip(","), parts[2].rstrip(","), parts[3]
                registers[rd] = registers[rs] - registers[rt]
            elif parts[0] == "and":  # R-Type and
                rd, rs, rt = parts[1].rstrip(","), parts[2].rstrip(","), parts[3]
                registers[rd] = registers[rs] & registers[rt]
            elif parts[0] == "or":  # R-Type or
                rd, rs, rt = parts[1].rstrip(","), parts[2].rstrip(","), parts[3]
                registers[rd] = registers[rs] | registers[rt]
            elif parts[0] == "slt":  # R-Type slt
                rd, rs, rt = parts[1].rstrip(","), parts[2].rstrip(","), parts[3]
                registers[rd] = 1 if registers[rs] < registers[rt] else 0
            elif parts[0] == "sll":  # R-Type sll
                rd, rt, shamt = parts[1].rstrip(","), parts[2].rstrip(","), int(parts[3])
                registers[rd] = registers[rt] << shamt
            elif parts[0] == "srl":  # R-Type srl
                rd, rt, shamt = parts[1].rstrip(","), parts[2].rstrip(","), int(parts[3])
                registers[rd] = registers[rt] >> shamt
            elif parts[0] == "addi":  # I-Type addi
                rt, rs, imm = parts[1].rstrip(","), parts[2].rstrip(","), int(parts[3])
                registers[rt] = registers[rs] + imm
            elif parts[0] == "sw":  # I-Type sw
                rt, offset_rs = parts[1].rstrip(","), parts[2]
                offset, rs = offset_rs.split("(")
                rs = rs.rstrip(")")
                address = registers[rs] + int(offset)
                memory[address] = registers[rt]
            elif parts[0] == "lw":  # I-Type lw
                rt, offset_rs = parts[1].rstrip(","), parts[2]
                offset, rs = offset_rs.split("(")
                rs = rs.rstrip(")")
                address = registers[rs] + int(offset)
                registers[rt] = memory[address]
            elif parts[0] == "beq":  # I-Type beq
                rs, rt, label = parts[1].rstrip(","), parts[2].rstrip(","), parts[3]
                if registers[rs] == registers[rt]:
                    if label in labels:
                        pc = labels[label]  # Etiketle yönlendir
                        realistic_pc = pc * 2  # Realistic PC'yi güncelle
                        update_pc_display()
                        update_instruction_memory_display()  # Dinamik olarak Instruction Memory'yi güncelle
                        update_register_display()

                        return
                    else:
                        result_label.configure(text=f"Etiket bulunamadı: {label}", foreground="red")
                        return
                else:
                    pc+=1
                    realistic_pc+=2
                    update_pc_display()
                    return
            elif parts[0] == "bne":  # I-Type bne
                rs, rt, label = parts[1].rstrip(","), parts[2].rstrip(","), parts[3]
                if registers[rs] != registers[rt]:
                    if label in labels:
                        pc = labels[label]
                        realistic_pc = pc * 2
                        continue
            elif parts[0] == "j":  # J-Type j
                label = parts[1]
                if label in labels:
                    pc = labels[label]
                    realistic_pc = pc * 2
                    continue
            elif parts[0] == "jal":  # J-Type jal
                label = parts[1]
                if label in labels:
                    registers["$ra"] = pc + 1
                    pc = labels[label]
                    realistic_pc = pc * 2
                    continue
            elif parts[0] == "jr":  # J-Type jr
                rs = parts[1]
                pc = registers[rs]
                realistic_pc = pc * 2
                continue
            else:
                result_label.configure(text=f"Geçersiz komut: {instruction}", foreground="red")
                break
        except KeyError:
            result_label.configure(text=f"Register hatası: {instruction}", foreground="red")
            break
        except ValueError:
            result_label.configure(text=f"Geçersiz değer: {instruction}", foreground="red")
            break

        pc += 1
        realistic_pc = pc * 2
        executed_instructions += 1

    update_pc_display()
    update_register_display()
    update_instruction_memory_display()

# Register ekranını güncelleyen fonksiyon
def update_register_display():
    for i, name in enumerate(register_names):
        register_labels[i].configure(text=f"{name}: {registers[name]}")

# Register ekranını güncelleyen fonksiyon
def update_memory_display():
    memory_text.delete("1.0", tk.END)
    for i in range(0, len(memory), 4):  # 4 byte'lık bloklar halinde göster
        values = " ".join(f"{val:03}" for val in memory[i:i+4])
        memory_text.insert(tk.END, f"{i:03}: {values}\n")

def load_instruction_memory():
    global instruction_memory
    commands = input_text.get("1.0", tk.END).strip().split("\n")
    for i, command in enumerate(commands):
        if i < len(instruction_memory):
            instruction_memory[i] = command.strip()
        else:
            result_label.configure(text="Instruction Memory kapasitesini aştınız!", foreground="red")
            return
    result_label.configure(text="Instruction Memory yüklendi!", foreground="blue")
    update_instruction_memory_display()

def fetch_instruction(pc):
    if 0 <= pc < len(instruction_memory):
        instruction = instruction_memory[pc].strip()
        if instruction:  # Eğer komut boş değilse
            return instruction
        else:
            return None  # Boş komut durumunda None döner
    else:
        result_label.configure(text="Instruction Memory sınırını aştınız!", foreground="red")
        return None


def update_pc_display():
    realistic_pc_value_label.configure(text=f"Realistic PC: {realistic_pc:03}")

def update_instruction_memory_display():
    instruction_memory_text.delete("1.0", tk.END)  # Instruction Memory ekranını temizle

    # Eğer PC bir dallanma etiketine işaret ediyorsa, dallanma kontrolü yap
    if pc in labels.values():  # Eğer mevcut PC bir etikete işaret ediyorsa
        label_name = next((key for key, value in labels.items() if value == pc), None)
        if label_name:
            # Dallanma gerçekleşti, yalnızca dallanılan komutları göster
            instruction_memory_text.insert(tk.END, f"Dallanma: {label_name}\n", "branch")
            for i in range(pc, len(instruction_memory)):
                instruction = instruction_memory[i].strip()
                if instruction:  # Boş olmayan talimatlar için
                    instruction_memory_text.insert(tk.END, f"{i:03}: {instruction}\n", "executed")
            return  # Dallanma sonrası geri kalan komutları gösterme

    # Eğer dallanma gerçekleşmemişse, talimatları sırayla göster
    for i, instruction in enumerate(instruction_memory):
        if instruction.strip():  # Boş olmayan talimatlar için
            
            instruction_memory_text.insert(tk.END, f"{i:03}: {instruction}\n", "normal")

    # Pipeline'daki talimatları belirle
    for stage in pipeline_stages.values():
        if stage != "Empty":
            try:
                instruction_index = instruction_memory.index(stage.strip())
            except ValueError:
                continue

    # Atlanan talimatları belirlemek için dallanma kontrolü
    pc_values = [pc]  # Mevcut dallanma sonrası PC değerlerini kaydedin
    for i, instruction in enumerate(instruction_memory):
        if instruction.strip() and (instruction.startswith("beq") or instruction.startswith("bne") or instruction.startswith("j")):
            parts = instruction.split()
            label = parts[-1]  # Etiketin adı
            if label in labels:
                target_index = labels[label]
                if target_index > i:  # İleriye doğru bir dallanma varsa
                    pc_values.append(target_index)

   

def load_all():
    global labels, instruction_memory, pc
    # Komutları çok satırlı girişten alın
    instructions = input_text.get("1.0", tk.END).strip().split("\n")  # Input alanından komutlar
    labels = {}  # Etiketleri sıfırla
    pc = 0  # Program Counter'ı sıfırla
    realistic_pc = 0
    instruction_memory = [""] * 512  # Instruction Memory'yi sıfırla

    # Komutları Instruction Memory'ye yükle
    for i, instruction in enumerate(instructions):
        instruction = instruction.strip()
        if i < len(instruction_memory):
            if ":" in instruction:  # Eğer bir etiket varsa
                parts = instruction.split(":")
                label = parts[0].strip()  # Etiket ismini al
                labels[label] = i  # Etiketin bulunduğu satırı kaydet
                if len(parts) > 1 and parts[1].strip():  # Etiket sonrası komut varsa
                    instruction_memory[i] = parts[1].strip()  # Komut kısmını yükle
                else:
                    instruction_memory[i] = ""  # Sadece etiket varsa komut boş
            else:
                instruction_memory[i] = instruction  # Komutu doğrudan yükle
        else:
            result_label.configure(text="Instruction Memory kapasitesini aştınız!", foreground="red")
            return

    # Yükleme işlemi tamamlandı
    result_label.configure(text="Komutlar ve Instruction Memory yüklendi!", foreground="blue")
    update_instruction_memory_display()
    process_labels()
 


    # Komutları Instruction Memory'ye ve gerekli yapıya yükle
    for i, command in enumerate(commands):
        if i < len(instruction_memory):
            instruction_memory[i] = command
        else:
            break

    if instruction_memory[0].strip() == "":
        result_label.configure(text="İlk talimat boş, lütfen kontrol edin.", foreground="red")
        return


        # Etiketleri ayıkla ve komutları işle
        if ":" in command:  # Label kontrolü
            parts = command.split(":")
            label = parts[0].strip()
            labels[label] = i  # Etiketin bulunduğu satırı kaydet
            if len(parts) > 1 and parts[1].strip():  # Etiket sonrası komut varsa
                commands[i] = parts[1].strip()
            else:
                commands[i] = ""  # Etiketi temizle
        else:
            commands[i] = command

    result_label.configure(text="Komutlar ve Instruction Memory yüklendi!", foreground="blue")
    update_instruction_memory_display()



# Pipeline adımlarını tanımlama
def get_pipeline_stages(instruction):
    opcode = instruction.split()[0]
    if opcode in ["add", "sub", "and", "or", "slt"]:
        return ["IF", "ID", "EX", "WB"]
    elif opcode in ["sll", "srl"]:
        return ["IF", "ID", "EX", "WB"]
    elif opcode == "addi":
        return ["IF", "ID", "EX", "WB"]
    elif opcode == "lw":
        return ["IF", "ID", "EX", "MEM", "WB"]
    elif opcode == "sw":
        return ["IF", "ID", "EX", "MEM"]
    elif opcode in ["beq", "bne"]:
        return ["IF", "ID", "EX"]
    elif opcode == "j":
        return ["IF", "ID"]
    elif opcode == "jal":
        return ["IF", "ID", "WB"]
    elif opcode == "jr":
        return ["IF", "ID"]
    else:
        return []


def clear_pipeline():
    """Pipeline'ı temizlemek için tüm aşamaları 'Empty' yapar."""
    global pipeline_stages
    pipeline_stages = {"IF": "Empty", "ID": "Empty", "EX": "Empty", "MEM": "Empty", "WB": "Empty"}
    update_pipeline_stages()


def execute_instruction(instruction, write_back=False):
    global pc, realistic_pc
    parts = instruction.split()
    opcode = parts[0]

    try:
        if opcode == "add":
            rd, rs, rt = parts[1].rstrip(","), parts[2].rstrip(","), parts[3]
            registers[rd] = registers[rs] + registers[rt]
        elif opcode == "sub":
            rd, rs, rt = parts[1].rstrip(","), parts[2].rstrip(","), parts[3]
            registers[rd] = registers[rs] - registers[rt]
        elif opcode == "and":
            rd, rs, rt = parts[1].rstrip(","), parts[2].rstrip(","), parts[3]
            registers[rd] = registers[rs] & registers[rt]
        elif opcode == "or":
            rd, rs, rt = parts[1].rstrip(","), parts[2].rstrip(","), parts[3]
            registers[rd] = registers[rs] | registers[rt]
        elif opcode == "addi":
            rt, rs, imm = parts[1].rstrip(","), parts[2].rstrip(","), int(parts[3])
            registers[rt] = registers[rs] + imm
        elif opcode == "lw":
            rt, offset_rs = parts[1].rstrip(","), parts[2]
            offset, rs = offset_rs.split("(")
            rs = rs.rstrip(")")
            address = registers[rs] + int(offset)
            registers[rt] = memory[address]
        elif opcode == "sw":
            rt, offset_rs = parts[1].rstrip(","), parts[2]
            offset, rs = offset_rs.split("(")
            rs = rs.rstrip(")")
            address = registers[rs] + int(offset)
            memory[address] = registers[rt]
        elif opcode == "beq":
            rs, rt, label = parts[1].rstrip(","), parts[2].rstrip(","), parts[3]
            if registers[rs] == registers[rt] and label in labels:
                pc = labels[label]
                realistic_pc = pc * 2
                return
        elif opcode == "bne":
            rs, rt, label = parts[1].rstrip(","), parts[2].rstrip(","), parts[3]
            if registers[rs] != registers[rt] and label in labels:
                pc = labels[label]
                realistic_pc = pc * 2
                return
        elif opcode == "jal":  # J-Type jal
            label = parts[1]
            if label in labels:
                registers["R7"] = pc + 1  # R7'ye dönüş adresini (pc + 1) yaz
                pc = labels[label]  # Hedef etikete dallan
                realistic_pc = pc * 2
                return
            else:
                result_label.configure(text=f"Etiket bulunamadı: {label}", foreground="red")
                return

        elif opcode == "jr":  # J-Type jr
            rs = parts[1]
            if rs in registers:
                if registers[rs] == pc:  # Eğer aynı adrese dallanıyorsa, döngüyü kır
                    result_label.configure(text="Sonsuz döngü algılandı, bir sonraki komuta geçiliyor.", foreground="red")
                    pc += 1  # Bir sonraki komuta geç
                else:
                    pc = registers[rs]  # Register'daki adrese dallan
                realistic_pc = pc * 2
                return
            else:
                result_label.configure(text=f"Register bulunamadı: {rs}", foreground="red")
                return

        elif opcode == "j":  # J-Type j
            label = parts[1]
            if label in labels:
                pc = labels[label]
                realistic_pc = pc * 2
                return
            else:
                result_label.configure(text=f"Etiket bulunamadı: {label}", foreground="red")
                return



        elif opcode == "slt":
            rd, rs, rt = parts[1].rstrip(","), parts[2].rstrip(","), parts[3]
            registers[rd] = 1 if registers[rs] < registers[rt] else 0
        elif opcode == "srl":
            rd, rt, shamt = parts[1].rstrip(","), parts[2].rstrip(","), int(parts[3])
            registers[rd] = registers[rt] >> shamt
        elif opcode == "sll":
            rd, rt, shamt = parts[1].rstrip(","), parts[2].rstrip(","), int(parts[3])
            registers[rd] = registers[rt] << shamt

        # Güncelleme
        update_register_display()
        update_memory_display()
        update_pc_display()

    except KeyError as e:
        result_label.configure(text=f"Hata: Yanlış register ismi ({e})", foreground="red")
    except IndexError:
        result_label.configure(text="Hata: Eksik parametre", foreground="red")
    except ValueError:
        result_label.configure(text="Hata: Geçersiz sayı formatı", foreground="red")

    pc += 1  # Program counter'ı artır
    realistic_pc = pc * 2  # Realistic PC'yi güncelle



# Pipeline aşamalarını güncelleyen fonksiyon
def update_pipeline_stages():
    pipeline_text.delete("1.0", tk.END)
    for stage, instruction in pipeline_stages.items():
        pipeline_text.insert(tk.END, f"{stage}: {instruction or 'Empty'}\n")


def detect_hazards():
    hazards.clear()

    # Veri hazardlarını kontrol etmek için tüm pipeline aşamalarını analiz et
    pipeline_order = ["IF", "ID", "EX", "MEM", "WB"]

    for i, stage1 in enumerate(pipeline_order):
        for j, stage2 in enumerate(pipeline_order):
            if j <= i:  # Sadece sonraki aşamaları kontrol et
                continue
            if pipeline_stages[stage1] and pipeline_stages[stage2]:
                # Her iki aşamada bir komut varsa, register bağımlılığını kontrol et
                parts1 = pipeline_stages[stage1].split()
                parts2 = pipeline_stages[stage2].split()

                # Eğer iki komut bir register üzerinde bağımlıysa, data hazard oluştur
                if len(parts1) > 1 and len(parts2) > 1:
                    reg1 = parts1[1]  # İlk register'ı al
                    if reg1 in parts2[1:]:
                        hazards.append(f"Data hazard detected between {stage1} and {stage2}: {reg1}")

    # Kontrol hazardlarını kontrol et
    if pipeline_stages["IF"]:
        # Dallanma komutlarını IF aşamasında kontrol et
        if any(pipeline_stages["IF"].startswith(branch) for branch in ["beq", "bne", "j", "jal"]):
            hazards.append("Control hazard detected in IF stage due to branching.")

    # Pipeline'daki tüm aşamaları analiz ederek bağımlılıkları yakala
    registers_in_stages = {}
    for stage, instruction in pipeline_stages.items():
        if instruction:
            parts = instruction.split()
            if len(parts) > 1:
                reg = parts[1]
                if reg in registers_in_stages:
                    hazards.append(
                        f"Pipeline stall required: {reg} used in {stage} and {registers_in_stages[reg]}"
                    )
                registers_in_stages[reg] = stage

    # Hazard ekranını güncelle
    update_hazard_display()



def update_hazard_display():
    hazard_text.delete("1.0", tk.END)
    if hazards:
        for hazard in hazards:
            hazard_text.insert(tk.END, f"{hazard}\n")
    else:
        hazard_text.insert(tk.END, "No hazards detected.\n")

# Tek bir komutu işleyen ve pipeline'a entegre eden fonksiyon
def step_pipeline():
    global pc, realistic_pc, hazards

    # WB aşamasındaki talimatı çalıştır
    if pipeline_stages["WB"] != "Empty":
        execute_instruction(pipeline_stages["WB"], write_back=True)
        pipeline_stages["WB"] = "Empty"  # WB aşamasını boşalt

    # Pipeline aşamalarını kaydır
    pipeline_stages["WB"] = pipeline_stages["MEM"]
    pipeline_stages["MEM"] = pipeline_stages["EX"]
    pipeline_stages["EX"] = pipeline_stages["ID"]
    pipeline_stages["ID"] = pipeline_stages["IF"]

    # Yeni talimatı IF aşamasına yükle
    if pc < len(instruction_memory) and instruction_memory[pc].strip():
        pipeline_stages["IF"] = instruction_memory[pc]
        pc += 1
        realistic_pc += 2
    else:
        pipeline_stages["IF"] = "Empty"

    # Hazardları kontrol et ve güncelle
    detect_hazards()
    update_pipeline_stages()
    update_register_display()
    update_memory_display()
    update_pc_display()




# Pipeline ve Register Arasındaki GUI Sentezi
def update_pc_display():
    realistic_pc_value_label.configure(text=f"Realistic PC: {realistic_pc:03}")



def create_gui():
    global root, input_text, register_labels, memory_text, pipeline_text
    global instruction_memory_text, hazard_text, realistic_pc_value_label, result_label

    root = ttkthemes.ThemedTk()
    root.set_theme("equilux")  # Modern koyu tema
    root.title("16-bit RISC Processor Simulator")
    root.configure(bg='#1E1E1E')  # Arka plan koyu gri

    # Ana çerçeve
    main_frame = tk.Frame(root, bg='#1E1E1E')
    main_frame.pack(padx=20, pady=20, fill="both", expand=True)

    # Sol panel (Input ve Kontroller)
    left_panel = tk.Frame(main_frame, bg='#2B2B2B', relief="groove", bd=2)
    left_panel.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

    tk.Label(left_panel, text="Assembly Code Input", font=('Arial', 12, 'bold'), bg='#2B2B2B', fg='white').pack(anchor="w", pady=5)
    input_text = tk.Text(left_panel, width=40, height=20, font=('Consolas', 11), bg='#FFFFFF', fg='black')
    input_text.pack(padx=5, pady=5)

    button_frame = tk.Frame(left_panel, bg='#2B2B2B')
    button_frame.pack(pady=10)

    ttk.Button(button_frame, text="Load Program", command=load_commands).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Step Forward", command=step_pipeline).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Run All", command=run_command).pack(side=tk.LEFT, padx=5)

    # Result Label (Sonuç Mesajı)
    result_label = tk.Label(root, text="", font=('Arial', 11), bg='#1E1E1E', fg='white')
    result_label.pack(pady=10)

    # Register ekranı
    register_frame = tk.Frame(main_frame, bg='#2E7D32', relief="groove", bd=2)
    register_frame.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")

    tk.Label(register_frame, text="Registers", font=('Arial', 12, 'bold'), bg='#2E7D32', fg='white').pack(anchor="w", pady=5)

    register_labels = []
    for name in ["R0", "R1", "R2", "R3", "R4", "R5", "R6", "R7"]:
        value_label = tk.Label(register_frame, text="0", width=10, anchor="w", font=('Consolas', 10), bg='#2E7D32', fg='white')
        value_label.pack(pady=2, padx=5)
        register_labels.append(value_label)


    # Memory alanı
    memory_frame = tk.Frame(main_frame, bg='#4A148C', relief="groove", bd=2)
    memory_frame.grid(row=0, column=2, padx=15, pady=15, sticky="nsew")

    tk.Label(memory_frame, text="Data Memory", font=('Arial', 12, 'bold'), bg='#4A148C', fg='white').pack(anchor="w", pady=5)
    memory_text = tk.Text(memory_frame, width=35, height=15, font=('Consolas', 11), bg='#FFFFFF', fg='black')
    memory_text.pack(fill=tk.BOTH, expand=True)

    # Instruction Memory
    instruction_memory_frame = tk.Frame(main_frame, bg='#6A1B9A', relief="groove", bd=2)
    instruction_memory_frame.grid(row=0, column=3, padx=15, pady=15, sticky="nsew")

    tk.Label(instruction_memory_frame, text="Instruction Memory", font=('Arial', 12, 'bold'), bg='#6A1B9A', fg='white').pack(anchor="w", pady=5)
    instruction_memory_text = tk.Text(instruction_memory_frame, width=35, height=20, font=('Consolas', 11), bg='#FFFFFF', fg='black')
    instruction_memory_text.pack(fill=tk.BOTH, expand=True)

    # Pipeline ekranı
    pipeline_frame = tk.Frame(main_frame, bg='#424242', relief="groove", bd=2)
    pipeline_frame.grid(row=1, column=0, columnspan=2, padx=15, pady=15, sticky="nsew")

    tk.Label(pipeline_frame, text="Pipeline Stages", font=('Arial', 12, 'bold'), bg='#424242', fg='white').pack(anchor="w", pady=5)
    pipeline_text = tk.Text(pipeline_frame, width=80, height=10, font=('Consolas', 11), bg='#212121', fg='#00FF00')
    pipeline_text.pack(fill=tk.BOTH, expand=True)

    # Hazards alanı
    hazards_frame = tk.Frame(main_frame, bg='#424242', relief="groove", bd=2)
    hazards_frame.grid(row=1, column=2, padx=15, pady=15, sticky="nsew")

    tk.Label(hazards_frame, text="Hazards", font=('Arial', 12, 'bold'), bg='#424242', fg='white').pack(anchor="w", pady=5)
    hazard_text = tk.Text(hazards_frame, width=50, height=10, font=('Consolas', 11), bg='#212121', fg='#FF5722')
    hazard_text.pack(fill=tk.BOTH, expand=True)

    # Program Counter
    pc_frame = tk.Frame(main_frame, bg='#FBC02D', relief="groove", bd=2)
    pc_frame.grid(row=1, column=3, padx=15, pady=15, sticky="nsew")

    tk.Label(pc_frame, text="Program Counter", font=('Arial', 12, 'bold'), bg='#FBC02D', fg='black').pack(anchor="center", pady=5)
    realistic_pc_value_label = tk.Label(pc_frame, text="Realistic PC: 000", font=('Consolas', 12), bg='#FBC02D', fg='black')
    realistic_pc_value_label.pack(anchor="center", pady=5)

    return root


# GUI oluşturma ve başlatma
root = create_gui()
root.mainloop()
