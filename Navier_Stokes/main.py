import pygame
import asyncio
from math import *
import numpy as np

# Define window
pygame.init()
display = (1600, 800)
window = pygame.display.set_mode(display)

# Define grid dimensions
h  = 20
Nx = int(display[0]/h)+2
Ny = int(display[1]/h)+2
dx = display[0]/(Nx-2)
dy = display[1]/(Ny-2)

# Define grid primal variables
fixed = np.zeros((Nx,Ny),dtype=bool)
rho   = np.zeros((Nx,Ny)) # mass density
vx    = np.zeros((Nx,Ny)) # x-velocity
vy    = np.zeros((Nx,Ny)) # y-velocity

# Define additional grid variables
m  = np.zeros((Nx,Ny)) # lumped mass
fx = np.zeros((Nx,Ny)) # x-force
fy = np.zeros((Nx,Ny)) # y-force

# Define the fluid parameters
rho0  = 1.0 # reference density
kappa = 1.0 # bulk modulus
mu    = 1.0 # viscosity

# Set the fixed time step size (based on the CFL number)
CFLmax = 1.0
vmax   = 1.0
dt     = CFLmax*min(dx,dy)/vmax

# Initialize the system
def initialize():
    # Initialize the density at each grid point
    rho.fill(rho0)

    # Set fixed boundaries
    fixed[0,:]  = True # left   boundary
    fixed[:,0]  = True # bottom boundary
    fixed[-1,:] = True # right  boundary
    fixed[:,-1] = True # top    boundary

# Perform diffusion step
def diffusion(dt):
    # Zero-initialize lumped mass and forces
    m.fill(0.0)
    fx.fill(0.0)
    fy.fill(0.0)

    # Loop over all grid cells
    for i in range(Nx):
        for j in range(Ny):
            if (not fixed[i,j]):
                # Compute lumped mass
                m[i,j] = rho[i,j]*dx*dy

                # Compute the relative volume change
                J = rho0/rho[i,j]

                # Compute pressure
                p = 0.5*kappa*(1.0-J*J)

                # Compute velocity gradient
                dvdx = [[(vx[i+1,j]-vx[i-1,j])/(2*dx),
                         (vx[i,j+1]-vx[i,j-1])/(2*dy)],
                        [(vy[i+1,j]-vy[i-1,j])/(2*dx),
                         (vy[i,j+1]-vy[i,j-1])/(2*dy)]]

                # Compute the sym. deviatoric part
                dil = 0.5*(dvdx[0][0] + dvdx[1][1])
                dvdx[0][0] = dvdx[0][0] - dil
                dvdx[1][1] = dvdx[1][1] - dil
                dvdx[0][1] = 0.5*(dvdx[0][1] + dvdx[1][0])
                dvdx[1][0] = dvdx[0][1]

                # Compute stress
                stress = [[2.0*mu*dvdx[0][0]-p,
                           2.0*mu*dvdx[0][1]],
                          [2.0*mu*dvdx[1][0],
                           2.0*mu*dvdx[1][1]-p]]

                # Compute stress divergence
                fx[i-1,j] = fx[i-1,j] - stress[0][0]*(-1.0/(2*dx))*dx*dy
                fx[i+1,j] = fx[i+1,j] - stress[0][0]*(+1.0/(2*dx))*dx*dy
                fx[i,j-1] = fx[i,j-1] - stress[0][1]*(-1.0/(2*dy))*dx*dy
                fx[i,j+1] = fx[i,j+1] - stress[0][1]*(+1.0/(2*dy))*dx*dy
                fy[i-1,j] = fy[i-1,j] - stress[1][0]*(-1.0/(2*dx))*dx*dy
                fy[i+1,j] = fy[i+1,j] - stress[1][0]*(+1.0/(2*dx))*dx*dy
                fy[i,j-1] = fy[i,j-1] - stress[1][1]*(-1.0/(2*dy))*dx*dy
                fy[i,j+1] = fy[i,j+1] - stress[1][1]*(+1.0/(2*dy))*dx*dy
                
    # Loop over all grid cells
    for i in range(Nx):
        for j in range(Ny):
            if (not fixed[i,j]):
                # Update the velocity
                vx[i,j] = vx[i,j] + (fx[i,j]/m[i,j])*dt
                vy[i,j] = vy[i,j] + (fy[i,j]/m[i,j])*dt

# Perform advection step
def advection(dt):
    # Zero-initialize the mass and momentum fluxes
    m.fill(0.0)
    fx.fill(0.0)
    fy.fill(0.0)

    # Loop over all grid cells
    for i in range(Nx):
        for j in range(Ny):
            if (not fixed[i,j]):
                # Compute the mass and momentum density upwind x-fluxes
                if (vx[i,j] > 0.0):
                    drhodx = (rho[i,j]         - rho[i-1,j]          )/dx
                    dpxdx  = (rho[i,j]*vx[i,j] - rho[i-1,j]*vx[i-1,j])/dx
                    dpydx  = (rho[i,j]*vy[i,j] - rho[i-1,j]*vy[i-1,j])/dx
                else:
                    drhodx = (rho[i+1,j]           - rho[i,j]        )/dx
                    dpxdx  = (rho[i+1,j]*vx[i+1,j] - rho[i,j]*vx[i,j])/dx
                    dpydx  = (rho[i+1,j]*vy[i+1,j] - rho[i,j]*vy[i,j])/dx

                # Compute the mass and momentum density upwind y-fluxes
                if (vy[i,j] > 0.0):
                    drhody = (rho[i,j]         - rho[i,j-1]          )/dy
                    dpxdy  = (rho[i,j]*vx[i,j] - rho[i,j-1]*vx[i,j-1])/dy
                    dpydy  = (rho[i,j]*vy[i,j] - rho[i,j-1]*vy[i,j-1])/dy
                else:
                    drhody = (rho[i,j+1]           - rho[i,j]        )/dy
                    dpxdy  = (rho[i,j+1]*vx[i,j+1] - rho[i,j]*vx[i,j])/dy
                    dpydy  = (rho[i,j+1]*vy[i,j+1] - rho[i,j]*vy[i,j])/dy

                # Compute the total mass and momentum change
                m[i,j]  = -(drhodx*vx[i,j]*dy + drhody*vy[i,j]*dx)*dt
                fx[i,j] = -( dpxdx*vx[i,j]*dy +  dpxdy*vy[i,j]*dx)*dt
                fy[i,j] = -( dpydx*vx[i,j]*dy +  dpydy*vy[i,j]*dx)*dt

    # Loop over all grid cells
    for i in range(Nx):
        for j in range(Ny):
            if (not fixed[i,j]):
                # Update the mass density and velocity
                rho[i,j] = rho[i,j] + m[i,j]/(dx*dy)
                vx[i,j]  = vx[i,j]  + fx[i,j]/(rho[i,j]*dx*dy)
                vy[i,j]  = vy[i,j]  + fy[i,j]/(rho[i,j]*dx*dy)

def gridLines():
    for i in range(0,Nx):
        xi = i*dx
        pygame.draw.line(window, "Black", (xi,0), (xi,display[1]), 1)
    for j in range(0,Ny):
        yj = j*dy
        pygame.draw.line(window, "Black", (0,yj), (display[0],yj), 1)

def gridCells():
    for i in range(0,Nx-2):
        xi = i*dx
        for j in range(0,Ny-2):
            yj = j*dy
            value3 = max(min(int(255*exp(-rho[i+1,j+1]/rho0)),255),0)
            color = (value3,value3,255)
            pygame.draw.rect(window, color, pygame.Rect(xi, yj, dx, dy))

def cursor():
    pos = pygame.mouse.get_pos()
    pygame.draw.circle(window, "Black", pos, 10)
    
async def main():

    initialize()

    # Set the persistent cursor status
    mouse_pressed = False

    game_running = True
    while game_running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                game_running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pressed = True
            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_pressed = False

        if mouse_pressed:
            pos=pygame.mouse.get_pos()
            btn=pygame.mouse
            id = (int(pos[0]/dx)+1,int(pos[1]/dy)+1)
            rho[id[0],id[1]] = rho[id[0],id[1]] + 1

        window.fill("White")

        # Draw the geometry
        gridCells()
        gridLines()
        cursor()

        diffusion(dt)
        advection(dt)
    
        pygame.display.update()
        
        await asyncio.sleep(0)

asyncio.run(main())
