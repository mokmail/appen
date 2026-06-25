# BEV KI-Plattform

**KI-Plattform des Bundesamtes für Eich- und Vermessungswesen (BEV).**

Diese Webanwendung stellt den Mitarbeitenden des BEV eine selbst gehostete
KI-Umgebung mit lokalem RAG, Modellverwaltung und Werkzeugintegration zur
Verfügung. Sie basiert auf [Open WebUI](https://github.com/open-webui/open-webui),
wurde jedoch für den internen Einsatz am BEV angepasst und umgebrandet.

Weitere Informationen zur Behörde finden Sie unter
[bev.gv.at](https://bev.gv.at).

## Schnellstart mit Docker 🐳

```bash
docker run -d -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  --name open-webui --restart always \
  ghcr.io/open-webui/open-webui:main
```

Nach dem Start ist die Oberfläche unter
[http://localhost:3000](http://localhost:3000) erreichbar.

## Entwicklung

```bash
npm install
npm run dev
```

Für weitere Installations- und Konfigurationsmöglichkeiten siehe die
ursprüngliche Open-WebUI-Dokumentation im Upstream-Repository.

## Lizenz 📜

Dieses Projekt enthält Code unter mehreren Lizenzen. Die ursprünglichen
Open-WebUI-Komponenten stehen unter der Open WebUI License; detaillierte
Informationen finden Sie in [LICENSE](./LICENSE) und
[LICENSE_HISTORY](./LICENSE_HISTORY).