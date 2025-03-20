from tronpy.keys import PrivateKey
import concurrent.futures
import multiprocessing
import numba
import numpy as np

desired_suffix = "7777"
found_event = multiprocessing.Event()  


@numba.jit(nopython=True, parallel=True, nogil=True)
def generate_keys_gpu(num_keys, results):
    """Генерация приватных ключей на GPU"""
  
    for i in numba.prange(num_keys):
        priv_key = np.random.bytes(32)  
        results[i] = priv_key.hex()  


def check_keys_gpu():
    """Генерация и проверка адресов на GPU"""
  
    while not found_event.is_set():
        num_keys = 100000  
        results = np.empty(num_keys, dtype='<U64') 

        generate_keys_gpu(num_keys, results) 

        for hex_key in results:
            priv_key = PrivateKey(bytes.fromhex(hex_key))
            addr = priv_key.public_key.to_base58check_address()

            if addr.endswith(desired_suffix):
                print(f"адрес найден (GPU): {addr}")
                print(f"приватный ключ: {hex_key}")
                found_event.set()  
                return


def generate_keys_cpu():
    """Генерация и проверка адресов на CPU"""
  
    while not found_event.is_set():
        priv_key = PrivateKey.random()
        addr = priv_key.public_key.to_base58check_address()

      
        if addr.endswith(desired_suffix):
            print(f"адрес найден (CPU): {addr}")
            print(f"приватный ключ: {priv_key.hex()}")
            found_event.set()  
            return



if __name__ == "__main__":
    num_cpu_threads = multiprocessing.cpu_count()  
    num_gpu_threads = 1  

    with concurrent.futures.ProcessPoolExecutor(max_workers=num_cpu_threads + num_gpu_threads) as executor:
      
        for _ in range(num_cpu_threads):
            executor.submit(generate_keys_cpu)

        executor.submit(check_keys_gpu)
