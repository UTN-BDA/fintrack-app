from flask import Blueprint, Response, request, render_template, redirect, url_for, flash, session
import requests 
from datetime import datetime
from app.mapping import ResponseSchema
from app.services import TransactionService, UserService
from app.reports.csv_export import export_transactions_to_csv


home_bp = Blueprint('home', __name__)

response_schema = ResponseSchema()
user_service = UserService()
transaction_service = TransactionService()

@home_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')

        user = user_service.authenticate(login, password)
        if user:
            session['user_id'] = user.id  # Guarda el ID del usuario en la sesión
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('home.index'))
        else:
            flash('Usuario o contraseña incorrectos. Inténtalo de nuevo.', 'danger')  # Mensaje de error

    return render_template('login.html')

@home_bp.route('/')
def index():
    if 'user_id' not in session:  # Verifica si el usuario está autenticado
        flash('Debes iniciar sesión para acceder a esta página.', 'warning')
        return redirect(url_for('home.login'))  # Redirige al login si no está autenticado

    user_id = session['user_id']  # Obtiene el ID del usuario autenticado

    # Llamada a tu endpoint que genera el gráfico
    response = requests.get(f'http://localhost:5000/transactions/{user_id}/graph')
    image_url = None

    if response.status_code == 200:
        json_data = response.json()
        image_url = json_data['data']['image_url']

    # Obtiene los parámetros de filtro del formulario
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    is_income = request.args.get('is_income')
    category_id = request.args.get('category_id')

    # Convierte los valores de is_income y category_id si están presentes
    is_income = is_income.lower() == 'true' if is_income else None
    category_id = int(category_id) if category_id else None

    # Filtrar transacciones por usuario, rango de fechas, tipo e id de categoría
    transactions = transaction_service.filter_transactions(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        is_income=is_income,
        category_id=category_id
    )

    # Obtiene las categorías para el filtro
    resp = requests.get('http://localhost:5000/categories/all')
    categories = resp.json().get('data', []) if resp.status_code == 200 else []

    # Crea un diccionario id → nombre para lookup rápido
    category_dict = {cat['id']: cat['name'] for cat in categories}

    # Obtiene los totales dinámicos de ingresos, gastos y balance con filtros aplicados
    totals_url = f'http://localhost:5000/expenses/total_income_expense_balance?user_id={user_id}'
    totals_response = requests.get(totals_url)
    totals = totals_response.json().get('data', {}) if totals_response.status_code == 200 else {}

    # Convertir los valores a float
    total_ingresos = float(totals.get('total_ingresos', 0))
    total_gastos = float(totals.get('total_gastos', 0))
    balance = float(totals.get('balance', 0))

    return render_template(
        'index.html',
        transactions=transactions,
        image_url=image_url,
        categories=categories,
        category_dict=category_dict,
        total_ingresos=total_ingresos,
        total_gastos=total_gastos,
        balance=balance
    )

@home_bp.route('/add', methods=['GET', 'POST'])
def add_transaction():
    resp = requests.get('http://localhost:5000/categories/all')
    if 'user_id' not in session:  # Verifica si el usuario está autenticado
        flash('Debes iniciar sesión para acceder a esta página.', 'warning')
        return redirect(url_for('home.login'))  # Redirige al login si no está autenticado
    
    if resp.status_code == 200:
        categories = resp.json().get('data', [])  # extrae la lista real del JSON
    else:
        categories = []

    if request.method == 'POST':
        user_id = session.get('user_id')  # Obtiene el ID del usuario autenticado

        # Obtiene los datos del formulario
        amount = request.form.get('amount')
        date = request.form.get('date')
        description = request.form.get('description')
        method = request.form.get('method')
        is_income = request.form.get('is_income') == 'true'
        category_id = request.form.get('category_id')

        # Crea la transacción
        transaction_service.create_transaction(
            user_id=user_id,
            amount=amount,
            date=date,
            description=description,
            method=method,
            is_income=is_income,
            category_id=category_id
        )
        flash('Transacción agregada correctamente.', 'success')
        return redirect(url_for('home.index'))

    return render_template('add_transaction.html', categories=categories)  # Pasa las categorías al template

@home_bp.route('/edit', methods=['GET', 'POST'])
def edit_transaction():
    if 'user_id' not in session:  # Verifica si el usuario está autenticado
        flash('Debes iniciar sesión para acceder a esta página.', 'warning')
        return redirect(url_for('home.login'))  # Redirige al login si no está autenticado

    if request.method == 'POST':
        transaction_id = request.form.get('transaction_id')  # Obtiene el ID de la transacción a editar
        amount = request.form.get('amount')
        date = request.form.get('date')
        description = request.form.get('description')
        method = request.form.get('method')
        is_income = request.form.get('is_income') == 'true'
        category_id = request.form.get('category_id')

        # Actualiza la transacción
        success = transaction_service.update_transaction(
            transaction_id=transaction_id,
            amount=amount,
            date=date,
            description=description,
            method=method,
            is_income=is_income,
            category_id=category_id
        )
        if success:
            flash('Transacción actualizada correctamente.', 'success')
        else:
            flash('No se pudo actualizar la transacción. Verifica el ID.', 'danger')
        return redirect(url_for('home.index'))

    # Obtiene las transacciones del usuario para mostrarlas en el formulario
    user_id = session['user_id']
    transactions = transaction_service.filter_transactions(user_id=user_id)
    return render_template('edit_transaction.html', transactions=transactions)

@home_bp.route('/delete', methods=['GET', 'POST'])
def delete_transaction():
    if 'user_id' not in session:  # Verifica si el usuario está autenticado
        flash('Debes iniciar sesión para acceder a esta página.', 'warning')
        return redirect(url_for('home.login'))  # Redirige al login si no está autenticado

    if request.method == 'POST':
        transaction_id = request.form.get('transaction_id')  # Obtiene el ID de la transacción a eliminar
        if transaction_id:
            success = transaction_service.delete_transaction(transaction_id)
            if success:
                flash('Transacción eliminada correctamente.', 'success')
            else:
                flash('No se pudo eliminar la transacción. Verifica el ID.', 'danger')
        return redirect(url_for('home.index'))

    # Obtiene las transacciones del usuario para mostrarlas en el formulario
    user_id = session['user_id']
    transactions = transaction_service.filter_transactions(user_id=user_id)
    return render_template('delete_transaction.html', transactions=transactions)

@home_bp.route('/export', methods=['GET'])
def export_transactions():
    """Exporta transacciones a un archivo CSV"""
    try:
        # Obtener el ID del usuario autenticado
        user_id = session.get('user_id')  # Obtiene el ID del usuario autenticado
        if not user_id:
            flash('Debes iniciar sesión para exportar datos.', 'warning')
            return redirect(url_for('home.login'))

        # Obtener parámetros de consulta
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        is_income = request.args.get('is_income', type=lambda v: v.lower() == 'true')
        category_id = request.args.get('category_id', type=int)

        # Convertir fechas si están presentes
        start_date = start_date and datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = end_date and datetime.strptime(end_date, "%Y-%m-%d").date()

        # Filtrar transacciones solo del usuario autenticado
        transactions = transaction_service.filter_transactions(
            user_id=user_id,  # Filtra por el usuario autenticado
            start_date=start_date,
            end_date=end_date,
            is_income=is_income,
            category_id=category_id,
            page=1,
            per_page=10**6  # Exportar todas las transacciones
        )

        # Generar CSV
        csv_data = export_transactions_to_csv(transactions)

        # Crear respuesta con el archivo CSV
        response = Response(
            csv_data,
            mimetype='text/csv',
            headers={
                "Content-Disposition": "attachment; filename=transactions.csv"
            }
        )
        return response

    except Exception as e:
        flash('Error al exportar transacciones.', 'danger')
        return redirect(url_for('home.index'))

@home_bp.route('/logout')
def logout():
    session.pop('user_id', None)  # Elimina el ID del usuario de la sesión
    flash('Has cerrado sesión correctamente.', 'success')
    return redirect(url_for('home.login'))  # Redirige al login
