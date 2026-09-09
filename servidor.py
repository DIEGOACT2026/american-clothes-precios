#!/usr/bin/env python3
"""
Servidor para el Calculador de Precios American Clothes
Ejecuta este archivo en tu computadora: python3 servidor.py
Luego accede a: http://localhost:5000
"""

from flask import Flask, render_template_string, jsonify, request
import json
import os
from datetime import datetime

app = Flask(__name__)

# Archivo para guardar los parámetros
PARAMS_FILE = 'parametros.json'

# Parámetros por defecto
PARAMS_DEFAULT = {
    'tipoCambio': 19,
    'impuesto': 8,
    'margen1': 30,
    'margen2': 25,
    'margen3': 20
}

def cargar_parametros():
    """Carga los parámetros del archivo o devuelve los por defecto"""
    if os.path.exists(PARAMS_FILE):
        try:
            with open(PARAMS_FILE, 'r') as f:
                return json.load(f)
        except:
            return PARAMS_DEFAULT.copy()
    return PARAMS_DEFAULT.copy()

def guardar_parametros(params):
    """Guarda los parámetros en el archivo"""
    with open(PARAMS_FILE, 'w') as f:
        json.dump(params, f, indent=2)

# HTML de la aplicación
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema de Precios - American Clothes</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 26px;
            margin-bottom: 5px;
        }

        .header p {
            font-size: 13px;
            opacity: 0.9;
        }

        .content {
            padding: 30px;
        }

        .login-screen {
            display: none;
        }

        .login-screen.active {
            display: block;
        }

        .admin-screen {
            display: none;
        }

        .admin-screen.active {
            display: block;
        }

        .employee-screen {
            display: none;
        }

        .employee-screen.active {
            display: block;
        }

        .role-badge {
            display: inline-block;
            background: #4CAF50;
            color: white;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 20px;
        }

        .employee-badge {
            display: inline-block;
            background: #2196F3;
            color: white;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 20px;
        }

        .form-group {
            margin-bottom: 15px;
        }

        .form-group label {
            display: block;
            font-size: 13px;
            font-weight: 600;
            color: #333;
            margin-bottom: 8px;
            text-transform: uppercase;
        }

        .form-group input,
        .form-group select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 6px;
            font-size: 14px;
            transition: border-color 0.3s;
        }

        .form-group input:focus,
        .form-group select:focus {
            outline: none;
            border-color: #667eea;
        }

        button {
            padding: 12px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            width: 100%;
            margin-bottom: 10px;
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        button.secondary {
            background: #f0f0f0;
            color: #333;
        }

        button.secondary:hover {
            background: #e0e0e0;
        }

        button.danger {
            background: #f44336;
        }

        .admin-section {
            margin-bottom: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }

        .admin-section h3 {
            margin-bottom: 15px;
            color: #333;
            font-size: 16px;
        }

        .params-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }

        .param-input {
            display: flex;
            flex-direction: column;
        }

        .param-input label {
            font-size: 12px;
            font-weight: 600;
            color: #666;
            margin-bottom: 6px;
            text-transform: uppercase;
        }

        .param-input input {
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
        }

        .status-message {
            padding: 12px;
            border-radius: 6px;
            font-size: 13px;
            margin-bottom: 20px;
            display: none;
        }

        .status-message.success {
            background: #c8e6c9;
            color: #2e7d32;
            display: block;
        }

        .calculator-box {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 8px;
            margin-bottom: 20px;
        }

        .result-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 8px;
            text-align: center;
            display: none;
        }

        .result-box.active {
            display: block;
        }

        .result-box .price-label {
            font-size: 14px;
            opacity: 0.9;
            margin-bottom: 10px;
            text-transform: uppercase;
            font-weight: 600;
        }

        .result-box .price-value {
            font-size: 48px;
            font-weight: 700;
            margin-bottom: 15px;
        }

        .result-box .price-details {
            font-size: 12px;
            opacity: 0.8;
            line-height: 1.6;
        }

        .params-display {
            background: white;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 20px;
            border: 1px solid #e0e0e0;
            font-size: 12px;
        }

        .params-display p {
            margin-bottom: 8px;
            color: #666;
        }

        .params-display strong {
            color: #333;
        }

        .auto-update-indicator {
            font-size: 11px;
            color: #999;
            text-align: center;
            margin-top: 15px;
        }

        .auto-update-indicator.updating {
            color: #4CAF50;
        }

        .footer {
            padding: 15px 30px;
            background: #f8f9fa;
            border-top: 1px solid #e0e0e0;
            font-size: 11px;
            color: #999;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💰 Sistema de Precios</h1>
            <p>American Clothes - USD → MXN</p>
        </div>

        <!-- LOGIN SCREEN -->
        <div class="login-screen active" id="loginScreen">
            <div class="content">
                <div class="form-group" style="margin-bottom: 30px;">
                    <label>Selecciona tu rol:</label>
                    <select id="roleSelect" style="font-size: 16px; padding: 14px;">
                        <option value="">-- Elige una opción --</option>
                        <option value="admin">👨‍💼 Administrador</option>
                        <option value="employee">👥 Empleado</option>
                    </select>
                </div>

                <div id="adminLoginForm" style="display: none;">
                    <div class="form-group">
                        <label>Contraseña de Administrador:</label>
                        <input type="password" id="adminPassword" placeholder="Ingresa la contraseña">
                    </div>
                    <button onclick="loginAdmin()">Acceder como Admin</button>
                    <button class="secondary" onclick="resetLogin()">Cancelar</button>
                </div>

                <div id="employeeLoginForm" style="display: none;">
                    <div style="background: #e3f2fd; padding: 15px; border-radius: 6px; text-align: center; color: #1565c0; font-size: 14px; margin-bottom: 20px;">
                        ✓ Acceso libre para empleados
                    </div>
                    <button onclick="loginEmployee()">Acceder como Empleado</button>
                    <button class="secondary" onclick="resetLogin()">Cancelar</button>
                </div>
            </div>
        </div>

        <!-- ADMIN SCREEN -->
        <div class="admin-screen" id="adminScreen">
            <div class="content">
                <div class="role-badge">👨‍💼 Modo Administrador</div>

                <div id="statusMessage" class="status-message"></div>

                <div class="admin-section">
                    <h3>⚙️ Parámetros Generales</h3>
                    <div class="params-grid">
                        <div class="param-input">
                            <label>Tipo de Cambio (MXN/USD)</label>
                            <input type="number" id="adminTipoCambio" step="0.01" value="19">
                        </div>
                        <div class="param-input">
                            <label>Impuesto California (%)</label>
                            <input type="number" id="adminImpuesto" step="0.1" value="8">
                        </div>
                    </div>
                </div>

                <div class="admin-section">
                    <h3>📊 Márgenes de Ganancia</h3>
                    <div class="params-grid">
                        <div class="param-input">
                            <label>Margen < $50 USD (%)</label>
                            <input type="number" id="adminMargen1" step="0.1" value="30">
                        </div>
                        <div class="param-input">
                            <label>Margen $50-$100 USD (%)</label>
                            <input type="number" id="adminMargen2" step="0.1" value="25">
                        </div>
                        <div class="param-input">
                            <label>Margen > $100 USD (%)</label>
                            <input type="number" id="adminMargen3" step="0.1" value="20">
                        </div>
                    </div>
                </div>

                <button onclick="guardarParametros()">💾 Guardar Cambios</button>
                <button class="danger" onclick="logout()">Cerrar Sesión</button>

                <div class="auto-update-indicator">
                    ℹ️ Los cambios se actualizan inmediatamente para los empleados
                </div>
            </div>
        </div>

        <!-- EMPLOYEE SCREEN -->
        <div class="employee-screen" id="employeeScreen">
            <div class="content">
                <div class="employee-badge">👥 Modo Empleado</div>

                <div class="params-display">
                    <p><strong>Parámetros actuales:</strong></p>
                    <p>Dólar: <strong id="empDolar">$19.00</strong></p>
                    <p>Impuesto CA: <strong id="empImpuesto">8%</strong></p>
                </div>

                <div class="calculator-box">
                    <div class="form-group">
                        <label>Precio en Dólares (USD)</label>
                        <input type="number" id="precioUSD" placeholder="Ej: 45.50" step="0.01" oninput="calcularPrecioEmpleado()">
                    </div>

                    <div class="form-group">
                        <label>Descuento (%)</label>
                        <input type="number" id="descuentoPorcentaje" placeholder="Ej: 15, 25, 50..." step="0.1" min="0" max="100" oninput="calcularPrecioEmpleado()">
                    </div>
                </div>

                <div class="result-box" id="resultBox">
                    <div class="price-label">Precio de Venta</div>
                    <div class="price-value" id="precioFinal">$0.00</div>
                    <div class="price-details">
                        <p id="detalles"></p>
                    </div>
                </div>

                <button onclick="logout()" class="danger">Cerrar Sesión</button>

                <div class="auto-update-indicator updating">
                    🔄 Los parámetros se actualizan automáticamente
                </div>
            </div>
        </div>

        <div class="footer">
            © 2024 American Clothes
        </div>
    </div>

    <script>
        const ADMIN_PASSWORD = "american2024";

        let currentUser = null;
        let parametros = {
            tipoCambio: 19,
            impuesto: 8,
            margen1: 30,
            margen2: 25,
            margen3: 20
        };

        document.addEventListener('DOMContentLoaded', function() {
            cargarParametros();
            configurarListeners();

            // Actualizar parámetros cada 2 segundos si es empleado
            setInterval(function() {
                if (currentUser === 'employee') {
                    cargarParametros();
                    actualizarParametrosEmpleado();
                }
            }, 2000);
        });

        function cargarParametros() {
            fetch('/api/params')
                .then(r => r.json())
                .then(data => {
                    parametros = data;
                })
                .catch(e => console.error('Error cargando parámetros:', e));
        }

        function guardarParametros() {
            parametros.tipoCambio = parseFloat(document.getElementById('adminTipoCambio').value);
            parametros.impuesto = parseFloat(document.getElementById('adminImpuesto').value);
            parametros.margen1 = parseFloat(document.getElementById('adminMargen1').value);
            parametros.margen2 = parseFloat(document.getElementById('adminMargen2').value);
            parametros.margen3 = parseFloat(document.getElementById('adminMargen3').value);

            fetch('/api/params', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(parametros)
            })
            .then(r => r.json())
            .then(data => {
                mostrarMensaje('✓ Parámetros guardados correctamente', 'success');
                setTimeout(() => {
                    mostrarMensaje('', '');
                }, 3000);
            })
            .catch(e => {
                mostrarMensaje('❌ Error guardando parámetros', 'error');
                console.error(e);
            });
        }

        function configurarListeners() {
            document.getElementById('roleSelect').addEventListener('change', function(e) {
                const role = e.target.value;
                document.getElementById('adminLoginForm').style.display = role === 'admin' ? 'block' : 'none';
                document.getElementById('employeeLoginForm').style.display = role === 'employee' ? 'block' : 'none';
            });
        }

        function loginAdmin() {
            const password = document.getElementById('adminPassword').value;
            if (password === ADMIN_PASSWORD) {
                currentUser = 'admin';
                mostrarPantalla('admin');
                cargarParametrosAdmin();
            } else {
                alert('❌ Contraseña incorrecta');
            }
        }

        function loginEmployee() {
            currentUser = 'employee';
            mostrarPantalla('employee');
            actualizarParametrosEmpleado();
        }

        function logout() {
            currentUser = null;
            resetLogin();
        }

        function resetLogin() {
            document.getElementById('roleSelect').value = '';
            document.getElementById('adminLoginForm').style.display = 'none';
            document.getElementById('employeeLoginForm').style.display = 'none';
            document.getElementById('adminPassword').value = '';
            mostrarPantalla('login');
        }

        function mostrarPantalla(pantalla) {
            document.getElementById('loginScreen').classList.remove('active');
            document.getElementById('adminScreen').classList.remove('active');
            document.getElementById('employeeScreen').classList.remove('active');

            if (pantalla === 'login') {
                document.getElementById('loginScreen').classList.add('active');
            } else if (pantalla === 'admin') {
                document.getElementById('adminScreen').classList.add('active');
            } else if (pantalla === 'employee') {
                document.getElementById('employeeScreen').classList.add('active');
            }
        }

        function cargarParametrosAdmin() {
            document.getElementById('adminTipoCambio').value = parametros.tipoCambio;
            document.getElementById('adminImpuesto').value = parametros.impuesto;
            document.getElementById('adminMargen1').value = parametros.margen1;
            document.getElementById('adminMargen2').value = parametros.margen2;
            document.getElementById('adminMargen3').value = parametros.margen3;
        }

        function mostrarMensaje(texto, tipo) {
            const msg = document.getElementById('statusMessage');
            msg.textContent = texto;
            msg.className = 'status-message ' + tipo;
        }

        function obtenerMargen(precioUSD) {
            if (precioUSD < 50) return parametros.margen1;
            if (precioUSD <= 100) return parametros.margen2;
            return parametros.margen3;
        }

        function redondearADecimal(precio) {
            const parteDecimal = precio % 1;
            const numeroEntero = Math.floor(precio);

            if (parteDecimal < 0.245) {
                return numeroEntero + 0.49;
            } else if (parteDecimal < 0.745) {
                return numeroEntero + 0.49;
            } else {
                return numeroEntero + 0.99;
            }
        }

        function calcularPrecio(precioUSD, porcentajeDescuento) {
            const margen = obtenerMargen(precioUSD) / 100;

            let costeMXN = precioUSD * parametros.tipoCambio;
            costeMXN = costeMXN * (1 + parametros.impuesto / 100);

            let precioVenta = costeMXN * (1 + margen);
            precioVenta = precioVenta * (1 - (porcentajeDescuento / 100));

            precioVenta = redondearADecimal(precioVenta);

            return precioVenta;
        }

        function calcularPrecioEmpleado() {
            const precioUSD = parseFloat(document.getElementById('precioUSD').value);
            const descuento = parseFloat(document.getElementById('descuentoPorcentaje').value);

            if (!precioUSD || precioUSD < 0 || isNaN(descuento) || descuento < 0) {
                document.getElementById('resultBox').classList.remove('active');
                return;
            }

            const precioFinal = calcularPrecio(precioUSD, descuento);
            const margen = obtenerMargen(precioUSD);

            document.getElementById('precioFinal').textContent = '$' + precioFinal.toFixed(2);
            document.getElementById('detalles').innerHTML =
                `Precio USD: $${precioUSD.toFixed(2)}<br>` +
                `Descuento: ${descuento}%<br>` +
                `Margen: ${margen}%`;

            document.getElementById('resultBox').classList.add('active');
        }

        function actualizarParametrosEmpleado() {
            document.getElementById('empDolar').textContent = '$' + parametros.tipoCambio.toFixed(2);
            document.getElementById('empImpuesto').textContent = parametros.impuesto.toFixed(1) + '%';

            if (document.getElementById('precioUSD').value) {
                calcularPrecioEmpleado();
            }
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/params', methods=['GET'])
def get_params():
    """Obtiene los parámetros actuales"""
    return jsonify(cargar_parametros())

@app.route('/api/params', methods=['POST'])
def save_params():
    """Guarda los parámetros"""
    try:
        params = request.get_json()
        guardar_parametros(params)
        return jsonify({'status': 'success', 'message': 'Parámetros guardados'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Servidor American Clothes - Calculador de Precios")
    print("="*60)
    print("\n✅ El servidor está corriendo en: http://localhost:5000")
    print("\n📝 Instrucciones:")
    print("1. Abre tu navegador")
    print("2. Ve a: http://localhost:5000")
    print("3. Comparte este link con tus empleados por WhatsApp:")
    print("   http://TU_IP:5000")
    print("   (Reemplaza TU_IP con tu dirección IP local)")
    print("\n⚠️  Mantén esta ventana abierta mientras uses la app")
    print("="*60 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=False)
