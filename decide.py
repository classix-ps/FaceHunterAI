import numpy as np
from enum import Enum

from hslog import packets
from hearthstone import entities, deckstrings, enums

class Action:
    action_types = Enum('action_types', 'play choose target minion_attack hero_attack hero_power start_game mulligan confirm_mulligan end_turn end_game concede')
    
    action_type = None
    positions = []
    
    def __init__(self, action_type, *args):
        self.action_type = self.action_types[action_type]
        self.positions = []
        for elem in args:
            self.positions.append(elem)
        
    def _create_coords(self, wincap, loc):
        coords = []
        
        for pos in loc:
            area, dist = pos
            index = np.random.choice(np.arange(len(area)), p=dist)
            coords.append(wincap.get_screen_position(area[index]))

        return coords    
        
    def convert_to_command(self, dists, wincap):
        if self.action_type == self.action_types.play:
            if len(self.positions) == 2:
                loc = [dists['hand'][self.positions[0]-1][self.positions[1]-1], dists['play']]
            elif len(self.positions) == 3:
                loc = [dists['hand'][self.positions[0]-1][self.positions[1]-1], dists['play'], dists['heros'][self.positions[2]]]
            elif len(self.positions) == 5:
                loc = [dists['hand'][self.positions[0]-1][self.positions[1]-1], dists['play'], dists['minions'][self.positions[2]][self.positions[3]-1][self.positions[4]-1]]
        elif self.action_type == self.action_types.choose:
            loc = [dists['choose'][self.positions[0]-1][self.positions[1]]]
        elif self.action_type == self.action_types.target:
            if len(self.positions) == 3:
                loc = [dists['hand'][self.positions[0]-1][self.positions[1]-1], dists['heros'][self.positions[2]]]
            elif len(self.positions) == 5:
                loc = [dists['hand'][self.positions[0]-1][self.positions[1]-1], dists['minions'][self.positions[2]][self.positions[3]-1][self.positions[4]-1]]
        elif self.action_type == self.action_types.minion_attack:
            if len(self.positions) == 2:
                loc = [dists['minions'][0][self.positions[0]-1][self.positions[1]-1], dists['heros'][1]]
            elif len(self.positions) == 4:
                loc = [dists['minions'][0][self.positions[0]-1][self.positions[1]-1], dists['minions'][1][self.positions[2]-1][self.positions[3]-1]]
        elif self.action_type == self.action_types.hero_attack:
            if len(self.positions) == 0:
                loc = [dists['heros'][0], dists['heros'][1]]
            elif len(self.positions) == 2:
                loc = [dists['heros'][0], dists['minions'][1][self.positions[0]-1][self.positions[1]-1]]
        elif self.action_type == self.action_types.hero_power:
            if len(self.positions) == 0:
                loc = [dists['hero_power']]
            elif len(self.positions) == 1:
                loc = [dists['hero_power'], dists['heros'][self.positions[0]]]
            elif len(self.positions) == 3:
                loc = [dists['hero_power'], dists['minions'][self.positions[0]][self.positions[1]-1][self.positions[2]-1]]
        elif self.action_type == self.action_types.start_game:
            loc = [dists['start_game']]
        elif self.action_type == self.action_types.mulligan:
            loc = [dists['mulligan'][self.positions[0]][self.positions[1]-1]]
        elif self.action_type == self.action_types.confirm_mulligan:
            loc = [dists['confirm_mulligan']]
        elif self.action_type == self.action_types.end_turn:
            loc = [dists['end_turn']]
        elif self.action_type == self.action_types.end_game:
            loc = [dists['end_game']]
        elif self.action_type == self.action_types.concede:
            loc = [dists['concede']]
            
        return self._create_coords(wincap, loc)
            
class Decide:
    player_index = None
    enemy_index = None
    
    decklist = None
    
    def __init__(self, decklist):
        self.decklist = decklist
        return
        
    def set_player_indices(self, player_index, enemy_index):
        self.player_index = player_index
        self.enemy_index = enemy_index
    
    def _is_trait(self, entity, trait, expected_val=1):
        return (trait in entity.tags.keys() and entity.tags[trait] == expected_val)
    
    def _is_not_trait(self, entity, trait, expected_val=1):
        return (trait not in entity.tags.keys() or entity.tags[trait] != expected_val)
    
    def _get_trait_default(self, entity, trait, default=0):
        return default if trait not in entity.tags.keys() else entity.tags[trait]
    
    def mulligan(self, entity_tree):
        packet_tree = entity_tree.packet_tree
        mulligan_packet = next((packet for packet in packet_tree if type(packet) == packets.Choices and packet.entity == self.player_index + 2), None)
        if mulligan_packet:
            choices = mulligan_packet.choices
            if len(choices) == 5:
                choices.pop(-1) # Remove coin
                mulligan_count = 1 # Going second
            else:
                mulligan_count = 0 # Going first
            mulligans = [Action('mulligan', mulligan_count, self._get_trait_default(entity_tree.game.find_entity_by_id(choice), entities.GameTag.ZONE_POSITION)) for choice in choices if self._get_trait_default(entity_tree.game.find_entity_by_id(choice), entities.GameTag.TAG_LAST_KNOWN_COST_IN_HAND) > 2]
            return mulligans
        else:
            return []
    
    def primitive_play_order(self, entity_tree):
        packet = entity_tree.packet_tree.packets[-1]
    
        # A decision needs to be made when playing a card.
        # This needs to be handled before the options.
        if type(packet) == packets.Block and packet.type == enums.BlockType.PLAY:
            choices = packet.packets[-1].packets[-1].choices
            cards = [entity_tree.game.find_entity_by_id(choice) for choice in choices]
            
            #mana = self._get_trait_default(self.entity_tree.game.players[self.player_index], entities.GameTag.RESOURCES) + self._get_trait_default(self.entity_tree.game.players[self.player_index], entities.GameTag.TEMP_RESOURCES) - self._get_trait_default(self.entity_tree.game.players[self.player_index], entities.GameTag.RESOURCES_USED)
            mana = sum([self._get_trait_default(self.entity_tree.game.players[self.player_index], entities.GameTag.RESOURCES),
                self._get_trait_default(self.entity_tree.game.players[self.player_index], entities.GameTag.TEMP_RESOURCES),
                -self._get_trait_default(self.entity_tree.game.players[self.player_index], entities.GameTag.RESOURCES_USED)])

            closest_to_mana = np.argmin(np.abs(np.asarray([self._get_trait_default(card, entities.GameTag.LAST_KNOWN_COST_IN_HAND) for card in cards]) - mana))

            return Action('choose', len(choices), closest_to_mana)
    
        # Find all options and classify them.
        if type(packet) == packets.Options:
            minion_count = [0, 0]
            hand_count = 0
            for entity in entity_tree.game.players[self.player_index].entities:
                if entity.zone == entities.Zone.PLAY and entity.type == enums.CardType.MINION:
                    minion_count[0] += 1
                elif entity.zone == entities.Zone.HAND:
                    hand_count += 1
            for entity in entity_tree.game.players[self.enemy_index].entities:
                if entity.zone == entities.Zone.PLAY and entity.type == enums.CardType.MINION:
                    minion_count[1] += 1
                    
            options = packet.options
            options.pop(0) # End turn option
            
            hand_minion = next((option for option in options if option.error is None and entity_tree.game.find_entity_by_id(option.entity).zone == entities.Zone.HAND and entity_tree.game.find_entity_by_id(option.entity).type == entities.CardType.MINION), None)
            if hand_minion:
                card = entity_tree.game.find_entity_by_id(hand_minion.entity)
                target_cards = [entity_tree.game.find_entity_by_id(target.entity) for target in hand_minion.options if target.error is None]
                if target_cards:
                    enemy_hero = next((target for target in target_cards if self._is_trait(target, entities.GameTag.CARDTYPE, enums.CardType.HERO) and self._is_trait(target, entities.GameTag.CONTROLLER, self.enemy_index + 1)), None)
                    if enemy_hero:
                        return Action('play', hand_count, self._get_trait_default(card, entities.GameTag.ZONE_POSITION))
                    ally_minion = next((target for target in target_cards if self._is_trait(target, entities.GameTag.CARDTYPE, enums.CardType.MINION) and self._is_trait(target, entities.GameTag.CONTROLLER, self.player_index + 1)), None)
                    if ally_minion:
                        return Action('play', hand_count, self._get_trait_default(card, entities.GameTag.ZONE_POSITION), 0, minion_count[0], self._get_trait_default(ally_minion, entities.GameTag.ZONE_POSITION))
                else:
                    return Action('play', hand_count, self._get_trait_default(card, entities.GameTag.ZONE_POSITION))
                
            hand_spell = next((option for option in options if option.error is None and entity_tree.game.find_entity_by_id(option.entity).zone == entities.Zone.HAND and entity_tree.game.find_entity_by_id(option.entity).type == entities.CardType.SPELL), None)
            if hand_spell:
                card = entity_tree.game.find_entity_by_id(hand_spell.entity)
                target_cards = [entity_tree.game.find_entity_by_id(target.entity) for target in hand_spell.options if target.error is None]
                if target_cards:
                    enemy_hero = next((target for target in target_cards if self._is_trait(target, entities.GameTag.CARDTYPE, enums.CardType.HERO) and self._is_trait(target, entities.GameTag.CONTROLLER, self.enemy_index + 1)), None)
                    if enemy_hero:
                        return Action('target', hand_count, self._get_trait_default(card, entities.GameTag.ZONE_POSITION), 1)
                    ally_minion = next((target for target in target_cards if self._is_trait(target, entities.GameTag.CARDTYPE, enums.CardType.MINION) and self._is_trait(target, entities.GameTag.CONTROLLER, self.player_index + 1)), None)
                    if ally_minion:
                        return Action('target', hand_count, self._get_trait_default(card, entities.GameTag.ZONE_POSITION), 0, minion_count[0], self._get_trait_default(ally_minion, entities.GameTag.ZONE_POSITION))
                else:
                    return Action('play', hand_count, self._get_trait_default(card, entities.GameTag.ZONE_POSITION))
                
            hand_weapon = next((option for option in options if option.error is None and entity_tree.game.find_entity_by_id(option.entity).zone == entities.Zone.HAND and entity_tree.game.find_entity_by_id(option.entity).type == entities.CardType.WEAPON), None)
            if hand_weapon:
                card = entity_tree.game.find_entity_by_id(hand_weapon.entity)
                return Action('play', hand_count, self._get_trait_default(card, entities.GameTag.ZONE_POSITION))
            
            hand_hero = next((option for option in options if option.error is None and entity_tree.game.find_entity_by_id(option.entity).zone == entities.Zone.HAND and entity_tree.game.find_entity_by_id(option.entity).type == entities.CardType.HERO), None)
            if hand_hero:
                card = entity_tree.game.find_entity_by_id(hand_hero.entity)
                return Action('play', hand_count, self._get_trait_default(card, entities.GameTag.ZONE_POSITION))
            
            ally_attack = next((option for option in options if option.error is None and entity_tree.game.find_entity_by_id(option.entity).zone == entities.Zone.PLAY and entity_tree.game.find_entity_by_id(option.entity).type == entities.CardType.MINION), None)
            if ally_attack:
                card = entity_tree.game.find_entity_by_id(ally_attack.entity)
                target_cards = [entity_tree.game.find_entity_by_id(target.entity) for target in ally_attack.options if target.error is None]
                enemy_hero = next((target for target in target_cards if self._is_trait(target, entities.GameTag.CARDTYPE, enums.CardType.HERO)), None)
                if enemy_hero:
                    return Action('minion_attack', minion_count[0], self._get_trait_default(card, entities.GameTag.ZONE_POSITION))
                else:
                    return Action('minion_attack', minion_count[0], self._get_trait_default(card, entities.GameTag.ZONE_POSITION), minion_count[1], self._get_trait_default(target_cards[0], entities.GameTag.ZONE_POSITION))

            hero_attack = next((option for option in options if option.error is None and entity_tree.game.find_entity_by_id(option.entity).type == entities.CardType.HERO), None)
            if hero_attack:
                card = entity_tree.game.find_entity_by_id(hero_attack.entity)
                target_cards = [entity_tree.game.find_entity_by_id(target.entity) for target in hero_attack.options if target.error is None]
                enemy_taunt = next((target for target in target_cards if self._is_trait(target, entities.GameTag.CARDTYPE, enums.CardType.MINION) and self._is_trait(target, entities.GameTag.TAUNT)), None)
                if enemy_taunt:
                    return Action('hero_attack', minion_count[1], self._get_trait_default(enemy_taunt, entities.GameTag.ZONE_POSITION))
                enemy_hero = next((target for target in target_cards if self._is_trait(target, entities.GameTag.CARDTYPE, enums.CardType.HERO)), None)
                if enemy_hero:
                    return Action('hero_attack')
                
            hero_power = next((option for option in options if option.error is None and entity_tree.game.find_entity_by_id(option.entity).type == entities.CardType.HERO_POWER), None)
            if hero_power:
                card = entity_tree.game.find_entity_by_id(hero_power.entity)
                target_cards = [entity_tree.game.find_entity_by_id(target.entity) for target in hero_power.options if target.error is None]
                if target_cards:
                    enemy_taunt = next((target for target in target_cards if self._is_trait(target, entities.GameTag.CARDTYPE, enums.CardType.MINION) and self._is_trait(target, entities.GameTag.TAUNT) and self._is_trait(target, entities.GameTag.CONTROLLER, self.enemy_index + 1)), None)
                    if enemy_taunt:
                        return Action('hero_power', 1, minion_count[1], self._get_trait_default(enemy_taunt, entities.GameTag.ZONE_POSITION))
                    enemy_hero = next((target for target in target_cards if self._is_trait(target, entities.GameTag.CARDTYPE, enums.CardType.HERO) and self._is_trait(target, entities.GameTag.CONTROLLER, self.enemy_index + 1)), None)
                    if enemy_hero:
                        return Action('hero_power', 1)
                    enemy_minion = next((target for target in target_cards if self._is_trait(target, entities.GameTag.CARDTYPE, enums.CardType.MINION) and self._is_trait(target, entities.GameTag.CONTROLLER, self.enemy_index + 1)), None)
                    if enemy_minion:
                        return Action('hero_power', 1, minion_count[1], self._get_trait_default(enemy_minion, entities.GameTag.ZONE_POSITION))
                else:
                    return Action('hero_power')
                
            return Action('end_turn')
            
        return None
            
    def primitive(self, entity_tree):
        packet = entity_tree.packet_tree.packets[-1]
        
        # A decision needs to be made when playing a card.
        # This needs to be handled before the options.
        if type(packet) == packets.Block and packet.type == enums.BlockType.PLAY:
            choices = packet.packets[-1].packets[-1].choices
            cards = [entity_tree.game.find_entity_by_id(choice) for choice in choices]
            
            #mana = self._get_trait_default(self.entity_tree.game.players[self.player_index], entities.GameTag.RESOURCES) + self._get_trait_default(self.entity_tree.game.players[self.player_index], entities.GameTag.TEMP_RESOURCES) - self._get_trait_default(self.entity_tree.game.players[self.player_index], entities.GameTag.RESOURCES_USED)
            mana = sum([self._get_trait_default(self.entity_tree.game.players[self.player_index], entities.GameTag.RESOURCES),
                self._get_trait_default(self.entity_tree.game.players[self.player_index], entities.GameTag.TEMP_RESOURCES),
                -self._get_trait_default(self.entity_tree.game.players[self.player_index], entities.GameTag.RESOURCES_USED)])

            closest_to_mana = np.argmin(np.abs(np.asarray([self._get_trait_default(card, entities.GameTag.LAST_KNOWN_COST_IN_HAND) for card in cards]) - mana))

            return Action('choose', len(choices), closest_to_mana)
        
        # Find all options and classify them.
        if type(packet) == packets.Options:
            minion_count = [0, 0]
            hand_count = 0
            for entity in entity_tree.game.players[self.player_index].entities:
                if entity.zone == entities.Zone.PLAY and entity.type == enums.CardType.MINION:
                    minion_count[0] += 1
                elif entity.zone == entities.Zone.HAND:
                    hand_count += 1
            for entity in entity_tree.game.players[self.enemy_index].entities:
                if entity.zone == entities.Zone.PLAY and entity.type == enums.CardType.MINION:
                    minion_count[1] += 1
            
            options = packet.options
            options.pop(0) # End turn option
            for option in options:
                if option.error is None:
                    card = entity_tree.game.find_entity_by_id(option.entity)
                    
                    targets = option.options
                    target_cards = [entity_tree.game.find_entity_by_id(target.entity) for target in targets if target.error is None]
                    
                    if card.zone == entities.Zone.PLAY and card.type == entities.CardType.MINION:
                        for target in target_cards:
                            if self._is_trait(target, entities.GameTag.CARDTYPE, enums.CardType.HERO):
                                return Action('minion_attack', minion_count[0], self._get_trait_default(card, entities.GameTag.ZONE_POSITION))
                        return Action('minion_attack', minion_count[0], self._get_trait_default(card, entities.GameTag.ZONE_POSITION), minion_count[1], self._get_trait_default(target_cards[0], entities.GameTag.ZONE_POSITION))
                    elif card.zone == entities.Zone.HAND:
                        card_pos = self._get_trait_default(card, entities.GameTag.ZONE_POSITION)
                        enemy_hero = []
                        ally_minions = []
                        if target_cards:
                            for target in target_cards:
                                if self._is_trait(target, entities.GameTag.CARDTYPE, enums.CardType.HERO) and self._is_trait(target, entities.GameTag.CONTROLLER, self.enemy_index + 1):
                                    enemy_hero.append(target)
                                if self._is_trait(target, entities.GameTag.CARDTYPE, enums.CardType.MINION) and self._is_trait(target, entities.GameTag.CONTROLLER, self.player_index + 1):
                                    ally_minions.append(target)
                            if enemy_hero:
                                if self._is_trait(card, entities.GameTag.CARDTYPE, enums.CardType.MINION):
                                    return Action('play', hand_count, card_pos, 1)
                                elif self._is_trait(card, entities.GameTag.CARDTYPE, enums.CardType.SPELL):
                                    return Action('target', hand_count, card_pos, 1)
                            if ally_minions:
                                if self._is_trait(card, entities.GameTag.CARDTYPE, enums.CardType.MINION):
                                    return Action('play', hand_count, card_pos, 0, minion_count[0], self._get_trait_default(ally_minions[0], entities.GameTag.ZONE_POSITION))
                                elif self._is_trait(card, entities.GameTag.CARDTYPE, enums.CardType.SPELL):
                                    return Action('target', hand_count, card_pos, 0, minion_count[0], self._get_trait_default(ally_minions[0], entities.GameTag.ZONE_POSITION))
                        else:
                            return Action('play', hand_count, card_pos)
                    elif card.type == entities.CardType.HERO:
                        enemy_taunts = []
                        enemy_hero = []
                        for target in target_cards:
                            if self._is_trait(target, entities.GameTag.CARDTYPE, enums.CardType.MINION) and self._is_trait(target, entities.GameTag.TAUNT):
                                enemy_taunts.append(target)
                            if self._is_trait(target, entities.GameTag.CARDTYPE, enums.CardType.HERO):
                                enemy_hero.append(target)
                            if enemy_taunts:
                                return Action('hero_attack', minion_count[1], self._get_trait_default(enemy_taunts[0], entities.GameTag.ZONE_POSITION))
                            if enemy_hero:
                                return Action('hero_attack')
                    elif card.type == entities.CardType.HERO_POWER:
                        if target_cards:
                            enemy_taunts = []
                            enemy_hero = []
                            enemy_minions = []
                            for target in target_cards:
                                if self._is_trait(target, entities.GameTag.CARDTYPE, enums.CardType.MINION) and self._is_trait(target, entities.GameTag.TAUNT) and self._is_trait(target, entities.GameTag.CONTROLLER, self.enemy_index + 1):
                                    enemy_taunts.append(target)
                                if self._is_trait(target, entities.GameTag.CARDTYPE, enums.CardType.HERO) and self._is_trait(target, entities.GameTag.CONTROLLER, self.enemy_index + 1):
                                    enemy_hero.append(target)
                                if self._is_trait(target, entities.GameTag.CARDTYPE, enums.CardType.MINION) and self._is_trait(target, entities.GameTag.CONTROLLER, self.enemy_index + 1):
                                    enemy_minions.append(target)
                            if enemy_taunts:
                                return Action('hero_power', 1, minion_count[1], self._get_trait_default(enemy_taunts[0], entities.GameTag.ZONE_POSITION))
                            if enemy_hero:
                                return Action('hero_power', 1)
                            if enemy_minions:
                                return Action('hero_power', 1, minion_count[1], self._get_trait_default(enemy_minions[0], entities.GameTag.ZONE_POSITION))
                        else:
                            return Action('hero_power')
                
        return Action('end_turn')