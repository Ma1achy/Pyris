import pygame
from pygame_config import PyGameConfig
from handling import Handling
from four import Four
from render import Render
import time
import asyncio
from collections import deque 

class PyGameInstance():
    def __init__(self, show_all_debug:bool = False, show_render_debug:bool = False, show_tick_debug:bool = False):
        """"
        Create an instance of pygame to run the game
        
        args:
        (bool) show_all_debug: show all debug information
        (bool) show_render_debug: show only render debug information
        (bool) show_tick_debug: show only tick debug information
        """
        
        self.config = PyGameConfig()
        
        self.window = self.__init_window()
        self.render = Render(self.window)
        self.handling = Handling(self.config)
        
        self.render_clock = Clock()
        self.game_clock = Clock()
        self.current_time = 0
        
        self.next_frame_time = 0
        self.dt = 0
        self.exited = False
        
        self.show_all_debug = show_all_debug
        
        if show_all_debug:
            self.show_render_debug = True
            self.show_tick_debug = True
        else:
            self.show_render_debug = show_render_debug
            self.show_tick_debug = show_tick_debug
        
        self.debug_dict = True
        self.max_avg_len = 500
        
        self.tick_times = []
        self.exe_idx = 0
        self.worst_tick_time = 0
        self.best_tick_time = 0
        
        self.render_times = []
        self.r_idx = 0
        self.worst_render_time = 0
        self.best_render_time = 0
        
        self.tick_time = 0
        self.render_time_raw = 0
        
        self.FPSs = []
        self.FPS = self.config.FPS
        self.average_FPS = 0
        self.fps_idx = 0
        self.worst_fps = 0
        self.best_fps = 0
        
        self.TPSs = []
        self.TPS = self.config.TPS
        self.average_TPS = 0
        self.tps_idx = 0
        self.worst_tps = 0
        self.best_tps = 0
        
        self.dfs = []
        self.df_idx = 0
        self.average_df = 0
        self.delta_tick = 0
        self.worst_df = 0
        self.best_df = 0
                     
        self.state_snapshot = None
        self.next_tick_time = 0
        
        self.start_times = {
            'handle_events': 0,
            'game_loop': 0,
            'get_debug_info': 0,
            'render_loop': 0
        }
        
        self.elapsed_times = {
            'handle_events': 0,
            'game_loop': 0,
            'get_debug_info': 0,
            'render_loop': 0
        }
        
        self.iter_times = {
            'handle_events': 1,
            'game_loop': 1,
            'get_debug_info': 1,
            'render_loop': 1
        }
        
    def __initialise(self, four):
        """
        Initalise the instance of the game
        
        args:
        (Four) four: the instance of the game
        """
        self.state_snapshot = four.forward_state()
        self.start_time = time.perf_counter()
        pygame.init()
        
    def __init_window(self):
        """
        Create the window to draw to
        """
        pygame.display.set_caption(self.config.CAPTION)
        return pygame.display.set_mode((self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT), pygame.HWSURFACE|pygame.DOUBLEBUF)
    
    def __exit(self):
        """
        Exit the game
        """
        self.exited = True
        pygame.quit()
           
    async def run(self, four):
        """
        Run the game
    
        args:
        (Four) four: the instance of the game
        """
        
        self.__initialise(four)
        
        await asyncio.gather(
            self.__timing_wrapper("handle_events", self.__handle_events()),
            self.__timing_wrapper("game_loop", self.__game_loop(four)),
            self.__timing_wrapper("get_debug_info", self.__get_debug_info()),
            self.__timing_wrapper("render_loop", self.__render_loop()),
        )

    async def __timing_wrapper(self, name, coro):
        """
        Wrapper function to time coroutines of the game, 
        used to time the game loop, render loop and event handling loop
        
        args:
        (str) name: the name of the coroutine
        (coro) coro: the coroutine to time
        """
        
        self.start_times[name] = time.perf_counter()
        
        async def monitor():
            while True:
                
                iter_start = time.perf_counter()
                self.elapsed_times[name] = time.perf_counter() - self.start_times[name]
                self.iter_times[name] = time.perf_counter() - iter_start
                
                await asyncio.sleep(0) 
        
        monitor_task = asyncio.create_task(monitor())
        
        try:
            await coro
            
        finally:
            monitor_task.cancel()  

    async def __handle_events(self):
        """
        Handle pygame key events and pass them to the handling object, updates at an uncapped rate
        """
        while not self.exited:
            self.handling.current_time = self.elapsed_times["handle_events"]
            self.handling.delta_tick = self.delta_tick
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.__exit()
                    
                elif event.type == pygame.KEYDOWN:
                    self.handling.on_key_press(event.key)
                    
                elif event.type == pygame.KEYUP:
                    self.handling.on_key_release(event.key)

            await asyncio.sleep(0)
    
    async def __game_loop(self, four):
        """
        The main game loop, updates at a fixed tick rate
        
        args:
        (Four) four: the instance of the game
        """
        while not self.exited:
         
            self.current_time = self.elapsed_times["game_loop"]
            
            if self.current_time >= self.next_tick_time:
                
                self.__do_tick(four)
                self.next_tick_time += 1/self.config.TPS
            
            self.__get_tps()
            
            await asyncio.sleep(0)

    async def __render_loop(self):
        """
        The main render loop, updates at a fixed or uncapped frame rate
        """
        while not self.exited:
            
            if self.config.UNCAPPED_FPS:
                
                self.__do_render()
                
            elif self.current_time >= self.next_frame_time and not self.config.UNCAPPED_FPS:
                self.__do_render()
                self.next_frame_time += 1/self.config.FPS
        
            self.__get_fps()
            
            await asyncio.sleep(0)
            
    def __do_tick(self, four):
        """
        Peform one tick of the game logic
        
        args:
        (Four) four: the instance of the game
        """
        self.delta_tick = self.__calc_df()
        four.loop()
        self.state_snapshot = four.forward_state()
        self.game_clock.tick()
    
    def __do_render(self):
        """
        Render a single frame of the game
        """
        self.render.render_frame(self.state_snapshot, self.show_render_debug, self.show_tick_debug, self.debug_dict)
        self.render_clock.tick()
               
    def __exit(self):
        """
        Exit the game
        """
        self.exited = True
        pygame.quit()
        
    def __get_tps(self):
        """
        Update the stored TPS value
        """
        self.TPS = self.game_clock.get_fps()
    
    def __get_fps(self):
        """
        Update the stored FPS value
        """
        self.FPS = self.render_clock.get_fps()

    def __calc_exe_time_avg(self):
        """
        For debug menu, calculate the average execution time of a tick
        """
        
        if self.exe_idx >= self.max_avg_len:
            self.exe_idx = 0
            
        if len(self.tick_times) >= self.max_avg_len:
            self.tick_times.pop(self.exe_idx)
             
        self.tick_times.append(self.iter_times["game_loop"])
            
        self.best_tick_time = min(self.tick_times)
        self.worst_tick_time = max(self.tick_times)
            
        self.exe_idx += 1   
        self.tick_time = sum(self.tick_times)/len(self.tick_times)
        
    def __calc_render_time_avg(self):
        """
        For debug menu, calculate the average time to render a frame
        """
        
        if self.r_idx >= self.max_avg_len:
            self.r_idx = 0
            
        if len(self.render_times) >= self.max_avg_len:
            self.render_times.pop(self.r_idx)
            
        self.render_times.append(self.iter_times["render_loop"])
            
        self.best_render_time = min(self.render_times)
        self.worst_render_time = max(self.render_times)
        
        self.r_idx += 1
        self.render_time_avg =  sum(self.render_times)/len(self.render_times)
        
    def __calc_average_TPS(self):
        """
        For debug menu, calculate the average TPS
        """
        
        if self.TPS == float('inf') or self.TPS == float('-inf'):
            self.TPS = 0

        if self.tps_idx >= self.max_avg_len:
            self.tps_idx = 0
            
        if len(self.TPSs) >= self.max_avg_len:
            self.TPSs.pop(self.tps_idx)
                
        self.TPSs.append(self.TPS)
        
        self.tps_idx += 1
    
        self.worst_tps = min(self.TPSs)
        self.best_tps = max(self.TPSs)
        
        self.average_TPS = sum(self.TPSs) / len(self.TPSs)
        
    def __calc_average_FPS(self):
        """
        For debug menu, calculate the average FPS
        """
    
        if self.fps_idx >= self.max_avg_len:
            self.fps_idx = 0
            
        if len(self.FPSs) >= self.max_avg_len:
            self.FPSs.pop(self.fps_idx)
                        
        self.FPSs.append(self.FPS)
        
        self.fps_idx += 1
        self.average_FPS = sum(self.FPSs)/len(self.FPSs)
    
        self.worst_fps = min(self.FPSs)
        self.best_fps = max(self.FPSs)
        
    def __calc_df(self):
        """
        For debug menu, calculate the delta frame time, how many frames behind or ahead the game is to the desired TPS
        """
        if self.TPS == float('inf') or self.TPS == float('-inf'):
            self.TPS = 0
        
        self.delta_tick = int(self.config.TPS - self.TPS)
        
        if self.df_idx >= self.max_avg_len - 1:
            self.df_idx = 0
            
        if len(self.dfs) >= self.max_avg_len - 1:
            self.dfs.pop(self.df_idx)
            
        self.dfs.append(self.delta_tick)
        self.average_df = sum(self.dfs)/len(self.dfs)
        
        self.worst_df = max(self.dfs)
        self.best_df = min(self.dfs)
        
        self.df_idx += 1
        
    async def __get_debug_info(self):
        """
        Fetch the debug information for the debug menu
        """
        while not self.exited:
            if self.show_all_debug:
                    self.__calc_average_FPS()
                    self.__calc_render_time_avg()
                    
                    self.__calc_average_TPS()
                    self.__calc_exe_time_avg()
                    
                    self.debug_dict = {
                        'FPS': self.average_FPS,
                        'TPS': self.average_TPS,
                        'TPS_RAW': self.TPS,
                        'FPS_RAW': self.FPS,
                        'SIM_T': self.tick_time,
                        'SIM_T_RAW': self.iter_times["game_loop"],
                        'REN_T': self.render_time_avg,
                        'REN_T_RAW': self.iter_times["render_loop"],
                        'DF': self.average_df,
                        'DF_RAW': self.delta_tick,
                        'TICKCOUNT': self.state_snapshot.tick_counter,
                        'WORST_SIM_T': self.worst_tick_time,
                        'WORST_REN_T': self.worst_render_time,
                        'WORST_FPS': self.worst_fps,
                        'WORST_TPS': self.worst_tps,
                        'WORST_DF': self.worst_df,
                        'BEST_SIM_T': self.best_tick_time,
                        'BEST_REN_T': self.best_render_time,
                        'BEST_FPS': self.best_fps,
                        'BEST_TPS': self.best_tps,
                        'BEST_DF': self.best_df
                    }
                    
            elif self.show_render_debug and not self.show_all_debug and not self.show_tick_debug:
                self.__calc_average_FPS()
                self.__calc_render_time_avg()
                
                self.debug_dict = {
                    'FPS': self.average_FPS,
                    'FPS_RAW': self.FPS,
                    'WORST_FPS': self.worst_fps,
                    'BEST_FPS': self.best_fps,
                    
                    'REN_T': self.render_time_avg,
                    'REN_T_RAW': self.render_time_raw,
                    
                    'WORST_REN_T': self.worst_render_time,
                    'BEST_REN_T': self.best_render_time
                }
                
            elif self.show_tick_debug and not self.show_all_debug and not self.show_render_debug:
                self.__calc_average_TPS()
                self.__calc_exe_time_avg()
                
                self.debug_dict = {
                    'TPS': self.average_TPS,
                    'TPS_RAW': self.TPS,
                    'WORST_TPS': self.worst_tps,
                    'BEST_TPS': self.worst_tps,
                    
                    'SIM_T': self.tick_time,
                    'SIM_T_RAW': self.tick_time_raw,
                    'WORST_SIM_T': self.worst_tick_time,
                    'BEST_SIM_T': self.best_tick_time,
                    
                    'DF': self.average_df,
                    'DF_RAW': self.delta_tick,
                    'WORST_DF': self.worst_df,
                    'BEST_DF': self.best_df,
                    
                    'TICKCOUNT': self.state_snapshot.tick_counter
                }
        
            await asyncio.sleep(0)

class Clock:
    def __init__(self, max_entries = 128):
        """
        Custom clock object as pygames inbuilt clock is trash for timing microsecond processes (has a resolution of 10ms????)
        Instead use clock with highest resolution possible (time.perf_counter) and calculate the FPS from the average time between ticks
        (literally a copy of pygame.time.Clock but with time.perf_counter)
        
        args:
        (int) max_entries: the maximum number of entries to store in the clock
        """
        self.max_entries = max_entries
        self.times = deque(maxlen = max_entries)
        self.last_time = time.perf_counter()
        self.fps = 0

    def tick(self):
        """
        Tick the clock once, and calculate the average time between ticks to calculate the FPS
        """
        current_time = time.perf_counter()
        dt = current_time - self.last_time
        self.last_time = current_time
        self.times.append(dt)
        
        if len(self.times) > 1:
            average_time = sum(self.times) / len(self.times)
            self.fps = 1 / average_time
        else:
            self.fps = 0  
    
    def get_fps(self):
        """
        Return the FPS of the clock
        """
        return self.fps
            
async def main():
    pygame_instance = PyGameInstance(show_all_debug = True, show_render_debug = False, show_tick_debug = False)
    four = Four(pygame_instance)
    await pygame_instance.run(four)

if __name__ == "__main__":
    asyncio.run(main())
