//! RegressÃµes do estado compartilhado pelos rasterizadores CPU e GPU.
use zeebx::video::{gles, rasterizer::{GlState, TexEnv}};

#[test]
fn funcao_invalida_preserva_dot3_e_dot3_nao_e_funcao_de_alfa() {
    let mut env = TexEnv::default();
    env.define(gles::GL_COMBINE_RGB, gles::GL_DOT3_RGB, 0.0);
    for invalid in [gles::GL_TEXTURE0, gles::GL_COMBINE] {
        env.define(gles::GL_COMBINE_RGB, invalid, 0.0);
        assert_eq!(env.combina[0], gles::GL_DOT3_RGB);
    }
    env.define(gles::GL_COMBINE_ALPHA, gles::GL_REPLACE, 0.0);
    env.define(gles::GL_COMBINE_ALPHA, gles::GL_DOT3_RGBA, 0.0);
    assert_eq!(env.combina[1], gles::GL_REPLACE);
}

#[test]
fn agua_usa_alfa_da_textura_em_vez_do_zero_anterior() {
    let mut gl = GlState::new(1, 1);
    gl.set_active_texture(gles::GL_TEXTURE0 + 1);
    gl.set_texture_env(gles::GL_COMBINE);
    gl.set_texture_env_param(gles::GL_COMBINE_ALPHA, gles::GL_REPLACE, 0.0);
    gl.set_texture_env_param(gles::GL_SRC0_ALPHA, gles::GL_TEXTURE0 + 1, 0.0);
    let env = gl.unidade1().env;
    let texel = [0.4, 0.5, 0.6, 187.0 / 255.0];
    let result = env.aplica_com([0.0; 4], [0.0; 4], texel, [Some([0.0; 4]), Some(texel)]);
    assert!((result[3] - 187.0 / 255.0).abs() < 0.00001);
}
