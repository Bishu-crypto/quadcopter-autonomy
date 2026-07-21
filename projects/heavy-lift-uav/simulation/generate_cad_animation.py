import os
import math
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation

def generate_cad_turntable(output_dir="projects/heavy-lift-uav/reports/figures"):
    os.makedirs(output_dir, exist_ok=True)
    gif_path = os.path.join(output_dir, "cad_360_turntable.gif")
    print("Rendering 360-degree CAD turntable animation...")

    fig = plt.figure(figsize=(8, 6), dpi=150)
    ax = fig.add_subplot(111, projection='3d')
    fig.patch.set_facecolor('#0F172A') # Dark slate background for premium look
    ax.set_facecolor('#0F172A')

    arm_length = 1.12
    angles_rad = np.radians([0, 60, 120, 180, 240, 300])
    directions = [[np.cos(a), np.sin(a)] for a in angles_rad]
    prop_length = 0.508

    def update_frame(frame):
        ax.clear()
        ax.set_facecolor('#0F172A')
        
        # Center Frame Hex Plates
        ax.plot([-0.20, 0.20], [0, 0], [0.04, 0.04], color='#64748B', linewidth=4)
        ax.plot([0, 0], [-0.20, 0.20], [0.04, 0.04], color='#64748B', linewidth=4)
        ax.plot([-0.20, 0.20], [0, 0], [-0.04, -0.04], color='#64748B', linewidth=4)
        ax.plot([0, 0], [-0.20, 0.20], [-0.04, -0.04], color='#64748B', linewidth=4)

        # 6 Arms, Motors, 2-Blade Props
        for d in directions:
            end_xy = arm_length * np.array(d)
            # Arm Tube
            ax.plot([0, end_xy[0]], [0, end_xy[1]], [0, 0], color='#94A3B8', linewidth=4.5)
            # Motor Stator/Rotor Bell
            ax.plot([end_xy[0]], [end_xy[1]], [0.02], 'o', color='#CBD5E1', markersize=7)
            ax.plot([end_xy[0]], [end_xy[1]], [0.045], 'o', color='#F8FAFC', markersize=9)
            
            # Propeller
            prop_dir = np.array([-d[1], d[0], 0])
            p1 = end_xy + prop_length * prop_dir[:2]
            p2 = end_xy - prop_length * prop_dir[:2]
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [0.068], color='#38BDF8', linewidth=3, alpha=0.95)

        # Payload Cargo Bay (Safety Orange)
        ax.bar3d(-0.15, -0.10, -0.255, 0.30, 0.20, 0.15, color='#F97316', alpha=0.85)
        # Camera Gimbal & Lens Barrel
        ax.scatter([0.18], [0.0], [-0.125], color='#F8FAFC', s=100)
        ax.plot([0.18, 0.205], [0, 0], [-0.125, -0.125], color='#38BDF8', linewidth=4)
        # Antenna
        ax.plot([0, 0], [0.08, 0.08], [0.04, 0.16], color='#EF4444', linewidth=2)

        # Landing Gear Legs & Skid Pads
        ax.plot([-0.2, -0.2], [-0.45, 0.45], [-0.45, -0.45], color='#64748B', linewidth=3)
        ax.plot([0.2, 0.2], [-0.45, 0.45], [-0.45, -0.45], color='#64748B', linewidth=3)
        ax.plot([-0.2, -0.2], [0.2, 0.2], [0, -0.45], color='#64748B', linewidth=2)
        ax.plot([0.2, 0.2], [0.2, 0.2], [0, -0.45], color='#64748B', linewidth=2)
        ax.plot([-0.2, -0.2], [-0.2, -0.2], [0, -0.45], color='#64748B', linewidth=2)
        ax.plot([0.2, 0.2], [-0.2, -0.2], [0, -0.45], color='#64748B', linewidth=2)
        ax.plot([-0.27, -0.13], [0.2, 0.2], [-0.455, -0.455], color='#F8FAFC', linewidth=5)
        ax.plot([0.13, 0.27], [0.2, 0.2], [-0.455, -0.455], color='#F8FAFC', linewidth=5)

        ax.set_xlim([-1.3, 1.3])
        ax.set_ylim([-1.3, 1.3])
        ax.set_zlim([-0.6, 0.6])
        ax.axis('off')
        
        azim_angle = frame * 10
        ax.view_init(elev=22, azim=azim_angle)
        plt.title('Heavy-Lift Hexacopter 3D CAD Assembly (360° Turntable)', color='#F8FAFC', fontsize=11, fontweight='bold', pad=10)

    anim = animation.FuncAnimation(fig, update_frame, frames=36, interval=100)
    anim.save(gif_path, writer='pillow', fps=10)
    plt.close()
    print(f"360-degree CAD turntable GIF saved to {gif_path}")

if __name__ == "__main__":
    generate_cad_turntable()
