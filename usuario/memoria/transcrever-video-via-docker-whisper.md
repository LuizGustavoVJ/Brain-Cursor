---
name: transcrever-video-via-docker-whisper
description: "Como transcrever vídeo/áudio nesta máquina: não há ffmpeg nem whisper no host; usar a imagem docker do Playwright (ffmpeg embutido) + faster-whisper"
metadata:
  type: reference
---

**18/08/2026** — O host **não tem** ffmpeg, ffprobe, whisper, pip nem numpy/cv2. Receita que funcionou para transcrever uma gravação de reunião (26 min):

1. **ffmpeg vem de graça** na imagem `mcr.microsoft.com/playwright:v1.61.1-jammy` (já baixada) — `/usr/bin/ffmpeg` e `/usr/bin/ffprobe`.
2. **Docker Desktop só monta paths sob `/home/luizfinotello`** — montar `/tmp/...` (inclusive o scratchpad da sessão) falha com *"path is not shared from the host"*. Usar `~/.cache/<algo>` como diretório de trabalho.
3. Extrair áudio: `docker run --rm --user "$(id -u):$(id -g)" -v "<pasta-video>":/in:ro -v "$O":/out --entrypoint ffmpeg <img> -i /in/video.mp4 -vn -ac 1 -ar 16000 -c:a pcm_s16le /out/audio.wav`
4. Transcrever: no mesmo container, `HOME=/cache`, instalar pip via `get-pip.py --user` e `pip install --user faster-whisper`; modelo `small`, `compute_type="int8"`, `cpu_threads=14`, `language="pt"`, `vad_filter=True`. ~26 min de áudio ≈ **8 min** de CPU. Modelo (~460 MB) fica cacheado em `download_root`.
5. Rodar em background (`nohup ... &`) e acompanhar o `.log`; o script grava linha a linha com timestamp.
6. Frames do vídeo (`-vf fps=1/60`) só valem quando há tela compartilhada com conteúdo novo — numa reunião de leitura de cards do ADO o valor está **no áudio**.

Relacionado: [[cartao-credito-pagarme-fase1]], [[verificar-antes-de-deduzir]].
