# =============================================================================
# CERTIFICATE VERIFICATION SYSTEM
# Minor Project | Python + Tkinter + SQLite
# =============================================================================
# Description:
#   This application allows an institution to:
#     1. Add new certificate records to a local SQLite database
#     2. Verify whether a certificate is genuine using Certificate ID
#     3. View all stored certificate records in a table
#     4. Search certificates by ID, name, or roll number
#     5. Delete certificate records with confirmation
#
# Run:  python certificate_verification.py
# =============================================================================

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os

# --------------------------------------------------------------------------
# DATABASE SETUP
# --------------------------------------------------------------------------

# Name of the local SQLite database file
DB_NAME = "certificates.db"


def init_database():
    """
    Creates the SQLite database file and the 'certificates' table
    if they do not already exist.
    Called once when the application starts.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create the certificates table with all required fields
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS certificates (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            certificate_id TEXT    UNIQUE NOT NULL,
            student_name   TEXT    NOT NULL,
            roll_number    TEXT    NOT NULL,
            course_name    TEXT    NOT NULL,
            department     TEXT    NOT NULL,
            issue_date     TEXT    NOT NULL,
            grade          TEXT    NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# --------------------------------------------------------------------------
# DATABASE HELPER FUNCTIONS
# --------------------------------------------------------------------------

def get_connection():
    """Returns a new SQLite connection to the database."""
    return sqlite3.connect(DB_NAME)


def add_certificate(cert_id, name, roll, course, dept, date, grade):
    """
    Inserts a new certificate record into the database.

    Parameters:
        cert_id  - Unique Certificate ID
        name     - Student's full name
        roll     - Student's roll number
        course   - Course name
        dept     - Department name
        date     - Date of issue (string)
        grade    - Grade or CGPA

    Returns:
        (True, "Success message")  on success
        (False, "Error message")   on failure (e.g., duplicate ID)
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO certificates
                (certificate_id, student_name, roll_number, course_name,
                 department, issue_date, grade)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (cert_id, name, roll, course, dept, date, grade))
        conn.commit()
        conn.close()
        return True, "Certificate added successfully!"
    except sqlite3.IntegrityError:
        # Triggered when certificate_id UNIQUE constraint is violated
        return False, "Certificate ID already exists. Please use a unique ID."
    except Exception as e:
        return False, f"An error occurred: {str(e)}"


def verify_certificate(cert_id):
    """
    Looks up a certificate by its Certificate ID.

    Parameters:
        cert_id - The Certificate ID to search for

    Returns:
        A dictionary with certificate data if found, or None if not found.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT certificate_id, student_name, roll_number, course_name,
                   department, issue_date, grade
            FROM certificates
            WHERE certificate_id = ?
        """, (cert_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            # Return a dictionary for easy access by field name
            return {
                "certificate_id": row[0],
                "student_name":   row[1],
                "roll_number":    row[2],
                "course_name":    row[3],
                "department":     row[4],
                "issue_date":     row[5],
                "grade":          row[6]
            }
        return None
    except Exception as e:
        messagebox.showerror("Database Error", str(e))
        return None


def get_all_certificates():
    """
    Fetches all certificate records from the database.

    Returns:
        A list of tuples — each tuple is one row from the certificates table.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT certificate_id, student_name, roll_number,
                   course_name, department, issue_date, grade
            FROM certificates
            ORDER BY id DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        messagebox.showerror("Database Error", str(e))
        return []


def search_certificates(keyword):
    """
    Searches for certificates matching a keyword in:
        - certificate_id
        - student_name
        - roll_number

    Parameters:
        keyword - The search term entered by the user

    Returns:
        A list of matching rows (tuples).
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        pattern = f"%{keyword}%"  # SQL LIKE pattern for partial matching
        cursor.execute("""
            SELECT certificate_id, student_name, roll_number,
                   course_name, department, issue_date, grade
            FROM certificates
            WHERE certificate_id LIKE ?
               OR student_name   LIKE ?
               OR roll_number    LIKE ?
        """, (pattern, pattern, pattern))
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        messagebox.showerror("Database Error", str(e))
        return []


def delete_certificate(cert_id):
    """
    Deletes a certificate record from the database by Certificate ID.

    Parameters:
        cert_id - The Certificate ID of the record to delete

    Returns:
        (True, "Success message")  if deletion was successful
        (False, "Error message")   if not found or error occurred
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM certificates WHERE certificate_id = ?", (cert_id,)
        )
        affected = cursor.rowcount  # Number of rows deleted
        conn.commit()
        conn.close()

        if affected > 0:
            return True, "Certificate deleted successfully."
        else:
            return False, "No certificate found with that ID."
    except Exception as e:
        return False, f"An error occurred: {str(e)}"


# --------------------------------------------------------------------------
# SAMPLE DATA LOADER
# --------------------------------------------------------------------------

def load_sample_data():
    """
    Inserts sample certificate records into the database for testing.
    Records are only added if the table is currently empty.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM certificates")
    count = cursor.fetchone()[0]
    conn.close()

    if count == 0:
        # Sample records for demonstration / testing
        samples = [
            ("CERT-2024-001", "Aarav Sharma",    "20CS001", "B.Tech Computer Science", "CSE",  "15-06-2024", "9.2"),
            ("CERT-2024-002", "Priya Patel",     "20EC045", "B.Tech Electronics",      "ECE",  "15-06-2024", "8.7"),
            ("CERT-2024-003", "Rahul Verma",     "20ME012", "Diploma Mechanical Engg", "MECH", "20-06-2024", "7.5"),
            ("CERT-2024-004", "Sneha Iyer",      "20CS078", "B.Tech Computer Science", "CSE",  "15-06-2024", "9.8"),
            ("CERT-2024-005", "Arjun Nair",      "20CE030", "B.Tech Civil Engg",       "CIVIL","22-06-2024", "8.1"),
        ]
        conn = get_connection()
        cursor = conn.cursor()
        cursor.executemany("""
            INSERT OR IGNORE INTO certificates
                (certificate_id, student_name, roll_number, course_name,
                 department, issue_date, grade)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, samples)
        conn.commit()
        conn.close()


# =============================================================================
# GUI WINDOW CLASSES
# =============================================================================

# --------------------------------------------------------------------------
# ADD CERTIFICATE WINDOW
# --------------------------------------------------------------------------

class AddCertificateWindow(tk.Toplevel):
    """
    A popup window form for adding a new certificate record.
    Validates inputs and saves to the database.
    """

    def __init__(self, parent, refresh_callback=None):
        super().__init__(parent)
        self.title("Add New Certificate")
        self.geometry("480x520")
        self.resizable(False, False)
        self.configure(bg="#f0f4f8")
        self.grab_set()  # Make this window modal (blocks parent interaction)

        self.refresh_callback = refresh_callback  # Called after successful add

        self._build_ui()

    def _build_ui(self):
        """Builds all form widgets inside the window."""

        # ----- Title Label -----
        tk.Label(
            self, text="ADD NEW CERTIFICATE",
            font=("Arial", 14, "bold"), bg="#1a3c5e", fg="white",
            pady=10
        ).pack(fill="x")

        # ----- Form Frame -----
        form_frame = tk.Frame(self, bg="#f0f4f8", padx=30, pady=15)
        form_frame.pack(fill="both", expand=True)

        # Field labels and corresponding StringVar entries
        fields = [
            ("Certificate ID *",  "cert_id"),
            ("Student Name *",    "student_name"),
            ("Roll Number *",     "roll_number"),
            ("Course Name *",     "course_name"),
            ("Department *",      "department"),
            ("Date of Issue *",   "issue_date"),
            ("Grade / CGPA *",    "grade"),
        ]

        self.entries = {}  # Dictionary to hold Entry widgets by field key

        for i, (label_text, key) in enumerate(fields):
            # Label
            tk.Label(
                form_frame, text=label_text,
                font=("Arial", 10), bg="#f0f4f8", anchor="w"
            ).grid(row=i, column=0, sticky="w", pady=5)

            # Entry widget
            entry = tk.Entry(form_frame, font=("Arial", 10), width=28,
                             relief="solid", bd=1)
            entry.grid(row=i, column=1, sticky="ew", padx=(10, 0), pady=5)
            self.entries[key] = entry

        # Placeholder hint for date field
        self.entries["issue_date"].insert(0, "DD-MM-YYYY")
        self.entries["issue_date"].config(fg="grey")
        self.entries["issue_date"].bind("<FocusIn>",  self._clear_date_hint)
        self.entries["issue_date"].bind("<FocusOut>", self._restore_date_hint)

        form_frame.columnconfigure(1, weight=1)

        # ----- Note Label -----
        tk.Label(
            self, text="* All fields are mandatory",
            font=("Arial", 8), bg="#f0f4f8", fg="#666"
        ).pack(anchor="w", padx=30)

        # ----- Buttons -----
        btn_frame = tk.Frame(self, bg="#f0f4f8", pady=15)
        btn_frame.pack()

        tk.Button(
            btn_frame, text="  SAVE CERTIFICATE  ",
            font=("Arial", 10, "bold"), bg="#1a3c5e", fg="white",
            relief="flat", cursor="hand2", padx=10, pady=6,
            command=self._save
        ).grid(row=0, column=0, padx=8)

        tk.Button(
            btn_frame, text="  CLEAR  ",
            font=("Arial", 10), bg="#888", fg="white",
            relief="flat", cursor="hand2", padx=10, pady=6,
            command=self._clear_fields
        ).grid(row=0, column=1, padx=8)

    def _clear_date_hint(self, event):
        """Clears the placeholder hint when date field is focused."""
        if self.entries["issue_date"].get() == "DD-MM-YYYY":
            self.entries["issue_date"].delete(0, tk.END)
            self.entries["issue_date"].config(fg="black")

    def _restore_date_hint(self, event):
        """Restores the placeholder hint if date field is left empty."""
        if self.entries["issue_date"].get() == "":
            self.entries["issue_date"].insert(0, "DD-MM-YYYY")
            self.entries["issue_date"].config(fg="grey")

    def _clear_fields(self):
        """Clears all input fields in the form."""
        for key, entry in self.entries.items():
            entry.delete(0, tk.END)
        self.entries["issue_date"].insert(0, "DD-MM-YYYY")
        self.entries["issue_date"].config(fg="grey")

    def _save(self):
        """
        Reads values from the form, validates them,
        and calls add_certificate() to store the record.
        """
        # Read all field values (strip whitespace)
        cert_id = self.entries["cert_id"].get().strip()
        name    = self.entries["student_name"].get().strip()
        roll    = self.entries["roll_number"].get().strip()
        course  = self.entries["course_name"].get().strip()
        dept    = self.entries["department"].get().strip()
        date    = self.entries["issue_date"].get().strip()
        grade   = self.entries["grade"].get().strip()

        # Remove placeholder if still present
        if date == "DD-MM-YYYY":
            date = ""

        # ----- Validation -----
        if not all([cert_id, name, roll, course, dept, date, grade]):
            messagebox.showwarning(
                "Missing Fields",
                "All fields are mandatory.\nPlease fill in every field.",
                parent=self
            )
            return

        # ----- Save to Database -----
        success, message = add_certificate(
            cert_id, name, roll, course, dept, date, grade
        )

        if success:
            messagebox.showinfo("Success", message, parent=self)
            self._clear_fields()
            # Refresh parent table if a callback is provided
            if self.refresh_callback:
                self.refresh_callback()
        else:
            messagebox.showerror("Error", message, parent=self)


# --------------------------------------------------------------------------
# VIEW / SEARCH CERTIFICATES WINDOW
# --------------------------------------------------------------------------

class ViewCertificatesWindow(tk.Toplevel):
    """
    A popup window that displays all certificate records in a table.
    Supports searching by Certificate ID, Name, or Roll Number.
    Also allows deleting a selected record.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.title("All Certificate Records")
        self.geometry("900x520")
        self.configure(bg="#f0f4f8")
        self.grab_set()

        self._build_ui()
        self._load_all()  # Load all records when window opens

    def _build_ui(self):
        """Builds the search bar, table, and action buttons."""

        # ----- Title -----
        tk.Label(
            self, text="CERTIFICATE RECORDS",
            font=("Arial", 14, "bold"), bg="#1a3c5e", fg="white", pady=10
        ).pack(fill="x")

        # ----- Search Bar -----
        search_frame = tk.Frame(self, bg="#f0f4f8", pady=8, padx=15)
        search_frame.pack(fill="x")

        tk.Label(
            search_frame, text="Search:", font=("Arial", 10),
            bg="#f0f4f8"
        ).pack(side="left")

        self.search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_frame, textvariable=self.search_var,
            font=("Arial", 10), width=30, relief="solid", bd=1
        )
        search_entry.pack(side="left", padx=8)

        tk.Button(
            search_frame, text="Search",
            font=("Arial", 9), bg="#1a3c5e", fg="white",
            relief="flat", cursor="hand2", padx=8,
            command=self._do_search
        ).pack(side="left", padx=4)

        tk.Button(
            search_frame, text="Show All",
            font=("Arial", 9), bg="#555", fg="white",
            relief="flat", cursor="hand2", padx=8,
            command=self._load_all
        ).pack(side="left", padx=4)

        # ----- Table (Treeview) -----
        table_frame = tk.Frame(self, bg="#f0f4f8")
        table_frame.pack(fill="both", expand=True, padx=15, pady=5)

        # Column definitions
        columns = (
            "cert_id", "student_name", "roll_number",
            "course_name", "department", "issue_date", "grade"
        )
        col_headings = {
            "cert_id":      "Certificate ID",
            "student_name": "Student Name",
            "roll_number":  "Roll Number",
            "course_name":  "Course",
            "department":   "Department",
            "issue_date":   "Date of Issue",
            "grade":        "Grade/CGPA",
        }
        col_widths = [130, 150, 100, 180, 90, 100, 80]

        # Scrollbars
        y_scroll = ttk.Scrollbar(table_frame, orient="vertical")
        x_scroll = ttk.Scrollbar(table_frame, orient="horizontal")
        y_scroll.pack(side="right", fill="y")
        x_scroll.pack(side="bottom", fill="x")

        self.tree = ttk.Treeview(
            table_frame, columns=columns, show="headings",
            yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set,
            selectmode="browse"
        )

        # Configure column headings and widths
        for col, width in zip(columns, col_widths):
            self.tree.heading(col, text=col_headings[col])
            self.tree.column(col, width=width, anchor="center")

        y_scroll.config(command=self.tree.yview)
        x_scroll.config(command=self.tree.xview)
        self.tree.pack(fill="both", expand=True)

        # Alternating row colors for readability
        self.tree.tag_configure("even", background="#eaf0f8")
        self.tree.tag_configure("odd",  background="#ffffff")

        # ----- Status + Delete Button -----
        bottom_frame = tk.Frame(self, bg="#f0f4f8", pady=8, padx=15)
        bottom_frame.pack(fill="x")

        self.status_label = tk.Label(
            bottom_frame, text="", font=("Arial", 9),
            bg="#f0f4f8", fg="#333"
        )
        self.status_label.pack(side="left")

        tk.Button(
            bottom_frame, text="Delete Selected",
            font=("Arial", 9, "bold"), bg="#c0392b", fg="white",
            relief="flat", cursor="hand2", padx=10, pady=4,
            command=self._delete_selected
        ).pack(side="right")

    def _load_all(self):
        """Loads all certificate records into the table."""
        self.search_var.set("")
        rows = get_all_certificates()
        self._populate_table(rows)

    def _do_search(self):
        """Searches for records matching the entered keyword."""
        keyword = self.search_var.get().strip()
        if not keyword:
            messagebox.showwarning(
                "Search", "Please enter a search term.", parent=self
            )
            return
        rows = search_certificates(keyword)
        self._populate_table(rows)

    def _populate_table(self, rows):
        """
        Clears the table and inserts the given rows.

        Parameters:
            rows - List of tuples from the database query
        """
        # Clear existing rows
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not rows:
            self.status_label.config(text="No records found.")
            return

        # Insert each row with alternating colors
        for index, row in enumerate(rows):
            tag = "even" if index % 2 == 0 else "odd"
            self.tree.insert("", "end", values=row, tags=(tag,))

        self.status_label.config(text=f"Total records: {len(rows)}")

    def _delete_selected(self):
        """
        Deletes the currently selected row after user confirmation.
        """
        selected = self.tree.selection()  # Get selected row ID
        if not selected:
            messagebox.showwarning(
                "No Selection",
                "Please select a certificate row to delete.",
                parent=self
            )
            return

        # Get the Certificate ID from the first column of the selected row
        values = self.tree.item(selected[0], "values")
        cert_id = values[0]
        student = values[1]

        # ----- Confirmation Dialog -----
        confirmed = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete this certificate?\n\n"
            f"Certificate ID : {cert_id}\n"
            f"Student Name   : {student}\n\n"
            f"This action cannot be undone.",
            parent=self
        )

        if confirmed:
            success, message = delete_certificate(cert_id)
            if success:
                messagebox.showinfo("Deleted", message, parent=self)
                self._load_all()  # Refresh the table
            else:
                messagebox.showerror("Error", message, parent=self)


# --------------------------------------------------------------------------
# MAIN APPLICATION WINDOW
# --------------------------------------------------------------------------

class CertificateVerificationApp(tk.Tk):
    """
    The main application window.
    Contains:
        - Left Panel  : Administrator controls (Add, View, Delete, Exit)
        - Right Panel : Verification panel (Enter ID → check certificate)
    """

    def __init__(self):
        super().__init__()
        self.title("CERTIFICATE VERIFICATION SYSTEM")
        self.geometry("860x580")
        self.resizable(False, False)
        self.configure(bg="#0d1f35")

        self._build_header()
        self._build_body()
        self._build_footer()

    # ------------------------------------------------------------------
    # UI BUILDERS
    # ------------------------------------------------------------------

    def _build_header(self):
        """Creates the top title bar of the application."""
        header = tk.Frame(self, bg="#1a3c5e", pady=14)
        header.pack(fill="x")

        tk.Label(
            header,
            text="🎓  CERTIFICATE VERIFICATION SYSTEM",
            font=("Arial", 17, "bold"),
            bg="#1a3c5e", fg="white"
        ).pack()

        tk.Label(
            header,
            text="Institutional Digital Certificate Management & Verification Portal",
            font=("Arial", 9),
            bg="#1a3c5e", fg="#a8c8e8"
        ).pack()

    def _build_body(self):
        """Creates the two-panel body layout."""
        body = tk.Frame(self, bg="#0d1f35", pady=15, padx=15)
        body.pack(fill="both", expand=True)

        # Left panel (Admin Controls)
        self._build_left_panel(body)

        # Divider
        tk.Frame(body, bg="#2a4a6e", width=2).pack(
            side="left", fill="y", padx=15
        )

        # Right panel (Verification)
        self._build_right_panel(body)

    def _build_left_panel(self, parent):
        """
        Builds the Administrator Panel with action buttons.
        Located on the left side of the main window.
        """
        left = tk.Frame(parent, bg="#0d1f35")
        left.pack(side="left", fill="y", padx=(0, 10))

        # Section title
        tk.Label(
            left,
            text="🔧  ADMINISTRATOR PANEL",
            font=("Arial", 11, "bold"),
            bg="#0d1f35", fg="#a8c8e8", pady=5
        ).pack(anchor="w")

        tk.Frame(left, bg="#2a4a6e", height=2).pack(fill="x", pady=6)

        tk.Label(
            left,
            text="Manage certificate records\nusing the options below.",
            font=("Arial", 9), bg="#0d1f35", fg="#7a9fc0",
            justify="left"
        ).pack(anchor="w", pady=(0, 15))

        # Button definitions: (label, command, color)
        buttons = [
            ("➕  Add Certificate",    self._open_add_window,  "#1a6b35"),
            ("📋  View Certificates",  self._open_view_window, "#1a4a6e"),
            ("🔍  Search Records",     self._open_view_window, "#3a2a6e"),
            ("🗑  Delete Certificate", self._open_delete_dialog,"#7a1a1a"),
            ("❌  Exit Application",   self._exit_app,         "#444444"),
        ]

        for label, cmd, color in buttons:
            tk.Button(
                left, text=label,
                font=("Arial", 10, "bold"),
                bg=color, fg="white",
                relief="flat", cursor="hand2",
                width=22, pady=8, anchor="w", padx=12,
                command=cmd
            ).pack(pady=5, fill="x")

        # Brief stats display
        tk.Frame(left, bg="#2a4a6e", height=2).pack(fill="x", pady=10)
        self.stats_label = tk.Label(
            left, text="", font=("Arial", 9),
            bg="#0d1f35", fg="#a8c8e8", justify="left"
        )
        self.stats_label.pack(anchor="w")
        self._refresh_stats()

    def _build_right_panel(self, parent):
        """
        Builds the Verification Panel.
        Located on the right side of the main window.
        """
        right = tk.Frame(parent, bg="#0d1f35")
        right.pack(side="left", fill="both", expand=True)

        # Section title
        tk.Label(
            right,
            text="✅  VERIFICATION PANEL",
            font=("Arial", 11, "bold"),
            bg="#0d1f35", fg="#a8c8e8", pady=5
        ).pack(anchor="w")

        tk.Frame(right, bg="#2a4a6e", height=2).pack(fill="x", pady=6)

        tk.Label(
            right,
            text="Enter a Certificate ID below to verify its authenticity.",
            font=("Arial", 9), bg="#0d1f35", fg="#7a9fc0"
        ).pack(anchor="w", pady=(0, 12))

        # ----- Certificate ID Input -----
        input_frame = tk.Frame(right, bg="#0d1f35")
        input_frame.pack(anchor="w")

        tk.Label(
            input_frame, text="Certificate ID:",
            font=("Arial", 10, "bold"), bg="#0d1f35", fg="#c8dff0"
        ).grid(row=0, column=0, sticky="w", pady=5)

        self.verify_entry = tk.Entry(
            input_frame, font=("Arial", 11), width=24,
            relief="solid", bd=1
        )
        self.verify_entry.grid(row=0, column=1, padx=10, pady=5)

        # Allow pressing Enter to trigger verification
        self.verify_entry.bind("<Return>", lambda e: self._do_verify())

        tk.Button(
            input_frame, text="  VERIFY  ",
            font=("Arial", 10, "bold"), bg="#1a6b35", fg="white",
            relief="flat", cursor="hand2", padx=10, pady=5,
            command=self._do_verify
        ).grid(row=0, column=2, padx=5)

        tk.Button(
            input_frame, text="Clear",
            font=("Arial", 9), bg="#555", fg="white",
            relief="flat", cursor="hand2", padx=6, pady=5,
            command=self._clear_verify
        ).grid(row=0, column=3, padx=4)

        # ----- Result Area -----
        tk.Frame(right, bg="#2a4a6e", height=1).pack(fill="x", pady=10)

        tk.Label(
            right, text="Verification Result:",
            font=("Arial", 10, "bold"), bg="#0d1f35", fg="#c8dff0"
        ).pack(anchor="w")

        # Result display box
        result_outer = tk.Frame(right, bg="#122840", bd=1, relief="solid")
        result_outer.pack(fill="both", expand=True, pady=8)

        self.result_text = tk.Text(
            result_outer,
            font=("Courier", 10),
            bg="#122840", fg="#c8dff0",
            relief="flat", bd=8,
            state="disabled",   # Read-only by default
            wrap="word",
            height=14
        )
        self.result_text.pack(fill="both", expand=True)

        # Configure text tags for coloring different parts
        self.result_text.tag_config("verified",  foreground="#2ecc71", font=("Courier", 11, "bold"))
        self.result_text.tag_config("invalid",   foreground="#e74c3c", font=("Courier", 11, "bold"))
        self.result_text.tag_config("label",     foreground="#7a9fc0", font=("Courier", 10))
        self.result_text.tag_config("value",     foreground="#e8f4ff", font=("Courier", 10, "bold"))
        self.result_text.tag_config("separator", foreground="#2a4a6e")

        # Default placeholder message
        self._show_placeholder()

    def _build_footer(self):
        """Creates the bottom status bar."""
        footer = tk.Frame(self, bg="#0a1520", pady=5)
        footer.pack(fill="x", side="bottom")

        tk.Label(
            footer,
            text="Certificate Verification System  |  Minor Project  |  Python + Tkinter + SQLite",
            font=("Arial", 8), bg="#0a1520", fg="#4a6a8a"
        ).pack()

    # ------------------------------------------------------------------
    # ACTION HANDLERS
    # ------------------------------------------------------------------

    def _do_verify(self):
        """
        Reads the Certificate ID from the input field,
        calls verify_certificate(), and displays the result.
        """
        cert_id = self.verify_entry.get().strip()

        if not cert_id:
            messagebox.showwarning(
                "Input Required",
                "Please enter a Certificate ID to verify."
            )
            return

        # Query the database
        record = verify_certificate(cert_id)

        # Display the result
        self._display_result(record)

    def _display_result(self, record):
        """
        Updates the result text area with certificate details or error.

        Parameters:
            record - A dictionary of certificate data, or None if not found.
        """
        # Enable editing temporarily
        self.result_text.config(state="normal")
        self.result_text.delete("1.0", tk.END)

        sep = "─" * 42 + "\n"

        if record:
            # ----- VERIFIED -----
            self.result_text.insert(tk.END, "\n")
            self.result_text.insert(tk.END, "  ✅  Certificate Status: VERIFIED\n", "verified")
            self.result_text.insert(tk.END, sep, "separator")

            # Display each field
            fields = [
                ("  Certificate ID", record["certificate_id"]),
                ("  Student Name  ", record["student_name"]),
                ("  Roll Number   ", record["roll_number"]),
                ("  Course Name   ", record["course_name"]),
                ("  Department    ", record["department"]),
                ("  Date of Issue ", record["issue_date"]),
                ("  Grade / CGPA  ", record["grade"]),
            ]
            for label, value in fields:
                self.result_text.insert(tk.END, f"{label}  :  ", "label")
                self.result_text.insert(tk.END, f"{value}\n",     "value")

            self.result_text.insert(tk.END, sep, "separator")
            self.result_text.insert(
                tk.END,
                "  This certificate is authentic and issued by\n"
                "  the institution's records database.\n",
                "label"
            )
        else:
            # ----- INVALID -----
            self.result_text.insert(tk.END, "\n")
            self.result_text.insert(
                tk.END, "  ❌  Certificate Status: INVALID CERTIFICATE\n", "invalid"
            )
            self.result_text.insert(tk.END, sep, "separator")
            self.result_text.insert(
                tk.END,
                "\n  No matching record found in the database.\n\n"
                "  Possible reasons:\n"
                "    • The Certificate ID entered is incorrect.\n"
                "    • The certificate was never issued by this institution.\n"
                "    • The record may have been deleted.\n\n"
                "  Please double-check the ID and try again.",
                "label"
            )

        # Make read-only again
        self.result_text.config(state="disabled")

    def _show_placeholder(self):
        """Displays the default placeholder message in the result area."""
        self.result_text.config(state="normal")
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(
            tk.END,
            "\n\n  Enter a Certificate ID in the field above\n"
            "  and click VERIFY to check its authenticity.\n\n"
            "  Example IDs to try:\n"
            "    CERT-2024-001\n"
            "    CERT-2024-002\n"
            "    CERT-2024-003",
            "label"
        )
        self.result_text.config(state="disabled")

    def _clear_verify(self):
        """Clears the verification input and result area."""
        self.verify_entry.delete(0, tk.END)
        self._show_placeholder()

    def _open_add_window(self):
        """Opens the Add Certificate popup window."""
        AddCertificateWindow(self, refresh_callback=self._refresh_stats)

    def _open_view_window(self):
        """Opens the View / Search Certificates popup window."""
        ViewCertificatesWindow(self)

    def _open_delete_dialog(self):
        """
        Opens a simple dialog prompting for a Certificate ID to delete.
        Uses a Toplevel dialog instead of opening the full view window.
        """
        dialog = tk.Toplevel(self)
        dialog.title("Delete Certificate")
        dialog.geometry("380x180")
        dialog.resizable(False, False)
        dialog.configure(bg="#f0f4f8")
        dialog.grab_set()

        tk.Label(
            dialog, text="DELETE CERTIFICATE",
            font=("Arial", 12, "bold"), bg="#7a1a1a", fg="white", pady=8
        ).pack(fill="x")

        inner = tk.Frame(dialog, bg="#f0f4f8", pady=20, padx=30)
        inner.pack(fill="both", expand=True)

        tk.Label(
            inner, text="Enter Certificate ID to delete:",
            font=("Arial", 10), bg="#f0f4f8"
        ).grid(row=0, column=0, sticky="w")

        del_entry = tk.Entry(inner, font=("Arial", 10), width=22,
                             relief="solid", bd=1)
        del_entry.grid(row=1, column=0, pady=10, sticky="ew")

        def confirm_delete():
            cert_id = del_entry.get().strip()
            if not cert_id:
                messagebox.showwarning(
                    "Input Required", "Please enter a Certificate ID.", parent=dialog
                )
                return
            # Confirmation dialog
            yes = messagebox.askyesno(
                "Confirm Deletion",
                f"Are you sure you want to delete certificate:\n{cert_id}?\n\n"
                f"This cannot be undone.",
                parent=dialog
            )
            if yes:
                success, message = delete_certificate(cert_id)
                if success:
                    messagebox.showinfo("Deleted", message, parent=dialog)
                    self._refresh_stats()
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", message, parent=dialog)

        tk.Button(
            inner, text="DELETE",
            font=("Arial", 10, "bold"), bg="#7a1a1a", fg="white",
            relief="flat", cursor="hand2", padx=12, pady=5,
            command=confirm_delete
        ).grid(row=2, column=0, sticky="ew")

    def _refresh_stats(self):
        """Updates the small stats label on the left panel."""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM certificates")
            total = cursor.fetchone()[0]
            conn.close()
            self.stats_label.config(
                text=f"📊 Total Records in Database:\n    {total} certificate(s)"
            )
        except Exception:
            pass

    def _exit_app(self):
        """Asks for confirmation before closing the application."""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.destroy()


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    # Step 1: Create database and table if not present
    init_database()

    # Step 2: Load sample data for demonstration (only if table is empty)
    load_sample_data()

    # Step 3: Launch the main application window
    app = CertificateVerificationApp()
    app.mainloop()
