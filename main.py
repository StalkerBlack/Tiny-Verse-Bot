# -*- coding: utf-8 -*-
import asyncio
import subprocess
import sys

from curl_cffi.requests import AsyncSession

from utils import *
from logger import logger


async def get_clients() -> list[tuple[str, str]]:
    tokens: list[str] = await read_file_txt(file_path='tokens.txt')
    proxies: list[str] = await read_file_txt(file_path='proxies.txt')
    
    if len(tokens) == 0:
        logger.error("No tokens found. Please check tokens.txt file")
        return []

    if len(proxies) == 0:
        logger.warning("No proxies found, program will run without them")
        return [(token, '') for token in tokens]
    
    min_length = min(len(proxies), len(tokens))
    proxies = proxies[:min_length]
    tokens = tokens[:min_length]
    
    valid_proxies = await asyncio.gather(*(check_proxy(proxy) for proxy in proxies))

    invalid_proxies = [proxy for proxy, is_valid in zip(proxies, valid_proxies) if not is_valid]
    invalid_count = len(invalid_proxies)
    
    if invalid_count > 0:
        logger.warning(f"Checked {len(proxies)} proxies. {invalid_count} proxies are not working")
        logger.error(f"Invalid proxies: {invalid_proxies}")

    clients = [(token, proxy) for token, proxy, is_valid in zip(tokens, proxies, valid_proxies) if is_valid]

    logger.debug(f'Initialized {len(clients)} clients for operation')
    
    return clients

async def claim_duster_for_client(token: str, proxy: str, client_name: str):
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'ru,en-US;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'DNT': '1',
        'Origin': 'https://app.tonverse.app',
        'Referer': 'https://app.tonverse.app/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': get_user_agent(),
        'X-Application-Version': '0.7.37',
        'X-Requested-With': 'XMLHttpRequest',
    }

    async with AsyncSession() as session:
        while True:
            try:
                # Check if proxy exists
                if proxy:
                    response = await session.post(
                        url='https://api.tonverse.app/galaxy/collect',
                        proxy=proxy,
                        headers=headers,
                        data={'session': token}
                    )
                else:
                    response = await session.post(
                        url='https://api.tonverse.app/galaxy/collect',
                        headers=headers,
                        data={'session': token}
                    )

                if response.status_code != 200:
                    logger.error(f'{client_name} | Request error: {response.status_code}')
                else:
                    logger.success(f'{client_name} | Successfully claimed dust')
            except Exception as e:
                logger.error(f'{client_name} | Request error: {e}')

            duration = random.randint(25 * 60, 50 * 60)
            minutes = duration // 60
            seconds = duration % 60 

            logger.info(f"{client_name} | ⏳ Next dust claim in {minutes} min {seconds} sec ...")

            await asyncio.sleep(duration)


async def claim_duster():
    clients = await get_clients()

    if not clients:
        logger.error("No available clients for operation.")
        return

    tasks = []
    for client_index, (token, proxy) in enumerate(clients, start=1):
        client_name = f"Client {client_index}"
        
        if client_index > 1:
            delay = 10
            logger.debug(f"⏳ Waiting {delay} seconds before starting the next client...")
            await asyncio.sleep(delay)

        tasks.append(
            asyncio.create_task(claim_duster_for_client(token, proxy, client_name))
        )

    await asyncio.gather(*tasks)

def install_requirements():
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while installing requirements: {e}")


if __name__ == "__main__":
    install_requirements()
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(claim_duster())
