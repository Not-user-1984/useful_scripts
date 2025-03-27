import os
import tiktoken
import argparse
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

current_dir = os.getcwd()

text_extensions = [".txt", ".py", ".md", ".csv"]

DEFAULT_OUTPUT_DIR = "/Users/diplug/my_dev/temp_file"

MAX_TOKENS = 10000
ENCODING_NAME = "cl100k_base"


try:
    ENCODING = tiktoken.get_encoding(ENCODING_NAME)
except Exception as e:
    logger.error(
        f"Ну удалось получить кодировку tiktoken{ENCODING_NAME} ошибка: {str(e)}"
        "Проверьте, что у вас установлено tiktoken.\n"
        "Установка: pip install tiktoken"
    )


def count_tokens(text: str) -> int:
    return len(ENCODING.encode(text))


def optimize_content(content, filepath):
    """Оптимизирует содержимое файла для уменьшения токенов"""
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    if filepath.endswith(".py"):
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
            try:
                relative_path = os.path.relpath(item_path, base_dir).replace(
                    os.sep, "/"
                )
            except ValueError as e:
                logger.warning(
                    f"Не удалось получить относительный путь для {item_path} от {base_dir}: {e}"
                )
                continue

            is_file = os.path.isfile(item_path)
            is_dir = os.path.isdir(item_path)

            if is_file:
                process_this_file = False
                if target_files is not None:
                    if relative_path in target_files:
                        process_this_file = True

                else:
                    if any(item.endswith(ext) for ext in text_extensions):
                        process_this_file = True

                if process_this_file:
                    try:
                        with open(
                            item_path, "r", encoding="utf-8", errors="ignore"
                        ) as infile:
                            content = infile.read()
                        optimized_content = optimize_content(content, item_path)
                        result_lines.append(f"[{relative_path}] {optimized_content}")
                        logger.info(f"Обработан файл: {relative_path}")
                    except Exception as e:
                        logger.error(
                            f"Ошибка при обработке файла {item_path}: {str(e)}"
                        )

            elif is_dir:
                should_recurse = True
                if target_files is not None:
                    dir_prefix = relative_path + "/"
                    if not any(
                        target.startswith(dir_prefix) for target in target_files
                    ):
                        should_recurse = False

                if should_recurse:
                    result_lines.extend(
                        process_directory(item_path, base_dir, target_files)
                    )

    except FileNotFoundError:
        logger.warning(f"Директория не найдена при сканировании: {directory}")
    except PermissionError:
        logger.warning(f"Нет прав доступа к директории: {directory}")
    except Exception as e:
        logger.error(f"Ошибка при обработке директории {directory}: {str(e)}")

    return result_lines


def split_and_save(lines, output_base_path):
    """Разбивает содержимое на файлы по MAX_TOKENS и сохраняет их"""
    current_part = 1
    current_content = []
    current_tokens = 0

    for line in lines:
        line_tokens = count_tokens(line)

        if current_tokens + line_tokens > MAX_TOKENS and current_content:
            output_path = f"{output_base_path}_part{current_part}.txt"
            with open(output_path, "w", encoding="utf-8") as outfile:
                outfile.write("\n".join(current_content) + "\n")
            logger.info(
                f"Сохранена часть: {output_path} (токенов: {current_tokens})"
                )
            current_part += 1
            current_content = []
            current_tokens = 0
        current_content.append(line)
        current_tokens += line_tokens

    if current_content:
        output_path = (
            f"{output_base_path}_part{current_part}.txt"
            if current_part > 1
            else f"{output_base_path}.txt"
        )
        with open(output_path, "w", encoding="utf-8") as outfile:
            outfile.write("\n".join(current_content) + "\n")
        logger.info(
            f"Сохранена часть: {output_path} (токенов: {current_tokens})")


def combine_files(start_dir=current_dir, output_path=None, target_files=None):
    """Главная функция для объединения файлов"""
    folder_name = os.path.basename(start_dir)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    if output_path is None:
        output_base_filename = f"combined_{folder_name}_{timestamp}"
        output_base_path = os.path.join(DEFAULT_OUTPUT_DIR, output_base_filename)
    else:
        output_base_path = os.path.splitext(output_path)[0]

    os.makedirs(os.path.dirname(output_base_path), exist_ok=True)

    try:
        all_lines = process_directory(
            start_dir, base_dir=start_dir, target_files=target_files
        )

        total_tokens = count_tokens("\n".join(all_lines))
        logger.info(f"\nОбщее количество токенов: {total_tokens}")

        split_and_save(all_lines, output_base_path)

        logger.info(
            "Все содержимое обработано и сохранено (файлов)"
            f"{len([l for l in all_lines if l.strip()])})"
        )
        logger.info(f"Количество символов в сумме: {len(''.join(all_lines))}")
        logger.info(f"Количество слов в сумме: {len(' '.join(all_lines).split())}")

    except Exception as e:
        logger.info(f"Произошла ошибка: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Объединяет текстовые файлы в один с оптимизацией токенов."
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="Путь для сохранения выходного файла",
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
