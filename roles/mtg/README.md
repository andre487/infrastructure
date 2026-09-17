# MTG

Роль использует SSH SOCKS для выхода в интернет. Все параметры развёртывания,
включая настройки Docker-сети, адрес и порты SSH-прокси и пользователя,
задаются внутри `ansible-inventory.yml` внешнего inventory: общие — в
`tg_proxies.vars`, индивидуальные — в `tg_proxies.hosts` под нужным хостом.
В infrastructure хранятся только задачи и шаблоны.

Учётные записи выходных SSH-прокси управляются через MegaProxyServer и его
inventory; путь к inventory записан в `inventory-path` того проекта.

Приватный ключ туннеля хранится в переменной `mtg_ssh_private_key` внешнего
inventory как значение `!vault`. Роль доставляет его на сервер MTG в
`/etc/mtg/ssh/id_ed25519` с правами `0600`. Публичная часть той же пары хранится
в inventory MegaProxyServer у соответствующего SSH-пользователя. При замене
пары сначала примените публичный ключ на выходном SSH-прокси, затем приватный
на сервере MTG.

Для расшифровки используйте `ANSIBLE_VAULT_PASSWORD_FILE` или `--ask-vault-pass`.
Проверка host key выходного прокси отключена; смена ключа сервера не требует
обновления inventory.

Применение с путём к inventory в `INFRASTRUCTURE_INVENTORY`:

```sh
bin/ansible-playbook tg-proxy.yml --tags tg-proxy
```

Проверка SSH-туннеля на сервере MTG:

```sh
sudo systemctl status mtg-ssh-egress
sudo journalctl -u mtg-ssh-egress --since '10 minutes ago'
```
