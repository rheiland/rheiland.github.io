package gui;

import actor.BlackCat;
import actor.RatBotActor;
import actor.Block;
import grid.Grid;
import grid.Location;
import java.util.ArrayList;
import java.util.Random;
import world.World;

/**
 * The Arena class includes all of the methods needed to setup the arena 
 * according to the rules of the game.  
 * @author Spock
 */
public class RatBotsArena 
{
    private final int PERCENT_BLOCKS = 12;
    /**
     * The size of a side of the central starting room in the arena. 
     */
    public  static final int CENTER_SIZE = 6;
    
    private Random randy = new Random();
    
    private boolean showBlocks = true;

    
    /**
     * Toggles whether the grid will include Blocks or not.  
     * This is an option in the Arena menu.
     */
    public void toggleShowBlocks(World world) 
    { 
        showBlocks = ! showBlocks; 
    }

    /**
     * Initializes the Arena based on the selected rules.  
     * @param world the world that the Arena is within
     */
    public void initializeArena(World world)
    {
    	// rwh: test 0 (normal, random)
//        if(showBlocks) addRandomBlocks(world);
//        if(showBlocks) addCenterBlocks(world);
//        if(showBlocks) world.add(getRandomCenterLocation(world), new BlackCat());
        
        // test 1 - rwh - make a simple "trap" of 3 blocks
        Location loc = new Location(11,11);
        world.add(loc, new Block());
        loc = new Location(12,12);
        world.add(loc, new Block());
        loc = new Location(13,11);
        world.add(loc, new Block());
    }
    
    private void addRandomBlocks(World world)
    {
        Grid grid = world.getGrid();
        int rows = grid.getNumRows();
        int cols = grid.getNumCols();

        for (int i = 0; i < rows; i++)
            for (int j = 0; j < cols; j++)
            {
                Location loc = new Location(i, j);
                
                if (grid.isValid(loc) && grid.get(loc) == null && 
                         randy.nextInt(100)<PERCENT_BLOCKS && !isInCenter(loc,grid))
                    world.add(loc, new Block());
            }        
    }
    
    private void addCenterBlocks(World world)
    {
        Grid grid = world.getGrid();
        int doorway = 5;
        for(int q=0;q<(CENTER_SIZE-1)/2;q++)
        {
            int small = (grid.getNumCols()-CENTER_SIZE)/2;
            int large = (grid.getNumCols()+CENTER_SIZE)/2-1;
            if(!((Math.abs(q+doorway))<=2))
            {
                world.add(new Location(small+q,small), new Block());
                world.add(new Location(small,small+q), new Block());
                world.add(new Location(large-q,large), new Block());
                world.add(new Location(large,large-q), new Block());
                world.add(new Location(small+q,large), new Block());
                world.add(new Location(large,small+q), new Block());
                world.add(new Location(large-q,small), new Block());
                world.add(new Location(small,large-q), new Block());
            }
        }
    }
       
    private Location getRandomCenterLocation(World world)
    {
        Grid<RatBotActor> gr = world.getGrid();
        int tailCount = 0;
        // get all valid empty locations and pick one at random
        ArrayList<Location> emptyLocs = new ArrayList<Location>();
        for(int x=0; x<gr.getNumCols(); x++)
        {
            for(int y=0; y<gr.getNumRows(); y++)
            {
                Location loc = new Location(y,x);
                if( gr.isValid(loc) && gr.get(loc)==null && this.isInCenter(loc, gr) )
                {
                    emptyLocs.add(loc);
                }
            }
        }
        
        if (emptyLocs.isEmpty())
        {
            System.out.println("WARNING: could not find an empty non-center location!!! " + tailCount);
            return new Location(15,15);
        }
        int r = randy.nextInt(emptyLocs.size());
        return emptyLocs.get(r);       

    }
        
    private boolean isInCenter(Location loc, Grid<RatBotActor> grid)
    {
        if( loc.getCol() >= (grid.getNumCols()-CENTER_SIZE)/2 &&
            loc.getCol() < (grid.getNumCols()+CENTER_SIZE)/2 &&
            loc.getRow() >= (grid.getNumRows()-CENTER_SIZE)/2 &&
            loc.getRow() < (grid.getNumRows()+CENTER_SIZE)/2 )
            return true;
        return false;                 
    }
    
    
}
