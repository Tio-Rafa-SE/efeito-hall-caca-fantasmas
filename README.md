# Fantasma 5: Caça-Fantasmas com Efeito Hall

Projeto publicado na revista **Mecatrônica Jovem nº 16**, como uma versão atualizada do projeto original do professor **Newton C. Braga**. Autor: **Tio Rafa**. Um Arduino lê o campo magnético com o módulo **KY-024**, acende LED e buzzer quando o campo passa de um limite e desenha o valor em um gráfico em tempo real.

O sensor não encontra fantasmas de verdade: ele mede campos magnéticos (ímãs, alto-falantes, motores). O "fantasma" é o campo invisível, e o projeto serve para enxergar o que os olhos não veem.

## O que tem aqui

```text
efeito-hall-caca-fantasmas/
├── arduino/Hall/Hall.ino      sketch do Arduino UNO
├── python/hall_plotter.py     gráfico em tempo real (Tkinter + Matplotlib)
├── requirements.txt           dependências do Python
└── README.md
```

## Hardware

| Item | Observação |
|---|---|
| Arduino UNO R3 | O sketch foi escrito para o UNO (pinos PWM 3, 5, 6, 9, 10 e 11) |
| Módulo KY-024 | Sensor Hall linear 49E + comparador LM393. Pinos: A0, G, +, D0 |
| 2 LEDs + resistores | Resistor de 220 a 470 ohms em cada LED |
| Buzzer ativo | Liga com nível alto no pino |
| Ímã | Qualquer um serve; os de neodímio são os mais sensíveis |

## Ligações

| Peça | Pino do Arduino |
|---|---|
| KY-024 A0 | A0 |
| KY-024 D0 | D9 |
| KY-024 + | 5V |
| KY-024 G | GND |
| LED de alerta (digital) | D13 |
| LED de brilho (PWM) | D6 |
| Buzzer | D7 |

O catodo dos LEDs e o outro terminal do buzzer vão ao GND, junto com o GND do módulo.

## Como gravar o Arduino

1. Abra `arduino/Hall/Hall.ino` na Arduino IDE.
2. Em **Ferramentas > Placa**, escolha **Arduino UNO**; em **Porta**, escolha a do seu Arduino.
3. Clique em **Carregar**.
4. Abra **Ferramentas > Plotter Serial** (9600 baud) e aproxime o ímã.

## Como rodar o gráfico em Python

```bash
pip install -r requirements.txt
python python/hall_plotter.py                      # procura a porta sozinho
python python/hall_plotter.py --porta COM3         # Windows
python python/hall_plotter.py --porta /dev/ttyACM0 # Linux
```

Antes de rodar, feche o Monitor Serial e o Plotter Serial da Arduino IDE: só um programa usa a porta por vez.

No Linux, o Tkinter pode vir separado: `sudo apt install python3-tk`.

Para ter um banner no topo da janela, coloque uma imagem chamada `cabecalho.png` ao lado do `hall_plotter.py`. Sem ela, o programa roda normalmente.

## Resultado esperado

1. Sem ímã por perto, o LED de alerta e o buzzer ficam desligados.
2. Ao aproximar o ímã do sensor, o valor bruto sai do valor de repouso, a linha rosa sobe e o LED de brilho acende mais forte.
3. Quando o campo passa do limite do trimpot, o LED de alerta acende e o buzzer toca.
4. No Plotter Serial e no `hall_plotter.py` aparecem duas curvas: bruto (verde) e mapeado (rosa).

## Calibração

A faixa `LEITURA_MINIMA = 390` e `LEITURA_MAXIMA = 820` do `Hall.ino` veio dos testes do artigo. Cada módulo é um pouco diferente: olhe o valor bruto no Plotter Serial com e sem ímã e ajuste esses dois números. O sensor responde também à **polaridade**: inverter o ímã leva o valor para o outro lado do repouso.

Se o LED e o buzzer ficarem ligados sem ímã, mude `NIVEL_D0_DETECTANDO` para `LOW` (alguns módulos usam nível baixo ao detectar) ou gire o trimpot do módulo.

## Problemas comuns

| Sintoma | O que verificar |
|---|---|
| Nada no gráfico | Porta e velocidade (9600), e se o Plotter Serial da IDE está fechado |
| Valor preso em 0 ou 1023 | Ligação do 5V, do GND e do A0 |
| Buzzer sempre ligado | `NIVEL_D0_DETECTANDO` e trimpot |
| LED de brilho só liga e desliga | O LED precisa estar em um pino PWM (D6) |

## O que mudou em relação à versão da revista

- `ledD` não existia no código antigo e a compilação falhava. Agora há `PINO_LED_ALERTA` (D13) e `PINO_LED_BRILHO` (D6).
- `analogWrite()` recebe 0 a 255, mas o código antigo mandava até 1023. Agora o valor é dividido por 4.
- O pino 13 do UNO não tem PWM, então o LED de brilho passou para o pino 6.
- `constrain()` segura a leitura na faixa de calibração antes do `map()`.
- O `delay(100)` virou temporização com `millis()`.
- O Python não fixa mais `COM3`, não depende de um caminho do computador do autor e lê todas as linhas que chegaram, para o gráfico não atrasar.

## Validação

- Análise do código: feita.
- Sintaxe do sketch: verificada com um compilador C++ e um `Arduino.h` simulado. **Não** foi compilado com o core real da Arduino IDE.
- Lógica do Python: testada com serial e Tkinter simulados.
- Teste em hardware: **PENDENTE**.

## Créditos

Projeto original do detector magnético: professor Newton C. Braga. Esta é uma versão atualizada, publicada na revista Mecatrônica Jovem nº 16. Artigo e código: Tio Rafa.
