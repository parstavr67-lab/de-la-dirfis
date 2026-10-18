import sqlite3
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import messagebox, ttk

# ==========================================
# ΕΚΤΡΟΦΕΙΟ DE LA DIRFIS
# ==========================================

DB_NAME = "de_la_dirfis.db"


# ==========================================
# ΒΑΣΗ ΔΕΔΟΜΕΝΩΝ
# ==========================================

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# Πίνακας Σκύλων Εκτροφείου
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS dogs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    sex TEXT,
    birth_date TEXT,
    microchip TEXT,
    pedigree TEXT,
    father TEXT,
    mother TEXT,
    breeder TEXT,
    color TEXT,
    notes TEXT
)
"""
)

# Πίνακας Εκπαίδευσης Πελατών
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS trainings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    city TEXT,
    dog_name TEXT NOT NULL,
    dog_breed TEXT,
    training_type TEXT,
    start_date TEXT,
    end_date TEXT,
    status TEXT,
    total_cost REAL,
    advance_payment REAL,
    notes TEXT
)
"""
)

# Πίνακας Ζευγαρωμάτων
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS matings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    male_dog TEXT NOT NULL,
    female_dog TEXT NOT NULL,
    mating_date TEXT NOT NULL,
    expected_birth_date TEXT,
    status TEXT,
    notes TEXT
)
"""
)

# Πίνακας Γεννών
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS litters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mating_info TEXT NOT NULL,
    birth_date TEXT NOT NULL,
    males_count INTEGER,
    females_count INTEGER,
    total_puppies INTEGER,
    notes TEXT
)
"""
)

# Πίνακας Μεμονωμένων Κουταβιών
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS puppies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    litter_info TEXT NOT NULL,
    name TEXT,
    sex TEXT,
    color TEXT,
    microchip TEXT,
    status TEXT,
    price REAL,
    deposit REAL,
    buyer_name TEXT,
    buyer_phone TEXT,
    notes TEXT
)
"""
)

# Πίνακας Ενδιαφερομένων / Πελατών (Λίστα Αναμονής)
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    city TEXT,
    pref_sex TEXT,
    pref_color TEXT,
    purpose TEXT,
    deposit REAL,
    status TEXT,
    notes TEXT
)
"""
)

# Πίνακας Οικονομικών / Συναλλαγών
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trans_date TEXT NOT NULL,
    trans_type TEXT NOT NULL, -- 'Έσοδο' ή 'Έξοδο'
    category TEXT,
    amount REAL NOT NULL,
    payment_method TEXT,
    description TEXT,
    notes TEXT
)
"""
)

conn.commit()


# ==========================================
# ΚΕΝΤΡΙΚΟ ΠΑΡΑΘΥΡΟ
# ==========================================

window = tk.Tk()
window.title("Εκτροφείο de la Dirfis")
window.geometry("1000x700")
window.minsize(900, 600)



# ==========================================
# ΓΕΝΙΚΗ ΠΡΟΣΩΠΙΚΗ ΚΑΡΤΕΛΑ ΓΙΑ ΟΛΕΣ ΤΙΣ ΕΝΟΤΗΤΕΣ
# ==========================================

def open_record_card(table_name, record_id, title_text):
    """Ανοίγει προσωπική καρτέλα μιας εγγραφής και επιτρέπει την αποθήκευση αλλαγών."""
    allowed_tables = {
        "dogs": "Σκύλου",
        "matings": "Ζευγαρώματος",
        "litters": "Γέννας",
        "puppies": "Κουταβιού",
        "clients": "Πελάτη / Ενδιαφερόμενου",
        "trainings": "Εκπαίδευσης",
        "transactions": "Συναλλαγής",
    }

    if table_name not in allowed_tables:
        messagebox.showerror("Σφάλμα", "Μη έγκυρη καρτέλα.")
        return

    try:
        cursor.execute(f"PRAGMA table_info({table_name})")
        table_info = cursor.fetchall()
        columns = [row[1] for row in table_info]
        if not columns:
            messagebox.showerror("Σφάλμα", "Δεν βρέθηκαν στοιχεία της καρτέλας.")
            return

        cursor.execute(
            f"SELECT {', '.join(columns)} FROM {table_name} WHERE id = ?",
            (record_id,),
        )
        row = cursor.fetchone()
        if row is None:
            messagebox.showerror("Σφάλμα", "Η εγγραφή δεν βρέθηκε.")
            return
    except Exception as e:
        messagebox.showerror("Σφάλμα", f"Δεν ήταν δυνατό να ανοίξει η καρτέλα:\n{e}")
        return

    card = tk.Toplevel(window)
    card.title(f"📋 {title_text}")
    card.geometry("760x700")
    card.minsize(650, 550)
    card.transient(window)

    title = tk.Label(
        card,
        text=f"📋 {title_text}",
        font=("Arial", 20, "bold"),
    )
    title.pack(pady=(12, 4))

    subtitle = tk.Label(
        card,
        text=f"ID εγγραφής: {record_id}",
        font=("Arial", 10),
    )
    subtitle.pack(pady=(0, 10))

    outer = tk.Frame(card)
    outer.pack(fill="both", expand=True, padx=20, pady=5)

    canvas = tk.Canvas(outer, highlightthickness=0)
    scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
    form = tk.Frame(canvas)

    form.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=form, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    labels = {
        "id": "ID",
        "name": "Όνομα",
        "sex": "Φύλο",
        "birth_date": "Ημερομηνία γέννησης",
        "microchip": "Microchip",
        "pedigree": "Pedigree",
        "father": "Πατέρας",
        "mother": "Μητέρα",
        "breeder": "Εκτροφέας",
        "color": "Χρώμα",
        "notes": "Σημειώσεις",
        "male_dog": "Αρσενικός (Πατέρας)",
        "female_dog": "Θηλυκιά (Μητέρα)",
        "mating_date": "Ημερομηνία ζεύξης",
        "expected_birth_date": "Πιθανή ημερομηνία γέννας",
        "status": "Κατάσταση",
        "mating_info": "Ζευγάρωμα",
        "birth_date": "Ημερομηνία γέννας",
        "males_count": "Αρσενικά κουτάβια",
        "females_count": "Θηλυκά κουτάβια",
        "total_puppies": "Σύνολο κουταβιών",
        "litter_info": "Γέννα",
        "price": "Τιμή (€)",
        "deposit": "Προκαταβολή (€)",
        "buyer_name": "Αγοραστής",
        "buyer_phone": "Τηλέφωνο αγοραστή",
        "full_name": "Ονοματεπώνυμο",
        "phone": "Τηλέφωνο",
        "email": "Email",
        "city": "Περιοχή / Πόλη",
        "pref_sex": "Επιθυμητό φύλο",
        "pref_color": "Επιθυμητό χρώμα",
        "purpose": "Σκοπός χρήσης",
        "client_name": "Ονοματεπώνυμο πελάτη",
        "dog_name": "Όνομα σκύλου",
        "dog_breed": "Ράτσα / Φυλή",
        "training_type": "Είδος εκπαίδευσης",
        "start_date": "Έναρξη",
        "end_date": "Λήξη",
        "total_cost": "Συνολικό κόστος (€)",
        "advance_payment": "Προκαταβολή (€)",
        "trans_date": "Ημερομηνία",
        "trans_type": "Τύπος",
        "category": "Κατηγορία",
        "amount": "Ποσό (€)",
        "payment_method": "Τρόπος πληρωμής",
        "description": "Περιγραφή",
    }

    variables = {}
    text_widgets = {}

    for row_index, (column, value) in enumerate(zip(columns, row)):
        if column == "id":
            continue

        label_text = labels.get(column, column.replace("_", " ").title())

        tk.Label(
            form,
            text=f"{label_text}:",
            font=("Arial", 10, "bold"),
            width=25,
            anchor="e",
        ).grid(row=row_index, column=0, padx=8, pady=6, sticky="ne")

        # Οι σημειώσεις παίρνουν μεγάλο πεδίο πολλών γραμμών.
        if column == "notes":
            widget = tk.Text(form, width=48, height=5, font=("Arial", 10))
            widget.insert("1.0", "" if value is None else str(value))
            widget.grid(row=row_index, column=1, padx=8, pady=6, sticky="w")
            text_widgets[column] = widget
        else:
            var = tk.StringVar(value="" if value is None else str(value))
            variables[column] = var

            # Κρατάμε το ID μόνο για εμφάνιση και δεν το επιτρέπουμε να αλλάξει.
            widget = tk.Entry(
                form,
                textvariable=var,
                width=50,
                font=("Arial", 10),
            )
            widget.grid(row=row_index, column=1, padx=8, pady=6, sticky="w")

    def save_changes():
        values = []
        update_columns = []

        for column in columns:
            if column == "id":
                continue

            if column in text_widgets:
                value = text_widgets[column].get("1.0", tk.END).strip()
            else:
                value = variables[column].get().strip()

            update_columns.append(column)
            values.append(value)

        try:
            set_clause = ", ".join(f"{column} = ?" for column in update_columns)
            cursor.execute(
                f"UPDATE {table_name} SET {set_clause} WHERE id = ?",
                values + [record_id],
            )
            conn.commit()

            messagebox.showinfo(
                "Επιτυχία",
                f"Οι αλλαγές στην καρτέλα αποθηκεύτηκαν επιτυχώς.",
                parent=card,
            )
            card.destroy()

            # Ενημέρωση των ανοιχτών λιστών, όπου υπάρχει refresh function.
            try:
                if table_name == "dogs":
                    load_dogs()
                elif table_name == "matings":
                    load_matings()
                elif table_name == "litters":
                    load_litters()
                elif table_name == "puppies":
                    load_puppies()
                elif table_name == "clients":
                    load_clients()
                elif table_name == "trainings":
                    load_trainings()
                elif table_name == "transactions":
                    load_transactions()
            except Exception:
                pass

        except Exception as e:
            messagebox.showerror(
                "Σφάλμα",
                f"Δεν αποθηκεύτηκαν οι αλλαγές:\n\n{e}",
                parent=card,
            )

    def print_card():
        """Εκτυπώνει την τρέχουσα καρτέλα μέσω του προεπιλεγμένου εκτυπωτή των Windows."""
        import os
        import tempfile

        try:
            lines = [
                "ΕΚΤΡΟΦΕΙΟ de la Dirfis",
                "=" * 70,
                f"ΚΑΡΤΕΛΑ: {title_text}",
                f"ID εγγραφής: {record_id}",
                "=" * 70,
                "",
            ]

            for column in columns:
                if column == "id":
                    continue

                label_text = labels.get(column, column.replace("_", " ").title())

                if column in text_widgets:
                    value = text_widgets[column].get("1.0", tk.END).strip()
                else:
                    value = variables[column].get().strip()

                lines.append(f"{label_text}:")
                lines.append(value if value else "-")
                lines.append("")

            lines.extend([
                "=" * 70,
                "Εκτύπωση από το Εκτροφείο de la Dirfis",
                datetime.now().strftime("Ημερομηνία εκτύπωσης: %d/%m/%Y %H:%M"),
            ])

            fd, file_path = tempfile.mkstemp(
                prefix="de_la_dirfis_",
                suffix=".txt",
            )
            os.close(fd)

            with open(file_path, "w", encoding="utf-8-sig") as f:
                f.write("\n".join(lines))

            try:
                os.startfile(file_path, "print")
                messagebox.showinfo(
                    "Εκτύπωση",
                    "Η καρτέλα στάλθηκε για εκτύπωση στον προεπιλεγμένο εκτυπωτή των Windows.",
                    parent=card,
                )
            except Exception as print_error:
                messagebox.showerror(
                    "Σφάλμα εκτύπωσης",
                    "Δεν ήταν δυνατή η αυτόματη εκτύπωση.\n\n"
                    f"{print_error}\n\n"
                    "Το αρχείο εκτύπωσης δημιουργήθηκε προσωρινά και μπορείς να το ανοίξεις.",
                    parent=card,
                )

        except Exception as e:
            messagebox.showerror(
                "Σφάλμα",
                f"Δεν δημιουργήθηκε το αρχείο εκτύπωσης:\n\n{e}",
                parent=card,
            )

    buttons = tk.Frame(card)
    buttons.pack(pady=10)

    tk.Button(
        buttons,
        text="💾 Αποθήκευση αλλαγών",
        command=save_changes,
        font=("Arial", 11, "bold"),
        width=22,
    ).grid(row=0, column=0, padx=6)

    tk.Button(
        buttons,
        text="🖨 Εκτύπωση",
        command=print_card,
        font=("Arial", 11, "bold"),
        width=16,
    ).grid(row=0, column=1, padx=6)

    tk.Button(
        buttons,
        text="✖ Κλείσιμο",
        command=card.destroy,
        font=("Arial", 11, "bold"),
        width=16,
    ).grid(row=0, column=2, padx=6)

    # Διπλό κλικ σε οποιοδήποτε πεδίο της καρτέλας δεν κλείνει τίποτα.
    card.grab_set()
    card.focus_set()


# ==========================================
# ΕΝΟΤΗΤΑ: ΣΚΥΛΟΙ ΕΚΤΡΟΦΕΙΟΥ
# ==========================================


def open_dogs():
    dogs_window = tk.Toplevel(window)
    dogs_window.title("Σκύλοι - Εκτροφείο de la Dirfis")
    dogs_window.geometry("1100x750")
    dogs_window.minsize(950, 650)

    title = tk.Label(
        dogs_window, text="🐕 ΣΚΥΛΟΙ ΕΚΤΡΟΦΕΙΟΥ", font=("Arial", 22, "bold")
    )
    title.pack(pady=10)

    form = tk.Frame(dogs_window)
    form.pack(pady=5)

    name_var = tk.StringVar()
    sex_var = tk.StringVar()
    birth_var = tk.StringVar()
    chip_var = tk.StringVar()
    pedigree_var = tk.StringVar()
    father_var = tk.StringVar()
    mother_var = tk.StringVar()
    breeder_var = tk.StringVar()
    color_var = tk.StringVar()
    search_var = tk.StringVar()

    def add_field(frame, row, col, label, variable):
        tk.Label(frame, text=label, font=("Arial", 10, "bold")).grid(
            row=row, column=col, sticky="e", padx=6, pady=4
        )
        tk.Entry(frame, textvariable=variable, width=30, font=("Arial", 10)).grid(
            row=row, column=col + 1, padx=6, pady=4, sticky="w"
        )

    add_field(form, 0, 0, "Όνομα:", name_var)
    add_field(form, 1, 0, "Ημερομηνία γέννησης:", birth_var)
    add_field(form, 2, 0, "Microchip:", chip_var)
    add_field(form, 3, 0, "Αριθμός Pedigree:", pedigree_var)
    add_field(form, 4, 0, "Πατέρας:", father_var)

    tk.Label(form, text="Φύλο:", font=("Arial", 10, "bold")).grid(
        row=0, column=2, sticky="e", padx=6, pady=4
    )
    sex_combo = ttk.Combobox(
        form,
        textvariable=sex_var,
        values=["Αρσενικό", "Θηλυκό"],
        state="readonly",
        width=28,
        font=("Arial", 10),
    )
    sex_combo.grid(row=0, column=3, padx=6, pady=4, sticky="w")

    add_field(form, 1, 2, "Μητέρα:", mother_var)
    add_field(form, 2, 2, "Εκτροφέας:", breeder_var)
    add_field(form, 3, 2, "Χρώμα:", color_var)

    tk.Label(form, text="Σημειώσεις:", font=("Arial", 10, "bold")).grid(
        row=4, column=2, sticky="ne", padx=6, pady=4
    )
    notes_text = tk.Text(form, width=30, height=3, font=("Arial", 10))
    notes_text.grid(row=4, column=3, padx=6, pady=4, sticky="w")

    search_frame = tk.Frame(dogs_window)
    search_frame.pack(fill="x", padx=20, pady=(10, 0))

    tk.Label(
        search_frame, text="🔍 Αναζήτηση:", font=("Arial", 10, "bold")
    ).pack(side="left", padx=(0, 5))
    search_entry = tk.Entry(
        search_frame, textvariable=search_var, font=("Arial", 10), width=35
    )
    search_entry.pack(side="left")

    list_frame = tk.Frame(dogs_window)
    list_frame.pack(fill="both", expand=True, padx=20, pady=10)

    columns = (
        "id",
        "name",
        "sex",
        "birth",
        "microchip",
        "pedigree",
        "father",
        "mother",
    )
    tree = ttk.Treeview(
        list_frame, columns=columns, show="headings", selectmode="browse"
    )

    tree.heading("id", text="ID")
    tree.heading("name", text="Όνομα")
    tree.heading("sex", text="Φύλο")
    tree.heading("birth", text="Γέννηση")
    tree.heading("microchip", text="Microchip")
    tree.heading("pedigree", text="Pedigree")
    tree.heading("father", text="Πατέρας")
    tree.heading("mother", text="Μητέρα")

    tree.column("id", width=40, anchor="center")
    tree.column("name", width=130)
    tree.column("sex", width=90, anchor="center")
    tree.column("birth", width=100, anchor="center")
    tree.column("microchip", width=130)
    tree.column("pedigree", width=120)
    tree.column("father", width=120)
    tree.column("mother", width=120)

    scrollbar = ttk.Scrollbar(
        list_frame, orient="vertical", command=tree.yview
    )
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def open_selected_record(event=None):
        selected = tree.selection()
        if not selected:
            return
        item = tree.item(selected[0])
        values = item.get("values", [])
        if not values:
            return
        record_id = values[0]
        try:
            record_id = int(record_id)
        except (TypeError, ValueError):
            return
        open_record_card("dogs", record_id, "ΣΚΥΛΟΥ")

    tree.bind("<Double-1>", open_selected_record)


    def clear_form():
        name_var.set("")
        sex_var.set("")
        birth_var.set("")
        chip_var.set("")
        pedigree_var.set("")
        father_var.set("")
        mother_var.set("")
        breeder_var.set("")
        color_var.set("")
        notes_text.delete("1.0", tk.END)

    def load_dogs(query=""):
        for item in tree.get_children():
            tree.delete(item)

        if query.strip():
            q = f"%{query.strip()}%"
            cursor.execute(
                """
                SELECT id, name, sex, birth_date, microchip, pedigree, father, mother
                FROM dogs
                WHERE name LIKE ? OR microchip LIKE ? OR pedigree LIKE ?
                ORDER BY id DESC
            """,
                (q, q, q),
            )
        else:
            cursor.execute("""
                SELECT id, name, sex, birth_date, microchip, pedigree, father, mother
                FROM dogs ORDER BY id DESC
            """)

        rows = cursor.fetchall()
        for row in rows:
            tree.insert("", tk.END, values=row)

    search_entry.bind(
        "<KeyRelease>", lambda event: load_dogs(search_var.get())
    )

    def save_dog():
        name = name_var.get().strip()
        if not name:
            messagebox.showwarning(
                "Προσοχή", "Πρέπει να συμπληρώσεις το όνομα του σκύλου."
            )
            return

        cursor.execute(
            """
            INSERT INTO dogs (name, sex, birth_date, microchip, pedigree, father, mother, breeder, color, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                name,
                sex_var.get(),
                birth_var.get(),
                chip_var.get(),
                pedigree_var.get(),
                father_var.get(),
                mother_var.get(),
                breeder_var.get(),
                color_var.get(),
                notes_text.get("1.0", tk.END).strip(),
            ),
        )
        conn.commit()
        messagebox.showinfo("Επιτυχία", "Ο σκύλος αποθηκεύτηκε επιτυχώς!")
        clear_form()
        load_dogs()

    def delete_dog():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning(
                "Προσοχή", "Επίλεξε πρώτα έναν σκύλο από τη λίστα."
            )
            return
        item = tree.item(selected[0])
        dog_id = item["values"][0]
        if messagebox.askyesno(
            "Διαγραφή", f"Θέλεις να διαγράψεις τον σκύλο:\n\n{item['values'][1]};"
        ):
            cursor.execute("DELETE FROM dogs WHERE id = ?", (dog_id,))
            conn.commit()
            clear_form()
            load_dogs()

    buttons = tk.Frame(dogs_window)
    buttons.pack(pady=5)
    tk.Button(
        buttons,
        text="💾 Αποθήκευση",
        command=save_dog,
        font=("Arial", 11, "bold"),
        width=16,
    ).grid(row=0, column=0, padx=5)
    tk.Button(
        buttons,
        text="🧹 Καθαρισμός",
        command=clear_form,
        font=("Arial", 11, "bold"),
        width=16,
    ).grid(row=0, column=1, padx=5)
    tk.Button(
        buttons,
        text="🗑️ Διαγραφή",
        command=delete_dog,
        font=("Arial", 11, "bold"),
        width=16,
    ).grid(row=0, column=2, padx=5)

    load_dogs()


# ==========================================
# ΕΝΟΤΗΤΑ: ΖΕΥΓΑΡΩΜΑΤΑ
# ==========================================


def open_matings():
    mating_window = tk.Toplevel(window)
    mating_window.title("Ζευγαρώματα - Εκτροφείο de la Dirfis")
    mating_window.geometry("1000x700")
    mating_window.minsize(900, 600)

    title = tk.Label(
        mating_window,
        text="❤️ ΔΙΑΧΕΙΡΙΣΗ ΖΕΥΓΑΡΩΜΑΤΩΝ",
        font=("Arial", 20, "bold"),
    )
    title.pack(pady=10)

    form = tk.Frame(mating_window)
    form.pack(pady=5)

    male_var = tk.StringVar()
    female_var = tk.StringVar()
    date_var = tk.StringVar(value=datetime.today().strftime("%Y-%m-%d"))
    exp_date_var = tk.StringVar()
    status_var = tk.StringVar(value="Αναμένεται")

    cursor.execute("SELECT name FROM dogs WHERE sex = 'Αρσενικό'")
    males = [r[0] for r in cursor.fetchall()]

    cursor.execute("SELECT name FROM dogs WHERE sex = 'Θηλυκό'")
    females = [r[0] for r in cursor.fetchall()]

    tk.Label(form, text="Αρσενικός (Πατέρας):", font=("Arial", 10, "bold")).grid(
        row=0, column=0, sticky="e", padx=5, pady=5
    )
    ttk.Combobox(
        form,
        textvariable=male_var,
        values=males,
        width=25,
        font=("Arial", 10),
    ).grid(row=0, column=1, sticky="w", padx=5, pady=5)

    tk.Label(form, text="Θηλυκιά (Μητέρα):", font=("Arial", 10, "bold")).grid(
        row=1, column=0, sticky="e", padx=5, pady=5
    )
    ttk.Combobox(
        form,
        textvariable=female_var,
        values=females,
        width=25,
        font=("Arial", 10),
    ).grid(row=1, column=1, sticky="w", padx=5, pady=5)

    tk.Label(
        form,
        text="Ημ/νία Ζεύξης (ΕΕΕΕ-ΜΜ-ΗΗ):",
        font=("Arial", 10, "bold"),
    ).grid(row=0, column=2, sticky="e", padx=5, pady=5)
    date_entry = tk.Entry(
        form, textvariable=date_var, width=20, font=("Arial", 10)
    )
    date_entry.grid(row=0, column=3, sticky="w", padx=5, pady=5)

    tk.Label(
        form, text="Πιθανή Ημ/νία Γέννας:", font=("Arial", 10, "bold")
    ).grid(row=1, column=2, sticky="e", padx=5, pady=5)
    tk.Entry(
        form,
        textvariable=exp_date_var,
        width=20,
        font=("Arial", 10),
        state="readonly",
    ).grid(row=1, column=3, sticky="w", padx=5, pady=5)

    tk.Label(form, text="Κατάσταση:", font=("Arial", 10, "bold")).grid(
        row=2, column=0, sticky="e", padx=5, pady=5
    )
    ttk.Combobox(
        form,
        textvariable=status_var,
        values=["Αναμένεται", "Επιτυχές (Γέννα)", "Αποτυχία"],
        state="readonly",
        width=23,
        font=("Arial", 10),
    ).grid(row=2, column=1, sticky="w", padx=5, pady=5)

    tk.Label(form, text="Σημειώσεις:", font=("Arial", 10, "bold")).grid(
        row=2, column=2, sticky="ne", padx=5, pady=5
    )
    notes_text = tk.Text(form, width=30, height=3, font=("Arial", 10))
    notes_text.grid(row=2, column=3, sticky="w", padx=5, pady=5)

    def calculate_expected(event=None):
        try:
            d = datetime.strptime(date_var.get().strip(), "%Y-%m-%d")
            exp = d + timedelta(days=63)
            exp_date_var.set(exp.strftime("%Y-%m-%d"))
        except ValueError:
            exp_date_var.set("")

    date_entry.bind("<KeyRelease>", calculate_expected)
    calculate_expected()

    list_frame = tk.Frame(mating_window)
    list_frame.pack(fill="both", expand=True, padx=20, pady=10)

    columns = ("id", "male", "female", "mating_date", "expected_date", "status")
    tree = ttk.Treeview(
        list_frame, columns=columns, show="headings", selectmode="browse"
    )

    tree.heading("id", text="ID")
    tree.heading("male", text="Πατέρας")
    tree.heading("female", text="Μητέρα")
    tree.heading("mating_date", text="Ημ/νία Ζεύξης")
    tree.heading("expected_date", text="Πιθανή Γέννα (+63d)")
    tree.heading("status", text="Κατάσταση")

    tree.column("id", width=40, anchor="center")
    tree.column("male", width=150)
    tree.column("female", width=150)
    tree.column("mating_date", width=120, anchor="center")
    tree.column("expected_date", width=130, anchor="center")
    tree.column("status", width=130, anchor="center")

    scrollbar = ttk.Scrollbar(
        list_frame, orient="vertical", command=tree.yview
    )
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def open_selected_record(event=None):
        selected = tree.selection()
        if not selected:
            return
        item = tree.item(selected[0])
        values = item.get("values", [])
        if not values:
            return
        record_id = values[0]
        try:
            record_id = int(record_id)
        except (TypeError, ValueError):
            return
        open_record_card("matings", record_id, "ΖΕΥΓΑΡΩΜΑΤΟΣ")

    tree.bind("<Double-1>", open_selected_record)


    def load_matings():
        for item in tree.get_children():
            tree.delete(item)
        cursor.execute(
            "SELECT id, male_dog, female_dog, mating_date, expected_birth_date, status FROM matings ORDER BY id DESC"
        )
        for row in cursor.fetchall():
            tree.insert("", tk.END, values=row)

    def save_mating():
        m_dog = male_var.get().strip()
        f_dog = female_var.get().strip()
        m_date = date_var.get().strip()

        if not m_dog or not f_dog or not m_date:
            messagebox.showwarning(
                "Προσοχή",
                "Συμπλήρωσε τον Πατέρα, τη Μητέρα και την Ημερομηνία Ζεύξης.",
            )
            return

        cursor.execute(
            """
            INSERT INTO matings (male_dog, female_dog, mating_date, expected_birth_date, status, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                m_dog,
                f_dog,
                m_date,
                exp_date_var.get(),
                status_var.get(),
                notes_text.get("1.0", tk.END).strip(),
            ),
        )
        conn.commit()
        messagebox.showinfo("Επιτυχία", "Το ζευγάρωμα καταχωρήθηκε!")
        male_var.set("")
        female_var.set("")
        notes_text.delete("1.0", tk.END)
        load_matings()

    def delete_mating():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning(
                "Προσοχή", "Επίλεξε ένα ζευγάρωμα από τη λίστα."
            )
            return
        m_id = tree.item(selected[0])["values"][0]
        if messagebox.askyesno(
            "Διαγραφή", "Θέλεις να διαγράψεις αυτό το ζευγάρωμα;"
        ):
            cursor.execute("DELETE FROM matings WHERE id = ?", (m_id,))
            conn.commit()
            load_matings()

    buttons = tk.Frame(mating_window)
    buttons.pack(pady=5)

    tk.Button(
        buttons,
        text="💾 Αποθήκευση",
        command=save_mating,
        font=("Arial", 11, "bold"),
        width=16,
    ).grid(row=0, column=0, padx=5)
    tk.Button(
        buttons,
        text="🗑️ Διαγραφή",
        command=delete_mating,
        font=("Arial", 11, "bold"),
        width=16,
    ).grid(row=0, column=1, padx=5)

    load_matings()


# ==========================================
# ΕΝΟΤΗΤΑ: ΓΕΝΝΕΣ
# ==========================================


def open_litters():
    litter_window = tk.Toplevel(window)
    litter_window.title("Γέννες - Εκτροφείο de la Dirfis")
    litter_window.geometry("1000x700")
    litter_window.minsize(900, 600)

    title = tk.Label(
        litter_window, text="🐶 ΔΙΑΧΕΙΡΙΣΗ ΓΕΝΝΩΝ", font=("Arial", 20, "bold")
    )
    title.pack(pady=10)

    form = tk.Frame(litter_window)
    form.pack(pady=5)

    mating_var = tk.StringVar()
    birth_var = tk.StringVar(value=datetime.today().strftime("%Y-%m-%d"))
    males_var = tk.StringVar(value="0")
    females_var = tk.StringVar(value="0")
    total_var = tk.StringVar(value="0")

    cursor.execute(
        "SELECT id, male_dog, female_dog, mating_date FROM matings ORDER BY id DESC"
    )
    matings_list = [
        f"#{r[0]} | {r[1]} x {r[2]} ({r[3]})" for r in cursor.fetchall()
    ]

    tk.Label(form, text="Ζευγάρωμα:", font=("Arial", 10, "bold")).grid(
        row=0, column=0, sticky="e", padx=5, pady=5
    )
    ttk.Combobox(
        form,
        textvariable=mating_var,
        values=matings_list,
        width=35,
        font=("Arial", 10),
    ).grid(row=0, column=1, sticky="w", padx=5, pady=5)

    tk.Label(
        form, text="Ημ/νία Γέννας (ΕΕΕΕ-ΜΜ-ΗΗ):", font=("Arial", 10, "bold")
    ).grid(row=1, column=0, sticky="e", padx=5, pady=5)
    tk.Entry(
        form, textvariable=birth_var, width=20, font=("Arial", 10)
    ).grid(row=1, column=1, sticky="w", padx=5, pady=5)

    tk.Label(form, text="Αρσενικά Κουτάβια:", font=("Arial", 10, "bold")).grid(
        row=0, column=2, sticky="e", padx=5, pady=5
    )
    m_ent = tk.Entry(form, textvariable=males_var, width=10, font=("Arial", 10))
    m_ent.grid(row=0, column=3, sticky="w", padx=5, pady=5)

    tk.Label(form, text="Θηλυκά Κουτάβια:", font=("Arial", 10, "bold")).grid(
        row=1, column=2, sticky="e", padx=5, pady=5
    )
    f_ent = tk.Entry(
        form, textvariable=females_var, width=10, font=("Arial", 10)
    )
    f_ent.grid(row=1, column=3, sticky="w", padx=5, pady=5)

    tk.Label(form, text="Σύνολο Κουταβιών:", font=("Arial", 10, "bold")).grid(
        row=2, column=2, sticky="e", padx=5, pady=5
    )
    tk.Entry(
        form,
        textvariable=total_var,
        width=10,
        font=("Arial", 10, "bold"),
        state="readonly",
    ).grid(row=2, column=3, sticky="w", padx=5, pady=5)

    tk.Label(form, text="Σημειώσεις:", font=("Arial", 10, "bold")).grid(
        row=2, column=0, sticky="ne", padx=5, pady=5
    )
    notes_text = tk.Text(form, width=35, height=3, font=("Arial", 10))
    notes_text.grid(row=2, column=1, sticky="w", padx=5, pady=5)

    def update_total(event=None):
        try:
            m = int(males_var.get() or 0)
            f = int(females_var.get() or 0)
            total_var.set(str(m + f))
        except ValueError:
            total_var.set("0")

    m_ent.bind("<KeyRelease>", update_total)
    f_ent.bind("<KeyRelease>", update_total)

    list_frame = tk.Frame(litter_window)
    list_frame.pack(fill="both", expand=True, padx=20, pady=10)

    columns = ("id", "mating", "birth_date", "males", "females", "total")
    tree = ttk.Treeview(
        list_frame, columns=columns, show="headings", selectmode="browse"
    )

    tree.heading("id", text="ID")
    tree.heading("mating", text="Ζευγάρωμα (Γονείς)")
    tree.heading("birth_date", text="Ημ/νία Γέννας")
    tree.heading("males", text="Αρσενικά")
    tree.heading("females", text="Θηλυκά")
    tree.heading("total", text="Σύνολο")

    tree.column("id", width=40, anchor="center")
    tree.column("mating", width=300)
    tree.column("birth_date", width=120, anchor="center")
    tree.column("males", width=90, anchor="center")
    tree.column("females", width=90, anchor="center")
    tree.column("total", width=90, anchor="center")

    scrollbar = ttk.Scrollbar(
        list_frame, orient="vertical", command=tree.yview
    )
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def open_selected_record(event=None):
        selected = tree.selection()
        if not selected:
            return
        item = tree.item(selected[0])
        values = item.get("values", [])
        if not values:
            return
        record_id = values[0]
        try:
            record_id = int(record_id)
        except (TypeError, ValueError):
            return
        open_record_card("litters", record_id, "ΓΕΝΝΑΣ")

    tree.bind("<Double-1>", open_selected_record)


    def load_litters():
        for item in tree.get_children():
            tree.delete(item)
        cursor.execute(
            "SELECT id, mating_info, birth_date, males_count, females_count, total_puppies FROM litters ORDER BY id DESC"
        )
        for row in cursor.fetchall():
            tree.insert("", tk.END, values=row)

    def save_litter():
        m_info = mating_var.get().strip()
        b_date = birth_var.get().strip()

        if not m_info or not b_date:
            messagebox.showwarning(
                "Προσοχή",
                "Επίλεξε ζευγάρωμα και συμπλήρωσε την ημερομηνία γέννας.",
            )
            return

        try:
            m_cnt = int(males_var.get() or 0)
            f_cnt = int(females_var.get() or 0)
            tot = m_cnt + f_cnt
        except ValueError:
            messagebox.showerror(
                "Σφάλμα", "Ο αριθμός κουταβιών πρέπει να είναι ακέραιος."
            )
            return

        cursor.execute(
            """
            INSERT INTO litters (mating_info, birth_date, males_count, females_count, total_puppies, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                m_info,
                b_date,
                m_cnt,
                f_cnt,
                tot,
                notes_text.get("1.0", tk.END).strip(),
            ),
        )

        mating_id = m_info.split(" | ")[0].replace("#", "")
        if mating_id.isdigit():
            cursor.execute(
                "UPDATE matings SET status = 'Επιτυχές (Γέννα)' WHERE id = ?",
                (mating_id,),
            )

        conn.commit()
        messagebox.showinfo("Επιτυχία", "Η γέννα καταχωρήθηκε επιτυχώς!")
        mating_var.set("")
        males_var.set("0")
        females_var.set("0")
        total_var.set("0")
        notes_text.delete("1.0", tk.END)
        load_litters()

    def delete_litter():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Προσοχή", "Επίλεξε μια γέννα από τη λίστα.")
            return
        l_id = tree.item(selected[0])["values"][0]
        if messagebox.askyesno(
            "Διαγραφή", "Θέλεις να διαγράψεις αυτή τη γέννα;"
        ):
            cursor.execute("DELETE FROM litters WHERE id = ?", (l_id,))
            conn.commit()
            load_litters()

    buttons = tk.Frame(litter_window)
    buttons.pack(pady=5)

    tk.Button(
        buttons,
        text="💾 Αποθήκευση",
        command=save_litter,
        font=("Arial", 11, "bold"),
        width=16,
    ).grid(row=0, column=0, padx=5)
    tk.Button(
        buttons,
        text="🗑️ Διαγραφή",
        command=delete_litter,
        font=("Arial", 11, "bold"),
        width=16,
    ).grid(row=0, column=1, padx=5)

    load_litters()


# ==========================================
# ΕΝΟΤΗΤΑ: ΚΟΥΤΑΒΙΑ (PUPPY PROFILES)
# ==========================================


def open_puppies():
    pup_window = tk.Toplevel(window)
    pup_window.title("Κουτάβια - Εκτροφείο de la Dirfis")
    pup_window.geometry("1100x750")
    pup_window.minsize(950, 650)

    title = tk.Label(
        pup_window,
        text="🐾 ΔΙΑΧΕΙΡΙΣΗ ΚΟΥΤΑΒΙΩΝ / ΠΩΛΗΣΕΙΣ",
        font=("Arial", 20, "bold"),
    )
    title.pack(pady=10)

    form = tk.Frame(pup_window)
    form.pack(pady=5)

    litter_var = tk.StringVar()
    name_var = tk.StringVar()
    sex_var = tk.StringVar(value="Αρσενικό")
    color_var = tk.StringVar()
    chip_var = tk.StringVar()
    status_var = tk.StringVar(value="Διαθέσιμο")

    price_var = tk.StringVar(value="0")
    deposit_var = tk.StringVar(value="0")
    buyer_name_var = tk.StringVar()
    buyer_phone_var = tk.StringVar()

    cursor.execute(
        "SELECT id, mating_info, birth_date FROM litters ORDER BY id DESC"
    )
    litters_list = [
        f"Γέννα #{r[0]} | {r[1]} ({r[2]})" for r in cursor.fetchall()
    ]

    def add_f(frame, row, col, label, var, width=22):
        tk.Label(frame, text=label, font=("Arial", 10, "bold")).grid(
            row=row, column=col, sticky="e", padx=5, pady=3
        )
        tk.Entry(frame, textvariable=var, width=width, font=("Arial", 10)).grid(
            row=row, column=col + 1, sticky="w", padx=5, pady=3
        )

    tk.Label(form, text="Γέννα:", font=("Arial", 10, "bold")).grid(
        row=0, column=0, sticky="e", padx=5, pady=3
    )
    ttk.Combobox(
        form,
        textvariable=litter_var,
        values=litters_list,
        width=35,
        font=("Arial", 10),
    ).grid(row=0, column=1, columnspan=2, sticky="w", padx=5, pady=3)

    add_f(form, 1, 0, "Όνομα / Κωδικός:", name_var)

    tk.Label(form, text="Φύλο:", font=("Arial", 10, "bold")).grid(
        row=2, column=0, sticky="e", padx=5, pady=3
    )
    ttk.Combobox(
        form,
        textvariable=sex_var,
        values=["Αρσενικό", "Θηλυκό"],
        state="readonly",
        width=20,
        font=("Arial", 10),
    ).grid(row=2, column=1, sticky="w", padx=5, pady=3)

    add_f(form, 3, 0, "Χρώμα / Σημάδια:", color_var)
    add_f(form, 4, 0, "Microchip:", chip_var)

    tk.Label(form, text="Κατάσταση:", font=("Arial", 10, "bold")).grid(
        row=0, column=3, sticky="e", padx=5, pady=3
    )
    ttk.Combobox(
        form,
        textvariable=status_var,
        values=["Διαθέσιμο", "Κρατημένο", "Πωλήθηκε", "Κρατήθηκε Εκτροφείο"],
        state="readonly",
        width=20,
        font=("Arial", 10),
    ).grid(row=0, column=4, sticky="w", padx=5, pady=3)

    add_f(form, 1, 3, "Τιμή (€):", price_var, width=15)
    add_f(form, 2, 3, "Προκαταβολή (€):", deposit_var, width=15)
    add_f(form, 3, 3, "Αγοραστής:", buyer_name_var)
    add_f(form, 4, 3, "Τηλ. Αγοραστή:", buyer_phone_var)

    tk.Label(form, text="Σημειώσεις:", font=("Arial", 10, "bold")).grid(
        row=5, column=0, sticky="ne", padx=5, pady=5
    )
    notes_text = tk.Text(form, width=65, height=2, font=("Arial", 10))
    notes_text.grid(row=5, column=1, columnspan=4, sticky="w", padx=5, pady=5)

    list_frame = tk.Frame(pup_window)
    list_frame.pack(fill="both", expand=True, padx=20, pady=10)

    columns = (
        "id",
        "litter",
        "name",
        "sex",
        "status",
        "price",
        "deposit",
        "buyer",
    )
    tree = ttk.Treeview(
        list_frame, columns=columns, show="headings", selectmode="browse"
    )

    tree.heading("id", text="ID")
    tree.heading("litter", text="Γέννα")
    tree.heading("name", text="Όνομα")
    tree.heading("sex", text="Φύλο")
    tree.heading("status", text="Κατάσταση")
    tree.heading("price", text="Τιμή (€)")
    tree.heading("deposit", text="Προκαταβολή")
    tree.heading("buyer", text="Αγοραστής")

    tree.column("id", width=35, anchor="center")
    tree.column("litter", width=220)
    tree.column("name", width=110)
    tree.column("sex", width=80, anchor="center")
    tree.column("status", width=120, anchor="center")
    tree.column("price", width=80, anchor="e")
    tree.column("deposit", width=90, anchor="e")
    tree.column("buyer", width=140)

    scrollbar = ttk.Scrollbar(
        list_frame, orient="vertical", command=tree.yview
    )
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def open_selected_record(event=None):
        selected = tree.selection()
        if not selected:
            return
        item = tree.item(selected[0])
        values = item.get("values", [])
        if not values:
            return
        record_id = values[0]
        try:
            record_id = int(record_id)
        except (TypeError, ValueError):
            return
        open_record_card("puppies", record_id, "ΚΟΥΤΑΒΙΟΥ")

    tree.bind("<Double-1>", open_selected_record)


    def clear_form():
        litter_var.set("")
        name_var.set("")
        sex_var.set("Αρσενικό")
        color_var.set("")
        chip_var.set("")
        status_var.set("Διαθέσιμο")
        price_var.set("0")
        deposit_var.set("0")
        buyer_name_var.set("")
        buyer_phone_var.set("")
        notes_text.delete("1.0", tk.END)

    def load_puppies():
        for item in tree.get_children():
            tree.delete(item)
        cursor.execute(
            "SELECT id, litter_info, name, sex, status, price, deposit, buyer_name FROM puppies ORDER BY id DESC"
        )
        for r in cursor.fetchall():
            pr = f"{r[5]:.2f}" if r[5] else "0.00"
            dp = f"{r[6]:.2f}" if r[6] else "0.00"
            tree.insert(
                "",
                tk.END,
                values=(r[0], r[1], r[2], r[3], r[4], pr, dp, r[7]),
            )

    def save_puppy():
        lit = litter_var.get().strip()
        p_name = name_var.get().strip()

        if not lit or not p_name:
            messagebox.showwarning(
                "Προσοχή", "Επίλεξε γέννα και δώσε ένα όνομα/κωδικό κουταβιού."
            )
            return

        try:
            p_price = float(price_var.get() or 0)
            p_dep = float(deposit_var.get() or 0)
        except ValueError:
            messagebox.showerror(
                "Σφάλμα", "Η τιμή και η προκαταβολή πρέπει να είναι αριθμοί."
            )
            return

        cursor.execute(
            """
            INSERT INTO puppies (litter_info, name, sex, color, microchip, status, price, deposit, buyer_name, buyer_phone, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                lit,
                p_name,
                sex_var.get(),
                color_var.get(),
                chip_var.get(),
                status_var.get(),
                p_price,
                p_dep,
                buyer_name_var.get(),
                buyer_phone_var.get(),
                notes_text.get("1.0", tk.END).strip(),
            ),
        )
        conn.commit()

        # Αυτόματη καταχώρηση στα οικονομικά εάν υπάρχει προκαταβολή ή πληρωμή
        if p_dep > 0:
            cursor.execute(
                """
                INSERT INTO transactions (trans_date, trans_type, category, amount, payment_method, description, notes)
                VALUES (?, 'Έσοδο', 'Πώληση Κουταβιού (Προκαταβολή)', ?, 'Μετρητά/Κατάθεση', ?, 'Αυτόματη εγγραφή από κουτάβια')
            """,
                (
                    datetime.today().strftime("%Y-%m-%d"),
                    p_dep,
                    f"Κουτάβι {p_name} ({buyer_name_var.get()})",
                ),
            )
            conn.commit()

        messagebox.showinfo("Επιτυχία", "Το κουτάβι καταχωρήθηκε!")
        clear_form()
        load_puppies()

    def delete_puppy():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning(
                "Προσοχή", "Επίλεξε ένα κουτάβι από τη λίστα."
            )
            return
        p_id = tree.item(selected[0])["values"][0]
        if messagebox.askyesno(
            "Διαγραφή", "Θέλεις να διαγράψεις αυτό το κουτάβι;"
        ):
            cursor.execute("DELETE FROM puppies WHERE id = ?", (p_id,))
            conn.commit()
            clear_form()
            load_puppies()

    buttons = tk.Frame(pup_window)
    buttons.pack(pady=5)
    tk.Button(
        buttons,
        text="💾 Αποθήκευση",
        command=save_puppy,
        font=("Arial", 11, "bold"),
        width=16,
    ).grid(row=0, column=0, padx=5)
    tk.Button(
        buttons,
        text="🧹 Καθαρισμός",
        command=clear_form,
        font=("Arial", 11, "bold"),
        width=16,
    ).grid(row=0, column=1, padx=5)
    tk.Button(
        buttons,
        text="🗑️ Διαγραφή",
        command=delete_puppy,
        font=("Arial", 11, "bold"),
        width=16,
    ).grid(row=0, column=2, padx=5)

    load_puppies()


# ==========================================
# ΕΝΟΤΗΤΑ: ΕΝΔΙΑΦΕΡΟΜΕΝΟΙ / ΠΕΛΑΤΕΣ (WAITLIST)
# ==========================================


def open_clients():
    cli_window = tk.Toplevel(window)
    cli_window.title("Ενδιαφερόμενοι / Πελάτες - Εκτροφείο de la Dirfis")
    cli_window.geometry("1100x750")
    cli_window.minsize(950, 650)

    title = tk.Label(
        cli_window,
        text="👤 ΕΝΔΙΑΦΕΡΟΜΕΝΟΙ & ΛΙΣΤΑ ΑΝΑΜΟΝΗΣ",
        font=("Arial", 20, "bold"),
    )
    title.pack(pady=10)

    form = tk.Frame(cli_window)
    form.pack(pady=5)

    name_var = tk.StringVar()
    phone_var = tk.StringVar()
    email_var = tk.StringVar()
    city_var = tk.StringVar()

    pref_sex_var = tk.StringVar(value="Οποιοδήποτε")
    pref_color_var = tk.StringVar()
    purpose_var = tk.StringVar(value="Κυνηγετικό")

    deposit_var = tk.StringVar(value="0")
    status_var = tk.StringVar(value="Σε Αναμονή")
    search_var = tk.StringVar()

    def add_f(frame, row, col, label, var, width=22):
        tk.Label(frame, text=label, font=("Arial", 10, "bold")).grid(
            row=row, column=col, sticky="e", padx=5, pady=3
        )
        tk.Entry(frame, textvariable=var, width=width, font=("Arial", 10)).grid(
            row=row, column=col + 1, sticky="w", padx=5, pady=3
        )

    add_f(form, 0, 0, "Ονοματεπώνυμο:", name_var)
    add_f(form, 1, 0, "Τηλέφωνο:", phone_var)
    add_f(form, 2, 0, "Email:", email_var)
    add_f(form, 3, 0, "Περιοχή/Πόλη:", city_var)

    tk.Label(form, text="Επιθυμητό Φύλο:", font=("Arial", 10, "bold")).grid(
        row=0, column=2, sticky="e", padx=5, pady=3
    )
    ttk.Combobox(
        form,
        textvariable=pref_sex_var,
        values=["Αρσενικό", "Θηλυκό", "Οποιοδήποτε"],
        state="readonly",
        width=20,
        font=("Arial", 10),
    ).grid(row=0, column=3, sticky="w", padx=5, pady=3)

    add_f(form, 1, 2, "Επιθυμητό Χρώμα:", pref_color_var)

    tk.Label(form, text="Σκοπός Χρήσης:", font=("Arial", 10, "bold")).grid(
        row=2, column=2, sticky="e", padx=5, pady=3
    )
    ttk.Combobox(
        form,
        textvariable=purpose_var,
        values=["Κυνηγετικό", "Συντροφιά", "Εκθέσεις / Αναπαραγωγή"],
        width=20,
        font=("Arial", 10),
    ).grid(row=2, column=3, sticky="w", padx=5, pady=3)

    add_f(form, 3, 2, "Προκαταβολή (€):", deposit_var, width=15)

    tk.Label(form, text="Κατάσταση:", font=("Arial", 10, "bold")).grid(
        row=4, column=0, sticky="e", padx=5, pady=3
    )
    ttk.Combobox(
        form,
        textvariable=status_var,
        values=["Σε Αναμονή", "Επικοινώνησε", "Ακυρώθηκε", "Ολοκληρώθηκε"],
        state="readonly",
        width=20,
        font=("Arial", 10),
    ).grid(row=4, column=1, sticky="w", padx=5, pady=3)

    tk.Label(form, text="Σημειώσεις / Απαιτήσεις:", font=("Arial", 10, "bold")).grid(
        row=5, column=0, sticky="ne", padx=5, pady=5
    )
    notes_text = tk.Text(form, width=65, height=2, font=("Arial", 10))
    notes_text.grid(row=5, column=1, columnspan=3, sticky="w", padx=5, pady=5)

    search_frame = tk.Frame(cli_window)
    search_frame.pack(fill="x", padx=20, pady=(10, 0))

    tk.Label(
        search_frame,
        text="🔍 Αναζήτηση (Όνομα, Τηλέφωνο, Πόλη):",
        font=("Arial", 10, "bold"),
    ).pack(side="left", padx=(0, 5))
    search_entry = tk.Entry(
        search_frame, textvariable=search_var, font=("Arial", 10), width=35
    )
    search_entry.pack(side="left")

    list_frame = tk.Frame(cli_window)
    list_frame.pack(fill="both", expand=True, padx=20, pady=10)

    columns = (
        "id",
        "name",
        "phone",
        "city",
        "pref_sex",
        "purpose",
        "deposit",
        "status",
    )
    tree = ttk.Treeview(
        list_frame, columns=columns, show="headings", selectmode="browse"
    )

    tree.heading("id", text="ID")
    tree.heading("name", text="Ονοματεπώνυμο")
    tree.heading("phone", text="Τηλέφωνο")
    tree.heading("city", text="Πόλη")
    tree.heading("pref_sex", text="Προτίμηση Φύλου")
    tree.heading("purpose", text="Σκοπός")
    tree.heading("deposit", text="Προκαταβολή (€)")
    tree.heading("status", text="Κατάσταση")

    tree.column("id", width=35, anchor="center")
    tree.column("name", width=160)
    tree.column("phone", width=110, anchor="center")
    tree.column("city", width=110)
    tree.column("pref_sex", width=110, anchor="center")
    tree.column("purpose", width=120)
    tree.column("deposit", width=100, anchor="e")
    tree.column("status", width=120, anchor="center")

    scrollbar = ttk.Scrollbar(
        list_frame, orient="vertical", command=tree.yview
    )
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def open_selected_record(event=None):
        selected = tree.selection()
        if not selected:
            return
        item = tree.item(selected[0])
        values = item.get("values", [])
        if not values:
            return
        record_id = values[0]
        try:
            record_id = int(record_id)
        except (TypeError, ValueError):
            return
        open_record_card("clients", record_id, "ΠΕΛΑΤΗ / ΕΝΔΙΑΦΕΡΟΜΕΝΟΥ")

    tree.bind("<Double-1>", open_selected_record)


    def clear_form():
        name_var.set("")
        phone_var.set("")
        email_var.set("")
        city_var.set("")
        pref_sex_var.set("Οποιοδήποτε")
        pref_color_var.set("")
        purpose_var.set("Κυνηγετικό")
        deposit_var.set("0")
        status_var.set("Σε Αναμονή")
        notes_text.delete("1.0", tk.END)

    def load_clients(query=""):
        for item in tree.get_children():
            tree.delete(item)

        if query.strip():
            q = f"%{query.strip()}%"
            cursor.execute(
                """
                SELECT id, full_name, phone, city, pref_sex, purpose, deposit, status
                FROM clients
                WHERE full_name LIKE ? OR phone LIKE ? OR city LIKE ?
                ORDER BY id DESC
            """,
                (q, q, q),
            )
        else:
            cursor.execute("""
                SELECT id, full_name, phone, city, pref_sex, purpose, deposit, status
                FROM clients ORDER BY id DESC
            """)

        for r in cursor.fetchall():
            dep = f"{r[6]:.2f}" if r[6] else "0.00"
            tree.insert(
                "",
                tk.END,
                values=(r[0], r[1], r[2], r[3], r[4], r[5], dep, r[7]),
            )

    search_entry.bind(
        "<KeyRelease>", lambda event: load_clients(search_var.get())
    )

    def save_client():
        c_name = name_var.get().strip()
        if not c_name:
            messagebox.showwarning(
                "Προσοχή", "Πρέπει να συμπληρώσεις το Ονοματεπώνυμο."
            )
            return

        try:
            dep = float(deposit_var.get() or 0)
        except ValueError:
            messagebox.showerror(
                "Σφάλμα", "Η προκαταβολή πρέπει να είναι αριθμός."
            )
            return

        cursor.execute(
            """
            INSERT INTO clients (full_name, phone, email, city, pref_sex, pref_color, purpose, deposit, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                c_name,
                phone_var.get(),
                email_var.get(),
                city_var.get(),
                pref_sex_var.get(),
                pref_color_var.get(),
                purpose_var.get(),
                dep,
                status_var.get(),
                notes_text.get("1.0", tk.END).strip(),
            ),
        )
        conn.commit()

        # Καταχώρηση προκαταβολής κράτησης στα οικονομικά
        if dep > 0:
            cursor.execute(
                """
                INSERT INTO transactions (trans_date, trans_type, category, amount, payment_method, description, notes)
                VALUES (?, 'Έσοδο', 'Προκαταβολή Λίστας Αναμονής', ?, 'Μετρητά/Κατάθεση', ?, 'Αυτόματη εγγραφή από λίστα αναμονής')
            """,
                (
                    datetime.today().strftime("%Y-%m-%d"),
                    dep,
                    f"Κράτηση: {c_name}",
                ),
            )
            conn.commit()

        messagebox.showinfo(
            "Επιτυχία", "Ο ενδιαφερόμενος καταχωρήθηκε στη λίστα!"
        )
        clear_form()
        load_clients()

    def delete_client():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning(
                "Προσοχή", "Επίλεξε ένα άτομο από τη λίστα."
            )
            return
        c_id = tree.item(selected[0])["values"][0]
        if messagebox.askyesno(
            "Διαγραφή", "Θέλεις να διαγράψεις αυτόν τον ενδιαφερόμενο;"
        ):
            cursor.execute("DELETE FROM clients WHERE id = ?", (c_id,))
            conn.commit()
            clear_form()
            load_clients()

    buttons = tk.Frame(cli_window)
    buttons.pack(pady=5)
    tk.Button(
        buttons,
        text="💾 Αποθήκευση",
        command=save_client,
        font=("Arial", 11, "bold"),
        width=16,
    ).grid(row=0, column=0, padx=5)
    tk.Button(
        buttons,
        text="🧹 Καθαρισμός",
        command=clear_form,
        font=("Arial", 11, "bold"),
        width=16,
    ).grid(row=0, column=1, padx=5)
    tk.Button(
        buttons,
        text="🗑️ Διαγραφή",
        command=delete_client,
        font=("Arial", 11, "bold"),
        width=16,
    ).grid(row=0, column=2, padx=5)

    load_clients()


# ==========================================
# ΕΝΟΤΗΤΑ: ΕΚΠΑΙΔΕΥΣΗ (ΠΕΛΑΤΕΣ)
# ==========================================


def open_training():
    train_window = tk.Toplevel(window)
    train_window.title("Εκπαίδευση Σκύλων / Πελάτες - de la Dirfis")
    train_window.geometry("1150x780")
    train_window.minsize(1000, 650)

    title = tk.Label(
        train_window,
        text="🎯 ΕΚΠΑΙΔΕΥΣΗ ΣΚΥΛΩΝ & ΠΕΛΑΤΕΣ",
        font=("Arial", 20, "bold"),
    )
    title.pack(pady=10)

    form = tk.Frame(train_window)
    form.pack(pady=5)

    client_var = tk.StringVar()
    phone_var = tk.StringVar()
    email_var = tk.StringVar()
    city_var = tk.StringVar()

    dog_name_var = tk.StringVar()
    dog_breed_var = tk.StringVar()
    type_var = tk.StringVar()
    status_var = tk.StringVar(value="Σε εξέλιξη")

    start_var = tk.StringVar()
    end_var = tk.StringVar()
    cost_var = tk.StringVar(value="0")
    advance_var = tk.StringVar(value="0")

    search_var = tk.StringVar()

    def add_f(frame, row, col, label, var, width=25):
        tk.Label(frame, text=label, font=("Arial", 10, "bold")).grid(
            row=row, column=col, sticky="e", padx=5, pady=3
        )
        tk.Entry(frame, textvariable=var, width=width, font=("Arial", 10)).grid(
            row=row, column=col + 1, sticky="w", padx=5, pady=3
        )

    tk.Label(
        form,
        text="--- ΣΤΟΙΧΕΙΑ ΠΕΛΑΤΗ ---",
        font=("Arial", 10, "bold", "underline"),
    ).grid(row=0, column=0, columnspan=2, pady=(0, 5))
    add_f(form, 1, 0, "Ονοματεπώνυμο:", client_var)
    add_f(form, 2, 0, "Τηλέφωνο:", phone_var)
    add_f(form, 3, 0, "Email:", email_var)
    add_f(form, 4, 0, "Περιοχή/Πόλη:", city_var)

    tk.Label(
        form,
        text="--- ΣΤΟΙΧΕΙΑ ΕΚΠΑΙΔΕΥΣΗΣ ---",
        font=("Arial", 10, "bold", "underline"),
    ).grid(row=0, column=2, columnspan=2, pady=(0, 5))
    add_f(form, 1, 2, "Όνομα Σκύλου:", dog_name_var)
    add_f(form, 2, 2, "Ράτσα/Φυλή:", dog_breed_var)

    tk.Label(form, text="Είδος Εκπαίδευσης:", font=("Arial", 10, "bold")).grid(
        row=3, column=2, sticky="e", padx=5, pady=3
    )
    ttk.Combobox(
        form,
        textvariable=type_var,
        values=[
            "Βασική Υπακοή",
            "Προηγμένη Υπακοή",
            "Διόρθωση Συμπεριφοράς",
            "Κυνηγετική Εκπαίδευση",
            "Εκπαίδευση Κουταβιού",
            "Άλλο",
        ],
        width=23,
        font=("Arial", 10),
    ).grid(row=3, column=3, sticky="w", padx=5, pady=3)

    tk.Label(form, text="Κατάσταση:", font=("Arial", 10, "bold")).grid(
        row=4, column=2, sticky="e", padx=5, pady=3
    )
    ttk.Combobox(
        form,
        textvariable=status_var,
        values=["Σε εξέλιξη", "Ολοκληρώθηκε", "Ακυρώθηκε", "Αναμονή"],
        state="readonly",
        width=23,
        font=("Arial", 10),
    ).grid(row=4, column=3, sticky="w", padx=5, pady=3)

    tk.Label(
        form,
        text="--- ΧΡΟΝΟΣ & ΚΟΣΤΟΣ ---",
        font=("Arial", 10, "bold", "underline"),
    ).grid(row=0, column=4, columnspan=2, pady=(0, 5))
    add_f(form, 1, 4, "Έναρξη (ΕΕΕΕ-ΜΜ-ΗΗ):", start_var, width=15)
    add_f(form, 2, 4, "Λήξη (ΕΕΕΕ-ΜΜ-ΗΗ):", end_var, width=15)
    add_f(form, 3, 4, "Συνολικό Κόστος (€):", cost_var, width=15)
    add_f(form, 4, 4, "Προκαταβολή (€):", advance_var, width=15)

    tk.Label(
        form, text="Σημειώσεις / Στόχοι:", font=("Arial", 10, "bold")
    ).grid(row=5, column=0, sticky="ne", padx=5, pady=5)
    notes_text = tk.Text(form, width=75, height=3, font=("Arial", 10))
    notes_text.grid(row=5, column=1, columnspan=5, sticky="w", padx=5, pady=5)

    search_frame = tk.Frame(train_window)
    search_frame.pack(fill="x", padx=20, pady=(10, 0))

    tk.Label(
        search_frame,
        text="🔍 Αναζήτηση (Πελάτης, Σκύλος, Τηλέφωνο):",
        font=("Arial", 10, "bold"),
    ).pack(side="left", padx=(0, 5))
    search_entry = tk.Entry(
        search_frame, textvariable=search_var, font=("Arial", 10), width=35
    )
    search_entry.pack(side="left")

    list_frame = tk.Frame(train_window)
    list_frame.pack(fill="both", expand=True, padx=20, pady=10)

    columns = (
        "id",
        "client",
        "phone",
        "dog",
        "breed",
        "type",
        "status",
        "cost",
        "advance",
        "balance",
    )
    tree = ttk.Treeview(
        list_frame, columns=columns, show="headings", selectmode="browse"
    )

    tree.heading("id", text="ID")
    tree.heading("client", text="Πελάτης")
    tree.heading("phone", text="Τηλέφωνο")
    tree.heading("dog", text="Σκύλος")
    tree.heading("breed", text="Ράτσα")
    tree.heading("type", text="Πρόγραμμα")
    tree.heading("status", text="Κατάσταση")
    tree.heading("cost", text="Κόστος (€)")
    tree.heading("advance", text="Προκαταβολή (€)")
    tree.heading("balance", text="Υπόλοιπο (€)")

    tree.column("id", width=35, anchor="center")
    tree.column("client", width=140)
    tree.column("phone", width=100, anchor="center")
    tree.column("dog", width=110)
    tree.column("breed", width=110)
    tree.column("type", width=130)
    tree.column("status", width=100, anchor="center")
    tree.column("cost", width=80, anchor="e")
    tree.column("advance", width=90, anchor="e")
    tree.column("balance", width=90, anchor="e")

    scrollbar = ttk.Scrollbar(
        list_frame, orient="vertical", command=tree.yview
    )
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def open_selected_record(event=None):
        selected = tree.selection()
        if not selected:
            return
        item = tree.item(selected[0])
        values = item.get("values", [])
        if not values:
            return
        record_id = values[0]
        try:
            record_id = int(record_id)
        except (TypeError, ValueError):
            return
        open_record_card("trainings", record_id, "ΕΚΠΑΙΔΕΥΣΗΣ")

    tree.bind("<Double-1>", open_selected_record)


    def clear_form():
        client_var.set("")
        phone_var.set("")
        email_var.set("")
        city_var.set("")
        dog_name_var.set("")
        dog_breed_var.set("")
        type_var.set("")
        status_var.set("Σε εξέλιξη")
        start_var.set("")
        end_var.set("")
        cost_var.set("0")
        advance_var.set("0")
        notes_text.delete("1.0", tk.END)

    def load_trainings(query=""):
        for item in tree.get_children():
            tree.delete(item)

        if query.strip():
            q = f"%{query.strip()}%"
            cursor.execute(
                """
                SELECT id, client_name, phone, dog_name, dog_breed, training_type, status, total_cost, advance_payment
                FROM trainings
                WHERE client_name LIKE ? OR dog_name LIKE ? OR phone LIKE ?
                ORDER BY id DESC
            """,
                (q, q, q),
            )
        else:
            cursor.execute("""
                SELECT id, client_name, phone, dog_name, dog_breed, training_type, status, total_cost, advance_payment
                FROM trainings ORDER BY id DESC
            """)

        rows = cursor.fetchall()
        for r in rows:
            cost = r[7] if r[7] else 0.0
            advance = r[8] if r[8] else 0.0
            balance = cost - advance
            tree.insert(
                "",
                tk.END,
                values=(
                    r[0],
                    r[1],
                    r[2],
                    r[3],
                    r[4],
                    r[5],
                    r[6],
                    f"{cost:.2f}",
                    f"{advance:.2f}",
                    f"{balance:.2f}",
                ),
            )

    search_entry.bind(
        "<KeyRelease>", lambda event: load_trainings(search_var.get())
    )

    def save_training():
        client = client_var.get().strip()
        dog = dog_name_var.get().strip()

        if not client or not dog:
            messagebox.showwarning(
                "Προσοχή",
                "Συμπλήρωσε τουλάχιστον το Ονοματεπώνυμο Πελάτη και το Όνομα Σκύλου.",
            )
            return

        try:
            tot_c = float(cost_var.get() or 0)
            adv_p = float(advance_var.get() or 0)
        except ValueError:
            messagebox.showerror(
                "Σφάλμα", "Το κόστος και η προκαταβολή πρέπει να είναι αριθμοί."
            )
            return

        cursor.execute(
            """
            INSERT INTO trainings (client_name, phone, email, city, dog_name, dog_breed, training_type, start_date, end_date, status, total_cost, advance_payment, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                client,
                phone_var.get(),
                email_var.get(),
                city_var.get(),
                dog,
                dog_breed_var.get(),
                type_var.get(),
                start_var.get(),
                end_var.get(),
                status_var.get(),
                tot_c,
                adv_p,
                notes_text.get("1.0", tk.END).strip(),
            ),
        )
        conn.commit()

        # Καταχώρηση προκαταβολής εκπαίδευσης στα οικονομικά
        if adv_p > 0:
            cursor.execute(
                """
                INSERT INTO transactions (trans_date, trans_type, category, amount, payment_method, description, notes)
                VALUES (?, 'Έσοδο', 'Εκπαίδευση (Προκαταβολή)', ?, 'Μετρητά/Κατάθεση', ?, 'Αυτόματη εγγραφή από εκπαιδεύσεις')
            """,
                (
                    datetime.today().strftime("%Y-%m-%d"),
                    adv_p,
                    f"Εκπαίδευση {dog} ({client})",
                ),
            )
            conn.commit()

        messagebox.showinfo(
            "Επιτυχία", "Η καταχώρηση εκπαίδευσης αποθηκεύτηκε!"
        )
        clear_form()
        load_trainings()

    def delete_training():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Προσοχή", "Επίλεξε μια εγγραφή από τη λίστα.")
            return
        item = tree.item(selected[0])
        t_id = item["values"][0]

        if messagebox.askyesno(
            "Διαγραφή",
            f"Θέλεις να διαγράψεις την εκπαίδευση του σκύλου {item['values'][3]} (Πελάτης: {item['values'][1]});",
        ):
            cursor.execute("DELETE FROM trainings WHERE id = ?", (t_id,))
            conn.commit()
            clear_form()
            load_trainings()

    buttons = tk.Frame(train_window)
    buttons.pack(pady=5)
    tk.Button(
        buttons,
        text="💾 Αποθήκευση Νέου",
        command=save_training,
        font=("Arial", 11, "bold"),
        width=18,
    ).grid(row=0, column=0, padx=5)
    tk.Button(
        buttons,
        text="🧹 Καθαρισμός",
        command=clear_form,
        font=("Arial", 11, "bold"),
        width=15,
    ).grid(row=0, column=1, padx=5)
    tk.Button(
        buttons,
        text="🗑️ Διαγραφή",
        command=delete_training,
        font=("Arial", 11, "bold"),
        width=15,
    ).grid(row=0, column=2, padx=5)

    load_trainings()


# ==========================================
# ΕΝΟΤΗΤΑ: ΟΙΚΟΝΟΜΙΚΑ & ΠΛΗΡΩΜΕΣ
# ==========================================


def open_finances():
    fin_window = tk.Toplevel(window)
    fin_window.title("Οικονομικά & Ταμείο - Εκτροφείο de la Dirfis")
    fin_window.geometry("1100x780")
    fin_window.minsize(950, 650)

    title = tk.Label(
        fin_window, text="💰 ΟΙΚΟΝΟΜΙΚΑ & ΤΑΜΕΙΟ", font=("Arial", 20, "bold")
    )
    title.pack(pady=10)

    # --- KPI SUMMARY CARDS ---
    summary_frame = tk.Frame(fin_window)
    summary_frame.pack(pady=5)

    income_label = tk.Label(
        summary_frame,
        text="Έσοδα: €0.00",
        font=("Arial", 12, "bold"),
        fg="green",
        bg="#e8f5e9",
        width=22,
        padx=10,
        pady=8,
        relief="groove",
    )
    income_label.grid(row=0, column=0, padx=10)

    expense_label = tk.Label(
        summary_frame,
        text="Έξοδα: €0.00",
        font=("Arial", 12, "bold"),
        fg="red",
        bg="#ffebee",
        width=22,
        padx=10,
        pady=8,
        relief="groove",
    )
    expense_label.grid(row=0, column=1, padx=10)

    balance_label = tk.Label(
        summary_frame,
        text="Ταμείο: €0.00",
        font=("Arial", 12, "bold"),
        fg="blue",
        bg="#e3f2fd",
        width=22,
        padx=10,
        pady=8,
        relief="groove",
    )
    balance_label.grid(row=0, column=2, padx=10)

    # --- ΦΟΡΜΑ ΚΑΤΑΧΩΡΗΣΗΣ ---
    form = tk.Frame(fin_window)
    form.pack(pady=10)

    date_var = tk.StringVar(value=datetime.today().strftime("%Y-%m-%d"))
    type_var = tk.StringVar(value="Έσοδο")
    cat_var = tk.StringVar(value="Πώληση Κουταβιού")
    amount_var = tk.StringVar(value="0")
    method_var = tk.StringVar(value="Μετρητά")
    desc_var = tk.StringVar()

    def add_f(frame, row, col, label, var, width=20):
        tk.Label(frame, text=label, font=("Arial", 10, "bold")).grid(
            row=row, column=col, sticky="e", padx=5, pady=3
        )
        tk.Entry(frame, textvariable=var, width=width, font=("Arial", 10)).grid(
            row=row, column=col + 1, sticky="w", padx=5, pady=3
        )

    add_f(form, 0, 0, "Ημερομηνία:", date_var)

    tk.Label(form, text="Τύπος:", font=("Arial", 10, "bold")).grid(
        row=0, column=2, sticky="e", padx=5, pady=3
    )
    type_cb = ttk.Combobox(
        form,
        textvariable=type_var,
        values=["Έσοδο", "Έξοδο"],
        state="readonly",
        width=18,
        font=("Arial", 10),
    )
    type_cb.grid(row=0, column=3, sticky="w", padx=5, pady=3)

    tk.Label(form, text="Κατηγορία:", font=("Arial", 10, "bold")).grid(
        row=1, column=0, sticky="e", padx=5, pady=3
    )
    cat_cb = ttk.Combobox(
        form,
        textvariable=cat_var,
        values=[
            "Πώληση Κουταβιού",
            "Εκπαίδευση Σκύλου",
            "Προκαταβολή Κράτησης",
            "Ζωοτροφές / Τροφή",
            "Κτηνίατρος / Εμβόλια",
            "Εξοπλισμός / Αναλώσιμα",
            "Αγώνες / Εκθέσεις",
            "Διάφορα Έξοδα",
            "Άλλο Έσοδο",
        ],
        width=18,
        font=("Arial", 10),
    )
    cat_cb.grid(row=1, column=1, sticky="w", padx=5, pady=3)

    add_f(form, 1, 2, "Ποσό (€):", amount_var)

    tk.Label(form, text="Τρόπος Πληρωμής:", font=("Arial", 10, "bold")).grid(
        row=2, column=0, sticky="e", padx=5, pady=3
    )
    ttk.Combobox(
        form,
        textvariable=method_var,
        values=["Μετρητά", "Τραπεζική Κατάθεση", "Κάρτα (POS)", "Άλλο"],
        state="readonly",
        width=18,
        font=("Arial", 10),
    ).grid(row=2, column=1, sticky="w", padx=5, pady=3)

    add_f(form, 2, 2, "Περιγραφή / Πελάτης:", desc_var, width=25)

    tk.Label(form, text="Σημειώσεις:", font=("Arial", 10, "bold")).grid(
        row=3, column=0, sticky="ne", padx=5, pady=5
    )
    notes_text = tk.Text(form, width=55, height=2, font=("Arial", 10))
    notes_text.grid(row=3, column=1, columnspan=3, sticky="w", padx=5, pady=5)

    list_frame = tk.Frame(fin_window)
    list_frame.pack(fill="both", expand=True, padx=20, pady=10)

    columns = ("id", "date", "type", "category", "amount", "method", "desc")
    tree = ttk.Treeview(
        list_frame, columns=columns, show="headings", selectmode="browse"
    )

    tree.heading("id", text="ID")
    tree.heading("date", text="Ημερομηνία")
    tree.heading("type", text="Τύπος")
    tree.heading("category", text="Κατηγορία")
    tree.heading("amount", text="Ποσό (€)")
    tree.heading("method", text="Τρόπος")
    tree.heading("desc", text="Περιγραφή")

    tree.column("id", width=35, anchor="center")
    tree.column("date", width=100, anchor="center")
    tree.column("type", width=90, anchor="center")
    tree.column("category", width=150)
    tree.column("amount", width=100, anchor="e")
    tree.column("method", width=120, anchor="center")
    tree.column("desc", width=220)

    scrollbar = ttk.Scrollbar(
        list_frame, orient="vertical", command=tree.yview
    )
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def open_selected_record(event=None):
        selected = tree.selection()
        if not selected:
            return
        item = tree.item(selected[0])
        values = item.get("values", [])
        if not values:
            return
        record_id = values[0]
        try:
            record_id = int(record_id)
        except (TypeError, ValueError):
            return
        open_record_card("transactions", record_id, "ΣΥΝΑΛΛΑΓΗΣ")

    tree.bind("<Double-1>", open_selected_record)


    def clear_form():
        date_var.set(datetime.today().strftime("%Y-%m-%d"))
        type_var.set("Έσοδο")
        cat_var.set("Πώληση Κουταβιού")
        amount_var.set("0")
        method_var.set("Μετρητά")
        desc_var.set("")
        notes_text.delete("1.0", tk.END)

    def load_transactions():
        for item in tree.get_children():
            tree.delete(item)

        cursor.execute(
            "SELECT id, trans_date, trans_type, category, amount, payment_method, description FROM transactions ORDER BY id DESC"
        )
        rows = cursor.fetchall()

        total_in = 0.0
        total_out = 0.0

        for r in rows:
            amt = r[4] if r[4] else 0.0
            if r[2] == "Έσοδο":
                total_in += amt
            else:
                total_out += amt

            tree.insert(
                "",
                tk.END,
                values=(r[0], r[1], r[2], r[3], f"{amt:.2f}", r[5], r[6]),
            )

        bal = total_in - total_out
        income_label.config(text=f"Έσοδα: €{total_in:.2f}")
        expense_label.config(text=f"Έξοδα: €{total_out:.2f}")
        balance_label.config(text=f"Ταμείο: €{bal:.2f}")

    def save_transaction():
        t_date = date_var.get().strip()
        try:
            amt = float(amount_var.get() or 0)
            if amt <= 0:
                messagebox.showwarning(
                    "Προσοχή", "Το ποσό πρέπει να είναι μεγαλύτερο του 0."
                )
                return
        except ValueError:
            messagebox.showerror("Σφάλμα", "Δώσε έγκυρο αριθμητικό ποσό.")
            return

        cursor.execute(
            """
            INSERT INTO transactions (trans_date, trans_type, category, amount, payment_method, description, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                t_date,
                type_var.get(),
                cat_var.get(),
                amt,
                method_var.get(),
                desc_var.get(),
                notes_text.get("1.0", tk.END).strip(),
            ),
        )
        conn.commit()
        messagebox.showinfo("Επιτυχία", "Η συναλλαγή αποθηκεύτηκε!")
        clear_form()
        load_transactions()

    def delete_transaction():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning(
                "Προσοχή", "Επίλεξε μια συναλλαγή από τη λίστα."
            )
            return
        t_id = tree.item(selected[0])["values"][0]
        if messagebox.askyesno(
            "Διαγραφή", "Θέλεις να διαγράψεις αυτή τη συναλλαγή;"
        ):
            cursor.execute("DELETE FROM transactions WHERE id = ?", (t_id,))
            conn.commit()
            clear_form()
            load_transactions()

    buttons = tk.Frame(fin_window)
    buttons.pack(pady=5)
    tk.Button(
        buttons,
        text="💾 Αποθήκευση",
        command=save_transaction,
        font=("Arial", 11, "bold"),
        width=16,
    ).grid(row=0, column=0, padx=5)
    tk.Button(
        buttons,
        text="🧹 Καθαρισμός",
        command=clear_form,
        font=("Arial", 11, "bold"),
        width=16,
    ).grid(row=0, column=1, padx=5)
    tk.Button(
        buttons,
        text="🗑️ Διαγραφή",
        command=delete_transaction,
        font=("Arial", 11, "bold"),
        width=16,
    ).grid(row=0, column=2, padx=5)

    load_transactions()


# ==========================================
# ΕΝΟΤΗΤΑ: ΑΝΑΦΟΡΕΣ
# ==========================================


def open_reports():
    rep_window = tk.Toplevel(window)
    rep_window.title("Αναφορές - Εκτροφείο de la Dirfis")
    rep_window.geometry("1050x760")
    rep_window.minsize(900, 650)

    tk.Label(
        rep_window,
        text="📊 ΑΝΑΦΟΡΕΣ ΕΚΤΡΟΦΕΙΟΥ",
        font=("Arial", 22, "bold"),
    ).pack(pady=12)

    summary = tk.Frame(rep_window)
    summary.pack(pady=5)

    def get_count(table):
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        return cursor.fetchone()[0]

    dogs_count = get_count("dogs")
    matings_count = get_count("matings")
    litters_count = get_count("litters")
    puppies_count = get_count("puppies")
    clients_count = get_count("clients")
    training_count = get_count("trainings")

    cursor.execute("SELECT COUNT(*) FROM dogs WHERE sex = 'Αρσενικό'")
    males = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM dogs WHERE sex = 'Θηλυκό'")
    females = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM puppies WHERE status = 'Διαθέσιμο'")
    available_puppies = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM puppies WHERE status = 'Κρατημένο'")
    reserved_puppies = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM puppies WHERE status = 'Πωλημένο'")
    sold_puppies = cursor.fetchone()[0]

    cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE trans_type = 'Έσοδο'")
    income = cursor.fetchone()[0] or 0
    cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE trans_type = 'Έξοδο'")
    expenses = cursor.fetchone()[0] or 0
    balance = income - expenses

    cards = [
        ("🐕 Σκύλοι", dogs_count),
        ("♂ Αρσενικά", males),
        ("♀ Θηλυκά", females),
        ("❤️ Ζευγαρώματα", matings_count),
        ("🐶 Γέννες", litters_count),
        ("🐾 Κουτάβια", puppies_count),
        ("👤 Πελάτες", clients_count),
        ("🎯 Εκπαιδεύσεις", training_count),
    ]

    for i, (label, value) in enumerate(cards):
        tk.Label(
            summary,
            text=f"{label}\n{value}",
            font=("Arial", 11, "bold"),
            width=16,
            height=3,
            relief="groove",
            bd=2,
        ).grid(row=i // 4, column=i % 4, padx=7, pady=7)

    financial = tk.Frame(rep_window)
    financial.pack(pady=10)
    tk.Label(financial, text=f"💰 Συνολικά Έσοδα: €{income:.2f}", font=("Arial", 12, "bold"), width=25).grid(row=0, column=0, padx=8)
    tk.Label(financial, text=f"💸 Συνολικά Έξοδα: €{expenses:.2f}", font=("Arial", 12, "bold"), width=25).grid(row=0, column=1, padx=8)
    tk.Label(financial, text=f"📌 Υπόλοιπο: €{balance:.2f}", font=("Arial", 12, "bold"), width=25).grid(row=0, column=2, padx=8)

    puppy_frame = tk.LabelFrame(rep_window, text="Κατάσταση Κουταβιών", font=("Arial", 11, "bold"), padx=15, pady=10)
    puppy_frame.pack(fill="x", padx=25, pady=10)
    tk.Label(puppy_frame, text=f"Διαθέσιμα: {available_puppies}", font=("Arial", 11, "bold"), width=20).pack(side="left", padx=10)
    tk.Label(puppy_frame, text=f"Κρατημένα: {reserved_puppies}", font=("Arial", 11, "bold"), width=20).pack(side="left", padx=10)
    tk.Label(puppy_frame, text=f"Πωλημένα: {sold_puppies}", font=("Arial", 11, "bold"), width=20).pack(side="left", padx=10)

    detail_frame = tk.LabelFrame(rep_window, text="Αναφορά Γεννών", font=("Arial", 11, "bold"), padx=10, pady=10)
    detail_frame.pack(fill="both", expand=True, padx=25, pady=10)

    columns = ("id", "mating", "date", "males", "females", "total")
    tree = ttk.Treeview(detail_frame, columns=columns, show="headings")
    headings = {
        "id": "ID",
        "mating": "Ζευγάρωμα",
        "date": "Ημερομηνία",
        "males": "Αρσενικά",
        "females": "Θηλυκά",
        "total": "Σύνολο",
    }
    widths = {"id": 45, "mating": 260, "date": 110, "males": 100, "females": 100, "total": 90}
    for col in columns:
        tree.heading(col, text=headings[col])
        tree.column(col, width=widths[col], anchor="center")

    scroll = ttk.Scrollbar(detail_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scroll.set)
    tree.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")

    cursor.execute("SELECT id, mating_info, birth_date, males_count, females_count, total_puppies FROM litters ORDER BY birth_date DESC, id DESC")
    for row in cursor.fetchall():
        tree.insert("", tk.END, values=row)

    tk.Button(rep_window, text="🔄 Ανανέωση Αναφορών", command=lambda: [rep_window.destroy(), open_reports()], font=("Arial", 11, "bold"), width=22).pack(pady=8)


# ==========================================
# ΕΝΟΤΗΤΑ: BACKUP ΒΑΣΗΣ
# ==========================================


def open_backup():
    import os
    import shutil
    from tkinter import filedialog

    backup_window = tk.Toplevel(window)
    backup_window.title("Backup - Εκτροφείο de la Dirfis")
    backup_window.geometry("650x430")
    backup_window.minsize(600, 380)

    tk.Label(
        backup_window,
        text="💾 BACKUP ΒΑΣΗΣ ΔΕΔΟΜΕΝΩΝ",
        font=("Arial", 20, "bold"),
    ).pack(pady=15)

    tk.Label(
        backup_window,
        text=(
            "Το Backup κρατάει αντίγραφο ολόκληρης της βάσης\n"
            "με όλους τους σκύλους, γέννες, κουτάβια, πελάτες και οικονομικά.\n\n"
            "Μην διαγράψεις ποτέ το αρχικό de_la_dirfis.db."
        ),
        font=("Arial", 11),
        justify="center",
    ).pack(pady=10)

    status = tk.Label(backup_window, text="Έτοιμο για Backup.", font=("Arial", 11, "bold"))
    status.pack(pady=10)

    def create_backup():
        folder = filedialog.askdirectory(title="Επίλεξε πού θα αποθηκευτεί το Backup")
        if not folder:
            return

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_name = f"de_la_dirfis_BACKUP_{timestamp}.db"
        destination = os.path.join(folder, backup_name)

        try:
            # Commit πρώτα για να γραφτούν όλα τα δεδομένα στο αρχείο.
            conn.commit()
            shutil.copy2(DB_NAME, destination)
            status.config(text=f"✅ Το Backup δημιουργήθηκε:\n{backup_name}")
            messagebox.showinfo(
                "Backup ολοκληρώθηκε",
                f"Το αντίγραφο ασφαλείας δημιουργήθηκε με επιτυχία.\n\n{destination}",
            )
        except Exception as e:
            messagebox.showerror("Σφάλμα Backup", f"Δεν μπόρεσε να δημιουργηθεί το Backup.\n\n{e}")

    def open_database_folder():
        import os
        folder = os.path.abspath(os.path.dirname(DB_NAME) or ".")
        try:
            os.startfile(folder)
        except Exception as e:
            messagebox.showerror("Σφάλμα", f"Δεν μπόρεσε να ανοίξει ο φάκελος.\n\n{e}")

    tk.Button(
        backup_window,
        text="💾 Δημιουργία Backup",
        command=create_backup,
        font=("Arial", 12, "bold"),
        width=25,
        height=2,
    ).pack(pady=10)

    tk.Button(
        backup_window,
        text="📂 Άνοιγμα φακέλου προγράμματος",
        command=open_database_folder,
        font=("Arial", 11, "bold"),
        width=28,
    ).pack(pady=8)

    tk.Button(
        backup_window,
        text="✖ Κλείσιμο",
        command=backup_window.destroy,
        font=("Arial", 11, "bold"),
        width=18,
    ).pack(pady=15)


# ==========================================
# ΚΕΝΤΡΙΚΗ ΟΘΟΝΗ & ΚΟΥΜΠΙΑ
# ==========================================

title = tk.Label(
    window, text="Εκτροφείο de la Dirfis", font=("Arial", 28, "bold")
)
title.pack(pady=(30, 5))

subtitle = tk.Label(
    window,
    text="Διαχείριση Εκτροφής & Εκπαίδευσης Κυνηγετικών Σκύλων",
    font=("Arial", 13),
)
subtitle.pack(pady=(0, 30))

main_frame = tk.Frame(window)
main_frame.pack()

button_style = {"font": ("Arial", 13, "bold"), "width": 25, "height": 2}

tk.Button(
    main_frame, text="🐕  Σκύλοι", command=open_dogs, **button_style
).grid(row=0, column=0, padx=10, pady=8)

tk.Button(
    main_frame, text="❤️  Ζευγαρώματα", command=open_matings, **button_style
).grid(row=0, column=1, padx=10, pady=8)

tk.Button(
    main_frame, text="🐶  Γέννες", command=open_litters, **button_style
).grid(row=1, column=0, padx=10, pady=8)

tk.Button(
    main_frame, text="🐾  Κουτάβια / Πωλήσεις", command=open_puppies, **button_style
).grid(row=1, column=1, padx=10, pady=8)

tk.Button(
    main_frame,
    text="🎯  Εκπαίδευση Σκύλων",
    command=open_training,
    **button_style,
).grid(row=2, column=0, padx=10, pady=8)

tk.Button(
    main_frame,
    text="👤  Ενδιαφερόμενοι / Πελάτες",
    command=open_clients,
    **button_style,
).grid(row=2, column=1, padx=10, pady=8)

# ΣΥΝΔΕΔΕΜΕΝΟ ΚΟΥΜΠΙ ΟΙΚΟΝΟΜΙΚΩΝ
tk.Button(
    main_frame,
    text="💰  Οικονομικά / Πληρωμές",
    command=open_finances,
    **button_style,
).grid(row=3, column=0, padx=10, pady=8)

tk.Button(
    main_frame,
    text="📊  Αναφορές",
    command=open_reports,
    **button_style,
).grid(row=3, column=1, padx=10, pady=8)

tk.Button(
    main_frame,
    text="💾  Backup",
    command=open_backup,
    **button_style,
).grid(row=4, column=0, columnspan=2, pady=20)


def close_program():
    conn.close()
    window.destroy()


window.protocol("WM_DELETE_WINDOW", close_program)

window.mainloop()
