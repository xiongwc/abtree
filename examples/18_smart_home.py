#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 16: Smart Home System – Expert-Level Scenario

Difficulty: Expert Level
Demonstrates how to model and manage a complex smart home system using ABTree, including multi-device coordination,
scene management, user preference learning, and fault recovery.

Key Learning Points:

    Modeling complex systems with behavior trees

    Coordinated control across multiple devices

    Scene/mode management

    Learning user preferences

    Fault handling and recovery

    Real-time monitoring and alerting

    How to configure a smart home system using XML strings
"""

import asyncio
import json
import random
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum

from abtree import BehaviorTree, Sequence, Selector, Action, Condition, register_node
from abtree.core import Status
from abtree.engine.blackboard import Blackboard
from abtree.parser.xml_parser import XMLParser


# Register custom node types
def register_custom_nodes():
    """Register custom node types"""
    register_node("UpdateSensorsAction", UpdateSensorsAction)
    register_node("UpdateDevicesAction", UpdateDevicesAction)
    register_node("CheckSecurityAction", CheckSecurityAction)
    register_node("SceneModeSelector", SceneModeSelector)
    register_node("ApplySceneModeAction", ApplySceneModeAction)
    register_node("EnergyOptimizationAction", EnergyOptimizationAction)
    register_node("SecurityMonitoringAction", SecurityMonitoringAction)
    register_node("UserComfortAction", UserComfortAction)
    register_node("MaintenanceCheckAction", MaintenanceCheckAction)
    register_node("GenerateReportAction", GenerateReportAction)
    register_node("HandleSecurityEventAction", HandleSecurityEventAction)
    register_node("HasSecurityAlertCondition", HasSecurityAlertCondition)
    register_node("SceneChangedCondition", SceneChangedCondition)
    register_node("NeedsMaintenanceCondition", NeedsMaintenanceCondition)
    register_node("HasLowBatteryCondition", HasLowBatteryCondition)
    register_node("IsEnergySavingModeCondition", IsEnergySavingModeCondition)


# ==================== Data Models ====================

class DeviceType(Enum):
    """Device types"""
    LIGHT = "light"
    THERMOSTAT = "thermostat"
    SECURITY = "security"
    ENTERTAINMENT = "entertainment"
    APPLIANCE = "appliance"


class RoomType(Enum):
    """Room types"""
    LIVING_ROOM = "living_room"
    BEDROOM = "bedroom"
    KITCHEN = "kitchen"
    BATHROOM = "bathroom"
    STUDY = "study"


class SceneMode(Enum):
    """Scene modes"""
    HOME = "home"
    AWAY = "away"
    SLEEP = "sleep"
    PARTY = "party"
    WORK = "work"
    MOVIE = "movie"


@dataclass
class Device:
    """Device information"""
    id: str
    name: str
    type: DeviceType
    room: RoomType
    status: bool = False
    value: float = 0.0
    battery: float = 100.0
    last_update: datetime = None
    
    def __post_init__(self):
        if self.last_update is None:
            self.last_update = datetime.now()


@dataclass
class Room:
    """Room information"""
    type: RoomType
    temperature: float = 22.0
    humidity: float = 50.0
    light_level: float = 0.0
    occupancy: bool = False
    last_motion: datetime = None
    
    def __post_init__(self):
        if self.last_motion is None:
            self.last_motion = datetime.now()


@dataclass
class UserPreference:
    """User preferences"""
    preferred_temp: float = 22.0
    preferred_light: float = 0.7
    sleep_time: str = "22:00"
    wake_time: str = "07:00"
    away_mode: bool = False
    energy_saving: bool = True


@dataclass
class SecurityEvent:
    """Security event"""
    timestamp: datetime
    event_type: str
    device_id: str
    severity: str
    description: str


# ==================== Smart Home System ====================

class SmartHomeSystem:
    """Smart home system"""
    
    def __init__(self):
        self.devices: Dict[str, Device] = {}
        self.rooms: Dict[RoomType, Room] = {}
        self.user_prefs = UserPreference()
        self.current_scene = SceneMode.HOME
        self.security_events: List[SecurityEvent] = []
        self.energy_usage = 0.0
        self.last_maintenance = datetime.now()
        
        self._initialize_system()
    
    def _initialize_system(self):
        """Initialize system"""
        # Initialize rooms
        for room_type in RoomType:
            self.rooms[room_type] = Room(type=room_type)
        
        # Initialize devices
        device_configs = [
            ("light_living", "Living Room Light", DeviceType.LIGHT, RoomType.LIVING_ROOM),
            ("light_bedroom", "Bedroom Light", DeviceType.LIGHT, RoomType.BEDROOM),
            ("light_kitchen", "Kitchen Light", DeviceType.LIGHT, RoomType.KITCHEN),
            ("thermostat_living", "Living Room Thermostat", DeviceType.THERMOSTAT, RoomType.LIVING_ROOM),
            ("thermostat_bedroom", "Bedroom Thermostat", DeviceType.THERMOSTAT, RoomType.BEDROOM),
            ("camera_front", "Front Door Camera", DeviceType.SECURITY, RoomType.LIVING_ROOM),
            ("sensor_motion", "Motion Sensor", DeviceType.SECURITY, RoomType.LIVING_ROOM),
            ("tv_living", "Living Room TV", DeviceType.ENTERTAINMENT, RoomType.LIVING_ROOM),
            ("speaker_living", "Living Room Speaker", DeviceType.ENTERTAINMENT, RoomType.LIVING_ROOM),
            ("coffee_maker", "Coffee Maker", DeviceType.APPLIANCE, RoomType.KITCHEN),
        ]
        
        for device_id, name, device_type, room in device_configs:
            self.devices[device_id] = Device(
                id=device_id,
                name=name,
                type=device_type,
                room=room
            )
    
    async def update_sensors(self):
        """Update sensor data"""
        await asyncio.sleep(0.01)  # Simulate sensor update
        for room in self.rooms.values():
            room.temperature += random.uniform(-0.5, 0.5)
            room.humidity += random.uniform(-2, 2)
            room.light_level = random.uniform(0, 1)
            room.occupancy = random.choice([True, False])

    async def update_devices(self):
        """Update device status"""
        await asyncio.sleep(0.01)  # Simulate device update
        for device in self.devices.values():
            device.battery -= random.uniform(0, 0.5)
            device.last_update = datetime.now()

    async def check_security(self):
        """Check security status"""
        await asyncio.sleep(0.01)  # Simulate security check
        # Simulate security event
        if random.random() < 0.3:
            event = SecurityEvent(
                timestamp=datetime.now(),
                event_type="motion_detected",
                device_id="motion_sensor_1",
                severity="medium",
                description="Motion detected in living room"
            )
            self.security_events.append(event)
    
    def get_room_devices(self, room_type: RoomType) -> List[Device]:
        """Get devices in a room"""
        return [d for d in self.devices.values() if d.room == room_type]
    
    def get_devices_by_type(self, device_type: DeviceType) -> List[Device]:
        """Get devices by type"""
        return [d for d in self.devices.values() if d.type == device_type]


# ==================== Custom Nodes ====================

class UpdateSensorsAction(Action):
    """Update sensor data"""
    
    async def execute(self, blackboard: Blackboard) -> Status:
        system = blackboard.get("smart_home_system")
        await system.update_sensors()
        blackboard.set("sensors_updated", True)
        return Status.SUCCESS


class UpdateDevicesAction(Action):
    """Update device status"""
    
    async def execute(self, blackboard: Blackboard) -> Status:
        system = blackboard.get("smart_home_system")
        await system.update_devices()
        blackboard.set("devices_updated", True)
        return Status.SUCCESS


class CheckSecurityAction(Action):
    """Check security status"""
    
    async def execute(self, blackboard: Blackboard) -> Status:
        system = blackboard.get("smart_home_system")
        await system.check_security()
        
        # Check for security events
        recent_events = [
            e for e in system.security_events
            if datetime.now() - e.timestamp < timedelta(minutes=5)
        ]
        
        if recent_events:
            blackboard.set("security_alert", True)
            blackboard.set("security_events", recent_events)
            return Status.SUCCESS
        else:
            blackboard.set("security_alert", False)
            return Status.FAILURE


class SceneModeSelector(Action):
    """Scene mode selector"""
    
    async def execute(self, blackboard: Blackboard) -> Status:
        system = blackboard.get("smart_home_system")
        current_time = datetime.now().time()
        
        # Select scene based on time and user preferences
        if system.user_prefs.away_mode:
            new_scene = SceneMode.AWAY
        elif current_time.hour >= 22 or current_time.hour < 7:
            new_scene = SceneMode.SLEEP
        elif current_time.hour >= 9 and current_time.hour <= 17:
            new_scene = SceneMode.WORK
        else:
            new_scene = SceneMode.HOME
        
        if new_scene != system.current_scene:
            system.current_scene = new_scene
            blackboard.set("scene_changed", True)
            blackboard.set("current_scene", new_scene)
            return Status.SUCCESS
        
        return Status.FAILURE


class ApplySceneModeAction(Action):
    """Apply scene mode"""
    
    async def execute(self, blackboard: Blackboard) -> Status:
        system = blackboard.get("smart_home_system")
        scene = system.current_scene
        
        print(f"Applying scene mode: {scene.value}")
        
        if scene == SceneMode.SLEEP:
            # Sleep mode: turn off most devices
            for device in system.devices.values():
                if device.type == DeviceType.LIGHT:
                    device.status = False
                elif device.type == DeviceType.ENTERTAINMENT:
                    device.status = False
                elif device.type == DeviceType.THERMOSTAT:
                    device.value = 20.0  # Lower temperature
        
        elif scene == SceneMode.AWAY:
            # Away mode: enable security devices, turn off others
            for device in system.devices.values():
                if device.type == DeviceType.SECURITY:
                    device.status = True
                else:
                    device.status = False
        
        elif scene == SceneMode.WORK:
            # Work mode: moderate lighting, energy saving settings
            for device in system.devices.values():
                if device.type == DeviceType.LIGHT:
                    device.status = True
                    device.value = 0.5
                elif device.type == DeviceType.THERMOSTAT:
                    device.value = 23.0
        
        elif scene == SceneMode.HOME:
            # Home mode: normal usage
            for device in system.devices.values():
                if device.type == DeviceType.LIGHT:
                    device.status = True
                    device.value = 0.8
                elif device.type == DeviceType.THERMOSTAT:
                    device.value = system.user_prefs.preferred_temp
        
        blackboard.set("scene_applied", True)
        return Status.SUCCESS


class EnergyOptimizationAction(Action):
    """Energy optimization action"""
    
    async def execute(self, blackboard: Blackboard) -> Status:
        """Execute energy optimization"""
        print("Executing energy optimization...")
        await asyncio.sleep(0.01)
        
        system = blackboard.get("smart_home_system")
        
        # Turn off unused devices
        for device in system.devices.values():
            if device.type == DeviceType.LIGHT and not system.rooms[device.room].occupancy:
                device.status = False
                print(f"Turn off lights in unused room: {device.name}")
        
        blackboard.set("energy_optimized", True)
        return Status.SUCCESS


class SecurityMonitoringAction(Action):
    """Security monitoring action"""
    
    async def execute(self, blackboard: Blackboard) -> Status:
        """Execute security monitoring"""
        print("Executing security monitoring...")
        await asyncio.sleep(0.01)
        
        system = blackboard.get("smart_home_system")
        
        # Check for low battery devices
        low_battery_devices = [
            d for d in system.devices.values()
            if d.type == DeviceType.SECURITY and d.battery < 20
        ]
        
        if low_battery_devices:
            blackboard.set("low_battery_alert", True)
            blackboard.set("low_battery_devices", low_battery_devices)
        
        return Status.SUCCESS


class UserComfortAction(Action):
    """User comfort optimization action"""
    
    async def execute(self, blackboard: Blackboard) -> Status:
        """Execute user comfort optimization"""
        print("Optimizing user comfort...")
        await asyncio.sleep(0.01)
        
        system = blackboard.get("smart_home_system")
        
        # Adjust temperature based on user preferences
        for room in system.rooms.values():
            if room.occupancy:
                target_temp = system.user_prefs.preferred_temp
                if abs(room.temperature - target_temp) > 1:
                    # Find thermostat in this room
                    for device in system.devices.values():
                        if device.type == DeviceType.THERMOSTAT and device.room == room.type:
                            device.value = target_temp
                            break
        
        return Status.SUCCESS


class MaintenanceCheckAction(Action):
    """Maintenance check action"""
    
    async def execute(self, blackboard: Blackboard) -> Status:
        """Execute maintenance check"""
        print("Executing maintenance check...")
        await asyncio.sleep(0.01)
        
        system = blackboard.get("smart_home_system")
        
        # Check device maintenance needs
        maintenance_needed = []
        for device in system.devices.values():
            if device.battery < 10 or (datetime.now() - device.last_update).days > 30:
                maintenance_needed.append(device)
        
        if maintenance_needed:
            blackboard.set("maintenance_needed", True)
            blackboard.set("maintenance_devices", maintenance_needed)
        
        return Status.SUCCESS


class GenerateReportAction(Action):
    """Generate system report action"""
    
    async def execute(self, blackboard: Blackboard) -> Status:
        """Execute report generation"""
        print("Generating system report...")
        await asyncio.sleep(0.01)
        
        system = blackboard.get("smart_home_system")
        
        # Generate comprehensive report
        report = {
            "timestamp": datetime.now(),
            "rooms": len(system.rooms),
            "total_devices": len(system.devices),
            "active_devices": len([d for d in system.devices.values() if d.status]),
            "energy_usage": sum(d.battery for d in system.devices.values()),
            "security_events": len(system.security_events),
            "current_scene": system.current_scene.value
        }
        
        blackboard.set("system_report", report)
        return Status.SUCCESS


class HandleSecurityEventAction(Action):
    """Handle security event action"""
    
    async def execute(self, blackboard: Blackboard) -> Status:
        """Execute security event handling"""
        print("Handling security alert...")
        return Status.SUCCESS


# ==================== Condition Nodes ====================

class HasSecurityAlertCondition(Condition):
    """Check if there is a security alert"""
    
    async def evaluate(self, blackboard: Blackboard) -> bool:
        return blackboard.get("security_alert", False)


class SceneChangedCondition(Condition):
    """Check if scene has changed"""
    
    async def evaluate(self, blackboard: Blackboard) -> bool:
        return blackboard.get("scene_changed", False)


class NeedsMaintenanceCondition(Condition):
    """Check if maintenance is needed"""
    
    async def evaluate(self, blackboard: Blackboard) -> bool:
        system = blackboard.get("smart_home_system")
        days_since_maintenance = (datetime.now() - system.last_maintenance).days
        return days_since_maintenance >= 30


class HasLowBatteryCondition(Condition):
    """Check if any device has low battery"""
    
    async def evaluate(self, blackboard: Blackboard) -> bool:
        system = blackboard.get("smart_home_system")
        low_battery_devices = [
            d for d in system.devices.values()
            if d.battery < 20 and d.type in [DeviceType.SECURITY, DeviceType.LIGHT]
        ]
        return len(low_battery_devices) > 0


class IsEnergySavingModeCondition(Condition):
    """Check if energy saving mode is enabled"""
    
    async def evaluate(self, blackboard: Blackboard) -> bool:
        system = blackboard.get("smart_home_system")
        return system.user_prefs.energy_saving


# ==================== Main Function ====================

async def main():
    """Main function"""
    
    # Register custom node types
    register_custom_nodes()
    
    print("=== Smart Home System Example ===")
    print("This example demonstrates how to use behavior trees to manage complex smart home systems")
    print("Including device management, scene modes, security monitoring, energy optimization, etc.\n")
    
    # Create smart home system
    smart_home = SmartHomeSystem()
    
    # Create blackboard
    blackboard = Blackboard()
    blackboard.set("smart_home_system", smart_home)
    
    # Build behavior tree
    root = Sequence("Smart Home Main Controller")
    
    # System monitoring branch
    monitoring = Sequence("System Monitoring")
    monitoring.add_child(UpdateSensorsAction("Update Sensors"))
    monitoring.add_child(UpdateDevicesAction("Update Devices"))
    monitoring.add_child(CheckSecurityAction("Check Security"))
    root.add_child(monitoring)
    
    # Scene management branch
    scene_management = Sequence("Scene Management")
    scene_management.add_child(SceneModeSelector("Select Scene Mode"))
    scene_management.add_child(ApplySceneModeAction("Apply Scene Mode"))
    root.add_child(scene_management)
    
    # Security handling branch
    security_handling = Selector("Security Handling")
    
    # Create security alert sequence
    security_alert_seq = Sequence("Handle Security Alert")
    security_alert_seq.add_child(HasSecurityAlertCondition("Check Security Alert"))
    security_alert_seq.add_child(HandleSecurityEventAction("Handle Security Event"))
    security_handling.add_child(security_alert_seq)
    
    # Create security monitoring sequence
    security_monitoring_seq = Sequence("Security Monitoring")
    security_monitoring_seq.add_child(SecurityMonitoringAction("Execute Security Monitoring"))
    security_handling.add_child(security_monitoring_seq)
    
    root.add_child(security_handling)
    
    # Optimization branch
    optimization = Selector("System Optimization")
    
    # Energy optimization
    energy_opt = Sequence("Energy Optimization")
    energy_opt.add_child(IsEnergySavingModeCondition("Check Energy Saving Mode"))
    energy_opt.add_child(EnergyOptimizationAction("Execute Energy Optimization"))
    optimization.add_child(energy_opt)
    
    # User comfort optimization
    comfort_opt = Sequence("Comfort Optimization")
    comfort_opt.add_child(UserComfortAction("Optimize User Comfort"))
    optimization.add_child(comfort_opt)
    
    root.add_child(optimization)
    
    # Maintenance branch
    maintenance = Sequence("System Maintenance")
    maintenance.add_child(NeedsMaintenanceCondition("Check Maintenance Needs"))
    maintenance.add_child(MaintenanceCheckAction("Execute Maintenance"))
    root.add_child(maintenance)
    
    # Report generation
    root.add_child(GenerateReportAction("Generate System Report"))
    
    # 3. Create behavior tree
    tree = BehaviorTree()
    tree.load_from_root(root)
    
    # Set smart home system in blackboard
    tree.blackboard.set("smart_home_system", smart_home)
    
    # Run multiple rounds
    for round_num in range(3):
        print(f"\n--- Round {round_num + 1} Execution ---")
        
        # Reset blackboard state
        tree.blackboard.clear()
        tree.blackboard.set("smart_home_system", smart_home)
        
        # Execute behavior tree
        result = await tree.tick()
        
        # Display system status
        print(f"Execution result: {result}")
        print(f"Current scene: {smart_home.current_scene.value}")
        print(f"Active devices: {len([d for d in smart_home.devices.values() if d.status])}")
        print(f"Security events: {len(smart_home.security_events)}")
        
        # Display report
        report = tree.blackboard.get("system_report")
        if report:
            print("System Report:")
            print(f"  Room status: {len(report['rooms'])} rooms")
            print(f"  Device status: {report['active_devices']}/{report['total_devices']} active")
            print(f"  Energy usage: {report['energy_usage']:.2f}")
        
        await asyncio.sleep(0.1)
    
    print("\n=== Example Complete ===")
    print("This example demonstrates how to build complex smart home control systems")
    print("Including multi-device coordination, scene management, security monitoring, energy optimization, etc.")
    
    # 5. Demonstrate XML configuration method
    print("\n=== XML Configuration Example ===")
    xml_config = '''
    <BehaviorTree name="SmartHomeXML" description="XML configuration example for a smart home system">
        <Sequence name="Root Sequence">
            <Selector name="Smart Home Main Controller">
                <Sequence name="System Monitoring">
                    <UpdateSensorsAction name="Update Sensors" />
                    <UpdateDevicesAction name="Update Devices" />
                    <CheckSecurityAction name="Check Security" />
                </Sequence>
                <Sequence name="Scene Management">
                    <SceneModeSelector name="Select Scene Mode" />
                    <ApplySceneModeAction name="Apply Scene Mode" />
                </Sequence>
                <Selector name="Security Handling">
                    <Sequence name="Handle Security Alert">
                        <HasSecurityAlertCondition name="Check Security Alert" />
                        <HandleSecurityEventAction name="Handle Security Event" />
                    </Sequence>
                    <Sequence name="Security Monitoring">
                        <SecurityMonitoringAction name="Execute Security Monitoring" />
                    </Sequence>
                </Selector>
                <Selector name="System Optimization">
                    <Sequence name="Energy Optimization">
                        <IsEnergySavingModeCondition name="Check Energy Saving Mode" />
                        <EnergyOptimizationAction name="Execute Energy Optimization" />
                    </Sequence>
                    <Sequence name="Comfort Optimization">
                        <UserComfortAction name="Optimize User Comfort" />
                    </Sequence>
                </Selector>
                <Sequence name="System Maintenance">
                    <NeedsMaintenanceCondition name="Check Maintenance Needs" />
                    <MaintenanceCheckAction name="Execute Maintenance" />
                </Sequence>
                <GenerateReportAction name="Generate System Report" />
            </Selector>
        </Sequence>
    </BehaviorTree>
    '''
    xml_tree = BehaviorTree()
    xml_tree.load_from_string(xml_config)
    
    # Set smart home system in XML tree blackboard
    xml_tree.blackboard.set("smart_home_system", smart_home)
    
    print("Smart home system configured via XML string:")
    print(xml_config.strip())
    print("\nStarting XML configured smart home system execution...")
    xml_result = await xml_tree.tick()
    print(f"XML configured execution complete! Result: {xml_result}")


if __name__ == "__main__":
    asyncio.run(main()) 