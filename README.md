## Telegram Voice-to-Text Bot (FastAPI + OpenAI/Vosk)

Бот принимает голосовые сообщения в Telegram и отвечает текстом. Поддерживаются два провайдера распознавания: OpenAI (облако) и Vosk (бесплатно/офлайн).

### Локальный запуск

1. Скопируй `env.example` в `.env` и укажи:
   - `TELEGRAM_BOT_TOKEN`
   - Провайдер STT:
     - OpenAI: `STT_PROVIDER=openai`, `OPENAI_API_KEY` (+ при необходимости `OPENAI_ORG_ID`, `OPENAI_PROJECT_ID`)
     - Vosk: `STT_PROVIDER=vosk`, `VOSK_MODEL_PATH` (путь к распакованной модели), `FFMPEG_BIN` (если не в PATH)
   - `APP_BASE_URL` (для вебхука в проде; локально можно пустым)
   - `WEBHOOK_SECRET` (опционально)
   - `DEBUG=1` (опционально для подробных ошибок)
2. Установка зависимостей:
   ```bash
   pip install -r requirements.txt
   ```
3. Модель Vosk (пример для русского):
   - Скачай модель, например `vosk-model-small-ru-0.22` с `https://alphacephei.com/vosk/models`
   - Распакуй и укажи путь к папке модели в `VOSK_MODEL_PATH`
4. Запуск:
   ```bash
   uvicorn main:app --reload
   ```

### Деплой на Railway

- Для OpenAI: достаточно стандартных переменных (`STT_PROVIDER=openai`, ключи OpenAI, `APP_BASE_URL`).
- Для Vosk: добавь переменные `STT_PROVIDER=vosk`, `VOSK_MODEL_PATH=/app/models/vosk`, и положи модель в репозиторий или загружай на старте (см. ниже). В проект уже добавлен `nixpacks.toml`, который устанавливает `ffmpeg`.

#### Как положить модель Vosk на Railway
- Вариант простой: добавить папку модели в репозиторий (большой размер!) и выставить `VOSK_MODEL_PATH` на неё.
- Вариант экономный: на старте скачивать и распаковывать модель (нужно добавить код/скрипт скачивания и кэшировать в volumes). Могу добавить авто-скачивание при старте.

### Команды
- `/start` — бот подскажет отправить голосовое сообщение.

### Траблшутинг
- `429 insufficient_quota` — для OpenAI проверь план/биллинг.
- Для Vosk убедись, что установлен `ffmpeg` (в Railway ставится через `nixpacks.toml`), `VOSK_MODEL_PATH` корректен, и модель распакована.