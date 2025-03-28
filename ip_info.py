import subprocess
import requests
import socket
import platform
import concurrent.futures
import re
import whois
import os
from colorama import init, Fore, Style

# Inizializza colorama
init(autoreset=True)

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    banner = f"""
{Fore.CYAN}{Style.BRIGHT}
  ___  ____  _____      _    ___ _____ _   _ ___ _     
 |_ _|/ ___|| ____|    / \  |_ _|_   _| | | |_ _| |    
  | | \___ \|  _|     / _ \  | |  | | | |_| || || |    
  | |  ___) | |___   / ___ \ | |  | | |  _  || || |___ 
 |___||____/|_____| /_/   \_\___| |_| |_| |_||_||_____|
 
             IP Toolkit - Network Utility
{Style.RESET_ALL}
"""
    print(banner)

def print_error(message):
    print(f"{Fore.RED}Error: {message}{Style.RESET_ALL}")

def ping_ip(ip_address):
    try:
        print(f"{Fore.YELLOW}PINGING {ip_address}{Style.RESET_ALL}")
        result = subprocess.run(['ping', ip_address], capture_output=True, text=True, timeout=10)
        print(result.stdout)
    except subprocess.TimeoutExpired:
        print_error("Timeout expired. No response received.")
    except Exception as e:
        print_error(str(e))

def format_timezone(timezone_info):
    if timezone_info:
        return f"{timezone_info.get('name')} (UTC{timezone_info.get('offset')})"
    else:
        return "Not available"

def get_ip_information(ip_address):
    try:
        api_key = '2cae345f9d5e481ba7c306df400afbb1' 
        url = f"https://api.ipgeolocation.io/ipgeo?apiKey={api_key}&ip={ip_address}"
        response = requests.get(url).json()
        
        print(f"{Fore.YELLOW}IP INFORMATION for {ip_address}{Style.RESET_ALL}")
        ip_info = {
            "IP Address": response.get("ip"),
            "Continent": f"{response.get('continent_name')} ({response.get('continent_code')})",
            "Country": f"{response.get('country_name')} ({response.get('country_code3')})",
            "Region": response.get("state_prov"),
            "City": response.get("city"),
            "Postal Code": response.get("zipcode") if response.get("zipcode") else "Not available",
            "Latitude": response.get("latitude"),
            "Longitude": response.get("longitude"),
            "Time Zone": format_timezone(response.get('time_zone')),
            "ISP": response.get("isp"),
            "Organization": response.get("organization"),
            "Domain": response.get("domain") if response.get("domain") else "Not available",
            "ASN": response.get("asn"),
            "Altitude": response.get("altitude") if response.get("altitude") else "Not available",
            "Threat Level": response.get("threat", {}).get("is_tor", "Not available")
        }

        for key, value in ip_info.items():
            if value:
                print(f"{Fore.GREEN}{key}: {value}{Style.RESET_ALL}")

    except Exception as e:
        print_error(str(e))

def traceroute_ip(ip_address, max_hops=30, timeout=5):
    try:
        if platform.system().lower() == "windows":
            command = ['tracert', '-h', str(max_hops), '-w', str(timeout * 1000), ip_address]
        else:
            command = ['traceroute', '-m', str(max_hops), '-w', str(timeout), ip_address]
        
        print(f"{Fore.YELLOW}TRACEROUTE {ip_address}{Style.RESET_ALL}")
        result = subprocess.run(command, capture_output=True, text=True)
        print(result.stdout)

    except subprocess.CalledProcessError as cpe:
        print_error(f"Command failed with error: {cpe}")
    except FileNotFoundError:
        print_error("Traceroute command not found. Please ensure it is installed on your system.")
    except Exception as e:
        print_error(str(e))

def reverse_dns_lookup(ip_address, dns_server=None):
    try:
        command = ['nslookup', ip_address]
        if dns_server:
            command.append(dns_server)
        
        print(f"{Fore.YELLOW}REVERSE DNS LOOKUP {ip_address}{Style.RESET_ALL}")
        result = subprocess.run(command, capture_output=True, text=True)
        print(result.stdout)

    except subprocess.CalledProcessError as cpe:
        print_error(f"Command failed with error: {cpe}")
    except FileNotFoundError:
        print_error("nslookup command not found. Please ensure it is installed on your system.")
    except Exception as e:
        print_error(str(e))

def scan_port(ip_address, port, timeout=1):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip_address, port))
        sock.close()
        return port if result == 0 else None
    except Exception as e:
        print_error(f"Error scanning port {port}: {e}")
        return None

def port_scan(ip_address, start_port=1, end_port=1024, timeout=1, max_workers=100):
    open_ports = []
    print(f"{Fore.YELLOW}Scanning ports on {ip_address} from {start_port} to {end_port}...{Style.RESET_ALL}")
    
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(scan_port, ip_address, port, timeout): port for port in range(start_port, end_port + 1)}
            for future in concurrent.futures.as_completed(futures):
                port = futures[future]
                if future.result():
                    open_ports.append(port)
                    print(f"{Fore.GREEN}Port {port} is open{Style.RESET_ALL}")
        
        print(f"{Fore.YELLOW}OPEN PORTS ON {ip_address}:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{open_ports}{Style.RESET_ALL}")
    
    except Exception as e:
        print_error(f"An error occurred during port scanning: {e}")

def whois_lookup(ip_address):
    try:
        if not re.match(r"^\d{1,3}(\.\d{1,3}){3}$", ip_address):
            print_error("Invalid IP address format.")
            return

        result = whois.whois(ip_address)
        print(f"{Fore.YELLOW}WHOIS LOOKUP {ip_address}{Style.RESET_ALL}")
        
        if result:
            for key, value in result.items():
                if value:
                    if isinstance(value, list):
                        for item in value:
                            print(f"{Fore.GREEN}{key}: {item}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.GREEN}{key}: {value}{Style.RESET_ALL}")
        else:
            print("No WHOIS information found for the IP address.")

    except whois.parser.PywhoisError as e:
        print_error(f"WHOIS lookup failed: {e}")
    except Exception as e:
        print_error(str(e))

def blacklist_check(ip_address):
    try:
        headers = {
            'Key': 'your_abuseipdb_api_key',
            'Accept': 'application/json'
        }
        url = f"https://api.abuseipdb.com/api/v2/check?ipAddress={ip_address}"
        response = requests.get(url, headers=headers).json()
        print(f"{Fore.YELLOW}BLACKLIST CHECK {ip_address}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{response}{Style.RESET_ALL}")
    except Exception as e:
        print_error(str(e))

def asn_info(ip_address):
    try:
        url = f"https://api.iptoasn.com/v1/as/ip/{ip_address}"
        response = requests.get(url).json()

        print(f"{Fore.YELLOW}ASN INFORMATION {ip_address}{Style.RESET_ALL}")
        asn_info_to_display = {
            "IP Range": response.get("announced"),
            "ASN": response.get("as_number"),
            "ASN Organization": response.get("as_description"),
            "Country": response.get("country_code"),
            "Created": response.get("allocated") if response.get("allocated") else "Unknown",
            "Last Updated": response.get("updated") if response.get("updated") else "Unknown",
        }

        for key, value in asn_info_to_display.items():
            print(f"{Fore.GREEN}{key}: {value}{Style.RESET_ALL}")

    except requests.RequestException as e:
        print_error(f"Error fetching ASN information: {e}")
    except Exception as e:
        print_error(str(e))

def main():
    clear()
    print_banner()
    
    menu = f"""
{Fore.BLUE}{Style.BRIGHT}1.{Style.RESET_ALL} Ping IP
{Fore.BLUE}{Style.BRIGHT}2.{Style.RESET_ALL} Get IP Information
{Fore.BLUE}{Style.BRIGHT}3.{Style.RESET_ALL} Traceroute IP
{Fore.BLUE}{Style.BRIGHT}4.{Style.RESET_ALL} Reverse DNS Lookup
{Fore.BLUE}{Style.BRIGHT}5.{Style.RESET_ALL} Port Scan
{Fore.BLUE}{Style.BRIGHT}6.{Style.RESET_ALL} WHOIS Lookup
{Fore.BLUE}{Style.BRIGHT}7.{Style.RESET_ALL} Blacklist Check
{Fore.BLUE}{Style.BRIGHT}8.{Style.RESET_ALL} ASN Information
{Fore.BLUE}{Style.BRIGHT}9.{Style.RESET_ALL} Exit
"""
    while True:
        print(menu)
        choice = input(f"{Fore.MAGENTA}Enter your choice: {Style.RESET_ALL}").strip()
        
        if choice == '1':
            ip_address = input(f"{Fore.MAGENTA}Enter IP address to ping: {Style.RESET_ALL}").strip()
            ping_ip(ip_address)
        elif choice == '2':
            ip_address = input(f"{Fore.MAGENTA}Enter IP address to get information for: {Style.RESET_ALL}").strip()
            get_ip_information(ip_address)
        elif choice == '3':
            ip_address = input(f"{Fore.MAGENTA}Enter IP address for traceroute: {Style.RESET_ALL}").strip()
            traceroute_ip(ip_address)
        elif choice == '4':
            ip_address = input(f"{Fore.MAGENTA}Enter IP address for reverse DNS lookup: {Style.RESET_ALL}").strip()
            reverse_dns_lookup(ip_address)
        elif choice == '5':
            ip_address = input(f"{Fore.MAGENTA}Enter IP address for port scan: {Style.RESET_ALL}").strip()
            try:
                start_port = int(input(f"{Fore.MAGENTA}Enter starting port number: {Style.RESET_ALL}").strip())
                end_port = int(input(f"{Fore.MAGENTA}Enter ending port number: {Style.RESET_ALL}").strip())
            except ValueError:
                print_error("Port numbers must be integers.")
                continue
            port_scan(ip_address, start_port, end_port)
        elif choice == '6':
            ip_address = input(f"{Fore.MAGENTA}Enter IP address for WHOIS lookup: {Style.RESET_ALL}").strip()
            whois_lookup(ip_address)
        elif choice == '7':
            ip_address = input(f"{Fore.MAGENTA}Enter IP address for blacklist check: {Style.RESET_ALL}").strip()
            blacklist_check(ip_address)
        elif choice == '8':
            ip_address = input(f"{Fore.MAGENTA}Enter IP address for ASN information: {Style.RESET_ALL}").strip()
            asn_info(ip_address)
        elif choice == '9':
            print(f"{Fore.CYAN}Exiting...{Style.RESET_ALL}")
            break
        else:
            print_error("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
