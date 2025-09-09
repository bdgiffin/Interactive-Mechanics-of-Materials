import pygame
import asyncio
from math import *

# Include the pygame_widgets module
import pygame_widgets
from pygame_widgets.slider  import Slider

pygame.init()
window_width  = 1600
window_height = 800
window = pygame.display.set_mode((window_width,window_height))

# Create a slider
Nsteps = 50
sxx_slider = Slider(window,210, 20, 440, 15,
                    min=0, max=2*Nsteps, step=1, initial=int(Nsteps+0.7*Nsteps))
syy_slider = Slider(window,210, 50, 440, 15,
                    min=0, max=2*Nsteps, step=1, initial=int(Nsteps-0.4*Nsteps))
sxy_slider = Slider(window,210, 80, 440, 15,
                    min=0, max=2*Nsteps, step=1, initial=int(Nsteps+0.9*Nsteps))

async def main():

    # Initialize a new font for drawing text
    pygame.font.init()
    font_type  = 'None'
    font_size  = 30 # (pixels)
    stress_font = pygame.font.SysFont(font_type, font_size)

    # Create rendered text with the title of the game
    game_title    = "Mohr's circle σ-x τ-xy"
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
        points = [[0,          -width/2],
                  [length,     -width/2],
                  [length,     -size/2 ],
                  [length+size, 0      ],
                  [length,     +size/2 ],
                  [length,     +width/2],
                  [0,          +width/2]]

        # return the rotated and translated arrow
        points = rotate(points,theta)
        return translate(points,x0)

    def draw_arrow(x0, dx, width, size, color, label="", label_offset=0):
        length = sqrt(dx[0]*dx[0]+dx[1]*dx[1])
        theta  = atan2(dx[1],dx[0])

        # only draw the arrow if it is long enough
        if (length > 1):
            pygame.draw.polygon(window, color, arrow(x0,dx,width,size))
            label_text = stress_font.render(label, False, color)
            text_rect = label_text.get_rect()
            text_rect.center = (x0[0]+(length+label_offset)*cos(theta),x0[1]-(length+label_offset)*sin(theta))
            window.blit(label_text,text_rect)

    def draw_arc(x0,r,theta0,dtheta,negative,color,label="{:.0f}°",label_offset=0):
        # only draw the angle if it is large enough and radius is non-zero
        ddegrees = abs(dtheta*180/pi)
        if ((ddegrees > 1) and (r > 0)):
            pygame.draw.arc(window, color, (x0[0]-r, x0[1]-r, 2*r, 2*r), -theta0, -(theta0+dtheta))
            if (negative):
                ddegrees = -ddegrees
            label_text = stress_font.render(label.format(ddegrees), False, color)
            text_rect = label_text.get_rect()
            text_rect.center = (x0[0]+(r+label_offset)*cos(-theta0-0.5*dtheta),x0[1]-(r+label_offset)*sin(-theta0-0.5*dtheta))
            window.blit(label_text,text_rect)

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
    max_stress_value = 1
    sxx = max_stress_value*(sxx_slider.getValue()-Nsteps)
    syy = max_stress_value*(syy_slider.getValue()-Nsteps)
    sxy = max_stress_value*(sxy_slider.getValue()-Nsteps)

    mouse_pressed = False
    game_running = True
    while game_running:
        events = pygame.event.get()
        for event in events:
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

        # Update stresses defined in primary x,y coordinate frame
        sxx = max_stress_value*(sxx_slider.getValue()-Nsteps)
        syy = max_stress_value*(syy_slider.getValue()-Nsteps)
        sxy = max_stress_value*(sxy_slider.getValue()-Nsteps)

        # Compute stress invariants
        I1 = sxx + syy
        I2 = sxx*syy + sxy*sxy

        # Compute max shear and principal stresses
        savg = 0.5*I1
        tmax = sqrt(0.25*(sxx-syy)*(sxx-syy) + sxy*sxy)
        s1 = savg + tmax
        s2 = savg - tmax

        # Compute the rotation angle to the principal stress configuration
        thetap = 0.5*atan2(sxy,sxx-savg)

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
        x_axis = (int(0.25*inner_block_size),0)
        y_axis = (0,int(0.25*inner_block_size))
        xprime_axis = (int(+0.25*inner_block_size*cos(theta+0*pi/2)),int(-0.25*inner_block_size*sin(theta+0*pi/2)))
        yprime_axis = (int(-0.25*inner_block_size*cos(theta+1*pi/2)),int(+0.25*inner_block_size*sin(theta+1*pi/2)))

        # Draw inner block
        pygame.draw.polygon(window, "Light Steel Blue", inner_block)

        # Draw axes
        axis_width = 4
        axis_size  = 12
        draw_arrow(block_center,x_axis,axis_width,axis_size,"Dark Grey","x ",label_offset=25)
        draw_arrow(block_center,y_axis,axis_width,axis_size,"Dark Grey","y ",label_offset=25)
        draw_arrow(block_center,xprime_axis,axis_width,axis_size,"Steel Blue","x'",label_offset=25)
        draw_arrow(block_center,yprime_axis,axis_width,axis_size,"Steel Blue","y'",label_offset=25)

        # Draw angle
        theta_arc = -theta
        if (theta_arc < 0):
            draw_arc((block_center[0], block_center[1]),0.1*inner_block_size,-theta_arc,theta_arc,True,"Black",label_offset=20)
        else:
            draw_arc((block_center[0], block_center[1]),0.1*inner_block_size,0,-theta_arc,False,"Black",label_offset=20)

        # Draw stresses on outer block
        stress_offset = 10+outer_block_size
        stress_width = 8
        stress_size  = 24
        draw_arrow((block_center[0]+stress_offset,block_center[1]),(sxx,0),stress_width,stress_size, "Red", "σ-x", label_offset=45)
        draw_arrow((block_center[0]+stress_offset,block_center[1]),(0,sxy),stress_width,stress_size, "Red", "τ-xy",label_offset=35)
        draw_arrow((block_center[0]-stress_offset,block_center[1]),(-sxx,0),stress_width,stress_size,"Red", "σ-x", label_offset=45)
        draw_arrow((block_center[0]-stress_offset,block_center[1]),(0,-sxy),stress_width,stress_size,"Red", "τ-xy",label_offset=35)
        draw_arrow((block_center[0],block_center[1]-stress_offset),(0,syy),stress_width,stress_size ,"Blue","σ-y", label_offset=34)
        draw_arrow((block_center[0],block_center[1]-stress_offset),(sxy,0),stress_width,stress_size ,"Blue","τ-yx",label_offset=47)
        draw_arrow((block_center[0],block_center[1]+stress_offset),(0,-syy),stress_width,stress_size,"Blue","σ-y", label_offset=34)
        draw_arrow((block_center[0],block_center[1]+stress_offset),(-sxy,0),stress_width,stress_size,"Blue","τ-yx",label_offset=47)

        # Draw stresses on inner block
        stress_offset = -30+inner_block_size
        stress_width = 8
        stress_size  = 24
        dx = (int(+stress_offset*cos(theta+0*pi/2)),int(+stress_offset*sin(theta+0*pi/2)))
        draw_arrow((block_center[0]+dx[0],block_center[1]+dx[1]),(+txx*cos(theta),-txx*sin(theta)),stress_width,stress_size,"Magenta","σ-x'",label_offset=45)
        draw_arrow((block_center[0]+dx[0],block_center[1]+dx[1]),(+txy*sin(theta),+txy*cos(theta)),stress_width,stress_size,"Magenta","τ-x'y'",label_offset=48)
        draw_arrow((block_center[0]-dx[0],block_center[1]-dx[1]),(-txx*cos(theta),+txx*sin(theta)),stress_width,stress_size,"Magenta","σ-x'",label_offset=45)
        draw_arrow((block_center[0]-dx[0],block_center[1]-dx[1]),(-txy*sin(theta),-txy*cos(theta)),stress_width,stress_size,"Magenta","τ-x'y'",label_offset=48)
        dx = (int(-stress_offset*cos(theta+1*pi/2)),int(-stress_offset*sin(theta+1*pi/2)))
        draw_arrow((block_center[0]+dx[0],block_center[1]+dx[1]),(+tyy*sin(theta),+tyy*cos(theta)),stress_width,stress_size,"Purple","σ-y'",label_offset=45)
        draw_arrow((block_center[0]+dx[0],block_center[1]+dx[1]),(+txy*cos(theta),-txy*sin(theta)),stress_width,stress_size,"Purple","τ-y'x'",label_offset=48)
        draw_arrow((block_center[0]-dx[0],block_center[1]-dx[1]),(-tyy*sin(theta),-tyy*cos(theta)),stress_width,stress_size,"Purple","σ-y'",label_offset=45)
        draw_arrow((block_center[0]-dx[0],block_center[1]-dx[1]),(-txy*cos(theta),+txy*sin(theta)),stress_width,stress_size,"Purple","τ-y'x'",label_offset=48)

        # Draw Mohr's circle
        axis_length = window_height*0.77
        axis_height = window_height*0.6
        axis_width = 4
        axis_size  = 16
        plot_scale = 3
        draw_arrow((circle_center[0]-axis_length*0.5,circle_center[1]),(axis_length,0),axis_width,axis_size,"Dark Grey","σ",label_offset=30)
        draw_arrow((circle_center[0],circle_center[1]-axis_height*0.5),(0,-axis_height),axis_width,axis_size,"Dark Grey","τ",label_offset=30)
        pygame.draw.circle(window, "Violet", (circle_center[0]+plot_scale*savg,circle_center[1]), plot_scale*tmax, 3)

        # Draw vectors to points
        draw_arrow((circle_center[0]+plot_scale*savg,circle_center[1]),(+plot_scale*(sxx-savg),-plot_scale*sxy), 2, 0,"Red",    "({:.0f},{:.0f})".format(sxx,sxy),label_offset=50)
        draw_arrow((circle_center[0]+plot_scale*savg,circle_center[1]),(+plot_scale*(syy-savg),+plot_scale*sxy), 2, 0,"Blue",   "({:.0f},{:.0f})".format(syy,-sxy),label_offset=50)
        draw_arrow((circle_center[0]+plot_scale*savg,circle_center[1]),(+plot_scale*(txx-savg),-plot_scale*txy), 2, 0,"Magenta","({:.0f},{:.0f})".format(txx,txy),label_offset=50)
        draw_arrow((circle_center[0]+plot_scale*savg,circle_center[1]),(+plot_scale*(tyy-savg),+plot_scale*txy), 2, 0,"Purple", "({:.0f},{:.0f})".format(tyy,-txy),label_offset=50)

        # Draw stress points
        pygame.draw.circle(window, "Red",     (circle_center[0]+plot_scale*sxx,circle_center[1]+plot_scale*sxy), 10)
        pygame.draw.circle(window, "Blue",    (circle_center[0]+plot_scale*syy,circle_center[1]-plot_scale*sxy), 10)
        pygame.draw.circle(window, "Magenta", (circle_center[0]+plot_scale*txx,circle_center[1]+plot_scale*txy), 10)
        pygame.draw.circle(window, "Purple",  (circle_center[0]+plot_scale*tyy,circle_center[1]-plot_scale*txy), 10)

        # Draw arc
        arc_radius = 0.3*plot_scale*tmax
        if (theta_arc < 0):
            draw_arc((circle_center[0]+plot_scale*savg, circle_center[1]),arc_radius,2*thetap-2*theta_arc,2*theta_arc,True,"Black",label_offset=20)
        else:
            draw_arc((circle_center[0]+plot_scale*savg, circle_center[1]),arc_radius,2*thetap,-2*theta_arc,False,"Black",label_offset=20)

        # Draw text
        window.blit(stress_font.render("σ-x",  False, "Red"),  (720-620, 20-5))
        window.blit(stress_font.render("σ-y",  False, "Blue"), (720-620, 50-5))
        window.blit(stress_font.render("τ-xy", False, "Red"),  (640-620, 80-5))
        window.blit(stress_font.render("=",    False, "Black"),(690-620, 80-5))
        window.blit(stress_font.render("τ-yx", False, "Blue"), (710-620, 80-5))
        window.blit(stress_font.render("= {:3d}".format(sxx), False, "Black"), (760-620, 20-5))
        window.blit(stress_font.render("= {:3d}".format(syy), False, "Black"), (760-620, 50-5))
        window.blit(stress_font.render("= {:3d}".format(sxy), False, "Black"), (760-620, 80-5))
    
        # Draw different widgets within the window:
        pygame_widgets.update(events)

        pygame.display.update()

        await asyncio.sleep(0)

asyncio.run(main())
