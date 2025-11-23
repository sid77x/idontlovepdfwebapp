"""
PDF Microservices Demo
Demonstrates how to test the microservices individually and through the orchestrator
"""

import asyncio
import httpx
import json
from pathlib import Path


class MicroservicesDemo:
    """Demo class for PDF microservices."""
    
    def __init__(self):
        self.orchestrator_url = "http://localhost:8000"
        self.merge_service_url = "http://localhost:8001"
        self.rotate_service_url = "http://localhost:8002"
        self.split_service_url = "http://localhost:8003"
    
    async def test_service_health(self, service_name: str, url: str):
        """Test if a service is healthy."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{url}/health")
                if response.status_code == 200:
                    health_data = response.json()
                    print(f"✅ {service_name}: {health_data['status']} (uptime: {health_data['uptime_seconds']:.1f}s)")
                    return True
                else:
                    print(f"❌ {service_name}: HTTP {response.status_code}")
                    return False
        except Exception as e:
            print(f"❌ {service_name}: Connection failed - {str(e)}")
            return False
    
    async def test_orchestrator_info(self):
        """Test orchestrator root endpoint."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.orchestrator_url}/")
                if response.status_code == 200:
                    info = response.json()
                    print(f"🎯 Orchestrator Info:")
                    print(f"   Service: {info['service']}")
                    print(f"   Version: {info['version']}")
                    print(f"   Status: {info['status']}")
                    print(f"   Registered Services: {info['registered_services']}")
                    print(f"   Available Operations: {len(info['available_operations'])}")
                    return True
                else:
                    print(f"❌ Orchestrator info failed: HTTP {response.status_code}")
                    return False
        except Exception as e:
            print(f"❌ Orchestrator info failed: {str(e)}")
            return False
    
    async def test_service_discovery(self):
        """Test service discovery through orchestrator."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.orchestrator_url}/services")
                if response.status_code == 200:
                    services = response.json()
                    print(f"🔍 Discovered Services: {len(services)}")
                    for service in services:
                        print(f"   - {service['name']} ({service['operation_type']}) at {service['host']}:{service['port']}")
                    return True
                else:
                    print(f"❌ Service discovery failed: HTTP {response.status_code}")
                    return False
        except Exception as e:
            print(f"❌ Service discovery failed: {str(e)}")
            return False
    
    def create_sample_pdf_content(self) -> bytes:
        """Create a simple PDF for testing."""
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from io import BytesIO
        
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.drawString(100, 750, "Sample PDF for Microservices Testing")
        p.drawString(100, 700, "Page 1 Content")
        p.showPage()
        p.drawString(100, 750, "Page 2 Content")  
        p.showPage()
        p.drawString(100, 750, "Page 3 Content")
        p.save()
        
        buffer.seek(0)
        return buffer.getvalue()
    
    async def test_file_upload(self):
        """Test file upload to orchestrator."""
        try:
            # Create sample PDF
            pdf_content = self.create_sample_pdf_content()
            
            async with httpx.AsyncClient() as client:
                files = {"files": ("test_document.pdf", pdf_content, "application/pdf")}
                response = await client.post(f"{self.orchestrator_url}/upload", files=files)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"📤 File Upload Success:")
                    print(f"   Files uploaded: {len(result['files'])}")
                    for file_info in result['files']:
                        print(f"   - {file_info['filename']} ({file_info['size_mb']:.2f} MB)")
                    return True
                else:
                    print(f"❌ File upload failed: HTTP {response.status_code}")
                    print(f"   Response: {response.text}")
                    return False
        except Exception as e:
            print(f"❌ File upload failed: {str(e)}")
            return False
    
    async def test_merge_operation(self):
        """Test PDF merge operation through orchestrator."""
        try:
            # First upload some files
            pdf_content1 = self.create_sample_pdf_content()
            pdf_content2 = self.create_sample_pdf_content()
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Upload files
                files = [
                    ("files", ("doc1.pdf", pdf_content1, "application/pdf")),
                    ("files", ("doc2.pdf", pdf_content2, "application/pdf"))
                ]
                upload_response = await client.post(f"{self.orchestrator_url}/upload", files=files)
                
                if upload_response.status_code != 200:
                    print(f"❌ Upload failed for merge test")
                    return False
                
                # Test merge operation
                merge_request = {
                    "file_names": ["doc1.pdf", "doc2.pdf"],
                    "output_filename": "merged_test.pdf"
                }
                
                merge_response = await client.post(
                    f"{self.orchestrator_url}/merge", 
                    json=merge_request
                )
                
                if merge_response.status_code == 200:
                    result = merge_response.json()
                    print(f"🔗 PDF Merge Success:")
                    print(f"   Success: {result['success']}")
                    print(f"   Message: {result['message']}")
                    print(f"   File Size: {result.get('file_size_mb', 'N/A')} MB")
                    print(f"   Processing Time: {result.get('processing_time_ms', 'N/A')} ms")
                    if result.get('file_url'):
                        print(f"   Download URL: {result['file_url']}")
                    return True
                else:
                    print(f"❌ Merge operation failed: HTTP {merge_response.status_code}")
                    print(f"   Response: {merge_response.text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Merge operation failed: {str(e)}")
            return False
    
    async def test_rotate_operation(self):
        """Test PDF rotate operation."""
        try:
            pdf_content = self.create_sample_pdf_content()
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Upload file
                files = {"files": ("rotate_test.pdf", pdf_content, "application/pdf")}
                upload_response = await client.post(f"{self.orchestrator_url}/upload", files=files)
                
                if upload_response.status_code != 200:
                    print(f"❌ Upload failed for rotate test")
                    return False
                
                # Test rotate operation
                rotate_request = {
                    "file_name": "rotate_test.pdf",
                    "rotation_angle": 90,
                    "pages": None  # Rotate all pages
                }
                
                rotate_response = await client.post(
                    f"{self.orchestrator_url}/rotate", 
                    json=rotate_request
                )
                
                if rotate_response.status_code == 200:
                    result = rotate_response.json()
                    print(f"🔄 PDF Rotate Success:")
                    print(f"   Success: {result['success']}")
                    print(f"   Message: {result['message']}")
                    print(f"   Processing Time: {result.get('processing_time_ms', 'N/A')} ms")
                    return True
                else:
                    print(f"❌ Rotate operation failed: HTTP {rotate_response.status_code}")
                    print(f"   Response: {rotate_response.text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Rotate operation failed: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Run all demo tests."""
        print("🚀 PDF Microservices Demo")
        print("=" * 50)
        
        print("\\n📊 Testing Service Health...")
        health_results = await asyncio.gather(
            self.test_service_health("Orchestrator", self.orchestrator_url),
            self.test_service_health("Merge Service", self.merge_service_url),
            self.test_service_health("Rotate Service", self.rotate_service_url),
            self.test_service_health("Split Service", self.split_service_url),
            return_exceptions=True
        )
        
        if not any(isinstance(r, bool) and r for r in health_results):
            print("\\n❌ No services are running. Please start services with: python start_services.py")
            return False
        
        print("\\n🎯 Testing Orchestrator...")
        if await self.test_orchestrator_info():
            await self.test_service_discovery()
        
        print("\\n📤 Testing File Operations...")
        if await self.test_file_upload():
            print("\\n🔗 Testing PDF Merge...")
            await self.test_merge_operation()
            
            print("\\n🔄 Testing PDF Rotate...")
            await self.test_rotate_operation()
        
        print("\\n" + "=" * 50)
        print("✅ Demo completed! Check the results above.")
        print("\\n💡 Tips:")
        print("   - View API docs at: http://localhost:8000/docs")
        print("   - Check service health at: http://localhost:8000/health")
        print("   - List services at: http://localhost:8000/services")
        
        return True


async def main():
    """Main demo function."""
    try:
        demo = MicroservicesDemo()
        await demo.run_all_tests()
    except KeyboardInterrupt:
        print("\\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"\\n❌ Demo failed: {str(e)}")


if __name__ == "__main__":
    print("Starting PDF Microservices Demo...")
    print("Make sure services are running with: python start_services.py")
    print()
    
    asyncio.run(main())