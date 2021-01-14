from decide import Action
from decide import Decide
from execute import Execute
from windowcapture import WindowCapture

from hslog.parser import LogParser
from hslog.export import EntityTreeExporter
from hearthstone import entities

import os
import time
import keyboard

import pickle
        
class Game:
    parser = None
    dists = None
    wincap = None
    
    decide = None
    execute = None
    
    path = None
    name = None
    
    my_turn = None
    
    def kill(self):
        os._exit(0)
    
    def __init__(self, path, name, decklist):
        keyboard.add_hotkey('q', self.kill)
        
        self.parser = LogParser()
        with open('Areas/distributions.txt', 'rb') as f:
            self.dists = pickle.load(f)
        self.wincap = WindowCapture('Hearthstone')
        self.wincap.bring_to_front()
        
        self.decide = Decide(decklist)
        self.execute = Execute()
        
        self.path = path
        self.name = name
    
    def get_entity_tree(self):
        if os.path.isfile(self.path):
            with open(self.path, 'r') as f:
                self.parser.read(f)
                
            if self.parser.games:
                packet_tree = self.parser.games[-1]
                exporter = EntityTreeExporter(packet_tree)
                entity_tree = exporter.export()
                return entity_tree
        return None
    
    def start_game(self):
        entity_tree = self.get_entity_tree()
        if entity_tree is not None and self.decide._is_not_trait(entity_tree.game, entities.GameTag.STATE, entities.State.COMPLETE): # Game in progress
            print('Game in progress.')
            if entity_tree.game.players[0].name == self.name:
                self.decide.set_player_indices(0, 1)
            else:
                self.decide.set_player_indices(1, 0)
            if self.decide._is_not_trait(entity_tree.game, entities.GameTag.STEP, entities.Step.BEGIN_MULLIGAN):
                self.my_turn = self.decide._is_trait(entity_tree.game.players[self.decide.player_index], entities.GameTag.CURRENT_PLAYER)
                if self.my_turn:
                    print('It is your turn.')
                else:
                    print('It is the opponent\'s turn')
                return
        else:
            print('Starting game...')
            action = Action('start_game')
            self.execute.execute_command(action.convert_to_command(self.dists, self.wincap))
            time.sleep(5)
    
            while True:
                entity_tree = self.get_entity_tree()
                if entity_tree is not None and self.decide._is_trait(entity_tree.game, entities.GameTag.STEP, entities.Step.BEGIN_MULLIGAN):
                    print('Game started.')
                    if entity_tree.game.players[0].name == self.name:
                        self.decide.set_player_indices(0, 1)
                    else:
                        self.decide.set_player_indices(1, 0)
                    break
                time.sleep(1)
            time.sleep(20)
        
        self.my_turn = self.decide._is_trait(entity_tree.game.players[self.decide.player_index], entities.GameTag.FIRST_PLAYER)
        if self.my_turn:
            print('You are going first.')
        else:
            print('You are going second.')
        
        print('Mulliganing...')
        mulligans = self.decide.mulligan(entity_tree)
        #mulligans = self.decide.mulligan(self.get_entity_tree())
        for mulligan in mulligans:
            print(vars(mulligan))
            self.execute.execute_command(mulligan.convert_to_command(self.dists, self.wincap))
        action = Action('confirm_mulligan')
        self.execute.execute_command(action.convert_to_command(self.dists, self.wincap))
        time.sleep(15)
    
    def take_turn(self, entity_tree):
        #move = self.decide.primitive(entity_tree)
        move = self.decide.primitive_play_order(entity_tree)
        if move:
            print(vars(move))
            self.execute.execute_command(move.convert_to_command(self.dists, self.wincap))

    def exit_game(self):
        print('Game over.\n')
        time.sleep(10)
        action = Action('end_game')
        self.execute.execute_command(action.convert_to_command(self.dists, self.wincap))
        time.sleep(5)

    def run(self):
        while True:
            self.start_game()
            
            while self.decide._is_trait(self.get_entity_tree().game, entities.GameTag.STATE, entities.State.RUNNING):
                entity_tree = self.get_entity_tree()
                if self.decide._is_trait(entity_tree.game.players[self.decide.player_index], entities.GameTag.CURRENT_PLAYER, 1):
                    if not self.my_turn: # wait when turn starts to draw card
                        time.sleep(8)
                    self.take_turn(entity_tree)
                    self.my_turn = True
                else:
                    self.my_turn = False
                time.sleep(1) # Check state
                    
            self.exit_game()
        
game = Game('D:/Battle.net/Hearthstone/Logs/Power.log', 'mesmerizinq#2366', '')
game.run()