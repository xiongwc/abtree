#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 18: Smart Home - XML Configuration Version

This is the XML configuration version of the Smart Home example.
It demonstrates how to configure smart home systems using XML.

Key Learning Points:
    - How to define smart home systems using XML
    - How to configure device coordination
    - How to implement scene management with XML
    - Understanding energy optimization in XML
"""

import asyncio
import json
import random
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
from abtree import (
    BehaviorTree, Sequence, Selector, Action, Condition, Status,
    register_node,
)
from abtree.nodes.condition import Condition
from abtree.engine.blackboard import Blackboard


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
    battery_level: float = 100.0
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


class SmartHomeSystem:
    """Smart home system"""
    
    def __init__(self):
        self.devices = {}
        self.rooms = {}
        self.user_preferences = UserPreference()
        self.current_scene = SceneMode.HOME
        self.security_events = []
        self.energy_usage = 0.0
        
        self._initialize_system()
    
    def _initialize_system(self):
        """Initialize the smart home system"""
        # Initialize rooms
        for room_type in RoomType:
            self.rooms[room_type] = Room(type=room_type)
        
        # Initialize devices
        devices_data = [
            ("light_1", "Living Room Light", DeviceType.LIGHT, RoomType.LIVING_ROOM),
            ("light_2", "Bedroom Light", DeviceType.LIGHT, RoomType.BEDROOM),
            ("thermostat_1", "Living Room Thermostat", DeviceType.THERMOSTAT, RoomType.LIVING_ROOM),
            ("thermostat_2", "Bedroom Thermostat", DeviceType.THERMOSTAT, RoomType.BEDROOM),
            ("security_1", "Front Door Sensor", DeviceType.SECURITY, RoomType.LIVING_ROOM),
            ("security_2", "Motion Sensor", DeviceType.SECURITY, RoomType.BEDROOM),
            ("tv_1", "Living Room TV", DeviceType.ENTERTAINMENT, RoomType.LIVING_ROOM),
            ("coffee_1", "Coffee Maker", DeviceType.APPLIANCE, RoomType.KITCHEN),
        ]
        
        for device_id, name, device_type, room in devices_data:
            self.devices[device_id] = Device(
                id=device_id,
                name=name,
                type=device_type,
                room=room
            )
    
    async def update_sensors(self):
        """Update sensor data"""
        for room in self.rooms.values():
            # Simulate sensor updates
            room.temperature += random.uniform(-0.5, 0.5)
            room.humidity += random.uniform(-2, 2)
            room.light_level += random.uniform(-0.1, 0.1)
            
            # Clamp values
            room.temperature = max(15, min(30, room.temperature))
            room.humidity = max(30, min(80, room.humidity))
            room.light_level = max(0, min(1, room.light_level))
    
    async def update_devices(self):
        """Update device status"""
        for device in self.devices.values():
            # Simulate device updates
            if device.type == DeviceType.LIGHT and device.status:
                device.value = min(1.0, device.value + random.uniform(-0.1, 0.1))
            elif device.type == DeviceType.THERMOSTAT and device.status:
                device.value += random.uniform(-0.5, 0.5)
                device.value = max(16, min(28, device.value))
    
    async def check_security(self):
        """Check security status"""
        # Simulate security events
        if random.random() < 0.05:  # 5% chance of security event
            event = SecurityEvent(
                timestamp=datetime.now(),
                event_type="motion_detected",
                device_id="security_2",
                severity="medium",
                description="Motion detected in bedroom"
            )
            self.security_events.append(event)
            print(f"🚨 Security Event: {event.description}")
    
    def get_room_devices(self, room_type: RoomType) -> List[Device]:
        """Get devices in a room"""
        return [device for device in self.devices.values() if device.room == room_type]
    
    def get_devices_by_type(self, device_type: DeviceType) -> List[Device]:
        """Get devices by type"""
        return [device for device in self.devices.values() if device.type == device_type]


class UpdateSensorsAction(Action):
    """Update sensors action"""
    
    async def execute(self):
        system = self.blackboard.get("smart_home_system")
        if system is None:
            return Status.FAILURE
        
        await system.update_sensors()
        self.blackboard.set("sensors_updated", True)
        print("📡 Sensor data updated")
        return Status.SUCCESS


class UpdateDevicesAction(Action):
    """Update devices action"""
    
    async def execute(self):
        system = self.blackboard.get("smart_home_system")
        if system is None:
            return Status.FAILURE
        
        await system.update_devices()
        self.blackboard.set("devices_updated", True)
        print("🔧 Device status updated")
        return Status.SUCCESS


class CheckSecurityAction(Action):
    """Check security action"""
    
    async def execute(self):
        system = self.blackboard.get("smart_home_system")
        if system is None:
            return Status.FAILURE
        
        await system.check_security()
        
        # Check for security alerts
        recent_events = [
            event for event in system.security_events
            if (datetime.now() - event.timestamp).seconds < 60
        ]
        
        if recent_events:
            self.blackboard.set("security_alert", True)
            self.blackboard.set("security_events", recent_events)
            print(f"🚨 Detected {len(recent_events)} security events")
        else:
            self.blackboard.set("security_alert", False)
        
        return Status.SUCCESS


class SceneModeSelector(Action):
    """Scene mode selector action"""
    async def execute(self):
        system = self.blackboard.get("smart_home_system")
        if system is None:
            return Status.FAILURE
        # Determine scene based on time and user preferences
        current_time = datetime.now().time()
        current_hour = current_time.hour
        if current_hour < 7 or current_hour > 22:
            new_scene = SceneMode.SLEEP
        elif current_hour >= 9 and current_hour <= 17:
            new_scene = SceneMode.WORK
        elif system.user_preferences.away_mode:
            new_scene = SceneMode.AWAY
        else:
            new_scene = SceneMode.HOME
        if new_scene != system.current_scene:
            system.current_scene = new_scene
            self.blackboard.set("scene_changed", True)
            self.blackboard.set("current_scene", new_scene.value)
            print(f"🏠 Scene switched: {new_scene.value}")
        else:
            self.blackboard.set("scene_changed", False)
        return Status.SUCCESS
    async def tick(self):
        return await self.execute()


class ApplySceneModeAction(Action):
    """Apply scene mode action"""
    
    async def execute(self):
        system = self.blackboard.get("smart_home_system")
        if system is None:
            return Status.FAILURE
        
        scene = system.current_scene
        print(f"🎭 Apply scene mode: {scene.value}")
        
        # Apply scene-specific settings
        if scene == SceneMode.SLEEP:
            # Turn off most lights, lower temperature
            for device in system.devices.values():
                if device.type == DeviceType.LIGHT:
                    device.status = False
                    device.value = 0.0
                elif device.type == DeviceType.THERMOSTAT:
                    device.status = True
                    device.value = 18.0
        elif scene == SceneMode.AWAY:
            # Turn off all devices, enable security
            for device in system.devices.values():
                if device.type in [DeviceType.LIGHT, DeviceType.ENTERTAINMENT, DeviceType.APPLIANCE]:
                    device.status = False
                elif device.type == DeviceType.SECURITY:
                    device.status = True
        elif scene == SceneMode.HOME:
            # Normal home settings
            for device in system.devices.values():
                if device.type == DeviceType.LIGHT:
                    device.status = True
                    device.value = 0.7
                elif device.type == DeviceType.THERMOSTAT:
                    device.status = True
                    device.value = 22.0
        elif scene == SceneMode.WORK:
            # Work mode settings
            for device in system.devices.values():
                if device.type == DeviceType.LIGHT:
                    device.status = True
                    device.value = 0.9
                elif device.type == DeviceType.THERMOSTAT:
                    device.status = True
                    device.value = 20.0
        
        self.blackboard.set("scene_applied", True)
        return Status.SUCCESS


class EnergyOptimizationAction(Action):
    """Energy optimization action"""
    
    async def execute(self):
        system = self.blackboard.get("smart_home_system")
        if system is None:
            return Status.FAILURE
        
        print("⚡ Execute energy optimization...")
        
        # Calculate current energy usage
        total_energy = 0.0
        for device in system.devices.values():
            if device.status:
                if device.type == DeviceType.LIGHT:
                    total_energy += device.value * 0.1
                elif device.type == DeviceType.THERMOSTAT:
                    total_energy += 0.5
                elif device.type == DeviceType.ENTERTAINMENT:
                    total_energy += 0.3
                elif device.type == DeviceType.APPLIANCE:
                    total_energy += 0.8
        
        system.energy_usage = total_energy
        blackboard.set("energy_usage", total_energy)
        
        # Optimize energy usage
        if system.user_preferences.energy_saving and total_energy > 2.0:
            print("  🔋 Enable energy saving mode")
            for device in system.devices.values():
                if device.type == DeviceType.LIGHT and device.value > 0.5:
                    device.value *= 0.8
                elif device.type == DeviceType.THERMOSTAT and device.value > 20:
                    device.value -= 1.0
        
        print(f"   Current energy usage: {total_energy:.2f} kW")
        return Status.SUCCESS


class SecurityMonitoringAction(Action):
    """Security monitoring action"""
    
    async def execute(self):
        system = self.blackboard.get("smart_home_system")
        if system is None:
            return Status.FAILURE
        
        print("🔒 Security monitoring...")
        
        # Check security devices
        security_devices = system.get_devices_by_type(DeviceType.SECURITY)
        active_security = sum(1 for device in security_devices if device.status)
        
        if active_security > 0:
            print(f"  ✅ {active_security} security devices activated")
            blackboard.set("security_active", True)
        else:
            print("  ⚠️ No security devices activated")
            blackboard.set("security_active", False)
        
        return Status.SUCCESS


class UserComfortAction(Action):
    """User comfort action"""
    
    async def execute(self):
        system = self.blackboard.get("smart_home_system")
        if system is None:
            return Status.FAILURE
        
        print("👤 Optimize user comfort...")
        
        # Adjust temperature based on user preferences
        for room in system.rooms.values():
            if room.occupancy:
                thermostat = next(
                    (d for d in system.get_room_devices(room.type) if d.type == DeviceType.THERMOSTAT),
                    None
                )
                if thermostat:
                    temp_diff = system.user_preferences.preferred_temp - room.temperature
                    if abs(temp_diff) > 1.0:
                        thermostat.value += temp_diff * 0.5
                        print(f"  🌡️ Adjust {room.type.value} temperature: {thermostat.value:.1f}°C")
        
        # Adjust lighting based on user preferences
        for device in system.get_devices_by_type(DeviceType.LIGHT):
            if device.status:
                light_diff = system.user_preferences.preferred_light - device.value
                if abs(light_diff) > 0.1:
                    device.value += light_diff * 0.3
                    print(f"  💡 Adjust {device.name} brightness: {device.value:.2f}")
        
        return Status.SUCCESS


class MaintenanceCheckAction(Action):
    """Maintenance check action"""
    
    async def execute(self):
        system = self.blackboard.get("smart_home_system")
        if system is None:
            return Status.FAILURE
        
        print("🔧 Check device maintenance status...")
        
        maintenance_needed = []
        for device in system.devices.values():
            if device.battery_level < 20.0:
                maintenance_needed.append(f"{device.name} (Battery level: {device.battery_level:.1f}%)")
        
        if maintenance_needed:
            print(f"  ⚠️ Devices needing maintenance: {len(maintenance_needed)}")
            for device in maintenance_needed:
                print(f"    - {device}")
            blackboard.set("maintenance_needed", True)
            blackboard.set("maintenance_devices", maintenance_needed)
        else:
            print("  ✅ All devices in good condition")
            blackboard.set("maintenance_needed", False)
        
        return Status.SUCCESS


class GenerateReportAction(Action):
    """Generate report action"""
    
    async def execute(self):
        system = self.blackboard.get("smart_home_system")
        if system is None:
            return Status.FAILURE
        
        print("📊 Generate system report...")
        
        # Generate system report
        report = {
            "timestamp": datetime.now().isoformat(),
            "current_scene": system.current_scene.value,
            "energy_usage": system.energy_usage,
            "active_devices": sum(1 for device in system.devices.values() if device.status),
            "total_devices": len(system.devices),
            "security_events": len(system.security_events),
            "rooms": {
                room.type.value: {
                    "temperature": room.temperature,
                    "humidity": room.humidity,
                    "light_level": room.light_level,
                    "occupancy": room.occupancy
                }
                for room in system.rooms.values()
            }
        }
        
        blackboard.set("system_report", report)
        print(f"  📈 System report generated")
        print(f"    Current scene: {report['current_scene']}")
        print(f"    Energy usage: {report['energy_usage']:.2f} kW")
        print(f"    Active devices: {report['active_devices']}/{report['total_devices']}")
        
        return Status.SUCCESS


class HandleSecurityEventAction(Action):
    """Handle security event action"""
    
    async def execute(self):
        print("🚨 Handling security event...")
        
        security_events = self.blackboard.get("security_events", [])
        if security_events:
            for event in security_events:
                print(f"  📢 Security event: {event.description}")
                print(f"    Time: {event.timestamp}")
                print(f"    Severity: {event.severity}")
        
        blackboard.set("security_handled", True)
        return Status.SUCCESS


class HasSecurityAlertCondition(Condition):
    """Has security alert condition"""
    
    async def evaluate(self):
        return self.blackboard.get("security_alert", False)


class SceneChangedCondition(Condition):
    """Scene changed condition"""
    
    async def evaluate(self):
        return self.blackboard.get("scene_changed", False)


class NeedsMaintenanceCondition(Condition):
    """Needs maintenance condition"""
    
    async def evaluate(self):
        return self.blackboard.get("maintenance_needed", False)


class HasLowBatteryCondition(Condition):
    """Has low battery condition"""
    
    async def evaluate(self):
        system = self.blackboard.get("smart_home_system")
        if system is None:
            return False
        
        low_battery_devices = [
            device for device in system.devices.values()
            if device.battery_level < 20.0
        ]
        
        return len(low_battery_devices) > 0


class IsEnergySavingModeCondition(Condition):
    """Is energy saving mode condition"""
    
    async def evaluate(self):
        system = self.blackboard.get("smart_home_system")
        if system is None:
            return False
        
        return system.user_preferences.energy_saving


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


async def main():
    """Main function - Demonstrates smart home configuration based on XML"""
    
    print("=== ABTree Smart Home XML Configuration Example ===\n")
    
    # Register custom node types
    register_custom_nodes()
    
    # Create smart home system
    smart_home = SmartHomeSystem()
    
    # Create blackboard
    blackboard = Blackboard()
    blackboard.set("smart_home_system", smart_home)
    blackboard.set("sensors_updated", False)
    blackboard.set("devices_updated", False)
    blackboard.set("security_alert", False)
    blackboard.set("scene_changed", False)
    blackboard.set("maintenance_needed", False)
    
    # Create behavior tree
    tree = BehaviorTree()
    
    # Define XML configuration string
    xml_config = '''
    <BehaviorTree name="SmartHomeXML" description="Smart home system with XML configuration">
        <Selector name="Smart Home Root">
            <!-- Security event handling (highest priority) -->
            <Sequence name="Security Event Handling">
                <HasSecurityAlertCondition name="Check Security Alert" />
                <HandleSecurityEventAction name="Handle Security Event" />
            </Sequence>
            
            <!-- Maintenance management -->
            <Sequence name="Maintenance Management">
                <NeedsMaintenanceCondition name="Check Maintenance Needed" />
                <MaintenanceCheckAction name="Perform Maintenance Check" />
            </Sequence>
            
            <!-- Scene management -->
            <Sequence name="Scene Management">
                <SceneModeSelector name="Select Scene Mode" />
                <SceneChangedCondition name="Check Scene Changed" />
                <ApplySceneModeAction name="Apply Scene Mode" />
            </Sequence>
            
            <!-- Energy management -->
            <Sequence name="Energy Management">
                <IsEnergySavingModeCondition name="Check Energy Saving Mode" />
                <EnergyOptimizationAction name="Optimize Energy Usage" />
            </Sequence>
            
            <!-- User comfort -->
            <Sequence name="User Comfort">
                <UserComfortAction name="Optimize User Comfort" />
            </Sequence>
            
            <!-- System monitoring -->
            <Sequence name="System Monitoring">
                <UpdateSensorsAction name="Update Sensors" />
                <UpdateDevicesAction name="Update Devices" />
                <CheckSecurityAction name="Check Security" />
                <SecurityMonitoringAction name="Monitor Security" />
                <GenerateReportAction name="Generate Report" />
            </Sequence>
        </Selector>
    </BehaviorTree>
    '''
    
    # Load XML configuration
    tree.load_from_string(xml_config)
    
    print("Smart Home behavior tree configured:")
    print("  - Security event handling: Highest priority")
    print("  - Maintenance management: Check device status")
    print("  - Scene management: Automatic scene switching")
    print("  - Energy management: Energy saving mode management")
    print("  - User comfort: Personalized settings")
    print("  - System monitoring: Sensor and device monitoring")
    
    # Execute behavior tree
    print("\n=== Starting smart home system execution ===")
    
    for i in range(15):
        print(f"\n--- Execution round {i+1} ---")
        
        # Simulate some random events
        if i == 3:  # 4th round simulates a security event
            smart_home.security_events.append(SecurityEvent(
                timestamp=datetime.now(),
                event_type="door_opened",
                device_id="security_1",
                severity="high",
                description="Front door opened"
            ))
            print("🚨 Simulated security event!")
        elif i == 7:  # 8th round lowers device battery levels
            for device in smart_home.devices.values():
                device.battery_level *= 0.8
            print("🔋 Device battery levels lowered!")
        elif i == 11:  # 12th round switches user preferences
            smart_home.user_preferences.energy_saving = not smart_home.user_preferences.energy_saving
            print("⚡ Energy saving mode switched!")
        
        # Execute behavior tree
        result = await tree.tick()
        print(f"Execution result: {result}")
        
        # Display current state
        print(f"Current scene: {smart_home.current_scene.value}")
        print(f"Energy usage: {smart_home.energy_usage:.2f} kW")
        print(f"Active devices: {sum(1 for d in smart_home.devices.values() if d.status)}/{len(smart_home.devices)}")
        
        await asyncio.sleep(0.01)
    
    print("\nSmart home system execution completed!")


if __name__ == "__main__":
    asyncio.run(main()) 