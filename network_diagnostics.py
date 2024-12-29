import tkinter as tk
import subprocess
import socket
import platform
import requests
import json
import ipaddress
import netifaces

from utilities import log_output

class NetworkDiagnosticsExecutor:
    def __init__(self, text_area):
        self.text_area = text_area

    def log(self, message):
        """Utility method to log messages to the text area."""
        if hasattr(self.text_area, 'insert'):
            self.text_area.config(state='normal')
            self.text_area.insert(tk.END, message + "\n")
            self.text_area.config(state='disabled')
            self.text_area.see(tk.END)
        else:
            print(message)

    def network_info(self):
        """Get comprehensive network information."""
        try:
            # Get public IP
            public_ip = self.get_public_ip()
            
            # Get local network details
            local_ip = self.get_local_ip()
            
            # DNS servers
            dns_servers = self.get_dns_servers()
            
            # Network interfaces
            interfaces = self.get_network_interfaces()
            
            # Compile full report
            report = {
                "Public IP": public_ip,
                "Local IP": local_ip,
                "DNS Servers": dns_servers,
                "Network Interfaces": interfaces
            }
            
            return json.dumps(report, indent=2)
        except Exception as e:
            return f"Network info error: {e}"

    def get_public_ip(self):
        """Retrieve public IP address."""
        try:
            response = requests.get('https://api.ipify.org?format=json')
            return response.json()['ip']
        except Exception:
            try:
                # Fallback method
                return requests.get('https://httpbin.org/ip').json()['origin']
            except Exception:
                return "Unable to retrieve public IP"

    def get_local_ip(self):
        """Get local IP address."""
        try:
            # Create a temporary socket to get local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception:
            return "Unable to retrieve local IP"

    def get_dns_servers(self):
        """Retrieve DNS servers."""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(['ipconfig', '/all'], 
                                        capture_output=True, 
                                        text=True, 
                                        shell=True)
                return self._parse_windows_dns(result.stdout)
            elif platform.system() == "Linux":
                with open('/etc/resolv.conf', 'r') as f:
                    return [line.split()[1] for line in f if line.startswith('nameserver')]
            elif platform.system() == "Darwin":  # macOS
                result = subprocess.run(['scutil', '--dns'], 
                                        capture_output=True, 
                                        text=True)
                return self._parse_macos_dns(result.stdout)
            return []
        except Exception:
            return ["Unable to retrieve DNS servers"]

    def _parse_windows_dns(self, output):
        """Parse DNS servers from Windows ipconfig output."""
        dns_servers = []
        for line in output.split('\n'):
            if 'DNS Servers' in line:
                # Extract IP addresses
                ips = [part.strip() for part in line.split(':')[1].split()]
                dns_servers.extend([ip for ip in ips if self._is_valid_ip(ip)])
        return dns_servers

    def _parse_macos_dns(self, output):
        """Parse DNS servers from macOS scutil output."""
        dns_servers = []
        for line in output.split('\n'):
            if 'nameserver' in line:
                ip = line.split(':')[1].strip()
                if self._is_valid_ip(ip):
                    dns_servers.append(ip)
        return dns_servers

    def _is_valid_ip(self, ip):
        """Validate IP address."""
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

    def get_network_interfaces(self):
        """Get details of network interfaces."""
        try:
            
            interfaces = {}
            
            for interface in netifaces.interfaces():
                try:
                    # Get IP addresses
                    addrs = netifaces.ifaddresses(interface)
                    
                    # IPv4 address
                    ipv4 = addrs.get(netifaces.AF_INET, [{}])[0].get('addr', 'N/A')
                    
                    # MAC address
                    mac = addrs.get(netifaces.AF_LINK, [{}])[0].get('addr', 'N/A')
                    
                    interfaces[interface] = {
                        'IPv4': ipv4,
                        'MAC': mac
                    }
                except Exception:
                    pass
            
            return interfaces
        except ImportError:
            return "netifaces module not installed"

    def advanced_traceroute(self, host):
        """Perform an advanced traceroute with additional information."""
        try:
            # Use platform-specific traceroute
            if platform.system().lower() == "windows":
                result = subprocess.run(['tracert', '-d', host], 
                                        capture_output=True, 
                                        text=True)
            else:
                result = subprocess.run(['traceroute', '-n', host], 
                                        capture_output=True, 
                                        text=True)
            
            # Parse and enhance traceroute output
            enhanced_trace = self._enhance_traceroute(result.stdout)
            return enhanced_trace
        except Exception as e:
            return f"Advanced traceroute error: {e}"

    def _enhance_traceroute(self, traceroute_output):
        """Enhance traceroute output with additional information."""
        enhanced_lines = []
        for line in traceroute_output.split('\n'):
            try:
                # Try to resolve hostnames for IP addresses
                parts = line.split()
                for i, part in enumerate(parts):
                    if self._is_valid_ip(part):
                        try:
                            hostname = socket.gethostbyaddr(part)[0]
                            parts[i] = f"{part} ({hostname})"
                        except (socket.herror, socket.gaierror):
                            pass
                enhanced_lines.append(' '.join(parts))
            except Exception:
                enhanced_lines.append(line)
        
        return '\n'.join(enhanced_lines)

    def port_scan(self, host, start_port=1, end_port=1024):
        """
        Perform a comprehensive port scan with service detection.
        
        Known ports reference:
        - 20/21: FTP
        - 22: SSH
        - 23: Telnet
        - 25: SMTP
        - 80: HTTP
        - 443: HTTPS
        - 3306: MySQL
        - 5432: PostgreSQL
        """
        open_ports = []
        common_ports = {
            20: 'FTP (Data)', 
            21: 'FTP (Control)', 
            22: 'SSH', 
            23: 'Telnet', 
            25: 'SMTP', 
            80: 'HTTP', 
            443: 'HTTPS',
            3306: 'MySQL',
            5432: 'PostgreSQL'
        }

        for port in range(start_port, min(end_port + 1, 65536)):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.1)
            
            try:
                result = sock.connect_ex((host, port))
                if result == 0:
                    service = common_ports.get(port, 'Unknown Service')
                    open_ports.append(f"Port {port}: {service}")
            except Exception:
                pass
            finally:
                sock.close()
        
        return open_ports if open_ports else ["No open ports found"]

def execute_network_command(command, text_area):
    """
    Execute advanced network diagnostic commands with improved error handling.
    
    Supported commands:
    - network-info: Get comprehensive network details
    - traceroute <host>: Advanced traceroute
    - portscan <host>: Scan ports on a host
    """
    try:
        executor = NetworkDiagnosticsExecutor(text_area)
        
        # Split command into parts
        parts = command.split()
        
        if parts[0] == 'network-info':
            result = executor.network_info()
            log_output(text_area, "Network Info:\n" + result)
        
        elif parts[0] == 'traceroute' and len(parts) > 1:
            host = parts[1]
            try:
                result = executor.advanced_traceroute(host)
                log_output(text_area, f"Traceroute to {host}:\n{result}")
            except Exception as trace_error:
                log_output(text_area, f"Traceroute error: Unable to trace route to {host}. {str(trace_error)}")
        
        elif parts[0] == 'portscan' and len(parts) > 1:
            host = parts[1]
            try:
                # Validate host
                socket.gethostbyname(host)
                
                # Optional: specify port range
                start_port = int(parts[2]) if len(parts) > 2 else 1
                end_port = int(parts[3]) if len(parts) > 3 else 1024
                
                # Validate port range
                if start_port < 1 or end_port > 65535 or start_port > end_port:
                    log_output(text_area, "Invalid port range. Must be between 1 and 65535.")
                    return
                
                result = executor.port_scan(host, start_port, end_port)
                
                if result:
                    log_output(text_area, f"Port scan results for {host}:\n" + "\n".join(result))
                else:
                    log_output(text_area, f"No open ports found on {host}.")
            
            except socket.gaierror:
                log_output(text_area, f"Error: Could not resolve hostname {host}")
            except Exception as scan_error:
                log_output(text_area, f"Port scan error: {str(scan_error)}")
        
        else:
            log_output(text_area, "Invalid network command. Use:\n"
                       "- network-info\n"
                       "- traceroute <host>\n"
                       "- portscan <host> [start_port] [end_port]")
    
    except Exception as e:
        log_output(text_area, f"Unexpected error in network command: {str(e)}")