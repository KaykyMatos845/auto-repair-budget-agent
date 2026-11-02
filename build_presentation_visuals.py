import os
from PIL import Image, ImageDraw, ImageFont

DIRECTORY = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(DIRECTORY, "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

def create_ai_inspection_image():
    sample_path = os.path.join(DIRECTORY, "public", "samples", "onix_rear.jpg")
    if not os.path.exists(sample_path):
        print(f"Sample not found: {sample_path}")
        return None
    
    img = Image.open(sample_path).convert("RGBA")
    w, h = img.size

    # Create overlay
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Box 1: Taillight (Red/Rose)
    b1_x1, b1_y1, b1_x2, b1_y2 = int(w * 0.58), int(h * 0.28), int(w * 0.88), int(h * 0.58)
    draw.rectangle([b1_x1, b1_y1, b1_x2, b1_y2], outline=(244, 63, 94, 255), width=6)
    draw.rectangle([b1_x1, b1_y1 - 36, b1_x1 + 380, b1_y1], fill=(244, 63, 94, 230))
    draw.text((b1_x1 + 10, b1_y1 - 30), "LANTERNA ESQ: SUBSTITUICAO (95%)", fill=(255, 255, 255, 255))

    # Box 2: Bumper (Gold)
    b2_x1, b2_y1, b2_x2, b2_y2 = int(w * 0.18), int(h * 0.55), int(w * 0.92), int(h * 0.88)
    draw.rectangle([b2_x1, b2_y1, b2_x2, b2_y2], outline=(245, 158, 11, 255), width=6)
    draw.rectangle([b2_x1, b2_y1 - 36, b2_x1 + 410, b2_y1], fill=(245, 158, 11, 230))
    draw.text((b2_x1 + 10, b2_y1 - 30), "PARACHOQUE TRAS: RECUPERACAO / PINTURA", fill=(15, 23, 42, 255))

    # Top Banner
    draw.rectangle([20, 20, 680, 75], fill=(15, 23, 42, 230), outline=(56, 189, 248, 255), width=2)
    draw.text((40, 36), "AI VISION: CHEVROLET ONIX HATCH 2021 • DETECCAO ATIVA", fill=(56, 189, 248, 255))

    out = Image.alpha_composite(img, overlay).convert("RGB")
    out_path = os.path.join(ASSETS_DIR, "ai_annotated_inspection.jpg")
    out.save(out_path, quality=92)
    print(f"Created: {out_path}")
    return out_path

def create_swarm_diagram_image():
    w, h = 1600, 900
    img = Image.new("RGB", (w, h), (10, 15, 29))
    draw = ImageDraw.Draw(img)

    # Title
    draw.text((60, 40), "DOCKER SWARM CLUSTER (DOCKER-IN-DOCKER)", fill=(251, 191, 36))
    draw.text((60, 80), "Arquitetura com 1 Manager + 2 Workers em Overlay Network VXLAN", fill=(148, 163, 184))

    # 3 Large Nodes
    node_w, node_h = 460, 520
    top_y = 160

    # Node 1: Manager
    n1_x = 60
    draw.rounded_rectangle([n1_x, top_y, n1_x + node_w, top_y + node_h], radius=16, fill=(22, 32, 54), outline=(245, 158, 11), width=3)
    draw.rounded_rectangle([n1_x + 20, top_y + 20, n1_x + node_w - 20, top_y + 80], radius=8, fill=(30, 45, 75))
    draw.text((n1_x + 40, top_y + 35), "SWARM-MANAGER (LEADER)", fill=(251, 191, 36))
    
    # Manager Containers
    draw.rounded_rectangle([n1_x + 20, top_y + 110, n1_x + node_w - 20, top_y + 200], radius=8, fill=(15, 23, 42), outline=(56, 189, 248), width=2)
    draw.text((n1_x + 40, top_y + 125), "Visualizer Dashboard", fill=(255, 255, 255))
    draw.text((n1_x + 40, top_y + 155), "Porta 8080:8080 • docker.sock", fill=(148, 163, 184))

    draw.rounded_rectangle([n1_x + 20, top_y + 220, n1_x + node_w - 20, top_y + 310], radius=8, fill=(15, 23, 42), outline=(245, 158, 11), width=2)
    draw.text((n1_x + 40, top_y + 235), "Local Docker Registry", fill=(255, 255, 255))
    draw.text((n1_x + 40, top_y + 265), "Porta 5000:5000 • Imagens Privadas", fill=(148, 163, 184))

    draw.rounded_rectangle([n1_x + 20, top_y + 330, n1_x + node_w - 20, top_y + 420], radius=8, fill=(15, 23, 42), outline=(52, 211, 153), width=2)
    draw.text((n1_x + 40, top_y + 345), "Ingress Load Balancer", fill=(255, 255, 255))
    draw.text((n1_x + 40, top_y + 375), "Porta 80:80 • IPVS Routing Mesh", fill=(148, 163, 184))

    # Node 2: Worker 1
    n2_x = 570
    draw.rounded_rectangle([n2_x, top_y, n2_x + node_w, top_y + node_h], radius=16, fill=(22, 32, 54), outline=(6, 182, 212), width=2)
    draw.rounded_rectangle([n2_x + 20, top_y + 20, n2_x + node_w - 20, top_y + 80], radius=8, fill=(30, 45, 75))
    draw.text((n2_x + 40, top_y + 35), "SWARM-WORKER-1", fill=(56, 189, 248))

    draw.rounded_rectangle([n2_x + 20, top_y + 110, n2_x + node_w - 20, top_y + 240], radius=8, fill=(15, 23, 42), outline=(52, 211, 153), width=2)
    draw.text((n2_x + 40, top_y + 130), "autobudget_backend.1", fill=(255, 255, 255))
    draw.text((n2_x + 40, top_y + 165), "Python REST API • Gemini AI Engine", fill=(148, 163, 184))
    draw.text((n2_x + 40, top_y + 195), "Status: Running [Replica 1/2]", fill=(52, 211, 153))

    draw.rounded_rectangle([n2_x + 20, top_y + 260, n2_x + node_w - 20, top_y + 390], radius=8, fill=(15, 23, 42), outline=(56, 189, 248), width=2)
    draw.text((n2_x + 40, top_y + 280), "autobudget_frontend.1", fill=(255, 255, 255))
    draw.text((n2_x + 40, top_y + 315), "Nginx Alpine • React Standalone", fill=(148, 163, 184))
    draw.text((n2_x + 40, top_y + 345), "Status: Running [Replica 1/2]", fill=(52, 211, 153))

    # Node 3: Worker 2
    n3_x = 1080
    draw.rounded_rectangle([n3_x, top_y, n3_x + node_w, top_y + node_h], radius=16, fill=(22, 32, 54), outline=(6, 182, 212), width=2)
    draw.rounded_rectangle([n3_x + 20, top_y + 20, n3_x + node_w - 20, top_y + 80], radius=8, fill=(30, 45, 75))
    draw.text((n3_x + 40, top_y + 35), "SWARM-WORKER-2", fill=(56, 189, 248))

    draw.rounded_rectangle([n3_x + 20, top_y + 110, n3_x + node_w - 20, top_y + 240], radius=8, fill=(15, 23, 42), outline=(52, 211, 153), width=2)
    draw.text((n3_x + 40, top_y + 130), "autobudget_backend.2", fill=(255, 255, 255))
    draw.text((n3_x + 40, top_y + 165), "Python REST API • Gemini AI Engine", fill=(148, 163, 184))
    draw.text((n3_x + 40, top_y + 195), "Status: Running [Replica 2/2]", fill=(52, 211, 153))

    draw.rounded_rectangle([n3_x + 20, top_y + 260, n3_x + node_w - 20, top_y + 390], radius=8, fill=(15, 23, 42), outline=(56, 189, 248), width=2)
    draw.text((n3_x + 40, top_y + 280), "autobudget_frontend.2", fill=(255, 255, 255))
    draw.text((n3_x + 40, top_y + 315), "Nginx Alpine • React Standalone", fill=(148, 163, 184))
    draw.text((n3_x + 40, top_y + 345), "Status: Running [Replica 2/2]", fill=(52, 211, 153))

    # Overlay Network Connection Bar
    bar_y = top_y + node_h + 30
    draw.rounded_rectangle([60, bar_y, w - 60, bar_y + 90], radius=12, fill=(16, 36, 60), outline=(56, 189, 248), width=3)
    draw.text((90, bar_y + 25), "OVERLAY NETWORK: autobudget-net (Driver Overlay VXLAN Multi-Host Mesh)", fill=(56, 189, 248))
    draw.text((90, bar_y + 55), "Criptografia de comunicacao interna e resolucao automatica de nomes DNS (backend:5000)", fill=(148, 163, 184))

    out_path = os.path.join(ASSETS_DIR, "swarm_cluster_diagram.png")
    img.save(out_path, quality=95)
    print(f"Created: {out_path}")
    return out_path

if __name__ == "__main__":
    create_ai_inspection_image()
    create_swarm_diagram_image()
