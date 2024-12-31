# -*- coding: utf-8 -*-
import random
import aiofiles
from curl_cffi.requests import AsyncSession
from logger import logger

def get_user_agent():
    random_version = f"{random.uniform(520, 540):.2f}"
    return (f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/{random_version}'
            f' (KHTML, like Gecko) Chrome/121.0.0.0 Safari/{random_version} Edg/121.0.0.0')

async def read_file_txt(file_path):
    try:
        async with aiofiles.open(file_path, "r") as file:
            content = await file.read()
            return content.splitlines()
    except FileNotFoundError:
        logger.error(f"Error: File '{file_path}' not found.")
    except PermissionError:
        logger.error(f"Error: Permission denied to read file '{file_path}'.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

async def check_proxy(proxy: str) -> tuple[str, bool]:
    url = "http://httpbin.org/ip"
    try:
        async with AsyncSession() as session:
            response = await session.get(url=url, proxy=proxy, timeout=30)
            if response.status_code == 200:
                return True
            else:
                return False
    except Exception as e:
        logger.error(f'Proxy check error: {e}')
        return False
