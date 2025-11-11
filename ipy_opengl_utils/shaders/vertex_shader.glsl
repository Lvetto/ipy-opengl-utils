#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 instancePos;
layout (location = 2) in vec3 instanceColor;

out vec3 Normal;
out vec3 FragPos;
out vec3 FragColor;
flat out int vInstanceID;

uniform mat4 view;
uniform mat4 projection;
uniform vec3 materialColor;
uniform bool isLine;

void main()
{
    vec3 worldPos = aPos;
    if (isLine) {
        FragColor = materialColor;
        vInstanceID = -1;
    } else {
        worldPos += instancePos;
        FragColor = instanceColor;
        vInstanceID = gl_InstanceID;
    }
    gl_Position = projection * view * vec4(worldPos, 1.0);
    FragPos = worldPos;
    Normal = normalize(aPos);
}