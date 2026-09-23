import os
import flet as ft
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, db

# --- 1. تهيئة الاتصال بـ Firebase (سحابياً) ---
json_file = "serviceAccountKey.json"
firebase_initialized = False

if os.path.exists(json_file):
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(json_file)
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://king-137e3-default-rtdb.firebaseio.com' # رابط قاعدة بياناتك
            })
        firebase_initialized = True
        print("تم الاتصال بـ Firebase بنجاح!")
    except Exception as e:
        print(f"خطأ في التهيئة: {e}")

# --- 2. دالّات التعامل مع البيانات أونلاين ---
def load_data():
    if not firebase_initialized:
        return {"credentials": {"username": "1", "password": "2"}, "customers": {}}
    try:
        ref = db.reference('/')
        data = ref.get()
        if not data:
            default_data = {"credentials": {"username": "1", "password": "2"}, "customers": {}}
            ref.set(default_data)
            return default_data
        if "customers" not in data or data["customers"] is None:
            data["customers"] = {}
        if "credentials" not in data or data["credentials"] is None:
            data["credentials"] = {"username": "1", "password": "2"}
        return data
    except Exception as e:
        print(f"Error loading online data: {e}")
        return {"credentials": {"username": "1", "password": "2"}, "customers": {}}

def save_data_to_firebase(data):
    if not firebase_initialized:
        return False
    try:
        ref = db.reference('/')
        ref.set(data)
        return True
    except Exception as e:
        print(f"Error saving to Firebase: {e}")
        return False

# --- 3. التطبيق الرئيسي ---
def main(page: ft.Page):
    page.title = "نظام الأقساط وإدارة الأموال (سحابي)"
    page.rtl = True
    page.bgcolor = "#0B0F19"
    page.padding = 0
    page.spacing = 0

    app_data = load_data()
    credentials_data = app_data.get("credentials", {"username": "1", "password": "2"})
    customers_data = app_data.get("customers", {})

    def save_app_state():
        full_data = {
            "credentials": credentials_data,
            "customers": customers_data
        }
        save_data_to_firebase(full_data)

    # --- شاشة تسجيل الدخول ---
    def show_login_screen():
        page.clean()
        page.bgcolor = "#0B192C"
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        status_msg = ""
        status_color = "#94A3B8"
        if not firebase_initialized:
            status_msg = "⚠️ لم يتم العثور على ملف serviceAccountKey.json (الوضع محلي)"
            status_color = "#F59E0B"
        else:
            status_msg = "🟢 متصل بالسحابة (Online)"
            status_color = "#10B981"

        custom_logo = ft.Container(
            content=ft.Row([
                ft.Text("H S", size=22, weight=ft.FontWeight.BOLD, color="#38bdf8"),
                ft.VerticalDivider(width=10, color="#38bdf8", thickness=2),
                ft.Column([
                    ft.Text("SYSTEMS", size=11, weight=ft.FontWeight.BOLD, color="white"),
                    ft.Text("FINANCE & INSTALLMENTS", size=8, color="#94A3B8"),
                ], spacing=0)
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            padding=12,
            bgcolor="#1E3E62",
            border_radius=8
        )

        error_text = ft.Text(value="", color="#f87171", weight=ft.FontWeight.BOLD, size=12)

        def handle_login(e):
            latest_data = load_data()
            creds = latest_data.get("credentials", credentials_data)
            if username_field.value == creds["username"] and password_field.value == creds["password"]:
                show_main_app()
            else:
                error_text.value = "خطأ في اسم المستخدم أو كلمة السر!"
                page.update()

        def handle_cancel(e):
            username_field.value = ""
            password_field.value = ""
            error_text.value = ""
            page.update()

        username_field = ft.TextField(
            label="اسم المستخدم",
            value="",
            color="black",
            bgcolor="white",
            border_color="black",
            height=52,
            text_size=15
        )
        
        password_field = ft.TextField(
            label="كلمة السر",
            value="",
            password=True,
            can_reveal_password=True,
            color="black",
            bgcolor="white",
            border_color="black",
            height=52,
            text_size=15,
            on_submit=handle_login
        )

        login_box = ft.Container(
            content=ft.Column([
                username_field,
                password_field,
                error_text,
                ft.Divider(height=5, color="transparent"),
                ft.Row([
                    ft.GestureDetector(
                        on_tap=handle_login,
                        content=ft.Container(
                            content=ft.Text("موافق", color="black", weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                            bgcolor="white",
                            padding=12,
                            border_radius=6,
                            expand=True
                        )
                    ),
                    ft.GestureDetector(
                        on_tap=handle_cancel,
                        content=ft.Container(
                            content=ft.Text("إلغاء الأمر", color="black", weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                            bgcolor="white",
                            padding=12,
                            border_radius=6,
                            expand=True
                        )
                    ),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)
            ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=25,
            bgcolor="#1E3E62",
            width=420,
            border_radius=12
        )

        header_section = ft.Column([
            custom_logo,
            ft.Divider(height=10, color="transparent"),
            ft.Text("نظام لإدارة الحسابات والمبيعات السحابي", size=14, color="#94A3B8", weight=ft.FontWeight.BOLD),
            ft.Text(status_msg, size=12, color=status_color, weight=ft.FontWeight.BOLD),
            ft.Divider(height=5, color="transparent"),
            ft.Text("نظام الأقساط وإدارة الأموال", size=24, color="white", weight=ft.FontWeight.BOLD),
            ft.Divider(height=10, color="white", thickness=1),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        footer_section = ft.Column([
            ft.Text("نظام لإدارة الحسابات والمبيعات", size=11, color="white"),
            ft.Text("مبرمج حسين ثائر", size=13, color="#38bdf8", weight=ft.FontWeight.BOLD),
            ft.Text("Mob: 07752168736", size=12, color="white")
        ], horizontal_alignment=ft.CrossAxisAlignment.START, spacing=3)

        page.add(
            ft.Column([
                header_section,
                ft.Divider(height=15, color="transparent"),
                ft.Row([
                    footer_section,
                    login_box
                ], alignment=ft.MainAxisAlignment.SPACE_AROUND, vertical_alignment=ft.CrossAxisAlignment.CENTER)
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
        page.update()

    # --- النظام الرئيسي بعد تسجيل الدخول ---
    def show_main_app():
        page.clean()
        page.bgcolor = "#0B0F19"
        page.vertical_alignment = ft.VerticalAlignment.START
        page.horizontal_alignment = ft.CrossAxisAlignment.START

        content_area = ft.Container(expand=True, padding=30)

        def change_view(content_widget):
            content_area.content = content_widget
            page.update()

        def refresh_online_data():
            nonlocal customers_data, credentials_data
            data = load_data()
            customers_data = data.get("customers", {})
            credentials_data = data.get("credentials", {"username": "1", "password": "2"})

        def show_dashboard(e=None):
            refresh_online_data()
            total_cust = len(customers_data)
            total_remaining = sum(c.get("remaining", 0) for c in customers_data.values())
            total_profit = sum(c.get("profit", c.get("total", 0) - c.get("cost", 0)) for c in customers_data.values())

            dashboard_view = ft.Column([
                ft.Row([
                    ft.Text("📊 نظرة عامة على النظام (سحابي)", size=24, weight=ft.FontWeight.BOLD, color="#F8FAFC"),
                    ft.Row([
                        ft.GestureDetector(
                            on_tap=show_change_credentials_screen,
                            content=ft.Container(
                                content=ft.Row([
                                    ft.Text("🔐", size=15),
                                    ft.Text("تغيير معلومات الدخول", color="white", weight=ft.FontWeight.BOLD, size=13)
                                ], spacing=8),
                                bgcolor="#1F2937", padding=10, border_radius=8,
                                border=ft.Border(top=ft.BorderSide(1, "#374151"), bottom=ft.BorderSide(1, "#374151"), left=ft.BorderSide(1, "#374151"), right=ft.BorderSide(1, "#374151"))
                            )
                        ),
                        ft.GestureDetector(
                            on_tap=lambda e: show_login_screen(),
                            content=ft.Container(
                                content=ft.Row([
                                    ft.Text("🚪", size=15),
                                    ft.Text("تسجيل خروج", color="white", weight=ft.FontWeight.BOLD, size=13)
                                ], spacing=8),
                                bgcolor="#7F1D1D", padding=10, border_radius=8,
                                border=ft.Border(top=ft.BorderSide(1, "#991B1B"), bottom=ft.BorderSide(1, "#991B1B"), left=ft.BorderSide(1, "#991B1B"), right=ft.BorderSide(1, "#991B1B"))
                            )
                        )
                    ], spacing=10)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=15, color="transparent"),
                ft.Row([
                    ft.Container(
                        content=ft.Column([
                            ft.Text("إجمالي الزبائن", size=14, color="#94A3B8"),
                            ft.Text(str(total_cust), size=28, weight=ft.FontWeight.BOLD, color="#38BDF8")
                        ], spacing=5),
                        bgcolor="#111827", padding=20, border_radius=12, expand=True,
                        border=ft.Border(top=ft.BorderSide(1, "#1F2937"), bottom=ft.BorderSide(1, "#1F2937"), left=ft.BorderSide(1, "#1F2937"), right=ft.BorderSide(1, "#1F2937"))
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("إجمالي الديون المتبقية", size=14, color="#94A3B8"),
                            ft.Text(f"{total_remaining:,.0f} د.ع", size=28, weight=ft.FontWeight.BOLD, color="#F43F5E")
                        ], spacing=5),
                        bgcolor="#111827", padding=20, border_radius=12, expand=True,
                        border=ft.Border(top=ft.BorderSide(1, "#1F2937"), bottom=ft.BorderSide(1, "#1F2937"), left=ft.BorderSide(1, "#1F2937"), right=ft.BorderSide(1, "#1F2937"))
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("إجمالي الأرباح المتوقعة", size=14, color="#94A3B8"),
                            ft.Text(f"{total_profit:,.0f} د.ع", size=28, weight=ft.FontWeight.BOLD, color="#10B981")
                        ], spacing=5),
                        bgcolor="#111827", padding=20, border_radius=12, expand=True,
                        border=ft.Border(top=ft.BorderSide(1, "#1F2937"), bottom=ft.BorderSide(1, "#1F2937"), left=ft.BorderSide(1, "#1F2937"), right=ft.BorderSide(1, "#1F2937"))
                    ),
                ], spacing=20),
                ft.Divider(height=20, color="transparent"),
                ft.Container(
                    content=ft.Column([
                        ft.Text("مرحباً بك في نظام إدارة الأقساط الفاخر (المتصل أونلاين)", size=20, weight=ft.FontWeight.BOLD, color="#F8FAFC"),
                        ft.Text("اختر إحدى الوظائف من القائمة الجانبية للبدء بالعمل وتحديث البيانات عبر السحابة مباشرة.", size=15, color="#94A3B8"),
                    ], spacing=10),
                    bgcolor="#111827", padding=25, border_radius=12,
                    border=ft.Border(top=ft.BorderSide(1, "#1F2937"), bottom=ft.BorderSide(1, "#1F2937"), left=ft.BorderSide(1, "#1F2937"), right=ft.BorderSide(1, "#1F2937"))
                ),
                ft.Divider(height=10, color="transparent"),
                ft.Container(
                    content=ft.Row([
                        ft.Text("💻 تطوير المبرمج: حسين ثائر", color="#38BDF8", weight=ft.FontWeight.BOLD, size=15),
                        ft.Text("📞 07752168736", color="#E2E8F0", weight=ft.FontWeight.BOLD, size=15),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    bgcolor="#111827", padding=20, border_radius=12,
                    border=ft.Border(top=ft.BorderSide(1, "#2563EB"), bottom=ft.BorderSide(1, "#2563EB"), left=ft.BorderSide(1, "#2563EB"), right=ft.BorderSide(1, "#2563EB"))
                )
            ], spacing=10, scroll=ft.ScrollMode.AUTO)
            change_view(dashboard_view)

        def show_change_credentials_screen(e=None):
            refresh_online_data()
            new_user_field = ft.TextField(label="اسم المستخدم الجديد", value=credentials_data["username"], color="white", bgcolor="#1F2937", height=55, text_size=15, label_style=ft.TextStyle(color="#94A3B8", size=14), border_color="#374151", focused_border_color="#38BDF8")
            new_pass_field = ft.TextField(label="كلمة السر الجديدة", value=credentials_data["password"], color="white", bgcolor="#1F2937", height=55, text_size=15, password=True, can_reveal_password=True, label_style=ft.TextStyle(color="#94A3B8", size=14), border_color="#374151", focused_border_color="#38BDF8")
            msg_txt = ft.Text(value="", size=14, weight=ft.FontWeight.BOLD)

            def save_new_creds(e):
                if new_user_field.value and new_pass_field.value:
                    credentials_data["username"] = new_user_field.value
                    credentials_data["password"] = new_pass_field.value
                    save_app_state()
                    msg_txt.value = "✨ تم تحديث بيانات تسجيل الدخول سحابياً بنجاح!"
                    msg_txt.color = "#10B981"
                else:
                    msg_txt.value = "⚠️ يرجى عدم ترك الحقول فارغة!"
                    msg_txt.color = "#F43F5E"
                page.update()

            view = ft.Column([
                ft.Text("🔐 تغيير معلومات تسجيل الدخول", size=24, weight=ft.FontWeight.BOLD, color="#F8FAFC"),
                ft.Divider(height=10, color="transparent"),
                ft.Container(
                    content=ft.Column([
                        new_user_field,
                        new_pass_field,
                        msg_txt,
                        ft.Divider(height=10, color="transparent"),
                        ft.Row([
                            ft.GestureDetector(
                                on_tap=save_new_creds,
                                content=ft.Container(
                                    content=ft.Text("💾 حفظ البيانات الجديدة سحابياً", color="white", weight=ft.FontWeight.BOLD, size=15, text_align=ft.TextAlign.CENTER),
                                    bgcolor="#2563EB", padding=15, border_radius=10, width=240
                                )
                            )
                        ], alignment=ft.MainAxisAlignment.START)
                    ], spacing=20),
                    bgcolor="#111827", padding=35, border_radius=12,
                    border=ft.Border(top=ft.BorderSide(1, "#1F2937"), bottom=ft.BorderSide(1, "#1F2937"), left=ft.BorderSide(1, "#1F2937"), right=ft.BorderSide(1, "#1F2937")), width=500
                )
            ], spacing=10, scroll=ft.ScrollMode.AUTO)
            change_view(view)

        # --- شاشة إضافة / التراكم على زبون ---
        def show_add_customer_screen(e=None):
            refresh_online_data()
            name_field = ft.TextField(label="اسم الزبون الكامل", color="white", bgcolor="#1F2937", height=55, text_size=15, label_style=ft.TextStyle(color="#94A3B8", size=14), border_color="#374151", focused_border_color="#38BDF8")
            phone_field = ft.TextField(label="رقم الهاتف", color="white", bgcolor="#1F2937", height=55, text_size=15, label_style=ft.TextStyle(color="#94A3B8", size=14), border_color="#374151", focused_border_color="#38BDF8")
            device_field = ft.TextField(label="نوع المادة أو الجهاز الجديدة", color="white", bgcolor="#1F2937", height=55, text_size=15, label_style=ft.TextStyle(color="#94A3B8", size=14), border_color="#374151", focused_border_color="#38BDF8")
            price_field = ft.TextField(label="سعر المنتج الجديد (البيع)", color="white", bgcolor="#1F2937", height=55, text_size=15, label_style=ft.TextStyle(color="#94A3B8", size=14), border_color="#374151", focused_border_color="#38BDF8")
            cost_field = ft.TextField(label="رأس المال (التكلفة)", color="white", bgcolor="#1F2937", height=55, text_size=15, label_style=ft.TextStyle(color="#94A3B8", size=14), border_color="#374151", focused_border_color="#38BDF8")
            advance_field = ft.TextField(label="المقدمة المدفوعة حالياً", color="white", bgcolor="#1F2937", height=55, text_size=15, label_style=ft.TextStyle(color="#94A3B8", size=14), border_color="#374151", focused_border_color="#38BDF8")
            
            system_dropdown = ft.Dropdown(
                label="نظام القسط",
                label_style=ft.TextStyle(color="#94A3B8", size=14),
                color="white",
                bgcolor="#1F2937",
                height=55,
                text_size=15,
                value="شهري",
                border_color="#374151",
                focused_border_color="#38BDF8",
                options=[
                    ft.dropdown.Option("شهري"),
                    ft.dropdown.Option("أسبوعي"),
                    ft.dropdown.Option("يومي"),
                ]
            )

            msg_text = ft.Text(value="", size=14, weight=ft.FontWeight.BOLD)

            def save_customer(e):
                refresh_online_data()
                if name_field.value and price_field.value and cost_field.value:
                    try:
                        new_total_price = float(price_field.value)
                        new_cost = float(cost_field.value)
                        new_advance = float(advance_field.value) if advance_field.value else 0
                    except ValueError:
                        msg_text.value = "يرجى إدخال أرقام صحيحة في الحقول المالية!"
                        msg_text.color = "#F43F5E"
                        page.update()
                        return

                    name = name_field.value.strip()
                    system_type = system_dropdown.value
                    new_device = device_field.value.strip() if device_field.value else "جهاز عام"

                    now = datetime.now()
                    if system_type == "شهري":
                        next_due = now + timedelta(days=30)
                    elif system_type == "أسبوعي":
                        next_due = now + timedelta(days=7)
                    else:
                        next_due = now + timedelta(days=1)

                    current_date_str = now.strftime("%Y-%m-%d %H:%M")
                    next_due_str = next_due.strftime("%Y-%m-%d")

                    # التعديل هنا: فحص إذا كان الزبون موجوداً مسبقاً
                    if name in customers_data:
                        cust = customers_data[name]
                        # تحديث الأرقام التراكمية
                        cust["total"] = float(cust.get("total", 0)) + new_total_price
                        cust["cost"] = float(cust.get("cost", 0)) + new_cost
                        cust["profit"] = float(cust.get("profit", 0)) + (new_total_price - new_cost)
                        cust["paid"] = float(cust.get("paid", 0)) + new_advance
                        cust["remaining"] = float(cust.get("remaining", 0)) + (new_total_price - new_advance)
                        cust["system_type"] = system_type
                        cust["next_due_date"] = next_due_str
                        if phone_field.value:
                            cust["phone"] = phone_field.value

                        # دمج الأجهزة السابقة والجديدة
                        old_device = cust.get("device", "")
                        cust["device"] = f"{old_device} + {new_device}" if old_device else new_device

                        if "history" not in cust:
                            cust["history"] = []
                        cust["history"].append(f"إضافة عملية شراء جديدة ({new_device}) بقيمة {new_total_price} ومقدمة {new_advance} بتاريخ {current_date_str}")
                        
                        msg_text.value = f"✨ تم إضافة المنتج الجديد فوق حساب الزبون ({name}) بنجاح! المتبقي الكلي: {cust['remaining']:,.0f} د.ع"
                    else:
                        # إنشاء زبون جديد لأول مرة
                        customers_data[name] = {
                            "phone": phone_field.value if phone_field.value else "غير متوفر",
                            "device": new_device,
                            "total": new_total_price,
                            "cost": new_cost,
                            "profit": new_total_price - new_cost,
                            "paid": new_advance,
                            "remaining": new_total_price - new_advance,
                            "system_type": system_type,
                            "next_due_date": next_due_str,
                            "history": [f"إضافة الحساب بـ ({new_device}) بقيمة {new_total_price} ومقدمة {new_advance} بنظام ({system_type}) بتاريخ {current_date_str}"]
                        }
                        msg_text.value = f"✨ تم تسجيل الزبون الجديد {name} بنجاح! القسط القادم: {next_due_str}"

                    save_app_state()
                    msg_text.color = "#10B981"
                    name_field.value = ""
                    phone_field.value = ""
                    device_field.value = ""
                    price_field.value = ""
                    cost_field.value = ""
                    advance_field.value = ""
                    page.update()
                else:
                    msg_text.value = "⚠️ يرجى ملء كافة الحقول الأساسية المطلوبة!"
                    msg_text.color = "#F43F5E"
                    page.update()

            form_view = ft.Column([
                ft.Text("➕ إضافة زبون جديد أو إضافة منتج على حساب زبون سابق", size=24, weight=ft.FontWeight.BOLD, color="#F8FAFC"),
                ft.Text("ملاحظة: إذا أدخلت اسم زبون موجود حالياً، سيتم إضافة الجهاز والمبلغ تلقائياً فوق حسابه القديم دون حذفه.", size=13, color="#38BDF8"),
                ft.Divider(height=10, color="transparent"),
                ft.Container(
                    content=ft.Column([
                        ft.Row([ft.Container(content=name_field, expand=True), ft.Container(content=phone_field, expand=True)], spacing=20),
                        ft.Row([ft.Container(content=device_field, expand=True), ft.Container(content=system_dropdown, expand=True)], spacing=20),
                        ft.Row([ft.Container(content=price_field, expand=True), ft.Container(content=cost_field, expand=True), ft.Container(content=advance_field, expand=True)], spacing=20),
                        msg_text,
                        ft.Divider(height=10, color="transparent"),
                        ft.Row([
                            ft.GestureDetector(
                                on_tap=save_customer,
                                content=ft.Container(
                                    content=ft.Text("💾 حفظ / إضافة للحساب سحابياً", color="white", weight=ft.FontWeight.BOLD, size=15, text_align=ft.TextAlign.CENTER),
                                    bgcolor="#2563EB", padding=15, border_radius=10, width=240
                                )
                            )
                        ], alignment=ft.MainAxisAlignment.START)
                    ], spacing=20),
                    bgcolor="#111827", padding=35, border_radius=12,
                    border=ft.Border(top=ft.BorderSide(1, "#1F2937"), bottom=ft.BorderSide(1, "#1F2937"), left=ft.BorderSide(1, "#1F2937"), right=ft.BorderSide(1, "#1F2937"))
                )
            ], spacing=10, scroll=ft.ScrollMode.AUTO)
            change_view(form_view)

        def show_customers_count_screen(e=None):
            refresh_online_data()
            def delete_customer(name):
                if name in customers_data:
                    del customers_data[name]
                    save_app_state()
                    show_customers_count_screen()

            cards = []
            for name, data in customers_data.items():
                remaining_val = data.get('remaining', 0)
                phone = data.get('phone', 'غير متوفر')
                device = data.get('device', 'غير محدد')
                
                card = ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text(f"👤 {name}", color="white", weight=ft.FontWeight.BOLD, size=16),
                            ft.Text(f"📞 هاتف: {phone} | 📦 المواد/الأجهزة: {device}", color="#94A3B8", size=13),
                        ], spacing=4, expand=True),
                        ft.Column([
                            ft.Text(f"المتبقي: {remaining_val:,.0f} د.ع", color="#F43F5E", weight=ft.FontWeight.BOLD, size=15),
                        ]),
                        ft.Container(width=20),
                        ft.GestureDetector(
                            on_tap=lambda e, n=name: delete_customer(n),
                            content=ft.Container(
                                content=ft.Text("🗑️ حذف الحساب", color="white", weight=ft.FontWeight.BOLD, size=13),
                                bgcolor="#DC2626", padding=10, border_radius=8
                            )
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    bgcolor="#1F2937", padding=15, border_radius=10,
                    border=ft.Border(top=ft.BorderSide(1, "#374151"), bottom=ft.BorderSide(1, "#374151"), left=ft.BorderSide(1, "#374151"), right=ft.BorderSide(1, "#374151"))
                )
                cards.append(card)

            if not cards:
                cards.append(ft.Text("لا يوجد زبائن مسجلين في النظام حالياً.", color="#94A3B8", size=15))

            view = ft.Column([
                ft.Row([
                    ft.Text("👥 إدارة وحذف الزبائن", size=24, weight=ft.FontWeight.BOLD, color="#F8FAFC"),
                    ft.Container(
                        content=ft.Text(f"العدد الكلي: {len(customers_data)}", color="#38BDF8", weight=ft.FontWeight.BOLD, size=14),
                        bgcolor="#1F2937", padding=10, border_radius=8
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=10, color="transparent"),
                ft.Container(
                    content=ft.Column(cards, spacing=12, scroll=ft.ScrollMode.AUTO),
                    bgcolor="#111827", padding=25, border_radius=12,
                    border=ft.Border(top=ft.BorderSide(1, "#1F2937"), bottom=ft.BorderSide(1, "#1F2937"), left=ft.BorderSide(1, "#1F2937"), right=ft.BorderSide(1, "#1F2937")), height=500
                )
            ], spacing=10, scroll=ft.ScrollMode.AUTO)
            change_view(view)

        def show_pay_debt_screen(e=None):
            refresh_online_data()
            search_field = ft.TextField(label="اسم الزبون", color="white", bgcolor="#1F2937", height=55, text_size=15, label_style=ft.TextStyle(color="#94A3B8", size=14), border_color="#374151", focused_border_color="#38BDF8")
            amount_field = ft.TextField(label="مبلغ التسديد المدفوع", color="white", bgcolor="#1F2937", height=55, text_size=15, label_style=ft.TextStyle(color="#94A3B8", size=14), border_color="#374151", focused_border_color="#38BDF8")
            res_text = ft.Text(value="", size=14, weight=ft.FontWeight.BOLD)

            def submit_payment(e):
                refresh_online_data()
                name = search_field.value.strip() if search_field.value else ""
                if name in customers_data and amount_field.value:
                    try:
                        paid_amount = float(amount_field.value)
                    except ValueError:
                        res_text.value = "⚠️ يرجى إدخال مبلغ صحيح!"
                        res_text.color = "#F43F5E"
                        page.update()
                        return

                    cust = customers_data[name]
                    cust["paid"] = float(cust.get("paid", 0)) + paid_amount
                    cust["remaining"] = float(cust.get("remaining", 0)) - paid_amount

                    now = datetime.now()
                    current_date = now.strftime("%Y-%m-%d %H:%M")
                    
                    system_type = cust.get("system_type", "شهري")
                    if system_type == "شهري":
                        next_due = now + timedelta(days=30)
                    elif system_type == "أسبوعي":
                        next_due = now + timedelta(days=7)
                    else:
                        next_due = now + timedelta(days=1)
                    
                    cust["next_due_date"] = next_due.strftime("%Y-%m-%d")

                    if "history" not in cust:
                        cust["history"] = []
                    cust["history"].append(f"تسديد مبلغ {paid_amount} د.ع وتحديث موعد القسط إلى {cust['next_due_date']} بتاريخ {current_date}")

                    save_app_state()
                    show_receipt_screen(name, paid_amount, cust["remaining"], current_date, cust.get("device", "جهاز"))
                else:
                    res_text.value = "⚠️ الزبون غير موجود أو لم تقم بإدخال المبلغ!"
                    res_text.color = "#F43F5E"
                    page.update()

            view = ft.Column([
                ft.Text("💵 تسديد ديون وإصدار وصل", size=24, weight=ft.FontWeight.BOLD, color="#F8FAFC"),
                ft.Divider(height=10, color="transparent"),
                ft.Container(
                    content=ft.Column([
                        search_field,
                        amount_field,
                        res_text,
                        ft.Divider(height=10, color="transparent"),
                        ft.Row([
                            ft.GestureDetector(
                                on_tap=submit_payment,
                                content=ft.Container(
                                    content=ft.Text("🖨️ إتمام التسديد وإصدار الوصل", color="white", weight=ft.FontWeight.BOLD, size=15, text_align=ft.TextAlign.CENTER),
                                    bgcolor="#10B981", padding=15, border_radius=10, width=260
                                )
                            )
                        ], alignment=ft.MainAxisAlignment.START)
                    ], spacing=20),
                    bgcolor="#111827", padding=35, border_radius=12,
                    border=ft.Border(top=ft.BorderSide(1, "#1F2937"), bottom=ft.BorderSide(1, "#1F2937"), left=ft.BorderSide(1, "#1F2937"), right=ft.BorderSide(1, "#1F2937"))
                )
            ], spacing=10, scroll=ft.ScrollMode.AUTO)
            change_view(view)

        def show_receipt_screen(customer_name, paid_amt, remaining_amt, payment_date, device_type):
            print_msg = ft.Text(value="", size=14, weight=ft.FontWeight.BOLD)

            def print_receipt_action(e):
                html_content = f"""
                <!DOCTYPE html>
                <html lang="ar" dir="rtl">
                <head>
                    <meta charset="UTF-8">
                    <title>سند قبض</title>
                    <style>
                        body {{ font-family: 'Tahoma', Arial, sans-serif; background: #fff; color: #000; padding: 20px; }}
                        .receipt-box {{ border: 2px solid #b45309; padding: 25px; border-radius: 12px; max-width: 480px; margin: auto; background: #fffdf5; }}
                        .header {{ text-align: center; border-bottom: 2px dashed #b45309; padding-bottom: 12px; margin-bottom: 15px; }}
                        .header h2 {{ color: #92400e; margin: 0; font-size: 24px; }}
                        .header p {{ color: #78350f; margin: 5px 0 0; font-size: 15px; font-weight: bold; }}
                        .row {{ display: flex; justify-content: space-between; margin-bottom: 12px; font-size: 16px; }}
                        .footer {{ text-align: center; margin-top: 25px; border-top: 2px dashed #b45309; padding-top: 12px; font-size: 13px; color: #555; }}
                    </style>
                </head>
                <body onload="window.print()">
                    <div class="receipt-box">
                        <div class="header">
                            <h2>سند قبض</h2>
                            <p>مكتب المهندس للأقساط</p>
                        </div>
                        <div class="row"><span><b>التاريخ والوقت:</b></span> <span>{payment_date}</span></div>
                        <div class="row"><span><b>إستلمنا من السيد/ة:</b></span> <span>{customer_name}</span></div>
                        <div class="row"><span><b>مبلغ وقدره فقط:</b></span> <span style="color: #047857; font-weight: bold;">{paid_amt:,.0f} د.ع</span></div>
                        <div class="row"><span><b>وذلك مقابل:</b></span> <span>تسديد قسط عن ({device_type})</span></div>
                        <div class="row"><span><b>المبلغ المتبقي الكلي:</b></span> <span style="color: #b91c1c; font-weight: bold;">{remaining_amt:,.0f} د.ع</span></div>
                        <div class="footer">
                            <p><b>المحاسب:</b> ترف | <b>المبرمج:</b> حسين ثائر</p>
                            <p>لا يعتبر هذا السند نهائياً إلا بعد تحصيل المبلغ.</p>
                        </div>
                    </div>
                </body>
                </html>
                """
                try:
                    import tempfile
                    tf = tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8")
                    tf.write(html_content)
                    tf.close()
                    os.startfile(tf.name)
                    print_msg.value = "🖨️ تم فتح نافذة الطباعة بنجاح!"
                    print_msg.color = "#10B981"
                except Exception as ex:
                    print_msg.value = f"خطأ: {str(ex)}"
                    print_msg.color = "#F43F5E"
                page.update()

            view = ft.Column([
                ft.Text("🧾 معاينة وإصدار سند القبض", size=24, weight=ft.FontWeight.BOLD, color="#F8FAFC"),
                ft.Divider(height=10, color="transparent"),
                ft.Container(
                    content=ft.Column([
                        ft.Text("🏢 مكتب المهندس للأقساط", color="#FBBF24", size=18, weight=ft.FontWeight.BOLD),
                        ft.Divider(color="#374151"),
                        ft.Text(f"👤 اسم الزبون: {customer_name}", color="white", size=16),
                        ft.Text(f"💵 المبلغ المدفوع: {paid_amt:,.0f} د.ع", color="#10B981", size=16, weight=ft.FontWeight.BOLD),
                        ft.Text(f"⚠️ المبلغ المتبقي الكلي: {remaining_amt:,.0f} د.ع", color="#F43F5E", size=16, weight=ft.FontWeight.BOLD),
                        ft.Text(f"📦 المواد/الأجهزة: {device_type}", color="#94A3B8", size=15),
                        ft.Text(f"📅 التاريخ: {payment_date}", color="#94A3B8", size=15),
                        print_msg,
                        ft.Divider(color="#374151"),
                        ft.Row([
                            ft.GestureDetector(
                                on_tap=print_receipt_action,
                                content=ft.Container(content=ft.Text("🖨️ طباعة الوصل الآن", color="white", weight=ft.FontWeight.BOLD, size=15, text_align=ft.TextAlign.CENTER), bgcolor="#3B82F6", padding=15, border_radius=10, expand=True)
                            ),
                            ft.GestureDetector(
                                on_tap=show_pay_debt_screen,
                                content=ft.Container(content=ft.Text("تسديد جديد", color="white", weight=ft.FontWeight.BOLD, size=15, text_align=ft.TextAlign.CENTER), bgcolor="#374151", padding=15, border_radius=10, expand=True)
                            )
                        ], spacing=15)
                    ], spacing=15),
                    bgcolor="#111827", padding=35, border_radius=12,
                    border=ft.Border(top=ft.BorderSide(1, "#1F2937"), bottom=ft.BorderSide(1, "#1F2937"), left=ft.BorderSide(1, "#1F2937"), right=ft.BorderSide(1, "#1F2937")), width=600
                )
            ], spacing=10, scroll=ft.ScrollMode.AUTO)
            change_view(view)

        def show_late_customers_screen(e=None):
            refresh_online_data()
            today_str = datetime.now().strftime("%Y-%m-%d")
            today_date = datetime.now().date()
            
            late_cards = []
            for name, data in customers_data.items():
                remaining_val = data.get('remaining', 0)
                next_due_date_str = data.get('next_due_date', today_str)
                
                try:
                    due_date = datetime.strptime(next_due_date_str, "%Y-%m-%d").date()
                except:
                    due_date = today_date

                if remaining_val > 0 and due_date <= today_date:
                    phone = data.get('phone', 'غير متوفر')
                    system_type = data.get('system_type', 'شهري')
                    card = ft.Container(
                        content=ft.Row([
                            ft.Column([
                                ft.Text(f"👤 {name}", color="white", weight=ft.FontWeight.BOLD, size=16),
                                ft.Text(f"📞 هاتف: {phone} | ⏳ النظام: {system_type}", color="#94A3B8", size=13),
                                ft.Text(f"📅 موعد الاستحقاق: {next_due_date_str}", color="#FBBF24", size=13, weight=ft.FontWeight.BOLD),
                            ], spacing=4, expand=True),
                            ft.Text(f"المتبقي: {remaining_val:,.0f} د.ع", color="#F43F5E", weight=ft.FontWeight.BOLD, size=16)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        bgcolor="#1F2937", padding=15, border_radius=10,
                        border=ft.Border(top=ft.BorderSide(1, "#374151"), bottom=ft.BorderSide(1, "#374151"), left=ft.BorderSide(1, "#374151"), right=ft.BorderSide(1, "#374151"))
                    )
                    late_cards.append(card)

            if not late_cards:
                late_cards.append(ft.Text("لا يوجد زبائن متأخرون عن موعد السداد حالياً 🎉", color="#10B981", size=16, weight=ft.FontWeight.BOLD))

            view = ft.Column([
                ft.Text("⚠️ الزبائن المتأخرون عن الدفع", size=24, weight=ft.FontWeight.BOLD, color="#F8FAFC"),
                ft.Divider(height=10, color="transparent"),
                ft.Container(
                    content=ft.Column(late_cards, spacing=12, scroll=ft.ScrollMode.AUTO),
                    bgcolor="#111827", padding=25, border_radius=12,
                    border=ft.Border(top=ft.BorderSide(1, "#1F2937"), bottom=ft.BorderSide(1, "#1F2937"), left=ft.BorderSide(1, "#1F2937"), right=ft.BorderSide(1, "#1F2937")), height=500
                )
            ], spacing=10, scroll=ft.ScrollMode.AUTO)
            change_view(view)

        def show_statistics_screen(e=None):
            refresh_online_data()
            total_capital = sum(float(c.get("cost", 0)) for c in customers_data.values())
            total_profit = sum(float(c.get("profit", c.get("total", 0) - c.get("cost", 0))) for c in customers_data.values())
            
            cards = []
            for name, data in customers_data.items():
                cost = float(data.get("cost", 0))
                profit = float(data.get("profit", data.get("total", 0) - cost))
                remaining = float(data.get("remaining", 0))
                
                card = ft.Container(
                    content=ft.Row([
                        ft.Text(f"👤 {name}", color="white", weight=ft.FontWeight.BOLD, size=15, expand=True),
                        ft.Text(f"رأس المال: {cost:,.0f} د.ع", color="#38BDF8", size=13, expand=True),
                        ft.Text(f"الربح: {profit:,.0f} د.ع", color="#10B981", size=13, expand=True),
                        ft.Text(f"المتبقي: {remaining:,.0f} د.ع", color="#F43F5E", size=13, weight=ft.FontWeight.BOLD, expand=True),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    bgcolor="#1F2937", padding=15, border_radius=10,
                    border=ft.Border(top=ft.BorderSide(1, "#374151"), bottom=ft.BorderSide(1, "#374151"), left=ft.BorderSide(1, "#374151"), right=ft.BorderSide(1, "#374151"))
                )
                cards.append(card)

            view = ft.Column([
                ft.Text("📊 إحصائيات الأرباح ورأس المال", size=24, weight=ft.FontWeight.BOLD, color="#F8FAFC"),
                ft.Text(f"إجمالي رأس المال: {total_capital:,.0f} د.ع | إجمالي الأرباح المتوقعة: {total_profit:,.0f} د.ع", color="#38BDF8", size=15, weight=ft.FontWeight.BOLD),
                ft.Divider(height=10, color="transparent"),
                ft.Container(
                    content=ft.Column(cards, spacing=12, scroll=ft.ScrollMode.AUTO),
                    bgcolor="#111827", padding=25, border_radius=12,
                    border=ft.Border(top=ft.BorderSide(1, "#1F2937"), bottom=ft.BorderSide(1, "#1F2937"), left=ft.BorderSide(1, "#1F2937"), right=ft.BorderSide(1, "#1F2937")), height=460
                )
            ], spacing=10, scroll=ft.ScrollMode.AUTO)
            change_view(view)

        def show_statement_screen(e=None):
            cust_search = ft.TextField(
                label="أدخل اسم الزبون للبحث وعرض كشف الحساب",
                color="white",
                bgcolor="#1F2937",
                height=55,
                text_size=15,
                label_style=ft.TextStyle(color="#94A3B8", size=14),
                border_color="#374151",
                focused_border_color="#38BDF8"
            )
            result_container = ft.Column([], spacing=10)

            def search_customer(e):
                refresh_online_data()
                result_container.controls.clear()
                name = cust_search.value.strip() if cust_search.value else ""
                if name in customers_data:
                    cust = customers_data[name]
                    raw_history = cust.get("history", [])
                    history_items = [ft.Text(f"• {h}", color="#94A3B8", size=13) for h in reversed(raw_history)]

                    statement_box = ft.Container(
                        content=ft.Column([
                            ft.Text(f"👤 اسم الزبون: {name}", color="white", weight=ft.FontWeight.BOLD, size=18),
                            ft.Text(f"📞 رقم الهاتف: {cust.get('phone', '-')} | 📦 المواد/الأجهزة: {cust.get('device', '-')}", color="#94A3B8", size=15),
                            ft.Text(f"⏳ نظام القسط: {cust.get('system_type', 'شهري')} | 📅 القسط القادم: {cust.get('next_due_date', 'غير محدد')}", color="#FBBF24", size=15, weight=ft.FontWeight.BOLD),
                            ft.Divider(color="#374151"),
                            ft.Row([
                                ft.Text(f"💰 السعر الكلي: {float(cust.get('total', 0)):,.0f} د.ع", color="#38BDF8", size=15),
                                ft.Text(f"💵 المدفوع: {float(cust.get('paid', 0)):,.0f} د.ع", color="#10B981", size=15),
                                ft.Text(f"⚠️ المتبقي الكلي: {float(cust.get('remaining', 0)):,.0f} د.ع", color="#F43F5E", size=15, weight=ft.FontWeight.BOLD),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Divider(color="#374151"),
                            ft.Text("📅 سجل العمليات والدفعات المشتريات السابقة:", color="#38BDF8", weight=ft.FontWeight.BOLD, size=15),
                            ft.Container(
                                content=ft.Column(history_items, spacing=8, scroll=ft.ScrollMode.AUTO),
                                height=200
                            )
                        ], spacing=12),
                        bgcolor="#111827", padding=25, border_radius=12,
                        border=ft.Border(top=ft.BorderSide(1, "#1F2937"), bottom=ft.BorderSide(1, "#1F2937"), left=ft.BorderSide(1, "#1F2937"), right=ft.BorderSide(1, "#1F2937")),
                        width=700
                    )
                    result_container.controls.append(statement_box)
                else:
                    result_container.controls.append(ft.Text("⚠️ الزبون غير موجود في النظام!", color="#F43F5E", size=15, weight=ft.FontWeight.BOLD))
                page.update()

            view = ft.Column([
                ft.Text("📑 كشف حساب زبون", size=24, weight=ft.FontWeight.BOLD, color="#F8FAFC"),
                ft.Divider(height=10, color="transparent"),
                ft.Row([
                    ft.Container(content=cust_search, width=450),
                    ft.GestureDetector(
                        on_tap=search_customer,
                        content=ft.Container(
                            content=ft.Text("بحث", color="white", weight=ft.FontWeight.BOLD, size=15, text_align=ft.TextAlign.CENTER),
                            bgcolor="#2563EB", padding=16, border_radius=10, width=130
                        )
                    )
                ], spacing=15),
                ft.Divider(height=10, color="transparent"),
                result_container
            ], spacing=10, scroll=ft.ScrollMode.AUTO)
            change_view(view)

        def create_nav_btn(text, action, icon_symbol):
            return ft.GestureDetector(
                on_tap=action,
                content=ft.Container(
                    content=ft.Row([
                        ft.Text(icon_symbol, size=18),
                        ft.Text(text, color="#E2E8F0", weight=ft.FontWeight.BOLD, size=15),
                    ], spacing=15),
                    bgcolor="#111827",
                    padding=16,
                    border_radius=12,
                    border=ft.Border(top=ft.BorderSide(1, "#1F2937"), bottom=ft.BorderSide(1, "#1F2937"), left=ft.BorderSide(1, "#1F2937"), right=ft.BorderSide(1, "#1F2937"))
                )
            )

        programmer_info = ft.Container(
            content=ft.Column([
                ft.Divider(color="#1F2937", height=10),
                ft.Text("💻 تطوير المبرمج:", size=12, color="#94A3B8"),
                ft.Text("حسين ثائر", size=14, weight=ft.FontWeight.BOLD, color="#38BDF8"),
                ft.Text("📞 07752168736", size=12, color="#E2E8F0"),
            ], spacing=4),
            padding=10,
            bgcolor="#111827",
            border_radius=10,
            border=ft.Border(top=ft.BorderSide(1, "#1F2937"), bottom=ft.BorderSide(1, "#1F2937"), left=ft.BorderSide(1, "#1F2937"), right=ft.BorderSide(1, "#1F2937"))
        )

        sidebar = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Column([
                        ft.Text("⚡ مكتب المهندس", size=20, weight=ft.FontWeight.BOLD, color="#F8FAFC"),
                        ft.Text("نظام إدارة الأقساط (أونلاين)", size=12, color="#94A3B8"),
                    ], spacing=4),
                    padding=10
                ),
                ft.Divider(color="#1F2937", height=20),
                create_nav_btn("لوحة التحكم الرئيسية", show_dashboard, "🏠"),
                create_nav_btn("إضافة زبون / منتج جديد", show_add_customer_screen, "➕"),
                create_nav_btn("إدارة وحذف الزبائن", show_customers_count_screen, "👥"),
                create_nav_btn("تسديد ديون وإصدار وصل", show_pay_debt_screen, "💵"),
                create_nav_btn("الزبائن المتأخرون", show_late_customers_screen, "⚠️"),
                create_nav_btn("إحصائيات الأرباح", show_statistics_screen, "📊"),
                create_nav_btn("كشف حساب زبون", show_statement_screen, "📑"),
                ft.Container(expand=True),
                programmer_info
            ], spacing=10, scroll=ft.ScrollMode.AUTO),
            bgcolor="#0D1322",
            padding=25,
            width=300,
            border=ft.Border(left=ft.BorderSide(1, "#1F2937"))
        )

        main_layout = ft.Row([
            sidebar,
            content_area
        ], expand=True, spacing=0)

        page.add(main_layout)
        show_dashboard()

    show_login_screen()

ft.app(target=main)
