import datetime
import os
from typing import Dict
from resources import Resource, ResourceRegistry
from logger import Logger

# Main application
class CloudConnect:
    """Main app - handles CLI and resource management"""
    def __init__(self):
        self.resources: Dict[str, Resource] = {}
        self.logger = Logger()

    def _get_resource(self, name: str) -> Resource:
        if name not in self.resources:
            raise KeyError(f"Resource '{name}' not found.")
        return self.resources[name]

    def create_resource(self):
        registered_types = ResourceRegistry.get_registered_types()
        print("Select resource type:")
        for i, r_type in enumerate(registered_types):
            print(f"{i + 1}. {r_type}")

        try:
            choice_idx = int(input("Choice: ")) - 1
            if not 0 <= choice_idx < len(registered_types):
                raise IndexError()
            selected_type = registered_types[choice_idx]
            name = input("Enter resource name: ")
            if name in self.resources:
                print("Error: A resource with this name already exists.")
                return

            config = {'name': name}
            if selected_type == "AppService":
                config['runtime'] = input("Select runtime (python / nodejs / dotnet): ")
                config['region'] = input("Select region (EastUS / WestEurope / CentralIndia): ")
                config['replica_count'] = int(input("Select replica count (1 / 2 / 3): "))
            elif selected_type == "StorageAccount":
                config['encryption_enabled'] = input("Enable encryption? (true / false): ").lower() == 'true'
                config['access_key'] = input("Enter access key: ")
                config['max_size_gb'] = int(input("Enter max size (GB): "))
            elif selected_type == "CacheDB":
                config['ttl_seconds'] = int(input("Enter TTL (seconds): "))
                config['capacity_mb'] = int(input("Enter capacity (MB): "))
                config['eviction_policy'] = input("Enter eviction policy (LRU / FIFO): ")

            self.resources[name] = ResourceRegistry.create(selected_type, **config)
            print(f"{selected_type} created successfully!")

        except (ValueError, IndexError):
            print("Invalid selection. Please try again.")

    def start_resource(self):
        name = input("Enter resource name: ")
        try:
            resource = self._get_resource(name)
            resource.start()

            timestamp = datetime.datetime.now().strftime("%I:%M %p")
            print(f"{type(resource).__name__} started at {timestamp} in {getattr(resource, 'region', 'N/A')}")
            print(f"(Log written to {self.logger.get_log_path(name)})")

            self.logger.log(name, resource.get_start_log_message())
        except (KeyError, ValueError, PermissionError) as e:
            print(f"{e}")

    def stop_resource(self):
        name = input("Enter resource name: ")
        try:
            resource = self._get_resource(name)
            resource.stop()
            print(f"{type(resource).__name__} stopped successfully.")
            self.logger.log(name, f"{type(resource).__name__} stopped successfully")
        except (KeyError, ValueError, PermissionError) as e:
            print(f"{e}")

    def delete_resource(self):
        name = input("Enter resource name: ")
        try:
            resource = self._get_resource(name)
            resource.soft_delete()
            print(f"{type(resource).__name__} marked as deleted.")
            self.logger.log(name, f"{type(resource).__name__} marked as deleted")
        except (KeyError, PermissionError) as e:
            print(f"{e}")

    def view_logs(self):
        name = input("Enter resource name: ")
        log_file = self.logger.get_log_path(name)
        if os.path.exists(log_file) and os.path.getsize(log_file) > 0:
            print("Displaying latest log entries...")
            with open(log_file, "r") as f:
                print(f.read().strip())
        else:
            print("No logs found for this resource.")

    def run(self):
        while True:
            print("\n1. Create Resource")
            print("2. Start Resource")
            print("3. Stop Resource")
            print("4. Delete Resource")
            print("5. View Logs")
            print("6. Exit")

            choice = input("Enter choice: ")
            actions = {
                '1': self.create_resource, '2': self.start_resource,
                '3': self.stop_resource, '4': self.delete_resource,
                '5': self.view_logs
            }
            if choice in actions:
                actions[choice]()
            elif choice == '6':
                break
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    app = CloudConnect()
    app.run()
