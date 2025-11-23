#!/usr/bin/env python3
"""
PDF Microservices Shutdown Script
Stops all running microservices and the orchestrator
"""

import os
import sys
import time
import psutil
import socket
from pathlib import Path


class ServiceStopper:
    """Stops all PDF microservices."""
    
    def __init__(self):
        # All service ports
        self.ports = [
            8000,  # Orchestrator
            8001,  # Merge
            8002,  # Rotate
            8003,  # Split
            8004,  # Protect
            8005,  # Compress
            8006,  # Watermark
            8007,  # Page Numbers
            8008,  # Crop
            8009,  # Repair
            8010,  # OCR
            8011,  # PDF to Image
            8012,  # Image to PDF
            8013,  # PDF to Word
            8014,  # Word to PDF
            8015,  # PDF to Excel
            8016,  # Excel to PDF
            8017,  # PDF to HTML
            8018,  # HTML to PDF
            8019,  # PDF to PowerPoint
            8020,  # PowerPoint to PDF
        ]
        
        self.service_names = {
            8000: "Orchestrator",
            8001: "Merge",
            8002: "Rotate",
            8003: "Split",
            8004: "Protect",
            8005: "Compress",
            8006: "Watermark",
            8007: "Page Numbers",
            8008: "Crop",
            8009: "Repair",
            8010: "OCR",
            8011: "PDF to Image",
            8012: "Image to PDF",
            8013: "PDF to Word",
            8014: "Word to PDF",
            8015: "PDF to Excel",
            8016: "Excel to PDF",
            8017: "PDF to HTML",
            8018: "HTML to PDF",
            8019: "PDF to PowerPoint",
            8020: "PowerPoint to PDF",
        }
    
    def find_process_by_port(self, port: int):
        """Find process ID using a specific port."""
        try:
            for conn in psutil.net_connections():
                if conn.laddr.port == port and conn.status == 'LISTEN':
                    return conn.pid
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass
        return None
    
    def stop_process(self, pid: int, name: str) -> bool:
        """Stop a process by PID."""
        try:
            process = psutil.Process(pid)
            process_name = process.name()
            
            print(f"  Stopping {name} (PID: {pid}, Process: {process_name})...")
            
            # Try graceful termination first
            process.terminate()
            
            # Wait up to 5 seconds for process to terminate
            try:
                process.wait(timeout=5)
                print(f"  ✅ {name} stopped gracefully")
                return True
            except psutil.TimeoutExpired:
                # Force kill if still running
                print(f"  ⚠️  {name} didn't stop gracefully, force killing...")
                process.kill()
                process.wait(timeout=2)
                print(f"  🔥 {name} force killed")
                return True
                
        except psutil.NoSuchProcess:
            print(f"  ℹ️  {name} already stopped")
            return True
        except psutil.AccessDenied:
            print(f"  ❌ Access denied to stop {name} (try running as administrator)")
            return False
        except Exception as e:
            print(f"  ❌ Error stopping {name}: {str(e)}")
            return False
    
    def stop_all_services(self) -> dict:
        """Stop all services and return results."""
        print("🛑 Stopping PDF Microservices...")
        print("=" * 50)
        
        results = {
            "stopped": [],
            "not_running": [],
            "failed": []
        }
        
        # Check each port for running services
        for port in self.ports:
            service_name = self.service_names.get(port, f"Service on port {port}")
            pid = self.find_process_by_port(port)
            
            if pid:
                if self.stop_process(pid, service_name):
                    results["stopped"].append(service_name)
                else:
                    results["failed"].append(service_name)
            else:
                results["not_running"].append(service_name)
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 Shutdown Summary:")
        
        if results["stopped"]:
            print(f"\n✅ Stopped ({len(results['stopped'])}):")
            for service in results["stopped"]:
                print(f"  • {service}")
        
        if results["not_running"]:
            print(f"\nℹ️  Not Running ({len(results['not_running'])}):")
            for service in results["not_running"]:
                print(f"  • {service}")
        
        if results["failed"]:
            print(f"\n❌ Failed to Stop ({len(results['failed'])}):")
            for service in results["failed"]:
                print(f"  • {service}")
            print("\n💡 Try running this script as administrator")
        
        success = len(results["failed"]) == 0
        if success:
            print("\n🎉 All services stopped successfully!")
        
        return results
    
    def check_service_status(self) -> dict:
        """Check which services are currently running."""
        print("📊 Checking service status...")
        print("=" * 50)
        
        running_services = []
        stopped_services = []
        
        for port in self.ports:
            service_name = self.service_names.get(port, f"Service on port {port}")
            pid = self.find_process_by_port(port)
            
            if pid:
                try:
                    process = psutil.Process(pid)
                    running_services.append({
                        "name": service_name,
                        "port": port,
                        "pid": pid,
                        "process": process.name()
                    })
                except psutil.NoSuchProcess:
                    stopped_services.append(service_name)
            else:
                stopped_services.append(service_name)
        
        if running_services:
            print(f"\n✅ Running Services ({len(running_services)}):")
            for service in running_services:
                print(f"  • {service['name']} (port {service['port']}, PID: {service['pid']})")
        else:
            print("\nℹ️  No services are currently running")
        
        if stopped_services:
            print(f"\n⚪ Stopped Services ({len(stopped_services)}):")
            for service in stopped_services:
                print(f"  • {service}")
        
        return {
            "running": running_services,
            "stopped": stopped_services
        }


def main():
    """Main entry point."""
    print("📄 PDF Microservices Stopper")
    print("=" * 50)
    
    stopper = ServiceStopper()
    
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        # Just show status, don't stop
        stopper.check_service_status()
    else:
        # Stop all services
        results = stopper.stop_all_services()
        
        # Return exit code based on results
        if results["failed"]:
            return 1
        return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)
