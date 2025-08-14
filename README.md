## Telegram Voice-to-Text Bot (FastAPI + OpenAI)

Бот принимает голосовые сообщения в Telegram, распознаёт через OpenAI и отвечает текстом. Готов для деплоя на Railway.

### Локальный запуск

1. Создай `env.example` копированием в `.env` и укажи:
   - `TELEGRAM_BOT_TOKEN`
   - `OPENAI_API_KEY`
   - `OPENAI_ORG_ID` (опционально)
   - `OPENAI_PROJECT_ID` (опционально)
   - `APP_BASE_URL` (для вебхука в проде; локально можно оставить пустым)
   - `WEBHOOK_SECRET` (опционально)
   - `DEBUG=1` (опционально — выводит текст ошибки в ответе)
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
   - `OPENAI_ORG_ID` (если используешь Organizations)
   - `OPENAI_PROJECT_ID` (если используешь Projects)
   - `APP_BASE_URL` = публичный домен Railway (например, `https://your-app.up.railway.app`)
   - `WEBHOOK_SECRET` (любая строка; защита вебхука заголовком)
   - `DEBUG=1` (по желанию)
4. Деплой. На старте приложение автоматически вызовет `setWebhook` на `APP_BASE_URL/webhook/telegram`.

### Команды

- `/start` — бот подскажет отправить голосовое сообщение.

### Траблшутинг распознавания

- `429 insufficient_quota` — проверь платёжные данные и лимиты на `platform.openai.com`.
- Включи `DEBUG=1`, чтобы бот отвечал текстом ошибки (временно, не для продакшна).
- Проверь логи Railway → Deployments → Logs.
- Формат: Telegram `voice` — OGG/OPUS; поддержаны также `audio`, `video_note`.