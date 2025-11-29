# -*- coding: utf-8 -*-
"""
Real-Time Sports Chatbot
Live cricket o football data
"""

import asyncio
from realtime_mcp_client import RealTimeMCPClient
from datetime import datetime


class RealTimeSportsChatbot:
    """Real-time sports information chatbot"""
    
    def __init__(self):
        self.client = RealTimeMCPClient()
        self.is_running = False
        self.cache = {
            'cricket': [],
            'football': [],
            'last_updated': None
        }
    
    async def initialize(self):
        """Initialize chatbot"""
        print("\n🔄 Starting Real-Time Sports Chatbot...")
        success = await self.client.connect()
        if success:
            self.is_running = True
            print("✅ Chatbot ready! Real-time data available.")
            # Pre-fetch data
            await self.refresh_cache()
        return success
    
    async def refresh_cache(self):
        """Cache update for faster responses"""
        print("🔄 Refreshing data cache...")
        self.cache['cricket'] = await self.client.fetch_cricket_current_matches()
        self.cache['football'] = await self.client.fetch_football_today_matches()
        self.cache['last_updated'] = datetime.now()
        print(f"✅ Cache updated at {datetime.now().strftime('%H:%M:%S')}")
    
    async def shutdown(self):
        """Shutdown"""
        await self.client.disconnect()
        self.is_running = False
    
    def print_header(self, title: str, emoji: str = "📋"):
        """Pretty header"""
        print("\n" + "="*70)
        print(f"{emoji} {title}")
        print("="*70)
    
    async def show_live_cricket(self):
        """Live cricket matches with real data"""
        self.print_header("🔴 LIVE CRICKET MATCHES", "🏏")
        
        matches = self.cache.get('cricket', [])
        
        if not matches:
            print("\n⏳ Fetching latest data...")
            matches = await self.client.fetch_cricket_current_matches()
            self.cache['cricket'] = matches
        
        live_matches = [m for m in matches if 'live' in m.get('status', '').lower() 
                       or 'inning' in m.get('status', '').lower()]
        
        if not live_matches:
            upcoming = [m for m in matches if 'not started' in m.get('status', '').lower()]
            
            if upcoming:
                print("\n📺 Ekhon kono live match nai. Upcoming matches:")
                for i, match in enumerate(upcoming[:5], 1):
                    print(f"\n{i}. 🏆 {match['team1']} vs {match['team2']}")
                    print(f"   Format: {match['format']}")
                    print(f"   Status: {match['status']}")
                    print(f"   Venue: {match['venue']}")
                    print(f"   Series: {match['series']}")
            else:
                print("\n📺 Kono match information pawa jacche na.")
        else:
            for i, match in enumerate(live_matches, 1):
                print(f"\n🔴 LIVE {i}. {match['team1']} vs {match['team2']}")
                print(f"   Format: {match['format']}")
                print(f"   Status: {match['status']}")
                print(f"   Venue: {match['venue']}")
                if match.get('score'):
                    print(f"   Score: {match['score']}")
        
        print(f"\n⏰ Last updated: {self.cache['last_updated'].strftime('%H:%M:%S') if self.cache['last_updated'] else 'N/A'}")
        print("="*70)
    
    async def show_live_football(self):
        """Live football matches"""
        self.print_header("🔴 LIVE FOOTBALL MATCHES", "⚽")
        
        matches = self.cache.get('football', [])
        
        if not matches:
            print("\n⏳ Fetching latest data...")
            matches = await self.client.fetch_football_today_matches()
            self.cache['football'] = matches
        
        live_matches = [m for m in matches if 'live' in m.get('status', '').lower() 
                       or 'progress' in m.get('status', '').lower()]
        
        if not live_matches:
            upcoming = [m for m in matches if 'not started' in m.get('status', '').lower()]
            
            if upcoming:
                print("\n📺 Ekhon kono live match nai. Today's matches:")
                for i, match in enumerate(upcoming[:5], 1):
                    print(f"\n{i}. ⚽ {match['team1']} vs {match['team2']}")
                    print(f"   League: {match['league']}")
                    print(f"   Status: {match['status']}")
                    print(f"   Venue: {match['venue']}")
                    print(f"   Country: {match['country']}")
            else:
                print("\n📺 Kono match information pawa jacche na.")
        else:
            for i, match in enumerate(live_matches, 1):
                print(f"\n🔴 LIVE {i}. {match['team1']} vs {match['team2']}")
                print(f"   League: {match['league']}")
                print(f"   Status: {match['status']}")
                print(f"   Venue: {match['venue']}")
                if match.get('score'):
                    score = match['score']
                    print(f"   Score: {score.get('home', 0)} - {score.get('away', 0)}")
        
        print(f"\n⏰ Last updated: {self.cache['last_updated'].strftime('%H:%M:%S') if self.cache['last_updated'] else 'N/A'}")
        print("="*70)
    
    async def show_all_live(self):
        """All live matches"""
        await self.show_live_cricket()
        await self.show_live_football()
    
    async def show_today_cricket(self):
        """Today's cricket"""
        self.print_header("📅 TODAY'S CRICKET MATCHES", "🏏")
        
        matches = self.cache.get('cricket', [])
        if not matches:
            matches = await self.client.fetch_cricket_current_matches()
        
        for i, match in enumerate(matches[:8], 1):
            print(f"\n{i}. 🏆 {match['team1']} vs {match['team2']}")
            print(f"   Format: {match['format']}")
            print(f"   Status: {match['status']}")
            print(f"   Venue: {match['venue']}")
            print(f"   Series: {match['series']}")
        
        print("\n" + "="*70)
    
    async def show_today_football(self):
        """Today's football"""
        self.print_header("📅 TODAY'S FOOTBALL MATCHES", "⚽")
        
        matches = self.cache.get('football', [])
        if not matches:
            matches = await self.client.fetch_football_today_matches()
        
        for i, match in enumerate(matches[:8], 1):
            print(f"\n{i}. ⚽ {match['team1']} vs {match['team2']}")
            print(f"   League: {match['league']}")
            print(f"   Status: {match['status']}")
            print(f"   Venue: {match['venue']}")
        
        print("\n" + "="*70)
    
    async def show_country_info(self, country: str):
        """Country info"""
        info = await self.client.get_country_rankings(country)
        
        if not info:
            print(f"\n❌ '{country}' er data nai!")
            return
        
        self.print_header(f"{info['name'].upper()} INFO", "🌍")
        print(f"\n🏏 Cricket Rankings:")
        print(f"   Test: #{info['cricket']['test']}")
        print(f"   ODI: #{info['cricket']['odi']}")
        print(f"   T20: #{info['cricket']['t20']}")
        print(f"\n⚽ Football: FIFA #{info['football']['fifa_rank']}")
        print(f"\n📊 Last Updated: {info['last_updated']}")
        print("\n" + "="*70)
    
    def show_help(self):
        """Help menu"""
        self.print_header("COMMANDS - REAL-TIME DATA", "📖")
        print("\n🔴 LIVE:")
        print("   'live'              → All live matches")
        print("   'live cricket'      → Live cricket only")
        print("   'live football'     → Live football only")
        print("\n📅 TODAY:")
        print("   'today'             → Today's all matches")
        print("   'cricket'           → Cricket matches")
        print("   'football'          → Football matches")
        print("\n🌍 COUNTRY:")
        print("   'bangladesh'        → Country info")
        print("   'india', 'pakistan', etc.")
        print("\n⚙️  SYSTEM:")
        print("   'refresh'           → Refresh data")
        print("   'help'              → This menu")
        print("   'exit'              → Quit")
        print("\n💡 TIP: Data updates automatically!")
        print("="*70)
    
    async def process_command(self, cmd: str) -> bool:
        """Process user command"""
        cmd = cmd.lower().strip()
        
        if not cmd:
            return True
        
        # Exit
        if cmd in ['exit', 'quit', 'bye', 'bondho']:
            return False
        
        # Help
        if 'help' in cmd:
            self.show_help()
            return True
        
        # Refresh
        if 'refresh' in cmd or 'update' in cmd:
            await self.refresh_cache()
            print("\n✅ Data refreshed!")
            return True
        
        # Live matches
        if 'live' in cmd:
            if 'cricket' in cmd:
                await self.show_live_cricket()
            elif 'football' in cmd:
                await self.show_live_football()
            else:
                await self.show_all_live()
            return True
        
        # Today
        if 'today' in cmd or 'ajker' in cmd:
            await self.show_today_cricket()
            await self.show_today_football()
            return True
        
        # Cricket
        if 'cricket' in cmd:
            await self.show_today_cricket()
            return True
        
        # Football
        if 'football' in cmd:
            await self.show_today_football()
            return True
        
        # Countries
        countries = ['bangladesh', 'india', 'pakistan', 'australia', 'england']
        for country in countries:
            if country in cmd:
                await self.show_country_info(country)
                return True
        
        print("\n🤔 Command bujhini! 'help' type korun.")
        return True
    
    async def start(self):
        """Start chatbot"""
        if not await self.initialize():
            print("❌ Failed to start!")
            return
        
        print("\n" + "="*70)
        print(" "*10 + "🔴 REAL-TIME SPORTS CHATBOT 🔴")
        print("="*70)
        print("\n👋 Assalamu Alaikum! Live cricket o football data!")
        print("🔴 Real-time updates available\n")
        self.show_help()
        
        while self.is_running:
            try:
                user_input = input("\n💬 You: ").strip()
                should_continue = await self.process_command(user_input)
                
                if not should_continue:
                    print("\n👋 Khoda Hafez! 😊")
                    break
                    
            except KeyboardInterrupt:
                print("\n\n👋 Bye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
        
        await self.shutdown()


async def main():
    """Main entry"""
    chatbot = RealTimeSportsChatbot()
    await chatbot.start()


if __name__ == "__main__":
    print("\n🚀 Starting Real-Time Sports Chatbot...\n")
    asyncio.run(main())