# Сборка и запуск корпуса в docker #

## Сборка корпуса ##

- Один раз надо создать docker образ с помощью команды:

```
cd docker/index
docker build -t manatee-index .
```

- При получении новых файлов надо запускать docker container c подключением директорий, detcorpus и detcorpus-build:

```
docker run -v [путь на конретной машине]/detcorpus:/home/detcorpus -v [путь на конкретной машине]/detcorpus-build:/home/detcorpus-build  manatee-index
```

## Запуск веб сервера с построенным индексом ##

- Создаем docker образ:

```
cd docker/web
docker build -t manatee-web .
```

- Запускаем его и делаем доступным на 80 порту

```
docker run -p 80:80 -v [путь до сборочной директории]detcorpus-build/export:/var/lib/manatee -d manatee-web
```

Контайнер запустится в detached режиме и к нему можно будет подключиться командой:

```
docker exec -it [имя контейнерa] /bin/bash
```

