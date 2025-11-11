#version 330 core
in vec3 fragColor;

out vec4 OutColor;

void main() {
    OutColor = vec4(fragColor, 1.0);
}