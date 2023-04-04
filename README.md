# Definitieve Overheids Organisatie Register

Momenteel Gemeenten en provincies op bases van door het CBS beschikbaar gestelde open data. Het resultaat is een lijst van gemeenten en provincies met begin- end einddatum (voor zover bekend).

## installatie

Docker dient geinstalleerd te zijn.
```
./bin/dev.sh
```

## gebruik

In je cron kan je iets als het volgende stoppen:
```
5 5 * * * docker exec door_shell_1 ./bin/update.sh
```
Resulterende bestanden komen in de `html/` map. Die zou je met iets als nginx kunnen delen, als nodig.

## contact

Breyten Ernsting <breyten@openstate.eu>
