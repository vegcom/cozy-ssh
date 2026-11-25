# cozy-ssh

```plain
   ╭────────────────────────────────────────╮
   │ cozy‑share — a warm little ssh_config  │
   ╰────────────────────────────────────────╯
                   (^-^)
                          ✧
                         ✧ ✧     Q(-_-q)
                       ✧  ✧  ✧
                         ✧ ✧
                          ✧
           (づ｡◕‿‿◕｡)づ
```

## TODO

Make a good readme

## Reference

### Version

Requires >=OpenSSH 9.6

- [openssh.org/releasenotes](https://www.openssh.org/releasenotes.html)
  - [release-9.6](https://www.openssh.org/txt/release-9.6)

#### Windows

- [PowerShell/openssh-portable](https://github.com/PowerShell/openssh-portable)

```pwsh
# SSH Agent - as superuser
Get-Service ssh-agent | Set-Service -StartupType Automatic
Start-Service ssh-agent
```

### Tokens (preffer docse)

|Token|Meaning|
|-|-|
|%h|Host name from the Host line in your SSH config (after alias resolution)|
|%n|Original hostname as given on the command line (before alias resolution)|
|%p|Port number|
|%r|Remote username|
|%u|Local username|
|%l|Local hostname|
|%L|Local hostname (without domain)|
|%d|Local user's home directory|
|%C|A hash of %l%p%h%r — useful for unique socket paths in ControlPath|

## Games / CI

- Dungeon Crawl Stone Soup
  - [crawl.akrasiac.org](https://crawl.akrasiac.org/)
  - [cao_key](https://crawl.akrasiac.org/cao_key)
