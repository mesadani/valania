# myapp/views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .service.phantom_wallet import get_balance, get_nfts, extract_nft_info, get_nft_transactions, extract_nft_info_extends
import json

# Vista que renderiza el HTML donde el frontend puede interactuar con Phantom
def connect(request):
    return render(request, 'connect.html')  # Asegúrate de que el archivo index.html esté en la carpeta de plantillas (templates)

@csrf_exempt
def nftInfo(request):
    if request.method == "POST":
        # Imprimir el cuerpo de la solicitud para depuración
        try:
            # Deserializar el JSON recibido en el cuerpo de la solicitud
            data = json.loads(request.body)
           
            # Verificar que la dirección de la wallet esté presentes
            mintAddress = data.get("mintAddress")
            if not mintAddress:
                return JsonResponse({"error": "Wallet address is required"}, status=400)

            # Obtener saldo y s
     
            balance = get_nft_transactions(mintAddress,5)
               

            return JsonResponse({"balance": balance})

        except json.JSONDecodeError as e:
            return JsonResponse({"error": f"Invalid JSON format: {str(e)}"}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Internal Server Error: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method. Use POST."}, status=405)


@csrf_exempt
def wallet_info(request):
    """
    Endpoint para obtener saldo y NFTs de una wallet Phantom.
    """
    if request.method == "POST":
        # Imprimir el cuerpo de la solicitud para depuración
      

        try:
            # Deserializar el JSON recibido en el cuerpo de la solicitud
            data = json.loads(request.body)
           
            # Verificar que la dirección de la wallet esté presentes
            wallet_address = data.get("wallet_address")
            if not wallet_address:
                return JsonResponse({"error": "Wallet address is required"}, status=400)

            # Obtener saldo y s
     
            balance = get_balance(wallet_address)
            sol_balance = balance / 1_000_000_000  # convierte de lamports a SOL
       
            nfts = get_nfts(wallet_address)
           
            data = extract_nft_info_extends({"nfts": nfts})
            return JsonResponse({"balance": sol_balance, "nfts": data, "data": data})

        except json.JSONDecodeError as e:
            return JsonResponse({"error": f"Invalid JSON format: {str(e)}"}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Internal Server Error: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method. Use POST."}, status=405)


def wallet_info_nft(wallet_address):
    """
    Endpoint para obtener saldo y NFTs de una wallet Phantom.
    """

    try:
        # Deserializar el JSON recibido en el cuerpo de la solicitud
       
        if not wallet_address:
            return JsonResponse({"error": "Wallet address is required"}, status=400)
        
        nfts = get_nfts(wallet_address)
        
        data = extract_nft_info({"nfts": nfts})
        return JsonResponse({"nfts": data, "data": data})

    except json.JSONDecodeError as e:
        return JsonResponse({"error": f"Invalid JSON format: {str(e)}"}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"Internal Server Error: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method. Use POST."}, status=405)


@csrf_exempt
def wallet_info_extend(request):
    if request.method == "POST":
        # Imprimir el cuerpo de la solicitud para depuración
      

        try:
            # Deserializar el JSON recibido en el cuerpo de la solicitud
            data = json.loads(request.body)
           
            # Verificar que la dirección de la wallet esté presentes
            wallet_address = data.get("wallet_address")
            if not wallet_address:
                return JsonResponse({"error": "Wallet address is required"}, status=400)

            # Obtener saldo y s
     
            balance = get_balance(wallet_address)
            sol_balance = balance / 1_000_000_000  # convierte de lamports a SOL
       
            nfts = get_nfts(wallet_address)
           
            data = extract_nft_info({"nfts": nfts})
            return JsonResponse({"balance": sol_balance, "nfts": data, "data": data})

        except json.JSONDecodeError as e:
            return JsonResponse({"error": f"Invalid JSON format: {str(e)}"}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Internal Server Error: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method. Use POST."}, status=405)    