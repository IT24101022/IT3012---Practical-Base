#include <GL/glut.h>
#include <iostream>

struct Vertex3D {
    float x, y, z;
};

struct Edge {
    int v1, v2;
};

struct Face {
    int v[4];
};

Vertex3D vertices[8] = {
    {-1,-1,-1}, { 1,-1,-1}, { 1, 1,-1}, {-1, 1,-1},
    {-1,-1, 1}, { 1,-1, 1}, { 1, 1, 1}, {-1, 1, 1}
};

Edge edges[12] = {
    {0,1},{1,2},{2,3},{3,0},
    {4,5},{5,6},{6,7},{7,4},
    {0,4},{1,5},{2,6},{3,7}
};

// Define the 6 faces using the vertex indices
Face faces[6] = {
    {0, 3, 2, 1}, // Front face (-z)
    {4, 5, 6, 7}, // Back face (+z)
    {0, 1, 5, 4}, // Bottom face (-y)
    {3, 7, 6, 2}, // Top face (+y)
    {1, 2, 6, 5}, // Right face (+x)
    {0, 4, 7, 3}  // Left face (-x)
};

float angleY = 0.0f;
bool isWireframe = true; // Toggle for wireframe/solid

void init() {
    glClearColor(0.1f, 0.1f, 0.1f, 1.0f);
    glEnable(GL_DEPTH_TEST);
}

void display() {
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    glLoadIdentity();
    
    // Move the cube back so we can see it
    glTranslatef(0.0f, 0.0f, -6.0f);
    
    // Add continuous rotation around Y axis
    glRotatef(angleY, 0.0f, 1.0f, 0.0f);
    // Add a slight X rotation for a better 3D perspective
    glRotatef(25.0f, 1.0f, 0.0f, 0.0f); 

    if (isWireframe) {
        // 6. Render the edges using GL_LINES
        glColor3f(0.0f, 1.0f, 0.0f); // Green color for wireframe
        glBegin(GL_LINES);
        for (int i = 0; i < 12; i++) {
            glVertex3f(vertices[edges[i].v1].x, vertices[edges[i].v1].y, vertices[edges[i].v1].z);
            glVertex3f(vertices[edges[i].v2].x, vertices[edges[i].v2].y, vertices[edges[i].v2].z);
        }
        glEnd();
    } else {
        // 7. Render each quadrilateral face as two triangles
        glBegin(GL_TRIANGLES);
        for (int i = 0; i < 6; i++) {
            // Give each face a different color so they are distinguishable
            glColor3f((i%2)*0.5f + 0.3f, (i%3)*0.4f + 0.2f, (i%4)*0.3f + 0.3f);
            
            // First triangle (v0, v1, v2)
            glVertex3f(vertices[faces[i].v[0]].x, vertices[faces[i].v[0]].y, vertices[faces[i].v[0]].z);
            glVertex3f(vertices[faces[i].v[1]].x, vertices[faces[i].v[1]].y, vertices[faces[i].v[1]].z);
            glVertex3f(vertices[faces[i].v[2]].x, vertices[faces[i].v[2]].y, vertices[faces[i].v[2]].z);
            
            // Second triangle (v0, v2, v3)
            glVertex3f(vertices[faces[i].v[0]].x, vertices[faces[i].v[0]].y, vertices[faces[i].v[0]].z);
            glVertex3f(vertices[faces[i].v[2]].x, vertices[faces[i].v[2]].y, vertices[faces[i].v[2]].z);
            glVertex3f(vertices[faces[i].v[3]].x, vertices[faces[i].v[3]].y, vertices[faces[i].v[3]].z);
        }
        glEnd();
    }
    
    glutSwapBuffers();
}

void update(int value) {
    // 8. Add continuous rotation
    angleY += 1.0f;
    if (angleY > 360.0f) angleY -= 360.0f;
    
    glutPostRedisplay();
    glutTimerFunc(16, update, 0); // Call update again after ~16ms (60 FPS)
}

void keyboard(unsigned char key, int x, int y) {
    // 9. Add a keyboard control to switch between wireframe and solid rendering
    if (key == 'w' || key == 'W') {
        isWireframe = !isWireframe;
    }
}

void reshape(int w, int h) {
    if (h == 0) h = 1;
    float aspect = (float)w / h;
    
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    gluPerspective(45.0f, aspect, 0.1f, 100.0f);
    
    glMatrixMode(GL_MODELVIEW);
}

int main(int argc, char** argv) {
    glutInit(&argc, argv);
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH);
    glutInitWindowSize(800, 600);
    glutCreateWindow("B-rep Cube - Press 'w' to toggle wireframe");
    
    init();
    
    glutDisplayFunc(display);
    glutReshapeFunc(reshape);
    glutKeyboardFunc(keyboard); // Register keyboard callback
    glutTimerFunc(16, update, 0); // Start the rotation timer
    
    std::cout << "Starting program. Press 'w' to toggle between wireframe and solid mode." << std::endl;
    
    glutMainLoop();
    return 0;
}
