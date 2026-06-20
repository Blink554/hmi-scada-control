import socket
import flet as ft
import os

def main(page: ft.Page):
    page.title = "SCADA Remote Control"
    page.bgcolor = "#F8FAFC"
    page.padding = 30
    page.theme_mode = ft.ThemeMode.LIGHT

    # Networking configuration (UDP Client)
    udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # --- UI State & Updates ---
    status_text = ft.Text("System Ready", size=14, weight=ft.FontWeight.W_600, color=ft.Colors.BLUE_GREY_600)
    status_icon = ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.BLUE_GREY_400, size=20)
    
    def update_status(text, color, icon):
        status_text.value = text
        status_text.color = color
        status_icon.name = icon
        status_icon.color = color
        page.update()

    # Settings Card Inputs
    ip_input = ft.TextField(
        label="SCADA Server IP", 
        value="10.201.205.60", 
        prefix_icon=ft.Icons.WIFI,
        border_radius=8,
        border_color=ft.Colors.BLUE_GREY_200,
        focused_border_color=ft.Colors.BLUE_700,
        text_align=ft.TextAlign.CENTER,
        height=55,
        content_padding=10
    )
    
    port_input = ft.TextField(
        label="Server Port", 
        value="61234", 
        prefix_icon=ft.Icons.SETTINGS_ETHERNET,
        border_radius=8,
        border_color=ft.Colors.BLUE_GREY_200,
        focused_border_color=ft.Colors.BLUE_700,
        text_align=ft.TextAlign.CENTER,
        height=55,
        content_padding=10
    )
    
    def send_command(cmd):
        update_status("Sending Command...", ft.Colors.BLUE_700, ft.Icons.HOURGLASS_TOP)
        try:
            target_ip = ip_input.value.strip()
            target_port = int(port_input.value.strip())
            
            if not target_ip:
                raise ValueError("IP address cannot be empty")
            
            udp_client.settimeout(2.0)
            udp_client.sendto(cmd.encode('utf-8'), (target_ip, target_port))
            
            try:
                data, _ = udp_client.recvfrom(1024)
                response = data.decode('utf-8')
                
                if response == "MOTOR_ON":
                    update_status("Motor is ON", ft.Colors.GREEN_600, ft.Icons.CHECK_CIRCLE)
                elif response == "MOTOR_OFF":
                    update_status("Motor is OFF", ft.Colors.RED_600, ft.Icons.CANCEL)
                else:
                    update_status("Command Sent", ft.Colors.GREEN_600, ft.Icons.CHECK_CIRCLE)
            except socket.timeout:
                update_status("Timeout (No Reply)", ft.Colors.ORANGE_600, ft.Icons.WARNING)
                
        except ValueError:
            update_status("Invalid Port", ft.Colors.RED_600, ft.Icons.ERROR)
        except Exception as e:
            update_status(f"Error: {e}", ft.Colors.RED_600, ft.Icons.ERROR)

    settings_card = ft.Container(
        content=ft.Column([
            ft.Text("NETWORK", size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_400),
            ip_input,
            port_input
        ], spacing=10),
        padding=20,
        bgcolor=ft.Colors.WHITE,
        border_radius=10,
    )

    status_card = ft.Container(
        content=ft.Row([
            status_icon,
            status_text
        ], alignment=ft.MainAxisAlignment.START, spacing=10),
        padding=15,
        bgcolor=ft.Colors.WHITE,
        border_radius=10,
    )

    # Big Bag Counter
    bag_count = ft.Text("0", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_800)
    
    def minus_click(e):
        current = int(bag_count.value)
        if current > 0:
            bag_count.value = str(current - 1)
            page.update()

    def plus_click(e):
        bag_count.value = str(int(bag_count.value) + 1)
        page.update()

    counter_ui = ft.Container(
        content=ft.Row([
            ft.IconButton(ft.Icons.REMOVE_CIRCLE_OUTLINE, on_click=minus_click, icon_color=ft.Colors.RED_400, icon_size=35),
            bag_count,
            ft.IconButton(ft.Icons.ADD_CIRCLE_OUTLINE, on_click=plus_click, icon_color=ft.Colors.GREEN_400, icon_size=35),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
        padding=10,
        bgcolor="#F1F5F9",
        border_radius=15,
        width=200
    )

    # Main Visual Control Button
    motor_button = ft.Button(
        content=ft.Row([
            ft.Icon(ft.Icons.POWER_SETTINGS_NEW, color=ft.Colors.WHITE, size=18),
            ft.Text("START P05", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=13)
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.BLUE_700,
            shape=ft.RoundedRectangleBorder(radius=6),
            padding=15,
        ),
        on_click=lambda e: send_command("start_motor"),
        width=150
    )

    left_column = ft.Column([
        ft.Column([
            ft.Icon(ft.Icons.KEYBOARD_ARROW_DOWN, size=30, color=ft.Colors.BLUE_300),
            ft.Icon(ft.Icons.KEYBOARD_ARROW_DOWN, size=30, color=ft.Colors.BLUE_500),
        ], spacing=-10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        ft.Image(src="bigbag.png", height=380, fit="contain"),
        ft.Container(height=10),
        counter_ui
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5)

    right_column = ft.Column([
        ft.Image(src="motor.png", height=55, fit="contain"),
        ft.Container(height=30),
        motor_button
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0)

    main_assembly = ft.Row([
        left_column,
        right_column
    ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.START, spacing=-40)

    visual_card = ft.Container(
        content=ft.Column([
            ft.Text("PROCESS CONTROL", size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_400),
            ft.Container(height=30),
            main_assembly
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=40,
        expand=True
    )

    # --- Assemble Main Layout ---
    page.scroll = ft.ScrollMode.AUTO
    page.add(
        ft.ResponsiveRow([
            ft.Column([
                settings_card,
                status_card
            ], col={"sm": 12, "md": 4, "xl": 3}, alignment=ft.MainAxisAlignment.START, spacing=20),
            ft.Container(
                content=visual_card,
                col={"sm": 12, "md": 8, "xl": 9}
            )
        ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START)
    )

if __name__ == "__main__":
    ft.app(main, assets_dir="assets")
