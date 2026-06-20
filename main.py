import socket
import pyautogui

# CRITICAL: Disable PyAutoGUI delays for instant reaction times
pyautogui.PAUSE = 0.0
pyautogui.FAILSAFE = False

def start_server():
    # Local PC testing configuration
    IP_ADDRESS = "10.201.205.60"  
    PORT = 61234

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((IP_ADDRESS, PORT))
    
    print(f"=== PC UDP SERVER RUNNING ===")
    print(f"Listening on {IP_ADDRESS}:{PORT}...")
    print("Testing clean click releases. Watch your cursor!\n") 

    while True:
        try:
            data, address = server.recvfrom(1024)
            command = data.decode('utf-8')
            print(f"[Signal] {command}", flush=True)
            
            if command == "left_click":
                # Force an explicit press and instant hardware release
                pyautogui.mouseDown(button='left')
                pyautogui.mouseUp(button='left')
                
            elif command == "double_click":
                # Clean native double click execution with an explicit interval
                pyautogui.click(clicks=1, interval=1)
                
            elif command == "right_click":
                pyautogui.rightClick()
                
            elif command == "start_motor":
                # User config: set these to the exact coordinates of the motor button in SCADA
                motor_x = 500
                motor_y = 500
                print(f"Clicking motor at ({motor_x}, {motor_y})")
                pyautogui.click(x=motor_x, y=motor_y)
                
                # Check pixel color to verify motor state
                import time
                time.sleep(0.5) # Wait for SCADA UI to update
                try:
                    r, g, b = pyautogui.pixel(motor_x, motor_y)
                    print(f"Pixel color at ({motor_x}, {motor_y}): R={r}, G={g}, B={b}")
                    
                    # If Green channel is dominant, we consider it ON (Green)
                    # You can change this to match the exact RGB of your SCADA green color if needed
                    if g > r + 30 and g > b + 30:
                        print("-> Status: ON (Green detected)")
                        server.sendto(b"MOTOR_ON", address)
                    else:
                        print("-> Status: OFF (Gray detected)")
                        server.sendto(b"MOTOR_OFF", address)
                except Exception as e:
                    print(f"Could not read pixel: {e}")
                    server.sendto(b"CLICKED", address)

                
        except KeyboardInterrupt:
            print("\nShutting down server.")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    start_server()
