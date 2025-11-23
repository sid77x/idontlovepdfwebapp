#!/usr/bin/env python3
"""
PDF Microservices Launcher
Starts all microservices and the orchestrator
"""

import os
import sys
import time
import signal
import subprocess
import threading
from pathlib import Path


class ServiceManager:
    """Manages PDF microservices."""
    
    def __init__(self):
        self.services = {}
        self.orchestrator_process = None
        self.running = False
        
        # Service configurations: (script_name, port)
        self.service_configs = {
            "merge": ("merge_service.py", 8001),
            "rotate": ("rotate_service.py", 8002), 
            "split": ("split_service.py", 8003),
            "protect": ("protect_service.py", 8004),
            "compress": ("compress_service.py", 8005),
            "watermark": ("watermark_service.py", 8006),
            # "page_numbers": ("page_numbers_service.py", 8007),  # Not implemented yet
            # "crop": ("crop_service.py", 8008),  # Not implemented yet
            # "repair": ("repair_service.py", 8009),  # Not implemented yet
            "ocr": ("ocr_service.py", 8010),
            "pdf_to_image": ("pdf_to_image_service.py", 8011),
            "image_to_pdf": ("image_to_pdf_service.py", 8012),
            # "pdf_to_word": ("pdf_to_word_service.py", 8013),  # Not implemented yet
            # "word_to_pdf": ("word_to_pdf_service.py", 8014),  # Not implemented yet
            # "pdf_to_excel": ("pdf_to_excel_service.py", 8015),  # Not implemented yet
            # "excel_to_pdf": ("excel_to_pdf_service.py", 8016),  # Not implemented yet
            # "pdf_to_html": ("pdf_to_html_service.py", 8017),  # Not implemented yet
            # "html_to_pdf": ("html_to_pdf_service.py", 8018),  # Disabled - GTK issues on Windows
            # "pdf_to_powerpoint": ("pdf_to_powerpoint_service.py", 8019),  # Not implemented yet
            # "powerpoint_to_pdf": ("powerpoint_to_pdf_service.py", 8020),  # Not implemented yet
        }
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print(f"\\nReceived signal {signum}. Shutting down services...")
        self.stop_all_services()
        sys.exit(0)
    
    def start_service(self, name: str, script_path: str, port: int) -> bool:
        """Start a single microservice."""
        try:
            print(f"Starting {name} service on port {port}...")
            
            # Change to services directory
            services_dir = Path(__file__).parent / "services"
            
            # Start service process
            process = subprocess.Popen(
                [sys.executable, script_path],
                cwd=services_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.services[name] = {
                "process": process,
                "port": port,
                "script": script_path
            }
            
            # Wait a moment to check if it started successfully
            time.sleep(2)
            
            if process.poll() is None:
                print(f"✅ {name} service started successfully (PID: {process.pid})")
                return True
            else:
                stdout, stderr = process.communicate()
                print(f"❌ {name} service failed to start:")
                if stderr:
                    print(f"Error: {stderr.decode()}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start {name} service: {str(e)}")
            return False
    
    def start_orchestrator(self) -> bool:
        """Start the orchestrator service."""
        try:
            print("Starting PDF Orchestrator on port 8000...")
            
            # Change to orchestrator directory
            orchestrator_dir = Path(__file__).parent / "orchestrator"
            
            # Start orchestrator process
            self.orchestrator_process = subprocess.Popen(
                [sys.executable, "main.py"],
                cwd=orchestrator_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait a moment to check if it started successfully
            time.sleep(3)
            
            if self.orchestrator_process.poll() is None:
                print(f"✅ Orchestrator started successfully (PID: {self.orchestrator_process.pid})")
                return True
            else:
                stdout, stderr = self.orchestrator_process.communicate()
                print("❌ Orchestrator failed to start:")
                if stderr:
                    print(f"Error: {stderr.decode()}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start orchestrator: {str(e)}")
            return False
    
    def start_all_services(self) -> bool:
        """Start all microservices and orchestrator."""
        print("🚀 Starting PDF Microservices...")
        print(f"Working directory: {Path(__file__).parent}")
        
        failed_services = []
        
        # Start individual services
        for name, (script, port) in self.service_configs.items():
            if not self.start_service(name, script, port):
                failed_services.append(name)
        
        # Start orchestrator if we have at least some services running
        if len(self.services) > 0:
            time.sleep(2)  # Give services time to fully initialize
            orchestrator_success = self.start_orchestrator()
        else:
            orchestrator_success = False
        
        if orchestrator_success:
            self.running = True
            if failed_services:
                print(f"\\n⚠️ Some services failed to start: {', '.join(failed_services)}")
            print("\\n🎉 Available services started successfully!")
            print("\\n📊 Service Status:")
            print(f"  • Orchestrator: http://localhost:8000")
            for name, config in self.services.items():
                print(f"  • {name.title()}: http://localhost:{config['port']}")
            print("\\n📖 API Documentation:")
            print("  • Orchestrator Docs: http://localhost:8000/docs")
            print("\\n💡 Use Ctrl+C to stop all services")
            return True
        else:
            print("\\n❌ Failed to start orchestrator. Cleaning up...")
            self.stop_all_services()
            return False
    
    def stop_service(self, name: str):
        """Stop a single service."""
        if name in self.services:
            service = self.services[name]
            try:
                service["process"].terminate()
                service["process"].wait(timeout=5)
                print(f"✅ Stopped {name} service")
            except subprocess.TimeoutExpired:
                service["process"].kill()
                print(f"🔥 Force killed {name} service")
            except Exception as e:
                print(f"❌ Error stopping {name} service: {str(e)}")
            
            del self.services[name]
    
    def stop_orchestrator(self):
        """Stop the orchestrator."""
        if self.orchestrator_process:
            try:
                self.orchestrator_process.terminate()
                self.orchestrator_process.wait(timeout=5)
                print("✅ Stopped orchestrator")
            except subprocess.TimeoutExpired:
                self.orchestrator_process.kill()
                print("🔥 Force killed orchestrator")
            except Exception as e:
                print(f"❌ Error stopping orchestrator: {str(e)}")
            
            self.orchestrator_process = None
    
    def stop_all_services(self):
        """Stop all running services."""
        print("\\n🛑 Stopping all services...")
        
        # Stop orchestrator first
        self.stop_orchestrator()
        
        # Stop individual services
        for name in list(self.services.keys()):
            self.stop_service(name)
        
        self.running = False
        print("✅ All services stopped")
    
    def check_service_status(self) -> dict:
        """Check status of all services."""
        status = {
            "orchestrator": False,
            "services": {}
        }
        
        # Check orchestrator
        if self.orchestrator_process and self.orchestrator_process.poll() is None:
            status["orchestrator"] = True
        
        # Check services
        for name, service in self.services.items():
            status["services"][name] = service["process"].poll() is None
        
        return status
    
    def monitor_services(self):
        """Monitor services and restart if needed."""
        while self.running:
            time.sleep(10)
            
            status = self.check_service_status()
            
            # Check for failed services
            for name, is_running in status["services"].items():
                if not is_running:
                    print(f"⚠️  {name} service has stopped. Restarting...")
                    script, port = self.service_configs[name]
                    self.stop_service(name)  # Clean up
                    self.start_service(name, script, port)
            
            # Check orchestrator
            if not status["orchestrator"] and self.running:
                print("⚠️  Orchestrator has stopped. Restarting...")
                self.stop_orchestrator()  # Clean up
                self.start_orchestrator()
    
    def run(self):
        """Run the service manager."""
        if not self.start_all_services():
            return False
        
        # Start monitoring in background thread
        monitor_thread = threading.Thread(target=self.monitor_services)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        
        return True


def main():
    """Main entry point."""
    print("📄 PDF Microservices Manager")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    
    # Check if in correct directory
    current_dir = Path(__file__).parent
    if not (current_dir / "services").exists() or not (current_dir / "orchestrator").exists():
        print("❌ Services or orchestrator directory not found")
        print(f"Current directory: {current_dir}")
        print("Make sure you're running this script from the microservices directory")
        return False
    
    # Create service manager and run
    manager = ServiceManager()
    return manager.run()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)