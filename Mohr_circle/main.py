import pygame
import asyncio
from math import *

pygame.init()
window_width  = 1600
window_height = 800
window = pygame.display.set_mode((window_width,window_height))

async def main():

    # Initialize a new font for drawing text
    pygame.font.init()
    font_type  = 'PT Mono'
    font_size  = 30 # (pixels)
    stress_font = pygame.font.SysFont(font_type, font_size)

    # Create rendered text with the title of the game
    game_title    = "Mohr's circle"
    anti_aliasing = True # (adjusts pixelized appearance of rendered text)
    text_color    = "Black"
    title_text = stress_font.render(game_title, anti_aliasing, text_color)

    # Define Mohr's circle dimensions

    circle_center = (int(window_width*0.2),int(window_height/2))

    # Define inner and outer block dimensions
    block_center = (int(window_width*0.72),int(window_height/2))
    outer_block_size = int(window_height*3/8)
    inner_block_size = int(outer_block_size*0.7)
    outer_block = ((block_center[0]-outer_block_size,block_center[1]-outer_block_size),
                   (block_center[0]+outer_block_size,block_center[1]-outer_block_size),
                   (block_center[0]+outer_block_size,block_center[1]+outer_block_size),
                   (block_center[0]-outer_block_size,block_center[1]+outer_block_size))
    theta = 0.0

    def arrow(x0, dx, width, size):
        # get length and orientation angle of the vector
        length = sqrt(dx[0]*dx[0]+dx[1]*dx[1])
        theta  = atan2(dx[1],dx[0])

        # define points of the arrow
        if (length > 1):
            points = [[0,          -width/2],
                      [length,     -width/2],
                      [length,     -size/2 ],
                      [length+size, 0      ],
                      [length,     +size/2 ],
                      [length,     +width/2],
                      [0,          +width/2]]
        else:
            points = [[0,0],[0,0],[0,0]]

        # return the rotated and translated arrow
        points = rotate(points,theta)
        return translate(points,x0)

    def translate(points,dx):
        for i, point in enumerate(points):
            points[i][0] = point[0] + dx[0]
            points[i][1] = point[1] + dx[1]
        return points

    def rotate(points,angle):
        for i, point in enumerate(points):
            points[i] = [+point[0]*cos(angle)+point[1]*sin(angle),-point[0]*sin(angle)+point[1]*cos(angle)]
        return points

    # Define the global stresses
    stress_scale = 5
    sxx =  10*stress_scale
    syy = -5*stress_scale
    sxy =  15*stress_scale

    mouse_pressed = False
    game_running = True
    while game_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
            if ((event.type == pygame.MOUSEBUTTONDOWN) or (event.type == pygame.FINGERDOWN)):
                mouse_pressed = True
            if ((event.type == pygame.MOUSEBUTTONUP) or (event.type == pygame.FINGERUP)):
                mouse_pressed = False

        if mouse_pressed:
            mouse_x, mouse_y = event.pos
            if (mouse_x > 0.5*window_width):
                theta = atan2(mouse_y-block_center[1],mouse_x-block_center[0])

        # Compute stress invariants
        I1 = sxx + syy
        I2 = sxx*syy + sxy*sxy

        # Compute max shear and principal stresses
        savg = 0.5*I1
        tmax = sqrt(0.25*(sxx-syy)*(sxx-syy) + sxy*sxy)
        s1 = savg + tmax
        s2 = savg - tmax

        # Update Euler angles
        cost = cos(-theta)
        sint = sin(-theta)

        # Compute the local stresses
        txx = sxx*cost*cost + syy*sint*sint + 2*sxy*sint*cost
        tyy = sxx*sint*sint + syy*cost*cost - 2*sxy*sint*cost
        txy = (syy-sxx)*sint*cost + sxy*(cost*cost - sint*sint)

        if mouse_pressed:
            mouse_x, mouse_y = event.pos
            if (mouse_x > 0.5*window_width):
                print("theta = " + str(theta*180/pi))
                print("sxx = " + str(sxx))
                print("syy = " + str(syy))
                print("sxy = " + str(sxy))
                print("txx = " + str(txx))
                print("tyy = " + str(tyy))
                print("txy = " + str(txy))

        window.fill("White")

        # Draw outer block
        pygame.draw.polygon(window, "Light Grey", outer_block)

        # Define rotation matrix
        inner_block = ((int(block_center[0]+inner_block_size*cos(theta-3*pi/4)),int(block_center[1]+inner_block_size*sin(theta-3*pi/4))),
                       (int(block_center[0]+inner_block_size*cos(theta-1*pi/4)),int(block_center[1]+inner_block_size*sin(theta-1*pi/4))),
                       (int(block_center[0]+inner_block_size*cos(theta+1*pi/4)),int(block_center[1]+inner_block_size*sin(theta+1*pi/4))),
                       (int(block_center[0]+inner_block_size*cos(theta+3*pi/4)),int(block_center[1]+inner_block_size*sin(theta+3*pi/4))))
        xprime_axis = (int(+0.25*inner_block_size*cos(theta+0*pi/2)),int(-0.25*inner_block_size*sin(theta+0*pi/2)))
        yprime_axis = (int(-0.25*inner_block_size*cos(theta+1*pi/2)),int(+0.25*inner_block_size*sin(theta+1*pi/2)))

        # Draw inner block
        pygame.draw.polygon(window, "Light Steel Blue", inner_block)
        axis_width = 4
        axis_size  = 12
        pygame.draw.polygon(window, "Steel Blue", arrow(block_center,xprime_axis,axis_width,axis_size))
        pygame.draw.polygon(window, "Steel Blue", arrow(block_center,yprime_axis,axis_width,axis_size))

        # Draw stresses on outer block
        stress_offset = 10+outer_block_size
        stress_width = 8
        stress_size  = 24
        pygame.draw.polygon(window, "Red",  arrow((block_center[0]+stress_offset,block_center[1]),(sxx,0),stress_width,stress_size))
        pygame.draw.polygon(window, "Red",  arrow((block_center[0]+stress_offset,block_center[1]),(0,sxy),stress_width,stress_size))
        pygame.draw.polygon(window, "Red",  arrow((block_center[0]-stress_offset,block_center[1]),(-sxx,0),stress_width,stress_size))
        pygame.draw.polygon(window, "Red",  arrow((block_center[0]-stress_offset,block_center[1]),(0,-sxy),stress_width,stress_size))
        pygame.draw.polygon(window, "Blue", arrow((block_center[0],block_center[1]-stress_offset),(0,syy),stress_width,stress_size))
        pygame.draw.polygon(window, "Blue", arrow((block_center[0],block_center[1]-stress_offset),(sxy,0),stress_width,stress_size))
        pygame.draw.polygon(window, "Blue", arrow((block_center[0],block_center[1]+stress_offset),(0,-syy),stress_width,stress_size))
        pygame.draw.polygon(window, "Blue", arrow((block_center[0],block_center[1]+stress_offset),(-sxy,0),stress_width,stress_size))

        # Write text
        stress_offset = 50+outer_block_size
        #window.blit(stress_font.render(str(sxx), anti_aliasing, "Red"), (block_center[0]+stress_offset+sxx,block_center[1]))
        #window.blit(stress_font.render(str(syy), anti_aliasing, "Blue"), (block_center[0],block_center[1]+stress_offset+syy))

        # Draw stresses on inner block
        stress_offset = -30+inner_block_size
        stress_width = 8
        stress_size  = 24
        dx = (int(+stress_offset*cos(theta+0*pi/2)),int(+stress_offset*sin(theta+0*pi/2)))
        pygame.draw.polygon(window, "Magenta", arrow((block_center[0]+dx[0],block_center[1]+dx[1]),(+txx*cos(theta),-txx*sin(theta)),stress_width,stress_size))
        pygame.draw.polygon(window, "Magenta", arrow((block_center[0]+dx[0],block_center[1]+dx[1]),(+txy*sin(theta),+txy*cos(theta)),stress_width,stress_size))
        pygame.draw.polygon(window, "Magenta", arrow((block_center[0]-dx[0],block_center[1]-dx[1]),(-txx*cos(theta),+txx*sin(theta)),stress_width,stress_size))
        pygame.draw.polygon(window, "Magenta", arrow((block_center[0]-dx[0],block_center[1]-dx[1]),(-txy*sin(theta),-txy*cos(theta)),stress_width,stress_size))
        dx = (int(-stress_offset*cos(theta+1*pi/2)),int(-stress_offset*sin(theta+1*pi/2)))
        pygame.draw.polygon(window, "Purple", arrow((block_center[0]+dx[0],block_center[1]+dx[1]),(+tyy*sin(theta),+tyy*cos(theta)),stress_width,stress_size))
        pygame.draw.polygon(window, "Purple", arrow((block_center[0]+dx[0],block_center[1]+dx[1]),(+txy*cos(theta),-txy*sin(theta)),stress_width,stress_size))
        pygame.draw.polygon(window, "Purple", arrow((block_center[0]-dx[0],block_center[1]-dx[1]),(-tyy*sin(theta),-tyy*cos(theta)),stress_width,stress_size))
        pygame.draw.polygon(window, "Purple", arrow((block_center[0]-dx[0],block_center[1]-dx[1]),(-txy*cos(theta),+txy*sin(theta)),stress_width,stress_size))

        # Draw Mohr's circle
        axis_length = window_height*0.7
        axis_width = 4
        axis_size  = 16
        plot_scale = 2
        pygame.draw.polygon(window, "Black", arrow((circle_center[0]-axis_length*0.5,circle_center[1]),(axis_length,0),axis_width,axis_size))
        pygame.draw.polygon(window, "Black", arrow((circle_center[0],circle_center[1]+axis_length*0.5),(0,axis_length),axis_width,axis_size))
        pygame.draw.circle(window, "Violet", (circle_center[0]+plot_scale*savg,circle_center[1]), plot_scale*tmax, 3)

        # Draw vectors to points
        pygame.draw.polygon(window, "Red",     arrow((circle_center[0]+plot_scale*savg,circle_center[1]),(+plot_scale*(sxx-savg),-plot_scale*sxy), 2, 0))
        pygame.draw.polygon(window, "Blue",    arrow((circle_center[0]+plot_scale*savg,circle_center[1]),(+plot_scale*(syy-savg),+plot_scale*sxy), 2, 0))
        pygame.draw.polygon(window, "Magenta", arrow((circle_center[0]+plot_scale*savg,circle_center[1]),(+plot_scale*(txx-savg),-plot_scale*txy), 2, 0))
        pygame.draw.polygon(window, "Purple",  arrow((circle_center[0]+plot_scale*savg,circle_center[1]),(+plot_scale*(tyy-savg),+plot_scale*txy), 2, 0))

        # Draw stress points
        pygame.draw.circle(window, "Red",        (circle_center[0]+plot_scale*sxx,circle_center[1]+plot_scale*sxy), 10)
        pygame.draw.circle(window, "Blue",       (circle_center[0]+plot_scale*syy,circle_center[1]-plot_scale*sxy), 10)
        pygame.draw.circle(window, "Magenta",    (circle_center[0]+plot_scale*txx,circle_center[1]+plot_scale*txy), 10)
        pygame.draw.circle(window, "Purple",     (circle_center[0]+plot_scale*tyy,circle_center[1]-plot_scale*txy), 10)

        # Draw the title text
        #title_position = (circle_center[0]-120,window_height-100) # (x,y)
        #window.blit(title_text, title_position)

        pygame.display.update()

        await asyncio.sleep(0)

asyncio.run(main())
