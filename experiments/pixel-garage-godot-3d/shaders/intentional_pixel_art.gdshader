shader_type canvas_item;
render_mode unshaded;
uniform sampler2D screen_texture : hint_screen_texture, repeat_disable, filter_nearest;
uniform float palette_steps : hint_range(4.0, 16.0, 1.0) = 7.0;
uniform float dither_amount : hint_range(0.0, 1.0, 0.01) = 0.11;
uniform float ink_amount : hint_range(0.0, 0.5, 0.01) = 0.16;
uniform float contrast : hint_range(0.8, 1.4, 0.01) = 1.09;
float bayer4(ivec2 p) {
 int x = ((p.x%4)+4)%4;
 int y = ((p.y%4)+4)%4;
 if(y==0){if(x==0)return 0.0;if(x==1)return 8.0;if(x==2)return 2.0;return 10.0;}
 if(y==1){if(x==0)return 12.0;if(x==1)return 4.0;if(x==2)return 14.0;return 6.0;}
 if(y==2){if(x==0)return 3.0;if(x==1)return 11.0;if(x==2)return 1.0;return 9.0;}
 if(x==0)return 15.0;if(x==1)return 7.0;if(x==2)return 13.0;return 5.0;
}
float luminance(vec3 c){return dot(c,vec3(0.2126,0.7152,0.0722));}
void fragment(){
 vec3 src=texture(screen_texture,SCREEN_UV).rgb;
 vec3 cx=texture(screen_texture,SCREEN_UV+vec2(SCREEN_PIXEL_SIZE.x,0.0)).rgb;
 vec3 cy=texture(screen_texture,SCREEN_UV+vec2(0.0,SCREEN_PIXEL_SIZE.y)).rgb;
 float edge=max(abs(luminance(src)-luminance(cx)),abs(luminance(src)-luminance(cy)));
 vec3 art=clamp((src-0.5)*contrast+0.5,vec3(0.0),vec3(1.0));
 float b=(bayer4(ivec2(FRAGCOORD.xy))/16.0-0.5)*dither_amount;
 art=floor(art*palette_steps+vec3(b)+0.5)/palette_steps;
 art=clamp(art-vec3(smoothstep(0.09,0.33,edge)*ink_amount),vec3(0.0),vec3(1.0));
 COLOR=vec4(art,1.0);
}
