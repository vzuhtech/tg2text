## Telegram Voice-to-Text Bot (FastAPI + OpenAI/Vosk)

Бот принимает голосовые сообщения в Telegram и отвечает текстом. Поддерживаются два провайдера распознавания: OpenAI (облако) и Vosk (бесплатно/офлайн).

### Локальный запуск

1. Скопируй `env.example` в `.env` и укажи:
   - `TELEGRAM_BOT_TOKEN`
   - Провайдер STT:
     - OpenAI: `STT_PROVIDER=openai`, `OPENAI_API_KEY` (+ при необходимости `OPENAI_ORG_ID`, `OPENAI_PROJECT_ID`)
     - Vosk: `STT_PROVIDER=vosk`. Модель может скачиваться автоматически:
       - `VOSK_MODEL_URL` — URL архива модели (`.zip` или `.tar.gz`), по умолчанию русская small
       - `VOSK_MODEL_SHA256` — опционально, контрольная сумма
       - `VOSK_STORAGE_DIR` — куда класть модели (по умолчанию `/app/models`)
       - `VOSK_MODEL_PATH` — опционально, итоговый путь модели (если не задан, будет `/app/models/vosk-model`)
       - `FFMPEG_BIN` — путь к ffmpeg (по умолчанию `ffmpeg`)
   - `APP_BASE_URL` (для вебхука в проде; локально можно пустым)
   - `WEBHOOK_SECRET` (опционально)
   - `DEBUG=1` (опционально для подробных ошибок)
2. Установка зависимостей:
   ```bash
   pip install -r requirements.txt
   ```
3. Запуск:
   ```bash
   uvicorn main:app --reload
   ```

### Деплой на Railway

- Для OpenAI: стандартные переменные (`STT_PROVIDER=openai`, ключи OpenAI, `APP_BASE_URL`).
- Для Vosk (автоскачивание):
  - `STT_PROVIDER=vosk`
  - (опц.) `VOSK_MODEL_URL`, `VOSK_MODEL_SHA256`, `VOSK_STORAGE_DIR`, `VOSK_MODEL_PATH`
  - `FFMPEG_BIN=ffmpeg`
  - При старте модель скачается и распакуется в указанную директорию. `nixpacks.toml` уже устанавливает `ffmpeg`.

### Команды
- `/start` — бот подскажет отправить голосовое сообщение.

### Траблшутинг
- OpenAI `429 insufficient_quota` — проверь план/биллинг.
- Vosk — смотри логи старта: сообщение `Vosk model ready at ...`. Если ошибка — проверь URL/сумму/доступность `ffmpeg`.