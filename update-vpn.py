import requests

sources = [
    "https://sub.vlessfo.ru/vlessforu/working_configs.txt",
    "https://hub.mos.ru/akelladejavu/bunker/-/raw/main/WHITE_LIST.txt"
]

new_configs = []
counter = 1

for url in sources:
    try:
        print(f"Скачивание источника: {url}")
        response = requests.get(url, timeout=20)
        lines = response.text.splitlines()
        
        for line in lines:
            line = line.strip()
            
            # Добавлено пропущенное двоеточие в конце строки
            if line.startswith(('vless://', 'vmess://', 'trojan://', 'ss://')):
                if '#' in line:
                    base_config = line.split('#')[0]
                else:
                    base_config = line
              
                custom_name = f"TargeterVPN_{counter}"
                new_config = f"{base_config}#{custom_name}"
                new_configs.append(new_config)
                counter += 1
                
    except Exception as e:
        print(f"Ошибка при обработке источника {url}: {e}")

if new_configs:
    with open("working_configs.txt", "w", encoding="utf-8") as f:
        f.write('\n'.join(new_configs))
    print(f"Успешно объединено и сохранено {len(new_configs)} серверов в стиле TargeterVPN.")
else:
    print("Критическая ошибка: не удалось собрать сервера ни из одного источника.")

