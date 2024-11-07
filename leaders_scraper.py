from utils import get_leaders, save, load

def leaders_scraper():
    leaders_dict = get_leaders()
    
    save(leaders_dict, 'leaders.json')
    
    loaded_data = load('leaders.json')
    
    print(loaded_data)

if __name__ == "__main__":
    leaders_scraper()