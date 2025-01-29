# Foodgram
## Описание
Foodgram — это веб-платформа для публикации и поиска кулинарных рецептов, на которой пользователи могут публиковать свои собственные рецепты, а также добавлять рецепты других пользователей в избранное или список покупок. Кроме того, существует возможность скачать список продуктов, необходимых для выбранных рецептов.
## Запуск
Клонируйте репозиторий
```
git clone git@github.com:TheWeeper/foodgram-st.git
```
Перейдите в директорию ```infra```, создайте файл ```.env``` и заполните его на примере ```.env.example```
```
cd foodgram-st/infra/
touch .env
```
Запустите проект
```
docker compose up
```
Выполните миграции
```
docker exec foodgram-backend python manage.py migrate.py
```
Загрузите ингредиенты в базу данных
```
docker exec foodgram-backend python manage.py load_inredients ingredients.json
```
