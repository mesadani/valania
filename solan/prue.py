import asyncio
import matplotlib.pyplot as plt
from datetime import datetime
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
import os
import django

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valProject.settings')  # Reemplaza 'mi_proyecto' con tu proyecto real
django.setup()

# Dirección del NFT en Solana
NFT_ADDRESS = "AbycFawZQS7qd6Gh9cKdBy5EGyK9FSSddjqgLjdpjgm"

# Conectar al RPC de Solana
RPC_URL = "https://api.mainnet-beta.solana.com"
client = AsyncClient(RPC_URL)

async def get_token_supply(nft_address: str):
    """Obtiene el supply del NFT en la blockchain de Solana."""
    response = await client.get_token_supply(Pubkey.from_string(nft_address))
    return response.value.amount if response.value else None

async def get_nft_movements(nft_address: str, limit=10):
    """Obtiene las últimas transacciones del NFT."""
    signatures_response = await client.get_signatures_for_address(Pubkey.from_string(nft_address), limit=limit)
    signatures = signatures_response.value

    movements = []
    for sig in signatures:
        tx_response = await client.get_transaction(sig.signature)
        if tx_response.value:
            movements.append({
                "signature": sig.signature,
                "slot": tx_response.value.slot,
                "timestamp": sig.block_time,
            })
    
    return movements

async def main():
    supply = await get_token_supply(NFT_ADDRESS)
    print(f"Supply del NFT: {supply}")

    movements = await get_nft_movements(NFT_ADDRESS, limit=20)
    
    if not movements:
        print("No se encontraron transacciones para este NFT.")
        return

    print(f"Se encontraron {len(movements)} transacciones.")
    
    for m in movements:
        print(f" - Tx: {m['signature']} | Slot: {m['slot']} | Fecha: {datetime.utcfromtimestamp(m['timestamp'])}")

    # Graficar los movimientos en el tiempo
    timestamps = [m["timestamp"] for m in movements]
    dates = [datetime.utcfromtimestamp(t) for t in timestamps]
    values = list(range(1, len(dates) + 1))

    plt.figure(figsize=(10, 5))
    plt.plot(dates, values, marker="o", linestyle="-", color="b")
    plt.xlabel("Fecha")
    plt.ylabel("Número de transacciones")
    plt.title("Actividad del NFT en la Blockchain de Solana")
    plt.xticks(rotation=45)
    plt.grid()
    plt.show()

# Ejecutar el script
asyncio.run(main())
