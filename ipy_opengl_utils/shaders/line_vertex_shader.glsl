#version 330 core
layout (location = 0) in vec3 aPos;

uniform mat4 view;
uniform mat4 projection;
uniform vec3 lineColor;

out vec3 fragColor;

void main() {
    gl_Position = projection * view * vec4(aPos, 1.0);
    fragColor = lineColor;
}