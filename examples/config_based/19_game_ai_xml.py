#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 19: Game AI - XML Configuration Version

This is the XML configuration version of the Game AI example.
It demonstrates how to configure game AI systems using XML.

Key Learning Points:
    - How to define game AI using XML
    - How to configure character behavior decisions
    - How to implement combat AI with XML
    - Understanding team coordination in XML
"""

import asyncio
import math
import random
import time
from dataclasses import dataclass
from typing import List, Dict, Tuple
from abtree import (
    BehaviorTree, Sequence, Selector, Action, Condition, Status,
    register_node,
)
from abtree.engine.blackboard import Blackboard


@dataclass
class Vector2:
    """2D vector class"""
    x: float
    y: float
    
    def distance_to(self, other: 'Vector2') -> float:
        """Calculate distance to another vector"""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def normalize(self) -> 'Vector2':
        """Normalize vector"""
        length = math.sqrt(self.x**2 + self.y**2)
        if length > 0:
            return Vector2(self.x / length, self.y / length)
        return Vector2(0, 0)


@dataclass
class GameEntity:
    """Game entity base class"""
    id: int
    position: Vector2
    health: float
    max_health: float
    speed: float
    team: int
    
    def is_alive(self) -> bool:
        """Check if alive"""
        return self.health > 0
    
    def get_health_percentage(self) -> float:
        """Get health percentage"""
        return self.health / self.max_health if self.max_health > 0 else 0


class Player(GameEntity):
    """Player class"""
    
    def __init__(self, player_id: int, position: Vector2, team: int):
        super().__init__(player_id, position, 100.0, 100.0, 2.0, team)
        self.ammo = 30
        self.max_ammo = 30
        self.weapon_damage = 25
        self.last_shot_time = 0
        self.shot_cooldown = 0.5
        self.target = None
        self.path = []
        self.current_behavior = "idle"
    
    def can_shoot(self) -> bool:
        """Check if can shoot"""
        return (self.ammo > 0 and 
                time.time() - self.last_shot_time >= self.shot_cooldown)
    
    def shoot(self, target: 'GameEntity') -> bool:
        """Shoot target"""
        if not self.can_shoot():
            return False
        
        distance = self.position.distance_to(target.position)
        if distance > 30.0:  # Maximum shooting range
            return False
        
        # Calculate hit chance based on distance
        hit_chance = max(0.1, 1.0 - distance / 30.0)
        if random.random() < hit_chance:
            target.health -= self.weapon_damage
            print(f"🎯 Player {self.id} hit target for {self.weapon_damage} damage!")
        else:
            print(f"💨 Player {self.id} missed the shot!")
        
        self.ammo -= 1
        self.last_shot_time = time.time()
        return True
    
    def move_towards(self, target_pos: Vector2, delta_time: float):
        """Move towards target position"""
        direction = Vector2(
            target_pos.x - self.position.x,
            target_pos.y - self.position.y
        ).normalize()
        
        move_distance = self.speed * delta_time
        self.position.x += direction.x * move_distance
        self.position.y += direction.y * move_distance
        
        print(f"🚶 Player {self.id} moved to ({self.position.x:.1f}, {self.position.y:.1f})")


class Enemy(GameEntity):
    """Enemy class"""
    
    def __init__(self, enemy_id: int, position: Vector2, team: int):
        super().__init__(enemy_id, position, 80.0, 80.0, 1.5, team)
        self.attack_damage = 15
        self.attack_range = 5.0
        self.last_attack_time = 0
        self.attack_cooldown = 1.0
        self.target = None
        self.patrol_points = []
        self.current_patrol_index = 0
    
    def can_attack(self) -> bool:
        """Check if can attack"""
        return time.time() - self.last_attack_time >= self.attack_cooldown
    
    def attack(self, target: GameEntity) -> bool:
        """Attack target"""
        if not self.can_attack():
            return False
        
        distance = self.position.distance_to(target.position)
        if distance > self.attack_range:
            return False
        
        target.health -= self.attack_damage
        self.last_attack_time = time.time()
        print(f"⚔️ Enemy {self.id} attacked for {self.attack_damage} damage!")
        return True
    
    def move_towards(self, target_pos: Vector2, delta_time: float):
        """Move towards target position"""
        direction = Vector2(
            target_pos.x - self.position.x,
            target_pos.y - self.position.y
        ).normalize()
        
        move_distance = self.speed * delta_time
        self.position.x += direction.x * move_distance
        self.position.y += direction.y * move_distance
        
        print(f"👹 Enemy {self.id} moved to ({self.position.x:.1f}, {self.position.y:.1f})")


class GameWorld:
    """Game world class"""
    
    def __init__(self):
        self.players = []
        self.enemies = []
        self.difficulty = 1.0
        self.game_time = 0.0
    
    def add_player(self, player: Player):
        """Add player to world"""
        self.players.append(player)
        print(f"🎮 Player {player.id} joined the game")
    
    def add_enemy(self, enemy: Enemy):
        """Add enemy to world"""
        self.enemies.append(enemy)
        print(f"👹 Enemy {enemy.id} spawned")
    
    def get_nearest_enemy(self, entity: GameEntity, max_distance: float = 50.0) -> Enemy:
        """Get nearest enemy"""
        nearest_enemy = None
        min_distance = max_distance
        
        for enemy in self.enemies:
            if enemy.team != entity.team and enemy.is_alive():
                distance = entity.position.distance_to(enemy.position)
                if distance < min_distance:
                    min_distance = distance
                    nearest_enemy = enemy
        
        return nearest_enemy
    
    def get_nearest_ally(self, entity: GameEntity, max_distance: float = 30.0) -> GameEntity:
        """Get nearest ally"""
        nearest_ally = None
        min_distance = max_distance
        
        # Check players
        for player in self.players:
            if player.id != entity.id and player.team == entity.team and player.is_alive():
                distance = entity.position.distance_to(player.position)
                if distance < min_distance:
                    min_distance = distance
                    nearest_ally = player
        
        # Check enemies (for enemy team)
        for enemy in self.enemies:
            if enemy.id != entity.id and enemy.team == entity.team and enemy.is_alive():
                distance = entity.position.distance_to(enemy.position)
                if distance < min_distance:
                    min_distance = distance
                    nearest_ally = enemy
        
        return nearest_ally
    
    def is_position_valid(self, position: Vector2) -> bool:
        """Check if position is valid"""
        return 0 <= position.x <= 100 and 0 <= position.y <= 100
    
    def update_difficulty(self):
        """Update game difficulty"""
        alive_players = sum(1 for player in self.players if player.is_alive())
        alive_enemies = sum(1 for enemy in self.enemies if enemy.is_alive())
        
        if alive_players == 0:
            self.difficulty = 0.0
        elif alive_enemies == 0:
            self.difficulty = 2.0
        else:
            # Dynamic difficulty based on player/enemy ratio
            ratio = alive_enemies / max(alive_players, 1)
            self.difficulty = min(2.0, max(0.5, ratio))
        
        print(f"🎯 Game difficulty: {self.difficulty:.2f}")


class HealthCheckCondition(Condition):
    """Health check condition"""
    
    def __init__(self, name, threshold=0.3, **kwargs):
        self.name = name
        self.threshold = threshold
    
    async def evaluate(self, blackboard):
        entity = blackboard.get("current_entity")
        if entity is None:
            return False
        
        health_percentage = entity.get_health_percentage()
        is_low_health = health_percentage < self.threshold
        
        print(f"❤️ Health check {self.name}: {health_percentage:.1%} (low: {is_low_health})")
        return is_low_health


class EnemyNearbyCondition(Condition):
    """Enemy nearby condition"""
    
    def __init__(self, name, detection_range=20.0, **kwargs):
        self.name = name
        self.detection_range = detection_range
    
    async def evaluate(self, blackboard):
        entity = blackboard.get("current_entity")
        world = blackboard.get("game_world")
        
        if entity is None or world is None:
            return False
        
        nearest_enemy = world.get_nearest_enemy(entity, self.detection_range)
        enemy_detected = nearest_enemy is not None
        
        if enemy_detected:
            distance = entity.position.distance_to(nearest_enemy.position)
            print(f"👹 Enemy detection {self.name}: {distance:.1f}m")
            blackboard.set("nearest_enemy", nearest_enemy)
        else:
            print(f"👹 Enemy detection {self.name}: No enemies nearby")
        
        return enemy_detected


class AllyNearbyCondition(Condition):
    """Ally nearby condition"""
    
    def __init__(self, name, detection_range=15.0, **kwargs):
        self.name = name
        self.detection_range = detection_range
    
    async def evaluate(self, blackboard):
        entity = blackboard.get("current_entity")
        world = blackboard.get("game_world")
        
        if entity is None or world is None:
            return False
        
        nearest_ally = world.get_nearest_ally(entity, self.detection_range)
        ally_detected = nearest_ally is not None
        
        if ally_detected:
            distance = entity.position.distance_to(nearest_ally.position)
            print(f"🤝 Ally detection {self.name}: {distance:.1f}m")
            blackboard.set("nearest_ally", nearest_ally)
        else:
            print(f"🤝 Ally detection {self.name}: No allies nearby")
        
        return ally_detected


class AttackAction(Action):
    """Attack action"""
    
    def __init__(self, name, **kwargs):
        self.name = name
    
    async def execute(self, blackboard):
        entity = blackboard.get("current_entity")
        target = blackboard.get("nearest_enemy")
        
        if entity is None or target is None:
            return Status.FAILURE
        
        print(f"⚔️ Executing attack: {self.name}")
        
        if isinstance(entity, Player):
            success = entity.shoot(target)
        elif isinstance(entity, Enemy):
            success = entity.attack(target)
        else:
            success = False
        
        if success:
            print(f"✅ Attack successful!")
            if not target.is_alive():
                print(f"💀 Target eliminated!")
            return Status.SUCCESS
        else:
            print(f"❌ Attack failed!")
            return Status.FAILURE


class MoveToTargetAction(Action):
    """Move to target action"""
    
    def __init__(self, name, **kwargs):
        self.name = name
    
    async def execute(self, blackboard):
        entity = blackboard.get("current_entity")
        target = blackboard.get("nearest_enemy")
        
        if entity is None or target is None:
            return Status.FAILURE
        
        print(f"🚶 Executing move to target: {self.name}")
        
        # Move towards target
        entity.move_towards(target.position, 0.5)
        
        # Check if close enough to attack
        distance = entity.position.distance_to(target.position)
        if isinstance(entity, Player) and distance <= 30.0:
            print(f"🎯 In shooting range!")
            return Status.SUCCESS
        elif isinstance(entity, Enemy) and distance <= 5.0:
            print(f"⚔️ In attack range!")
            return Status.SUCCESS
        else:
            print(f"🔄 Moving to target...")
            return Status.RUNNING


class RetreatAction(Action):
    """Retreat action"""
    
    def __init__(self, name, **kwargs):
        self.name = name
    
    async def execute(self, blackboard):
        entity = blackboard.get("current_entity")
        world = blackboard.get("game_world")
        
        if entity is None or world is None:
            return Status.FAILURE
        
        print(f"🏃 Executing retreat: {self.name}")
        
        # Find safe position (away from enemies)
        safe_position = Vector2(50, 50)  # Center of map
        
        # Move towards safe position
        entity.move_towards(safe_position, 0.5)
        
        # Check if reached safe position
        distance_to_safe = entity.position.distance_to(safe_position)
        if distance_to_safe < 10.0:
            print(f"✅ Reached safe position!")
            return Status.SUCCESS
        else:
            print(f"🔄 Retreating...")
            return Status.RUNNING


class HealAction(Action):
    """Heal action"""
    
    def __init__(self, name, **kwargs):
        self.name = name
    
    async def execute(self, blackboard):
        entity = blackboard.get("current_entity")
        
        if entity is None:
            return Status.FAILURE
        
        print(f"💊 Executing heal: {self.name}")
        
        # Simulate healing
        heal_amount = 20.0
        entity.health = min(entity.max_health, entity.health + heal_amount)
        
        print(f"💚 Healed {heal_amount} HP. Current health: {entity.health:.1f}")
        return Status.SUCCESS


class PatrolAction(Action):
    """Patrol action"""
    
    def __init__(self, name, **kwargs):
        self.name = name
    
    async def execute(self, blackboard):
        entity = blackboard.get("current_entity")
        
        if entity is None:
            return Status.FAILURE
        
        print(f"🔄 Executing patrol: {self.name}")
        
        # Generate patrol points if not set
        if not hasattr(entity, 'patrol_points') or not entity.patrol_points:
            entity.patrol_points = [
                Vector2(random.uniform(10, 90), random.uniform(10, 90)),
                Vector2(random.uniform(10, 90), random.uniform(10, 90)),
                Vector2(random.uniform(10, 90), random.uniform(10, 90))
            ]
            entity.current_patrol_index = 0
        
        # Move to current patrol point
        current_patrol = entity.patrol_points[entity.current_patrol_index]
        entity.move_towards(current_patrol, 0.3)
        
        # Check if reached patrol point
        distance_to_patrol = entity.position.distance_to(current_patrol)
        if distance_to_patrol < 5.0:
            entity.current_patrol_index = (entity.current_patrol_index + 1) % len(entity.patrol_points)
            print(f"✅ Reached patrol point {entity.current_patrol_index}")
            return Status.SUCCESS
        else:
            print(f"🔄 Patrolling...")
            return Status.RUNNING


class TeamCoordinationAction(Action):
    """Team coordination action"""
    
    def __init__(self, name, **kwargs):
        self.name = name
    
    async def execute(self, blackboard):
        entity = blackboard.get("current_entity")
        world = blackboard.get("game_world")
        
        if entity is None or world is None:
            return Status.FAILURE
        
        print(f"🤝 Executing team coordination: {self.name}")
        
        # Find nearest ally
        nearest_ally = world.get_nearest_ally(entity, 30.0)
        if nearest_ally is None:
            print(f"❌ No allies nearby for coordination")
            return Status.FAILURE
        
        # Coordinate with ally
        ally_distance = entity.position.distance_to(nearest_ally.position)
        if ally_distance > 15.0:
            # Move closer to ally
            entity.move_towards(nearest_ally.position, 0.3)
            print(f"🔄 Moving closer to ally...")
            return Status.RUNNING
        else:
            # In coordination range
            print(f"✅ Coordinating with ally at {ally_distance:.1f}m")
            return Status.SUCCESS


def register_custom_nodes():
    """Register custom node types"""
    register_node("HealthCheckCondition", HealthCheckCondition)
    register_node("EnemyNearbyCondition", EnemyNearbyCondition)
    register_node("AllyNearbyCondition", AllyNearbyCondition)
    register_node("AttackAction", AttackAction)
    register_node("MoveToTargetAction", MoveToTargetAction)
    register_node("RetreatAction", RetreatAction)
    register_node("HealAction", HealAction)
    register_node("PatrolAction", PatrolAction)
    register_node("TeamCoordinationAction", TeamCoordinationAction)


async def main():
    """Main function - demonstrate XML-based game AI configuration"""
    
    print("=== ABTree Game AI XML Configuration Example ===\n")
    
    # Register custom node types
    register_custom_nodes()
    
    # Create game world
    world = GameWorld()
    
    # Add players
    player1 = Player(1, Vector2(10, 10), 1)
    player2 = Player(2, Vector2(20, 20), 1)
    world.add_player(player1)
    world.add_player(player2)
    
    # Add enemies
    enemy1 = Enemy(1, Vector2(80, 80), 2)
    enemy2 = Enemy(2, Vector2(85, 85), 2)
    world.add_enemy(enemy1)
    world.add_enemy(enemy2)
    
    # Create behavior tree
    tree = BehaviorTree()
    
    # Define XML configuration string
    xml_config = '''
    <BehaviorTree name="GameAIXML" description="Game AI with XML configuration">
        <Selector name="Game AI Root">
            <!-- Low health handling (highest priority) -->
            <Sequence name="Low Health Handling">
                <HealthCheckCondition name="Check Low Health" threshold="0.3" />
                <RetreatAction name="Retreat to Safety" />
                <HealAction name="Heal Self" />
            </Sequence>
            
            <!-- Combat behavior -->
            <Sequence name="Combat Behavior">
                <EnemyNearbyCondition name="Check Enemy Nearby" detection_range="25.0" />
                <MoveToTargetAction name="Move to Enemy" />
                <AttackAction name="Attack Enemy" />
            </Sequence>
            
            <!-- Team coordination -->
            <Sequence name="Team Coordination">
                <AllyNearbyCondition name="Check Ally Nearby" detection_range="20.0" />
                <TeamCoordinationAction name="Coordinate with Ally" />
            </Sequence>
            
            <!-- Patrol behavior -->
            <Sequence name="Patrol Behavior">
                <PatrolAction name="Patrol Area" />
            </Sequence>
        </Selector>
    </BehaviorTree>
    '''
    
    # Load XML configuration
    tree.load_from_string(xml_config)
    
    # Get blackboard and set initial data
    blackboard = tree.blackboard
    blackboard.set("game_world", world)
    blackboard.set("current_entity", player1)
    
    print("Game AI behavior tree configured:")
    print("  - Low health handling: Retreat and heal")
    print("  - Combat behavior: Attack enemies")
    print("  - Team coordination: Coordinate with allies")
    print("  - Patrol behavior: Patrol area")
    
    # Execute behavior tree
    print("\n=== Starting Game AI Execution ===")
    
    for i in range(20):
        print(f"\n--- Game Round {i+1} ---")
        
        # Update game world
        world.game_time += 0.5
        world.update_difficulty()
        
        # Execute AI for each entity
        for entity in [player1, player2, enemy1, enemy2]:
            if entity.is_alive():
                blackboard.set("current_entity", entity)
                print(f"\n🎮 {type(entity).__name__} {entity.id} AI:")
                
                result = await tree.tick()
                print(f"  Execution result: {result}")
                
                # Display entity status
                print(f"  Position: ({entity.position.x:.1f}, {entity.position.y:.1f})")
                print(f"  Health: {entity.health:.1f}/{entity.max_health:.1f}")
        
        # Display game status
        alive_players = sum(1 for p in world.players if p.is_alive())
        alive_enemies = sum(1 for e in world.enemies if e.is_alive())
        print(f"\n📊 Game Status: Players {alive_players}/2, Enemies {alive_enemies}/2")
        
        await asyncio.sleep(0.05)
    
    print("\nGame AI execution completed!")


if __name__ == "__main__":
    asyncio.run(main()) 