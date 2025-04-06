from sqlalchemy import create_engine, Column, Integer, String, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json
import os

Base = declarative_base()

class Card(Base):
    __tablename__ = 'cards'
    
    id = Column(Integer, primary_key=True)
    set_code = Column(String)
    card_number = Column(String)
    name = Column(String)
    type = Column(String)
    hp = Column(Integer)
    abilities = Column(JSON)
    weakness = Column(String)
    retreat_cost = Column(Integer)
    illustrator = Column(String)
    flavor_text = Column(String)
    image_url = Column(String)
    
    def __repr__(self):
        return f"<Card(name='{self.name}', set='{self.set_code}', number='{self.card_number}')>"

class Database:
    def __init__(self, db_path="data/pokemon_cards.db"):
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
    def add_card(self, card_data: dict):
        """Add a single card to the database"""
        card = Card(**card_data)
        self.session.add(card)
        self.session.commit()
        
    def add_cards_from_json(self, json_file: str):
        """Add multiple cards from a JSON file"""
        with open(json_file, 'r', encoding='utf-8') as f:
            cards = json.load(f)
            
        for card_data in cards:
            # Convert string values to appropriate types
            if 'hp' in card_data:
                card_data['hp'] = int(card_data['hp'].split()[0]) if card_data['hp'] else 0
            if 'retreat_cost' in card_data:
                card_data['retreat_cost'] = int(card_data['retreat_cost']) if card_data['retreat_cost'] else 0
                
            self.add_card(card_data)
            
    def get_card(self, set_code: str, card_number: str) -> Card:
        """Get a specific card by set code and number"""
        return self.session.query(Card).filter_by(
            set_code=set_code,
            card_number=card_number
        ).first()
        
    def get_cards_by_set(self, set_code: str) -> list:
        """Get all cards from a specific set"""
        return self.session.query(Card).filter_by(set_code=set_code).all()
        
    def get_all_cards(self) -> list:
        """Get all cards in the database"""
        return self.session.query(Card).all()
        
    def close(self):
        """Close the database session"""
        self.session.close()
        
def main():
    # Example usage
    db = Database()
    
    # Add cards from JSON file
    json_file = "data/shining_revelry_cards.json"
    if os.path.exists(json_file):
        db.add_cards_from_json(json_file)
        
    # Get all cards from a set
    cards = db.get_cards_by_set("A2b")
    for card in cards:
        print(card)
        
    db.close()
    
if __name__ == "__main__":
    main() 