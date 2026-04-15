# X. Aceleração por GPU na Fedora 42 com Secure Boot

## O problema

Ao executar a primeira célula do `mlp_heartbeat_v2.ipynb`, três mensagens
apareciam no `stderr`:

```
WARNING: All log messages before absl::InitializeLog() is called are written to STDERR
I0000 port.cc:153] oneDNN custom operations are on...
I0000 cudart_stub.cc:31] Could not find cuda drivers on your machine, GPU will not be used.
```

A terceira — "Could not find cuda drivers" — indicava que o TensorFlow
carregava em modo CPU-only. Em hardware com NVIDIA RTX 4070 Laptop
disponível, a execução sem GPU representa desperdício mensurável: o treino
de 50 épocas sobre 87 mil batimentos toma vários minutos em CPU e segundos
em GPU. A mensagem era, portanto, um sinal legítimo de ausência de
aceleração — não um alerta informativo ignorável.

## Diagnóstico

O `lspci` confirmou que a máquina possui duas GPUs:

```
0000:00:02.0 VGA compatible controller: Intel Corporation Raptor Lake-S UHD Graphics
0000:01:00.0 VGA compatible controller: NVIDIA Corporation AD106M [GeForce RTX 4070 Max-Q / Mobile]
```

A NVIDIA está presente mas o TensorFlow não a enxergava. As causas
possíveis eram três: driver NVIDIA ausente, driver presente mas módulo
kernel não assinado sob Secure Boot ativo, ou driver funcional mas
bibliotecas CUDA (cuDNN, cuBLAS, cuFFT, etc.) ausentes do `LD_LIBRARY_PATH`
do TensorFlow.

A inspeção revelou:

1. **Driver NVIDIA instalado**: pacotes `akmod-nvidia-580.126.18` e
   `xorg-x11-drv-nvidia-cuda-580.126.18` presentes.
2. **Módulo kernel compilado**: `nvidia.ko.xz` em
   `/lib/modules/$(uname -r)/extra/nvidia/` desde 19 de fevereiro.
3. **Secure Boot ativo**: `mokutil --sb-state` retornou "SecureBoot enabled".
4. **Chave assinadora já enrollada**: `mokutil --test-key` confirmou que
   `/etc/pki/akmods/certs/amoena_1764988624_7082c2a8.der` estava enrollada
   no MOK. O módulo `nvidia.ko.xz` foi assinado com essa mesma chave
   (`modinfo` reportou `signer: amoena_1764988624_7082c2a8`).
5. **Módulo carregado e funcional**: `lsmod | grep nvidia` listou cinco
   módulos ativos (`nvidia`, `nvidia_uvm`, `nvidia_modeset`, `nvidia_drm`,
   `nvidia_wmi_ec_backlight`), e `nvidia-smi` reportou a RTX 4070 com 8 GB
   de memória disponível.

Ou seja: o driver estava instalado, assinado, carregado e operacional. A
falha de detecção residia no TensorFlow, não no sistema.

## A instalação das bibliotecas CUDA

O TensorFlow a partir da versão 2.16 distribui as bibliotecas CUDA como
*wheels* do PyPI — o usuário não precisa instalar o CUDA Toolkit via RPM.
Basta:

```bash
pip install --upgrade 'tensorflow[and-cuda]'
```

O comando baixou aproximadamente 2,6 GB entre `nvidia-cublas-cu12`,
`nvidia-cudnn-cu12`, `nvidia-cuda-runtime-cu12`, `nvidia-cufft-cu12`,
`nvidia-cusparse-cu12`, `nvidia-cusolver-cu12`, `nvidia-curand-cu12`,
`nvidia-nccl-cu12`, `nvidia-nvjitlink-cu12` e complementos.

Porém, após a instalação, `tf.config.list_physical_devices('GPU')`
continuava retornando lista vazia, com novo aviso:

```
W0000 gpu_device.cc:2365] Cannot dlopen some GPU libraries.
Skipping registering GPU devices...
```

## Por que as bibliotecas CUDA não foram encontradas

A instalação do `pip` caiu em modo `--user` automaticamente porque o
usuário não tem escrita em `site-packages` global (`Defaulting to user
installation because normal site-packages is not writeable`). As wheels
NVIDIA foram depositadas em:

```
~/.local/lib/python3.13/site-packages/nvidia/{cublas,cudnn,cufft,...}/lib/
```

O TensorFlow usa `dlopen()` em tempo de execução para carregar essas
`.so`, mas o *dynamic linker* do sistema (`ld.so`) só procura em
`LD_LIBRARY_PATH`, nos diretórios listados em `/etc/ld.so.conf.d/`, ou em
`rpath` embutido no binário. Nenhum desses caminhos aponta para o
`site-packages` do usuário.

Em distribuições onde o TensorFlow é instalado em ambiente isolado
(`venv`, `conda`), existem *hooks* que resolvem esse path
automaticamente via `__init__.py` dos pacotes `nvidia-*`. No install
`--user` sobre o Python global da Fedora, esses hooks não têm efeito
sobre o dynamic linker porque a variável de ambiente só é lida **no
momento do `execve`** do processo Python — modificar `os.environ`
depois não adianta.

## A solução aplicada

Teste imediato com `LD_LIBRARY_PATH` explícito confirmou a hipótese:

```bash
CUDA_LIBS=$(find ~/.local/lib/python3.13/site-packages/nvidia -name lib -type d | tr '\n' ':')
LD_LIBRARY_PATH="${CUDA_LIBS}${LD_LIBRARY_PATH}" python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"
# [PhysicalDevice(name='/physical_device:GPU:0', device_type='GPU')]
```

Para tornar a configuração persistente em qualquer shell, o seguinte
bloco foi adicionado ao `~/.bashrc`:

```bash
# ---- TensorFlow CUDA paths (pip user install) ----
if [ -d "$HOME/.local/lib/python3.13/site-packages/nvidia" ]; then
    _TF_CUDA_LIBS=$(find "$HOME/.local/lib/python3.13/site-packages/nvidia" -maxdepth 2 -name lib -type d 2>/dev/null | tr '\n' ':')
    export LD_LIBRARY_PATH="${_TF_CUDA_LIBS}${LD_LIBRARY_PATH}"
    unset _TF_CUDA_LIBS
fi
```

O `maxdepth 2` limita a varredura a `nvidia/*/lib`, evitando que o `find`
desça em subdiretórios arbitrários. O prefixo `_TF_CUDA_LIBS` segue a
convenção de variável auxiliar descartável. A ordem de precedência
coloca as libs NVIDIA antes do `LD_LIBRARY_PATH` preexistente, garantindo
que sobreponham versões eventualmente conflitantes do sistema.

## Verificação

Benchmark matmul de matrizes 2000×2000 repetido 20 vezes:

| Dispositivo | Tempo | Speedup |
|-------------|-------|---------|
| CPU (Raptor Lake) | 0.403 s | 1x |
| GPU (RTX 4070 Laptop) | 0.031 s | **12.8x** |

O TensorFlow reportou o device corretamente:

```
Created device /job:localhost/replica:0/task:0/device:GPU:0 with 5993 MB memory:
-> device: 0, name: NVIDIA GeForce RTX 4070 Laptop GPU,
pci bus id: 0000:01:00.0, compute capability: 8.9
```

## Por que a solução foi correção, não contorno

A classificação importa. O sistema tinha todos os componentes necessários
(driver, módulo, chave, CUDA toolkit via pip) mas faltava o elo de
configuração que os ligasse ao processo Python. Ajustar o
`LD_LIBRARY_PATH` é **configuração legítima de ambiente**, não supressão
de sintoma — o analógico é configurar `PATH` para encontrar binários.
Alternativas contorcidas como `ctypes.CDLL` pré-carregando as `.so` antes
de `import tensorflow`, ou monkey-patching dos pacotes `nvidia-*`,
produziriam o mesmo efeito numérico mas introduziriam fragilidade
estrutural no pipeline.

A mensagem de erro original desapareceu porque o sistema agora a
contradiz factualmente: o TensorFlow **encontra** os drivers CUDA. Não
há silenciamento envolvido.
