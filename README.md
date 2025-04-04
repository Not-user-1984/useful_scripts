
Этот Python-скрипт рекурсивно объединяет текстовые файлы из указанной директории в один или несколько выходных файлов, оптимизируя их содержимое для уменьшения количества токенов, сохраняя при этом структуру для обработки ИИ. Поддерживается разбиение на части, если количество токенов превышает 10,000 или количество файлов в части превышает 5.

## Возможности
- Рекурсивно обрабатывает текстовые файлы (`.txt`, `.py`, `.md`, `.csv`) в текущей директории и подпапках.
- Оптимизирует содержимое файлов, удаляя лишние пробелы и комментарии (для `.py`).
- Записывает относительные пути к файлам для удобства ИИ.
- Разбивает результат на части, если токенов > 10,000 или файлов > 5 в одной части.
- Настраиваемый путь вывода и выбор конкретных файлов через флаги командной строки.

## Требования
- Python 3.6+
- Библиотека `tiktoken` для точного подсчета токенов:
  ```bash
  uv sync
  ```

## Установка
1. Скачайте или склонируйте этот скрипт (`combine_files.py`).
2. Установите необходимую зависимость:
   ```bash
   pip install tiktoken
   ```
3. (Опционально) Сделайте скрипт исполняемым:
   ```bash
   chmod +x combine_files.py
   ```

## Использование
Запускайте скрипт из терминала в директории, которую хотите обработать.

### Базовая команда
Объединить все файлы в текущей директории:
```bash
python combine_files.py
```
Результат сохранится в `/your_path/combined_<папка>_<дата-время>.txt` (например, `combined_project_2025-03-26_15-00-00_part1.txt`).

### Параметры командной строки
- `-o, --output`: Указать путь для выходного файла.
- `-f, --files`: Список конкретных файлов для обработки (через пробел).

#### Примеры
1. **Свой путь вывода**:
   ```bash
   python combine_files.py -o /custom/output
   ```
   Результат: `/custom/output_part1.txt`, `/custom/output_part2.txt` и т.д., если есть разбиение.

2. **Конкретные файлы**:
   ```bash
   python combine_files.py -f file1.txt subfolder/file2.py
   ```
   Обрабатываются только `file1.txt` и `subfolder/file2.py`.

3. **Свой путь и файлы**:
   ```bash
   python combine_files.py -o ./output.txt -f readme.txt script.py
   ```

4. **Справка**:
   ```bash
   python combine_files.py --help
   ```

### Формат вывода
Каждая строка в выходном файле содержит:
```
[относительный/путь/к/файлу] оптимизированное содержимое
```
- Относительные пути считаются от стартовой директории.
- При превышении 10,000 токенов или 5 файлов результат разбивается на части с суффиксом `_partX`.

### Пример вывода
Для директории `/home/user/project`:
```
[readme.txt] Привет, мир
[subfolder/script.py] print Привет
```
Если есть разбиение:
- `combined_project_2025-03-26_15-00-00_part1.txt`
- `combined_project_2025-03-26_15-00-00_part2.txt`

## Настройки
- **Директория по умолчанию**: `/Users/diplug/my_dev/temp_file` (измените `DEFAULT_OUTPUT_DIR` в скрипте).
- **Максимум токенов**: 10,000 на часть (измените `MAX_TOKENS`).
- **Максимум файлов на часть**: 5 (измените `MAX_FILES_PER_PART`).
- **Поддерживаемые расширения**: `.txt`, `.py`, `.md`, `.csv` (измените `text_extensions`).

## Примечания
- Скрытые директории (начинаются с `.`) и специальные (начинаются с `__`) пропускаются.
- Ошибки выводятся в консоль, но не прерывают работу.
- При использовании `-f` указывайте имена файлов относительно текущей директории (например, `subfolder/file.txt`).
