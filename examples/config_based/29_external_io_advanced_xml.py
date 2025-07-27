#!/usr/bin/env python3
"""
External IO Advanced XML Example

This example demonstrates advanced ExternalIO communication patterns including:
- Multiple input/output channels
- Data transformation
- Error handling
- Statistics monitoring
"""

import asyncio
import json
from abtree import BehaviorForest, load_tree_from_string

# Global data storage for demonstration
input_data_buffer = []
output_data_buffer = []

async def sensor_input_handler(input_info):
    """Handle sensor data input"""
    print(f"🌡️ Sensor data received: {input_info}")
    input_data_buffer.append(input_info)
    
    # Transform sensor data
    if "data" in input_info:
        sensor_data = input_info["data"]
        if isinstance(sensor_data, dict):
            # Add timestamp and transform
            sensor_data["processed"] = True
            sensor_data["timestamp"] = input_info["timestamp"]
            print(f"📊 Processed sensor data: {sensor_data}")

async def command_output_handler(output_info):
    """Handle command output"""
    print(f"🎮 Command output sent: {output_info}")
    output_data_buffer.append(output_info)
    
    # Log command details
    if "data" in output_info:
        command_data = output_info["data"]
        print(f"📋 Command details: {command_data}")

async def status_input_handler(input_info):
    """Handle status input"""
    print(f"📈 Status update received: {input_info}")
    
    # Process status information
    if "data" in input_info:
        status_data = input_info["data"]
        print(f"🔄 System status: {status_data}")

async def alert_output_handler(output_info):
    """Handle alert output"""
    print(f"🚨 Alert output sent: {output_info}")
    
    # Process alert
    if "data" in output_info:
        alert_data = output_info["data"]
        print(f"⚠️ Alert level: {alert_data.get('level', 'unknown')}")

async def main():
    # XML configuration for advanced external IO communication
    xml_config = """
    <BehaviorForest name="AdvancedExternalIOForest">
        <!-- Sensor Data Processing Tree -->
        <BehaviorTree name="SensorProcessor">
            <Sequence name="Sensor Processing">
                <CommExternalInput name="ReceiveSensorData" channel="sensor_data" timeout="5.0"/>
                <Log name="LogSensorData" message="Processing sensor data"/>
                <CommExternalOutput name="SendProcessedData" channel="processed_data" data="{sensor_data}"/>
            </Sequence>
        </BehaviorTree>
        
        <!-- Command Processing Tree -->
        <BehaviorTree name="CommandProcessor">
            <Sequence name="Command Processing">
                <CommExternalInput name="ReceiveCommands" channel="commands" timeout="2.0"/>
                <Log name="LogCommands" message="Processing commands"/>
                <CommExternalOutput name="SendCommandAck" channel="command_ack" data="{command_status}"/>
            </Sequence>
        </BehaviorTree>
        
        <!-- Status Monitoring Tree -->
        <BehaviorTree name="StatusMonitor">
            <Sequence name="Status Monitoring">
                <CommExternalInput name="ReceiveStatus" channel="status_updates" timeout="3.0"/>
                <Log name="LogStatus" message="Monitoring system status"/>
                <CommExternalOutput name="SendStatusReport" channel="status_reports" data="{status_summary}"/>
            </Sequence>
        </BehaviorTree>
        
        <!-- Alert System Tree -->
        <BehaviorTree name="AlertSystem">
            <Selector name="Alert Processing">
                <Sequence name="High Priority Alert">
                    <CommExternalInput name="ReceiveAlerts" channel="alerts" timeout="1.0"/>
                    <Log name="LogAlert" message="High priority alert detected"/>
                    <CommExternalOutput name="SendAlertResponse" channel="alert_responses" data="{alert_response}"/>
                </Sequence>
                <CommExternalOutput name="SendHeartbeat" channel="heartbeat" data="{heartbeat_data}"/>
            </Selector>
        </BehaviorTree>
        
        <!-- Communication Configuration -->
        <Communication>
            <!-- Sensor Data Channel -->
            <CommExternalIO name="sensor_data">
                <CommExternalInput service="SensorProcessor" />
            </CommExternalIO>
            <CommExternalIO name="processed_data">
                <CommExternalOutput service="SensorProcessor" />
            </CommExternalIO>
            
            <!-- Command Channel -->
            <CommExternalIO name="commands">
                <CommExternalInput service="CommandProcessor" />
            </CommExternalIO>
            <CommExternalIO name="command_ack">
                <CommExternalOutput service="CommandProcessor" />
            </CommExternalIO>
            
            <!-- Status Channel -->
            <CommExternalIO name="status_updates">
                <CommExternalInput service="StatusMonitor" />
            </CommExternalIO>
            <CommExternalIO name="status_reports">
                <CommExternalOutput service="StatusMonitor" />
            </CommExternalIO>
            
            <!-- Alert Channel -->
            <CommExternalIO name="alerts">
                <CommExternalInput service="AlertSystem" />
            </CommExternalIO>
            <CommExternalIO name="alert_responses">
                <CommExternalOutput service="AlertSystem" />
            </CommExternalIO>
            <CommExternalIO name="heartbeat">
                <CommExternalOutput service="AlertSystem" />
            </CommExternalIO>
        </Communication>
    </BehaviorForest>
    """
    
    # Load forest from XML
    forest = load_tree_from_string(xml_config)
    
    # Register external IO handlers for all channels
    forest.on_input("sensor_data", sensor_input_handler)
    forest.on_output("processed_data", command_output_handler)
    forest.on_input("commands", command_output_handler)
    forest.on_output("command_ack", command_output_handler)
    forest.on_input("status_updates", status_input_handler)
    forest.on_output("status_reports", command_output_handler)
    forest.on_input("alerts", alert_output_handler)
    forest.on_output("alert_responses", alert_output_handler)
    forest.on_output("heartbeat", command_output_handler)
    
    await forest.start()

    print("🚀 Starting advanced external IO communication demo...")
    
    # Simulate various external data inputs
    print("\n📡 Simulating sensor data input...")
    await forest.input("sensor_data", {
        "temperature": 24.5,
        "humidity": 65.2,
        "pressure": 1013.25,
        "timestamp": asyncio.get_event_loop().time()
    }, "weather_station")
    
    print("\n📡 Simulating command input...")
    await forest.input("commands", {
        "action": "move",
        "direction": "north",
        "speed": 0.5,
        "priority": "normal"
    }, "control_system")
    
    print("\n📡 Simulating status update...")
    await forest.input("status_updates", {
        "system_health": "good",
        "battery_level": 85,
        "active_processes": 12,
        "uptime": 3600
    }, "system_monitor")
    
    print("\n📡 Simulating alert input...")
    await forest.input("alerts", {
        "level": "warning",
        "message": "Battery level below 20%",
        "source": "power_monitor",
        "timestamp": asyncio.get_event_loop().time()
    }, "alert_system")
    
    # Wait for processing
    await asyncio.sleep(2)
    
    # Get comprehensive statistics
    print("\n📊 External IO Statistics:")
    io_stats = forest.get_external_io_stats()
    print(json.dumps(io_stats, indent=2))
    
    print(f"\n📈 Data Buffer Statistics:")
    print(f"Input data buffer size: {len(input_data_buffer)}")
    print(f"Output data buffer size: {len(output_data_buffer)}")
    
    await forest.stop()
    print("\n✅ Advanced external IO demo completed!")

if __name__ == "__main__":
    asyncio.run(main()) 