import streamlit as st
from PIL import Image
import json
import os
import webbrowser
from datetime import datetime

# ====================== KONFIGURASI ======================
PRODUCTS_FILE = "data/products.json"
TRANSACTIONS_FILE = "data/transactions.json"
USERS_FILE = "data/users.json"
LOGO_PATH = "assets/logo.png"
PRODUCT_IMAGE_DIR = "assets/products/"

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# ====================== FUNGSI UTILITAS ======================
def setup_files():
    """Inisialisasi file dan folder"""
    os.makedirs("data", exist_ok=True)
    os.makedirs("assets", exist_ok=True)
    os.makedirs(PRODUCT_IMAGE_DIR, exist_ok=True)
    
    # Buat logo default jika tidak ada
    if not os.path.exists(LOGO_PATH):
        img = Image.new('RGB', (200, 100), color='#FFA500')
        img.save(LOGO_PATH)
    
    # Inisialisasi produk contoh
    if not os.path.exists(PRODUCTS_FILE):
        sample_products = [
            {
                "id": 1,
                "name": "Bawang Merah",
                "price": 15000,
                "stock": 100,
                "description": "Bawang merah segar kualitas premium",
                "category": "bawang",
                "rating": 4.5,
                "image": os.path.join(PRODUCT_IMAGE_DIR, "bawang_merah.jpg")
            },
            {
                "id": 2,
                "name": "Bibit Bawang Merah",
                "price": 25000,
                "stock": 50,
                "description": "Bibit unggul siap tanam",
                "category": "bibit",
                "rating": 4.8,
                "image": os.path.join(PRODUCT_IMAGE_DIR, "bibit_bawang.jpg")
            }
        ]
        save_to_json(PRODUCTS_FILE, sample_products)
        
        # Buat gambar contoh
        for product in sample_products:
            if not os.path.exists(product["image"]):
                color = '#FF6347' if product["category"] == "bawang" else '#32CD32'
                img = Image.new('RGB', (400, 300), color=color)
                img.save(product["image"])

    # Inisialisasi file lainnya
    if not os.path.exists(TRANSACTIONS_FILE):
        save_to_json(TRANSACTIONS_FILE, [])
    if not os.path.exists(USERS_FILE):
        save_to_json(USERS_FILE, [])

def load_from_json(file_path):
    """Memuat data dari file JSON dengan error handling"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if content.endswith(','):
                content = content[:-1]
            return json.loads(content) if content else []
    except Exception as e:
        st.error(f"Gagal memuat file {file_path}: {str(e)}")
        return []

def save_to_json(file_path, data):
    """Menyimpan data ke file JSON"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        st.error(f"Gagal menyimpan ke {file_path}: {str(e)}")

# ====================== FUNGSI AUTHENTIKASI ======================
def login_page():
    """Halaman login"""
    st.title("🔐 Login Tukang Bawang")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.form_submit_button("Login"):
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                st.session_state.logged_in = True
                st.session_state.username = ADMIN_USERNAME
                st.session_state.page = "products"
                st.rerun()
            
            users = load_from_json(USERS_FILE)
            user = next((u for u in users if u["username"] == username and u["password"] == password), None)
            if user:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.page = "products"
                st.rerun()
            else:
                st.error("Username/password salah")
    
    if st.button("Daftar Akun Baru"):
        st.session_state.register_mode = True

def register_page():
    """Halaman pendaftaran"""
    st.title("📝 Daftar Akun Baru")
    
    with st.form("register_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm_pass = st.text_input("Konfirmasi Password", type="password")
        
        if st.form_submit_button("Daftar"):
            if not username or not password:
                st.error("Username dan password harus diisi")
            elif password != confirm_pass:
                st.error("Password tidak cocok")
            else:
                users = load_from_json(USERS_FILE)
                if any(u["username"] == username for u in users):
                    st.error("Username sudah digunakan")
                else:
                    users.append({"username": username, "password": password})
                    save_to_json(USERS_FILE, users)
                    st.success("Pendaftaran berhasil! Silakan login")
                    st.session_state.register_mode = False
    
    if st.button("Kembali ke Login"):
        st.session_state.register_mode = False

# ====================== FUNGSI PRODUK ======================
def display_product_card(product, index):
    """Menampilkan kartu produk dengan key unik"""
    with st.container():
        col_img, col_info = st.columns([1, 2])
        
        with col_img:
            img_path = product.get("image", LOGO_PATH)
            try:
                image_obj = Image.open(img_path) if os.path.exists(img_path) else Image.open(LOGO_PATH)
                st.image(image_obj, width=150, use_container_width=True)   

            except:
                st.image(Image.open(LOGO_PATH), width=150, use_container_width=True)
        
        with col_info:
            st.subheader(product["name"])
            st.write(f"**Harga:** Rp{product['price']:,}/kg")
            
            if product["stock"] < 10:
                st.error(f"🛑 Stok: {product['stock']} kg (Hampir Habis!)")
            else:
                st.success(f"✅ Stok: {product['stock']} kg")
            
            rating = product.get("rating", 4)
            st.write("⭐" * int(rating) + "☆" * (5 - int(rating)))
            
            st.caption(product["description"])
            
            # Gunakan index untuk membuat key unik
            quantity = st.number_input(
                "Jumlah (kg)",
                min_value=1,
                max_value=product["stock"],
                value=1,
                key=f"qty_{product['id']}_{index}"
            )
            
            if st.button(
                "🛒 Tambah ke Keranjang",
                key=f"add_{product['id']}_{index}"
            ):
                add_to_cart(product, quantity)
                st.success(f"Ditambahkan {quantity} kg {product['name']}")

def show_products():
    """Tampilkan daftar produk"""
    st.header("🛍️ Daftar Produk")
    
    products = load_from_json(PRODUCTS_FILE)
    if not products:
        st.warning("Tidak ada produk")
        return
    
    tab1, tab2, tab3 = st.tabs(["Semua Produk", "Bawang", "Bibit"])
    
    with tab1:
        for index, product in enumerate(products):
            display_product_card(product, index)
            st.divider()
    
    with tab2:
        bawang_products = [p for p in products if p["category"] == "bawang"]
        if not bawang_products:
            st.warning("Tidak ada produk bawang")
        for index, product in enumerate(bawang_products):
            display_product_card(product, index)
            st.divider()
    
    with tab3:
        bibit_products = [p for p in products if p["category"] == "bibit"]
        if not bibit_products:
            st.warning("Tidak ada produk bibit")
        for index, product in enumerate(bibit_products):
            display_product_card(product, index)
            st.divider()

# ====================== FUNGSI KERANJANG ======================
def add_to_cart(product, quantity):
    """Tambahkan produk ke keranjang"""
    if 'cart' not in st.session_state:
        st.session_state.cart = []
    
    for item in st.session_state.cart:
        if item["product"]["id"] == product["id"]:
            new_quantity = item["quantity"] + quantity
            if new_quantity > product["stock"]:
                st.error("Stok tidak cukup!")
                return
            item["quantity"] = new_quantity
            st.success(f"Jumlah {product['name']} ditambah {quantity} kg")
            return
    
    st.session_state.cart.append({
        "product": product,
        "quantity": quantity
    })

def show_cart():
    """Tampilkan keranjang belanja"""
    st.header("🛒 Keranjang Belanja")
    
    if 'cart' not in st.session_state or not st.session_state.cart:
        st.warning("Keranjang kosong")
        return
    
    total = 0
    for i, item in enumerate(st.session_state.cart):
        product = item["product"]
        subtotal = product["price"] * item["quantity"]
        total += subtotal
        
        with st.container():
            cols = st.columns([3, 2, 1, 1])
            with cols[0]:
                st.write(f"**{product['name']}**")
                st.write(f"Rp{product['price']:,}/kg")
            
            with cols[1]:
                new_quantity = st.number_input(
                    "Jumlah (kg)",
                    min_value=1,
                    max_value=product["stock"],
                    value=item["quantity"],
                    key=f"edit_qty_{i}"
                )
                
                if new_quantity != item["quantity"]:
                    if st.button("Update", key=f"update_{i}"):
                        item["quantity"] = new_quantity
                        st.rerun()
            
            with cols[2]:
                st.write(f"Subtotal: Rp{subtotal:,}")
            
            with cols[3]:
                if st.button("❌", key=f"del_{i}"):
                    st.session_state.cart.pop(i)
                    st.rerun()
            
            st.divider()
    
    st.subheader(f"Total: Rp{total:,}")
    
    if st.button("🚀 Lanjut ke Checkout", type="primary"):
        st.session_state.checkout_active = True

# ====================== FUNGSI CHECKOUT ======================
def show_checkout():
    """Tampilkan form checkout"""
    st.header("💳 Checkout")
    
    total = sum(item["product"]["price"] * item["quantity"] for item in st.session_state.cart)
    
    with st.form("checkout_form"):
        st.subheader("Informasi Pengiriman")
        name = st.text_input("Nama Penerima")
        phone = st.text_input("Nomor Telepon")
        address = st.text_area("Alamat Lengkap")
        
        st.subheader("Metode Pengiriman")
        shipping_method = st.selectbox(
            "Pilihan Pengiriman",
            ["JNE Reguler (Rp15.000)", "J&T Express (Rp12.000)", "SiCepat (Rp10.000)"]
        )
        
        shipping_cost = 15000 if "JNE" in shipping_method else 12000 if "J&T" in shipping_method else 10000
        grand_total = total + shipping_cost
        
        st.subheader("Metode Pembayaran")
        payment_method = st.selectbox(
            "Pembayaran",
            ["Transfer BRI", "Transfer BCA", "Transfer SeaBank", "COD (Bayar di Tempat)"]
        )
        
        st.subheader("Ringkasan Pembayaran")
        col1, col2 = st.columns(2)
        with col1:
            st.write("Subtotal:")
            st.write("Ongkos Kirim:")
            st.write("**Total:**")
        with col2:
            st.write(f"Rp{total:,}")
            st.write(f"Rp{shipping_cost:,}")
            st.write(f"**Rp{grand_total:,}**")
        
        st.divider()
        
        if st.form_submit_button("Konfirmasi Pesanan", type="primary"):
            if not name or not phone or not address.strip():
                st.error("Harap lengkapi semua informasi pengiriman!")
            else:
                process_checkout(
                    name, phone, address,
                    shipping_method, payment_method,
                    grand_total, shipping_cost
                )

def process_checkout(name, phone, address, shipping_method, payment_method, grand_total, shipping_cost):
    """Proses checkout"""
    try:
        transactions = load_from_json(TRANSACTIONS_FILE)
        
        transaction = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "username": st.session_state.username,
            "customer": {"name": name, "phone": phone, "address": address},
            "items": [{
                "id": item["product"]["id"],
                "name": item["product"]["name"],
                "price": item["product"]["price"],
                "quantity": item["quantity"]
            } for item in st.session_state.cart],
            "total": grand_total,
            "payment": {"method": payment_method, "status": "pending"},
            "shipping": {
                "method": shipping_method.split()[0],
                "cost": shipping_cost,
                "estimate": "2-3 hari" if "JNE" in shipping_method else "1-2 hari" if "J&T" in shipping_method else "3-5 hari"
            },
            "status": "pending"
        }
        
        transactions.append(transaction)
        save_to_json(TRANSACTIONS_FILE, transactions)
        
        # Update stok produk
        products = load_from_json(PRODUCTS_FILE)
        for item in st.session_state.cart:
            for product in products:
                if product["id"] == item["product"]["id"]:
                    product["stock"] -= item["quantity"]
                    break
        save_to_json(PRODUCTS_FILE, products)
        
        st.session_state.cart = []
        st.session_state.checkout_active = False
        st.session_state.checkout_success = True
        st.rerun()
        
    except Exception as e:
        st.error(f"Gagal memproses checkout: {str(e)}")

def show_checkout_success():
    """Tampilkan pesan sukses checkout"""
    st.balloons()
    st.success("""
    ✅ **Pesanan Berhasil!**
    
    Silakan lakukan pembayaran dan konfirmasi via WhatsApp:
    """)
    
    if st.button("💬 Hubungi via WhatsApp", type="primary"):
        webbrowser.open("https://wa.me/6281234567890")
    
    if st.button("🏠 Kembali ke Beranda"):
        st.session_state.checkout_success = False
        st.session_state.page = "products"
        st.rerun()

# ====================== FUNGSI ADMIN ======================
def show_admin_panel():
    """Panel admin"""
    st.header("👨‍💻 Admin Dashboard")
    
    tab1, tab2, tab3 = st.tabs(["Laporan", "Kelola Produk", "Kelola User"])
    
    with tab1:
        show_admin_report()
    with tab2:
        manage_products()
    with tab3:
        manage_users()

def show_admin_report():
    """Laporan penjualan"""
    transactions = load_from_json(TRANSACTIONS_FILE)
    
    completed_trans = [t for t in transactions if t.get("status") == "completed"]
    total_sales = sum(t["total"] for t in completed_trans)
    total_transactions = len(completed_trans)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Penjualan", f"Rp{total_sales:,}")
    with col2:
        st.metric("Total Transaksi", total_transactions)
    
    st.subheader("Transaksi Terakhir")
    for i, trans in enumerate(transactions[-5:]):
        with st.expander(f"📦 Pesanan #{trans['id']} - {trans['date']}"):
            st.write(f"**Status:** {trans.get('status', 'pending').title()}")
            st.write(f"**Customer:** {trans['customer']['name']}")
            st.write(f"**Total:** Rp{trans['total']:,}")
            
            st.write("**Items:**")
            for item in trans["items"]:
                st.write(f"- {item['name']} ({item['quantity']}kg) @ Rp{item['price']:,}")
            
            # Gunakan kombinasi ID + index untuk key unik
            if st.button(f"Update Status", key=f"status_{trans['id']}_{i}"):
                update_transaction_status(trans["id"])

def update_transaction_status(trans_id):
    """Update status transaksi"""
    transactions = load_from_json(TRANSACTIONS_FILE)
    
    for t in transactions:
        if t["id"] == trans_id:
            # Gunakan timestamp untuk key unik
            unique_key = f"status_{trans_id}_{datetime.now().timestamp()}"
            new_status = st.selectbox(
                "Status Baru:",
                ["pending", "completed"],
                index=0 if t.get("status") == "pending" else 1,
                key=unique_key
            )
            
            if st.button("Simpan Perubahan", key=f"save_{unique_key}"):
                t["status"] = new_status
                save_to_json(TRANSACTIONS_FILE, transactions)
                st.success("Status transaksi diperbarui!")
                st.rerun()
            break

def manage_products():
    """Kelola produk"""
    products = load_from_json(PRODUCTS_FILE)
    
    st.subheader("➕ Tambah Produk Baru")
    with st.form("add_product_form"):
        cols = st.columns(2)
        with cols[0]:
            name = st.text_input("Nama Produk*")
            price = st.number_input("Harga*", min_value=1000, step=1000)
            stock = st.number_input("Stok*", min_value=0)
        with cols[1]:
            category = st.selectbox("Kategori*", ["bawang", "bibit"])
            rating = st.slider("Rating", 1.0, 5.0, 4.0, 0.1)
        
        description = st.text_area("Deskripsi Produk")
        uploaded_file = st.file_uploader("Gambar Produk (jpg/png)", type=["jpg", "png", "jpeg"])
        
        if st.form_submit_button("💾 Simpan Produk"):
            if not name or not price or not stock:
                st.error("Harap isi field wajib (*)")
            else:
                image_path = LOGO_PATH
                if uploaded_file is not None:
                    image_path = os.path.join(PRODUCT_IMAGE_DIR, uploaded_file.name)
                    with open(image_path, "wb") as img_file:
                        img_file.write(uploaded_file.getbuffer())
                
                new_product = {
                    "id": max(p["id"] for p in products) + 1 if products else 1,
                    "name": name,
                    "price": price,
                    "stock": stock,
                    "description": description,
                    "category": category,
                    "rating": rating,
                    "image": image_path
                }
                
                products.append(new_product)
                save_to_json(PRODUCTS_FILE, products)
                st.success("Produk berhasil ditambahkan!")
                st.rerun()
    
    st.subheader("📋 Daftar Produk")
    for product in products:
        with st.expander(f"{product['name']} (ID: {product['id']})"):
            cols = st.columns([3, 1])
            with cols[0]:
                st.write(f"**Harga:** Rp{product['price']:,}")
                st.write(f"**Stok:** {product['stock']} kg")
                st.write(f"**Kategori:** {product['category'].title()}")
                st.write(f"**Rating:** {product['rating']} ⭐")
            with cols[1]:
                try:
                    st.image(
                        product.get("image", LOGO_PATH),
                        width=200,
                        use_container_width=True
                    )
                except:
                    st.image(LOGO_PATH, width=200, use_container_width=True)
            
            with st.form(f"edit_{product['id']}"):
                new_stock = st.number_input(
                    "Update Stok", 
                    value=product["stock"], 
                    min_value=0,
                    key=f"stock_{product['id']}"
                )
                
                new_image = st.file_uploader(
                    "Ganti Gambar",
                    type=["jpg", "png", "jpeg"],
                    key=f"image_{product['id']}"
                )
                
                if st.form_submit_button("🔄 Update Produk"):
                    product["stock"] = new_stock
                    
                    if new_image is not None:
                        if product["image"] != LOGO_PATH and os.path.exists(product["image"]):
                            os.remove(product["image"])
                        
                        image_path = os.path.join(PRODUCT_IMAGE_DIR, new_image.name)
                        with open(image_path, "wb") as img_file:
                            img_file.write(new_image.getbuffer())
                        product["image"] = image_path
                    
                    save_to_json(PRODUCTS_FILE, products)
                    st.success("Produk diperbarui!")
                    st.rerun()
            
            if st.button(f"🗑️ Hapus Produk", key=f"del_{product['id']}"):
                if product["image"] != LOGO_PATH and os.path.exists(product["image"]):
                    os.remove(product["image"])
                
                products.remove(product)
                save_to_json(PRODUCTS_FILE, products)
                st.success("Produk dihapus!")
                st.rerun()

def manage_users():
    """Kelola user"""
    users = load_from_json(USERS_FILE)
    
    st.subheader("👥 Daftar Pengguna")
    for user in users:
        cols = st.columns([3, 1])
        with cols[0]:
            st.write(f"**Username:** {user['username']}")
        with cols[1]:
            if st.button(f"Hapus", key=f"del_{user['username']}"):
                users.remove(user)
                save_to_json(USERS_FILE, users)
                st.success("Pengguna dihapus!")
                st.rerun()
    
    st.divider()
    
    st.subheader("➕ Tambah Pengguna Baru")
    with st.form("add_user_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.form_submit_button("Tambah Pengguna"):
            if not username or not password:
                st.error("Username dan password harus diisi")
            elif any(u["username"] == username for u in users):
                st.error("Username sudah digunakan")
            else:
                users.append({"username": username, "password": password})
                save_to_json(USERS_FILE, users)
                st.success("Pengguna berhasil ditambahkan!")
                st.rerun()

def show_history():
    """Tampilkan riwayat transaksi"""
    st.header("📜 Riwayat Transaksi")
    
    transactions = load_from_json(TRANSACTIONS_FILE)
    user_transactions = [t for t in transactions if t["username"] == st.session_state.username]
    
    if not user_transactions:
        st.warning("Belum ada riwayat transaksi")
        return
    
    for trans in reversed(user_transactions):
        with st.expander(f"📦 Pesanan #{trans['id']} - {trans['date']}"):
            st.write(f"**Status:** {trans.get('status', 'pending').title()}")
            st.write(f"**Total:** Rp{trans['total']:,}")
            st.write(f"**Metode Pembayaran:** {trans['payment']['method']}")
            
            st.write("**Items:**")
            for item in trans["items"]:
                st.write(f"- {item['name']} ({item['quantity']}kg) @ Rp{item['price']:,}")
            
            st.write("**Alamat Pengiriman:**")
            st.write(trans["customer"]["address"])

# ====================== FUNGSI UTAMA ======================
def main():
    """Aplikasi utama"""
    setup_files()
    
    # Inisialisasi session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'register_mode' not in st.session_state:
        st.session_state.register_mode = False
    if 'page' not in st.session_state:
        st.session_state.page = "products"
    if 'checkout_active' not in st.session_state:
        st.session_state.checkout_active = False
    if 'checkout_success' not in st.session_state:
        st.session_state.checkout_success = False
    if 'cart' not in st.session_state:
        st.session_state.cart = []
    
    # Tampilan login jika belum login
    if not st.session_state.logged_in:
        if st.session_state.register_mode:
            register_page()
        else:
            login_page()
        return
    
    # Sidebar
    with st.sidebar:
        st.image(LOGO_PATH, use_container_width=True)
        st.title(f"Halo, {st.session_state.username}")
        
        if st.session_state.username == ADMIN_USERNAME:
            st.success("👑 Mode Admin")
        
        # Menu navigasi
        menu_options = ["🛍️ Produk", "🛒 Keranjang", "📜 Riwayat"]
        if st.session_state.username == ADMIN_USERNAME:
            menu_options.append("👨‍💻 Admin")
        
        selected = st.radio("Menu", menu_options)
        
        # Set halaman berdasarkan pilihan menu
        if "🛍️ Produk" in selected:
            st.session_state.page = "products"
        elif "🛒 Keranjang" in selected:
            st.session_state.page = "cart"
        elif "📜 Riwayat" in selected:
            st.session_state.page = "history"
        elif "👨‍💻 Admin" in selected:
            st.session_state.page = "admin"
        
        if st.button("🔒 Logout"):
            st.session_state.logged_in = False
            st.rerun()
    
    # Tampilkan halaman aktif
    if st.session_state.checkout_success:
        show_checkout_success()
    elif st.session_state.checkout_active:
        show_checkout()
    elif st.session_state.page == "products":
        show_products()
    elif st.session_state.page == "cart":
        show_cart()
    elif st.session_state.page == "history":
        show_history()
    elif st.session_state.page == "admin":
        show_admin_panel()

if __name__ == "__main__":
    main()