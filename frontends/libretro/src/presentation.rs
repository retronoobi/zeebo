//! Apresenta a tela composta pelo motor, incluindo as camadas BREW 2D.
use glow::HasContext;
use std::{num::NonZeroU32, sync::{Arc, Mutex}};

struct Presenter {
    gl: Arc<glow::Context>,
    texture: glow::Texture,
    fbo: glow::Framebuffer,
}
static PRESENTER: Mutex<Option<Presenter>> = Mutex::new(None);

// 0.4.0 informa perda de contexto também em callbacks sem GL corrente.
// Nomes do contexto antigo não podem ser deletados no contexto novo.
pub fn abandon() {
    if let Ok(mut slot) = PRESENTER.lock() { *slot = None; }
}

pub fn present(gl: Arc<glow::Context>, pixels: &[u8], width: u32, height: u32, target: u32) -> Result<(), String> {
    let mut slot = PRESENTER.lock().map_err(|e| e.to_string())?;
    unsafe {
        if slot.is_none() {
            let texture = gl.create_texture()?;
            let fbo = match gl.create_framebuffer() {
                Ok(fbo) => fbo,
                Err(e) => { gl.delete_texture(texture); return Err(e); }
            };
            *slot = Some(Presenter { gl: gl.clone(), texture, fbo });
        }
        let p = slot.as_ref().unwrap();
        gl.active_texture(glow::TEXTURE0);
        gl.bind_texture(glow::TEXTURE_2D, Some(p.texture));
        gl.bind_buffer(glow::PIXEL_UNPACK_BUFFER, None);
        gl.pixel_store_i32(glow::UNPACK_ALIGNMENT, 2);
        gl.pixel_store_i32(glow::UNPACK_ROW_LENGTH, 0);
        gl.pixel_store_i32(glow::UNPACK_SKIP_ROWS, 0);
        gl.pixel_store_i32(glow::UNPACK_SKIP_PIXELS, 0);
        gl.tex_image_2d(glow::TEXTURE_2D, 0, glow::RGB8 as i32, width as i32, height as i32, 0,
            glow::RGB, glow::UNSIGNED_SHORT_5_6_5, glow::PixelUnpackData::Slice(Some(pixels)));
        gl.tex_parameter_i32(glow::TEXTURE_2D, glow::TEXTURE_MIN_FILTER, glow::NEAREST as i32);
        gl.tex_parameter_i32(glow::TEXTURE_2D, glow::TEXTURE_MAG_FILTER, glow::NEAREST as i32);
        gl.bind_framebuffer(glow::READ_FRAMEBUFFER, Some(p.fbo));
        gl.framebuffer_texture_2d(glow::READ_FRAMEBUFFER, glow::COLOR_ATTACHMENT0, glow::TEXTURE_2D, Some(p.texture), 0);
        gl.bind_framebuffer(glow::DRAW_FRAMEBUFFER, NonZeroU32::new(target).map(glow::NativeFramebuffer));
        gl.disable(glow::SCISSOR_TEST);
        gl.disable(glow::FRAMEBUFFER_SRGB);
        // O contrato original é bottom_left_origin=false: linha zero continua sendo o topo.
        gl.blit_framebuffer(0, 0, width as i32, height as i32, 0, 0, width as i32, height as i32,
            glow::COLOR_BUFFER_BIT, glow::NEAREST);
        gl.bind_framebuffer(glow::FRAMEBUFFER, NonZeroU32::new(target).map(glow::NativeFramebuffer));
        gl.bind_texture(glow::TEXTURE_2D, None);
        gl.pixel_store_i32(glow::UNPACK_ALIGNMENT, 4);
        // Equivalente à devolução da 0.4.1 para nosso caminho composto: o motor
        // usa FBO interno, portanto sua devolve_ao_frontend não desliga esses objetos.
        gl.bind_vertex_array(None);
        gl.use_program(None);
        gl.bind_buffer(glow::ARRAY_BUFFER, None);
    }
    Ok(())
}
