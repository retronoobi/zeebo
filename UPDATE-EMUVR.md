# Port EmuVR baseado em 0.4.2

Atualização de 11/10/2026 em pasta separada, preservando a entrega 0.4.1.

Motor `src/` idêntico ao oficial 0.4.2. Inclui as correções upstream do relógio dos save states, limite acumulado de chamadas, desempenho do Dynarmic, formatação BREW, heap e renderização GL.

As adaptações do frontend 0.4.1 foram integradas por comparação de três versões: port anterior, base oficial anterior e base oficial nova. Mantidos lançadores `.zeebo`, caminhos relativos, catálogo, reset, splash e transições da Z-Wheel, composição completa RGB565, materialização explícita GL e retomada do contexto, cache de dpad_to_analog e cadência virtual de 60 Hz. Frameskip usa agora os tipos e o contador compartilhados da 0.4.2.

Mapeamento anterior preservado, Start/Select como HOME. Nenhuma sonda própria de mapeamento foi reintroduzida. Fast-forward, rewind, turbo e configurações por jogo continuam a cargo do frontend RetroArch; não foi adicionada interface de standalone.

Cargo.lock difere da base apenas pelas dependências serde/serde_json do frontend, já presentes no workspace oficial e nos avisos de terceiros. Não houve atualização de versões de dependências por iniciativa do port. A distribuição inclui LICENSE, LICENSE-GPL3 e THIRD-PARTY-NOTICES.txt oficiais. Compilação GNU mantém runtimes estáticos e remoção de símbolos internos.

Estados novos incluem a parcela de tempo ocioso corrigida pelo upstream; estados antigos sem ela mantêm a limitação anterior. Não se presume compatibilidade completa entre versões nem solução de netplay.

Os resultados de validação da entrega serão registrados abaixo.

## Entrega validada

Compilação release concluída: 12,868,096 bytes. SHA-256 `f19b252f68dc7bbc29355954d7e9fbdb5f841a99dd168b7134169198cef3ccc3`. ABI 1, 25 exports, extensões mod|zip|7z|zeebo. Dependências importadas apenas do Windows/UCRT; sem DLL externa de runtime GCC. DLL conferida sem INPUT-TRACE. Entrega 0.4.1 preservada e hash conferido.

Suíte do frontend: 18 testes passaram e um ignorado; os testes condicionais de ROM retornam sem executar quando suas variáveis não são fornecidas. O teste ignorado de splash foi executado separadamente com Z-Wheel e Double Dragon e passou.

Host WGL: 600 chamadas por conteúdo; Z-Wheel via .zeebo, Double Dragon e Boia Cross passaram, incluindo reset e cache/mudança de opções. Áudio acumulado: 9,999 s, 10,007 s e 7,537 s respectivamente (Boia inclui abertura). Z-Wheel conferida visualmente em quadro completo 640x480. Resultados equivalentes aos registrados no port 0.4.1.

Não foi feita validação manual no EmuVR, teste longo de Ridge Racer, nem cobertura de todos os jogos corrigidos. A correção de relógio dos save states foi incorporada do upstream, sem teste específico dela nesta entrega.

## Preparação para publicação

Scripts e host WGL tornados autossuficientes, README do fork e exemplo público adicionados. Workflows originais arquivados em docs/upstream-workflows; somente emuvr-windows.yml fica ativo. Motor e lógica do frontend preservados. Novo script compilou localmente; pacote passou na ABI e na lista de dependências, incluindo licenças dos runtimes estáticos. YAML e sintaxe PowerShell verificados. Workflow ainda não executado no GitHub. A recompilação de preparação tem SHA256 0eb6b289582712a897c5aa797c33e84e1dab126b0bc0d60274204e46ba926c81; entrega anterior permanece em entrega/.
