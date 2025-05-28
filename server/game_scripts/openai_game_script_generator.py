#!/usr/bin/env python3
"""
OpenAI Game Script Generator

This script generates fantasy football game scripts using OpenAI's chat completion endpoint 
for each game in the `game-sample.json` file.

SETUP:
1. Install dependencies:
   pip install -r requirements.txt (from server directory)

2. Set up your OpenAI API key:
   Create a `.env` file in the root directory and add your OpenAI API key:
   
   
   Alternatively, you can set the environment variable directly:

USAGE:
Run the script from the server/game_scripts directory:
python openai_game_script_generator.py

WHAT IT DOES:
1. Reads game data from `game-sample.json`
2. Loads the prompt template from `game-script-generator-prompt.md`
3. Processes each game by calling OpenAI's chat completion endpoint
4. Generates 4-5 sentence game scripts following the fantasy football analysis framework
5. Saves results to `game_scripts_output.json`
6. Displays results in the console

OUTPUT:
The script creates a JSON file (`game_scripts_output.json`) containing:
- Total number of games processed
- Generation timestamp
- Individual results for each game with:
  - Game ID and matchup
  - Original game data
  - Generated script

FEATURES:
- Error handling for missing files and API errors
- Rate limiting protection with 1-second delays between API calls
- Cost optimization using gpt-4o-mini model
- Comprehensive logging of progress and results
- Structured output in both JSON and console formats

REQUIREMENTS:
- Python 3.7+
- OpenAI API key
- Internet connection for API calls

COST CONSIDERATIONS:
The script uses the `gpt-4o-mini` model for cost efficiency. With 16 games in the sample file, 
expect minimal API costs (typically under $0.10 total).

TROUBLESHOOTING:
- "OPENAI_API_KEY not set": Ensure your API key is properly configured in the .env file
- "File not found": Make sure `game-sample.json` and `game-script-generator-prompt.md` are in the same directory
- "API errors": Check your OpenAI account balance and API key validity

DEPENDENCIES (already in server/requirements.txt):
- openai>=1.0.0
- python-dotenv==1.0.1
"""

import json
import os
import time
from typing import Dict, List, Any
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GameScriptGenerator:
    """
    A class to generate fantasy football game scripts using OpenAI's chat completion endpoint.
    
    This class handles loading game data, prompt templates, and orchestrating the OpenAI API calls
    to generate detailed fantasy football analysis for each game.
    """
    
    def __init__(self):
        """
        Initialize the OpenAI client and load the prompt template.
        
        Raises:
            FileNotFoundError: If game-script-generator-prompt.md is not found
            Exception: If OpenAI client initialization fails
        """
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.prompt_template = self._load_prompt_template()
        
    def _load_prompt_template(self) -> str:
        """
        Load the prompt template from the markdown file.
        
        Returns:
            str: The complete prompt template content
            
        Raises:
            FileNotFoundError: If game-script-generator-prompt.md is not found
        """
        try:
            with open('game-script-generator-prompt.md', 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError("game-script-generator-prompt.md not found. Please ensure the file exists.")
    
    def _load_games_data(self) -> List[Dict[str, Any]]:
        """
        Load game data from the JSON file.
        
        Returns:
            List[Dict[str, Any]]: List of game dictionaries containing game data
            
        Raises:
            FileNotFoundError: If game-sample.json is not found
            ValueError: If JSON is invalid
        """
        try:
            with open('game-sample.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('games', [])
        except FileNotFoundError:
            raise FileNotFoundError("game-sample.json not found. Please ensure the file exists.")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in game-sample.json: {e}")
    
    def _format_game_data(self, game: Dict[str, Any]) -> str:
        """
        Format game data for inclusion in the OpenAI prompt.
        
        Args:
            game (Dict[str, Any]): Game data dictionary containing team info, spreads, and totals
            
        Returns:
            str: Formatted game data string for the prompt
        """
        return f"""
Game Data:
- Game ID: {game['game_id']}
- Away Team: {game['away_team']}
- Home Team: {game['home_team']}
- Over/Under: {game['over_under']}
- Away Spread: {game['away_spread']}
- Home Spread: {game['home_spread']}
- Away Implied Points: {game['away_implied']}
- Home Implied Points: {game['home_implied']}

Please generate a 4-5 sentence game script for this matchup following the framework provided.
"""
    
    def generate_game_script(self, game: Dict[str, Any]) -> str:
        """
        Generate a game script for a single game using OpenAI's chat completion endpoint.
        
        This method combines the prompt template with specific game data and sends it to OpenAI
        to generate a fantasy football analysis following the detailed framework.
        
        Args:
            game (Dict[str, Any]): Game data dictionary
            
        Returns:
            str: Generated game script or error message
        """
        game_data = self._format_game_data(game)
        full_prompt = f"{self.prompt_template}\n\n{game_data}"
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Using gpt-4o-mini for cost efficiency
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert fantasy football analyst. Generate concise, actionable game scripts based on the provided framework and game data."
                    },
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating script for game {game['game_id']}: {e}")
            return f"Error generating script for {game['away_team']} at {game['home_team']}"
    
    def process_all_games(self, output_file: str = "game_scripts_output.json") -> None:
        """
        Process all games and save results to a JSON file.
        
        This method orchestrates the entire process:
        1. Loads all game data
        2. Processes each game through OpenAI
        3. Saves results to JSON file
        4. Displays results in console
        
        Features include:
        - Progress tracking and logging
        - Rate limiting protection (1-second delays)
        - Error handling for individual games
        - Structured output in both JSON and console formats
        
        Args:
            output_file (str): Name of the output JSON file (default: "game_scripts_output.json")
        """
        games = self._load_games_data()
        results = []
        
        print(f"Processing {len(games)} games...")
        
        for i, game in enumerate(games, 1):
            print(f"Processing game {i}/{len(games)}: {game['away_team']} at {game['home_team']}")
            
            script = self.generate_game_script(game)
            
            result = {
                "game_id": game["game_id"],
                "matchup": f"{game['away_team']} at {game['home_team']}",
                "game_data": game,
                "generated_script": script
            }
            
            results.append(result)
            
            # Add a small delay to avoid rate limiting
            if i < len(games):
                time.sleep(1)
        
        # Save results to JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "total_games": len(results),
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "results": results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\nCompleted! Results saved to {output_file}")
        
        # Also print results to console
        print("\n" + "="*80)
        print("GENERATED GAME SCRIPTS")
        print("="*80)
        
        for result in results:
            print(f"\n{result['matchup']} (Game {result['game_id']})")
            print("-" * 50)
            print(result['generated_script'])

def main():
    """
    Main function to run the game script generator.
    
    This function:
    1. Checks for required environment variables
    2. Initializes the GameScriptGenerator
    3. Processes all games
    4. Handles any top-level errors
    
    Environment Variables Required:
        OPENAI_API_KEY

    Files Required:
        - game-sample.json: Contains the game data to process
        - game-script-generator-prompt.md: Contains the prompt template for OpenAI
    
    Output:
        - game_scripts_output.json: JSON file with all generated scripts
        - Console output: Progress updates and final results display
    """
    # Check for required environment variable
    if not os.getenv('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY environment variable not set.")
        print("Please set your OpenAI API key in your .env file or environment variables.")
        print("\nTo set up:")
        print("1. Create a .env file in the root directory")
        print("2. Add: OPENAI_API_KEY")
        print("3. Or export OPENAI_API_KEY")
        return
    
    try:
        generator = GameScriptGenerator()
        generator.process_all_games()
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("- Ensure game-sample.json exists in the current directory")
        print("- Ensure game-script-generator-prompt.md exists in the current directory")
        print("- Check your OpenAI API key and account balance")
        print("- Verify internet connection for API calls")

if __name__ == "__main__":
    main() 