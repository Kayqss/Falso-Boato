# Automação de Cortes & Publicação de Shorts

Aplicação desktop em Python projetada para automatizar o fluxo completo de canais de cortes e vídeos curtos (TikTok, YouTube Shorts e Instagram Reels). 

O sistema elimina o trabalho repetitivo de edição manual: ele recebe gravações brutas ou lives, extrai os melhores trechos, adapta a proporção de tela para o formato vertical (9:16) com sobreposição de webcam e publica os clipes prontos nas redes de forma programada.

---

## Principais Módulos

### 1. Recorte com Inteligência Artificial
- Análise multimodal de vídeo através da API do Google Gemini.
- Identificação contextual dos momentos mais relevantes (reações, jogadas, momentos cômicos, falhas e sustos).
- Geração automática de títulos e legendas no estilo hook em caixa alta.
- Redução automática de arquivos pesados via proxy temporário para acelerar o envio e minimizar custos de API.
- Painel financeiro com cálculo de tokens consumidos e abatimento de saldo da fatura em tempo real.

### 2. Recorte Simples e Manual
- Fatiamento linear de gravações longas em partes com duração configurada em segundos.
- Titulação sequencial automática estampada diretamente na mídia (ex.: Parte 1, Parte 2, Parte Final).
- Preservação da fidelidade de áudio e aceleração via hardware/FFmpeg com libx264.

### 3. Engine de Edição & Layout Streamer
- Conversão de mídia 16:9 em formato vertical 9:16 (1080x1920).
- Calibração de câmera no próprio painel com guias visuais em tempo real (posição X/Y, largura e altura).
- Diagramação com webcam no terço superior, gameplay centralizada e card flutuante renderizado dinamicamente via Pillow.
- Aplicação de assinatura (@handle) configurável no rodapé de cada vídeo.

### 4. Publicação & Postagem Automática
- Módulo de agendamento e envio direto dos vídeos processados para as plataformas de vídeo curto.
- Metadados automáticos: aplicação de descrição, títulos gerados e tags correspondentes.
- Fila de postagem autônoma para manter frequência consistente sem intervenção manual.

---

## Pré-requisitos

1. **Python 3.10** ou superior instalado no sistema.
2. **FFmpeg** configurado nas variáveis de ambiente (`PATH`).
3. Chave de API do **Google Gemini** gerada no Google AI Studio.
4. Credenciais de API das redes sociais configuradas no módulo de postagem.
