package main;

import util.PAGuiUtil;
import util.RatBotManager;
import world.RatBotWorld;

public class RatBotsRunner
{
    public static void main(String[] args)
    {
        PAGuiUtil.setLookAndFeelToOperatingSystemLookAndFeel();
        
        RatBotWorld world = new RatBotWorld();
        
        // Load RatBots from the 'ratbot' package
        RatBotManager.loadRatBotsFromClasspath("ratbot/", world);

        // Prompt for additional RatBot loading
        RatBotManager.loadRatBotsFromDirectoryIntoWorld(world, false);

//        //This is where you can add RatBots to the match.  
//        world.add(new RandomRat());
//        world.add(new DartRat());
//        world.add(new LazyRat());
//        world.add(new SmartRat());
        
        world.add(new RatUTest());  
        world.show();
    }
}