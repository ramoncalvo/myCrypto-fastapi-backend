#!/usr/bin/env python3
"""
Script para mostrar el SQL necesario para crear las tablas en Supabase
"""

import os
from config import settings

def create_tables():
    """Crear todas las tablas necesarias en Supabase usando conexión directa"""
    
    # Construir la URL de conexión desde las variables de entorno
    # Formato: postgresql://postgres:password@host:port/database
    supabase_url = settings.supabase_url
    if not supabase_url:
        print("❌ SUPABASE_URL no encontrada en variables de entorno")
        return False
    
    # Extraer información de la URL
    # https://yeincwcqvhxpytmiczld.supabase.co -> db.yeincwcqvhxpytmiczld.supabase.co
    project_ref = supabase_url.replace("https://", "").replace(".supabase.co", "")
    
    print("📋 Para crear las tablas, necesitas ejecutar el siguiente SQL en Supabase:")
    print("=" * 60)
    
    with open('sql_schema.sql', 'r') as f:
        sql_content = f.read()
        print(sql_content)
    
    print("=" * 60)
    print("\n🔗 Pasos:")
    print("1. Ve a https://supabase.com")
    print("2. Selecciona tu proyecto")
    print("3. Ve a 'SQL Editor' en la barra lateral")
    print("4. Copia y pega el SQL de arriba")
    print("5. Haz clic en 'Run' para ejecutar")
    
    print("\n💡 Alternativamente, puedes usar la conexión directa de PostgreSQL")
    print("   si tienes la contraseña de la base de datos.")
    
    return True

def insert_sample_data():
    """Insertar datos de ejemplo usando el cliente de Supabase"""
    from database import supabase_client
    
    print("📊 Insertando criptomonedas de ejemplo...")
    
    crypto_assets = [
        {"symbol": "BTC", "name": "Bitcoin", "current_price": 45000.00},
        {"symbol": "ETH", "name": "Ethereum", "current_price": 3000.00},
        {"symbol": "ADA", "name": "Cardano", "current_price": 0.50},
        {"symbol": "DOT", "name": "Polkadot", "current_price": 25.00},
        {"symbol": "SOL", "name": "Solana", "current_price": 100.00}
    ]
    
    for asset in crypto_assets:
        try:
            result = supabase_client.table("crypto_assets").insert(asset).execute()
            print(f"   ✓ {asset['symbol']} - {asset['name']}")
        except Exception as e:
            if "duplicate key" in str(e).lower() or "already exists" in str(e).lower():
                print(f"   ⚠️  {asset['symbol']} ya existe")
            else:
                print(f"   ❌ Error insertando {asset['symbol']}: {e}")

if __name__ == "__main__":
    create_tables()
    
    # Preguntar si quiere insertar datos de ejemplo
    response = input("\n¿Quieres insertar datos de ejemplo? (y/n): ").lower()
    if response in ['y', 'yes', 'sí', 's']:
        insert_sample_data()
