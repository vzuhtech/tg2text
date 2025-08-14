## Telegram Voice-to-Text Bot (FastAPI + OpenAI)

Бот принимает голосовые сообщения в Telegram, распознаёт через OpenAI и отвечает текстом. Готов для деплоя на Railway.

### Локальный запуск

1. Создай `env.example` копированием в `.env` и укажи:
   - `TELEGRAM_BOT_TOKEN`
   - `OPENAI_API_KEY`
   - `APP_BASE_URL` (для вебхука в проде; локально можно оставить пустым)
   - `WEBHOOK_SECRET` (опционально)
2. Установи зависимости:
   ```bash
   pip install -r requirements.txt
   ```
3. Запусти сервер:
   ```bash
   uvicorn main:app --reload
   ```

Локально вебхук не нужен. Для теста можно использовать `ngrok` и задать `APP_BASE_URL`.

### Деплой на Railway

1. Запушь проект в GitHub.
2. В Railway создай новый проект из репозитория.
3. В Variables добавь:
   - `TELEGRAM_BOT_TOKEN`
   - `OPENAI_API_KEY`
   - `APP_BASE_URL` = публичный домен Railway (например, `https://your-app.up.railway.app`)
   - `WEBHOOK_SECRET` (любая строка; защита вебхука заголовком)
4. Деплой. На старте приложение автоматически вызовет `setWebhook` на `APP_BASE_URL/webhook/telegram`.

### Команды

- `/start` — бот подскажет отправить голосовое сообщение.

### Примечания

- Поддерживаются `voice`, `audio`, `video_note` (файлы Telegram). Голосовые обычно `OGG/OPUS`.
- Для явного выбора языка добавь параметр в `transcribe_ogg_bytes`.