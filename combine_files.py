import os
import tiktoken
import argparse
from datetime import datetime

# Текущая директория, откуда запущен скрипт
current_dir = os.getcwd()

# Список расширений файлов по умолчанию
text_extensions = [".txt", ".py", ".md", ".csv"]

# Дефолтный путь для сохранения файла (без имени файла, только директория)
DEFAULT_OUTPUT_DIR = "/Users/diplug/my_dev/temp_file"

# Максимальное количество токенов в одном файле
MAX_TOKENS = 10000


def count_tokens(text, encoding_name="cl100k_base"):
    """Подсчитывает количество токенов"""
    encoding = tiktoken.get_encoding(encoding_name)
    tokens = encoding.encode(text)
    return len(tokens)


def optimize_content(content):
    """Оптимизирует содержимое файла для уменьшения токенов"""
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    if content.endswith(".py"):
        lines = [line for line in lines if not line.startswith("#")]
    return " ".join(lines)


def process_directory(directory, base_dir, target_files=None):
    """Рекурсивно собирает содержимое файлов и возвращает список строк"""
    result_lines = []
    try:
        for item in os.listdir(directory):
            if item.startswith(".") or item.startswith("__"):
                continue

            item_path = os.path.join(directory, item)
            relative_path = os.path.relpath(item_path, base_dir)

            if target_files is not None and item not in target_files:
                continue

            if os.path.isfile(item_path) and any(
                item.endswith(ext) for ext in text_extensions
            ):
                try:
                    with open(item_path, "r", encoding="utf-8") as infile:
                        content = infile.read()
                        optimized_content = optimize_content(content)
                        result_lines.append(f"[{relative_path}] {optimized_content}")
                    print(f"Обработан файл: {relative_path}")
                except Exception as e:
                    print(f"Ошибка при обработке файла {item_path}: {str(e)}")

            elif os.path.isdir(item_path):
                result_lines.extend(
                    process_directory(item_path, base_dir, target_files)
                )

    except Exception as e:
        print(f"Ошибка при обработке директории {directory}: {str(e)}")

    return result_lines


def split_and_save(lines, output_base_path):
    """Разбивает содержимое на файлы по MAX_TOKENS и сохраняет их"""
    current_part = 1
    current_content = []
    current_tokens = 0

    for line in lines:
        line_tokens = count_tokens(line)

        # Если добавление строки превысит лимит, сохраняем текущую часть
        if current_tokens + line_tokens > MAX_TOKENS and current_content:
            output_path = f"{output_base_path}_part{current_part}.txt"
            with open(output_path, "w", encoding="utf-8") as outfile:
                outfile.write("\n".join(current_content) + "\n")
            print(f"Сохранена часть: {output_path} (токенов: {current_tokens})")
            current_part += 1
            current_content = []
            current_tokens = 0

        # Добавляем строку в текущую часть
        current_content.append(line)
        current_tokens += line_tokens

    # Сохраняем последнюю часть, если есть что сохранять
    if current_content:
        output_path = (
            f"{output_base_path}_part{current_part}.txt"
            if current_part > 1
            else f"{output_base_path}.txt"
        )
        with open(output_path, "w", encoding="utf-8") as outfile:
            outfile.write("\n".join(current_content) + "\n")
        print(f"Сохранена часть: {output_path} (токенов: {current_tokens})")


def combine_files(start_dir=current_dir, output_path=None, target_files=None):
    """Главная функция для объединения файлов"""
    # Получаем имя папки из текущей директории
    folder_name = os.path.basename(start_dir)
    # Получаем текущее время в формате ГГГГ-ММ-ДД_ЧЧ-ММ-СС
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Если output_path не указан, формируем базовое имя файла
    if output_path is None:
        output_base_filename = f"combined_{folder_name}_{timestamp}"
        output_base_path = os.path.join(DEFAULT_OUTPUT_DIR, output_base_filename)
    else:
        # Если указан путь, используем его как базовый (без расширения пока)
        output_base_path = os.path.splitext(output_path)[0]

    # Убеждаемся, что директория для выходного файла существует
    os.makedirs(os.path.dirname(output_base_path), exist_ok=True)

    try:
        # Собираем все строки
        all_lines = process_directory(
            start_dir, base_dir=start_dir, target_files=target_files
        )

        # Проверяем общее количество токенов
        total_tokens = count_tokens("\n".join(all_lines))
        print(f"\nОбщее количество токенов: {total_tokens}")

        # Разбиваем и сохраняем
        split_and_save(all_lines, output_base_path)

        print(
            f"Все содержимое обработано и сохранено (файлов: {len([l for l in all_lines if l.strip()])})"
        )
        print(f"Количество символов в сумме: {len(''.join(all_lines))}")
        print(f"Количество слов в сумме: {len(' '.join(all_lines).split())}")

    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")


if __name__ == "__main__":
    # Настройка аргументов командной строки
    parser = argparse.ArgumentParser(
        description="Объединяет текстовые файлы в один с оптимизацией токенов."
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="Путь для сохранения выходного файла (по умолчанию: combined_<folder>_<timestamp>.txt в /Users/diplug/my_dev/temp_file)",
    )
    parser.add_argument(
        "-f",
        "--files",
        type=str,
        nargs="*",
        default=None,
        help="Список имен файлов для обработки (например, file1.txt file2.py). Если не указано, обрабатываются все файлы.",
    )

    args = parser.parse_args()
    target_files = set(args.files) if args.files else None
    combine_files(output_path=args.output, target_files=target_files)
