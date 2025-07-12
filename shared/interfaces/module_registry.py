"""
Module Registry

This manages the registration and lifecycle of all modules in the system.
It ensures modules are loaded in the correct order based on dependencies.
"""

from typing import Dict, List, Optional, Any, Type
from .base_module import IModule, ModuleInfo
from core import get_logger, get_event_bus
from core.utils import ServiceUnavailableError, ModuleBoundaryError
import importlib


class ModuleRegistry:
    """
    Central registry for all system modules.
    
    This registry manages:
    - Module registration and discovery
    - Dependency resolution
    - Module lifecycle (init, start, stop)
    - Inter-module communication validation
    """
    
    def __init__(self):
        """Initialize the module registry"""
        self.logger = get_logger("module_registry")
        self.event_bus = get_event_bus()
        
        # Registered modules
        self._modules: Dict[str, IModule] = {}
        self._module_classes: Dict[str, Type[IModule]] = {}
        self._interfaces: Dict[str, Any] = {}
        
        # Module states
        self._initialization_order: List[str] = []
        self._is_initialized = False
    
    def register_module_class(self, name: str, module_class: Type[IModule]):
        """
        Register a module class (before instantiation).
        
        Args:
            name: Module name
            module_class: Module class that implements IModule
        """
        if name in self._module_classes:
            raise ValueError(f"Module class '{name}' already registered")
        
        self._module_classes[name] = module_class
        self.logger.info(f"Registered module class: {name}")
    
    def register_module(self, module: IModule):
        """
        Register an instantiated module.
        
        Args:
            module: Module instance
        """
        info = module.get_info()
        
        if info.name in self._modules:
            raise ValueError(f"Module '{info.name}' already registered")
        
        self._modules[info.name] = module
        self.logger.info(f"Registered module: {info.name} v{info.version}")
    
    def discover_modules(self, module_path: str = "modules"):
        """
        Discover and load modules from the modules directory.
        
        Args:
            module_path: Path to modules directory
        """
        self.logger.info(f"Discovering modules in {module_path}")
        
        # Define module loading order based on dependencies
        module_order = [
            "vps_management",
            "mailbox_management", 
            "warmup_engine",
            "campaign_system",
            "reporting",
            "integrations"
        ]
        
        for module_name in module_order:
            try:
                # Import module's main module
                module_import = importlib.import_module(f"{module_path}.{module_name}")
                
                # Look for MODULE_CLASS attribute
                if hasattr(module_import, 'MODULE_CLASS'):
                    module_class = getattr(module_import, 'MODULE_CLASS')
                    self.register_module_class(module_name, module_class)
                    
                # Look for get_module function
                elif hasattr(module_import, 'get_module'):
                    get_module_func = getattr(module_import, 'get_module')
                    module_instance = get_module_func()
                    self.register_module(module_instance)
                    
                else:
                    self.logger.warning(f"Module {module_name} has no MODULE_CLASS or get_module")
                    
            except ImportError as e:
                self.logger.warning(f"Could not import module {module_name}: {e}")
            except Exception as e:
                self.logger.error(f"Error loading module {module_name}: {e}")
    
    def initialize_all(self, configs: Optional[Dict[str, Dict[str, Any]]] = None) -> bool:
        """
        Initialize all modules in dependency order.
        
        Args:
            configs: Module configurations keyed by module name
            
        Returns:
            True if all modules initialized successfully
        """
        if self._is_initialized:
            return True
        
        configs = configs or {}
        
        # Resolve initialization order
        self._initialization_order = self._resolve_dependencies()
        
        # Initialize modules
        for module_name in self._initialization_order:
            module = self._modules.get(module_name)
            if not module:
                # Try to instantiate from class
                if module_name in self._module_classes:
                    module_class = self._module_classes[module_name]
                    module = module_class()
                    self._modules[module_name] = module
                else:
                    self.logger.error(f"Module {module_name} not found")
                    return False
            
            config = configs.get(module_name, {})
            
            self.logger.info(f"Initializing module: {module_name}")
            if not module.initialize(config):
                self.logger.error(f"Failed to initialize module: {module_name}")
                return False
            
            # Register module interface
            try:
                interface = module.get_interface()
                if interface:
                    self._interfaces[module_name] = interface
            except Exception as e:
                self.logger.warning(f"Module {module_name} has no interface: {e}")
        
        self._is_initialized = True
        self.event_bus.emit("system.modules_initialized", {
            "modules": self._initialization_order
        })
        
        return True
    
    def start_all(self) -> bool:
        """
        Start all modules in dependency order.
        
        Returns:
            True if all modules started successfully
        """
        if not self._is_initialized:
            self.logger.error("Cannot start modules: not initialized")
            return False
        
        for module_name in self._initialization_order:
            module = self._modules[module_name]
            
            self.logger.info(f"Starting module: {module_name}")
            if not module.start():
                self.logger.error(f"Failed to start module: {module_name}")
                return False
        
        self.event_bus.emit("system.modules_started", {
            "modules": self._initialization_order
        })
        
        return True
    
    def stop_all(self) -> bool:
        """
        Stop all modules in reverse dependency order.
        
        Returns:
            True if all modules stopped successfully
        """
        # Stop in reverse order
        for module_name in reversed(self._initialization_order):
            module = self._modules.get(module_name)
            if module and module.get_info().status == "running":
                self.logger.info(f"Stopping module: {module_name}")
                if not module.stop():
                    self.logger.error(f"Failed to stop module: {module_name}")
        
        self.event_bus.emit("system.modules_stopped", {
            "modules": self._initialization_order
        })
        
        return True
    
    def get_module(self, name: str) -> Optional[IModule]:
        """
        Get a module by name.
        
        Args:
            name: Module name
            
        Returns:
            Module instance or None
        """
        return self._modules.get(name)
    
    def get_interface(self, name: str) -> Any:
        """
        Get a module's public interface.
        
        Args:
            name: Module name
            
        Returns:
            Module interface
            
        Raises:
            ServiceUnavailableError: If module not available
        """
        if name not in self._interfaces:
            raise ServiceUnavailableError(
                f"Module '{name}'",
                "Module not initialized or has no interface"
            )
        
        return self._interfaces[name]
    
    def validate_module_access(self, source_module: str, target_module: str, 
                             operation: str = "access") -> bool:
        """
        Validate if one module can access another.
        
        Args:
            source_module: Module making the request
            target_module: Module being accessed
            operation: Type of operation
            
        Returns:
            True if access allowed
            
        Raises:
            ModuleBoundaryError: If access not allowed
        """
        # Get module info
        source = self._modules.get(source_module)
        target = self._modules.get(target_module)
        
        if not source or not target:
            return False
        
        source_info = source.get_info()
        target_info = target.get_info()
        
        # Check if target provides what source consumes
        target_provides = set(target_info.provides)
        source_consumes = set(source_info.consumes)
        
        if not target_provides.intersection(source_consumes):
            raise ModuleBoundaryError(source_module, target_module, operation)
        
        return True
    
    def get_module_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status of all modules.
        
        Returns:
            Dictionary of module statuses
        """
        status = {}
        
        for name, module in self._modules.items():
            info = module.get_info()
            health = module.health_check()
            
            status[name] = {
                "version": info.version,
                "status": info.status,
                "healthy": health["healthy"],
                "health_message": health["message"],
                "dependencies": info.dependencies,
                "provides": info.provides,
                "consumes": info.consumes
            }
        
        return status
    
    def _resolve_dependencies(self) -> List[str]:
        """
        Resolve module dependencies and return initialization order.
        
        Returns:
            List of module names in initialization order
        """
        # For now, use a predefined order
        # In the future, implement topological sort based on dependencies
        
        order = []
        module_names = list(self._modules.keys()) + list(self._module_classes.keys())
        
        # Core modules first
        core_order = [
            "vps_management",
            "mailbox_management", 
            "warmup_engine",
            "campaign_system",
            "reporting",
            "integrations"
        ]
        
        for name in core_order:
            if name in module_names:
                order.append(name)
        
        # Add any remaining modules
        for name in module_names:
            if name not in order:
                order.append(name)
        
        return order


# Global module registry instance
_module_registry: Optional[ModuleRegistry] = None


def get_module_registry() -> ModuleRegistry:
    """
    Get the global module registry instance.
    
    Returns:
        ModuleRegistry instance
    """
    global _module_registry
    if _module_registry is None:
        _module_registry = ModuleRegistry()
    return _module_registry