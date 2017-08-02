
package world;

import actor.Rat;
import actor.RatBot;
import actor.RatBotActor;
import actor.Tail;
import grid.Grid;
import grid.Location;
import grid.RatBotsGrid;
import gui.RatBotsArena;
import gui.RatBotsColorAssigner;
import gui.RatBotsScoreBoard;
import java.util.ArrayList;
import java.util.Random;



/**
 * A RatBotWorld is full of Actors used in the game RatBots.  
 * @author Spock
 */
public class RatBotWorld extends ActorWorld
{
    private static final String DEFAULT_MESSAGE = "RatBots is awesome.";
    private static Random randy = new Random();

    private static int moveNum = 0;
    private static int roundNum = 0;
    private boolean roundRobin = false;
    private int rr1=0; 
    private int rr2=0;
    private boolean matchReady = false;
    private long matchstart;
    
    
    /**
     * The number of moves in a round of RatBots competition.
     */
    public static final int NUM_MOVES_IN_ROUND = 500;
    /**
     * The number of rounds in a match of RatBots competition.  
     */
    public static final int NUM_ROUNDS_IN_MATCH = 100;
    
    private RatBotsArena arena = new RatBotsArena();
    
    private ArrayList<Rat> rats = new ArrayList<Rat>();
    private ArrayList<Rat> allrats = new ArrayList<Rat>();
    
    /**
     * Constructs a RatBot world with a default grid.
     */
    public RatBotWorld()
    {
        initializeGridForRound();
        initializeMatch();
    }

    /**
     * Constructs a RatBot world with a given grid.
     * @param grid the grid for this world.
     */
    public RatBotWorld(Grid<RatBotActor> grid)
    {
        super(grid);
        initializeGridForRound();
        initializeMatch();
    }

    /**
     * gets the Arena used in this World.
     * @return the Arena
     */
    public RatBotsArena getArena() { return arena; }
    /**
     * Gets the current move number in the round being played.  
     * @return the move number in the current round.
     */
    public static int getMoveNum() { return moveNum; }
    /**
     * Gets the current round number in the match being played.  
     * @return the round number in the current match.
     */
    public static int getRoundNum() { return roundNum; }
    
    private void initializeMatch()
    {
//        RatBotsGrid gr = (RatBotsGrid)getGrid();
//        ArrayList<Rat> rats = gr.getAllRats();
        
//        System.out.println("INITIALIZING MATCH");
        moveNum = 0;
        roundNum = 0;
        matchReady = true;
        
        if(!roundRobin)
        {
            rats.clear(); 
            rats.addAll(allrats);
        }
        else
        {
            if(rats.size() > 1)
            {
                System.out.println(rats.get(0).getRatBot().getName()+","+rats.get(0).getRoundsWon()
                        +","+  rats.get(1).getRatBot().getName()+","+rats.get(1).getRoundsWon() );
//                        +"      time(sec)="+(int)((System.currentTimeMillis() - matchstart)/1000));
                if(rats.get(0).getRoundsWon()+rats.get(1).getRoundsWon()<100)
                    System.out.println("Incomplete match...???");
                //score match
                if(rats.get(0).getRoundsWon()>rats.get(1).getRoundsWon())
                {
                    rats.get(0).increaseMatchesWon();
                    rats.get(1).increaseMatchesLost();
                }
                if(rats.get(0).getRoundsWon()==rats.get(1).getRoundsWon())
                {
                    rats.get(0).increaseMatchesTied();
                    rats.get(1).increaseMatchesTied();
                }
                if(rats.get(0).getRoundsWon()<rats.get(1).getRoundsWon())
                {
                    rats.get(1).increaseMatchesWon();
                    rats.get(0).increaseMatchesLost();
                }
                rats.get(0).setRoundsWon(0);
                rats.get(1).setRoundsWon(0);
                
            }
            rats.clear(); 
            rr2++;
            if(rr2==allrats.size())
            {
                rr1++;
                rr2=rr1+1;
                if(rr1==allrats.size()-1)
                {
                    for(Rat x : allrats)
                    {
                        System.out.println(x.getRatBot().getName()+
                               ",  TP=,"+x.getTotalScore() +
                                ",  w=,"+x.getMatchesWon()+
                                ",  t=,"+x.getMatchesTied()+
                                ",  l=,"+x.getMatchesLost()                              
                                );
                    }
                    System.out.println("TOURNEY COMPLETE");
                    
                }
            }
            rats.add(allrats.get(rr1));
            rats.add(allrats.get(rr2));

        }
            initializeGridForRound();
            matchstart = System.currentTimeMillis();
    }
    
    
    
    
    /**
     * Initialize the arena and each of the RatBots for a round of competition.
     */
    public final void initializeGridForRound()
    {
    	if (false)   // rwh: true is normal; false is my block
    	{
        clearAllObjectsFromGrid();
        arena.initializeArena(this);
        for(Rat r : rats) 
        {
            r.initialize();
            r.putSelfInGrid(getGrid(), getRandomEmptyCenterLocation());
            r.setDirection(getRandomDirection());
        }
        moveNum = 0; 
    	}
    	else  // rwh block
    	{
        clearAllObjectsFromGrid();
        arena.initializeArena(this);
        Location loc = new Location(12,8);  // rwh
        for(Rat r : rats) 
        {
            r.putSelfInGrid(getGrid(), loc);  // rwh: set rat loc/dir
            r.setDirection(90);
        }
        moveNum = 0; 
    	}
    }
    /**
     * Clears the Arena in preparation of starting a new round. 
     * @return an ArrayList of the Rats in the arena.
     */
    public void clearAllObjectsFromGrid()
    {
        RatBotsGrid<RatBotActor> gr = (RatBotsGrid<RatBotActor>)this.getGrid();
        for(int x=0; x<gr.getNumCols(); x++)
        {
            for(int y=0; y<gr.getNumRows(); y++)
            {
                Location loc = new Location(y,x);
                RatBotActor a = gr.get(loc);
                if(a != null)
                {
                    a.removeSelfFromGrid();
//                    if(a instanceof Rat)
//                    {
//                        Rat r = (Rat)a;
//                        rats.add(r);
//                    }
                }
            }
        }
//        ArrayList<Location> locs = this.getGrid().getOccupiedLocations();
//        rats.clear();
//        for(Location loc : locs)
//        {      
//            Actor a = gr.get(loc);
//            a.removeSelfFromGrid();
//            if(a instanceof Rat)
//            {
//                Rat r = (Rat)a;
//                rats.add(r);
//            }
//        }
//        locs = this.getGrid().getOccupiedLocations();
//        System.out.println("size = "+locs.size());
//        return rats;
    }
    /**
     * Scores the results from a round of competition.
     */
    public void scoreRound()
    {
        int max = RatBotsScoreBoard.getMaxScore();
        for(Rat r : rats)
        {
            if(r.getScore() == max)
                r.increaseRoundsWon();
        }
        roundNum++;
    }
    
    //inheirits javadoc comment from world.
    @Override
    public void show()
    {
        if (getMessage() == null)
            setMessage(DEFAULT_MESSAGE);
        super.show();
    }

    //inheirits javadoc comment from world.
    @Override
    public void step()
    {
        Grid<RatBotActor> gr = getGrid();

        if(!matchReady)
            initializeMatch();
            
        
        moveNum++;
        if(moveNum > NUM_MOVES_IN_ROUND)
        {
//            clearAllObjectsFromGrid();
            scoreRound();
            initializeGridForRound();
            moveNum = 1;
        }
        if(roundNum >= NUM_ROUNDS_IN_MATCH && roundRobin) 
        {
            initializeMatch();
            return;
        } 
//        else
//        {
//            System.out.println("roundNum "+roundNum);            
//        }
        ArrayList<RatBotActor> actors = new ArrayList<RatBotActor>();
        // Look at all grid locations.
        for (int r = 0; r < gr.getNumRows(); r++)
        {
            for (int c = 0; c < gr.getNumCols(); c++)
            {
                // If there's an object at this location, put it in the array.
                Location loc = new Location(r, c);
                if (gr.get(loc) != null) 
                    actors.add(gr.get(loc));
            }
        }

        for (RatBotActor a : actors)
        {
            // only act if another actor hasn't removed a
            if (a.getGrid() == gr)
                a.act();
        }
        
        for (RatBotActor a : actors)
        {
            if (a.getGrid() == gr && a instanceof Rat)
            {
                Rat r = (Rat)a;
                r.cleanUpDeadTailsAndUpdateScore();                
            }
        }
        
        
    }
    /**
     * Add a new RatBot to the arena. 
     * @param bot the RatBot to be added.  
     */
    public void add(RatBot bot)
    {
        Rat newRat = new Rat(bot,RatBotsColorAssigner.getAssignedColor());
        Location inCenter = this.getRandomEmptyCenterLocation();
        allrats.add(newRat);
        rats.add(newRat);
        initializeGridForRound();
        
//        newRat.putSelfInGrid(getGrid(), inCenter);        
    }    
    /**
     * Gets one of the 8 possible directions.
     * @return a random direction.
     */
    public int getRandomDirection()
    {
        return randy.nextInt(4)*90;
    }
    /**
     * Gets an empty Location in the center room.  
     * @return a random empty Location from the center room.  
     */
    public Location getRandomEmptyCenterLocation()
    {
        Grid<RatBotActor> gr = getGrid();
        int rows = gr.getNumRows();
        int cols = gr.getNumCols();

        // get all valid empty locations and pick one at random
        ArrayList<Location> emptyLocs = new ArrayList<Location>();
        for (int i = (rows-RatBotsArena.CENTER_SIZE)/2; i < (rows+RatBotsArena.CENTER_SIZE)/2; i++)
        {
            for (int j = (cols-RatBotsArena.CENTER_SIZE)/2; j < (cols+RatBotsArena.CENTER_SIZE)/2; j++)
            {
                Location loc = new Location(i, j);
                if (gr.isValid(loc) && (gr.get(loc) == null || gr.get(loc) instanceof Tail))
                    emptyLocs.add(loc);
            }
        }
        if (emptyLocs.isEmpty())
        {
            System.out.println("WARNING: could not find an empty center location!!!");
            return new Location(15,15);
        }
        int r = randy.nextInt(emptyLocs.size());
        return emptyLocs.get(r);       
    }
    
}
