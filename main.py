from src.pokemon_agent import PokemonInfoTool
def main():
    print("Hello from pokemon-agent-backend!")


if __name__ == "__main__":
    main()

tool = PokemonInfoTool()
tool.run("Pikachu")