#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
download_wiki_ru.py - Скачивание и обработка русской Википедии в txt

Этим скриптом собраны 584 фрагмента корпуса ENGRAMS (часть 3).
Разбор дампа: mwxml + mwparserfromhell (strip_code), только статьи
(namespace 0), последняя ревизия, статьи короче 100 знаков пропускаются,
каждая статья пишется как "### Заголовок ###", фрагменты по 20 МиБ.
Для публикации изменён только путь по умолчанию для --chunks-dir
и эта строка описания; логика сборки — как в исходном запуске.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
import requests
from tqdm import tqdm

def download_file(url: str, output_path: str) -> bool:
    """Скачивание с progress bar"""
    print(f"Скачиваю: {url}")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(output_path, 'wb') as f:
            with tqdm(total=total_size, unit='B', unit_scale=True) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))
        
        print(f"✓ Скачано: {output_path}")
        return True
    
    except Exception as e:
        print(f"✗ Ошибка скачивания: {e}")
        return False

def extract_wiki_dump(dump_path: str, output_dir: str) -> bool:
    """Извлечение текста из Wikipedia dump и нарезка на чанки"""
    print(f"\nИзвлекаю текст из {dump_path}...")
    
    # Проверяем зависимости
    try:
        import mwxml
        import mwparserfromhell
    except ImportError:
        print("Устанавливаю зависимости...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "mwxml", "mwparserfromhell", "--break-system-packages"])
        import mwxml
        import mwparserfromhell
    
    try:
        import bz2
        os.makedirs(output_dir, exist_ok=True)
        
        file_idx = 0
        article_count = 0
        current_file = None
        current_size = 0
        max_size = 20 * 1024 * 1024  # 20MB per chunk (как в chunk_maker)
        
        print("Парсинг dump файла (может занять 1-2 часа)...")
        
        # Определяем формат файла
        is_compressed = dump_path.endswith('.bz2')
        
        if is_compressed:
            print("Формат: сжатый BZ2 (медленнее)")
            file_handle = bz2.open(dump_path, 'rt', encoding='utf-8')
        else:
            print("Формат: распакованный XML (быстрее)")
            file_handle = open(dump_path, 'r', encoding='utf-8')
        
        with file_handle as f:
            dump = mwxml.Dump.from_file(f)
            
            for page in tqdm(dump, desc="Статьи"):
                # Пропускаем не-статьи
                if page.namespace != 0:
                    continue
                
                for revision in page:
                    if revision.text is None:
                        continue
                    
                    # Парсим wiki-разметку
                    try:
                        wikicode = mwparserfromhell.parse(revision.text)
                        text = wikicode.strip_code()
                        
                        if len(text) < 100:  # Слишком короткая статья
                            continue
                        
                        # Создаем новый chunk если нужно
                        if current_file is None or current_size >= max_size:
                            if current_file:
                                current_file.close()
                            
                            # Именование как в chunk_maker: chunk_000000.txt
                            filename = os.path.join(output_dir, f"chunk_{file_idx:06d}.txt")
                            current_file = open(filename, 'w', encoding='utf-8')
                            file_idx += 1
                            current_size = 0
                        
                        # Пишем статью
                        article_text = f"### {page.title} ###\n\n{text}\n\n"
                        current_file.write(article_text)
                        current_size += len(article_text.encode('utf-8'))
                        article_count += 1
                        
                    except Exception:
                        continue
                    
                    break  # Берем только последнюю ревизию
        
        if current_file:
            current_file.close()
        
        print(f"✓ Извлечено статей: {article_count}")
        print(f"✓ Создано чанков: {file_idx}")
        return True
    
    except Exception as e:
        print(f"✗ Ошибка извлечения: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    parser = argparse.ArgumentParser(description="Скачать и обработать Wikipedia RU dump")
    parser.add_argument("--output-dir", type=str, default="wiki_ru_dataset", 
                        help="Директория для хранения dump файла")
    parser.add_argument("--chunks-dir", type=str, default="chunks",
                        help="Директория для чанков (по умолчанию: ./chunks)")
    parser.add_argument("--skip-download", action="store_true",
                        help="Пропустить скачивание (если файл уже есть)")
    parser.add_argument("--dump-date", type=str, default="latest",
                        help="Дата dump (например: 20240101 или latest)")
    
    args = parser.parse_args()
    
    base_dir = Path(args.output_dir)
    base_dir.mkdir(exist_ok=True)
    
    chunks_dir = Path(args.chunks_dir)
    chunks_dir.mkdir(parents=True, exist_ok=True)
    
    # URLs
    if args.dump_date == "latest":
        dump_url = "https://dumps.wikimedia.org/ruwiki/latest/ruwiki-latest-pages-articles.xml.bz2"
    else:
        dump_url = f"https://dumps.wikimedia.org/ruwiki/{args.dump_date}/ruwiki-{args.dump_date}-pages-articles.xml.bz2"
    
    dump_file_bz2 = base_dir / "ruwiki-dump.xml.bz2"
    dump_file_xml = base_dir / "ruwiki-dump.xml"
    
    # Определяем какой файл использовать (XML быстрее чем BZ2)
    if dump_file_xml.exists():
        dump_file = dump_file_xml
        file_size_gb = dump_file.stat().st_size / (1024**3)
        print("=" * 60)
        print(f"✓ Найден распакованный XML ({file_size_gb:.2f} GB)")
        print("=" * 60)
        print(f"Файл: {dump_file}")
        print("Обработка будет быстрее (~2-3x)")
        skip_download = True
    elif dump_file_bz2.exists():
        dump_file = dump_file_bz2
        file_size_gb = dump_file.stat().st_size / (1024**3)
        print("=" * 60)
        print(f"✓ Найден сжатый BZ2 ({file_size_gb:.2f} GB)")
        print("=" * 60)
        print(f"Файл: {dump_file}")
        skip_download = True
    else:
        dump_file = dump_file_bz2
        skip_download = False
    
    # Шаг 1: Скачивание
    if skip_download:
        print("Пропускаю скачивание...")
    elif not args.skip_download:
        print("=" * 60)
        print("ШАГ 1: Скачивание Wikipedia RU dump")
        print("=" * 60)
        if not download_file(dump_url, str(dump_file)):
            print("✗ Не удалось скачать dump")
            return 1
    else:
        print(f"✗ Файл не найден: {dump_file}")
        print("Запустите без --skip-download для скачивания")
        return 1
    
    # Шаг 2: Извлечение текста
    if chunks_dir.exists() and list(chunks_dir.glob("chunk_*.txt")):
        existing_count = len(list(chunks_dir.glob("chunk_*.txt")))
        print("\n" + "=" * 60)
        print(f"✓ Найдены уже извлеченные чанки ({existing_count} шт.)")
        print("=" * 60)
        print(f"Директория: {chunks_dir}")
        print("Пропускаю извлечение...")
    else:
        print("\n" + "=" * 60)
        print("ШАГ 2: Извлечение и нарезка на чанки")
        print("=" * 60)
        if not extract_wiki_dump(str(dump_file), str(chunks_dir)):
            print("✗ Не удалось извлечь текст")
            return 1
    
    # Финальная статистика
    final_count = len(list(chunks_dir.glob("chunk_*.txt")))
    
    print("\n" + "=" * 60)
    print("✓ ГОТОВО!")
    print("=" * 60)
    print(f"Чанков создано: {final_count}")
    print(f"Директория: {chunks_dir}")
    print(f"\nЧанки готовы к обработке build_co_occ_sparse.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
