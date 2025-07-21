#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 19: Game AI System - Game AI Applications

Demonstrates how to use ABTree to build a game AI system, including character behavior decisions, combat AI,
pathfinding algorithms, team coordination, and dynamic difficulty adjustment.

Key Learning Points:
    Character behavior decision-making
    Combat AI
    Pathfinding algorithms
    Team coordination
    Dynamic difficulty adjustment
    How to configure a game AI system using XML strings
"""

import asyncio
import math
import random
import time
from dataclasses import dataclass
from typing import List, Dict, Tuple
from abtree import BehaviorTree, Sequence, Selector, Action, Condition, register_node
from abtree.core import Status
from abtree.parser.xml_parser import XMLParser


# Register custom node types
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
        
        self.ammo -= 1
        self.last_shot_time = time.time()
        
        # Calculate damage
        damage = self.weapon_damage
        target.health = max(0, target.health - damage)
        
        print(f"Player {self.id} shoots target {target.id}, deals {damage} damage")
        return True
    
    def move_towards(self, target_pos: Vector2, delta_time: float):
        """Move towards target position"""
        direction = Vector2(target_pos.x - self.position.x, 
                          target_pos.y - self.position.y)
        direction = direction.normalize()
        
        move_distance = self.speed * delta_time
        self.position.x += direction.x * move_distance
        self.position.y += direction.y * move_distance
        
        print(f"Player {self.id} moves to ({self.position.x:.2f}, {self.position.y:.2f})")


class Enemy(GameEntity):
    """Enemy class"""
    
    def __init__(self, enemy_id: int, position: Vector2, team: int):
        super().__init__(enemy_id, position, 80.0, 80.0, 1.5, team)
        self.attack_damage = 15
        self.attack_range = 2.0
        self.attack_cooldown = 1.0
        self.last_attack_time = 0
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
        
        self.last_attack_time = time.time()
        damage = self.attack_damage
        target.health = max(0, target.health - damage)
        
        print(f"Enemy {self.id} attacks target {target.id}, deals {damage} damage")
        return True
    
    def move_towards(self, target_pos: Vector2, delta_time: float):
        """Move towards target position"""
        direction = Vector2(target_pos.x - self.position.x, 
                          target_pos.y - self.position.y)
        direction = direction.normalize()
        
        move_distance = self.speed * delta_time
        self.position.x += direction.x * move_distance
        self.position.y += direction.y * move_distance
        
        print(f"Enemy {self.id} moves to ({self.position.x:.2f}, {self.position.y:.2f})")


class GameWorld:
    """Game world"""
    
    def __init__(self):
        self.players = []
        self.enemies = []
        self.entities = []
        self.map_size = Vector2(100, 100)
        self.obstacles = []
        self.game_time = 0
        self.difficulty_level = 1.0
    
    def add_player(self, player: Player):
        """Add player"""
        self.players.append(player)
        self.entities.append(player)
    
    def add_enemy(self, enemy: Enemy):
        """Add enemy"""
        self.enemies.append(enemy)
        self.entities.append(enemy)
    
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
        
        for ally in self.entities:
            if (ally.team == entity.team and ally != entity and ally.is_alive()):
                distance = entity.position.distance_to(ally.position)
                if distance < min_distance:
                    min_distance = distance
                    nearest_ally = ally
        
        return nearest_ally
    
    def is_position_valid(self, position: Vector2) -> bool:
        """Check if position is valid"""
        return (0 <= position.x <= self.map_size.x and 
                0 <= position.y <= self.map_size.y)
    
    def update_difficulty(self):
        """Update game difficulty"""
        alive_players = sum(1 for p in self.players if p.is_alive())
        alive_enemies = sum(1 for e in self.enemies if e.is_alive())
        
        if alive_players > 0:
            self.difficulty_level = 1.0 + (alive_enemies / alive_players) * 0.5
        else:
            self.difficulty_level = 2.0
        
        print(f"Game difficulty updated: {self.difficulty_level:.2f}")


# Global game world instance for XML nodes
_global_game_world = None
_global_player = None
_global_enemy = None


class HealthCheckCondition(Condition):
    """Health check condition"""
    
    def __init__(self, name, threshold=0.3):
        super().__init__(name)
        self.threshold = threshold
    
    async def evaluate(self, blackboard):
        global _global_player
        if _global_player is None:
            return False
        
        health_percentage = _global_player.get_health_percentage()
        print(f"Health check condition {self.name}: health {health_percentage:.1%}, threshold {self.threshold:.1%}")
        return health_percentage < self.threshold


class EnemyNearbyCondition(Condition):
    """Enemy nearby check condition"""
    
    def __init__(self, name, detection_range=20.0):
        super().__init__(name)
        self.detection_range = detection_range
    
    async def evaluate(self, blackboard):
        global _global_game_world, _global_player
        if _global_game_world is None or _global_player is None:
            return False
        
        nearest_enemy = _global_game_world.get_nearest_enemy(_global_player, self.detection_range)
        has_enemy = nearest_enemy is not None
        
        if has_enemy:
            distance = _global_player.position.distance_to(nearest_enemy.position)
            print(f"Enemy nearby condition {self.name}: found enemy {nearest_enemy.id}, distance {distance:.2f}")
        else:
            print(f"Enemy nearby condition {self.name}: no enemies")
        
        return has_enemy


class AllyNearbyCondition(Condition):
    """Ally nearby check condition"""
    
    def __init__(self, name, detection_range=15.0):
        super().__init__(name)
        self.detection_range = detection_range
    
    async def evaluate(self, blackboard):
        global _global_game_world, _global_player
        if _global_game_world is None or _global_player is None:
            return False
        
        nearest_ally = _global_game_world.get_nearest_ally(_global_player, self.detection_range)
        has_ally = nearest_ally is not None
        
        if has_ally:
            distance = _global_player.position.distance_to(nearest_ally.position)
            print(f"Ally nearby condition {self.name}: found ally {nearest_ally.id}, distance {distance:.2f}")
        else:
            print(f"Ally nearby condition {self.name}: no allies")
        
        return has_ally


class AttackAction(Action):
    """Attack action"""
    
    def __init__(self, name):
        super().__init__(name)
    
    async def execute(self, blackboard):
        global _global_game_world, _global_player
        if _global_game_world is None or _global_player is None:
            return Status.FAILURE
        
        print(f"Attack action {self.name}: start attack")
        
        # Get nearest target
        target = _global_game_world.get_nearest_enemy(_global_player)
        if target and _global_player.can_shoot():
            success = _global_player.shoot(target)
            if success:
                print(f"Attack action {self.name}: attack successful")
                return Status.SUCCESS
        
        print(f"Attack action {self.name}: cannot attack")
        return Status.FAILURE


class MoveToTargetAction(Action):
    """Move to target action"""
    
    def __init__(self, name):
        super().__init__(name)
    
    async def execute(self, blackboard):
        global _global_game_world, _global_player
        if _global_game_world is None or _global_player is None:
            return Status.FAILURE
        
        print(f"Move to target action {self.name}: start moving")
        
        # Get target
        target = _global_game_world.get_nearest_enemy(_global_player)
        if not target:
            print(f"Move to target action {self.name}: no target")
            return Status.FAILURE
        
        # Move towards target
        _global_player.move_towards(target.position, 0.1)
        
        # Check if reached attack range
        distance = _global_player.position.distance_to(target.position)
        attack_range = 10.0  # Shooting range
        
        if distance <= attack_range:
            print(f"Move to target action {self.name}: reached attack range")
            return Status.SUCCESS
        else:
            print(f"Move to target action {self.name}: moving...")
            return Status.RUNNING


class RetreatAction(Action):
    """Retreat action"""
    
    def __init__(self, name):
        super().__init__(name)
    
    async def execute(self, blackboard):
        global _global_game_world, _global_player
        if _global_game_world is None or _global_player is None:
            return Status.FAILURE
        
        print(f"Retreat action {self.name}: start retreat")
        
        # Get nearest enemy
        nearest_enemy = _global_game_world.get_nearest_enemy(_global_player)
        if not nearest_enemy:
            print(f"Retreat action {self.name}: no enemies, no need to retreat")
            return Status.SUCCESS
        
        # Calculate retreat direction
        enemy_pos = nearest_enemy.position
        retreat_direction = Vector2(
            _global_player.position.x - enemy_pos.x,
            _global_player.position.y - enemy_pos.y
        )
        retreat_direction = retreat_direction.normalize()
        
        # Calculate retreat target position
        retreat_distance = 15.0
        retreat_target = Vector2(
            _global_player.position.x + retreat_direction.x * retreat_distance,
            _global_player.position.y + retreat_direction.y * retreat_distance
        )
        
        # Ensure retreat position is within valid range
        if not _global_game_world.is_position_valid(retreat_target):
            retreat_target = Vector2(
                max(0, min(_global_game_world.map_size.x, retreat_target.x)),
                max(0, min(_global_game_world.map_size.y, retreat_target.y))
            )
        
        # Move to retreat position
        _global_player.move_towards(retreat_target, 0.1)
        
        # Check if already far from enemy
        current_distance = _global_player.position.distance_to(nearest_enemy.position)
        if current_distance > 20.0:
            print(f"Retreat action {self.name}: retreat completed")
            return Status.SUCCESS
        else:
            print(f"Retreat action {self.name}: retreating...")
            return Status.RUNNING


class HealAction(Action):
    """Heal action"""
    
    def __init__(self, name):
        super().__init__(name)
    
    async def execute(self, blackboard):
        global _global_player
        if _global_player is None:
            return Status.FAILURE
        
        print(f"Heal action {self.name}: start healing")
        
        # Simulate healing process
        heal_amount = 20.0
        _global_player.health = min(_global_player.max_health, _global_player.health + heal_amount)
        
        print(f"Heal action {self.name}: healing completed, current health {_global_player.get_health_percentage():.1%}")
        return Status.SUCCESS


class PatrolAction(Action):
    """Patrol action"""
    
    def __init__(self, name):
        super().__init__(name)
    
    async def execute(self, blackboard):
        global _global_game_world, _global_player
        if _global_game_world is None or _global_player is None:
            return Status.FAILURE
        
        print(f"Patrol action {self.name}: start patrolling")
        
        # Generate patrol points
        if not hasattr(_global_player, 'patrol_points') or not _global_player.patrol_points:
            _global_player.patrol_points = [
                Vector2(random.uniform(0, _global_game_world.map_size.x),
                       random.uniform(0, _global_game_world.map_size.y))
                for _ in range(3)
            ]
            _global_player.current_patrol_index = 0
        
        # Move to current patrol point
        current_patrol_point = _global_player.patrol_points[_global_player.current_patrol_index]
        _global_player.move_towards(current_patrol_point, 0.1)
        
        # Check if reached patrol point
        distance = _global_player.position.distance_to(current_patrol_point)
        if distance < 2.0:
            _global_player.current_patrol_index = (_global_player.current_patrol_index + 1) % len(_global_player.patrol_points)
            print(f"Patrol action {self.name}: reached patrol point, moving to next")
        
        await asyncio.sleep(0.01)  # Fast simulation
        return Status.RUNNING


class TeamCoordinationAction(Action):
    """Team coordination action"""
    
    def __init__(self, name):
        super().__init__(name)
    
    async def execute(self, blackboard):
        global _global_game_world, _global_player
        if _global_game_world is None or _global_player is None:
            return Status.FAILURE
        
        print(f"Team coordination action {self.name}: start team coordination")
        
        # Get nearest ally
        nearest_ally = _global_game_world.get_nearest_ally(_global_player)
        if not nearest_ally:
            print(f"Team coordination action {self.name}: no allies")
            return Status.FAILURE
        
        # Move near ally
        support_position = Vector2(
            nearest_ally.position.x + random.uniform(-5, 5),
            nearest_ally.position.y + random.uniform(-5, 5)
        )
        
        # Ensure position is valid
        if not _global_game_world.is_position_valid(support_position):
            support_position = nearest_ally.position
        
        _global_player.move_towards(support_position, 0.1)
        
        # Check if reached support position
        distance = _global_player.position.distance_to(support_position)
        if distance < 3.0:
            print(f"Team coordination action {self.name}: reached support position")
            return Status.SUCCESS
        else:
            print(f"Team coordination action {self.name}: moving...")
            return Status.RUNNING


async def main():
    """Main function - demonstrate game AI system"""
    
    # Register custom node types
    register_custom_nodes()
    
    print("=== ABTree Game AI System Example ===\n")
    
    # 1. Create game world
    game_world = GameWorld()
    
    # 2. Create players and enemies
    player1 = Player(1, Vector2(10, 10), 1)
    player2 = Player(2, Vector2(15, 15), 1)
    enemy1 = Enemy(101, Vector2(80, 80), 2)
    enemy2 = Enemy(102, Vector2(85, 85), 2)
    
    game_world.add_player(player1)
    game_world.add_player(player2)
    game_world.add_enemy(enemy1)
    game_world.add_enemy(enemy2)
    
    # Set global references for XML nodes
    global _global_game_world, _global_player, _global_enemy
    _global_game_world = game_world
    _global_player = player1
    _global_enemy = enemy1
    
    # 3. Create behavior tree
    root = Selector("Game AI System")
    
    # 4. Create AI behavior trees for each entity
    
    # Player1 AI
    player1_ai = Selector("Player1 AI")
    
    # Emergency retreat
    player1_emergency = Sequence("Player1 Emergency Retreat")
    player1_emergency.add_child(HealthCheckCondition("Player1 Health Check", 0.2))
    player1_emergency.add_child(RetreatAction("Player1 Retreat"))
    
    # Attack behavior
    player1_attack = Sequence("Player1 Attack")
    player1_attack.add_child(EnemyNearbyCondition("Player1 Enemy Check", 20.0))
    player1_attack.add_child(MoveToTargetAction("Player1 Move to Target"))
    player1_attack.add_child(AttackAction("Player1 Attack"))
    
    # Team coordination
    player1_team = Sequence("Player1 Team Coordination")
    player1_team.add_child(AllyNearbyCondition("Player1 Ally Check", 15.0))
    player1_team.add_child(TeamCoordinationAction("Player1 Team Coordination"))
    
    # Patrol
    player1_patrol = PatrolAction("Player1 Patrol")
    
    player1_ai.add_child(player1_emergency)
    player1_ai.add_child(player1_attack)
    player1_ai.add_child(player1_team)
    player1_ai.add_child(player1_patrol)
    
    # Enemy1 AI
    enemy1_ai = Selector("Enemy1 AI")
    
    # Attack behavior
    enemy1_attack = Sequence("Enemy1 Attack")
    enemy1_attack.add_child(EnemyNearbyCondition("Enemy1 Target Check", 25.0))
    enemy1_attack.add_child(MoveToTargetAction("Enemy1 Move to Target"))
    enemy1_attack.add_child(AttackAction("Enemy1 Attack"))
    
    # Patrol
    enemy1_patrol = PatrolAction("Enemy1 Patrol")
    
    enemy1_ai.add_child(enemy1_attack)
    enemy1_ai.add_child(enemy1_patrol)
    
    # 5. Assemble main behavior tree
    root.add_child(player1_ai)
    root.add_child(enemy1_ai)
    
    # 6. Create behavior tree instance
    tree = BehaviorTree()
    tree.load_from_root(root)
    blackboard = tree.blackboard
    
    # 7. Initialize data
    blackboard.set("game_time", 0)
    blackboard.set("difficulty_level", 1.0)
    
    print("Starting game AI system execution...")
    print("=" * 50)
    
    # 8. Execute game loop - reduced to 3 seconds
    start_time = time.time()
    max_execution_time = 3.0  # 3 seconds max
    
    for i in range(10):  # Reduced iterations
        current_time = time.time()
        if current_time - start_time > max_execution_time:
            print(f"\nExecution time limit reached ({max_execution_time}s)")
            break
            
        print(f"\n--- Round {i+1} ---")
        
        # Update game time
        game_world.game_time += 1
        blackboard.set("game_time", game_world.game_time)
        
        # Update difficulty
        game_world.update_difficulty()
        blackboard.set("difficulty_level", game_world.difficulty_level)
        
        # Execute AI
        result = await tree.tick()
        print(f"AI execution result: {result}")
        
        # Display game status
        print(f"Player1: position({player1.position.x:.1f}, {player1.position.y:.1f}), "
              f"health{player1.get_health_percentage():.1%}, ammo{player1.ammo}")
        print(f"Enemy1: position({enemy1.position.x:.1f}, {enemy1.position.y:.1f}), "
              f"health{enemy1.get_health_percentage():.1%}")
        print(f"Game difficulty: {game_world.difficulty_level:.2f}")
        
        # Check game end conditions
        alive_players = sum(1 for p in game_world.players if p.is_alive())
        alive_enemies = sum(1 for e in game_world.enemies if e.is_alive())
        
        if alive_players == 0:
            print("Game over: All players dead")
            break
        elif alive_enemies == 0:
            print("Game over: All enemies eliminated")
            break
        
        await asyncio.sleep(0.01)  # Fast simulation
    
    execution_time = time.time() - start_time
    print(f"\n=== Game End ===")
    print(f"Execution time: {execution_time:.2f}s")
    print(f"Player1 final status: health{player1.get_health_percentage():.1%}")
    print(f"Enemy1 final status: health{enemy1.get_health_percentage():.1%}")
    print(f"Final game difficulty: {game_world.difficulty_level:.2f}")   
 


if __name__ == "__main__":
    asyncio.run(main()) 