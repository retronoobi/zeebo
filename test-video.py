"""Teste isolado do frontend: WGL, lançador, reset e captura do quadro final."""
import ctypes as C
import importlib.util
import os
from pathlib import Path
import sys
import time
from PIL import Image

root = Path(__file__).resolve().parent
out = root / 'target' / ('video-' + sys.argv[3])
out.mkdir(parents=True, exist_ok=True)
os.environ['APPDATA'] = str(out / 'appdata')
spec = importlib.util.spec_from_file_location('wgl', root/'scripts/libretro-wgl.py')
wgl = importlib.util.module_from_spec(spec); spec.loader.exec_module(wgl)
host = wgl.Host()
core = C.CDLL(str(Path(sys.argv[1]).resolve()))
class Game(C.Structure):
    _fields_ = [('path', C.c_char_p), ('data', C.c_void_p), ('size', C.c_size_t), ('meta', C.c_char_p)]
class Descriptor(C.Structure):
    _fields_ = [('port', C.c_uint), ('device', C.c_uint), ('index', C.c_uint), ('id', C.c_uint), ('text', C.c_char_p)]
class Variable(C.Structure):
    _fields_ = [('key', C.c_char_p), ('value', C.c_char_p)]
option_reads = {b'zeebx_dpad_to_analog_p1': 0, b'zeebx_dpad_to_analog_p2': 0}
option_changed = False
option_value = b'disabled'
directories = {9: str(out/'system').encode(), 31: str(out/'saves').encode()}
for p in directories.values(): Path(os.fsdecode(p)).mkdir(parents=True, exist_ok=True)
@C.CFUNCTYPE(C.c_bool, C.c_uint, C.c_void_p)
def environment(cmd, data):
    global option_changed
    if cmd == 15:
        var = C.cast(data, C.POINTER(Variable)).contents
        if var.key in option_reads:
            option_reads[var.key] += 1
            var.value = option_value
            return True
    if cmd == 17:
        C.cast(data, C.POINTER(C.c_bool))[0] = option_changed
        option_changed = False
        return True
    if cmd in directories:
        C.cast(data, C.POINTER(C.c_char_p))[0] = directories[cmd]; return True
    if cmd == 10: return C.cast(data, C.POINTER(C.c_uint))[0] == 2
    if cmd == 14: return host.environment(data)
    if cmd == 11:
        descriptors = C.cast(data, C.POINTER(Descriptor)); i = 0
        while descriptors[i].text:
            assert len(descriptors[i].text) < 80, 'Nome de botão sem terminador'
            i += 1
        return True
    return False
count = 0
@C.CFUNCTYPE(None, C.c_void_p, C.c_uint, C.c_uint, C.c_size_t)
def video(data, width, height, pitch):
    global count
    count += 1
    assert data == C.c_void_p(-1).value
audio_frames = 0
@C.CFUNCTYPE(C.c_size_t, C.c_void_p, C.c_size_t)
def audio(data, frames):
    global audio_frames
    audio_frames += frames
    return frames
@C.CFUNCTYPE(None)
def poll(): pass
@C.CFUNCTYPE(C.c_int16, C.c_uint, C.c_uint, C.c_uint, C.c_uint)
def state(port, device, index, button): return 0
for name, callback in [('environment',environment),('video_refresh',video),('audio_sample_batch',audio),('input_poll',poll),('input_state',state)]:
    getattr(core,'retro_set_'+name)(callback)
core.retro_load_game.argtypes = [C.POINTER(Game)]; core.retro_load_game.restype = C.c_bool
core.retro_init()
game = Game(str(Path(sys.argv[2]).resolve()).encode(), None, 0, None)
assert core.retro_load_game(C.byref(game))
host.reset()
started = time.perf_counter()
use_program = C.WINFUNCTYPE(None,C.c_uint)(host.address(b'glUseProgram'))
bind_vao = C.WINFUNCTYPE(None,C.c_uint)(host.address(b'glBindVertexArray'))
for i in range(int(os.environ.get('ZEEBX_TEST_FRAMES', '600'))):
    if i == 20: reads_initial = option_reads.copy()
    if i == 299: assert option_reads == reads_initial, option_reads
    if i == 300:
        option_changed = True
        option_value = b'enabled'
    # Simula o frontend usando o contexto entre chamadas do core.
    use_program(0)
    bind_vao(0)
    core.retro_run()
assert all(option_reads[k] == reads_initial[k] + 1 for k in option_reads), option_reads
print('option cache/update PASS', option_reads, flush=True)
print('elapsed_seconds', round(time.perf_counter()-started, 3), 'audio_seconds', round(audio_frames/44100,3), flush=True)
raw = host.pixels(640,480)
im = Image.frombytes('RGBA',(640,480),raw)
im.save(out/'frame.png')
print('frames',count,'bottom_nonblack_pixels',sum(any(raw[i:i+3]) for i in range(640*240*4,len(raw),4)),flush=True)
core.retro_reset()
for i in range(60): core.retro_run()
host.pixels(640,480)
print('reset PASS',flush=True)
if host.hardware.destroy: C.CFUNCTYPE(None)(host.hardware.destroy)()
core.retro_unload_game(); core.retro_deinit(); host.close()
print('PASS',flush=True)
