# Port EmuVR sobre Zeebx 0.4.3

Atualização de 22/10/2026, em pasta própria. A versão anterior permanece em `old/zeebx-original-emuvr-0.4.2`.

## Integração

- Motor `src/` idêntico ao oficial 0.4.3. A correção local limitada da água foi substituída pelo combinador oficial, com fontes das duas unidades de textura; o teste local foi adaptado à nova API.
- Preservados lançadores .zeebo, catálogo, caminhos relativos e separação entre lançador e pacote real.
- Preservadas apresentação RGB565 completa, materialização GL, recuperação do contexto, splash pelo overlay do VFS e ordem da transição do Z-Wheel.
- Preservada integralmente a compensação de cadência/áudio do Boia Cross. O usuário confirmou que o problema ainda ocorre no core oficial 0.4.3; não removemos a compensação baseada no relógio virtual.
- Mapeamento anterior, Start/Select=HOME e cache de dpad_to_analog preservados. O motor novo acrescenta a compatibilidade HOME/Quake e corrige a soltura BREW; não há remapeamento dos botões de ação por jogo.
- Incorporadas as correções oficiais de save states, apresentação GL, Alice, Ultimate Chess e Rally Master Pro.
- Workflow EmuVR, verificação de ABI, runtimes estáticos e símbolos internos removidos preservados. O comando auxiliar `standalone` agora verifica `zeebx-cli`, pois o pacote egui foi removido pelo upstream.
- Nenhuma instrumentação de mapeamento ou captura de desenhos foi importada da árvore de diagnóstico.

O lock e os avisos de terceiros são os da 0.4.3. O lock só acrescenta ao pacote libretro as dependências serde e serde_json já existentes no workspace, sem trocar ou acrescentar versões de bibliotecas. A conferência automática dos avisos não pôde ser executada porque cargo-about 0.9.2 não está instalado; o arquivo de avisos oficial foi preservado integralmente.

## Limites

A reconstrução oficial do áudio ao restaurar estados não é reprodução exata de toda a posição do mixer: loops podem recomeçar e sons sem cache podem aguardar nova reprodução. Não há nova promessa de determinismo, compatibilidade integral entre estados de versões diferentes ou solução do consumo de RAM em netplay.

Testes isolados não substituem a avaliação manual no EmuVR, especialmente do áudio durante a corrida e do ciclo interativo do Z-Wheel.

## Validação da entrega

- Build release Windows x64 concluído. 20 testes comuns passaram; um teste opcional de splash foi executado separadamente com Z-Wheel e Double Dragon e também passou. Os testes condicionais da suíte que exigem ZEEBX_CORE_ROM retornam sem ROM; não representam execução adicional de jogos.
- Host WGL: Z-Wheel por .zeebo e Double Dragon, 600 chamadas cada, com reset. Boia Cross por ZIP, 600 e 1.200 chamadas, com reset. Todas as execuções passaram, incluindo uso do contexto GL pelo host entre chamadas e atualização/cache das opções do analógico.
- Z-Wheel: captura completa, com 150.464 pixels não pretos na metade inferior. Teste separado confirmou splash do overlay herdado na troca de applet; simula a troca de arquivo do guest e não automatiza toda a navegação interativa.
- Boia Cross: 7,537 s de áudio em 600 chamadas e 17,520 s em 1.200, diferença de 9,983 s para as 600 adicionais. As transições iniciais apresentam quadros sem avanço virtual. Medição consistente com a cadência anterior; não é avaliação auditiva da corrida.
- ABI 1, 25 exports, extensões mod|zip|7z|zeebo e dependências Windows/UCRT verificadas. O verificador do upstream foi adaptado para reconhecer a extensão do port.
- DLL: 12.894.208 bytes; SHA-256 `29591d3d180fd89246bb97824e62a3feeb8d274fd517086b6d1f6f768a3b0f20`.
- Avisos de compilação restantes: três variáveis estáticas de áudio do upstream e o campo gl do apresentador, sem erros de compilação.

Não foram executados testes de netplay, corridas completas ou compatibilidade de estados entre versões.
