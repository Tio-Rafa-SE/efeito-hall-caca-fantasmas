// ========================================================
// Projeto : Caça-Fantasmas com Efeito Hall (Fantasma 5)
// Autor   : Tio Rafa - Revista Mecatrônica Jovem nº 16
// Origem  : versão atualizada do projeto original do prof. Newton C. Braga
// Placa   : Arduino UNO R3 (ATmega328P)
// IDE     : Arduino IDE
// Sensor  : módulo KY-024 (sensor Hall linear 49E + comparador LM393)
// ========================================================
//
// O que este programa faz:
//   1. Lê a saída analógica (A0) do KY-024: quanto mais forte o campo
//      magnético, mais o valor se afasta do "repouso".
//   2. Lê a saída digital (D0): vira "ativa" quando o campo passa do
//      limite ajustado no trimpot do módulo.
//   3. Liga o LED e o buzzer quando o D0 dispara.
//   4. Faz o brilho de um segundo LED acompanhar a intensidade do campo.
//   5. Envia "bruto,mapeado" pela Serial (uma linha a cada 100 ms) para o
//      Plotter Serial da Arduino IDE ou para o hall_plotter.py.
//
// Ligações (confira com o esquema do artigo):
//   KY-024  A0 -> A0      KY-024  D0 -> D9
//   KY-024  +  -> 5V      KY-024  G  -> GND
//   LED digital (com resistor) -> D13 (é também o LED "L" da placa)
//   LED de brilho (com resistor) -> D6  (PWM)
//   Buzzer ativo -> D7

// -------------------- Pinos --------------------
const uint8_t PINO_KY024_A0   = A0;  // saída analógica do módulo
const uint8_t PINO_KY024_D0   = 9;   // saída digital do módulo
const uint8_t PINO_LED_ALERTA = 13;  // acende quando o D0 dispara
const uint8_t PINO_LED_BRILHO = 6;   // precisa ser pino PWM (3, 5, 6, 9, 10 ou 11 no UNO)
const uint8_t PINO_BUZZER     = 7;

// -------------------- Ajustes --------------------
// Em alguns módulos o D0 fica em nível ALTO quando detecta; em outros, em BAIXO.
// Se o LED e o buzzer ficarem ligados SEM ímã por perto, troque HIGH por LOW.
const uint8_t NIVEL_D0_DETECTANDO = HIGH;

// Faixa observada no A0 durante os testes do artigo (repouso até ímã bem perto).
// Cada sensor é um pouco diferente: abra o Plotter Serial, aproxime e afaste
// o ímã e ajuste estes dois números para o SEU módulo.
const int LEITURA_MINIMA = 390;
const int LEITURA_MAXIMA = 820;

const unsigned long INTERVALO_MS = 100;  // tempo entre uma leitura e outra
const long VELOCIDADE_SERIAL = 9600;     // precisa ser igual no hall_plotter.py

// -------------------- Variáveis --------------------
unsigned long ultimoEnvio = 0;

void setup() {
  Serial.begin(VELOCIDADE_SERIAL);

  pinMode(PINO_KY024_D0, INPUT);
  pinMode(PINO_LED_ALERTA, OUTPUT);
  pinMode(PINO_LED_BRILHO, OUTPUT);
  pinMode(PINO_BUZZER, OUTPUT);

  // Começa com tudo desligado.
  digitalWrite(PINO_LED_ALERTA, LOW);
  digitalWrite(PINO_BUZZER, LOW);
  analogWrite(PINO_LED_BRILHO, 0);
}

void loop() {
  // millis() em vez de delay(): o Arduino não "dorme" entre as leituras.
  unsigned long agora = millis();
  if (agora - ultimoEnvio < INTERVALO_MS) {
    return;
  }
  ultimoEnvio = agora;

  int leituraBruta = analogRead(PINO_KY024_A0);  // 0 a 1023
  bool detectando = (digitalRead(PINO_KY024_D0) == NIVEL_D0_DETECTANDO);

  // Alerta digital: LED + buzzer.
  digitalWrite(PINO_LED_ALERTA, detectando ? HIGH : LOW);
  digitalWrite(PINO_BUZZER, detectando ? HIGH : LOW);

  // constrain() segura o valor dentro da faixa; sem ele o map() devolveria
  // números negativos ou maiores que 1023 fora da faixa de calibração.
  int leituraLimitada = constrain(leituraBruta, LEITURA_MINIMA, LEITURA_MAXIMA);
  int leituraMapeada  = map(leituraLimitada, LEITURA_MINIMA, LEITURA_MAXIMA, 0, 1023);

  // analogWrite() aceita 0 a 255, então dividimos por 4 (1023 / 4 = 255).
  analogWrite(PINO_LED_BRILHO, leituraMapeada / 4);

  // Formato "bruto,mapeado": o Plotter Serial desenha duas linhas.
  Serial.print(leituraBruta);
  Serial.print(",");
  Serial.println(leituraMapeada);
}
