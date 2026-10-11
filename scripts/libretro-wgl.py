"""Hidden Windows OpenGL 3.3 host for the libretro integration test."""
import ctypes as C

class PixelFormat(C.Structure):
    _fields_ = [('size',C.c_ushort),('version',C.c_ushort),('flags',C.c_uint),
        ('pixel_type',C.c_ubyte),('color',C.c_ubyte),('red',C.c_ubyte),('red_shift',C.c_ubyte),
        ('green',C.c_ubyte),('green_shift',C.c_ubyte),('blue',C.c_ubyte),('blue_shift',C.c_ubyte),
        ('alpha',C.c_ubyte),('alpha_shift',C.c_ubyte),('accum',C.c_ubyte),('ar',C.c_ubyte),
        ('ag',C.c_ubyte),('ab',C.c_ubyte),('aa',C.c_ubyte),('depth',C.c_ubyte),('stencil',C.c_ubyte),
        ('aux',C.c_ubyte),('layer',C.c_ubyte),('reserved',C.c_ubyte),
        ('layer_mask',C.c_uint),('visible_mask',C.c_uint),('damage_mask',C.c_uint)]
class Hardware(C.Structure):
    _fields_ = [('kind',C.c_uint),('reset',C.c_void_p),('get_fbo',C.c_void_p),('get_proc',C.c_void_p),
        ('depth',C.c_bool),('stencil',C.c_bool),('bottom_left',C.c_bool),
        ('major',C.c_uint),('minor',C.c_uint),('cache',C.c_bool),('destroy',C.c_void_p),('debug',C.c_bool)]

class Host:
    def __init__(self):
        self.user = C.WinDLL('user32'); self.gdi = C.WinDLL('gdi32'); self.gl = C.WinDLL('opengl32')
        self.kernel = C.WinDLL('kernel32')
        def sig(dll,name,restype,args):
            f = getattr(dll,name); f.restype = restype; f.argtypes = args; return f
        pointer = C.c_void_p
        sig(self.user,'CreateWindowExW',pointer,[C.c_uint,C.c_wchar_p,C.c_wchar_p,C.c_uint,
            C.c_int,C.c_int,C.c_int,C.c_int,pointer,pointer,pointer,pointer])
        sig(self.user,'GetDC',pointer,[pointer]); sig(self.user,'DestroyWindow',C.c_bool,[pointer])
        sig(self.user,'ReleaseDC',C.c_int,[pointer,pointer])
        sig(self.gdi,'ChoosePixelFormat',C.c_int,[pointer,C.POINTER(PixelFormat)])
        sig(self.gdi,'SetPixelFormat',C.c_bool,[pointer,C.c_int,C.POINTER(PixelFormat)])
        sig(self.gl,'wglCreateContext',pointer,[pointer]); sig(self.gl,'wglMakeCurrent',C.c_bool,[pointer,pointer])
        sig(self.gl,'wglDeleteContext',C.c_bool,[pointer]); sig(self.gl,'wglGetProcAddress',pointer,[C.c_char_p])
        sig(self.kernel,'GetProcAddress',pointer,[pointer,C.c_char_p])
        self.window = self.user.CreateWindowExW(0,'STATIC','Zeebx state test',0x80000000,0,0,640,480,None,None,None,None)
        assert self.window, 'Hidden window creation failed'
        self.dc = self.user.GetDC(self.window)
        fmt = PixelFormat(); fmt.size=C.sizeof(fmt); fmt.version=1; fmt.flags=0x25
        fmt.color=32; fmt.depth=24; fmt.stencil=8
        index = self.gdi.ChoosePixelFormat(self.dc,C.byref(fmt))
        assert index and self.gdi.SetPixelFormat(self.dc,index,C.byref(fmt))
        legacy = self.gl.wglCreateContext(self.dc)
        assert legacy and self.gl.wglMakeCurrent(self.dc,legacy)
        create = C.WINFUNCTYPE(pointer,pointer,pointer,C.POINTER(C.c_int))(self.address(b'wglCreateContextAttribsARB'))
        attrs = (C.c_int*7)(0x2091,3,0x2092,3,0x9126,1,0)
        self.context = create(self.dc,None,attrs)
        assert self.context and self.gl.wglMakeCurrent(self.dc,self.context)
        self.gl.wglDeleteContext(legacy)
        self.bind_fbo = C.WINFUNCTYPE(None,C.c_uint,C.c_uint)(self.address(b'glBindFramebuffer'))
        self.read_pixels = sig(self.gl,'glReadPixels',None,[C.c_int,C.c_int,C.c_int,C.c_int,C.c_uint,C.c_uint,pointer])
        self.get_error = sig(self.gl,'glGetError',C.c_uint,[])
        self.fbo_callback = C.CFUNCTYPE(C.c_size_t)(lambda: 0)
        self.proc_callback = C.CFUNCTYPE(pointer,C.c_char_p)(self.address)
        self.hardware = None
    def address(self,name):
        address = self.gl.wglGetProcAddress(name)
        if address in (None,0,1,2,3,C.c_void_p(-1).value):
            address = self.kernel.GetProcAddress(self.gl._handle,name)
        return address
    def environment(self,data):
        value = C.cast(data,C.POINTER(Hardware)).contents
        assert value.kind == 3 and value.major == 3 and value.minor == 3
        value.get_fbo=C.cast(self.fbo_callback,C.c_void_p).value
        value.get_proc=C.cast(self.proc_callback,C.c_void_p).value
        self.hardware=Hardware.from_buffer_copy(value)
        return True
    def reset(self):
        self.current(); C.CFUNCTYPE(None)(self.hardware.reset)()
    def current(self):
        assert self.gl.wglMakeCurrent(self.dc,self.context)
    def suspend(self):
        assert self.gl.wglMakeCurrent(None,None)
    def pixels(self,w,h):
        self.bind_fbo(0x8ca8,0)
        buf=C.create_string_buffer(w*h*4)
        self.read_pixels(0,0,w,h,0x1908,0x1401,buf)
        error=self.get_error()
        assert error == 0, f'OpenGL error {error:#x}'
        return buf.raw
    def close(self):
        self.gl.wglMakeCurrent(None,None)
        self.gl.wglDeleteContext(self.context)
        self.user.ReleaseDC(self.window,self.dc)
        self.user.DestroyWindow(self.window)
