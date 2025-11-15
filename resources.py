import abc
from typing import Dict, Type, List

# Resource registry - keeps track of all resource types we support
class ResourceRegistry:
    """Registry to manage different types of cloud resources"""
    _registry: Dict[str, Type['Resource']] = {}

    @classmethod
    def register(cls, resource_type_name: str):
        """Decorator to auto-register resource classes"""
        def decorator(resource_class: Type['Resource']) -> Type['Resource']:
            cls._registry[resource_type_name] = resource_class
            return resource_class
        return decorator

    @classmethod
    def create(cls, resource_type_name: str, **kwargs) -> 'Resource':
        """Create a new resource instance"""
        if resource_type_name not in cls._registry:
            raise ValueError(f"Unknown resource type: '{resource_type_name}'")
        return cls._registry[resource_type_name](**kwargs)

    @classmethod
    def get_registered_types(cls) -> List[str]:
        return list(cls._registry.keys())

# Base class for all resources
class Resource(abc.ABC):
    """
    Base resource class - all cloud resources inherit from this
    """
    def __init__(self, name: str):
        self.name = name
        self.state = "stopped"
        self.is_deleted = False

    @abc.abstractmethod
    def get_details(self) -> str:
        """Get resource configuration details"""
        pass

    def start(self):
        """Start the resource"""
        if self.is_deleted:
            raise PermissionError(f"Resource '{self.name}' is deleted and cannot be started.")
        if self.state == "running":
            raise ValueError(f"Resource '{self.name}' is already running.")
        self.state = "running"

    def stop(self):
        """Stop the resource"""
        if self.is_deleted:
            raise PermissionError(f"Resource '{self.name}' is deleted and cannot be stopped.")
        if self.state == "stopped":
            raise ValueError(f"Resource '{self.name}' is already stopped.")
        self.state = "stopped"

    def soft_delete(self):
        """Mark resource as deleted (soft delete)"""
        if self.state == "running":
            raise PermissionError("Cannot delete: Resource must be stopped first.")
        self.is_deleted = True

    def get_start_log_message(self) -> str:
        """Generate log message for start action"""
        return f"{type(self).__name__} started"

# Concrete resource types
@ResourceRegistry.register("AppService")
class AppService(Resource):
    """Application service resource"""
    def __init__(self, name: str, runtime: str, region: str, replica_count: int):
        super().__init__(name)
        self.runtime = runtime
        self.region = region
        self.replica_count = replica_count

    def get_details(self) -> str:
        return f"AppService: runtime={self.runtime}, region={self.region}, replicas={self.replica_count}"

    def get_start_log_message(self) -> str:
        return f"AppService started in {self.region}"

@ResourceRegistry.register("StorageAccount")
class StorageAccount(Resource):
    """Storage account resource"""
    def __init__(self, name: str, encryption_enabled: bool, access_key: str, max_size_gb: int):
        super().__init__(name)
        self.encryption_enabled = encryption_enabled
        self.access_key = access_key
        self.max_size_gb = max_size_gb

    def get_details(self) -> str:
        return f"StorageAccount: encryption={self.encryption_enabled}, size={self.max_size_gb}GB"

@ResourceRegistry.register("CacheDB")
class CacheDB(Resource):
    """Cache database resource"""
    def __init__(self, name: str, ttl_seconds: int, capacity_mb: int, eviction_policy: str):
        super().__init__(name)
        self.ttl_seconds = ttl_seconds
        self.capacity_mb = capacity_mb
        self.eviction_policy = eviction_policy

    def get_details(self) -> str:
        return f"CacheDB: capacity={self.capacity_mb}MB, policy={self.eviction_policy}"