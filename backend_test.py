#!/usr/bin/env python3
"""
INEI Inventory Management System - Backend API Tests
Tests all API endpoints for the inventory management system
"""

import requests
import sys
import json
from datetime import datetime
import io
import tempfile
import pandas as pd

class INEIInventoryTester:
    def __init__(self, base_url="https://002aece6-6576-4ac8-938a-8c9fe8a71844.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_data = []

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'} if not files else {}
        
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files)
                else:
                    response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            
            if success:
                print(f"   Status: {response.status_code} ✅")
                try:
                    response_data = response.json() if response.content else {}
                    if response_data:
                        print(f"   Response keys: {list(response_data.keys())}")
                except:
                    print(f"   Response: Binary/Non-JSON content")
                self.log_test(name, True)
                return True, response
            else:
                print(f"   Status: {response.status_code} (expected {expected_status}) ❌")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Error: {response.text}")
                self.log_test(name, False, f"Status {response.status_code}")
                return False, response

        except Exception as e:
            print(f"   Exception: {str(e)} ❌")
            self.log_test(name, False, str(e))
            return False, None

    def test_root_endpoint(self):
        """Test root API endpoint"""
        return self.run_test("Root API Endpoint", "GET", "", 200)

    def test_stats_endpoint(self):
        """Test dashboard statistics endpoint"""
        success, response = self.run_test("Dashboard Statistics", "GET", "stats", 200)
        if success:
            try:
                data = response.json()
                required_fields = ['total_items', 'items_bien', 'items_mal_estado', 
                                 'items_en_reparacion', 'items_robados', 'devices_by_type', 'recent_repairs']
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    print(f"   Missing fields: {missing_fields}")
                    return False
                print(f"   Stats: Total={data['total_items']}, Good={data['items_bien']}, Bad={data['items_mal_estado']}")
            except Exception as e:
                print(f"   Error parsing stats: {e}")
                return False
        return success

    def test_create_inventory_item(self):
        """Test creating inventory items"""
        # Test valid item
        test_item = {
            "persona": "Juan Pérez Test",
            "dni": "12345678",
            "dispositivo": "Tablet Samsung",
            "control_patrimonial": "PAT001",
            "modelo": "Galaxy Tab A8",
            "numero_serie": "SN123456789",
            "imei": "123456789012345",
            "funda_tablet": True,
            "plan_datos": False,
            "power_tech": True,
            "telefono": "987654321",
            "correo_personal": "juan.perez@gmail.com",
            "estado": "bien",
            "robado": False,
            "motivo_reparacion": ""
        }
        
        success, response = self.run_test("Create Valid Inventory Item", "POST", "inventory", 201, test_item)
        if success:
            try:
                data = response.json()
                self.test_data.append(data)
                print(f"   Created item ID: {data.get('id')}")
            except:
                pass
        
        # Test invalid DNI
        invalid_item = test_item.copy()
        invalid_item["dni"] = "123"  # Invalid DNI
        invalid_item["persona"] = "Invalid DNI Test"
        
        self.run_test("Create Item with Invalid DNI", "POST", "inventory", 422, invalid_item)
        
        # Test duplicate DNI
        duplicate_item = test_item.copy()
        duplicate_item["persona"] = "Duplicate Test"
        
        self.run_test("Create Duplicate DNI Item", "POST", "inventory", 400, duplicate_item)
        
        return success

    def test_get_inventory(self):
        """Test getting inventory list"""
        success, response = self.run_test("Get Inventory List", "GET", "inventory", 200)
        if success:
            try:
                data = response.json()
                print(f"   Found {len(data)} inventory items")
            except:
                pass
        return success

    def test_get_inventory_item(self):
        """Test getting specific inventory item"""
        if not self.test_data:
            print("⚠️  No test data available for individual item test")
            return False
            
        item_id = self.test_data[0].get('id')
        return self.run_test("Get Specific Inventory Item", "GET", f"inventory/{item_id}", 200)[0]

    def test_update_inventory_item(self):
        """Test updating inventory item"""
        if not self.test_data:
            print("⚠️  No test data available for update test")
            return False
            
        item_id = self.test_data[0].get('id')
        update_data = {
            "estado": "mal estado",
            "motivo_reparacion": "Pantalla rota"
        }
        
        return self.run_test("Update Inventory Item", "PUT", f"inventory/{item_id}", 200, update_data)[0]

    def test_search_inventory(self):
        """Test inventory search functionality"""
        # Search by persona
        search_data = {"persona": "Juan"}
        success1, _ = self.run_test("Search by Persona", "POST", "inventory/search", 200, search_data)
        
        # Search by estado
        search_data = {"estado": "bien"}
        success2, _ = self.run_test("Search by Estado", "POST", "inventory/search", 200, search_data)
        
        # Search by robado status
        search_data = {"robado": False}
        success3, _ = self.run_test("Search by Robado Status", "POST", "inventory/search", 200, search_data)
        
        return success1 and success2 and success3

    def test_create_repair_item(self):
        """Test creating repair items"""
        repair_item = {
            "persona": "Juan Pérez Test",
            "dni": "12345678",
            "dispositivo": "Tablet Samsung",
            "modelo": "Galaxy Tab A8",
            "motivo_reparacion": "Pantalla rota durante censo"
        }
        
        return self.run_test("Create Repair Item", "POST", "repairs", 201, repair_item)[0]

    def test_get_repairs(self):
        """Test getting repairs list"""
        success, response = self.run_test("Get Repairs List", "GET", "repairs", 200)
        if success:
            try:
                data = response.json()
                print(f"   Found {len(data)} repair items")
            except:
                pass
        return success

    def test_excel_export(self):
        """Test Excel export functionality"""
        success, response = self.run_test("Excel Export", "GET", "inventory/export/excel", 200)
        if success:
            # Check if response is Excel file
            content_type = response.headers.get('content-type', '')
            if 'spreadsheet' in content_type or 'excel' in content_type:
                print(f"   Excel file size: {len(response.content)} bytes")
                return True
            else:
                print(f"   Unexpected content type: {content_type}")
                return False
        return success

    def test_excel_import(self):
        """Test Excel import functionality"""
        # Create a sample Excel file
        try:
            # Create sample data
            sample_data = {
                'Persona': ['María García Test', 'Carlos López Test'],
                'DNI': ['87654321', '11223344'],
                'Dispositivo': ['Laptop HP', 'Tablet Lenovo'],
                'Control Patrimonial': ['PAT002', 'PAT003'],
                'Modelo': ['HP Pavilion', 'Tab M10'],
                'Número de Serie': ['SN987654321', 'SN111222333'],
                'IMEI': ['987654321098765', '111222333444555'],
                'Funda Tablet': ['No', 'Sí'],
                'Plan de Datos': ['Sí', 'No'],
                'Power Tech': ['No', 'Sí'],
                'Teléfono': ['999888777', '555444333'],
                'Correo Personal': ['maria.garcia@yahoo.com', 'carlos.lopez@outlook.com'],
                'Estado': ['bien', 'mal estado'],
                'Robado': ['No', 'No'],
                'Motivo Reparación': ['', 'Batería defectuosa']
            }
            
            df = pd.DataFrame(sample_data)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
                df.to_excel(tmp_file.name, index=False)
                tmp_file_path = tmp_file.name
            
            # Upload the file
            with open(tmp_file_path, 'rb') as f:
                files = {'file': ('test_import.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
                success, response = self.run_test("Excel Import", "POST", "inventory/import/excel", 200, files=files)
            
            if success:
                try:
                    data = response.json()
                    print(f"   Import result: {data.get('message', 'No message')}")
                    print(f"   Imported count: {data.get('imported_count', 0)}")
                    if data.get('errors'):
                        print(f"   Errors: {len(data['errors'])}")
                except:
                    pass
            
            return success
            
        except Exception as e:
            print(f"   Error creating test Excel file: {e}")
            return False

    def test_delete_operations(self):
        """Test delete operations"""
        # Test delete by DNI
        success1, _ = self.run_test("Delete Person by DNI", "DELETE", "inventory/87654321", 200)
        
        # Test delete all (be careful with this in production!)
        # success2, _ = self.run_test("Delete All Inventory", "DELETE", "inventory", 200)
        
        return success1  # and success2

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting INEI Inventory Management System Backend Tests")
        print(f"📡 Testing API at: {self.api_url}")
        print("=" * 60)
        
        # Basic connectivity tests
        self.test_root_endpoint()
        self.test_stats_endpoint()
        
        # Inventory CRUD tests
        self.test_create_inventory_item()
        self.test_get_inventory()
        self.test_get_inventory_item()
        self.test_update_inventory_item()
        self.test_search_inventory()
        
        # Repair management tests
        self.test_create_repair_item()
        self.test_get_repairs()
        
        # Excel functionality tests
        self.test_excel_export()
        self.test_excel_import()
        
        # Delete operations tests
        self.test_delete_operations()
        
        # Final results
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed! Backend API is working correctly.")
            return 0
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed. Check the issues above.")
            return 1

def main():
    """Main test runner"""
    tester = INEIInventoryTester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())