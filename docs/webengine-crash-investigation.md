# Diagnóstico de crashes do QtWebEngine

Este procedimento investiga SIGSEGV no processo principal durante despacho de
eventos. Não presume que `WebView.event -> super().event` identifique um gesto,
nem que dois fingerprints iguais comprovem a mesma causa raiz. Crashes de
renderer, vídeo/GPU, navegação reentrante e shutdown são grupos separados.

## Relatório por sessão

O marcador JSON `.session-active` guarda o ambiente sanitizado, PID local,
identificador local da sessão, variante A/B, fase e posição inicial do
faulthandler. Ele só começa depois que `SingleApplication` aceita esta execução
como instância principal; um segundo lançamento não sobrescreve a sessão viva.
O marcador permanece durante `aboutToQuit` e o fallback de teardown e só é
removido ao completar esse fluxo. Não cobre uma falha anterior à construção da
aplicação, nem garante detectar uma falha na finalização do interpretador após
`main()` retornar.

Na próxima inicialização, somente o último registro fatal depois da posição
salva entra no relatório. A leitura é limitada a 64 KiB. Log ausente, rotacionado,
truncado, registro cortado ou marcador legado resulta em evidência desconhecida;
nunca se usa o histórico antigo para preencher essa lacuna. O ambiente da
execução seguinte não substitui o ambiente desconhecido da execução anterior.
O parâmetro legado `logs_provider` continua disponível para testes/integradores;
a aplicação usa o caminho e offset do arquivo, sem ler o histórico inteiro.

`fingerprint_version=2` distingue sinal, componente e até cinco frames de
aplicação da thread explicitamente marcada como atual. Números de linha,
endereços, diretórios de instalação e frames de workers ficam de fora.
`runtime_fingerprint` acrescenta Qt carregado, WebEngine, Chromium, PyQt,
PyQt-WebEngine e SIP. O componente é uma classificação da fronteira Python;
não identifica a instrução C++ fatal. Evidência sem frames/sinal permanece
`unknown` e não justifica consolidação automática de issues.

## Instrumentação opt-in

`ZAPZAP_WEBENGINE_TRACE=1` habilita JSONL local em
`crash-dumps/webengine-<sessão>.jsonl`. O probe usa append sem buffer antes da
chamada C++, com entrada/saída, profundidade, tipo do evento, gesto quando
disponível, estado de shutdown, callbacks, timers, associação/descarte de páginas
e signals `destroyed`. IDs de objetos são contadores locais, não IDs de contas.
Não consulta `page()`, `profile()`, título, URL, JavaScript, mensagens ou contatos
para gerar logs. `page()` poderia criar uma página e alterar o experimento.

Cada segmento tem até 4 MiB, com um segmento anterior por sessão e retenção de
até seis arquivos. A cauda de até 16 KiB da sessão que caiu pode entrar no
relatório sanitizado/revisável. Os arquivos JSONL completos continuam locais;
nada é enviado automaticamente. A gravação não faz `fsync` por evento: serve
para morte do processo, não garante persistência após perda de energia.
Falha de I/O desativa o probe sem alterar o resultado do despacho.

Instrumentação muda timing e pode mascarar races. Compare também execuções sem
trace; ausência de crash em poucos minutos não comprova estabilidade.

## Variantes A/B

O launcher usa somente biblioteca padrão no host; não instala dependências.
Ele roda o **código do checkout**, com as bibliotecas do Flatpak instalado,
sem compilar, atualizar, instalar nem usar `flatpak override`.
Encerre a instância existente antes de cada execução; mantenha conta,
configurações, GPU, sandbox, plataforma Qt e carga constantes.

```bash
python3 tools/webengine_ab.py --variant baseline --dry-run
python3 tools/webengine_ab.py --variant baseline
python3 tools/webengine_ab.py --variant no-event-override
python3 tools/webengine_ab.py --variant consume-native-gestures
python3 tools/webengine_ab.py --variant baseline --trace
```

Não execute todos simultaneamente. O launcher define variáveis apenas para o
processo; nenhuma preferência é persistida. Ausência/valor inválido de
`ZAPZAP_WEBENGINE_EVENT_MODE` mantém `baseline`.

| Execução | Hipótese | Se os crashes desaparecem | Se continuam |
|---|---|---|---|
| Baseline sem trace | Taxa de referência | Estender observação antes de testar | Guardar frequência e assinatura |
| `no-event-override` sem trace | Override/trampoline participa | Repetir e comparar com baseline; pode ser timing | Qt continua sendo chamado; mudança do frame não conta como resolução |
| `consume-native-gestures` sem trace | Dependência de gesto nativo | Separar depois tipos/dispositivos; não publicar bloqueio amplo como correção | Enfraquece hipótese de gestos se a cobertura estiver confirmada |
| Baseline com trace | Tipo do evento e lifecycle | Pode ter mascarado timing | Buscar entrada sem saída e operações aninhadas, correlacionando com backtrace |
| Mesmo código em stack Qt coerente alternativo | Versão/empacotamento | Sustenta dependência do stack, ainda sem atribuir Qt versus PyQt | Investigar código/caminho comum |
| Baseline sob gdb | Instrução e objeto nativo fatal | Debugger pode mudar timing | Identifica a família nativa e threads envolvidas |

`no-event-override` remove o método da classe Python no import, antes de criar
views. Mantém o filtro global e o bloqueio de Zoom quando a preferência estiver
ativa. `consume-native-gestures` consome todos os NativeGesture na view e nos
descendentes cobertos pelo filtro, independentemente da preferência de pinch;
não bloqueia gestos em outras janelas. É exclusivamente diagnóstico.

Este checkout pode ser mais novo que 7.4.5. Não atribua um resultado obtido na
7.5 à 7.4.5. Para a regressão histórica, prepare a mesma instrumentação numa
base 7.4.5, valide a versão declarada e mantenha essa base em todos os A/B.
Comparar 7.4.4/7.4.5 exige depois fixar o mesmo stack e isolar commits como #892
e badge; nunca reverta a proteção de navegação em uma release para esse teste.

## Runtime e backtrace nativo

Guarde os relatórios das duas execuções, arquitetura, revisão do código,
commit do artefato Flatpak, commit do runtime e manifestos/builds da BaseApp:

```bash
git rev-parse HEAD
flatpak info com.rtosta.zapzap
flatpak info org.kde.Platform//6.11
flatpak info --show-metadata com.rtosta.zapzap
coredumpctl list --since "10 minutes ago"
coredumpctl info <PID>
coredumpctl debug <PID>
```

No gdb, use `thread apply all bt full` e `info sharedlibrary`. Capture SIGSEGV,
SIGABRT e SIGTRAP antes de continuar a execução; o faulthandler padrão não
cobre SIGTRAP. Use os símbolos e bibliotecas do artefato que caiu, incluindo
SIP/PyQt, Qt e WebEngine/Chromium. Um core do Flatpak interpretado somente com
bibliotecas do host pode produzir frames incorretos. Se não houver core, rode
sob gdb dentro de ambiente SDK compatível e reproduza a variante baseline.
Não use `--disable-sandbox` como parte da coleta.

Registre build IDs com `readelf -n` nas bibliotecas carregadas apontadas pelo
gdb. Nunca substitua `.so` isoladamente para testar versões: mantenha Qt,
WebEngine, PyQt/SIP, plugins e subprocesso WebEngine ABI-coerentes. Atualizar o
runtime compartilhado pode mudar outros aplicativos; prefira instalação/build
de teste isolado. O launcher não automatiza essa troca.

Backtraces `full` e cores podem conter dados pessoais, tokens e memória de
conversas. Revise a versão textual antes de publicar; não anexe um core bruto a
uma issue pública. Anote duração, ação imediatamente anterior, tipo de sinal,
PID/componente e se houve popup, troca de conta, hide/close ou shutdown.

## Critério de implementação

Só transformar um experimento em correção após repetição A/B e evidência do
evento ou lifecycle envolvido. Para lifecycle, exigir ordem observada de
`destroyed` de páginas/popups/DevTools antes do profile, callbacks pendentes e
ausência de reentrância problemática. Para upstream, reduzir a um reproducer
com versões/build IDs. Nenhuma dessas correções está implementada neste conjunto.
