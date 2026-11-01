# infrastructure

Ansible playbooks for the remaining infrastructure: web/Docker services,
host bootstrap and package maintenance.

Services managed by separate projects:

- [MegaProxyServer](https://github.com/andre487/MegaProxyServer): HTTPS/SSH proxies, chains, users and client configuration exports.
- [MegaTgProxyServer](https://github.com/andre487/MegaTgProxyServer): Telegram MTG/MTProxy servers and SSH egress.
- [ClamavMirror487](https://github.com/andre487/ClamavMirror487): ClamAV database mirror, Caddy HTTPS, updates and optional DNS publication.

Keep migrated hosts and credentials in those projects' inventories. Do not reintroduce
them into infrastructure-wide provisioning or maintenance groups. Shared Docker,
nginx, firewall and security roles remain for other services.
