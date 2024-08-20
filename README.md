# KV-storage_Tarantool
VK internship test task 

# Инструкция
* установите tt - Tarantool CLI utility
* клонируйте репозиторий
* создайте папку для проекта
* инициализируйте среду с помощью tt init
* переместите папки data_cluster и user_cluster в папку instances.enabled/
* соберите образы с помощью tt build data_cluster и tt build user_cluster
* запустите их tt start
* подключитесь к роутерам и иницилизируйте шардирование в кластере 
  * tt connect user_cluster:user_router-a-001
  * vshard.router.bootstrap()
  * tt connect data_cluster:data_router-a-001
  * vshard.router.bootstrap()
* запустите сервер uvicorn python -m uvicorn main:app --reload 
* Готово!
### PS
Проект очень интересный и он будет закончен в скором времени ;)
