import os
from google.cloud import translate_v2 as translate

# Налаштування доступу до Google Translate API
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'Translation.json'
translate_client = translate.Client()


def read_config(config_file):
    config = {}
    try:
        with open(config_file, 'r', encoding='utf-8') as file:
            for line in file:
                key, value = line.strip().split('=')
                config[key.strip()] = value.strip()
    except FileNotFoundError:
        print(f"Помилка: Конфігураційний файл {config_file} не знайдено.")
    except Exception as e:
        print(f"Помилка при читанні конфігураційного файлу: {e}")
    return config


def count_text_properties(text):
    """Підрахунок кількості символів, слів і речень у тексті"""
    num_chars = len(text)
    num_words = len(text.split())
    num_sentences = text.count('.') + text.count('!') + text.count('?')
    return num_chars, num_words, num_sentences


def read_text_file(text_file, char_limit=None, word_limit=None, sentence_limit=None):
    """Читає текстовий файл з обмеженнями"""
    try:
        with open(text_file, 'r', encoding='utf-8') as file:
            text = ""
            num_chars, num_words, num_sentences = 0, 0, 0

            for line in file:
                text += line
                num_chars, num_words, num_sentences = count_text_properties(text)

                if (char_limit and num_chars > char_limit) or \
                        (word_limit and num_words > word_limit) or \
                        (sentence_limit and num_sentences > sentence_limit):
                    break

            return text, num_chars, num_words, num_sentences
    except FileNotFoundError:
        print(f"Помилка: Файл {text_file} не знайдено.")
        return None, 0, 0, 0
    except Exception as e:
        print(f"Помилка при читанні файлу: {e}")
        return None, 0, 0, 0


def TransLate(text, lang):
    """Переклад тексту на зазначену мову"""
    try:
        result = translate_client.translate(text, target_language=CodeLang(lang))
        return result['translatedText']
    except Exception as e:
        return f"Помилка при перекладі: {e}"


def LangDetect(text):
    """Визначення мови тексту та впевненості"""
    try:
        result = translate_client.detect_language(text)
        language_code = result['language']
        confidence = result['confidence'] * 100
        return language_code, confidence
    except Exception as e:
        return None, 0


def CodeLang(lang):
    """Отримання коду мови з назви або коду мови"""
    lang_codes = {
        'en': 'English', 'uk': 'Ukrainian', 'de': 'German', 'fr': 'French', 'es': 'Spanish', 'ru': 'Russian',
        'it': 'Italian', 'zh': 'Chinese', 'ja': 'Japanese'
    }
    if lang.lower() in lang_codes:
        return lang.lower()
    for code, name in lang_codes.items():
        if lang.lower() == name.lower():
            return code
    raise ValueError("Невірний код або назва мови")


def main():
    config_file = 'config.txt'  # Ім'я конфігураційного файлу
    config = read_config(config_file)

    if not config:
        return

    text_file = config.get('text_file')
    target_language = config.get('target_language')
    output = config.get('output')
    char_limit = int(config.get('char_limit', 1000))
    word_limit = int(config.get('word_limit', 200))
    sentence_limit = int(config.get('sentence_limit', 10))

    print(f"Назва файлу: {text_file}")

    text, num_chars, num_words, num_sentences = read_text_file(text_file, char_limit, word_limit, sentence_limit)

    if not text:
        print("Помилка: текст не зчитано.")
        return

    print(f"Розмір файлу: {os.path.getsize(text_file)} байт")
    print(f"Кількість символів: {num_chars}")
    print(f"Кількість слів: {num_words}")
    print(f"Кількість речень: {num_sentences}")

    detected_lang_code, confidence = LangDetect(text)
    if detected_lang_code:
        detected_lang = CodeLang(detected_lang_code)
        print(f"Визначена мова: {detected_lang}, Впевненість: {confidence:.2f}%")
    else:
        print("Не вдалося визначити мову.")

    translated_text = TransLate(text, target_language)

    if output == 'screen':
        print(f"Переклад на {CodeLang(target_language)}:")
        print(translated_text)
    elif output == 'file':
        output_file = 'translated_text.txt'
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(translated_text)
        print(f"Перекладений текст збережено у {output_file}")



main()
